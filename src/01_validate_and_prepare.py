"""Source CSV validation; builds a unique listing-by-month fact and dimensions."""
from pathlib import Path
import json, runpy
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'; OUT=ROOT/'data/processed'; REPORT=ROOT/'reports'
publish_frames = runpy.run_path(str(Path(__file__).with_name('pipeline_io.py')))['publish_frames']
source_tools = runpy.run_path(str(Path(__file__).with_name('source_audit.py')))

def run():
    OUT.mkdir(parents=True,exist_ok=True);REPORT.mkdir(parents=True,exist_ok=True)
    a=pd.read_csv(RAW/'past_rates.csv',dtype={'listing_id':str},low_memory=False)
    b=pd.read_csv(RAW/'listings_monthly.csv',dtype={'listing_id':str, 'host_id':'string'},low_memory=False)
    parquet_audit = source_tools['run'](RAW, REPORT)
    for name,d in [('past_rates',a),('listings_monthly',b)]:
        if d[['listing_id','month_date']].duplicated().any():raise ValueError(f'Duplicate key in {name}')
        if d.empty or d.listing_id.isna().any() or d.listing_id.str.strip().eq('').any():
            raise ValueError(f'Empty source or missing listing ID in {name}')
        dates = pd.to_datetime(d.month_date,format='%Y-%m-%d',errors='raise')
        if dates.isna().any() or not dates.dt.is_month_start.all():
            raise ValueError(f'Missing or non-month-start date in {name}')
        flag = d.active.astype('string').str.lower().map({'true': True, 'false': False, '1': True, '0': False})
        if flag.isna().any(): raise ValueError(f'Invalid active flag in {name}')
        d['active'] = flag.astype(bool)
        for field in ('native_avg_daily_rate', 'native_revenue', 'native_revpar', 'occupancy'):
            if not (np.isfinite(d[field]) & d[field].ge(0)).all():
                raise ValueError(f'Missing/nonfinite/negative {field} in {name}')
        if not d.occupancy.le(1).all(): raise ValueError(f'Invalid occupancy in {name}')
        for field in ('available_days', 'unavailable_days'):
            if not (d[field].ge(0) & d[field].mod(1).eq(0)).all():
                raise ValueError(f'Invalid {field} in {name}')
        if not d.currency.eq('AED').all(): raise ValueError(f'Non-AED currency in {name}')
        beds = pd.to_numeric(d.bedrooms, errors='raise').dropna()
        if not (beds.ge(0) & beds.mod(1).eq(0)).all():
            raise ValueError(f'Invalid bedrooms in {name}')
    keys=pd.MultiIndex.from_frame(a[['listing_id','month_date']])
    missed=int((~pd.MultiIndex.from_frame(b[['listing_id','month_date']]).isin(keys)).sum())
    if missed:raise ValueError(f'{missed} enriched monthly keys not found in primary source')
    # Cross-check the duplicate monthly measures agree before treating the enriched file as metadata only.
    shared=['native_avg_daily_rate','occupancy','native_revenue','native_revpar','active',
            'bedrooms','latitude','longitude','neighborhood','room_type','listing_type',
            'currency','available_days','unavailable_days']
    check=a[['listing_id','month_date']+shared].merge(
        b[['listing_id','month_date']+shared],on=['listing_id','month_date'],
        suffixes=('_primary','_enriched'),validate='one_to_one')
    mismatches={}
    for name in shared:
        x,y=check[name+'_primary'],check[name+'_enriched']
        count=int((~(x.eq(y)|(x.isna()&y.isna()))).sum())
        mismatches[name]=count
    if any(mismatches.values()):raise ValueError(f'Inconsistent shared fields: {mismatches}')
    columns=['listing_id','month_date','active','listing_type','room_type','latitude','longitude','bedrooms',
             'neighborhood','available_days','unavailable_days','occupancy','native_avg_daily_rate',
             'native_revenue','native_revpar','currency']
    fact=a[columns].copy();fact['month_date']=pd.to_datetime(fact.month_date)
    snapshot = pd.read_parquet(RAW/'listings.parquet')
    snapshot['listing_id'] = snapshot.listing_id.astype(str)
    if snapshot.listing_id.duplicated().any() or set(snapshot.listing_id)!=set(a.listing_id):
        raise ValueError('Listing snapshot must contain exactly one row per historical listing')
    native_booked = source_tools['nested_months'](snapshot)[['listing_id','month_date','native_booked_rate_avg']]
    native_booked['month_date'] = pd.to_datetime(native_booked.month_date)
    fact = fact.merge(native_booked,on=['listing_id','month_date'],how='left',validate='one_to_one')
    booked = fact.native_booked_rate_avg.dropna()
    if not (np.isfinite(booked) & booked.ge(0)).all(): raise ValueError('Invalid native booked rate')
    fact['bedrooms']=pd.to_numeric(fact.bedrooms,errors='coerce').astype('Int64')
    fact=fact.sort_values(['listing_id','month_date']).reset_index(drop=True)
    prev=fact.groupby('listing_id').month_date.shift()
    fact['same_listing_prev_month']=(prev==(fact.month_date-pd.offsets.MonthBegin(1))).fillna(False)
    bad_days=int(((fact.available_days+fact.unavailable_days)!=fact.month_date.dt.days_in_month).sum())
    bad_ccy=int((fact.currency!='AED').sum())
    if bad_days or bad_ccy:raise ValueError(f'Bad monthly days={bad_days}, non-AED={bad_ccy}')
    # Latest snapshot for DimListing; matching always uses month-grain fields from fact.
    primary_latest=fact.sort_values('month_date').drop_duplicates('listing_id',keep='last')
    extra=['listing_id','guests','beds','baths','num_reviews','star_rating','superhost','property_type','host_id']
    dim=primary_latest[['listing_id','listing_type','room_type','bedrooms','latitude','longitude','neighborhood']].merge(
        snapshot[extra],how='left',on='listing_id',validate='one_to_one')
    for col in ('guests','beds','baths','num_reviews','star_rating'):
        dim[col] = pd.to_numeric(dim[col],errors='raise')
    dim['enriched_metadata_available']=dim.listing_id.isin(snapshot.listing_id)
    dim['metadata_source']='listings.parquet (undated snapshot)'
    dim['superhost']=dim.superhost.map(lambda v: str(v) if pd.notna(v) else None)
    months=pd.DataFrame({'month_date':pd.date_range(fact.month_date.min(),fact.month_date.max(),freq='MS')})
    months['year']=months.month_date.dt.year
    months['month_number']=months.month_date.dt.month
    months['month_label']=months.month_date.dt.strftime('%b %Y')
    months['month_sort']=months.year*100+months.month_number
    months['year_month']=months.month_date.dt.strftime('%Y-%m')
    coverage=fact.groupby('month_date',as_index=False).agg(
        observed_listings=('listing_id','nunique'),active_listings=('active','sum'),
        neighborhood_missing_pct=('neighborhood',lambda v:float(v.isna().mean()*100)),
        bedrooms_missing_pct=('bedrooms',lambda v:float(v.isna().mean()*100)),
        same_listing_prev_month=('same_listing_prev_month','sum'))
    act=fact[fact.active]
    coverage=coverage.merge(act.groupby('month_date').agg(
        median_active_adr_aed=('native_avg_daily_rate','median'),
        median_active_estimated_occupancy=('occupancy','median')).reset_index(),on='month_date',how='left')
    coverage['coverage_change_pct']=coverage.observed_listings.pct_change(fill_method=None)*100
    # Assert monthly continuity figures are fully populated; older cached exports
    # had 60 missing 'same_listing_prev_month' counts despite correct fact data.
    expected_returning = fact.groupby('month_date')['same_listing_prev_month'].sum()
    actual_returning = coverage.set_index('month_date')['same_listing_prev_month']
    if (actual_returning.isna().any() or not actual_returning.equals(expected_returning)
            or not actual_returning.le(coverage.set_index('month_date')['observed_listings']).all()):
        raise AssertionError('Monthly returning-listing counts did not reconcile')
    for d in [fact,coverage,months]:d['month_date']=d.month_date.dt.strftime('%Y-%m-%d')
    publish_frames(dict(fact_listing_month=fact,dim_listing=dim,dim_month=months,
                        fact_coverage_month=coverage), OUT, 'preparation_manifest.json',
                   sources=[RAW/n for n in ('past_rates.csv','listings_monthly.csv','past_rates.parquet','listings.parquet')])
    latest=fact.month_date.max();latest_all=fact[fact.month_date==latest];latest_active=latest_all[latest_all.active]
    info={
        'source_sha256': {n:v['sha256'] for n,v in parquet_audit['sources'].items()},
        'primary_rows':len(fact),'enriched_rows':len(b),'enriched_rows_not_in_primary':missed,
        'shared_field_mismatches':mismatches,
        'unique_historical_listings':int(fact.listing_id.nunique()),'enriched_unique_listings':int(b.listing_id.nunique()),
        'snapshot_enriched_unique_listings':int(snapshot.listing_id.nunique()),
        'first_month':fact.month_date.min(),'latest_month':latest,'month_count':int(len(months)),
        'latest_observed':int(len(latest_all)),'latest_active':int(len(latest_active)),
        'latest_median_active_adr_aed':float(latest_active.native_avg_daily_rate.median()),
        'latest_median_estimated_occupancy':float(latest_active.occupancy.median()),
        'latest_zero_occupancy_count':int((latest_active.occupancy==0).sum()),
        'latest_zero_occupancy_pct':float((latest_active.occupancy==0).mean()*100),
        'latest_sample_estimated_revenue_aed':float(latest_active.native_revenue.sum()),
        'latest_missing_neighborhood_pct':float(latest_all.neighborhood.isna().mean()*100),
        'latest_missing_bedrooms_pct':float(latest_all.bedrooms.isna().mean()*100),
        'max_listing_id_length':int(fact.listing_id.str.len().max()),
        'bad_month_day_count':bad_days,'bad_currency':bad_ccy,
        'parquet_inspected':True,
        'parquet_present':{n:(RAW/n).exists() for n in ['listings.parquet','past_rates.parquet']},
        'largest_observed_monthly_count_changes':coverage.loc[coverage.coverage_change_pct.abs().nlargest(3).index,
            ['month_date','observed_listings','coverage_change_pct']].round(2).to_dict('records')
    }
    (REPORT/'data_quality_summary.json').write_text(json.dumps(info,indent=2))
    lines=['# Source validation — actual CSV data','',f'- Primary records: **{len(fact):,}** (unique listing × month).',
          f'- Enriched metadata records: **{len(b):,}**; **not additive** to primary records.',
          f'- Dates: **{info["first_month"]}** to **{latest}** ({len(months)} months).',
          f'- Distinct historical listings: **{info["unique_historical_listings"]:,}**.',
          f'- Latest observed: **{len(latest_all):,}**, active: **{len(latest_active):,}**.',
          f'- Latest median ADR across active sampled listings: **AED {info["latest_median_active_adr_aed"]:,.0f}**.',
          f'- Median provider-estimated occupancy in latest active records: **{info["latest_median_estimated_occupancy"]:.1%}**.',
          f'- Latest active records with zero modeled occupancy: **{info["latest_zero_occupancy_count"]:,}** (**{info["latest_zero_occupancy_pct"]:.1f}%**) — interpret carefully.',
          f'- Latest-month missing neighborhood: **{info["latest_missing_neighborhood_pct"]:.1f}%**.',
          f'- Latest-month missing bedrooms: **{info["latest_missing_bedrooms_pct"]:.1f}%**.',
          f'- Listing IDs are TEXT; maximum **{info["max_listing_id_length"]}** digits.',
          '', '## Largest sample count changes']
    for r in info['largest_observed_monthly_count_changes']:
        lines.append(f'- {r["month_date"]}: {r["observed_listings"]:,} listings ({r["coverage_change_pct"]:+.1f}% MoM).')
    lines +=['','## Not demonstrated','- Source is not a complete Dubai market census.',
           '- Modeled occupancy/revenue are not verified bookings, cash receipts or profit.',
           '- All four files inspected; details and checksums are in source_audit.json.',
           '- Undated Parquet snapshot metadata is descriptive only, never historical matching evidence.']
    (REPORT/'data_quality_summary.md').write_text('\n'.join(lines)+'\n')
    print(f'PASS source: {len(fact):,} rows, {len(months)} months; latest {latest}: {len(latest_active):,} active')
    return info

if __name__=='__main__':run()

"""Brute-force benchmark reconstruction from ORIGINAL CSV, across every month.

Does not import the matching engine or its eligibility/distance implementation.
Aggregated evidence only is published; source rows remain private.
"""
from pathlib import Path
import json
import time
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def run():
    start=time.perf_counter()
    raw=pd.read_csv(ROOT/'data/raw/past_rates.csv',dtype={'listing_id':str})
    fact=pd.read_csv(ROOT/'data/processed/fact_listing_month.csv',dtype={'listing_id':str})
    bench=pd.read_csv(ROOT/'data/processed/fact_peer_benchmark.csv',dtype={'listing_id':str})
    keys=['listing_id','month_date']
    source=raw.set_index(keys).sort_index(); prepared=fact.set_index(keys).sort_index()
    pd.testing.assert_frame_equal(source[prepared.columns.intersection(source.columns)],
                                  prepared[prepared.columns.intersection(source.columns)],check_dtype=False)
    eligible=(raw.active.eq(True)&raw.room_type.notna()&raw.bedrooms.ge(0)&raw.bedrooms.mod(1).eq(0)
              &raw.latitude.between(24.5,25.6)&raw.longitude.between(54.5,56)
              &np.isfinite(raw.native_avg_daily_rate)&raw.native_avg_daily_rate.gt(0))
    stored=bench.set_index(keys).sort_index()
    expected_keys=pd.MultiIndex.from_frame(raw.loc[eligible,keys])
    assert set(expected_keys)==set(stored[stored.comparison_status.ne('Ineligible')].index)
    assert set(source.index)==set(stored.index)
    checked=0; latest=raw.month_date.max(); sensitivity=[]; example_gaps=[]
    for group_key,g in raw[eligible].groupby(['month_date','room_type','bedrooms']):
        coords=np.deg2rad(g[['latitude','longitude']].to_numpy())
        rates=g.native_avg_daily_rate.to_numpy(); occupancy=g.occupancy.to_numpy()
        ids=g.listing_id.to_numpy()
        for i in range(len(g)):
            # Brute force vector against all members; no spatial tree/candidate pruning.
            h=np.sin((coords[:,0]-coords[i,0])/2)**2 + np.cos(coords[:,0])*np.cos(coords[i,0])*np.sin((coords[:,1]-coords[i,1])/2)**2
            km=2*6371.0088*np.arctan2(np.sqrt(np.clip(h,0,1)),np.sqrt(np.clip(1-h,0,1)))
            km[i]=np.inf
            inner=km<=2+1e-7; outer=km<=5+1e-7
            radius=2 if inner.sum()>=10 else 5
            chosen=inner if radius==2 else outer
            row=stored.loc[(ids[i],group_key[0])]
            assert row.peer_count==chosen.sum() and row.radius_km==radius
            assert row.comparison_status==('Eligible' if chosen.sum()>=10 else 'Insufficient peers')
            if chosen.sum()>=10:
                median=np.median(rates[chosen]); premium=100*(rates[i]/median-1)
                np.testing.assert_allclose([row.peer_p25_aed,row.peer_median_aed,row.peer_p75_aed],np.quantile(rates[chosen],[.25,.5,.75]))
                np.testing.assert_allclose(row.peer_median_estimated_occupancy,np.median(occupancy[chosen]))
                np.testing.assert_allclose(row.premium_pct,premium,atol=1e-8)
                np.testing.assert_allclose(row.estimated_occupancy_gap_pp,100*(occupancy[i]-np.median(occupancy[chosen])),atol=1e-8)
                absolute=round(abs(premium),9)
                assert row.review_signal==('Large deviation' if absolute>=35 else 'Review' if absolute>=20 else 'Within threshold')
                if group_key[0]==latest:
                    # Also investigate expansion for subjects whose 2km cohort was already sufficient.
                    two=np.median(rates[inner]) if inner.sum()>=2 else np.nan
                    five=np.median(rates[outer])
                    sensitivity.append({'radius':radius,'two_peers':int(inner.sum()),'five_peers':int(outer.sum()),
                                        'five_vs_two_pct':100*(five/two-1) if np.isfinite(two) else np.nan})
                    order=np.lexsort((ids,km)); examples=order[:5]
                    example_gaps.append(abs(100*(np.median(rates[examples])/median-1)))
            else:
                assert pd.isna(row.peer_median_aed) and pd.isna(row.premium_pct)
            checked+=1
    sensitivity=pd.DataFrame(sensitivity)
    valid=bench[(bench.month_date==latest)&bench.comparison_status.eq('Eligible')]
    data=valid.merge(raw,on=keys,validate='one_to_one')
    extreme=data[data.premium_pct.gt(200)]
    result={'eligible_listing_months_reconstructed':checked,'source_rows_preserved':len(fact),
            'seconds':round(time.perf_counter()-start,3),'latest_month':latest,
            'latest_abs_five_example_median_gap_over20':int((np.array(example_gaps)>20).sum()),
            'latest_median_example_gap_pct':float(np.median(example_gaps)),
            'latest_peer_iqr_above40_count':int(((valid.peer_p75_aed-valid.peer_p25_aed)/valid.peer_median_aed>.4).sum()),
            'latest_above200pct_count':len(extreme),
            'extreme_subject_rate_range_aed':[float(extreme.native_avg_daily_rate.min()),float(extreme.native_avg_daily_rate.max())],
            'extreme_peer_median_range_aed':[float(extreme.peer_median_aed.min()),float(extreme.peer_median_aed.max())],
            'max_premium_pct':float(data.premium_pct.max()),
            'radius_sensitivity':[]}
    for radius,rows in sensitivity.groupby('radius'):
        delta=rows.five_vs_two_pct.dropna().abs()
        result['radius_sensitivity'].append({'selected_radius':int(radius),'subjects':len(rows),'two_km_diagnostics':len(delta),
                    'median_abs_five_vs_two_pct':float(delta.median()),'p90_abs_five_vs_two_pct':float(delta.quantile(.9))})
    # Provider metrics are preserved, not redefined. Diagnose candidate identities only.
    days=pd.to_datetime(raw.month_date).dt.days_in_month
    result['metric_definition_diagnostics']={
        'revpar_vs_revenue_per_calendar_day_within1aed':int(np.isclose(raw.native_revpar,raw.native_revenue/days,atol=1,rtol=0).sum()),
        'revenue_vs_reported_rate_times_occupancy_days_within1aed':int(np.isclose(raw.native_revenue,raw.native_avg_daily_rate*raw.occupancy*days,atol=1,rtol=0).sum()),
        'denominator':len(raw),'note':'Numerical compatibility is not verification of provider definitions or actual bookings.'}
    (ROOT/'reports/independent_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


if __name__=='__main__':print(json.dumps(run(),indent=2))

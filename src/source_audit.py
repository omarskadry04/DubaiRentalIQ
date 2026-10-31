"""Inspect all four source files without publishing listing-level records."""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MONTH_FIELDS = {
    'date': 'month_date', 'rate_avg': 'avg_daily_rate',
    'native_rate_avg': 'native_avg_daily_rate', 'rev_par': 'revpar',
    'native_rev_par': 'native_revpar',
}


def nested_months(listings):
    rows = []
    for listing_id, months in zip(listings.listing_id, listings.months):
        if months is not None:
            for month in months:
                rows.append({'listing_id': str(listing_id), **month})
    result = pd.DataFrame(rows).rename(columns=MONTH_FIELDS)
    result['month_date'] = pd.to_datetime(result.month_date).dt.strftime('%Y-%m-%d')
    return result


def disagreements(left, right, keys, fields):
    merged = left[keys+fields].merge(right[keys+fields], on=keys, how='outer',
                                    suffixes=('_a','_b'), validate='one_to_one', indicator=True)
    if not merged['_merge'].eq('both').all():
        raise ValueError('Source key sets differ')
    counts = {}
    for field in fields:
        a, b = merged[field+'_a'], merged[field+'_b']
        if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
            equal = np.isclose(a.astype(float), b.astype(float), rtol=1e-12, atol=1e-9, equal_nan=True)
        else:
            equal = a.eq(b) | (a.isna() & b.isna())
        counts[field] = int((~equal).sum())
    return counts


def run(raw=None, report=None):
    raw = Path(raw) if raw is not None else ROOT/'data/raw'
    report = Path(report) if report is not None else ROOT/'reports'
    report.mkdir(parents=True, exist_ok=True)
    frames = {name: pd.read_csv(raw/name, dtype={'listing_id':str,'host_id':'string'}, low_memory=False)
              for name in ('past_rates.csv','listings_monthly.csv')}
    for name in ('past_rates.parquet','listings.parquet'):
        frames[name] = pd.read_parquet(raw/name)
        frames[name]['listing_id'] = frames[name].listing_id.astype(str)
    a = frames['past_rates.csv']
    nested = nested_months(frames['listings.parquet'])
    keys = ['listing_id','month_date']
    overlap_fields = [c for c in nested if c in a and c not in keys]
    parquet_agreement = disagreements(a, frames['past_rates.parquet'], keys, [c for c in a if c not in keys])
    nested_agreement = disagreements(a, nested, keys, overlap_fields)
    if any(parquet_agreement.values()) or any(nested_agreement.values()):
        raise ValueError('Parquet monthly data disagrees with CSV')
    profiles = []
    inventory = {}
    for name, frame in frames.items():
        key = keys if 'month_date' in frame else ['listing_id']
        inventory[name] = {'rows': len(frame), 'columns': len(frame.columns),
                           'unique_listings': int(frame.listing_id.nunique()),
                           'duplicate_keys': int(frame.duplicated(key).sum()),
                           'sha256': hashlib.sha256((raw/name).read_bytes()).hexdigest()}
        for column in frame:
            profiles.append({'source':name,'column':column,'dtype':str(frame[column].dtype),
                             'missing':int(frame[column].isna().sum()),'rows':len(frame)})
    pd.DataFrame(profiles).to_csv(report/'source_column_profile.csv',index=False)
    listing = frames['listings.parquet']
    facts_latest = a.sort_values('month_date').drop_duplicates('listing_id',keep='last')
    snapshot = listing[['listing_id','bedrooms','room_type','latitude','longitude']].copy()
    for c in ('bedrooms','latitude','longitude'): snapshot[c] = pd.to_numeric(snapshot[c])
    snapshot_diffs = disagreements(facts_latest,snapshot,['listing_id'],['bedrooms','room_type','latitude','longitude'])
    result = {'sources':inventory,'csv_parquet_disagreements':parquet_agreement,
              'nested_monthly_rows':len(nested),'nested_monthly_disagreements':nested_agreement,
              'snapshot_vs_latest_fact_disagreements':snapshot_diffs,
              'native_booked_rate_nonnull':int(nested.native_booked_rate_avg.notna().sum()),
              'geographic_ranges':a[['latitude','longitude']].agg(['min','max']).to_dict(),
              'countries':a.country.value_counts().to_dict(),
              'decision':'CSV history retained; redundant rates Parquet audited; listing snapshot enriches dimensions only; nested native booked rate retained separately. No historical quality matching.'}
    (report/'source_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


if __name__=='__main__':
    print(json.dumps(run(),indent=2))

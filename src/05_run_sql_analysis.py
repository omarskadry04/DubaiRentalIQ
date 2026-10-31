"""Execute standalone business SQL; independently reconcile values with pandas."""
from pathlib import Path
from contextlib import closing
import json
import platform
import sqlite3
import statistics
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def run(root=ROOT):
    root = Path(root)
    report = root/'reports/sql'
    report.mkdir(parents=True,exist_ok=True)
    database = root/'data/processed/dubai_rentals.sqlite'
    with closing(sqlite3.connect(database.as_uri()+'?mode=ro',uri=True)) as conn:
        results = {}
        timings = {}
        for path in sorted((root/'sql').glob('0[3-8]*.sql')):
            start = time.perf_counter()
            results[path.stem] = pd.read_sql_query(path.read_text(encoding='utf-8'),conn)
            timings[path.stem] = round(time.perf_counter()-start,4)
        validation = results['08_data_validation']
        if not validation.violations.eq(0).all():
            raise AssertionError(validation.loc[validation.violations.ne(0)].to_dict('records'))
        f = pd.read_csv(root/'data/processed/fact_listing_month.csv',dtype={'listing_id':str})
        b = pd.read_csv(root/'data/processed/fact_peer_benchmark.csv',dtype={'listing_id':str})
        active = f[f.active.eq(True)]
        expected = active.groupby('month_date').agg(median_active_adr_aed=('native_avg_daily_rate','median'),
                    mean_active_adr_aed=('native_avg_daily_rate','mean'),
                    median_estimated_occupancy=('occupancy','median'),
                    active_estimated_revenue_aed=('native_revenue','sum'))
        market = results['03_market_performance'].set_index('month_date')
        for col in expected:
            np.testing.assert_allclose(market.loc[expected.index,col],expected[col],rtol=1e-10,atol=1e-7)
        # Independently construct adjacent pairs with a calendar-shifted self-join (not LAG).
        before = f[['listing_id','month_date','active','native_avg_daily_rate']].copy()
        before.month_date = (pd.to_datetime(before.month_date)+pd.offsets.MonthBegin(1)).dt.strftime('%Y-%m-%d')
        joined = f.merge(before,on=['listing_id','month_date'],suffixes=('','_prev'),validate='one_to_one')
        pairs = joined[joined.active & joined.active_prev & joined.native_avg_daily_rate_prev.gt(0)].copy()
        pairs['change'] = 100*(pairs.native_avg_daily_rate/pairs.native_avg_daily_rate_prev-1)
        sql_pairs = pd.read_sql_query('SELECT listing_id,month_date,mom_change_pct FROM vw_listing_rate_transitions WHERE mom_change_pct IS NOT NULL',conn)
        pair_check = pairs.merge(sql_pairs,on=['listing_id','month_date'],how='outer',validate='one_to_one',indicator=True)
        assert pair_check['_merge'].eq('both').all()
        np.testing.assert_allclose(pair_check.change,pair_check.mom_change_pct,atol=1e-8)
        next_expected=pairs[['listing_id','month_date','change']].copy()
        next_expected.month_date=(pd.to_datetime(next_expected.month_date)-pd.offsets.MonthBegin(1)).dt.strftime('%Y-%m-%d')
        next_sql=pd.read_sql_query('SELECT listing_id,month_date,next_change_pct FROM vw_listing_rate_transitions WHERE next_change_pct IS NOT NULL',conn)
        next_check=next_expected.merge(next_sql,on=['listing_id','month_date'],how='outer',validate='one_to_one',indicator=True)
        assert next_check['_merge'].eq('both').all()
        np.testing.assert_allclose(next_check.change,next_check.next_change_pct,atol=1e-8)
        changes = results['04_historical_trends'].set_index(['month_date','room_type']).sort_index()
        grouped = pairs.groupby(['month_date','room_type']).change
        for col, values in [('matched_pairs',grouped.size()),('mean_change_pct',grouped.mean()),('median_change_pct',grouped.median())]:
            np.testing.assert_allclose(changes[col],values.sort_index(),atol=1e-8)
        def trimmed(s):
            values=np.sort(s.to_numpy()); k=int(len(values)*.05)
            return values[k:len(values)-k].mean()
        np.testing.assert_allclose(changes.trimmed_mean_5pct,grouped.apply(trimmed).sort_index(),atol=1e-8)
        # All segments, including missing bedrooms; independently check nearest-rank quartiles.
        sql_segments=pd.read_sql_query('SELECT * FROM vw_segment_pricing',conn)
        joined=f.merge(b,on=['listing_id','month_date'],validate='one_to_one')
        grouped=joined[joined.active].groupby(['month_date','room_type','bedrooms'],dropna=False)
        expected_seg=grouped.agg(active_listings=('listing_id','size'),median_adr_aed=('native_avg_daily_rate','median'),
                                 mean_adr_aed=('native_avg_daily_rate','mean'),
                                 benchmarked=('comparison_status',lambda s:s.eq('Eligible').sum()),
                                 review_candidates=('review_signal',lambda s:s.isin(['Review','Large deviation']).sum())).reset_index()
        seg=sql_segments.merge(expected_seg,on=['month_date','room_type','bedrooms'],suffixes=('','_expected'),how='outer',validate='one_to_one')
        for col in expected_seg.columns[3:]:
            np.testing.assert_allclose(seg[col],seg[col+'_expected'],atol=1e-8)
        for p,col in [(.25,'p25_adr_aed'),(.75,'p75_adr_aed')]:
            q=grouped.native_avg_daily_rate.apply(lambda s:np.sort(s.to_numpy())[int(np.ceil(len(s)*p))-1]).reset_index(name='q')
            q=sql_segments.merge(q,on=['month_date','room_type','bedrooms'],validate='one_to_one')
            np.testing.assert_allclose(q[col],q.q)
        cohort=results['04b_fixed_cohort']
        last=pd.Timestamp(f.month_date.max()); start=(last-pd.DateOffset(months=11)).strftime('%Y-%m-%d')
        recent=active[active.month_date.ge(start)]
        ids=recent.groupby('listing_id').month_date.nunique(); ids=ids[ids.eq(12)].index
        stable=recent[recent.listing_id.isin(ids)].groupby('month_date').native_avg_daily_rate.agg(['size','median','mean'])
        assert cohort.cohort_listings.eq(len(ids)).all()
        if len(ids):
            np.testing.assert_allclose(cohort.cohort_median_aed,stable['median'])
            np.testing.assert_allclose(cohort.cohort_mean_aed,stable['mean'])
        priority=pd.read_sql_query('SELECT * FROM vw_latest_review_priority',conn)
        latest=joined[joined.month_date.eq(f.month_date.max()) & joined.active].copy()
        dispersion=100*(latest.peer_p75_aed-latest.peer_p25_aed)/latest.peer_median_aed
        flagged=latest.review_signal.isin(['Review','Large deviation'])
        supported=flagged & latest.radius_km.eq(2) & latest.peer_count.ge(20) & dispersion.le(40)
        latest['expected_tier']=np.select([supported,flagged,latest.comparison_status.ne('Eligible')],[1,2,3],default=4)
        check=priority.merge(latest[['listing_id','expected_tier']],on='listing_id',how='outer',validate='one_to_one')
        assert check.priority_tier.eq(check.expected_tier).all()
        assert priority.review_order.is_unique and len(priority)==len(latest)
        plans=pd.read_sql_query((root/'sql/09_query_performance.sql').read_text(),conn)
        plans.to_csv(report/'query_plans.csv',index=False)
        # Measure a real month aggregation with and without the existing month index.
        # INDEXED BY/NOT INDEXED compare access paths without altering the user's DB.
        performance=[]
        for strategy in ('NOT INDEXED','INDEXED BY idx_fact_month'):
            query=f'SELECT SUM(native_revenue) FROM fact_listing_month {strategy} WHERE month_date=? AND active=1'
            durations=[]
            for _ in range(11):
                tick=time.perf_counter(); conn.execute(query,(f.month_date.max(),)).fetchone()
                durations.append((time.perf_counter()-tick)*1000)
            performance.append({'strategy':strategy,'median_ms_10_warm_runs':statistics.median(durations[1:]),
                                'plan':conn.execute('EXPLAIN QUERY PLAN '+query,(f.month_date.max(),)).fetchall()})
        for name,frame in results.items():frame.to_csv(report/(name+'.csv'),index=False)
        audit={'sql_checks':validation.to_dict('records'),'source_rows':len(f),'adjacent_active_pairs':len(pairs),
               'monthly_metrics_reconciled':len(market),'segment_groups_reconciled':len(sql_segments),
               'fixed_12month_cohort':len(ids),'priority_rows_reconciled':len(priority),
               'query_seconds':timings,'performance':performance,'sqlite_version':sqlite3.sqlite_version,
               'python_version':platform.python_version(),'pandas_version':pd.__version__,
               'limitations':'Warm local measurements, not a production benchmark. Cohort has survivor bias.'}
        (report/'analysis_validation.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    return audit


if __name__=='__main__':
    print(json.dumps(run(),indent=2))

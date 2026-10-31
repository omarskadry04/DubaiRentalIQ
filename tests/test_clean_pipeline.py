"""Execute real preparation, matching and SQL code with private-data-free fixtures."""
import contextlib
import importlib.util
import io
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'src'/name)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def sources(root):
    raw=root/'data/raw';raw.mkdir(parents=True)
    rows=[]
    for month in ('2025-01-01','2025-02-01','2025-03-01'):
        for i in range(13):
            if month=='2025-02-01' and i==0:continue  # deliberate time-series gap
            rows.append(dict(listing_id=str(9000000000000000000+i),month_date=month,active=True,
                listing_type='Apartment',room_type='entire_home',latitude=25.,longitude=55.,bedrooms=1.,
                neighborhood=None,available_days=pd.Timestamp(month).days_in_month,unavailable_days=0,
                occupancy=.5,native_avg_daily_rate=100.+i*10,native_revenue=1000.,native_revpar=30.,currency='AED',
                country='United Arab Emirates',avg_daily_rate=30.,revenue=300.,revpar=10.))
    a=pd.DataFrame(rows);a.to_csv(raw/'past_rates.csv',index=False);a.to_parquet(raw/'past_rates.parquet',index=False)
    b=a.assign(host_id='0001234567890123456789',guests=2,beds=1,baths=1.,num_reviews=5,star_rating=4.5,superhost=True,property_type='Apartment')
    b.to_csv(raw/'listings_monthly.csv',index=False)
    listing=b.sort_values('month_date').drop_duplicates('listing_id',keep='last').copy()
    mapper={'month_date':'date','avg_daily_rate':'rate_avg','native_avg_daily_rate':'native_rate_avg','revpar':'rev_par','native_revpar':'native_rev_par'}
    fields=['month_date','active','available_days','unavailable_days','occupancy','native_avg_daily_rate','native_revenue','native_revpar','avg_daily_rate','revenue','revpar']
    months=[]
    for key in listing.listing_id:
        frame=a[a.listing_id.eq(key)][fields].rename(columns=mapper).assign(native_booked_rate_avg=90.)
        months.append(frame.to_dict('records'))
    listing['months']=months
    listing.drop(columns='month_date').to_parquet(raw/'listings.parquet',index=False)


class CleanStart(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT, prefix='.test_');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);sources(self.root)
        self.prep=load('01_validate_and_prepare.py');self.peer=load('02_build_peer_benchmarks.py');self.db=load('03_build_powerbi_exports.py')
        self.out=self.root/'data/processed'; self.report=self.root/'reports'
        self.prep.RAW=self.root/'data/raw';self.prep.OUT=self.out;self.prep.REPORT=self.report
        self.peer.OUT=self.out;self.peer.REPORT=self.report
        self.db.PROCESSED=self.out;self.db.EXPORTS=self.root/'powerbi/data';self.db.DB_FILE=self.out/'dubai_rentals.sqlite'

    def pipeline(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.prep.run();self.peer.run();return self.db.run()

    def test_clean_end_to_end_and_advanced_sql(self):
        audit=self.pipeline()
        self.assertEqual(audit['foreign_key_violations'],0)
        host=pd.read_csv(self.out/'dim_listing.csv',dtype={'host_id':str})
        self.assertTrue(host.host_id.eq('0001234567890123456789').all())
        shutil.copytree(ROOT/'sql',self.root/'sql')
        analysis=load('05_run_sql_analysis.py').run(self.root)
        self.assertTrue(all(r['violations']==0 for r in analysis['sql_checks']))

    def test_invalid_source_preserves_prepared_outputs(self):
        self.pipeline();before=(self.out/'fact_listing_month.csv').read_bytes()
        p=self.prep.RAW/'past_rates.csv';frame=pd.read_csv(p,dtype={'listing_id':str});frame.loc[0,'month_date']=None;frame.to_csv(p,index=False)
        with self.assertRaises((ValueError,AssertionError)): self.prep.run()
        self.assertEqual(before,(self.out/'fact_listing_month.csv').read_bytes())

    def test_benchmark_generation_failure_preserves_both_files(self):
        self.pipeline();names=['fact_peer_benchmark.csv','peer_examples_latest.csv']
        before={n:(self.out/n).read_bytes() for n in names}
        with patch.object(self.peer,'haversine_km',side_effect=RuntimeError('injected calculation failure')):
            with self.assertRaises(RuntimeError):self.peer.run()
        self.assertEqual(before,{n:(self.out/n).read_bytes() for n in names})

    def test_failed_database_build_preserves_database_and_exports(self):
        self.pipeline();before=self.db.DB_FILE.read_bytes()
        exports={p.name:p.read_bytes() for p in self.db.EXPORTS.glob('*.csv')}
        with patch.object(self.db,'_validate',side_effect=AssertionError('injected validation failure')):
            with self.assertRaises(AssertionError):self.db.run()
        self.assertEqual(before,self.db.DB_FILE.read_bytes())
        self.assertEqual(exports,{p.name:p.read_bytes() for p in self.db.EXPORTS.glob('*.csv')})

    def test_missing_inputs_fail_without_skipping(self):
        with self.assertRaises(FileNotFoundError):self.db.run()
        with self.assertRaises(FileNotFoundError):self.peer.run()

    def test_stale_generation_is_rejected(self):
        self.pipeline()
        with (self.out/'fact_peer_benchmark.csv').open('a') as stream:stream.write('\n')
        with self.assertRaises(ValueError):self.db.run()


class MatchingFixtures(unittest.TestCase):
    def test_production_matching_boundaries_and_isolation(self):
        mod=load('02_build_peer_benchmarks.py')
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.test_') as temp:
            mod.OUT=Path(temp);mod.REPORT=Path(temp)
            for distance,expected_radius,expected_count in [(2.,2,10),(3.,5,10),(5.,5,10),(5.01,5,9)]:
                rows=[]
                for i,km in enumerate([0.]+[1.]*9+[distance]):
                    rows.append(dict(listing_id=str(i),month_date='2025-01-01',active=True,room_type='entire_home',
                       bedrooms=1.,latitude=25.+np.rad2deg(km/6371.0088),longitude=55.,native_avg_daily_rate=100.+i,occupancy=.5))
                # Same coordinates but inadmissible: inactive, other month, type, beds, missing beds, bad rate.
                for i,change in enumerate([{'active':False},{'month_date':'2025-02-01'},{'room_type':'private_room'},
                                          {'bedrooms':2.},{'bedrooms':None},{'native_avg_daily_rate':0.}]):
                    rows.append({**rows[0],'listing_id':'x'+str(i),**change})
                pd.DataFrame(rows).to_csv(mod.OUT/'fact_listing_month.csv',index=False)
                with contextlib.redirect_stdout(io.StringIO()):bench,examples=mod.run()
                row=bench[bench.listing_id.eq('0')].iloc[0]
                self.assertEqual((row.radius_km,row.peer_count),(expected_radius,expected_count))
                if expected_count==10:self.assertEqual(row.peer_median_aed,105.5)
                else:self.assertTrue(pd.isna(row.peer_median_aed))
                self.assertFalse(examples.listing_id.eq(examples.peer_listing_id).any())

    def test_exact_review_thresholds(self):
        mod=load('02_build_peer_benchmarks.py')
        for v,label in [(20,'Review'),(-20,'Review'),(35,'Large deviation'),(-35,'Large deviation'),(19.999,'Within threshold')]:
            self.assertEqual(mod.classify(v),label)
        self.assertEqual(mod.classify(100*(1.2-1)),'Review')

    def test_recoverable_promotion_rollback(self):
        mod=load('pipeline_io.py')
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.test_') as temp:
            root=Path(temp);old=root/'old';old.write_text('original');stage=root/'staged';stage.write_text('new')
            with self.assertRaises(FileNotFoundError):mod.promote({old:stage,root/'other':root/'absent'})
            self.assertEqual(old.read_text(),'original')


if __name__=='__main__':unittest.main()

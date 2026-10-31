"""Checks generated outputs when source-derived tables are available locally."""
import unittest
from pathlib import Path
import pandas as pd
import numpy as np

P=Path(__file__).resolve().parents[1]/'data/processed'

@unittest.skipUnless((P/'fact_peer_benchmark.csv').exists(), 'Run pipeline first')
class TestDataModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f=pd.read_csv(P/'fact_listing_month.csv',dtype={'listing_id':str})
        cls.b=pd.read_csv(P/'fact_peer_benchmark.csv',dtype={'listing_id':str})
        cls.e=pd.read_csv(P/'peer_examples_latest.csv',dtype={'listing_id':str,'peer_listing_id':str})
    def test_unique_grain(self):
        self.assertGreater(len(self.f),0)
        self.assertFalse(self.f[['listing_id','month_date']].duplicated().any())
        self.assertEqual(len(self.b),len(self.f))
        self.assertFalse(self.b[['listing_id','month_date']].duplicated().any())
    def test_valid_peer_premium_and_suppression(self):
        eligible=self.b[self.b.comparison_status=='Eligible']
        bad=self.b[self.b.comparison_status!='Eligible']
        self.assertTrue((eligible.peer_count>=10).all())
        self.assertTrue(bad.premium_pct.isna().all())
        d=eligible.merge(self.f[['listing_id','month_date','native_avg_daily_rate']],on=['listing_id','month_date'],validate='one_to_one')
        expected=100*(d.native_avg_daily_rate/d.peer_median_aed-1)
        self.assertTrue(np.allclose(d.premium_pct,expected))
    def test_peer_examples_month_and_ids(self):
        self.assertTrue((self.e.month_date==self.f.month_date.max()).all())
        self.assertFalse((self.e.listing_id==self.e.peer_listing_id).any())
        self.assertTrue((self.e.distance_km<=5.001).all())
        self.assertTrue((self.e.groupby('listing_id').size()<=5).all())
        a=self.f[self.f.month_date==self.f.month_date.max()][['listing_id','room_type','bedrooms']]
        pair=self.e.merge(a,on='listing_id',validate='many_to_one')
        pair=pair.merge(a, left_on='peer_listing_id',right_on='listing_id',suffixes=('_subject','_peer'),validate='many_to_one')
        self.assertTrue((pair.room_type_subject==pair.room_type_peer).all())
        self.assertTrue((pair.bedrooms_subject==pair.bedrooms_peer).all())

if __name__=='__main__':unittest.main()

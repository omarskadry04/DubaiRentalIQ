"""Monthly peer groups: 2 km Haversine; fall back to 5 km; require >=10 peers."""
from pathlib import Path
import runpy
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/processed';REPORT=ROOT/'reports'
EARTH_KM=6371.0088
MIN_PEERS=10
PRIMARY_RADIUS_KM=2
FALLBACK_RADIUS_KM=5
DISTANCE_TOL_KM=1e-7
publish_frames = runpy.run_path(str(Path(__file__).with_name('pipeline_io.py')))['publish_frames']

def classify(premium):
    """Nine decimal percent precision makes exact 20/35% boundaries stable."""
    value = round(abs(float(premium)), 9)
    return 'Large deviation' if value >= 35 else ('Review' if value >= 20 else 'Within threshold')

def xyz_from_degrees(lat,lon):
    lat,lon=np.deg2rad(np.asarray(lat,dtype=float)),np.deg2rad(np.asarray(lon,dtype=float))
    return np.column_stack([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)])

def chord(km): return 2*np.sin(km/(2*EARTH_KM))

def haversine_km(lat1,lon1,lat2,lon2):
    la1,lo1=np.deg2rad(lat1),np.deg2rad(lon1)
    la2,lo2=np.deg2rad(lat2),np.deg2rad(lon2)
    s=np.sin((la2-la1)/2)**2+np.cos(la1)*np.cos(la2)*np.sin((lo2-lo1)/2)**2
    return 2*EARTH_KM*np.arcsin(np.sqrt(np.clip(s,0,1)))

def eligibility(d):
    bed=pd.to_numeric(d.bedrooms,errors='coerce')
    return (d.active.astype(str).str.lower().isin(['true','1'])
        & d.room_type.notna() & bed.notna() & (bed>=0) & (bed%1==0)
        & d.latitude.between(24.5,25.6) & d.longitude.between(54.5,56)
        & np.isfinite(d.native_avg_daily_rate) & (d.native_avg_daily_rate>0))

def run():
    OUT.mkdir(parents=True,exist_ok=True); REPORT.mkdir(parents=True,exist_ok=True)
    d=pd.read_csv(OUT/'fact_listing_month.csv',dtype={'listing_id':str},low_memory=False)
    if d.empty or d[['listing_id','month_date']].isna().any().any() or d.duplicated(['listing_id','month_date']).any():
        raise ValueError('Benchmark input requires nonempty unique listing-month keys')
    d['eligible']=eligibility(d)
    latest=d.month_date.max()
    out=[];nearest=[]
    for date,month in d.groupby('month_date',sort=True):
        month=month.copy()
        # one output record per source month-row
        results={i:dict(listing_id=row['listing_id'],month_date=date,peer_count=0,radius_km=np.nan,
                        peer_median_aed=np.nan,peer_p25_aed=np.nan,peer_p75_aed=np.nan,
                        peer_median_estimated_occupancy=np.nan,premium_pct=np.nan,
                        estimated_occupancy_gap_pp=np.nan,comparison_status='Ineligible',
                        review_signal='Unassessed',confidence_label='Unassessed')
                 for i,row in month.iterrows()}
        eligible=month[month.eligible].copy()
        for (room,bed),grp in eligible.groupby(['room_type','bedrooms'],dropna=False):
            # cKDTree candidate selection in Earth-centered 3D, exact Haversine for final radius.
            idx=grp.index.to_numpy()
            coords=grp[['latitude','longitude']].to_numpy(float)
            pts=xyz_from_degrees(coords[:,0],coords[:,1])
            tree=cKDTree(pts)
            candidates_2=tree.query_ball_point(pts,r=chord(PRIMARY_RADIUS_KM+DISTANCE_TOL_KM)+1e-12,return_sorted=False)
            rate=grp.native_avg_daily_rate.to_numpy(float)
            occup=grp.occupancy.to_numpy(float)
            ids=grp.listing_id.to_numpy(str)
            for j,group_index in enumerate(idx):
                cand=np.asarray([p for p in candidates_2[j] if p!=j],dtype=int)
                dist=haversine_km(coords[j,0],coords[j,1],coords[cand,0],coords[cand,1])
                peers=cand[dist<=PRIMARY_RADIUS_KM+1e-7]
                dists=dist[dist<=PRIMARY_RADIUS_KM+1e-7]
                radius=PRIMARY_RADIUS_KM
                if len(peers)<MIN_PEERS:
                    cand=np.asarray([p for p in tree.query_ball_point(pts[j],r=chord(FALLBACK_RADIUS_KM+DISTANCE_TOL_KM)+1e-12) if p!=j],dtype=int)
                    dist=haversine_km(coords[j,0],coords[j,1],coords[cand,0],coords[cand,1])
                    peers=cand[dist<=FALLBACK_RADIUS_KM+1e-7]
                    dists=dist[dist<=FALLBACK_RADIUS_KM+1e-7]
                    radius=FALLBACK_RADIUS_KM
                rec=results[group_index]
                rec.update(peer_count=len(peers),radius_km=radius)
                if len(peers)<MIN_PEERS:
                    rec['comparison_status']='Insufficient peers'
                    rec['confidence_label']='Insufficient'
                    continue
                pvals=rate[peers]
                med=float(np.median(pvals))
                prem=100*(rate[j]/med-1)
                occupancy_gap=100*(occup[j]-np.median(occup[peers]))
                status=classify(prem)
                rec.update(peer_median_aed=med,peer_p25_aed=float(np.quantile(pvals,.25)),
                    peer_p75_aed=float(np.quantile(pvals,.75)),
                    peer_median_estimated_occupancy=float(np.median(occup[peers])),
                    premium_pct=float(prem),estimated_occupancy_gap_pp=float(occupancy_gap),
                    comparison_status='Eligible',review_signal=status,
                    confidence_label='Higher peer coverage' if len(peers)>=20 and radius==2 else 'Moderate peer coverage')
                if date==latest:
                    close=np.lexsort((ids[peers], dists))[:5]
                    for k in close:
                        p=peers[k]
                        nearest.append(dict(listing_id=ids[j],month_date=date,peer_listing_id=ids[p],
                            distance_km=round(float(dists[k]),3),peer_adr_aed=float(rate[p]),
                            peer_room_type=room,peer_bedrooms=int(bed),peer_estimated_occupancy=float(occup[p])))
        out.extend(results.values())
        print(date,'eligible',len(eligible),'benchmarked',sum(v['comparison_status']=='Eligible' for v in results.values()))
    bench=pd.DataFrame(out)
    assert not bench[['listing_id','month_date']].duplicated().any()
    assert len(bench)==len(d)
    assert bench.loc[bench.comparison_status!='Eligible','premium_pct'].isna().all()
    peers=pd.DataFrame(nearest,columns=['listing_id','month_date','peer_listing_id','distance_km','peer_adr_aed',
                                       'peer_room_type','peer_bedrooms','peer_estimated_occupancy'])
    publish_frames(dict(fact_peer_benchmark=bench,peer_examples_latest=peers), OUT,
                   'benchmark_manifest.json', sources=[OUT/'fact_listing_month.csv'])
    latest_b=bench[bench.month_date==latest]
    summary={
        'month':latest,'active_sample':int(d[(d.month_date==latest)&d.active].shape[0]),
        'eligible_for_matching':int(d[(d.month_date==latest)&d.eligible].shape[0]),
        'with_valid_benchmark':int((latest_b.comparison_status=='Eligible').sum()),
        'insufficient_peers':int((latest_b.comparison_status=='Insufficient peers').sum()),
        'review_signals':latest_b.review_signal.value_counts().to_dict(),
        'peer_examples_rows':int(len(peers))
    }
    import json
    (REPORT/'benchmark_latest_summary.json').write_text(json.dumps(summary,indent=2))
    print('PASS benchmark',summary)
    return bench,peers

if __name__=='__main__':run()

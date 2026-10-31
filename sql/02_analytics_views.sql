-- All figures refer only to the AirROI dataset sample, not the Dubai market.
DROP VIEW IF EXISTS vw_latest_price_review_queue;
CREATE VIEW vw_latest_price_review_queue AS
SELECT f.listing_id, f.month_date, f.room_type, f.bedrooms,
       f.latitude, f.longitude, f.native_avg_daily_rate AS subject_adr_aed,
       ROUND(f.occupancy*100, 1) AS subject_estimated_occupancy_pct,
       ROUND(b.peer_median_aed, 1) AS peer_median_aed,
       ROUND(b.premium_pct, 1) AS premium_pct,
       ROUND(b.estimated_occupancy_gap_pp, 1) AS est_occupancy_gap_pp,
       b.peer_count, b.radius_km, b.review_signal, b.confidence_label
FROM fact_peer_benchmark b
JOIN fact_listing_month f
 ON b.listing_id=f.listing_id AND b.month_date=f.month_date
WHERE f.month_date = (SELECT MAX(month_date) FROM fact_listing_month)
 AND b.comparison_status='Eligible'
 AND b.review_signal IN ('Review','Large deviation');

DROP VIEW IF EXISTS vw_monthly_coverage_and_performance;
CREATE VIEW vw_monthly_coverage_and_performance AS
SELECT c.month_date,c.observed_listings,c.active_listings,
       ROUND(c.coverage_change_pct,2) AS coverage_change_pct,
       ROUND(c.median_active_adr_aed,1) AS median_active_adr_aed,
       ROUND(100*c.median_active_estimated_occupancy,1) AS median_est_occupancy_pct,
       ROUND(c.neighborhood_missing_pct,1) AS neighborhood_missing_pct,
       ROUND(c.bedrooms_missing_pct,1) AS bedrooms_missing_pct,
       c.same_listing_prev_month
FROM fact_coverage_month c;

DROP VIEW IF EXISTS vw_segment_monthly_rates;
CREATE VIEW vw_segment_monthly_rates AS
SELECT month_date,room_type,bedrooms,
       COUNT(*) AS active_sample_listings,
       ROUND(AVG(native_avg_daily_rate),1) AS mean_adr_aed,
       ROUND(AVG(occupancy)*100,1) AS mean_est_occupancy_pct,
       ROUND(SUM(native_revenue),1) AS sum_modeled_revenue_aed
FROM fact_listing_month
WHERE active=1 AND bedrooms IS NOT NULL
GROUP BY month_date,room_type,bedrooms;
-- Weighted/mean rates are descriptive of observed rows; not market rates.

DROP VIEW IF EXISTS vw_pairwise_same_listing_month;
CREATE VIEW vw_pairwise_same_listing_month AS
WITH tracked AS (
 SELECT listing_id,month_date,active,native_avg_daily_rate,
        LAG(month_date) OVER (PARTITION BY listing_id ORDER BY month_date) AS prev_date,
        LAG(native_avg_daily_rate) OVER (PARTITION BY listing_id ORDER BY month_date) AS prev_rate,
        LAG(active) OVER (PARTITION BY listing_id ORDER BY month_date) AS prev_active
 FROM fact_listing_month
)
SELECT listing_id,month_date,native_avg_daily_rate,prev_rate,
       ROUND((native_avg_daily_rate/NULLIF(prev_rate,0)-1)*100,2) AS mom_rate_change_pct
FROM tracked
WHERE active=1 AND prev_active=1
AND prev_date=DATE(month_date,'-1 month');
-- Do not confuse this matched-listing price-change subset with changing sample-wide composition.

DROP VIEW IF EXISTS vw_latest_benchmark_status;
CREATE VIEW vw_latest_benchmark_status AS
SELECT comparison_status,confidence_label,review_signal,COUNT(*) AS listing_count
FROM fact_peer_benchmark
WHERE month_date=(SELECT MAX(month_date) FROM fact_listing_month)
GROUP BY comparison_status,confidence_label,review_signal;

-- Recompute monthly metrics from facts: does not simply echo the Python coverage table.
DROP VIEW IF EXISTS vw_market_monthly;
CREATE VIEW vw_market_monthly AS
WITH ordered AS (
 SELECT month_date,native_avg_daily_rate AS rate,occupancy,
        ROW_NUMBER() OVER(PARTITION BY month_date ORDER BY native_avg_daily_rate,listing_id) AS rn,
        ROW_NUMBER() OVER(PARTITION BY month_date ORDER BY occupancy,listing_id) AS occ_rn,
        COUNT(*) OVER(PARTITION BY month_date) AS n
 FROM fact_listing_month WHERE active=1
), medians AS (
 SELECT month_date,
        AVG(CASE WHEN rn IN ((n+1)/2,(n+2)/2) THEN rate END) AS median_active_adr_aed,
        AVG(CASE WHEN occ_rn IN ((n+1)/2,(n+2)/2) THEN occupancy END) AS median_estimated_occupancy
 FROM ordered GROUP BY month_date
), totals AS (
 SELECT month_date,COUNT(*) AS observed_listings,SUM(active) AS active_listings,
        AVG(CASE WHEN active=1 THEN native_avg_daily_rate END) AS mean_active_adr_aed,
        SUM(CASE WHEN active=1 THEN native_revenue END) AS active_estimated_revenue_aed,
        SUM(CASE WHEN active=1 AND occupancy=0 THEN 1 ELSE 0 END) AS active_zero_occupancy
 FROM fact_listing_month GROUP BY month_date
)
SELECT t.*,m.median_active_adr_aed,m.median_estimated_occupancy,
       100.0*(observed_listings*1.0/NULLIF(LAG(observed_listings) OVER(ORDER BY t.month_date),0)-1)
          AS coverage_change_pct
FROM totals t LEFT JOIN medians m ON t.month_date=m.month_date;

-- Window before filtering: missing/inactive months must not be bridged.
DROP VIEW IF EXISTS vw_listing_rate_transitions;
CREATE VIEW vw_listing_rate_transitions AS
WITH history AS (
 SELECT listing_id,month_date,room_type,bedrooms,active,native_avg_daily_rate,
        LAG(month_date) OVER w AS prev_month,
        LAG(active) OVER w AS prev_active,
        LAG(native_avg_daily_rate) OVER w AS prev_rate,
        LEAD(month_date) OVER w AS next_month,
        LEAD(active) OVER w AS next_active,
        LEAD(native_avg_daily_rate) OVER w AS next_rate
 FROM fact_listing_month
 WINDOW w AS (PARTITION BY listing_id ORDER BY month_date)
)
SELECT *,
 CASE WHEN active=1 AND prev_active=1 AND prev_month=DATE(month_date,'-1 month') AND prev_rate>0
      THEN 100.0*(native_avg_daily_rate/prev_rate-1) END AS mom_change_pct,
 CASE WHEN active=1 AND next_active=1 AND next_month=DATE(month_date,'+1 month') AND native_avg_daily_rate>0
      THEN 100.0*(next_rate/native_avg_daily_rate-1) END AS next_change_pct
FROM history;

-- A fixed 12-month survivor cohort (active in EVERY month). Retention is explicit.
DROP VIEW IF EXISTS vw_fixed_cohort_monthly;
CREATE VIEW vw_fixed_cohort_monthly AS
WITH bounds AS (SELECT MAX(month_date) AS last_month FROM fact_listing_month),
cohort AS (
 SELECT listing_id FROM fact_listing_month,bounds
 WHERE month_date BETWEEN DATE(last_month,'-11 months') AND last_month AND active=1
 GROUP BY listing_id HAVING COUNT(DISTINCT month_date)=12
), ranked AS (
 SELECT f.month_date,f.native_avg_daily_rate,
 ROW_NUMBER() OVER(PARTITION BY f.month_date ORDER BY f.native_avg_daily_rate,f.listing_id) AS rn,
 COUNT(*) OVER(PARTITION BY f.month_date) AS n
 FROM fact_listing_month f JOIN cohort USING(listing_id) CROSS JOIN bounds
 WHERE f.month_date BETWEEN DATE(last_month,'-11 months') AND last_month
), monthly AS (
 SELECT month_date,COUNT(*) AS cohort_listings,
 AVG(native_avg_daily_rate) AS cohort_mean_aed,
 AVG(CASE WHEN rn IN ((n+1)/2,(n+2)/2) THEN native_avg_daily_rate END) AS cohort_median_aed
 FROM ranked GROUP BY month_date
)
SELECT m.month_date,m.active_listings,COALESCE(c.cohort_listings,0) AS cohort_listings,
       100.0*COALESCE(c.cohort_listings,0)/NULLIF(m.active_listings,0) AS retained_active_pct,
       c.cohort_mean_aed,c.cohort_median_aed,m.median_active_adr_aed AS full_sample_median_aed
FROM vw_market_monthly m CROSS JOIN bounds LEFT JOIN monthly c ON m.month_date=c.month_date
WHERE m.month_date BETWEEN DATE(last_month,'-11 months') AND last_month;

-- Unknown bedrooms are retained as a separate NULL segment. No dimension snapshot leakage.
-- Quartiles here use nearest-rank (ceil(p*n)); Python PEER quartiles use linear interpolation.
DROP VIEW IF EXISTS vw_segment_pricing;
CREATE VIEW vw_segment_pricing AS
WITH ordered AS (
 SELECT f.*, b.comparison_status,b.review_signal,b.radius_km,
 ROW_NUMBER() OVER(PARTITION BY f.month_date,f.room_type,f.bedrooms
                   ORDER BY f.native_avg_daily_rate,f.listing_id) AS rn,
 COUNT(*) OVER(PARTITION BY f.month_date,f.room_type,f.bedrooms) AS n
 FROM fact_listing_month f JOIN fact_peer_benchmark b USING(listing_id,month_date)
 WHERE active=1
)
SELECT month_date,room_type,bedrooms,COUNT(*) AS active_listings,
 AVG(native_avg_daily_rate) AS mean_adr_aed,
 AVG(CASE WHEN rn IN ((n+1)/2,(n+2)/2) THEN native_avg_daily_rate END) AS median_adr_aed,
 MAX(CASE WHEN rn=(n+3)/4 THEN native_avg_daily_rate END) AS p25_adr_aed,
 MAX(CASE WHEN rn=(3*n+3)/4 THEN native_avg_daily_rate END) AS p75_adr_aed,
 AVG(occupancy) AS mean_estimated_occupancy,
 SUM(native_revenue) AS estimated_revenue_aed,
 SUM(comparison_status='Eligible') AS benchmarked,
 SUM(review_signal IN ('Review','Large deviation')) AS review_candidates,
 SUM(comparison_status='Eligible' AND radius_km=5) AS fallback_benchmarks,
 100.0*SUM(review_signal IN ('Review','Large deviation'))/
    NULLIF(SUM(comparison_status='Eligible'),0) AS review_share_of_benchmarked_pct
FROM ordered GROUP BY month_date,room_type,bedrooms;

-- Priority is an explicit operational heuristic, not a calibrated prediction.
-- Geography/dispersion concerns go to comparability review, not a price-action queue.
DROP VIEW IF EXISTS vw_latest_review_priority;
CREATE VIEW vw_latest_review_priority AS
WITH signals AS (
 SELECT f.listing_id,f.month_date,f.active,f.room_type,f.bedrooms,
        f.native_avg_daily_rate AS subject_adr_aed,b.comparison_status,b.review_signal,
        b.premium_pct,b.peer_count,b.radius_km,
        100.0*(b.peer_p75_aed-b.peer_p25_aed)/NULLIF(b.peer_median_aed,0) AS peer_iqr_pct
 FROM fact_listing_month f JOIN fact_peer_benchmark b USING(listing_id,month_date)
 WHERE f.month_date=(SELECT MAX(month_date) FROM fact_listing_month) AND f.active=1
), labeled AS (
 SELECT listing_id,month_date,room_type,bedrooms,subject_adr_aed,
        comparison_status,review_signal,premium_pct,peer_count,radius_km,peer_iqr_pct,
 CASE WHEN comparison_status!='Eligible' THEN 'Data/peer coverage investigation'
      WHEN review_signal='Within threshold' THEN 'Monitor'
      WHEN radius_km=2 AND peer_count>=20 AND peer_iqr_pct<=40 THEN 'Pricing Review Candidate'
      ELSE 'Comparability review first' END AS action,
 CASE WHEN comparison_status!='Eligible' THEN NULL
      WHEN premium_pct>0 THEN 'Above Peer Benchmark'
      WHEN premium_pct<0 THEN 'Below Peer Benchmark' ELSE 'At Peer Benchmark' END AS direction,
 CASE WHEN review_signal IN ('Review','Large deviation') AND radius_km=2 AND peer_count>=20
           AND peer_iqr_pct<=40 THEN 1
      WHEN review_signal IN ('Review','Large deviation') THEN 2
      WHEN comparison_status!='Eligible' THEN 3 ELSE 4 END AS priority_tier
 FROM signals
)
SELECT *,DENSE_RANK() OVER(PARTITION BY priority_tier ORDER BY ABS(premium_pct) DESC) AS deviation_rank,
 ROW_NUMBER() OVER(ORDER BY priority_tier,ABS(premium_pct) DESC,listing_id) AS review_order
FROM labeled;

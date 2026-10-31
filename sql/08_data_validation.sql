-- Every returned violations value must equal zero. Executed/asserted by 05_run_sql_analysis.py.
SELECT 'missing benchmark keys' AS check_name,COUNT(*) AS violations
FROM fact_listing_month f LEFT JOIN fact_peer_benchmark b USING(listing_id,month_date)
WHERE b.listing_id IS NULL
UNION ALL
SELECT 'foreign keys',COUNT(*) FROM pragma_foreign_key_check
UNION ALL
SELECT 'fact duplicate keys',COUNT(*) FROM (
 SELECT listing_id,month_date FROM fact_listing_month GROUP BY 1,2 HAVING COUNT(*)>1)
UNION ALL
SELECT 'monthly coverage',COUNT(*) FROM vw_market_monthly m
LEFT JOIN fact_coverage_month c USING(month_date)
WHERE c.month_date IS NULL OR m.observed_listings IS NOT c.observed_listings
 OR m.active_listings IS NOT c.active_listings
 OR ABS(m.median_active_adr_aed-c.median_active_adr_aed)>1e-7
 OR ABS(m.median_estimated_occupancy-c.median_active_estimated_occupancy)>1e-7
UNION ALL
SELECT 'month keys',COUNT(*) FROM fact_listing_month WHERE month_date IS NOT DATE(month_date,'start of month')
UNION ALL
SELECT 'calendar continuity',COUNT(*) FROM (
 SELECT month_date,LAG(month_date) OVER(ORDER BY month_date) AS prior FROM dim_month)
WHERE prior IS NOT NULL AND prior!=DATE(month_date,'-1 month')
UNION ALL
SELECT 'required metrics',COUNT(*) FROM fact_listing_month
WHERE currency IS NOT 'AED' OR occupancy IS NULL OR occupancy NOT BETWEEN 0 AND 1
 OR native_avg_daily_rate IS NULL OR native_avg_daily_rate<0
 OR native_revenue IS NULL OR native_revenue<0 OR native_revpar IS NULL OR native_revpar<0
 OR available_days+unavailable_days!=CAST(STRFTIME('%d',DATE(month_date,'+1 month','-1 day')) AS INTEGER)
UNION ALL
SELECT 'peer suppression/classification',COUNT(*) FROM fact_peer_benchmark
WHERE comparison_status IS NULL OR review_signal IS NULL
 OR comparison_status NOT IN ('Eligible','Insufficient peers','Ineligible')
 OR (comparison_status='Eligible' AND (peer_count<10 OR peer_median_aed IS NULL OR peer_median_aed<=0
 OR radius_km IS NULL OR radius_km NOT IN (2,5) OR premium_pct IS NULL
 OR peer_count IS NULL OR peer_p25_aed IS NULL OR peer_p75_aed IS NULL
 OR peer_p25_aed>peer_median_aed OR peer_p75_aed<peer_median_aed
 OR review_signal!=CASE WHEN ROUND(ABS(premium_pct),9)>=35 THEN 'Large deviation'
                       WHEN ROUND(ABS(premium_pct),9)>=20 THEN 'Review' ELSE 'Within threshold' END))
 OR (comparison_status!='Eligible' AND (premium_pct IS NOT NULL OR peer_median_aed IS NOT NULL OR review_signal!='Unassessed'))
 OR (comparison_status='Ineligible' AND (peer_count IS NOT 0 OR radius_km IS NOT NULL))
 OR (comparison_status='Insufficient peers' AND (peer_count IS NULL OR peer_count NOT BETWEEN 0 AND 9 OR radius_km IS NOT 5))
UNION ALL
SELECT 'premium arithmetic',COUNT(*) FROM fact_peer_benchmark b JOIN fact_listing_month f USING(listing_id,month_date)
WHERE b.comparison_status='Eligible' AND ABS(b.premium_pct-100.0*(f.native_avg_daily_rate/b.peer_median_aed-1))>1e-7
UNION ALL
SELECT 'example self/latest/radius',COUNT(*) FROM peer_examples_latest e
JOIN fact_peer_benchmark b USING(listing_id,month_date)
WHERE e.listing_id=e.peer_listing_id OR e.month_date!=(SELECT MAX(month_date) FROM fact_listing_month)
 OR e.distance_km>b.radius_km+.001 OR b.comparison_status!='Eligible'
UNION ALL
SELECT 'example maximum five',COUNT(*) FROM (
 SELECT listing_id,month_date FROM peer_examples_latest GROUP BY 1,2 HAVING COUNT(*)>5);

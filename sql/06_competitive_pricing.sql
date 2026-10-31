-- All observed rows are the denominator, including inactive/ineligible subjects.
SELECT f.month_date,f.room_type,f.bedrooms,COUNT(*) AS observed,
 SUM(f.active) AS active,
 SUM(b.comparison_status='Eligible') AS benchmarked,
 SUM(b.comparison_status='Insufficient peers') AS insufficient_peers,
 SUM(b.comparison_status='Ineligible') AS ineligible,
 SUM(b.review_signal IN ('Review','Large deviation') AND b.premium_pct>0) AS above_peer_candidates,
 SUM(b.review_signal IN ('Review','Large deviation') AND b.premium_pct<0) AS below_peer_candidates,
 SUM(b.comparison_status='Eligible' AND b.radius_km=5) AS fallback_benchmarks,
 100.0*SUM(b.comparison_status='Eligible')/NULLIF(SUM(f.active),0) AS active_benchmark_coverage_pct
FROM fact_listing_month f JOIN fact_peer_benchmark b USING(listing_id,month_date)
WHERE f.month_date=(SELECT MAX(month_date) FROM fact_listing_month)
GROUP BY f.month_date,f.room_type,f.bedrooms ORDER BY observed DESC,room_type,bedrooms;

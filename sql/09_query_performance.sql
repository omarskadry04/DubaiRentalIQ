-- Indexed month lookup and composite-key join. Timings are generated on the actual DB.
EXPLAIN QUERY PLAN
SELECT f.listing_id,f.native_avg_daily_rate,b.premium_pct
FROM fact_listing_month f JOIN fact_peer_benchmark b USING(listing_id,month_date)
WHERE f.month_date=(SELECT MAX(month_date) FROM fact_listing_month)
 AND b.comparison_status='Eligible';

-- Aggregate action workload; inspect listing-level vw_latest_review_priority locally.
SELECT priority_tier,action,COUNT(*) AS active_listings,
 SUM(direction='Above Peer Benchmark') AS above_peer,
 SUM(direction='Below Peer Benchmark') AS below_peer,
 AVG(peer_iqr_pct) AS mean_peer_iqr_pct,
 MAX(ABS(premium_pct)) AS max_absolute_premium_pct
FROM vw_latest_review_priority GROUP BY priority_tier,action ORDER BY priority_tier;

-- Current room type describes each comparison; previous/next rates require calendar adjacency.
WITH ordered AS (
 SELECT month_date,room_type,mom_change_pct,next_change_pct,
 ROW_NUMBER() OVER(PARTITION BY month_date,room_type ORDER BY mom_change_pct,listing_id) AS rn,
 COUNT(*) OVER(PARTITION BY month_date,room_type) AS n
 FROM vw_listing_rate_transitions WHERE mom_change_pct IS NOT NULL
)
SELECT month_date,room_type,COUNT(*) AS matched_pairs,
 AVG(mom_change_pct) AS mean_change_pct,
 AVG(CASE WHEN rn IN ((n+1)/2,(n+2)/2) THEN mom_change_pct END) AS median_change_pct,
 AVG(CASE WHEN rn>CAST(n*.05 AS INTEGER) AND rn<=n-CAST(n*.05 AS INTEGER)
     THEN mom_change_pct END) AS trimmed_mean_5pct,
 SUM(ABS(mom_change_pct)>=35) AS substantial_changes,
 SUM(CASE WHEN ABS(mom_change_pct)>=35 AND next_change_pct IS NOT NULL THEN 1 ELSE 0 END) AS changes_with_followup,
 SUM(CASE WHEN ABS(mom_change_pct)>=35 AND mom_change_pct*next_change_pct<0 THEN 1 ELSE 0 END) AS direction_reversals
FROM ordered GROUP BY month_date,room_type ORDER BY month_date,room_type;

-- Small segments remain in the view, but ranking screens to >=10 active observations.
WITH sufficiently_observed AS (
 SELECT * FROM vw_segment_pricing
 WHERE month_date=(SELECT MAX(month_date) FROM fact_listing_month) AND active_listings>=10
)
SELECT *,100.0*(p75_adr_aed-p25_adr_aed)/NULLIF(median_adr_aed,0) AS segment_iqr_pct,
 DENSE_RANK() OVER(PARTITION BY room_type ORDER BY median_adr_aed DESC) AS rate_rank_in_room_type
FROM sufficiently_observed ORDER BY active_listings DESC,room_type,bedrooms;

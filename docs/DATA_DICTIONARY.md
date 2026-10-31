# Data dictionary — saved Power BI model

Verified against the saved TMDL tables/relationships and relevant PBIR bindings on 29 October 2026. This is a documentation inspection, not a fresh source or runtime audit. The [model definition](../powerbi/DubaiRentalIntelligence.SemanticModel/definition/model.tmdl) remains authoritative; older starter DAX and generated catalogs do not enumerate the complete final model.

## Tables, grain and relationships

| Saved table | Grain / key | Role |
|---|---|---|
| `FactListingMonth` | One text `listing_id` × date `month_date` | Historical observations **plus joined, precomputed peer benchmarks and investigation fields**; 99,745 records in existing audit |
| `DimListing` | One text `listing_id` | All 4,364 listing identities with undated snapshot descriptors/provenance; completeness varies by attribute |
| `DimMonth` | One `month_date` | 60 month starts; year, month number/name, labels and chronological sort fields |
| `DimAccommodation` | One `room_type` | Display `accommodation_label` for historical room types |
| `DimBedrooms` | One `bedroom_label` | Label and `bedroom_sort`, including unknown handling |
| `DimArea` | One `area_label` | Observed historical label domain, including `Unknown area`; not boundary geometry |
| `CoverageMonth` | One `month_date` | Prepared monthly source coverage; observed/active counts, missingness, continuity and active medians |
| `PeerExamples` | Subject `listing_id` × `month_date` × `peer_listing_id` | Stored latest-month nearest examples; at most five per eligible subject |
| `Analytics` | Hidden placeholder column plus measures | Main market, executive, Studio and investigation measure home; not an observation table |

[relationships.tmdl](../powerbi/DubaiRentalIntelligence.SemanticModel/definition/relationships.tmdl) defines six active dimension-to-fact filter paths using the model's default single-direction many-to-one relationships: `FactListingMonth.listing_id → DimListing.listing_id`; `month_date → DimMonth.month_date`; `room_type → DimAccommodation.room_type`; `bedroom_label → DimBedrooms.bedroom_label`; `area_label → DimArea.area_label`; and `CoverageMonth.month_date → DimMonth.month_date`. No bidirectional relationship is introduced for visual interaction.

`PeerExamples`, the selector/support tables below and measure homes have no additional relationships in that file. Measures apply their intended contexts explicitly. CoverageMonth is related only to month, so its prepared counts must not be assumed segment-responsive; segment-specific trend contributors come from fact measures.

**Pipeline versus saved model names:** prepared `FactPeerBenchmark`/benchmark CSV outputs are joined into `FactListingMonth` for this semantic model. There is no separate final-model `FactPeerBenchmark`, `FactCoverageMonth` or `PeerExamplesLatest` table; saved names are `CoverageMonth` and `PeerExamples`.

## Important observation and benchmark fields

| Table / field | Type or unit | Meaning / validity |
|---|---|---|
| `FactListingMonth.listing_id` | String | Preserve full identity; never convert to floating-point or infer selection from incidental single-candidate filters |
| `month_date` | DateTime storing month-start dates | Reporting month, not a booking date; composite unique key with listing ID |
| `active` | Boolean | Observed source status; inactive record differs from no record |
| `native_avg_daily_rate` | Numeric, AED | Provider-reported monthly rate; market/Geography zero-rate handling differs from positive-rate peer eligibility |
| `occupancy` | Numeric fraction [0,1] | Provider estimate; percentage formatting multiplies display by 100; zero remains valid |
| `native_revenue`, `native_revpar` | Numeric, AED | Provider estimates; neither audited realized income nor an imposed ADR identity |
| `native_booked_rate_avg` | Nullable numeric, AED | Separate nested-source estimate; not the reported-rate substitute or matching rate |
| `room_type`, `bedrooms`, `bedroom_label` | Text / numeric / text | Historical matching attributes and display category; missing bedrooms remain unknown |
| `latitude`, `longitude` | Numeric degrees | Source coordinates; mapped validity bounds latitude 24.5–25.6, longitude 54.5–56.0 |
| `neighborhood`, `area_label` | Text | Source historical label and model display label; no undated snapshot backfill |
| `Geo Coordinate Pair` | Calculated string | Latitude and longitude each formatted to ten decimals with `en-US`, separated by ` \| `; blank if either input blank. Grouping alone does not validate bounds. |
| `same_listing_prev_month` | Boolean | Prior-calendar-month observation continuity, not proof of active continuity |
| `peer_count`, `radius_km` | Count / km | Full comparable population excluding subject; selected 2 km or expanded 5 km radius |
| `peer_median_aed`, `peer_p25_aed`, `peer_p75_aed` | Nullable numeric, AED | Full eligible peer distribution; suppressed when benchmark unavailable |
| `peer_median_estimated_occupancy` | Nullable fraction | Full-peer estimated occupancy median |
| `premium_pct`, `estimated_occupancy_gap_pp` | Percentage points | Relative price deviation and occupancy difference; not fractions |
| `peer_iqr_ratio` | Fraction | Peer IQR / median; descriptive comparability evidence |
| `comparison_status`, `review_signal` | Text | Eligibility and threshold-based review result; unassessed is not a zero deviation |
| `priority_tier`, `action`, `direction`, `confidence_label` | Text | Precomputed workflow heuristics; not calibrated confidence or a recommendation to change price |
| `review_order`, `deviation_rank` | Numeric ordering | Existing queue/ranking inputs |
| `mom_change_pct`, `stable_cohort`, `mom_band` | Derived change / membership / category | Historical comparison support; do not bridge absent observations |
| `DimListing.metadata_source` | Text | Undated snapshot provenance; host/quality/capacity descriptors are not historically effective-dated |
| `PeerExamples.distance_km`, `peer_adr_aed`, `peer_estimated_occupancy` | km / AED / fraction | Display evidence for a stored example, not the full benchmark population |

Other source fields such as available/unavailable days and listing descriptors remain in the fact/dimension. Their presence does not authorize deriving verified booked nights, profitability or historical quality controls. See [Methodology](METHODOLOGY.md).

## Disconnected selectors and support tables

| Saved table / field | Values / purpose |
|---|---|
| `MetricSelector[Metric]` | Overview: Reported rate (AED), Estimated occupancy, Estimated revenue (AED) |
| `Trends Metric[Metric]` | Nightly rate, Est. occupancy, Est. revenue; local selector and Trends measure home |
| `Geography Metric[Metric]` | Same three labels; local community comparison selector and Geography measure home; does not change map weighting |
| `Deep Dive Metric[Metric]` | Same three labels; default Est. occupancy; property-history measure home |
| `Investigation Priority[Label/Code]` | All review cases / 0; Stronger evidence / 1; Comparability review / 2 |
| `Investigation Direction[Label/Code]` | Both directions / 0; Above peer median / 1; Below peer median / 2 |
| `Studio Price Categories[Metric]` | Peer P25, Peer Median, Peer P75, Property Rate; ordered chart categories |
| `Deep Dive Subject[listing_id]` | Distinct listing identities copied from DimListing; disconnected exact handoff target, not an extra visible lookup |
| `Deep Dive Calendar` | All DimMonth dates as `Month`, plus Year, MonthName, MonthNumber and chronological Index; 60 rows |
| `Deep Dive Run[Run]` | Integer series 1–calendar count; separates historical line segments across gaps |
| `CohortSelector[Cohort]` | Full sample / Fixed 12-month cohort; retained analytical support, not a new shared Market Lens control |
| `ReviewThreshold[Threshold]` | 10, 15, 20, 25, 30, 35, 40, 50 percentage-point sensitivity choices; does not replace the queue's stored classification |

Overview sync fields are `DimArea[area_label]`, `DimAccommodation[accommodation_label]`, `DimBedrooms[bedroom_label]` and `DimMonth[year_month]`. The first three sync to Trends, Geography and Investigations; month syncs only to Geography. Studio's unsynchronized research controls use `DimListing[listing_id]` and `DimMonth[month_label]`. These UI fields resolve through the model keys above.

## Important measures and filter contracts

| Measure / family | Definition and output |
|---|---|
| `Observed Listings`, `Active Listings`, `Active Listing Months` | Distinct observed IDs; distinct active IDs with zero fallback; active record count. Their multi-month denominators differ. |
| `Median Reported Rate`, `Median Estimated Occupancy`, `Estimated Revenue` | Active-record median rate (AED), median occupancy (%), **sum** estimated revenue (AED) in current context |
| `Benchmarked Listing Months`, `Benchmark Coverage`, `Review Candidate Share` | Eligible listing-month count and related denominator-aware shares; not unique properties across arbitrary multi-month contexts |
| `Selected Metric Value`, `Selected Metric Smoother` | Overview's local metric and three-month average of monthly metric values |
| `Trends Monthly Value`, `Trends Contributing Listings` | Active median selected metric and distinct active nonblank contributors per month; explicit property filters removed |
| `Trends Seasonal Value`, `Trends Seasonal Months` | Median of valid monthly medians and number of contributing year-months |
| `Geo Snapshot Valid` | One value of `DimMonth[year_month]`; otherwise geographic snapshot measures remain blank/explanatory |
| `Geo Active Listings`, `Geo Mapped Listings`, `Geo Known Area Listings` | Same-context distinct active IDs; mapped additionally requires nonblank in-bounds coordinates; known additionally requires nonempty non-Unknown area |
| `Geo Mapped Share`, `Geo Known Area Share` | Respective numerator / Geo Active Listings via DIVIDE; blank at zero denominator; formats 0.0% / 0.00% |
| `Geo Median Nightly Rate`, `Geo Median Est Occupancy`, `Geo Median Est Revenue` | Active valid-record community medians; nonnegative rate/revenue, occupancy [0,1], nonblank; zeros included |
| `Geo Contributors`, `Geo Ranking Eligible`, `Geo Top 10 Visible` | Selected-metric contributor count; named-area minimum ten; descending selected median Top 10 with label tie-break |
| `Investigation Snapshot Month`, `Investigation Review Signals`, `Investigation Queue Visible` | Latest classified snapshot, local Priority/Direction and market dimensions; queue shows qualifying listing rows, independent of Overview month |
| `Studio Incoming Property`, `Studio Explicit Property` | Explicit single fact-ID inbound guard takes precedence; otherwise explicit single DimListing ID. No arbitrary ID fallback. |
| `Studio Property Month Valid` | One explicit authoritative ID and one actual observed comparison month; incoming investigation uses the latest snapshot context |
| `Studio Property Rate`, `Studio Peer Median/Count/P25/P75`, `Studio Premium` | Selected observed property and full precomputed benchmark; market-segment filters removed; blank benchmark remains unavailable |
| `Studio History Rate`, `Studio History Peer Median` | Property and contemporaneous stored peer history; independent from comparison-month truncation through the configured history context |
| `Studio Example Visible` | Explicit valid property-month, eligible benchmark and latest month; filters the disconnected stored examples through measures |
| `Deep Dive Transfer Match`, `Deep Dive Destination` | Match confirmation-row subject to authoritative Studio property; enable exact transfer rather than unrestricted navigation |
| `Deep Dive Property` | Exactly one explicitly filtered Deep Dive Subject ID, validated to exist in all fact records |
| `Deep Dive First/Latest Month`, `Deep Dive Observed Months` | Min/max actual observed date and count of records for that ID across ALL fact rows; valid under unique listing-month grain |
| `Deep Dive Latest Rate/Occupancy/Revenue` | Each selects the same property-specific latest record, regardless of activity; no independent latest-nonblank substitution |
| `Deep Dive Monthly Rate/Occupancy/Revenue` | Exact subject × disconnected calendar month; no record yields blank, valid zeros retained |
| `Deep Dive Observation Status`, `Deep Dive Coverage Symbol` | Active/A, Inactive/I, No observation/—, Activity unknown/?; no property produces blank/selection-required context |
| `Deep Dive Monthly Value`, `Deep Dive Run Value` | Local metric with AED/% formatting; run-index segmentation excludes gaps without interpolating |

The ArcGIS `Location` role binds `Geo Coordinate Pair`; Latitude/Longitude bind historical fact coordinates; Size **and** Tooltips bind `Geo Mapped Listings`. The saved renderer uses graduated count classes. Exact count remains available even when multiple counts share a size class.

## Evidence and maintenance boundary

Current field/relationship/measure descriptions were checked against saved definitions; numerical findings are reused from the [analytical reconciliation](../VALIDATION_SUMMARY.md). No DAX, relationships, filters or report state changed. Native interaction evidence remains separate. The [Methodology limitations](METHODOLOGY.md#remaining-limitations-and-evidence) retain R01–R03 and residual R04 cases, including the future-null loose-equality caveat in legacy zero-count measures.

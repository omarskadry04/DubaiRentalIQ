# Methodology, assumptions and guardrails

This document reconciles the final saved model with existing numerical audits. It describes the historical sample and implemented analytical contracts, not a new data refresh or native acceptance run. See the [Data Dictionary](DATA_DICTIONARY.md) for exact table and measure names.

## Source and grain

The observation spine is one record per **text listing ID × reporting month**. Existing independent audits reconcile **99,745 records, 4,364 distinct listings and 60 consecutive months, March 2021–February 2026**, with no duplicate listing-month keys. A reporting month is not a reservation/check-in date.

Four source files have distinct roles:

- `past_rates.csv` supplies historical observations. `past_rates.parquet` contains the same 99,745 × 23 history and is reconciled, not appended (numeric tolerances 1e-9 absolute / 1e-12 relative).
- `listings_monthly.csv` contains 22,629 overlapping records for 1,000 properties; overlap is not extra supply.
- `listings.parquet` supplies an **undated** 4,364-property snapshot and 99,745 nested monthly records. Shared monthly measures reconcile; the separate nullable `native_booked_rate_avg` contributes 45,938 non-null observations and is not substituted for reported ADR.

The snapshot covers all listing IDs, but individual descriptors remain incomplete. Its ratings, amenities and capacity do not become historical attributes. Historical room type, bedrooms, coordinates and community labels come from the observed listing-month record; missing historical areas are not filled from a property's later neighborhood.

Source fingerprints and missingness evidence are recorded in the existing [Python/SQL audit](../VALIDATION_SUMMARY.md) and [data-quality audit](../VALIDATION_SUMMARY.md). This revision did not repeat those tests.

## Populations, aggregation and units

`active = TRUE()` identifies an active observation; it does not prove availability or bookings on every day. At a single month, `Active Listings` counts distinct active listing IDs. Across multiple months, distinct active properties and active listing-month records are different denominators. `Observed Listings` includes inactive observations; property history also retains inactive records.

| Metric / workspace | Implemented aggregation and population |
|---|---|
| Overview nightly rate | Median reported `native_avg_daily_rate` among active records in context |
| Overview occupancy | Median active-record `occupancy`; stored as a 0–1 fraction and formatted as a percentage |
| Overview estimated revenue | Sum of active-record `native_revenue` in context; sample revenue, not a citywide estimate |
| Overview historical series | Selected market metric by month; smoother averages monthly metric values over a three-month window, not a pooled listing median |
| Market Trends | Monthly median rate, occupancy or estimated revenue among active observations; contributor counts require a nonblank selected metric |
| Seasonality | Median of valid year-month medians within each calendar month, with equal weight per contributing year-month |
| Geography | One-month active population; community medians with metric-specific valid contributors |
| Studio | One explicitly selected property-month and its stored full-peer benchmark; history is evaluated separately across months |
| Deep Dive | Recorded values for one explicit listing, including inactive observations; all three latest KPIs use its same latest observed record |

Rate, revenue, RevPAR and benchmark prices are AED. `premium_pct` is stored in **percentage points** (20 means 20%); occupancy and `peer_iqr_ratio` are fractions. Do not multiply an already percentage-point deviation by 100 again.

February 2026 contains **2,471 observed / 1,955 active** listings. Existing audits found **1,615 active listings with eligible benchmarks**, and the latest review queue contains **902** cases. Denominators such as benchmark coverage are listing-month based when multiple months are in scope; they must not be divided by an unrelated distinct-property count.

## Missing values, valid zeros and history

Current source validation found no null, negative or nonfinite values in the audited rate, occupancy and revenue fields; occupancy is within 0–1. That does not make a missing property-month record a zero-valued record. Other attributes and benchmarks can be missing.

Market measures rely on the validated source contract. Geography explicitly accepts nonblank nonnegative rate/revenue and occupancy in [0,1]; valid zeros contribute to its medians and contributor counts. **Benchmark eligibility instead requires strictly positive rate.** An insufficient or ineligible peer median remains blank, not zero.

Deep Dive uses a disconnected calendar derived from all reporting months. Its full-calendar table distinguishes active, inactive, no observation and ambiguous activity. Recorded zeros remain visible. Missing financial values remain blank, with no forward filling. The historical chart uses run segmentation to prevent missing values from being bridged as one continuous series.

Latest-observed KPIs use the property's maximum month containing a record, not the latest calendar month and not three independent latest-nonblank lookups. An inactive latest record is still the latest observed record. Coverage counts actual listing-month records out of 60; the verified unique-key contract makes this an observed-month count.

## Geographic evidence and ArcGIS

Source coordinate validation uses latitude **24.5–25.6** and longitude **54.5–56.0**, inclusive. These are approximate source bounds, not Dubai administrative polygons or independent address verification. Missing coordinates are not replaced with zero. Co-located listings are not automatically duplicate properties.

For one focus month and the same Market Lens:

- **Mapped Share** = distinct active listings with valid nonblank coordinates / all distinct active listings.
- **Known-Area Share** = distinct active listings with a nonblank, nonempty label other than `Unknown area` / all distinct active listings.
- Zero denominators produce blank shares. No unique focus month produces an explanatory state, not an unlabeled multi-month map.

February's active population has **1,955 mapped listings across 1,782 coordinate groups**, with **452 known-area listings (23.12%)** and **1,503 Unknown (76.88%)**. These percentages use active observations; older neighborhood-missing percentages over all observations are not interchangeable.

The production visual is **ArcGIS**, not Azure Maps or the earlier coordinate-only scatterplot. Latitude/longitude use historical fact fields. `Geo Coordinate Pair` formats both coordinates to ten decimal places with a separator. `Geo Mapped Listings` is assigned to **Size and Tooltips**, retaining the contribution of co-located listings and valid Unknown-area locations.

Saved symbology uses natural-break graduated size classes. At the reconciled saved state, class endpoints were counts 1, 2, 4, 7 and 11, with increasing symbol sizes 3–30. This is **count-driven graduated sizing, not continuous proportional area**; different counts within a class can share a size. Exact counts remain in tooltips. Do not promise fixed class endpoints under every filter state or infer a verified neighborhood polygon from a point.

Community ranking excludes Unknown and requires **at least ten valid contributors to the selected metric**, then selects up to ten communities by descending median with an area-label tie-break. The evidence table retains smaller communities and explicitly identifies Unknown. These are comparisons of observed labels, not official whole-market neighborhood rankings. See [map reconciliation](../VALIDATION_SUMMARY.md).

## Peer benchmarks and review classifications

Eligible subjects and peers are active, have finite positive reported rate, known room type, integer bedrooms ≥0 and valid source coordinates. Peers exclude the subject and match **month, room type and exact bedroom count**. Haversine distance selects peers within **2 km**; if fewer than ten exist, expand to **5 km**. If still fewer than ten exist, suppress benchmark median, deviation and assessed review signal. Candidate retrieval uses a spatial index; both distance stages retain the documented 1e-7 km boundary tolerance.

Use the **entire eligible peer group** for rate median, linearly interpolated P25/P75 and estimated occupancy median. Deviation is `(subject rate / peer median − 1) × 100`. Absolute deviations ≥20% indicate review and ≥35% large deviation, after rounding to nine decimal percentage places for stable threshold comparisons. These are analyst-selected screening rules, not calibrated confidence or proven mispricing.

The five nearest examples are a latest-month illustration, ordered deterministically using listing ID for equal-distance ties. They do not define the benchmark: prior validation found their median differed from the full median by more than 20% for 530 latest-month subjects. Full-history independent reconstruction covered 70,649 matching-eligible observations, including insufficient groups. Large dispersion is common: 1,157 of 1,615 latest eligible groups had IQR/median above 40%.

SQL priority classifications combine count, radius and dispersion as review heuristics. The latest queue has **173 stronger-evidence + 729 comparability-review = 902 cases**; stronger-evidence/above-peer filtering yields **91**. These are different scopes, not conflicting totals. Priority and Direction filter the latest queue independently of Overview's selected month.

## Context ownership and property identity

| Workspace | Month and selection contract |
|---|---|
| Overview | Owns shared Area/Accommodation/Bedrooms and Reporting Month; selected-month briefing and configured full-history visual |
| Geography | Inherits all four controls; requires one focus month |
| Market Trends | Inherits the three dimensions, not Reporting Month; full 60-month timeline |
| Investigations | Inherits the three dimensions; latest classified February 2026 snapshot |
| Studio | Explicit inbound investigation ID takes precedence; otherwise an explicitly selected lookup ID and research month. Global market dimensions do not define the property. |
| Deep Dive | Exact transferred subject ID plus disconnected full calendar; comparison month cannot truncate history |

Studio checks an explicit single fact-ID filter for inbound identity, rather than trusting `SELECTEDVALUE` alone. Direct Research checks an explicit single dimension-ID filter. The confirmation row exposes the matching subject through `Deep Dive Transfer Match`; selection is required for the handoff. Deep Dive validates one explicit subject filter against existing fact records. Missing/ambiguous identity produces an empty state, not the first available listing.

Restores retain their existing scopes. Overview can change the shared Market Lens; the local Trends/Geography/Investigations restores preserve it. Studio's reset clears its research/inbound context. Deep Dive's restore preserves the subject and historical calendar. See [User Guide](USER_GUIDE.md).

## Remaining limitations and evidence

- **R01 — geography/attributes:** locations are source-valid, not verified addresses/boundaries. Historical bedroom missingness affects 7.53% of records and matching eligibility. Do not impute unknown attributes or generalize the known-area subset to all Dubai rentals.
- **R02 — provider/representativeness:** estimates are not bookings, realized income, cash flow or a census. ADR × estimated occupancy × days agrees within AED 1 with reported revenue for only 55,230/99,745 observations; preserve separate provider metrics rather than “repairing” revenue. RevPAR/calendar-day numerical agreement does not establish external field definitions.
- **R03 — future-null risk:** current occupancy/revenue inputs have no nulls, but legacy zero-count measures use loose DAX `= 0`. If nullable inputs become permitted, strict blank/zero tests require review. No current zero-count discrepancy was found.
- **R04 — residual native cases:** owner-confirmed navigation, month synchronization, both property workflows, scoped restores and persistence do not close every rendered-coordinate, pan, ranking-edge, short/early-ending-property or historical-row test. Saved definitions and numerical checks are not proof of all runtime behavior.

Sample composition changes over time. Adjacent-month rate comparisons require actual consecutive active observations and a positive previous rate; gaps are not bridged. The 989-property March 2025–February 2026 fixed cohort is retrospective survivor analysis, not a forecasting feature or a year-over-year comparison. Undated capacity, ratings and amenities remain uncontrolled in historical matching.

Evidence sources distinguish [source/reference checks](../VALIDATION_SUMMARY.md), [saved-model and analytical reconciliation](../VALIDATION_SUMMARY.md), [native acceptance cases](../VALIDATION_SUMMARY.md) and [performance measurements/owner observations](../VALIDATION_SUMMARY.md). Overlapping assertion totals must not be combined.

## Freshness and rights

The last reporting month is **February 2026**. Dataset redistribution and ArcGIS map screenshot/public-display rights remain unresolved until separately verified. Retain source archives, raw/generated listing-level data, private diagnostics and runtime caches outside publication. Aggregation or screenshot capture is not automatically a rights clearance. A license for original code would not cover third-party data, imagery or map tiles.

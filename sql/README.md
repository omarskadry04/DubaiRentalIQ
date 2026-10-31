# SQL analytics — Dubai Short-Term Rental Intelligence

SQLite provides reusable coverage, historical, segmentation and pricing-review analyses. Python owns geographic matching; SQL consumes its validated outputs without redefining peers. Source period: March 2021–February 2026. Source verification and audit results are documented in the [Validation Summary](../VALIDATION_SUMMARY.md).

## Architecture

| Table | Grain / primary key | Role |
|---|---|---|
| `dim_listing` | `listing_id` | Latest fact attributes and undated Parquet snapshot descriptors |
| `dim_month` | `month_date` | Consecutive monthly calendar |
| `fact_listing_month` | `(listing_id,month_date)` | Provider rate and estimated performance, nullable native booked rate |
| `fact_peer_benchmark` | `(listing_id,month_date)` | One benchmark status per observed row |
| `fact_coverage_month` | `month_date` | Global coverage, not additive across property joins |
| `peer_examples_latest` | `(listing_id,month_date,peer_listing_id)` | Up to five examples, not the full peer population |

IDs are TEXT, dates ISO month-start strings, booleans constrained 0/1 integers. Facts reference listing/month dimensions; benchmarks and both ends of examples reference the composite fact key. Enable `PRAGMA foreign_keys=ON` on every writing connection; the builder does so before import. Snapshot attributes are not historically versioned: use monthly fact fields for historical segmentation. Join facts on **both** keys; joining examples before summing revenue would double-count.

## Script organization and execution

| File | Purpose / techniques |
|---|---|
| `01_database_schema.sql` | Canonical constraints and indexes; empty database only |
| `02_analytics_views.sql` | Ten reusable views; joins, CTEs, CASE, LAG/LEAD, ROW_NUMBER, DENSE_RANK |
| `03_market_performance.sql` | Fact-derived monthly medians, performance and coverage |
| `04_historical_trends.sql` | Adjacent active pairs, mean/median/trimmed mean and subsequent direction |
| `04b_fixed_cohort.sql` | Final 12-month stable cohort and retention |
| `05_property_segmentation.sql` | Room type/bedrooms, price dispersion and review share |
| `06_competitive_pricing.sql` | Directional candidates, insufficient peers and radius fallback |
| `07_opportunity_analysis.sql` | Aggregate action workload from listing-level priority view |
| `08_data_validation.sql` | Named violation counts, asserted zero by Python |
| `09_query_performance.sql` | EXPLAIN QUERY PLAN for reporting joins |

After Python preparation and benchmarking, run from the root:

```bash
python src/03_build_powerbi_exports.py
python src/05_run_sql_analysis.py
python -m unittest discover -s tests -v
```

The builder reads schema/views directly from SQL, imports dimensions before facts, validates a temporary database and publishes only on success. No competing schema is embedded in Python. The read-only analysis runner saves aggregates, reconciliations, plans and timings in `reports/sql/`.

The reporting and validation SQL files can be run in SQLite **after** the database has been populated and the analytical views have been created. The schema script is intended only for an empty database. For example:

```bash
sqlite3 -header -csv data/processed/dubai_rentals.sqlite ".read sql/03_market_performance.sql"
```

`.read` is a SQLite **CLI command**, not embedded in SQL scripts. Direct database setup requires schema, correctly typed/null-aware import of all six CSVs, then views. The Python loader is the supported import path; naive CSV import can mishandle booleans and blanks. Never execute schema over an existing database.

## Analytical contracts

- Monthly medians rank active property rates and average the middle one/two rows; not a booked-night-weighted market ADR. Required measures cannot be missing during preparation.
- LAG/LEAD windows precede filters. Comparisons require consecutive calendar months and active observations; prior rate must be positive. Missing follow-up is reported separately, not as no reversal.
- Trimmed mean excludes `floor(n*0.05)` values per tail within month/type; underlying data are retained.
- Fixed cohort requires activity in **every** final 12-month period. Retrospective membership has survivor bias and is unsuitable as an ex-ante prediction feature.
- Segment quartiles use nearest-rank `ceil(p*n)`; Python **peer** quartiles use linear interpolation. These refer to different populations and definitions.
- Review share denominator is benchmarked listings; active/observed counts remain explicit. Ranking screens segments to ≥10 active observations; the view retains all, including unknown bedrooms.
- Revenue and occupancy are estimates. Do not reconstruct revenue as reported ADR × occupancy × days: many source records disagree with that identity. Native booked rate is separate, missing in 53,807 observations.

## Explainable priorities

`vw_latest_review_priority` retains every latest active listing:

1. **Priority tier 1 — Pricing review**: eligible benchmark, a flagged price deviation (at least 20% in absolute value), at least 20 peers within a 2 km radius, and peer IQR/median ≤40%.
2. **Priority tier 2 — Comparability review first**: other listings with flagged deviations that do not meet all tier-1 conditions.
3. **Priority tier 3 — Data/peer coverage investigation**: listings without an eligible benchmark.
4. **Priority tier 4 — Monitor**: listings with eligible benchmarks but no flagged deviation.

The view also provides an `action` label as a separate field from `priority_tier`. These labels are operational guidance, not guaranteed pricing decisions; consult the tier and review signal together.

DENSE_RANK orders absolute deviations within tiers; ROW_NUMBER adds a deterministic ID tie-break. These are operational heuristics, not calibrated predictions. Even first-tier deviations may reflect legitimate quality differences. Classification uses absolute premium rounded to **nine decimal percentage places** before 20/35% comparisons to stabilize floating-point boundaries; display rounding never determines flags.

## Verified business findings

| Question | Result from supplied snapshot | Interpretation / stakeholder relevance |
|---|---|---|
| Latest sample performance? | Feb 2026: 1,955 active, median AED 870, mean AED 1,187.13; estimated sample revenue AED 13,505,777 | Inspect skew and mix; not audited revenue or a Dubai total. |
| Coverage affects apparent trends? | Five months change >25%; June 2024 increases 308.77% | Show counts/cohorts alongside market commentary; not proof of market growth. |
| Stable cohort versus changing sample? | 989 active in every Mar 2025–Feb 2026 month; median AED 756 → 882 versus full-sample AED 721.5 → 870 | Membership changes the comparison; seasonality and survivor bias remain. |
| Bedroom segments? | One-bedroom entire homes: 956 active, median AED 725.5; two-bedroom: 524, AED 1,238.5 | Descriptive segmentation, not causal bedroom value. |
| Competitive review workload? | 902/1,615 benchmarked: 471 above, 431 below; 145 use 5 km | Review candidates require comparable quality and real booking evidence. |
| Investigate first? | 173 first-tier; 729 comparability-first; 340 coverage investigations; 713 monitor | Transparent managerial triage, no validated pricing benefit. |

Historical SQL reconciles **71,960 consecutive active pairs** and reports mean, median and trimmed mean to expose extreme movements. These figures describe the previously validated local dataset. See the [Validation Summary](../VALIDATION_SUMMARY.md) for details; generated `reports/sql/` outputs remain local.

## Validation and performance

In the previously tested local environment, the builder validated primary/foreign keys, row counts, exact queue membership/values, coverage, segments, and a rejected invalid FK insertion. The SQL validation file checks calendar/domain rules, suppression/classification, premium arithmetic and examples. Independent pandas calculations reconcile all monthly medians/revenue, adjacent-pair keys/changes, **972 segment groups**, quartiles, cohort membership and each priority assignment. A separate raw-CSV validator reconstructs **all 70,649 eligible listing-months** without importing the matching engine.

The local `analysis_validation.json` report records execution times. It also compares the median time of ten repeated runs using the month index against a version of the same revenue query that scans the table instead. `09_query_performance.sql` separately uses `EXPLAIN QUERY PLAN` to show how SQLite plans a reporting join; that command does **not** measure execution time. These are measurements from the tested local environment, not guaranteed speed improvements on other systems. Full-history queries can still require scans and sorting. Existing primary-key and month indexes support common joins; an unnecessary duplicate index was removed.

## Limitations

Metadata is undated, proximity does not validate amenities/quality, performance estimates lack booking ground truth, and sample membership changes. The five examples are not the full benchmark. No causal uplift, ROI, whole-market coverage or Power BI interaction testing is claimed. Data redistribution rights remain unverified; keep listing-level results private.

# SQL Analytics — Dubai Short-Term Rental Intelligence

SQLite provides reusable coverage, historical, segmentation, and pricing-review analyses. Python owns geographic matching; SQL consumes its validated outputs without redefining peers.

**Source period:** March 2021–February 2026.

Source verification and audit results are documented in the [Validation Summary](../VALIDATION_SUMMARY.md).

## Architecture

| Table | Grain / primary key | Role |
|---|---|---|
| `dim_listing` | `listing_id` | Latest fact attributes and undated Parquet snapshot descriptors |
| `dim_month` | `month_date` | Consecutive monthly calendar |
| `fact_listing_month` | `(listing_id, month_date)` | Provider rate and estimated performance, nullable native booked rate |
| `fact_peer_benchmark` | `(listing_id, month_date)` | One benchmark status per observed row |
| `fact_coverage_month` | `month_date` | Global coverage, not additive across property joins |
| `peer_examples_latest` | `(listing_id, month_date, peer_listing_id)` | Up to five examples, not the full peer population |

IDs are stored as `TEXT`, dates as ISO month-start strings, and booleans as constrained 0/1 integers.

Facts reference listing and month dimensions. Benchmarks and both ends of peer examples reference the composite fact key.

Enable `PRAGMA foreign_keys=ON` on every writing connection. The Python database builder does so before importing data.

Snapshot attributes are not historically versioned; use monthly fact fields for historical segmentation.

Join facts on **both listing and month keys**. Joining peer examples before aggregating revenue may duplicate rows and inflate totals.

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

### Build and validate the database

After completing the Python preparation and peer-benchmarking stages, run the following commands from the repository root:

```powershell
python src/03_build_powerbi_exports.py
python src/05_run_sql_analysis.py
python -m unittest discover -s tests -v
```

The builder reads the canonical schema and views directly from the SQL files, imports dimensions before facts, validates a temporary database, and publishes the database only after successful validation.

No competing database schema is embedded in Python.

The read-only analysis runner saves aggregates, reconciliations, query plans, and timing results in `reports/sql/`.

The prepared SQLite database is already included in the public repository, so these steps are optional for readers who only want to inspect the supplied analytical results.

### Execute individual SQL analyses

The reporting and validation SQL files can be executed using SQLite **after** the database has been populated and the analytical views have been created.

For example, with the SQLite command-line utility installed:

```powershell
sqlite3 -header -csv data/processed/dubai_rentals.sqlite ".read sql/03_market_performance.sql"
```

The `.read` instruction is a SQLite CLI command, not embedded SQL syntax.

Direct database setup requires the schema, correctly typed and null-aware imports of the six analytical CSV tables, followed by creation of the analytical views.

The Python loader is the supported import path. Naive CSV imports may mishandle boolean values and missing data.

**Never execute the schema script over an existing populated database.** It is intended for an empty database.

For the full environment and regeneration instructions, see [Local Setup](../docs/SETUP.md).

## Analytical contracts

- **Monthly medians:** Rank active property rates and average the middle one or two rows. This is not a booked-night-weighted market ADR. Required measures cannot be missing during preparation.
- **Historical comparisons:** LAG/LEAD windows are evaluated before filters. Comparisons require consecutive calendar months and active observations; the preceding nightly rate must be positive. Missing follow-up is reported separately rather than interpreted as no reversal.
- **Trimmed mean:** Excludes `floor(n*0.05)` values from each tail within month/type. The original observations remain in the dataset.
- **Fixed cohort:** Requires activity in every month of the final twelve-month period. Retrospective cohort membership introduces survivor bias and is unsuitable as an ex-ante prediction feature.
- **Segment quartiles:** Use nearest-rank `ceil(p*n)`. Python peer quartiles use linear interpolation. These are different definitions applied to different populations.
- **Review share:** Uses benchmarked listings as its denominator, while active and observed counts remain explicit. Ranking screens segments with at least ten active observations. The underlying view retains all segments, including unknown bedrooms.
- **Revenue and occupancy:** These are provider estimates. Do not reconstruct estimated revenue as reported ADR × occupancy × days because many source observations do not satisfy that identity. Native booked rate is separately recorded and missing in 53,807 observations.

## Explainable priorities

The `vw_latest_review_priority` view retains every listing active in the latest reporting month.

It applies four interpretable operational priority tiers:

1. **Priority tier 1 — Pricing review:** An eligible peer benchmark, a flagged absolute price deviation of at least 20%, at least 20 peers within a 2 km radius, and peer IQR/median no greater than 40%.

2. **Priority tier 2 — Comparability review first:** Other listings with flagged deviations that do not satisfy every tier-1 condition.

3. **Priority tier 3 — Data/peer coverage investigation:** Listings without an eligible peer benchmark.

4. **Priority tier 4 — Monitor:** Listings with an eligible benchmark but no flagged price deviation.

The view provides an `action` label separately from `priority_tier`.

These labels support review prioritization and are not guaranteed pricing recommendations. The priority tier and the underlying review signal should be interpreted together.

`DENSE_RANK` orders absolute deviations within priority tiers, while `ROW_NUMBER` adds a deterministic listing-ID tie-break.

These are operational heuristics rather than calibrated predictions. Even substantial price deviations may reflect legitimate property-quality or amenity differences.

Classification uses the absolute premium rounded to **nine decimal percentage places** before comparisons with the 20% and 35% thresholds, reducing floating-point boundary inconsistencies.

Displayed rounding does not determine review flags.

## Verified business findings

The following findings describe the previously validated historical dataset included in the repository.

| Business question | Result from supplied snapshot | Interpretation / stakeholder relevance |
|---|---|---|
| Latest sample performance? | February 2026: 1,955 active listings; median AED 870; mean AED 1,187.13; estimated sample revenue AED 13,505,777 | Inspect skew and composition; not audited revenue or a Dubai-wide total |
| Does coverage affect apparent trends? | Five months change by more than 25%; June 2024 increases by 308.77% | Show observation counts and cohorts alongside trends; not proof of market growth |
| Stable cohort versus changing sample? | 989 active in every March 2025–February 2026 month; median AED 756 → 882 versus full-sample AED 721.5 → 870 | Membership changes the comparison; seasonality and survivor bias remain |
| Bedroom segments? | One-bedroom entire homes: 956 active, median AED 725.5; two-bedroom: 524, median AED 1,238.5 | Descriptive segmentation, not causal bedroom value |
| Competitive review workload? | 902 of 1,615 benchmarked listings: 471 above, 431 below; 145 use the 5 km fallback | Review candidates need comparable-quality and real-booking evidence |
| Which listings should be investigated first? | 173 tier-1; 729 comparability-first; 340 coverage investigations; 713 monitor | Transparent managerial triage, not validated pricing benefit |

Historical SQL analysis reconciles **71,960 consecutive active observation pairs** and reports mean, median, and trimmed mean to expose extreme movements.

These findings represent the documented historical sample and previously verified local analytical outputs. They are not newly collected market statistics.

See [Validation Summary](../VALIDATION_SUMMARY.md) for additional verification details. Generated `reports/sql/` analysis outputs remain local and are not required to inspect the included SQLite database.

## Validation and performance

In the previously tested local environment, the database builder validated:

- Primary and foreign keys
- Row counts and domain constraints
- Exact review-queue membership and values
- Monthly coverage and segmentation
- Rejection of an intentionally invalid foreign-key insertion

The SQL validation script checks calendar and domain rules, benchmark suppression and classification, premium arithmetic, and peer-example relationships.

Independent pandas calculations reconcile monthly medians and revenue, adjacent observation-pair keys and changes, **972 segment groups**, quartiles, fixed-cohort membership, and priority assignments.

A separate raw-CSV validator reconstructs **all 70,649 eligible listing-months** without importing the primary peer-matching implementation.

### Query performance

The local `analysis_validation.json` report records execution times.

It compares the median time of ten repeated runs using the month index with a version of the same revenue query that scans the table.

Separately, `09_query_performance.sql` uses `EXPLAIN QUERY PLAN` to inspect how SQLite plans reporting joins. This command shows execution strategy; it does **not** independently measure elapsed execution time.

These results describe the previously tested local environment and do not guarantee identical performance on other computers.

Full-history queries may still require scans and sorting.

Existing primary-key and month indexes support common analytical joins. An unnecessary duplicate index was removed during development.

## Limitations

Listing metadata is not historically versioned, geographic proximity does not establish equivalent amenities or property quality, and provider-estimated performance lacks verified booking-level ground truth. Changes in sample membership can influence historical comparisons.

The five nearest peer examples are illustrative and do not represent the full competitor benchmark population.

The analysis does not establish causal revenue uplift, financial ROI, complete Dubai market coverage, or independently verified Power BI interaction behavior.

The public repository includes the original AirROI source datasets and prepared analytical derivatives. The project's [MIT License](../LICENSE) applies to the author's original licensed code and does not automatically extend to third-party datasets.

Public availability does not independently establish redistribution rights. Applicable source-data licensing terms and permissions should be verified.

Dubai Rental IQ is an independent analytical portfolio project, not an endorsed commercial pricing system.

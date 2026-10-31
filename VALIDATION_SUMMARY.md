# Dubai Rental IQ — Validation Summary

This is the sanitized public evidence summary. It reuses prior audits; packaging did not rerun analytical queries, native acceptance, refreshes or performance recordings. Original detailed evidence remains private.

## Source and analytical evidence

- Historical sample: March 2021–February 2026, 60 months, 99,745 unique listing-month records and 4,364 listings.
- February 2026: 2,471 observed properties; 1,955 active; 1,615 active with eligible benchmarks. The review queue contains 902 cases: 173 stronger-evidence and 729 comparability-review.
- Geography: 1,955 mapped active listings across 1,782 coordinate groups; 452 known-area listings (23.12%), 1,503 Unknown. Source-valid coordinates do not verify addresses.
- A focused audit recorded 45 numerical passes. A separate dated acceptance baseline recorded 16,059 automated passes, zero failures and 633 preservation hashes. These overlapping scopes must not be added together or treated as proof of every subsequent runtime state.
- Earlier Python/SQL work reconciled full eligible peer populations and source-derived aggregates independently. Five Nearest Examples are illustrations, never the benchmark denominator.

## Functional evidence and remaining gaps

Static, native and owner-confirmed results are distinct. Existing native/user evidence covers the six-page journey, Market Lens/month ownership, 902/91 investigation contexts, both Studio selection modes, stale-ID precedence, scoped restores and save/reopen. ArcGIS count sizing is static + user verified; count-driven graduated classes and exact tooltips are not continuous proportional-area symbols.

Residual R04 cases include complete rendered-map group reconciliation, some pan/ranking edges, early-ending/short-history property runtime cases and unspecified remaining checklist edges. They are not silently marked passed. The approved screenshots show a 21/60-month investigation property in Deep Dive; the separately validated 42/60-month property with an 18-month gap is a different test case.

## Performance evidence

Existing Performance Analyzer exports cover all six pages. The following approximate maxima are for individual visual events, not full-page load times, typical response, averages or a controlled benchmark. Lifecycle and DAX maxima may belong to different events; concurrent durations cannot be summed.

| Page | Maximum recorded visual lifecycle | Maximum nested DAX duration |
|---|---:|---:|
| Overview | 6.88 s | 0.19 s |
| Market Trends | 5.65 s | 0.25 s |
| Geography | 6.43 s resumed / 1.35 s earlier | 0.13 s resumed / 0.09 s earlier |
| Investigations | 9.23 s | 0.36 s |
| Pricing Studio | 16.24 s | 0.98 s |
| Property Deep Dive | 2.29 s | 1.03 s |

One Studio event recorded approximately 16.24 s lifecycle, 15.98 s outer Query, 0.05 s nested DAX and 0.18 s Render. Outer Query is not the native DAX category; the remainder after subtracting outer Query and Render is not native Other. A directly observed Analyzer row separately showed 1,550 ms Total = 193 ms DAX + 23 ms Visual display + 1,334 ms Other. Complete per-workflow Display/Other summaries were not preserved; none are invented here.

The owner estimated roughly 6 s for the first map load and 3 s for subsequent updates, considered acceptable; Studio/Investigation interactions were reported quick. Those are manual observations, not instrumented service levels. Cache, hardware, scheduling and network were not controlled; ArcGIS tiles may complete outside recorded visual lifecycle. **No immediate optimization is currently justified.** Diagnose only a repeatable user-facing delay before changing validated logic. This is not a performance certification.

## Methodological limits

R01: geographic labels/coordinates and undated attributes have verification and historical-coverage limits. R02: the provider-derived sample is not a census; occupancy/revenue are estimates, not bookings or realized outcomes. R03: a legacy loose-equality zero-count pattern has a future-null caveat; current checks do not justify silently changing its calculation. Retain missing records, inactive observations and valid zeros as distinct states.

Peer matching does not control for every amenity, quality or capacity difference. Review flags are not proven mispricing; no profitability, adoption, financial uplift or deployment claim is supported. Raw datasets, databases, native recordings and detailed private audit artifacts are excluded.

See [Methodology](docs/METHODOLOGY.md), [Data Dictionary](docs/DATA_DICTIONARY.md), [User Guide](docs/USER_GUIDE.md) and [publication checklist](docs/PUBLICATION_NOTES.md).

## Reproduction corrections — Task F

The standalone `src/08_export_model_imports.py` closes the missing final-import stage. It reads the existing SQLite data/views in read-only mode, derives exact column contracts from saved TMDL, and writes only twelve CSV data files under the configured DataFolder/model. No global builder is imported/executed and no report/model definition is rewritten.

Ten focused synthetic tests pass with zero failures: complete file/type contracts and text IDs; missing database/view; duplicate/missing keys; zero/blank/inactive/gap semantics; invalid columns/integer types; calendar/dimension/coverage consistency; reference-population gate; rollback; unrelated-file and definition-directory protection. An initial Windows cleanup error exposed an unclosed SQLite handle; explicit connection closure fixed it, and the full ten-test rerun passed. Tests do not require provider data.

A separate read-only verification used the existing authorized private SQLite input, exported into a temporary excluded directory, and compared every value in all twelve tables with the existing private model imports after sorting by keys. Columns, row populations, identifiers, nulls/logicals and values matched; floating-point comparison tolerances were 1e-12 relative / 1e-9 absolute. The optional reference gate confirmed 99,745 observations, 4,364 listings, 60 months and the documented February populations. The input database hash stayed unchanged; generated files were temporary and are not packaged.

This establishes final-import equivalence for the current prepared database. It is not a fresh raw-data run, clean dependency installation, independent revalidation of every stored benchmark, or native refresh/save-reopen test of the public copy. Complete Desktop smoke testing after lawful local loading remains pending. The existing 60-month and handoff evidence is preserved, not newly retested here.

H01 (missing exporter), M01 (Python minimum/setup) and L01 (Notebook 07 framing) are addressed in this copy. Python 3.11+ is explicit; Python 3.12.14 is the previously tested environment. Notebook code cells and execution order/counts are unchanged, outputs remain cleared, and only Notebook 07 Markdown was clarified. See [Local Setup](docs/SETUP.md). No optimization or dashboard redesign was performed.

Final package check: 4,245,538 cell values compared across the twelve imports; 14 Python files compiled, eight SQL statements prepared, 91 local references resolved, six screenshots unchanged and all notebook outputs empty. No temporary generated data is published.

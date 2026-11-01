# Dubai Rental IQ — Validation Summary

This document summarizes the historical analytical, functional, performance, and publication validation evidence for Dubai Rental IQ.

The public GitHub repository includes the four original AirROI source datasets, prepared analytical CSV files, SQLite database, twelve Power BI model imports, and saved six-page Power BI report definitions.

The validation results below were recorded during earlier development and publication audits. Subsequent documentation and packaging updates did not constitute a new execution of the complete analytical pipeline, native Power BI acceptance tests, or performance recordings. Certain detailed audit logs, runtime recordings, and temporary validation artifacts remain excluded from the repository.

## Source and analytical evidence

- **Historical sample:** March 2021–February 2026, covering 60 months, 99,745 unique listing-month records, and 4,364 listings.
- **February 2026:** 2,471 observed properties; 1,955 active; 1,615 active with eligible benchmarks. The review queue contains 902 cases: 173 stronger-evidence pricing reviews and 729 comparability-first reviews.
- **Geography:** 1,955 mapped active listings across 1,782 coordinate groups; 452 known-area listings (23.12%) and 1,503 Unknown. Source-valid coordinates do not establish verified addresses.
- **Numerical validation:** A focused audit recorded 45 numerical passes. A separate dated acceptance baseline recorded 16,059 automated passes, zero failures, and 633 preservation hashes. These validation scopes overlap and must not be added together or interpreted as proof of every subsequent runtime state.
- **Independent analytical reconciliation:** Earlier Python and SQL validation independently reconciled full eligible peer populations and source-derived aggregates. The Five Nearest Examples are illustrative records, never the denominator used for peer benchmarks.

These findings describe the supplied historical AirROI-derived sample, not the complete Dubai short-term rental market.

## Functional evidence and remaining gaps

Static verification, native Power BI testing, and owner-confirmed behavior represent distinct forms of evidence.

Existing native and user-confirmed evidence covers:

- The six-page analytical workflow
- Shared Market Lens and reporting-month ownership
- The 902-case investigation queue and 91 investigated contexts
- Both Pricing Studio selection modes
- Precedence of an incoming investigation property over a stale saved lookup ID
- Page-scoped restore actions
- Previously tested save/reopen behavior

ArcGIS count sizing has static and user-confirmed evidence. The map uses count-driven graduated classes rather than continuously proportional-area symbols, and exact listing counts are available through the configured tooltips.

### Remaining functional verification gaps

Residual R04 cases include:

- Complete reconciliation of rendered geographic groups
- Selected map pan and community-ranking edge cases
- Early-ending and short-history property runtime scenarios
- Other unspecified remaining checklist edge cases

These cases are not silently treated as passed.

The approved screenshots show a **21/60-month investigation property** in Property Deep Dive.

The separately validated **42/60-month property with an 18-month observation gap** represents a different test case. The two examples should not be conflated.

## Performance evidence

Existing Power BI Performance Analyzer exports cover all six report pages.

The following approximate maxima are for **individual visual events**, not complete page-load times, typical response times, averages, or controlled performance benchmarks.

Visual lifecycle and nested DAX maxima may refer to different events. Concurrent or nested durations must not be added together.

| Page | Maximum recorded visual lifecycle | Maximum nested DAX duration |
|---|---|---|
| Overview | 6.88 s | 0.19 s |
| Market Trends | 5.65 s | 0.25 s |
| Geography | 6.43 s resumed / 1.35 s earlier | 0.13 s resumed / 0.09 s earlier |
| Investigations | 9.23 s | 0.36 s |
| Pricing Studio | 16.24 s | 0.98 s |
| Property Deep Dive | 2.29 s | 1.03 s |

One Pricing Studio event recorded approximately:

- **16.24 s** visual lifecycle
- **15.98 s** outer Query
- **0.05 s** nested DAX
- **0.18 s** Render

Outer Query is not the native DAX category. The remainder after subtracting outer Query and Render must not be labeled as native Other.

A separately observed Performance Analyzer row recorded:

**1,550 ms Total = 193 ms DAX + 23 ms Visual display + 1,334 ms Other.**

Complete per-workflow Display and Other summaries were not preserved, and no missing measurements are inferred.

### User-observed responsiveness

The project owner estimated approximately six seconds for the initial map load and three seconds for subsequent map updates, which were considered acceptable.

Pricing Studio and Investigations interactions were reported as responsive.

These are manual observations rather than instrumented service-level measurements.

Hardware, caching, scheduling, and network conditions were not controlled. ArcGIS tile loading may also continue outside a recorded visual lifecycle.

**No immediate performance optimization is justified by the available evidence.** A repeatable, user-facing delay should be diagnosed before altering previously validated calculations or interactions.

This evidence is not a performance certification.

## Reproduction corrections — Task F

The standalone `src/08_export_model_imports.py` closes the previously identified missing final-import stage.

It reads the existing SQLite database and views in read-only mode, derives exact column contracts from the saved TMDL definitions, and writes only the twelve CSV data files under the configured `DataFolder/model` directory.

No global report or semantic-model builder is imported or executed, and no saved report or model definition is rewritten.

### Synthetic exporter tests

Ten focused synthetic tests passed with zero failures.

The tests covered:

- Complete file and data-type contracts, including text identifiers
- Missing database and required-view scenarios
- Duplicate and missing keys
- Zero, blank, inactive, and missing-observation semantics
- Invalid columns and integer data types
- Calendar, dimension, and coverage consistency
- Reference-population validation
- Rollback behavior
- Unrelated-file protection
- Protection of report and semantic-model definition directories

An initial Windows cleanup error exposed an unclosed SQLite connection.

Explicit connection closure corrected the issue, and the complete ten-test rerun subsequently passed.

The synthetic tests do not require provider source data.

### Final-import equivalence

A separate read-only verification used the authorized local SQLite reference database, exported the model data into a temporary excluded directory, and compared all values across the twelve generated import tables with the existing reference model imports.

After sorting by keys, the comparison confirmed matching:

- Column structures and data types
- Row populations
- Listing and other text identifiers
- Null and boolean representations
- Analytical values

Floating-point comparison tolerances were:

- Relative: `1e-12`
- Absolute: `1e-9`

The optional reference-population gate confirmed:

| Reference measure | Validated value |
|---|---:|
| Listing-month observations | 99,745 |
| Distinct listings | 4,364 |
| Reporting months | 60 |

The February 2026 reference-population checks also passed.

The input SQLite database hash remained unchanged. Temporary verification files were removed and are not included in the published repository.

The public repository separately includes the intended production SQLite database and twelve model import CSV files.

### What this verification establishes

The historical Task F comparison establishes final-import equivalence for the prepared reference database used in that audit.

It does **not** establish:

- A new end-to-end regeneration directly from all raw source files
- A clean dependency installation on a separate machine
- Independent revalidation of every stored geographic benchmark
- A new native Power BI Desktop refresh or save/reopen acceptance test of the public repository
- Guaranteed behavior across all Power BI Desktop versions

Previously documented 60-month history and property-transfer evidence is retained rather than represented as newly executed testing.

## Resolution of identified publication issues

The original publication audit identified three relevant issues:

| Issue | Original concern | Resolution |
|---|---|---|
| H01 | Missing final Power BI model import exporter | Addressed by `src/08_export_model_imports.py` |
| M01 | Python minimum version and setup documentation | Python 3.11+ requirement documented |
| L01 | Notebook 07 historical intermediate-export framing | Notebook Markdown clarified without altering the analytical workflow |

Python 3.12.14 was the previously tested environment.

The original eight notebooks retained their analytical code and notebook order during the publication preparation.

Their saved outputs were cleared. A subsequent documentation-maintenance update also cleared saved execution counts, so the published notebooks should not be described as retaining their original execution counts.

A later maintenance edit removed a historical `FileNotFoundError` output from Notebook 08 without changing its analytical code. Clearing that saved output is not evidence of a newly successful execution.

No performance optimization or Power BI dashboard redesign was performed as part of these publication corrections.

## Fresh-clone Power BI verification — 1 November 2026

A fresh clone of the public GitHub repository was successfully opened in Power BI Desktop. After configuring `DataFolder` and loading the included CSV imports, the February 2026 KPIs matched the documented reference values (1,955 active listings, AED 870 median nightly rate, and approximately AED 13.51 million estimated revenue). The project remained populated after saving and reopening, and all six dashboard pages were manually confirmed functional. 

## Final historical package verification

The original Task F publication audit recorded the following checks.

| Verification area | Recorded result |
|---|---|
| Power BI model import comparison | 4,245,538 cell values compared across twelve tables |
| Python compilation | 14 Python files compiled |
| SQL static preparation | Eight SQL statements prepared |
| Documentation references | 91 local references resolved |
| Dashboard screenshots | Six screenshots preserved unchanged |
| Notebook saved outputs | Eight notebook publication outputs cleared |
| Model/report definitions | Preserved apart from the intentional blank local `DataFolder` value |

These results belong to the recorded historical audit and should not be treated as evidence that every test was rerun after subsequent GitHub documentation updates.

The public repository contains the intentionally included production datasets and analytical outputs. Temporary verification exports, discarded test artifacts, and other excluded runtime files are not part of the release.

The publication inventory and SHA-256 payload manifest provide additional file-integrity records. Following documentation updates, the corresponding checksum entries must be refreshed to match the published files.

**Overall verification status:** Historical analytical validation retained; fresh-clone Power BI loading, KPI reconciliation, save/reopen and manual six-page verification passed on 1 November 2026. 

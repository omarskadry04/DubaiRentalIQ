# Dubai Rental IQ

**Six connected Power BI workspaces for market monitoring, pricing review and property history.**

Dubai Rental IQ helps an analyst move from a historical market snapshot to a property requiring review, examine its comparable-peer evidence, and inspect its observed performance history. It combines Python preparation and geographic matching, SQLite analysis, and a native Power BI application with an Obsidian Luxury interface.

The dashboard is implemented. Its findings describe an **AirROI-derived sample from March 2021 to February 2026**, not current market conditions, a Dubai rental census, verified bookings or realized income.

## Explore the application

| Workspace | Main question |
|---|---|
| **Overview — Executive Command Center** | What does the selected market segment and reporting month show? |
| **Market Trends & Seasonality** | How do reported rates, estimated performance and sample coverage vary over 60 months? |
| **Geography — Geographic Market Intelligence** | Where are observed listings located, and how do communities compare? |
| **Investigations — Opportunity & Action Center** | Which latest-snapshot pricing-review cases warrant examination? |
| **Competitive Pricing Studio** | How does one explicitly selected property compare with its full eligible peer group? |
| **Property Performance Deep Dive** | How has that property's recorded performance evolved, including missing months? |

The main property workflow is **Investigations → Pricing Studio → confirm listing → Property Deep Dive**. Direct Research provides an alternative entry through Studio. Overview owns the shared Market Lens; page-specific month and property contexts remain separate. See the [User Guide](docs/USER_GUIDE.md).

## Portfolio walkthrough

Read the [portfolio case study](docs/PORTFOLIO_CASE_STUDY.md) for the business problem, engineering decisions, six-page walkthrough and demonstrated skills. The project combines independent source reconciliation, geographic peer benchmarking, explicit property handoffs and honest missing-month evidence.

**Six owner-approved screenshots are available below.** Captions describe the actual captured states; public-use rights and identifier exposure remain subject to owner review.

**Overview → Market Trends → Geography → Investigations → Pricing Studio → Property Deep Dive**

### Executive Command Center

![Executive Command Center with February 2026 market filters, active-listing and estimated-performance KPIs, history and benchmark coverage.](docs/01_executive_command_center.png)

*The executive snapshot establishes the active sample and benchmark coverage before deeper analysis.*

### Market Trends & Seasonality

![Market Trends with nightly-rate history in a scrollable viewport, seasonal bars and contributing-listing counts over the 60-month context.](docs/02_market_trends_seasonality.png)

*Historical rates are read alongside seasonality and changing sample coverage; the main chart has a scrollable viewport.*

### Geographic Market Intelligence

![Dark Dubai ArcGIS map with graduated listing-count markers, coverage KPIs, community comparison, Unknown-area evidence and visible Esri attribution.](docs/03_geographic_market_intelligence.png)

*Source-valid listing locations are mapped without hiding the large Unknown-community share. Esri and map-provider credits remain visible.*

### Opportunity & Action Center

![Investigations showing 902 review cases, priority and direction filters, a selected queue row, Case Preview and Investigate Property action.](docs/04_opportunity_action_center.png)

*The 902-case review queue connects a selected case’s evidence to property investigation.*

### Competitive Pricing Studio

![Pricing Studio showing Investigation Active, a confirmed listing, full-peer benchmark, historical chart, five nearest examples and performance handoff.](docs/05_competitive_pricing_studio.png)

*One property is assessed against full-peer evidence, with history and nearest examples kept distinct.*

### Property Performance Deep Dive

![Property Deep Dive showing 21 of 60 months observed, estimated revenue history, active and inactive observations, missing records and newest-first evidence.](docs/06_property_performance_deep_dive.png)

*The selected property’s revenue history, 21/60 observed months and explicit observation states distinguish missing evidence from recorded zeros.*


## Verified sample findings

These figures reuse the existing numerical audits; they are not new claims of business impact.

| Evidence | Result |
|---|---:|
| Historical records / distinct listings / reporting months | 99,745 / 4,364 / 60 |
| February 2026 observed / active listings | 2,471 / 1,955 |
| February active listings with eligible peer benchmarks | 1,615 |
| Latest pricing-review queue | 902 cases: 173 stronger-evidence and 729 comparability-review |
| February active listings with source-valid coordinates | 1,955 across 1,782 coordinate groups |
| February active listings with known historical area | 452 (23.12%); 1,503 classified Unknown area |

Review signals identify investigation candidates, not proven mispricing. Five Nearest Examples are illustrations; benchmark medians and quartiles use the full eligible peer population. ArcGIS bubbles use graduated listing-count classes, with exact counts in tooltips.

## Architecture and workflow

```text
Four provider source files
  → Python validation, historical facts/dimensions and peer matching
  → SQLite analytical views and independent reconciliation
  → twelve model import CSV files
  → Power BI TMDL semantic model + PBIR report
  → six connected analytical workspaces
```

Python preserves the listing-month grain and computes same-month geographic peer sets. SQL supplies analytical views and review classifications. Power BI provides context-aware measures, synchronized market controls, guarded property handoffs, complete historical calendars and interactive evidence.

The eight [notebooks](notebooks/README.md) explain the analytical pipeline; [SQL documentation](sql/README.md) explains its relational layer. Dependencies are listed in `requirements.txt`; `requirements-lock.txt` records the tested environment and includes platform-specific packages. Earlier pipeline execution evidence is summarized in [Validation Summary](VALIDATION_SUMMARY.md). This dataset-inclusive release adds the four source files, processed analytical outputs, SQLite database and twelve Power BI import CSVs.

## Included data and model inputs

This public dataset-inclusive release includes the following reproducibility assets alongside the code, notebooks, SQL and report definitions:

| Folder | Included assets |
|---|---|
| `data/raw/` | Four original AirROI source files (two CSV and two Parquet) |
| `data/processed/` | Validated SQLite database, five analytical CSVs and two preparation/benchmark manifests |
| `powerbi/data/` | Six intermediate analytical CSVs |
| `powerbi/data/model/` | Twelve CSV tables consumed by the Power BI semantic model |

The report design remains PBIP/PBIR/TMDL rather than a populated PBIX file. These files allow a reader to inspect the prepared data without running the entire pipeline, but **Power BI Desktop may still need a local `DataFolder` parameter and refresh**. Do not confuse the provided source/processed CSVs with an embedded Power BI model cache.

## Open the project safely

The report entry point is [powerbi/DubaiRentalIntelligence.pbip](powerbi/DubaiRentalIntelligence.pbip). Use Power BI Desktop with the existing report/model folders and authorized local imports. Preserve any open unsaved work before switching projects.

**A fresh checkout includes the source datasets, processed data, SQLite database and twelve model import CSVs, but opening the report may still require local Power BI configuration.** The tracked `DataFolder` parameter is intentionally blank, and populated Power BI caches, PBIX files and proprietary native-query libraries are not supplied. Set `DataFolder` to the local `powerbi/data` folder (the parent of `model/`) and load/refresh the report using Power BI Desktop. **Power BI reproducibility:** Successfully tested from a fresh GitHub clone on 1 November 2026, including model loading, KPI reconciliation, save/reopen, and manual verification of all six dashboard pages. See [Validation Summary](VALIDATION_SUMMARY.md).

Do not run the legacy global report or semantic-model generators over the accepted project. They are development artifacts, not a supported way to recreate its final manual formatting and interactions. Documentation work does not require refreshing or rebuilding anything.

## Documentation and evidence

- [Portfolio Case Study](docs/PORTFOLIO_CASE_STUDY.md): problem, architecture, decisions and six-page walkthrough.
- [Publication Notes](docs/PUBLICATION_NOTES.md): included data inventory, exclusions, attribution and redistribution conditions.
- [Local Setup](docs/SETUP.md): Python requirements, included local inputs, pipeline steps and the data-only twelve-file exporter.
- [User Guide](docs/USER_GUIDE.md): navigation, filters, handoffs, restores and missing states.
- [Methodology](docs/METHODOLOGY.md): metric populations, source limitations, peer rules and geography.
- [Data Dictionary](docs/DATA_DICTIONARY.md): saved-model tables, relationships, selectors and important measures.
- [Validation and performance evidence](VALIDATION_SUMMARY.md): dated analytical checks, functional acceptance, owner-confirmed workflows, measured-performance scope and remaining gaps. Internal audit snapshots and backups remain excluded.

Automated/static checks, native execution and owner-confirmed behavior are different evidence categories. Historical assertion totals overlap and must not be added together or treated as proof of every current runtime interaction.

## Limitations and Data Sources

The analysis is based on historical AirROI data covering March 2021 to February 2026 and should not be interpreted as a representation of current Dubai rental market conditions.

Occupancy and revenue figures are provider estimates rather than verified bookings or realized income. Sample composition and data coverage vary over time, while missing observations do not necessarily indicate property inactivity or zero revenue.

Geographic analysis uses available listing coordinates and community classifications, which may contain incomplete or uncertain information. Competitive benchmarking identifies comparable properties based on defined criteria but does not account for every difference in property quality, capacity, amenities, or market positioning.

The resulting insights and pricing-review signals are intended to support exploratory market analysis and informed decision-making, rather than guarantee property performance or investment outcomes.

**Data source:** [AirROI — Airbnb Short-Term Rental Data: Dubai](https://www.kaggle.com/datasets/jasonairroi/airbnb-short-term-rental-data-dubai) | [AirROI Methodology](https://www.airroi.com/data-portal/methodology)


## License and Reproduction

The project's original code is available under the [MIT License](LICENSE). Third-party datasets and assets remain subject to their respective terms.

The repository includes the datasets, processed analytical outputs, and Power BI project files. For installation, Power BI configuration, and reproduction instructions, see the [Local Setup Guide](docs/SETUP.md).

This is an independent portfolio project with no affiliation or endorsement by AirROI or Airbnb.

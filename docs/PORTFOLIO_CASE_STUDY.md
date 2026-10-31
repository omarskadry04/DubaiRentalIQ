# Dubai Rental IQ — Portfolio Case Study

**From a changing rental sample to an explainable property investigation.**

Dubai Rental IQ is a six-workspace Power BI application built on a Python and SQLite analytical pipeline. It helps a property or revenue analyst examine historical market conditions, find pricing-review candidates, compare one property with eligible peers, and inspect its observed performance history without losing context.

The result is a connected analytical product with explicit evidence boundaries. It does not claim business adoption, realized revenue gains, forecasting accuracy or proven mispricing.

## The business problem

A property rate can look unusual because of location, accommodation type, bedroom count, data coverage or genuine differences not captured in the dataset. A citywide average cannot resolve those questions. The project therefore separates three decisions:

1. **Understand the sample:** what is observed in the selected month and market segment?
2. **Prioritize a review:** which properties differ from a sufficiently populated comparable group?
3. **Examine the property:** does the historical record support a useful investigation, and where is evidence missing?

The interface makes these decisions successive steps rather than disconnected dashboards.

## Data and analytical challenges

The AirROI-derived historical sample covers **March 2021–February 2026**, with **99,745 unique listing-month observations, 4,364 listings and 60 reporting months**, according to existing independent audits. Four supplied files contain overlapping history and an undated property snapshot. The pipeline reconciles overlap rather than appending duplicate observations, preserves listing IDs as text, and keeps undated descriptors separate from historical matching attributes.

Coverage matters as much as a metric value. February has **2,471 observed listings, of which 1,955 are active**. Only **452 active listings (23.12%)** have a known historical community label. Coordinates can be source-valid while the community remains Unknown. Missing months, inactive records and valid zero estimates must remain different states.

Occupancy and revenue are provider estimates, not verified bookings or host accounts. These constraints shaped both the calculations and the visible explanations.

## Architecture

```text
Provider source files
  → Python validation and historical preparation
  → geographic peer matching and stored benchmark results
  → SQLite analytical views and independent reconciliation
  → private Power BI imports
  → TMDL semantic model + PBIR report
  → six connected workspaces
```

Python handles source reconciliation, spatial candidate search and benchmark construction. SQLite supplies reusable market, coverage, historical and investigation analyses. Power BI handles filter ownership, page-specific measures, exact property transfers, visualization and explanatory states. The final model stores benchmark fields alongside listing-month observations; it does not perform a new geographic peer search on every click.

The saved project uses the Obsidian Luxury palette, restrained typography and shared sidebar navigation. A central Market Lens supports market exploration, while explicit property identity governs the research pages.

## Explainable peer benchmarking

Peers are other active listings in the **same reporting month, room type and bedroom count**, with valid coordinates and a positive reported rate. Search starts within **2 km** and expands to **5 km** when fewer than ten peers are available. A benchmark remains unavailable if the expanded group still has fewer than ten peers.

Median and quartile evidence use the **full eligible peer population**. Five Nearest Examples are illustrations, not the benchmark denominator. Price deviations of 20% and 35% support review classifications; they do not establish mispricing or prescribe a price change. Quality, amenities and other uncontrolled differences remain limitations.

## Six-page walkthrough and screenshot register

**Screenshot status: six owner-approved images verified from disk.** The images below show the actual supplied states; no image was regenerated or edited. The approved images retain their existing paths directly under `docs/`. Visual approval does not clear third-party rights or the public disclosure of listing IDs. See [Publication Notes](PUBLICATION_NOTES.md#screenshot-capture-and-approval).

**Overview → Market Trends → Geography → Investigations → Pricing Studio → Property Deep Dive**

### 1. Executive Command Center

The starting point combines the shared Market Lens, selected-month KPIs, historical market evidence and benchmark coverage. It gives the analyst a population and context before investigating individual cases.

![Executive Command Center with February 2026 market filters, active-listing and estimated-performance KPIs, history and benchmark coverage.](01_executive_command_center.png)

*The executive snapshot establishes the active sample and benchmark coverage before deeper analysis.*

- **Captured state:** February 2026; all market dimensions. The image shows 1,955 active listings and 2,471 observed properties.
- **Review:** Owner visually approved; owner retention decision recorded; third-party rights remain separate.

### 2. Market Trends & Seasonality

A local metric selector connects monthly history, seasonal patterns and contributor evidence. The 60-month timeline remains independent of Overview's selected reporting month. Seasonal values are medians of valid year-month medians, not causal estimates.

![Market Trends with nightly-rate history in a scrollable viewport, seasonal bars and contributing-listing counts over the 60-month context.](02_market_trends_seasonality.png)

*Historical rates are read alongside seasonality and changing sample coverage; the main chart has a scrollable viewport.*

- **Captured state:** All market dimensions; Nightly rate. The context states March 2021–February 2026 and 60 contributing months; the scrollable main chart viewport ends at January 2025 in this image.
- **Review:** Owner visually approved; owner retention decision recorded; third-party rights remain separate.

### 3. Geographic Market Intelligence

The ArcGIS map groups source coordinates and uses active listings at each location for graduated bubble size and exact tooltips. Community comparisons retain Unknown coverage, metric-specific minimum contributors and smaller communities in the evidence table.

![Dark Dubai ArcGIS map with graduated listing-count markers, coverage KPIs, community comparison, Unknown-area evidence and visible Esri attribution.](03_geographic_market_intelligence.png)

*Source-valid listing locations are mapped without hiding the large Unknown-community share. Esri and map-provider credits remain visible.*

- **Captured state:** February 2026; all dimensions. The image shows 1,955 active listings, 100.0% source-valid mapped share, 23.12% known-area share and 1,503 Unknown-area listings.
- **Review:** Owner visually approved; owner retention decision recorded; third-party rights remain separate.

### 4. Opportunity & Action Center

Evidence Priority and Pricing Direction narrow the latest-snapshot queue. Selecting a case updates Case Preview and enables the exact property handoff to Studio. Review signals remain visibly distinct from proven pricing errors.

![Investigations showing 902 review cases, priority and direction filters, a selected queue row, Case Preview and Investigate Property action.](04_opportunity_action_center.png)

*The 902-case review queue connects a selected case’s evidence to property investigation.*

- **Captured state:** February 2026; All review cases and Both directions. The image shows 902 cases, including 173 stronger-evidence and 729 comparability-review cases, with one selected case.
- **Review:** Owner visually approved; owner retention decision recorded; third-party rights remain separate.

### 5. Competitive Pricing Studio

Studio compares one authoritative property with its full eligible peers and retains separate historical evidence. Investigation Active takes precedence over stale lookup selections. Direct Research supports an explicit listing and research month. The confirmation row makes the next handoff deliberate.

![Pricing Studio showing Investigation Active, a confirmed listing, full-peer benchmark, historical chart, five nearest examples and performance handoff.](05_competitive_pricing_studio.png)

*One property is assessed against full-peer evidence, with history and nearest examples kept distinct.*

- **Captured state:** Investigation Active for the same case as Investigations; February 2026. The image shows AED 7.03K rate, AED 538.50 full-peer median and 82 peers; confirmation row and nearest examples are visible.
- **Review:** Owner visually approved; owner retention decision recorded; third-party rights remain separate.

### 6. Property Performance Deep Dive

The transferred property is evaluated across the complete reporting calendar. All latest KPI values come from the same latest observed month. A disconnected calendar and segmented series preserve missing months, while the ledger distinguishes active, inactive and absent observations.

![Property Deep Dive showing 21 of 60 months observed, estimated revenue history, active and inactive observations, missing records and newest-first evidence.](06_property_performance_deep_dive.png)

*The selected property’s revenue history, 21/60 observed months and explicit observation states distinguish missing evidence from recorded zeros.*

- **Captured state:** The same investigation property, first observed June 2024 and latest February 2026; Est. revenue selected and 21/60 observed months. The latest record shows AED 7.03K rate, 0.0% estimated occupancy and AED 0.00 estimated revenue. This is not the separately validated 42/60-month gap example.
- **Review:** Owner visually approved; owner retention decision recorded; third-party rights remain separate.

Image QA findings and publication gates are in [Publication Notes](PUBLICATION_NOTES.md#screenshot-capture-and-approval).

## The connected property workflow

**Choose case → review preview → Investigate Property → inspect Studio evidence → select confirmation row → View Property Performance.**

The transfer carries one explicit listing identity. It does not silently replace the selected property with a stale Direct Research selection or allow the Studio comparison month to truncate Deep Dive history. The supported Open Pricing Studio return action and page-specific restores preserve the intended workflow. See the [User Guide](USER_GUIDE.md) for exact controls and Desktop Ctrl+click behavior.

## Verified findings and engineering evidence

| Finding | Interpretation |
|---|---|
| 1,615 of 1,955 February active listings have eligible benchmarks | Benchmark availability is a coverage condition, not a quality guarantee |
| 902 review cases: 173 stronger-evidence + 729 comparability-review | A defensible review workload, not 902 proven pricing mistakes |
| 1,955 mapped active listings across 1,782 coordinate groups | Co-located observations must contribute to count weighting |
| 1,503 active listings have Unknown area | Named-community comparisons cover a limited subset |
| Five-example median differs from the full benchmark by over 20% for 530 latest-month subjects | Nearest examples cannot replace full-peer evidence |

Existing validation includes independent peer reconstruction, source/model reconciliation and native workflow testing. The dated acceptance audit records **16,059 automated passes and zero failures**, and the focused data-quality audit records **45 numerical passes**. These are separate, overlapping scopes, not a combined total or a blanket runtime guarantee. Owner-confirmed workflows supplement native/static evidence; residual cases remain pending.

Performance Analyzer recordings cover all six pages. The analysis separates nested DAX execution, visual rendering and waiting/coordination. Individual visual-lifecycle outliers are not whole-page response times or proof of a repeatable user delay. Owner observations accepted the map's approximate initial/subsequent loading experience; **no immediate optimization is currently justified**. Measurement limitations remain in the evidence register in [Publication Notes](PUBLICATION_NOTES.md#validation-evidence).

## Technical challenges and skills demonstrated

| Challenge | Implemented approach | Skills demonstrated |
|---|---|---|
| Overlapping sources and undated metadata | Reconcile keys/values, retain provenance, avoid historical backfill | Python data engineering, data quality and temporal reasoning |
| Geographic comparability | Spatial candidate retrieval, Haversine distance, minimum peer counts and deterministic examples | Geospatial analytics and explainable benchmarking |
| Different page contexts | Central market controls, independent latest-snapshot review and explicit property guards | Power BI modeling, DAX filter-context design and UX architecture |
| Historical gaps and latest values | Full calendar, segmented series, same-record KPI selection and explicit observation states | Time-series semantics and analytical QA |
| Reset and handoff regressions | Scoped bookmarks, guarded confirmation and native workflow validation | Integration testing and application-state discipline |
| Perceived versus measured delay | Analyzer exports separated from owner estimates; no speculative optimization | Performance diagnosis and evidence-based tradeoffs |

## Limitations and responsible presentation

This is a historical provider-derived sample, not a Dubai census. Estimated occupancy/revenue are not verified bookings or financial outcomes. Coordinates are not independently verified addresses or community boundaries; graduated marker classes are not continuous proportional-area symbols. Peer matching omits quality and amenity differences. Missing months are not proof of closure.

R01–R03 limitations and residual R04 edge cases remain documented, including future-null zero-count behavior and incomplete rendered-population/edge-case verification. Dataset redistribution and ArcGIS screenshot rights are unresolved. No financial uplift, adoption, deployment, forecasting or universal acceptance claim is made.

Explore the [Methodology](METHODOLOGY.md), [Data Dictionary](DATA_DICTIONARY.md), [User Guide](USER_GUIDE.md) and [publication checklist](PUBLICATION_NOTES.md). Source: [AirROI Dubai dataset on Kaggle](https://www.kaggle.com/datasets/jasonairroi/airbnb-short-term-rental-data-dubai); no endorsement implied.

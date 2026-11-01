# Dubai Rental IQ — Power BI application

The saved Power BI Project (PBIP) contains six implemented analytical pages plus a hidden occupancy-tooltip page. The current report definitions and accepted manual edits are authoritative. This guide documents the completed Power BI application, its navigation, data configuration, and analytical interpretation.

## Getting started — open the included data in Power BI

**What the published dataset-inclusive release provides:** The public repository includes four original AirROI source files in `data/raw/`, the prepared SQLite database and analytical CSVs in `data/processed/`, six intermediate CSVs in `powerbi/data/`, and **twelve model import CSVs** in `powerbi/data/model/`.

The PBIP contains the six report pages and saved semantic-model definitions, but **not a loaded Power BI model cache or populated PBIX**. On a new computer, dashboards may initially be empty or prompt for data until `DataFolder` is configured and the model is refreshed.

**Data provenance and licensing:** The public repository includes original AirROI source files and their prepared analytical derivatives. The project's MIT License applies to the author's original licensed code and does not automatically extend to third-party datasets or assets. Public availability does not independently establish redistribution rights.

Original data source: [AirROI — Airbnb Short-Term Rental Data: Dubai](https://www.kaggle.com/datasets/jasonairroi/airbnb-short-term-rental-data-dubai).

### Open with the included model imports

1. Download or clone the repository, preserving `powerbi/DubaiRentalIntelligence.pbip` alongside the `DubaiRentalIntelligence.Report` and `DubaiRentalIntelligence.SemanticModel` directories.

2. Use a compatible version of Power BI Desktop on Windows that supports the saved PBIP, PBIR, and TMDL project formats.

3. Open `powerbi/DubaiRentalIntelligence.pbip` in Power BI Desktop. If prompted about missing data or connection parameters, continue with the existing project's parameter configuration rather than recreating the report.

4. In **Power Query / Manage Parameters**, set the existing `DataFolder` parameter to the **absolute path of your local `powerbi/data` directory**, which is the parent of `model/`—not the `model/` folder itself.

   For example:

   ```text
   C:\Projects\DubaiRentalIQ\powerbi\data
   ```

   The committed parameter is intentionally blank to avoid storing a machine-specific path.

5. Apply the parameter change and refresh or load the semantic model using Power BI Desktop's supported workflow. The twelve model CSVs should be read from `powerbi/data/model/`.

6. Check the page-level data and interactions after the refresh. ArcGIS visuals may additionally require supported external service access and permissions.

The exact first-open prompts may vary between Power BI Desktop versions.

**Fresh-clone verification (1 November 2026):** The Power BI project was successfully opened from a fresh GitHub clone, populated using the included CSV imports, and saved and reopened with data retained. The February 2026 headline KPIs matched the reference results, and all six dashboard pages were manually confirmed functional. 
### Regenerate the data (optional)

The supplied final CSV imports mean users should **not need to rerun the Python pipeline merely to attempt a Power BI refresh**.

To regenerate or independently audit the data, consult [Local Setup](../docs/SETUP.md) and the [Analytical Notebook Guide](../notebooks/README.md).

The pipeline uses these four included source files under `data/raw/`:

- `past_rates.csv`
- `listings_monthly.csv`
- `past_rates.parquet`
- `listings.parquet`

After the documented preparation, peer-benchmarking, and SQLite stages, run the data-only model exporter from the repository root:

```powershell
python src/08_export_model_imports.py --expect-reference
```

This exporter validates and produces the twelve import CSVs under `powerbi/data/model/`.

Its reference check requires the audited historical input population. Different source datasets may legitimately fail the reference-population check.

Do not bypass that requirement without understanding the resulting analytical differences.

For the complete regeneration sequence and optional automated tests, see [Local Setup](../docs/SETUP.md).

## Opening requirements

Open `DubaiRentalIntelligence.pbip` in Power BI Desktop with its sibling report and semantic-model directories intact.

Preserve unsaved Desktop work before opening another copy, and avoid overwriting the finalized report with temporary test selections.

The complete definition set includes an intentionally empty `DataFolder` parameter while preserving its lineage and other model metadata.

Point this parameter to your local `powerbi/data` directory and use the included CSV files under `powerbi/data/model/`.

Do not commit your computer-specific parameter value.

Native DAX audit utilities depend on separately available compatible libraries. These libraries are not required merely to read the documentation and are not redistributed with the repository.

The global report and semantic-model builders are intentionally not included. Do not use older copies of these builders to regenerate the finalized application.

Older build and design documents are retained only as historical references, not instructions to rebuild accepted pages.

Reading the documentation requires no model refresh, settings changes, or Microsoft/Esri permission changes.

**Opening and populating the interactive report**, by contrast, requires the local data connection and may require a semantic-model refresh.

ArcGIS rendering requires supported external services and appropriate permissions; offline map functionality is not guaranteed.

## Six workspaces and context ownership

| Sidebar destination / page | Context and purpose |
|---|---|
| **Overview / Executive Command Center** | Central Area, Accommodation, Bedrooms and Reporting Month controls; active-sample KPIs, market history and benchmark coverage. Its historical visual retains history through configured interactions. |
| **Market Trends / Market Trends & Seasonality** | Inherited market dimensions; full March 2021–February 2026 timeline, local metric, seasonality and contributor evidence. Overview's selected month is not synchronized here. |
| **Geography / Geographic Market Intelligence** | Inherited dimensions and Overview focus month; ArcGIS grouped locations, coverage KPIs, community comparison and evidence. Requires one month. |
| **Investigations / Opportunity & Action Center** | Inherited market dimensions; latest classified February 2026 snapshot. Local Evidence Priority and Pricing Direction; queue and Case Preview. |
| **Pricing Studio / Competitive Pricing Studio** | Explicit property and independent comparison context. Investigation Active takes priority over stale Direct Research selections. Full peers, property history and latest-only Five Nearest Examples. |
| **Property Deep Dive / Property Performance Deep Dive** | Explicit transferred property; disconnected 60-month calendar, latest-observed KPIs, historical metrics, coverage matrix and monthly ledger. |

All six destinations remain in the sidebar.

Ordinary navigation is not a substitute for a property-transfer action.

**Investigate Property** and **View Property Performance** carry guarded property context. Pricing Studio's confirmation-row selection remains required.

Deep Dive's **Open Pricing Studio** is the supported property-return action.

See the step-by-step [User Guide](../docs/USER_GUIDE.md) for the full interaction workflow.

## Controls and restores

Overview is the only visible editor of the shared Market Lens.

Hidden synchronized instances on the market pages implement filter inheritance. Pricing Studio and Deep Dive do not participate in those synchronization groups.

Local metric selectors remain independent.

Geography's selected metric affects community comparison, not the map's listing-count meaning.

| Restore action | Existing behavior to preserve |
|---|---|
| **Overview** | Restores its saved February 2026 executive/default context. Its global selections can propagate to the intended synchronized pages; it is not a local-only market reset. |
| **Market Trends** | Restores local metric/chart state while preserving inherited dimensions. |
| **Geography** | Restores local metric, map, ranking and evidence state; preserves shared dimensions and focus month, including ranking eligibility. |
| **Investigations** | Resets local Priority, Direction and queue selection, not the shared Market Lens. |
| **Pricing Studio** | Resets Studio research controls and clears inbound investigation context according to its existing bookmark behavior. Use it to return to Direct Research. |
| **Deep Dive** | Restores estimated occupancy and local visual state, including newest-first evidence order, while preserving the selected property. |

**Clear filters is not equivalent to Restore Overview.**

Clearing slicers may remove the unique focus month. Re-select one month before interpreting a geographic snapshot.

In Power BI Desktop edit mode, **Ctrl+click** activates navigation and action buttons. Select slicer values and confirmation rows using a normal click.

## Interpretation and evidence

### Market and revenue interpretation

Overview's estimated revenue is an active-sample sum.

Market Trends and Geography revenue comparisons use medians per listing.

Deep Dive presents recorded provider-derived values for one property. Its first three KPI cards all refer to that property's same latest observed month, even if the property was inactive or the latest observation predates February 2026.

These measures should not be interpreted as equivalent aggregations across different report pages.

### Geographic interpretation

The ArcGIS map uses the existing latitude and longitude data, `Geo Coordinate Pair`, and `Geo Mapped Listings` in Size and Tooltips.

Count-driven graduated map classes are not a continuous proportional-area scale.

Listings with unknown community labels but valid coordinates remain included in the geographic evidence.

Named-community ranking requires at least ten valid contributors to the selected metric and excludes Unknown from the named ranking.

The evidence table retains Unknown-area observations.

### Analytical definitions

Refer to the following documentation for calculation definitions, coverage treatment, peer eligibility and known limitations:

- [Methodology](../docs/METHODOLOGY.md)
- [Data Dictionary](../docs/DATA_DICTIONARY.md)
- [Validation Summary](../VALIDATION_SUMMARY.md)
- [User Guide](../docs/USER_GUIDE.md)

Earlier starter DAX, generated catalogs and design blueprints are incomplete historical references.

The current TMDL definitions are authoritative for calculations, while the current PBIR definitions are authoritative for visual bindings and interactions.

## Publication status and verification boundaries

This documentation describes the **published dataset-inclusive release** and its saved Power BI project definitions.

The fresh-clone verification confirms successful Power BI loading and save/reopen in the tested environment. 

Previously recorded native tests, owner-confirmed workflows and static verification results remain distinct forms of evidence.

The published repository contains source data, prepared analytical tables and model-ready imports, but a reader must still configure the local data parameter and load the semantic model to use the interactive Power BI report.

The project is an independent analytical portfolio implementation, not an endorsed product or hosted Power BI service.

Third-party dataset and mapping assets remain subject to their applicable licensing terms. Public repository availability does not independently establish rights to redistribute or reuse those assets.

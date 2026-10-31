# Dubai Rental IQ — Power BI application

The saved PBIP contains six implemented analytical pages plus a hidden occupancy-tooltip page. The current report definitions and accepted manual edits are authoritative. This guide replaces earlier unfinished-page and rebuild instructions.

## Getting started — open the included data in Power BI

**What the data-inclusive release provides:** The repository includes the four source data files in `data/raw/`, the prepared SQLite database and analytical CSVs in `data/processed/`, six intermediate CSVs in `powerbi/data/`, and **twelve model import CSVs** in `powerbi/data/model/`. The PBIP contains the six report pages and saved semantic-model definitions, but **not a loaded Power BI model cache or populated PBIX**. On a new computer, the dashboards may initially be empty or prompt for data until `DataFolder` is configured and the model is refreshed.

**Before publishing the data-inclusive revision:** Confirm redistribution authorization for the four original AirROI files **and their row-level derivatives**. The existing MIT code license does not grant dataset redistribution rights. Source: [AirROI — Airbnb Short-Term Rental Data: Dubai](https://www.kaggle.com/datasets/jasonairroi/airbnb-short-term-rental-data-dubai).

### Open with the included model imports

1. Download or clone the entire repository, preserving `powerbi/DubaiRentalIntelligence.pbip` beside its sibling report and semantic-model directories.
2. Use a compatible version of Power BI Desktop on Windows that supports the saved PBIP/PBIR/TMDL project formats.
3. Open `powerbi/DubaiRentalIntelligence.pbip` in Power BI Desktop. If prompted about missing data or connection parameters, continue with the existing project's parameter configuration; do not recreate the report.
4. In **Power Query / Manage Parameters**, set the existing `DataFolder` parameter to the **absolute path of your local `powerbi/data` directory**, which is the parent of `model/`—**not** the `model/` folder itself. The committed parameter is intentionally blank to avoid shipping a machine-specific path.
5. Apply the parameter change and refresh/load the semantic model using Power BI Desktop's supported workflow. The twelve import CSVs should be read from `powerbi/data/model/`.
6. Check the page-level data and interactions after the refresh. ArcGIS visuals may additionally require supported external service access and permissions.

The exact first-open prompts may vary across Power BI Desktop versions. **A clean-clone Desktop refresh has not yet been independently verified**, so the screenshots in the main README remain documented examples of the previously accepted local report, not a guarantee of zero-configuration opening on another machine.

### Regenerate the data (optional)

The supplied final CSV imports mean a reader should **not need to rerun the Python pipeline just to attempt a Power BI refresh**. To regenerate or audit them instead, use [Local Setup](../docs/SETUP.md) and [the notebook guide](../notebooks/README.md). The pipeline expects these exact source filenames in `data/raw/`:

- `past_rates.csv`
- `listings_monthly.csv`
- `past_rates.parquet`
- `listings.parquet`

After the documented preparation, peer-benchmark and SQLite stages, run from the repository root:

```powershell
python src/08_export_model_imports.py --expect-reference
```

This data-only exporter validates and produces the twelve import CSVs under `powerbi/data/model/`. Its reference check requires the audited historical input population; differing datasets can cause a legitimate check failure. Do not bypass that requirement without understanding the resulting differences. For the complete sequence and optional automated checks, see [Local Setup](../docs/SETUP.md).

## Opening requirements

Open `DubaiRentalIntelligence.pbip` in Power BI Desktop with its sibling report and semantic-model directories intact. Preserve unsaved Desktop work before opening another copy, and do not overwrite production with temporary test selections.

The complete definition set includes an intentionally empty `DataFolder` parameter, preserving its lineage and other metadata. Point it to your **local** `powerbi/data` folder and use the included `powerbi/data/model/` CSVs as documented above. Do not commit your computer-specific parameter value. Native DAX audit utilities depend on separately available compatible libraries; those are not required merely to read documentation and are not redistributed. No clean-clone native execution is promised by this documentation.

The global report and semantic-model builders are intentionally not included; do not use older copies to regenerate the finalized application. Older build/design documents are historical references, not instructions to regenerate accepted pages. Opening documentation requires no model refresh, settings changes or Microsoft/Esri permission changes. **Opening and populating the report**, by contrast, requires the local data connection and may require a refresh. ArcGIS rendering requires its supported external service and previously accepted permissions; this is not an offline map guarantee.

## Six workspaces and context ownership

| Sidebar destination / page | Context and purpose |
|---|---|
| **Overview / Executive Command Center** | Central Area, Accommodation, Bedrooms and Reporting Month controls; active-sample KPIs, market history and benchmark coverage. Its historical visual retains history through configured interactions. |
| **Market Trends / Market Trends & Seasonality** | Inherited market dimensions; full March 2021–February 2026 timeline, local metric, seasonality and contributor evidence. Overview's selected month is not synchronized here. |
| **Geography / Geographic Market Intelligence** | Inherited dimensions and Overview focus month; ArcGIS grouped locations, coverage KPIs, community comparison and evidence. Requires one month. |
| **Investigations / Opportunity & Action Center** | Inherited market dimensions; latest classified February 2026 snapshot. Local Evidence Priority and Pricing Direction; queue and Case Preview. |
| **Pricing Studio / Competitive Pricing Studio** | Explicit property and independent comparison context. Investigation Active takes priority over stale Direct Research selections. Full peers, property history and latest-only Five Nearest Examples. |
| **Property Deep Dive / Property Performance Deep Dive** | Explicit transferred property; disconnected 60-month calendar, latest-observed KPIs, historical metrics, coverage matrix and monthly ledger. |

All six destinations remain in the sidebar. Ordinary navigation is not a substitute for a property-transfer action. **Investigate Property** and **View Property Performance** carry guarded property context. Studio's confirmation-row selection remains required. Deep Dive's **Open Pricing Studio** is the supported property-return action. See the step-by-step [User Guide](../docs/USER_GUIDE.md).

## Controls and restores

Overview is the only visible editor of the shared Market Lens. Hidden synchronized instances on market pages implement inheritance; Studio and Deep Dive do not join those sync groups. Local metric selectors are independent. Geography's metric affects community comparison, not the map's listing-count meaning.

| Restore action | Existing behavior to preserve |
|---|---|
| **Overview** | Restores its saved February 2026 executive/default context. Its global selections can propagate to the intended synchronized pages; it is not a local-only market reset. |
| **Market Trends** | Restores local metric/chart state while preserving inherited dimensions. |
| **Geography** | Restores local metric/map/ranking/evidence state; preserves shared dimensions and focus month, including ranking eligibility. |
| **Investigations** | Resets local Priority, Direction and queue selection, not the shared Market Lens. |
| **Pricing Studio** | Resets Studio research controls and clears inbound investigation context according to its existing bookmark behavior. Use it to return to Direct Research. |
| **Deep Dive** | Restores Est. occupancy and local visual state, including newest-first evidence order, while preserving the selected property. |

**Clear filters** is not the same as **Restore Overview**: clearing slicers can remove the unique focus month. Re-select one month before interpreting a geographic snapshot. In Desktop edit mode, **Ctrl+click** activates buttons; select slicer values and confirmation rows normally.

## Interpretation and evidence

Overview estimated revenue is an active-sample sum. Market Trends and Geography revenue comparisons are medians per listing. Deep Dive values are recorded values for one property; its first three KPI cards all use that property's same latest observed month, even if inactive or earlier than February 2026.

The ArcGIS map uses existing latitude/longitude, `Geo Coordinate Pair`, and `Geo Mapped Listings` in Size and Tooltips. Count-driven graduated classes are not a continuous proportional-area scale. Unknown-area listings with valid coordinates remain included. Named-community ranking requires at least ten selected-metric contributors and excludes Unknown; the evidence table retains it.

See the [Methodology](../docs/METHODOLOGY.md), current [Data Dictionary](../docs/DATA_DICTIONARY.md), data-quality reconciliation and canonical performance audit. Earlier starter DAX, generated catalogs and design blueprints are incomplete historical references. Current TMDL is authoritative for calculations; current PBIR is authoritative for bindings and interactions.

This documentation revision reflects the **planned data-inclusive release** and the saved project definitions; it does not certify a new native Desktop refresh or resolve residual runtime edge cases. Owner-confirmed workflows and previously recorded native tests remain explicitly distinguished from static checks. Confirm third-party data redistribution rights and applicable ArcGIS screenshot/public-display rights before publishing new files. This independent portfolio project is not an endorsed product or hosted Power BI service.

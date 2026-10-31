# Dubai Rental IQ — Power BI application

The saved PBIP contains six implemented analytical pages plus a hidden occupancy-tooltip page. The current report definitions and accepted manual edits are authoritative. This guide replaces earlier unfinished-page and rebuild instructions.

## Getting started — obtain the dataset and connect Power BI

**Why the report opens without data:** This public-release Power BI project includes the report pages and semantic-model definitions, but **not** the source dataset, generated model import files, or populated model cache. The dashboard screenshots in the [main README](../README.md) show the completed report using locally prepared data. A fresh download of this Power BI project will not show those results automatically.

1. **Get the source data.** Visit [AirROI — Airbnb Short-Term Rental Data: Dubai on Kaggle](https://www.kaggle.com/datasets/jasonairroi/airbnb-short-term-rental-data-dubai). Check the dataset's access conditions and usage rights before downloading. The preparation workflow expects these four files with these exact names:
   - `past_rates.csv`
   - `listings_monthly.csv`
   - `past_rates.parquet`
   - `listings.parquet`
2. **Place the files locally.** Extract the downloaded data and place the four files in `data/raw/` under the repository root. Do **not** add the downloaded files to the public GitHub repository. Confirm that the files you obtained correspond to the historical source version used by the project; a newer or different dataset version may produce different results or fail reference checks.
3. **Prepare the data.** From the repository root, follow [Local Setup](../docs/SETUP.md) to install Python dependencies and run the data preparation, competitor comparison, and SQL steps in their documented order. The [notebooks guide](../notebooks/README.md) explains the notebook workflow.
4. **Generate the Power BI imports.** After the required intermediate data exists, run:

   ```bash
   python src/08_export_model_imports.py --expect-reference
   ```

   This generates twelve import CSV files in the configured local output location. The reference check can fail if the inputs are not the same version as those used for the original audit; follow the setup guide rather than bypassing the check silently.
5. **Connect a local working copy in Power BI Desktop.** Keep `DubaiRentalIntelligence.pbip` beside its `.Report` and `.SemanticModel` folders. Open the project, set the blank **`DataFolder`** parameter to the folder **containing** `model/` (default: `powerbi/data`, not `powerbi/data/model`), and load the prepared data according to [Local Setup](../docs/SETUP.md). Do not commit your computer-specific parameter value or generated data files.

**What to expect:** The published project is suitable for inspecting the report structure and model definitions without the dataset. To explore populated dashboards interactively, you need lawful access to compatible source files and must complete the local preparation steps. A fresh-clone, end-to-end reproduction has **not** been independently verified, and the dataset provider may change file availability or terms. The project does not redistribute AirROI data or grant third-party usage rights.

## Opening requirements

Open [DubaiRentalIntelligence.pbip](DubaiRentalIntelligence.pbip) in Power BI Desktop with its sibling `.Report` and `.SemanticModel` folders intact. Use the existing authorized local environment; preserve unsaved Desktop work before opening another copy. Do not overwrite production with temporary test selections.

The complete definition set includes an intentionally empty `DataFolder` parameter, preserving its lineage and other metadata. Follow the dataset and import instructions above before attempting to populate a local working copy. Native DAX audit utilities depend on separately available compatible libraries; those are not required merely to read documentation and are not redistributed. No clean-clone execution is promised by this documentation.

The global report and semantic-model builders are intentionally not included; do not use older copies to regenerate the finalized application. Older build/design documents are historical references, not instructions to regenerate accepted pages. Opening documentation requires no model refresh, settings changes or Microsoft/Esri permission changes. ArcGIS rendering requires its supported external service and previously accepted permissions; this is not an offline map guarantee.

## Six workspaces and context ownership

| Sidebar destination / page | Context and purpose |
|---|---|
| Overview / Executive Command Center | Central Area, Accommodation, Bedrooms and Reporting Month controls; active-sample KPIs, market history and benchmark coverage. Its historical visual retains history through configured interactions. |
| Market Trends / Market Trends & Seasonality | Inherited market dimensions; full March 2021–February 2026 timeline, local metric, seasonality and contributor evidence. Overview's selected month is not synchronized here. |
| Geography / Geographic Market Intelligence | Inherited dimensions **and** Overview focus month; ArcGIS grouped locations, coverage KPIs, community comparison and evidence. Requires one month. |
| Investigations / Opportunity & Action Center | Inherited market dimensions; latest classified February 2026 snapshot. Local Evidence Priority and Pricing Direction; queue and Case Preview. |
| Pricing Studio / Competitive Pricing Studio | Explicit property and independent comparison context. Investigation Active takes priority over stale Direct Research selections. Full peers, property history and latest-only Five Nearest Examples. |
| Property Deep Dive / Property Performance Deep Dive | Explicit transferred property; disconnected 60-month calendar, latest-observed KPIs, historical metrics, coverage matrix and monthly ledger. |

All six destinations remain in the sidebar. Ordinary navigation is not a substitute for a property-transfer action. **Investigate Property** and **View Property Performance** carry guarded property context. Studio's confirmation-row selection remains required. Deep Dive's **Open Pricing Studio** is the supported property-return action. See the [step-by-step User Guide](../docs/USER_GUIDE.md).

## Controls and restores

Overview is the only visible editor of the shared Market Lens. Hidden synchronized instances on market pages implement inheritance; Studio and Deep Dive do not join those sync groups. Local metric selectors are independent. Geography's metric affects community comparison, not the map's listing-count meaning.

| Restore action | Existing behavior to preserve |
|---|---|
| Overview | Restores its saved February 2026 executive/default context. Its global selections can propagate to the intended synchronized pages; it is not a local-only market reset. |
| Market Trends | Restores local metric/chart state while preserving inherited dimensions. |
| Geography | Restores local metric/map/ranking/evidence state; preserves shared dimensions and focus month, including ranking eligibility. |
| Investigations | Resets local Priority, Direction and queue selection, not the shared Market Lens. |
| Pricing Studio | Resets Studio research controls and clears inbound investigation context according to its existing bookmark behavior. Use it to return to Direct Research. |
| Deep Dive | Restores Est. occupancy and local visual state, including newest-first evidence order, while preserving the selected property. |

**Clear filters is not the same as Restore Overview:** clearing slicers can remove the unique focus month. Re-select one month before interpreting a geographic snapshot. In Desktop edit mode, Ctrl+click activates buttons; select slicer values and confirmation rows normally.

## Interpretation and evidence

Overview estimated revenue is an active-sample **sum**. Market Trends and Geography revenue comparisons are **medians per listing**. Deep Dive values are recorded values for one property; its first three KPI cards all use that property's same latest observed month, even if inactive or earlier than February 2026.

The ArcGIS map uses existing latitude/longitude, `Geo Coordinate Pair`, and `Geo Mapped Listings` in Size and Tooltips. Count-driven graduated classes are not a continuous proportional-area scale. Unknown-area listings with valid coordinates remain included. Named-community ranking requires at least ten selected-metric contributors and excludes Unknown; the evidence table retains it.

See the [Methodology](../docs/METHODOLOGY.md), [current Data Dictionary](../docs/DATA_DICTIONARY.md), [data-quality reconciliation](../VALIDATION_SUMMARY.md) and [canonical performance audit](../VALIDATION_SUMMARY.md). Earlier starter DAX, generated catalogs and design blueprints are incomplete historical references. Current TMDL is authoritative for calculations; current PBIR is authoritative for bindings and interactions.

This documentation revision checked saved definitions only. It did not repeat native acceptance, refresh data or close residual runtime edge cases. Owner-confirmed workflows and previously recorded native tests remain explicitly distinguished from static checks. Data redistribution and ArcGIS screenshot rights still require separate verification.

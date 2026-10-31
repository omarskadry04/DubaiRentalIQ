# Local setup and reproducibility

The completed six-page report is supplied as PBIP/PBIR/TMDL definitions. This guide describes the **proposed data-inclusive release**, staged locally but not yet published. The release is intended to include the four AirROI source files, prepared SQLite and CSV outputs, and twelve Power BI model import CSVs. It does **not** contain a populated Power BI model cache or an immediately interactive PBIX file. Publishing source and row-level derived data requires explicit redistribution authorization; until confirmed, keep those assets out of the public GitHub history. This is an independent portfolio project with no implied affiliation or endorsement.

## Python and dependencies

Use **Python 3.11 or newer**. Python **3.12.14** was the existing audit/test environment; a fresh installation has **not** been tested. Python 3.11 is the minimum because the pipeline uses `hashlib.file_digest`. Power BI Desktop requires a compatible Windows installation with support for PBIP/PBIR/TMDL and permitted ArcGIS access. No particular fresh Desktop installation is certified here.

Example commands from the repository root, using PowerShell after installing a suitable CPython interpreter:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` defines supported package ranges. `requirements-lock.txt` records an earlier Windows-oriented pinned environment, including platform-specific packages; it is not a universal cross-platform lock or a new clean-install guarantee. Use the requirements file for ordinary setup; use the lock only when deliberately reproducing its compatible Windows environment. No installation was performed during package preparation.

## Inputs and included data folders

Source: **AirROI — Airbnb Short-Term Rental Data: Dubai**, available from [the original Kaggle dataset](https://www.kaggle.com/datasets/jasonairroi/airbnb-short-term-rental-data-dubai). The four source files are **present in the locally staged data-inclusive release**, but **have not been cleared for a public commit in this workflow**. Confirm authorization to redistribute both original data and row-level derivatives; attribution alone is not permission.

The intended release includes these four files under `data/raw/`:

- `past_rates.csv`
- `listings_monthly.csv`
- `past_rates.parquet`
- `listings.parquet`

The staged project also includes:

- `data/processed/`: validated SQLite database (`dubai_rentals.sqlite`), processed CSV tables, and preparation/benchmark manifests.
- `powerbi/data/`: six intermediate model-preparation CSVs.
- `powerbi/data/model/`: the twelve final model-import CSVs listed below.

Preserve source filenames and listing IDs. Keep these datasets in a local copy until redistribution rights and a content/privacy review are complete. The source files are historical provider data, not a live feed.

## Quick start with included data (once the data-inclusive release is approved)

1. Download or clone the complete release and keep the `powerbi/` project folders together.
2. Install a compatible Power BI Desktop version. If you only want to view the report, you do **not** need to regenerate the Python/SQLite pipeline.
3. Open `powerbi/DubaiRentalIntelligence.pbip` in Desktop. Set the `DataFolder` parameter to the **absolute path of the local `powerbi/data` folder** (the parent of `model/`).
4. Apply the parameter change and load/refresh the semantic model using Desktop's supported workflow. Check all six pages and inspect the ArcGIS map subject to its access requirements.

The model import CSVs are supplied, but the Power BI model cache is **not**. The first successful Desktop load/refresh has not been independently verified from a clean checkout. Avoid committing a machine-specific `DataFolder` path back to GitHub.

The steps below are for users who want to **rebuild or validate** the supplied data, not a prerequisite to opening the saved report definitions.

## Rebuild data, then export model imports (optional)

To regenerate the supplied outputs from the source files, run in this order in a separate local working copy **after backing up the shipped CSVs and database**:

```powershell
.\.venv\Scripts\python.exe src/01_validate_and_prepare.py
.\.venv\Scripts\python.exe src/02_build_peer_benchmarks.py
.\.venv\Scripts\python.exe src/03_build_powerbi_exports.py
.\.venv\Scripts\python.exe src/08_export_model_imports.py --expect-reference
```

The first three stages reconcile source observations, create full-peer benchmarks, and create the validated SQLite database plus six intermediate CSVs. The fourth is the **standalone data-only exporter** for the saved model. It reads SQLite in read-only mode, including the validated priority/transition views, and writes only CSV data under `powerbi/data/model/`. It does not run a builder or write report/model definitions.

Alternatively, run the eight [notebooks](../notebooks/README.md) in their documented order to produce the same intermediate data, then run `08_export_model_imports.py`. Notebook 07 validates the six intermediate exports; the new exporter separately validates the final twelve imports. Notebook outputs remain intentionally empty in the staged package. SQL analysis and independent validation utilities are optional additional evidence runs, not substitutes for the exporter.

### Final twelve files

`Analytics.csv`, `CohortSelector.csv`, `CoverageMonth.csv`, `DimAccommodation.csv`, `DimArea.csv`, `DimBedrooms.csv`, `DimListing.csv`, `DimMonth.csv`, `FactListingMonth.csv`, `MetricSelector.csv`, `PeerExamples.csv`, `ReviewThreshold.csv`.

The exporter reads the saved M-partition column order/types from TMDL, validates keys/relationships, contiguous calendar, population preservation, coverage counts, benchmark eligibility and example limits, and checks CSV round-trip values before replacing outputs. Missing tables/views or invalid input are errors; no missing dataset is replaced with an empty placeholder. An empty PeerExamples table is legitimate only as an actual input result without eligible examples.

`--expect-reference` additionally requires the audited March 2021–February 2026 population: 99,745 observations, 4,364 listings, 60 months, and the documented February counts. It is recommended for this project. Without that flag, structural/population consistency still runs; different input populations are not automatically certified as the audited dashboard.

For a custom local destination:

```powershell
.\.venv\Scripts\python.exe src/08_export_model_imports.py --database data/processed/dubai_rentals.sqlite --data-folder local-imports --expect-reference
```

Only `local-imports/model/` receives CSV outputs. Do not put unrelated CSVs there; the exporter refuses an unexpected file set instead of deleting it. Staging/backups are temporary CSVs inside the model directory. Recoverable exceptions roll back replaced files; a process kill, machine crash or concurrent writers are not a multi-file transaction. Run one writer, keep Desktop closed while replacing its local imports, and rerun a complete successful export after interruption before loading the model.

## Configure and open Power BI

Set the existing **DataFolder** parameter in a local working copy to the parent directory containing `model/`: for the default commands this is your local `powerbi/data` directory, **not** `powerbi/data/model`. The tracked parameter is intentionally blank; never commit a machine-specific value.

Then open [DubaiRentalIntelligence.pbip](../powerbi/DubaiRentalIntelligence.pbip) with its sibling Report/SemanticModel directories intact. Load or refresh the model from the included local imports using Desktop's supported workflow. **A populated model is not bundled**, and a fresh Desktop load/refresh was not independently completed during package preparation. ArcGIS needs supported service access/permissions; do not bypass consent or security controls.

**Never regenerate the finished report or semantic model.** Neither global builder is needed or included. All calculations, bookmarks, navigation and approved manual formatting remain defined by the saved files.

## Focused checks

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_model_import_exporter.py -v
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_business_rules.py -v
```

Exporter tests create synthetic fixtures and temporary directories, then clean them up; the focused exporter tests do not need provider inputs. The complete test suite includes data-dependent tests and tests that write local fixtures. A passing exporter is not native Power BI acceptance. See [Validation Summary](../VALIDATION_SUMMARY.md) for actual results and remaining Desktop checks, and [Publication Notes](PUBLICATION_NOTES.md) for rights and exclusions.

## Publication status and safety

This document is an updated **draft for the locally staged, data-inclusive release**, not a statement that the source datasets have already been made public. Before committing or pushing, verify redistribution permission for the four AirROI source files and their row-level derivatives, review identifiers and metadata for sensitive content, and reconcile the README, Power BI documentation, publication notes, file inventory, and checksum manifest. Do not add `.venv/`, historical backups, private audit recordings, credentials, Power BI caches or machine-specific settings.

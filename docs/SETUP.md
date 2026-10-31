# Local setup and reproducibility

The completed six-page report is supplied as PBIP/PBIR/TMDL definitions. No provider dataset, loaded model cache or database is redistributed. This is an independent portfolio project with no implied affiliation or endorsement.

## Python and dependencies

Use **Python 3.11 or newer**. Python **3.12.14** was the existing audit/test environment; a fresh installation has **not** been tested. Python 3.11 is the minimum because the pipeline uses `hashlib.file_digest`. Power BI Desktop requires a compatible Windows installation with support for PBIP/PBIR/TMDL and permitted ArcGIS access. No particular fresh Desktop installation is certified here.

Example commands from the repository root, using PowerShell after installing a suitable CPython interpreter:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` defines supported package ranges. `requirements-lock.txt` records an earlier Windows-oriented pinned environment, including platform-specific packages; it is not a universal cross-platform lock or a new clean-install guarantee. Use the requirements file for ordinary setup; use the lock only when deliberately reproducing its compatible Windows environment. No installation was performed during package preparation.

## Obtain authorized inputs

Source: **AirROI — Airbnb Short-Term Rental Data: Dubai**, available from [the original Kaggle dataset](https://www.kaggle.com/datasets/jasonairroi/airbnb-short-term-rental-data-dubai). The original dataset is not included or redistributed. Obtain the applicable rights separately; attribution does not establish permission.

Place these four original files in a locally created `data/raw/` directory:

- `past_rates.csv`
- `listings_monthly.csv`
- `past_rates.parquet`
- `listings.parquet`

Preserve source filenames and listing IDs. Do not put provider files, generated imports or notebook outputs into a future commit.

## Prepare data, then export model imports

Run in this order in a separate local working copy:

```powershell
.\.venv\Scripts\python.exe src/01_validate_and_prepare.py
.\.venv\Scripts\python.exe src/02_build_peer_benchmarks.py
.\.venv\Scripts\python.exe src/03_build_powerbi_exports.py
.\.venv\Scripts\python.exe src/08_export_model_imports.py --expect-reference
```

The first three stages reconcile source observations, create full-peer benchmarks, and create the validated SQLite database plus six intermediate CSVs. The fourth is the **standalone data-only exporter** for the saved model. It reads SQLite in read-only mode, including the validated priority/transition views, and writes only CSV data under `powerbi/data/model/`. It does not run a builder or write report/model definitions.

Alternatively, run the eight [notebooks](../notebooks/README.md) in their documented order to produce the same intermediate data, then run `08_export_model_imports.py`. Notebook 07 validates the six intermediate exports; the new exporter separately validates the final twelve imports. Notebook outputs are intentionally empty in the public package. SQL analysis and independent validation utilities are optional additional evidence runs, not substitutes for the exporter.

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

Then open [DubaiRentalIntelligence.pbip](../powerbi/DubaiRentalIntelligence.pbip) with its sibling Report/SemanticModel directories intact. Populate the model from the authorized local imports using Desktop's supported workflow. This user reproduction step is distinct from this task: no Desktop load, refresh or permission changes were performed during package preparation. ArcGIS needs supported service access/permissions; do not bypass consent or security controls.

**Never regenerate the finished report or semantic model.** Neither global builder is needed or included. All calculations, bookmarks, navigation and approved manual formatting remain defined by the saved files.

## Focused checks

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_model_import_exporter.py -v
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_business_rules.py -v
```

Exporter tests create synthetic fixtures and temporary directories, then clean them up; no private inputs are needed. The complete test suite includes data-dependent tests and tests that write local fixtures. A passing exporter is not native Power BI acceptance. See [Validation Summary](../VALIDATION_SUMMARY.md) for actual results and remaining Desktop checks, and [Publication Notes](PUBLICATION_NOTES.md) for rights and exclusions.

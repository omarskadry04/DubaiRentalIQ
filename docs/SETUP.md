# Local setup and reproducibility

Dubai Rental IQ includes the four source datasets, prepared analytical CSV files, the SQLite database, and the twelve CSV tables used by the Power BI semantic model. The six-page report is supplied as **PBIP/PBIR/TMDL definitions**, not a preloaded PBIX file. You can inspect the included data immediately; to use the interactive report, configure its local data folder and load the model in Power BI Desktop.

A complete fresh-machine setup and Power BI refresh have **not yet been independently verified**.

## 1. Download the project

Download or clone this repository, keeping its folder structure intact. If you have Git installed:

```powershell
git clone https://github.com/omarskadry04/DubaiRentalIQ.git
cd DubaiRentalIQ
```

Alternatively, use GitHub's **Code → Download ZIP**, extract it, and open PowerShell in the extracted `DubaiRentalIQ` folder. Repository access is required while the project is private.

## 2. What is already included

You do **not** need to download the source data or rerun the Python pipeline just to use the prepared outputs included in this release.

| Folder | Included contents | Purpose |
|---|---|---|
| `data/raw/` | `past_rates.csv`, `listings_monthly.csv`, `past_rates.parquet`, `listings.parquet` | Original AirROI data inputs |
| `data/processed/` | `dubai_rentals.sqlite`, five analytical CSVs, and two manifest JSON files | Prepared data and relational analysis |
| `powerbi/data/` | Six intermediate CSV files | Intermediate Power BI export tables |
| `powerbi/data/model/` | Twelve model-ready CSV files | Tables consumed by the saved Power BI semantic model |

The twelve model import files are:

`Analytics.csv`, `CohortSelector.csv`, `CoverageMonth.csv`, `DimAccommodation.csv`, `DimArea.csv`, `DimBedrooms.csv`, `DimListing.csv`, `DimMonth.csv`, `FactListingMonth.csv`, `MetricSelector.csv`, `PeerExamples.csv`, `ReviewThreshold.csv`.

Keep the `powerbi/data/model/` files together and retain their filenames. The model cache is not bundled, so Power BI Desktop may need to load or refresh the data on first opening.

## 3. Open and populate the Power BI report

1. Install a version of **Power BI Desktop** that supports Power BI Projects (PBIP), PBIR, and TMDL.
2. Open `powerbi/DubaiRentalIntelligence.pbip` in Power BI Desktop. Leave its sibling `.Report` and `.SemanticModel` folders in place.
3. In Power BI Desktop, locate the existing **DataFolder** parameter, typically through **Home → Transform data → Edit parameters** (the location may vary with Desktop version).
4. Set `DataFolder` to the **absolute path** of the repository's `powerbi/data` folder on your computer. For example, if you cloned to `C:\Projects\DubaiRentalIQ`, enter:

   ```text
   C:\Projects\DubaiRentalIQ\powerbi\data
   ```

   Set the path to the folder **containing** `model/`, not to `model/` itself.
5. Apply the parameter change and load or refresh the model using Power BI Desktop's supported workflow.
6. Check the six analytical pages. The ArcGIS map also requires a working network connection and supported ArcGIS service availability.

The tracked `DataFolder` parameter is intentionally blank so the repository does not contain a computer-specific path. Configure it in your own working copy; avoid committing your local path.

**Do not regenerate or overwrite the finished report or semantic model definitions.** Their DAX, relationships, navigation, bookmarks and manual formatting are preserved in the supplied files. The legacy global report/model builders are not needed.

## 4. Optional: install Python to reproduce the data preparation

The prepared CSV and SQLite outputs are already included. **The steps below are optional** and intended for users who want to rerun or inspect the analytical pipeline.

Use **Python 3.11 or newer**. Python 3.12.14 was the existing audit/test environment. The minimum is Python 3.11 because the pipeline uses `hashlib.file_digest`.

From the repository root in PowerShell:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` contains supported dependency ranges. `requirements-lock.txt` describes an earlier Windows-oriented pinned environment; it is not a universal cross-platform lock or proof of a fresh clean installation.

### Regenerate the prepared data

Work in a **separate local copy** if you want to preserve the included reference outputs. Run the scripts in order:

```powershell
.\.venv\Scripts\python.exe src/01_validate_and_prepare.py
.\.venv\Scripts\python.exe src/02_build_peer_benchmarks.py
.\.venv\Scripts\python.exe src/03_build_powerbi_exports.py
.\.venv\Scripts\python.exe src/08_export_model_imports.py --expect-reference
```

The first three stages validate and reconcile observations, construct full-peer benchmarks, and prepare SQLite plus six intermediate CSV files. The final **data-only exporter** reads the SQLite database in read-only mode and produces the twelve model tables under `powerbi/data/model/`. It does not rewrite the report or semantic model definitions.

You may also run the eight [notebooks](../notebooks/README.md) in their documented order for an explanatory notebook workflow. Notebook 07 checks intermediate exports; the standalone exporter checks the final twelve imports.

The `--expect-reference` option checks the audited March 2021–February 2026 sample, including **99,745 observations, 4,364 listings and 60 reporting months**. It is appropriate for the included reference inputs. Without this option, structural and population-consistency checks still run, but a different population is not automatically certified as equivalent to the documented dashboard.

To export the final model tables to a different folder:

```powershell
.\.venv\Scripts\python.exe src/08_export_model_imports.py --database data/processed/dubai_rentals.sqlite --data-folder local-imports --expect-reference
```

This writes CSVs under `local-imports/model/`. Do not add unrelated CSVs to the target model directory. Close Power BI Desktop while replacing data files, use one exporter process at a time, and complete a fresh successful export after any interruption before loading the data again.

## 5. Optional validation tests

After installing Python dependencies, run:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_model_import_exporter.py -v
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_business_rules.py -v
```

The exporter tests use synthetic fixtures and temporary folders. Passing them checks specific Python and data rules; it does not by itself verify a fresh Power BI Desktop load or every report interaction.

For the historical verification results and known limitations, see [Validation Summary](../VALIDATION_SUMMARY.md). For navigation and interpretation of the six dashboards, see the [User Guide](USER_GUIDE.md) and [Power BI README](../powerbi/README.md).

## 6. Troubleshooting

- **Power BI cannot find a CSV:** Verify that `DataFolder` points to `powerbi/data` and that `powerbi/data/model/` contains the twelve files listed above.
- **The report opens without populated visuals:** Apply the parameter setting and complete the model load/refresh; the repository does not include a populated model cache.
- **Python is not found:** Install Python 3.11+ and check `python --version` in a new PowerShell window.
- **A reference-population check fails:** Verify the source files and their versions. Do not silently disable the check and claim the results match the reference dashboard.
- **ArcGIS does not render:** Check the network connection and supported service availability; the map is not guaranteed to work offline.

This is an independent portfolio project with no implied affiliation or endorsement.

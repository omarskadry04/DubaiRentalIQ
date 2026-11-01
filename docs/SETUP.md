# Local setup and reproducibility

Dubai Rental IQ includes the four source datasets, prepared analytical CSV files, the SQLite database, and the twelve CSV tables used by the Power BI semantic model. The six-page report is supplied as **PBIP/PBIR/TMDL definitions**, not a preloaded PBIX file.

You can inspect the included data immediately. To use the interactive Power BI report, configure its local data folder and load the semantic model in Power BI Desktop.

A complete fresh-machine setup and Power BI refresh have **not yet been independently verified**.

## 1. Download the project

Clone the public GitHub repository using Git:

```powershell
git clone https://github.com/omarskadry04/DubaiRentalIQ.git
cd DubaiRentalIQ
```

Alternatively, open the [Dubai Rental IQ repository](https://github.com/omarskadry04/DubaiRentalIQ), select **Code → Download ZIP**, extract the archive, and open PowerShell in the extracted project folder.

Keep the original repository structure intact.

## 2. What is already included

You do **not** need to download the source datasets or rerun the Python pipeline just to inspect the prepared analytical outputs included in this release.

| Folder | Included contents | Purpose |
|---|---|---|
| `data/raw/` | `past_rates.csv`, `listings_monthly.csv`, `past_rates.parquet`, `listings.parquet` | Original AirROI data inputs |
| `data/processed/` | `dubai_rentals.sqlite`, five analytical CSV files, and two manifest JSON files | Prepared data and relational analysis |
| `powerbi/data/` | Six intermediate CSV files | Intermediate Power BI export tables |
| `powerbi/data/model/` | Twelve model-ready CSV files | Tables consumed by the saved Power BI semantic model |

### Twelve Power BI model import files

The `powerbi/data/model/` directory contains:

- `Analytics.csv`
- `CohortSelector.csv`
- `CoverageMonth.csv`
- `DimAccommodation.csv`
- `DimArea.csv`
- `DimBedrooms.csv`
- `DimListing.csv`
- `DimMonth.csv`
- `FactListingMonth.csv`
- `MetricSelector.csv`
- `PeerExamples.csv`
- `ReviewThreshold.csv`

Keep these files together and preserve their filenames.

The repository does not include a populated Power BI model cache, so Power BI Desktop may need to load or refresh the data when the project is opened for the first time.

## 3. Open and populate the Power BI report

1. Install a compatible version of **Power BI Desktop** supporting PBIP, PBIR, and TMDL.

2. Open the following project file:

   `powerbi/DubaiRentalIntelligence.pbip`

   Keep it alongside the existing `DubaiRentalIntelligence.Report` and `DubaiRentalIntelligence.SemanticModel` directories.

3. In Power BI Desktop, locate the existing **DataFolder** parameter. Depending on the Desktop version, this may be available through **Home → Transform data → Edit parameters**.

4. Set `DataFolder` to the absolute path of the repository's `powerbi/data` directory.

   For example, if the project is located at `C:\Projects\DubaiRentalIQ`, use:

   ```text
   C:\Projects\DubaiRentalIQ\powerbi\data
   ```

   **Important:** The parameter must point to the directory containing `model/`, not to `model/` itself.

5. Apply the parameter change and load or refresh the semantic model using Power BI Desktop.

6. Verify the six analytical report pages and their available data.

The ArcGIS map requires a working network connection and supported ArcGIS service availability.

### Important Power BI considerations

The tracked `DataFolder` parameter is intentionally blank to avoid storing a computer-specific path in the repository.

Configure this parameter in your own local working copy and avoid committing the local absolute path.

**Do not regenerate or overwrite the finalized report or semantic-model definitions.** Their existing DAX measures, relationships, navigation, bookmarks, and manual formatting are preserved in the supplied files.

Legacy global report and semantic-model builders are not required.

## 4. Optional: Reproduce the Python data preparation

The prepared CSV and SQLite outputs are already included. The steps below are optional and intended for users who want to rerun, validate, or inspect the analytical pipeline.

### Python requirements

Use **Python 3.11 or newer**.

Python 3.12.14 was used in the existing audit/test environment. Python 3.11 is the minimum because the pipeline uses `hashlib.file_digest`.

From the repository root, open PowerShell and run:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` specifies supported dependency ranges.

`requirements-lock.txt` records an earlier Windows-oriented pinned environment. It is not a universal cross-platform lock or a guarantee of successful clean installation.

### Regenerate the prepared data

Use a **separate local working copy** if you want to preserve the supplied reference outputs.

Run the scripts in the following order:

```powershell
.\.venv\Scripts\python.exe src/01_validate_and_prepare.py
.\.venv\Scripts\python.exe src/02_build_peer_benchmarks.py
.\.venv\Scripts\python.exe src/03_build_powerbi_exports.py
.\.venv\Scripts\python.exe src/08_export_model_imports.py --expect-reference
```

The first three stages:

1. Validate and reconcile historical source observations.
2. Construct geographic peer benchmarks using the documented eligibility and comparison rules.
3. Prepare the SQLite analytical database and six intermediate Power BI CSV exports.

The final **data-only exporter** reads SQLite in read-only mode and produces the twelve final model tables under `powerbi/data/model/`.

It does not regenerate the saved Power BI report or semantic-model definitions.

### Alternative notebook workflow

The eight [Jupyter notebooks](../notebooks/README.md) document the analytical workflow.

They can be executed in their documented order to inspect and reproduce the preparation, benchmarking, analysis, and validation stages.

Notebook 07 checks the intermediate Power BI exports. The standalone model exporter separately validates the twelve final model imports.

### Reference population validation

The `--expect-reference` option validates the audited historical population covering March 2021 through February 2026:

| Reference metric | Expected value |
|---|---:|
| Historical observations | 99,745 |
| Distinct listings | 4,364 |
| Reporting months | 60 |

This option is appropriate for the included reference inputs.

Without `--expect-reference`, structural and population-consistency checks still run, but a different source population is not automatically certified as equivalent to the documented dashboard.

### Export to a custom location

To generate the final model CSVs in a different local directory, run:

```powershell
.\.venv\Scripts\python.exe src/08_export_model_imports.py --database data/processed/dubai_rentals.sqlite --data-folder local-imports --expect-reference
```

This writes the twelve CSV outputs under `local-imports/model/`.

Do not place unrelated CSV files in the destination model directory.

When regenerating exports:

- Keep Power BI Desktop closed while replacing its local import files.
- Run only one exporter process at a time.
- Preserve the supplied reference outputs by working in a separate copy.
- After an interrupted export, complete a new successful export before loading the files into Power BI.

## 5. Optional validation tests

After installing the Python dependencies, you can run the focused automated tests from the repository root:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_model_import_exporter.py -v
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_business_rules.py -v
```

The exporter tests use synthetic fixtures and temporary directories.

These tests validate specific Python behavior, data rules, and export contracts. They do not independently certify a new Power BI Desktop installation, successful model refresh, or every report interaction.

For previous verification results and known limitations, see:

- [Validation Summary](../VALIDATION_SUMMARY.md)
- [Methodology](METHODOLOGY.md)
- [Data Dictionary](DATA_DICTIONARY.md)

## 6. Troubleshooting

**Power BI cannot locate a CSV file**

Verify that `DataFolder` points to the local `powerbi/data` directory and that `powerbi/data/model/` contains all twelve expected model CSVs.

**The Power BI report opens without populated visuals**

Apply the `DataFolder` parameter configuration and complete the model load or refresh. The repository includes the import CSVs but does not include a populated semantic-model cache.

**Python is not found**

Install Python 3.11 or newer, then open a new PowerShell window and check:

```powershell
python --version
```

If you already created a virtual environment, use its Python executable directly.

**A reference-population validation fails**

Verify that the input files correspond to the documented source snapshot and have not been modified. A different input population may generate different results.

Do not bypass the reference check and claim that the resulting outputs match the audited dashboard.

**ArcGIS does not render**

Check your internet connection, Power BI Desktop compatibility, and ArcGIS service availability. The map is not guaranteed to function offline.

**A notebook cannot locate the project directory**

Open Jupyter from the repository root or the `notebooks/` directory, as described in the notebook guide. Avoid running notebooks from an unrelated working directory.

## 7. Additional documentation

For further information, consult:

- [Main README](../README.md) — project overview, findings, architecture, and six dashboard screenshots.
- [Power BI README](../powerbi/README.md) — report navigation, configuration, and analytical interactions.
- [User Guide](USER_GUIDE.md) — filters, workspace navigation, property handoffs, and restores.
- [Portfolio Case Study](PORTFOLIO_CASE_STUDY.md) — business problem, technical decisions, and demonstrated analytical skills.
- [Publication Notes](PUBLICATION_NOTES.md) — release inventory, provenance, validation evidence, and maintenance information.

---

Dubai Rental IQ is an independent data analytics portfolio project. The historical findings are based on the documented AirROI-derived dataset and should not be interpreted as current Dubai rental market conditions or verified commercial outcomes.

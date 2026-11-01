# Analytical notebooks — portfolio review guide

The eight Jupyter notebooks document the Dubai Rental IQ analytical workflow, from source inspection and data preparation to competitor benchmarking, SQL analysis, Power BI data validation, and business insights.

**Run the notebooks in the exact numerical order shown below.** The publication copies preserve the analytical code and notebook structure, with saved outputs and execution counts cleared. The notebooks were not re-executed as part of the publication packaging process.

| Notebook | Analytical purpose | Main output |
|---|---|---|
| `01_data_inspection.ipynb` | All-four-file structure, grain, overlap, currency and nested Parquet reconciliation | Source audit and sample-coverage chart |
| `02_data_quality_assessment.ipynb` | Rule-based checks, missingness, currency consistency and snapshot risks | Auditable quality CSVs and quality-risk chart |
| `03_data_preparation.ipynb` | Transform raw CSVs to four uniquely keyed analytical tables | `data/processed/fact_*` and `dim_*` CSVs |
| `04_competitor_benchmarking.ipynb` | Nearest matching competitors, minimum peer thresholds, price deviations and QA | Benchmark and nearest-peer explanation tables |
| `05_sql_database_setup.ipynb` | Reproducible SQLite model, indexes and analytical views | `data/processed/dubai_rentals.sqlite` plus BI CSVs |
| `06_sql_business_analysis.ipynb` | Source-derived KPIs, coverage-aware time series, SQL window functions and review queue | Aggregate SQL evidence files and chart |
| `07_powerbi_export_validation.ipynb` | Keys, relationships, types, suppression and Power BI data reconciliation | BI export QA manifest |
| `08_insights_and_decision_brief.ipynb` | Evidence synthesis, justified managerial recommendations and limitations | `reports/business_insights_summary.md` |

## Reproduce in Jupyter

Use **Python 3.11 or newer**. Python 3.12.14 was used in the existing audit/test environment, but this does not constitute an independently verified fresh installation.

See [Local Setup](../docs/SETUP.md) for complete setup instructions, dependency specifications, optional regeneration procedures, and Power BI configuration.

### 1. Check the source datasets

The public repository already includes the four original AirROI source files under `data/raw/`:

- `past_rates.csv`
- `listings_monthly.csv`
- `past_rates.parquet`
- `listings.parquet`

You do not need to download these files separately to reproduce the included historical analytical sample.

The notebooks inspect and reconcile the source files, including the Parquet inputs. The `pyarrow` package is declared in the project dependencies.

### 2. Install the Python environment

From the repository root, run the following commands in PowerShell:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The project uses dependency ranges in `requirements.txt`. The separate `requirements-lock.txt` reflects an earlier Windows-oriented pinned environment and is not a universal cross-platform lockfile.

### 3. Start Jupyter and execute the notebooks

Start Jupyter from the project directory using an environment with the necessary notebook packages installed.

Open:

`notebooks/01_data_inspection.ipynb`

Execute the notebooks in numerical order, using **Restart Kernel and Run All Cells** before moving to the next notebook.

This sequence covers source inspection, quality assessment, preparation, benchmarking, SQLite construction, SQL business analysis, intermediate Power BI export validation, and the final decision brief.

The included prepared CSVs and SQLite database can be inspected without rerunning the notebooks.

### 4. Generate the final Power BI model imports

After the analytical preparation stages, the standalone model exporter produces the twelve final CSV tables used by the Power BI semantic model.

From the repository root, run:

```powershell
.\.venv\Scripts\python.exe src/08_export_model_imports.py --expect-reference
```

The `--expect-reference` option checks the documented March 2021–February 2026 historical sample, including 99,745 observations, 4,364 listings, and 60 reporting months.

Notebook 07 validates the intermediate exports. The standalone exporter validates and produces the final twelve model import tables.

The public repository already contains those twelve CSV files under `powerbi/data/model/`, so regeneration is optional for users who only want to open the existing analytical report.

### 5. Run the available validation tests

After installing dependencies and preparing any required outputs, run:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

These tests cover available analytical rules, benchmarking logic, synthetic exporter fixtures, and output-integrity checks where the required files are present.

Some tests may generate temporary files or require previously prepared outputs.

Passing the Python tests does not independently verify successful Power BI Desktop loading or every interactive report behavior.

## Automated notebook execution and independent validation

The project also includes a notebook execution utility:

```powershell
.\.venv\Scripts\python.exe src/07_execute_notebooks.py
```

This utility is intended to execute all eight notebooks using fresh kernels and record execution information in:

`reports/notebook_execution.json`

The independent validation script:

`src/06_independent_validation.py`

separately reconstructs historical peer comparisons from raw CSV inputs without importing the primary matching implementation.

These utilities support workflow testing and analytical verification; they are not required merely to review the saved notebooks or inspect the included outputs.

Additional reports, execution logs, diagnostics, and generated files should be reviewed before committing them to the public repository.

For historical test results and known validation boundaries, see [Validation Summary](../VALIDATION_SUMMARY.md).

## Power BI report relationship

The notebooks are responsible for preparing, analyzing, and validating data. They do **not** recreate the finalized six-page Power BI report.

The supplied report project is:

[powerbi/DubaiRentalIntelligence.pbip](../powerbi/DubaiRentalIntelligence.pbip)

The repository includes the saved PBIP/PBIR/TMDL report and semantic-model definitions, together with twelve model-ready CSV files.

It does not include a populated PBIX file or embedded semantic-model cache.

To open the interactive report, configure the existing `DataFolder` parameter to point to the local `powerbi/data` directory and load or refresh the model in a compatible version of Power BI Desktop.

See the [Power BI README](../powerbi/README.md) for instructions and the [User Guide](../docs/USER_GUIDE.md) for dashboard navigation and interpretation.

**Do not use notebook execution or legacy report builders to overwrite the finalized Power BI report definitions.**

## Analytical interpretation and limitations

The analysis represents the observed **AirROI historical sample**, not the complete Dubai short-term rental market.

Nightly rates, occupancy estimates, revenue estimates, historical coverage, and competitor comparisons must be interpreted within the documented source and methodology limitations.

In particular:

- Estimated occupancy and revenue are provider-derived estimates, not verified bookings or realized commercial revenue.
- Missing monthly records are not automatically equivalent to inactivity, zero occupancy, or zero revenue.
- Competitor benchmarking depends on documented eligibility rules, geographic matching, and minimum peer thresholds.
- Review flags identify cases for further examination; they do not independently establish that a property is overpriced or underpriced.
- Historical analytical findings are not current market forecasts or guaranteed pricing recommendations.

For calculation definitions and coverage limitations, consult [Methodology](../docs/METHODOLOGY.md) and [Data Dictionary](../docs/DATA_DICTIONARY.md).

## Source and distribution

The public GitHub repository includes the four original AirROI source files, prepared analytical CSVs, the SQLite database, six intermediate Power BI exports, and twelve final Power BI model import CSVs.

The eight analytical notebooks are included with saved outputs and execution counts cleared. Local execution can regenerate analytical outputs and supporting diagnostics.

Additional generated reports and diagnostic files should be reviewed before publication.

**Original data source:** [AirROI — Airbnb Short-Term Rental Data: Dubai](https://www.kaggle.com/datasets/jasonairroi/airbnb-short-term-rental-data-dubai).

The project's [MIT License](../LICENSE) applies to the author's original licensed code and does not automatically extend to third-party datasets, mapping services, or other vendor assets.

Public availability of the included source and derived data does not independently establish redistribution rights. Applicable third-party licensing terms remain relevant.

For further details, see [Publication Notes](../docs/PUBLICATION_NOTES.md) and [Local Setup](../docs/SETUP.md).

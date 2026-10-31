# Analytical notebooks — portfolio review guide

**Run in this exact order.** Each notebook retains its original code cells, cell order, saved execution counts and validation logic. Notebook 07’s publication prose distinguishes its historical intermediate-data stage from the completed report. All saved outputs have been cleared in this publication copy; they will appear only after authorized local execution. No notebooks were executed during packaging.

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

Use **Python 3.11+**; Python 3.12.14 is the existing tested audit environment, not a fresh-install certification. Follow [Local Setup](../docs/SETUP.md) for dependency ranges versus the Windows-oriented lockfile and the complete reproduction sequence.

1. Put all four original files (`past_rates.csv`, `listings_monthly.csv`, `past_rates.parquet`, `listings.parquet`) in `data/raw/`. Parquet validation is required; `pyarrow` is a declared dependency.
2. Run `python -m pip install -r requirements.txt`, start Jupyter from the project directory, and open `notebooks/01_data_inspection.ipynb`.
3. Run each notebook in numerical order using **Restart Kernel and Run All Cells** before moving to the next.
4. Run `python src/08_export_model_imports.py --expect-reference` to produce the twelve final model imports; configure DataFolder as described in [Local Setup](../docs/SETUP.md).
5. Run `python -B -m unittest discover -s tests -v` to verify benchmark rules, synthetic exporter fixtures and available generated outputs. These tests can create temporary files; output-integrity tests require prepared data.

`python src/07_execute_notebooks.py` automates fresh-kernel execution of all eight notebooks and records `reports/notebook_execution.json`. `src/06_independent_validation.py` separately reconstructs historical peers from raw CSV without importing the matching implementation. The full audit/SQL findings are linked from the root README. Static narrative figures reflect earlier local evidence; source fingerprints and generated reports are private and are not included. See [Validation Summary](../VALIDATION_SUMMARY.md).

**Important:** The analysis describes *AirROI's sample*, not the full Dubai rental market; price/occupancy estimates are not verified bookings, actual revenue or optimization recommendations. The finalized six-page report is [powerbi/DubaiRentalIntelligence.pbip](../powerbi/DubaiRentalIntelligence.pbip); a separate PBIX is not required. These notebooks prepare data and do not regenerate that report.

## Source and distribution

The downloadable third-party raw records and regenerable row-level exports are excluded from the GitHub-ready bundle pending license review. Notebook outputs are intentionally absent. Local execution regenerates outputs that must be reviewed before any later publication; do not upload the original ZIP or provider data. Source attribution: https://www.kaggle.com/datasets/jasonairroi/airbnb-short-term-rental-data-dubai

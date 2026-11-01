# Dubai Rental IQ — Publication Notes

**Release status (1 November 2026):** Dubai Rental IQ is publicly available on GitHub as a dataset-inclusive data analytics portfolio project. The repository includes Python and SQL analytical workflows, original AirROI source files, processed datasets, a SQLite database, twelve Power BI model imports, six-page Power BI report definitions, and supporting documentation.

The dataset-inclusive revision has been committed and published. The publication inventory records **553 files**, with SHA-256 checksums maintained for the package contents. Historical technical validations are documented below. A fresh-machine end-to-end reproduction and native Power BI refresh have not yet been independently verified.

## 1. Release Overview

Dubai Rental IQ is an end-to-end historical rental-market intelligence project combining Python, SQLite/SQL, geographic peer benchmarking, and Power BI.

The repository provides the analytical workflows, supporting datasets, and completed Power BI report definitions needed to inspect the implementation and reproduce the analysis in a compatible local environment.

| Component | Release status | Description |
|---|---|---|
| Python source code | Included | Preparation, validation, geographic matching, benchmarking and model export |
| SQL scripts | Included | Database analysis, market trends, benchmarking and validation |
| Jupyter notebooks | Included | Eight documented analytical notebooks with saved outputs cleared |
| Raw datasets | Included | Four AirROI source files |
| Processed datasets | Included | SQLite database, analytical CSVs and preparation manifests |
| Power BI model imports | Included | Twelve model-ready CSV files and six intermediate CSVs |
| Power BI application | Included | PBIP/PBIR/TMDL report and semantic-model definitions |
| Dashboard screenshots | Included | Six analytical page screenshots |
| Tests and documentation | Included | Validation, methodology, setup, data dictionary and portfolio case study |
| Populated PBIX or model cache | Not included | Local Power BI configuration and refresh may be required |
| Fresh-environment reproduction | Not independently verified | No completed clean-machine end-to-end acceptance is claimed |

The finalized Power BI design, DAX measures, visual configurations, bookmarks, and navigation were not rebuilt during the dataset-inclusive release.

## 2. Included Data and Analytical Assets

The repository contains the following production data directories.

| Directory | Files | Contents |
|---|---:|---|
| `data/raw/` | 4 | Original AirROI CSV and Parquet source files |
| `data/processed/` | 9 | SQLite database, analytical CSVs and two preparation/benchmark manifests |
| `powerbi/data/` | 6 | Intermediate analytical CSV files |
| `powerbi/data/model/` | 12 | Final CSV imports for the Power BI semantic model |
| **Total** | **31** | **Data-related production files** |

### Original Source Files

The four files in `data/raw/` are:

- `listings.parquet`
- `listings_monthly.csv`
- `past_rates.csv`
- `past_rates.parquet`

These represent the source inputs used for the project's historical analytical sample.

### Processed Analytical Files

The `data/processed/` directory contains:

- `dubai_rentals.sqlite`
- `dim_listing.csv`
- `dim_month.csv`
- `fact_coverage_month.csv`
- `fact_listing_month.csv`
- `fact_peer_benchmark.csv`
- `peer_examples_latest.csv`
- `preparation_manifest.json`
- `benchmark_manifest.json`

The processed files support SQL analysis, peer-benchmark calculations, validation procedures, and downstream Power BI reporting.

### Power BI Model Imports

The `powerbi/data/model/` directory contains twelve CSV tables used by the saved Power BI semantic model.

These imports were previously generated and compared against the corresponding prepared reference data during the documented historical validation process.

The supplied data files do not represent an embedded Power BI model cache. The report may require the local `DataFolder` parameter to be configured and the model to be loaded or refreshed.

## 3. Repository Structure and Exclusions

The repository retains the required analytical implementation and reporting assets while excluding unnecessary development artifacts.

**Included project materials:**

- Python source modules and validation tests
- SQL analytical scripts and reusable views
- Eight Jupyter notebooks
- Python dependency specifications
- Source and processed analytical datasets
- Power BI import CSV files
- Complete saved PBIP/PBIR/TMDL report definitions
- Report themes, resources and model relationships
- Six analytical dashboard screenshots
- Project documentation and validation summaries
- MIT License for the author's original licensed code
- Publication file inventory and SHA-256 manifest

**Excluded development and runtime materials:**

- Local Python virtual environments
- Historical development backups and temporary files
- Internal audit snapshots and duplicate test projects
- Logs, credentials, secrets and machine-specific settings
- Power BI `.pbi` runtime caches
- Proprietary native libraries and local recordings
- Temporary notebook outputs and generated diagnostic artifacts
- Legacy global report/model generators not required for the finalized application

The `.gitignore` configuration permits the selected production datasets while retaining exclusions for local environments, runtime files, backups and credentials.

The Power BI `DataFolder` parameter remains intentionally blank in the tracked semantic-model definitions. Locally configured absolute paths should not be committed.

## 4. Data Provenance and Licensing

The historical input data originates from:

**AirROI — Airbnb Short-Term Rental Data: Dubai**

[Original dataset on Kaggle](https://www.kaggle.com/datasets/jasonairroi/airbnb-short-term-rental-data-dubai)

The project is an independent analytical portfolio implementation. It does not imply affiliation with or endorsement by AirROI, Airbnb, Microsoft, Esri, or any other data or software provider.

The repository's [MIT License](../LICENSE) applies to the author's original licensed code. Third-party datasets, map imagery, vendor assets and proprietary components remain subject to their respective terms.

The dataset-inclusive repository is publicly accessible on GitHub. Public availability does not alter the applicable licensing terms of the original data or third-party assets.

The dashboard screenshots retain available map-provider credits, including Esri and other displayed attribution.

## 5. Opening and Reproducing the Project

### Opening the Power BI Application

The report entry point is:

`powerbi/DubaiRentalIntelligence.pbip`

The PBIP file must remain alongside its corresponding `.Report` and `.SemanticModel` directories.

To populate the report in Power BI Desktop:

1. Open the supplied PBIP project in a compatible Power BI Desktop installation.
2. Locate the existing `DataFolder` parameter.
3. Set it to the local repository's `powerbi/data` directory, which is the parent of `model/`.
4. Apply the parameter configuration and load or refresh the semantic model.
5. Inspect the report pages, relationships, measures and available analytical results.

The project provides the source and processed datasets as well as the model import files. Regenerating the data is optional for initial inspection of the supplied outputs.

See [Power BI README](../powerbi/README.md) for report-specific opening requirements and instructions.

### Reproducing the Analytical Pipeline

For regeneration or independent analytical inspection, consult:

- [Local Setup](SETUP.md)
- [Notebook Guide](../notebooks/README.md)
- [Methodology](METHODOLOGY.md)
- [Data Dictionary](DATA_DICTIONARY.md)
- [Validation Summary](../VALIDATION_SUMMARY.md)

The data-only Power BI exporter is:

```powershell
python src/08_export_model_imports.py --expect-reference
```

The reference check requires the compatible source and prepared-data version. Regeneration may overwrite generated files, so a separate working copy is recommended when preserving the supplied analytical snapshot.

The saved report and semantic-model definitions remain authoritative. Legacy global report/model generators should not be used to overwrite finalized manual report configurations.

### Reproducibility Boundary

The repository supplies the documented components for local setup, but a clean installation, complete raw-data rerun, native Power BI refresh, and save/reopen acceptance have not been independently verified on a new machine.

Previous static, analytical, and native validation results are retained as historical evidence rather than described as new execution results.

---

## 6. Historical Verification — Original Publication Package

The following results document the original publication preparation and associated technical audits conducted in October 2026.

These findings are retained for traceability. They do not, by themselves, constitute a new test of the expanded dataset-inclusive package.

### Preserved Power BI Report State

The finalized report contains six analytical pages and a hidden tooltip page.

Existing navigation, measures, filter interactions, visual formatting, bookmarks, and page-specific context behavior were retained.

The following saved report selections were preserved unchanged during the original publication preparation:

- `powerbi/DubaiRentalIntelligence.Report/definition/pages/2f21bf8024f171def418/page.json`
- `powerbi/DubaiRentalIntelligence.Report/definition/pages/9eea1fade12e5c8f74b8/visuals/963019e1f23cf3001fc1/visual.json`

No new report-building procedure was substituted for the accepted manually configured application.

### ArcGIS Inspection

The historical inspection decoded the saved ArcGIS cache associated with:

`powerbi/DubaiRentalIntelligence.Report/definition/pages/c35114d1e71555730786/visuals/8c2c687cc1baff98e231/visual.json`

The inspected object resolved to JSON `null`, with serialized placeholders rather than a redistributed listing table. No credential-like keys were identified within that inspected object.

The saved visual was preserved. External basemap services, vendor schemas, and supported ArcGIS access remain relevant to native rendering.

This was a bounded inspection of the identified saved object, not a comprehensive audit of external map services or every runtime component.

## 7. Dashboard Screenshot Evidence

The original publication review inspected all six dashboard screenshots.

The screenshots retained their existing dimensions and analytical content without resizing or regeneration.

| Screenshot | Dimensions | Captured analytical context |
|---|---|---|
| `01_executive_command_center.png` | 1435 × 808 | February 2026 market overview; 1,955 active listings |
| `02_market_trends_seasonality.png` | 1433 × 810 | Nightly-rate trends and seasonality; 60-month analytical context |
| `03_geographic_market_intelligence.png` | 1435 × 807 | February 2026 geography; 23.12% known-area share |
| `04_opportunity_action_center.png` | 1434 × 806 | 902 investigation cases and selected property context |
| `05_competitive_pricing_studio.png` | 1432 × 801 | Selected case, full-peer benchmark and nearest examples |
| `06_property_performance_deep_dive.png` | 1418 × 797 | Selected property history, estimated revenue and 21/60 observed months |

The screenshots document actual saved report states rather than illustrative redesigns.

Some original viewport and formatting characteristics remain, including scrollable chart areas, abbreviated month labels and small explanatory text.

The selected property and competitor examples retain their original identifiers and analytical values.

The screenshots include the attribution displayed by the underlying mapping and visualization services.

## 8. Historical Technical Validation

The original Task F validation documented the following results.

| Validation area | Recorded outcome |
|---|---|
| Exporter tests | 10 passed, zero failed |
| Power BI model exports | 12/12 matched the prepared reference tables |
| Cell-value comparisons | 4,245,538 values compared with documented normalization and tolerances |
| Python compilation | 14 files compiled |
| SQL statement preparation | 8 statements prepared against the defined in-memory test schema |
| Local documentation references | 91 checked with zero failures |
| Power BI artifact comparison | 466 non-Markdown artifacts compared with production |
| Dashboard screenshots | 6/6 preserved byte-for-byte |
| Jupyter notebooks | Eight publication notebooks with saved outputs cleared at the recorded audit point |

The original validation confirmed that the retained saved report definitions differed from the production reference only where the publication `DataFolder` value was intentionally emptied.

The twelve Power BI imports were compared against reference data following key sorting and saved-type normalization, using documented floating-point tolerances.

### Additional Validation Scope

The broader [Validation Summary](../VALIDATION_SUMMARY.md) documents earlier source reconciliation, numerical checks, workflow acceptance, and performance observations.

Those checks cover overlapping analytical and functional areas. Their assertion totals should not be added together as if they represented independent tests.

A later maintenance edit removed a saved `FileNotFoundError` output from Notebook 08 without changing its analytical code. Clearing a saved notebook output does not certify successful runtime execution.

### Limitations of the Historical Evidence

The historical checks did not establish:

- A successful fresh installation of the required Python dependencies on a new computer
- A complete source-to-output rerun from a clean checkout
- A newly populated Power BI model accepted in an independent environment
- Universal runtime behavior for all filters, interactions and edge cases
- Availability or behavior of every external ArcGIS service
- External validation of the historical provider estimates as actual bookings or realized revenue

These are verification boundaries, not evidence of newly discovered analytical defects.

## 9. Publication Inventory and Integrity

The expanded publication inventory was generated after the dataset-inclusive files and documentation updates were prepared.

The recorded package contains:

| Record | Count |
|---|---:|
| Publication file-list entries | 553 |
| SHA-256 payload records | 552 |

`PUBLICATION_FILE_LIST.txt` records the package files, and `PUBLICATION_MANIFEST.sha256` contains SHA-256 entries for all listed files except the manifest itself, avoiding a self-referential checksum.

The original expanded package passed a full SHA-256 check with zero errors. Subsequent documentation edits made directly on GitHub required corresponding manifest updates, which have been maintained through separate commits.

A full checksum verification should be rerun after the latest changes before treating the current package as newly integrity-verified.

The manifest is an integrity record, not proof of data correctness, software reproducibility, or external licensing compliance.

## 10. Maintenance and Verification Checklist

For future changes to the repository:

1. Preserve the finalized Power BI report and semantic-model definitions unless an intentional technical revision is required.
2. Keep the project README, setup guide, methodology, data dictionary and portfolio case study consistent with the actual repository contents.
3. Maintain the four source datasets, processed analytical outputs and model imports as a coherent, documented analytical snapshot.
4. Check whether dataset changes affect previously validated findings, population counts, benchmarking results or Power BI calculations.
5. Inspect modified or newly added files for machine-specific paths, credentials, private diagnostics and unintended generated artifacts.
6. Update `PUBLICATION_FILE_LIST.txt` when the set of included files changes.
7. Update `PUBLICATION_MANIFEST.sha256` whenever a tracked payload file changes, then verify the recorded checksums.
8. Keep the local Git repository synchronized with GitHub, particularly after edits made directly through the GitHub web interface.
9. Run relevant Python, SQL and Power BI tests after substantive analytical or model changes.
10. Record any new validation outcomes separately from historical audit evidence.

## 11. Current Project Status

Dubai Rental IQ is publicly available on GitHub as a dataset-inclusive analytical portfolio project.

The repository provides source data, prepared relational and CSV outputs, Power BI model inputs, finalized report definitions, and supporting documentation.

The project demonstrates historical market analysis, geographic peer benchmarking, screening-based pricing investigation, explicit property context transfer, and longitudinal performance interpretation.

The numerical findings describe the historical AirROI-derived sample rather than current Dubai rental conditions or verified commercial outcomes.

The existing validation evidence supports the documented analytical workflow, while independent fresh-environment reproduction and native Power BI refresh remain unverified.

**Overall status: Dataset-inclusive public GitHub repository; analytical implementation, supporting data, Power BI report definitions, and documentation available. Historical validation retained; independent fresh-environment reproduction remains unverified.**

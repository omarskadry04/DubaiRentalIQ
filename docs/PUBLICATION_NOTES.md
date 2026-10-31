# Dubai Rental IQ — Publication Notes

**Release status (31 October 2026):** The original code-and-documentation portfolio repository has already been published on GitHub. A **dataset-inclusive revision** is prepared locally but **has not yet been committed or pushed**. These notes describe the planned revision; the checks documented in the historical sections below apply to the earlier data-excluded package unless specifically stated otherwise.

## Current release readiness

| Status | Item | Finding |
|---|---|---|
| CONFIRMED LOCALLY | Data-file inventory | 31 intended additional files appear as Git-trackable files: four raw inputs, nine processed assets, six intermediate Power BI CSVs and twelve model import CSVs. |
| CONFIRMED LOCALLY | Source project preservation | Production files were copied into the GitHub working folder; the original project was not deliberately edited. |
| PREPARED | `.gitignore` | Explicit exceptions allow the chosen data files while retaining exclusions for environments, credentials, caches, backups and unrelated outputs. |
| IN PROGRESS | Documentation | Main README, setup guide and Power BI README have been revised locally; their final contents and links still require consistency checks. |
| PENDING | File inventory and hashes | Regenerate `PUBLICATION_FILE_LIST.txt` and `PUBLICATION_MANIFEST.sha256` **after** all final file edits; compare against the staged Git files. |
| PENDING | Redistribution authority | Confirm that applicable terms or permission explicitly allow public redistribution of **all four original AirROI files** and row-level derivative datasets (including CSV, Parquet and SQLite copies). Public display approval or attribution alone is not sufficient. |
| PENDING | Privacy and security | Inspect source and derivative files, identifiers, connection settings and staged paths; the historical bounded checks did not audit these newly included assets. |
| NOT VERIFIED | Fresh environment | A clean checkout with a native Power BI load/refresh has not been independently tested; prepackaged CSVs are not a populated Power BI cache. |

**Publication gate:** Do not push the 31 data files to the already-public repository until redistribution rights and a staged-file/data review are confirmed. The source-code release remains publicly accessible meanwhile.

## Included materials in the proposed revision

| Directory | New items | Purpose |
|---|---:|---|
| `data/raw/` | 4 | `listings.parquet`, `listings_monthly.csv`, `past_rates.csv`, `past_rates.parquet` |
| `data/processed/` | 9 | SQLite database, five prepared CSVs, two process/benchmark manifests |
| `powerbi/data/` | 6 | Intermediate analytical CSVs |
| `powerbi/data/model/` | 12 | Final CSV imports for the saved Power BI semantic model |
| **Total** | **31** | Added to the previously published code-and-documentation package, pending verification and authorization |

The existing project includes Python source, SQL, eight cleaned notebooks, tests, requirements, saved Power BI PBIP/PBIR/TMDL definitions and resources, six dashboard screenshots, project documentation and the MIT license for original code. The finalized report design and DAX are **not** being rebuilt as part of the data-inclusive revision. The tracked `DataFolder` value is intentionally blank; a user must configure a local directory (parent of `model/`) and refresh the model in Power BI Desktop.

**Remain excluded:** `.venv`, `reports/private/`, historical test snapshots, backups, credentials and secrets, logs, `.pbi` runtime caches, machine-specific settings, native libraries and duplicate audit/backup report projects. No populated PBIX or embedded model cache is supplied. The selected Git exceptions do not replace a review of actual staged files.

## Data provenance, licensing and privacy

The original data is attributed to **AirROI — Airbnb Short-Term Rental Data: Dubai**, from [its Kaggle source](https://www.kaggle.com/datasets/jasonairroi/airbnb-short-term-rental-data-dubai). The project's MIT license applies to its original licensed code, **not** automatically to third-party datasets, basemaps or vendor assets. Verify the current license holder/text directly in [LICENSE](../LICENSE) rather than relying on the older audit's attribution wording.

If authorized for redistribution, document the permission's source, scope and conditions **before publishing** the dataset-inclusive revision. The four raw files and prepared listing-level files include provider-derived records; check them for personal or sensitive information and identifiers. Screenshots retaining listing/queue/competitor identifiers remain an owner-approved choice, not a substitute for relevant third-party rights checks. This independent portfolio project has no implied affiliation with or endorsement by AirROI, Airbnb, Microsoft or Esri.

The Geography screenshot retains displayed credits including Esri, TomTom, Garmin, FAO, NOAA and USGS. Attribution must remain visible; it does not by itself establish publication rights for any particular map image or dataset.

## Opening and regeneration

The proposed revision supplies source data, prepared tables, a SQLite database and twelve model import CSV files. To open the report, use [the Power BI guide](../powerbi/README.md), configure the blank `DataFolder` parameter to the local `powerbi/data` directory, then load/refresh using Power BI Desktop. The model is **not already populated** in a clean clone.

For optional regeneration or audit of the data, follow [Local Setup](SETUP.md), [Notebook Guide](../notebooks/README.md) and [Validation Summary](../VALIDATION_SUMMARY.md). The final data exporter is `src/08_export_model_imports.py --expect-reference`; do not run legacy report/model builders over the finalized manually formatted report.

## Final pre-push checklist

1. Obtain and record an explicit redistribution license/permission for original and derived data; if it cannot be confirmed, **keep the 31 datasets local** and publish documentation-only improvements.
2. Confirm the correct updated `README.md`, `docs/SETUP.md`, `powerbi/README.md` and this file are saved inside the repository.
3. Inspect the actual 31 staged data files for provenance, identifiers and accidental secrets; do not include other local or backup content.
4. Verify that `DataFolder` remains blank and saved PBIP/PBIR/TMDL, DAX, visuals and notebooks are unchanged unless intentionally edited.
5. Rebuild file inventory and SHA-256 payload manifest, then recheck every hash and the exact staged Git paths.
6. Run relevant tests and, ideally, a clean local Power BI refresh. Disclose any validation that is not performed.
7. Only then commit and push the revision to the existing public GitHub repository.

---

## Historical verification — original data-excluded package (October 2026)

The evidence below is retained for traceability. These results **do not certify the newly bundled 31 data files**, nor establish their redistribution permission, fresh environment reproducibility or new security review.

### Preserved report state and ArcGIS inspection


The following saved selections are retained unchanged by owner decision:

- `powerbi/DubaiRentalIntelligence.Report/definition/pages/2f21bf8024f171def418/page.json`
- `powerbi/DubaiRentalIntelligence.Report/definition/pages/9eea1fade12e5c8f74b8/visuals/963019e1f23cf3001fc1/visual.json`

Screenshots `docs/04_opportunity_action_center.png`, `docs/05_competitive_pricing_studio.png` and `docs/06_property_performance_deep_dive.png` expose real subject/queue/competitor identifiers and analytical examples. No identities were fabricated or silently changed. Owner retention is recorded; any unresolved third-party disclosure concern must be resolved before public upload.

Task C decoded the current ArcGIS cache in `powerbi/DubaiRentalIntelligence.Report/definition/pages/c35114d1e71555730786/visuals/8c2c687cc1baff98e231/visual.json` as JSON `null` (gzip/base64). Serialized source/features were empty-attribute, zero-coordinate placeholders, not a redistributed listing table. Template attributes were null; no credential-like keys were found in that object. This evidence is reused, with the visual preserved byte-for-byte. Remote basemap style references and vendor schemas remain required references, not bundled imagery or guarantees of service access.

### Screenshot evidence


Task C inspected all six actual images, with no editing panels/ribbon, tooltip popups or resize handles visible. No new screenshots or image modifications were made for this package. Titles and principal analytical content are readable. Native scroll viewports, abbreviated month labels, some small footnotes and thin edge pixels remain as visually approved.

| Image | Dimensions | Actual context |
|---|---|---|
| `docs/01_executive_command_center.png` | 1435 × 808 | February 2026 all-market; 1,955 active listings |
| `docs/02_market_trends_seasonality.png` | 1433 × 810 | Nightly rate; 60-month context, visible main viewport ends January 2025 |
| `docs/03_geographic_market_intelligence.png` | 1435 × 807 | February 2026; 23.12% known-area share; dark ArcGIS with visible provider credits |
| `docs/04_opportunity_action_center.png` | 1434 × 806 | 902 cases, both directions, selected investigation case |
| `docs/05_competitive_pricing_studio.png` | 1432 × 801 | Same case, Investigation Active, full-peer benchmark and nearest examples |
| `docs/06_property_performance_deep_dive.png` | 1418 × 797 | Same case, Est. revenue and 21/60 observed months; not the separate 42/60 gap test |

### Historical Task F technical checks


- **10 exporter tests passed, zero failed** on the final run. The earlier SQLite handle cleanup issue was fixed before completion.
- **12/12 final imports matched** the current private reference tables: 4,245,538 cell values compared after key sorting and saved-type normalization, with the documented floating-point tolerances. Reference population gate passed; private database hash unchanged; temporary CSVs removed.
- **14 Python files compiled**, **8 SQL analysis statements prepared** against a six-table/ten-view in-memory schema, and **91 local document/image/anchor/notebook-Markdown references resolved**, zero failures.
- **466 non-Markdown Power BI artifacts** compared with production; only the pre-existing intentionally blank publication DataFolder value differs. Task F did not change any report or model definition.
- **6/6 screenshots remain byte-identical.** All eight notebooks have empty outputs and unchanged code cells/order/execution counts; Notebook 07 Markdown changes are documented.
- Bounded credential/path/excluded-file checks passed. Synthetic test identifiers are generated fixtures, not provider rows. No temporary private/synthetic data is included. No fresh installation, raw-data rerun or native Desktop acceptance was claimed.

The historical baseline's publication manifest and file count must be regenerated for the expanded revision. The prior packaging audit verified a data-excluded bundle; statements from that audit that said datasets and SQLite were absent no longer describe the proposed revision.

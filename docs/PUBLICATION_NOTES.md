# Dubai Rental IQ — Publication Checklist

Prepared 30 October 2026 as an isolated local publication package. No Git initialization, staging, commit, push, upload or deployment occurred. Production and original evidence remain unchanged.

## Readiness

| Status | Item | Finding |
|---|---|---|
| PASS | Six screenshots | Owner approved; retained byte-for-byte at existing `docs/01_…06_….png` paths. Slightly different native dimensions are retained without resizing. |
| PASS | Analytical examples and identities | Owner explicitly chose to retain examples. Saved selections, visible subject/queue/competitor IDs, drillthrough guards and screenshot identities are unchanged. This is an owner retention decision, not independent privacy/rights clearance. |
| PASS | Complete Power BI definitions | All original report definitions, themes/resources, platform descriptors, model table/relationship definitions and model diagram are included. Only the publication-copy DataFolder value is emptied; lineage/annotations remain. |
| PASS | Notebook cleanup | Eight notebooks retain original code cells, cell order and execution counts; Notebook 07 publication prose is clarified. All 125 output blocks are removed only in the publication copies; no notebooks were executed. Future generated outputs require review. |
| PASS | Excluded data and runtime files | No raw/processed source tables, databases, imported model caches, `.pbi`, native recordings, logs or backups are intentionally included. DataFolder is blank and reproduction prerequisites are documented. |
| PASS | Original-code license | MIT text is supplied in [LICENSE](../LICENSE), scoped to original code only; author attribution uses “Dubai Rental IQ contributors.” Owner should confirm that attribution before publication. |
| NEEDS REVIEW | Third-party publication rights | Dataset links establish provenance, not redistribution permission. Public display of provider-derived observations in screenshots and vendor basemap/imagery rights remain unverified. Retaining examples is not a legal clearance. |
| NEEDS REVIEW | Runtime acceptance in a new environment | No fresh-clone execution, new native tests, data refresh or external-service availability test was performed. An empty DataFolder and absent imports/cache require local setup. |

**Overall: technically prepared; third-party rights review remains open. Publication is not authorized by this preparation task.** No blocking technical defect is intentionally concealed; results below distinguish checks from open decisions.

## Included and excluded materials

Included: ten Python source modules, ten SQL scripts, four test modules, eight output-free notebooks, dependency specifications, complete reviewed PBIP/PBIR/TMDL definitions and required resources, existing theme, technical/user/portfolio documentation, six unchanged approved screenshots and [Validation Summary](../VALIDATION_SUMMARY.md). [PUBLICATION_FILE_LIST.txt](../PUBLICATION_FILE_LIST.txt) enumerates every file; [PUBLICATION_MANIFEST.sha256](../PUBLICATION_MANIFEST.sha256) hashes the package payload.

Excluded: original AirROI files and archives; processed observations and listing-level exports; all SQLite/database files; Power BI `.pbi`, imports and local settings; PBIX/native libraries; backups/test projects; detailed private checkpoints, QA JSON, source fingerprints and native performance exports; credentials, environment files and logs; legacy global report/model generators. No required visual/relationship file is removed to conceal an issue.

The `.gitignore` protects generated data, caches, environments and likely credential/log files without globally ignoring PBIP, PBIR, TMDL or JSON. The blank model parameter remains tracked so the definition set stays complete. After local configuration, review its diff and restore the blank value before a future commit; ignore rules cannot protect a tracked file from accidental edits.

## Saved selections and ArcGIS

The following saved selections are retained unchanged by owner decision:

- `powerbi/DubaiRentalIntelligence.Report/definition/pages/2f21bf8024f171def418/page.json`
- `powerbi/DubaiRentalIntelligence.Report/definition/pages/9eea1fade12e5c8f74b8/visuals/963019e1f23cf3001fc1/visual.json`

Screenshots `docs/04_opportunity_action_center.png`, `docs/05_competitive_pricing_studio.png` and `docs/06_property_performance_deep_dive.png` expose real subject/queue/competitor identifiers and analytical examples. No identities were fabricated or silently changed. Owner retention is recorded; any unresolved third-party disclosure concern must be resolved before public upload.

Task C decoded the current ArcGIS cache in `powerbi/DubaiRentalIntelligence.Report/definition/pages/c35114d1e71555730786/visuals/8c2c687cc1baff98e231/visual.json` as JSON `null` (gzip/base64). Serialized source/features were empty-attribute, zero-coordinate placeholders, not a redistributed listing table. Template attributes were null; no credential-like keys were found in that object. This evidence is reused, with the visual preserved byte-for-byte. Remote basemap style references and vendor schemas remain required references, not bundled imagery or guarantees of service access.

## Screenshot capture and approval

Task C inspected all six actual images, with no editing panels/ribbon, tooltip popups or resize handles visible. No new screenshots or image modifications were made for this package. Titles and principal analytical content are readable. Native scroll viewports, abbreviated month labels, some small footnotes and thin edge pixels remain as visually approved.

| Image | Dimensions | Actual context |
|---|---|---|
| `docs/01_executive_command_center.png` | 1435 × 808 | February 2026 all-market; 1,955 active listings |
| `docs/02_market_trends_seasonality.png` | 1433 × 810 | Nightly rate; 60-month context, visible main viewport ends January 2025 |
| `docs/03_geographic_market_intelligence.png` | 1435 × 807 | February 2026; 23.12% known-area share; dark ArcGIS with visible provider credits |
| `docs/04_opportunity_action_center.png` | 1434 × 806 | 902 cases, both directions, selected investigation case |
| `docs/05_competitive_pricing_studio.png` | 1432 × 801 | Same case, Investigation Active, full-peer benchmark and nearest examples |
| `docs/06_property_performance_deep_dive.png` | 1418 × 797 | Same case, Est. revenue and 21/60 observed months; not the separate 42/60 gap test |

## Attribution and rights

Data provenance: **AirROI — Airbnb Short-Term Rental Data: Dubai**, via [the original Kaggle dataset](https://www.kaggle.com/datasets/jasonairroi/airbnb-short-term-rental-data-dubai). Obtain the dataset separately under applicable terms; no data files are redistributed here. No endorsement by AirROI, Airbnb, Microsoft or Esri is implied.

The Geography screenshot retains its displayed credits: **Esri, TomTom, Garmin, FAO, NOAA, USGS** and **Powered by Esri**. Keep them visible. Attribution alone does not establish permission for the exact basemap/data screenshot combination. Existing review references: [Esri attribution](https://doc.arcgis.com/en/arcgis-online/reference/display-copyrights.htm), [item-specific use constraints](https://doc.arcgis.com/en/arcgis-online/reference/access-use-constraints.htm) and [ArcGIS-enabled report sharing](https://doc.arcgis.com/en/power-bi/latest/workflows/share-a-map-enabled-report.htm). Current rights were not reverified in packaging. The MIT template source lookup was unavailable during this task; standard MIT text is supplied, not legal advice or a third-party rights determination.

## Validation evidence

[VALIDATION_SUMMARY.md](../VALIDATION_SUMMARY.md) is this package’s canonical sanitized analytical, functional and performance evidence. It separates automated/static, native and user-confirmed results, retains R01–R03 and residual R04 gaps, and distinguishes visual event maxima from page response. No immediate performance optimization is justified by existing measurements. Private originals are neither deleted nor republished.

## Local setup and owner checklist

1. Review the MIT attribution and third-party screenshot/provider rights. Owner-approved examples remain intact.
2. Obtain lawful raw data separately; follow [notebook instructions](../notebooks/README.md) and dependencies in a separate local environment. Do not publish regenerated records/outputs by default.
3. Follow [Local Setup](SETUP.md), including the data-only twelve-file exporter, then configure the blank DataFolder in a working copy. Do not run a global report/model generator or expect a cache-free clone to contain the loaded dataset.
4. Before any future commit, inspect exact staged paths, parameter diffs, notebook outputs and secret scan findings. A `.gitignore` is not a staging/history security audit.
5. Request separate authorization for Git initialization/publication. No upload is part of this package preparation.

## Package verification results

- 552 original protected files were hashed before/after preparation: zero changes. The original project and approved PNGs remain untouched.
- 458 definition/resource files checked against production: all included, byte-identical except the explicitly emptied publication DataFolder value. PBIP/PBIR entry points, platform descriptors and model diagram are also retained. Six analytical pages and one hidden tooltip page remain present; no navigation, DAX, fields or bookmark edits.
- All six screenshot hashes match originals. Eight notebooks retain code/cell order/execution counts exactly, with zero saved outputs (125 removed); Notebook 07 Markdown is updated for publication.
- Markdown/image/anchor and notebook-Markdown targets resolve locally. Runtime-generated data/report paths in source code are intentionally absent, not broken public documentation links. External web links are retained provenance references; online availability and legal terms are not certified.
- The initial package check parsed 447 JSON-family files and compiled 12 Python modules; Task F adds one exporter and one focused test module. Dependency installation and native Power BI opening were not tested.
- No raw/processed table/database/cache/archive/log files are present. Bounded text checks found no absolute drive/home paths, strong private-key header or tested long credential literal. This is not a comprehensive security certification; retained real listing identifiers are intentional and documented above.
- The package is approximately 5 MiB; the largest file is approximately 1.21 MiB. No large-file storage is needed for the current contents.
- The exact file list includes itself and the SHA-256 manifest. The manifest hashes every package file except itself, to avoid self-reference. Review this list before any separately authorized staging/publication.

**PASS:** technical packaging, preserved analytics, output cleanup, screenshot integrity and local document link closure. **NEEDS REVIEW:** original-code attribution, third-party rights, final staged-file review and new-environment runtime setup. **BLOCKED:** no confirmed technical package blocker; public upload remains outside this authorization and must await rights review and separate approval.

## Task F disposition

**READY AFTER CHECKS.** The confirmed technical/documentation defects H01, M01 and L01 are resolved in the publication copy. All twelve imports were generated and value-compared using current private inputs, with ten passing focused synthetic tests. Results and limits are in [Validation Summary](../VALIDATION_SUMMARY.md). No source records or generated CSVs are included.

The exporter writes only data under the selected DataFolder/model; the saved PBIP/PBIR/TMDL, DAX, navigation, bookmarks and approved screenshots remain unchanged. Notebook 07 changes are Markdown only. Temporary fixtures and private-equivalence outputs were cleaned up. SQL definitions and dependency pins are unchanged.

**Still unverified:** fresh dependency installation and end-to-end raw-data rerun; native loading/refresh, ArcGIS service behavior and save/reopen of a newly populated public copy. These are verification gaps, not newly found analytical defects. Recoverable exporter exceptions roll back; abrupt machine failure/concurrent writers are outside transactional guarantees.

**Owner decisions:** confirm the MIT copyright-holder line currently reading “Dubai Rental IQ contributors.” No legal name has been inferred. This independent portfolio project has no implied affiliation or endorsement. The original AirROI dataset is not included or redistributed. Approved analytical examples/screenshots remain intact, including Esri and other displayed map-provider credits. Attribution is not permission; third-party publication rights remain a concise separate review item, not a technical exporter defect.

### Final Task F package checks

- **10 exporter tests passed, zero failed** on the final run. The earlier SQLite handle cleanup issue was fixed before completion.
- **12/12 final imports matched** the current private reference tables: 4,245,538 cell values compared after key sorting and saved-type normalization, with the documented floating-point tolerances. Reference population gate passed; private database hash unchanged; temporary CSVs removed.
- **14 Python files compiled**, **8 SQL analysis statements prepared** against a six-table/ten-view in-memory schema, and **91 local document/image/anchor/notebook-Markdown references resolved**, zero failures.
- **466 non-Markdown Power BI artifacts** compared with production; only the pre-existing intentionally blank publication DataFolder value differs. Task F did not change any report or model definition.
- **6/6 screenshots remain byte-identical.** All eight notebooks have empty outputs and unchanged code cells/order/execution counts; Notebook 07 Markdown changes are documented.
- Bounded credential/path/excluded-file checks passed. Synthetic test identifiers are generated fixtures, not provider rows. No temporary private/synthetic data is included. No fresh installation, raw-data rerun or native Desktop acceptance was claimed.

Task F files created/updated (publication copy only):

```text
src/08_export_model_imports.py
tests/test_model_import_exporter.py
docs/SETUP.md
README.md
powerbi/README.md
notebooks/README.md
notebooks/07_powerbi_export_validation.ipynb
requirements.txt
VALIDATION_SUMMARY.md
docs/PUBLICATION_NOTES.md
PUBLICATION_FILE_LIST.txt
PUBLICATION_MANIFEST.sha256
```

The exact file list and SHA-256 payload manifest were regenerated after these changes. The historical external pre-publication audit is retained unchanged; this disposition supersedes its H01/M01/L01 open status only. Rights/attribution decisions and new-environment runtime checks remain separate.

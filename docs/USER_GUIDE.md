# Dubai Rental IQ — User Guide

Use the dashboard to explore the observed March 2021–February 2026 sample, review pricing evidence and inspect one property's history. Amounts are AED. Occupancy and revenue are provider estimates, not verified transactions.

## Start and navigate

Open the existing configured PBIP using the [Power BI requirements](../powerbi/README.md#opening-requirements). Keep the six-destination sidebar as your main navigation. In Power BI Desktop edit mode, **Ctrl+click buttons** to activate navigation, drillthrough or restores. Select slicer values, table rows and confirmation rows with a normal click.

Start on **Overview**, choose Area, Accommodation, Bedrooms and one Reporting Month, then read the context strip before interpreting results. Use the page's Restore action to recover its saved view. Clear filters can leave no unique reporting month and is not equivalent to Restore Overview.

## Understand which context follows you

| Page | Market dimensions | Month/property context |
|---|---|---|
| Overview | Visible shared editor | Selected reporting month; historical visual retains its configured timeline |
| Market Trends | Inherited | Full 60-month timeline, independent local metric |
| Geography | Inherited | Same unique focus month as Overview |
| Investigations | Inherited | Latest February 2026 snapshot, independent Priority/Direction |
| Pricing Studio | Independent property research | Inbound investigation property/latest snapshot, or explicitly selected lookup property/research month |
| Deep Dive | Independent property history | Exact transferred listing; all 60 calendar months |

Changing Overview to March 2021 changes Geography's snapshot; it does not truncate Market Trends or move Investigations away from its latest snapshot. Editing a local metric does not change another page's metric. Local chart selections are not a promise of a transferred community or property filter.

## Market exploration

### Overview

Read active listings, median reported rate, median estimated occupancy and summed estimated sample revenue. Use Historical Metric to switch the history chart. Review benchmark coverage and methodology tooltips before moving into a case. Counts describe the selected observed sample, not all Dubai rentals.

### Market Trends

Choose Nightly rate, Est. occupancy or Est. revenue. The revenue series is median estimated monthly revenue per listing, not Overview's summed revenue. Use the chart's horizontal scrolling where present to reach the end of the history. Read the contributor evidence alongside trends; changing sample composition can explain movement. The seasonal pattern is the median of valid year-month medians for each calendar month, not a causal seasonal effect.

### Geography

Check Focus Month, Mapped Share and Known-Area Share before reading the ArcGIS map. Hover a location for its exact active-listing count; co-located properties contribute to that count. Bubble sizes use graduated classes, so two different counts can share the same size. Coordinates and community labels are source observations, not verified addresses or polygons.

Change the community metric to compare nightly rate, estimated occupancy or estimated revenue. Ranking shows up to ten named communities with at least ten valid contributors to that metric. Smaller communities and **Unknown area** remain in the evidence table; Unknown is not a named Dubai community. Use Edit Market Lens to return to Overview. Restore Geography clears local selections while preserving inherited scope. If tiles do not load, do not interpret the empty basemap as no listings or change security permissions without review.

## Investigate a property

1. On **Investigations**, choose Evidence Priority and Pricing Direction.
2. Select one queue row. Check the exact selected identity, rate/peer evidence and caution text in Case Preview.
3. Activate **Investigate Property**. In Desktop edit mode, use Ctrl+click.
4. In **Pricing Studio**, confirm **Investigation Active** and the incoming listing. This property is authoritative even if an old Saved lookup ID remains visible. The comparison uses the investigation snapshot.
5. Review full-peer median, count, quartiles/radius and evidence limitations. Read Property History separately from the selected-month comparison. Five Nearest Examples are latest-month illustrations, not the full benchmark group.
6. Select the authoritative **listing confirmation row**, then activate **View Property Performance**. The selection step is required; ordinary sidebar navigation does not perform this transfer.
7. Confirm the same listing on **Deep Dive** before interpreting history.

A review flag is a reason to inspect comparability, not proof that a property is overpriced or underpriced. An unavailable benchmark is a valid evidence state, not a zero-valued peer price.

## Direct Research in Pricing Studio

Use **Restore Pricing Studio** to clear the prior investigation/research context. Select exactly one **Saved lookup ID** and one **Research month**. Confirm the selected listing/month and any availability message. No arbitrary listing is chosen when the selection is missing or ambiguous.

For an observed property-month, review the recorded rate even if the peer benchmark is unavailable. Fewer than ten eligible peers suppress the benchmark; Five Nearest Examples are only available for eligible latest-month comparisons. Property History keeps the property's historical observations rather than becoming a one-month chart. Its horizontal scrolling and approved category spacing are intentional.

To continue, select the confirmation row and activate View Property Performance. Do not re-enter the ID on Deep Dive. If the action is unavailable, verify one explicit property, the confirmation selection and the context message; do not bypass the identity guard.

## Read Property Deep Dive

The context strip identifies the exact listing, first observation, latest observation and latest activity state. The first three KPI cards all refer to the **same latest observed month**, which may precede February 2026. The fourth reports actual observed months out of 60.

Switch Nightly rate, Est. occupancy and Est. revenue in Historical Performance. Valid zeros remain values; missing observations remain gaps. Observation Coverage and Monthly Evidence retain all 60 calendar months:

| Symbol / status | Meaning |
|---|---|
| A / Active | A monthly record exists and is marked active |
| I / Inactive | A monthly record exists and is marked inactive |
| — / No observation | No record exists; performance values are blank |
| ? / Activity unknown | A record exists but activity is ambiguous, if encountered |

Missing records do not prove closure, vacancy or zero revenue. Scroll Monthly Evidence for older months; its default order is newest first. Restore Deep Dive returns to Est. occupancy and default local selections/order without clearing the property. Use **Open Pricing Studio** for the supported return to that property, or the Investigations destination to return to the latest queue. Direct navigation without a valid transferred property shows the selection-required state.

## Restore and empty-state reference

| Page | Restore scope / important caution |
|---|---|
| Overview | Saved executive/default filters and February 2026; shared changes can propagate |
| Market Trends | Local metric/charts; shared dimensions remain |
| Geography | Local metric and selections; shared month/dimensions and ranking safeguards remain |
| Investigations | Local Priority, Direction and queue selection |
| Pricing Studio | Local research controls and existing inbound-clearing behavior; select a property again for Direct Research |
| Deep Dive | Est. occupancy, local selections and evidence order; selected property remains |

An empty market segment, no single focus month, no selected property, no monthly record and insufficient peers are different states. Follow the displayed explanation. Do not turn blanks into zeros or infer that a blank visual establishes a market outcome.

## Evidence limits

Core workflows have existing native and/or owner-confirmed evidence; this guide is not a new execution of every interaction. Pending cases include complete rendered geographic-group reconciliation, some pan/ranking edges, early-ending/short-history property runtime cases and unspecified checklist edges. See the [data-quality reconciliation](../VALIDATION_SUMMARY.md) and [Methodology](METHODOLOGY.md#remaining-limitations-and-evidence). The owner-approved screenshots are included separately; no source-data redistribution rights are granted by this guide.

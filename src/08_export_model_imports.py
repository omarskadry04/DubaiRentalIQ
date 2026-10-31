"""Export CSV data only for the existing Power BI model. Never writes definitions.

Input: the validated SQLite database produced by 03_build_powerbi_exports.py.
Output: exactly twelve CSVs under DataFolder/model/. No source data is bundled.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import tempfile

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFINITION = ROOT / "powerbi/DubaiRentalIntelligence.SemanticModel/definition"
NAMES = {
    "Analytics", "CohortSelector", "CoverageMonth", "DimAccommodation", "DimArea",
    "DimBedrooms", "DimListing", "DimMonth", "FactListingMonth", "MetricSelector",
    "PeerExamples", "ReviewThreshold",
}
KEYS = {
    "Analytics": ["placeholder"], "CohortSelector": ["Cohort"],
    "CoverageMonth": ["month_date"], "DimAccommodation": ["room_type"],
    "DimArea": ["area_label"], "DimBedrooms": ["bedroom_label"],
    "DimListing": ["listing_id"], "DimMonth": ["month_date"],
    "FactListingMonth": ["listing_id", "month_date"], "MetricSelector": ["Metric"],
    "PeerExamples": ["listing_id", "month_date", "peer_listing_id"],
    "ReviewThreshold": ["Threshold"],
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def contracts(definition=DEFINITION):
    """Read exact CSV column order and M types; calculated columns are not imports."""
    result = {}
    for file in (Path(definition) / "tables").glob("*.tmdl"):
        text = file.read_text(encoding="utf-8-sig")
        match = re.search(r'File.Contents\(DataFolder & "/model/([^"/]+)\.csv"\)', text)
        if not match:
            continue
        pairs = re.findall(r'\{"([^"\n]+)", (type \w+|Int64.Type)\}', text)
        require(pairs and len(dict(pairs)) == len(pairs), f"Unrecognized import contract: {file.name}")
        require(match[1] not in result, f"Duplicate import: {match[1]}")
        result[match[1]] = dict(pairs)
    require(set(result) == NAMES, "Saved TMDL must define exactly the twelve supported CSV imports")
    return result


def keys(frame, columns, label):
    require(not frame[columns].isna().any().any(), f"Null key: {label}")
    require(all(frame[c].astype("string").str.strip().ne("").all() for c in columns), f"Empty key: {label}")
    require(not frame.duplicated(columns).any(), f"Duplicate key: {label}")
    return set(frame[columns].itertuples(index=False, name=None))


def read_database(database):
    database = Path(database).resolve()
    if not database.is_file():
        raise FileNotFoundError("Validated SQLite input is missing; run preparation, peers, and src/03_build_powerbi_exports.py first")
    queries = {
        "fact": "SELECT * FROM fact_listing_month",
        "bench": "SELECT * FROM fact_peer_benchmark",
        "listings": "SELECT * FROM dim_listing",
        "months": "SELECT * FROM dim_month",
        "coverage": "SELECT * FROM fact_coverage_month",
        "examples": "SELECT * FROM peer_examples_latest",
        "priority": "SELECT listing_id,month_date,priority_tier,action,direction,deviation_rank,review_order FROM vw_latest_review_priority",
        "transitions": "SELECT listing_id,month_date,mom_change_pct FROM vw_listing_rate_transitions",
    }
    # URI mode=ro cannot create a missing database or alter a real database.
    with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as con:
        con.execute("PRAGMA query_only=ON")
        con.execute("BEGIN")
        require(con.execute("PRAGMA integrity_check").fetchone()[0] == "ok", "SQLite integrity check failed")
        require(not con.execute("PRAGMA foreign_key_check").fetchall(), "SQLite foreign-key violations")
        try:
            frames = {name: pd.read_sql_query(query, con) for name, query in queries.items()}
        except (sqlite3.Error, pd.errors.DatabaseError) as exc:
            raise ValueError("Missing/incompatible validated tables or views; rebuild only the Python/SQL data pipeline") from exc
    for frame in frames.values():
        for column in (c for c in frame if c.endswith("_id")):
            require(frame[column].dropna().map(lambda v: isinstance(v, str)).all(),
                    f"{column} must already be stored as text; numeric IDs cannot be repaired safely")
            frame[column] = frame[column].astype("string")
    return frames


def transform(source):
    """Preserve the validated data-shaping logic, without importing its old builder."""
    f = source["fact"].copy()
    require(not f.empty, "No listing observations; refusing empty model imports")
    fact_keys = keys(f, KEYS["FactListingMonth"], "fact")
    require(keys(source["bench"], KEYS["FactListingMonth"], "benchmarks") == fact_keys,
            "Benchmark and observation key populations differ")
    require(keys(source["transitions"], KEYS["FactListingMonth"], "transitions") == fact_keys,
            "Transitions do not cover exactly the observations")
    for column in ["active", "same_listing_prev_month"]:
        require(f[column].isin([0, 1]).all(), f"Invalid non-null activity flag: {column}")
    latest = f.month_date.max()
    expected_priority = keys(f[(f.month_date == latest) & f.active.eq(1)], KEYS["FactListingMonth"], "latest active")
    require(keys(source["priority"], KEYS["FactListingMonth"], "priority") == expected_priority,
            "Priority view must contain exactly the latest active population")
    f = f.merge(source["bench"], on=["listing_id", "month_date"], validate="one_to_one")
    f = f.merge(source["priority"], on=["listing_id", "month_date"], how="left", validate="one_to_one")
    f = f.merge(source["transitions"], on=["listing_id", "month_date"], validate="one_to_one")
    start = (pd.Timestamp(latest) - pd.DateOffset(months=11)).strftime("%Y-%m-%d")
    cohort = f[f.active.eq(1) & f.month_date.ge(start)].groupby("listing_id").month_date.nunique()
    f["stable_cohort"] = f.listing_id.isin(cohort[cohort == 12].index) & f.month_date.ge(start)
    f["active"] = f.active.eq(1)
    f["same_listing_prev_month"] = f.same_listing_prev_month.eq(1)
    require(f.bedrooms.dropna().map(lambda x: x >= 0 and x % 1 == 0).all(), "Invalid bedroom count")
    f["bedroom_label"] = f.bedrooms.map(lambda n: "Unknown" if pd.isna(n) else "Studio" if n == 0 else str(int(n)))
    f["area_label"] = f.neighborhood.fillna("Unknown area")
    f["peer_iqr_ratio"] = (f.peer_p75_aed - f.peer_p25_aed) / f.peer_median_aed
    f["deviation_direction"] = f.premium_pct.map(lambda v: "Unassessed" if pd.isna(v) else "Above Peer Benchmark" if v > 0 else "Below Peer Benchmark" if v < 0 else "At Peer Benchmark")
    f["mom_band"] = pd.cut(f.mom_change_pct, [-float("inf"), -50, -20, -5, 5, 20, 50, float("inf")],
                          labels=["<-50%", "-50 to -20%", "-20 to -5%", "-5 to 5%", "5 to 20%", "20 to 50%", ">50%"]).astype(object)
    months = source["months"].copy()
    months["month_name"] = pd.to_datetime(months.month_date).dt.month.map(dict(enumerate(MONTHS, 1)))
    accommodation = f[["room_type"]].drop_duplicates().sort_values("room_type")
    accommodation["accommodation_label"] = accommodation.room_type.str.replace("_", " ", regex=False).str.capitalize()
    bedrooms = f[["bedroom_label", "bedrooms"]].drop_duplicates().copy()
    bedrooms["bedroom_sort"] = bedrooms.bedrooms.fillna(99).astype(int)
    coordinates = f[["listing_id", "month_date", "latitude", "longitude"]].rename(columns={"listing_id": "peer_listing_id"})
    examples = source["examples"].merge(coordinates, on=["peer_listing_id", "month_date"], validate="many_to_one")
    require(len(examples) == len(source["examples"]), "Peer-coordinate join dropped examples")
    return {
        "FactListingMonth": f, "DimListing": source["listings"].copy(), "DimMonth": months,
        "DimAccommodation": accommodation, "DimBedrooms": bedrooms[["bedroom_label", "bedroom_sort"]],
        "DimArea": f[["area_label"]].drop_duplicates().sort_values("area_label"),
        "CoverageMonth": source["coverage"].copy(), "PeerExamples": examples,
        "MetricSelector": pd.DataFrame({"Metric": ["Reported rate (AED)", "Estimated occupancy", "Estimated revenue (AED)"]}),
        "CohortSelector": pd.DataFrame({"Cohort": ["Full sample", "Fixed 12-month cohort"]}),
        "ReviewThreshold": pd.DataFrame({"Threshold": [10, 15, 20, 25, 30, 35, 40, 50]}),
        "Analytics": pd.DataFrame({"placeholder": [1]}),
    }


def conform(frames, contract):
    require(set(frames) == NAMES, "Incorrect model file set")
    result = {}
    for name, spec in contract.items():
        frame = frames[name].copy()
        require(set(frame.columns) == set(spec), f"Column contract mismatch: {name}")
        frame = frame[list(spec)]
        for col, kind in spec.items():
            series = frame[col]
            if kind == "type text":
                frame[col] = series.astype("string")
            elif kind == "type date":
                require(series.notna().all() and series.astype(str).str.fullmatch(r"\d{4}-\d{2}-\d{2}").all(), f"Invalid date: {name}.{col}")
                dates = pd.to_datetime(series, format="%Y-%m-%d", errors="raise")
                require(dates.dt.day.eq(1).all(), f"Not a month start: {name}.{col}")
                frame[col] = dates.dt.strftime("%Y-%m-%d")
            elif kind == "type logical":
                mapped = series.astype("string").str.lower().map({"true": True, "false": False, "1": True, "0": False})
                require(mapped.notna().all(), f"Invalid boolean: {name}.{col}")
                frame[col] = mapped.astype(bool)
            elif kind in {"type number", "Int64.Type"}:
                values = pd.to_numeric(series, errors="raise")
                require(np.isfinite(values.dropna().astype(float)).all(), f"Nonfinite value: {name}.{col}")
                if kind == "Int64.Type":
                    require(values.dropna().mod(1).eq(0).all(), f"Noninteger value: {name}.{col}")
                    values = values.astype("Int64")
                frame[col] = values
            else:
                raise ValueError(f"Unsupported saved M type: {kind}")
        keys(frame, KEYS[name], name)
        # Empty examples are valid if there are no eligible latest subjects, not a substitute for missing input.
        require(not frame.empty or name == "PeerExamples", f"Unexpected empty import: {name}")
        result[name] = frame
    return result


def validate(frames, expect_reference=False):
    f, months, coverage = (frames[x] for x in ["FactListingMonth", "DimMonth", "CoverageMonth"])
    calendar = sorted(months.month_date)
    require(calendar == list(pd.date_range(calendar[0], calendar[-1], freq="MS").strftime("%Y-%m-%d")), "Reporting calendar is not contiguous")
    require(set(f.month_date) == set(calendar) == set(coverage.month_date), "Fact/calendar/coverage months differ")
    for dim, column in [("DimListing", "listing_id"), ("DimMonth", "month_date"), ("DimAccommodation", "room_type"), ("DimBedrooms", "bedroom_label"), ("DimArea", "area_label")]:
        require(f[column].notna().all() and f[column].isin(frames[dim][column]).all(), f"Missing dimension relationship: {dim}")
    require(set(f.listing_id) == set(frames["DimListing"].listing_id), "Listing dimension/population mismatch")
    actual = f.groupby("month_date").agg(observed_listings=("listing_id", "size"), active_listings=("active", "sum"))
    observed = coverage.set_index("month_date").loc[actual.index]
    for col in ["observed_listings", "active_listings"]:
        require(actual[col].eq(observed[col]).all(), f"Coverage population mismatch: {col}")
    for col in ["native_avg_daily_rate", "native_revenue"]:
        require(f[col].dropna().ge(0).all(), f"Negative metric: {col}")
    require(f.occupancy.dropna().between(0, 1).all(), "Occupancy must be a fraction")
    eligible = f.comparison_status.eq("Eligible")
    require((f.loc[eligible, "peer_count"].ge(10) & f.loc[eligible, "peer_median_aed"].gt(0)).all(), "Invalid eligible benchmark")
    require(f.loc[~eligible, "peer_median_aed"].isna().all(), "Ineligible benchmarks must remain blank")
    e = frames["PeerExamples"]
    fk = keys(f, KEYS["FactListingMonth"], "facts")
    for id_col in ["listing_id", "peer_listing_id"]:
        require(set(e[[id_col, "month_date"]].itertuples(index=False, name=None)) <= fk, "Example property-month missing")
    require(e.month_date.eq(calendar[-1]).all() and e.listing_id.ne(e.peer_listing_id).all(), "Examples must be latest-only and exclude subject")
    require(e.groupby("listing_id").size().le(5).all(), "More than five examples")
    latest = f[f.month_date.eq(calendar[-1])]
    active = latest[latest.active]
    known = active.area_label.notna() & active.area_label.str.strip().ne("") & active.area_label.ne("Unknown area")
    stats = dict(observations=len(f), listings=f.listing_id.nunique(), months=len(calendar), first_month=calendar[0], last_month=calendar[-1],
                 latest_observed=len(latest), latest_active=len(active), latest_benchmarked=int(active.comparison_status.eq("Eligible").sum()),
                 stronger=int(latest.priority_tier.eq(1).sum()), comparability=int(latest.priority_tier.eq(2).sum()), known_area=int(known.sum()))
    if expect_reference:
        expected = dict(observations=99745, listings=4364, months=60, first_month="2021-03-01", last_month="2026-02-01",
                        latest_observed=2471, latest_active=1955, latest_benchmarked=1615, stronger=173, comparability=729, known_area=452)
        require(stats == expected, f"Reference population mismatch: {stats}")
    return stats


def read_exports(folder, contract):
    return conform({name: pd.read_csv(Path(folder) / (name + ".csv"), dtype={c: "string" for c, t in spec.items() if t == "type text"},
                                    keep_default_na=False, na_values=[""], low_memory=False)
                    for name, spec in contract.items()}, contract)


def publish(frames, folder, contract):
    folder = Path(folder).resolve()
    require(not any(x.endswith((".Report", ".SemanticModel")) for x in folder.parts), "Refusing output inside Power BI definitions")
    expected = {n + ".csv" for n in NAMES}
    require(not folder.exists() or {x.name for x in folder.glob("*.csv")} <= expected, "Unexpected CSVs in model output directory; inspect without deleting them")
    folder.mkdir(parents=True, exist_ok=True)
    # Staging/backups are also CSV data under the configured model directory.
    # Recoverable exceptions roll back; a machine crash is not a multi-file transaction.
    with tempfile.TemporaryDirectory(prefix=".stage_", dir=folder) as temp:
        stage = Path(temp).resolve()
        require(folder in stage.parents, "Unsafe staging directory")
        backup = stage / "backup"
        backup.mkdir()
        for name, frame in frames.items():
            frame.to_csv(stage / (name + ".csv"), index=False)
        reread = read_exports(stage, contract)
        for name in NAMES:
            pd.testing.assert_frame_equal(frames[name].reset_index(drop=True), reread[name].reset_index(drop=True),
                                          check_dtype=False, rtol=1e-12, atol=1e-9)
        validate(reread)
        replaced = []
        try:
            for name in sorted(expected):
                target = folder / name
                if target.exists():
                    shutil.copy2(target, backup / name)
                os.replace(stage / name, target)
                replaced.append(name)
        except BaseException:
            for name in reversed(replaced):
                if (backup / name).exists():
                    os.replace(backup / name, folder / name)
                else:
                    (folder / name).unlink()
            raise
    require({x.name for x in folder.glob("*.csv")} == expected, "Final model file set differs")


def export(database, data_folder, definition=DEFINITION, expect_reference=False):
    contract = contracts(definition)
    frames = conform(transform(read_database(database)), contract)
    stats = validate(frames, expect_reference)
    publish(frames, Path(data_folder) / "model", contract)
    return {"files": len(frames), **stats}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=ROOT / "data/processed/dubai_rentals.sqlite")
    parser.add_argument("--data-folder", type=Path, default=ROOT / "powerbi/data", help="DataFolder parent; CSVs go in its model subdirectory")
    parser.add_argument("--definition", type=Path, default=DEFINITION, help="Read-only saved TMDL definition directory")
    parser.add_argument("--expect-reference", action="store_true", help="Also require the audited March 2021–February 2026 population")
    args = parser.parse_args()
    try:
        print(json.dumps(export(args.database, args.data_folder, args.definition, args.expect_reference), indent=2))
    except (ValueError, FileNotFoundError, sqlite3.Error, pd.errors.DatabaseError) as exc:
        parser.exit(2, f"Model data export failed: {exc}\n")


if __name__ == "__main__":
    main()

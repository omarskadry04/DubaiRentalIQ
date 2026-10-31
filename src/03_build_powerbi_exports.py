"""Build a validated SQLite analytical database and Power BI exports.

Run after Notebooks 03 and 04 have generated the six processed CSV files.
The existing SQLite database remains untouched if a build or validation fails.
Source and raw data are never modified.
"""
from __future__ import annotations

import os
import shutil
import sqlite3
import tempfile
import runpy
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
EXPORTS = ROOT / "powerbi" / "data"
SQL_FILE = ROOT / "sql" / "02_analytics_views.sql"
DB_FILE = PROCESSED / "dubai_rentals.sqlite"
_io = runpy.run_path(str(Path(__file__).with_name('pipeline_io.py')))

# Loading dimensions first keeps foreign-key enforcement active during import.
LOAD_ORDER = (
    "dim_listing", "dim_month", "fact_listing_month",
    "fact_coverage_month", "fact_peer_benchmark", "peer_examples_latest",
)
TEXT_KEYS = {"listing_id", "peer_listing_id"}
BOOL_COLUMNS = {"active", "same_listing_prev_month", "enriched_metadata_available"}

SCHEMA_FILE = ROOT / 'sql/01_database_schema.sql'


def _read_processed() -> dict[str, pd.DataFrame]:
    frames = {}
    for name in LOAD_ORDER:
        path = PROCESSED / f"{name}.csv"
        if not path.is_file():
            raise FileNotFoundError(f"Missing processed input: {path}. Run Notebooks 03–04 first.")
        text_dtypes = {key: "string" for key in TEXT_KEYS}
        if name == "dim_listing":
            text_dtypes.update({"host_id": "string", "property_type": "string", "superhost": "string"})
        df = pd.read_csv(path, dtype=text_dtypes, low_memory=False)
        for key in TEXT_KEYS.intersection(df.columns):
            if df[key].isna().any() or df[key].str.strip().eq("").any():
                raise ValueError(f"{name}.{key} contains a missing/blank identifier")
            df[key] = df[key].astype(str)
        for col in (BOOL_COLUMNS.intersection(df.columns)
                    if name in {"fact_listing_month", "dim_listing"} else []):
            values = df[col].astype("string").str.lower().map({"true": 1, "false": 0, "1": 1, "0": 0})
            if values.isna().any():
                raise ValueError(f"{name}.{col}: unexpected/missing boolean value")
            df[col] = values.astype(int)
        frames[name] = df
    _validate_coverage_source(frames)
    return frames


def _validate_coverage_source(frames: dict[str, pd.DataFrame]) -> None:
    """Reject stale or broken monthly coverage before publishing exports.

    This check is deliberately independent of the stored coverage summaries.
    A blank count must not silently reach Power BI just because table keys match.
    """
    fact = frames["fact_listing_month"]
    coverage = frames["fact_coverage_month"].copy()
    if coverage["same_listing_prev_month"].isna().any():
        raise ValueError("Coverage source has null returning-listing counts; rerun Notebook 03")
    expected = fact.groupby("month_date", dropna=False).agg(
        observed_listings=("listing_id", "size"),
        active_listings=("active", "sum"),
        same_listing_prev_month=("same_listing_prev_month", "sum"),
    ).reset_index()
    joined = expected.merge(coverage, on="month_date", how="outer",
                            suffixes=("_fact", "_coverage"), validate="one_to_one",
                            indicator=True)
    if not joined["_merge"].eq("both").all():
        raise ValueError("Coverage reporting months do not match fact months")
    for field in ("observed_listings", "active_listings", "same_listing_prev_month"):
        a = pd.to_numeric(joined[field + "_fact"], errors="coerce")
        b = pd.to_numeric(joined[field + "_coverage"], errors="coerce")
        if b.isna().any() or not a.eq(b).all():
            raise ValueError(f"Coverage {field} disagrees with source facts; rerun Notebook 03")
    if not joined["same_listing_prev_month_coverage"].le(joined["observed_listings_coverage"]).all():
        raise ValueError("Returning listing count exceeds observed sample")


def _validate_frame_columns(frames: dict[str, pd.DataFrame], conn: sqlite3.Connection) -> None:
    for name, df in frames.items():
        expected = [r[1] for r in conn.execute(f"PRAGMA table_info({name})")]
        if list(df.columns) != expected:
            raise ValueError(f"{name} column mismatch. Expected {expected}; got {list(df.columns)}")


def _assert_equal(actual: int | float, expected: int | float, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: SQL={actual}; source={expected}")


def _validate(conn: sqlite3.Connection, frames: dict[str, pd.DataFrame]) -> dict:
    if conn.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        raise AssertionError("Foreign-key enforcement is disabled")
    assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        raise AssertionError(f"Foreign key violations: {violations[:5]}")
    counts = {}
    for table, data in frames.items():
        counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        _assert_equal(counts[table], len(data), f"{table} row reconciliation")

    # Validate every declared primary key and every corresponding source business key.
    key_map = {
        "dim_listing": ["listing_id"],
        "dim_month": ["month_date"],
        "fact_listing_month": ["listing_id", "month_date"],
        "fact_coverage_month": ["month_date"],
        "fact_peer_benchmark": ["listing_id", "month_date"],
        "peer_examples_latest": ["listing_id", "month_date", "peer_listing_id"],
    }
    for table, keys in key_map.items():
        if frames[table][keys].isna().any().any() or frames[table].duplicated(keys).any():
            raise AssertionError(f"Source has invalid business keys: {table}")
        cols = ", ".join(keys)
        dupes = conn.execute(
            f"SELECT COUNT(*) FROM (SELECT {cols}, COUNT(*) n FROM {table} GROUP BY {cols} HAVING n>1)"
        ).fetchone()[0]
        _assert_equal(dupes, 0, f"{table} duplicate primary keys")

    for name, column in (("fact_listing_month", "listing_id"), ("peer_examples_latest", "peer_listing_id")):
        types = conn.execute(f"SELECT DISTINCT typeof({column}) FROM {name}").fetchall()
        if types and types != [("text",)]:
            raise AssertionError(f"{name}.{column} must use SQLite TEXT affinity; got {types}")

    latest = str(frames["fact_listing_month"].month_date.max())
    latest_fact = frames["fact_listing_month"].query("month_date == @latest")
    latest_bench = frames["fact_peer_benchmark"].query("month_date == @latest")
    expected_review = int((
        latest_bench.comparison_status.eq("Eligible")
        & latest_bench.review_signal.isin(["Review", "Large deviation"])
    ).sum())
    review_queue = conn.execute("SELECT COUNT(*) FROM vw_latest_price_review_queue").fetchone()[0]
    _assert_equal(review_queue, expected_review, "latest pricing review queue")

    # Reconcile latest review view values, not just the number of flagged listings.
    fact_cols = ["listing_id", "month_date", "native_avg_daily_rate"]
    bench_cols = ["listing_id", "month_date", "peer_median_aed", "premium_pct", "peer_count", "radius_km"]
    expected_queue = (
        latest_fact[fact_cols].merge(
            latest_bench.loc[
                latest_bench.comparison_status.eq("Eligible")
                & latest_bench.review_signal.isin(["Review", "Large deviation"]),
                bench_cols,
            ],
            on=["listing_id", "month_date"],
            validate="one_to_one",
        )
        .sort_values("listing_id")
        .reset_index(drop=True)
    )
    sql_queue = pd.read_sql_query("""
        SELECT listing_id, subject_adr_aed, peer_median_aed,
               premium_pct, peer_count, radius_km
        FROM vw_latest_price_review_queue ORDER BY listing_id
    """, conn)
    if sql_queue.listing_id.tolist() != expected_queue.listing_id.tolist():
        raise AssertionError("Review queue contains wrong listing identifiers")
    checks = {
        "subject_adr_aed": (expected_queue.native_avg_daily_rate, 1e-7),
        "peer_median_aed": (expected_queue.peer_median_aed, 0.051),
        "premium_pct": (expected_queue.premium_pct, 0.051),
        "peer_count": (expected_queue.peer_count, 1e-7),
        "radius_km": (expected_queue.radius_km, 1e-7),
    }
    for column, (expected, tolerance) in checks.items():
        if not ((sql_queue[column].to_numpy() - expected.to_numpy()).__abs__() <= tolerance).all():
            raise AssertionError(f"Review queue field does not reconcile: {column}")

    coverage_rows = conn.execute("SELECT COUNT(*) FROM vw_monthly_coverage_and_performance").fetchone()[0]
    _assert_equal(coverage_rows, len(frames["fact_coverage_month"]), "monthly coverage view")
    coverage_match = conn.execute("""
        SELECT COUNT(*) FROM vw_monthly_coverage_and_performance v
        JOIN fact_coverage_month c ON v.month_date=c.month_date
        WHERE v.observed_listings=c.observed_listings
          AND v.active_listings=c.active_listings
    """).fetchone()[0]
    _assert_equal(coverage_match, coverage_rows, "coverage view content")

    expected_segments = latest_fact.loc[(latest_fact.active == 1) & latest_fact.bedrooms.notna()]
    segment_count = conn.execute("""
        SELECT SUM(active_sample_listings) FROM vw_segment_monthly_rates
        WHERE month_date=?
    """, (latest,)).fetchone()[0]
    _assert_equal(int(segment_count or 0), len(expected_segments), "segment view listing reconciliation")
    expected_by_segment = (
        expected_segments.groupby(["room_type", "bedrooms"], dropna=False)
        .agg(expected_count=("listing_id", "size"), expected_mean_adr=("native_avg_daily_rate", "mean"))
        .reset_index()
    )
    sql_by_segment = pd.read_sql_query("""
        SELECT room_type, bedrooms, active_sample_listings, mean_adr_aed
        FROM vw_segment_monthly_rates WHERE month_date=?
    """, conn, params=(latest,))
    merged_segments = sql_by_segment.merge(
        expected_by_segment, on=["room_type", "bedrooms"], validate="one_to_one", indicator=True
    )
    if (len(merged_segments) != len(sql_by_segment)
            or len(merged_segments) != len(expected_by_segment)
            or not merged_segments._merge.eq("both").all()):
        raise AssertionError("Latest segment groups do not reconcile")
    if not (merged_segments.active_sample_listings == merged_segments.expected_count).all():
        raise AssertionError("Segment active listing counts do not reconcile")
    if not ((merged_segments.mean_adr_aed - merged_segments.expected_mean_adr).abs() <= 0.051).all():
        raise AssertionError("Segment average ADR does not reconcile")

    last_status = conn.execute("""
        SELECT SUM(listing_count) FROM vw_latest_benchmark_status
    """).fetchone()[0]
    _assert_equal(int(last_status or 0), len(latest_bench), "benchmark status view reconciliation")

    # Independently derive the same-listing consecutive-month count using pandas.
    history = frames["fact_listing_month"]["listing_id month_date active".split()].copy()
    history["period"] = pd.PeriodIndex(history["month_date"], freq="M")
    history.sort_values(["listing_id", "period"], inplace=True)
    previous_period = history.groupby("listing_id")["period"].shift(1)
    previous_active = history.groupby("listing_id")["active"].shift(1)
    expected_pairs = int((
        history.active.eq(1) & previous_active.eq(1)
        & ((history.period - previous_period).apply(lambda p: p.n if pd.notna(p) else -999) == 1)
    ).sum())
    actual_pairs = conn.execute("SELECT COUNT(*) FROM vw_pairwise_same_listing_month").fetchone()[0]
    _assert_equal(actual_pairs, expected_pairs, "same-listing consecutive month view")

    # A smoke test of actual enforcement, rolled back so the exported database is unchanged.
    conn.execute("SAVEPOINT fk_enforcement_test")
    fk_rejected = False
    try:
        conn.execute("""
            INSERT INTO fact_coverage_month(month_date, observed_listings, active_listings)
            VALUES ('2099-01-01', 0, 0)
        """)
    except sqlite3.IntegrityError:
        fk_rejected = True
    finally:
        conn.execute("ROLLBACK TO fk_enforcement_test")
        conn.execute("RELEASE fk_enforcement_test")
    if not fk_rejected:
        raise AssertionError("Invalid month unexpectedly accepted despite foreign key")

    return {
        "table_counts": counts,
        "latest_month": latest,
        "latest_observed_listings": len(latest_fact),
        "review_queue": review_queue,
        "review_queue_values_reconciled": True,
        "segment_adr_values_reconciled": True,
        "monthly_coverage_rows": coverage_rows,
        "latest_segment_listings": int(segment_count or 0),
        "latest_benchmark_status_rows": int(last_status or 0),
        "same_listing_month_pairs": actual_pairs,
        "foreign_keys_enabled": True,
        "foreign_key_violations": len(violations),
        "fk_insert_rejected": fk_rejected,
        "sqlite_integrity": "ok",
    }


def run() -> dict:
    """Create a fully validated temporary DB, then publish it atomically.

    Counts are inferred from the supplied processed sources, not hardcoded to
    the October 2026 project snapshot.
    """
    PROCESSED.mkdir(parents=True, exist_ok=True)
    EXPORTS.mkdir(parents=True, exist_ok=True)
    if not SQL_FILE.is_file():
        raise FileNotFoundError(f"Missing SQL views: {SQL_FILE}")
    frames = _read_processed()
    # A hard termination during multi-file publication must not silently mix runs.
    for manifest in ('preparation_manifest.json', 'benchmark_manifest.json'):
        _io['verify_manifest'](PROCESSED, manifest)
    benchmark_source = json.loads((PROCESSED/'benchmark_manifest.json').read_text())['sources']
    if benchmark_source['fact_listing_month.csv'] != _io['digest'](PROCESSED/'fact_listing_month.csv'):
        raise ValueError('Benchmarks belong to a different fact generation; rerun benchmarking')
    with tempfile.TemporaryDirectory(prefix="sqlite_build_", dir=PROCESSED) as build_dir, \
         tempfile.TemporaryDirectory(prefix="bi_exports_", dir=EXPORTS.parent) as export_dir:
        temp_db = Path(build_dir) / "validated.sqlite"
        conn = sqlite3.connect(temp_db)
        try:
            conn.execute("PRAGMA foreign_keys=ON")
            conn.executescript(SCHEMA_FILE.read_text(encoding='utf-8'))
            _validate_frame_columns(frames, conn)
            for name in LOAD_ORDER:
                frames[name].to_sql(name, conn, if_exists="append", index=False, chunksize=4000)
            conn.executescript(SQL_FILE.read_text(encoding="utf-8"))
            conn.commit()
            audit = _validate(conn, frames)
            validation_sql = SQL_FILE.with_name('08_data_validation.sql')
            validation = pd.read_sql_query(validation_sql.read_text(encoding='utf-8'), conn)
            if not validation.violations.eq(0).all():
                raise AssertionError(validation.loc[validation.violations.ne(0)].to_dict('records'))
            audit['independent_sql_checks'] = validation.to_dict('records')
            conn.commit()
        finally:
            conn.close()

        staged_exports = Path(export_dir)
        for name in LOAD_ORDER:
            shutil.copy2(PROCESSED / f"{name}.csv", staged_exports / f"{name}.csv")
        # A database is published only after all validations have succeeded.
        publication = {DB_FILE: temp_db}
        publication.update({EXPORTS / f"{name}.csv": staged_exports / f"{name}.csv" for name in LOAD_ORDER})
        _io['promote'](publication)

    return audit


if __name__ == "__main__":
    report = run()
    print("SQLite build passed, all relations validated:")
    for name, value in report.items():
        print(f"  {name}: {value}")

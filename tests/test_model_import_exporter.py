"""Synthetic, temporary-directory tests. Never reads private provider inputs."""
import contextlib
import importlib.util
import io
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ModelImports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix=".test_export_", dir=ROOT)
        cls.root = Path(cls.temp.name).resolve()
        assert ROOT.resolve() in cls.root.parents
        cls.addClassCleanup(cls.temp.cleanup)
        fixture = load(ROOT / "tests/test_clean_pipeline.py")
        fixture.sources(cls.root)
        prep = load(ROOT / "src/01_validate_and_prepare.py")
        peers = load(ROOT / "src/02_build_peer_benchmarks.py")
        database = load(ROOT / "src/03_build_powerbi_exports.py")
        prep.RAW = cls.root / "data/raw"
        prep.OUT = peers.OUT = database.PROCESSED = cls.root / "data/processed"
        prep.REPORT = peers.REPORT = cls.root / "reports"
        database.EXPORTS = cls.root / "intermediate"
        database.DB_FILE = cls.root / "data/processed/dubai_rentals.sqlite"
        with contextlib.redirect_stdout(io.StringIO()):
            prep.run()
            peers.run()
            database.run()
        cls.database = database.DB_FILE
        cls.exporter = load(ROOT / "src/08_export_model_imports.py")
        cls.contract = cls.exporter.contracts()

    def setUp(self):
        self.temp_case = tempfile.TemporaryDirectory(dir=self.root)
        self.case = Path(self.temp_case.name).resolve()
        assert self.root in self.case.parents
        self.addCleanup(self.temp_case.cleanup)
        self.db = self.case / "fixture.sqlite"
        shutil.copy2(self.database, self.db)
        self.folder = self.case / "imports"

    def frames(self):
        return self.exporter.conform(self.exporter.transform(self.exporter.read_database(self.db)), self.contract)

    def test_twelve_contracts_and_exact_text_ids(self):
        before = self.db.read_bytes()
        stats = self.exporter.export(self.db, self.folder)
        self.assertEqual((stats['files'], stats['observations'], stats['listings'], stats['months']), (12, 38, 13, 3))
        self.assertEqual(self.db.read_bytes(), before)
        self.assertEqual({p.stem for p in (self.folder / 'model').glob('*.csv')}, self.exporter.NAMES)
        frames = self.exporter.read_exports(self.folder / 'model', self.contract)
        self.assertTrue(frames['DimListing'].host_id.eq('0001234567890123456789').all())
        self.assertEqual(frames['FactListingMonth'].listing_id.iloc[0], '9000000000000000000')
        for name, frame in frames.items():
            self.assertEqual(list(frame), list(self.contract[name]))

    def test_missing_database_creates_no_output(self):
        with self.assertRaisesRegex(FileNotFoundError, 'SQLite input is missing'):
            self.exporter.export(self.case / 'missing.sqlite', self.folder)
        self.assertFalse(self.folder.exists())

    def test_missing_view_creates_no_output(self):
        with contextlib.closing(sqlite3.connect(self.db)) as con, con:
            con.execute('DROP VIEW vw_listing_rate_transitions')
        with self.assertRaisesRegex(ValueError, 'Missing/incompatible'):
            self.exporter.export(self.db, self.folder)
        self.assertFalse(self.folder.exists())

    def test_duplicate_and_missing_benchmark_keys_rejected(self):
        src = self.exporter.read_database(self.db)
        original = src['bench'].copy()
        src['bench'] = pd.concat([original, original.iloc[[0]]])
        with self.assertRaisesRegex(ValueError, 'Duplicate key'):
            self.exporter.transform(src)
        src['bench'] = original.iloc[1:]
        with self.assertRaisesRegex(ValueError, 'populations differ'):
            self.exporter.transform(src)

    def test_zero_blank_inactive_and_gap_remain_distinct(self):
        with contextlib.closing(sqlite3.connect(self.db)) as con, con:
            con.execute("UPDATE fact_listing_month SET active=0,occupancy=0,native_revenue=NULL,native_booked_rate_avg=NULL WHERE listing_id=? AND month_date='2025-01-01'", ('9000000000000000000',))
            con.execute("UPDATE fact_coverage_month SET active_listings=active_listings-1 WHERE month_date='2025-01-01'")
        self.exporter.export(self.db, self.folder)
        f = self.exporter.read_exports(self.folder / 'model', self.contract)['FactListingMonth']
        subject = f[f.listing_id.eq('9000000000000000000')]
        row = subject[subject.month_date.eq('2025-01-01')].iloc[0]
        self.assertFalse(row.active)
        self.assertEqual(row.occupancy, 0)
        self.assertTrue(pd.isna(row.native_revenue))
        self.assertTrue(pd.isna(row.native_booked_rate_avg))
        self.assertFalse(subject.month_date.eq('2025-02-01').any())
        self.assertTrue(pd.isna(subject[subject.month_date.eq('2025-03-01')].iloc[0].mom_change_pct))

    def test_bad_contract_and_noninteger_rejected(self):
        frames = self.frames()
        frames['FactListingMonth']['unexpected'] = 1
        with self.assertRaisesRegex(ValueError, 'Column contract mismatch'):
            self.exporter.conform(frames, self.contract)
        frames = self.frames()
        frames['FactListingMonth']['peer_count'] = 10.5
        with self.assertRaisesRegex(ValueError, 'Noninteger'):
            self.exporter.conform(frames, self.contract)

    def test_calendar_relationship_and_coverage_rejected(self):
        frames = self.frames()
        frames['DimMonth'] = frames['DimMonth'].iloc[[0, 2]]
        with self.assertRaisesRegex(ValueError, 'not contiguous'):
            self.exporter.validate(frames)
        frames = self.frames()
        frames['DimListing'] = frames['DimListing'].iloc[1:]
        with self.assertRaisesRegex(ValueError, 'dimension relationship'):
            self.exporter.validate(frames)
        frames = self.frames()
        frames['CoverageMonth'].loc[0, 'active_listings'] += 1
        with self.assertRaisesRegex(ValueError, 'Coverage population mismatch'):
            self.exporter.validate(frames)

    def test_reference_gate_preserves_existing_exports(self):
        self.exporter.export(self.db, self.folder)
        before = {p.name: p.read_bytes() for p in (self.folder / 'model').glob('*.csv')}
        with self.assertRaisesRegex(ValueError, 'Reference population mismatch'):
            self.exporter.export(self.db, self.folder, expect_reference=True)
        self.assertEqual(before, {p.name: p.read_bytes() for p in (self.folder / 'model').glob('*.csv')})

    def test_interrupted_promotion_rolls_back(self):
        self.exporter.export(self.db, self.folder)
        before = {p.name: p.read_bytes() for p in (self.folder / 'model').glob('*.csv')}
        frames = self.frames()
        frames['Analytics'].loc[0, 'placeholder'] = 2
        real_replace = self.exporter.os.replace
        calls = 0

        def interrupted(source, target):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError('simulated interruption')
            return real_replace(source, target)

        with patch.object(self.exporter.os, 'replace', side_effect=interrupted):
            with self.assertRaisesRegex(OSError, 'simulated interruption'):
                self.exporter.publish(frames, self.folder / 'model', self.contract)
        self.assertEqual(before, {p.name: p.read_bytes() for p in (self.folder / 'model').glob('*.csv')})
        self.assertFalse(list((self.folder / 'model').glob('.stage_*')))

    def test_unexpected_files_and_definition_output_protected(self):
        self.folder.mkdir()
        model = self.folder / 'model'
        model.mkdir()
        (model / 'unrelated.csv').write_text('keep me', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Unexpected CSVs'):
            self.exporter.export(self.db, self.folder)
        self.assertEqual((model / 'unrelated.csv').read_text(), 'keep me')
        with self.assertRaisesRegex(ValueError, 'Refusing output'):
            self.exporter.export(self.db, self.case / 'Protected.Report')


if __name__ == '__main__':
    unittest.main()

"""Stage complete files before publication; roll back recoverable promotion failures.

Atomic replacement protects each individual file. A multi-file set is not a
filesystem transaction: the manifest detects a mixed generation after hard
termination/power loss. Run only one writer at a time; rebuild after such a loss.
"""
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import numpy as np


def digest(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def promote(files):
    """Publish {destination: staged_file}, restoring originals on exceptions."""
    files = {Path(dst): Path(src) for dst, src in files.items()}
    backups = {}
    published = []
    with tempfile.TemporaryDirectory(dir=next(iter(files)).parent) as directory:
        for i, dst in enumerate(files):
            if dst.exists():
                backup = Path(directory) / str(i)
                shutil.copy2(dst, backup)
                backups[dst] = backup
        try:
            for dst, staged in files.items():
                os.replace(staged, dst)
                published.append(dst)
        except BaseException:
            for dst in reversed(published):
                if dst in backups:
                    os.replace(backups[dst], dst)
                else:
                    dst.unlink(missing_ok=True)
            raise


def publish_frames(frames, directory, manifest_name, sources=()):
    """Validate CSV round trips and publish a checksum manifest last."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="stage_", dir=directory) as temp:
        staged = Path(temp)
        manifest = {"sources": {Path(p).name: digest(p) for p in sources}, "outputs": {}}
        files = {}
        for name, frame in frames.items():
            path = staged / f"{name}.csv"
            frame.to_csv(path, index=False)
            types = {c: "string" for c in frame if c.endswith("_id")}
            reread = pd.read_csv(path, dtype=types, low_memory=False)
            if len(reread) != len(frame) or list(reread.columns) != list(frame.columns):
                raise ValueError(f"CSV round-trip mismatch: {name}")
            for column in frame:
                expected = frame[column].reset_index(drop=True)
                actual = reread[column]
                if pd.api.types.is_numeric_dtype(expected):
                    equal = np.allclose(pd.to_numeric(actual).to_numpy(dtype=float),
                                        expected.to_numpy(dtype=float, na_value=np.nan),
                                        rtol=1e-12, atol=1e-9, equal_nan=True)
                else:
                    equal = expected.astype('string').fillna('<NULL>').eq(
                        actual.astype('string').fillna('<NULL>')).all()
                if not equal:
                    raise ValueError(f"CSV values changed during serialization: {name}.{column}")
            keys = [c for c in ("listing_id", "month_date", "peer_listing_id") if c in frame]
            if keys and (reread[keys].isna().any().any() or reread.duplicated(keys).any()):
                raise ValueError(f"Invalid published keys: {name}")
            manifest["outputs"][path.name] = {"sha256": digest(path), "rows": len(frame)}
            files[directory / path.name] = path
        path = staged / manifest_name
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        files[directory / manifest_name] = path
        promote(files)


def verify_manifest(directory, name):
    directory = Path(directory)
    manifest = json.loads((directory / name).read_text(encoding="utf-8"))
    for filename, metadata in manifest["outputs"].items():
        if digest(directory / filename) != metadata["sha256"]:
            raise ValueError(f"Stale/incomplete generation: {filename}; rebuild upstream")
    return manifest

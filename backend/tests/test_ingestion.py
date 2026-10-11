"""Tests for the data ingestion pipeline (scripts/ingest_data.py).

Tests call the ingest module functions directly. They do NOT perform real
data insertion against a live database:

- ``_upsert_dataframe`` with an empty DataFrame returns before touching the
  connection, so ``conn=None`` is safe.
- ``ingest`` with no CSVs present is exercised with a mocked engine/Base so no
  real database connection is made; we only assert it logs the
  "not found, skipping" warnings and does not crash.

These tests import pandas (via ingest_data), so they only run where pandas is
installed (the Docker backend container). Locally the backend pytest suite
cannot be collected due to the missing analytics packages.
"""
import os
import sys
from unittest.mock import MagicMock

# Add the scripts/ directory to sys.path so `import ingest_data` resolves.
# (conftest.py has already added backend/ and set DATABASE_URL before this
# module is collected.)
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts")),
)

import pandas as pd  # noqa: E402  (path set up above)

import ingest_data  # noqa: E402
from app.models.olist import Customer  # noqa: E402


def test_upsert_dataframe_empty_returns_zero_stats():
    """An empty DataFrame short-circuits before any DB access (conn=None)."""
    stats = ingest_data._upsert_dataframe(
        pd.DataFrame(), Customer, ["customer_id"], conn=None
    )
    assert set(stats.keys()) == {"rows_read", "rows_inserted", "rows_skipped"}
    assert stats == {"rows_read": 0, "rows_inserted": 0, "rows_skipped": 0}


def test_ingest_missing_csvs_no_crash(tmp_path, monkeypatch, capsys):
    """With no CSVs in DATA_DIR, ingest() logs skip warnings and does not raise."""
    monkeypatch.setattr(ingest_data, "DATA_DIR", tmp_path)
    monkeypatch.setattr(ingest_data, "engine", MagicMock())
    monkeypatch.setattr(ingest_data, "Base", MagicMock())

    # Should not raise; no real DB connection occurs (all files missing).
    ingest_data.ingest(truncate=False)

    captured = capsys.readouterr().out
    assert "not found, skipping" in captured

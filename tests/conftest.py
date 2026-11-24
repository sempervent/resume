from __future__ import annotations

from pathlib import Path

import pytest

from career_docs.load import load_inventory


@pytest.fixture(scope="session")
def inventory():
    return load_inventory(Path(__file__).resolve().parents[1])


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]

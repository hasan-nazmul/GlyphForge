"""Shared test fixtures and configuration."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
INPUT_DIR = FIXTURES_DIR / "input"
EXPECTED_DIR = FIXTURES_DIR / "expected"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def input_dir() -> Path:
    return INPUT_DIR


@pytest.fixture
def basic_md() -> str:
    return (INPUT_DIR / "basic.md").read_text(encoding="utf-8")


@pytest.fixture
def math_md() -> str:
    return (INPUT_DIR / "math.md").read_text(encoding="utf-8")


@pytest.fixture
def tables_md() -> str:
    return (INPUT_DIR / "tables.md").read_text(encoding="utf-8")


@pytest.fixture
def code_md() -> str:
    return (INPUT_DIR / "code.md").read_text(encoding="utf-8")


@pytest.fixture
def messy_md() -> str:
    return (INPUT_DIR / "messy_llm.md").read_text(encoding="utf-8")


@pytest.fixture
def demo_md() -> str:
    demo_path = Path(__file__).parent.parent / "demo" / "logistic_regression.md"
    return demo_path.read_text(encoding="utf-8")

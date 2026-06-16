"""Shared fixtures for the test suite."""

import os
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
STEPS_DIR = REPO_ROOT / ".github" / "steps"


@pytest.fixture
def repo_root():
    return REPO_ROOT


@pytest.fixture
def workflows_dir():
    return WORKFLOWS_DIR


@pytest.fixture
def steps_dir():
    return STEPS_DIR


@pytest.fixture
def workflow_files():
    """Return a dict of workflow filename -> parsed YAML content."""
    workflows = {}
    for f in sorted(WORKFLOWS_DIR.glob("*.yml")):
        with open(f) as fh:
            workflows[f.name] = yaml.safe_load(fh)
    return workflows


@pytest.fixture
def step_files():
    """Return a dict of step filename -> content."""
    steps = {}
    for f in sorted(STEPS_DIR.iterdir()):
        steps[f.name] = f.read_text()
    return steps

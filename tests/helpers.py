"""Shared constants and utilities for the test suite."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
STEPS_DIR = REPO_ROOT / ".github" / "steps"

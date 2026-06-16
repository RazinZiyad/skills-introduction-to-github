"""Unit tests for step files.

Validates that all step markdown files exist, have proper content,
and are consistent with the workflow definitions.
"""

import pytest
from pathlib import Path

from tests.helpers import STEPS_DIR, REPO_ROOT


EXPECTED_STEP_FILES = [
    "-step.txt",
    "0-welcome.md",
    "1-create-a-branch.md",
    "2-commit-a-file.md",
    "3-open-a-pull-request.md",
    "4-merge-your-pull-request.md",
    "X-finish.md",
]


class TestStepFilePresence:
    """Verify all expected step files exist."""

    def test_all_step_files_exist(self, steps_dir):
        existing = [f.name for f in steps_dir.iterdir()]
        for step_file in EXPECTED_STEP_FILES:
            assert step_file in existing, f"Missing step file: {step_file}"

    def test_no_unexpected_step_files(self, steps_dir):
        existing = {f.name for f in steps_dir.iterdir()}
        expected = set(EXPECTED_STEP_FILES)
        unexpected = existing - expected
        assert not unexpected, f"Unexpected step files: {unexpected}"


class TestStepTracker:
    """Validate the step tracker file."""

    def test_step_tracker_exists(self, steps_dir):
        tracker = steps_dir / "-step.txt"
        assert tracker.exists()

    def test_step_tracker_contains_valid_step(self, steps_dir):
        tracker = steps_dir / "-step.txt"
        content = tracker.read_text().strip()
        valid_values = {"0", "1", "2", "3", "4", "X"}
        assert content in valid_values, (
            f"Step tracker contains '{content}', expected one of {valid_values}"
        )

    def test_step_tracker_is_single_line(self, steps_dir):
        tracker = steps_dir / "-step.txt"
        content = tracker.read_text()
        lines = [line for line in content.split("\n") if line.strip()]
        assert len(lines) == 1, "Step tracker should contain exactly one line"


class TestStepContent:
    """Validate step file content structure."""

    STEP_MD_FILES = [f for f in EXPECTED_STEP_FILES if f.endswith(".md") and f != "0-welcome.md"]

    @pytest.mark.parametrize("step_file", STEP_MD_FILES)
    def test_step_file_not_empty(self, steps_dir, step_file):
        path = steps_dir / step_file
        content = path.read_text()
        assert len(content.strip()) > 0, f"{step_file} is empty"

    @pytest.mark.parametrize("step_file", STEP_MD_FILES)
    def test_step_file_has_header(self, steps_dir, step_file):
        path = steps_dir / step_file
        content = path.read_text()
        assert "#" in content, f"{step_file} is missing a markdown header"

    def test_welcome_step_is_placeholder(self, steps_dir):
        """The 0-welcome.md is a placeholder that gets replaced by the workflow."""
        content = (steps_dir / "0-welcome.md").read_text()
        # This file is intentionally minimal - it's a placeholder
        assert len(content.strip()) > 0

    def test_create_branch_step_mentions_branch(self, steps_dir):
        content = (steps_dir / "1-create-a-branch.md").read_text()
        assert "branch" in content.lower()

    def test_commit_step_mentions_commit(self, steps_dir):
        content = (steps_dir / "2-commit-a-file.md").read_text()
        assert "commit" in content.lower()

    def test_pull_request_step_mentions_pr(self, steps_dir):
        content = (steps_dir / "3-open-a-pull-request.md").read_text()
        assert "pull request" in content.lower()

    def test_merge_step_mentions_merge(self, steps_dir):
        content = (steps_dir / "4-merge-your-pull-request.md").read_text()
        assert "merge" in content.lower()

    def test_finish_step_indicates_completion(self, steps_dir):
        content = (steps_dir / "X-finish.md").read_text()
        # The finish step should indicate the course is done
        lower = content.lower()
        assert any(
            word in lower for word in ["finish", "complete", "done", "congratulations"]
        ), "Finish step should indicate course completion"


class TestStepFileConsistency:
    """Validate that step files are consistent with workflows."""

    def test_each_workflow_has_matching_step_file(self, workflows_dir, steps_dir):
        """Every numbered workflow should have a corresponding step .md file."""
        for wf_file in workflows_dir.glob("*.yml"):
            # Extract step number from workflow filename (e.g., "1" from "1-create-a-branch.yml")
            prefix = wf_file.stem.split("-")[0]
            if prefix.isdigit():
                step_num = int(prefix)
                # Find matching step file
                matching_steps = [
                    f
                    for f in steps_dir.iterdir()
                    if f.name.startswith(f"{step_num}-") and f.suffix == ".md"
                ]
                assert len(matching_steps) >= 1, (
                    f"Workflow {wf_file.name} has no matching step file"
                )

    def test_step_numbers_are_sequential(self, steps_dir):
        """Step files should have sequential numbering."""
        numbered_steps = []
        for f in steps_dir.iterdir():
            if f.suffix == ".md":
                prefix = f.stem.split("-")[0]
                if prefix.isdigit():
                    numbered_steps.append(int(prefix))

        numbered_steps.sort()
        expected = list(range(numbered_steps[0], numbered_steps[-1] + 1))
        assert numbered_steps == expected, (
            f"Step numbering is not sequential: {numbered_steps}"
        )

    def test_my_first_branch_referenced_in_relevant_steps(self, steps_dir):
        """Steps that involve the branch should reference 'my-first-branch'."""
        branch_relevant_steps = [
            "1-create-a-branch.md",
            "2-commit-a-file.md",
            "3-open-a-pull-request.md",
        ]
        for step_file in branch_relevant_steps:
            content = (steps_dir / step_file).read_text()
            assert "my-first-branch" in content, (
                f"{step_file} should reference 'my-first-branch'"
            )

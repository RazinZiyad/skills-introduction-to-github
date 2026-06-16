"""Unit tests for repository configuration files.

Validates dependabot configuration, .gitignore patterns,
and overall repository structure.
"""

import yaml
import pytest
from pathlib import Path

from tests.helpers import REPO_ROOT


class TestDependabotConfig:
    """Validate the Dependabot configuration."""

    @pytest.fixture
    def dependabot_config(self):
        path = REPO_ROOT / ".github" / "dependabot.yml"
        with open(path) as f:
            return yaml.safe_load(f)

    def test_dependabot_file_exists(self):
        path = REPO_ROOT / ".github" / "dependabot.yml"
        assert path.exists(), "dependabot.yml is missing"

    def test_dependabot_has_version(self, dependabot_config):
        assert "version" in dependabot_config
        assert dependabot_config["version"] == 2

    def test_dependabot_has_updates(self, dependabot_config):
        assert "updates" in dependabot_config
        assert len(dependabot_config["updates"]) > 0

    def test_dependabot_monitors_github_actions(self, dependabot_config):
        ecosystems = [u["package-ecosystem"] for u in dependabot_config["updates"]]
        assert "github-actions" in ecosystems, (
            "Dependabot should monitor github-actions ecosystem"
        )

    def test_dependabot_update_has_directory(self, dependabot_config):
        for update in dependabot_config["updates"]:
            assert "directory" in update, "Each update entry needs a directory"

    def test_dependabot_update_has_schedule(self, dependabot_config):
        for update in dependabot_config["updates"]:
            assert "schedule" in update, "Each update entry needs a schedule"
            assert "interval" in update["schedule"], "Schedule needs an interval"

    def test_dependabot_schedule_is_valid(self, dependabot_config):
        valid_intervals = {"daily", "weekly", "monthly"}
        for update in dependabot_config["updates"]:
            interval = update["schedule"]["interval"]
            assert interval in valid_intervals, (
                f"Invalid schedule interval: {interval}"
            )


class TestGitignore:
    """Validate the .gitignore file."""

    @pytest.fixture
    def gitignore_content(self):
        path = REPO_ROOT / ".gitignore"
        return path.read_text()

    @pytest.fixture
    def gitignore_patterns(self, gitignore_content):
        """Parse .gitignore into active patterns (ignoring comments/blanks)."""
        patterns = []
        for line in gitignore_content.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                patterns.append(stripped)
        return patterns

    def test_gitignore_exists(self):
        assert (REPO_ROOT / ".gitignore").exists()

    def test_gitignore_not_empty(self, gitignore_content):
        assert len(gitignore_content.strip()) > 0

    def test_ignores_os_files(self, gitignore_patterns):
        """Should ignore common OS-generated files."""
        os_patterns = {".DS_Store", "Thumbs.db"}
        for pattern in os_patterns:
            assert pattern in gitignore_patterns, (
                f".gitignore should ignore {pattern}"
            )

    def test_ignores_compiled_files(self, gitignore_patterns):
        """Should ignore compiled source files."""
        compiled_patterns = {"*.exe", "*.dll", "*.so", "*.class"}
        for pattern in compiled_patterns:
            assert pattern in gitignore_patterns, (
                f".gitignore should ignore {pattern}"
            )

    def test_ignores_archive_files(self, gitignore_patterns):
        """Should ignore common archive formats."""
        archive_patterns = {"*.zip", "*.tar", "*.gz"}
        for pattern in archive_patterns:
            assert pattern in gitignore_patterns, (
                f".gitignore should ignore {pattern}"
            )

    def test_ignores_log_files(self, gitignore_patterns):
        """Should ignore log files."""
        assert "*.log" in gitignore_patterns


class TestRepoStructure:
    """Validate overall repository structure."""

    def test_readme_exists(self):
        assert (REPO_ROOT / "README.md").exists()

    def test_license_exists(self):
        assert (REPO_ROOT / "LICENSE").exists()

    def test_github_directory_exists(self):
        assert (REPO_ROOT / ".github").is_dir()

    def test_workflows_directory_exists(self):
        assert (REPO_ROOT / ".github" / "workflows").is_dir()

    def test_steps_directory_exists(self):
        assert (REPO_ROOT / ".github" / "steps").is_dir()

    def test_images_directory_exists(self):
        assert (REPO_ROOT / "images").is_dir()

    def test_images_are_png(self):
        images_dir = REPO_ROOT / "images"
        for img in images_dir.iterdir():
            assert img.suffix == ".png", (
                f"Image {img.name} should be PNG format"
            )

    def test_readme_references_images(self):
        readme = (REPO_ROOT / "README.md").read_text()
        images_dir = REPO_ROOT / "images"
        # At least some images should be referenced in the README
        referenced_count = 0
        for img in images_dir.iterdir():
            if img.name in readme:
                referenced_count += 1
        assert referenced_count > 0, "README should reference at least one image"

    def test_license_is_mit(self):
        license_text = (REPO_ROOT / "LICENSE").read_text()
        assert "MIT" in license_text or "mit" in license_text.lower(), (
            "License should be MIT"
        )

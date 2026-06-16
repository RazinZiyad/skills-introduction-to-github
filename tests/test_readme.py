"""Unit tests for README.md content.

Validates that the README contains proper course structure,
instructions, and references.
"""

import re
import pytest
from pathlib import Path

from tests.helpers import REPO_ROOT


@pytest.fixture
def readme_content():
    return (REPO_ROOT / "README.md").read_text()


class TestReadmeStructure:
    """Validate README markdown structure."""

    def test_has_title(self, readme_content):
        assert "# " in readme_content, "README should have a title"

    def test_title_is_introduction_to_github(self, readme_content):
        assert "Introduction to GitHub" in readme_content

    def test_has_step_headers(self, readme_content):
        assert "## Step" in readme_content or "## step" in readme_content

    def test_has_activity_section(self, readme_content):
        assert "Activity" in readme_content, (
            "README should have an activity section"
        )

    def test_has_footer(self, readme_content):
        assert "<footer>" in readme_content and "</footer>" in readme_content

    def test_has_header(self, readme_content):
        assert "<header>" in readme_content and "</header>" in readme_content


class TestReadmeContent:
    """Validate README content quality."""

    def test_mentions_git(self, readme_content):
        assert "Git" in readme_content or "git" in readme_content

    def test_mentions_repository(self, readme_content):
        assert "repository" in readme_content.lower()

    def test_mentions_branch(self, readme_content):
        assert "branch" in readme_content.lower()

    def test_mentions_my_first_branch(self, readme_content):
        assert "my-first-branch" in readme_content

    def test_has_github_docs_links(self, readme_content):
        assert "docs.github.com" in readme_content, (
            "README should link to GitHub docs"
        )

    def test_has_numbered_instructions(self, readme_content):
        """README should have numbered instruction steps."""
        # Match patterns like "1.", "2.", "3." etc
        numbered = re.findall(r"^\d+\.", readme_content, re.MULTILINE)
        assert len(numbered) >= 3, "README should have numbered instructions"

    def test_includes_help_resources(self, readme_content):
        """README should include help/support links."""
        lower = readme_content.lower()
        assert "help" in lower or "support" in lower or "discussion" in lower


class TestReadmeImages:
    """Validate image references in README."""

    def test_image_references_are_valid(self, readme_content):
        """All image references should point to existing files."""
        # Find markdown image references like ![alt](/images/foo.png)
        image_refs = re.findall(r"!\[.*?\]\((/images/[^)]+)\)", readme_content)
        for ref in image_refs:
            # Remove leading slash for path resolution
            img_path = REPO_ROOT / ref.lstrip("/")
            assert img_path.exists(), f"Referenced image not found: {ref}"

    def test_no_broken_relative_image_links(self, readme_content):
        """Images referenced with relative paths should exist."""
        image_refs = re.findall(r"!\[.*?\]\((images/[^)]+)\)", readme_content)
        for ref in image_refs:
            img_path = REPO_ROOT / ref
            assert img_path.exists(), f"Referenced image not found: {ref}"

    def test_has_image_alt_text(self, readme_content):
        """Image references should have alt text."""
        # Find images with empty alt text
        empty_alt = re.findall(r"!\[\]\(", readme_content)
        assert len(empty_alt) == 0, "All images should have alt text"

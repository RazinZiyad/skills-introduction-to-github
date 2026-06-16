"""Unit tests for GitHub Actions workflow files.

Validates structure, required fields, trigger configurations,
step transitions, and permissions for all course workflows.
"""

import yaml
import pytest
from pathlib import Path

from conftest import WORKFLOWS_DIR, REPO_ROOT


COURSE_WORKFLOWS = [
    "0-welcome.yml",
    "1-create-a-branch.yml",
    "2-commit-a-file.yml",
    "3-open-a-pull-request.yml",
    "4-merge-your-pull-request.yml",
]

INFRA_WORKFLOWS = [
    "test.yml",
]

EXPECTED_WORKFLOWS = COURSE_WORKFLOWS + INFRA_WORKFLOWS


class TestWorkflowPresence:
    """Ensure all expected workflow files exist."""

    def test_all_expected_workflows_exist(self, workflows_dir):
        existing = [f.name for f in workflows_dir.glob("*.yml")]
        for wf in EXPECTED_WORKFLOWS:
            assert wf in existing, f"Missing workflow file: {wf}"

    def test_no_unexpected_workflows(self, workflows_dir):
        existing = {f.name for f in workflows_dir.glob("*.yml")}
        expected = set(EXPECTED_WORKFLOWS)
        unexpected = existing - expected
        assert not unexpected, f"Unexpected workflow files: {unexpected}"


class TestWorkflowStructure:
    """Validate the YAML structure of each workflow."""

    @pytest.mark.parametrize("workflow_name", EXPECTED_WORKFLOWS)
    def test_workflow_is_valid_yaml(self, workflows_dir, workflow_name):
        path = workflows_dir / workflow_name
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data is not None, f"{workflow_name} is empty or invalid YAML"

    @pytest.mark.parametrize("workflow_name", EXPECTED_WORKFLOWS)
    def test_workflow_has_name(self, workflow_files, workflow_name):
        wf = workflow_files[workflow_name]
        assert "name" in wf, f"{workflow_name} missing 'name' field"
        assert isinstance(wf["name"], str) and len(wf["name"]) > 0

    @pytest.mark.parametrize("workflow_name", EXPECTED_WORKFLOWS)
    def test_workflow_has_trigger(self, workflow_files, workflow_name):
        wf = workflow_files[workflow_name]
        assert True in wf or "on" in wf, f"{workflow_name} missing trigger ('on')"

    @pytest.mark.parametrize("workflow_name", EXPECTED_WORKFLOWS)
    def test_workflow_has_permissions(self, workflow_files, workflow_name):
        wf = workflow_files[workflow_name]
        assert "permissions" in wf, f"{workflow_name} missing 'permissions'"

    @pytest.mark.parametrize("workflow_name", EXPECTED_WORKFLOWS)
    def test_workflow_has_jobs(self, workflow_files, workflow_name):
        wf = workflow_files[workflow_name]
        assert "jobs" in wf, f"{workflow_name} missing 'jobs'"
        assert len(wf["jobs"]) > 0

    @pytest.mark.parametrize("workflow_name", COURSE_WORKFLOWS)
    def test_course_workflow_requires_contents_write(self, workflow_files, workflow_name):
        wf = workflow_files[workflow_name]
        permissions = wf.get("permissions", {})
        assert permissions.get("contents") == "write", (
            f"{workflow_name} should have contents: write permission"
        )


class TestWorkflowTriggers:
    """Validate trigger configurations are appropriate for each step."""

    def test_welcome_triggers_on_push_to_main(self, workflow_files):
        wf = workflow_files["0-welcome.yml"]
        triggers = wf.get(True) or wf.get("on", {})
        assert "push" in triggers
        assert "main" in triggers["push"]["branches"]

    def test_create_branch_triggers_on_create(self, workflow_files):
        wf = workflow_files["1-create-a-branch.yml"]
        triggers = wf.get(True) or wf.get("on", {})
        assert "create" in triggers

    def test_commit_file_triggers_on_push_to_branch(self, workflow_files):
        wf = workflow_files["2-commit-a-file.yml"]
        triggers = wf.get(True) or wf.get("on", {})
        assert "push" in triggers
        assert "my-first-branch" in triggers["push"]["branches"]

    def test_open_pr_triggers_on_pull_request(self, workflow_files):
        wf = workflow_files["3-open-a-pull-request.yml"]
        triggers = wf.get(True) or wf.get("on", {})
        assert "pull_request" in triggers
        pr_config = triggers["pull_request"]
        assert "opened" in pr_config["types"]
        assert "reopened" in pr_config["types"]

    def test_merge_pr_triggers_on_push_to_main(self, workflow_files):
        wf = workflow_files["4-merge-your-pull-request.yml"]
        triggers = wf.get(True) or wf.get("on", {})
        assert "push" in triggers
        assert "main" in triggers["push"]["branches"]

    @pytest.mark.parametrize("workflow_name", COURSE_WORKFLOWS)
    def test_course_workflows_support_workflow_dispatch(self, workflow_files, workflow_name):
        wf = workflow_files[workflow_name]
        triggers = wf.get(True) or wf.get("on", {})
        assert "workflow_dispatch" in triggers, (
            f"{workflow_name} should support manual workflow_dispatch"
        )


class TestWorkflowJobs:
    """Validate job structure and dependencies for course workflows."""

    @pytest.mark.parametrize("workflow_name", COURSE_WORKFLOWS)
    def test_has_get_current_step_job(self, workflow_files, workflow_name):
        wf = workflow_files[workflow_name]
        assert "get_current_step" in wf["jobs"], (
            f"{workflow_name} missing get_current_step job"
        )

    @pytest.mark.parametrize("workflow_name", COURSE_WORKFLOWS)
    def test_get_current_step_outputs_step_number(self, workflow_files, workflow_name):
        wf = workflow_files[workflow_name]
        job = wf["jobs"]["get_current_step"]
        assert "outputs" in job
        assert "current_step" in job["outputs"]

    @pytest.mark.parametrize("workflow_name", COURSE_WORKFLOWS)
    def test_main_job_depends_on_get_current_step(self, workflow_files, workflow_name):
        wf = workflow_files[workflow_name]
        jobs = wf["jobs"]
        main_jobs = [k for k in jobs if k != "get_current_step"]
        for job_name in main_jobs:
            job = jobs[job_name]
            assert "needs" in job, f"{workflow_name}/{job_name} missing 'needs'"
            needs = job["needs"]
            if isinstance(needs, str):
                assert needs == "get_current_step"
            else:
                assert "get_current_step" in needs

    @pytest.mark.parametrize("workflow_name", COURSE_WORKFLOWS)
    def test_main_job_uses_checkout(self, workflow_files, workflow_name):
        wf = workflow_files[workflow_name]
        jobs = wf["jobs"]
        main_jobs = [k for k in jobs if k != "get_current_step"]
        for job_name in main_jobs:
            job = jobs[job_name]
            step_uses = [s.get("uses", "") for s in job.get("steps", [])]
            checkout_found = any("actions/checkout" in u for u in step_uses)
            assert checkout_found, (
                f"{workflow_name}/{job_name} missing actions/checkout step"
            )

    @pytest.mark.parametrize("workflow_name", COURSE_WORKFLOWS)
    def test_main_job_runs_on_ubuntu(self, workflow_files, workflow_name):
        wf = workflow_files[workflow_name]
        jobs = wf["jobs"]
        for job_name, job in jobs.items():
            assert "runs-on" in job, f"{workflow_name}/{job_name} missing runs-on"
            assert "ubuntu" in job["runs-on"]


class TestStepTransitions:
    """Validate that workflows correctly transition between steps."""

    EXPECTED_TRANSITIONS = [
        ("0-welcome.yml", 0, 1),
        ("1-create-a-branch.yml", 1, 2),
        ("2-commit-a-file.yml", 2, 3),
        ("3-open-a-pull-request.yml", 3, 4),
        ("4-merge-your-pull-request.yml", 4, "X"),
    ]

    @pytest.mark.parametrize("workflow_name,from_step,to_step", EXPECTED_TRANSITIONS)
    def test_workflow_transitions_correctly(
        self, workflow_files, workflow_name, from_step, to_step
    ):
        wf = workflow_files[workflow_name]
        jobs = wf["jobs"]
        main_jobs = [k for k in jobs if k != "get_current_step"]

        for job_name in main_jobs:
            job = jobs[job_name]
            steps = job.get("steps", [])
            update_steps = [
                s for s in steps if "skills/action-update-step" in s.get("uses", "")
            ]
            assert len(update_steps) == 1, (
                f"{workflow_name} should have exactly one update-step action"
            )
            with_block = update_steps[0].get("with", {})
            assert with_block.get("from_step") == from_step, (
                f"{workflow_name} from_step should be {from_step}"
            )
            assert with_block.get("to_step") == to_step, (
                f"{workflow_name} to_step should be {to_step}"
            )

    @pytest.mark.parametrize("workflow_name,from_step,to_step", EXPECTED_TRANSITIONS)
    def test_workflow_condition_checks_correct_step(
        self, workflow_files, workflow_name, from_step, to_step
    ):
        wf = workflow_files[workflow_name]
        jobs = wf["jobs"]
        main_jobs = [k for k in jobs if k != "get_current_step"]

        for job_name in main_jobs:
            job = jobs[job_name]
            condition = job.get("if", "")
            assert f"current_step == {from_step}" in condition, (
                f"{workflow_name}/{job_name} should check current_step == {from_step}"
            )

    @pytest.mark.parametrize("workflow_name", COURSE_WORKFLOWS)
    def test_workflow_checks_not_template(self, workflow_files, workflow_name):
        wf = workflow_files[workflow_name]
        jobs = wf["jobs"]
        main_jobs = [k for k in jobs if k != "get_current_step"]

        for job_name in main_jobs:
            job = jobs[job_name]
            condition = job.get("if", "")
            assert "is_template" in condition, (
                f"{workflow_name}/{job_name} should check is_template"
            )

    def test_transitions_form_complete_chain(self, workflow_files):
        """Verify that step transitions form a complete chain from 0 to X."""
        transitions = {}
        for wf_name, wf in workflow_files.items():
            jobs = wf["jobs"]
            main_jobs = [k for k in jobs if k != "get_current_step"]
            for job_name in main_jobs:
                steps = jobs[job_name].get("steps", [])
                for step in steps:
                    if "skills/action-update-step" in step.get("uses", ""):
                        with_block = step.get("with", {})
                        transitions[with_block["from_step"]] = with_block["to_step"]

        # Verify chain: 0 -> 1 -> 2 -> 3 -> 4 -> X
        current = 0
        expected_chain = [0, 1, 2, 3, 4, "X"]
        actual_chain = [0]
        while current in transitions:
            current = transitions[current]
            actual_chain.append(current)

        assert actual_chain == expected_chain, (
            f"Expected chain {expected_chain}, got {actual_chain}"
        )

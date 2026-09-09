"""
Tests for scripts/review-cv.
Verifies command line interface, help output, argument validation,
and run directory / scaffolding creation.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REVIEW_CV_SCRIPT = REPO_ROOT / "scripts" / "review-cv"


def test_review_cv_help_flag():
    """Verify scripts/review-cv --help and -h produce usage text and exit 0."""
    res_long = subprocess.run(
        [str(REVIEW_CV_SCRIPT), "--help"],
        capture_output=True,
        text=True,
    )
    assert res_long.returncode == 0
    assert "Usage:" in res_long.stdout
    assert "scripts/review-cv" in res_long.stdout

    res_short = subprocess.run(
        [str(REVIEW_CV_SCRIPT), "-h"],
        capture_output=True,
        text=True,
    )
    assert res_short.returncode == 0
    assert "Usage:" in res_short.stdout


def test_review_cv_missing_arguments():
    """Verify exit codes and error output when required arguments are missing."""
    # No arguments
    res_none = subprocess.run(
        [str(REVIEW_CV_SCRIPT)],
        capture_output=True,
        text=True,
    )
    assert res_none.returncode == 2

    # Missing --roles
    dummy_file = REPO_ROOT / "tests" / "__dummy.pdf"
    dummy_file.write_text("dummy", encoding="utf-8")
    try:
        res_no_roles = subprocess.run(
            [str(REVIEW_CV_SCRIPT), "Candidate Name", str(dummy_file)],
            capture_output=True,
            text=True,
        )
        assert res_no_roles.returncode == 2
        assert "--roles is required" in res_no_roles.stderr
    finally:
        if dummy_file.exists():
            dummy_file.unlink()

    # Nonexistent CV file
    res_missing_file = subprocess.run(
        [
            str(REVIEW_CV_SCRIPT),
            "Candidate Name",
            "/path/to/nonexistent/cv_file.pdf",
            "--roles",
            "Data Analyst",
        ],
        capture_output=True,
        text=True,
    )
    assert res_missing_file.returncode == 1
    assert "CV file not found" in res_missing_file.stderr


def test_review_cv_run_initialization(tmp_path: Path):
    """Verify directory scaffolding and files created by scripts/review-cv."""
    dummy_cv = tmp_path / "jane_doe_cv.pdf"
    dummy_cv.write_text("Dummy CV content", encoding="utf-8")

    dummy_projects = tmp_path / "projects.md"
    dummy_projects.write_text("# Projects\n- Project A", encoding="utf-8")

    candidate_name = "Jane Test Candidate"
    candidate_slug = "jane-test-candidate"
    run_date = "2026-09-09"
    roles = "Data Analyst, Application Support"
    candidate_dir = REPO_ROOT / "output" / "candidates" / candidate_slug

    try:
        cmd = [
            str(REVIEW_CV_SCRIPT),
            candidate_name,
            str(dummy_cv),
            "--roles",
            roles,
            "--projects",
            str(dummy_projects),
            "--date",
            run_date,
        ]
        res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert res.returncode == 0, f"Script failed with stderr: {res.stderr}"

        # Check run directory
        run_dir = candidate_dir / run_date
        assert run_dir.exists()
        assert run_dir.is_dir()

        # Check required shared subdirectories at date level
        for subdir in ["input", "scratch", "reports", "portfolio"]:
            sub_path = run_dir / subdir
            assert sub_path.exists(), f"Subdirectory missing: {subdir}"
            assert sub_path.is_dir()

        # Check required per-position subdirectories: [Date]/[Position]/{cv,salary,interview,application,platform}
        for role_slug in ["data-analyst", "application-support"]:
            role_path = run_dir / role_slug
            assert role_path.exists(), f"Role directory missing: {role_slug}"
            for cat in ["cv", "salary", "interview", "application", "platform"]:
                cat_path = role_path / cat
                assert cat_path.exists(), f"Category {cat} missing in {role_slug}"

        # Check input files copied / created
        assert (run_dir / "input" / "original-cv.pdf").exists()
        assert (run_dir / "input" / "projects-list.md").exists()
        assert (run_dir / "input" / "target-brief.md").exists()
        assert (run_dir / "input" / "harvard-resume-checklist.md").exists()

        # Check target-brief content
        brief_content = (run_dir / "input" / "target-brief.md").read_text(encoding="utf-8")
        assert candidate_name in brief_content
        assert "Data Analyst" in brief_content
        assert "Application Support" in brief_content

        # Check LATEST.md
        latest_file = candidate_dir / "LATEST.md"
        assert latest_file.exists()
        assert run_date in latest_file.read_text(encoding="utf-8")

    finally:
        # Clean up test output directory
        if candidate_dir.exists():
            shutil.rmtree(candidate_dir, ignore_errors=True)

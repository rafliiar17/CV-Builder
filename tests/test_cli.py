"""
Tests for scripts/cli.py.
Verifies the unified CLI subcommands: init, extract, render, audit.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLI_SCRIPT = REPO_ROOT / "scripts" / "cli.py"


def test_cli_help():
    res = subprocess.run([sys.executable, str(CLI_SCRIPT), "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "cvb [-h] {init,extract,render,audit}" in res.stdout


def test_cli_extract_text(tmp_path: Path):
    sample = tmp_path / "sample.txt"
    sample.write_text("Hello World from CLI test", encoding="utf-8")

    res = subprocess.run(
        [sys.executable, str(CLI_SCRIPT), "extract", str(sample)],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "Hello World from CLI test" in res.stdout


def test_cli_init_run(tmp_path: Path):
    dummy_cv = tmp_path / "candidate_cv.pdf"
    dummy_cv.write_text("Dummy CV content for CLI test", encoding="utf-8")

    candidate_name = "Alex Test"
    candidate_slug = "alex-test"
    run_date = "2026-09-09"
    roles = "DevOps Engineer"
    expected_run_id = f"{run_date}-devops-engineer"
    candidate_dir = REPO_ROOT / "output" / "candidates" / candidate_slug

    try:
        cmd = [
            sys.executable,
            str(CLI_SCRIPT),
            "init",
            candidate_name,
            str(dummy_cv),
            "--roles",
            roles,
            "--date",
            run_date,
        ]
        res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert res.returncode == 0
        assert "Successfully initialized run directory" in res.stdout

        run_dir = candidate_dir / expected_run_id
        assert run_dir.exists()
        assert (run_dir / "input" / "extracted.txt").exists()
        assert (run_dir / "input" / "target-brief.md").exists()
        assert (run_dir / "input" / "harvard-resume-checklist.md").exists()
        assert (candidate_dir / "LATEST.md").exists()
    finally:
        if candidate_dir.exists():
            shutil.rmtree(candidate_dir, ignore_errors=True)

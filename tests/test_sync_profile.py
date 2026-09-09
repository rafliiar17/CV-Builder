"""
Tests for scripts/sync_to_profile.py.
Verifies discovery, destination mapping, file synchronization, and metadata updates.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync_to_profile.py"

from scripts.sync_to_profile import resolve_run_dir, sync_files, update_profile_metadata


def test_sync_script_help():
    res = subprocess.run([sys.executable, str(SYNC_SCRIPT), "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "Sync CV-Brainstormer deliverables into profile-new" in res.stdout


def test_resolve_run_dir(tmp_path: Path):
    candidate_slug = "test-candidate"
    fake_candidate_dir = tmp_path / "output" / "candidates" / candidate_slug
    run_dir = fake_candidate_dir / "2026-09-09"
    run_dir.mkdir(parents=True)
    latest_file = fake_candidate_dir / "LATEST.md"
    latest_file.write_text(f"output/candidates/{candidate_slug}/2026-09-09\n", encoding="utf-8")

    res = resolve_run_dir(candidate_slug, base_dir=tmp_path)
    assert res == run_dir


def test_sync_files_and_metadata(tmp_path: Path):
    # Setup dummy run_dir
    run_dir = tmp_path / "run_2026_09_09"
    run_dir.mkdir()

    app_cv = run_dir / "application-support-l2" / "cv"
    app_cv.mkdir(parents=True)
    (app_cv / "cv-rafli_arraafi-application-support-en.pdf").write_bytes(b"%PDF-dummy-en")
    (app_cv / "cv-rafli_arraafi-application-support-id.pdf").write_bytes(b"%PDF-dummy-id")
    (app_cv / "cv-rafli_arraafi-application-support-en.docx").write_bytes(b"DOCX-dummy-en")
    (app_cv / "cv-rafli_arraafi-application-support-id.docx").write_bytes(b"DOCX-dummy-id")

    # Setup dummy profile_dir
    profile_dir = tmp_path / "profile_repo"
    (profile_dir / "CV" / "pdf").mkdir(parents=True)
    (profile_dir / "CV" / "docx").mkdir(parents=True)
    (profile_dir / "scripts").mkdir(parents=True)
    (profile_dir / "data").mkdir(parents=True)

    (profile_dir / "scripts" / "upload-cvs-r2.mjs").write_text(
        "const CV_MAPPING = [\n];\n",
        encoding="utf-8",
    )
    (profile_dir / "data" / "en.json").write_text(
        json.dumps({"settings": {"cvRepository": []}, "hero": {"cvRepository": []}}),
        encoding="utf-8",
    )
    (profile_dir / "data" / "id.json").write_text(
        json.dumps({"settings": {"cvRepository": []}}),
        encoding="utf-8",
    )

    # 1. Test Dry Run
    copied, synced = sync_files(run_dir, profile_dir, dry_run=True)
    assert copied == 4
    assert len(synced) == 1
    assert not (profile_dir / "CV" / "pdf" / "CV-Rafli-Arraafi-Albaasith-EN.pdf").exists()

    # 2. Test Real Sync
    copied, synced = sync_files(run_dir, profile_dir, dry_run=False)
    assert copied == 4
    assert len(synced) == 1
    assert (profile_dir / "CV" / "pdf" / "CV-Rafli-Arraafi-Albaasith-EN.pdf").read_bytes() == b"%PDF-dummy-en"
    assert (profile_dir / "CV" / "pdf" / "CV-Rafli-Arraafi-Albaasith-ID.pdf").read_bytes() == b"%PDF-dummy-id"
    assert (profile_dir / "CV" / "docx" / "CV-Rafli-Arraafi-Albaasith-EN.docx").read_bytes() == b"DOCX-dummy-en"
    assert (profile_dir / "CV" / "docx" / "CV-Rafli-Arraafi-Albaasith-ID.docx").read_bytes() == b"DOCX-dummy-id"

    # 3. Test Metadata Update
    update_profile_metadata(profile_dir, synced, dry_run=False)

    r2_script = (profile_dir / "scripts" / "upload-cvs-r2.mjs").read_text(encoding="utf-8")
    assert "CV-Rafli-Arraafi-Albaasith-EN.pdf" in r2_script

    en_json = json.loads((profile_dir / "data" / "en.json").read_text(encoding="utf-8"))
    assert len(en_json["settings"]["cvRepository"]) == 1
    assert en_json["settings"]["cvRepository"][0]["category"] == "Application Support"
    assert "hero" not in en_json or "cvRepository" not in en_json.get("hero", {})

#!/usr/bin/env python3
"""
Sync CV-Brainstormer generated deliverables to profile-new portfolio repository.

Copies verified PDF & DOCX outputs into profile-new/CV/pdf/ and profile-new/CV/docx/
and optionally updates profile-new metadata (upload-cvs-r2.mjs, data/en.json, data/id.json).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROFILE_DIR = Path("/home/archy/Projects/profile-new")


class RoleMapping(NamedTuple):
    role_slug: str
    r2_folder: str
    en_label: str
    id_label: str
    file_prefix_en: str
    file_prefix_id: str


ROLE_MAPPINGS: list[RoleMapping] = [
    RoleMapping(
        role_slug="application-support-l2",
        r2_folder="application-support",
        en_label="Application Support",
        id_label="Application Support",
        file_prefix_en="CV-Rafli-Arraafi-Albaasith-EN",
        file_prefix_id="CV-Rafli-Arraafi-Albaasith-ID",
    ),
    RoleMapping(
        role_slug="business-analyst",
        r2_folder="business-analyst",
        en_label="Business & System Analyst",
        id_label="Business & System Analyst",
        file_prefix_en="CV-Rafli-Arraafi-Albaasith-BA-EN",
        file_prefix_id="CV-Rafli-Arraafi-Albaasith-BA",
    ),
    RoleMapping(
        role_slug="database-administrator",
        r2_folder="database-administrator",
        en_label="Database Administrator",
        id_label="Database Administrator",
        file_prefix_en="CV-Rafli-Arraafi-Albaasith-DBA-EN",
        file_prefix_id="CV-Rafli-Arraafi-Albaasith-DBA",
    ),
    RoleMapping(
        role_slug="qa-engineer",
        r2_folder="qa-tester",
        en_label="Quality Assurance",
        id_label="Quality Assurance",
        file_prefix_en="CV-Rafli-Arraafi-Albaasith-QA-EN",
        file_prefix_id="CV-Rafli-Arraafi-Albaasith-QA",
    ),
    RoleMapping(
        role_slug="data-analyst",
        r2_folder="data-analyst",
        en_label="Data Analyst",
        id_label="Data Analyst",
        file_prefix_en="CV-Rafli-Arraafi-Albaasith-DA-EN",
        file_prefix_id="CV-Rafli-Arraafi-Albaasith-DA",
    ),
    RoleMapping(
        role_slug="it-operations",
        r2_folder="it-operations",
        en_label="IT Operations & Systems",
        id_label="Operasional TI & Sistem",
        file_prefix_en="CV-Rafli-Arraafi-Albaasith-IT-Ops-EN",
        file_prefix_id="CV-Rafli-Arraafi-Albaasith-IT-Ops",
    ),
    RoleMapping(
        role_slug="data-entry",
        r2_folder="data-entry",
        en_label="Data Entry & Operations",
        id_label="Data Entry & Operasional",
        file_prefix_en="CV-Rafli-Arraafi-Albaasith-Data-Entry-EN",
        file_prefix_id="CV-Rafli-Arraafi-Albaasith-Data-Entry",
    ),
]


def resolve_run_dir(candidate_slug: str, date_str: str | None = None) -> Path:
    """Find the target run directory for a candidate."""
    candidate_dir = REPO_ROOT / "output" / "candidates" / candidate_slug
    if not candidate_dir.exists():
        raise FileNotFoundError(f"Candidate directory not found: {candidate_dir}")

    if date_str:
        target = candidate_dir / date_str
        if not target.exists():
            raise FileNotFoundError(f"Run date directory not found: {target}")
        return target

    latest_file = candidate_dir / "LATEST.md"
    if latest_file.exists():
        text = latest_file.read_text(encoding="utf-8")
        match = re.search(r"output/candidates/[^/]+/([0-9]{4}-[0-9]{2}-[0-9]{2}[^\s`]*)", text)
        if match:
            target = candidate_dir / match.group(1)
            if target.exists():
                return target

    subdirs = sorted([d for d in candidate_dir.iterdir() if d.is_dir() and d.name != "scratch"], reverse=True)
    if not subdirs:
        raise FileNotFoundError(f"No run folders found in {candidate_dir}")
    return subdirs[0]


def sync_files(
    run_dir: Path,
    profile_dir: Path,
    dry_run: bool = False,
) -> tuple[int, list[RoleMapping]]:
    """Copy matching PDF and DOCX files into profile-new/CV/."""
    pdf_dest_dir = profile_dir / "CV" / "pdf"
    docx_dest_dir = profile_dir / "CV" / "docx"

    if not dry_run:
        pdf_dest_dir.mkdir(parents=True, exist_ok=True)
        docx_dest_dir.mkdir(parents=True, exist_ok=True)

    copied_count = 0
    synced_roles: list[RoleMapping] = []

    for mapping in ROLE_MAPPINGS:
        role_cv_dir = run_dir / mapping.role_slug / "cv"
        if not role_cv_dir.exists():
            continue

        role_synced = False
        files_in_cv = list(role_cv_dir.iterdir())

        # Match EN & ID files for PDF and DOCX
        targets = [
            ("en", ".pdf", mapping.file_prefix_en + ".pdf", pdf_dest_dir),
            ("id", ".pdf", mapping.file_prefix_id + ".pdf", pdf_dest_dir),
            ("en", ".docx", mapping.file_prefix_en + ".docx", docx_dest_dir),
            ("id", ".docx", mapping.file_prefix_id + ".docx", docx_dest_dir),
        ]

        for lang, ext, dest_name, dest_dir in targets:
            # Find source file matching lang & ext
            match = None
            for f in files_in_cv:
                if f.suffix.lower() == ext and f"-{lang}{ext}" in f.name.lower():
                    match = f
                    break

            if match:
                dest_file = dest_dir / dest_name
                try:
                    rel_src = match.relative_to(REPO_ROOT)
                except ValueError:
                    rel_src = match
                try:
                    rel_dst = dest_file.relative_to(profile_dir)
                except ValueError:
                    rel_dst = dest_file

                if dry_run:
                    print(f"  [DRY-RUN] {rel_src} -> {dest_file}")
                else:
                    shutil.copy2(match, dest_file)
                    print(f"  [SYNCED] {match.name} -> {rel_dst}")
                copied_count += 1
                role_synced = True

        if role_synced:
            synced_roles.append(mapping)

    return copied_count, synced_roles


def update_profile_metadata(
    profile_dir: Path,
    synced_roles: list[RoleMapping],
    dry_run: bool = False,
) -> None:
    """Update upload-cvs-r2.mjs, data/en.json, and data/id.json in profile-new."""
    # 1. Update upload-cvs-r2.mjs CV_MAPPING
    script_file = profile_dir / "scripts" / "upload-cvs-r2.mjs"
    if script_file.exists():
        content = script_file.read_text(encoding="utf-8")
        mapping_entries: list[dict[str, str]] = []
        for r in synced_roles:
            mapping_entries.append({"folder": r.r2_folder, "file": f"{r.file_prefix_id}.pdf"})
            mapping_entries.append({"folder": r.r2_folder, "file": f"{r.file_prefix_en}.pdf"})

        # Format JS array
        formatted_rows = [f"  {{ folder: '{m['folder']}', file: '{m['file']}' }}," for m in mapping_entries]
        new_block = "const CV_MAPPING = [\n" + "\n".join(formatted_rows) + "\n];"

        updated = re.sub(r"const CV_MAPPING = \[\s*[\s\S]*?\s*\];", new_block, content)
        if dry_run:
            print(f"  [DRY-RUN] Update CV_MAPPING in {script_file.relative_to(profile_dir)}")
        else:
            script_file.write_text(updated, encoding="utf-8")
            print(f"  [UPDATED] {script_file.relative_to(profile_dir)}")

    # 2. Update data/en.json and data/id.json
    for json_name, lang_key, label_en, label_id in [
        ("en.json", "en", "English Version", "Indonesian Version"),
        ("id.json", "id", "Versi Bahasa Inggris", "Versi Bahasa Indonesia"),
    ]:
        json_path = profile_dir / "data" / json_name
        if not json_path.exists():
            continue

        data = json.loads(json_path.read_text(encoding="utf-8"))
        hero = data.get("hero", {})
        existing_repo = hero.get("cvRepository", [])
        existing_folders = {item.get("folder") for item in existing_repo}

        for r in synced_roles:
            category_title = r.en_label if lang_key == "en" else r.id_label
            entry = {
                "category": category_title,
                "folder": r.r2_folder,
                "files": [
                    {"label": label_en, "file": f"{r.file_prefix_en}.pdf"},
                    {"label": label_id, "file": f"{r.file_prefix_id}.pdf"},
                ],
            }
            if r.r2_folder in existing_folders:
                # Update existing entry
                for idx, item in enumerate(existing_repo):
                    if item.get("folder") == r.r2_folder:
                        existing_repo[idx] = entry
            else:
                existing_repo.append(entry)
                existing_folders.add(r.r2_folder)

        hero["cvRepository"] = existing_repo
        data["hero"] = hero

        if dry_run:
            print(f"  [DRY-RUN] Update cvRepository in {json_path.relative_to(profile_dir)}")
        else:
            json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"  [UPDATED] {json_path.relative_to(profile_dir)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync CV-Brainstormer deliverables into profile-new portfolio repository."
    )
    parser.add_argument(
        "--candidate",
        default="rafli-arraafi",
        help="Candidate slug (default: 'rafli-arraafi')",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Run date folder (default: latest from LATEST.md)",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=DEFAULT_PROFILE_DIR,
        help=f"Path to profile-new repository (default: {DEFAULT_PROFILE_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without copying or writing files",
    )
    parser.add_argument(
        "--upload-r2",
        action="store_true",
        help="Trigger bun run upload:cvs in profile-new after syncing",
    )

    args = parser.parse_args()

    try:
        run_dir = resolve_run_dir(args.candidate, args.date)
    except FileNotFoundError as err:
        sys.stderr.write(f"Error: {err}\n")
        return 1

    profile_dir = args.target_dir.resolve()
    if not profile_dir.exists():
        sys.stderr.write(f"Error: Target profile repository not found: {profile_dir}\n")
        return 1

    print(f"\n🚀 Syncing CV deliverables from: {run_dir}")
    print(f"   Destination portfolio:         {profile_dir}\n")

    copied_count, synced_roles = sync_files(run_dir, profile_dir, dry_run=args.dry_run)
    print(f"\n✔ Total files processed: {copied_count} across {len(synced_roles)} roles.")

    update_profile_metadata(profile_dir, synced_roles, dry_run=args.dry_run)

    if args.upload_r2 and not args.dry_run:
        print("\n☁️ Triggering Cloudflare R2 upload script...")
        try:
            res = subprocess.run(
                ["bun", "scripts/upload-cvs-r2.mjs"],
                cwd=profile_dir,
                capture_output=True,
                text=True,
            )
            print(res.stdout)
            if res.returncode != 0:
                sys.stderr.write(res.stderr)
        except Exception as exc:
            sys.stderr.write(f"Failed to execute bun upload script: {exc}\n")

    print("\n🎉 Sync operation completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

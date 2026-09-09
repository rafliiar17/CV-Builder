#!/usr/bin/env python3
"""
CV-Brainstormer Unified CLI.

Centralized command-line interface for the CV-Brainstormer workflow:
  cvb init      Initialize candidate run directory and extract input files
  cvb extract   Extract plain text and hyperlinks from PDF/DOCX/TXT
  cvb render    Batch compile deliverable documents to PDF and DOCX via MarkForge
  cvb audit     Audit CV ATS compliance and keyword density
"""

from __future__ import annotations

import argparse
import datetime
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.extract import extract_file


def slugify(text: str) -> str:
    """Generate URL/folder-safe slug from arbitrary text."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return re.sub(r"-+", "-", slug)


def file_slugify(text: str) -> str:
    """Generate filename-safe slug with underscores instead of hyphens."""
    return slugify(text).replace("-", "_")


# ==============================================================================
# SUBCOMMAND: init
# ==============================================================================
def cmd_init(args: argparse.Namespace) -> int:
    """Initialize a candidate run directory with standardized subfolders and inputs."""
    candidate_name = args.candidate
    cv_file = Path(args.cv).resolve()

    if not cv_file.exists():
        sys.stderr.write(f"Error: CV file not found: {cv_file}\n")
        return 1

    projects_file = Path(args.projects).resolve() if args.projects else None
    if projects_file and not projects_file.exists():
        sys.stderr.write(f"Error: Projects file not found: {projects_file}\n")
        return 1

    run_date = args.date or datetime.date.today().isoformat()
    candidate_slug = slugify(candidate_name)
    candidate_file_slug = file_slugify(candidate_name)
    target_slug = slugify(args.roles)
    run_id = f"{run_date}-{target_slug}"

    base_candidate_dir = REPO_ROOT / "output" / "candidates" / candidate_slug
    run_dir = base_candidate_dir / run_id

    # Create subdirectories matching architecture contract
    subdirs = [
        "input",
        "scratch",
        "reports",
        "salary",
        "cv",
        "portfolio",
        "interview",
        "application",
        "platform",
    ]
    for sub in subdirs:
        (run_dir / sub).mkdir(parents=True, exist_ok=True)

    # Copy CV file
    cv_ext = cv_file.suffix
    dest_cv = run_dir / "input" / f"original-cv{cv_ext}"
    shutil.copy2(cv_file, dest_cv)

    # Extract text from CV
    try:
        extracted_text = extract_file(dest_cv)
    except Exception as exc:
        extracted_text = f"[Extraction warning: {exc}]\n"
    (run_dir / "input" / "extracted.txt").write_text(extracted_text, encoding="utf-8")

    # Copy or initialize projects-list.md
    dest_projects = run_dir / "input" / "projects-list.md"
    if projects_file:
        shutil.copy2(projects_file, dest_projects)
    else:
        sample_projects = REPO_ROOT / "input" / "projects-list.md"
        if sample_projects.exists():
            shutil.copy2(sample_projects, dest_projects)
        else:
            dest_projects.write_text(f"# Projects List — {candidate_name}\n\n- Add projects here\n", encoding="utf-8")

    # Generate target-brief.md
    brief_content = f"""# Target Brief — {candidate_name}

- **Candidate**: {candidate_name}
- **Candidate Slug**: {candidate_slug}
- **File Slug**: {candidate_file_slug}
- **Run ID**: {run_id}
- **Target Roles**: {args.roles}
- **Date**: {run_date}

## Instructions
1. Run Agent 00.25 (Role Discovery Interviewer) and Agent 00.5 (Target Decision Gate).
2. Execute Agents 01–06 in parallel to analyze ATS, HR, Tech, Achievements, and Bias.
3. Verify evidence with Agent 04.5 and review salary with Agent 05.75.
4. Synthesize and tailor CVs with Agent 07 and Agent 08.
5. Generate application packages with Agent 10 and Agent 11.
"""
    (run_dir / "input" / "target-brief.md").write_text(brief_content, encoding="utf-8")

    # Generate harvard-resume-checklist.md
    harvard_checklist = """# Harvard Resume Standard — Pre-Flight Checklist
- [ ] Visual Hierarchy & Single-Column ATS Layout
- [ ] Contact Header with GitHub, LinkedIn, Website, Threads
- [ ] Bullet points start with strong power verbs (e.g. Architected, Engineered)
- [ ] STAR / XYZ format used (Accomplished [X] as measured by [Y] by doing [Z])
- [ ] All metrics verified against Evidence Gate (04.5)
- [ ] Zero buzzwords, subjective fluff, or unsubstantiated claims
"""
    (run_dir / "input" / "harvard-resume-checklist.md").write_text(harvard_checklist, encoding="utf-8")

    # Update LATEST.md
    latest_content = f"""# Latest Run
- **Run ID**: {run_id}
- **Directory**: {run_dir}
- **Roles**: {args.roles}
- **Updated At**: {datetime.datetime.now().isoformat()}
"""
    (base_candidate_dir / "LATEST.md").write_text(latest_content, encoding="utf-8")

    print("\n✔ Successfully initialized run directory:")
    print(f"  {run_dir}\n")
    print(f"Candidate:    {candidate_name} ({candidate_slug})")
    print(f"Target Roles: {args.roles}")
    print(f"Extracted CV: {run_dir / 'input' / 'extracted.txt'}")
    return 0


# ==============================================================================
# SUBCOMMAND: extract
# ==============================================================================
def cmd_extract(args: argparse.Namespace) -> int:
    """Extract plain text and hyperlinks from PDF/DOCX/TXT file."""
    src = Path(args.file).resolve()
    if not src.exists():
        sys.stderr.write(f"Error: File not found: {src}\n")
        return 1

    try:
        text = extract_file(src)
        if args.output:
            out_path = Path(args.output).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(text, encoding="utf-8")
            if not args.quiet:
                print(f"✔ Extracted {len(text)} characters to {out_path}")
        else:
            print(text)
        return 0
    except Exception as exc:
        sys.stderr.write(f"Extraction failed: {exc}\n")
        return 1


# ==============================================================================
# SUBCOMMAND: render
# ==============================================================================
def cmd_render(args: argparse.Namespace) -> int:
    """Compile markdown files to DOCX and PDF using MarkForge or fallback."""
    target = Path(args.target).resolve()
    if not target.exists():
        sys.stderr.write(f"Error: Target path does not exist: {target}\n")
        return 1

    script_markforge = REPO_ROOT / "scripts" / "render-markforge.sh"

    # Forward to render-markforge.sh if available
    if script_markforge.exists() and not args.fallback:
        cmd = [str(script_markforge), str(target)]
        if args.template:
            cmd.extend(["-t", args.template])
        if args.format:
            cmd.extend(["-f", args.format])
        if args.outdir:
            cmd.extend(["-o", str(args.outdir)])
        if args.quiet:
            cmd.append("-q")

        res = subprocess.run(cmd)
        return res.returncode

    # Fallback to python render_outputs
    from scripts.render_outputs import main as fallback_main
    fallback_args = [str(target)]
    if args.format:
        fallback_args.extend(["-f", args.format])
    if args.outdir:
        fallback_args.extend(["-o", str(args.outdir)])
    return fallback_main(fallback_args)


# ==============================================================================
# SUBCOMMAND: audit
# ==============================================================================
def cmd_audit(args: argparse.Namespace) -> int:
    """Audit CV ATS compliance and keyword density."""
    target = Path(args.cv).resolve()
    if not target.exists():
        sys.stderr.write(f"Error: CV markdown file not found: {target}\n")
        return 1

    script_audit = REPO_ROOT / "scripts" / "ats-audit.sh"
    if not script_audit.exists():
        sys.stderr.write(f"Error: Audit script not found: {script_audit}\n")
        return 1

    cmd = [str(script_audit), str(target)]
    if args.json:
        cmd.append("--json")
    res = subprocess.run(cmd)
    return res.returncode


# ==============================================================================
# MAIN PARSER
# ==============================================================================
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cvb",
        description="CV-Brainstormer Unified CLI — Manage candidate reviews, extraction, and rendering.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Init
    p_init = subparsers.add_parser("init", help="Initialize a candidate review run directory.")
    p_init.add_argument("candidate", help="Candidate full name (e.g. 'Rafli Arraafi')")
    p_init.add_argument("cv", help="Path to original CV file (PDF, DOCX, or TXT)")
    p_init.add_argument("--roles", required=True, help="Target roles, comma-separated (e.g. 'Data Analyst, Application Support')")
    p_init.add_argument("--projects", help="Path to existing projects-list.md file")
    p_init.add_argument("--date", help="Override run date (YYYY-MM-DD)")
    p_init.set_defaults(func=cmd_init)

    # Extract
    p_extract = subparsers.add_parser("extract", help="Extract plain text and links from CV file.")
    p_extract.add_argument("file", help="Path to document (PDF, DOCX, or TXT)")
    p_extract.add_argument("-o", "--output", help="Output path for extracted text")
    p_extract.add_argument("-q", "--quiet", action="store_true", help="Suppress output to stdout")
    p_extract.set_defaults(func=cmd_extract)

    # Render
    p_render = subparsers.add_parser("render", help="Compile documents to DOCX and PDF.")
    p_render.add_argument("target", help="Markdown file or candidate run directory")
    p_render.add_argument("-t", "--template", help="Template override (ats-classic, tech-spec, modern-accent)")
    p_render.add_argument("-f", "--format", choices=["both", "pdf", "docx"], default="both", help="Output format")
    p_render.add_argument("-o", "--outdir", help="Output directory")
    p_render.add_argument("-q", "--quiet", action="store_true", help="Suppress non-essential messages")
    p_render.add_argument("--fallback", action="store_true", help="Force python-docx/weasyprint fallback renderer")
    p_render.set_defaults(func=cmd_render)

    # Audit
    p_audit = subparsers.add_parser("audit", help="Audit CV ATS compliance and metrics.")
    p_audit.add_argument("cv", help="Path to CV markdown file")
    p_audit.add_argument("--json", action="store_true", help="Output JSON results")
    p_audit.set_defaults(func=cmd_audit)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

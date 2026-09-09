#!/usr/bin/env python3
"""
MarkForge Integration Bridge for CV-Brainstormer.

Connects CV-Brainstormer to the MarkForge document compilation engine (PDF & DOCX)
and AST-based ATS compliance analyzer.

Usage:
  # Render a single markdown file (auto-detects template)
  python scripts/markforge_bridge.py build path/to/cv-data-analyst-en.md

  # Render an entire candidate run directory
  python scripts/markforge_bridge.py build output/candidates/rafli-arraafi/2026-06-01-data-analyst-application-support/

  # Audit a CV with deterministic AST analyzer
  python scripts/markforge_bridge.py audit path/to/cv-data-analyst-en.md

  # Check MarkForge environment and engines
  python scripts/markforge_bridge.py doctor
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ─── Template Mapping Rules ──────────────────────────────────────────────────
# Maps document types and filename patterns to MarkForge presets:
# - CVs (cv-*.md) -> ats-classic (100% ATS compliant, single-column)
# - Reports & Benchmarks -> tech-spec (RFC/spec layout with callouts & tables)
# - Portfolios (projects-from-list.md) -> modern-accent (clean portfolio layout)
# - Platform & Application packages -> tech-spec or executive
TEMPLATE_MAP = [
    # Portfolios
    (r"projects-from-list", "modern-accent"),
    (r"portfolio", "modern-accent"),
    # CVs (ATS optimized)
    (r"cv-", "ats-classic"),
    (r"^cv\.", "ats-classic"),
    (r"/cv/", "ats-classic"),
    # Reports, Salary benchmarks, STAR interview prep
    (r"final-report", "tech-spec"),
    (r"verification-report", "tech-spec"),
    (r"salary-market", "tech-spec"),
    (r"star-", "tech-spec"),
    (r"star-story-bank", "tech-spec"),
    (r"harvard-.*review", "tech-spec"),
    (r"target-brief", "tech-spec"),
    # Application & Platform documents
    (r"cover-letter", "ats-classic"),
    (r"email-application", "tech-spec"),
    (r"email-follow-up", "tech-spec"),
    (r"glints", "tech-spec"),
    (r"linkedin", "tech-spec"),
    (r"upwork", "tech-spec"),
]


def detect_template(file_path: Path | str) -> str:
    """
    Detects the optimal MarkForge template for a given Markdown file
    based on its filename and directory location.
    """
    p = Path(file_path)
    filename = p.name.lower()
    path_str = str(p).lower()

    # 1. Exact or prefix matches on filename
    if filename.startswith("cv-") or filename == "cv.md" or "/cv/" in path_str:
        return "ats-classic"
    if "projects-from-list" in filename or "/portfolio/" in path_str:
        return "modern-accent"
    if any(k in filename for k in ["final-report", "verification-report", "salary-market", "star-"]):
        return "tech-spec"

    # 2. Pattern match in full path
    for pattern, template in TEMPLATE_MAP:
        if pattern in filename or pattern in path_str:
            return template

    # Default fallback
    return "tech-spec"


class MarkForgeEngine:
    """Manages discovery and execution of the MarkForge CLI engine."""

    def __init__(self, markforge_dir: Optional[str] = None):
        self.markforge_dir = self._resolve_markforge_dir(markforge_dir)
        self.bun_bin = self._resolve_bun_bin()
        self.global_cli = shutil.which("markforge")

    def _resolve_markforge_dir(self, custom_dir: Optional[str] = None) -> Optional[Path]:
        if custom_dir:
            p = Path(custom_dir)
            if p.exists():
                return p.resolve()

        # Check environment variable
        env_dir = os.environ.get("MARKFORGE_DIR")
        if env_dir and Path(env_dir).exists():
            return Path(env_dir).resolve()

        # Check known sibling paths
        candidates = [
            Path("/home/archy/Projects/markforge"),
            Path(__file__).resolve().parent.parent.parent / "markforge",
            Path.cwd().parent / "markforge",
            Path.cwd() / "markforge",
        ]
        for c in candidates:
            if c.exists() and (c / "packages" / "cli" / "src" / "index.ts").exists():
                return c.resolve()

        return None

    def _resolve_bun_bin(self) -> Optional[str]:
        # 1. Standard PATH
        bun_path = shutil.which("bun")
        if bun_path:
            return bun_path

        # 2. Common install locations
        home = Path.home()
        candidates = [
            home / ".bun" / "bin" / "bun",
            Path("/usr/local/bin/bun"),
            Path("/usr/bin/bun"),
        ]
        for c in candidates:
            if c.exists() and os.access(c, os.X_OK):
                return str(c)

        return None

    def is_available(self) -> bool:
        if self.global_cli:
            return True
        return bool(self.bun_bin and self.markforge_dir)

    def get_invocation_command(self) -> List[str]:
        if os.environ.get("MARKFORGE_BIN"):
            return [os.environ["MARKFORGE_BIN"]]

        if self.global_cli:
            return [self.global_cli]

        if self.bun_bin and self.markforge_dir:
            cli_entry = self.markforge_dir / "packages" / "cli" / "src" / "index.ts"
            if cli_entry.exists():
                return [self.bun_bin, "run", str(cli_entry)]

        raise RuntimeError(
            "MarkForge could not be located. Ensure either:\n"
            "  1. MarkForge repo is located at /home/archy/Projects/markforge (or set MARKFORGE_DIR)\n"
            "  2. 'markforge' is installed globally in PATH\n"
            "  3. Bun is installed at ~/.bun/bin/bun"
        )

    def run_command(self, args: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        cmd = self.get_invocation_command() + args
        cwd = str(self.markforge_dir) if self.markforge_dir else None
        return subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=False,
        )


@dataclass
class BuildResult:
    file_path: str
    template: str
    format: str
    success: bool
    output_files: List[str]
    error_message: Optional[str] = None
    telemetry: Optional[Dict[str, Any]] = None


def compile_document(
    file_path: Path | str,
    template: Optional[str] = None,
    fmt: str = "both",
    outdir: Optional[Path | str] = None,
    quiet: bool = False,
    telemetry: bool = False,
    json_output: bool = False,
    engine: Optional[MarkForgeEngine] = None,
) -> BuildResult:
    """
    Compiles a Markdown document to PDF, DOCX, and/or HTML using MarkForge.
    """
    engine = engine or MarkForgeEngine()
    path_obj = Path(file_path).resolve()
    if not path_obj.exists():
        return BuildResult(
            file_path=str(path_obj),
            template=template or "ats-classic",
            format=fmt,
            success=False,
            output_files=[],
            error_message=f"File not found: {path_obj}",
        )

    selected_template = template or detect_template(path_obj)
    target_outdir = Path(outdir).resolve() if outdir else path_obj.parent

    cmd_args = [
        "build",
        str(path_obj),
        "-t", selected_template,
        "-f", fmt,
        "-o", str(target_outdir),
    ]

    if quiet:
        cmd_args.append("-q")
    if telemetry:
        cmd_args.append("--telemetry")
    if json_output:
        cmd_args.append("--json")

    proc = engine.run_command(cmd_args, capture_output=not (not json_output and not quiet and sys.stdout.isatty()))

    expected_exts = []
    if fmt in ("pdf", "both", "all"):
        expected_exts.append(".pdf")
    if fmt in ("docx", "both", "all"):
        expected_exts.append(".docx")
    if fmt in ("html", "all"):
        expected_exts.append(".html")

    base_name = path_obj.stem
    output_files = [str(target_outdir / f"{base_name}{ext}") for ext in expected_exts if (target_outdir / f"{base_name}{ext}").exists()]

    telemetry_data = None
    if json_output and proc.stdout:
        try:
            parsed = json.loads(proc.stdout)
            telemetry_data = parsed.get("telemetry")
        except json.JSONDecodeError:
            pass

    return BuildResult(
        file_path=str(path_obj),
        template=selected_template,
        format=fmt,
        success=(proc.returncode == 0 and len(output_files) > 0),
        output_files=output_files,
        error_message=proc.stderr if proc.returncode != 0 else None,
        telemetry=telemetry_data,
    )


def audit_document(
    file_path: Path | str,
    json_output: bool = False,
    engine: Optional[MarkForgeEngine] = None,
) -> Dict[str, Any]:
    """
    Runs MarkForge AST analyzer on a markdown document to compute ATS compliance,
    action verb count, and metrics density.
    """
    engine = engine or MarkForgeEngine()
    path_obj = Path(file_path).resolve()
    if not path_obj.exists():
        raise FileNotFoundError(f"Input file not found: {path_obj}")

    cmd_args = ["analyze", str(path_obj)]
    if json_output:
        cmd_args.append("--json")

    proc = engine.run_command(cmd_args, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"MarkForge analyze failed: {proc.stderr or proc.stdout}")

    if json_output:
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError:
            return {"raw_output": proc.stdout}

    return {"output": proc.stdout}


def discover_candidate_run_files(run_dir: Path) -> List[Path]:
    """
    Discovers all candidate output markdown files in a run directory,
    excluding scratch/ and input/ directories.
    """
    collected: List[Path] = []
    for root, dirs, files in os.walk(run_dir):
        # Skip scratch and input directories
        rel_path = Path(root).relative_to(run_dir)
        parts = rel_path.parts
        if parts and parts[0] in ("scratch", "input", ".git"):
            continue

        for f in files:
            if f.endswith(".md"):
                collected.append(Path(root) / f)

    # Sort: CVs first, then reports, then portfolio, then interviews, then application/platform
    def sort_key(p: Path) -> Tuple[int, str]:
        s = str(p).lower()
        if "/cv/" in s or p.name.startswith("cv-"):
            return (0, str(p))
        if "/reports/" in s or "report" in s:
            return (1, str(p))
        if "/salary/" in s:
            return (2, str(p))
        if "/portfolio/" in s:
            return (3, str(p))
        if "/interview/" in s or "star-" in s:
            return (4, str(p))
        return (5, str(p))

    collected.sort(key=sort_key)
    return collected


def main() -> int:
    parser = argparse.ArgumentParser(
        description="MarkForge Integration Bridge for CV-Brainstormer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Command to execute")

    # ─── Build Command ───────────────────────────────────────────────────────
    build_p = subparsers.add_parser("build", help="Compile markdown file(s) or run folder to PDF & DOCX")
    build_p.add_argument("target", help="Markdown file or candidate run directory")
    build_p.add_argument("-t", "--template", help="Template override (ats-classic, tech-spec, modern-accent, academic, executive)")
    build_p.add_argument("-f", "--format", default="both", choices=["both", "pdf", "docx", "html", "all"], help="Output format")
    build_p.add_argument("-o", "--outdir", help="Output directory")
    build_p.add_argument("-q", "--quiet", action="store_true", help="Suppress non-essential logging")
    build_p.add_argument("--telemetry", action="store_true", help="Print compilation timing telemetry")
    build_p.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # ─── Audit Command ───────────────────────────────────────────────────────
    audit_p = subparsers.add_parser("audit", help="Run deterministic ATS compliance & metrics audit")
    audit_p.add_argument("target", help="Markdown file or directory containing CVs")
    audit_p.add_argument("--json", action="store_true", help="Output audit report as JSON")
    audit_p.add_argument("--min-score", type=int, default=0, help="Fail if ATS score is below this threshold")

    # ─── Doctor Command ──────────────────────────────────────────────────────
    doctor_p = subparsers.add_parser("doctor", help="Inspect MarkForge environment and PDF/DOCX engines")
    doctor_p.add_argument("--json", action="store_true", help="Output diagnostics as JSON")

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        return 0

    engine = MarkForgeEngine()

    if args.subcommand == "doctor":
        if not engine.is_available():
            print("❌ MarkForge engine not available.")
            print(f"   Directory checked: {engine.markforge_dir}")
            print(f"   Bun path: {engine.bun_bin}")
            return 1
        proc = engine.run_command(["doctor"] + (["--json"] if args.json else []), capture_output=False)
        return proc.returncode

    if args.subcommand == "audit":
        target_path = Path(args.target).resolve()
        if not target_path.exists():
            print(f"Error: Target path not found: {target_path}", file=sys.stderr)
            return 1

        files_to_audit: List[Path] = []
        if target_path.is_dir():
            # Find all cv-*.md files in directory
            for root, _, files in os.walk(target_path):
                for f in files:
                    if (f.startswith("cv-") or f == "cv.md") and f.endswith(".md"):
                        files_to_audit.append(Path(root) / f)
            if not files_to_audit:
                # If no cv-*.md found, audit all .md files in cv/
                for f in target_path.glob("*.md"):
                    files_to_audit.append(f)
        else:
            files_to_audit.append(target_path)

        if not files_to_audit:
            print(f"No markdown documents found to audit in {target_path}", file=sys.stderr)
            return 1

        all_passed = True
        results = []

        for f in files_to_audit:
            try:
                res = audit_document(f, json_output=args.json, engine=engine)
                if args.json:
                    results.append({"file": str(f), "audit": res})
                    score = res.get("score", 0)
                    if args.min_score and score < args.min_score:
                        all_passed = False
                else:
                    print(f"\n📄 Auditing: {f.name} ({f.parent})")
                    print(res.get("output", ""))
                    if "--min-score" in sys.argv:
                        json_res = audit_document(f, json_output=True, engine=engine)
                        score = json_res.get("score", 0)
                        if score < args.min_score:
                            print(f"❌ Score {score} is below minimum required {args.min_score}!")
                            all_passed = False
                        else:
                            print(f"✔ Score {score} meets minimum threshold ({args.min_score}).")
            except Exception as e:
                print(f"Error auditing {f}: {e}", file=sys.stderr)
                all_passed = False

        if args.json:
            print(json.dumps(results, indent=2))

        return 0 if all_passed else 1

    if args.subcommand == "build":
        target_path = Path(args.target).resolve()
        if not target_path.exists():
            print(f"Error: Target not found: {target_path}", file=sys.stderr)
            return 1

        files_to_build: List[Path] = []
        if target_path.is_dir():
            files_to_build = discover_candidate_run_files(target_path)
            if not files_to_build:
                print(f"No markdown documents found in {target_path}", file=sys.stderr)
                return 1
            if not args.quiet and not args.json:
                print(f"🔍 Discovered {len(files_to_build)} document(s) to compile in {target_path.name}:")
                for f in files_to_build:
                    t = args.template or detect_template(f)
                    rel = f.relative_to(target_path)
                    print(f"   • {rel}  →  template: [{t}]")
                print()
        else:
            files_to_build.append(target_path)

        all_success = True
        built_records = []

        for f in files_to_build:
            res = compile_document(
                file_path=f,
                template=args.template,
                fmt=args.format,
                outdir=args.outdir,
                quiet=args.quiet,
                telemetry=args.telemetry,
                json_output=args.json,
                engine=engine,
            )
            built_records.append(res)
            if not res.success:
                all_success = False

        if args.json:
            print(json.dumps([
                {
                    "file": r.file_path,
                    "template": r.template,
                    "format": r.format,
                    "success": r.success,
                    "outputs": r.output_files,
                    "error": r.error_message,
                    "telemetry": r.telemetry,
                }
                for r in built_records
            ], indent=2))
        elif not args.quiet:
            print("\n" + "═" * 70)
            total = len(built_records)
            successes = sum(1 for r in built_records if r.success)
            print(f"🎉 MarkForge Build Complete: {successes}/{total} document(s) compiled successfully.")
            print("═" * 70)

        return 0 if all_success else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

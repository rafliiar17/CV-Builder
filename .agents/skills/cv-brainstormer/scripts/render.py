#!/usr/bin/env python3
"""
CV Brainstormer — Report & Document Renderer
Delegates rendering to scripts/render_outputs.py.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Locate repository root and ensure scripts/ is importable
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from scripts.render_outputs import (
        add_formatted_runs,
        add_table_to_docx,
        find_markdown_files,
        main as render_outputs_main,
        render_docx,
        render_file,
        render_pdf,
        strip_md,
    )
except ImportError as err:
    sys.stderr.write(f"Error importing render_outputs from {REPO_ROOT}: {err}\n")
    raise


def check_dependencies() -> None:
    """Verify required libraries are available."""
    missing = []
    for pkg in ("docx", "markdown", "weasyprint"):
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg if pkg != "docx" else "python-docx")
    if missing:
        sys.stderr.write(f"ERROR: Missing dependencies: {' '.join(missing)}\n")
        sys.stderr.write(f"Install with: pip install {' '.join(missing)} --break-system-packages\n")
        sys.exit(1)


def extract_cv_section(content: str) -> str:
    """Extract revised CV section if embedded in a monolithic report (legacy helper)."""
    patterns = [
        r"## Revised CV Draft.*?\n(.*?)(?=\n---|\n## |\Z)",
        r"## Draft CV yang Telah Diperbaiki.*?\n(.*?)(?=\n---|\n## |\Z)",
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            cv_content = match.group(1).strip()
            return re.sub(r"^>.*?\n\n", "", cv_content, flags=re.DOTALL)
    return ""


def md_to_docx(content: str, output_path: Path | str, doc_type: str = "report") -> Path:
    """Backward compatibility helper: renders markdown string to docx."""
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    temp_md = out_path.with_suffix(".temp.md")
    try:
        temp_md.write_text(content, encoding="utf-8")
        render_docx(temp_md, out_path)
    finally:
        if temp_md.exists():
            temp_md.unlink()
    return out_path


def md_to_pdf(content: str, output_path: Path | str) -> Path:
    """Backward compatibility helper: renders markdown string to pdf."""
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    temp_md = out_path.with_suffix(".temp.md")
    try:
        temp_md.write_text(content, encoding="utf-8")
        render_pdf(temp_md, out_path)
    finally:
        if temp_md.exists():
            temp_md.unlink()
    return out_path


def main(argv: list[str] | None = None) -> int:
    """Delegate CLI arguments to scripts/render_outputs.py."""
    if argv is None:
        argv = sys.argv[1:]

    # Strip legacy flag if present
    filtered_args = [arg for arg in argv if arg != "--no-cv"]
    return render_outputs_main(filtered_args)


if __name__ == "__main__":
    raise SystemExit(main())

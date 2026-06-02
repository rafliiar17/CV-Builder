from __future__ import annotations

import html
import re
import sys
from pathlib import Path

import markdown
from docx import Document
from docx.shared import Inches, Pt
from weasyprint import HTML


CSS = """
@page { size: A4; margin: 16mm; }
body {
  font-family: Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.42;
  color: #1f2933;
}
h1 { font-size: 20pt; margin: 0 0 6px; }
h2 { font-size: 13pt; margin: 18px 0 6px; border-bottom: 1px solid #d0d7de; padding-bottom: 3px; }
h3 { font-size: 11.5pt; margin: 14px 0 4px; }
p { margin: 0 0 7px; }
ul { margin: 4px 0 8px 18px; padding: 0; }
li { margin-bottom: 3px; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 12px; }
th, td { border: 1px solid #d0d7de; padding: 5px 6px; vertical-align: top; }
th { background: #f6f8fa; }
a { color: #0969da; text-decoration: none; }
"""


def strip_md(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", text)
    return text.strip()


def render_docx(md_path: Path) -> Path:
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.55)
    section.right_margin = Inches(0.55)

    styles = document.styles
    styles["Normal"].font.name = "Arial"
    styles["Normal"].font.size = Pt(10)

    lines = md_path.read_text(encoding="utf-8").splitlines()
    for line in lines:
        raw = line.rstrip()
        if not raw:
            continue
        if raw.startswith("# "):
            document.add_heading(strip_md(raw[2:]), level=1)
        elif raw.startswith("## "):
            document.add_heading(strip_md(raw[3:]), level=2)
        elif raw.startswith("### "):
            document.add_heading(strip_md(raw[4:]), level=3)
        elif raw.startswith("- "):
            document.add_paragraph(strip_md(raw[2:]), style="List Bullet")
        elif raw.startswith("|"):
            continue
        else:
            document.add_paragraph(strip_md(raw))

    out_path = md_path.with_suffix(".docx")
    document.save(out_path)
    return out_path


def render_pdf(md_path: Path) -> Path:
    body = markdown.markdown(
        md_path.read_text(encoding="utf-8"),
        extensions=["tables", "sane_lists"],
        output_format="html5",
    )
    title = html.escape(md_path.stem)
    page = f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>"
    out_path = md_path.with_suffix(".pdf")
    HTML(string=page, base_url=str(md_path.parent)).write_pdf(out_path)
    return out_path


def main(paths: list[str]) -> int:
    if not paths:
        print("usage: render_outputs.py FILE.md [FILE.md ...]", file=sys.stderr)
        return 2

    for item in paths:
        md_path = Path(item)
        if not md_path.exists():
            print(f"missing: {md_path}", file=sys.stderr)
            return 1
        docx_path = render_docx(md_path)
        pdf_path = render_pdf(md_path)
        print(f"rendered: {docx_path}")
        print(f"rendered: {pdf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

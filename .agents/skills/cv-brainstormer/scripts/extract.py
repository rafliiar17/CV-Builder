#!/usr/bin/env python3
"""
CV Brainstormer — CV Extractor Script
Extracts text from PDF or DOCX files into plain text for Agent 00.

Usage:
    python extract.py <input_file> [output_file]

Examples:
    python extract.py input/my-cv.pdf
    python extract.py input/my-cv.docx input/extracted.txt
"""

import sys
import os
from pathlib import Path


def extract_pdf(filepath: str) -> str:
    """Extract text from PDF using pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        print("ERROR: pdfplumber not installed.")
        print("Run: pip install pdfplumber --break-system-packages")
        sys.exit(1)

    text_parts = []
    with pdfplumber.open(filepath) as pdf:
        print(f"PDF has {len(pdf.pages)} page(s).")
        for i, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"--- PAGE {i} ---")
                text_parts.append(page_text.strip())
            else:
                print(f"WARNING: Page {i} has no extractable text (may be image-based).")
                print("Consider using OCR for scanned PDFs.")

    return "\n\n".join(text_parts)


def extract_docx(filepath: str) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        from docx import Document
    except ImportError:
        print("ERROR: python-docx not installed.")
        print("Run: pip install python-docx --break-system-packages")
        sys.exit(1)

    doc = Document(filepath)
    text_parts = []

    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text.strip())

    # Also extract text from tables
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(
                cell.text.strip() for cell in row.cells if cell.text.strip()
            )
            if row_text:
                text_parts.append(row_text)

    return "\n".join(text_parts)


def extract_txt(filepath: str) -> str:
    """Read plain text file."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)

    # Determine output path
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = Path("input/extracted.txt")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Extract based on file type
    ext = input_path.suffix.lower()
    print(f"Extracting: {input_path} ({ext})")

    if ext == ".pdf":
        text = extract_pdf(str(input_path))
    elif ext in (".docx", ".doc"):
        text = extract_docx(str(input_path))
    elif ext in (".txt", ".md"):
        text = extract_txt(str(input_path))
    else:
        print(f"ERROR: Unsupported file type: {ext}")
        print("Supported: .pdf, .docx, .doc, .txt, .md")
        sys.exit(1)

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"=== EXTRACTED FROM: {input_path.name} ===\n\n")
        f.write(text)
        f.write("\n\n=== END OF EXTRACTION ===\n")

    print(f"Done. Output saved to: {output_path}")
    print(f"Character count: {len(text):,}")
    print(f"Word count (approx): {len(text.split()):,}")
    print()
    print("Next step: Pass this file to Agent 00 (Extractor) for normalization.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Example: Extract and inspect pitch deck PDF content.

Demonstrates the PDF extraction pipeline.
Requires a PDF file path as argument, or generates a sample PDF.
"""

import io
import sys
import tempfile
from pathlib import Path

from pitchcritic.extractor import extract_pdf


def create_sample_pdf() -> Path:
    """Generate a minimal sample pitch deck PDF for demonstration."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    slides = [
        ("The Problem", "Enterprise data pipelines break 3x per week on average."),
        ("Our Solution", "Self-healing pipelines powered by anomaly detection."),
        ("Market Opportunity", "TAM: $85B data infrastructure market."),
    ]

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    for title, body in slides:
        c.setFont("Helvetica-Bold", 24)
        c.drawString(72, 700, title)
        c.setFont("Helvetica", 14)
        c.drawString(72, 650, body)
        c.showPage()
    c.save()

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.write(buffer.getvalue())
    tmp.close()
    return Path(tmp.name)


def main() -> None:
    if len(sys.argv) > 1:
        pdf_path = Path(sys.argv[1])
        if not pdf_path.exists():
            print(f"Error: {pdf_path} not found")
            sys.exit(1)
    else:
        print("No PDF provided — generating sample pitch deck...")
        pdf_path = create_sample_pdf()
        print(f"Sample PDF created at: {pdf_path}\n")

    content = extract_pdf(pdf_path)

    print(f"Slide Count: {content.slide_count}")
    print(f"Total Text Length: {len(content.text)} characters\n")

    for i, page_text in enumerate(content.pages, 1):
        print(f"--- Slide {i} ---")
        print(page_text[:200] if page_text else "(empty slide)")
        print()


if __name__ == "__main__":
    main()

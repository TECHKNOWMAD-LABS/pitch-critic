"""Shared test fixtures including a reportlab-generated pitch deck PDF."""

import io
from pathlib import Path

import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Create a 10-slide pitch deck PDF using reportlab."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    slides = [
        ("Problem", "Small businesses lose $50B annually to manual invoicing errors."),
        ("Solution", "AI-powered invoicing that reduces errors by 95%."),
        ("Market", "TAM: $200B. SAM: $40B. SOM: $2B in 3 years."),
        ("Business Model", "SaaS. $99/mo per seat. 40% gross margin."),
        ("Traction", "500 beta users. $50K MRR. 15% MoM growth."),
        ("Team", "CEO: ex-Stripe. CTO: ex-Google. 3 engineers."),
        ("Competition", "QuickBooks, FreshBooks. We win on AI automation."),
        ("Financials", "Year 1: $1.2M ARR. Year 3: $15M ARR. Burn: $150K/mo."),
        ("GTM", "Bottom-up via SMB communities. $180 CAC. 24-month payback."),
        ("Ask", "Raising $3M Seed at $15M cap. 18-month runway."),
    ]

    for title, body in slides:
        c.setFont("Helvetica-Bold", 24)
        c.drawString(72, 700, title)
        c.setFont("Helvetica", 14)
        c.drawString(72, 650, body)
        c.showPage()

    c.save()
    return buffer.getvalue()


@pytest.fixture
def sample_pdf_path(tmp_path: Path, sample_pdf_bytes: bytes) -> Path:
    pdf_file = tmp_path / "pitch.pdf"
    pdf_file.write_bytes(sample_pdf_bytes)
    return pdf_file


@pytest.fixture
def single_page_pdf_bytes() -> bytes:
    """One-page PDF with minimal content."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(72, 700, "We are disrupting the disruption space.")
    c.showPage()
    c.save()
    return buffer.getvalue()

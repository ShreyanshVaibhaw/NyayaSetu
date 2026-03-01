"""Generate admin analytics report PDF for MSEFC/Ministry users."""

from __future__ import annotations

from io import BytesIO
from typing import Dict

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def build_admin_report_pdf(metrics: Dict, highlights: list[str] | None = None) -> bytes:
    """Create compact monthly admin report PDF."""
    highlights = highlights or []
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    y = 800
    lines = [
        "NYAYASETU ADMIN REPORT",
        "",
        f"Total Disputes: {metrics.get('total_disputes', 0):,}",
        f"Total Amount Disputed: Rs {metrics.get('total_amount_disputed', 0):,.2f}",
        f"Total Recovered: Rs {metrics.get('total_recovered', 0):,.2f}",
        f"Recovery Rate: {metrics.get('recovery_rate', 0):.2f}%",
        f"Average Resolution Days: {metrics.get('avg_resolution_days', 0)}",
        "",
        "Highlights:",
    ]
    lines.extend([f"- {item}" for item in highlights] or ["- No highlights provided."])
    for line in lines:
        c.drawString(50, y, line)
        y -= 18
    c.showPage()
    c.save()
    return buf.getvalue()

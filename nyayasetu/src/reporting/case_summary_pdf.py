"""Generate one-page dispute case summary PDFs."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.common.models import CaseOutcomePrediction, DisputeCase
from src.reporting.pdf_base import build_header, draw_page_chrome, get_pdf_styles


def build_case_summary_pdf(dispute: DisputeCase, prediction: CaseOutcomePrediction | None = None) -> bytes:
    """Create one-page summary PDF for MSE records."""
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=0.9 * inch,
        title="Case Summary",
    )
    styles = get_pdf_styles()
    story: list = []

    build_header(story, "NYAYASETU CASE SUMMARY", f"Case ID: {dispute.case_id} | Date: {dispute.created_at.date().isoformat()}")
    if prediction and prediction.settlement_probability >= 0.8:
        strength = "🟢 Strong"
    elif prediction and prediction.settlement_probability >= 0.5:
        strength = "🟡 Moderate"
    else:
        strength = "🔴 Weak"

    summary_table = Table(
        [
            ["Case Details", "Financial Summary"],
            [
                f"MSE: {dispute.mse.enterprise_name}\nBuyer: {dispute.buyer.buyer_name}\nStage: {dispute.current_stage}\nJurisdiction: MSEFC {dispute.msefc_state}",
                f"Principal: Rs {dispute.total_principal:,.2f}\nInterest: Rs {dispute.total_interest:,.2f}\nTotal Claim: Rs {dispute.total_claim:,.2f}\nStrength: {strength}",
            ],
            ["Prediction", "Recommendation"],
            [
                (
                    "No prediction available"
                    if prediction is None
                    else f"Settlement Probability: {prediction.settlement_probability*100:.1f}%\n"
                    f"Expected Recovery: Rs {prediction.predicted_recovery_amount:,.2f}\n"
                    f"Resolution: {prediction.estimated_days_to_resolution} days"
                ),
                (
                    "Proceed with filing review."
                    if prediction is None
                    else f"Strategy: {prediction.recommended_strategy}\n"
                    f"Confidence: {prediction.confidence:.2f}\n"
                    f"Top risk: {(prediction.risk_factors[0] if prediction.risk_factors else 'General uncertainty')}"
                ),
            ],
        ],
        colWidths=[2.9 * inch, 2.9 * inch],
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#D1D5DB")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E2D4D")),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#1E2D4D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("TEXTCOLOR", (0, 2), (-1, 2), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, 3), "Helvetica"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph("This summary is generated for rapid case review and planning.", styles["NyClause"]))

    doc.build(
        story,
        onFirstPage=lambda canvas, d: draw_page_chrome(canvas, d, watermark="SUMMARY"),
        onLaterPages=lambda canvas, d: draw_page_chrome(canvas, d, watermark="SUMMARY"),
    )
    return buf.getvalue()


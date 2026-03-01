"""Generate settlement agreement PDF output."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.common.models import SettlementAgreement
from src.reporting.pdf_base import build_header, draw_page_chrome, get_pdf_styles


def build_settlement_agreement_pdf(agreement: SettlementAgreement) -> bytes:
    """Create professional settlement agreement PDF and return bytes."""
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=0.9 * inch,
        title="Settlement Agreement",
    )
    styles = get_pdf_styles()
    story: list = []

    build_header(story, "SETTLEMENT AGREEMENT", f"Reference: {agreement.agreement_id} | Date: {agreement.generated_at.date().isoformat()}")
    party_table = Table(
        [
            ["First Party (MSE)", agreement.mse_name],
            ["Second Party (Buyer)", agreement.buyer_name],
            ["Case Reference", agreement.case_id],
            ["Settlement Amount", f"Rs {agreement.settlement_amount:,.2f}"],
            ["Interest Waived", f"Rs {agreement.interest_waived:,.2f}"],
        ],
        colWidths=[2.2 * inch, 3.8 * inch],
    )
    party_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#D1D5DB")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F4F6")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(party_table)
    story.append(Spacer(1, 0.15 * inch))
    story.append(HRFlowable(color=colors.HexColor("#D1D5DB"), thickness=1))
    story.append(Spacer(1, 0.1 * inch))

    recitals = [
        "WHEREAS, the Supplier has raised dues against delayed payment under MSMED Act, 2006;",
        "WHEREAS, the Buyer intends to settle the matter amicably without prejudice to legal rights;",
        "WHEREAS, Parties agree to resolve on terms recorded below.",
    ]
    story.append(Paragraph("Recitals", styles["NyStrong"]))
    for idx, recital in enumerate(recitals, start=1):
        story.append(Paragraph(f"{idx}. {recital}", styles["NyClause"]))

    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph("Payment Schedule", styles["NyStrong"]))
    schedule_rows = [["Installment", "Date", "Amount (Rs)", "Description"]]
    for idx, sched in enumerate(agreement.payment_schedule, start=1):
        schedule_rows.append(
            [
                str(idx),
                str(sched.get("date", "")),
                f"{float(sched.get('amount', 0)):,.2f}",
                str(sched.get("description", "Installment payment")),
            ]
        )
    schedule_table = Table(schedule_rows, colWidths=[0.9 * inch, 1.3 * inch, 1.4 * inch, 2.4 * inch])
    schedule_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#D1D5DB")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E2D4D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F9FAFB")]),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(schedule_table)
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph("Terms and Conditions", styles["NyStrong"]))
    for idx, term in enumerate(agreement.terms_and_conditions, start=1):
        story.append(Paragraph(f"{idx}. {term}", styles["NyClause"]))

    story.append(Spacer(1, 0.16 * inch))
    story.append(Paragraph("Signatures", styles["NyStrong"]))
    sig_table = Table(
        [
            ["Supplier (MSE)", "Buyer"],
            ["\n\n__________________________", "\n\n__________________________"],
            ["Name/Designation", "Name/Designation"],
            ["\nWitness 1: ____________________", "Witness 2: ____________________"],
        ],
        colWidths=[2.9 * inch, 2.9 * inch],
    )
    sig_table.setStyle(
        TableStyle(
            [
                ("LINEABOVE", (0, 1), (-1, 1), 0.7, colors.HexColor("#9CA3AF")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(sig_table)

    doc.build(
        story,
        onFirstPage=lambda canvas, d: draw_page_chrome(canvas, d, watermark="DRAFT"),
        onLaterPages=lambda canvas, d: draw_page_chrome(canvas, d, watermark="DRAFT"),
    )
    return buf.getvalue()


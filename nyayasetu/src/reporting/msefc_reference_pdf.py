"""Generate MSEFC reference application PDF."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.common.models import DisputeCase
from src.reporting.pdf_base import build_header, draw_page_chrome, get_pdf_styles


def build_msefc_reference_pdf(dispute: DisputeCase) -> bytes:
    """Create MSEFC reference document PDF bytes."""
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=0.9 * inch,
        title="MSEFC Reference",
    )
    styles = get_pdf_styles()
    story: list = []

    build_header(
        story,
        "APPLICATION UNDER SECTION 18, MSMED ACT, 2006",
        f"Before the Micro and Small Enterprises Facilitation Council, {dispute.msefc_state}",
    )
    story.append(Paragraph(f"Case ID: {dispute.case_id}", styles["NyClause"]))
    story.append(Spacer(1, 0.08 * inch))

    party_table = Table(
        [
            ["Complainant (MSE)", f"{dispute.mse.enterprise_name} | Udyam: {dispute.mse.udyam_number}"],
            ["Respondent (Buyer)", f"{dispute.buyer.buyer_name} | GSTIN: {dispute.buyer.gstin or 'N/A'}"],
            ["Jurisdiction", f"MSEFC {dispute.msefc_state}"],
            ["Claim Amount", f"Rs {dispute.total_claim:,.2f} (Principal {dispute.total_principal:,.2f} + Interest {dispute.total_interest:,.2f})"],
        ],
        colWidths=[2.1 * inch, 3.9 * inch],
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
    story.append(Spacer(1, 0.12 * inch))

    story.append(Paragraph("Facts of the Dispute", styles["NyStrong"]))
    facts = [
        "1. The Complainant supplied goods/services to the Respondent against valid invoices.",
        "2. The Respondent failed to make payment within the agreed/statutory period under Section 15.",
        "3. Statutory interest under Section 16 has accrued on delayed payment.",
        f"4. Brief description: {dispute.dispute_description}",
    ]
    for row in facts:
        story.append(Paragraph(row, styles["NyClause"]))

    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Prayer", styles["NyStrong"]))
    prayers = [
        "a) Kindly register this reference under Section 18 of MSMED Act.",
        "b) Initiate conciliation proceedings between the parties.",
        "c) Upon failure of conciliation, proceed to arbitration as per law.",
        "d) Direct payment of principal, statutory interest, and costs.",
    ]
    for row in prayers:
        story.append(Paragraph(row, styles["NyClause"]))

    story.append(Spacer(1, 0.14 * inch))
    story.append(Paragraph("Verification", styles["NyStrong"]))
    story.append(
        Paragraph(
            "I/We hereby verify that the statements made above are true and correct to the best of my/our knowledge and belief.",
            styles["NyClause"],
        )
    )
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Authorized Signatory: ____________________", styles["NyClause"]))
    story.append(Paragraph(f"Place: {dispute.mse.state} | Date: {dispute.created_at.date().isoformat()}", styles["NyClause"]))

    doc.build(
        story,
        onFirstPage=lambda canvas, d: draw_page_chrome(canvas, d, watermark="COMPUTER GENERATED"),
        onLaterPages=lambda canvas, d: draw_page_chrome(canvas, d, watermark="COMPUTER GENERATED"),
    )
    return buf.getvalue()


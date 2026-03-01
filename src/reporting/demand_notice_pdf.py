"""Generate demand notice PDF documents."""

from __future__ import annotations

from datetime import date
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.common.models import DisputeCase
from src.reporting.pdf_base import build_header, draw_page_chrome, get_pdf_styles


def build_demand_notice_pdf(dispute: DisputeCase) -> bytes:
    """Build a professional demand notice PDF and return bytes."""
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=0.9 * inch,
        title="Demand Notice",
    )
    styles = get_pdf_styles()
    story: list = []

    build_header(story, "LEGAL NOTICE UNDER SECTION 15-16 MSMED ACT, 2006", f"Notice Date: {date.today().isoformat()}")

    party_table = Table(
        [
            ["To (Buyer)", f"{dispute.buyer.buyer_name}\n{dispute.buyer.address or 'Address as per records'}"],
            ["From (MSE)", f"{dispute.mse.enterprise_name}\nUdyam: {dispute.mse.udyam_number}"],
            ["Case Reference", dispute.case_id],
        ],
        colWidths=[1.8 * inch, 4.2 * inch],
    )
    party_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#D1D5DB")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F4F6")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(party_table)
    story.append(Spacer(1, 0.12 * inch))

    story.append(Paragraph("Outstanding Summary", styles["NyStrong"]))
    summary_table = Table(
        [
            ["Principal Outstanding", f"Rs {dispute.total_principal:,.2f}"],
            ["Statutory Interest (Section 16)", f"Rs {dispute.total_interest:,.2f}"],
            ["Total Claim", f"Rs {dispute.total_claim:,.2f}"],
        ],
        colWidths=[3.7 * inch, 2.3 * inch],
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#D1D5DB")),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#FFF8E1")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph("Invoice-wise Breakdown", styles["NyStrong"]))
    invoice_rows = [["Invoice", "Date", "Outstanding (Rs)", "Overdue Days"]]
    for inv in dispute.invoices:
        invoice_rows.append([inv.invoice_number, inv.invoice_date, f"{inv.amount_outstanding:,.2f}", str(inv.days_overdue)])
    invoice_table = Table(invoice_rows, colWidths=[1.3 * inch, 1.2 * inch, 1.8 * inch, 1.7 * inch])
    invoice_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#D1D5DB")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E2D4D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F9FAFB")]),
                ("ALIGN", (2, 1), (2, -1), "RIGHT"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(invoice_table)
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph("Legal Basis", styles["NyStrong"]))
    clauses = [
        "Section 15: Buyer must pay within agreed period (maximum 45 days from acceptance/deemed acceptance).",
        "Section 16: Delay attracts compound interest with monthly rests at 3x RBI bank rate.",
        "Section 17: Supplier is entitled to principal plus statutory interest.",
        "Section 18: Matter may be referred to MSEFC for conciliation/arbitration on non-payment.",
    ]
    for idx, clause in enumerate(clauses, start=1):
        story.append(Paragraph(f"{idx}. {clause}", styles["NyClause"]))

    deadline_box = Table(
        [[
            "FINAL DEADLINE: You are required to clear total dues within 7 days from receipt of this notice, "
            "failing which MSEFC proceedings will be initiated."
        ]],
        colWidths=[6.0 * inch],
    )
    deadline_box.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#F59E0B")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF7ED")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#9A3412")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(Spacer(1, 0.1 * inch))
    story.append(deadline_box)

    doc.build(
        story,
        onFirstPage=lambda canvas, d: draw_page_chrome(canvas, d, watermark="LEGAL NOTICE"),
        onLaterPages=lambda canvas, d: draw_page_chrome(canvas, d, watermark="LEGAL NOTICE"),
    )
    return buf.getvalue()


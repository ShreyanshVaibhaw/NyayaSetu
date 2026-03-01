"""Core dispute construction pipeline for VaadPatra."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

import config
from src.common.models import BuyerProfile, DisputeCase, Invoice
from src.vaadpatra.document_ocr import DocumentOCR


@dataclass
class DisputeBuilder:
    """Build fully-structured dispute cases from manual, OCR, or conversation input."""

    udyam_fetcher: object
    gst_validator: object
    interest_calc: object
    eligibility_checker: object
    llm_client: Optional[object] = None
    ocr_engine: Optional[DocumentOCR] = None

    @staticmethod
    def _parse_date(value: str) -> date:
        """Parse date from common UI/document formats."""
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Unsupported date format: {value}")

    @staticmethod
    def _to_ddmmyyyy(value: date) -> str:
        """Format a date in DD-MM-YYYY format used by invoice models."""
        return value.strftime("%d-%m-%Y")

    def _compute_due_date(self, acceptance_date: date, has_agreement: bool, agreed_days: Optional[int]) -> date:
        """Compute statutory due date based on Section 15 limits."""
        credit_days = config.DEFAULT_CREDIT_NO_AGREEMENT
        if has_agreement and agreed_days:
            credit_days = min(agreed_days, config.MAX_CREDIT_PERIOD_DAYS)
        return acceptance_date + timedelta(days=credit_days)

    def _safe_llm_description(self, mse_name: str, buyer_name: str, principal: float, total_interest: float) -> str:
        """Generate a concise narrative with LLM fallback."""
        if not self.llm_client:
            return (
                f"{mse_name} supplied goods/services to {buyer_name} and seeks recovery of outstanding "
                f"principal Rs {principal:.2f} plus statutory interest Rs {total_interest:.2f} under MSMED Act."
            )
        prompt = (
            "Draft a concise legal dispute description (2 sentences) for MSME delayed payment filing. "
            f"MSE: {mse_name}; Buyer: {buyer_name}; Principal: {principal:.2f}; Interest: {total_interest:.2f}"
        )
        return self.llm_client.generate(prompt=prompt).strip() or (
            f"{mse_name} seeks recovery from {buyer_name} for delayed payment under MSMED Act."
        )

    def build_dispute(
        self,
        udyam_number: str,
        buyer_info: Dict,
        invoices: List[Dict],
        has_agreement: bool = False,
        agreed_days: Optional[int] = None,
        uploaded_documents: Optional[List[str]] = None,
    ) -> DisputeCase:
        """Build complete dispute object ready for filing/export."""
        mse = self.udyam_fetcher.fetch_by_udyam_number(udyam_number)
        if mse is None:
            raise ValueError("Unable to fetch valid MSE profile for provided Udyam number.")

        gst_data = self.gst_validator.validate_gstin(buyer_info.get("gstin", ""))
        buyer_state = buyer_info.get("state") or gst_data.get("state") or mse.state

        first_invoice_date = self._parse_date(invoices[0]["invoice_date"]).isoformat()
        max_days_overdue = 0
        invoice_models: List[Invoice] = []
        total_principal = 0.0
        total_interest = 0.0
        today = date.today()

        for item in invoices:
            inv_date = self._parse_date(item["invoice_date"])
            acceptance = self._parse_date(item.get("acceptance_date", item.get("delivery_date", item["invoice_date"])))
            due_date = self._compute_due_date(acceptance, has_agreement, agreed_days)
            days_overdue = max(0, (today - due_date).days)
            max_days_overdue = max(max_days_overdue, days_overdue)

            invoice_amount = float(item.get("invoice_amount", item.get("amount", 0.0)))
            amount_paid = float(item.get("amount_paid", 0.0))
            outstanding = float(item.get("amount_outstanding", max(0.0, invoice_amount - amount_paid)))

            interest_result = self.interest_calc.calculate_interest(
                principal=outstanding,
                start_date=due_date.isoformat(),
                end_date=today.isoformat(),
            )

            invoice_models.append(
                Invoice(
                    invoice_number=item["invoice_number"],
                    invoice_date=self._to_ddmmyyyy(inv_date),
                    invoice_amount=invoice_amount,
                    goods_services_description=item.get("goods_services_description", "Goods/services supplied"),
                    delivery_date=item.get("delivery_date"),
                    acceptance_date=item.get("acceptance_date", self._to_ddmmyyyy(acceptance)),
                    po_number=item.get("po_number"),
                    payment_due_date=self._to_ddmmyyyy(due_date),
                    amount_paid=amount_paid,
                    amount_outstanding=outstanding,
                    days_overdue=days_overdue,
                )
            )
            total_principal += outstanding
            total_interest += interest_result.interest_amount

        eligibility = self.eligibility_checker.check_eligibility(
            udyam_date=mse.date_of_udyam,
            earliest_invoice_date=first_invoice_date,
            enterprise_type=mse.enterprise_type,
            days_overdue=max_days_overdue,
            major_activity=mse.major_activity,
            has_written_agreement=has_agreement,
            agreed_credit_days=agreed_days or 0,
        )
        if not eligibility["eligible"]:
            raise ValueError(f"Dispute is not eligible: {eligibility['reasons']}")

        buyer = BuyerProfile(
            buyer_name=buyer_info.get("buyer_name", buyer_info.get("name", "Unknown Buyer")),
            buyer_type=buyer_info.get("buyer_type", "Private Ltd"),
            gstin=buyer_info.get("gstin"),
            pan=buyer_info.get("pan"),
            state=buyer_state,
            district=buyer_info.get("district", "Unknown"),
            address=buyer_info.get("address", ""),
            contact_person=buyer_info.get("contact_person"),
            contact_email=buyer_info.get("contact_email"),
            contact_phone=buyer_info.get("contact_phone"),
            industry_sector=buyer_info.get("industry_sector"),
        )

        dispute_description = self._safe_llm_description(
            mse_name=mse.enterprise_name,
            buyer_name=buyer.buyer_name,
            principal=total_principal,
            total_interest=total_interest,
        )
        relief_sought = (
            "Direction to buyer to pay outstanding principal and compound interest under Sections 15 and 16 of MSMED Act."
        )

        return DisputeCase(
            case_id=f"NS-{uuid4().hex[:10].upper()}",
            mse=mse,
            buyer=buyer,
            invoices=invoice_models,
            total_principal=round(total_principal, 2),
            total_interest=round(total_interest, 2),
            total_claim=round(total_principal + total_interest, 2),
            has_written_agreement=has_agreement,
            agreed_credit_days=agreed_days,
            dispute_description=dispute_description,
            relief_sought=relief_sought,
            supporting_documents=uploaded_documents or [],
            filed_date=None,
            current_stage="Filed",
            msefc_state=mse.state,
            created_at=datetime.now(UTC),
        )

    def build_from_conversation(self, conversation_data: Dict) -> DisputeCase:
        """Build dispute from already extracted conversational entities."""
        return self.build_dispute(
            udyam_number=conversation_data["udyam_number"],
            buyer_info=conversation_data["buyer_info"],
            invoices=conversation_data["invoices"],
            has_agreement=conversation_data.get("has_agreement", False),
            agreed_days=conversation_data.get("agreed_days"),
            uploaded_documents=conversation_data.get("uploaded_documents", []),
        )

    def build_from_ocr(self, invoice_images: List[str], udyam_number: str, buyer_gstin: str) -> DisputeCase:
        """Run OCR extraction then construct a dispute case."""
        ocr_engine = self.ocr_engine or DocumentOCR(llm_client=self.llm_client)
        extracted = ocr_engine.batch_extract(invoice_images)
        invoices = []
        for idx, row in enumerate(extracted, start=1):
            invoices.append(
                {
                    "invoice_number": row.get("invoice_number") or f"INV-OCR-{idx:03d}",
                    "invoice_date": row.get("invoice_date") or "01-01-2026",
                    "invoice_amount": float(row.get("total_amount") or 0.0),
                    "goods_services_description": ", ".join(row.get("items", [])) or "OCR extracted invoice items",
                    "delivery_date": row.get("delivery_date"),
                    "acceptance_date": row.get("delivery_date") or "03-01-2026",
                    "po_number": row.get("po_reference"),
                    "amount_paid": 0.0,
                    "amount_outstanding": float(row.get("total_amount") or 0.0),
                }
            )

        buyer_info = {
            "buyer_name": extracted[0].get("buyer_name", "OCR Buyer") if extracted else "OCR Buyer",
            "buyer_type": "Private Ltd",
            "gstin": buyer_gstin,
            "state": self.gst_validator.extract_state_from_gst(buyer_gstin),
            "district": "Unknown",
            "address": "Address from OCR/Manual confirmation pending",
        }
        return self.build_dispute(
            udyam_number=udyam_number,
            buyer_info=buyer_info,
            invoices=invoices,
            has_agreement=True,
            agreed_days=45,
            uploaded_documents=invoice_images,
        )

    def generate_filing_summary(self, dispute: DisputeCase) -> str:
        """Create a concise summary for MSE review before filing."""
        return (
            f"Case {dispute.case_id}: {dispute.mse.enterprise_name} vs {dispute.buyer.buyer_name} | "
            f"Principal Rs {dispute.total_principal:.2f}, Interest Rs {dispute.total_interest:.2f}, "
            f"Total Claim Rs {dispute.total_claim:.2f}, Jurisdiction MSEFC {dispute.msefc_state}."
        )

    def export_odr_format(self, dispute: DisputeCase) -> Dict:
        """Export dispute in ODR-friendly serializable dictionary format."""
        return {
            "complainant_details": dispute.mse.model_dump(),
            "respondent_details": dispute.buyer.model_dump(),
            "invoice_details": [inv.model_dump() for inv in dispute.invoices],
            "dispute_details": {
                "total_principal": dispute.total_principal,
                "total_interest": dispute.total_interest,
                "total_claim": dispute.total_claim,
                "has_written_agreement": dispute.has_written_agreement,
                "agreed_credit_days": dispute.agreed_credit_days,
                "dispute_description": dispute.dispute_description,
                "relief_sought": dispute.relief_sought,
            },
            "jurisdiction": dispute.msefc_state,
            "stage": dispute.current_stage,
        }


"""Document gap analysis for dispute-filing completeness."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from src.common.models import DisputeCase


DOCUMENT_REQUIREMENTS: Dict[str, Dict[str, List[str]]] = {
    "delayed_payment_goods": {
        "mandatory": ["udyam_certificate", "invoice", "purchase_order_or_contract", "delivery_proof"],
        "recommended": ["payment_demand_letter", "correspondence", "bank_statement"],
        "optional": ["quality_inspection_report"],
    },
    "delayed_payment_services": {
        "mandatory": ["udyam_certificate", "invoice", "work_order_or_contract", "service_completion_proof"],
        "recommended": ["payment_demand_letter", "timesheets", "correspondence"],
        "optional": ["acceptance_certificate"],
    },
    "partial_payment": {
        "mandatory": ["udyam_certificate", "invoice", "purchase_order_or_contract", "bank_statement_showing_partial"],
        "recommended": ["payment_demand_letter", "receipt_of_partial_payment"],
        "optional": ["correspondence"],
    },
    "quality_dispute_payment_withheld": {
        "mandatory": ["udyam_certificate", "invoice", "delivery_proof", "quality_communication_records"],
        "recommended": ["inspection_report", "payment_demand_letter"],
        "optional": ["third_party_quality_certificate"],
    },
    "contractual_terms_violation": {
        "mandatory": ["udyam_certificate", "invoice", "signed_contract_or_po", "delivery_proof"],
        "recommended": ["payment_reminders", "bank_statement"],
        "optional": ["meeting_minutes"],
    },
    "payment_acknowledgment_missing": {
        "mandatory": ["udyam_certificate", "invoice", "delivery_proof_with_acknowledgment", "transport_or_ewaybill"],
        "recommended": ["correspondence", "payment_demand_letter"],
        "optional": ["witness_statement"],
    },
    "cross_invoice_dispute": {
        "mandatory": ["udyam_certificate", "invoice", "purchase_order_or_contract", "reconciliation_statement"],
        "recommended": ["email_thread", "payment_demand_letter"],
        "optional": ["revised_invoice_notes"],
    },
}


@dataclass
class DocumentChecker:
    """Assess filing document completeness and missing critical gaps."""

    @staticmethod
    def detect_document_type(filename_or_text: str) -> str:
        """Infer canonical document type from filename/text hints."""
        raw = (filename_or_text or "").lower()
        name = Path(raw).name
        if "udyam" in name or "certificate" in name:
            return "udyam_certificate"
        if "invoice" in name or "bill" in name:
            return "invoice"
        if "purchase" in name or "contract" in name or "po" in name:
            return "purchase_order_or_contract"
        if "challan" in name or "delivery" in name or "eway" in name:
            return "delivery_proof"
        if "bank" in name or "statement" in name:
            return "bank_statement"
        if "demand" in name or "notice" in name or "letter" in name:
            return "payment_demand_letter"
        if "email" in name or "mail" in name or "chat" in name:
            return "correspondence"
        if "inspection" in name or "quality" in name:
            return "quality_inspection_report"
        return "other"

    @staticmethod
    def _status_row(doc: str, uploaded_set: set[str], mandatory: bool) -> Dict:
        uploaded = doc in uploaded_set
        if uploaded:
            return {"doc": doc, "status": "uploaded", "icon": "✅", "severity": "good"}
        if mandatory:
            return {"doc": doc, "status": "missing", "icon": "❌", "severity": "critical"}
        return {"doc": doc, "status": "recommended_missing", "icon": "⚠️", "severity": "warning"}

    def check_documents(self, category: str, uploaded_docs: List[str], dispute: DisputeCase | None = None) -> Dict:
        """Return mandatory/recommended checklist with completeness and impact."""
        req = DOCUMENT_REQUIREMENTS.get(category, DOCUMENT_REQUIREMENTS["delayed_payment_goods"])
        detected = [self.detect_document_type(x) for x in uploaded_docs]
        if dispute is not None:
            detected += [self.detect_document_type(x.invoice_number) for x in dispute.invoices]
        detected.append("invoice")
        detected.append("udyam_certificate")
        uploaded_set = {d for d in detected if d != "other"}

        mandatory_rows = [self._status_row(doc, uploaded_set, mandatory=True) for doc in req["mandatory"]]
        recommended_rows = [self._status_row(doc, uploaded_set, mandatory=False) for doc in req["recommended"]]
        optional_rows = [self._status_row(doc, uploaded_set, mandatory=False) for doc in req["optional"]]

        mandatory_uploaded = sum(1 for row in mandatory_rows if row["status"] == "uploaded")
        recommended_uploaded = sum(1 for row in recommended_rows if row["status"] == "uploaded")
        mandatory_total = max(1, len(mandatory_rows))
        recommended_total = max(1, len(recommended_rows))
        completeness = (mandatory_uploaded / mandatory_total) * 0.8 + (recommended_uploaded / recommended_total) * 0.2
        missing_critical = [row["doc"] for row in mandatory_rows if row["status"] != "uploaded"]

        if missing_critical:
            impact = f"Your case strength drops by ~{min(35, 10 + 5 * len(missing_critical))}% without critical proof."
        else:
            impact = "Document set is strong for filing and negotiation leverage."

        return {
            "mandatory": mandatory_rows,
            "recommended": recommended_rows,
            "optional": optional_rows,
            "completeness_score": round(completeness, 4),
            "missing_critical": missing_critical,
            "strength_impact": impact,
            "detected_doc_types": sorted(uploaded_set),
        }

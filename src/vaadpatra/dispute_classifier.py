"""Dispute sub-category classification for MSME delayed payment cases."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List

import config


TAXONOMY: Dict[str, Dict[str, List[str] | str]] = {
    "delayed_payment_goods": {
        "label": "Delayed Payment - Goods",
        "sections": ["Section 15", "Section 16", "Section 17"],
        "keywords": ["goods", "material", "supply", "delivered", "invoice overdue"],
    },
    "delayed_payment_services": {
        "label": "Delayed Payment - Services",
        "sections": ["Section 15", "Section 16", "Section 17"],
        "keywords": ["service", "work order", "consulting", "maintenance", "services rendered"],
    },
    "partial_payment": {
        "label": "Partial Payment",
        "sections": ["Section 15", "Section 16", "Section 17"],
        "keywords": ["partial", "balance", "part payment", "paid partly"],
    },
    "quality_dispute_payment_withheld": {
        "label": "Payment Withheld for Quality Dispute",
        "sections": ["Section 15", "Section 16", "Section 18"],
        "keywords": ["quality", "defect", "rework", "rejected goods", "poor quality"],
    },
    "contractual_terms_violation": {
        "label": "Contractual Terms Violation",
        "sections": ["Section 15", "Section 16", "Section 18"],
        "keywords": ["agreed credit", "contract", "terms violated", "agreement breached"],
    },
    "payment_acknowledgment_missing": {
        "label": "Payment Acknowledgment Missing",
        "sections": ["Section 15", "Section 16", "Section 18"],
        "keywords": ["not received", "acknowledgment missing", "delivery denied", "denies receipt"],
    },
    "cross_invoice_dispute": {
        "label": "Cross Invoice / PO Mismatch",
        "sections": ["Section 15", "Section 16", "Section 18"],
        "keywords": ["po mismatch", "invoice mismatch", "rate mismatch", "quantity mismatch"],
    },
}


@dataclass
class DisputeClassifier:
    """Classify dispute into MSME delayed-payment sub-categories."""

    def _llm_classify(self, dispute_description: str, invoice_data: Dict, llm_client: object) -> Dict:
        prompt = f"""
You are classifying MSME delayed-payment dispute sub-categories in India.
Categories: {list(TAXONOMY.keys())}

Dispute description:
{dispute_description}

Invoice data:
{json.dumps(invoice_data, ensure_ascii=False)}

Return only JSON:
{{
  "category": "<one category from list>",
  "confidence": 0.0,
  "reasoning": "short reasoning",
  "applicable_sections": ["Section 15","Section 16"]
}}
"""
        payload = llm_client.generate_json(prompt=prompt) if hasattr(llm_client, "generate_json") else {}
        if isinstance(payload, dict) and payload.get("category") in TAXONOMY:
            return {
                "category": payload.get("category"),
                "confidence": float(payload.get("confidence", 0.75)),
                "reasoning": str(payload.get("reasoning", "Classified via LLM analysis.")),
                "applicable_sections": payload.get("applicable_sections") or TAXONOMY[payload["category"]]["sections"],
            }
        return {}

    def _rule_based(self, dispute_description: str, invoice_data: Dict) -> Dict:
        text = (dispute_description or "").lower()
        total = float(invoice_data.get("total_amount", invoice_data.get("total_claim", 0.0)) or 0.0)
        paid = float(invoice_data.get("amount_paid", 0.0) or 0.0)
        days_overdue = int(invoice_data.get("days_overdue", 0) or 0)
        has_agreement = bool(invoice_data.get("has_agreement", False))
        is_service = "service" in text or "consulting" in text

        if paid > 0 and paid < max(total, 1):
            category = "partial_payment"
            reason = "Partial payment pattern detected in invoice values."
        elif "quality" in text or "defect" in text or "rework" in text:
            category = "quality_dispute_payment_withheld"
            reason = "Buyer appears to withhold payment citing quality concerns."
        elif "not received" in text or "denies receipt" in text or "acknowledgment" in text:
            category = "payment_acknowledgment_missing"
            reason = "Dispute suggests delivery/acknowledgment contention."
        elif "mismatch" in text or "po" in text and "invoice" in text:
            category = "cross_invoice_dispute"
            reason = "PO and invoice mismatch indicators found."
        elif has_agreement and days_overdue > 45:
            category = "contractual_terms_violation"
            reason = "Overdue period exceeds contractual/statutory credit norms."
        elif is_service:
            category = "delayed_payment_services"
            reason = "Service-related delayed payment indicators detected."
        else:
            category = "delayed_payment_goods"
            reason = "Default overdue goods-supply delayed payment classification."

        confidence = 0.9 if category in {"partial_payment", "quality_dispute_payment_withheld"} else 0.78
        return {
            "category": category,
            "confidence": confidence,
            "reasoning": reason,
            "applicable_sections": TAXONOMY[category]["sections"],
        }

    def classify_dispute(self, dispute_description: str, invoice_data: Dict, llm_client: object | None = None) -> Dict:
        """Classify with LLM first, fallback to deterministic rules."""
        if config.APP_MODE != "DEMO" and llm_client is not None:
            llm_out = self._llm_classify(dispute_description, invoice_data, llm_client)
            if llm_out:
                return llm_out
        return self._rule_based(dispute_description, invoice_data)


"""Settlement and legal notice drafting utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

from src.common.models import DisputeCase, SettlementAgreement
from src.llm.prompt_templates import SETTLEMENT_DRAFT_TEMPLATE


@dataclass
class SettlementDrafter:
    """Draft demand notices, MSEFC references, and settlement agreements."""

    llm_client: object
    templates_path: str

    def __post_init__(self) -> None:
        self.templates = self._load_templates(self.templates_path)

    @staticmethod
    def _load_templates(path: str) -> Dict:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}

    def generate_installment_plan(
        self,
        total_amount: float,
        num_installments: int,
        start_date: str,
        plan_type: str = "equal_monthly",
    ) -> List[Dict]:
        """Generate schedule for lump-sum, equal, or front-loaded plan."""
        if num_installments <= 1 or plan_type == "lump_sum":
            return [
                {
                    "date": start_date,
                    "amount": round(total_amount, 2),
                    "description": "Lump-sum payment",
                }
            ]

        start = date.fromisoformat(start_date)
        schedule: List[Dict] = []

        if plan_type == "front_loaded":
            upfront = round(total_amount * 0.5, 2)
            remaining = total_amount - upfront
            schedule.append({"date": start.isoformat(), "amount": upfront, "description": "Upfront 50% payment"})
            monthly = round(remaining / max(1, num_installments - 1), 2)
            for idx in range(1, num_installments):
                due = start + timedelta(days=30 * idx)
                amt = monthly if idx < num_installments - 1 else round(total_amount - upfront - (monthly * (num_installments - 2)), 2)
                schedule.append({"date": due.isoformat(), "amount": amt, "description": f"Installment {idx+1}"})
            return schedule

        monthly = round(total_amount / num_installments, 2)
        for idx in range(num_installments):
            due = start + timedelta(days=30 * idx)
            amount = monthly if idx < num_installments - 1 else round(total_amount - (monthly * (num_installments - 1)), 2)
            schedule.append({"date": due.isoformat(), "amount": amount, "description": f"Installment {idx+1}"})
        return schedule

    def _fallback_terms(self, dispute: DisputeCase) -> List[str]:
        return [
            "WHEREAS, the Supplier provided goods/services and raised invoices for value received by Buyer.",
            "WHEREAS, delayed payment has triggered statutory consequences under Sections 15 and 16 of MSMED Act.",
            "The Parties agree this settlement resolves dues without prejudice to statutory rights under Section 18.",
            "If any installment defaults beyond 7 days, the full original claim revives with applicable statutory interest.",
            f"Governing law: MSMED Act, 2006; Jurisdiction: MSEFC {dispute.msefc_state}.",
            "Confidentiality: Parties shall keep settlement terms confidential except legal/regulatory disclosures.",
        ]

    def _llm_settlement_clauses(
        self,
        dispute: DisputeCase,
        settlement_amount: float,
        payment_schedule: List[Dict],
        interest_waived: float,
    ) -> List[str]:
        if not self.llm_client:
            return []
        prompt = SETTLEMENT_DRAFT_TEMPLATE.format(
            mse_name=dispute.mse.enterprise_name,
            udyam_number=dispute.mse.udyam_number,
            mse_address=dispute.mse.address,
            buyer_name=dispute.buyer.buyer_name,
            buyer_gstin=dispute.buyer.gstin or "N/A",
            buyer_address=dispute.buyer.address,
            total_claim=round(dispute.total_claim, 2),
            settlement_amount=round(settlement_amount, 2),
            payment_schedule=json.dumps(payment_schedule, ensure_ascii=False),
            interest_waived=round(interest_waived, 2),
        )
        try:
            output = self.llm_client.generate(prompt=prompt, temperature=0.2)
        except Exception:
            return []
        if not output:
            return []
        clauses = [line.strip(" -\t") for line in output.splitlines() if line.strip()]
        cleaned = [c for c in clauses if len(c) > 12]
        if len(cleaned) < 4:
            return []
        return cleaned[:18]

    def draft_settlement(
        self,
        dispute: DisputeCase,
        settlement_amount: float,
        payment_schedule: List[Dict],
        interest_waived: float = 0,
    ) -> SettlementAgreement:
        """Generate structured settlement agreement model."""
        llm_terms = self._llm_settlement_clauses(dispute, settlement_amount, payment_schedule, interest_waived)
        terms = llm_terms if llm_terms else self._fallback_terms(dispute)
        return SettlementAgreement(
            agreement_id=f"SET-{uuid4().hex[:10].upper()}",
            case_id=dispute.case_id,
            mse_name=dispute.mse.enterprise_name,
            buyer_name=dispute.buyer.buyer_name,
            settlement_amount=round(settlement_amount, 2),
            payment_schedule=payment_schedule,
            interest_waived=round(interest_waived, 2),
            terms_and_conditions=terms,
            generated_at=datetime.now(UTC),
        )

    def draft_settlement_agreement_text(self, agreement: SettlementAgreement, dispute: DisputeCase) -> str:
        """Return formatted legal-style text for UI preview."""
        lines = [
            "SETTLEMENT AGREEMENT",
            f"Agreement Ref: {agreement.agreement_id}",
            f"Date: {agreement.generated_at.date().isoformat()}",
            "",
            f"BETWEEN {agreement.mse_name} (Supplier/MSE) AND {agreement.buyer_name} (Buyer)",
            "",
            "WHEREAS clauses:",
            f"1. Supplier raised claim of Rs {dispute.total_claim:,.2f} under MSMED delayed-payment framework.",
            f"2. Parties agreed to settle for Rs {agreement.settlement_amount:,.2f}, waiving Rs {agreement.interest_waived:,.2f} interest.",
            "",
            "Payment Schedule:",
        ]
        for idx, row in enumerate(agreement.payment_schedule, start=1):
            lines.append(f"{idx}. {row.get('date')}: Rs {float(row.get('amount', 0)):,.2f} ({row.get('description', 'Payment')})")
        lines += ["", "Terms and Conditions:"]
        for idx, term in enumerate(agreement.terms_and_conditions, start=1):
            lines.append(f"{idx}. {term}")
        lines += [
            "",
            "Signatures:",
            "Supplier: _____________________",
            "Buyer: ________________________",
            "Witness 1: ____________________",
            "Witness 2: ____________________",
        ]
        return "\n".join(lines)

    def draft_demand_notice(self, dispute: DisputeCase) -> str:
        """Generate formal pre-litigation demand notice text."""
        invoice_refs = ", ".join(inv.invoice_number for inv in dispute.invoices)
        return (
            f"To,\n{dispute.buyer.buyer_name}\n\n"
            f"Subject: Demand Notice under MSMED Act, 2006\n\n"
            f"This is to notify that Rs {dispute.total_principal:,.2f} remains outstanding against invoices {invoice_refs}. "
            f"As per Section 15, payment was due within statutory credit period. Under Section 16, "
            f"compound interest with monthly rests is payable, currently calculated at Rs {dispute.total_interest:,.2f}. "
            f"Total due is Rs {dispute.total_claim:,.2f}. Kindly remit within 7 days from receipt of this notice, "
            f"failing which proceedings before MSEFC {dispute.msefc_state} shall be initiated under Section 18.\n\n"
            f"Regards,\n{dispute.mse.enterprise_name}"
        )

    def draft_msefc_reference(self, dispute: DisputeCase) -> str:
        """Draft formal Section 18 reference application content."""
        lines = [
            "Reference Application under Section 18, MSMED Act, 2006",
            f"Case ID: {dispute.case_id}",
            f"Complainant: {dispute.mse.enterprise_name} (Udyam: {dispute.mse.udyam_number})",
            f"Respondent: {dispute.buyer.buyer_name}",
            f"Jurisdiction: MSEFC {dispute.msefc_state}",
            f"Total Principal: Rs {dispute.total_principal:,.2f}",
            f"Total Interest (Section 16): Rs {dispute.total_interest:,.2f}",
            f"Total Claim: Rs {dispute.total_claim:,.2f}",
            "Relief sought: Recovery of principal and statutory compound interest with costs.",
            f"Facts: {dispute.dispute_description}",
            "Prayer: Kindly initiate conciliation and, upon failure, proceed to arbitration as per statute.",
        ]
        return "\n".join(lines)

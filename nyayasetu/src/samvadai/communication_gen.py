"""Negotiation communication generation with LLM + template fallback."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from src.common.models import DisputeCase
from src.llm.prompt_templates import NEGOTIATION_STRATEGY_TEMPLATE


@dataclass
class CommunicationGenerator:
    """Generate legally-grounded negotiation communication."""

    llm_client: object
    templates_path: str

    def __post_init__(self) -> None:
        self.templates = self._load_templates(self.templates_path)

    @staticmethod
    def _load_templates(path: str) -> Dict:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _template_fallback(message_type: str, context: Dict) -> str:
        if message_type == "initial_demand":
            return (
                f"Dear {context['buyer_name']}, an amount of Rs {context['total']:,} is overdue against invoice(s) "
                f"{context['invoice_numbers']}. As per Sections 15 and 16 of MSMED Act, kindly clear dues within "
                f"{context['deadline']} to avoid MSEFC escalation."
            )
        if message_type == "counter_offer":
            return (
                f"We note your response. To resolve amicably, we propose settlement at Rs {context['counter_amount']:,} "
                f"with immediate confirmation and time-bound payment plan."
            )
        if message_type == "escalation_warning":
            return (
                "Despite repeated reminders, payment remains unresolved. Unless settled within 7 days, we will proceed "
                "with Section 18 reference before the competent MSEFC."
            )
        return (
            f"Please settle the outstanding dues of Rs {context['total']:,} under MSMED Act Sections 15 and 16."
        )

    def generate_smart_message(
        self,
        message_type: str,
        dispute_context: Dict,
        round_number: int,
        strategy: str,
        llm_client: object | None,
        language: str = "en",
        previous_messages: List[Dict] | None = None,
        tactic_detected: str | None = None,
    ) -> str:
        """Generate contextual negotiation messages with legal framing."""
        previous_messages = previous_messages or []
        context = {
            "buyer_name": dispute_context.get("buyer_name", "Buyer"),
            "mse_name": dispute_context.get("mse_name", "MSE"),
            "total": float(dispute_context.get("total", 0.0)),
            "principal": float(dispute_context.get("principal", 0.0)),
            "interest": float(dispute_context.get("interest", 0.0)),
            "invoice_numbers": dispute_context.get("invoice_numbers", "N/A"),
            "days_overdue": int(dispute_context.get("days_overdue", 0)),
            "buyer_type": dispute_context.get("buyer_type", "Private Ltd"),
            "counter_amount": float(dispute_context.get("counter_amount", dispute_context.get("total", 0.0))),
            "deadline": dispute_context.get("deadline", "7 days"),
            "case_strength": dispute_context.get("case_strength", "moderate"),
            "settlement_prob": dispute_context.get("settlement_prob", 65.0),
            "expected_recovery": dispute_context.get("expected_recovery", 75.0),
            "buyer_position": dispute_context.get("buyer_position", "pending response"),
            "previous_offers": dispute_context.get("previous_offers", "N/A"),
        }
        llm = llm_client or self.llm_client
        if llm:
            try:
                base_prompt = NEGOTIATION_STRATEGY_TEMPLATE.format(**context, round_number=round_number)
                smart_prompt = (
                    f"{base_prompt}\n\n"
                    f"Generate a {message_type} communication in language={language}, strategy={strategy}, "
                    f"tactic_detected={tactic_detected or 'unknown'}. Keep it concise, professional, and legally grounded.\n"
                    f"Previous messages:\n{json.dumps(previous_messages[-6:], ensure_ascii=False)}\n"
                    "Return only the message text."
                )
                message = llm.generate(prompt=smart_prompt, temperature=0.15)
                if isinstance(message, str) and message.strip():
                    return message.strip()
            except Exception:
                pass

        fallback = self._template_fallback(message_type, context)
        if language == "hi":
            return (
                f"प्रिय {context['buyer_name']}, MSMED Act धारा 15 और 16 के अनुसार "
                f"₹{context['total']:,.0f} देय है। कृपया {context['deadline']} में भुगतान करें।"
            )
        return fallback

    def generate_message(self, dispute: DisputeCase, message_type: str, language: str = "en", **kwargs) -> str:
        """Backward-compatible wrapper for existing call sites."""
        context = {
            "buyer_name": dispute.buyer.buyer_name,
            "mse_name": dispute.mse.enterprise_name,
            "total": dispute.total_claim,
            "principal": dispute.total_principal,
            "interest": dispute.total_interest,
            "invoice_numbers": ", ".join(inv.invoice_number for inv in dispute.invoices),
            "days_overdue": max((inv.days_overdue for inv in dispute.invoices), default=0),
            "buyer_type": dispute.buyer.buyer_type,
            "counter_amount": kwargs.get("counter_amount", dispute.total_claim),
            "deadline": kwargs.get("deadline", "7 days"),
            "case_strength": kwargs.get("case_strength", "moderate"),
            "settlement_prob": kwargs.get("settlement_prob", 70),
            "expected_recovery": kwargs.get("expected_recovery", 75),
            "buyer_position": kwargs.get("buyer_position", "pending response"),
            "previous_offers": kwargs.get("previous_offers", "N/A"),
        }
        return self.generate_smart_message(
            message_type=message_type,
            dispute_context=context,
            round_number=int(kwargs.get("round_number", 1)),
            strategy=str(kwargs.get("strategy", "firm_demand")),
            llm_client=self.llm_client,
            language=language,
            previous_messages=kwargs.get("previous_messages", []),
            tactic_detected=kwargs.get("tactic_detected"),
        )

    def generate_sms(self, dispute: DisputeCase, message_type: str) -> str:
        """Generate short SMS notification (<=160 chars)."""
        sms = (
            f"NyayaSetu: {message_type.replace('_', ' ').title()} | Buyer {dispute.buyer.buyer_name} | "
            f"Claim Rs {dispute.total_claim:,.0f} under MSMED Act."
        )
        return sms[:160]


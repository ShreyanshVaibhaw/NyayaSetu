"""Negotiation orchestration logic for SamvadAI."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from uuid import uuid4

from src.common.models import CaseOutcomePrediction, DisputeCase, NegotiationState
from src.samvadai.communication_gen import CommunicationGenerator
from src.samvadai.offer_optimizer import OfferOptimizer
from src.samvadai.tactic_detector import TacticDetector


@dataclass
class NegotiationEngine:
    """Run round-based buyer negotiation with strategy adaptation."""

    llm_client: object
    prediction_model: object
    templates_path: str
    optimizer: OfferOptimizer = field(default_factory=OfferOptimizer)
    _context_store: Dict[str, Dict] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.templates = self._load_templates(self.templates_path)
        self.tactic_detector = TacticDetector(self.llm_client)
        self.message_gen = CommunicationGenerator(self.llm_client, self.templates_path)

    @staticmethod
    def _load_templates(path: str) -> Dict:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return {}

    def initialize_negotiation(self, dispute: DisputeCase, prediction: CaseOutcomePrediction) -> NegotiationState:
        """Start negotiation with strategy inferred from predicted recovery strength."""
        if prediction.predicted_recovery_percentage >= 80:
            strategy = "firm_demand"
        elif prediction.predicted_recovery_percentage >= 50:
            strategy = "gradual_concession"
        else:
            strategy = "principal_focus"

        opening_offer = round(dispute.total_principal + dispute.total_interest, 2)
        state = NegotiationState(
            negotiation_id=f"NEG-{uuid4().hex[:10].upper()}",
            case_id=dispute.case_id,
            round_number=1,
            mse_offer=opening_offer,
            buyer_counter=None,
            mse_strategy=strategy,
            messages=[],
            status="active",
            settlement_amount=None,
            settlement_terms=None,
        )
        self._context_store[state.negotiation_id] = {
            "claim": dispute.total_claim,
            "principal": dispute.total_principal,
            "interest": dispute.total_interest,
            "days": max((inv.days_overdue for inv in dispute.invoices), default=0),
            "buyer_type": dispute.buyer.buyer_type,
            "buyer_name": dispute.buyer.buyer_name,
            "mse_name": dispute.mse.enterprise_name,
            "invoice_numbers": ", ".join(inv.invoice_number for inv in dispute.invoices),
            "settlement_prob": round(prediction.settlement_probability * 100, 2),
            "expected_recovery": round(prediction.predicted_recovery_percentage, 2),
            "case_strength": "strong" if prediction.settlement_probability >= 0.75 else ("moderate" if prediction.settlement_probability >= 0.5 else "weak"),
            "previous_offers": [],
        }
        return state

    @staticmethod
    def _extract_amount(text: str) -> float:
        matches = []
        for token in text.replace("₹", " ").replace("rs", " ").replace("Rs", " ").split():
            stripped = token.strip().strip(",.")
            if stripped.replace(",", "").isdigit():
                matches.append(float(stripped.replace(",", "")))
        if not matches:
            return 0.0
        return max(matches)

    def generate_round(self, state: NegotiationState, buyer_response: str | None = None, language: str = "en") -> Dict:
        """Generate current round output and next recommended action."""
        ctx = self._context_store.get(state.negotiation_id, {})

        if state.round_number == 1 and not buyer_response:
            message = self.message_gen.generate_smart_message(
                message_type="initial_demand",
                dispute_context={
                    **ctx,
                    "total": state.mse_offer,
                    "deadline": "7 days",
                    "buyer_position": "opening demand",
                },
                round_number=state.round_number,
                strategy=state.mse_strategy,
                llm_client=self.llm_client,
                language=language,
                previous_messages=state.messages,
            )
            state.messages.append({"round": 1, "sender": "mse", "message": message, "offer": state.mse_offer})
            ctx.setdefault("previous_offers", []).append(state.mse_offer)
            return {
                "message": message,
                "offer_amount": state.mse_offer,
                "strategy": state.mse_strategy,
                "should_escalate": False,
                "sentiment_analysis": None,
            }

        tactic_data = self.tactic_detector.analyze_buyer_response(
            message=buyer_response or "",
            context=state,
            dispute_context=ctx,
        )
        state.messages.append(
            {
                "round": state.round_number,
                "sender": "buyer",
                "message": buyer_response or "",
                "tactic": tactic_data["tactic"],
                "sentiment_score": tactic_data.get("sentiment_score"),
                "cooperation_level": tactic_data.get("cooperation_level"),
                "aggression_level": tactic_data.get("aggression_level"),
            }
        )

        buyer_offer = self._extract_amount(buyer_response or "")
        state.buyer_counter = buyer_offer if buyer_offer > 0 else state.buyer_counter
        if buyer_offer > 0:
            ctx.setdefault("previous_offers", []).append(buyer_offer)

        case_strength = "strong" if state.mse_strategy == "firm_demand" else "moderate"
        optimized = self.optimizer.calculate_optimal_offer(
            principal=max(state.mse_offer * 0.8, state.mse_offer - 200000),
            interest=max(state.mse_offer * 0.2, 0),
            case_strength=case_strength,
            round_number=state.round_number + 1,
            buyer_type=str(ctx.get("buyer_type", "Private Ltd")),
        )

        next_offer = optimized["demand"]
        if buyer_offer > 0 and buyer_offer >= optimized["minimum_acceptable"]:
            state.status = "settled"
            state.settlement_amount = buyer_offer
            message = (
                f"Offer of Rs {buyer_offer:,.2f} accepted. Proceeding to settlement agreement."
            )
            state.messages.append({"round": state.round_number, "sender": "mse", "message": message, "offer": buyer_offer})
            return {
                "message": message,
                "offer_amount": buyer_offer,
                "strategy": "accept",
                "should_escalate": False,
                "sentiment_analysis": tactic_data,
            }

        counter_msg = self.message_gen.generate_smart_message(
            message_type="counter_offer",
            dispute_context={
                **ctx,
                "total": ctx.get("claim", state.mse_offer),
                "counter_amount": next_offer,
                "buyer_position": buyer_response or "pending response",
                "previous_offers": ctx.get("previous_offers", []),
            },
            round_number=state.round_number + 1,
            strategy=state.mse_strategy,
            llm_client=self.llm_client,
            language=language,
            previous_messages=state.messages,
            tactic_detected=tactic_data["tactic"],
        )

        state.round_number += 1
        state.mse_offer = next_offer
        state.messages.append({"round": state.round_number, "sender": "mse", "message": counter_msg, "offer": next_offer})
        ctx.setdefault("previous_offers", []).append(next_offer)

        escalate, reason = self.should_escalate(state, tactic_data=tactic_data)
        if escalate:
            state.status = "escalated"
            counter_msg = f"Negotiation closed. Escalating to MSEFC. Reason: {reason}"

        return {
            "message": counter_msg,
            "offer_amount": next_offer,
            "strategy": state.mse_strategy,
            "should_escalate": escalate,
            "sentiment_analysis": tactic_data,
        }

    def should_escalate(self, state: NegotiationState, tactic_data: Dict | None = None) -> Tuple[bool, str]:
        """Decide whether negotiation should be escalated to formal proceedings."""
        tactic_data = tactic_data or {}
        escalation_risk = float(tactic_data.get("escalation_risk", 0.0))
        tactic = tactic_data.get("tactic", "")
        if state.round_number >= 4 and state.status != "settled":
            return True, "Three or more rounds completed without acceptable progress."
        if tactic in {"ghosting", "threatening"}:
            return True, "Buyer behavior indicates non-cooperative risk."
        if escalation_risk >= 0.75:
            return True, "Sentiment trajectory indicates low settlement probability."
        return False, ""

    def get_sentiment_series(self, state: NegotiationState) -> List[Dict]:
        """Extract round-wise sentiment trajectory for visualization."""
        rows: List[Dict] = []
        for msg in state.messages:
            if msg.get("sender") == "buyer" and msg.get("sentiment_score") is not None:
                rows.append(
                    {
                        "round": int(msg.get("round", 0)),
                        "sentiment_score": float(msg.get("sentiment_score", 0.0)),
                        "tactic": msg.get("tactic", ""),
                    }
                )
        return rows

    def generate_negotiation_summary(self, state: NegotiationState) -> str:
        """Summarize negotiation history and current status."""
        return (
            f"Negotiation {state.negotiation_id} for case {state.case_id}: "
            f"{len(state.messages)} messages exchanged across {state.round_number} rounds. "
            f"Status: {state.status}. "
            f"{'Settlement at Rs ' + format(state.settlement_amount, ',.2f') if state.settlement_amount else 'No settlement yet.'}"
        )


"""Buyer tactic + sentiment analysis for negotiation flow."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict

import config
from src.common.models import NegotiationState


@dataclass
class TacticDetector:
    """Classify buyer response behavior with LLM + deterministic fallback."""

    llm_client: object | None = None

    @staticmethod
    def _empty_context() -> Dict:
        return {"claim": 0.0, "days": 0, "buyer_type": "Private Ltd"}

    def _analyze_keyword_fallback(self, message: str, context: NegotiationState) -> Dict:
        text = (message or "").lower().strip()

        tactic = "cooperative"
        confidence = 0.72
        intent = "settle"
        red_flags = []
        recommended = "Continue negotiation with measured concessions."
        good_faith = True

        if any(key in text for key in ["more time", "later", "next month", "need approval", "internal process"]):
            tactic = "stalling"
            confidence = 0.86
            intent = "delay"
            recommended = "Set a clear deadline and cite statutory payment obligations under Sections 15 and 16."
        elif any(key in text for key in ["wrong invoice", "not accepted", "quality issue", "defect"]):
            tactic = "disputing_amount"
            confidence = 0.83
            intent = "contest liability"
            recommended = "Request specific documented objections and signed quality records."
        elif any(
            key in text
            for key in [
                "stop business",
                "blacklist",
                "no future orders",
                "future orders",
                "threat",
                "legal action against you",
            ]
        ):
            tactic = "threatening"
            confidence = 0.91
            intent = "pressure supplier"
            recommended = "Preserve evidence, remain formal, and prepare escalation to MSEFC."
            red_flags.append("Coercive or retaliatory language detected.")
            good_faith = False
        elif text == "":
            tactic = "ghosting"
            confidence = 0.94
            intent = "avoid engagement"
            recommended = "Send final notice with 7-day deadline and trigger escalation protocol."
            red_flags.append("No substantive response.")
            good_faith = False
        elif any(key in text for key in ["can pay", "offer", "we propose", "settle at", "partial payment"]):
            tactic = "partial_offer"
            confidence = 0.84
            intent = "settle with discount"
            recommended = "Counter with principal-focused settlement and time-bound schedule."
        elif any(key in text for key in ["cash flow", "financial difficulty", "hardship", "funding issue"]):
            tactic = "genuine_hardship"
            confidence = 0.78
            intent = "seeking flexibility"
            recommended = "Offer installment structure with strict default clause."
        elif any(key in text for key in ["not our fault", "supplier delayed", "client has not paid us"]):
            tactic = "blame_shifting"
            confidence = 0.76
            intent = "deflect accountability"
            recommended = "Bring discussion back to contractual due date and delivery evidence."
        elif any(key in text for key in ["as discussed", "let's close", "agreed", "accepted"]):
            tactic = "cooperative"
            confidence = 0.9
            intent = "close settlement"
            recommended = "Proceed to settlement drafting and payment schedule confirmation."

        sentiment = {
            "cooperative": 0.65,
            "partial_offer": 0.25,
            "genuine_hardship": 0.05,
            "stalling": -0.25,
            "disputing_amount": -0.35,
            "blame_shifting": -0.45,
            "threatening": -0.85,
            "ghosting": -0.7,
            "deflecting": -0.4,
        }.get(tactic, 0.0)
        aggression = max(0.0, min(1.0, (1 - sentiment) / 2))
        cooperation = max(0.0, min(1.0, (sentiment + 1) / 2))
        escalation_risk = max(0.05, min(0.95, 1 - cooperation + (0.2 if tactic in {"threatening", "ghosting"} else 0.0)))

        emotion_map = {
            "cooperative": ["willingness"],
            "partial_offer": ["anxiety", "willingness"],
            "genuine_hardship": ["anxiety"],
            "stalling": ["indifference"],
            "disputing_amount": ["frustration"],
            "blame_shifting": ["frustration", "indifference"],
            "threatening": ["anger"],
            "ghosting": ["indifference"],
        }

        return {
            "tactic": tactic,
            "confidence": round(confidence, 3),
            "intent": intent,
            "buyer_intent": intent,
            "recommended_response": recommended,
            "red_flags": red_flags,
            "good_faith": good_faith,
            "is_acting_in_good_faith": good_faith,
            "round_number": context.round_number,
            "sentiment_score": round(float(sentiment), 3),
            "emotions": emotion_map.get(tactic, ["indifference"]),
            "aggression_level": round(float(aggression), 3),
            "cooperation_level": round(float(cooperation), 3),
            "escalation_risk": round(float(escalation_risk), 3),
            "tone_description": "cooperative and practical" if sentiment > 0.2 else "guarded or evasive",
        }

    def analyze_with_llm(self, buyer_text: str, round_number: int, dispute_context: Dict) -> Dict:
        """Use LLM to infer tactic and sentiment for a buyer message."""
        if not self.llm_client:
            return {}
        ctx = self._empty_context()
        ctx.update(dispute_context or {})
        prompt = f"""
You are an expert negotiation analyst for MSME delayed payment disputes in India.

Analyze this buyer's response in Round {round_number} of negotiation:
\"{buyer_text}\"

Dispute context: Claim amount ₹{ctx['claim']}, overdue {ctx['days']} days, buyer type: {ctx['buyer_type']}

Return ONLY valid JSON:
{{
  "tactic": one of ["stalling", "disputing_amount", "threatening", "ghosting", "partial_offer", "genuine_hardship", "cooperative", "deflecting", "blame_shifting"],
  "sentiment_score": float from -1.0 to 1.0,
  "emotions": ["frustration","anger","anxiety","indifference","willingness","guilt"],
  "aggression_level": float 0.0 to 1.0,
  "cooperation_level": float 0.0 to 1.0,
  "good_faith": boolean,
  "intent": "brief intent",
  "red_flags": ["list"],
  "confidence": float 0.0 to 1.0,
  "recommended_response": "specific strategy",
  "escalation_risk": float 0.0 to 1.0,
  "tone_description": "tone descriptor"
}}
"""
        try:
            payload = self.llm_client.generate_json(prompt=prompt)
        except Exception:
            return {}
        if not isinstance(payload, dict):
            return {}
        required = {
            "tactic",
            "sentiment_score",
            "emotions",
            "aggression_level",
            "cooperation_level",
            "good_faith",
            "intent",
            "red_flags",
            "confidence",
            "recommended_response",
            "escalation_risk",
            "tone_description",
        }
        if not required.issubset(payload.keys()):
            return {}
        payload["buyer_intent"] = payload.get("intent", "")
        payload["is_acting_in_good_faith"] = bool(payload.get("good_faith", False))
        return payload

    def analyze_buyer_response(self, message: str, context: NegotiationState, dispute_context: Dict | None = None) -> Dict:
        """Analyze response with LLM if available, otherwise deterministic fallback."""
        if config.APP_MODE == "DEMO":
            data = self._analyze_keyword_fallback(message, context)
            # Demo mode enhancement: deterministic round-based drift.
            drift = ((context.round_number % 3) - 1) * 0.08
            data["sentiment_score"] = round(max(-1.0, min(1.0, data["sentiment_score"] + drift)), 3)
            data["cooperation_level"] = round(max(0.0, min(1.0, data["cooperation_level"] - drift / 2)), 3)
            data["aggression_level"] = round(max(0.0, min(1.0, 1 - data["cooperation_level"])), 3)
            return data

        llm_out = self.analyze_with_llm(
            buyer_text=message,
            round_number=context.round_number,
            dispute_context=dispute_context or self._empty_context(),
        )
        if llm_out:
            return llm_out
        return self._analyze_keyword_fallback(message, context)

"""AI-assisted buyer response simulation for negotiation demos."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import config


@dataclass
class BuyerSimulator:
    """Simulate buyer responses across behavior profiles."""

    llm_client: object | None = None

    _demo_sequences = {
        "cooperative": [
            "We acknowledge the dues. We can release Rs 350000 this week and close the balance quickly.",
            "We can improve and offer Rs 400000 if you waive part interest.",
            "Agreed. We accept Rs 410000 and will sign settlement.",
        ],
        "stalling": [
            "Our finance team needs more time and internal approval.",
            "We are still reconciling invoice records, please wait two weeks.",
            "Can we revisit next month? Cash release is pending.",
        ],
        "aggressive": [
            "Your claim is inflated and we reject the interest amount.",
            "If you escalate, we may stop future orders with your firm.",
            "Offer Rs 280000 final, take it or proceed legally.",
        ],
        "hardship": [
            "We are facing temporary cash-flow stress due to delayed receivables.",
            "Can we settle in installments? We can pay Rs 250000 now.",
            "We can increase to Rs 370000 over two months.",
        ],
        "ghosting": ["", "", ""],
    }

    def _llm_simulation(self, dispute: Dict, round_number: int, mse_offer: float, profile: str) -> str:
        if not self.llm_client:
            return ""
        prompt = f"""
You are simulating a buyer in MSME delayed-payment negotiation.
Profile: {profile}
Round: {round_number}
Current MSE offer: ₹{mse_offer}
Dispute context: {dispute}

Generate one realistic buyer response in Indian business tone.
Requirements:
- Keep numeric counter-offer realistic relative to current demand.
- Include occasional Hindi-English mix if natural.
- Avoid extra explanation, return only buyer response text.
"""
        try:
            text = self.llm_client.generate(prompt=prompt, temperature=0.35)
            return text.strip()
        except Exception:
            return ""

    def simulate_response(self, dispute: Dict, round_number: int, mse_offer: float, buyer_profile: str) -> str:
        """Generate buyer response for selected profile."""
        profile = (buyer_profile or "cooperative").strip().lower()
        if profile not in self._demo_sequences:
            profile = "cooperative"
        if config.APP_MODE == "DEMO":
            sequence = self._demo_sequences[profile]
            return sequence[min(len(sequence) - 1, max(0, round_number - 1))]

        llm_text = self._llm_simulation(dispute=dispute, round_number=round_number, mse_offer=mse_offer, profile=profile)
        if llm_text:
            return llm_text
        sequence = self._demo_sequences[profile]
        return sequence[min(len(sequence) - 1, max(0, round_number - 1))]


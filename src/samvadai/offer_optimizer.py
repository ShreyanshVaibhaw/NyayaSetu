"""Offer optimization rules for settlement rounds."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class OfferOptimizer:
    """Calculate round-wise offer amounts and concession bounds."""

    def calculate_optimal_offer(
        self,
        principal: float,
        interest: float,
        case_strength: str,
        round_number: int,
        buyer_type: str,
    ) -> Dict:
        """Compute recommended demand and floor for current round."""
        full_claim = principal + interest
        if round_number <= 1:
            demand = full_claim
        elif round_number == 2:
            demand = max(principal, full_claim - (0.35 * interest))
        elif round_number == 3:
            demand = max(principal, principal + (0.5 * interest))
        else:
            demand = max(principal, principal + (0.25 * interest))

        if case_strength == "strong":
            minimum = max(principal * 0.95, principal + interest * 0.2)
        elif case_strength == "moderate":
            minimum = max(principal * 0.9, principal)
        else:
            minimum = principal * 0.8

        if buyer_type in {"Central Govt", "State Govt", "PSU"}:
            minimum *= 1.02

        minimum = min(minimum, demand)
        concession = full_claim - demand
        return {
            "demand": round(demand, 2),
            "minimum_acceptable": round(minimum, 2),
            "concession_from_last": round(concession, 2),
            "justification": f"Round {round_number} strategy with {case_strength} case and {buyer_type} buyer profile.",
        }

    def calculate_settlement_value(self, principal: float, interest: float, resolution_days: int) -> float:
        """Discount delayed recovery to present-value settlement estimate."""
        full_claim = principal + interest
        annual_discount = 0.15
        time_factor = resolution_days / 365.0
        discounted = full_claim / ((1 + annual_discount) ** time_factor)
        return round(max(principal * 0.8, discounted), 2)

"""Timeline estimation for dispute resolution stages."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from src.common.models import DisputeCase


@dataclass
class TimelineEstimator:
    """Estimate optimistic/expected/pessimistic timelines for resolution."""

    msefc_data_path: str

    def __post_init__(self) -> None:
        self.msefc_data = self._load_msefc(self.msefc_data_path)

    @staticmethod
    def _load_msefc(path: str) -> Dict[str, Dict]:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        index: Dict[str, Dict] = {}
        for row in payload:
            index[row["state"]] = row
        return index

    def estimate_timeline(self, dispute: DisputeCase, strategy: str) -> Dict:
        """Estimate total timeline with stage-wise split."""
        state_info = self.msefc_data.get(dispute.msefc_state, {})
        base_state_days = int(state_info.get("avg_resolution_days", 95))

        unp_days = 20 if strategy == "negotiate" else 30
        conciliation_days = 35
        arbitration_days = 55

        if dispute.buyer.buyer_type in {"PSU", "Central Govt", "State Govt"}:
            unp_days += 8
            arbitration_days += 10
        if dispute.total_claim > 1000000:
            conciliation_days += 10
            arbitration_days += 15
        if dispute.buyer.state != dispute.mse.state:
            unp_days += 6
            conciliation_days += 8

        expected = max(base_state_days, unp_days + conciliation_days + arbitration_days)
        optimistic = max(30, int(expected * 0.75))
        pessimistic = int(expected * 1.4)

        return {
            "optimistic": optimistic,
            "expected": expected,
            "pessimistic": pessimistic,
            "stage_breakdown": {
                "unp": unp_days,
                "conciliation": conciliation_days,
                "arbitration": arbitration_days,
            },
            "state_reference_days": base_state_days,
        }

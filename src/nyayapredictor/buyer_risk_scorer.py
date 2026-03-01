"""Buyer risk scoring for delayed payment propensity."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import pandas as pd

from src.common.models import BuyerRiskScore


@dataclass
class BuyerRiskScorer:
    """Estimate buyer payment risk using historical behavior features."""

    buyer_data_path: str = "data/synthetic/buyer_profiles.csv"

    def __post_init__(self) -> None:
        self.buyer_history = self._load_buyer_data(self.buyer_data_path)

    @staticmethod
    def _load_buyer_data(path: str) -> pd.DataFrame:
        source = Path(path)
        if source.exists():
            try:
                return pd.read_csv(source)
            except Exception:
                pass
        return pd.DataFrame(columns=["buyer_gstin", "buyer_name", "risk_score"])

    @staticmethod
    def _categorize(score: float) -> str:
        if score <= 25:
            return "Low"
        if score <= 50:
            return "Medium"
        if score <= 75:
            return "High"
        return "Critical"

    def score_buyer(self, buyer_gstin: str, buyer_name: str, buyer_type: str) -> BuyerRiskScore:
        """Compute buyer risk score and explanatory factors."""
        factors = []
        base = 42.0

        if buyer_type in {"Central Govt", "State Govt"}:
            base -= 12
            factors.append("Government entity generally has lower default risk.")
        elif buyer_type == "PSU":
            base -= 8
            factors.append("PSU payment reliability is moderate to high, though often delayed.")
        elif buyer_type == "Proprietorship":
            base += 12
            factors.append("Proprietorship buyers show higher payment variance.")
        elif buyer_type == "Private Ltd":
            base += 4
            factors.append("Private entities may negotiate aggressively on delayed dues.")

        record = self.buyer_history.loc[self.buyer_history.get("buyer_gstin", pd.Series(dtype=str)) == buyer_gstin]
        if not record.empty:
            row = record.iloc[0]
            history_score = float(row.get("risk_score", base))
            past_disputes = int(row.get("past_disputes_count", max(1, int(history_score / 10))))
            avg_delay = int(row.get("avg_payment_delay_days", 45 + int(history_score)))
            total_outstanding = float(row.get("total_outstanding_to_mses", max(0.0, history_score * 100000)))
            gst_status = str(row.get("gst_compliance_status", "Compliant"))
            base = (base * 0.5) + (history_score * 0.5)
            factors.append("Historical dispute data exists for this buyer.")
        else:
            past_disputes = 1 if buyer_type in {"Central Govt", "State Govt", "PSU"} else 3
            avg_delay = 55 if buyer_type in {"PSU", "Central Govt", "State Govt"} else 78
            total_outstanding = float((past_disputes * 120000) + (avg_delay * 1500))
            gst_status = "Likely Compliant" if buyer_type in {"Central Govt", "State Govt", "PSU"} else "Unknown"
            factors.append("No direct history found; score derived from buyer type priors.")

        score = float(max(0, min(100, round(base + (past_disputes * 2) + ((avg_delay - 45) * 0.3), 2))))
        category = self._categorize(score)
        if score >= 70:
            factors.append("High expected delay risk; push tighter settlement deadlines.")
        elif score <= 30:
            factors.append("Relatively lower risk profile for voluntary settlement.")

        return BuyerRiskScore(
            buyer_gstin=buyer_gstin,
            buyer_name=buyer_name,
            risk_score=score,
            risk_category=category,  # type: ignore[arg-type]
            past_disputes_count=past_disputes,
            avg_payment_delay_days=avg_delay,
            total_outstanding_to_mses=round(total_outstanding, 2),
            gst_compliance_status=gst_status,
            factors=factors,
        )

    def get_buyer_report(self, buyer_gstin: str) -> Dict:
        """Return detailed report payload for dashboard display."""
        record = self.buyer_history.loc[self.buyer_history.get("buyer_gstin", pd.Series(dtype=str)) == buyer_gstin]
        if record.empty:
            return {"buyer_gstin": buyer_gstin, "found": False, "history": []}
        return {"buyer_gstin": buyer_gstin, "found": True, "history": record.to_dict(orient="records")}

"""Repeat-offender buyer analytics for risk warnings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd
import plotly.graph_objects as go


@dataclass
class BuyerBlacklist:
    """Identify and present high-risk repeat offender buyers."""

    disputes_path: str
    buyer_profiles_path: str

    def __post_init__(self) -> None:
        self.disputes = pd.read_csv(self.disputes_path)
        self.buyers = pd.read_csv(self.buyer_profiles_path)

    def get_repeat_offenders(self, min_disputes: int = 3) -> pd.DataFrame:
        """Buyers with dispute count above threshold."""
        agg = self.disputes.groupby(["buyer_gstin", "buyer_name"], as_index=False).agg(
            dispute_count=("case_id", "count"),
            total_outstanding=("dispute_amount", "sum"),
            avg_overdue=("days_overdue", "mean"),
        )
        return agg.loc[agg["dispute_count"] >= min_disputes].sort_values(
            ["dispute_count", "total_outstanding"], ascending=False
        )

    def get_blacklist_table(self) -> go.Figure:
        """Top 20 buyers by outstanding amount and dispute frequency."""
        offenders = self.get_repeat_offenders(min_disputes=3).head(20)
        return go.Figure(
            data=[
                go.Table(
                    header=dict(values=["Buyer GSTIN", "Buyer Name", "Disputes", "Outstanding", "Avg Overdue"]),
                    cells=dict(
                        values=[
                            offenders["buyer_gstin"],
                            offenders["buyer_name"],
                            offenders["dispute_count"],
                            offenders["total_outstanding"].round(2),
                            offenders["avg_overdue"].round(1),
                        ]
                    ),
                )
            ]
        )

    def check_buyer(self, buyer_gstin: str) -> Dict:
        """Return quick risk warning for one buyer GSTIN."""
        subset = self.disputes.loc[self.disputes["buyer_gstin"] == buyer_gstin]
        if subset.empty:
            return {"buyer_gstin": buyer_gstin, "is_offender": False, "message": "No known disputes found."}
        disputes = int(subset["case_id"].count())
        total = float(subset["dispute_amount"].sum())
        avg_overdue = float(subset["days_overdue"].mean())
        return {
            "buyer_gstin": buyer_gstin,
            "is_offender": disputes >= 3,
            "disputes": disputes,
            "total_outstanding": round(total, 2),
            "avg_overdue_days": round(avg_overdue, 1),
            "message": "Buyer appears on repeat-offender watchlist." if disputes >= 3 else "Buyer has limited dispute history.",
        }

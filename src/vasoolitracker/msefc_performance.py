"""MSEFC performance analytics visualizations."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


@dataclass
class MSEFCPerformance:
    """Rank and analyze state-level MSEFC outcomes."""

    state_pendency_path: str
    disputes_path: str

    def __post_init__(self) -> None:
        self.pendency = pd.read_csv(self.state_pendency_path)
        self.disputes = pd.read_csv(self.disputes_path)

    def get_msefc_ranking(self) -> go.Figure:
        """Rank states by disposal, recovery, and speed."""
        df = self.pendency.copy()
        df["score"] = (
            (df["disposal_rate"] * 0.4)
            + (df["recovery_rate"] * 0.4)
            + ((100 - df["avg_resolution_days"]).clip(lower=0) * 0.2)
        )
        df = df.sort_values("score", ascending=False)
        return px.bar(df, x="state", y="score", title="MSEFC Composite Performance Score")

    def get_pendency_analysis(self) -> go.Figure:
        """Compare pending vs disposed by state."""
        return px.bar(
            self.pendency,
            x="state",
            y=["pending", "disposed"],
            barmode="group",
            title="State-wise Pendency vs Disposal",
        )

    def get_90_day_compliance(self) -> go.Figure:
        """Statutory 90-day disposal compliance by state."""
        return px.bar(
            self.pendency.sort_values("compliance_90_day_pct", ascending=False),
            x="state",
            y="compliance_90_day_pct",
            title="90-Day Compliance by State (%)",
        )

"""Dispute analytics and plot generation for VasooliTracker."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


@dataclass
class DisputeAnalytics:
    """Compute KPIs and charts for dispute outcomes."""

    disputes_path: str

    def __post_init__(self) -> None:
        self.data = pd.read_csv(self.disputes_path)

    def get_overview_metrics(self) -> Dict:
        """Return top-level dashboard metrics."""
        total_disputes = int(len(self.data))
        total_amount_disputed = float(self.data["dispute_amount"].sum())
        total_recovered = float(self.data["recovered_amount"].sum())
        recovery_rate = (total_recovered / total_amount_disputed * 100.0) if total_amount_disputed else 0.0
        avg_resolution_days = int(self.data["resolution_days"].mean()) if total_disputes else 0
        return {
            "total_disputes": total_disputes,
            "total_amount_disputed": round(total_amount_disputed, 2),
            "total_recovered": round(total_recovered, 2),
            "recovery_rate": round(recovery_rate, 2),
            "avg_resolution_days": avg_resolution_days,
        }

    def get_stage_funnel(self) -> go.Figure:
        """Build stage funnel chart."""
        order = ["Filed", "UNP_Initiated", "UNP_Settled", "MSEFC_Referred", "Conciliation", "Arbitration", "Award_Passed", "Recovered"]
        counts = [int((self.data["stage"] == stage).sum()) for stage in order]
        return go.Figure(go.Funnel(y=order, x=counts))

    def get_monthly_trend(self) -> go.Figure:
        """Line chart of monthly filings and recoveries."""
        monthly = self.data.groupby("month", as_index=False).agg(
            filed=("case_id", "count"),
            resolved=("recovery_percentage", lambda s: int((s >= 60).sum())),
            recovered_amount=("recovered_amount", "sum"),
        )
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly["month"], y=monthly["filed"], mode="lines+markers", name="Filed"))
        fig.add_trace(go.Scatter(x=monthly["month"], y=monthly["resolved"], mode="lines+markers", name="Resolved"))
        fig.add_trace(go.Scatter(x=monthly["month"], y=monthly["recovered_amount"], mode="lines+markers", name="Recovered Amount"))
        return fig

    def get_amount_distribution(self) -> go.Figure:
        """Histogram with dispute amount spread."""
        return px.histogram(self.data, x="dispute_amount", nbins=40, title="Dispute Amount Distribution")

    def get_resolution_time_analysis(self) -> go.Figure:
        """Resolution day distribution by buyer type."""
        return px.box(
            self.data,
            x="buyer_type",
            y="resolution_days",
            color="stage",
            title="Resolution Days by Buyer Type and Stage",
        )

    def get_sector_breakdown(self) -> go.Figure:
        """Pie chart by sector."""
        agg = self.data.groupby("sector", as_index=False).agg(count=("case_id", "count"))
        return px.pie(agg, names="sector", values="count", title="Disputes by Sector")

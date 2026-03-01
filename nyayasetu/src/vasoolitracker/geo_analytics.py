"""Geospatial analytics for delayed payment concentration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict

import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


@dataclass
class GeoAnalytics:
    """Build map-based and state comparison analytics."""

    disputes_path: str
    state_data_path: str

    def __post_init__(self) -> None:
        self.disputes = pd.read_csv(self.disputes_path)
        self.states = self._load_states(self.state_data_path)

    @staticmethod
    def _load_states(path: str) -> Dict:
        payload = json.loads(open(path, "r", encoding="utf-8").read())
        index = {}
        for row in payload:
            districts = row.get("districts", [])
            if districts:
                index[row["state"]] = {
                    "lat": districts[0]["lat"],
                    "lon": districts[0]["lon"],
                    "district": districts[0]["name"],
                }
        return index

    def get_state_heatmap(self) -> folium.Map:
        """Create state-wise amount heat bubble map."""
        grouped = self.disputes.groupby("state", as_index=False).agg(
            total_disputes=("case_id", "count"),
            total_amount=("dispute_amount", "sum"),
            recovery_rate=("recovery_percentage", "mean"),
        )
        fmap = folium.Map(location=[22.5, 79.0], zoom_start=5, tiles="cartodbpositron")
        for _, row in grouped.iterrows():
            loc = self.states.get(row["state"])
            if not loc:
                continue
            folium.CircleMarker(
                location=[loc["lat"], loc["lon"]],
                radius=max(4, min(20, row["total_disputes"] / 150)),
                color="#C0392B",
                fill=True,
                fill_opacity=0.7,
                popup=(
                    f"{row['state']}<br>Disputes: {int(row['total_disputes'])}<br>"
                    f"Amount: Rs {row['total_amount']:,.0f}<br>"
                    f"Recovery: {row['recovery_rate']:.1f}%"
                ),
            ).add_to(fmap)
        return fmap

    def get_delayed_payment_hotspots(self) -> folium.Map:
        """Bubble map for worst delayed-payment states/districts."""
        grouped = self.disputes.groupby("state", as_index=False).agg(
            avg_overdue=("days_overdue", "mean"),
            total_amount=("dispute_amount", "sum"),
        )
        grouped = grouped.sort_values("total_amount", ascending=False).head(15)
        fmap = folium.Map(location=[22.5, 79.0], zoom_start=5, tiles="cartodbpositron")
        for _, row in grouped.iterrows():
            loc = self.states.get(row["state"])
            if not loc:
                continue
            folium.Circle(
                location=[loc["lat"], loc["lon"]],
                radius=float(row["total_amount"] / 500),
                color="#1B2A4A",
                fill=True,
                fill_opacity=0.25,
                popup=(
                    f"{row['state']} hotspot<br>Avg overdue: {row['avg_overdue']:.0f} days<br>"
                    f"Amount: Rs {row['total_amount']:,.0f}"
                ),
            ).add_to(fmap)
        return fmap

    def get_state_comparison(self) -> go.Figure:
        """State recovery rate and resolution-days comparison."""
        grouped = self.disputes.groupby("state", as_index=False).agg(
            recovery_rate=("recovery_percentage", "mean"),
            avg_resolution_days=("resolution_days", "mean"),
        )
        grouped = grouped.sort_values("recovery_rate", ascending=False).head(15)
        return px.bar(
            grouped,
            x="state",
            y=["recovery_rate", "avg_resolution_days"],
            barmode="group",
            title="State Comparison: Recovery vs Resolution Time",
        )

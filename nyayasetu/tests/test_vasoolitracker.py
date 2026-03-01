"""Tests for VasooliTracker analytics and synthetic data generation."""

from __future__ import annotations

from scripts.generate_synthetic_data import (
    generate_buyer_profiles,
    generate_case_outcomes,
    generate_disputes,
    generate_recovery_funnel,
    generate_state_pendency,
)
from src.vasoolitracker.buyer_blacklist import BuyerBlacklist
from src.vasoolitracker.dispute_analytics import DisputeAnalytics
from src.vasoolitracker.geo_analytics import GeoAnalytics
from src.vasoolitracker.msefc_performance import MSEFCPerformance


def test_generate_all_synthetic_data() -> None:
    disputes = generate_disputes(5000)
    outcomes = generate_case_outcomes(5000)
    buyers = generate_buyer_profiles(500)
    funnel = generate_recovery_funnel()
    state = generate_state_pendency()

    assert len(disputes) == 5000
    assert len(outcomes) == 5000
    assert len(buyers) == 500
    assert len(funnel) == 12
    assert len(state) >= 10


def test_dispute_analytics_metrics_and_charts() -> None:
    analytics = DisputeAnalytics("data/synthetic/disputes.csv")
    metrics = analytics.get_overview_metrics()
    assert metrics["total_disputes"] == 5000
    assert metrics["total_amount_disputed"] > 0
    assert metrics["recovery_rate"] >= 0

    assert analytics.get_stage_funnel() is not None
    assert analytics.get_monthly_trend() is not None
    assert analytics.get_amount_distribution() is not None
    assert analytics.get_resolution_time_analysis() is not None
    assert analytics.get_sector_breakdown() is not None


def test_geo_analytics_render() -> None:
    geo = GeoAnalytics("data/synthetic/disputes.csv", "data/msme/state_districts.json")
    assert geo.get_state_heatmap() is not None
    assert geo.get_delayed_payment_hotspots() is not None
    assert geo.get_state_comparison() is not None


def test_buyer_blacklist_and_msefc_performance() -> None:
    blacklist = BuyerBlacklist("data/synthetic/disputes.csv", "data/synthetic/buyer_profiles.csv")
    offenders = blacklist.get_repeat_offenders(3)
    assert len(offenders) > 0
    assert blacklist.get_blacklist_table() is not None
    sample_gstin = offenders.iloc[0]["buyer_gstin"]
    status = blacklist.check_buyer(sample_gstin)
    assert status["buyer_gstin"] == sample_gstin

    perf = MSEFCPerformance("data/synthetic/state_pendency.csv", "data/synthetic/disputes.csv")
    assert perf.get_msefc_ranking() is not None
    assert perf.get_pendency_analysis() is not None
    assert perf.get_90_day_compliance() is not None

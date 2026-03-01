"""End-to-end integration tests for NyayaSetu pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from src.llm.ollama_client import LLMClient
from src.nyayapredictor.outcome_predictor import OutcomePredictor
from src.samvadai.negotiation_engine import NegotiationEngine
from src.samvadai.settlement_drafter import SettlementDrafter
from src.vaadpatra.dispute_builder import DisputeBuilder
from src.vaadpatra.eligibility_checker import EligibilityChecker
from src.vaadpatra.gst_validator import GSTValidator
from src.vaadpatra.interest_calculator import InterestCalculator
from src.vaadpatra.udyam_fetcher import UdyamFetcher


def _build_pipeline():
    llm = LLMClient(host="localhost", port=11434)
    builder = DisputeBuilder(
        udyam_fetcher=UdyamFetcher("data/msme/sample_disputes.json"),
        gst_validator=GSTValidator(),
        interest_calc=InterestCalculator("data/legal/rbi_bank_rates.json"),
        eligibility_checker=EligibilityChecker(),
        llm_client=llm,
    )
    predictor = OutcomePredictor()
    negotiation = NegotiationEngine(llm, predictor, "data/odr/negotiation_templates.json")
    drafter = SettlementDrafter(llm, "data/odr/settlement_templates.json")
    return builder, predictor, negotiation, drafter


def _sample_dispute(builder: DisputeBuilder):
    return builder.build_dispute(
        udyam_number="UDYAM-RJ-01-1000001",
        buyer_info={
            "buyer_name": "XYZ Engineering Pvt Ltd",
            "buyer_type": "Private Ltd",
            "gstin": "08AABCX1234E1ZP",
            "state": "Rajasthan",
            "district": "Jodhpur",
            "address": "Industrial Area",
        },
        invoices=[
            {
                "invoice_number": "INV-001",
                "invoice_date": "2025-09-01",
                "invoice_amount": 200000.0,
                "goods_services_description": "Auto parts",
                "delivery_date": "2025-09-04",
                "acceptance_date": "2025-09-06",
                "amount_paid": 0.0,
                "amount_outstanding": 200000.0,
            },
            {
                "invoice_number": "INV-002",
                "invoice_date": "2025-10-01",
                "invoice_amount": 150000.0,
                "goods_services_description": "Auto parts",
                "delivery_date": "2025-10-04",
                "acceptance_date": "2025-10-06",
                "amount_paid": 0.0,
                "amount_outstanding": 150000.0,
            },
            {
                "invoice_number": "INV-003",
                "invoice_date": "2025-11-01",
                "invoice_amount": 100000.0,
                "goods_services_description": "Auto parts",
                "delivery_date": "2025-11-03",
                "acceptance_date": "2025-11-05",
                "amount_paid": 0.0,
                "amount_outstanding": 100000.0,
            },
        ],
        has_agreement=True,
        agreed_days=45,
    )


def test_full_pipeline() -> None:
    builder, predictor, negotiation, drafter = _build_pipeline()
    dispute = _sample_dispute(builder)
    prediction = predictor.predict(dispute)
    state = negotiation.initialize_negotiation(dispute, prediction)
    negotiation.generate_round(state)
    negotiation.generate_round(state, "We can pay 300000 in 30 days")
    negotiation.generate_round(state, "We agree to pay 410000")

    if state.status == "settled" and state.settlement_amount:
        agreement = drafter.draft_settlement(
            dispute,
            settlement_amount=state.settlement_amount,
            payment_schedule=[{"date": "2026-03-15", "amount": state.settlement_amount}],
        )
        assert agreement.settlement_amount > 0
    else:
        # Pipeline still valid if strategy decides to escalate.
        assert state.status in {"active", "escalated"}


def test_interest_accuracy(tmp_path: Path) -> None:
    rates = tmp_path / "rates.json"
    rates.write_text(json.dumps([{"effective_date": "2020-01-01", "bank_rate": 6.0, "applicable_interest": 18.0}]), encoding="utf-8")
    calc = InterestCalculator(str(rates))
    result = calc.calculate_interest(500000.0, "2025-08-01", "2026-02-01")
    assert round(result.interest_amount, 2) == 46721.63


def test_prediction_model() -> None:
    builder, predictor, _, _ = _build_pipeline()
    dispute = _sample_dispute(builder)
    pred = predictor.predict(dispute)
    assert 0 < pred.settlement_probability < 1
    assert 0 < pred.predicted_recovery_percentage <= 100
    assert pred.estimated_days_to_resolution > 0


def test_negotiation_flow() -> None:
    builder, predictor, negotiation, _ = _build_pipeline()
    dispute = _sample_dispute(builder)
    pred = predictor.predict(dispute)
    state = negotiation.initialize_negotiation(dispute, pred)

    negotiation.generate_round(state)
    out_stalling = negotiation.generate_round(state, "We need more time to verify invoices")
    out_threat = negotiation.generate_round(state, "We will stop future orders if you escalate")
    assert "message" in out_stalling
    assert "message" in out_threat


def test_demo_mode() -> None:
    # Force unreachable LLM endpoint; pipeline should still run with fallbacks.
    llm = LLMClient(host="127.0.0.1", port=65500, retries=1, timeout_seconds=1)
    builder = DisputeBuilder(
        udyam_fetcher=UdyamFetcher("data/msme/sample_disputes.json"),
        gst_validator=GSTValidator(),
        interest_calc=InterestCalculator("data/legal/rbi_bank_rates.json"),
        eligibility_checker=EligibilityChecker(),
        llm_client=llm,
    )
    dispute = _sample_dispute(builder)
    assert dispute.total_claim > 0
    payload = llm.generate_json("Return demo JSON for OCR")
    assert isinstance(payload, dict)

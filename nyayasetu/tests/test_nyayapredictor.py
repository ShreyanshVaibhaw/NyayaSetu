"""Tests for NyayaPredictor module components."""

from __future__ import annotations

from datetime import UTC, datetime

from src.common.models import BuyerProfile, DisputeCase, Invoice, MSEProfile
from src.nyayapredictor.buyer_risk_scorer import BuyerRiskScorer
from src.nyayapredictor.case_similarity import CaseSimilarityEngine
from src.nyayapredictor.outcome_predictor import OutcomePredictor
from src.nyayapredictor.timeline_estimator import TimelineEstimator


def _make_dispute(
    case_id: str,
    amount: float,
    buyer_type: str = "Private Ltd",
    mse_state: str = "Gujarat",
    buyer_state: str = "Gujarat",
    has_agreement: bool = True,
) -> DisputeCase:
    mse = MSEProfile(
        udyam_number="UDYAM-GJ-01-0001001",
        enterprise_name="Textile MSME",
        owner_name="Owner",
        enterprise_type="Micro",
        major_activity="Manufacturing",
        nic_code="13",
        nic_description="Textiles",
        state=mse_state,
        district="Ahmedabad",
        pincode="380001",
        address="Industrial Estate",
        mobile="9876543210",
        email="owner@example.com",
        date_of_udyam="2022-01-01",
        gstin="24ABCDE1234F1Z5",
        pan="ABCDE1234F",
        bank_account="1234567890",
    )
    buyer = BuyerProfile(
        buyer_name="Buyer Corp",
        buyer_type=buyer_type,  # type: ignore[arg-type]
        gstin="24AABCX1234E1ZP",
        pan="AABCX1234E",
        state=buyer_state,
        district="Ahmedabad",
        address="Business Park",
        contact_person="Finance Head",
        contact_email="finance@buyer.com",
        contact_phone="9012345678",
        industry_sector="Garments",
    )
    inv = Invoice(
        invoice_number="INV-001",
        invoice_date="01-09-2025",
        invoice_amount=amount,
        goods_services_description="Fabric supply",
        delivery_date="05-09-2025",
        acceptance_date="06-09-2025",
        po_number="PO-001",
        payment_due_date="20-10-2025",
        amount_paid=0.0,
        amount_outstanding=amount,
        days_overdue=140,
    )
    return DisputeCase(
        case_id=case_id,
        mse=mse,
        buyer=buyer,
        invoices=[inv],
        total_principal=amount,
        total_interest=amount * 0.1,
        total_claim=amount * 1.1,
        has_written_agreement=has_agreement,
        agreed_credit_days=45 if has_agreement else None,
        dispute_description="Textile supply payment delayed beyond agreed credit period.",
        relief_sought="Principal plus statutory interest",
        supporting_documents=["invoice.pdf"],
        filed_date=None,
        current_stage="Filed",
        msefc_state=mse_state,
        created_at=datetime.now(UTC),
    )


def test_predict_outcomes_for_varied_disputes() -> None:
    predictor = OutcomePredictor()
    cases = [
        _make_dispute("C1", 120000, "Private Ltd", "Gujarat", "Gujarat", True),
        _make_dispute("C2", 800000, "PSU", "Maharashtra", "Maharashtra", True),
        _make_dispute("C3", 2200000, "Private Ltd", "Tamil Nadu", "Karnataka", True),
        _make_dispute("C4", 300000, "Proprietorship", "Rajasthan", "Rajasthan", False),
        _make_dispute("C5", 1500000, "State Govt", "Delhi", "Delhi", True),
    ]
    for case in cases:
        pred = predictor.predict(case)
        assert 0 < pred.settlement_probability < 1
        assert 0 < pred.predicted_recovery_percentage <= 100
        assert pred.estimated_days_to_resolution >= 20


def test_higher_amount_reduces_probability_signal() -> None:
    predictor = OutcomePredictor()
    low = predictor.predict(_make_dispute("LOW", 150000))
    high = predictor.predict(_make_dispute("HIGH", 2500000))
    assert high.settlement_probability <= low.settlement_probability


def test_find_similar_cases_for_textile_dispute() -> None:
    engine = CaseSimilarityEngine("data/legal/legal_precedents.json")
    dispute = _make_dispute("SIM", 450000, "Private Ltd", "Maharashtra", "Maharashtra")
    similar = engine.find_similar_cases(dispute, top_k=5)
    assert len(similar) == 5
    assert similar[0]["similarity_score"] >= similar[-1]["similarity_score"]
    assert "recovery_percentage" in similar[0]


def test_score_buyer_psu_vs_proprietorship() -> None:
    scorer = BuyerRiskScorer()
    psu = scorer.score_buyer("27AAACP1234A1Z1", "PSU Buyer", "PSU")
    prop = scorer.score_buyer("27AAACP9999A1Z1", "Prop Buyer", "Proprietorship")
    assert psu.risk_score <= prop.risk_score
    assert psu.risk_category in {"Low", "Medium", "High", "Critical"}


def test_timeline_estimation_for_different_states() -> None:
    estimator = TimelineEstimator("data/legal/msefc_directory.json")
    fast_state_case = _make_dispute("FAST", 400000, "Private Ltd", "Tamil Nadu", "Tamil Nadu")
    slow_state_case = _make_dispute("SLOW", 400000, "Private Ltd", "Uttar Pradesh", "Uttar Pradesh")

    fast = estimator.estimate_timeline(fast_state_case, strategy="negotiate")
    slow = estimator.estimate_timeline(slow_state_case, strategy="negotiate")
    assert fast["expected"] <= slow["expected"]


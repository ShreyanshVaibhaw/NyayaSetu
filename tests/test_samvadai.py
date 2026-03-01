"""Tests for SamvadAI negotiation and drafting flows."""

from __future__ import annotations

from datetime import UTC, datetime

from src.common.models import (
    BuyerProfile,
    CaseOutcomePrediction,
    DisputeCase,
    Invoice,
    MSEProfile,
    NegotiationState,
)
from src.samvadai.communication_gen import CommunicationGenerator
from src.samvadai.negotiation_engine import NegotiationEngine
from src.samvadai.settlement_drafter import SettlementDrafter
from src.samvadai.tactic_detector import TacticDetector


class _DummyPredictor:
    def predict(self, dispute: DisputeCase) -> CaseOutcomePrediction:
        return CaseOutcomePrediction(
            case_id=dispute.case_id,
            settlement_probability=0.82,
            predicted_recovery_percentage=91.0,
            predicted_recovery_amount=dispute.total_claim * 0.91,
            estimated_days_to_resolution=70,
            recommended_strategy="negotiate",
            confidence=0.8,
            similar_cases=[],
            risk_factors=[],
            favorable_factors=[],
        )


class _DummyLLM:
    def generate(self, prompt: str, system: str | None = None, temperature: float = 0.1) -> str:
        return "Generated response."

    def generate_json(self, prompt: str, system: str | None = None) -> dict:
        return {"status": "ok"}


def _make_dispute() -> DisputeCase:
    mse = MSEProfile(
        udyam_number="UDYAM-MH-01-0001234",
        enterprise_name="Rajasthani Auto Parts",
        owner_name="A Kumar",
        enterprise_type="Micro",
        major_activity="Manufacturing",
        nic_code="29",
        nic_description="Auto parts",
        state="Maharashtra",
        district="Mumbai",
        pincode="400001",
        address="MIDC Area",
        mobile="9876543210",
        email="mse@example.com",
        date_of_udyam="2022-01-10",
        gstin="27ABCDE1234F1Z5",
        pan="ABCDE1234F",
        bank_account="000111222333",
    )
    buyer = BuyerProfile(
        buyer_name="XYZ Engineering Pvt Ltd",
        buyer_type="Private Ltd",
        gstin="27AABCX1234E1ZP",
        pan="AABCX1234E",
        state="Maharashtra",
        district="Mumbai",
        address="Andheri East",
        contact_person="Finance Head",
        contact_email="finance@xyz.com",
        contact_phone="9000000001",
        industry_sector="Engineering",
    )
    invoice = Invoice(
        invoice_number="INV-001",
        invoice_date="01-10-2025",
        invoice_amount=1000000,
        goods_services_description="Auto parts",
        delivery_date="05-10-2025",
        acceptance_date="06-10-2025",
        po_number="PO-88",
        payment_due_date="20-11-2025",
        amount_paid=0.0,
        amount_outstanding=1000000,
        days_overdue=120,
    )
    return DisputeCase(
        case_id="CASE-001",
        mse=mse,
        buyer=buyer,
        invoices=[invoice],
        total_principal=1000000.0,
        total_interest=100000.0,
        total_claim=1100000.0,
        has_written_agreement=True,
        agreed_credit_days=45,
        dispute_description="Buyer delayed payment beyond agreed credit period.",
        relief_sought="Principal + interest",
        supporting_documents=["invoice.pdf"],
        filed_date=None,
        current_stage="Filed",
        msefc_state="Maharashtra",
        created_at=datetime.now(UTC),
    )


def test_three_round_negotiation_simulation() -> None:
    dispute = _make_dispute()
    prediction = _DummyPredictor().predict(dispute)
    engine = NegotiationEngine(_DummyLLM(), _DummyPredictor(), "data/odr/negotiation_templates.json")
    state = engine.initialize_negotiation(dispute, prediction)

    round1 = engine.generate_round(state)
    assert round1["offer_amount"] == 1100000.0

    round2 = engine.generate_round(state, "We can pay 600000 in 30 days")
    assert round2["offer_amount"] > 600000
    assert state.status == "active"

    round3 = engine.generate_round(state, "We agree to pay 850000")
    assert state.status in {"settled", "active"}
    if state.status == "settled":
        assert state.settlement_amount == 850000


def test_tactic_detection_messages() -> None:
    detector = TacticDetector(_DummyLLM())
    ctx = NegotiationState(
        negotiation_id="N1",
        case_id="C1",
        round_number=2,
        mse_offer=1000000,
        buyer_counter=600000,
        mse_strategy="firm_demand",
        messages=[],
        status="active",
        settlement_amount=None,
        settlement_terms=None,
    )

    stalling = detector.analyze_buyer_response("We need more time to verify invoices", ctx)
    threatening = detector.analyze_buyer_response("We will stop all future orders", ctx)
    cooperative = detector.analyze_buyer_response("Let's settle this amount", ctx)

    assert stalling["tactic"] == "stalling"
    assert threatening["tactic"] == "threatening"
    assert cooperative["tactic"] == "cooperative"


def test_settlement_draft_for_5l_dispute() -> None:
    dispute = _make_dispute()
    dispute.total_principal = 500000.0
    dispute.total_interest = 50000.0
    dispute.total_claim = 550000.0
    drafter = SettlementDrafter(_DummyLLM(), "data/odr/settlement_templates.json")
    agreement = drafter.draft_settlement(
        dispute=dispute,
        settlement_amount=500000.0,
        payment_schedule=[{"date": "2026-03-15", "amount": 500000.0}],
        interest_waived=50000.0,
    )
    assert agreement.settlement_amount == 500000.0
    assert agreement.interest_waived == 50000.0
    assert len(agreement.terms_and_conditions) >= 4


def test_demand_notice_generation() -> None:
    drafter = SettlementDrafter(_DummyLLM(), "data/odr/settlement_templates.json")
    notice = drafter.draft_demand_notice(_make_dispute())
    assert "Section 15" in notice
    assert "Section 16" in notice
    assert "MSEFC" in notice


def test_communication_in_hindi() -> None:
    generator = CommunicationGenerator(_DummyLLM(), "data/odr/negotiation_templates.json")
    msg = generator.generate_message(_make_dispute(), "initial_demand", language="hi")
    assert "प्रिय" in msg


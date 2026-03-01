"""NyayaSetu end-to-end scripted demo (<3 minutes narrative)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.llm.ollama_client import LLMClient
from src.nyayapredictor.outcome_predictor import OutcomePredictor
from src.samvadai.negotiation_engine import NegotiationEngine
from src.samvadai.settlement_drafter import SettlementDrafter
from src.vaadpatra.dispute_builder import DisputeBuilder
from src.vaadpatra.eligibility_checker import EligibilityChecker
from src.vaadpatra.gst_validator import GSTValidator
from src.vaadpatra.interest_calculator import InterestCalculator
from src.vaadpatra.udyam_fetcher import UdyamFetcher
from src.vasoolitracker.dispute_analytics import DisputeAnalytics


def run_demo() -> None:
    """Demonstrate filing, prediction, negotiation, and dashboard flow."""
    llm = LLMClient()
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

    print("Scene 1: Smart Dispute Filing")
    dispute = builder.build_dispute(
        udyam_number="UDYAM-RJ-01-1000001",
        buyer_info={
            "buyer_name": "XYZ Engineering Pvt Ltd",
            "buyer_type": "Private Ltd",
            "gstin": "08AABCX1234E1ZP",
            "state": "Rajasthan",
            "district": "Jodhpur",
            "address": "Industrial Zone, Jodhpur",
        },
        invoices=[
            {
                "invoice_number": "INV-001",
                "invoice_date": "2025-06-01",
                "invoice_amount": 200000,
                "goods_services_description": "Auto part batch 1",
                "delivery_date": "2025-06-03",
                "acceptance_date": "2025-06-05",
                "amount_paid": 0.0,
                "amount_outstanding": 200000,
            },
            {
                "invoice_number": "INV-002",
                "invoice_date": "2025-07-01",
                "invoice_amount": 150000,
                "goods_services_description": "Auto part batch 2",
                "delivery_date": "2025-07-03",
                "acceptance_date": "2025-07-05",
                "amount_paid": 0.0,
                "amount_outstanding": 150000,
            },
            {
                "invoice_number": "INV-003",
                "invoice_date": "2025-08-01",
                "invoice_amount": 100000,
                "goods_services_description": "Auto part batch 3",
                "delivery_date": "2025-08-03",
                "acceptance_date": "2025-08-05",
                "amount_paid": 0.0,
                "amount_outstanding": 100000,
            },
        ],
        has_agreement=True,
        agreed_days=45,
    )
    print(f"Principal: Rs {dispute.total_principal:,.0f}, Interest: Rs {dispute.total_interest:,.0f}, Claim: Rs {dispute.total_claim:,.0f}")
    print("Eligibility: VALID")

    print("\nScene 2: Case Prediction")
    pred = predictor.predict(dispute)
    print(f"Settlement probability: {pred.settlement_probability * 100:.1f}%")
    print(f"Expected recovery: Rs {pred.predicted_recovery_amount:,.0f} ({pred.predicted_recovery_percentage:.1f}%)")
    print(f"Timeline: {pred.estimated_days_to_resolution} days")
    print(f"Strategy: {pred.recommended_strategy}")

    print("\nScene 3: AI Negotiation")
    state = negotiation.initialize_negotiation(dispute, pred)
    r1 = negotiation.generate_round(state)
    print(f"Round 1 demand: Rs {r1['offer_amount']:,.0f}")
    r2 = negotiation.generate_round(state, "We can pay 300000 in 30 days")
    print(f"Round 2 counter: Rs {r2['offer_amount']:,.0f}")
    r3 = negotiation.generate_round(state, "We agree to pay 410000")
    print(r3["message"])
    if state.status == "settled" and state.settlement_amount:
        settlement = drafter.draft_settlement(
            dispute,
            settlement_amount=state.settlement_amount,
            payment_schedule=[{"date": "2026-03-15", "amount": state.settlement_amount}],
            interest_waived=max(0.0, dispute.total_claim - state.settlement_amount),
        )
        print(f"Settlement agreement generated: {settlement.agreement_id}")

    print("\nScene 4: Dashboard")
    metrics = DisputeAnalytics("data/synthetic/disputes.csv").get_overview_metrics()
    print(
        f"{metrics['total_disputes']:,} disputes | Rs {metrics['total_amount_disputed']/10000000:.1f} crore disputed | "
        f"Rs {metrics['total_recovered']/10000000:.1f} crore recovered ({metrics['recovery_rate']:.1f}%)"
    )
    print("\nNyayaSetu: Helping India's MSMEs recover what's rightfully theirs.")


def main() -> None:
    run_demo()


if __name__ == "__main__":
    main()

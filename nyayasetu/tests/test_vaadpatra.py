"""Tests for VaadPatra legal computation and eligibility checks."""

from __future__ import annotations

import json
from pathlib import Path

from src.common.models import Invoice
from src.vaadpatra.dispute_builder import DisputeBuilder
from src.vaadpatra.document_ocr import DocumentOCR
from src.vaadpatra.eligibility_checker import EligibilityChecker
from src.vaadpatra.gst_validator import GSTValidator
from src.vaadpatra.interest_calculator import InterestCalculator
from src.vaadpatra.udyam_fetcher import UdyamFetcher
from src.voice.bhashini_client import BhashiniClient
from src.voice.conversation_engine import ConversationEngine


def test_interest_calculator_fixed_rate_six_months(tmp_path: Path) -> None:
    """Verify 6-month monthly compounding at fixed 6.50% RBI rate."""
    rates_path = tmp_path / "rbi_rates.json"
    rates_path.write_text(
        json.dumps([{"effective_date": "2020-01-01", "bank_rate": 6.50, "applicable_interest": 19.50}]),
        encoding="utf-8",
    )
    calculator = InterestCalculator(str(rates_path))

    result = calculator.calculate_interest(
        principal=100000.0,
        start_date="2024-01-01",
        end_date="2024-07-01",
    )

    assert round(result.interest_amount, 2) == 10154.78
    assert round(result.total_due, 2) == 110154.78
    assert result.months_overdue == 6


def test_interest_calculator_multiple_invoices() -> None:
    """Verify aggregate results for multiple invoice calculations."""
    calculator = InterestCalculator("data/legal/rbi_bank_rates.json")
    invoices = [
        Invoice(
            invoice_number="INV-001",
            invoice_date="01-09-2025",
            invoice_amount=200000.0,
            goods_services_description="Auto components supply",
            delivery_date="05-09-2025",
            acceptance_date="10-09-2025",
            po_number="PO-001",
            payment_due_date="25-10-2025",
            amount_paid=0.0,
            amount_outstanding=200000.0,
            days_overdue=120,
        ),
        Invoice(
            invoice_number="INV-002",
            invoice_date="15-09-2025",
            invoice_amount=150000.0,
            goods_services_description="Additional shipment",
            delivery_date="19-09-2025",
            acceptance_date="22-09-2025",
            po_number="PO-002",
            payment_due_date="06-11-2025",
            amount_paid=0.0,
            amount_outstanding=150000.0,
            days_overdue=100,
        ),
    ]

    result = calculator.calculate_for_invoices(invoices=invoices, end_date="2026-02-01")
    assert result["total_principal"] == 350000.0
    assert result["total_interest"] > 0
    assert result["total_claim"] > result["total_principal"]
    assert len(result["per_invoice"]) == 2


def test_interest_rate_change_mid_period() -> None:
    """Verify calculation handles periods that cross RBI rate changes."""
    calculator = InterestCalculator("data/legal/rbi_bank_rates.json")
    result = calculator.calculate_interest(
        principal=500000.0,
        start_date="2025-01-01",
        end_date="2025-06-01",
    )

    rates_seen = {round(row["rbi_bank_rate"], 2) for row in result.calculation_breakdown}
    assert 6.25 in rates_seen
    assert 6.0 in rates_seen
    assert result.interest_amount > 0


def test_eligibility_valid_case() -> None:
    """Valid micro/small dispute should pass eligibility checks."""
    checker = EligibilityChecker()
    verdict = checker.check_eligibility(
        udyam_date="2023-01-10",
        earliest_invoice_date="2025-01-15",
        enterprise_type="Micro",
        days_overdue=120,
        major_activity="Manufacturing",
        has_written_agreement=True,
        agreed_credit_days=45,
    )
    assert verdict["eligible"] is True
    assert verdict["reasons"] == []


def test_eligibility_udyam_after_invoice_invalid() -> None:
    """Udyam registration after invoice date should be rejected."""
    checker = EligibilityChecker()
    verdict = checker.check_eligibility(
        udyam_date="2025-02-01",
        earliest_invoice_date="2025-01-15",
        enterprise_type="Micro",
        days_overdue=120,
        major_activity="Manufacturing",
    )
    assert verdict["eligible"] is False
    assert any("Udyam registration date is after invoice date" in reason for reason in verdict["reasons"])


def test_eligibility_medium_enterprise_invalid() -> None:
    """Medium enterprise should fail MSMED micro/small eligibility check."""
    checker = EligibilityChecker()
    verdict = checker.check_eligibility(
        udyam_date="2023-01-01",
        earliest_invoice_date="2025-01-01",
        enterprise_type="Medium",
        days_overdue=120,
        major_activity="Manufacturing",
    )
    assert verdict["eligible"] is False
    assert any("Only Micro or Small enterprises" in reason for reason in verdict["reasons"])


class _DummyLLM:
    def generate(self, prompt: str, system: str | None = None, temperature: float = 0.1) -> str:
        return "Supplier seeks principal plus statutory interest for delayed payment."

    def generate_json(self, prompt: str, system: str | None = None) -> dict:
        return {
            "document_type": "invoice",
            "invoice_number": "INV-MOCK-001",
            "invoice_date": "01-01-2026",
            "seller_name": "Demo Seller",
            "buyer_name": "Demo Buyer",
            "buyer_gstin": "08AABCX1234E1ZP",
            "total_amount": 100000.0,
            "items": ["Demo item - Rs 100000"],
            "po_reference": "PO-MOCK-001",
            "delivery_date": "03-01-2026",
            "payment_terms": "45 days",
            "confidence": 0.9,
        }


def _builder() -> DisputeBuilder:
    return DisputeBuilder(
        udyam_fetcher=UdyamFetcher("data/msme/sample_disputes.json"),
        gst_validator=GSTValidator(),
        interest_calc=InterestCalculator("data/legal/rbi_bank_rates.json"),
        eligibility_checker=EligibilityChecker(),
        llm_client=_DummyLLM(),
    )


def test_build_dispute_from_sample_case() -> None:
    """Build a realistic dispute end-to-end from manual inputs."""
    builder = _builder()
    dispute = builder.build_dispute(
        udyam_number="UDYAM-RJ-01-1000001",
        buyer_info={
            "buyer_name": "XYZ Engineering Pvt Ltd",
            "buyer_type": "Private Ltd",
            "gstin": "08AABCX1234E1ZP",
            "state": "Rajasthan",
            "district": "Jaipur",
            "address": "Industrial Area Jaipur",
        },
        invoices=[
            {
                "invoice_number": "INV-001",
                "invoice_date": "2025-09-01",
                "invoice_amount": 200000,
                "goods_services_description": "Auto components",
                "delivery_date": "2025-09-05",
                "acceptance_date": "2025-09-10",
                "amount_paid": 0,
                "amount_outstanding": 200000,
            },
            {
                "invoice_number": "INV-002",
                "invoice_date": "2025-10-01",
                "invoice_amount": 150000,
                "goods_services_description": "Auto components",
                "delivery_date": "2025-10-05",
                "acceptance_date": "2025-10-10",
                "amount_paid": 0,
                "amount_outstanding": 150000,
            },
        ],
        has_agreement=True,
        agreed_days=45,
    )
    assert dispute.total_principal == 350000
    assert dispute.total_interest > 0
    assert dispute.total_claim > dispute.total_principal
    assert dispute.msefc_state == "Rajasthan"
    assert len(dispute.invoices) == 2


def test_ocr_pipeline_mock_fallback() -> None:
    """OCR extraction should not crash even when OCR dependencies are unavailable."""
    extractor = DocumentOCR(llm_client=None)
    data = extractor.extract_from_invoice("nonexistent_invoice.png")
    assert data["document_type"] == "invoice"
    assert data["total_amount"] >= 0


def test_conversation_flow_hindi_five_turn() -> None:
    """Validate 5-turn Hindi voice flow to final dispute generation."""
    builder = _builder()
    engine = ConversationEngine(
        llm_client=_DummyLLM(),
        dispute_builder=builder,
        bhashini_client=BhashiniClient(),
    )
    state = engine.start_session(language="hi")

    state, _ = engine.process_message(state, "UDYAM-RJ-01-1000001")
    state, _ = engine.process_message(state, "XYZ Engineering Pvt Ltd")
    state, _ = engine.process_message(state, "08AABCX1234E1ZP")
    state, _ = engine.process_message(state, "200000, 150000, 100000")
    state, response = engine.process_message(state, "हाँ")

    assert state["step"] == "completed"
    assert state["dispute"] is not None
    assert "शिकायत तैयार" in response

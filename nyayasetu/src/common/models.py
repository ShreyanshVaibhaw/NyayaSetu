"""Core Pydantic models used across NyayaSetu modules."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class MSEProfile(BaseModel):
    """Micro/Small Enterprise (the seller/complainant)."""

    udyam_number: str = Field(..., description="UDYAM-XX-00-0000000")
    enterprise_name: str
    owner_name: str
    enterprise_type: Literal["Micro", "Small"]
    major_activity: Literal["Manufacturing", "Services"]
    nic_code: str
    nic_description: str
    state: str
    district: str
    pincode: str
    address: str
    mobile: str
    email: Optional[str] = None
    date_of_udyam: str = Field(..., description="Critical: must be before invoice date")
    gstin: Optional[str] = None
    pan: Optional[str] = None
    bank_account: Optional[str] = None


class BuyerProfile(BaseModel):
    """The buyer (respondent in dispute)."""

    buyer_name: str
    buyer_type: Literal[
        "Central Govt",
        "State Govt",
        "PSU",
        "Private Ltd",
        "LLP",
        "Proprietorship",
        "Partnership",
        "Trust/Society",
    ]
    gstin: Optional[str] = None
    pan: Optional[str] = None
    state: str
    district: str
    address: str
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    industry_sector: Optional[str] = None


class Invoice(BaseModel):
    """Individual invoice in a dispute."""

    invoice_number: str
    invoice_date: str = Field(..., description="DD-MM-YYYY")
    invoice_amount: float
    goods_services_description: str
    delivery_date: Optional[str] = None
    acceptance_date: Optional[str] = None
    po_number: Optional[str] = None
    payment_due_date: Optional[str] = None
    amount_paid: float = 0.0
    amount_outstanding: float
    days_overdue: int


class DisputeCase(BaseModel):
    """Complete dispute case for filing."""

    case_id: str
    mse: MSEProfile
    buyer: BuyerProfile
    invoices: List[Invoice]
    total_principal: float
    total_interest: float
    total_claim: float
    has_written_agreement: bool
    agreed_credit_days: Optional[int] = None
    dispute_description: str
    relief_sought: str
    supporting_documents: List[str]
    filed_date: Optional[str] = None
    current_stage: str
    msefc_state: str
    created_at: datetime


class InterestCalculation(BaseModel):
    """Compound interest calculation per Section 16."""

    invoice_number: str
    principal: float
    start_date: str
    end_date: str
    rbi_bank_rate: float
    applicable_rate: float
    months_overdue: int
    interest_amount: float
    total_due: float
    calculation_breakdown: List[Dict]


class CaseOutcomePrediction(BaseModel):
    """ML prediction of case outcome."""

    case_id: str
    settlement_probability: float
    predicted_recovery_percentage: float
    predicted_recovery_amount: float
    estimated_days_to_resolution: int
    recommended_strategy: str
    confidence: float
    similar_cases: List[Dict]
    risk_factors: List[str]
    favorable_factors: List[str]
    feature_contributions: List[Dict] = Field(default_factory=list)
    similar_case_summary: Optional[str] = None


class NegotiationState(BaseModel):
    """State of negotiation between MSE and buyer."""

    negotiation_id: str
    case_id: str
    round_number: int
    mse_offer: float
    buyer_counter: Optional[float] = None
    mse_strategy: str
    messages: List[Dict]
    status: Literal["active", "settled", "failed", "escalated"]
    settlement_amount: Optional[float] = None
    settlement_terms: Optional[str] = None


class SettlementAgreement(BaseModel):
    """Auto-generated settlement agreement."""

    agreement_id: str
    case_id: str
    mse_name: str
    buyer_name: str
    settlement_amount: float
    payment_schedule: List[Dict]
    interest_waived: float
    terms_and_conditions: List[str]
    generated_at: datetime


class BuyerRiskScore(BaseModel):
    """Risk assessment of a buyer."""

    buyer_gstin: str
    buyer_name: str
    risk_score: float
    risk_category: Literal["Low", "Medium", "High", "Critical"]
    past_disputes_count: int
    avg_payment_delay_days: int
    total_outstanding_to_mses: float
    gst_compliance_status: str
    factors: List[str]


class DisputeAnalytics(BaseModel):
    """Analytics for dashboard."""

    total_disputes: int
    total_amount_disputed: float
    total_recovered: float
    recovery_rate: float
    avg_resolution_days: int
    stage_distribution: Dict[str, int]
    state_wise: Dict[str, Dict]
    sector_wise: Dict[str, Dict]
    monthly_trend: List[Dict]

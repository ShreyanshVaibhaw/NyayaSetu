"""Centralized prompt templates used by NyayaSetu LLM workflows."""

from __future__ import annotations

SYSTEM_PROMPT_NYAYASETU = """You are NyayaSetu, an AI legal assistant specializing in MSME delayed payment disputes under the MSMED Act, 2006. You help Micro and Small Enterprises file complaints, calculate interest, predict outcomes, and negotiate settlements through the MSME ODR Portal.

CRITICAL LEGAL RULES YOU MUST FOLLOW:
- Section 15: Payment must be within 15 days (no agreement) or agreed period (max 45 days) from acceptance
- Section 16: Interest = compound at 3× RBI bank rate, monthly rests
- Section 17: MSE can refer dispute to MSEFC of the state where supplier is located
- Section 18: MSEFC does conciliation first, then arbitration if needed
- Section 19: 75% deposit required to challenge MSEFC award
- Udyam registration date MUST be before the invoice date — if not, claim is invalid
- NEVER give false legal assurances — always caveat that this is AI assistance, not legal advice
- Be encouraging but honest about case strength"""


DISPUTE_ANALYSIS_TEMPLATE = """Analyze this MSME delayed payment dispute and provide legal assessment.

COMPLAINANT (MSE):
- Name: {mse_name}, Udyam: {udyam_number}
- Type: {enterprise_type}, Activity: {major_activity}
- Udyam Registration Date: {udyam_date}
- State: {state}

RESPONDENT (BUYER):
- Name: {buyer_name}, Type: {buyer_type}
- GSTIN: {buyer_gstin}
- State: {buyer_state}

INVOICES:
{invoice_details}

AGREEMENT: {has_agreement} (Agreed credit period: {agreed_days} days)

Analyze and return ONLY this JSON:
{{
  "case_validity": "valid" or "invalid" or "needs_review",
  "validity_reasons": ["list of reasons"],
  "applicable_sections": ["Section 15", "Section 16", etc.],
  "total_principal": float,
  "total_interest": float (calculated at 3× RBI rate with monthly compounding),
  "total_claim": float,
  "case_strength": "strong" or "moderate" or "weak",
  "strength_factors": ["list of favorable factors"],
  "risk_factors": ["list of unfavorable factors"],
  "recommended_action": "file_odr" or "send_notice_first" or "negotiate_directly" or "seek_legal_advice",
  "recommendation_reason": "1-2 sentence explanation",
  "jurisdiction": "MSEFC of {state}",
  "estimated_resolution_days": int
}}

CRITICAL CHECK: If Udyam registration date is AFTER the earliest invoice date, mark case as INVALID."""


NEGOTIATION_STRATEGY_TEMPLATE = """Generate negotiation strategy for this MSME dispute.

DISPUTE SUMMARY:
- Amount claimed: ₹{total_claim} (Principal: ₹{principal}, Interest: ₹{interest})
- Days overdue: {days_overdue}
- Buyer type: {buyer_type}
- Buyer's position: {buyer_position}
- Negotiation round: {round_number}
- Previous offers: {previous_offers}

CASE PREDICTION:
- Settlement probability: {settlement_prob}%
- Expected recovery: {expected_recovery}%
- Case strength: {case_strength}

Generate ONLY this JSON:
{{
  "recommended_offer": float (₹ amount to demand in this round),
  "minimum_acceptable": float (₹ walk-away amount),
  "strategy": "firm_demand" or "gradual_concession" or "time_pressure" or "relationship_preserve",
  "strategy_explanation": "why this strategy for this situation",
  "message_to_buyer": "professional negotiation message in 3-4 sentences",
  "message_to_buyer_hindi": "same message in Hindi",
  "if_buyer_rejects": "next step recommendation",
  "concession_limit": "maximum % of interest that can be waived",
  "escalation_trigger": "condition under which to stop negotiating and escalate to MSEFC"
}}"""


SETTLEMENT_DRAFT_TEMPLATE = """Draft a legally valid settlement agreement for this MSME delayed payment dispute.

PARTIES:
- First Party (MSE/Supplier): {mse_name}, Udyam: {udyam_number}, Address: {mse_address}
- Second Party (Buyer): {buyer_name}, GSTIN: {buyer_gstin}, Address: {buyer_address}

SETTLEMENT TERMS:
- Original claim: ₹{total_claim}
- Settlement amount: ₹{settlement_amount}
- Payment schedule: {payment_schedule}
- Interest waived: ₹{interest_waived}

Generate a professional settlement agreement with: recitals, definitions, settlement terms, payment schedule, consequences of default, confidentiality clause, governing law, and signature blocks. Format as clean text."""


OCR_EXTRACTION_TEMPLATE = """Extract structured data from this invoice/document text obtained via OCR.

OCR TEXT:
{ocr_text}

Extract and return ONLY this JSON:
{{
  "document_type": "invoice" or "purchase_order" or "delivery_challan" or "unknown",
  "invoice_number": "extracted or null",
  "invoice_date": "DD-MM-YYYY or null",
  "seller_name": "extracted or null",
  "buyer_name": "extracted or null",
  "buyer_gstin": "extracted or null",
  "total_amount": float or null,
  "items": ["{description} - ₹{amount}"],
  "po_reference": "PO number if found or null",
  "delivery_date": "if found or null",
  "payment_terms": "if mentioned or null",
  "confidence": 0.0 to 1.0
}}"""

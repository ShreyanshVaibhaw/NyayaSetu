"""Voice-first conversational filing flow for NyayaSetu."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Tuple


@dataclass
class ConversationEngine:
    """Guided multi-turn intake that builds a dispute-ready payload."""

    llm_client: object
    dispute_builder: object
    bhashini_client: object

    def start_session(self, language: str = "hi") -> Dict:
        """Initialize conversation session state."""
        greeting = (
            "नमस्ते! न्यायसेतु में आपका स्वागत है। मैं आपकी पेमेंट वसूली में मदद करूँगा। "
            "कृपया अपना उद्यम नंबर बताइए।"
            if language == "hi"
            else "Welcome to NyayaSetu. Please share your Udyam number to begin."
        )
        return {
            "language": language,
            "step": "udyam",
            "greeting": greeting,
            "udyam_number": None,
            "buyer_info": {},
            "invoices": [],
            "has_agreement": True,
            "agreed_days": 45,
            "dispute": None,
        }

    @staticmethod
    def _extract_udyam(message: str) -> str:
        match = re.search(r"UDYAM-[A-Z]{2}-\d{2}-\d{7}", message.upper())
        return match.group(0) if match else ""

    @staticmethod
    def _extract_gstin(message: str) -> str:
        match = re.search(r"\b\d{2}[A-Z]{5}\d{4}[A-Z]\dZ[A-Z0-9]\b", message.upper())
        return match.group(0) if match else ""

    @staticmethod
    def _extract_amounts(message: str) -> list[float]:
        raw_values = re.findall(r"(?:₹|rs\.?|rupees?)?\s*([0-9][0-9,]{3,})", message.lower())
        amounts = []
        for raw in raw_values:
            cleaned = raw.replace(",", "")
            try:
                value = float(cleaned)
                if value > 0:
                    amounts.append(value)
            except ValueError:
                continue
        return amounts

    def process_message(self, state: Dict, message: str) -> Tuple[Dict, str]:
        """Advance guided dispute intake flow from free-form message text."""
        step = state.get("step", "udyam")
        text = message.strip()

        if step == "udyam":
            udyam = self._extract_udyam(text)
            if not udyam:
                return state, "कृपया सही उद्यम नंबर बताइए। उदाहरण: UDYAM-RJ-01-0012345"
            state["udyam_number"] = udyam
            state["step"] = "buyer_name"
            return state, "धन्यवाद। अब खरीदार (buyer) का नाम बताइए।"

        if step == "buyer_name":
            state["buyer_info"]["buyer_name"] = text
            state["buyer_info"]["buyer_type"] = "Private Ltd"
            state["buyer_info"]["state"] = "Rajasthan"
            state["buyer_info"]["district"] = "Jaipur"
            state["buyer_info"]["address"] = "Address to be confirmed"
            state["step"] = "buyer_gstin"
            return state, "खरीदार का GSTIN बताइए।"

        if step == "buyer_gstin":
            gstin = self._extract_gstin(text)
            if not gstin:
                return state, "GSTIN सही फॉर्मेट में दीजिए। उदाहरण: 08AABCX1234E1ZP"
            state["buyer_info"]["gstin"] = gstin
            state["step"] = "invoices"
            return state, "अब बाकी बिल की रकम बताइए। जैसे: 200000, 150000, 100000"

        if step == "invoices":
            amounts = self._extract_amounts(text)
            if not amounts:
                return state, "मुझे invoice amounts नहीं मिले। कृपया रकम फिर से लिखें।"
            today = date.today()
            invoices = []
            for idx, amount in enumerate(amounts, start=1):
                inv_date = today - timedelta(days=120 + idx * 15)
                invoices.append(
                    {
                        "invoice_number": f"VOICE-{idx:03d}",
                        "invoice_date": inv_date.strftime("%Y-%m-%d"),
                        "invoice_amount": amount,
                        "goods_services_description": "Invoice captured from conversation",
                        "delivery_date": (inv_date + timedelta(days=2)).strftime("%Y-%m-%d"),
                        "acceptance_date": (inv_date + timedelta(days=5)).strftime("%Y-%m-%d"),
                        "po_number": f"PO-{idx:03d}",
                        "amount_paid": 0.0,
                        "amount_outstanding": amount,
                    }
                )
            state["invoices"] = invoices
            state["step"] = "confirm"
            principal = sum(amounts)
            return state, f"कुल मूलधन ₹{principal:,.0f} है। क्या शिकायत दर्ज करें? (हाँ/Yes)"

        if step == "confirm":
            if text.lower() in {"हाँ", "ha", "haan", "yes", "y"}:
                dispute = self.dispute_builder.build_from_conversation(state)
                state["dispute"] = dispute
                state["step"] = "completed"
                return (
                    state,
                    f"✅ शिकायत तैयार है। कुल दावा ₹{dispute.total_claim:,.2f}. "
                    "डिमांड नोटिस और MSEFC रेफरेंस जनरेट किया जा सकता है।",
                )
            state["step"] = "invoices"
            return state, "ठीक है। कृपया revised invoice amounts दोबारा बताइए।"

        return state, "Session complete. You can start a new filing."

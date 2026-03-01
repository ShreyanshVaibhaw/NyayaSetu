"""Ollama client wrapper with safe fallbacks for demo mode."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

import requests

import config


def _default_demo_cache() -> Dict[str, str]:
    """Pre-cached responses for 5 demo scenarios."""
    return {
        "demo_case_1": '{"scenario":"auto_parts_private","settlement_probability":0.82,"expected_recovery":410000,"strategy":"firm_demand"}',
        "demo_case_2": '{"scenario":"it_psu","settlement_probability":0.74,"expected_recovery":1020000,"strategy":"gradual_concession"}',
        "demo_case_3": '{"scenario":"textile_exporter","settlement_probability":0.79,"expected_recovery":108000,"strategy":"negotiate"}',
        "demo_case_4": '{"scenario":"food_chain","settlement_probability":0.68,"expected_recovery":430000,"strategy":"principal_focus"}',
        "demo_case_5": '{"scenario":"steel_construction","settlement_probability":0.62,"expected_recovery":1320000,"strategy":"escalate_msefc"}',
    }


@dataclass
class LLMClient:
    """Client for interacting with a local Ollama server."""

    host: str = config.OLLAMA_HOST
    port: int = config.OLLAMA_PORT
    model: str = config.OLLAMA_MODEL
    timeout_seconds: int = 120
    retries: int = 3
    _demo_cache: Dict[str, str] = field(default_factory=_default_demo_cache)

    @property
    def base_url(self) -> str:
        """Base URL for Ollama HTTP endpoints."""
        return f"http://{self.host}:{self.port}"

    def health_check(self) -> bool:
        """Check whether the configured Ollama service is reachable."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            return response.ok
        except requests.RequestException:
            return False

    def _fallback_response(self, prompt: str) -> str:
        """Return deterministic mock responses for demo/failed calls."""
        lowered = prompt.lower()
        for key, value in self._demo_cache.items():
            if key in lowered:
                return value
        if "negotiation" in lowered or "counter" in lowered:
            return json.dumps(
                {
                    "recommended_offer": 425000,
                    "minimum_acceptable": 410000,
                    "strategy": "gradual_concession",
                    "strategy_explanation": "Buyer has shown willingness to settle.",
                    "message_to_buyer": "We can waive part interest if principal is settled quickly.",
                    "message_to_buyer_hindi": "हम कुछ ब्याज छोड़ सकते हैं यदि मूलधन जल्दी चुकाया जाए।",
                    "if_buyer_rejects": "Escalate to MSEFC with complete documentation.",
                    "concession_limit": "Up to 100% of interest",
                    "escalation_trigger": "No material movement after 3 rounds",
                }
            )
        if "ocr text" in lowered or "invoice" in lowered:
            return json.dumps(
                {
                    "document_type": "invoice",
                    "invoice_number": "INV-DEMO-001",
                    "invoice_date": "01-01-2026",
                    "seller_name": "Demo Seller",
                    "buyer_name": "Demo Buyer",
                    "buyer_gstin": "08AABCX1234E1ZP",
                    "total_amount": 100000.0,
                    "items": ["Demo line item - Rs 100000"],
                    "po_reference": "PO-DEMO-01",
                    "delivery_date": "03-01-2026",
                    "payment_terms": "45 days",
                    "confidence": 0.72,
                }
            )
        return self._demo_cache.get(
            prompt,
            '{"status":"demo_fallback","message":"Ollama unavailable; returning cached placeholder response."}',
        )

    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.1) -> str:
        """Generate text response from Ollama with retry and timeout safeguards."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if system:
            payload["system"] = system

        for attempt in range(1, self.retries + 1):
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=self.timeout_seconds,
                )
                response.raise_for_status()
                data = response.json()
                text = data.get("response", "").strip()
                if text:
                    self._demo_cache[prompt] = text
                    return text
            except requests.RequestException:
                if attempt < self.retries:
                    time.sleep(1.2 * attempt)
                    continue
                return self._fallback_response(prompt)

        return self._fallback_response(prompt)

    def generate_json(self, prompt: str, system: Optional[str] = None) -> Dict:
        """Generate JSON output, parsing safely from text with fallback extraction."""
        raw = self.generate(prompt=prompt, system=system, temperature=0.05)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return {"status": "parse_error", "raw_response": raw}

        return {"status": "no_json_found", "raw_response": raw}

"""NyayaSetu configuration constants."""

from __future__ import annotations

import os

PROJECT_NAME = "NyayaSetu"
PROJECT_SANSKRIT = "न्यायसेतु"
TAGLINE = "Bridge to Justice — AI that fights for India's MSMEs"

OLLAMA_MODEL = "qwen2.5:14b"
OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11434
POSTGRES_URI = os.getenv("DATABASE_URI", "sqlite:///data/nyayasetu.db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

BHASHINI_API_URL = "https://meity-auth.ulcacontrib.org"
BHASHINI_INFERENCE_URL = "https://dhruva-api.bhashini.gov.in"
BHASHINI_API_KEY = os.getenv("BHASHINI_API_KEY", "")
BHASHINI_USER_ID = os.getenv("BHASHINI_USER_ID", "")

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "mr": "Marathi",
    "bn": "Bengali",
    "te": "Telugu",
    "kn": "Kannada",
    "gu": "Gujarati",
}

UDYAM_API_URL = "https://udyamregistration.gov.in/api"
GST_API_URL = "https://gst.gov.in/api"
ODR_PORTAL_URL = "https://odr.msme.gov.in"
SAMADHAAN_URL = "https://samadhaan.msme.gov.in"

RBI_CURRENT_BANK_RATE = 6.50
INTEREST_MULTIPLIER = 3
MAX_CREDIT_PERIOD_DAYS = 45
DEFAULT_CREDIT_NO_AGREEMENT = 15

DISPUTE_STAGES = [
    "Filed",
    "UNP_Initiated",
    "UNP_Settled",
    "MSEFC_Referred",
    "Conciliation",
    "Arbitration",
    "Award_Passed",
    "Recovered",
    "Closed",
]

BUYER_TYPES = [
    "Central Govt",
    "State Govt",
    "PSU",
    "Private Ltd",
    "LLP",
    "Proprietorship",
    "Partnership",
    "Trust/Society",
]

PREDICTION_FEATURES = [
    "dispute_amount",
    "days_overdue",
    "buyer_type",
    "sector",
    "state",
    "has_written_agreement",
    "buyer_gst_compliant",
    "previous_disputes",
    "invoice_count",
]

APP_MODE = os.getenv("APP_MODE", "DEMO").upper()

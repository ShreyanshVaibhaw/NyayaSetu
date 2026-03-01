"""NyayaSetu Streamlit dashboard application."""

from __future__ import annotations

import json
import base64
import re
import tempfile
from datetime import date, timedelta
from io import BytesIO
from pathlib import Path
from typing import Dict
from urllib.parse import urlencode

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas

try:
    from streamlit_folium import st_folium

    STREAMLIT_FOLIUM_AVAILABLE = True
except ImportError:
    st_folium = None
    STREAMLIT_FOLIUM_AVAILABLE = False

import config
from src.common.i18n import tr
from src.llm.ollama_client import LLMClient
from src.llm.prompt_templates import DISPUTE_ANALYSIS_TEMPLATE
from src.nyayapredictor.buyer_risk_scorer import BuyerRiskScorer
from src.nyayapredictor.case_similarity import CaseSimilarityEngine
from src.nyayapredictor.outcome_predictor import OutcomePredictor
from src.nyayapredictor.timeline_estimator import TimelineEstimator
from src.samvadai.buyer_simulator import BuyerSimulator
from src.samvadai.negotiation_engine import NegotiationEngine
from src.samvadai.settlement_drafter import SettlementDrafter
from src.reporting import (
    build_admin_report_pdf,
    build_demand_notice_pdf,
    build_interest_calculation_excel,
    build_settlement_agreement_pdf,
    build_msefc_reference_pdf,
)
from src.voice.bhashini_client import BhashiniClient
from src.voice.conversation_engine import ConversationEngine
from src.vaadpatra.document_ocr import DocumentOCR
from src.vaadpatra.dispute_classifier import DisputeClassifier
from src.vaadpatra.document_checker import DocumentChecker
from src.vaadpatra.dispute_builder import DisputeBuilder
from src.vaadpatra.eligibility_checker import EligibilityChecker
from src.vaadpatra.gst_validator import GSTValidator
from src.vaadpatra.interest_calculator import InterestCalculator
from src.vaadpatra.udyam_fetcher import UdyamFetcher
from src.common.database import DatabaseManager
from src.vasoolitracker.buyer_blacklist import BuyerBlacklist
from src.vasoolitracker.dispute_analytics import DisputeAnalytics
from src.vasoolitracker.geo_analytics import GeoAnalytics
from src.vasoolitracker.msefc_performance import MSEFCPerformance


THEMES = {
    "theme_courtroom": {
        "name": "Courtroom Light",
        "primary": "#1E2D4D",
        "accent": "#B9973D",
        "bg": "#F7F8FA",
        "card": "#FFFFFF",
        "text": "#111827",
        "muted": "#6B7280",
    },
    "theme_exec": {
        "name": "Executive Blue",
        "primary": "#123C69",
        "accent": "#2A9D8F",
        "bg": "#F4F7FB",
        "card": "#FFFFFF",
        "text": "#0B1F33",
        "muted": "#5B6B7A",
    },
    "theme_slate": {
        "name": "Slate Clean",
        "primary": "#2F3A45",
        "accent": "#C06C2E",
        "bg": "#F5F6F8",
        "card": "#FFFFFF",
        "text": "#1F2937",
        "muted": "#6B7280",
    },
}


def load_json(path: str, fallback):
    """Load JSON with fallback."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return fallback


def format_inr(value: float) -> str:
    """Simple INR formatter."""
    return f"₹{value:,.2f}"


def normalize_speech_lang(lang: str) -> str:
    """Map UI language keys to Bhashini-compatible language code."""
    supported = {"en", "hi", "ta", "mr", "bn", "te", "kn", "gu"}
    return lang if lang in supported else "en"


def overdue_badge(days: int) -> str:
    """Return a color-coded overdue badge."""
    if days >= 180:
        return f"🔴 {days} days"
    if days >= 90:
        return f"🟠 {days} days"
    if days >= 30:
        return f"🟡 {days} days"
    return f"🟢 {days} days"


def risk_badge(category: str) -> str:
    """Return icon-coded buyer risk category."""
    cat = (category or "").lower()
    if "critical" in cat:
        return "🔴 Critical"
    if "high" in cat:
        return "🟠 High"
    if "medium" in cat:
        return "🟡 Medium"
    return "🟢 Low"


def extract_offer_amount(text: str) -> float | None:
    """Extract the highest numeric amount from buyer text."""
    matches = re.findall(r"(?:₹|rs\.?\s*)?([0-9][0-9,]*)", text or "", flags=re.IGNORECASE)
    if not matches:
        return None
    values = [float(token.replace(",", "")) for token in matches]
    return max(values) if values else None


def detect_text_language(text: str) -> str:
    """Simple script-based language detection for negotiation input."""
    sample = (text or "").strip()
    if not sample:
        return "en"
    if re.search(r"[\u0900-\u097F]", sample):
        return "hi"
    if re.search(r"[\u0B80-\u0BFF]", sample):
        return "ta"
    if re.search(r"[\u0980-\u09FF]", sample):
        return "bn"
    if re.search(r"[\u0C00-\u0C7F]", sample):
        return "te"
    if re.search(r"[\u0C80-\u0CFF]", sample):
        return "kn"
    if re.search(r"[\u0A80-\u0AFF]", sample):
        return "gu"
    return "en"


def translate_cached(services: Dict, text: str, source_lang: str, target_lang: str) -> str:
    """Translate text with session-level cache to avoid repeated API calls."""
    cache = st.session_state.setdefault("translation_cache", {})
    cache_key = f"{source_lang}:{target_lang}:{text}"
    if cache_key in cache:
        return cache[cache_key]
    translated = services["bhashini"].translate(text, source_language=source_lang, target_language=target_lang).get("text", text)
    cache[cache_key] = translated
    st.session_state["translation_cache"] = cache
    return translated


def render_pdf_preview(pdf_bytes: bytes, key: str, height: int = 420) -> None:
    """Render inline PDF preview using base64 iframe."""
    if not pdf_bytes:
        return
    b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    st.markdown(
        f'<iframe title="{key}" src="data:application/pdf;base64,{b64_pdf}" width="100%" height="{height}" '
        'style="border:1px solid #E5E7EB;border-radius:8px;"></iframe>',
        unsafe_allow_html=True,
    )


def activate_demo_tour(services: Dict) -> None:
    """Prepare a complete demo-ready sample case and navigate to filing."""
    samples = load_json("data/msme/sample_disputes.json", [])
    if not samples:
        st.warning("Demo data unavailable.")
        return
    sample = samples[0]
    buyer = sample.get("buyer", {})
    invoices = sample.get("invoices", [])
    try:
        dispute = services["builder"].build_dispute(
            udyam_number=sample.get("mse", {}).get("udyam_number", "UDYAM-RJ-01-1000001"),
            buyer_info={
                "buyer_name": buyer.get("buyer_name", "Demo Buyer Pvt Ltd"),
                "buyer_type": buyer.get("buyer_type", "Private Ltd"),
                "gstin": buyer.get("gstin", "08AABCX1234E1ZP"),
                "state": buyer.get("state", "Rajasthan"),
                "district": buyer.get("district", "Jaipur"),
                "address": buyer.get("address", "Demo business address"),
            },
            invoices=invoices,
            has_agreement=True,
            agreed_days=45,
            uploaded_documents=["udyam_certificate", "invoice", "purchase_order_or_contract", "delivery_proof"],
        )
        similar = services["similarity"].find_similar_cases(dispute, top_k=5)
        prediction = services["predictor"].predict(dispute, similar_cases=similar)
        st.session_state["active_dispute"] = dispute
        st.session_state["prediction"] = prediction
        st.session_state["similar_cases"] = similar
        st.session_state["negotiation_state"] = None
        saved = st.session_state.get("saved_cases", {})
        saved[dispute.case_id] = {"dispute": dispute, "prediction": prediction, "similar_cases": similar}
        st.session_state["saved_cases"] = saved
        st.session_state["demo_tour_active"] = True
        st.session_state["demo_tour_step"] = "file_dispute"
        st.session_state["_nav_target_key"] = "file_dispute"
        st.toast("Demo tour ready. Proceeding to filing workspace.")
        st.rerun()
    except Exception:
        st.warning("Demo tour setup failed. Please continue with manual filing.")


def render_demo_tour_hint(page_key: str) -> None:
    """Show guided tour hints and next-step navigation."""
    if not st.session_state.get("demo_tour_active"):
        return
    step = st.session_state.get("demo_tour_step", "file_dispute")
    if step != page_key:
        return

    if page_key == "file_dispute":
        st.info("Demo Tour 1/4: Review the prefilled case, run assessment, and generate filing documents.")
        if st.button("Next: Go to Negotiation", key="tour_next_negotiate"):
            st.session_state["demo_tour_step"] = "negotiate"
            st.session_state["_nav_target_key"] = "negotiate"
            st.rerun()
    elif page_key == "negotiate":
        st.info("Demo Tour 2/4: Run a negotiation round, inspect sentiment, and draft settlement outputs.")
        if st.button("Next: Go to Recovery Dashboard", key="tour_next_dashboard"):
            st.session_state["demo_tour_step"] = "dashboard"
            st.session_state["_nav_target_key"] = "dashboard"
            st.rerun()
    elif page_key == "dashboard":
        st.info("Demo Tour 3/4: Showcase analytics, heatmap, and export the dashboard PDF report.")
        if st.button("Next: Go to About", key="tour_next_about"):
            st.session_state["demo_tour_step"] = "about"
            st.session_state["_nav_target_key"] = "about"
            st.rerun()
    elif page_key == "about":
        st.success("Demo Tour 4/4 complete.")
        if st.button("End Demo Tour", key="tour_end"):
            st.session_state["demo_tour_active"] = False
            st.session_state["demo_tour_step"] = None
            st.toast("Demo tour ended.")
            st.rerun()


def build_interest_calculation_pdf(result) -> bytes:
    """Create a compact PDF for interest calculation output."""
    buf = BytesIO()
    c = pdf_canvas.Canvas(buf, pagesize=A4)
    y = 800

    def draw(line: str) -> None:
        nonlocal y
        c.drawString(45, y, line)
        y -= 16
        if y < 60:
            c.showPage()
            y = 800

    draw("INTEREST CALCULATION - MSMED ACT SECTION 16")
    draw("")
    draw(f"Principal: Rs {result.principal:,.2f}")
    draw(f"Start Date: {result.start_date}")
    draw(f"End Date: {result.end_date}")
    draw(f"RBI Bank Rate: {result.rbi_bank_rate:.2f}%")
    draw(f"Applicable Annual Rate (3x): {result.applicable_rate:.2f}%")
    draw(f"Interest Amount: Rs {result.interest_amount:,.2f}")
    draw(f"Total Due: Rs {result.total_due:,.2f}")
    draw("")
    draw("Breakdown:")
    for row in result.calculation_breakdown[:24]:
        draw(
            f"{row.get('period_start')} to {row.get('period_end')} | "
            f"Rate {row.get('applicable_annual_rate', 0)}% | "
            f"Interest Rs {row.get('interest_component', 0):,.2f}"
        )
    draw("")
    draw("NyayaSetu provides AI-assisted information. This is not legal advice.")
    c.showPage()
    c.save()
    return buf.getvalue()


def ensure_session_state() -> None:
    """Initialize required Streamlit session keys."""
    defaults = {
        "active_dispute": None,
        "prediction": None,
        "similar_cases": [],
        "negotiation_state": None,
        "language": "en",
        "theme_key": "theme_courtroom",
        "ocr_invoice_rows": [],
        "filing_docs_ready": False,
        "voice_state": None,
        "voice_transcript": "",
        "negotiation_voice_text": "",
        "translation_cache": {},
        "saved_cases": {},
        "demo_tour_active": False,
        "demo_tour_step": None,
        "case_analysis": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def t(key: str, **kwargs) -> str:
    """Translate key for active UI language."""
    return tr(st.session_state.get("language", "en"), key, **kwargs)


def render_ui_banner(title: str, subtitle: str, chips: list[str] | None = None) -> None:
    """Render a consistent banner block for major page sections."""
    chip_html = ""
    if chips:
        chip_html = "".join(f'<span class="ui-chip">{item}</span>' for item in chips if item)
    st.markdown(
        f"""
        <div class="ui-banner">
          <div class="ui-banner-title">{title}</div>
          <div class="ui-banner-sub">{subtitle}</div>
          <div>{chip_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_theme(theme_key: str) -> None:
    """Inject CSS variables for selected theme."""
    theme = THEMES.get(theme_key, THEMES["theme_courtroom"])
    primary = theme["primary"]
    accent = theme["accent"]
    bg = theme["bg"]
    card = theme["card"]
    text = theme["text"]
    muted = theme["muted"]
    st.markdown(
        f"""
        <style>
        /* ===== GLOBAL ===== */
        .stApp {{
          background: {bg};
          color: {text};
          font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        }}
        h1, h2, h3, h4 {{
          color: {primary} !important;
          font-weight: 700 !important;
        }}

        /* ===== SIDEBAR ===== */
        section[data-testid="stSidebar"] {{
          background: linear-gradient(180deg, {primary} 0%, {primary}E6 100%);
        }}
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {{
          color: #FFFFFF !important;
          font-size: 24px !important;
        }}
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stRadio label {{
          color: #E5E7EB !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{
          color: #FFFFFF !important;
        }}
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {{
          background: rgba(255,255,255,0.12);
          border-color: rgba(255,255,255,0.2);
          color: #FFFFFF;
        }}
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * {{
          color: #FFFFFF !important;
        }}
        section[data-testid="stSidebar"] .stSelectbox svg {{
          fill: #FFFFFF;
        }}
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
          color: rgba(255,255,255,0.75) !important;
          transition: all 0.2s;
        }}
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {{
          color: #FFFFFF !important;
        }}
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"],
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] div[data-checked="true"] label {{
          color: {accent} !important;
          font-weight: 700;
        }}
        section[data-testid="stSidebar"] hr {{
          border-color: rgba(255,255,255,0.15) !important;
        }}
        section[data-testid="stSidebar"] .stAlert {{
          background: rgba(255,255,255,0.1) !important;
          border: none !important;
          color: #FFFFFF !important;
        }}
        section[data-testid="stSidebar"] .stAlert p {{
          color: #FFFFFF !important;
        }}
        section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {{
          color: rgba(255,255,255,0.55) !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {{
          gap: 0.15rem !important;
        }}
        section[data-testid="stSidebar"] .element-container {{
          margin-bottom: 2px !important;
        }}
        section[data-testid="stSidebar"] .stSelectbox {{
          margin-bottom: 4px !important;
        }}
        section[data-testid="stSidebar"] .stRadio {{
          margin-bottom: 2px !important;
        }}
        section[data-testid="stSidebar"] hr {{
          margin: 6px 0 !important;
        }}

        /* ===== HERO BANNER ===== */
        .hero {{
          background: linear-gradient(135deg, {primary} 0%, {primary}CC 100%);
          color: #fff;
          border-radius: 16px;
          padding: 28px 32px;
          margin-bottom: 20px;
          box-shadow: 0 4px 16px rgba(30,45,77,0.15);
        }}
        .hero .card-title {{
          color: #FFFFFF !important;
          font-size: 26px;
          font-weight: 700;
          margin-bottom: 6px;
        }}
        .hero div {{
          color: rgba(255,255,255,0.9);
        }}

        /* ===== METRIC CARDS (CRITICAL FIX) ===== */
        div[data-testid="stMetric"] {{
          background: {card};
          border: 1px solid #E5E7EB;
          border-radius: 12px;
          padding: 16px 20px;
          box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        }}
        div[data-testid="stMetric"] label {{
          color: {muted} !important;
          font-size: 13px !important;
          font-weight: 500 !important;
          text-transform: uppercase;
          letter-spacing: 0.3px;
        }}
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
          color: {primary} !important;
          font-size: 26px !important;
          font-weight: 700 !important;
        }}
        div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {{
          color: {accent} !important;
        }}

        /* ===== SECTION CARDS ===== */
        .section-card {{
          background: {card};
          border: 1px solid #E5E7EB;
          border-radius: 12px;
          padding: 16px 18px;
          margin-bottom: 10px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}
        .card-title {{
          color: {primary};
          font-size: 18px;
          font-weight: 700;
          margin-bottom: 4px;
        }}
        .metric-label {{
          color: {muted};
          font-size: 12px;
          margin-bottom: 4px;
        }}
        .subtle {{
          color: {muted};
        }}

        /* ===== UI BANNER ===== */
        .ui-banner {{
          background: linear-gradient(120deg, {primary}12 0%, {accent}14 100%);
          border: 1px solid #E5E7EB;
          border-radius: 12px;
          padding: 14px 16px;
          margin: 8px 0 14px 0;
        }}
        .ui-banner-title {{
          color: {primary};
          font-size: 18px;
          font-weight: 700;
          margin-bottom: 2px;
        }}
        .ui-banner-sub {{
          color: {muted};
          font-size: 13px;
          margin-bottom: 8px;
        }}
        .ui-chip {{
          display: inline-block;
          font-size: 11px;
          color: {primary};
          border: 1px solid {primary}33;
          background: {primary}11;
          border-radius: 14px;
          padding: 2px 8px;
          margin-right: 6px;
          margin-bottom: 4px;
        }}

        /* ===== MODULE CARDS (HOME) ===== */
        .module-card {{
          background: {card};
          border: 1px solid #E5E7EB;
          border-radius: 14px;
          padding: 28px 20px 24px;
          text-align: center;
          transition: all 0.25s ease;
          box-shadow: 0 1px 4px rgba(0,0,0,0.04);
          min-height: 200px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }}
        .module-card:hover {{
          box-shadow: 0 8px 24px rgba(30,45,77,0.12);
          transform: translateY(-3px);
          border-color: {accent};
        }}
        .module-card .module-icon {{
          font-size: 40px;
          margin-bottom: 12px;
        }}
        .module-card .module-name {{
          color: {primary};
          font-size: 17px;
          font-weight: 700;
          margin-bottom: 8px;
        }}
        .module-card .module-desc {{
          color: {muted};
          font-size: 13px;
          line-height: 1.5;
          margin-bottom: 12px;
        }}
        .module-card .module-tag {{
          display: inline-block;
          background: {primary}14;
          color: {primary};
          font-size: 11px;
          font-weight: 600;
          padding: 4px 12px;
          border-radius: 20px;
        }}

        /* ===== EMPTY STATES ===== */
        .empty-state {{
          background: {card};
          border: 2px dashed #D1D5DB;
          border-radius: 16px;
          padding: 48px 32px;
          text-align: center;
          margin: 40px auto;
          max-width: 560px;
        }}
        .empty-state .empty-icon {{
          font-size: 56px;
          margin-bottom: 16px;
          opacity: 0.7;
        }}
        .empty-state .empty-title {{
          color: {primary};
          font-size: 20px;
          font-weight: 700;
          margin-bottom: 8px;
        }}
        .empty-state .empty-desc {{
          color: {muted};
          font-size: 14px;
          line-height: 1.6;
          margin-bottom: 20px;
        }}
        .empty-state .empty-steps {{
          text-align: left;
          display: inline-block;
          color: {text};
          font-size: 13px;
          line-height: 2.2;
        }}

        /* ===== BUTTONS ===== */
        .stButton > button {{
          background: {card};
          color: {primary};
          border: 1.5px solid {primary};
          border-radius: 8px;
          font-weight: 600;
          padding: 8px 24px;
          transition: all 0.2s ease;
        }}
        .stButton > button:hover {{
          background: {primary};
          color: #FFFFFF;
          border-color: {primary};
        }}
        .stDownloadButton > button {{
          background: {primary} !important;
          color: #FFFFFF !important;
          border: none !important;
          border-radius: 8px !important;
          font-weight: 600 !important;
          transition: background 0.2s;
        }}
        .stDownloadButton > button:hover {{
          background: {accent} !important;
        }}
        .stLinkButton > a {{
          color: {primary} !important;
          background: {card} !important;
          border: 1.5px solid {primary} !important;
          border-radius: 8px !important;
          text-decoration: none !important;
          font-weight: 600 !important;
          padding: 8px 24px !important;
          display: inline-block !important;
        }}
        .stLinkButton > a:hover {{
          background: {primary} !important;
          color: #FFFFFF !important;
        }}

        /* ===== TABS ===== */
        .stTabs [data-baseweb="tab-list"] {{
          gap: 4px;
          background: {card};
          border-radius: 10px;
          padding: 4px;
          border: 1px solid #E5E7EB;
        }}
        .stTabs [data-baseweb="tab"] {{
          border-radius: 8px;
          color: {muted};
          font-weight: 500;
          padding: 8px 16px;
        }}
        .stTabs [aria-selected="true"] {{
          background: {primary} !important;
          color: #FFFFFF !important;
          border-radius: 8px;
        }}

        /* ===== INPUTS ===== */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {{
          border-radius: 8px;
          border: 1.5px solid #D1D5DB;
          color: {text};
          background: {card};
        }}
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {{
          border-color: {primary};
          box-shadow: 0 0 0 2px rgba(30,45,77,0.1);
        }}

        /* ===== EXPANDERS ===== */
        .streamlit-expanderHeader {{
          background: {card};
          border: 1px solid #E5E7EB;
          border-radius: 10px !important;
          color: {text} !important;
          font-weight: 500;
        }}

        /* ===== DATAFRAMES ===== */
        .stDataFrame {{
          border: 1px solid #E5E7EB;
          border-radius: 10px;
          overflow: hidden;
        }}

        /* ===== ALERTS ===== */
        div[data-testid="stAlert"] {{
          border-radius: 10px;
        }}
        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] span,
        div[data-testid="stAlert"] div {{
          color: {text} !important;
        }}

        /* ===== PROGRESS BAR ===== */
        .stProgress > div > div > div {{
          background: {accent};
        }}

        /* ===== PLOTLY CHARTS ===== */
        .stPlotlyChart {{
          border-radius: 12px;
          overflow: hidden;
        }}

        /* ===== SIDEBAR CASE INDICATOR ===== */
        .sidebar-case-badge {{
          background: rgba(185,151,61,0.15);
          border-left: 3px solid {accent};
          padding: 8px 12px;
          border-radius: 0 8px 8px 0;
          margin: 8px 0;
          font-size: 13px;
          color: #FFFFFF;
        }}
        .sidebar-case-badge strong {{
          color: {accent};
        }}

        /* ===== RESPONSIVE ===== */
        @media (max-width: 900px) {{
          .hero {{
            padding: 20px 16px;
          }}
          .hero .card-title {{
            font-size: 22px;
          }}
          .module-card {{
            min-height: 170px;
            padding: 18px 12px;
          }}
          .ui-banner {{
            padding: 12px;
          }}
          div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
            font-size: 22px !important;
          }}
        }}

        /* ===== HIDE STREAMLIT BRANDING ===== */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def load_services() -> Dict:
    """Instantiate reusable service objects."""
    llm = LLMClient()
    interest = InterestCalculator("data/legal/rbi_bank_rates.json")
    fetcher = UdyamFetcher("data/msme/sample_disputes.json")
    gst = GSTValidator()
    eligibility = EligibilityChecker()
    builder = DisputeBuilder(fetcher, gst, interest, eligibility, llm)
    predictor = OutcomePredictor()
    similarity = CaseSimilarityEngine("data/legal/legal_precedents.json", config.EMBEDDING_MODEL)
    risk = BuyerRiskScorer("data/synthetic/buyer_profiles.csv")
    timeline = TimelineEstimator("data/legal/msefc_directory.json")
    negotiation = NegotiationEngine(llm, predictor, "data/odr/negotiation_templates.json")
    drafter = SettlementDrafter(llm, "data/odr/settlement_templates.json")
    buyer_simulator = BuyerSimulator(llm_client=llm)
    bhashini = BhashiniClient()
    conversation = ConversationEngine(llm_client=llm, dispute_builder=builder, bhashini_client=bhashini)
    return {
        "llm": llm,
        "interest": interest,
        "builder": builder,
        "predictor": predictor,
        "similarity": similarity,
        "risk": risk,
        "timeline": timeline,
        "negotiation": negotiation,
        "drafter": drafter,
        "buyer_simulator": buyer_simulator,
        "bhashini": bhashini,
        "conversation": conversation,
    }


def render_home(services: Dict) -> None:
    """Render clean home overview."""
    st.markdown(
        f"""
        <div class="hero">
          <div class="card-title">{t('hero_title')}</div>
          <div>{t('hero_desc')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cards = st.columns(4)
    modules = [
        ("📋", "VaadPatra", t("vaadpatra_subtitle"), t("vaadpatra_tag"), "file_dispute"),
        ("🔮", "NyayaPredictor", t("nyayapredictor_subtitle"), t("nyayapredictor_tag"), "file_dispute"),
        ("🤝", "SamvadAI", t("samvadai_subtitle"), t("samvadai_tag"), "negotiate"),
        ("📊", "RecoveryTracker", t("vasoolitracker_subtitle"), t("vasoolitracker_tag"), "dashboard"),
    ]
    for idx, (icon, name, desc, tag, nav_key) in enumerate(modules):
        with cards[idx]:
            st.markdown(
                f"""
                <div class="module-card">
                  <div class="module-icon">{icon}</div>
                  <div class="module-name">{name}</div>
                  <div class="module-desc">{desc}</div>
                  <div class="module-tag">{tag}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Open {name}", key=f"nav_{nav_key}_{idx}", use_container_width=True):
                st.session_state["_nav_target_key"] = nav_key
                st.rerun()

    st.markdown(f"### {t('quick_stats')}")
    metrics = DisputeAnalytics("data/synthetic/disputes.csv").get_overview_metrics()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t("total_disputes"), f"{metrics['total_disputes']:,}")
    m2.metric(t("amount_disputed"), f"₹{metrics['total_amount_disputed']:,.0f}")
    m3.metric(t("recovery_rate"), f"{metrics['recovery_rate']:.1f}%")
    m4.metric(t("avg_days"), str(metrics["avg_resolution_days"]))

    st.markdown(f"### {t('quick_interest_title')}")
    c1, c2 = st.columns(2)
    principal = c1.number_input(t("principal_amount"), min_value=1000.0, value=500000.0, step=1000.0)
    overdue_days = c2.number_input(t("days_overdue"), min_value=1, value=120, step=1)
    quick_interest = services["interest"].calculate_quick(principal, int((overdue_days + 29) / 30))
    st.success(f"{t('estimated_interest')}: {format_inr(quick_interest)} | {t('total')}: {format_inr(principal + quick_interest)}")
    st.caption(t("disclaimer"))


def render_file_dispute(services: Dict) -> None:
    """Render filing experience with voice + manual modes."""
    st.title(t("file_dispute"))
    render_demo_tour_hint("file_dispute")
    render_ui_banner(
        t("file_banner_title"),
        t("file_banner_subtitle"),
        chips=[t("chip_voice_asr_tts"), t("chip_ocr_extraction"), t("chip_subcategory_classifier"), t("chip_document_checklist")],
    )
    samples = load_json("data/msme/sample_disputes.json", [])
    sample_map = {row["mse"]["udyam_number"]: row for row in samples[:30]}
    classifier = DisputeClassifier()
    checker = DocumentChecker()

    voice_tab, manual_tab = st.tabs(["🎙️ Voice Filing", "📝 Manual Filing"])

    with voice_tab:
        st.subheader("🎙️ Voice Filing Assistant")
        st.caption(t("voice_caption_hint"))
        bhashini = services["bhashini"]
        conversation = services["conversation"]
        if st.session_state.get("voice_state") is None or st.session_state["voice_state"].get("language") != st.session_state["language"]:
            st.session_state["voice_state"] = conversation.start_session(language=st.session_state["language"])

        state = st.session_state["voice_state"]
        step_order = ["udyam", "buyer_name", "buyer_gstin", "invoices", "confirm", "completed"]
        step_labels = {
            "udyam": "Step 1/5: Tell us your Udyam number",
            "buyer_name": "Step 2/5: Tell us buyer name",
            "buyer_gstin": "Step 3/5: Tell us buyer GSTIN",
            "invoices": "Step 4/5: Tell us invoice amounts",
            "confirm": "Step 5/5: Confirm filing",
            "completed": "Completed",
        }
        current_step = state.get("step", "udyam")
        current_idx = step_order.index(current_step) if current_step in step_order else 0
        st.progress(min(1.0, current_idx / 5.0))
        st.caption(step_labels.get(current_step, "Step 1/5"))

        if not bhashini.is_available():
            st.info("Voice services connecting... Using text mode")

        recorded_audio = st.audio_input("Speak your dispute details")
        if recorded_audio is not None:
            encoded = base64.b64encode(recorded_audio.getvalue()).decode("utf-8")
            asr = bhashini.speech_to_text(encoded, language=normalize_speech_lang(st.session_state["language"]))
            st.session_state["voice_transcript"] = asr.get("text", "") or st.session_state.get("voice_transcript", "")
            if asr.get("source") == "fallback":
                st.info("Voice services connecting... Using text mode")

        transcript = st.text_area(
            "Transcription (editable)",
            value=st.session_state.get("voice_transcript", ""),
            key="voice_transcription_editor",
            height=120,
        )
        st.session_state["voice_transcript"] = transcript

        if st.button("Process Voice Input", key="process_voice_input"):
            if transcript.strip():
                with st.spinner("Processing voice filing input..."):
                    updated_state, response_text = conversation.process_message(state, transcript)
                st.session_state["voice_state"] = updated_state
                st.session_state["voice_system_message"] = response_text
                st.success(response_text)
                st.toast("Voice step captured.")
            else:
                st.warning("Please speak or enter transcription text first.")

        latest_message = st.session_state.get("voice_system_message", state.get("greeting", ""))
        if latest_message:
            st.write(f"Assistant: {latest_message}")
            if st.button("🔊 Listen", key="voice_assistant_tts"):
                tts = bhashini.text_to_speech(latest_message, language=normalize_speech_lang(st.session_state["language"]))
                if tts.get("audio"):
                    try:
                        st.audio(base64.b64decode(tts["audio"]))
                    except Exception:
                        st.info("Audio playback unavailable in current mode.")
                else:
                    st.info("Audio playback unavailable in current mode.")

        state = st.session_state["voice_state"]
        extracted = {
            "udyam_number": state.get("udyam_number"),
            "buyer_name": state.get("buyer_info", {}).get("buyer_name"),
            "buyer_gstin": state.get("buyer_info", {}).get("gstin"),
            "invoice_amounts": [row.get("amount_outstanding", row.get("invoice_amount")) for row in state.get("invoices", [])],
            "step": state.get("step"),
        }
        st.markdown("Extracted Fields")
        st.json(extracted, expanded=False)

    with manual_tab:
        st.caption(t("manual_caption_hint"))
        voice_state = st.session_state.get("voice_state") or {}
        voice_buyer = voice_state.get("buyer_info", {})
        voice_invoices = voice_state.get("invoices", [])

        st.markdown(f"### {t('step_1')}")
        c1, c2 = st.columns([2, 3])
        default_udyam = voice_state.get("udyam_number") or "UDYAM-RJ-01-1000001"
        udyam_input = c1.text_input(t("udyam_number"), value=default_udyam, key="manual_udyam")
        sample_pick = c2.selectbox(t("use_demo_mse"), ["None"] + list(sample_map.keys()), key="manual_sample_pick")
        if sample_pick != "None":
            udyam_input = sample_pick
        mse_profile = services["builder"].udyam_fetcher.fetch_by_udyam_number(udyam_input)
        if mse_profile:
            st.json(mse_profile.model_dump(), expanded=False)
        udyam_doc = st.file_uploader(
            "Upload Udyam certificate (optional, PDF/JPG/PNG)",
            type=["pdf", "jpg", "jpeg", "png"],
            key="manual_udyam_doc_upload",
        )

        st.markdown(f"### {t('step_2')}")
        b1, b2, b3, b4 = st.columns(4)
        buyer_name = b1.text_input(t("buyer_name"), value=voice_buyer.get("buyer_name", "XYZ Engineering Pvt Ltd"), key="manual_buyer_name")
        default_type = voice_buyer.get("buyer_type", "Private Ltd")
        default_type_idx = config.BUYER_TYPES.index(default_type) if default_type in config.BUYER_TYPES else 3
        buyer_type = b2.selectbox(t("buyer_type"), config.BUYER_TYPES, index=default_type_idx, key="manual_buyer_type")
        buyer_gstin = b3.text_input(t("buyer_gstin"), value=voice_buyer.get("gstin", "08AABCX1234E1ZP"), key="manual_buyer_gstin")
        buyer_state = b4.text_input(t("buyer_state"), value=voice_buyer.get("state", "Rajasthan"), key="manual_buyer_state")

        if st.button(t("check_buyer_risk"), use_container_width=False, key="manual_check_risk"):
            risk_score = services["risk"].score_buyer(buyer_gstin, buyer_name, buyer_type)
            r1, r2 = st.columns(2)
            r1.metric(t("check_buyer_risk"), f"{risk_score.risk_score}/100")
            r2.metric("Category", risk_badge(risk_score.risk_category))
            st.write(risk_score.factors)
            st.toast("Buyer risk score generated.")

        st.markdown(f"### {t('step_3')}")
        agreement_c1, agreement_c2 = st.columns(2)
        has_agreement = agreement_c1.checkbox(t("written_agreement"), value=True, key="manual_has_agreement")
        agreed_days = agreement_c2.slider(t("agreed_days"), min_value=1, max_value=45, value=45, key="manual_agreed_days")
        credit_days = min(agreed_days, 45) if has_agreement else 15

        invoice_uploads = st.file_uploader(
            "Upload invoice images for OCR (optional)",
            type=["jpg", "jpeg", "png", "pdf"],
            accept_multiple_files=True,
            key="manual_invoice_ocr_upload",
        )
        if st.button("Extract Invoice Data (OCR)", key="manual_extract_ocr"):
            if not invoice_uploads:
                st.warning("Please upload at least one invoice image/PDF for OCR.")
            else:
                paths = []
                ocr_client = DocumentOCR(llm_client=services["llm"])
                try:
                    for upload in invoice_uploads:
                        suffix = Path(upload.name).suffix or ".bin"
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                            tmp.write(upload.getbuffer())
                            paths.append(tmp.name)
                    st.session_state["ocr_invoice_rows"] = ocr_client.batch_extract(paths)
                    if any(row.get("source") == "mock_fallback" for row in st.session_state["ocr_invoice_rows"]):
                        st.info("OCR engine loading... Using demo data.")
                    st.toast("OCR extraction complete.")
                finally:
                    for path in paths:
                        try:
                            Path(path).unlink(missing_ok=True)
                        except Exception:
                            pass

        if st.session_state.get("ocr_invoice_rows"):
            st.markdown("OCR Extracted Fields")
            st.dataframe(pd.DataFrame(st.session_state["ocr_invoice_rows"]), use_container_width=True, height=180)

        default_count = len(voice_invoices) if voice_invoices else 3
        invoice_count = st.number_input(t("invoice_count"), min_value=1, max_value=5, value=max(1, min(5, default_count)), key="manual_invoice_count")
        invoices = []
        running_interest = 0.0
        for i in range(int(invoice_count)):
            source_invoice = voice_invoices[i] if i < len(voice_invoices) else {}
            with st.expander(f"{t('invoice_number')} {i+1}", expanded=(i == 0)):
                i1, i2, i3 = st.columns(3)
                inv_no = i1.text_input(
                    f"{t('invoice_number')} {i+1}",
                    value=source_invoice.get("invoice_number", f"INV-{i+1:03d}"),
                    key=f"manual_inv_no_{i}",
                )
                inv_default_date = source_invoice.get("invoice_date")
                inv_date_val = date.fromisoformat(inv_default_date) if isinstance(inv_default_date, str) and "-" in inv_default_date else date.today() - timedelta(days=120 + i * 25)
                inv_date = i2.date_input(f"{t('invoice_date')} {i+1}", value=inv_date_val, key=f"manual_inv_date_{i}")
                inv_amount = i3.number_input(
                    f"{t('invoice_amount')} {i+1}",
                    min_value=1000.0,
                    value=float(source_invoice.get("invoice_amount", 200000.0 - i * 30000)),
                    step=1000.0,
                    key=f"manual_inv_amt_{i}",
                )
                due_date = inv_date + timedelta(days=credit_days)
                days_overdue = max(0, (date.today() - due_date).days)
                preview = services["interest"].calculate_interest(
                    principal=inv_amount,
                    start_date=due_date.isoformat(),
                    end_date=date.today().isoformat(),
                )
                running_interest += preview.interest_amount
                st.caption(f"Due date: {due_date.isoformat()} | Overdue: {overdue_badge(days_overdue)}")
                invoices.append(
                    {
                        "invoice_number": inv_no,
                        "invoice_date": inv_date.isoformat(),
                        "invoice_amount": inv_amount,
                        "goods_services_description": "Goods/services supplied",
                        "delivery_date": (inv_date + timedelta(days=2)).isoformat(),
                        "acceptance_date": (inv_date + timedelta(days=5)).isoformat(),
                        "po_number": f"PO-{i+1:03d}",
                        "amount_paid": 0.0,
                        "amount_outstanding": inv_amount,
                    }
                )

        total_outstanding = sum(row["amount_outstanding"] for row in invoices)
        st.caption(f"{t('total')}: {format_inr(total_outstanding)}")
        st.caption(f"Interest (Section 16): {format_inr(running_interest)}")

        dispute_description = st.text_area(
            "Dispute summary",
            value=f"{buyer_name} has delayed payment against invoices raised by the MSME supplier.",
            key="manual_dispute_summary",
        )
        max_days = 0
        if invoices:
            max_days = max(0, int(max((date.today() - date.fromisoformat(row["acceptance_date"])).days for row in invoices)))
        invoice_snapshot = {
            "total_amount": total_outstanding,
            "amount_paid": sum(row.get("amount_paid", 0.0) for row in invoices),
            "days_overdue": max_days,
            "has_agreement": has_agreement,
        }
        classification = classifier.classify_dispute(dispute_description, invoice_snapshot, llm_client=services["llm"])
        st.markdown("#### Dispute Sub-Category")
        st.info(
            f"{classification['category']} | confidence {classification['confidence']:.2f} | "
            f"Sections: {', '.join(classification['applicable_sections'])}"
        )
        st.caption(classification.get("reasoning", ""))

        uploaded_docs = []
        if udyam_doc is not None:
            uploaded_docs.append(udyam_doc.name)
        if invoice_uploads:
            uploaded_docs.extend(upload.name for upload in invoice_uploads)
        uploaded_docs.extend([row.get("invoice_number", "") for row in invoices])
        doc_check = checker.check_documents(classification["category"], uploaded_docs, dispute=None)
        st.markdown("#### Document Checklist")
        doc_rows = doc_check["mandatory"] + doc_check["recommended"]
        cols = st.columns(4)
        for idx, row in enumerate(doc_rows):
            color = "#E8F5E9" if row["status"] == "uploaded" else ("#FDECEC" if row["severity"] == "critical" else "#FFF8E1")
            with cols[idx % 4]:
                st.markdown(
                    f"""
                    <div style="background:{color}; border:1px solid #E5E7EB; border-radius:10px; padding:10px; margin-bottom:8px;">
                      <div><strong>{row['icon']} {row['doc']}</strong></div>
                      <div style="font-size:12px;">{row['status']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.progress(float(doc_check["completeness_score"]))
        st.caption(f"Completeness Score: {doc_check['completeness_score']*100:.1f}%")
        if doc_check["missing_critical"]:
            st.warning(
                "Missing critical documents: "
                + ", ".join(doc_check["missing_critical"])
                + ". Upload delivery challan/receipt or equivalent proof to strengthen case."
            )
        st.caption(doc_check["strength_impact"])

        st.markdown(f"### {t('step_4')}")
        if st.button(t("assess_case"), use_container_width=True, key="manual_assess_case"):
            try:
                with st.spinner("Analyzing your case..."):
                    progress = st.progress(0.05)
                    dispute = services["builder"].build_dispute(
                        udyam_number=udyam_input,
                        buyer_info={
                            "buyer_name": buyer_name,
                            "buyer_type": buyer_type,
                            "gstin": buyer_gstin,
                            "state": buyer_state,
                            "district": voice_buyer.get("district", "Unknown"),
                            "address": voice_buyer.get("address", "Address pending confirmation"),
                        },
                        invoices=invoices,
                        has_agreement=has_agreement,
                        agreed_days=agreed_days,
                        uploaded_documents=uploaded_docs,
                    )
                    progress.progress(0.35)
                    similar = services["similarity"].find_similar_cases(dispute, top_k=5)
                    if not similar:
                        st.info("No historical data. Using synthetic dataset.")
                    prediction = services["predictor"].predict(dispute, similar_cases=similar)
                    timeline = services["timeline"].estimate_timeline(dispute, prediction.recommended_strategy)
                    progress.progress(0.7)
                    invoice_details = "\n".join(
                        f"- {row['invoice_number']}: amount {row['invoice_amount']}, date {row['invoice_date']}" for row in invoices
                    )
                    analysis_prompt = DISPUTE_ANALYSIS_TEMPLATE.format(
                        mse_name=dispute.mse.enterprise_name,
                        udyam_number=dispute.mse.udyam_number,
                        enterprise_type=dispute.mse.enterprise_type,
                        major_activity=dispute.mse.major_activity,
                        udyam_date=dispute.mse.date_of_udyam,
                        state=dispute.mse.state,
                        buyer_name=buyer_name,
                        buyer_type=buyer_type,
                        buyer_gstin=buyer_gstin,
                        buyer_state=buyer_state,
                        invoice_details=invoice_details,
                        has_agreement=has_agreement,
                        agreed_days=agreed_days,
                    )
                    if services["llm"].health_check():
                        case_analysis = services["llm"].generate_json(analysis_prompt)
                    else:
                        case_analysis = {"status": "offline", "message": "LLM service offline. Using rule-based mode."}
                    progress.progress(1.0)

                st.session_state["active_dispute"] = dispute
                st.session_state["prediction"] = prediction
                st.session_state["similar_cases"] = similar
                st.session_state["filing_docs_ready"] = False
                st.session_state["case_analysis"] = case_analysis if isinstance(case_analysis, dict) else {}
                saved = st.session_state.get("saved_cases", {})
                saved[dispute.case_id] = {"dispute": dispute, "prediction": prediction, "similar_cases": similar}
                st.session_state["saved_cases"] = saved
                try:
                    db = DatabaseManager()
                    db.save_dispute(dispute, prediction)
                except Exception:
                    pass

                if prediction.settlement_probability >= 0.8:
                    strength = t("strength_strong")
                elif prediction.settlement_probability >= 0.5:
                    strength = t("strength_moderate")
                else:
                    strength = t("strength_weak")

                st.success(f"{t('eligibility_valid')} | {strength}")
                st.toast("Case assessment complete.")
                c1, c2, c3 = st.columns(3)
                c1.metric(t("settlement_probability"), f"{prediction.settlement_probability * 100:.1f}%")
                c2.metric(t("expected_recovery"), format_inr(prediction.predicted_recovery_amount))
                c3.metric(t("timeline"), f"{timeline['optimistic']} - {timeline['pessimistic']} days")

                gauge = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=prediction.settlement_probability * 100,
                        title={"text": "Settlement Probability (%)"},
                        gauge={
                            "axis": {"range": [0, 100]},
                            "bar": {"color": "#1E2D4D"},
                            "steps": [
                                {"range": [0, 50], "color": "#FBE9E7"},
                                {"range": [50, 80], "color": "#FFF9C4"},
                                {"range": [80, 100], "color": "#E8F5E9"},
                            ],
                        },
                    )
                )
                st.plotly_chart(gauge, use_container_width=True)
                st.progress(min(100, max(0, int(round(prediction.predicted_recovery_percentage)))))
                st.write(f"{t('strategy')}: `{prediction.recommended_strategy}`")
                st.caption(f"Model confidence: {prediction.confidence * 100:.1f}%")

                if prediction.feature_contributions:
                    contrib_df = pd.DataFrame(prediction.feature_contributions)
                    contrib_df["impact_pct"] = contrib_df["impact"] * 100
                    waterfall = go.Figure(
                        go.Waterfall(
                            name="Drivers",
                            orientation="v",
                            x=contrib_df["feature"],
                            measure=["relative"] * len(contrib_df),
                            y=contrib_df["impact_pct"],
                            text=[f"{v:+.2f}%" for v in contrib_df["impact_pct"]],
                            connector={"line": {"color": "#9CA3AF"}},
                        )
                    )
                    waterfall.update_layout(title="Prediction Explainability (Feature Contribution %)")
                    st.plotly_chart(waterfall, use_container_width=True)
                    st.info(services["predictor"].explain_prediction(dispute, prediction))

                if prediction.similar_case_summary:
                    st.caption(prediction.similar_case_summary)

                avg_case = {"recovery_percentage": 65.0, "resolution_days": 95}
                try:
                    outcomes = pd.read_csv("data/synthetic/case_outcomes.csv")
                    if not outcomes.empty:
                        avg_case["recovery_percentage"] = float(outcomes["recovery_percentage"].mean())
                        avg_case["resolution_days"] = int(outcomes["resolution_days"].mean())
                except Exception:
                    pass

                best_similar = max(similar, key=lambda row: float(row.get("recovery_percentage", 0)), default={})
                cmp1, cmp2, cmp3 = st.columns(3)
                cmp1.metric("Your Case", f"{prediction.predicted_recovery_percentage:.1f}% recovery")
                cmp2.metric("Average MSME Case", f"{avg_case['recovery_percentage']:.1f}% recovery")
                cmp3.metric(
                    "Best Similar Case",
                    f"{float(best_similar.get('recovery_percentage', prediction.predicted_recovery_percentage)):.1f}% recovery",
                )
                st.markdown("#### Case Analysis")
                if st.session_state["case_analysis"]:
                    st.json(st.session_state["case_analysis"], expanded=False)
                st.markdown(f"**{t('top_similar_cases')}**")
                cards = st.columns(max(1, min(3, len(similar))))
                for idx, case in enumerate(similar[:3]):
                    with cards[idx]:
                        st.markdown(
                            f"""
                            <div class="section-card">
                              <div class="card-title">{case['case_id']}</div>
                              <div>Outcome: {case['outcome']}</div>
                              <div>Recovery: {case['recovery_percentage']}%</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            except Exception:
                st.error("Assessment failed. Please verify details and retry.")

        st.markdown(f"### {t('step_5')}")
        dispute = st.session_state.get("active_dispute")
        if dispute:
            st.success(services["builder"].generate_filing_summary(dispute))
            calc = services["interest"].calculate_interest(dispute.total_principal, start_date=(date.today() - timedelta(days=90)).isoformat())
            breakdown_df = pd.DataFrame(calc.calculation_breakdown)
            st.dataframe(breakdown_df, use_container_width=True, height=260)
            if st.button("Generate Filing Documents", key="manual_generate_docs"):
                st.session_state["filing_docs_ready"] = True
                st.toast("Filing document pack generated.")

            if st.session_state.get("filing_docs_ready"):
                demand_pdf = build_demand_notice_pdf(dispute)
                msefc_pdf = build_msefc_reference_pdf(dispute)
                interest_xlsx = build_interest_calculation_excel(calc)
                d1, d2, d3 = st.columns(3)
                d1.download_button(
                    "Download Demand Notice (PDF)",
                    data=demand_pdf,
                    file_name=f"{dispute.case_id}_demand_notice.pdf",
                    mime="application/pdf",
                )
                d2.download_button(
                    "Download MSEFC Reference (PDF)",
                    data=msefc_pdf,
                    file_name=f"{dispute.case_id}_msefc_reference.pdf",
                    mime="application/pdf",
                )
                d3.download_button(
                    t("download_interest_sheet"),
                    data=interest_xlsx,
                    file_name=f"{dispute.case_id}_interest_calculation.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            odr_prefill = urlencode({"case_id": dispute.case_id, "claim": f"{dispute.total_claim:.2f}", "state": dispute.msefc_state})
            st.link_button(t("file_on_odr"), f"{config.ODR_PORTAL_URL}?{odr_prefill}")
    st.caption(t("disclaimer"))
def render_negotiate(services: Dict) -> None:
    """Render negotiation workspace with simulation, sentiment, and legal docs."""
    st.title(t("negotiate"))
    render_demo_tour_hint("negotiate")
    render_ui_banner(
        t("negotiation_banner_title"),
        t("negotiation_banner_subtitle"),
        chips=[t("chip_buyer_simulator"), t("chip_tactic_detection"), t("chip_sentiment_analytics"), t("chip_settlement_package")],
    )
    dispute = st.session_state.get("active_dispute")
    prediction = st.session_state.get("prediction")
    if not dispute or not prediction:
        st.markdown(
            f"""
            <div class="empty-state">
              <div class="empty-icon">🤝</div>
              <div class="empty-title">{t('negotiate_empty_title')}</div>
              <div class="empty-desc">{t('negotiate_empty_desc')}</div>
              <div class="empty-steps">
                {t('negotiate_empty_step1')}<br>
                {t('negotiate_empty_step2')}<br>
                {t('negotiate_empty_step3')}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(t("disclaimer"))
        return

    if st.session_state["negotiation_state"] is None and st.button(t("init_negotiation")):
        st.session_state["negotiation_state"] = services["negotiation"].initialize_negotiation(dispute, prediction)
        st.session_state["settlement_agreement"] = None
        st.toast("Negotiation initialized.")

    state = st.session_state.get("negotiation_state")
    if not state:
        st.caption(t("disclaimer"))
        return
    if not services["llm"].health_check():
        st.warning("LLM service offline. Using rule-based mode.")

    top1, top2, top3 = st.columns(3)
    top1.metric(t("your_claim"), format_inr(dispute.total_claim))
    top1.metric("Minimum acceptable", format_inr(dispute.total_principal * 0.9))
    top2.metric(t("current_offer"), format_inr(state.mse_offer))
    top2.metric("AI strategy", state.mse_strategy.replace("_", " ").title())
    top3.metric(t("status_label"), state.status)
    top3.metric("Round", str(state.round_number))

    controls_left, controls_right = st.columns([2, 1])
    with controls_left:
        if st.button(t("generate_round1"), key="neg_round1"):
            out = services["negotiation"].generate_round(state, language=st.session_state.get("language", "en"))
            st.session_state["latest_negotiation_message"] = out.get("message", "")
            st.session_state["latest_sentiment"] = out.get("sentiment_analysis")
            st.toast("Round generated.")

    with controls_right:
        simulate_mode = st.toggle("🤖 AI Buyer Simulation (Demo Mode)", value=False, key="buyer_sim_toggle")
        profile = st.selectbox("Buyer Personality", ["cooperative", "stalling", "aggressive", "hardship", "ghosting"], key="buyer_profile")

    voice_col1, voice_col2 = st.columns([2, 1])
    with voice_col1:
        audio_response = st.audio_input("Speak buyer response (optional)")
        if audio_response is not None:
            encoded = base64.b64encode(audio_response.getvalue()).decode("utf-8")
            asr = services["bhashini"].speech_to_text(encoded, language=normalize_speech_lang(st.session_state.get("language", "en")))
            st.session_state["negotiation_voice_text"] = asr.get("text", "")
            if asr.get("source") == "fallback":
                st.info("Voice services connecting... Using text mode")

    with voice_col2:
        if st.button("🔊 Listen Latest", key="neg_tts"):
            latest = st.session_state.get("latest_negotiation_message", "")
            if latest:
                tts = services["bhashini"].text_to_speech(latest, language=normalize_speech_lang(st.session_state.get("language", "en")))
                if tts.get("audio"):
                    try:
                        st.audio(base64.b64decode(tts["audio"]))
                    except Exception:
                        st.info("Audio playback unavailable.")
                else:
                    st.info("Audio playback unavailable.")

    suggested_response = st.session_state.get("negotiation_voice_text", "")
    if simulate_mode and st.button("Simulate Buyer Response", key="simulate_buyer_btn"):
        with st.spinner("Buyer is responding..."):
            simulated = services["buyer_simulator"].simulate_response(
                dispute={
                    "claim": dispute.total_claim,
                    "buyer_type": dispute.buyer.buyer_type,
                    "days_overdue": max((inv.days_overdue for inv in dispute.invoices), default=0),
                },
                round_number=state.round_number,
                mse_offer=state.mse_offer,
                buyer_profile=profile,
            )
        suggested_response = simulated
        st.session_state["negotiation_voice_text"] = simulated

    buyer_response = st.text_input(t("buyer_response"), value=suggested_response, key="neg_buyer_input")
    detected_lang = detect_text_language(buyer_response)
    st.caption(f"Detected: {detected_lang.upper()} 🇮🇳")

    normalized_response = buyer_response
    target_lang = st.session_state.get("language", "en")
    if buyer_response.strip() and detected_lang != target_lang:
        translated = translate_cached(services, buyer_response, detected_lang, target_lang)
        st.info(f"Auto-translated ({detected_lang} → {target_lang}): {translated}")
        normalized_response = translated

    if st.button(t("process_response"), key="neg_process_response"):
        with st.spinner("Analyzing buyer tactic and generating next strategy..."):
            out = services["negotiation"].generate_round(
                state,
                buyer_response=normalized_response,
                language=target_lang,
            )
        st.session_state["latest_negotiation_message"] = out.get("message", "")
        st.session_state["latest_sentiment"] = out.get("sentiment_analysis")
        st.toast("Buyer response processed.")
        if out.get("should_escalate"):
            st.warning("Escalation recommended.")

    if state.messages:
        st.markdown(f"#### {t('negotiation_log')}")
        for idx, msg in enumerate(state.messages):
            role = "assistant" if msg.get("sender") == "mse" else "user"
            with st.chat_message(role):
                st.write(msg.get("message", ""))
                if st.button("🌐 Translate", key=f"translate_msg_{idx}"):
                    src_lang = detect_text_language(msg.get("message", ""))
                    translated_msg = translate_cached(services, msg.get("message", ""), src_lang, target_lang)
                    st.caption(translated_msg)

        rounds = sorted({int(msg.get("round", 0)) for msg in state.messages if msg.get("round") is not None})
        mse_series = {}
        buyer_series = {}
        for msg in state.messages:
            round_no = int(msg.get("round", 0))
            if msg.get("sender") == "mse" and msg.get("offer") is not None:
                mse_series[round_no] = float(msg["offer"])
            if msg.get("sender") == "buyer":
                offered = extract_offer_amount(msg.get("message", ""))
                if offered:
                    buyer_series[round_no] = offered
        if rounds and (mse_series or buyer_series):
            fig = go.Figure()
            if mse_series:
                fig.add_trace(go.Scatter(x=list(mse_series.keys()), y=list(mse_series.values()), mode="lines+markers", name="MSE Offer", line={"color": "#1E2D4D"}))
            if buyer_series:
                fig.add_trace(go.Scatter(x=list(buyer_series.keys()), y=list(buyer_series.values()), mode="lines+markers", name="Buyer Counter", line={"color": "#B9973D"}))
            fig.update_layout(title="Offer Convergence Over Rounds", xaxis_title="Round", yaxis_title="Amount (INR)")
            st.plotly_chart(fig, use_container_width=True)

    sentiment = st.session_state.get("latest_sentiment")
    if sentiment:
        st.markdown("### Sentiment Intelligence")
        s1, s2 = st.columns([1, 1])
        with s1:
            gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=float(sentiment.get("sentiment_score", 0.0)),
                    number={"valueformat": ".2f"},
                    title={"text": "Sentiment Score"},
                    gauge={
                        "axis": {"range": [-1, 1]},
                        "steps": [
                            {"range": [-1, -0.2], "color": "#FEE2E2"},
                            {"range": [-0.2, 0.2], "color": "#FEF3C7"},
                            {"range": [0.2, 1], "color": "#DCFCE7"},
                        ],
                        "bar": {"color": "#1E2D4D"},
                    },
                )
            )
            st.plotly_chart(gauge, use_container_width=True)
        with s2:
            bar = go.Figure(
                data=[
                    go.Bar(x=["Cooperation", "Aggression"], y=[float(sentiment.get("cooperation_level", 0.0)), float(sentiment.get("aggression_level", 0.0))], marker_color=["#16A34A", "#DC2626"])
                ]
            )
            bar.update_layout(title="Cooperation vs Aggression", yaxis=dict(range=[0, 1]))
            st.plotly_chart(bar, use_container_width=True)
        st.caption("Emotions: " + ", ".join(sentiment.get("emotions", [])))
        st.progress(min(100, max(0, int(float(sentiment.get("escalation_risk", 0.0)) * 100))))
        st.info(f"AI recommendation: {sentiment.get('recommended_response', 'Proceed with structured negotiation.')} | Tone: {sentiment.get('tone_description', 'N/A')}")

    sentiment_series = services["negotiation"].get_sentiment_series(state)
    if sentiment_series:
        series_df = pd.DataFrame(sentiment_series)
        st.line_chart(series_df.set_index("round")["sentiment_score"])
        buyer_tactics = [msg.get("tactic") for msg in state.messages if msg.get("sender") == "buyer" and msg.get("tactic")]
        if buyer_tactics:
            top_tactic = max(set(buyer_tactics), key=buyer_tactics.count)
            st.warning(f"Buyer has used '{top_tactic}' tactic in {buyer_tactics.count(top_tactic)} rounds.")
            avg_sentiment = float(series_df["sentiment_score"].mean())
            if avg_sentiment < -0.25:
                st.info("Based on sentiment trajectory, settlement is unlikely within 2 rounds.")
            else:
                st.info("Sentiment trend indicates possibility of settlement with disciplined concessions.")

    if state.status == "settled" and state.settlement_amount:
        st.markdown("### Settlement Package")
        plan_choice = st.radio(
            "Installment plan",
            ["Lump Sum (15 days)", "2 Equal Installments", "3 Monthly", "Custom"],
            horizontal=True,
        )
        num_installments = 1
        plan_type = "lump_sum"
        start_date = (date.today() + timedelta(days=15)).isoformat()
        if plan_choice == "2 Equal Installments":
            num_installments = 2
            plan_type = "equal_monthly"
        elif plan_choice == "3 Monthly":
            num_installments = 3
            plan_type = "equal_monthly"
        elif plan_choice == "Custom":
            c1, c2 = st.columns(2)
            num_installments = int(c1.number_input("Installments", min_value=1, max_value=12, value=3))
            start_date = c2.date_input("Start date", value=date.today() + timedelta(days=10)).isoformat()
            custom_plan = st.selectbox("Custom structure", ["equal_monthly", "front_loaded", "lump_sum"])
            plan_type = custom_plan

        plan = services["drafter"].generate_installment_plan(
            total_amount=state.settlement_amount,
            num_installments=num_installments,
            start_date=start_date,
            plan_type=plan_type,
        )
        if st.button(t("generate_settlement"), key="generate_settlement_btn"):
            agreement = services["drafter"].draft_settlement(
                dispute=dispute,
                settlement_amount=state.settlement_amount,
                payment_schedule=plan,
                interest_waived=max(0.0, dispute.total_claim - state.settlement_amount),
            )
            st.session_state["settlement_agreement"] = agreement
            st.toast("Settlement agreement drafted.")

        agreement = st.session_state.get("settlement_agreement")
        if agreement is not None:
            preview_text = services["drafter"].draft_settlement_agreement_text(agreement, dispute)
            with st.expander("Settlement Agreement Preview", expanded=True):
                st.markdown(f"```text\n{preview_text}\n```")

            settlement_pdf = build_settlement_agreement_pdf(agreement)
            demand_pdf = build_demand_notice_pdf(dispute)
            msefc_pdf = build_msefc_reference_pdf(dispute)

            tab1, tab2, tab3 = st.tabs(["Settlement", "Demand Notice", "MSEFC Reference"])
            with tab1:
                render_pdf_preview(settlement_pdf, key="settlement_pdf_preview")
                st.download_button("📄 Download Settlement Agreement PDF", settlement_pdf, f"{agreement.agreement_id}.pdf", "application/pdf")
            with tab2:
                render_pdf_preview(demand_pdf, key="demand_pdf_preview")
                st.download_button("📄 Download Demand Notice PDF", demand_pdf, f"{dispute.case_id}_demand.pdf", "application/pdf")
            with tab3:
                render_pdf_preview(msefc_pdf, key="msefc_pdf_preview")
                st.download_button("📄 Download MSEFC Reference PDF", msefc_pdf, f"{dispute.case_id}_msefc.pdf", "application/pdf")

    if st.button(t("escalate_msefc"), key="escalate_btn"):
        st.text(services["drafter"].draft_msefc_reference(dispute))
        st.toast("Escalation draft generated.")
    st.caption(t("disclaimer"))
def render_dashboard() -> None:
    """Render analytics dashboard with filters and demo-ready visuals."""
    st.title(t("dashboard"))
    render_demo_tour_hint("dashboard")
    render_ui_banner(
        t("dashboard_banner_title"),
        t("dashboard_banner_subtitle"),
        chips=[t("chip_my_vs_all_cases"), t("chip_state_heatmap"), t("chip_msefc_performance"), t("chip_pdf_export")],
    )
    analytics = DisputeAnalytics("data/synthetic/disputes.csv")
    geo = GeoAnalytics("data/synthetic/disputes.csv", "data/msme/state_districts.json")
    blacklist = BuyerBlacklist("data/synthetic/disputes.csv", "data/synthetic/buyer_profiles.csv")
    perf = MSEFCPerformance("data/synthetic/state_pendency.csv", "data/synthetic/disputes.csv")
    df = analytics.data.copy()
    if df.empty:
        st.warning("No historical data. Using synthetic dataset.")
        df = pd.read_csv("data/synthetic/disputes.csv")

    f1, f2, f3, f4 = st.columns(4)
    months = sorted(df["month"].dropna().astype(str).unique().tolist()) if "month" in df.columns else []
    if months:
        month_from, month_to = f1.select_slider("Date range", options=months, value=(months[0], months[-1]))
        mask_month = (df["month"].astype(str) >= month_from) & (df["month"].astype(str) <= month_to)
    else:
        mask_month = pd.Series([True] * len(df))

    states = sorted(df["state"].dropna().unique().tolist()) if "state" in df.columns else []
    state_filter = f2.multiselect("State filter", options=states, default=[])
    mask_state = df["state"].isin(state_filter) if state_filter else pd.Series([True] * len(df))

    buyer_types = sorted(df["buyer_type"].dropna().unique().tolist()) if "buyer_type" in df.columns else []
    buyer_filter = f3.multiselect("Buyer type", options=buyer_types, default=[])
    mask_buyer = df["buyer_type"].isin(buyer_filter) if buyer_filter else pd.Series([True] * len(df))

    if "dispute_amount" in df.columns:
        min_amt = float(df["dispute_amount"].min())
        max_amt = float(df["dispute_amount"].max())
        amount_range = f4.slider("Amount range (INR)", min_value=min_amt, max_value=max_amt, value=(min_amt, max_amt), step=10000.0)
        mask_amt = (df["dispute_amount"] >= amount_range[0]) & (df["dispute_amount"] <= amount_range[1])
    else:
        mask_amt = pd.Series([True] * len(df))

    filtered = df[mask_month & mask_state & mask_buyer & mask_amt].copy()
    if filtered.empty:
        st.warning("No rows for selected filters. Showing unfiltered analytics.")
        filtered = df.copy()

    tabs = st.tabs(["My Cases", "All Cases"])
    with tabs[0]:
        active = st.session_state.get("active_dispute")
        if not active:
            st.info("No active user case yet. File and assess a dispute to populate My Cases.")
        else:
            c_case1, c_case2, c_case3 = st.columns(3)
            c_case1.metric(t("my_case_id_label"), active.case_id)
            c_case2.metric(t("my_claim_value_label"), format_inr(active.total_claim))
            c_case3.metric(t("my_stage_label"), active.current_stage)
            my_case_rows = [
                {
                    "case_id": active.case_id,
                    "state": active.mse.state,
                    "buyer_type": active.buyer.buyer_type,
                    "dispute_amount": active.total_claim,
                    "principal": active.total_principal,
                    "interest": active.total_interest,
                    "stage": active.current_stage,
                }
            ]
            st.dataframe(pd.DataFrame(my_case_rows), use_container_width=True)
            st.metric("My Claim Amount", format_inr(active.total_claim))

    with tabs[1]:
        total_disputes = int(len(filtered))
        total_amount = float(filtered["dispute_amount"].sum()) if "dispute_amount" in filtered.columns else 0.0
        total_recovered = float(filtered["recovered_amount"].sum()) if "recovered_amount" in filtered.columns else 0.0
        recovery_rate = (total_recovered / total_amount * 100.0) if total_amount else 0.0
        avg_days = int(filtered["resolution_days"].mean()) if "resolution_days" in filtered.columns else 0

        if "month" in filtered.columns:
            month_stats = filtered.groupby("month", as_index=False).agg(disputed=("dispute_amount", "sum"), recovered=("recovered_amount", "sum"))
            month_stats = month_stats.sort_values("month")
            if len(month_stats) >= 2:
                prev = month_stats.iloc[-2]
                curr = month_stats.iloc[-1]
                delta_recovered = float(curr["recovered"] - prev["recovered"])
            else:
                delta_recovered = 0.0
        else:
            delta_recovered = 0.0

        c1, c2, c3, c4 = st.columns(4)
        st.caption(t("dashboard_filters_hint"))
        c1.metric("Total Disputes", f"{total_disputes:,}")
        c2.metric("Amount at Stake", format_inr(total_amount))
        c3.metric("Recovery Rate", f"{recovery_rate:.1f}%")
        c4.metric("Avg Resolution Days", str(avg_days), delta=f"{delta_recovered:,.0f}")

        left, right = st.columns(2)
        monthly = filtered.groupby("month", as_index=False).agg(
            filed=("case_id", "count"),
            recovered=("recovered_amount", "sum"),
            avg_recovery_pct=("recovery_percentage", "mean"),
        ) if "month" in filtered.columns else pd.DataFrame()
        if not monthly.empty:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=monthly["month"], y=monthly["filed"], name="Filed", mode="lines+markers"))
            fig_trend.add_trace(go.Scatter(x=monthly["month"], y=monthly["recovered"], name="Recovered Amount", mode="lines+markers"))
            fig_trend.update_layout(title="Dispute Trend Over Time")
            left.plotly_chart(fig_trend, use_container_width=True)
        else:
            left.info("Monthly trend unavailable.")

        if "buyer_type" in filtered.columns:
            buyer_recovery = filtered.groupby("buyer_type", as_index=False).agg(recovery_rate=("recovery_percentage", "mean"))
            fig_buyer = go.Figure(go.Bar(x=buyer_recovery["buyer_type"], y=buyer_recovery["recovery_rate"], marker_color="#B9973D"))
            fig_buyer.update_layout(title="Recovery Rate by Buyer Type", yaxis_title="Recovery %")
            right.plotly_chart(fig_buyer, use_container_width=True)

        left2, right2 = st.columns(2)
        left2.plotly_chart(analytics.get_amount_distribution(), use_container_width=True)
        right2.plotly_chart(analytics.get_stage_funnel(), use_container_width=True)

        st.markdown("### State Heatmap")
        if STREAMLIT_FOLIUM_AVAILABLE:
            st_folium(geo.get_state_heatmap(), width=1100, height=420)
        else:
            st.warning("streamlit-folium not installed; map disabled.")

        st.markdown("### MSEFC Performance")
        st.plotly_chart(perf.get_msefc_ranking(), use_container_width=True)
        st.plotly_chart(perf.get_90_day_compliance(), use_container_width=True)

        st.markdown("### Buyer Blacklist")
        st.plotly_chart(blacklist.get_blacklist_table(), use_container_width=True)

        st.markdown("### Sector Analysis")
        st.plotly_chart(analytics.get_sector_breakdown(), use_container_width=True)

        report_metrics = {
            "total_disputes": total_disputes,
            "total_amount_disputed": total_amount,
            "total_recovered": total_recovered,
            "recovery_rate": recovery_rate,
            "avg_resolution_days": avg_days,
        }
        report_pdf = build_admin_report_pdf(report_metrics, highlights=["Filtered dashboard snapshot", "Generated from VasooliTracker analytics"])
        st.download_button("Export Dashboard Report (PDF)", report_pdf, "dashboard_report.pdf", "application/pdf")

    st.caption(t("disclaimer"))
def render_interest_calculator(services: Dict) -> None:
    """Render standalone statutory interest calculator."""
    st.title(t("interest_calc"))
    qp = st.query_params
    default_principal = float(qp.get("principal", "500000"))
    default_start = qp.get("start", (date.today() - timedelta(days=180)).isoformat())
    default_end = qp.get("end", date.today().isoformat())
    c1, c2, c3 = st.columns(3)
    principal = c1.number_input(t("principal_amount"), min_value=1000.0, value=default_principal, step=1000.0)
    start = c2.date_input(t("overdue_start"), value=date.fromisoformat(default_start))
    end = c3.date_input(t("end_date"), value=date.fromisoformat(default_end))

    result = services["interest"].calculate_interest(principal=principal, start_date=start.isoformat(), end_date=end.isoformat())
    st.metric(t("total_owed"), format_inr(result.total_due))
    st.caption("Under Section 16, MSMED Act 2006")
    st.write(f"RBI Rate: {result.rbi_bank_rate:.2f}% | Statutory Annual Rate: {result.applicable_rate:.2f}%")
    df = pd.DataFrame(result.calculation_breakdown)
    st.dataframe(df, use_container_width=True, height=300)

    excel_bytes = build_interest_calculation_excel(result)
    pdf_bytes = build_interest_calculation_pdf(result)
    d1, d2, d3 = st.columns(3)
    d1.download_button("Download PDF", pdf_bytes, "interest_calculation.pdf", "application/pdf")
    d2.download_button(
        "Download Excel",
        excel_bytes,
        "interest_calculation.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    d3.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), "interest_breakdown.csv", "text/csv")

    share_qs = urlencode({"principal": f"{principal:.2f}", "start": start.isoformat(), "end": end.isoformat()})
    st.caption("Shareable pre-filled calculator link")
    st.code(f"?{share_qs}")
    st.link_button("Open pre-filled link", f"?{share_qs}")
    st.caption(t("disclaimer"))


def render_legal_guide() -> None:
    """Render legal guide and FAQ."""
    st.title(t("legal_guide"))
    st.markdown(f"### {t('how_to_file')}")
    st.write("1. Gather Udyam certificate, invoices, PO, delivery proof, and correspondence.")
    st.write("2. Send demand notice and track buyer response window.")
    st.write("3. File on ODR and proceed through UNP/conciliation.")
    st.write("4. Escalate to arbitration where required.")

    sections = load_json("data/legal/msmed_act_sections.json", {}).get("sections", [])
    for sec in sections:
        with st.expander(f"Section {sec.get('section')} - {sec.get('title')}"):
            st.write(sec.get("summary"))
            if sec.get("verbatim_text"):
                st.code(sec.get("verbatim_text"))
            for rule in sec.get("key_rules", []):
                st.write(f"- {rule}")

    st.markdown("### FAQ")
    faq = [
        ("Can I claim interest under MSMED Act?", "Yes. Section 16 provides compound interest with monthly rests at 3x RBI bank rate."),
        (
            "What if buyer threatens to stop business?",
            "Record communication, avoid informal concessions under pressure, and escalate through formal MSEFC process when needed.",
        ),
        (
            "What if buyer is in another state?",
            "Section 17/18 process can still be invoked. Jurisdiction generally follows supplier-side MSEFC routing in this workflow.",
        ),
    ]
    for q, a in faq:
        with st.expander(q):
            st.write(a)

    st.markdown("### MSEFC Directory")
    msefc = load_json("data/legal/msefc_directory.json", [])
    if msefc:
        states = sorted({row.get("state", "Unknown") for row in msefc})
        chosen = st.selectbox("Select state", states, key="msefc_state_select")
        for row in [item for item in msefc if item.get("state") == chosen][:3]:
            st.write(
                f"{row.get('state')}: {row.get('name', 'MSEFC')} | "
                f"Email: {row.get('email', 'N/A')} | Phone: {row.get('phone', 'N/A')}"
            )

    st.markdown("### Timeline Expectations")
    st.write("UNP/conciliation initiation: typically first few weeks after filing.")
    st.write("Conciliation completion target: up to 90 days in many workflows.")
    st.write("If unresolved, arbitration and award timeline depends on complexity and compliance.")
    st.caption(t("disclaimer"))


def render_workspace() -> None:
    """Render case workspace controls and export options."""
    st.title(t("workspace_title"))
    dispute = st.session_state.get("active_dispute")
    prediction = st.session_state.get("prediction")
    if not dispute:
        try:
            db = DatabaseManager()
            saved_list = db.list_disputes()
        except Exception:
            saved_list = []
        if saved_list:
            st.subheader("Saved Cases")
            st.caption("These cases are persisted in the database and survive browser refresh.")
            for item in saved_list[:10]:
                col_info, col_load = st.columns([4, 1])
                col_info.markdown(f"**{item['case_id']}** — {item['mse_name']} vs {item['buyer_name']} | ₹{item['total_claim']} | {item['stage']}")
                if col_load.button("Load", key=f"load_{item['case_id']}"):
                    loaded = db.load_dispute(item["case_id"])
                    if loaded:
                        from src.common.models import DisputeCase, CaseOutcomePrediction
                        st.session_state["active_dispute"] = DisputeCase(**loaded["dispute"])
                        if loaded.get("prediction"):
                            st.session_state["prediction"] = CaseOutcomePrediction(**loaded["prediction"])
                        st.rerun()
            st.markdown("---")
        st.markdown(
            f"""
            <div class="empty-state">
              <div class="empty-icon">💼</div>
              <div class="empty-title">{t('workspace_empty_title')}</div>
              <div class="empty-desc">{t('workspace_empty_desc')}</div>
              <div class="empty-steps">
                {t('workspace_empty_step1')}<br>
                {t('workspace_empty_step2')}<br>
                {t('workspace_empty_step3')}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(t("disclaimer"))
        return
    st.subheader(t("active_case"))
    st.markdown(f"**Case ID:** `{dispute.case_id}` | **MSE:** {dispute.mse.enterprise_name} | **Buyer:** {dispute.buyer.buyer_name}")
    m1, m2, m3 = st.columns(3)
    m1.metric("Principal", format_inr(dispute.total_principal))
    m2.metric("Interest", format_inr(dispute.total_interest))
    m3.metric("Total Claim", format_inr(dispute.total_claim))
    with st.expander("Full Case Data (JSON)", expanded=False):
        st.json(dispute.model_dump(), expanded=False)
    if prediction:
        st.subheader("Prediction")
        p1, p2, p3 = st.columns(3)
        p1.metric("Settlement Probability", f"{prediction.settlement_probability * 100:.1f}%")
        p2.metric("Recovery", format_inr(prediction.predicted_recovery_amount))
        p3.metric("Strategy", prediction.recommended_strategy.replace("_", " ").title())
        with st.expander("Full Prediction Data (JSON)", expanded=False):
            st.json(prediction.model_dump(), expanded=False)

    st.markdown("---")
    export_payload = {
        "dispute": dispute.model_dump(),
        "prediction": prediction.model_dump() if prediction else None,
        "similar_cases": st.session_state.get("similar_cases", []),
    }
    col_export, col_clear = st.columns(2)
    with col_export:
        st.download_button(
            t("export_case_json"),
            data=json.dumps(export_payload, indent=2, default=str).encode("utf-8"),
            file_name="nyayasetu_workspace_case.json",
            mime="application/json",
            use_container_width=True,
        )
    with col_clear:
        if st.button(t("clear_workspace"), use_container_width=True):
            st.session_state["active_dispute"] = None
            st.session_state["prediction"] = None
            st.session_state["similar_cases"] = []
            st.session_state["negotiation_state"] = None
            st.success(t("workspace_cleared"))
            st.toast("Workspace cleared.")
    st.caption(t("disclaimer"))


def render_about() -> None:
    """Render project information."""
    st.title(t("about"))
    render_demo_tour_hint("about")
    render_ui_banner(
        t("about_banner_title"),
        t("about_banner_subtitle"),
        chips=[t("chip_msmed_act"), t("chip_dpdp"), t("chip_voice_ai_ocr"), t("chip_odr_outputs")],
    )
    st.subheader("NyayaSetu")
    st.write("AI-enabled delayed-payment dispute resolution platform for MSMEs.")
    st.markdown("**Tagline:** Bridge to Justice for MSMEs")

    st.markdown("### Architecture")
    arch_html = """
    <div style="background:#F7F8FA;border:2px solid #E5E7EB;border-radius:16px;padding:28px 24px;font-family:monospace;font-size:13px;line-height:2.2;color:#1E2D4D;">
      <div style="text-align:center;font-size:15px;font-weight:700;margin-bottom:12px;">NyayaSetu System Architecture</div>
      <div style="text-align:center;">
        <span style="background:#1E2D4D;color:#fff;padding:6px 16px;border-radius:8px;">👤 MSME User</span>
        <br>▼ &nbsp; Voice (Bhashini ASR/TTS) &nbsp;|&nbsp; Text &nbsp;|&nbsp; OCR Upload
      </div>
      <div style="text-align:center;margin:12px 0;">
        <span style="background:#B9973D;color:#fff;padding:8px 20px;border-radius:8px;font-weight:700;">⚖️ Streamlit UI — 8 Languages</span>
      </div>
      <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin:12px 0;">
        <span style="background:#1E2D4D14;border:1px solid #1E2D4D;padding:6px 12px;border-radius:8px;">📋 VaadPatra<br><small>Filing + OCR + Classify</small></span>
        <span style="background:#1E2D4D14;border:1px solid #1E2D4D;padding:6px 12px;border-radius:8px;">🔮 NyayaPredictor<br><small>CatBoost + SHAP</small></span>
        <span style="background:#1E2D4D14;border:1px solid #1E2D4D;padding:6px 12px;border-radius:8px;">🤝 SamvadAI<br><small>Negotiate + Settle</small></span>
        <span style="background:#1E2D4D14;border:1px solid #1E2D4D;padding:6px 12px;border-radius:8px;">📊 RecoveryTracker<br><small>Analytics + Heatmap</small></span>
      </div>
      <div style="text-align:center;margin:12px 0;">▼ &nbsp; AI / ML / NLP Layer</div>
      <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;">
        <span style="background:#E8F5E9;padding:5px 12px;border-radius:6px;border:1px solid #4CAF50;">🧠 Qwen 2.5 14B<br><small>via Ollama</small></span>
        <span style="background:#E3F2FD;padding:5px 12px;border-radius:6px;border:1px solid #2196F3;">🎙️ Bhashini ULCA<br><small>ASR/TTS/NMT</small></span>
        <span style="background:#FFF3E0;padding:5px 12px;border-radius:6px;border:1px solid #FF9800;">📄 PaddleOCR<br><small>Invoice Extract</small></span>
        <span style="background:#F3E5F5;padding:5px 12px;border-radius:6px;border:1px solid #9C27B0;">📈 CatBoost+SHAP<br><small>Predictions</small></span>
      </div>
      <div style="text-align:center;margin:12px 0;">▼ &nbsp; Storage &amp; Output</div>
      <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;">
        <span style="background:#ECEFF1;padding:5px 12px;border-radius:6px;border:1px solid #607D8B;">🗄️ SQLite / PostgreSQL</span>
        <span style="background:#ECEFF1;padding:5px 12px;border-radius:6px;border:1px solid #607D8B;">📑 PDF / Excel Reports</span>
        <span style="background:#ECEFF1;padding:5px 12px;border-radius:6px;border:1px solid #607D8B;">🔗 ODR Portal Link</span>
      </div>
    </div>
    """
    st.markdown(arch_html, unsafe_allow_html=True)
    st.markdown("### Technology Stack")
    stack = pd.DataFrame(
        [
            {"Component": "Frontend", "Technology": "Streamlit 1.33+"},
            {"Component": "AI/LLM", "Technology": "Ollama (Qwen 2.5)"},
            {"Component": "ML", "Technology": "CatBoost / Scikit-learn"},
            {"Component": "Data", "Technology": "Pandas, NumPy"},
            {"Component": "Documents", "Technology": "ReportLab, OpenPyXL"},
            {"Component": "Voice", "Technology": "Bhashini ULCA APIs"},
        ]
    )
    st.dataframe(stack, use_container_width=True, hide_index=True)
    st.markdown("### Modules")
    st.write("VaadPatra: dispute filing, OCR extraction, document checks, legal eligibility.")
    st.write("NyayaPredictor: settlement probability, recovery forecast, explainability.")
    st.write("SamvadAI: negotiation rounds, tactic detection, settlement drafting.")
    st.write("RecoveryTracker: portfolio analytics, state heatmap, buyer risk tracking.")
    st.markdown("### Legal Framework")
    st.write("MSMED Act 2006 Sections 15-19, with Section 16 statutory interest and Section 18 MSEFC process.")
    st.markdown("### Privacy")
    st.write("Case data processing follows DPDP Act 2023 principles with access minimization and purpose limitation.")
    st.markdown("### Team")
    st.write("Team details placeholder: Product, Legal, and AI Engineering.")
    st.caption(t("disclaimer"))


def main() -> None:
    """Application entrypoint."""
    st.set_page_config(page_title="NyayaSetu — न्यायसेतु", page_icon="⚖️", layout="wide")
    ensure_session_state()

    # Sidebar controls first so selected theme applies in same run.
    st.sidebar.markdown(
        f'<h1 style="color:#FFFFFF !important;font-size:26px !important;margin-bottom:0;">⚖️ {tr(st.session_state["language"], "project_title")}</h1>',
        unsafe_allow_html=True,
    )
    st.sidebar.caption(tr(st.session_state["language"], "project_subtitle"))
    st.sidebar.markdown(
        '<div style="height:3px;background:linear-gradient(90deg,#B9973D 0%,transparent 100%);'
        'margin:4px 0 16px 0;border-radius:2px;"></div>',
        unsafe_allow_html=True,
    )
    _lang_options = list(config.SUPPORTED_LANGUAGES.keys())
    _current_lang = st.session_state.get("language", "en")
    _lang_index = _lang_options.index(_current_lang) if _current_lang in _lang_options else 0
    st.session_state["language"] = st.sidebar.selectbox(
        "Language / भाषा",
        options=_lang_options,
        index=_lang_index,
        format_func=lambda k: config.SUPPORTED_LANGUAGES.get(k, k),
    )
    st.session_state["theme_key"] = st.sidebar.selectbox(
        t("theme"),
        options=list(THEMES.keys()),
        format_func=lambda key: t(key),
    )
    apply_theme(st.session_state["theme_key"])

    services = load_services()
    st.sidebar.markdown("---")
    st.sidebar.write(t("status"))
    st.sidebar.success("Data Ready")
    llm_online = services["llm"].health_check()
    st.sidebar.write(
        "Ollama:",
        t("online") if llm_online else t("demo_mode"),
    )
    if not llm_online:
        st.sidebar.warning("LLM service offline. Using rule-based mode.")
    if st.session_state.get("active_dispute"):
        _active = st.session_state["active_dispute"]
        st.sidebar.markdown(
            f'<div class="sidebar-case-badge">'
            f'<strong>Active Case</strong><br>{_active.case_id}</div>',
            unsafe_allow_html=True,
        )
    saved_cases = st.session_state.get("saved_cases", {})
    if saved_cases:
        case_ids = ["-- Select Case --"] + sorted(saved_cases.keys())
        chosen_case = st.sidebar.selectbox("Quick Case Selector", case_ids, key="quick_case_select")
        if chosen_case != "-- Select Case --" and st.sidebar.button("Load Selected Case", key="quick_case_load_btn"):
            snapshot = saved_cases.get(chosen_case, {})
            st.session_state["active_dispute"] = snapshot.get("dispute")
            st.session_state["prediction"] = snapshot.get("prediction")
            st.session_state["similar_cases"] = snapshot.get("similar_cases", [])
            st.toast(f"Loaded case {chosen_case}.")
            st.rerun()

    nav_items = [
        ("home", f"🏠  {t('home')}"),
        ("file_dispute", f"📋  {t('file_dispute')}"),
        ("negotiate", f"🤝  {t('negotiate')}"),
        ("dashboard", f"📊  {t('dashboard')}"),
        ("interest_calc", f"🧮  {t('interest_calc')}"),
        ("legal_guide", f"📖  {t('legal_guide')}"),
        ("workspace", f"💼  {t('workspace')}"),
        ("about", f"ℹ️  {t('about')}"),
    ]
    _nav_map = {k: lbl for k, lbl in nav_items}
    _nav_target_key = st.session_state.pop("_nav_target_key", None)
    if _nav_target_key and _nav_target_key in _nav_map:
        st.session_state["_nav_radio"] = _nav_map[_nav_target_key]
    selected_label = st.sidebar.radio(t("nav"), [label for _, label in nav_items], key="_nav_radio")
    selected_key = next(key for key, label in nav_items if label == selected_label)

    st.markdown(
        """
        <script>
        if (!window.__nyayasetu_shortcut_bound__) {
          window.__nyayasetu_shortcut_bound__ = true;
          document.addEventListener("keydown", function(event) {
            if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
              const buttons = window.parent.document.querySelectorAll("button");
              for (const btn of buttons) {
                const label = (btn.innerText || "").toLowerCase();
                if (label.includes("assess case") || label.includes("process buyer response") || label.includes("generate settlement")) {
                  btn.click();
                  event.preventDefault();
                  break;
                }
              }
            }
          });
        }
        </script>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Quick action: press Ctrl+Enter to trigger key submit actions.")

    if selected_key == "home":
        render_home(services)
    elif selected_key == "file_dispute":
        render_file_dispute(services)
    elif selected_key == "negotiate":
        render_negotiate(services)
    elif selected_key == "dashboard":
        render_dashboard()
    elif selected_key == "interest_calc":
        render_interest_calculator(services)
    elif selected_key == "legal_guide":
        render_legal_guide()
    elif selected_key == "workspace":
        render_workspace()
    else:
        render_about()


if __name__ == "__main__":
    main()




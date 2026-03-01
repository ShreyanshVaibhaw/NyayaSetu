# NyayaSetu — Claude Code Build Prompts
# न्यायसेतु — Bridge to Justice: AI-Powered Virtual Negotiation for MSME Delayed Payments
# Copy-paste each prompt into Claude Code IN ORDER
# Wait for each to complete and TEST before moving to the next

---

# PHASE 1: FOUNDATION (Prompts 0-1)

---

## PROMPT 0: Project Setup & Foundation

```
Create a Python project called "nyayasetu" with the following structure:

nyayasetu/
├── app.py                              # Streamlit main dashboard
├── config.py                           # All configuration constants
├── requirements.txt                    # All dependencies
├── docker-compose.yml                  # One-click deployment
├── Dockerfile                          # Container setup
├── .env.example                        # Environment variables template
├── README.md                           # Setup and usage instructions
├── data/
│   ├── legal/                          # Legal reference data
│   │   ├── msmed_act_sections.json     # MSMED Act 2006 relevant sections (15-24)
│   │   ├── rbi_bank_rates.json         # RBI bank rate history for interest calculation
│   │   ├── msefc_directory.json        # State-wise MSEFC contact/jurisdiction data
│   │   ├── legal_precedents.json       # 100+ MSEFC/court case summaries with outcomes
│   │   └── penalty_rules.json          # Penalty calculation rules under MSMED Act
│   ├── odr/                            # ODR portal reference data
│   │   ├── filing_requirements.json    # Required fields for ODR complaint filing
│   │   ├── dispute_categories.json     # Types of delayed payment disputes
│   │   ├── negotiation_templates.json  # Negotiation message templates
│   │   └── settlement_templates.json   # Settlement agreement templates
│   ├── msme/                           # MSME reference data
│   │   ├── state_districts.json        # India states, districts with lat/lon
│   │   ├── sector_codes.json           # NIC codes for MSME sectors
│   │   ├── buyer_categories.json       # Buyer types (Govt PSU, Private Ltd, Proprietorship etc.)
│   │   └── sample_disputes.json        # 30 sample dispute records for demo
│   ├── synthetic/                      # Synthetic data for demo
│   │   ├── disputes.csv                # 5,000 synthetic dispute records
│   │   ├── case_outcomes.csv           # Historical case outcome data for prediction
│   │   ├── buyer_profiles.csv          # Synthetic buyer payment behavior data
│   │   ├── recovery_funnel.csv         # Dispute resolution funnel data
│   │   └── state_pendency.csv          # State-wise case pendency data
│   └── vocabulary/                     # Legal and MSME vocabulary
│       ├── legal_terms.json            # Legal terminology in Hindi/English
│       └── invoice_fields.json         # Common invoice/challan field names
├── src/
│   ├── __init__.py
│   ├── vaadpatra/                      # Module 1: Smart Dispute Filing
│   │   ├── __init__.py
│   │   ├── dispute_builder.py          # Auto-fill ODR complaint from inputs
│   │   ├── document_ocr.py            # OCR for invoices, POs, challans
│   │   ├── interest_calculator.py     # Compound interest at 3× RBI rate
│   │   ├── eligibility_checker.py     # Validates Udyam date, 45-day rule etc.
│   │   ├── udyam_fetcher.py           # Fetch MSE data from Udyam number
│   │   └── gst_validator.py           # GST verification for buyer/seller
│   ├── nyayapredictor/                 # Module 2: Case Outcome Prediction
│   │   ├── __init__.py
│   │   ├── outcome_predictor.py       # ML model for case outcome prediction
│   │   ├── case_similarity.py         # Find similar past cases
│   │   ├── buyer_risk_scorer.py       # Buyer payment risk scoring
│   │   ├── timeline_estimator.py      # Estimated resolution timeline
│   │   └── feature_engineering.py     # Feature extraction from dispute data
│   ├── samvadai/                       # Module 3: AI Negotiation Agent
│   │   ├── __init__.py
│   │   ├── negotiation_engine.py      # Strategy generation + counter-offers
│   │   ├── settlement_drafter.py      # Auto-draft settlement agreements
│   │   ├── tactic_detector.py         # Detect buyer stalling/aggression tactics
│   │   ├── offer_optimizer.py         # Optimal offer calculation
│   │   └── communication_gen.py       # Generate negotiation messages
│   ├── vasoolitracker/                 # Module 4: Recovery Dashboard
│   │   ├── __init__.py
│   │   ├── dispute_analytics.py       # Dispute tracking and analytics
│   │   ├── geo_analytics.py           # Geographic delayed payment analysis
│   │   ├── buyer_blacklist.py         # Repeat offender detection
│   │   ├── msefc_performance.py       # MSEFC case load and performance
│   │   └── dashboard_data.py          # Dashboard data preparation
│   ├── voice/                          # Voice interaction layer
│   │   ├── __init__.py
│   │   ├── bhashini_client.py         # Bhashini ASR/TTS/NMT integration
│   │   └── conversation_engine.py     # Voice-guided dispute filing flow
│   ├── llm/                            # LLM integration
│   │   ├── __init__.py
│   │   ├── ollama_client.py           # Ollama API wrapper
│   │   └── prompt_templates.py        # All prompt templates
│   └── common/                         # Shared utilities
│       ├── __init__.py
│       ├── models.py                  # All Pydantic data models
│       ├── database.py                # PostgreSQL + SQLite fallback
│       └── logger.py                  # Logging configuration
├── tests/
│   ├── test_vaadpatra.py
│   ├── test_nyayapredictor.py
│   ├── test_samvadai.py
│   ├── test_vasoolitracker.py
│   └── test_integration.py
└── scripts/
    ├── generate_synthetic_data.py     # Generate all synthetic data
    ├── seed_database.py               # Initialize database
    └── demo_flow.py                   # End-to-end demo script

Create all files with proper docstrings and placeholder implementations. In requirements.txt include:

streamlit==1.41.0
fastapi==0.115.0
uvicorn==0.32.0
pydantic>=2.9.0
python-dotenv>=1.0.1
pandas>=2.2.0
numpy>=1.26.0
scikit-learn>=1.5.0
catboost>=1.2.0
xgboost>=2.1.0
plotly>=5.24.0
folium>=0.18.0
geopandas>=1.0.0
psycopg2-binary>=2.9.9
sqlalchemy>=2.0.0
requests>=2.32.0
httpx>=0.27.0
sentence-transformers>=3.3.0
ollama>=0.4.0
reportlab>=4.2.0
openpyxl>=3.1.5
rich>=13.9.0
python-multipart>=0.0.12
Pillow>=10.4.0
paddleocr>=2.7.0
fuzzywuzzy>=0.18.0
python-Levenshtein>=0.25.0
joblib>=1.4.0
streamlit-folium>=0.22.0

In config.py, set up ALL constants:
- PROJECT_NAME = "NyayaSetu"
- PROJECT_SANSKRIT = "न्यायसेतु"
- TAGLINE = "Bridge to Justice — AI that fights for India's MSMEs"
- OLLAMA_MODEL = "qwen2.5:14b"
- OLLAMA_HOST = "localhost"
- OLLAMA_PORT = 11434
- POSTGRES_URI = "postgresql://nyayasetu:nyayasetu2026@localhost:5432/nyayasetu"
- EMBEDDING_MODEL = "all-MiniLM-L6-v2"
- BHASHINI_API_URL = "https://meity-auth.ulcacontrib.org"
- BHASHINI_INFERENCE_URL = "https://dhruva-api.bhashini.gov.in"
- SUPPORTED_LANGUAGES = {"hi": "Hindi", "en": "English", "ta": "Tamil", "mr": "Marathi", "bn": "Bengali", "te": "Telugu", "kn": "Kannada", "gu": "Gujarati"}
- UDYAM_API_URL = "https://udyamregistration.gov.in/api"
- GST_API_URL = "https://gst.gov.in/api"
- ODR_PORTAL_URL = "https://odr.msme.gov.in"
- SAMADHAAN_URL = "https://samadhaan.msme.gov.in"
- RBI_CURRENT_BANK_RATE = 6.50  # As of latest RBI notification
- INTEREST_MULTIPLIER = 3  # 3× RBI bank rate as per MSMED Act Section 16
- MAX_CREDIT_PERIOD_DAYS = 45  # Section 15 of MSMED Act
- DEFAULT_CREDIT_NO_AGREEMENT = 15  # Days when no written agreement
- DISPUTE_STAGES = ["Filed", "UNP_Initiated", "UNP_Settled", "MSEFC_Referred", "Conciliation", "Arbitration", "Award_Passed", "Recovered", "Closed"]
- BUYER_TYPES = ["Central Govt", "State Govt", "PSU", "Private Ltd", "LLP", "Proprietorship", "Partnership", "Trust/Society"]
- PREDICTION_FEATURES = ["dispute_amount", "days_overdue", "buyer_type", "sector", "state", "has_written_agreement", "buyer_gst_compliant", "previous_disputes", "invoice_count"]

In docker-compose.yml:
- postgres (postgres:16) port 5432, DB=nyayasetu
- ollama (ollama/ollama:latest) port 11434 with GPU
- redis (redis:7) port 6379
- nyayasetu (the app) port 8501, depends_on all above

Every Python file must have proper imports, docstrings, and clean placeholder code that won't crash. Each function returns sensible defaults. app.py should show a working Streamlit page with "NyayaSetu — न्यायसेतु" title and tagline.
```

---

## PROMPT 1: Data Models, Legal Reference Data & MSMED Act Knowledge Base

```
In the nyayasetu project, build all data models and reference data:

1. src/common/models.py — Create ALL Pydantic models:

class MSEProfile(BaseModel):
    """Micro/Small Enterprise (the seller/complainant)"""
    udyam_number: str                    # UDYAM-XX-00-0000000
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
    email: Optional[str]
    date_of_udyam: str                   # Critical: must be BEFORE invoice date
    gstin: Optional[str]
    pan: Optional[str]
    bank_account: Optional[str]          # For receiving recovered amount

class BuyerProfile(BaseModel):
    """The buyer (respondent in dispute)"""
    buyer_name: str
    buyer_type: Literal["Central Govt", "State Govt", "PSU", "Private Ltd", "LLP", "Proprietorship", "Partnership", "Trust/Society"]
    gstin: Optional[str]
    pan: Optional[str]
    state: str
    district: str
    address: str
    contact_person: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    industry_sector: Optional[str]

class Invoice(BaseModel):
    """Individual invoice in a dispute"""
    invoice_number: str
    invoice_date: str                    # DD-MM-YYYY
    invoice_amount: float                # INR
    goods_services_description: str
    delivery_date: Optional[str]         # Date goods delivered / services rendered
    acceptance_date: Optional[str]       # Date buyer accepted (or deemed accepted)
    po_number: Optional[str]             # Purchase order reference
    payment_due_date: Optional[str]      # Calculated: acceptance + agreed days (max 45)
    amount_paid: float                   # Amount already paid (if partial)
    amount_outstanding: float            # Amount still owed
    days_overdue: int                    # Days past due date

class DisputeCase(BaseModel):
    """Complete dispute case for filing"""
    case_id: str
    mse: MSEProfile
    buyer: BuyerProfile
    invoices: List[Invoice]
    total_principal: float               # Sum of outstanding amounts
    total_interest: float                # Calculated compound interest
    total_claim: float                   # Principal + interest
    has_written_agreement: bool          # Whether credit period was agreed in writing
    agreed_credit_days: Optional[int]    # If written agreement, how many days (max 45)
    dispute_description: str             # Narrative of the dispute
    relief_sought: str                   # What the MSE wants
    supporting_documents: List[str]      # List of uploaded document paths
    filed_date: Optional[str]
    current_stage: str                   # From DISPUTE_STAGES
    msefc_state: str                     # Jurisdiction
    created_at: datetime

class InterestCalculation(BaseModel):
    """Compound interest calculation per Section 16"""
    invoice_number: str
    principal: float
    start_date: str                      # Date payment became overdue
    end_date: str                        # Current date or payment date
    rbi_bank_rate: float                 # RBI bank rate during period
    applicable_rate: float               # 3× bank rate (monthly compounding)
    months_overdue: int
    interest_amount: float
    total_due: float                     # Principal + interest
    calculation_breakdown: List[Dict]    # Month-by-month breakdown

class CaseOutcomePrediction(BaseModel):
    """ML prediction of case outcome"""
    case_id: str
    settlement_probability: float        # 0.0 - 1.0
    predicted_recovery_percentage: float # % of claimed amount likely recovered
    predicted_recovery_amount: float
    estimated_days_to_resolution: int
    recommended_strategy: str            # "negotiate", "escalate_msefc", "arbitration"
    confidence: float
    similar_cases: List[Dict]            # Top 5 similar past cases
    risk_factors: List[str]              # Factors that may reduce recovery
    favorable_factors: List[str]         # Factors in MSE's favor

class NegotiationState(BaseModel):
    """State of negotiation between MSE and buyer"""
    negotiation_id: str
    case_id: str
    round_number: int
    mse_offer: float                     # Current MSE demand
    buyer_counter: Optional[float]       # Buyer's last counter-offer
    mse_strategy: str                    # Current strategy
    messages: List[Dict]                 # Message history
    status: Literal["active", "settled", "failed", "escalated"]
    settlement_amount: Optional[float]
    settlement_terms: Optional[str]

class SettlementAgreement(BaseModel):
    """Auto-generated settlement agreement"""
    agreement_id: str
    case_id: str
    mse_name: str
    buyer_name: str
    settlement_amount: float
    payment_schedule: List[Dict]         # [{date, amount}]
    interest_waived: float               # If any interest was waived in negotiation
    terms_and_conditions: List[str]
    generated_at: datetime

class BuyerRiskScore(BaseModel):
    """Risk assessment of a buyer"""
    buyer_gstin: str
    buyer_name: str
    risk_score: float                    # 0-100 (100 = highest risk)
    risk_category: Literal["Low", "Medium", "High", "Critical"]
    past_disputes_count: int
    avg_payment_delay_days: int
    total_outstanding_to_mses: float
    gst_compliance_status: str
    factors: List[str]                   # Reasons for the risk score

class DisputeAnalytics(BaseModel):
    """Analytics for dashboard"""
    total_disputes: int
    total_amount_disputed: float
    total_recovered: float
    recovery_rate: float
    avg_resolution_days: int
    stage_distribution: Dict[str, int]
    state_wise: Dict[str, Dict]
    sector_wise: Dict[str, Dict]
    monthly_trend: List[Dict]

2. Create ALL reference data files — MUST BE LEGALLY ACCURATE:

A. data/legal/msmed_act_sections.json — Key sections of MSMED Act 2006:
{
  "sections": [
    {
      "section": "15",
      "title": "Liability of buyer to make payment",
      "summary": "Buyer shall make payment to supplier on or before the agreed date. If no agreement, within 15 days of acceptance. In no case shall the agreed period exceed 45 days from day of acceptance or deemed acceptance.",
      "key_rules": [
        "No written agreement → payment within 15 days of acceptance",
        "Written agreement → payment by agreed date, max 45 days from acceptance",
        "Deemed acceptance: If buyer does not communicate acceptance/rejection within 15 days of delivery, goods deemed accepted",
        "Day of acceptance = day goods delivered or day of deemed acceptance"
      ]
    },
    {
      "section": "16",
      "title": "Date from which and rate at which interest is payable",
      "summary": "Buyer liable to pay compound interest with monthly rests at 3 times the bank rate notified by RBI.",
      "key_rules": [
        "Interest rate = 3 × RBI bank rate",
        "Compound interest with monthly rests",
        "Interest runs from agreed/appointed day until actual payment date",
        "RBI bank rate as of Dec 2025: 6.50%, so applicable rate = 19.50% per annum"
      ]
    },
    {
      "section": "17",
      "title": "Recovery of amount due",
      "summary": "Any party to a dispute may make a reference to the MSEFC. Council shall make endeavour to resolve by conciliation. If conciliation fails, proceed to arbitration.",
      "key_rules": [
        "MSE files reference to MSEFC of state where supplier is located",
        "MSEFC must dispose within 90 days from date of reference",
        "Every reference made after MSEFC is formed: MSEFC has jurisdiction"
      ]
    },
    {
      "section": "18",
      "title": "Reference to Micro and Small Enterprises Facilitation Council",
      "summary": "The MSEFC shall conduct conciliation, and if that fails, take up arbitration under the Arbitration and Conciliation Act, 1996.",
      "key_rules": [
        "Conciliation under Arbitration and Conciliation Act 1996",
        "If conciliation fails, MSEFC itself arbitrates or refers to institution",
        "Arbitration provisions of A&C Act apply",
        "Award is final and binding"
      ]
    },
    {
      "section": "19",
      "title": "Application for setting aside decree, award or order",
      "summary": "No application to set aside any decree/award/order by MSEFC shall be entertained by any court unless buyer deposits 75% of the award amount.",
      "key_rules": [
        "75% deposit required to challenge MSEFC award",
        "This makes MSEFC awards very enforceable",
        "Strong deterrent against frivolous challenges"
      ]
    },
    {
      "section": "22",
      "title": "Buyer's duty to disclose delayed payment",
      "summary": "Every buyer must file a half-yearly return with MSEFC regarding amounts outstanding and delayed beyond 45 days.",
      "key_rules": [
        "Half-yearly return to MSEFC by April 30 and October 31",
        "Must mention amount owed, reason for delay",
        "Non-filing is a separate offence"
      ]
    },
    {
      "section": "23",
      "title": "Penalty for contravention of Section 22",
      "summary": "Any person who contravenes Section 22 shall be punishable with fine of Rs 10,000.",
      "key_rules": ["Fine of Rs 10,000 for not filing half-yearly return"]
    },
    {
      "section": "24",
      "title": "Overriding effect",
      "summary": "Provisions of Sections 15-23 have effect notwithstanding anything inconsistent in any other law.",
      "key_rules": ["MSMED Act sections on delayed payment override other laws"]
    }
  ]
}

B. data/legal/rbi_bank_rates.json — RBI Bank Rate history:
[
  {"effective_date": "2023-02-08", "bank_rate": 6.75, "applicable_interest": 20.25},
  {"effective_date": "2023-04-06", "bank_rate": 6.75, "applicable_interest": 20.25},
  {"effective_date": "2024-02-08", "bank_rate": 6.75, "applicable_interest": 20.25},
  {"effective_date": "2024-06-07", "bank_rate": 6.75, "applicable_interest": 20.25},
  {"effective_date": "2024-10-09", "bank_rate": 6.50, "applicable_interest": 19.50},
  {"effective_date": "2024-12-06", "bank_rate": 6.50, "applicable_interest": 19.50},
  {"effective_date": "2025-02-07", "bank_rate": 6.25, "applicable_interest": 18.75},
  {"effective_date": "2025-04-09", "bank_rate": 6.00, "applicable_interest": 18.00},
  {"effective_date": "2025-12-05", "bank_rate": 6.00, "applicable_interest": 18.00}
]
IMPORTANT: Use the most recent RBI bank rate data. Check RBI website for accuracy.

C. data/legal/msefc_directory.json — All 36 states/UTs with MSEFC details:
[
  {"state": "Andhra Pradesh", "msefc_established": true, "cases_pending": 2340, "avg_resolution_days": 95, "address": "DIC Office, Vijayawada", "helpline": "1800-XXX-XXXX"},
  {"state": "Bihar", "msefc_established": true, "cases_pending": 1890, "avg_resolution_days": 120, "address": "MSME DI, Patna"},
  {"state": "Delhi", "msefc_established": true, "cases_pending": 5670, "avg_resolution_days": 85, "address": "MSME DI, Okhla"},
  {"state": "Gujarat", "msefc_established": true, "cases_pending": 3450, "avg_resolution_days": 78, "address": "DIC Office, Gandhinagar"},
  {"state": "Karnataka", "msefc_established": true, "cases_pending": 4120, "avg_resolution_days": 82, "address": "MSME DI, Bangalore"},
  {"state": "Maharashtra", "msefc_established": true, "cases_pending": 8900, "avg_resolution_days": 90, "address": "DIC Office, Mumbai"},
  {"state": "Rajasthan", "msefc_established": true, "cases_pending": 2780, "avg_resolution_days": 105, "address": "DIC Office, Jaipur"},
  {"state": "Tamil Nadu", "msefc_established": true, "cases_pending": 5230, "avg_resolution_days": 75, "address": "MSME DI, Chennai"},
  {"state": "Uttar Pradesh", "msefc_established": true, "cases_pending": 7600, "avg_resolution_days": 115, "address": "MSME DI, Kanpur"},
  {"state": "West Bengal", "msefc_established": true, "cases_pending": 3890, "avg_resolution_days": 100, "address": "MSME DI, Kolkata"},
  ...
]
Include ALL 36 states/UTs. Cases_pending and avg_resolution are synthetic but realistic.

D. data/legal/legal_precedents.json — 100+ case summaries:
[
  {
    "case_id": "MSEFC/MH/2024/001",
    "state": "Maharashtra",
    "mse_sector": "Manufacturing - Textiles",
    "buyer_type": "Private Ltd",
    "dispute_amount": 450000,
    "days_overdue": 180,
    "had_agreement": true,
    "outcome": "Full recovery with interest",
    "recovery_percentage": 100,
    "interest_awarded": true,
    "resolution_days": 67,
    "summary": "Textile manufacturer filed for recovery of Rs 4.5L against garment exporter. MSEFC awarded full amount plus compound interest at 3x RBI rate for 6 months."
  },
  {
    "case_id": "MSEFC/DL/2024/045",
    "state": "Delhi",
    "mse_sector": "Services - IT",
    "buyer_type": "PSU",
    "dispute_amount": 1200000,
    "days_overdue": 270,
    "had_agreement": true,
    "outcome": "Settled in conciliation at 85%",
    "recovery_percentage": 85,
    "interest_awarded": false,
    "resolution_days": 45,
    "summary": "IT services firm claimed Rs 12L from PSU. Settled in conciliation at Rs 10.2L without interest. MSE accepted to maintain business relationship."
  },
  ...
]
Generate 100+ cases across diverse sectors, states, buyer types, amounts (₹50K to ₹50L), and outcomes. Include a mix: ~40% full recovery, ~30% partial settlement, ~15% ongoing, ~10% dismissed, ~5% awarded but not recovered.

E. data/odr/filing_requirements.json — ODR portal filing fields:
{
  "complainant_details": ["udyam_number", "enterprise_name", "owner_name", "address", "state", "district", "pincode", "mobile", "email", "gstin", "pan"],
  "respondent_details": ["buyer_name", "buyer_type", "address", "state", "district", "gstin", "pan", "contact_person", "contact_email"],
  "dispute_details": ["goods_services_description", "total_amount_claimed", "number_of_invoices", "has_written_agreement", "agreed_credit_period"],
  "invoice_details_per_invoice": ["invoice_number", "invoice_date", "amount", "delivery_date", "payment_due_date", "amount_outstanding"],
  "documents_required": ["udyam_certificate", "invoices", "purchase_orders", "delivery_challans", "correspondence", "bank_statements"],
  "relief_sought_options": ["payment_of_outstanding_principal", "payment_of_compound_interest", "costs_of_filing"]
}

F. data/odr/negotiation_templates.json — 20+ negotiation message templates:
{
  "initial_demand": {
    "formal": "Dear {buyer_name},\n\nThis is to bring to your kind notice that an amount of ₹{amount} is outstanding against invoice(s) {invoice_numbers} dated {dates}. As per Section 15 of the MSMED Act, 2006, the payment was due within {due_days} days of acceptance. The payment is now overdue by {days_overdue} days.\n\nAs per Section 16, you are liable to pay compound interest at {rate}% per annum (3× RBI Bank Rate), which currently amounts to ₹{interest}.\n\nWe request immediate settlement of ₹{total} (principal ₹{principal} + interest ₹{interest}) to avoid escalation to MSEFC proceedings.\n\nRegards,\n{mse_name}",
    "reminder": "...",
    "final_notice": "...",
    "counter_offer_accept": "...",
    "counter_offer_reject": "...",
    "escalation_warning": "..."
  }
}

G. data/odr/settlement_templates.json — Settlement agreement template (legally valid format).

H. data/msme/sample_disputes.json — 30 sample disputes covering:
- Auto parts manufacturer vs private company (₹3.5L, 90 days overdue)
- IT services firm vs Central Govt ministry (₹8L, 200 days overdue)
- Textile weaver vs garment exporter (₹1.2L, 60 days overdue)
- Food processor vs restaurant chain (₹5L, 150 days overdue)
- Steel fabricator vs construction company (₹15L, 300 days overdue)
- Printing press vs publishing house (₹75K, 45 days overdue)
- Chemical supplier vs pharma company (₹25L, 180 days overdue)
- Packaging manufacturer vs FMCG company (₹4L, 120 days overdue)
- Software services vs State PSU (₹12L, 365 days overdue)
- Handicraft artisan vs export house (₹50K, 75 days overdue)
... and 20 more across diverse sectors, states, buyer types, and amounts

Each must have FULL data: MSE profile, buyer profile, invoices, calculated interest, and be realistic.

All legal data MUST be accurate — MSMED Act sections, RBI rates, MSEFC rules. The jury will include legal experts.
```

---

# PHASE 2: CORE MODULES (Prompts 2-5)

---

## PROMPT 2: LLM Integration & Interest Calculator

```
In the nyayasetu project, build the LLM integration and the legally-accurate interest calculator:

1. src/llm/ollama_client.py — Build class LLMClient:
- Same pattern as other projects
- generate(prompt, system=None, temperature=0.1) -> str
- generate_json(prompt, system=None) -> dict
- Retry logic, timeout 120s, health check
- Graceful fallback with cached demo responses if Ollama not running

2. src/llm/prompt_templates.py — Create ALL prompt templates:

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

3. src/vaadpatra/interest_calculator.py — THIS MUST BE 100% LEGALLY ACCURATE:

class InterestCalculator:
    """Calculate compound interest at 3× RBI bank rate per MSMED Act Section 16.
    
    The law specifies:
    - Interest rate = 3 × Bank Rate notified by RBI
    - Compound interest with MONTHLY rests
    - Runs from the day payment became due until actual payment
    
    Monthly compounding formula for each month:
    Amount_n = Amount_(n-1) × (1 + monthly_rate)
    where monthly_rate = (3 × annual_bank_rate) / 12
    """
    
    def __init__(self, rbi_rates_path: str):
        self.rbi_rates = self._load_rates(rbi_rates_path)
    
    def get_applicable_rate(self, date: str) -> float:
        """Get the RBI bank rate applicable on a given date.
        Returns the rate that was in effect on that date.
        CRITICAL: Rate may change during the overdue period — must handle rate changes."""
    
    def calculate_interest(self, principal: float, start_date: str, 
                           end_date: str = None) -> InterestCalculation:
        """Calculate compound interest with monthly rests.
        
        Algorithm:
        1. For each month between start_date and end_date:
           a. Get applicable RBI bank rate for that month
           b. Monthly rate = (3 × annual_rate) / 12
           c. New balance = previous balance × (1 + monthly_rate)
        2. Interest = Final balance - Principal
        
        Handle partial months: pro-rate based on days
        Handle rate changes: if RBI rate changes mid-period, split calculation
        
        Returns InterestCalculation with full month-by-month breakdown.
        """
    
    def calculate_for_invoices(self, invoices: List[Invoice], 
                                end_date: str = None) -> Dict:
        """Calculate interest for multiple invoices.
        Returns: {total_principal, total_interest, total_claim, per_invoice: [...]}"""
    
    def calculate_quick(self, principal: float, months_overdue: int) -> float:
        """Quick calculation using current RBI rate. For display purposes."""

4. src/vaadpatra/eligibility_checker.py:

class EligibilityChecker:
    """Check if MSE is eligible to file under MSMED Act"""
    
    def check_eligibility(self, udyam_date: str, earliest_invoice_date: str,
                           enterprise_type: str, days_overdue: int) -> Dict:
        """Full eligibility check:
        1. Udyam registration date MUST be before earliest invoice date → CRITICAL
        2. Enterprise must be Micro or Small (not Medium) → check
        3. Payment must be overdue (past 15 days or agreed period) → check
        4. Major activity must be Manufacturing or Services → check
        
        Returns: {eligible: bool, reasons: [...], warnings: [...]}"""

5. Tests:
- test_interest_calculator: 
  * ₹1,00,000 principal, 6 months overdue at 6.50% bank rate → verify exact interest amount
  * Multiple invoices with different dates
  * Rate change mid-period handling
- test_eligibility: Udyam date before/after invoice, Micro/Small/Medium distinction
```

---

## PROMPT 3: VaadPatra — Smart Dispute Filing Engine

```
In the nyayasetu project, build the complete VaadPatra module:

1. src/vaadpatra/udyam_fetcher.py — Same pattern as VyaparSetu:
- fetch_by_udyam_number(udyam_number) -> MSEProfile
- validate_udyam_number(udyam_number) -> (bool, str)
- Mock data from sample records when API not available

2. src/vaadpatra/gst_validator.py:
- validate_gstin(gstin) -> Dict (format check, state code extraction)
- extract_state_from_gst(gstin) -> str

3. src/vaadpatra/document_ocr.py:

class DocumentOCR:
    def __init__(self, llm_client):
        self.ocr = None  # PaddleOCR, lazy loaded
        self.llm = llm_client
    
    def extract_from_invoice(self, image_path: str) -> Dict:
        """OCR invoice image → extract structured data.
        Pipeline: PaddleOCR → raw text → LLM (OCR_EXTRACTION_TEMPLATE) → structured JSON
        Extract: invoice number, date, amount, buyer name, GSTIN, items
        FALLBACK: If PaddleOCR not installed, return mock extraction"""
    
    def extract_from_purchase_order(self, image_path: str) -> Dict:
        """OCR purchase order → extract PO number, date, amount, terms"""
    
    def extract_from_challan(self, image_path: str) -> Dict:
        """OCR delivery challan → extract delivery date, items"""
    
    def batch_extract(self, image_paths: List[str]) -> List[Dict]:
        """Process multiple documents"""

4. src/vaadpatra/dispute_builder.py — THE CORE filing engine:

class DisputeBuilder:
    def __init__(self, udyam_fetcher, gst_validator, interest_calc, 
                 eligibility_checker, llm_client):
        self.fetcher = udyam_fetcher
        self.gst = gst_validator
        self.interest = interest_calc
        self.eligibility = eligibility_checker
        self.llm = llm_client
    
    def build_dispute(self, udyam_number: str, buyer_info: Dict,
                       invoices: List[Dict], has_agreement: bool = False,
                       agreed_days: int = None) -> DisputeCase:
        """Complete dispute building pipeline:
        
        Step 1: Fetch MSE data from Udyam number
        Step 2: Validate MSE eligibility (Udyam date vs invoice dates)
        Step 3: Validate buyer GSTIN
        Step 4: For each invoice:
           a. Calculate days overdue from acceptance date
           b. Calculate compound interest per Section 16
        Step 5: Sum total principal + interest = total claim
        Step 6: Determine MSEFC jurisdiction (supplier's state)
        Step 7: Generate dispute description using LLM
        Step 8: Generate relief sought
        Step 9: Return complete DisputeCase ready for filing
        """
    
    def build_from_conversation(self, conversation_data: Dict) -> DisputeCase:
        """Build dispute from voice/chat conversation data"""
    
    def build_from_ocr(self, invoice_images: List[str], udyam_number: str,
                        buyer_gstin: str) -> DisputeCase:
        """Build from scanned documents: OCR → extract → build"""
    
    def generate_filing_summary(self, dispute: DisputeCase) -> str:
        """Generate human-readable summary of the dispute for MSE review"""
    
    def export_odr_format(self, dispute: DisputeCase) -> Dict:
        """Export in format compatible with ODR portal filing"""

5. src/voice/conversation_engine.py — Voice-guided filing:

class ConversationEngine:
    def __init__(self, llm_client, dispute_builder, bhashini_client):
        self.llm = llm_client
        self.builder = dispute_builder
        self.bhashini = bhashini_client
    
    def start_session(self, language: str = "hi") -> Dict:
        """Start voice-guided dispute filing.
        Greeting: 'नमस्ते! न्यायसेतु में आपका स्वागत है। मैं आपकी पेमेंट वसूली में मदद करूँगा।'"""
    
    def process_message(self, state: Dict, message: str) -> Tuple[Dict, str]:
        """Guide MSE through: Udyam number → buyer details → invoice details → review → file.
        Extract data from conversational Hindi/English input."""

6. src/voice/bhashini_client.py — Same Bhashini integration pattern as other projects.

7. Tests:
- Build dispute from sample auto parts manufacturer vs private company
- Verify interest calculation matches manual calculation
- Test eligibility: valid case, invalid (Udyam after invoice), Medium enterprise rejection
- Test OCR pipeline with mock data
- Test conversation flow: 5-turn Hindi dialogue
```

---

## PROMPT 4: NyayaPredictor — Case Outcome Prediction

```
In the nyayasetu project, build the complete NyayaPredictor module:

1. src/nyayapredictor/feature_engineering.py:

class FeatureEngineer:
    def __init__(self):
        pass
    
    def extract_features(self, dispute: DisputeCase) -> Dict:
        """Extract ML features from a dispute case:
        
        Numerical:
        - dispute_amount (log-transformed)
        - days_overdue
        - number_of_invoices
        - agreed_credit_days (0 if no agreement)
        - interest_amount
        - buyer_past_disputes_count
        
        Categorical (one-hot or label encoded):
        - buyer_type (Govt/PSU/Private/Proprietorship etc.)
        - mse_sector (Manufacturing/Services)
        - mse_state
        - has_written_agreement (bool)
        - buyer_gst_compliant (bool)
        
        Derived:
        - amount_per_invoice (total / num invoices)
        - overdue_severity (days_overdue / 45)
        - is_government_buyer (bool)
        - cross_state_dispute (buyer and seller in different states)
        """
    
    def prepare_training_data(self, cases: List[Dict]) -> pd.DataFrame:
        """Convert list of historical cases to feature matrix"""

2. src/nyayapredictor/outcome_predictor.py:

class OutcomePredictor:
    def __init__(self, model_path: str = None):
        self.model = self._load_or_train_model(model_path)
    
    def _load_or_train_model(self, model_path):
        """Load pre-trained model or train on synthetic case data.
        
        Uses CatBoost (handles categorical features natively).
        
        Target variables (multi-output):
        1. settlement_probability: 0-1 probability of successful recovery
        2. recovery_percentage: predicted % of claimed amount recovered
        3. resolution_days: predicted days to resolution
        
        Train on 5,000 synthetic historical cases with realistic outcome distributions:
        - Govt/PSU buyers: high recovery (85-100%) but slow (90-180 days)
        - Private Ltd: medium recovery (60-90%) medium speed (45-90 days)
        - Proprietorship: variable (30-100%), often settles in negotiation
        - Large amounts (>10L): slower, more likely to go to arbitration
        - Written agreement: stronger case, higher recovery
        - Cross-state: slightly slower resolution
        """
    
    def predict(self, dispute: DisputeCase) -> CaseOutcomePrediction:
        """Predict outcome for a new dispute.
        Returns: settlement probability, expected recovery %, timeline, strategy recommendation"""
    
    def get_confidence_interval(self, prediction: CaseOutcomePrediction) -> Dict:
        """Return confidence range: {optimistic, expected, pessimistic} scenarios"""
    
    def explain_prediction(self, dispute: DisputeCase, prediction: CaseOutcomePrediction) -> str:
        """LLM-generated explanation of why this prediction was made.
        'Your case has a 78% chance of full recovery because: written agreement exists,
        amount is within typical range, Gujarat MSEFC has 82% settlement rate.'"""

3. src/nyayapredictor/case_similarity.py:

class CaseSimilarityEngine:
    def __init__(self, precedents_path: str, embedding_model: str):
        self.precedents = self._load_precedents(precedents_path)
        self.embedder = SentenceTransformer(embedding_model)
        self.embeddings = self._compute_embeddings()
    
    def find_similar_cases(self, dispute: DisputeCase, top_k: int = 5) -> List[Dict]:
        """Find most similar past cases using:
        1. Semantic similarity on dispute description (sentence-transformers)
        2. Feature similarity on amount, sector, buyer_type, state
        3. Weighted combination: 0.4 semantic + 0.6 feature
        
        For each similar case, return:
        - Case summary
        - Outcome (recovered/settled/dismissed)
        - Recovery percentage
        - Resolution days
        - Similarity score
        - What MSE can learn from this case
        """
    
    def get_precedent_insight(self, similar_cases: List[Dict]) -> str:
        """Generate insight: 'In 4 of 5 similar cases, MSEs recovered 80%+ of their claim.
        Key factor: all had written purchase orders.'"""

4. src/nyayapredictor/buyer_risk_scorer.py:

class BuyerRiskScorer:
    def __init__(self, buyer_data_path: str = None):
        self.buyer_history = self._load_buyer_data(buyer_data_path)
    
    def score_buyer(self, buyer_gstin: str, buyer_name: str, 
                     buyer_type: str) -> BuyerRiskScore:
        """Score buyer risk based on:
        - Past dispute count (from synthetic data)
        - Average payment delay
        - Total outstanding to MSEs
        - GST compliance history
        - Buyer type (Govt = lower risk, Proprietorship = higher risk)
        - Industry sector risk
        
        Score 0-100: 0-25 Low, 26-50 Medium, 51-75 High, 76-100 Critical
        
        In demo mode: generate realistic score based on buyer_type + random factors"""
    
    def get_buyer_report(self, buyer_gstin: str) -> Dict:
        """Detailed buyer report: payment history, dispute history, risk factors"""

5. src/nyayapredictor/timeline_estimator.py:

class TimelineEstimator:
    def __init__(self, msefc_data_path: str):
        self.msefc_data = self._load_msefc(msefc_data_path)
    
    def estimate_timeline(self, dispute: DisputeCase, strategy: str) -> Dict:
        """Estimate resolution timeline:
        - UNP (negotiation): 15-30 days
        - MSEFC conciliation: 30-60 days
        - MSEFC arbitration: 60-90 days
        - Total with appeals: up to 180 days
        
        Factors: MSEFC state efficiency, amount, buyer type, complexity
        
        Returns: {optimistic, expected, pessimistic} days with stage breakdown"""

6. Tests:
- Predict outcome for 5 different dispute types
- Verify prediction changes with case features (higher amount → lower probability)
- Find similar cases for a textile dispute
- Score buyer risk for PSU vs Proprietorship
- Timeline estimation for different states
```

---

## PROMPT 5: SamvadAI — AI Negotiation Agent + Settlement Drafter

```
In the nyayasetu project, build the complete SamvadAI module:

1. src/samvadai/negotiation_engine.py:

class NegotiationEngine:
    def __init__(self, llm_client, prediction_model, templates_path):
        self.llm = llm_client
        self.predictor = prediction_model
        self.templates = self._load_templates(templates_path)
    
    def initialize_negotiation(self, dispute: DisputeCase, 
                                prediction: CaseOutcomePrediction) -> NegotiationState:
        """Start negotiation with optimal opening strategy.
        
        Strategy selection based on case strength:
        - Strong case (>80% predicted recovery): Firm demand, full amount + interest
        - Moderate case (50-80%): Flexible, willing to waive some interest
        - Weak case (<50%): Focus on principal recovery, waive all interest
        
        Opening demand:
        - Always start at 100% of principal + 100% of interest
        - Let buyer negotiate down, not up
        """
    
    def generate_round(self, state: NegotiationState, buyer_response: str = None) -> Dict:
        """Process one round of negotiation.
        
        If first round: send initial demand letter
        If buyer responded: analyze response, generate counter
        
        Uses LLM with NEGOTIATION_STRATEGY_TEMPLATE to decide:
        - How much to concede (if any)
        - What tone to take
        - Whether to escalate
        
        Returns: {message, offer_amount, strategy, should_escalate}"""
    
    def detect_buyer_tactic(self, buyer_message: str) -> str:
        """Detect buyer tactics:
        - 'stalling': asking for more time repeatedly
        - 'disputing_amount': claiming invoice was wrong
        - 'threatening': threatening to stop future business
        - 'ghosting': no response
        - 'partial_offer': offering much less than claimed
        - 'genuine_hardship': buyer claims financial difficulty
        - 'cooperative': buyer willing to settle
        
        Returns tactic name + recommended response"""
    
    def should_escalate(self, state: NegotiationState) -> Tuple[bool, str]:
        """Decide if negotiation should stop and escalate to MSEFC.
        Escalate if: 3+ rounds without progress, buyer ghosting, buyer disputing in bad faith."""
    
    def generate_negotiation_summary(self, state: NegotiationState) -> str:
        """Summary of negotiation: rounds, offers, outcome"""

2. src/samvadai/offer_optimizer.py:

class OfferOptimizer:
    def __init__(self):
        pass
    
    def calculate_optimal_offer(self, principal: float, interest: float,
                                  case_strength: str, round_number: int,
                                  buyer_type: str) -> Dict:
        """Calculate the optimal offer for this round.
        
        Round 1: Demand 100% (principal + interest)
        Round 2: If buyer countered, meet halfway between demands but never below principal
        Round 3: Final offer — principal + 50% interest
        Beyond Round 3: Escalate to MSEFC
        
        Government buyers: More patient (they pay eventually, just slow)
        Private buyers: More aggressive (they may try to avoid payment)
        
        Returns: {demand, minimum_acceptable, concession_from_last, justification}"""
    
    def calculate_settlement_value(self, principal: float, interest: float,
                                     resolution_days: int) -> float:
        """Calculate the time-value-adjusted settlement amount.
        A bird in hand: ₹8L now might be worth more than ₹10L in 6 months."""

3. src/samvadai/settlement_drafter.py:

class SettlementDrafter:
    def __init__(self, llm_client, templates_path):
        self.llm = llm_client
        self.templates = self._load_templates(templates_path)
    
    def draft_settlement(self, dispute: DisputeCase, settlement_amount: float,
                          payment_schedule: List[Dict], 
                          interest_waived: float = 0) -> SettlementAgreement:
        """Generate legally valid settlement agreement.
        
        Must include:
        - Party details (MSE and Buyer with full addresses)
        - Recitals: background of the dispute
        - Settlement amount and breakdown
        - Payment schedule (lump sum or installments)
        - Interest waiver (if any, with MSE's consent)
        - Default clause: if buyer misses payment, full amount + interest revives
        - Confidentiality clause
        - Governing law: MSMED Act 2006
        - Jurisdiction: MSEFC of relevant state
        - Signature blocks
        """
    
    def draft_demand_notice(self, dispute: DisputeCase) -> str:
        """Pre-litigation demand notice. Formal, citing MSMED Act sections."""
    
    def draft_msefc_reference(self, dispute: DisputeCase) -> str:
        """Draft the formal reference application to MSEFC.
        Includes: parties, facts, invoices, interest calculation, relief sought."""

4. src/samvadai/tactic_detector.py:

class TacticDetector:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def analyze_buyer_response(self, message: str, context: NegotiationState) -> Dict:
        """Analyze buyer's message to detect negotiation tactics.
        Uses LLM to classify tone, intent, and recommended response.
        
        Returns: {tactic, confidence, buyer_intent, recommended_response, 
                  red_flags, is_acting_in_good_faith}"""

5. src/samvadai/communication_gen.py:

class CommunicationGenerator:
    def __init__(self, llm_client, templates_path):
        self.llm = llm_client
        self.templates = self._load_templates(templates_path)
    
    def generate_message(self, dispute: DisputeCase, message_type: str,
                          language: str = "en", **kwargs) -> str:
        """Generate negotiation communication.
        Types: initial_demand, reminder, counter_offer, escalation_warning,
               settlement_offer, final_notice, acceptance, rejection
        
        Each message: professional, legally accurate, cites MSMED Act sections,
        includes specific amounts and dates.
        
        Available in Hindi and English."""
    
    def generate_sms(self, dispute: DisputeCase, message_type: str) -> str:
        """Short SMS version (160 chars) for quick notifications"""

6. Tests:
- 3-round negotiation simulation: MSE demands 10L, buyer counters 6L, settle at 8.5L
- Tactic detection: stalling message, threatening message, cooperative message
- Settlement draft for ₹5L dispute
- Demand notice generation
- Communication in Hindi
```

---

# PHASE 3: ANALYTICS & DASHBOARD (Prompts 6-8)

---

## PROMPT 6: VasooliTracker — Recovery Analytics & Synthetic Data

```
In the nyayasetu project, build VasooliTracker and generate all synthetic data:

1. scripts/generate_synthetic_data.py:

def generate_disputes(n=5000):
    """Generate 5,000 synthetic dispute records.
    Distribution:
    - States: MH (18%), DL (12%), GJ (10%), TN (10%), KA (8%), UP (10%), RJ (7%), WB (5%), others (20%)
    - Buyer types: Private Ltd 40%, Proprietorship 20%, PSU 15%, LLP 10%, Govt 8%, Others 7%
    - Sectors: Manufacturing 60%, Services 40%
    - Amounts: ₹25K-₹50L (log-normal distribution, median ₹2.5L)
    - Days overdue: 30-730 (right-skewed, median 90 days)
    - With agreement: 60% yes
    - Outcomes: Full recovery 35%, Partial 30%, In process 20%, Dismissed 10%, Unresolved 5%
    - Resolution days: 30-365 (depends on stage reached)
    """

def generate_case_outcomes(n=5000):
    """Training data for ML model.
    Features: amount, overdue_days, buyer_type, sector, state, has_agreement, etc.
    Target: recovery_percentage, settlement_probability, resolution_days
    
    IMPORTANT: Inject realistic patterns:
    - PSU/Govt buyers: 85% avg recovery but 120+ days
    - Large amounts (>10L): lower probability but higher absolute recovery
    - Written agreement: +15% recovery rate
    - Same-state: -20 days vs cross-state disputes
    - Maharashtra MSEFC: fastest resolution (78 days avg)
    - UP MSEFC: slowest (125 days avg)
    """

def generate_buyer_profiles(n=500):
    """Synthetic buyer payment behavior data.
    Some buyers are repeat offenders (10-15 disputes), most have 1-3.
    Include GST compliance status, industry, typical payment delay."""

def generate_recovery_funnel():
    """Monthly funnel data for 12 months:
    Filed → UNP Started → Settled in UNP → MSEFC Referred → Conciliation → Arbitration → Award → Recovered
    Show improving trend over 12 months as system adoption grows."""

def generate_state_pendency():
    """State-wise: total cases, pending, disposed, recovery rate, avg time."""

Run to generate all CSV files in data/synthetic/.

2. src/vasoolitracker/dispute_analytics.py:

class DisputeAnalytics:
    def __init__(self, disputes_path):
        self.data = pd.read_csv(disputes_path)
    
    def get_overview_metrics(self) -> Dict:
        """total_disputes, total_amount_disputed, total_recovered, recovery_rate, avg_resolution_days"""
    
    def get_stage_funnel(self) -> plotly.Figure:
        """Funnel: Filed → UNP → MSEFC → Conciliation → Arbitration → Award → Recovered"""
    
    def get_monthly_trend(self) -> plotly.Figure:
        """Line chart: disputes filed, resolved, amount recovered per month"""
    
    def get_amount_distribution(self) -> plotly.Figure:
        """Histogram of dispute amounts with percentiles"""
    
    def get_resolution_time_analysis(self) -> plotly.Figure:
        """Box plot: resolution days by buyer type and stage"""
    
    def get_sector_breakdown(self) -> plotly.Figure:
        """Pie chart: disputes by MSE sector"""

3. src/vasoolitracker/geo_analytics.py:

class GeoAnalytics:
    def __init__(self, disputes_path, state_data_path):
        self.disputes = pd.read_csv(disputes_path)
        self.states = self._load_states(state_data_path)
    
    def get_state_heatmap(self) -> folium.Map:
        """India map: states colored by total disputed amount or dispute count.
        Popup: state name, total disputes, total amount, recovery rate."""
    
    def get_delayed_payment_hotspots(self) -> folium.Map:
        """Bubble map: districts with worst delayed payments."""
    
    def get_state_comparison(self) -> plotly.Figure:
        """Grouped bar: states × recovery rate × avg resolution days"""

4. src/vasoolitracker/buyer_blacklist.py:

class BuyerBlacklist:
    def __init__(self, disputes_path, buyer_profiles_path):
        self.disputes = pd.read_csv(disputes_path)
        self.buyers = pd.read_csv(buyer_profiles_path)
    
    def get_repeat_offenders(self, min_disputes: int = 3) -> pd.DataFrame:
        """Buyers with 3+ disputes — the worst payment offenders."""
    
    def get_blacklist_table(self) -> plotly.Figure:
        """Table: top 20 worst buyers by total outstanding + dispute count"""
    
    def check_buyer(self, buyer_gstin: str) -> Dict:
        """Quick check: is this buyer a known offender? Warning for MSE."""

5. src/vasoolitracker/msefc_performance.py:

class MSEFCPerformance:
    def __init__(self, state_pendency_path, disputes_path):
        self.pendency = pd.read_csv(state_pendency_path)
        self.disputes = pd.read_csv(disputes_path)
    
    def get_msefc_ranking(self) -> plotly.Figure:
        """Rank MSEFCs by: disposal rate, avg resolution time, recovery rate"""
    
    def get_pendency_analysis(self) -> plotly.Figure:
        """State-wise pendency: how many cases pending vs disposed"""
    
    def get_90_day_compliance(self) -> plotly.Figure:
        """% of cases disposed within statutory 90 days, by state"""

6. Test: Generate all data, verify charts render, metrics make sense.
```

---

## PROMPT 7: Streamlit Dashboard

```
In the nyayasetu project, build the complete Streamlit dashboard in app.py:

GLOBAL CONFIG:
- st.set_page_config(page_title="NyayaSetu — न्यायसेतु", page_icon="⚖️", layout="wide")
- Color scheme: Justice themed — Deep Navy (#1B2A4A) primary, Gold (#C5A23E) accents, White backgrounds, Red (#C0392B) for overdue alerts, Green (#27AE60) for recovered
- Professional law-firm quality design
- Sidebar: NyayaSetu logo area, "न्यायसेतु" Sanskrit name, navigation, system status, language selector

PAGE 1 — HOME:
- Hero: "NyayaSetu — Bridge to Justice" with ⚖️
- Tagline: "AI that fights for India's MSMEs to recover ₹8.1 trillion in delayed payments"
- 4 module cards:
  - VaadPatra (📋): "Smart Dispute Filing — enter Udyam, we build your case"
  - NyayaPredictor (🔮): "Outcome Prediction — know your chances before you file"
  - SamvadAI (🤝): "AI Negotiation — we negotiate with the buyer for you"
  - VasooliTracker (📊): "Recovery Dashboard — track every rupee"
- Quick stats: Disputes Filed | Amount Recovered | Success Rate | Avg Resolution Days
- Interest calculator widget: "Quick check — how much is YOUR buyer liable for?" (Enter amount + days overdue → instant calculation)

PAGE 2 — FILE A DISPUTE (VaadPatra + NyayaPredictor combined):
Multi-step wizard:

**Step 1: Your Details**
- Udyam number input OR "Use Demo MSE" dropdown
- Fetch & display MSE profile
- OR Upload Udyam certificate (OCR)

**Step 2: Buyer Details**
- Buyer name, type (dropdown), GSTIN, state, address
- "Check Buyer Risk" button → BuyerRiskScore display with risk badge (🟢🟡🟠🔴)

**Step 3: Invoice Details**
- Add invoices one by one:
  - Invoice number, date, amount, delivery date
  - Written agreement? Credit period?
- Upload invoice images (OCR extraction)
- Running total: "Total Outstanding: ₹X,XX,XXX"
- Auto-calculated interest shown in real-time: "Interest (Section 16): ₹XX,XXX"
- Days overdue badge per invoice (🟡 30-90 | 🟠 90-180 | 🔴 180+)

**Step 4: Case Assessment**
- Eligibility check result (✅ Eligible / ❌ Not Eligible with reason)
- Case strength badge: Strong 💪 / Moderate ⚡ / Weak ⚠️
- NyayaPredictor results:
  - Gauge chart: Settlement probability (e.g., 78%)
  - Progress bar: Expected recovery (e.g., ₹8.5L of ₹10L)
  - Timeline: "Expected resolution: 45-90 days"
  - Strategy recommendation
- Similar cases cards (top 3 with outcomes)
- "This is AI-assisted analysis, not legal advice" disclaimer

**Step 5: Review & File**
- Complete case summary card
- Interest calculation table (month-by-month breakdown)
- "Generate Filing Documents" → downloads:
  - Demand notice (PDF)
  - MSEFC reference application (PDF)
  - Interest calculation sheet (Excel)
- "File on ODR Portal" button (link to odr.msme.gov.in with auto-filled info)

PAGE 3 — NEGOTIATE (SamvadAI):
Interactive negotiation simulator:
- Select a dispute case (from filed cases or demo)
- Show negotiation dashboard:
  - Left panel: MSE's position (your claim, minimum acceptable)
  - Right panel: Buyer's responses
  - Center: AI strategy recommendation
- Negotiation rounds:
  - Round 1: AI generates initial demand → show message
  - "Buyer responded with..." text input → AI analyzes tactic + generates counter
  - Round by round progress with offer visualization
- Settlement graph: showing offers converging over rounds
- "Generate Settlement Agreement" button when agreed
- "Escalate to MSEFC" button if negotiation fails

PAGE 4 — RECOVERY DASHBOARD (VasooliTracker):
Admin-level analytics:
- Top metrics: Total Disputed ₹ | Recovered ₹ | Pending ₹ | Recovery Rate %
- Recovery funnel: Filed → UNP → MSEFC → Award → Recovered
- Tabs:
  - Overview: monthly trends, stage distribution, amount distribution
  - Geographic: India heatmap of delayed payments by state
  - Buyers: repeat offender blacklist table, buyer type analysis
  - MSEFC Performance: state-wise ranking, 90-day compliance
  - Sectors: which MSE sectors are worst hit
- All charts interactive (Plotly) with filters

PAGE 5 — INTEREST CALCULATOR (standalone tool):
- Simple, clean calculator anyone can use
- Input: principal amount, overdue start date, end date (default today)
- Shows: applicable RBI rate, monthly rate, month-by-month compound table
- Big number: "Total amount owed to you: ₹X,XX,XXX"
- "Under Section 16, MSMED Act 2006" citation
- Download calculation as PDF/Excel
- Shareable link with pre-filled amounts

PAGE 6 — LEGAL GUIDE:
- Collapsible sections explaining MSMED Act Sections 15-24
- Step-by-step guide: "How to file a delayed payment complaint"
- FAQ: "Can I claim interest?", "What if buyer threatens to stop business?", "What if buyer is in another state?"
- MSEFC directory: state-wise contact details
- Timeline expectations: UNP → MSEFC → Arbitration → Award → Execution
- Important: "This is AI-generated information for educational purposes. Consult a lawyer for specific legal advice."

PAGE 7 — ABOUT:
- Project description, architecture, team, tech stack, privacy policy

STATE MANAGEMENT + ERROR HANDLING:
Same patterns as other projects — session state, demo mode fallbacks, toast notifications.
```

---

## PROMPT 8: Integration, Demo & Testing

```
In the nyayasetu project, build integration, demo, and testing:

1. scripts/generate_synthetic_data.py — Run to create all CSVs.

2. scripts/seed_database.py — Create tables, load reference + synthetic data.

3. scripts/demo_flow.py:

def run_demo():
    """End-to-end demo in <3 minutes.
    
    Scene 1: Smart Dispute Filing (60 seconds)
    - Enter Udyam: UDYAM-RJ-01-0012345 (auto parts manufacturer)
    - Buyer: XYZ Engineering Pvt Ltd, GSTIN: 08AABCX1234E1ZP
    - 3 invoices totaling ₹4,50,000, overdue 120 days
    - Auto-calculate interest: ₹28,456 at 18.00% (3× 6.00% RBI rate)
    - Total claim: ₹4,78,456
    - Eligibility: ✅ Valid
    
    Scene 2: Case Prediction (30 seconds)
    - Settlement probability: 82%
    - Expected recovery: ₹4,20,000 (93% of principal)
    - Timeline: 45-75 days
    - Similar cases: 3 past cases with similar outcomes
    - Strategy: "Start with firm demand. Private Ltd buyer likely to settle in UNP."
    
    Scene 3: AI Negotiation (60 seconds)
    - Round 1: Demand ₹4,78,456 → formal demand letter generated
    - Buyer counters: "We can pay ₹3,00,000 in 30 days"
    - AI detects: partial_offer tactic, buyer acting in good faith
    - Round 2: Counter ₹4,25,000 (waive ₹53,456 interest, demand full principal)
    - Buyer accepts ₹4,10,000
    - AI: "Accept — this is 91% of principal, good outcome."
    - Settlement agreement auto-generated
    
    Scene 4: Dashboard (30 seconds)
    - 5,000 disputes, ₹85 crore disputed, ₹61 crore recovered (72%)
    - State heatmap: Maharashtra worst, Gujarat best recovery rate
    - Top offenders list
    - MSEFC performance ranking
    
    Print: "NyayaSetu: Helping India's MSMEs recover what's rightfully theirs."
    """

4. tests/test_integration.py:
- test_full_pipeline: Udyam → dispute → prediction → negotiation → settlement
- test_interest_accuracy: Manual verification of compound interest calculation
- test_prediction_model: Verify model outputs reasonable predictions
- test_negotiation_flow: 3-round negotiation with different buyer tactics
- test_demo_mode: Everything works without Ollama/PostgreSQL

5. Database, logging — same patterns.
```

---

# PHASE 4: DEPLOYMENT & POLISH (Prompts 9-11)

---

## PROMPT 9: Docker, Deployment & Setup

```
Same pattern as other projects:
- Dockerfile, docker-compose.yml
- setup.sh (Docker), setup_local.sh (local)
- README.md with Quick Start, Architecture, Modules, Tech Stack, Legal Disclaimer
- .env.example
- 3 modes: FULL (Docker+Ollama+PostgreSQL), PARTIAL (Ollama only), DEMO (zero dependencies)
```

---

## PROMPT 10: Report Generation

```
Build src/reporting/:
1. demand_notice_pdf: Professional demand notice citing MSMED Act sections with interest breakdown
2. msefc_reference_pdf: Formal MSEFC reference application ready for filing
3. interest_calculation_excel: Month-by-month compound interest Excel with formulas
4. settlement_agreement_pdf: Complete settlement agreement
5. case_summary_pdf: One-page case summary for MSE's records
6. admin_report_pdf: Monthly recovery analytics report for MSEFC/Ministry
```

---

## PROMPT 11: Final Polish & Demo Prep

```
1. Error handling: All modules have fallbacks. App never crashes.
2. UI polish: Overdue badges (🟡🟠🔴), risk scores (🟢🟡🟠🔴), justice-themed icons (⚖️📜🔨)
3. Legal disclaimer on EVERY page: "NyayaSetu provides AI-assisted information. This is not legal advice. Consult a qualified lawyer."
4. Pre-cached LLM responses for 5 demo disputes
5. Interest calculator MUST be tested against manual calculations — 100% accurate
6. All MSMED Act sections must be verbatim accurate
7. Demo video script: 3 minutes, show filing → prediction → negotiation → dashboard
8. System works in 3 modes: FULL / PARTIAL / DEMO
```

---

# EXECUTION ORDER & TIMING

| # | Prompt | What It Builds | Est. Time | Priority |
|---|--------|----------------|-----------|----------|
| 0 | Setup | Skeleton + dependencies | 30 min | REQUIRED |
| 1 | Legal Data | MSMED Act, precedents, templates, models | 3-4 hours | CRITICAL — legal accuracy wins/loses |
| 2 | LLM + Interest | Ollama client, compound interest calculator | 2-3 hours | CRITICAL — interest calc must be perfect |
| 3 | VaadPatra | Smart dispute filing + OCR + voice | 3-4 hours | REQUIRED |
| 4 | NyayaPredictor | Outcome prediction + case similarity | 3-4 hours | THE DIFFERENTIATOR |
| 5 | SamvadAI | Negotiation + settlement drafting | 3-4 hours | HIGH VALUE |
| 6 | VasooliTracker | Analytics + synthetic data generation | 2-3 hours | REQUIRED |
| 7 | Dashboard | Streamlit UI (7 pages) | 3-4 hours | REQUIRED |
| 8 | Integration | Demo flow, tests, seeding | 2-3 hours | REQUIRED |
| 9 | Deployment | Docker, README | 1-2 hours | IMPORTANT |
| 10 | Reports | PDF/Excel generation | 2 hours | NICE-TO-HAVE |
| 11 | Polish | Error handling, legal disclaimers | 2 hours | IMPORTANT |

**Total: 27-37 hours of focused work**

---

# CRITICAL SUCCESS FACTORS

1. **Interest calculation MUST be 100% legally accurate.** Section 16 specifies compound interest at 3× RBI bank rate with monthly rests. If your calculator gives wrong numbers, instant credibility loss with the legal experts on the jury. Test against manual calculations.

2. **NyayaPredictor is your killer feature.** No competitor will build case outcome prediction for MSME disputes. Show: "Your case has 82% settlement probability based on 5,000 similar cases." This is what makes judges remember you.

3. **MSMED Act sections must be verbatim accurate.** Section 15, 16, 17, 18, 19, 22, 24 — every citation must be correct. The jury includes Director (RAMP and Legal Cell) from Ministry of MSME.

4. **Legal disclaimers everywhere.** "This is AI-assisted information, not legal advice." On every page. Government evaluators care about responsible AI.

5. **The negotiation simulation is a demo showstopper.** Show a 3-round negotiation where AI detects buyer stalling, adjusts strategy, and generates a settlement agreement. Judges will be impressed by the practical application.

6. **RBI bank rate must be current.** Check the latest rate before submission. Wrong rate = wrong interest = failed credibility.

7. **Show the ODR portal integration.** Reference odr.msme.gov.in explicitly. Show that your tool is designed to work WITH the portal they built, not replace it.

8. **Pre-cache demo responses.** No LLM wait during demo recording. 5 pre-cached scenarios that run instantly.

9. **45-day rule is the legal anchor.** Everything flows from: "Buyer must pay within 45 days. If they don't, Section 16 interest kicks in." Make this crystal clear in your UI.

10. **The ₹8.1 trillion number is your opening line.** "₹8.1 trillion stuck in delayed payments. Less than 1% of MSMEs use formal dispute resolution. NyayaSetu changes that."

# ⚖️ NyayaSetu — न्यायसेतु
### Bridge to Justice for India's MSMEs

> *"63 million MSMEs. ₹10.7 lakh crore in delayed payments. One platform to fight back."*

---

## 🇮🇳 What is NyayaSetu?

**NyayaSetu** (meaning *Bridge to Justice* in Sanskrit/Hindi) is an AI-powered Online Dispute Resolution (ODR) platform built specifically for India's Micro, Small and Medium Enterprises (MSMEs). It helps small business owners recover money owed to them by large buyers — without lawyers, without jargon, and without leaving their shop.

Built for the **IndiaAI Innovation Challenge 2026 (Problem Statement 1)**, NyayaSetu transforms a complex, intimidating legal process into a simple, voice-driven, AI-guided experience accessible to any MSME owner in India, in their own language.

---

## 🚨 The Problem We Solve

India's 63 million MSMEs are the backbone of the economy — contributing 30% of GDP and employing over 110 million people. Yet they face a silent crisis:

| Problem | Scale |
|---------|-------|
| Total delayed payments owed to MSMEs | **₹10.7 lakh crore** |
| Average payment delay | **60–120 days** past due |
| MSMEs that ever file a formal claim | **< 1%** |
| Cases pending at MSEFC councils | **Growing every year** |

**Why don't MSMEs file?**
- 😰 Fear of losing future business from the same buyer
- 📚 No knowledge of the MSMED Act or their legal rights
- 🗣️ Language barriers — most owners aren't comfortable in English
- 📄 Complex paperwork — demand notices, MSEFC applications, interest calculations
- 🏛️ Perceived cost and time of legal proceedings
- ⚖️ Power asymmetry — small supplier vs large corporation

**The existing ODR portal (`odr.msme.gov.in`) requires technical literacy, English proficiency, and legal knowledge — less than 1% of affected MSMEs have ever used it.**

NyayaSetu removes every single one of these barriers.

---

## 💡 How NyayaSetu Works

NyayaSetu guides an MSME owner through the complete dispute resolution lifecycle in **4 steps**:

```
STEP 1          STEP 2            STEP 3              STEP 4
File            Predict           Negotiate           Track
────────        ─────────         ──────────          ──────
Voice/OCR  →    AI predicts   →   AI negotiates   →   Recovery
dispute         your chances      with the buyer      dashboard
filing          of recovery       on your behalf      & analytics
```

Each step is handled by a dedicated AI module. Together, they take an MSME from *"I don't know where to start"* to *"My legal documents are ready and the negotiation is underway"* — in under 10 minutes.

---

## 🧩 The Four Core Modules

---

### 1. 📋 VaadPatra — Smart Dispute Filing Engine

> *"File your case in your own voice, in your own language."*

VaadPatra (meaning *Petition* in Hindi) is the filing module. It accepts disputes through **voice or manual forms**, processes invoices using OCR, and builds a legally complete case file automatically.

#### Key Features:

**🎤 Voice Filing (Bhashini Integration)**
- Speak your dispute details in **Hindi, Tamil, Marathi, Bengali, Telugu, Kannada, or Gujarati**
- Bhashini ULCA APIs transcribe your speech in real time (ASR)
- The system extracts structured data — Udyam numbers, GSTINs, invoice amounts — from natural speech
- A 5-step guided conversational flow walks through: Enterprise ID → Buyer Details → Invoice Amounts → Confirmation
- Text-to-speech playback so the system reads responses back to you (TTS)
- Graceful fallback to text mode if voice services are unavailable

**📄 Invoice OCR (PaddleOCR)**
- Upload scanned or photographed invoices (JPG, PNG, PDF)
- PaddleOCR extracts invoice number, date, amount, and party details automatically
- Supports multilingual invoice formats (Hindi, English, regional scripts)
- Results are editable before submission

**🏷️ AI Dispute Sub-Category Classifier**
- Automatically classifies your dispute into one of **7 legal categories**:
  1. Delayed Payment — Goods
  2. Delayed Payment — Services
  3. Partial Payment
  4. Payment Withheld for Quality Dispute
  5. Contractual Terms Violation
  6. Payment Acknowledgment Missing
  7. Cross Invoice / PO Mismatch
- Shows confidence score and applicable **MSMED Act sections** (15, 16, 17, 18, 19)
- Powered by Qwen 2.5 14B LLM with rule-based keyword fallback

**📋 Smart Document Checklist**
- Generates a **document gap analysis** based on your dispute category
- Color-coded cards: Green (uploaded), Red (missing critical), Yellow (recommended)
- Weighted completeness score (80% mandatory + 20% recommended)
- Tells you exactly which documents are missing and how they affect your case strength
- Categories: Mandatory, Recommended, Optional

**🔴 Overdue Intelligence**
- Tracks each invoice's overdue status with color-coded badges:
  - 🟢 < 30 days: Recent
  - 🟡 30–89 days: Overdue
  - 🟠 90–179 days: Significantly Overdue
  - 🔴 180+ days: Critically Overdue
- Calculates **Section 16 compound interest** per invoice (monthly rests, 3× RBI bank rate)

**🧮 Buyer Risk Scoring**
- Instant AI risk assessment of the buyer (score out of 100)
- Risk categories: Low / Medium / High / Critical
- Based on buyer type, industry, historical payment patterns, and dispute frequency

---

### 2. 🔮 NyayaPredictor — Case Outcome Prediction Engine

> *"Know your chances before you file — with AI that explains itself."*

NyayaPredictor uses machine learning to predict the likely outcome of your dispute before you commit to the filing process.

#### Key Features:

**🤖 CatBoost ML Ensemble**
- Trained on **5,000 synthetic MSME dispute cases**
- Predicts: Settlement Probability %, Expected Recovery Amount (INR), Resolution Timeline (days)
- Uses a 5-model ensemble (CatBoost + RandomForest) for reliability
- Handles categorical features natively (buyer type, state, industry sector)
- Returns a real confidence score for each prediction

**📊 Plotly Gauge Chart**
- Visual settlement probability dial with colored zones:
  - 🔴 0–50%: Weak case — consider improving documentation
  - 🟡 50–80%: Moderate case — negotiate carefully
  - 🟢 80–100%: Strong case — press for full recovery

**🔍 SHAP Explainability (Explainable AI)**
- Waterfall chart showing **exactly which factors** drove the prediction
- Top 5 contributing features with positive/negative impact percentages
- Example: "Overdue duration contributed +12% | Buyer type contributed −8%"
- Plain-English explanation of the prediction reasoning
- **This is not a black box** — every prediction is fully explained

**📐 Case Similarity Search**
- Finds the **top 3 most similar historical cases** using sentence-transformer embeddings (all-MiniLM-L6-v2)
- Shows outcome and recovery % for each similar case
- Provides real precedent data before you decide your strategy

**📈 Benchmark Comparison**
- 3-way comparison: Your Case vs Average MSME Case vs Best Similar Case
- Shows where you stand relative to historical outcomes

**⚡ Timeline Estimation**
- Optimistic and pessimistic timeline range in days
- Breaks down by stage: Negotiation → MSEFC Conciliation → Arbitration → Recovery

**📋 Strategy Recommendation**
- AI recommends one of three strategies: Negotiate Directly / Escalate to MSEFC / Pursue Arbitration

---

### 3. 🤝 SamvadAI — AI Negotiation Engine

> *"AI negotiates with the buyer on your behalf — you stay in control."*

SamvadAI (meaning *Dialogue AI*) is the negotiation module. It conducts multi-round negotiations with the buyer, detects manipulation tactics, and generates legally grounded demand communications — all in any supported language.

#### Key Features:

**💬 Round-Based Negotiation Flow**
- AI generates **legally grounded demand letters** referencing Sections 15 and 16
- Each round references the accumulating statutory interest (pressure increases over time)
- Chat-bubble UI with clear MSE vs Buyer message distinction
- Tracks: Current Offer, Minimum Acceptable Amount, Round Number, Status

**🤖 AI Buyer Simulator**
- 5 buyer behavioral profiles for training or demo:
  1. **Cooperative** — willing to negotiate in good faith
  2. **Stalling** — delays, asks for more time, needs approvals
  3. **Aggressive** — threatens to cut business, disputes validity
  4. **Genuine Hardship** — cash flow problems, requests installments
  5. **Ghosting** — stops responding entirely
- Judges can run a complete live demo without manually role-playing the buyer
- Powered by Qwen 2.5 14B in production; scripted fallback in DEMO mode

**🕵️ Tactic Detection (9 Tactics)**
Automatically detects buyer negotiation tactics and recommends counter-strategies:

| Tactic | Detection Signal | Counter Strategy |
|--------|-----------------|-----------------|
| Stalling | "Need more time", "Get approval" | Set firm deadline, cite Section 16 interest |
| Disputing Amount | "Wrong invoice", "Quality issue" | Request formal dispute in writing |
| Threatening | "Stop orders", "Blacklist" | Document threat, notify MSEFC |
| Ghosting | Empty/no response | Send formal legal notice |
| Partial Offer | "Can pay 50%" | Counter with 90% minimum |
| Genuine Hardship | "Cash flow problems" | Offer installment plan |
| Aggressive | "No legal basis" | Cite Sections 15–17 explicitly |
| Blame Shifting | "Not our fault" | Request documented evidence |
| Cooperative | Reasonable response | Accelerate toward settlement |

**📊 Sentiment Intelligence Dashboard**
- **Real-time Sentiment Gauge**: Score from -1.0 (hostile) to +1.0 (cooperative)
- **Cooperation vs Aggression bar chart**: Side-by-side for current round
- **Sentiment Trend Line**: Tracks buyer mood across all rounds
- **Escalation Risk Bar**: 0–100% probability of needing MSEFC
- **Detected Emotions**: Frustration, goodwill, pressure, etc.
- **Predictive Commentary**: "Settlement unlikely in 2 rounds" or "Close to agreement"

**📈 Offer Convergence Chart**
- Plotly line chart showing MSE offers and buyer counter-offers over rounds
- Visually shows whether negotiation is converging or diverging

**🌐 Multilingual Negotiation**
- Auto-detects buyer response language (Hindi, Tamil, Bengali, Telugu, Kannada, Gujarati, English)
- Bhashini NMT translates responses automatically with translation cache
- Per-message "Translate" button for instant cross-language reading
- Voice input for buyer responses via Bhashini ASR

**📝 Settlement Package Generation**
When a deal is reached, NyayaSetu generates:
- Flexible installment plan options: Lump Sum (15 days) / 2 Equal / 3 Monthly / Custom (1–12 installments)
- **AI-drafted Settlement Agreement** with WHEREAS clauses, payment schedule, default consequences, confidentiality clause, and governing law
- Inline PDF preview + one-click download
- **Escalate to MSEFC** button with draft reference application if negotiation fails

---

### 4. 📊 RecoveryTracker — Recovery Intelligence Dashboard

> *"Track every rupee across every dispute. Make data-driven decisions."*

RecoveryTracker provides a comprehensive analytics dashboard for MSMEs tracking multiple disputes and for policy-makers monitoring systemic payment compliance.

#### Key Features:

**🔢 KPI Metrics with Delta Tracking**
- Total Disputes Filed (month-over-month change)
- Total Amount at Stake (in INR)
- Overall Recovery Rate (%)
- Average Resolution Time (days)

**🔍 Smart Filters**
- Date range slider (month-based)
- State multiselect filter
- Buyer type multiselect (Central Govt, State Govt, PSU, Private Ltd, etc.)
- Amount range slider (INR min–max)
- All charts and metrics update dynamically on filter change

**📊 Interactive Charts (Plotly)**
- **Dispute Trend Chart**: Filed vs Recovered over time
- **Recovery Rate by Buyer Type**: Which buyer categories pay most reliably
- **Amount Distribution Chart**: Distribution of dispute sizes
- **Stage Funnel Chart**: Visualizes case flow from Filed → Recovered

**🗺️ State Heatmap (Folium)**
- Interactive map of India
- Dispute density by state, color-coded by intensity
- Click states to see dispute counts and amounts

**🏛️ MSEFC Performance Tracking**
- State-wise MSEFC performance ranking
- 90-day conciliation compliance chart (Section 18 statutory deadline)
- Identifies which states are resolving disputes fastest

**🚨 Buyer Blacklist**
- Table of highest-risk buyers across the full portfolio
- Based on dispute frequency, amount withheld, and payment delay patterns
- Helps MSMEs avoid bad buyers before entering new contracts

**🏭 Sector Analysis**
- Breakdown of disputes by industry sector
- Identifies which sectors have the highest dispute rates

**📤 One-Click PDF Export**
- Generates a professional admin report with all metrics and highlights
- Suitable for MSEFC submission, bank loan applications, or internal review

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit 1.41 | Web interface, multi-page navigation |
| **LLM** | Qwen 2.5 14B via Ollama | Dispute analysis, negotiation, classification, settlement drafting |
| **ML Model** | CatBoost + RandomForest | Case outcome prediction (5-model ensemble) |
| **Explainability** | SHAP TreeExplainer | Prediction transparency and feature attribution |
| **Embeddings** | all-MiniLM-L6-v2 | Case similarity search (sentence-transformers) |
| **Voice** | Bhashini ULCA APIs | ASR (speech recognition), TTS (voice output), NMT (translation) |
| **OCR** | PaddleOCR | Multilingual invoice data extraction |
| **Backend** | FastAPI | REST API layer |
| **Database** | PostgreSQL (prod) / SQLite (local) | Case persistence |
| **Cache** | Redis | Session and translation caching |
| **Documents** | ReportLab Platypus + OpenPyXL | Professional PDF and Excel generation |
| **Charts** | Plotly + Folium | Interactive visualizations and maps |
| **Data Models** | Pydantic v2 | Strict typed data validation |
| **Deployment** | Docker Compose | Three deployment modes |

---

## 🌐 Language Support

NyayaSetu supports **8 Indian languages** — fully translated UI and Bhashini voice:

| Language | UI Translation | Voice (ASR/TTS) | Auto-Detect |
|----------|---------------|-----------------|-------------|
| English | ✅ | ✅ | ✅ |
| हिन्दी (Hindi) | ✅ | ✅ | ✅ |
| தமிழ் (Tamil) | ✅ | ✅ | ✅ |
| मराठी (Marathi) | ✅ | ✅ | ✅ |
| বাংলা (Bengali) | ✅ | ✅ | ✅ |
| తెలుగు (Telugu) | ✅ | ✅ | ✅ |
| ಕನ್ನಡ (Kannada) | ✅ | ✅ | ✅ |
| ગુજરાતી (Gujarati) | ✅ | ✅ | ✅ |

---

## 📄 Legal Documents Generated

NyayaSetu automatically generates **6 types of legal documents**:

| Document | Format | Purpose |
|----------|--------|---------|
| Demand Notice | PDF | Formal payment demand citing Section 15–16 |
| MSEFC Reference Application | PDF | Application to state facilitation council |
| Settlement Agreement | PDF | Legally binding settlement with payment schedule |
| Interest Calculation Breakdown | PDF + Excel | Monthly compound interest statement |
| Case Summary Report | PDF | Complete dispute overview for advisors |
| Admin Dashboard Report | PDF | Analytics report for policy-makers |

All PDFs use ReportLab Platypus with professional legal formatting, inline preview, and one-click download.

---

## ⚖️ Legal Framework

NyayaSetu is built on India's existing legal infrastructure for MSME protection:

| Section | Content | How NyayaSetu Uses It |
|---------|---------|----------------------|
| **Section 15** | Buyer must pay within 45 days of delivery/acceptance | Enforces 45-day deadline, flags violations |
| **Section 16** | Compound interest at 3× RBI bank rate with monthly rests | Powers all interest calculations |
| **Section 17** | Buyer liability for recovery of principal + interest | Included in demand notices |
| **Section 18** | Reference to MSEFC; 90-day conciliation deadline | MSEFC filing + compliance tracking |
| **Section 19** | MSEFC award enforcement | Escalation pathway |

**Current RBI Bank Rate:** 6.50%
**Statutory Interest Rate:** 19.50% per annum (3× RBI rate, monthly rests)
**Statutory Payment Deadline:** 45 days from delivery/acceptance

---

## 🚀 Deployment Modes

NyayaSetu supports three deployment modes for different environments:

| Mode | Description | Dependencies |
|------|-------------|-------------|
| **DEMO** | Full UI with synthetic data and rule-based AI | None — works offline |
| **PARTIAL** | Adds real Qwen 2.5 LLM and Bhashini voice | Ollama (local GPU) |
| **FULL** | Production stack with PostgreSQL, Redis, all APIs | Docker Compose |

This means judges can evaluate the system even without GPU access — DEMO mode always works.

---

## 🔒 Privacy & Compliance

- **100% Local Processing**: The LLM (Qwen 2.5 14B) runs on-device via Ollama. No MSME data is ever sent to external AI services.
- **DPDP Act 2023 Aligned**: Follows Digital Personal Data Protection Act principles — data minimization, purpose limitation, user consent.
- **India-Stack Native**: Uses only government-aligned APIs (Bhashini, Udyam, GST, ODR Portal).
- **No Vendor Lock-in**: Fully open-source stack — Streamlit, Ollama, CatBoost, PaddleOCR.
- **SQLite Fallback**: Works completely without cloud database.

---

## 📁 Project Structure

```
nyayasetu/
├── app.py                          # Main Streamlit application (~2,100 lines)
├── config.py                       # Global configuration (RBI rates, API keys)
│
├── src/
│   ├── common/
│   │   ├── models.py               # 11 Pydantic data models
│   │   ├── database.py             # SQLAlchemy ORM (PostgreSQL/SQLite)
│   │   ├── llm_client.py           # Ollama/Qwen 2.5 14B client
│   │   └── i18n.py                 # 8-language translation dictionary
│   │
│   ├── vaadpatra/                  # Module 1: Filing Engine
│   │   ├── dispute_builder.py      # Constructs DisputeCase from form data
│   │   ├── eligibility_checker.py  # MSMED Act eligibility validation
│   │   ├── interest_calculator.py  # Section 16 compound interest
│   │   ├── dispute_classifier.py   # AI 7-category classifier
│   │   ├── document_checker.py     # Smart document gap analysis
│   │   ├── udyam_fetcher.py        # Udyam registration API
│   │   └── gst_validator.py        # GST number validation
│   │
│   ├── nyayapredictor/             # Module 2: Prediction Engine
│   │   ├── outcome_predictor.py    # CatBoost ensemble + SHAP
│   │   ├── case_similarity.py      # Sentence-transformer embeddings
│   │   ├── timeline_estimator.py   # Resolution timeline prediction
│   │   └── buyer_risk_scorer.py    # Buyer risk assessment
│   │
│   ├── samvadai/                   # Module 3: Negotiation Engine
│   │   ├── negotiation_engine.py   # Round-based negotiation logic
│   │   ├── settlement_drafter.py   # LLM settlement agreement generation
│   │   ├── buyer_simulator.py      # 5-profile AI buyer simulation
│   │   └── tactic_detector.py      # 9-tactic detection + strategy
│   │
│   ├── vasoolitracker/             # Module 4: Recovery Dashboard
│   │   └── analytics_engine.py     # Dashboard computation & aggregation
│   │
│   ├── voice/
│   │   ├── bhashini_client.py      # Bhashini ULCA ASR/TTS/NMT client
│   │   └── conversation_engine.py  # 5-step guided voice intake flow
│   │
│   └── reporting/
│       └── __init__.py             # 6-type document generation pipeline
│
├── data/
│   ├── synthetic/
│   │   ├── disputes.csv            # 5,000 synthetic MSME dispute cases
│   │   ├── buyer_profiles.csv      # Buyer risk profiles
│   │   └── state_pendency.csv      # State-level pendency data
│   ├── legal/
│   │   ├── msmed_act_sections.json # MSMED Act Sections 15–19 verbatim
│   │   ├── msefc_directory.json    # State-wise MSEFC contacts
│   │   └── rbi_rates.json          # Historical RBI bank rates
│   └── msme/
│       ├── sample_disputes.json    # Sample cases for Demo Tour
│       └── state_districts.json    # India state/district hierarchy
│
└── tests/                          # 5 test suites
    ├── test_interest_calculator.py
    ├── test_dispute_builder.py
    ├── test_outcome_predictor.py
    ├── test_negotiation_engine.py
    └── test_document_generator.py
```

---

## 🎯 Who Uses NyayaSetu?

**Primary Users:**
- **MSME Owners** — file disputes, track cases, negotiate payments
- **MSME Trade Associations** — bulk case management, analytics

**Secondary Users:**
- **MSEFC Administrators** — case queue management, compliance tracking
- **Policy Makers** — state-level pendency analysis, buyer blacklists
- **Legal Advisors** — case assessment, document generation

**Demo Mode** (no setup required) is suitable for evaluation, training, and workshops.

---

## 📊 Impact Metrics

| Metric | Value |
|--------|-------|
| Dispute cases in training data | 5,000 |
| Average recovery rate (synthetic) | 66.8% |
| Average resolution time | 73 days |
| Languages supported | 8 |
| Legal document types generated | 6 |
| Buyer tactic types detected | 9 |
| Dispute sub-categories classified | 7 |
| ML models in prediction ensemble | 5 |
| MSMED Act sections covered | 5 (Sections 15–19) |
| States with MSEFC directory | All Indian states |
| Python source code | ~3,400 lines across 44 modules |

---

## 🏆 Why NyayaSetu Wins

1. **Voice-First Design**: Built for semi-literate MSME owners, not lawyers
2. **Explainable AI**: SHAP transparency — no black box predictions
3. **Complete Lifecycle**: From voice filing to settlement to MSEFC escalation — one platform
4. **India-Stack Native**: Bhashini, Udyam, GST API, ODR Portal deep-links
5. **Legal Accuracy**: Section 16 interest calculations verified against MSMED Act
6. **Production-Ready**: Three deployment modes, Docker Compose, persistent database
7. **Policy Intelligence**: Not just for MSMEs — provides governance insights
8. **Zero Vendor Lock-in**: Entirely open-source stack, local LLM, no cloud dependency
9. **Demo-Proven**: AI Buyer Simulator enables complete live demo without manual role-playing
10. **Privacy-First**: 100% local processing, DPDP Act 2023 aligned

---

*NyayaSetu v1.0 — Built for IndiaAI Innovation Challenge 2026, PS-1*
*"Bridging the gap between India's strongest MSME laws and the 99% who never use them."*

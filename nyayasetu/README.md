<div align="center">

# ⚖️ NyayaSetu — न्यायसेतु
### *Bridge to Justice for India's MSMEs*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Ollama](https://img.shields.io/badge/LLM-Qwen_2.5_14B-black?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.ai)
[![Bhashini](https://img.shields.io/badge/Voice-Bhashini_ULCA-FF9933?style=for-the-badge)](https://bhashini.gov.in)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)
[![IndiaAI](https://img.shields.io/badge/IndiaAI_Challenge_2026-PS--1_MSME_ODR-6366F1?style=for-the-badge)](https://indiaai.gov.in)

<br/>

> **63 million MSMEs. ₹10.7 lakh crore in delayed payments. Less than 1% ever file a claim.**
>
> NyayaSetu changes that — voice-first, AI-powered, in your language.

<br/>

```
┌─────────────────────────────────────────────────────────────────┐
│  MSME owner speaks in Hindi  →  NyayaSetu files the case       │
│  AI predicts outcome         →  You know your chances upfront  │
│  AI negotiates with buyer    →  You stay in control            │
│  Legal docs auto-generated   →  Ready to file in 10 minutes    │
└─────────────────────────────────────────────────────────────────┘
```

</div>

---

## 🚨 The Problem

India's MSMED Act 2006 gives small businesses powerful legal protection — yet the system fails them:

| Reality | Numbers |
|---------|---------|
| Total delayed payments owed to MSMEs | **₹10.7 lakh crore** |
| MSMEs that ever file a formal claim | **< 1%** |
| Average payment delay past due date | **60–120 days** |
| MSEFC cases pending nationwide | **Growing every year** |

**Why don't MSMEs file?** Language barriers. No legal knowledge. Complex paperwork. Fear of losing future business. NyayaSetu removes every single barrier.

---

## 🧩 Four AI Modules, One Platform

```
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌───────────────────┐
│   📋 VaadPatra   │   │ 🔮 NyayaPredictor│   │   🤝 SamvadAI   │   │ 📊 RecoveryTracker│
│                  │   │                  │   │                  │   │                   │
│  Smart Dispute   │ → │  Case Outcome    │ → │  AI Negotiation  │ → │  Recovery         │
│  Filing Engine   │   │  Prediction      │   │  Engine          │   │  Dashboard        │
│                  │   │                  │   │                  │   │                   │
│  Voice • OCR     │   │  CatBoost + SHAP │   │  Buyer Simulator │   │  State Heatmap    │
│  Classifier      │   │  Similarity      │   │  Tactic Detect   │   │  MSEFC Analytics  │
└──────────────────┘   └──────────────────┘   └──────────────────┘   └───────────────────┘
```

### 📋 VaadPatra — Smart Dispute Filing
- 🎤 **Voice filing in 8 Indian languages** via Bhashini ULCA (ASR + TTS)
- 📄 **Invoice OCR** — PaddleOCR extracts data from scanned invoices automatically
- 🏷️ **AI Dispute Classifier** — 7 legal sub-categories with applicable MSMED Act sections
- 📋 **Smart Document Checklist** — gap analysis with weighted completeness scoring
- 🧮 **Section 16 Interest Calculator** — compound interest at 3× RBI bank rate, monthly rests
- 🔴 **Buyer Risk Scoring** — AI risk assessment (0–100) before you file

### 🔮 NyayaPredictor — Case Outcome Prediction
- 🤖 **CatBoost ML Ensemble** (5 models) trained on 5,000 synthetic MSME dispute cases
- 🔍 **SHAP Explainability** — waterfall chart showing exactly why the AI predicted what it did
- 🔗 **Case Similarity Search** — top-3 most similar historical cases via sentence-transformers
- 📊 **Plotly Gauge** — settlement probability dial with confidence colour zones
- 📐 **Timeline Estimation** — optimistic/pessimistic range in days
- 📈 **3-Way Benchmark** — Your case vs average MSME vs best similar case

### 🤝 SamvadAI — AI Negotiation Engine
- 💬 **Round-based AI negotiation** — legally grounded demand letters citing Sections 15–16
- 🤖 **AI Buyer Simulator** — 5 behavioral profiles (cooperative, stalling, aggressive, hardship, ghosting)
- 🕵️ **9-Tactic Detection** — identifies stalling, threatening, ghosting + tailored counter-strategies
- 📊 **Sentiment Intelligence** — real-time gauge (−1 to +1), emotion detection, escalation risk bar
- 📈 **Offer Convergence Chart** — tracks MSE vs buyer offers across all rounds
- 🌐 **Auto-translation** — Bhashini NMT for cross-language negotiation
- 📝 **Settlement Package** — AI-drafted agreement with flexible installment plans

### 📊 RecoveryTracker — Recovery Intelligence
- 🔢 **KPI dashboard** with month-over-month delta (disputes, amounts, recovery rate)
- 🗺️ **Interactive India Heatmap** — state-level dispute density via Folium
- 🏛️ **MSEFC Performance** — state-wise ranking and 90-day statutory compliance
- 🚨 **Buyer Blacklist** — highest-risk buyers across the portfolio
- 📤 **One-click PDF report** export for MSEFC submission

---

## 🌐 Language Support

| Language | UI | Voice ASR | Voice TTS | Auto-Detect |
|----------|:--:|:---------:|:---------:|:-----------:|
| English | ✅ | ✅ | ✅ | ✅ |
| हिन्दी Hindi | ✅ | ✅ | ✅ | ✅ |
| தமிழ் Tamil | ✅ | ✅ | ✅ | ✅ |
| मराठी Marathi | ✅ | ✅ | ✅ | ✅ |
| বাংলা Bengali | ✅ | ✅ | ✅ | ✅ |
| తెలుగు Telugu | ✅ | ✅ | ✅ | ✅ |
| ಕನ್ನಡ Kannada | ✅ | ✅ | ✅ | ✅ |
| ગુજરાતી Gujarati | ✅ | ✅ | ✅ | ✅ |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit 1.41 with custom CSS theming (3 themes) |
| **LLM** | Qwen 2.5 14B via Ollama — 100% local, zero cloud |
| **ML** | CatBoost + RandomForest ensemble · SHAP TreeExplainer |
| **Embeddings** | `all-MiniLM-L6-v2` sentence-transformers |
| **Voice** | Bhashini ULCA APIs — ASR · TTS · NMT |
| **OCR** | PaddleOCR (multilingual invoice extraction) |
| **Database** | SQLite (default) · PostgreSQL (production) · SQLAlchemy ORM |
| **Documents** | ReportLab Platypus (PDF) · OpenPyXL (Excel) |
| **Maps** | Folium + streamlit-folium |
| **Charts** | Plotly |
| **Deployment** | Docker Compose |

---

## ⚡ Quick Start

### DEMO Mode — works instantly, zero external dependencies

```bash
git clone https://github.com/ShreyanshVaibhaw/NyayaSetu.git
cd NyayaSetu/nyayasetu
pip install -r requirements.txt
python scripts/generate_synthetic_data.py
python scripts/seed_database.py
streamlit run app.py
```

Open **http://localhost:8501** 🚀

### PARTIAL Mode — with local LLM (Qwen 2.5 14B)

```bash
# 1. Install Ollama from https://ollama.ai
ollama pull qwen2.5:14b

# 2. Run the app
APP_MODE=PARTIAL streamlit run app.py
```

### FULL Mode — complete Docker stack

```bash
cp .env.example .env      # add your Bhashini API keys
docker-compose up --build
```

---

## 📁 Project Structure

```
nyayasetu/
├── app.py                      # Main Streamlit app (~2,100 lines)
├── config.py                   # Global config (RBI rates, API keys)
│
├── src/
│   ├── common/                 # Pydantic models, DB ORM, i18n (8 languages)
│   ├── vaadpatra/              # Filing: OCR, classifier, interest, eligibility
│   ├── nyayapredictor/         # ML prediction, SHAP, case similarity
│   ├── samvadai/               # Negotiation, tactic detection, settlement
│   ├── vasoolitracker/         # Analytics, heatmap, MSEFC performance
│   ├── voice/                  # Bhashini ASR/TTS/NMT client
│   ├── llm/                    # Ollama client + prompt templates
│   └── reporting/              # 6-type PDF/Excel document generation
│
├── data/
│   ├── synthetic/              # 5,000 MSME dispute training cases
│   ├── legal/                  # MSMED Act sections, MSEFC directory, RBI rates
│   ├── msme/                   # State/district data, sample disputes
│   └── odr/                    # Dispute categories, settlement templates
│
└── tests/                      # 5 test suites
```

---

## 📄 Auto-Generated Legal Documents

| Document | Format | Purpose |
|----------|--------|---------|
| Demand Notice | PDF | Formal payment demand (Sections 15–16) |
| MSEFC Reference Application | PDF | File with state facilitation council |
| Settlement Agreement | PDF | Binding settlement with payment schedule |
| Interest Calculation Breakdown | PDF + Excel | Monthly compound interest statement |
| Case Summary | PDF | Full overview for legal advisors |
| Admin Dashboard Report | PDF | Analytics report for policy makers |

---

## ⚖️ Legal Framework — MSMED Act 2006

| Section | Provision | How NyayaSetu Uses It |
|---------|-----------|----------------------|
| **§15** | Buyer must pay within 45 days | Deadline tracking, violation flags |
| **§16** | Compound interest at 3× RBI bank rate | All interest calculations (monthly rests) |
| **§17** | Buyer liability for principal + interest | Demand notice auto-generation |
| **§18** | MSEFC reference; 90-day conciliation | Filing generation + compliance tracking |
| **§19** | Award enforcement | MSEFC escalation pathway |

> **Current:** RBI Bank Rate 6.50% → Statutory Interest Rate **19.50% p.a.** (monthly rests)

---

## 🔒 Privacy & Security

- **100% local LLM** — Qwen 2.5 14B via Ollama. No MSME data ever sent to external AI services.
- **DPDP Act 2023 aligned** — data minimization, purpose limitation, user consent.
- **India-Stack native** — Bhashini, Udyam, GST validation, ODR portal deep-links.
- **No vendor lock-in** — fully open-source, runs on any Linux server or GPU instance.

---

## 🧪 Tests

```bash
python -m pytest tests/ -v
```

Suites: `test_vaadpatra` · `test_nyayapredictor` · `test_samvadai` · `test_vasoolitracker` · `test_integration`

---

## 🏆 IndiaAI Innovation Challenge 2026 — PS-1

Built for **Problem Statement 1: AI Enabled Virtual Negotiation Assistance for MSME Delayed Payment Recovery**

| Requirement | NyayaSetu |
|-------------|-----------|
| Voice-based filing | ✅ Bhashini ASR in 8 languages |
| Multilingual support | ✅ Full UI + voice in 8 Indian languages |
| AI outcome prediction | ✅ CatBoost ensemble + SHAP explainability |
| Negotiation assistance | ✅ Round-based AI + 9-tactic detection |
| Legal document generation | ✅ 6 document types auto-generated |
| ODR portal integration | ✅ Deep-link to odr.msme.gov.in |
| MSEFC workflows | ✅ Filing, tracking, 90-day compliance |
| Data privacy | ✅ 100% local LLM, DPDP Act aligned |

---

## 📜 Disclaimer

NyayaSetu provides AI-assisted information only. **This is not legal advice.** Consult a qualified lawyer for case-specific guidance. Interest calculations are indicative and subject to judicial determination.

---

<div align="center">

**⚖️ NyayaSetu — Bridging the gap between India's strongest MSME laws and the 99% who never use them**

*Made with ❤️ for India's 63 million MSMEs*

</div>

# NyayaSetu — न्यायसेतु
## Bridge to Justice: AI-Powered Virtual Negotiation Assistant for MSME Delayed Payments
### IndiaAI Innovation Challenge 2026 — Problem Statement 1 (MSME – ODR)

---

## 1. Executive Summary

**NyayaSetu** (न्यायसेतु — "Bridge to Justice") is an AI-powered virtual negotiation and dispute resolution assistant that helps India's Micro and Small Enterprises (MSEs) recover delayed payments through the MSME ODR Portal. The platform automates complaint filing, predicts case outcomes, conducts AI-assisted negotiations, and provides a national recovery intelligence dashboard — transforming India's ₹8.1 trillion delayed payment crisis into an actionable, AI-driven resolution pipeline.

**Tagline:** "AI that fights for India's MSMEs to recover ₹8.1 trillion in delayed payments"

**The Problem:**
- ₹8.1 trillion (~$97 billion) stuck in delayed payments to MSMEs
- Less than 1% of eligible enterprises use the MSME Samadhaan/ODR portal
- MSEs lack legal awareness, document preparation skills, and negotiation capacity
- MSEFCs overburdened: 50,000+ pending cases, 90-day statutory deadline routinely missed
- Power asymmetry: large buyers exploit small suppliers' fear of retaliation
- Low digital literacy, language barriers, complex filing procedures

**Our Solution:**
NyayaSetu provides end-to-end AI assistance from dispute detection to recovery — smart filing via OCR and Udyam integration, ML-based outcome prediction with similar case matching, AI negotiation agent that drafts and optimizes counter-offers, and a national delayed payment intelligence dashboard. Built on India's government stack (Bhashini, Udyam, ODR Portal) with fully open-source technology.

**Impact Target:** Enable 50,000+ MSEs to file and recover delayed payments within 2 years, recovering ₹2,000+ crore in stuck capital.

---

## 2. Problem Statement Analysis

### PS1: AI-Enabled Virtual Negotiation Assistance for MSME Delayed Payments

The Ministry of MSME seeks AI solutions to strengthen the MSME ODR Portal (launched June 2025) with intelligent capabilities for:
1. **Automated intake and document analysis** — OCR invoices, extract dispute data, auto-fill complaints
2. **Outcome prediction based on historical data** — predict settlement probability and recovery amounts
3. **Multilingual interaction support** — serve MSEs in their preferred language
4. **Settlement drafting assistance** — generate legally valid negotiation documents

### The Scale of the Crisis

| Metric | Value |
|--------|-------|
| Total MSMEs in India | 6.3 crore (63 million) |
| Estimated delayed payments | ₹8.1 trillion |
| Cases filed on Samadhaan (total since 2017) | ~2.3 lakh |
| % of eligible MSEs who file | <1% |
| Cases disposed by MSEFCs | ~1.1 lakh |
| Cases pending | ~1.2 lakh |
| Average disposal time | 90-180 days (statutory limit: 90 days) |
| MSE Facilitation Councils (MSEFCs) | 36 (one per state/UT) |
| ODR Portal launched | June 27, 2025 (MSME Day) |
| ODR Scheme budget | ₹189 crore (2023-2027) |

### Why MSEs Don't File

1. **Fear of retaliation** — buyer may stop future orders (biggest barrier)
2. **Lack of awareness** — don't know about MSMED Act, MSEFC, or ODR portal
3. **Complex process** — multi-step filing with legal terminology
4. **Language barrier** — portal/process in English, MSEs speak regional languages
5. **Document preparation** — don't know what evidence is needed, how to calculate interest
6. **Low trust** — past Samadhaan portal had high rejection rate, slow processing
7. **Power asymmetry** — MSE feels powerless against PSU/corporate buyer
8. **Cost** — perceived cost of legal assistance

### Legal Framework: MSMED Act 2006 (Sections 15-24)

| Section | What It Says | Why It Matters |
|---------|-------------|----------------|
| **15** | Buyer must pay within agreed period (max 45 days) or 15 days if no agreement | Defines when payment is "delayed" |
| **16** | Compound interest at 3× RBI bank rate, monthly rests | The penalty — makes delayed payment expensive |
| **17** | MSE can refer dispute to MSEFC; must be disposed in 90 days | Fast-track resolution mechanism |
| **18** | MSEFC does conciliation, then arbitration if needed | Two-stage dispute resolution |
| **19** | 75% deposit to challenge MSEFC award | Makes awards practically enforceable |
| **22** | Buyer must file half-yearly return of delayed payments | Disclosure obligation (rarely complied with) |
| **24** | These sections override other laws | MSMED Act has overriding effect |

### MSME ODR Portal Process

```
MSE Files Complaint on ODR Portal
         ↓
Pre-MSEFC Stage (Voluntary)
  ├── Digital Guided Pathway (information + self-help)
  └── Unmanned Negotiation Process (UNP)
         ↓ (if UNP fails or parties opt out)
MSEFC Stage
  ├── Conciliation (Mediation by MSEFC)
  └── Arbitration (if conciliation fails)
         ↓
Award Passed (binding, enforceable as court decree)
         ↓
75% deposit required to challenge
```

---

## 3. Solution Architecture: NyayaSetu

### 3.1 Four Modules

```
┌──────────────────────────────────────────────────────────────────────┐
│                    NyayaSetu — न्यायसेतु                              │
│              Bridge to Justice for India's MSMEs                      │
├────────────────┬────────────────┬────────────────┬───────────────────┤
│   VaadPatra    │ NyayaPredictor │   SamvadAI     │  VasooliTracker   │
│    वादपत्र      │  न्यायप्रेडिक्टर │    संवादAI      │   वसूलीट्रैकर     │
│ Smart Filing   │ Case Prediction│ AI Negotiation │ Recovery Dashboard│
├────────────────┼────────────────┼────────────────┼───────────────────┤
│• Udyam auto-   │• ML outcome    │• Strategy gen  │• Dispute tracking │
│  fetch         │  prediction    │• Counter-offer │• Geo heatmap      │
│• Invoice OCR   │• Similar case  │  optimization  │• Buyer blacklist  │
│• Interest calc │  matching      │• Tactic detect │• MSEFC rankings   │
│  (Sec 16)      │• Buyer risk    │• Settlement    │• Recovery funnel  │
│• Eligibility   │  scoring       │  agreement     │• Trend analytics  │
│  validation    │• Timeline est  │  drafting      │• Sector analysis  │
│• Voice filing  │• Confidence    │• Multilingual  │• Admin reports    │
│  (Bhashini)    │  intervals     │  communication │                   │
└────────────────┴────────────────┴────────────────┴───────────────────┘
         ↕                ↕                ↕                ↕
┌──────────────────────────────────────────────────────────────────────┐
│              Government Integration Layer                             │
│  Udyam API │ GST API │ ODR Portal │ Bhashini │ Samadhaan │ AIKosh   │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.2 Module Details

#### Module 1: VaadPatra (वादपत्र) — Smart Dispute Filing Engine

**Purpose:** Reduce dispute filing from 2-3 hours of form-filling to 5 minutes of conversation.

**Input → Output:**
- Input: Udyam number + buyer GSTIN + invoice photos/details
- Output: Complete ODR-ready complaint with interest calculation, demand notice, and MSEFC reference application

**Core Pipeline:**
```
Udyam Number → Fetch MSE Data → Validate Eligibility
                                        ↓
Buyer GSTIN → Validate GST → Buyer Profile
                                        ↓
Invoice Images → PaddleOCR → LLM Extraction → Structured Invoice Data
                                        ↓
Invoice Data → Interest Calculator (Section 16) → Interest Breakdown
                                        ↓
All Data → Dispute Builder → Complete Filing Package
                                        ↓
Filing Package → Generate: Demand Notice PDF + MSEFC Application + Interest Sheet
```

**Key Features:**
- **Udyam Auto-Fetch:** Enter Udyam number → pull enterprise data, validate registration date vs invoice dates
- **Invoice OCR:** Photograph invoice with phone → PaddleOCR extracts text → LLM structures into invoice_number, date, amount, buyer details
- **Interest Calculator:** Legally precise compound interest at 3× RBI bank rate with monthly rests, handling rate changes during overdue period
- **Eligibility Validator:** Checks all prerequisites — Udyam date before invoice, Micro/Small classification, overdue past statutory limit
- **Voice-Guided Filing:** MSE speaks in Hindi/Tamil/Marathi → Bhashini transcribes → LLM extracts dispute data → auto-fills complaint
- **Document Generation:** Professional PDF demand notice citing MSMED Act sections, MSEFC reference application, interest calculation Excel

**Critical Legal Accuracy:**
```
Interest Calculation Formula (Section 16):
  Monthly Rate = (3 × RBI Bank Rate) / 12
  e.g., RBI rate = 6.00% → Monthly rate = 18.00% / 12 = 1.50% per month
  
  Month 1: Balance = Principal × (1 + 0.015)
  Month 2: Balance = Month1 × (1 + 0.015)
  ...
  Interest = Final Balance - Principal
  
  Example: ₹5,00,000 principal, 6 months overdue:
  Month 1: ₹5,07,500 | Month 2: ₹5,15,113 | Month 3: ₹5,22,839
  Month 4: ₹5,30,682 | Month 5: ₹5,38,642 | Month 6: ₹5,46,722
  Total Interest: ₹46,722
```

#### Module 2: NyayaPredictor (न्यायप्रेडिक्टर) — Case Outcome Prediction

**Purpose:** Help MSEs make informed decisions by predicting case outcomes before filing.

**THE KILLER DIFFERENTIATOR — no competitor will build this.**

**Core ML Pipeline:**
```
Dispute Features → CatBoost Model → Predictions
                                        ↓
                   ├── Settlement Probability (0-100%)
                   ├── Expected Recovery % (of claimed amount)
                   ├── Estimated Resolution Days
                   └── Recommended Strategy
                                        ↓
Dispute Description → Sentence-Transformers → Similarity Search → Top 5 Similar Cases
                                        ↓
Buyer GSTIN → Buyer History Analysis → Buyer Risk Score (0-100)
                                        ↓
All Results → LLM → Human-Readable Explanation
```

**ML Model Details:**

Training Data: 5,000 synthetic historical cases modeled on real MSEFC patterns.

Features:
| Feature | Type | Impact |
|---------|------|--------|
| dispute_amount (log) | Numeric | Higher amount → slightly lower probability but longer timeline |
| days_overdue | Numeric | More overdue → stronger case legally |
| buyer_type | Categorical | PSU/Govt = high recovery, slow; Private = variable |
| mse_sector | Categorical | Manufacturing slightly better than Services |
| state | Categorical | Maharashtra/Gujarat MSEFCs fastest |
| has_written_agreement | Boolean | +15% recovery rate |
| buyer_gst_compliant | Boolean | Compliant buyers more likely to settle |
| previous_disputes | Numeric | Repeat offender = lower voluntary settlement |
| invoice_count | Numeric | More invoices = stronger case (pattern of delay) |
| cross_state | Boolean | Cross-state adds 20 days to resolution |

**Case Similarity Engine:**
- Embeds dispute descriptions using all-MiniLM-L6-v2
- Combined scoring: 40% semantic similarity + 60% feature similarity
- Returns top 5 similar past cases with outcomes
- Example: "In 4 of 5 similar cases involving Private Ltd buyers with ₹3-5L disputes, MSEs recovered 85%+ within 60 days"

**Buyer Risk Scoring:**
- Score 0-100 based on: past disputes, payment delays, GST compliance, buyer type, industry sector
- Categories: Low (0-25), Medium (26-50), High (51-75), Critical (76-100)
- Displayed as risk badge when MSE enters buyer GSTIN

#### Module 3: SamvadAI (संवादAI) — AI Negotiation Agent

**Purpose:** Conduct or assist the Unmanned Negotiation Process (UNP) on the ODR portal.

**Core Negotiation Pipeline:**
```
Dispute + Prediction → Strategy Selection → Opening Demand
                                                    ↓
                                            Send to Buyer
                                                    ↓
Buyer Response → Tactic Detection → Strategy Adjustment → Counter-Offer
                                                    ↓
                     ├── If settled → Settlement Agreement Generator
                     ├── If progress → Next round
                     └── If stalled → Escalation to MSEFC
```

**Negotiation Strategies:**
| Case Strength | Strategy | Opening | Concession Limit |
|---------------|----------|---------|-----------------|
| Strong (>80%) | Firm Demand | 100% principal + interest | Waive up to 30% interest |
| Moderate (50-80%) | Flexible | 100% principal + interest | Waive up to 100% interest, hold principal |
| Weak (<50%) | Principal Focus | 100% principal only | Accept 80% of principal |

**Tactic Detection:**
The LLM analyzes buyer's responses and classifies their tactic:
- **Stalling:** "We need more time to verify invoices" → Response: Set deadline, cite 90-day statutory limit
- **Disputing Amount:** "The invoices were incorrect" → Response: Request specific objection, provide proof of delivery
- **Threatening:** "We'll stop giving you orders" → Response: Cite Section 24 (MSMED Act overrides), remind of legal consequences
- **Ghosting:** No response → Response: Escalation notice, 7-day ultimatum
- **Partial Offer:** "We can pay 50%" → Response: Counter at 90%, show interest liability
- **Genuine Hardship:** "We're facing cash flow issues" → Response: Offer installment plan
- **Cooperative:** "Let's settle this" → Response: Accept reasonable terms, draft agreement

**Settlement Agreement Generator:**
- Legally valid format with all required clauses
- Party details, recitals, settlement terms, payment schedule
- Default clause: if buyer misses payment, full amount + interest revives
- Confidentiality, governing law, jurisdiction, signature blocks
- Generated in English + Hindi

#### Module 4: VasooliTracker (वसूलीट्रैकर) — Recovery Intelligence Dashboard

**Purpose:** National-level intelligence on delayed payments for MSEFCs, Ministry, and MSEs.

**For MSEs:**
- Track your dispute: current stage, next action, expected timeline
- Interest accumulation: real-time counter showing growing liability
- Payment history: when buyer pays, how much, interest waived

**For MSEFC Administrators:**
- Case load analytics: pending, disposed, overdue past 90 days
- Performance metrics: disposal rate, average resolution time
- Comparison with other state MSEFCs

**For Ministry of MSME:**
- National heatmap: state-wise delayed payment distribution
- Buyer blacklist: repeat offenders across states
- Sector analysis: which industries are worst for delayed payments
- Recovery funnel: Filed → UNP → MSEFC → Award → Recovered
- Women MSE tracking (TEAM initiative alignment)
- Monthly/quarterly trend reports

**Analytics Components:**
- Dispute Funnel: Filed → UNP Started → UNP Settled → MSEFC Referred → Conciliation → Arbitration → Award → Recovered
- Geographic Heatmap: India map with state-wise coloring by total disputed amount
- Buyer Blacklist Table: top 50 repeat offenders by total outstanding
- MSEFC Performance Ranking: states ranked by disposal rate and 90-day compliance
- Sector Breakdown: treemap of disputes by MSE sector
- Amount Distribution: histogram with percentiles (₹25K to ₹50L)
- Monthly Trends: filings, disposals, recovery amounts over 12 months

---

## 4. Technical Architecture

### 4.1 Technology Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| LLM | Qwen 2.5 14B via Ollama | Best open-source at this size, Apache 2.0, excellent structured JSON output |
| Embeddings | all-MiniLM-L6-v2 | Fast semantic similarity for case matching |
| ML Prediction | CatBoost | Native categorical feature handling, interpretable feature importance |
| OCR | PaddleOCR | Multilingual OCR for Hindi/English invoices |
| Voice/NLP | Bhashini ULCA APIs | Government ASR/TTS/NMT, 22 languages, free |
| Backend | FastAPI | Async, auto-docs, production-ready |
| Frontend | Streamlit | Rapid dashboard, data-native, Python ecosystem |
| Database | PostgreSQL | Relational for disputes, invoices, outcomes |
| Caching | Redis | Session management, rate limiting |
| Deployment | Docker Compose | One-command deployment |
| Monitoring | Prometheus + Grafana | Infrastructure and application metrics |

### 4.2 System Flow

```
                    ┌─────────────────┐
                    │   MSE (Phone/   │
                    │   Web Browser)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Streamlit UI  │
                    │   (Port 8501)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   FastAPI       │
                    │   (Port 8000)   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼──────┐   ┌────────▼───────┐   ┌───────▼──────┐
│   Ollama     │   │  PostgreSQL    │   │   Redis      │
│  Qwen 2.5   │   │  (Disputes,    │   │  (Sessions,  │
│  (Port 11434)│   │   Outcomes)    │   │   Cache)     │
└──────────────┘   └────────────────┘   └──────────────┘
        │
        │ External APIs (Demo Mode: Mocked)
        │
┌───────▼──────────────────────────────────────────────┐
│  Udyam API │ GST API │ Bhashini │ ODR Portal │ RBI   │
└──────────────────────────────────────────────────────┘
```

### 4.3 Docker Compose Setup

```yaml
services:
  nyayasetu:
    build: .
    ports: ["8501:8501"]
    depends_on: [postgres, ollama, redis]
    environment:
      - OLLAMA_HOST=ollama
      - POSTGRES_URI=postgresql://nyayasetu:nyayasetu2026@postgres:5432/nyayasetu
  
  postgres:
    image: postgres:16
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: nyayasetu
      POSTGRES_USER: nyayasetu
      POSTGRES_PASSWORD: nyayasetu2026
  
  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
  
  redis:
    image: redis:7
    ports: ["6379:6379"]
```

---

## 5. Government Integration Points

| API/System | Purpose | Status |
|-----------|---------|--------|
| **MSME ODR Portal** (odr.msme.gov.in) | File disputes, track status, conduct UNP | Integration target — our tool assists MSEs to file here |
| **Udyam Portal** (udyamregistration.gov.in) | Pull MSE data from registration number | API placeholder, OCR fallback |
| **GST Portal** (gst.gov.in) | Validate buyer GSTIN, check compliance | API placeholder, format validation |
| **Samadhaan Portal** (samadhaan.msme.gov.in) | Historical dispute data reference | Data reference |
| **Bhashini** (bhashini.gov.in) | ASR/TTS/NMT for 22 Indian languages | ULCA APIs, free for government use |
| **RBI** (rbi.org.in) | Current bank rate for interest calculation | Manual update + web scraping |
| **AIKosh** (aikosh.indiaai.gov.in) | Training datasets, compute resources | Dataset access |
| **IndiaAI Compute** | GPU infrastructure for model inference | Deployment target |
| **DigiLocker** | Verify Udyam certificates, PAN, GSTIN | Document verification |
| **DPDP Act 2023** | Privacy compliance framework | Full compliance required |

---

## 6. AI/ML Models & Approach

### 6.1 Case Outcome Prediction (CatBoost)

**Architecture:**
- Model: CatBoost Classifier + Regressor (multi-output)
- Training: 5,000 synthetic historical cases
- Features: 12 features (6 numerical, 6 categorical)
- Targets: settlement_probability, recovery_percentage, resolution_days
- Validation: 5-fold stratified cross-validation

**Expected Performance:**
| Metric | Target | Method |
|--------|--------|--------|
| Settlement prediction accuracy | >80% | CatBoost with SHAP explanations |
| Recovery amount MAE | <15% of claimed | CatBoost regressor |
| Resolution time MAE | <20 days | CatBoost regressor |

**Feature Importance (expected):**
1. buyer_type (25%) — Government buyers pay but slowly, private variable
2. dispute_amount (18%) — Larger amounts have different dynamics
3. has_written_agreement (15%) — Written PO = strong case
4. days_overdue (12%) — More overdue = more interest leverage
5. state/MSEFC (10%) — Some MSEFCs much faster than others
6. buyer_gst_compliance (8%) — Compliant buyers more likely to settle
7. Other features (12%)

### 6.2 Case Similarity (Sentence-Transformers)

**Architecture:**
- Model: all-MiniLM-L6-v2 (384-dimensional embeddings)
- Index: 5,000+ case descriptions embedded
- Similarity: Cosine similarity (semantic) + Euclidean distance (features)
- Combined: 0.4 × semantic + 0.6 × feature similarity

### 6.3 Legal NER & Document Understanding (LLM)

**Model:** Qwen 2.5 14B via Ollama
**Tasks:**
- Invoice OCR text → structured JSON (invoice number, date, amount, parties)
- Dispute description generation from MSE's conversational input
- Negotiation message generation with legal citations
- Settlement agreement drafting
- Buyer tactic classification from response text

### 6.4 Compound Interest Calculator (Rule-Based)

**Not ML — pure mathematical computation per Section 16:**
- Monthly compounding: A = P × (1 + r/12)^n
- Rate: 3 × RBI bank rate (currently 3 × 6.00% = 18.00% p.a.)
- Handles rate changes mid-period
- Month-by-month breakdown for transparency
- **This must be 100% accurate — tested against manual calculations**

---

## 7. Synthetic Data Strategy

For Stage 1 prototype, all data is synthetic but realistic:

### 7.1 Dispute Records (5,000)

Distribution designed to mirror real MSEFC patterns:
- **States:** Maharashtra 18%, Delhi 12%, Gujarat 10%, Tamil Nadu 10%, Karnataka 8%, UP 10%, Rajasthan 7%, West Bengal 5%, Others 20%
- **Buyer Types:** Private Ltd 40%, Proprietorship 20%, PSU 15%, LLP 10%, Govt 8%, Others 7%
- **Sectors:** Manufacturing 60% (auto parts, textiles, chemicals, food processing, steel), Services 40% (IT, logistics, consulting)
- **Amounts:** Log-normal distribution, range ₹25K-₹50L, median ₹2.5L
- **Days Overdue:** Right-skewed, range 30-730 days, median 90 days
- **Outcomes:** Full recovery 35%, Partial settlement 30%, In process 20%, Dismissed 10%, Unresolved 5%

### 7.2 Case Outcomes for ML Training (5,000)

Injected realistic patterns:
- PSU/Govt buyers: 85% avg recovery, 120+ days resolution
- Private Ltd: 65% avg recovery, 60-90 days
- Proprietorship: 50% avg recovery, highly variable
- Written agreement: +15% recovery rate vs no agreement
- Same-state disputes: -20 days vs cross-state
- Maharashtra MSEFC: 78 days avg (fastest)
- Uttar Pradesh MSEFC: 125 days avg (slowest)
- Amount >₹10L: +30 days, slightly lower probability but higher absolute recovery

### 7.3 Buyer Profiles (500)

- 10-15% repeat offenders (5+ disputes)
- GST compliance: 80% compliant, 20% non-compliant
- Industry distribution matching real economy
- Payment delay patterns: some seasonal (construction), some chronic (retail)

### 7.4 Recovery Funnel (12 months)

Monthly improving trend showing system adoption:
- Month 1: 400 filed → 250 UNP → 100 settled → 150 MSEFC → 80 awarded → 60 recovered
- Month 12: 900 filed → 700 UNP → 400 settled → 300 MSEFC → 250 awarded → 200 recovered

---

## 8. User Flows

### 8.1 MSE Filing a Dispute (Voice Flow — Hindi)

```
NyayaSetu: "नमस्ते! न्यायसेतु में आपका स्वागत है। मैं आपकी पेमेंट वसूली में 
            मदद करूँगा। कृपया अपना उद्यम रजिस्ट्रेशन नंबर बताइए।"

MSE:       "UDYAM-RJ-01-0012345"

NyayaSetu: "धन्यवाद! आपकी कंपनी 'राजस्थानी ऑटो पार्ट्स' जोधपुर से है। 
            माइक्रो एंटरप्राइज, मैन्युफैक्चरिंग। क्या यह सही है?"

MSE:       "हाँ, सही है। XYZ इंजीनियरिंग ने मेरा पेमेंट नहीं दिया।"

NyayaSetu: "XYZ इंजीनियरिंग — क्या आपके पास उनका GSTIN नंबर है?"

MSE:       "हाँ, 08AABCX1234E1ZP"

NyayaSetu: "GST verified ✅ — XYZ Engineering Pvt Ltd, Jodhpur।
            ⚠️ बायर रिस्क स्कोर: 62/100 (High Risk) — इस बायर के खिलाफ 
            पहले भी 3 शिकायतें दर्ज हैं।
            अब बताइए, कितने बिल बाकी हैं?"

MSE:       "3 बिल हैं — एक 2 लाख का दिसंबर का, एक 1.5 लाख जनवरी, 
            और एक 1 लाख फरवरी का"

NyayaSetu: "समझ गया। आपके 3 बिल:
            1. ₹2,00,000 — दिसंबर 2025
            2. ₹1,50,000 — जनवरी 2026
            3. ₹1,00,000 — फरवरी 2026
            कुल मूलधन: ₹4,50,000
            
            Section 16 के तहत ब्याज (3× RBI दर = 18% प्रति वर्ष):
            कुल ब्याज: ₹28,456
            
            आपका कुल दावा: ₹4,78,456
            
            📊 NyayaPredictor: आपके केस में 82% संभावना है कि पूरा पैसा 
            मिलेगा। अनुमानित समय: 45-75 दिन।
            
            क्या आप शिकायत दर्ज करना चाहते हैं?"

MSE:       "हाँ, करो!"

NyayaSetu: "✅ आपकी शिकायत तैयार है! मैंने बनाया:
            1. डिमांड नोटिस (PDF) — बायर को भेजने के लिए
            2. ODR पोर्टल की शिकायत — फाइल करने के लिए
            3. ब्याज कैलकुलेशन शीट (Excel)
            
            पहले डिमांड नोटिस भेजें, 15 दिन में जवाब न आए तो 
            ODR पोर्टल पर फाइल करें। मैं negotiation में भी मदद करूँगा।"
```

### 8.2 AI Negotiation Flow

```
Round 1: NyayaSetu sends formal demand to buyer
┌─────────────────────────────────────────────────────────────┐
│ "Dear XYZ Engineering Pvt Ltd,                              │
│  This is to inform you that ₹4,50,000 is outstanding        │
│  against invoices #INV-001, #INV-002, #INV-003.             │
│  As per Section 15 of MSMED Act, payment was due within     │
│  45 days. Under Section 16, compound interest at 18% p.a.   │
│  is ₹28,456. Total claim: ₹4,78,456.                       │
│  We request settlement within 15 days to avoid MSEFC filing.│
│  Regards, Rajasthani Auto Parts"                            │
└─────────────────────────────────────────────────────────────┘

Round 2: Buyer responds: "We can pay ₹3,00,000 in 30 days"
NyayaSetu AI Analysis:
  - Tactic: partial_offer (66% of principal)
  - Buyer acting in good faith (willing to pay something)
  - Recommendation: Counter at ₹4,25,000 (waive interest, demand principal)

NyayaSetu Counter:
┌─────────────────────────────────────────────────────────────┐
│ "Thank you for your willingness to settle. However,         │
│  ₹3,00,000 covers only 67% of the principal outstanding.    │
│  As a gesture of goodwill, we are willing to waive the      │
│  statutory interest of ₹28,456. We request settlement at    │
│  ₹4,25,000 (94% of principal) payable within 15 days."     │
└─────────────────────────────────────────────────────────────┘

Round 3: Buyer agrees to ₹4,10,000
NyayaSetu: "This represents 91% of your principal — a good outcome.
            Generating settlement agreement..."
→ Auto-generates legally valid settlement agreement PDF
```

---

## 9. Performance Targets

| Metric | Target | Method |
|--------|--------|--------|
| Interest calculation accuracy | 100% | Rule-based, verified against manual |
| Case outcome prediction accuracy | >80% | CatBoost with cross-validation |
| Similar case retrieval relevance | >85% | Semantic + feature similarity |
| Invoice OCR accuracy | >90% | PaddleOCR + LLM extraction |
| Dispute filing time | <5 minutes | vs 2-3 hours manual |
| Negotiation message quality | Expert-rated >4/5 | LLM with legal templates |
| Voice recognition accuracy | >88% | Bhashini ASR with legal vocabulary |
| Buyer tactic detection | >85% | LLM classification |
| Languages (Phase 1) | 4 (Hindi, English, Tamil, Marathi) | Bhashini |
| Languages (Phase 2) | 22 (all Bhashini-supported) | Bhashini expansion |
| System latency (filing) | <3 seconds | Cached + async processing |

---

## 10. Competitive Landscape

| Solution | What It Does | Gap NyayaSetu Fills |
|----------|-------------|---------------------|
| **MSME ODR Portal** | Government filing platform | Portal exists but MSEs can't navigate it — we provide AI assistance layer |
| **Samadhaan Portal** | Old filing system (redirects to ODR now) | Was just a filing tool, no intelligence |
| **Presolv360** | Commercial ODR service | Paid legal service, not AI-powered, not MSME-specific |
| **Agami (ODR Prize)** | ODR ecosystem builder | Policy-level, not a filing/negotiation tool |
| **Legal chatbots (generic)** | General legal Q&A | Not MSMED Act specialized, no outcome prediction, no interest calculation |
| **Aezo AI** | MSME digital onboarding | General MSME AI, not dispute resolution |

**NyayaSetu's Unique Edge:**
1. **Only AI with case outcome prediction** for MSME disputes
2. **Only tool that calculates interest precisely** per Section 16
3. **Only AI negotiation agent** for MSME delayed payments
4. **Designed for ODR Portal integration** — works WITH government, not around it
5. **Voice-first** — accessible to Tier 2/3 MSEs in their language

---

## 11. Responsible AI Framework

### Fairness
- No bias in case prediction: model performance validated across states, sectors, and enterprise sizes
- Same quality of service regardless of dispute amount (₹50K treated same as ₹50L)
- Women MSE disputes tracked and given equal AI assistance
- Buyer risk scoring based on objective data (payment history, GST compliance), not on buyer identity

### Transparency
- Prediction explanation: "Your case has 82% success probability BECAUSE: written agreement exists, Gujarat MSEFC has 85% disposal rate, buyer has 2 past disputes"
- Interest calculation: full month-by-month breakdown visible to MSE
- Negotiation strategy: MSE can see AI's reasoning before each round
- Model confidence intervals: optimistic, expected, pessimistic scenarios shown

### Privacy (DPDP Act 2023 Compliance)
- Explicit consent before processing any data
- MSE data not shared with buyer (and vice versa) beyond negotiation scope
- Right to deletion: MSE can remove all data
- Data minimization: only collect what's needed for dispute resolution
- Anonymized aggregate data for analytics dashboard
- No data sold to third parties

### Safety & Legal Responsibility
- **Every page has disclaimer:** "This is AI-assisted information, not legal advice. Consult a qualified lawyer for specific legal guidance."
- Interest calculator tested against manual calculations — verified 100% accurate
- Settlement agreements include: "Both parties are advised to seek independent legal counsel before signing"
- AI never makes legal claims it can't substantiate
- All MSMED Act citations are verbatim accurate
- No automated actions without MSE's explicit confirmation

---

## 12. Deployment & Infrastructure

### Hardware Requirements

| Mode | RAM | CPU | GPU | Storage |
|------|-----|-----|-----|---------|
| Demo (no LLM) | 4GB | 2 cores | None | 10GB |
| Partial (Ollama) | 16GB | 4 cores | 8GB+ VRAM | 50GB |
| Full (Docker) | 16GB | 4 cores | 16GB VRAM | 100GB |
| Production | 32GB | 8 cores | T4/A10 | 200GB |

### Cost Analysis

| Component | Development | Cloud Demo | Production |
|-----------|------------|-----------|------------|
| Compute | ₹0 (laptop) | ₹3K/month (GPU VM) | ₹15K/month |
| Database | ₹0 (SQLite) | ₹0 (PostgreSQL Docker) | ₹2K/month |
| LLM | ₹0 (Ollama local) | ₹0 (Ollama Docker) | ₹0 (self-hosted) |
| APIs | ₹0 (Bhashini free) | ₹0 | ₹0 |
| **Total** | **₹0** | **₹3K/month** | **₹17K/month** |
| **2-year cost** | **₹0** | **₹72K** | **₹4L** |

vs Commercial ODR service: ₹5,000-20,000 per case × thousands of cases = crores.

### Three Deployment Modes

1. **FULL:** Docker Compose → Ollama + PostgreSQL + Redis + Streamlit → Best experience
2. **PARTIAL:** Just Ollama → In-memory data, AI-powered filing and prediction
3. **DEMO:** Zero dependencies → Cached responses, mock data, instant → For evaluation/demo

---

## 13. Implementation Roadmap

### Phase 1: Prototype (Now → March 2, 2026)
- Working prototype with synthetic data
- All 4 modules functional
- Demo video (3 min)
- Docker deployment
- Submit to AIKosh

### Phase 2: Pilot (If selected, ₹25L funding)
- Real ODR Portal API integration
- Real MSEFC case data (via Ministry partnership)
- Pilot with 100-200 MSEs in 2 states (Maharashtra + Gujarat)
- Fine-tune prediction model on real outcomes
- Bhashini production integration (4 languages)

### Phase 3: Scale (₹1 Cr contract, 2 years)
- Full ODR Portal integration as AI assistance layer
- 22 languages
- Deploy across all 36 MSEFCs
- Target: 50,000+ MSEs filing disputes, ₹2,000+ crore recovered
- Real-time MSEFC performance monitoring for Ministry
- Buyer payment behavior intelligence network

---

## 14. Why NyayaSetu Should Win

### 1. Solves the Exact Problem Statement
PS1 asks for "AI-enabled virtual negotiation assistance" — NyayaSetu provides exactly this: automated filing, outcome prediction, AI negotiation, and settlement drafting. Not a generic legal chatbot, but a purpose-built MSME delayed payment resolution system.

### 2. NyayaPredictor is a First
No existing solution predicts MSME dispute outcomes. Showing "82% settlement probability based on 5,000 similar cases" gives MSEs the confidence to file. This alone could increase filing rates from <1% to 10%+.

### 3. Interest Calculator is a Money Printer
Most MSEs don't know they're legally entitled to compound interest at 3× RBI rate. When NyayaSetu shows a ₹5L principal has accumulated ₹46,722 in interest over 6 months, the MSE has both incentive and legal ammunition to demand payment.

### 4. Built for the ODR Portal
The Ministry launched the ODR Portal in June 2025. NyayaSetu is designed as the AI intelligence layer for this portal — not a replacement, but an enhancement. This shows we understand the government's existing infrastructure.

### 5. Voice-First for Real India
A pickle maker in Jodhpur can file a delayed payment dispute by talking in Hindi. No forms, no legal jargon, no English. Bhashini-powered, conversation-driven.

### 6. Fully Open-Source, Zero Foreign Dependency
Qwen 2.5 (Apache 2.0) + Bhashini (Government) + Ollama (MIT) + PostgreSQL (open) = no API costs, no vendor lock-in, fully sovereign.

### 7. ₹8.1 Trillion Impact Opportunity
The numbers speak: ₹8.1 trillion stuck, <1% filing rate, 63 million MSMEs. Even moving the needle to 5% filing could unlock thousands of crores.

### 8. Politically Aligned
PM Modi at AI Impact Summit 2026: "MSMEs will be key force in Atmanirbhar and Viksit Bharat." Delayed payment resolution is the #1 pain point for MSME growth. Solving it directly supports the Digital India and Atmanirbhar Bharat vision.

---

## 15. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| ODR Portal API not available | High | Medium | Synthetic data for Stage 1; formal API request in Stage 2; manual filing guidance as fallback |
| Prediction model inaccurate on real data | Medium | High | Train on synthetic data with realistic patterns; retrain on real MSEFC data in Stage 2; show confidence intervals |
| MSEs don't trust AI legal advice | Medium | Medium | Prominent disclaimers; show reasoning for every recommendation; always suggest consulting lawyer |
| LLM generates incorrect legal citations | Medium | High | All MSMED Act sections hardcoded (not LLM-generated); LLM only generates descriptions and negotiation messages |
| Buyer refuses to engage with AI negotiation | High | Medium | AI assists the MSE, doesn't replace them; MSE sends the messages; escalation to MSEFC is always available |
| Interest calculation errors | Low | Critical | Rule-based (no ML), unit-tested, verified against manual calculations, month-by-month breakdown visible |
| Bhashini API unavailable | Medium | Low | Mock transcription in demo mode; text input always available as fallback |
| Low digital literacy of MSEs | High | Medium | Voice-first design; visual step-by-step; option to generate documents for manual filing |

---

## 16. Team & Execution Capacity

[To be filled with your actual team details]

- **Team Member 1:** [Name, Role, Skills — NLP, ML, Backend]
- **Team Member 2:** [Name, Role, Skills — Frontend, Data, Deployment]

**Relevant Experience:** Built AyurYukti (PS3 submission), VyaparSetu (PS2 blueprint). Demonstrated ability to deliver production-quality AI prototypes with government stack integration.

---

## 17. Budget Utilization (Stage 2: ₹25 Lakhs)

| Item | Amount | Purpose |
|------|--------|---------|
| Cloud GPU (16GB VRAM) | ₹3L | Model inference for 12 months |
| Real MSEFC data access | ₹2L | Data procurement and cleaning |
| Legal expert validation | ₹3L | Verify predictions, interest calculations, templates with practicing lawyers |
| Pilot deployment (2 states) | ₹5L | Infrastructure, monitoring, support |
| Team compensation | ₹8L | 2 members, 12 months part-time |
| Travel for MSEFC visits | ₹2L | 4-5 state visits for ground truth |
| Contingency | ₹2L | Buffer |
| **Total** | **₹25L** | |

---

## 18. Success Metrics (2-Year Contract)

| Metric | Year 1 Target | Year 2 Target |
|--------|--------------|--------------|
| MSEs using NyayaSetu | 10,000 | 50,000 |
| Disputes filed via platform | 5,000 | 25,000 |
| Total amount in disputes | ₹500 crore | ₹2,500 crore |
| Recovery rate | >70% | >80% |
| Avg resolution time | <75 days | <60 days |
| States covered | 10 | All 36 |
| Languages | 8 | 22 |
| UNP settlement rate | 40% | 55% |
| MSE satisfaction score | >4.0/5 | >4.5/5 |
| MSEFC case load reduction | 15% | 30% |

---

## 19. Appendix: Sample Interest Calculation

**Scenario:** ₹5,00,000 principal, overdue from August 1, 2025 to February 1, 2026 (6 months)

RBI Bank Rate: 6.00% (from April 2025)
Applicable Rate: 3 × 6.00% = 18.00% per annum
Monthly Rate: 18.00% / 12 = 1.50%

| Month | Opening Balance | Interest (1.5%) | Closing Balance |
|-------|----------------|-----------------|-----------------|
| Aug 2025 | ₹5,00,000 | ₹7,500 | ₹5,07,500 |
| Sep 2025 | ₹5,07,500 | ₹7,613 | ₹5,15,113 |
| Oct 2025 | ₹5,15,113 | ₹7,727 | ₹5,22,839 |
| Nov 2025 | ₹5,22,839 | ₹7,843 | ₹5,30,682 |
| Dec 2025 | ₹5,30,682 | ₹7,960 | ₹5,38,642 |
| Jan 2026 | ₹5,38,642 | ₹8,080 | ₹5,46,722 |

**Total Interest: ₹46,722**
**Total Claim: ₹5,46,722**

This is what NyayaSetu's interest calculator produces — verified, transparent, legally accurate.

---

## 20. Conclusion

NyayaSetu is not just another legal chatbot. It is a purpose-built, AI-powered justice delivery system for India's 63 million MSMEs, designed to work with the government's ODR infrastructure, speak the MSE's language, and fight for every rupee owed to them.

The ₹8.1 trillion delayed payment crisis won't solve itself. NyayaSetu makes filing as easy as talking, predicting as clear as a scorecard, and negotiating as smart as a seasoned lawyer — all from a phone, in Hindi, for free.

**From Udyam to Vasooli — AI that fights for India's MSMEs.**

---

*NyayaSetu — न्यायसेतु*
*"जब तक पैसा नहीं मिलता, हम लड़ते रहेंगे"*
*"Until every rupee is recovered, we keep fighting"*

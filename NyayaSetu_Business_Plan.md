# NyayaSetu Business Plan
## AI-Enabled Virtual Negotiation Assistance for MSMEs
### IndiaAI Innovation Challenge 2026 — Problem Statement 1

---

## 1. Executive Summary

NyayaSetu ("Bridge to Justice") is an AI-powered virtual negotiation and dispute resolution platform purpose-built for India's Micro and Small Enterprises (MSEs). It addresses the systemic problem of delayed payments from buyers — a crisis affecting 45+ million MSMEs with an estimated outstanding of over Rs 10.7 lakh crore annually.

The platform provides end-to-end dispute lifecycle management: from voice-enabled filing and OCR-based document extraction, through AI-powered case prediction and sentiment-aware negotiation, to automated settlement drafting and recovery analytics — all grounded in the MSMED Act 2006 (Sections 15-19).

NyayaSetu is designed to integrate as a pre-MSEFC digital settlement layer within the existing ODR portal (odr.msme.gov.in), reducing the average resolution time from 180+ days to under 30 days.

---

## 2. Problem Statement

### 2.1 The Scale of the Crisis
- 45+ million registered MSMEs in India (Udyam portal data)
- 70% of MSMEs report delayed payments as their primary challenge (MSME Ministry survey)
- Average payment delay: 90-120 days beyond the statutory 45-day limit
- Estimated Rs 10.7 lakh crore locked in delayed receivables
- Only ~25,000 cases filed at MSEFCs annually vs millions affected — a 99.9% access gap

### 2.2 Why Existing Systems Fall Short
- **MSEFC process is slow:** Average disposal time is 90-180 days per case
- **In-person requirement:** MSEs must physically appear, causing productivity loss
- **Legal complexity:** Most MSE owners lack knowledge of Section 15-19 provisions
- **Language barrier:** ODR portals are primarily English-only; MSE owners operate in 22+ languages
- **No pre-litigation settlement:** Cases go directly to formal arbitration without AI-assisted negotiation

### 2.3 The Opportunity
The MSME Ministry's ODR portal provides the digital infrastructure. What's missing is an intelligent AI layer that can:
1. Guide illiterate/semi-literate MSE owners through voice-based filing in their language
2. Automatically assess case strength and predict outcomes
3. Conduct smart negotiation on behalf of the MSE
4. Draft legally valid settlement documents
5. Track recovery patterns across the country

---

## 3. Solution Overview

### 3.1 Four Core Modules

| Module | Function | AI/ML Technology |
|--------|----------|-----------------|
| **VaadPatra** | Smart Dispute Filing Engine | PaddleOCR, Bhashini ASR, LLM extraction, document classification |
| **NyayaPredictor** | Case Outcome Prediction | CatBoost ML ensemble, SHAP explainability, case similarity (MiniLM embeddings) |
| **SamvadAI** | AI Negotiation Agent | LLM-powered tactic detection, sentiment analysis, offer optimization, settlement drafting |
| **RecoveryTracker** | Recovery Intelligence Dashboard | Geospatial analytics (Folium), MSEFC performance scoring, buyer risk scoring |

### 3.2 Key Differentiators

1. **Voice-First Architecture:** Bhashini ULCA integration supporting 8 Indian languages (Hindi, Tamil, Marathi, Bengali, Telugu, Kannada, Gujarati, English) with ASR/TTS/NMT
2. **Legally Grounded AI:** Section 16 compound interest with monthly rests (exact statutory formula), MSEFC jurisdiction routing, Section 18 reference generation
3. **Explainable Predictions:** CatBoost ML with SHAP feature contributions — judges and MSEs can understand WHY a prediction was made
4. **Strategic Negotiation:** Round-based concession curves, 8-category tactic detection with sentiment analysis, buyer-type-specific strategy optimization
5. **Open-Source LLM:** Qwen 2.5 14B via Ollama — no dependency on proprietary APIs, deployable on government cloud infrastructure

---

## 4. Technology Architecture

### 4.1 Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | Streamlit 1.33+ | Rapid prototyping, built-in widgets, Python-native |
| LLM | Qwen 2.5 14B (Ollama) | Open-source, local deployment, no data leaves India |
| ML | CatBoost + SHAP | Best gradient boosting for categorical data + interpretability |
| Embeddings | all-MiniLM-L6-v2 | Lightweight sentence similarity for case matching |
| OCR | PaddleOCR | Multilingual, angle-aware, open-source |
| Voice | Bhashini ULCA APIs | Government-backed, 22 Indian languages |
| Database | SQLite (dev) / PostgreSQL (prod) | SQLAlchemy ORM, seamless switching |
| Reports | ReportLab + OpenPyXL | Professional PDF/Excel generation |
| Deployment | Docker Compose | Containerized, reproducible, cloud-ready |

### 4.2 Data Privacy and Compliance
- **DPDP Act 2023:** All case data processed locally; no external API calls carry PII
- **LLM is on-premises:** Qwen runs via Ollama on the same server — no data sent to cloud LLM providers
- **Bhashini API:** Only audio/text sent for ASR/TTS — no case data transmitted
- **Database encryption:** PostgreSQL with TLS in production deployment
- **Access control:** Role-based access planned for Phase 2 (MSME owner vs MSEFC official)

---

## 5. Target Users

### 5.1 Primary Users
- **MSE Owners/Operators:** 45M+ registered under Udyam, predominantly Hindi/regional language speakers, often first-generation entrepreneurs with limited legal knowledge
- **MSEFC Officials:** State-level facilitation council members who manage case intake, conciliation, and arbitration proceedings

### 5.2 Secondary Users
- **Industry Associations:** FICCI, CII, FISME — for aggregate analytics and policy advocacy
- **Banks/NBFCs:** Buyer risk scores for credit decisioning
- **Legal Professionals:** Settlement drafting and case management tools

---

## 6. Deployment Strategy

### Phase 1: Pilot (Months 1-6)
- **3 states:** Rajasthan, Maharashtra, Tamil Nadu (diverse geography + language + MSEFC maturity)
- **Target:** 500 disputes filed, 200 settlements achieved
- **Deployment:** NIC Cloud / MeghRaj (government cloud infrastructure)
- **Integration:** API hooks with odr.msme.gov.in for pre-filled case submission
- **Metrics:** Resolution time, settlement rate, user satisfaction (NPS), voice adoption rate

### Phase 2: National Scale (Months 7-18)
- **All 28 states + 8 UTs**
- **Target:** 50,000 disputes/year (2% of estimated total delayed payment cases)
- **Features added:** User authentication, case history, SMS/email notifications, mobile app
- **Integration:** Direct MSEFC case management system integration, Samadhaan portal sync
- **Data:** Real MSEFC case outcomes to retrain prediction models

### Phase 3: Ecosystem (Months 19-24)
- **APIs for banks/NBFCs:** Buyer risk scores, payment behavior intelligence
- **MSME credit scoring:** Dispute history as signal for creditworthiness
- **Policy intelligence:** Aggregate analytics for MSME Ministry on national payment behavior
- **WhatsApp/IVRS integration:** Voice-based filing via phone call for non-smartphone users

---

## 7. Revenue Model (Post-Contract)

| Revenue Stream | Model | Target |
|---------------|-------|--------|
| Government SaaS License | Annual license to MSME Ministry / state MSEFCs | Rs 50L - 1Cr/year |
| Per-Case Resolution Fee | Rs 200-500 per dispute processed (subsidized by Ministry) | Rs 1-2.5Cr/year at scale |
| Analytics API | Subscription for banks/NBFCs for buyer risk data | Rs 20-50L/year |
| Training/Support | MSEFC official training and helpdesk | Rs 10-20L/year |

**Note:** During the 2-year contract period, the solution is provided at no cost to end-user MSMEs as per IndiaAI guidelines.

---

## 8. Impact Metrics

| Metric | Current Baseline | NyayaSetu Target |
|--------|-----------------|-----------------|
| Average resolution time | 180+ days | 30 days |
| Cases filed at MSEFC/year | ~25,000 | 50,000+ (with digital filing) |
| Pre-litigation settlement rate | ~15% | 60%+ (with AI negotiation) |
| Cost per dispute resolution | Rs 25,000-50,000 | Rs 500-1,000 |
| Language accessibility | English only | 8 Indian languages |
| Rural/semi-urban access | In-person only | Voice-based remote access |

---

## 9. Competitive Landscape

| Feature | NyayaSetu | Generic ODR Platforms | Legal Tech Startups |
|---------|-----------|----------------------|-------------------|
| MSMED Act domain knowledge | Deep (Sections 15-19) | None | Surface |
| Voice filing (Indian languages) | 8 languages | None | English only |
| AI negotiation with tactic detection | Yes (8 categories) | No | Basic chatbot |
| ML outcome prediction with SHAP | CatBoost ensemble | No | No |
| Section 16 compound interest | Exact statutory formula | No | Flat estimate |
| Offline LLM (no data leakage) | Qwen 2.5 local | Cloud APIs | Cloud APIs |
| MSEFC integration ready | Yes | No | No |
| Government cloud deployable | Yes (Docker) | Vendor-dependent | Vendor-dependent |

---

## 10. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Low MSME digital literacy | Voice-first design with guided conversation flow; phone/IVRS planned |
| LLM accuracy on legal matters | Rule-based fallback for all statutory calculations; "Not legal advice" disclaimer |
| Bhashini API availability | Graceful degradation to text mode; offline speech models planned |
| Data privacy concerns | On-premises LLM, no PII in API calls, DPDP Act compliance by design |
| Scalability | Docker containerized; horizontal scaling via Kubernetes on NIC Cloud |
| Model accuracy on real data | Phase 1 pilot collects real outcomes; retrain CatBoost quarterly |

---

## 11. Team Capability

The team combines expertise in:
- **AI/ML Engineering:** LLM integration, ML model development, NLP pipelines
- **Legal-Tech Domain:** MSMED Act interpretation, MSEFC procedure knowledge, dispute resolution workflows
- **Product Development:** Streamlit/Python full-stack, cloud deployment, API design
- **Multilingual NLP:** Bhashini integration, Indian language processing, voice interface design

---

## 12. Budget Utilization Plan (Rs 25 Lakhs — Stage 1)

| Item | Allocation | Purpose |
|------|-----------|---------|
| Cloud Infrastructure (GPU) | Rs 5L | RTX 3090/A100 for LLM inference during pilot |
| Bhashini API credits | Rs 2L | ASR/TTS/NMT API usage for 8 languages |
| Data Collection & Labeling | Rs 4L | Real MSEFC case outcomes, legal precedent digitization |
| Development & Testing | Rs 8L | Feature completion, security audit, load testing |
| MSEFC Integration | Rs 3L | API development for odr.msme.gov.in, state portal integration |
| Documentation & Training | Rs 2L | User manuals, MSEFC training materials, video tutorials |
| Contingency | Rs 1L | Unforeseen requirements |

---

## 13. Key Milestones

| Month | Milestone | Deliverable |
|-------|-----------|-------------|
| M1 | Pilot launch in Rajasthan | Working deployment on NIC Cloud |
| M2 | Real case data integration | Model retrained on actual MSEFC outcomes |
| M3 | Maharashtra + Tamil Nadu rollout | Multi-state deployment |
| M4 | Security audit completion | CERT-In compliance report |
| M6 | Pilot report submission | Performance matrix, user feedback, impact data |

---

## 14. Conclusion

NyayaSetu is not just a technology solution — it is a bridge between India's MSMEs and the justice system. By combining voice-first design, legally grounded AI, and explainable predictions, it transforms the dispute resolution experience from intimidating and inaccessible to intuitive and empowering.

The platform is built to integrate with existing government infrastructure (ODR portal, Bhashini, NIC Cloud), comply with Indian data protection laws (DPDP Act 2023), and scale to serve millions of MSMEs across all states and languages.

With the IndiaAI Innovation Challenge support, NyayaSetu can move from proof-of-concept to national deployment within 24 months, directly impacting the Rs 10.7 lakh crore delayed payment crisis and enabling millions of MSMEs to recover their dues with confidence.

---

*NyayaSetu — Bridge to Justice for India's MSMEs*
*IndiaAI Innovation Challenge 2026 | Problem Statement 1*

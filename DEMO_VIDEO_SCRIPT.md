# NyayaSetu — Demo Video Script
## IndiaAI Innovation Challenge 2026 | Problem Statement 1
### Target Duration: 5–7 minutes

---

## 🎬 PRE-RECORDING CHECKLIST

Before you start recording:
- [ ] App running at localhost:8501
- [ ] Ollama running with Qwen 2.5 14B loaded (`ollama list` confirms)
- [ ] Clear browser cache / open Incognito window
- [ ] Screen resolution: 1920×1080 (Full HD)
- [ ] Use OBS Studio or built-in screen recorder
- [ ] Microphone tested, quiet environment
- [ ] Close all other tabs/notifications
- [ ] Language set to **English** initially (you'll switch later)
- [ ] Theme set to **Courtroom Light**
- [ ] No active case in workspace (fresh start)
- [ ] Keep the synthetic data seeded (5,000 cases)

---

## SCENE 1 — OPENING HOOK (0:00 – 0:30)
**[Screen: Title slide or Home page hero banner]**

### What to Say:
> "India's MSMEs are owed over 10.7 lakh crore rupees in delayed payments. Despite the MSMED Act providing strong legal protection, less than 1% of affected MSMEs ever file a claim — because the process is too complex, too intimidating, and too inaccessible.
>
> NyayaSetu — the Bridge to Justice — changes that. It's an AI-powered platform that takes an MSME from zero knowledge to a legally complete filing in under 10 minutes, in their own language, using just their voice."

### What to Show:
- Home page hero banner: **"Recover MSME dues with confidence"**
- Briefly hover over the 4 module cards (VaadPatra, NyayaPredictor, SamvadAI, RecoveryTracker)
- Point out sidebar: **System Status → Data Ready, Ollama → Online**

---

## SCENE 2 — QUICK STATS & THE SCALE (0:30 – 0:50)
**[Screen: Scroll down on Home page]**

### What to Say:
> "NyayaSetu is trained on 5,000 synthetic MSME dispute cases. Our dashboard tracks over 207 crore rupees in disputed amounts, with a 66.8% recovery rate and an average resolution time of 73 days. Let me show you the full flow."

### What to Show:
- Scroll down to **Quick Stats**: 5,000 disputes, ₹207 Cr amount, 66.8% recovery, 73 days avg
- Briefly show the **Quick Liability Check** — type ₹5,00,000 and 120 days, show the instant Section 16 interest calculation
- Point out: "Even from the home page, an MSME owner can instantly check their statutory interest entitlement"

---

## SCENE 3 — VOICE FILING IN HINDI (0:50 – 2:30) ⭐ KEY DIFFERENTIATOR
**[Screen: Navigate to "File A Dispute" → Voice Filing tab]**

### What to Say:
> "The biggest barrier for MSMEs is language and literacy. NyayaSetu supports voice filing in 8 Indian languages through Bhashini integration. Let me demonstrate filing a dispute entirely by voice in Hindi."

### What to Show & Do:

**Step 1 — Start Voice Filing:**
- Click **"File A Dispute"** in sidebar
- You'll land on the **Voice Filing** tab
- Show the greeting message: *"Namaste! NyayaSetu mein aapka swagat hai..."*
- Point out: "The system greets in Hindi and asks step-by-step questions"

**Step 2 — Speak the Udyam Number:**
- Click the microphone icon on `st.audio_input`
- Speak clearly: *"Mera Udyam number hai UDYAM-MH-02-0012345"*
- Show the **Bhashini ASR transcription** appearing
- Click **"Process Voice Input"**
- Show: System extracts the Udyam number using regex, moves to Step 2
- Point out the **progress bar** advancing (Step 1 → Step 2)

> "The voice engine uses Bhashini ASR to transcribe, then intelligently extracts structured data — Udyam numbers, GSTINs, amounts — from natural speech."

**Step 3 — Speak Buyer Details:**
- Speak: *"Buyer ka naam hai Rajesh Industries, unka GSTIN hai 27AABCR1234F1Z5"*
- Process → system extracts buyer name and GSTIN
- Show the **Extracted Fields** panel updating in real-time

**Step 4 — Speak Invoice Amount:**
- Speak: *"Unhone 3 lakh 50 hazaar ka payment roka hai, invoice 6 mahine purana hai"*
- Process → amount extracted

**Step 5 — Confirm:**
- System asks for confirmation
- Speak: *"Haan, sab sahi hai"*
- Show: All extracted fields are now populated

> "In 5 simple voice steps, a semi-literate MSME owner has filed a complete dispute — no forms, no typing, no legal knowledge needed."

**Step 6 — Show TTS Playback:**
- Click the **"🔊 Listen"** button on any assistant message
- Show: Bhashini TTS reads back the response in Hindi

> "The system also speaks back to the user — full two-way voice interaction."

### ⚠️ FALLBACK NOTE:
If Bhashini APIs are slow/unavailable during recording, switch to **Manual Filing** tab and say:
> "In production, this is fully voice-driven via Bhashini. Let me show the same flow manually."

---

## SCENE 4 — MANUAL FILING + OCR + AI CLASSIFICATION (2:30 – 3:45) ⭐ KEY DIFFERENTIATOR
**[Screen: Switch to Manual Filing tab OR continue from voice-populated data]**

### What to Say:
> "Whether filed by voice or manually, NyayaSetu's smart filing engine validates every field and adds AI intelligence at each step."

### What to Show & Do:

**Step 1 — MSE Details:**
- Show Udyam number pre-filled (from voice) or type: `UDYAM-MH-02-0012345`
- Click **demo MSE selector** → pick a sample enterprise
- Show: MSE profile auto-loads (name, type, state, district, activity)

> "NyayaSetu integrates with the Udyam registration database to auto-fetch enterprise details."

**Step 2 — Buyer Details:**
- Show buyer name, type dropdown (Private Ltd), GSTIN, State
- Click **"Check Buyer Risk"**
- Show: **Risk Score 72/100 — High Risk**, with risk factors listed

> "Our AI scores buyer risk based on historical payment patterns, dispute history, and industry benchmarks."

**Step 3 — Invoice Details:**
- If you have a sample invoice image, upload it and click **"Extract Invoice Data (OCR)"**
- Show: PaddleOCR extracts invoice number, date, amount automatically
- Otherwise, manually add 2-3 invoices with different dates and amounts
- Show: **Color-coded overdue badges** (red for 180+ days, orange for 90+)
- Show: **Real-time Section 16 interest** calculated per invoice with running totals

> "PaddleOCR extracts data from scanned invoices in multiple languages. Each invoice gets a statutory interest calculation with compound monthly rests as per Section 16."

**AI Dispute Classification (CRITICAL — show this clearly):**
- Scroll to the **Dispute Sub-Category** section
- Show: System has classified this as e.g., **"Delayed Payment - Goods"** with 89% confidence
- Show: **Applicable MSMED Act sections** listed (Section 15, 16, 17)
- Show: **Reasoning** explanation

> "NyayaSetu's AI classifier categorizes disputes into 7 legal sub-categories and identifies the exact MSMED Act sections that apply. This is crucial for MSEFC filings."

**Document Checklist (CRITICAL — show this clearly):**
- Show the **Document Gap Analysis** section
- Show: Color-coded cards — green (uploaded), red (missing critical), yellow (recommended)
- Show: **Completeness score bar** (e.g., 45% → needs Udyam certificate, purchase order)
- Show: **"Missing critical: Udyam Registration Certificate"** warning

> "The system generates a smart document checklist tailored to your dispute category. It tells you exactly what's missing and how it impacts your case strength."

---

## SCENE 5 — AI CASE ASSESSMENT + EXPLAINABLE PREDICTION (3:45 – 4:30) ⭐ KEY DIFFERENTIATOR
**[Screen: Step 4 — Case Assessment]**

### What to Say:
> "Now, the AI assesses the entire case using our CatBoost machine learning ensemble."

### What to Show & Do:

- Click **"⚖️ Assess Case"**
- Show the **progress bar** advancing (Building case → Running ML → Finding similar cases → Generating analysis)
- Wait for results

**Show Results:**
1. **3 Metric Cards**: Settlement Probability (e.g., 78%), Expected Recovery (₹3,85,000), Timeline (45-90 days)
2. **Plotly Gauge Chart**: Settlement probability dial with colored zones
3. **SHAP Waterfall Chart**: "Why this prediction?"
   - Point out: "Overdue days contributed +12% to settlement likelihood, buyer type contributed -8%"

> "This is not a black box. Our SHAP explainability shows exactly which factors drive the prediction — overdue duration, buyer type, claim amount, state jurisdiction, each with a positive or negative contribution."

4. **Benchmark Comparison**: Your Case vs Average MSME vs Best Similar Case
5. **Top 3 Similar Cases**: from 5,000-case database using sentence-transformer embeddings
6. **Recommended Strategy**: "Negotiate" / "Escalate to MSEFC"

> "The system also finds the 3 most similar historical cases using AI embeddings, so MSMEs can see real precedent data before deciding their strategy."

---

## SCENE 6 — FILING DOCUMENTS + ODR LINK (4:30 – 4:50)
**[Screen: Step 5 — Review & File]**

### What to Say:
> "Once assessed, NyayaSetu generates all legal documents automatically."

### What to Show:
- Click **"Generate Filing Documents"**
- Show 3 download buttons appearing:
  1. **📄 Demand Notice PDF** — click to show inline preview
  2. **📄 MSEFC Reference Application PDF** — click to preview
  3. **📊 Interest Calculation Excel** — download
- Show the **ODR Portal Link**: pre-filled URL pointing to `odr.msme.gov.in`

> "Three professional legal documents — demand notice, MSEFC reference application, and interest calculation spreadsheet — generated in one click. Plus a deep link to the government ODR portal with pre-filled parameters."

---

## SCENE 7 — AI NEGOTIATION WITH BUYER SIMULATOR (4:50 – 5:50) ⭐ KEY DIFFERENTIATOR
**[Screen: Navigate to "Negotiate"]**

### What to Say:
> "Before escalating to MSEFC, NyayaSetu's AI negotiation engine tries to resolve the dispute amicably. Let me show our AI Buyer Simulator in action."

### What to Show & Do:

**Initialize & First Round:**
- Click **"Initialize Negotiation"**
- Show metrics: Your Claim, Minimum Acceptable, Status = Active
- Click **"Generate Round 1 Demand"**
- Show: AI-generated demand letter referencing Section 15, 16 with specific amounts

**Enable Buyer Simulator:**
- Toggle **"AI Buyer Simulation"** ON
- Select personality: **"Stalling"**
- Click **"Simulate Buyer Response"**
- Show: AI generates a realistic stalling response ("We need more time to verify...")

**Process Response:**
- Click **"Process Buyer Response"**
- Show: **Tactic Detection** — "Stalling detected (85% confidence)"
- Show: **Sentiment Gauge** — score moving toward negative
- Show: Strategy recommendation: "Set firm deadline, cite Section 16 interest accumulation"

> "NyayaSetu detects 9 different buyer negotiation tactics — stalling, threatening, disputing amounts, ghosting — and provides real-time counter-strategies grounded in legal provisions."

**Run 2-3 Rounds Quickly:**
- Generate Round 2, simulate aggressive buyer response
- Show: **Offer Convergence Chart** — MSE offers and buyer counter-offers plotted
- Show: **Sentiment Trend** — tracking across rounds
- Show: **Escalation Risk** increasing

> "The sentiment intelligence panel tracks cooperation versus aggression across rounds, predicts settlement likelihood, and recommends when to escalate."

**Settlement (if reached) OR show document generation:**
- If a deal is reached, show **Settlement Package**:
  - Installment plan selector (Lump Sum / 2 Equal / 3 Monthly / Custom)
  - Click **"Generate Settlement Agreement"**
  - Show: Professional PDF with WHEREAS clauses, payment schedule, default terms

> "When settlement is reached, NyayaSetu generates a legally binding agreement with customizable payment plans — lump sum, installments, or front-loaded structures."

---

## SCENE 8 — MULTILINGUAL DEMO (5:50 – 6:10) ⭐ KEY DIFFERENTIATOR
**[Screen: Still on Negotiate page OR switch to Home]**

### What to Say:
> "NyayaSetu supports 8 Indian languages. Let me switch to Hindi."

### What to Show:
- Change **Language dropdown** in sidebar from English to **हिन्दी**
- Show: ENTIRE UI translates — sidebar labels, page titles, buttons, status messages
- Navigate to Home → show Hindi hero text
- Navigate to File A Dispute → show Hindi form labels
- Switch to **தமிழ்** (Tamil) → show Tamil UI
- Switch back to English

> "Every label, every button, every status message translates natively. Combined with Bhashini voice support, this makes NyayaSetu truly accessible to MSMEs across all of India."

---

## SCENE 9 — RECOVERY DASHBOARD (6:10 – 6:40)
**[Screen: Navigate to "Recovery Dashboard"]**

### What to Say:
> "For policy makers and MSEFC administrators, NyayaSetu provides a comprehensive recovery intelligence dashboard."

### What to Show:
- Show **4 KPI cards** with delta arrows
- Apply a filter: Select a state (Maharashtra), specific buyer type (Private Ltd)
- Show: **Dispute Trend Chart** — filed cases and recovered amounts over time
- Show: **Recovery Rate by Buyer Type** — bar chart
- Show: **Stage Funnel** — visualizing case progression from Filing to Recovery
- Scroll to **State Heatmap** (if Folium loads) — India map with dispute density
- Show: **MSEFC Performance** — state-wise ranking
- Show: **Buyer Blacklist** — highest-risk buyers
- Click **"Export Dashboard Report (PDF)"**

> "Date range filters, state-wise heatmaps, buyer blacklists, MSEFC 90-day compliance tracking, and one-click PDF export. This dashboard turns dispute data into actionable policy intelligence."

---

## SCENE 10 — WORKSPACE & PERSISTENCE (6:40 – 6:55)
**[Screen: Navigate to "Workspace"]**

### What to Say:
> "All cases are automatically saved to the database. MSMEs can return anytime and pick up where they left off."

### What to Show:
- Show: Active case with metrics (Principal, Interest, Total Claim)
- Show: **Saved Cases** list from database
- Click **"Load"** on a different case → show it loads with full data
- Click **"Export Case JSON"** → show the download

> "Full database persistence with SQLite, case switching, and JSON export for legal advisors."

---

## SCENE 11 — ARCHITECTURE & TECH STACK (6:55 – 7:15)
**[Screen: Navigate to "About"]**

### What to Say:
> "Under the hood, NyayaSetu uses a fully open-source, India-stack-aligned architecture."

### What to Show:
- Show the **Architecture Diagram** (HTML visual)
- Show the **Technology Stack** table:
  - LLM: Qwen 2.5 14B via Ollama (local, no data leaves India)
  - ML: CatBoost ensemble with SHAP explainability
  - Voice: Bhashini ULCA APIs (ASR, TTS, NMT in 22 languages)
  - OCR: PaddleOCR (multilingual invoice extraction)
  - Embeddings: all-MiniLM-L6-v2 (case similarity)
- Show: **Legal Framework** section — MSMED Act Sections 15-19
- Show: **DPDP Act 2023 compliance** principles

> "Everything runs locally — the LLM, the ML models, the database. No sensitive MSME data ever leaves the system. We're fully aligned with the Digital Personal Data Protection Act 2023."

---

## SCENE 12 — CLOSING IMPACT STATEMENT (7:15 – 7:30)
**[Screen: Home page OR title slide]**

### What to Say:
> "NyayaSetu bridges the gap between India's strong legal framework and the MSMEs who need it most. Voice-first filing removes language barriers. AI prediction removes uncertainty. Automated negotiation removes power asymmetry. And professional document generation removes complexity.
>
> 63 million MSMEs. 10.7 lakh crore in delayed payments. One bridge to justice.
>
> NyayaSetu — न्यायसेतु."

---

## 📝 KEY TALKING POINTS CHEAT SHEET

Keep these numbers ready to drop naturally during the demo:

| Stat | Value | When to Use |
|------|-------|-------------|
| Delayed payments crisis | ₹10.7 lakh crore | Opening, closing |
| MSMEs affected | 63 million | Opening, closing |
| ODR portal usage | < 1% of affected MSMEs | Opening |
| Training dataset | 5,000 synthetic cases | Quick Stats |
| Languages supported | 8 (voice + UI) | Voice filing, multilingual |
| Dispute sub-categories | 7 legal categories | Classification |
| Buyer tactics detected | 9 types | Negotiation |
| Buyer profiles | 5 AI simulation profiles | Negotiation |
| Legal documents generated | 6 types (3 PDFs + Excel + CSV + JSON) | Filing, Settlement |
| ML models in ensemble | CatBoost + RandomForest | Prediction |
| RBI bank rate | 6.50%, 3× = 19.5% annual | Interest calculator |
| Statutory payment deadline | 45 days (Section 15) | Domain knowledge |
| SHAP features shown | Top 5 contributors | Prediction |
| Compound interest | Monthly rests, Section 16 | Interest calculator |

---

## 🎯 FEATURES TO EMPHASIZE (Judge Scoring Priorities)

These are what judges score highest on — make sure each gets screen time:

1. **🎤 Voice Input (Bhashini ASR/TTS)** — Show it working in Hindi
2. **🏷️ Dispute Sub-Category Classification** — Show the 7-category classifier with confidence
3. **📋 Document Gap Analysis** — Show the smart checklist with completeness scoring
4. **🧠 Explainable AI (SHAP)** — Show the waterfall chart, explain each feature's contribution
5. **🤖 AI Buyer Simulator** — Show the 5 personality types, tactic detection
6. **📊 Sentiment Analysis** — Show the gauge, trend chart, escalation risk
7. **🌐 Multilingual (8 languages)** — Switch languages live on screen
8. **📄 Professional Legal Documents** — Show inline PDF previews
9. **🗺️ State Heatmap & MSEFC Performance** — Show the policy-maker dashboard
10. **🔒 Privacy & Open Source** — Mention local LLM, DPDP compliance, Bhashini stack

---

## ⏱️ TIMING GUIDE

| Scene | Content | Duration | Cumulative |
|-------|---------|----------|------------|
| 1 | Opening Hook | 0:30 | 0:30 |
| 2 | Quick Stats & Scale | 0:20 | 0:50 |
| 3 | Voice Filing (Hindi) | 1:40 | 2:30 |
| 4 | Manual Filing + OCR + Classification | 1:15 | 3:45 |
| 5 | AI Prediction + SHAP | 0:45 | 4:30 |
| 6 | Filing Documents + ODR | 0:20 | 4:50 |
| 7 | AI Negotiation + Buyer Sim | 1:00 | 5:50 |
| 8 | Multilingual Demo | 0:20 | 6:10 |
| 9 | Recovery Dashboard | 0:30 | 6:40 |
| 10 | Workspace & Persistence | 0:15 | 6:55 |
| 11 | Architecture & Tech | 0:20 | 7:15 |
| 12 | Closing Statement | 0:15 | 7:30 |

**Total: ~7 minutes 30 seconds** (trim to 5-7 min by shortening Scenes 3, 4, 7)

---

## 🎙️ VOICE & PRESENTATION TIPS

1. **Speak slowly and clearly** — judges may not be native English speakers
2. **Pause after showing each feature** — let the visual sink in (1-2 seconds)
3. **Use the cursor** to point at important elements (circle the gauge, underline the SHAP chart)
4. **Don't read the UI** — explain what it MEANS ("This 78% means the MSME has strong chances")
5. **Drop domain knowledge naturally** — "As per Section 16 of the MSMED Act..." shows expertise
6. **Show confidence** — "NyayaSetu handles this automatically" not "it tries to..."
7. **If something takes time to load**, fill with context: "While the AI processes this, note that we're running Qwen 2.5 14B locally — no cloud dependency"
8. **Record in segments** — record each scene separately, edit together in post
9. **Add zoom-ins in post** on: SHAP chart, sentiment gauge, tactic detection, document checklist
10. **Background music** — soft, professional (Indian classical fusion works well), volume at 10-15%

---

## 🚨 EMERGENCY FALLBACKS

| If This Fails... | Do This |
|---|---|
| Bhashini ASR not working | Switch to Manual Filing tab, say "In production, this is voice-driven via Bhashini" |
| Ollama LLM timeout | System auto-falls back to DEMO mode, say "Showing rule-based fallback — production uses Qwen 2.5 14B" |
| OCR extraction fails | Manually enter invoice data, say "PaddleOCR processes real invoices; using manual entry for demo" |
| Folium map doesn't load | Skip heatmap, focus on charts: "State-level analysis is also available as an interactive heatmap" |
| Streamlit crashes | Have a backup recording of that scene ready |
| Audio recording is noisy | Record voiceover separately and sync in post-production |

---

## 🏆 WINNING DIFFERENTIATORS TO HIGHLIGHT

These set NyayaSetu apart from competitors — weave into your narration:

1. **"Zero to Filing in 10 minutes"** — complete dispute filed with all documents
2. **"Voice-first, not form-first"** — designed for semi-literate MSME owners
3. **"AI that explains itself"** — SHAP explainability, not a black box
4. **"The buyer doesn't need to be present"** — AI simulates buyer for training/preparation
5. **"9 tactics, 9 counter-strategies"** — real negotiation intelligence
6. **"100% local, 100% private"** — no data leaves the system
7. **"India-stack native"** — Bhashini, Udyam, GST, ODR integration
8. **"From filing to settlement to MSEFC escalation"** — complete lifecycle
9. **"Policy-maker dashboard"** — not just for MSMEs, also for governance
10. **"Three deployment modes"** — works offline (DEMO), with local AI (PARTIAL), or full stack (FULL)

---

*Script created for NyayaSetu v1.0 — IndiaAI Innovation Challenge 2026, PS-1*
*Last updated: March 2026*

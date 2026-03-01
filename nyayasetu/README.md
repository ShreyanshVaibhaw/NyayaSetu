# NyayaSetu

NyayaSetu is an AI-assisted MSME delayed-payment resolution platform aligned with MSMED Act workflows and ODR integration goals.

## Legal Disclaimer
NyayaSetu provides AI-assisted information. This is not legal advice. Consult a qualified lawyer for case-specific guidance.

## Modules
- `VaadPatra`: Smart dispute intake, eligibility checks, statutory interest calculations.
- `NyayaPredictor`: Outcome prediction, case similarity, buyer risk scoring, timeline estimates.
- `SamvadAI`: Negotiation strategy, tactic detection, communication drafting, settlement drafting.
- `VasooliTracker`: Recovery analytics, geospatial views, buyer blacklist, MSEFC performance.

## Architecture
- Frontend: Streamlit (`app.py`)
- Core logic: Python modules under `src/`
- Data: JSON + synthetic CSVs in `data/`
- LLM: Ollama client with demo fallbacks
- Database: SQLite (default) with PostgreSQL-ready URI support
- Deployment: Docker Compose (`docker-compose.yml`)

## Quick Start
1. Generate data:
   - `python scripts/generate_synthetic_data.py`
2. Seed DB:
   - `python scripts/seed_database.py`
3. Run app:
   - `streamlit run app.py`

## Setup Modes
- `FULL`: Docker + Ollama + PostgreSQL + Redis.
  - Run: `./setup.sh`
- `PARTIAL`: Local Python + Ollama only (DB/services optional).
  - Run: `./setup_local.sh PARTIAL`
- `DEMO`: Local Python with fully mocked/fallback behavior.
  - Run: `./setup_local.sh DEMO`

## Scripts
- `scripts/generate_synthetic_data.py`: Builds all synthetic CSVs.
- `scripts/seed_database.py`: Seeds SQLite DB with synthetic/reference data.
- `scripts/demo_flow.py`: End-to-end CLI demo sequence.

## Testing
- Run all tests:
  - `python -m pytest -q`
- Key suites:
  - `tests/test_vaadpatra.py`
  - `tests/test_nyayapredictor.py`
  - `tests/test_samvadai.py`
  - `tests/test_vasoolitracker.py`
  - `tests/test_integration.py`

## Report Generation
Reporting utilities are in `src/reporting/`:
- Demand Notice PDF
- MSEFC Reference PDF
- Interest Calculation Excel
- Settlement Agreement PDF
- Case Summary PDF
- Admin Analytics Report PDF

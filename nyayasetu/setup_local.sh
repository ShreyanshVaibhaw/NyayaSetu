#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-DEMO}"

python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ "$MODE" = "PARTIAL" ]; then
  echo "[NyayaSetu] PARTIAL mode: expecting local Ollama, using local files for data."
elif [ "$MODE" = "FULL" ]; then
  echo "[NyayaSetu] FULL mode requested for local setup. Start postgres/redis/ollama separately."
else
  echo "[NyayaSetu] DEMO mode: zero external dependencies."
fi

python scripts/generate_synthetic_data.py
python scripts/seed_database.py
streamlit run app.py

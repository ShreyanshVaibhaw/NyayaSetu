#!/usr/bin/env bash
set -euo pipefail

echo "[NyayaSetu] FULL mode setup (Docker + Ollama + PostgreSQL + Redis)"
docker compose up --build -d
echo "[NyayaSetu] App should be available at http://localhost:8501"

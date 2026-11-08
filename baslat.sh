#!/usr/bin/env bash
# ECO AI - Başlatma (macOS / Linux)
# Kullanım: ./baslat.sh   (durdurmak için Ctrl+C)
set -euo pipefail
cd "$(dirname "$0")"

[ -x backend/.venv/bin/python ] || { echo "[HATA] Önce ./kurulum.sh çalıştırın."; exit 1; }
[ -d frontend/node_modules ] || { echo "[HATA] Önce ./kurulum.sh çalıştırın."; exit 1; }

echo "ECO AI başlatılıyor... (durdurmak için Ctrl+C)"

# Backend arka planda; script kapanınca o da kapansın
(cd backend && .venv/bin/python -m uvicorn app.main:app --port 8000) &
BACKEND_PID=$!
trap 'echo; echo "Kapatılıyor..."; kill $BACKEND_PID 2>/dev/null || true' EXIT INT TERM

# Backend hazır olana kadar bekle (en fazla ~60 sn)
for _ in $(seq 1 120); do
  curl -s http://localhost:8000/health >/dev/null 2>&1 && break
  sleep 0.5
done
echo "✅ Backend hazır: http://localhost:8000/docs"

# Tarayıcıyı birkaç saniye sonra aç (macOS: open, Linux: xdg-open)
( sleep 3; (command -v open >/dev/null && open http://localhost:5173) || (command -v xdg-open >/dev/null && xdg-open http://localhost:5173) || true ) &

cd frontend && npm run dev

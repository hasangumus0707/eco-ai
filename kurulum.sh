#!/usr/bin/env bash
# ECO AI - Kurulum (macOS / Linux). Yalnızca BİR KEZ çalıştırılır.
# Kullanım: ./kurulum.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "============================================"
echo "  ECO AI - Kurulum (macOS / Linux)"
echo "============================================"

# 1. Python: önce 3.12, yoksa python3
if command -v python3.12 >/dev/null 2>&1; then PY=python3.12
elif command -v python3 >/dev/null 2>&1; then PY=python3
else
  echo "[HATA] Python bulunamadı. Mac için: brew install python@3.12"; exit 1
fi
if ! "$PY" -c "import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] <= (3,13) else 1)"; then
  echo "[HATA] Python 3.10-3.13 gerekli (bulunan: $($PY --version)). Mac için: brew install python@3.12"; exit 1
fi
echo "[1/4] Python: $($PY --version)"

# 2. Node.js
command -v npm >/dev/null 2>&1 || { echo "[HATA] Node.js bulunamadı: https://nodejs.org"; exit 1; }
echo "[2/4] Node.js: $(node --version)"

# 3. Backend
echo "[3/4] Backend paketleri kuruluyor (PyTorch büyük, birkaç dakika sürebilir)..."
[ -x backend/.venv/bin/python ] || "$PY" -m venv backend/.venv
backend/.venv/bin/python -m pip install --upgrade pip --quiet
backend/.venv/bin/python -m pip install -r backend/requirements.txt

# 4. Frontend
echo "[4/4] Frontend paketleri kuruluyor..."
(cd frontend && npm install)

echo "Ortam kontrol ediliyor..."
(cd backend && .venv/bin/python -m training.check_device)

echo
echo "✅ KURULUM TAMAMLANDI! Başlatmak için: ./baslat.sh"

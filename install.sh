#!/usr/bin/env bash
set -e

echo "=== INSTALLER XEL-AUTOFEED-IG ==="
echo "[1] Mode Virtual Environment (.venv) — Rapi & otomatis dipakai saat jalanin python xelgrid.py"
echo "[2] Mode Langsung di Termux / Sistem — Tanpa venv"
read -r -p "Pilih mode install [1/2, Enter = 1]: " MODE
MODE=${MODE:-1}

if [[ "${PREFIX:-}" == *"com.termux"* ]]; then
    echo "→ Mendeteksi Termux: memastikan python, python-pillow, dan libjpeg-turbo terpasang..."
    pkg install -y python python-pillow libjpeg-turbo
fi

if [[ "$MODE" == "1" ]]; then
    echo "→ Membuat virtual environment (.venv)..."
    if [[ "${PREFIX:-}" == *"com.termux"* ]]; then
        python3 -m venv --system-site-packages .venv
    else
        python3 -m venv .venv
    fi
    echo "→ Memasang library ke .venv..."
    ./.venv/bin/pip install -r requirements.txt
    echo "✓ Selesai! Jalankan cukup dengan: python xelgrid.py (otomatis memakai .venv)"
elif [[ "$MODE" == "2" ]]; then
    echo "→ Memasang library langsung ke sistem/Termux..."
    python3 -m pip install -r requirements.txt || python3 -m pip install --break-system-packages -r requirements.txt
    echo "✓ Selesai! Jalankan dengan: python xelgrid.py"
else
    echo "Pilihan tidak valid."
    exit 1
fi

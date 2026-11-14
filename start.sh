#!/usr/bin/env bash
set -e

echo "======================================================"
echo "          MINI SCREEN COMPANION - STARTUP"
echo "======================================================"
echo ""

# 1. Check Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 is not installed or not in PATH!"
    exit 1
fi

# 2. Virtualenv
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

# 3. Activate
source .venv/bin/activate

# 4. Install dependencies
echo "[*] Checking dependencies..."
pip install -q -r requirements.txt

# 5. Config
if [ ! -f "config.json" ]; then
    echo "[*] Generating default config.json..."
    cp config.example.json config.json
fi

# 6. Launch
echo ""
echo "[*] Starting Mini Screen Companion..."
python -m mini_screen_companion once
python -m mini_screen_companion run

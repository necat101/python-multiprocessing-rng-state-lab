#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "==> python-multiprocessing-rng-state-lab"
echo ""
echo "[1/3] py_compile..."
python3 -m py_compile run_lab.py test_lab.py
echo "ok"
echo ""
echo "[2/3] run_lab.py..."
python3 run_lab.py
echo ""
echo "[3/3] unittest..."
python3 -m unittest -v

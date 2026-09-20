#!/usr/bin/env bash
# Runs the whole pipeline. Expects the source PDFs in source_pdfs/.
# OCR is the slow part - roughly 5 seconds per page on one CPU core.
set -euo pipefail
cd "$(dirname "$0")/.."
bash build/1_ocr.sh
python3 build/2_rasterize.py
python3 build/3_build_site.py

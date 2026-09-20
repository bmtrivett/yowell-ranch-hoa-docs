#!/usr/bin/env bash
# Step 1 — OCR every page of every PDF in source_pdfs/ into work/ocr/<doc>/<NNN>.txt
# The source PDFs are scans with no text layer, so text must be recognized, not extracted.
set -euo pipefail
cd "$(dirname "$0")/.."
SRC=source_pdfs
OUT=work/ocr
DPI=${DPI:-200}
shopt -s nullglob
mkdir -p "$OUT"
for f in "$SRC"/*.pdf; do
  base=$(basename "$f" .pdf)
  dir="$OUT/$base"
  mkdir -p "$dir"
  n=$(pdfinfo "$f" | awk '/^Pages/{print $2}')
  for ((i=1;i<=n;i++)); do
    pg=$(printf "%03d" "$i")
    [ -s "$dir/$pg.txt" ] && continue          # resumable: skip pages already done
    pdftoppm -gray -r "$DPI" -f "$i" -l "$i" -png "$f" "/tmp/ocr_$$"
    img=$(ls /tmp/ocr_$$*.png | head -1)
    tesseract "$img" "$dir/$pg" -l eng --psm 1 >/dev/null 2>&1
    rm -f /tmp/ocr_$$*.png
  done
  echo "ocr: $base ($n pages)"
done
echo "OCR complete -> $OUT"

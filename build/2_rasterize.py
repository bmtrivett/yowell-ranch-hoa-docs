#!/usr/bin/env python3
"""Step 2 - render every PDF page to a compact black-and-white PNG.

These are the page images shown beside the OCR text on the site. They are
bilevel (1-bit) on purpose: a full-page grayscale JPEG/WebP of a text scan runs
~110 KB, while the same page as bilevel PNG is ~20 KB. That difference decides
whether all 175 pages fit inside one self-contained HTML file.
"""
import glob, os, subprocess, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source_pdfs")
OUT = os.path.join(ROOT, "work", "img")
DPI = os.environ.get("DPI", "110")
THRESHOLD = 150      # gray level below which a pixel becomes black
MAX_BYTES = 70_000   # pages heavier than this (maps, seals) get scaled down

def page_count(path):
    info = subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout
    return int(info.split("Pages:")[1].split()[0])

def main():
    os.makedirs(OUT, exist_ok=True)
    pdfs = sorted(f for f in os.listdir(SRC) if f.lower().endswith(".pdf"))
    if not pdfs:
        sys.exit(f"No PDFs found in {SRC}")
    for f in pdfs:
        base = f[:-4]
        dest = os.path.join(OUT, base)
        os.makedirs(dest, exist_ok=True)
        for i in range(1, page_count(os.path.join(SRC, f)) + 1):
            png = os.path.join(dest, f"{i:03d}.png")
            if os.path.exists(png):
                continue
            subprocess.run(["pdftoppm", "-gray", "-r", DPI, "-f", str(i), "-l", str(i),
                            "-png", os.path.join(SRC, f), "/tmp/raster"], check=True)
            tmp = glob.glob("/tmp/raster*.png")[0]
            img = Image.open(tmp).convert("L")
            bw = img.point(lambda v: 255 if v > THRESHOLD else 0, mode="1")
            bw.save(png, optimize=True)
            if os.path.getsize(png) > MAX_BYTES:
                w, h = bw.size
                bw.resize((int(w * 0.75), int(h * 0.75))).save(png, optimize=True)
            os.remove(tmp)
        print("rasterized:", base, flush=True)
    print("Page images complete ->", OUT)

if __name__ == "__main__":
    main()

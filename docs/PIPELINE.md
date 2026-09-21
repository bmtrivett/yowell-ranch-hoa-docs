# How the site is built

Three steps turn a folder of scanned PDFs into one self-contained HTML file.
Each step writes into `work/` and can be re-run on its own; all of them skip
pages they have already finished, so an interrupted run resumes where it
stopped.

```
source_pdfs/*.pdf
      |
      |  build/1_ocr.sh          page image -> Tesseract
      v
work/ocr/<document>/NNN.txt      recognized text, one file per page
      |
      |  build/2_rasterize.py    page image -> bilevel PNG
      v
work/img/<document>/NNN.png      scan shown beside the text
      |
      |  build/3_build_site.py   + build/template.html
      v
index.html                       the published site
```

## Step 1 — OCR (`build/1_ocr.sh`)

The source PDFs are scans: `pdffonts` lists no fonts and `pdftotext` returns
essentially nothing, so there is no text layer to extract. Every page is
rendered to a grayscale image at 200 DPI and passed to Tesseract.

`--psm 1` (automatic page segmentation) handles the mix of body text, centered
headings, exhibit lists, and signature blocks in these documents. 200 DPI is
the point where accuracy stops improving much on this material; higher DPI
mostly costs time.

Override the resolution with `DPI=300 bash build/1_ocr.sh` if a document comes
out poorly.

## Step 2 — Page images (`build/2_rasterize.py`)

Each page is rendered again, at 110 DPI, and thresholded to pure black and
white. This is the single most important decision in the build:

| Format for one typical page | Size |
|---|---|
| Grayscale WebP, quality 40 | ~106 KB |
| Grayscale WebP, quality 55 | ~118 KB |
| Bilevel PNG | ~24 KB |

At ~110 KB per page, 175 pages would be ~19 MB before base64 encoding, which
inflates data by about a third. Bilevel PNG brings all 175 pages to roughly
3.7 MB, which survives base64 encoding with room to spare.

The tradeoff is real: thresholding drops faint pencil marks, light gray
stamps, and the tonal detail in notary seals. Body text stays sharp. Pages
that still exceed 70 KB — maps and plat exhibits, mostly — are scaled to 75%
rather than left to dominate the file.

## Step 3 — Assembly (`build/3_build_site.py`)

Reads every OCR text file, cleans it, and injects the recognized text and
base64-encoded page images directly into `build/template.html` (the script
inserts the data into the template at build time).

Text cleanup does three things:

1. **Lifts the recording stamp.** Every page begins with a line like
   `Doc-2528 Bk-OR Vl-7727 Pg-894`. It is moved out of the body and shown as
   page metadata.
2. **Rejoins hard-wrapped lines.** Tesseract breaks a line wherever the scan
   did. Single newlines become spaces; blank lines stay as paragraph breaks.
3. **Derives titles and categories** from the filenames, which follow the
   pattern `<id>_YR-<description> <instrument number>.pdf`.

Document titles come from the `TITLES` list at the top of the script and
categories from `category()`. Both are ordinary Python — edit them there if a
document is mislabeled.

## Why one self-contained file

`index.html` has no external CSS, JavaScript, fonts, or image requests. Page
images are inlined as `data:` URIs. That means it works on GitHub Pages, from
a `file://` URL, off a USB stick, or with no network at all — and there is no
way for a broken asset path to leave part of the page missing.

The cost is a ~4.9 MB download, all of it at once. For a reference document
people search occasionally, that is a good trade; for a high-traffic site it
would not be.

## Search

Search runs entirely in the browser over the text already on the page. A query
matches a page when every term appears somewhere on it; quoted terms match as
phrases. Matching pages show only their matching paragraphs, with the rest one
click away. There is no index and no server — the corpus is small enough that
scanning it directly is instant.

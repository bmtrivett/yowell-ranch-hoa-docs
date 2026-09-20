# Yowell Ranch HOA Documents

A searchable web page of the recorded governing documents for the Yowell Ranch
subdivision in Killeen, Texas — the declaration, its amendments and
corrections, the articles and bylaws, and the association's policies and
rules.

The source documents are scanned PDFs with no text layer, so none of them can
be searched, copied from, or read by a screen reader. This project runs OCR
over all 175 pages and publishes the result as a single HTML file where every
document is searchable and each page of recognized text can be checked against
an image of the original scan.

**Live site:** https://YOUR-USERNAME.github.io/yowell-ranch-hoa-docs/

## What the page does

- **Full-text search across all 26 documents.** A page matches when every term
  appears on it. Quote a phrase for an exact match: `"board of directors"`.
  Results show only the matching paragraphs, with the full page one click away.
- **Side-by-side scans.** "Show scan" on any page opens the original scanned
  image beside the text, so an OCR error can be caught immediately. The "Show
  scans" checkbox turns this on everywhere at once.
- **Browsing by category** — declaration, amendments, corrections, articles and
  bylaws, policies and rules — with live match counts per document.
- **Recording stamps preserved.** Each page keeps its county stamp
  (`Doc-…  Bk-…  Pg-…`) so anything found here can be located in the official
  record.
- **Works anywhere.** One file, no external requests, no network needed after
  loading. Dark mode and phone layouts included.

## Accuracy

The text is machine-recognized from scans and has not been proofread. Spot
checks read cleanly, but OCR misreads individual characters, and thresholding
the page images drops faint pencil marks and light gray stamps.

**This page is a finding aid, not a legal record.** Use it to locate a
provision; rely on the recorded instrument in the Bell County Official Public
Records for anything that matters.

## Publishing to GitHub Pages

1. Create a repository and push this folder to it.
2. In the repository, open **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to *Deploy from a branch*,
   pick your default branch (`main`) and the `/ (root)` folder, and save.
4. Wait a minute, then load `https://<your-username>.github.io/<repo-name>/`.

`index.html` at the repository root is all Pages needs. The empty `.nojekyll`
file tells GitHub to serve the file as-is rather than running it through
Jekyll. Update the "Live site" link above once you know your URL.

## Repository layout

```
index.html              The site. Self-contained: text, page scans, search, styles.
.nojekyll               Serve files as-is; do not run Jekyll.
build/
  1_ocr.sh              PDF pages -> Tesseract -> text
  2_rasterize.py        PDF pages -> compact black-and-white PNGs
  3_build_site.py       Text + images + template -> index.html
  template.html         Page markup, styles, and search code
  run_all.sh            Runs all three steps in order
docs/
  PIPELINE.md           How the build works and why it is built that way
source_pdfs/            The 26 original scanned PDFs the site is built from
work/                   Intermediate OCR text and page images (not tracked)
```

## Rebuilding the site

Only needed if you change the template, add documents, or want to redo the OCR.
`index.html` is already built and committed.

**Requirements:** Python 3.9+, Tesseract OCR, and Poppler (`pdfinfo`,
`pdftoppm`).

```bash
# macOS
brew install tesseract poppler

# Debian / Ubuntu
sudo apt install tesseract-ocr poppler-utils

pip install -r requirements.txt
```

Then, from the repository root:

```bash
bash build/run_all.sh
```

Expect OCR to take around 15 minutes for 175 pages on a single core; it is by
far the slowest step. Every step is resumable — pages already processed are
skipped — so you can interrupt a run and start it again.

To rebuild just the page after editing `build/template.html`:

```bash
python3 build/3_build_site.py
```

## Source documents

The original scans are committed in `source_pdfs/` (about 13 MB), so the site
can be rebuilt from scratch without hunting them down again.

Filenames must keep their original form — `<id>_YR-<description> <instrument
number>.pdf` — because the build derives each document's title, category, and
instrument number from them.

If you would rather not carry the PDFs in the repository, delete the folder and
add `source_pdfs/` to `.gitignore`.

## Adding or replacing a document

1. Drop the PDF into `source_pdfs/`, named to match the existing pattern.
2. Run `bash build/run_all.sh`. Only the new pages are processed.
3. Check the title and category on the rebuilt page. If either is wrong, edit
   `TITLES` or `category()` in `build/3_build_site.py` and rebuild.
4. Commit the updated `index.html`.

## Note on these documents

The recorded instruments are public records of Bell County, Texas. This
repository holds the code that makes them searchable; it is not affiliated
with the Yowell Ranch HOA or its management company.

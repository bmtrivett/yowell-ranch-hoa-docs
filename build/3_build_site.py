#!/usr/bin/env python3
"""Step 3 - assemble index.html from the OCR text and the page images.

Output is one self-contained file: no external CSS, JS, fonts, or image
requests, so it works on GitHub Pages, from a file:// URL, or offline.
Page images are inlined as base64 data URIs.
"""
import base64, glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OCR = os.path.join(ROOT, "work", "ocr")
IMG = os.path.join(ROOT, "work", "img")
TEMPLATE = os.path.join(ROOT, "build", "template.html")
OUTPUT = os.path.join(ROOT, "index.html")

# Filename fragments expanded into readable titles. Order matters: the first
# match wins, so longer fragments must precede the shorter ones they contain.
TITLES = [
    ("AOI and Bylaws", "Articles of Incorporation & Bylaws"),
    ("amen to decl", "Amendment to Declaration"),
    ("Arc Guidelines", "Architectural Guidelines"),
    ("Correction 3rd amend", "Correction to 3rd Amendment"),
    ("Correction 7th amend", "Correction to 7th Amendment"),
    ("amend", "Amendment"),
    ("Declaration", "Declaration of Covenants, Conditions & Restrictions"),
]
CATEGORY_ORDER = ["Declaration", "Amendments", "Corrections",
                  "Articles & Bylaws", "Policies & Rules"]

def category(name):
    if name.startswith("Declaration"):
        return "Declaration"
    if name.startswith("Correction"):
        return "Corrections"
    if "amend" in name or "amen to" in name:
        return "Amendments"
    if name.startswith("AOI"):
        return "Articles & Bylaws"
    return "Policies & Rules"

def title_for(raw):
    for fragment, full in TITLES:
        if fragment.lower() in raw.lower():
            return re.sub(re.escape(fragment), full, raw, flags=re.I)
    return raw

def read_pages(folder):
    pages = []
    for path in sorted(glob.glob(os.path.join(folder, "*.txt"))):
        text = open(path, encoding="utf-8", errors="replace").read().replace("\f", "")
        text = re.sub(r"[ \t]+\n", "\n", text).strip()
        # The county recording stamp is always the first line; lift it out so it
        # can be shown as metadata instead of as body text.
        lines = text.split("\n")
        stamp = ""
        if lines and re.match(r"^\s*Doc[-\s]", lines[0]):
            stamp = lines[0].strip()
            text = "\n".join(lines[1:]).strip()
        # Tesseract hard-wraps every line. Join single newlines back into
        # paragraphs; blank lines stay as paragraph breaks.
        text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
        pages.append({"n": int(os.path.basename(path)[:3]), "stamp": stamp, "text": text})
    return pages

def main():
    docs = []
    for name in sorted(os.listdir(OCR)):
        folder = os.path.join(OCR, name)
        if not os.path.isdir(folder):
            continue
        m = re.match(r"\d+_YR-(.*?)\s+([\d.\-]+)$", name)
        if not m:
            print("skipped (unexpected filename):", name)
            continue
        raw, instrument = m.group(1), m.group(2)
        docs.append({
            "dir": name,
            "id": re.sub(r"\W", "", name[:8]),
            "title": title_for(raw),
            "sub": "Instrument " + instrument,
            "cat": category(raw),
            "pages": read_pages(folder),
        })
    docs.sort(key=lambda d: CATEGORY_ORDER.index(d["cat"]))

    scans = {}
    for d in docs:
        for p in d["pages"]:
            png = os.path.join(IMG, d["dir"], "%03d.png" % p["n"])
            if os.path.exists(png):
                scans[d["id"] + "-" + str(p["n"])] = base64.b64encode(open(png, "rb").read()).decode()
    for d in docs:
        d.pop("dir")

    html = open(TEMPLATE, encoding="utf-8").read()
    # "</" inside a <script> block would close the tag early; escape it.
    html = html.replace("__DATA__", json.dumps(docs, ensure_ascii=False).replace("</", "<\\/"))
    html = html.replace("__SCANS__", json.dumps(scans))
    open(OUTPUT, "w", encoding="utf-8").write(html)
    print("%d documents, %d pages, %d scans -> %s (%d KB)"
          % (len(docs), sum(len(d["pages"]) for d in docs), len(scans),
             OUTPUT, len(html) // 1024))

if __name__ == "__main__":
    main()

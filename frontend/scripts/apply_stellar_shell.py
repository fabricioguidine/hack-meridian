#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrap every HTML in data/html/ with a Stellar <head> + <body class="stellar-dark"> shell
and write to pages/ (keeps original content inside <main>).
- Input:  data/html/*.html
- Output: pages/<same-name>.html
Safe: original files remain intact.
"""

import os, glob, io
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
IN_DIR = ROOT / "data" / "html"
OUT_DIR = ROOT / "pages"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONTS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Play:wght@700&display=swap" rel="stylesheet">
"""

DS = """
<link rel="stylesheet" href="../stellar_ds/css/stellar.css">
<link rel="stylesheet" href="../stellar_ds/css/overrides.css">
"""

INLINE_CSS = """
<style>
  body{max-width:1100px;margin:2rem auto;padding:0 1rem}
  .page-note{margin-bottom:16px}
  .page-note .st-muted{font-size:.95rem}
</style>
"""

def build_shell(title="POAP → Stellar Page", inner_html=""):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{title}</title>
  {FONTS}
  {DS}
  {INLINE_CSS}
</head>
<body class="stellar-dark">
  <h1 class="st-h1">{title}</h1>
  <p class="page-note st-muted">Wrapped automatically with Stellar design system.</p>
  <main>{inner_html}</main>
</body></html>"""

def extract_title(soup: BeautifulSoup) -> str:
    if soup.title and soup.title.string:
        t = soup.title.string.strip()
        if t: return t
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True): return h1.get_text(strip=True)
    return "POAP → Stellar Page"

def main():
    files = sorted(glob.glob(str(IN_DIR / "*.html")))
    if not files:
        print(f"[warn] no files in {IN_DIR}")
        return
    for src in files:
        raw = Path(src).read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(raw, "html.parser")

        # If it already has <html>, extract body contents; else take all content.
        if soup.body:
            inner = "".join(str(x) for x in soup.body.contents)
        else:
            # fall back to the whole parsed soup (without doctype/head duplication)
            tmp = BeautifulSoup("", "html.parser")
            # move everything top-level into a tmp container
            for el in list(soup.contents):
                tmp.append(el.extract())
            inner = str(tmp)

        title = extract_title(soup)
        html = build_shell(title=title, inner_html=inner)
        dst = OUT_DIR / Path(src).name
        dst.write_text(html, encoding="utf-8")
        print("[ok]", dst.relative_to(ROOT))
    # index
    idx = io.StringIO()
    idx.write("""<!doctype html><meta charset="utf-8"><title>Wrapped Pages</title>
<link rel="stylesheet" href="../stellar_ds/css/stellar.css">
<link rel="stylesheet" href="../stellar_ds/css/overrides.css">
<body class="stellar-dark" style="max-width:1100px;margin:2rem auto;padding:0 1rem">
<h1 class="st-h1">Wrapped Pages</h1><ul>
""")
    for dst in sorted(OUT_DIR.glob("*.html")):
        idx.write(f'<li><a href="{dst.name}">{dst.name}</a></li>\n')
    idx.write("</ul></body>")
    (OUT_DIR / "index.html").write_text(idx.getvalue(), encoding="utf-8")
    print("[done] open pages/index.html")
if __name__ == "__main__":
    main()
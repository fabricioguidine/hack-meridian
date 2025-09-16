#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a clean MVP gallery from messy POAP HTML:
- Reads:  data/html/*.html
- Extracts: title, subtitle/description, first image, primary CTA text
- Writes: mvp/index.html (grid of Stellar DS cards)
"""
import os, glob, re, html
from bs4 import BeautifulSoup

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IN_DIR = os.path.join(ROOT, "data", "html")
OUT_DIR = os.path.join(ROOT, "mvp")
CSS_REL = "../stellar_ds/css/stellar.css"  # relative from mvp/index.html

os.makedirs(OUT_DIR, exist_ok=True)

def pick_title(soup):
    # priority: h1, h2 (with text), fallback: <title>
    for sel in ["h1", "h2"]:
        el = soup.find(sel)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return "Untitled POAP"

def pick_subtitle(soup):
    # try a descriptive <p> near the first heading
    h = soup.find(["h1", "h2"])
    if h:
        # look forward siblings then parents
        sib_p = h.find_next("p")
        if sib_p and sib_p.get_text(strip=True):
            return sib_p.get_text(strip=True)[:160]
    # fallback: first reasonable <p>
    p = soup.find("p")
    if p and p.get_text(strip=True):
        return p.get_text(strip=True)[:160]
    return ""

def pick_image(soup):
    # prefer images that look like badges (class hints or square-ish)
    candidates = soup.find_all("img", src=True)
    best = None
    for img in candidates:
        cls = " ".join(img.get("class", [])).lower()
        alt = (img.get("alt") or "").lower()
        src = img["src"]
        if any(k in cls for k in ["poap", "badge", "event", "avatar"]) or "poap" in alt:
            best = src
            break
    if not best and candidates:
        best = candidates[0]["src"]
    # normalize: if data URLs or relative, just return as-is; browser will try to load
    return best or "https://via.placeholder.com/640x360.png?text=Badge"

def pick_cta_text(soup):
    for sel in ["button", "a", ".btn", ".button"]:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            txt = el.get_text(strip=True)
            # favor "Claim", "Mint", "View", "Start"
            for preferred in ["Claim", "Mint", "View", "Start", "Details"]:
                if preferred.lower() in txt.lower():
                    return preferred
            return txt[:16]
    return "View"

def extract_card_info(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    return {
        "title": pick_title(soup),
        "subtitle": pick_subtitle(soup),
        "image": pick_image(soup),
        "cta": pick_cta_text(soup),
    }

def build_index_html(cards):
    # minimal grid page using Stellar DS
    head = f"""<!doctype html>
<html><head><meta charset="utf-8"/>
<title>POAP → Stellar MVP</title>
<link rel="stylesheet" href="{CSS_REL}"/>
<style>
  body{{max-width:1100px;margin:2rem auto;padding:0 1rem}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}}
  .st-badge-card .st-title{{min-height:2.4em;line-height:1.2}}
  .st-badge-card img{{aspect-ratio:16/9;object-fit:cover}}
</style>
</head>
<body class="stellar-dark">
<h1 class="st-h1">POAP → Stellar MVP</h1>
<p class="st-muted">Minimal reskinned gallery compiled from scraped POAP HTML.</p>
<div class="grid">
"""
    parts = [head]
    for c in cards:
        title = html.escape(c["title"])
        subtitle = html.escape(c["subtitle"])
        image = c["image"]  # allow external/relative; no escape needed in src attr if quoted
        cta = html.escape(c["cta"])
        parts.append(f"""
  <div class="st-badge-card">
    <img src="{image}" alt="{title}">
    <div class="st-title">{title}</div>
    <div class="st-subtitle">{subtitle}</div>
    <div class="st-progress"><span style="--value:60%"></span></div>
    <button class="st-btn st-btn-primary" style="margin-top:12px">{cta}</button>
  </div>""")
    parts.append("""
</div>
</body></html>""")
    return "".join(parts)

def main():
    files = sorted(glob.glob(os.path.join(IN_DIR, "*.html")))
    if not files:
        print(f"[warn] No HTML files found in {IN_DIR}")
        return
    cards = []
    for path in files:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                html_text = f.read()
            card = extract_card_info(html_text)
            cards.append(card)
        except Exception as e:
            print(f"[skip] {os.path.basename(path)}: {e}")
    # keep only a reasonable number for MVP page (e.g. 60)
    cards = cards[:60]
    out_html = build_index_html(cards)
    out_path = os.path.join(OUT_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out_html)
    print(f"[ok] wrote {os.path.relpath(out_path, ROOT)} with {len(cards)} cards.")

if __name__ == "__main__":
    main()
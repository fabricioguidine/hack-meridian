#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reskin POAP HTML -> Stellar DS
- Reads:  data/html/*.html
- Writes: data/reskinned/*.html
- Injects: <link rel="stylesheet" href="../../stellar_ds/css/stellar.css">
- Adds: <body class="stellar-dark"> (preserves existing classes)
- Maps common POAP-ish elements to Stellar DS classes:
    Event cards     -> .st-badge-card
    Claim buttons   -> .st-btn .st-btn-primary
    Titles/Subtitles-> .st-title / .st-subtitle
    Progress bars   -> .st-progress > span[style="--value:NN%"]
- Idempotent: safe to run multiple times
- Dry-run: set DRY_RUN=1 to just print what would change
"""
import os, glob, re, shutil
from bs4 import BeautifulSoup

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IN_DIR = os.path.join(ROOT, "data", "html")
OUT_DIR = os.path.join(ROOT, "data", "reskinned")
CSS_REL = "../../stellar_ds/css/stellar.css"  # relative from OUT_DIR files

DRY_RUN = os.getenv("DRY_RUN", "0") == "1"
VERBOSE = os.getenv("VERBOSE", "1") == "1"

# --------- Heuristic selectors to map (adjust as you learn POAP structure) ----------
SELECTORS = {
    # Cards that likely wrap a badge/event
    "card": [
        ".EventCard", ".event-card", ".card", ".poap-card", "article.card", "div.card"
    ],
    # Titles inside cards
    "title": [
        ".EventCard h1", ".EventCard h2", ".event-card h2", ".card h2", ".poap-card h2",
        "h1.event-title", "h2.event-title"
    ],
    # Subtitles/descriptions inside cards
    "subtitle": [
        ".EventCard p", ".event-card p", ".card p", ".poap-card p", "p.subtitle", "p.description"
    ],
    # Claim buttons or primary CTAs
    "cta": [
        "button.ClaimButton", ".claim-button", "a.claim", "button.primary", ".btn-primary", "a.btn-primary"
    ],
    # Progress wrappers (if any)
    "progress": [
        ".ProgressBar", ".progress", "div[role='progressbar']"
    ],
    # Badge images
    "image": [
        "img.PoapImage", "img.badge", "img[event-image]", "img"
    ]
}

def log(msg):
    if VERBOSE:
        print(msg)

def ensure_head_and_body(soup):
    """Guarantee <head> and <body> exist."""
    if not soup.head:
        soup.html.insert(0, soup.new_tag("head"))
    if not soup.body:
        body = soup.new_tag("body")
        # move all top-level elems (except head) into body
        for el in list(soup.html.contents):
            if el.name != "head":
                body.append(el.extract())
        soup.html.append(body)

def inject_css_and_theme(soup):
    """Add stellar.css link (if missing) and ensure body has `stellar-dark`."""
    ensure_head_and_body(soup)
    css_href = CSS_REL
    exists = any((getattr(l, "get", lambda *_: None)("href") == css_href) for l in soup.head.find_all("link"))
    if not exists:
        link = soup.new_tag("link", rel="stylesheet", href=css_href)
        soup.head.append(link)

    # Add class to body
    existing = soup.body.get("class", [])
    if "stellar-dark" not in existing:
        soup.body["class"] = list(set(existing + ["stellar-dark"]))

def set_classes(el, *classes):
    el["class"] = list(dict.fromkeys([c for c in classes if c]))  # dedup, preserve order

def map_card(card):
    """Turn a generic 'card' into a Stellar badge card."""
    # Make the wrapper a DS card
    set_classes(card, "st-badge-card")

    # Find image -> ensure rounded + border via CSS (already in DS). Just ensure it stays inside the card.
    img = None
    for sel in SELECTORS["image"]:
        found = card.select_one(sel)
        if found:
            img = found
            break

    # Titles -> .st-title (prefer h2 over h1 for inside cards)
    title = None
    for sel in SELECTORS["title"]:
        t = card.select_one(sel)
        if t and t.get_text(strip=True):
            title = t
            break
    if title:
        set_classes(title, "st-title")
        # enforce uppercase in content? We leave CSS to uppercase it.

    # Subtitles -> .st-subtitle
    subtitle = None
    for sel in SELECTORS["subtitle"]:
        s = card.select_one(sel)
        if s and s.get_text(strip=True):
            subtitle = s
            break
    if subtitle:
        set_classes(subtitle, "st-subtitle")

    # CTA button -> .st-btn .st-btn-primary
    for sel in SELECTORS["cta"]:
        for cta in card.select(sel):
            set_classes(cta, "st-btn", "st-btn-primary")

    # Progress -> normalize to DS
    for sel in SELECTORS["progress"]:
        prog = card.select_one(sel)
        if not prog:
            continue
        # remove inner complexity; create DS bar
        value = None
        # try to read aria-valuenow or inline % text
        aria = prog.get("aria-valuenow")
        if aria and str(aria).isdigit():
            value = f"{int(float(aria))}%"
        else:
            text = prog.get_text(" ", strip=True)
            m = re.search(r"(\d{1,3})\s*%", text or "")
            if m:
                pct = max(0, min(100, int(m.group(1))))
                value = f"{pct}%"
        # rebuild DS bar
        new_prog = soup.new_tag("div", **{"class": "st-progress"})
        span = soup.new_tag("span")
        if value:
            span["style"] = f"--value:{value}"
        new_prog.append(span)
        prog.replace_with(new_prog)

def reskin_html(html: str) -> str:
    """Apply DS to one HTML string. Returns modified HTML."""
    global soup
    soup = BeautifulSoup(html, "html.parser")

    # Ensure HTML structure + CSS
    if not soup.html:
        # wrap if needed
        wrapper = BeautifulSoup("<html><head></head><body></body></html>", "html.parser")
        # put all content into body
        if soup:
            wrapper.body.append(soup)
        soup = wrapper

    inject_css_and_theme(soup)

    # Map cards
    seen_cards = 0
    for sel in SELECTORS["card"]:
        for card in soup.select(sel):
            map_card(card)
            seen_cards += 1

    # Also, generic CTAs outside cards
    for sel in SELECTORS["cta"]:
        for btn in soup.select(sel):
            set_classes(btn, "st-btn", "st-btn-primary")

    # Headings outside cards -> DS headings
    for h in soup.find_all(["h1", "h2"]):
        cls = h.get("class", [])
        # if not already st-title from a card:
        if "st-title" not in cls:
            if h.name == "h1":
                set_classes(h, "st-h1")
            elif h.name == "h2":
                set_classes(h, "st-h2")

    return str(soup)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    in_files = sorted(glob.glob(os.path.join(IN_DIR, "*.html")))
    if not in_files:
        print(f"[warn] No HTML files in {IN_DIR}")
        return

    print(f"[info] Reskinning {len(in_files)} files...")
    for src in in_files:
        with open(src, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()

        out_html = reskin_html(html)
        dst = os.path.join(OUT_DIR, os.path.basename(src))

        if DRY_RUN:
            print(f"[dry-run] Would write: {dst}")
        else:
            with open(dst, "w", encoding="utf-8") as f:
                f.write(out_html)
            log(f"[ok] {os.path.relpath(dst, ROOT)}")

    # Copy a simple index to browse outputs (optional)
    index_path = os.path.join(OUT_DIR, "index.html")
    if not DRY_RUN:
        with open(index_path, "w", encoding="utf-8") as idx:
            idx.write("""<!doctype html><meta charset="utf-8"><title>Reskinned POAP Samples</title>
<link rel="stylesheet" href="../stellar_ds/css/stellar.css">
<body class="stellar-dark" style="max-width:1000px;margin:2rem auto;padding:0 1rem">
<h1 class="st-h1">Reskinned POAP Samples</h1>
<p class="st-muted">Open any of the files in this folder to preview the reskin.</p>
<ul>
""" )
            for src in in_files:
                name = os.path.basename(src)
                idx.write(f'<li><a href="{name}">{name}</a></li>\n')
            idx.write("</ul></body>")

    print("[done] Check data/reskinned/ (open data/reskinned/index.html)")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera um site estático com menu + mega-menus no Stellar DS.

Saída:
  site/
    index.html
    about.html, issuers.html, collectors.html, builders.html
    <slug>.html (uma página por item do menu)
    assets/nav.css

Depende de:
  stellar_ds/css/stellar.css (já existente)
  (opcional) stellar_ds/css/overrides.css

Lê (opcional):
  data/html/*.html  -> tenta extrair <title> e 1º <p> como descrição
"""

import os, re, glob, html, unicodedata
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
IN_DIR = ROOT / "data" / "html"
OUT_DIR = ROOT / "site"
ASSETS = OUT_DIR / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

STELLAR_CSS = "../stellar_ds/css/stellar.css"
OVERRIDES_CSS = "../stellar_ds/css/overrides.css"  # se não existir, tudo bem

# ---- helpers ---------------------------------------------------------------

def slugify(text: str) -> str:
    txt = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    txt = re.sub(r"[^a-zA-Z0-9\s-]", "", txt).strip().lower()
    txt = re.sub(r"[\s_-]+", "-", txt)
    return txt or "page"

def extract_first_title_desc():
    """Vasculha data/html/* e cria um map heurístico {title: desc}"""
    res = {}
    for path in sorted(glob.glob(str(IN_DIR / "*.html"))):
        try:
            html_txt = Path(path).read_text("utf-8", errors="ignore")
            soup = BeautifulSoup(html_txt, "html.parser")
            title = None
            for tag in ("h1", "h2"):
                el = soup.find(tag)
                if el and el.get_text(strip=True):
                    title = el.get_text(strip=True)
                    break
            if not title and soup.title and soup.title.string:
                title = soup.title.string.strip()
            if not title:
                continue
            p = soup.find("p")
            desc = (p.get_text(" ", strip=True) if p else "")[:180]
            res[title] = desc
        except Exception:
            pass
    return res

# ---- conteúdo do menu (baseado nas capturas que você enviou) ---------------

MENU = {
    "About": [
        {
            "title": "About the Proof of Attendance Protocol",
            "desc": "Find out more about what a POAP is."
        },
        {
            "title": "About POAP Inc",
            "desc": "We are pioneers for the future of POAP."
        },
        {
            "title": "Case Studies",
            "desc": "Explore examples of POAP success stories."
        },
    ],
    "Issuers": [
        { "title": "How to use POAP", "desc": "Find out more about how you can use POAPs." },
        { "title": "Enterprise solutions", "desc": "Are you an organization? We have a solution for you." },
        { "title": "Packages", "desc": "Dive into our packages and pricing." },
        { "title": "POAP Fun", "desc": "Create raffles and offer prizes with POAPs." },
    ],
    "Collectors": [
        { "title": "Collectors", "desc": "See POAPs owned by you and other collectors." },
        { "title": "Gallery", "desc": "Explore the POAP collectible universe." },
        { "title": "Collections", "desc": "Create and view curated collections of POAPs." },
        { "title": "POAP Fun", "desc": "Create raffles and win prizes with POAPs." },
    ],
    "Builders": [
        { "title": "Docs", "desc": "Developer documentation and APIs." },
        { "title": "SDKs", "desc": "Build on top of POAP ecosystem." },
        { "title": "Community", "desc": "Join builders and collaborate." },
        { "title": "Status", "desc": "Platform availability and incidents." },
    ]
}

# tenta enriquecer descrições com dados reais extraídos
EXTRACTED = extract_first_title_desc()
for sec_items in MENU.values():
    for item in sec_items:
        t = item["title"]
        if t in EXTRACTED and len(EXTRACTED[t]) >= 40:
            item["desc"] = EXTRACTED[t]

# ---- HTML templates ---------------------------------------------------------

PAGE_HEAD = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{{title}}</title>

  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Play:wght@700&display=swap" rel="stylesheet">

  <!-- Stellar DS -->
  <link rel="stylesheet" href="{STELLAR_CSS}"/>
  <link rel="stylesheet" href="{OVERRIDES_CSS}" onerror="this.remove()"/>

  <!-- Menu CSS -->
  <link rel="stylesheet" href="assets/nav.css"/>
</head>
"""

NAV = """<header class="st-nav">
  <div class="st-nav__bar">
    <a class="st-logo" href="index.html">Stellar&nbsp;POAP</a>
    <nav class="st-menu">
      <div class="st-menu__item">
        <a href="about.html">About</a>
        <div class="st-mega">{about}</div>
      </div>
      <div class="st-menu__item">
        <a href="issuers.html">Issuers</a>
        <div class="st-mega">{issuers}</div>
      </div>
      <div class="st-menu__item">
        <a href="collectors.html">Collectors</a>
        <div class="st-mega">{collectors}</div>
      </div>
      <div class="st-menu__item">
        <a href="builders.html">Builders</a>
        <div class="st-mega">{builders}</div>
      </div>
    </nav>
  </div>
</header>
"""

def mega_for(section: str):
    cards = []
    for it in MENU[section]:
        slug = slugify(it["title"])
        href = f"{slug}.html"
        title = html.escape(it["title"])
        desc = html.escape(it["desc"])
        cards.append(f"""
        <a class="st-mega__card" href="{href}">
          <div class="st-mega__icon"></div>
          <div>
            <div class="st-mega__title">{title}</div>
            <div class="st-mega__desc">{desc}</div>
          </div>
        </a>""")
    return "\n".join(cards)

PAGE_WRAPPER_START = PAGE_HEAD + """
<body class="stellar-dark">
  {nav}
  <main class="container">
"""

PAGE_WRAPPER_END = """
  </main>
</body>
</html>
"""

def write_file(path: Path, content: str):
    path.write_text(content, encoding="utf-8")
    print("[ok]", path.relative_to(ROOT))

# ---- gera páginas -----------------------------------------------------------

def build_nav_css():
    css = r"""
/* nav.css — navegação/mega-menu no Stellar DS */
.container{max-width:1100px;margin:2rem auto;padding:0 1rem}

/* top bar */
.st-nav{position:sticky;top:0;z-index:50;background:linear-gradient(180deg, rgba(1,3,35,.98), rgba(1,3,35,.86));backdrop-filter: blur(6px);border-bottom:1px solid var(--ds-border)}
.st-nav__bar{max-width:1100px;margin:0 auto;display:flex;gap:24px;align-items:center;justify-content:space-between;padding:14px 16px}
.st-logo{font-family:var(--ds-font-heading);font-weight:800;letter-spacing:.04em;text-transform:uppercase;text-decoration:none;color:var(--ds-text)}

/* menu */
.st-menu{display:flex;gap:18px}
.st-menu__item{position:relative}
.st-menu__item > a{color:var(--ds-text);text-decoration:none;font-weight:800;letter-spacing:.04em;text-transform:uppercase;padding:10px 8px;display:inline-flex;align-items:center;border-bottom:3px solid transparent}
.st-menu__item:hover > a{color:var(--ds-primary);border-bottom-color:var(--ds-primary)}

/* mega */
.st-mega{display:none;position:absolute;left:0;top:100%;margin-top:10px;background:var(--ds-card);border:1px solid var(--ds-border);border-radius:18px;box-shadow:var(--ds-shadow-card);padding:14px;min-width:520px}
.st-menu__item:hover .st-mega{display:grid;grid-template-columns:1fr;gap:10px}

/* cada item (ícone + textos) */
.st-mega__card{display:grid;grid-template-columns:48px 1fr;gap:12px;align-items:center;text-decoration:none;background:linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.02));border:1px solid var(--ds-border);border-radius:14px;padding:10px;color:var(--ds-text)}
.st-mega__card:hover{border-color:var(--ds-primary);box-shadow:var(--ds-glow-primary)}
.st-mega__icon{width:48px;height:48px;border-radius:12px;background:rgba(127,127,255,.08);border:1px solid var(--ds-border)}
.st-mega__title{font-weight:800;letter-spacing:.02em}
.st-mega__desc{color:var(--ds-text-muted);font-size:.95rem}

/* grade da seção */
.section-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;margin-top:16px}
.section-card{background:var(--ds-card);border:1px solid var(--ds-border);border-radius:18px;padding:16px;box-shadow:var(--ds-shadow-card)}
.section-card:hover{border-color:var(--ds-primary);box-shadow:var(--ds-glow-primary), var(--ds-shadow-card)}
.section-card .title{font-weight:800;letter-spacing:.02em}
.section-card .desc{color:var(--ds-text-muted)}
"""
    write_file(ASSETS / "nav.css", css)

def render_nav():
    return NAV.format(
        about=mega_for("About"),
        issuers=mega_for("Issuers"),
        collectors=mega_for("Collectors"),
        builders=mega_for("Builders"),
    )

def page(title: str, inner_html: str):
    return (PAGE_WRAPPER_START.format(title=html.escape(title), nav=render_nav())
            + inner_html + PAGE_WRAPPER_END)

def build_home():
    blocks = []
    for section, items in MENU.items():
        cards = []
        for it in items:
            title = html.escape(it["title"])
            desc = html.escape(it["desc"])
            href = f"{slugify(it['title'])}.html"
            cards.append(f"""<a class="section-card" href="{href}">
              <div class="title">{title}</div>
              <div class="desc">{desc}</div>
              <button class="st-btn st-btn-primary" style="margin-top:12px">Open</button>
            </a>""")
        blocks.append(f"<h2 class='st-h2'>{section}</h2><div class='section-grid'>{''.join(cards)}</div>")
    write_file(OUT_DIR / "index.html", page("Home — Stellar POAP", "".join(blocks)))

def build_section(section: str):
    items = MENU[section]
    cards = []
    for it in items:
        href = f"{slugify(it['title'])}.html"
        cards.append(f"""<a class="section-card" href="{href}">
          <div class="title">{html.escape(it['title'])}</div>
          <div class="desc">{html.escape(it['desc'])}</div>
          <button class="st-btn st-btn-primary" style="margin-top:12px">Open</button>
        </a>""")
    html_out = f"<h1 class='st-h1'>{html.escape(section)}</h1><div class='section-grid'>{''.join(cards)}</div>"
    write_file(OUT_DIR / f"{section.lower()}.html", page(f"{section} — Stellar POAP", html_out))

def build_item_pages():
    for section, items in MENU.items():
        for it in items:
            slug = slugify(it["title"])
            title = it["title"]
            desc = it["desc"]
            content = f"""
            <h1 class="st-h1">{html.escape(title)}</h1>
            <p class="st-muted" style="max-width:70ch">{html.escape(desc)}</p>
            <div class="st-badge-card" style="margin-top:16px;max-width:720px">
              <img src="https://via.placeholder.com/1280x720.png?text={html.escape(title)}" alt="{html.escape(title)}"/>
              <div class="st-title">{html.escape(title)}</div>
              <div class="st-subtitle">{html.escape(desc)}</div>
              <div class="st-progress"><span style="--value:65%"></span></div>
              <button class="st-btn st-btn-primary" style="margin-top:12px">Get Started</button>
            </div>
            """
            write_file(OUT_DIR / f"{slug}.html", page(f"{title} — Stellar POAP", content))

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    build_nav_css()
    build_home()
    for sec in MENU.keys():
        build_section(sec)
    build_item_pages()
    print("[done] open site/index.html")

if __name__ == "__main__":
    main()
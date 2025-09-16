# pip install playwright==1.* && playwright install
import json, re, os
from collections import Counter
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

SEED_URLS = [
  "https://quest.stellar.org/",
  "https://quest.stellar.org/learn",
  "https://quest.stellar.org/side-quests",
  # adicione 2–4 quests reais (copie URLs que você abrir no navegador)
]

OUT_DIR = "stellar_ds_autogen"
os.makedirs(OUT_DIR, exist_ok=True)

def collect_styles(page):
    # retorna amostra de estilos computados de vários elementos
    js = """
    () => {
      const pick = (el) => {
        const cs = getComputedStyle(el);
        return {
          tag: el.tagName.toLowerCase(),
          txt: (el.innerText||"").trim().slice(0,60),
          color: cs.color,
          bg: cs.backgroundColor,
          font: cs.fontFamily,
          weight: cs.fontWeight,
          size: cs.fontSize,
          radius: cs.borderRadius,
          shadow: cs.boxShadow
        };
      };
      const els = Array.from(document.querySelectorAll("h1,h2,h3,button,a,div,section,article,nav,span"));
      const sample = [];
      for (let i=0; i<els.length && sample.length<400; i++) {
        sample.push(pick(els[i]));
      }
      return sample;
    }
    """
    return page.evaluate(js)

def normalize_color(c: str | None) -> str | None:
    if not c:
        return None
    c = c.strip().lower()
    if c == "transparent":
        return None

    # rgb/rgba( R, G, B [ , A ] )
    m = re.search(r'rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})', c)
    if m:
        r, g, b = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        r = max(0, min(r, 255))
        g = max(0, min(g, 255))
        b = max(0, min(b, 255))
        return f"#{r:02x}{g:02x}{b:02x}"

    # #rgb ou #rrggbb
    m = re.search(r'#([0-9a-f]{3}|[0-9a-f]{6})', c)
    if m:
        hexv = m.group(1)
        if len(hexv) == 3:
            hexv = ''.join(ch * 2 for ch in hexv)  # ex: #abc -> #aabbcc
        return f"#{hexv}"

    return None

def build_tokens(samples):
    colors_bg = Counter()
    colors_fg = Counter()
    fonts = Counter()
    radii = Counter()
    shadows = Counter()

    for s in samples:
        c = normalize_color(s.get("color"))
        b = normalize_color(s.get("bg"))
        if c: colors_fg[c]+=1
        if b: colors_bg[b]+=1
        f = s.get("font")
        if f: fonts[f]+=1
        r = s.get("radius")
        if r and r != "0px": radii[r]+=1
        sh = s.get("shadow")
        if sh and sh != "none": shadows[sh]+=1

    def top(counter, n=8):
        return [x for x,_ in counter.most_common(n)]

    tokens = {
        "colors": {
            "bg_candidates": top(colors_bg, 8),
            "fg_candidates": top(colors_fg, 8),
            "primary_guess": top(colors_fg, 1)[0] if colors_fg else None
        },
        "typography": {
            "font_candidates": top(fonts, 5),
            "h_weight_guess": "800",
            "body_weight_guess": "400"
        },
        "radius_candidates": top(radii, 5),
        "shadow_candidates": top(shadows, 5)
    }
    return tokens

def write_css_vars(tokens):
    # mapeia os candidatos para variáveis padrão; ajuste manual depois
    bg = (tokens["colors"]["bg_candidates"] or ["#0b0c10"])[0]
    text = (tokens["colors"]["fg_candidates"] or ["#f0f0f0"])[0]
    primary = tokens["colors"]["primary_guess"] or "#00fff7"
    font = (tokens["typography"]["font_candidates"] or ["ui-sans-serif, system-ui, -apple-system, Segoe UI, Inter"])[0]
    radius = (tokens["radius_candidates"] or ["20px"])[0]

    css = f""":root {{
  --ds-bg: {bg};
  --ds-text: {text};
  --ds-primary: {primary};
  --ds-accent: #d414fe;
  --ds-card: #12131a;
  --ds-border: #1e2230;
  --ds-font: {font};
  --ds-radius: {radius};
}}
body.stellar-dark {{
  background: var(--ds-bg); color: var(--ds-text); font-family: var(--ds-font);
}}
"""
    with open(os.path.join(OUT_DIR, "stellar.css"), "w") as f:
        f.write(css)

def main():
    all_samples = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for u in SEED_URLS:
            page.goto(u, wait_until="load")
            all_samples.extend(collect_styles(page))
        browser.close()

    tokens = build_tokens(all_samples)
    with open(os.path.join(OUT_DIR, "tokens.json"), "w") as f:
        json.dump(tokens, f, indent=2)
    write_css_vars(tokens)
    print("[ok] tokens.json + stellar.css gerados em", OUT_DIR)

if __name__ == "__main__":
    main()
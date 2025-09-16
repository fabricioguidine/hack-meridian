#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Captura estilos computados de CTAs no quest.stellar.org e gera overrides CSS.
Saída:
- stellar_ds_autogen/cta_tokens.json
- stellar_ds/css/overrides.css  (classe .st-btn-primary com os estilos reais)
"""
import os, json, re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stellar_ds_autogen"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OVR_DIR = ROOT / "stellar_ds" / "css"
OVR_DIR.mkdir(parents=True, exist_ok=True)

PAGES = [
    "https://quest.stellar.org/",
    "https://quest.stellar.org/learn",
    "https://quest.stellar.org/side-quests",
]

# Palavras-chave comuns de CTA
CTA_HINTS = [
    "get started", "start", "continue", "begin", "view", "claim", "enroll", "learn more"
]

SELECTOR_CANDIDATES = [
    "a", "button", "a[role=button]", "button[type=button]", "[data-testid], [class*='btn'], [class*='Button']"
]

def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

JS_GET_STYLES = """
(el) => {
  const cs = getComputedStyle(el);
  const rect = el.getBoundingClientRect();
  const text = (el.innerText || el.textContent || "").trim();
  return {
    text,
    tag: el.tagName.toLowerCase(),
    background: cs.background,
    backgroundImage: cs.backgroundImage,
    backgroundColor: cs.backgroundColor,
    color: cs.color,
    boxShadow: cs.boxShadow,
    border: cs.border,
    borderRadius: cs.borderRadius,
    letterSpacing: cs.letterSpacing,
    textTransform: cs.textTransform,
    fontFamily: cs.fontFamily,
    fontWeight: cs.fontWeight,
    fontSize: cs.fontSize,
    padding: [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft].join(" "),
    lineHeight: cs.lineHeight,
    height: rect.height,
    width: rect.width
  };
}
"""

def looks_like_cta(text: str) -> bool:
    t = (text or "").strip().lower()
    if not t:
        return False
    return any(h in t for h in CTA_HINTS)

def pick_best_cta(items):
    """
    Heurística: prioriza quem tem backgroundImage/boxShadow, largura razoável e texto de CTA.
    """
    scored = []
    for it in items:
        score = 0
        if looks_like_cta(it["text"]): score += 5
        if it["backgroundImage"] and it["backgroundImage"] != "none": score += 3
        if it["boxShadow"] and it["boxShadow"] != "none": score += 2
        # size sweet spot
        if 40 <= it["height"] <= 80: score += 1
        if 120 <= it["width"] <= 360: score += 1
        scored.append((score, it))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1] if scored else None

def gen_overrides_css(style: dict) -> str:
    """
    Gera CSS para .st-btn-primary com os valores exatos capturados.
    Mantemos estrutura de classe, mas com background/box-shadow/raio/letter-spacing idênticos.
    """
    # Segurança contra valores 'none' ou vazios
    bgimg = style.get("backgroundImage", "none")
    bgcolor = style.get("backgroundColor", "transparent")
    color = style.get("color", "#000")
    boxshadow = style.get("boxShadow", "none")
    radius = style.get("borderRadius", "9999px")
    ls = style.get("letterSpacing", "0.04em")
    tf = style.get("textTransform", "uppercase")
    ff = style.get("fontFamily", "Inter, sans-serif")
    fw = style.get("fontWeight", "800")
    fs = style.get("fontSize", "14px")
    pad = style.get("padding", "12px 18px")

    # Se houver backgroundImage, priorizamos ele; senão usamos backgroundColor
    if bgimg and bgimg != "none":
        bg_rule = f"background-image: {bgimg};\n  background-size: cover; background-repeat: no-repeat;"
    else:
        bg_rule = f"background: {bgcolor};"

    css = f"""/* Auto-generated from quest.stellar.org CTAs — do not edit by hand */
.st-btn.st-btn-primary {{
  {bg_rule}
  color: {color};
  box-shadow: {boxshadow};
  border-radius: {radius};
  letter-spacing: {ls};
  text-transform: {tf};
  font-family: {ff};
  font-weight: {fw};
  font-size: {fs};
  padding: {pad};
}}
"""
    return css

def main():
    data = {"captures": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for url in PAGES:
            page.goto(url, wait_until="load")
            # pega candidatos
            items = []
            for sel in SELECTOR_CANDIDATES:
                for el in page.query_selector_all(sel):
                    st = page.evaluate(JS_GET_STYLES, el)
                    st["page"] = url
                    st["selectorHit"] = sel
                    items.append(st)
            # filtra por texto de CTA e escolhe melhor
            best = pick_best_cta(items)
            if best:
                data["captures"].append(best)
        browser.close()

    # guarda tokens capturados
    out_json = OUT_DIR / "cta_tokens.json"
    out_json.write_text(json.dumps(data, indent=2))
    print(f"[ok] wrote {out_json}")

    # se houver pelo menos um capture, gera overrides
    best = data["captures"][0] if data["captures"] else None
    if best:
        overrides = gen_overrides_css(best)
        ovr_css = OVR_DIR / "overrides.css"
        ovr_css.write_text(overrides)
        print(f"[ok] wrote {ovr_css}")
        print("[hint] Include overrides.css AFTER stellar.css for exact CTA look.")
    else:
        print("[warn] No CTA found. Try adding more URLs or different keywords in CTA_HINTS.")

if __name__ == "__main__":
    main()
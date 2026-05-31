#!/usr/bin/env bash
# sync_project.sh — bring your repo to the expected state for the hackathon
# Usage:
#   chmod +x sync_project.sh
#   ./sync_project.sh           # create missing stuff only
#   ./sync_project.sh --force   # overwrite files with canonical versions

set -euo pipefail

FORCE=false
if [[ "${1:-}" == "--force" ]]; then
  FORCE=true
fi

ROOT="$(pwd)"

# ---------- helpers ----------
ensure_dir() {
  local d="$1"
  if [[ ! -d "$d" ]]; then
    mkdir -p "$d"
    echo "[mk] $d"
  fi
}

write_file() {
  # write_file <path> <heredoc_name>
  local path="$1"
  local blob="$2"

  if $FORCE || [[ ! -f "$path" ]]; then
    # shellcheck disable=SC2086
    cat > "$path" <<"$blob"
$(eval "echo \"\$$blob\"")
$blob
    echo "[wr] $path"
  else
    echo "[ok] $path (exists; use --force to overwrite)"
  fi
}

# ---------- desired folders ----------
ensure_dir "$ROOT/scripts"
ensure_dir "$ROOT/logs"
ensure_dir "$ROOT/data/html"
ensure_dir "$ROOT/data/extracts"
ensure_dir "$ROOT/data/state"
ensure_dir "$ROOT/stellar_ds/tokens"
ensure_dir "$ROOT/stellar_ds/css"
ensure_dir "$ROOT/stellar_ds/components"
ensure_dir "$ROOT/stellar_examples/tokens"
ensure_dir "$ROOT/stellar_examples/components"

# ---------- .gitignore (append if missing lines) ----------
GITIGNORE_PATH="$ROOT/.gitignore"
touch "$GITIGNORE_PATH"
append_once () {
  local line="$1"
  grep -qxF "$line" "$GITIGNORE_PATH" || echo "$line" >> "$GITIGNORE_PATH"
}

append_once "__pycache__/"
append_once ".venv/"
append_once "data/html/"
append_once "data/tmp/"
append_once "data/state/*"
append_once "!data/state/.gitkeep"
append_once "logs/"
append_once ".DS_Store"

# keep state dir visible in git if desired
touch "$ROOT/data/state/.gitkeep"

# ---------- canonical files (tokens + css) ----------
TOKENS_JSON='{
  "colors": {
    "bg": "#010323",
    "text": "#ffffff",
    "textMuted": "#cecece",
    "primary": "#07ffee",
    "accent": "#fff735",
    "card": "#19193e",
    "border": "#23234e",
    "surface": "#3e3f58"
  },
  "typography": {
    "fontFamilyBody": "Inter, sans-serif",
    "fontFamilyHeading": "Play, sans-serif",
    "h1": { "size": "2.25rem", "weight": 800, "transform": "uppercase", "letterSpacing": "0.02em" },
    "h2": { "size": "1.5rem", "weight": 700, "transform": "uppercase", "letterSpacing": "0.02em" },
    "body": { "size": "1rem", "weight": 400 }
  },
  "radius": {
    "sm": "4px",
    "md": "8px",
    "lg": "12px",
    "pill": "9999px"
  },
  "shadow": {
    "card": "0 10px 30px rgba(0,0,0,.35)",
    "glowPrimary": "0 0 0 2px rgba(7,255,238,.15), 0 0 30px rgba(7,255,238,.15)",
    "glowAccent": "0 0 0 2px rgba(255,247,53,.18), 0 0 30px rgba(255,247,53,.18)",
    "pixelPrimaryInset": "rgb(0, 216, 201) -2px -2px 0px 0px inset, rgb(166, 255, 249) 2px 2px 0px 0px inset, rgb(0, 216, 201) -2px -2px 0px 2px inset, rgb(166, 255, 249) 2px 2px 0px 2px inset",
    "pixelAccentInset": "rgb(224, 216, 0) -2px -2px 0px 0px inset, rgb(255, 251, 152) 2px 2px 0px 0px inset, rgb(224, 216, 0) -2px -2px 0px 2px inset, rgb(255, 251, 152) 2px 2px 0px 2px inset"
  },
  "spacing": {
    "xs": "6px",
    "sm": "10px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px"
  }
}'
STELLAR_CSS='/* ========== Tokens as CSS variables ========== */
:root {
  --ds-bg: #010323;
  --ds-text: #ffffff;
  --ds-text-muted: #cecece;
  --ds-primary: #07ffee;
  --ds-accent: #fff735;
  --ds-card: #19193e;
  --ds-border: #23234e;
  --ds-surface: #3e3f58;

  --ds-font-body: Inter, sans-serif;
  --ds-font-heading: Play, sans-serif;
  --ds-h1-size: 2.25rem; --ds-h1-weight: 800; --ds-hx-transform: uppercase; --ds-hx-tracking: 0.02em;
  --ds-h2-size: 1.5rem;  --ds-h2-weight: 700;

  --ds-radius-sm: 4px;
  --ds-radius-md: 8px;
  --ds-radius-lg: 12px;
  --ds-radius-pill: 9999px;

  --ds-shadow-card: 0 10px 30px rgba(0,0,0,.35);
  --ds-glow-primary: 0 0 0 2px rgba(7,255,238,.15), 0 0 30px rgba(7,255,238,.15);
  --ds-glow-accent: 0 0 0 2px rgba(255,247,53,.18), 0 0 30px rgba(255,247,53,.18);
  --ds-pixel-primary-inset: rgb(0, 216, 201) -2px -2px 0px 0px inset, rgb(166, 255, 249) 2px 2px 0px 0px inset, rgb(0, 216, 201) -2px -2px 0px 2px inset, rgb(166, 255, 249) 2px 2px 0px 2px inset;
  --ds-pixel-accent-inset: rgb(224, 216, 0) -2px -2px 0px 0px inset, rgb(255, 251, 152) 2px 2px 0px 0px inset, rgb(224, 216, 0) -2px -2px 0px 2px inset, rgb(255, 251, 152) 2px 2px 0px 2px inset;

  --ds-space-xs: 6px;
  --ds-space-sm: 10px;
  --ds-space-md: 16px;
  --ds-space-lg: 24px;
  --ds-space-xl: 32px;
}
body.stellar-dark { background: var(--ds-bg); color: var(--ds-text); font-family: var(--ds-font-body); }
h1, .st-h1 { font-family: var(--ds-font-heading); font-size: var(--ds-h1-size); font-weight: var(--ds-h1-weight); text-transform: var(--ds-hx-transform); letter-spacing: var(--ds-hx-tracking); margin: var(--ds-space-lg) 0 var(--ds-space-md); }
h2, .st-h2 { font-family: var(--ds-font-heading); font-size: var(--ds-h2-size); font-weight: var(--ds-h2-weight); text-transform: var(--ds-hx-transform); letter-spacing: var(--ds-hx-tracking); margin: var(--ds-space-md) 0 var(--ds-space-sm); }
.st-muted { color: var(--ds-text-muted); }

/* Badge Card */
.st-badge-card { background: var(--ds-card); border: 1px solid var(--ds-border); border-radius: var(--ds-radius-lg); box-shadow: var(--ds-shadow-card); padding: var(--ds-space-md); position: relative; transition: transform .15s, box-shadow .15s, border-color .15s; }
.st-badge-card:hover { transform: translateY(-2px); border-color: var(--ds-primary); box-shadow: var(--ds-glow-primary), var(--ds-shadow-card); }
.st-badge-card img { display: block; width: 100%; height: auto; border-radius: var(--ds-radius-md); border: 1px solid var(--ds-border); }
.st-badge-card .st-title { margin-top: var(--ds-space-sm); font-family: var(--ds-font-heading); font-weight: 800; text-transform: uppercase; letter-spacing: 0.02em; }
.st-badge-card .st-subtitle { color: var(--ds-text-muted); font-size: 0.95rem; }

/* Progress Bar */
.st-progress { margin-top: var(--ds-space-sm); height: 8px; width: 100%; background: var(--ds-surface); border: 1px solid var(--ds-border); border-radius: var(--ds-radius-md); overflow: hidden; }
.st-progress > span { display: block; height: 100%; width: var(--value, 0%); background: linear-gradient(90deg, var(--ds-primary), var(--ds-accent)); }

/* Button */
.st-btn { display: inline-flex; align-items: center; justify-content: center; padding: 10px 16px; border-radius: var(--ds-radius-pill); font-weight: 800; text-transform: uppercase; letter-spacing: 0.02em; border: 1px solid transparent; cursor: pointer; transition: filter .15s, box-shadow .15s, transform .1s; }
.st-btn-primary { background: linear-gradient(90deg, var(--ds-accent), var(--ds-primary)); color: #000; box-shadow: var(--ds-glow-accent); }
.st-btn-primary:hover { filter: brightness(1.05); transform: translateY(-1px); }

/* Pixel inset variants */
.st-btn-pixel-primary { box-shadow: var(--ds-pixel-primary-inset); background: var(--ds-card); color: var(--ds-text); }
.st-btn-pixel-accent { box-shadow: var(--ds-pixel-accent-inset); background: var(--ds-card); color: var(--ds-text); }

/* Tabs */
.st-tab { display: inline-flex; gap: 8px; border-bottom: 2px solid var(--ds-border); }
.st-tab a { padding: 10px 12px; text-decoration: none; color: var(--ds-text-muted); border-bottom: 4px solid transparent; font-weight: 700; text-transform: uppercase; }
.st-tab a.is-active { color: var(--ds-primary); border-bottom-color: var(--ds-primary); }
'

write_file "$ROOT/stellar_ds/tokens/tokens.json" TOKENS_JSON
write_file "$ROOT/stellar_ds/css/stellar.css" STELLAR_CSS

# ---------- minimal styleguide (optional) ----------
STYLEGUIDE_HTML='<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Stellar DS Styleguide</title>
  <link rel="stylesheet" href="../stellar_ds/css/stellar.css"/>
  <style>body{max-width:980px;margin:2rem auto;padding:0 1rem}</style>
</head>
<body class="stellar-dark">
  <h1 class="st-h1">Stellar Design System — Styleguide</h1>

  <h2 class="st-h2">Buttons</h2>
  <button class="st-btn st-btn-primary">Primary</button>
  <button class="st-btn st-btn-pixel-primary" style="margin-left:8px">Pixel Primary</button>
  <button class="st-btn st-btn-pixel-accent" style="margin-left:8px">Pixel Accent</button>

  <h2 class="st-h2">Badge Card</h2>
  <div class="st-badge-card" style="max-width:360px">
    <img src="https://via.placeholder.com/640x360.png?text=Badge" alt="">
    <div class="st-title">Pioneer Quest</div>
    <div class="st-subtitle">Complete intro task</div>
    <div class="st-progress"><span style="--value:60%"></span></div>
    <button class="st-btn st-btn-primary" style="margin-top:12px">Start</button>
  </div>

  <h2 class="st-h2" style="margin-top:24px">Tabs</h2>
  <div class="st-tab">
    <a href="#" class="is-active">Classic Quests</a>
    <a href="#">Side Quests</a>
  </div>
</body>
</html>'
ensure_dir "$ROOT/styleguide"
write_file "$ROOT/styleguide/index.html" STYLEGUIDE_HTML

echo "[done] Project synced. Use --force to overwrite canonical files."
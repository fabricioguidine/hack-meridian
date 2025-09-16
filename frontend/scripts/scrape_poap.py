#!/usr/bin/env python3
"""
POAP → Dataset de Referência (HTML + Componentes)
- Domínio: poap.xyz
- Salva: data/html/<sha1>.html (HTML cru)
         data/extracts/components.jsonl (componentes para guiar o DS Stellar)
- Boas práticas: robots.txt, rate limit, baixa concorrência, resume de estado
"""
import asyncio, aiohttp, aiofiles, os, json, hashlib, re
from urllib.parse import urljoin, urlparse, urldefrag
from bs4 import BeautifulSoup
from tqdm import tqdm

START_URLS = ["https://poap.xyz/", "https://poap.xyz/sitemap.xml"]
ALLOWED_HOST = "poap.xyz"

MAX_PAGES      = int(os.getenv("MAX_PAGES", "300"))
CONCURRENCY    = int(os.getenv("CONCURRENCY", "3"))
RATE_LIMIT_SEC = float(os.getenv("RATE_LIMIT_SEC", "0.8"))
TIMEOUT        = aiohttp.ClientTimeout(total=30)
UA             = "MeridianHackathon/POAP-Scraper/1.0 (+contact@example.org)"

DATA_DIR   = "data"
HTML_DIR   = os.path.join(DATA_DIR, "html")
STATE_DIR  = os.path.join(DATA_DIR, "state")
EXTR_DIR   = os.path.join(DATA_DIR, "extracts")
os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(EXTR_DIR, exist_ok=True)

STATE_FILE   = os.path.join(STATE_DIR, "frontier.json")
VISITED_FILE = os.path.join(STATE_DIR, "visited.json")
COMPONENTS_JL = os.path.join(EXTR_DIR, "components.jsonl")

def norm_url(url: str) -> str:
    url, _ = urldefrag(url)
    p = urlparse(url)
    if p.netloc.lower().endswith(ALLOWED_HOST) is False:
        return ""
    # ignorar query para reduzir duplicidade
    p = p._replace(query="")
    path = p.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    p = p._replace(path=path, netloc=p.netloc.replace(":80","").replace(":443",""))
    return p.geturl()

def is_html(content_type: str|None) -> bool:
    if not content_type: return False
    return content_type.split(";")[0].strip().lower() in {"text/html","application/xhtml+xml"}

def u2path(url: str) -> str:
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return os.path.join(HTML_DIR, f"{h}.html")

async def save_text(path: str, text: str):
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(text)

async def fetch_robots(session: aiohttp.ClientSession) -> str:
    try:
        async with session.get("https://poap.xyz/robots.txt") as r:
            if r.status == 200: return await r.text()
    except: pass
    return ""

def allowed_by_robots(robots: str, url: str) -> bool:
    # Checagem simples de Disallow p/ User-agent: *
    dis = []
    ua = None
    for line in robots.splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        if line.lower().startswith("user-agent:"):
            ua = line.split(":",1)[1].strip()
        elif line.lower().startswith("disallow:") and (ua == "*" or ua is None):
            rule = line.split(":",1)[1].strip()
            if rule: dis.append(rule)
    path = urlparse(url).path or "/"
    return not any(path.startswith(rule) for rule in dis)

def extract_links(base_url: str, html: str):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        n = norm_url(urljoin(base_url, a["href"]))
        if n: out.append(n)
    # de-dup preservando ordem
    seen, dedup = set(), []
    for u in out:
        if u not in seen:
            seen.add(u); dedup.append(u)
    return dedup

def extract_components(url: str, html: str) -> dict:
    """Extrai pistas de UI úteis para mapear para o DS Stellar (cards, títulos, CTAs)."""
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.string.strip() if soup.title and soup.title.string else "")
    headings = [h.get_text(strip=True) for h in soup.find_all(["h1","h2","h3"]) if h.get_text(strip=True)]
    buttons  = [b.get_text(strip=True) for b in soup.find_all(["button"]) if b.get_text(strip=True)]
    links_cta = [a.get_text(strip=True) for a in soup.find_all("a") if a.get_text(strip=True) and a.get("href","").startswith("https")]
    imgs_alt  = [img.get("alt","").strip() for img in soup.find_all("img") if img.get("alt")]
    classes   = {}
    for el in soup.find_all(True):
        cls = el.get("class")
        if cls:
            for c in cls:
                classes[c] = classes.get(c, 0) + 1
    # Heurística simples de “cards/badges”
    possible_cards = [div.get_text(" ", strip=True)[:120] for div in soup.find_all("div", class_=re.compile(r"(card|badge|poap|event)", re.I))]
    return {
        "url": url,
        "title": title,
        "headings": headings,
        "buttons": buttons[:40],
        "links_sample": links_cta[:40],
        "imgs_alt_sample": imgs_alt[:40],
        "top_classes": sorted(classes.items(), key=lambda kv: kv[1], reverse=True)[:40],
        "possible_cards_sample": possible_cards[:20],
    }

async def crawl():
    headers = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"}
    sem = asyncio.Semaphore(CONCURRENCY)
    connector = aiohttp.TCPConnector(limit_per_host=CONCURRENCY, ssl=False)

    # estado
    frontier = []
    visited = set()
    if os.path.exists(STATE_FILE):
        try: frontier = json.load(open(STATE_FILE)) or []
        except: frontier = []
    if os.path.exists(VISITED_FILE):
        try: visited = set(json.load(open(VISITED_FILE)) or [])
        except: visited = set()
    if not frontier:
        seeds = {norm_url(u) for u in START_URLS if norm_url(u)}
        frontier = list(seeds)

    async with aiohttp.ClientSession(headers=headers, connector=connector, timeout=TIMEOUT) as session:
        robots = await fetch_robots(session)
        pbar = tqdm(total=MAX_PAGES, desc="Crawled", unit="page")
        saved = 0

        # abrir arquivo jsonl de componentes
        comp_fp = await aiofiles.open(COMPONENTS_JL, "a", encoding="utf-8")

        while frontier and saved < MAX_PAGES:
            url = frontier.pop(0)
            if url in visited: continue
            if robots and not allowed_by_robots(robots, url):
                visited.add(url); continue

            async with sem:
                await asyncio.sleep(RATE_LIMIT_SEC)
                try:
                    async with session.get(url) as r:
                        ctype = r.headers.get("Content-Type","")
                        final = str(r.url)
                        visited.add(url)
                        if r.status == 200 and is_html(ctype):
                            html = await r.text()
                            # salva HTML
                            path = u2path(final)
                            await save_text(path, html)
                            saved += 1
                            pbar.update(1)
                            # extrai componentes e salva jsonl
                            comp = extract_components(final, html)
                            await comp_fp.write(json.dumps(comp, ensure_ascii=False) + "\n")
                            # expande frontier
                            for lk in extract_links(final, html):
                                if lk not in visited and lk not in frontier:
                                    frontier.append(lk)
                except:
                    visited.add(url)

            if len(visited) % 10 == 0:
                json.dump(frontier, open(STATE_FILE, "w"), indent=2)
                json.dump(list(visited), open(VISITED_FILE, "w"))

        json.dump(frontier, open(STATE_FILE, "w"), indent=2)
        json.dump(list(visited), open(VISITED_FILE, "w"))
        await comp_fp.close()
        pbar.close()

if __name__ == "__main__":
    try:
        asyncio.run(crawl())
    except KeyboardInterrupt:
        print("Interrompido. Estado salvo.")
#!/usr/bin/env python3
"""
Arizona Cardinals collector — mirrors your working Eagles/Colts shape.

- Uses a real User-Agent (some sources return empty without it).
- Blocks MLB "St. Louis Cardinals" noise; otherwise permissive for NFL Cards.
- Dedupe by (normalized title + canonical link).
- Sort newest → keep 50.
- Writes items.json with: team, updated_at, items[], sources[], links[].
"""

import json, re, time, hashlib, html, pathlib, urllib.parse
from datetime import datetime, timezone
import requests, feedparser

from feeds import FEEDS, STATIC_LINKS, TEAM_NAME

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "items.json"
MAX_ITEMS = 50
TIMEOUT = 20

UA_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/123.0 Safari/537.36"
    )
}

# ---------- helpers

def domain(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).netloc.lower().lstrip("www.")
    except Exception:
        return ""

def clean_url(u: str) -> str:
    if not u: return u
    try:
        p = urllib.parse.urlparse(u)
        q = urllib.parse.parse_qs(p.query)
        drop = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content","fbclid","gclid","mc_cid","mc_eid"}
        q = {k:v for k,v in q.items() if k not in drop}
        p = p._replace(query=urllib.parse.urlencode(q, doseq=True), fragment="")
        return urllib.parse.urlunparse(p)
    except Exception:
        return u

def norm_title(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").strip()).lower()

def ts_from(entry_dict) -> int:
    # entry_dict: {"published_parsed":, "updated_parsed":}
    for k in ("published_parsed","updated_parsed"):
        v = entry_dict.get(k)
        if v:
            try: return int(time.mktime(v))
            except Exception: pass
    return int(time.time())

# ---------- filter (NFL Cards; MLB guard)

MLB_BLOCK = {"st. louis cardinals","st louis cardinals","mlb","baseball","nl central"}

NAMES_HINTS = (
    "kyler murray","marvin harrison jr","trey mcbride","james conner",
    "jonathan gannon","paris johnson","budda baker","jalen thompson",
)

def allow(title: str, summary: str, src_dom: str) -> bool:
    t = f"{title or ''} {summary or ''}".lower()
    if any(x in t for x in MLB_BLOCK):
        return False
    if "arizona cardinals" in t or "az cardinals" in t:
        return True
    if "cardinals" in t:
        # If it's the generic "Cardinals", still allow unless MLB words appear (already blocked)
        return True
    if any(n in t for n in NAMES_HINTS):
        return True
    # fallback: accept from obviously football-y domains in FEEDS labels (handled via source label later)
    return False

def fetch_parse(url: str):
    """Fetch with UA, then feedparser-parse the bytes."""
    try:
        r = requests.get(url, headers=UA_HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        return feedparser.parse(r.content)
    except Exception:
        return {"entries": []}

# ---------- main

def main():
    seen = set()
    items = []

    for f in FEEDS:
        name, url = f["name"], f["url"]
        parsed = fetch_parse(url)
        entries = parsed.get("entries", []) or []

        for e in entries:
            title = re.sub(r"\s+", " ", (getattr(e, "title", "") or "").strip())
            link  = clean_url(getattr(e, "link", "") or getattr(e, "id", "") or "")
            if not title or not link:
                continue

            src_dom = domain(link)
            summary = getattr(e, "summary", "") or getattr(e, "description", "")

            if not allow(title, summary, src_dom):
                continue

            # dedupe
            key = hashlib.sha1((norm_title(title) + "|" + link).encode("utf-8")).hexdigest()
            if key in seen:
                continue
            seen.add(key)

            ts = ts_from({
                "published_parsed": getattr(e, "published_parsed", None),
                "updated_parsed": getattr(e, "updated_parsed", None),
            })

            items.append({
                "title": title,
                "link": link,
                "source": name,         # label from FEEDS, like Eagles/Colts
                "published": ts
            })

    # newest first, cap
    items.sort(key=lambda x: x.get("published") or 0, reverse=True)
    items = items[:MAX_ITEMS]

    data = {
        "team": TEAM_NAME,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "items": items,
        "sources": sorted({it["source"] for it in items}),
        "links": STATIC_LINKS
    }

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote items.json with {len(items)} items and {len(data['sources'])} sources at {data['updated_at']}")

if __name__ == "__main__":
    main()
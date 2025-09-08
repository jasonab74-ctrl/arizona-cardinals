#!/usr/bin/env python3
# Arizona Cardinals — hardened collector
# - Curated source list for dropdown (no random junk)
# - Strict Cardinals/NFL filters (drops Suns/D-backs/Coyotes etc.)
# - Always writes 'updated', 'links' and *string* 'sources' so UI never collapses
# - Normalizes hosts and strips tracking query params so de-duping is stable

import json, time, re, hashlib
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from datetime import datetime, timezone
import feedparser
from feeds import FEEDS, STATIC_LINKS

MAX_ITEMS = 60

# ---- Curated dropdown (10 reliable Cards sources) ----
CURATED_SOURCES = [
    "AZCardinals.com",
    "Arizona Republic / azcentral",
    "Arizona Sports (98.7)",
    "Revenge of the Birds",
    "Cards Wire",
    "PHNX Cardinals",
    "ESPN",
    "Yahoo Sports",
    "Sports Illustrated",
    "CBS Sports",
]
ALLOWED_SOURCES = set(CURATED_SOURCES)

# ---------------- utils ----------------
def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def _host(u: str) -> str:
    try:
        n = urlparse(u).netloc.lower()
        for p in ("www.","m.","amp."):
            if n.startswith(p): n = n[len(p):]
        return n
    except Exception:
        return ""

def canonical(u: str) -> str:
    try:
        p = urlparse(u)
        # keep only stable params; drop tracking
        keep = {"id","story","v","p"}
        q = parse_qs(p.query)
        q = {k:v for k,v in q.items() if k in keep}
        p = p._replace(query=urlencode(q, doseq=True), fragment="", netloc=_host(u))
        return urlunparse(p)
    except Exception:
        return u

def hid(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]

ALIASES = {
    "azcardinals.com":          "AZCardinals.com",
    "azcentral.com":            "Arizona Republic / azcentral",
    "arizonasports.com":        "Arizona Sports (98.7)",
    "revengeofthebirds.com":    "Revenge of the Birds",
    "cardswire.usatoday.com":   "Cards Wire",
    "gophnx.com":               "PHNX Cardinals",
    "espn.com":                 "ESPN",
    "sports.yahoo.com":         "Yahoo Sports",
    "si.com":                   "Sports Illustrated",
    "cbssports.com":            "CBS Sports",
}

# --------- content filters ----------
KEEP = [
    r"\bCardinals?\b", r"\bArizona Cardinals?\b", r"\bNFL\b",
    r"\bKyler Murray\b", r"\bJonathan Gannon\b", r"\bMarvin Harrison\b",
    r"\bBudda Baker\b", r"\bJames Conner\b", r"\bTrey McBride\b",
]
DROP = [
    r"\bSuns\b", r"\bNBA\b", r"\bCoyotes\b", r"\bNHL\b",
    r"\bDiamondbacks\b", r"\bD-?backs\b", r"\bMLB\b",
    r"\bbaseball\b", r"\bbasketball\b", r"\bhockey\b", r"\bsoccer\b",
    r"\bwomen'?s\b", r"\bWBB\b", r"\bvolleyball\b",
]

def text_ok(title: str, summary: str) -> bool:
    t = f"{title} {summary}"
    if not any(re.search(p, t, re.I) for p in KEEP): return False
    if any(re.search(p, t, re.I) for p in DROP): return False
    return True

def parse_time(entry):
    for key in ("published_parsed","updated_parsed"):
        if entry.get(key):
            try:
                return time.strftime("%Y-%m-%dT%H:%M:%S%z", entry[key])
            except Exception:
                pass
    # fallback so dates always render
    return now_iso()

def source_label(link: str, feed_name: str) -> str:
    # Map to a curated display label; fall back to feed name string
    return ALIASES.get(_host(link), feed_name.strip())

# ---------------- pipeline ----------------
def fetch_all():
    items, seen = [], set()
    for f in FEEDS:
        fname, furl = f["name"].strip(), f["url"].strip()
        try:
            parsed = feedparser.parse(furl)
        except Exception:
            continue
        for e in parsed.entries[:140]:
            link = canonical((e.get("link") or e.get("id") or "").strip())
            if not link: continue

            key = hid(link)
            if key in seen: continue

            src = source_label(link, fname)
            if src not in ALLOWED_SOURCES:
                continue  # keeps dropdown clean/curated

            title = (e.get("title") or "").strip()
            summary = (e.get("summary") or e.get("description") or "").strip()
            if not text_ok(title, summary): continue

            items.append({
                "id": key,
                "title": title or "(untitled)",
                "link": link,
                "source": src,                 # STRING (not object)
                "feed": fname,
                "published": parse_time(e),
                "summary": summary,
            })
            seen.add(key)

    items.sort(key=lambda x: x["published"], reverse=True)
    return items[:MAX_ITEMS]

def write_items(items):
    # Ensure 'sources' is an array of STRINGS (prevents [object Object] in UI)
    payload = {
        "updated": now_iso(),
        "items": items,
        "links": STATIC_LINKS,                 # buttons always present
        "sources": list(CURATED_SOURCES),      # frozen curated list
    }
    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def main():
    write_items(fetch_all())

if __name__ == "__main__":
    main()
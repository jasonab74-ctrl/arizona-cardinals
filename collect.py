#!/usr/bin/env python3
"""
Arizona Cardinals collector — pulls feeds, dedupes, filters to NFL Cards,
writes items.json the site uses.
"""

import json, re, time, datetime as dt, html
from urllib.parse import urlparse
import feedparser, requests

from feeds import FEEDS, STATIC_LINKS, TEAM_NAME

OUT_FILE = "items.json"
MAX_ITEMS = 50   # limit the list to the 50 most recent

# --- Keywords / filters -------------------------------------------------------

TEAM_KEYWORDS = [
    "Arizona Cardinals", "Cardinals", "AZ Cardinals", "Red Sea",
    # players/coaches (common ones—expand as needed)
    "Kyler Murray", "James Conner", "Marvin Harrison Jr", "Trey McBride",
    "Budda Baker", "Paris Johnson", "Darius Robinson", "Jonathan Gannon",
]

# Hard exclusions to avoid *St. Louis Cardinals* MLB contamination, etc.
EXCLUDE_PHRASES = [
    "St. Louis Cardinals", "Cardinals (MLB)", "MLB", "baseball", "pitcher",
    "Bats", "innings", "home run", "Cardinals vs. Cubs", "Cardinals vs Cubs",
    "Louisville Cardinals", "Ball State Cardinals"
]

TRUSTED_HOSTS = {
    "www.azcardinals.com", "azcardinals.com", "www.nfl.com", "nfl.com",
    "www.espn.com", "sports.yahoo.com", "bleacherreport.com",
    "cardswire.usatoday.com", "profootballtalk.nbcsports.com",
    "www.si.com", "www.revengeofthebirds.com"
}

# --- helpers ------------------------------------------------------------------

def now_iso():
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def clean_text(t):
    if not t: return ""
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def canonicalize_url(u):
    if not u: return u
    # follow simple redirects
    try:
        r = requests.head(u, allow_redirects=True, timeout=8)
        if r.ok:
            return r.url
    except Exception:
        pass
    return u

def is_trusted_host(u):
    try:
        h = urlparse(u).netloc.lower()
    except Exception:
        return False
    if h.startswith("www."):
        h = h[4:]
    return h in {x.replace("www.", "") for x in TRUSTED_HOSTS}

def looks_like_cards(title, summary):
    text = f"{title} {summary}".lower()

    # exclude MLB or other-cardinals teams
    for bad in EXCLUDE_PHRASES:
        if bad.lower() in text:
            return False

    # require at least one team keyword OR "Cardinals" + clear NFL signals
    has_kw = any(k.lower() in text for k in TEAM_KEYWORDS)
    nfl_hints = ["nfl", "quarterback", "wide receiver", "coach", "defensive", "touchdown", "training camp", "preseason"]
    has_cardinals = "cardinals" in text
    has_nfl_hint = any(x in text for x in nfl_hints)

    return has_kw or (has_cardinals and has_nfl_hint)

def entry_source_name(entry, fallback_host):
    # Prefer explicit source fields if present
    for key in ("source", "author", "dc_source", "feedburner_origlink"):
        v = entry.get(key)
        if isinstance(v, dict) and v.get("title"):
            return clean_text(v["title"])
        if isinstance(v, str) and v.strip():
            return clean_text(v)
    return fallback_host

# --- main ---------------------------------------------------------------------

def collect():
    items = []
    seen = set()

    for feed in FEEDS:
        try:
            d = feedparser.parse(feed["url"])
        except Exception:
            continue

        for e in d.get("entries", []):
            link = e.get("link") or e.get("id")
            if not link:
                continue
            link = canonicalize_url(link)
            host = urlparse(link).netloc or "source"

            title = clean_text(e.get("title", ""))
            summary = clean_text(e.get("summary", "") or e.get("description", ""))

            # basic dedupe by URL + normalized title
            dedupe_key = (link, title.lower())
            if dedupe_key in seen:
                continue

            # filtering
            trusted = is_trusted_host(link)
            if not trusted and not looks_like_cards(title, summary):
                continue

            # published time
            ts = None
            if e.get("published_parsed"):
                ts = time.mktime(e.published_parsed)
            elif e.get("updated_parsed"):
                ts = time.mktime(e.updated_parsed)

            pub_iso = None
            if ts:
                pub_iso = dt.datetime.utcfromtimestamp(ts).replace(microsecond=0).isoformat() + "Z"

            items.append({
                "title": title or "(untitled)",
                "url": link,
                "source": entry_source_name(e, host),
                "published_at": pub_iso,
            })
            seen.add(dedupe_key)

    # sort newest first, cap list
    def sort_key(it):
        return it.get("published_at") or "1970-01-01T00:00:00Z"

    items.sort(key=sort_key, reverse=True)
    items = items[:MAX_ITEMS]

    sources = sorted({it["source"] for it in items})
    out = {
        "team": TEAM_NAME,
        "updated_at": now_iso(),
        "items": items,
        "sources": sources,
        "links": STATIC_LINKS,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(items)} items to {OUT_FILE}. Sources: {len(sources)}")

if __name__ == "__main__":
    collect()
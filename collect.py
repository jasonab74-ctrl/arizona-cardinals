# collect.py — Cardinals collector
# Changes vs. your non-working version:
# 1) Always sends a real User-Agent (some feeds block default clients).
# 2) Filter is NFL-safe: allows "Cardinals" headlines but hard-blocks MLB phrases.
# 3) Keeps 50 latest, dedupes by (normalized title + canonical link).
# 4) Writes sources list so your dropdown fills.

import json, re, time, hashlib, html, pathlib, urllib.parse
from datetime import datetime, timezone
import feedparser
import requests

from feeds import FEEDS, STATIC_LINKS

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "items.json"
MAX_ITEMS = 50

UA = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0 Safari/537.36"
}

def domain_of(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).netloc.lower().lstrip("www.")
    except Exception:
        return ""

def strip_tracking(u: str) -> str:
    try:
        p = urllib.parse.urlparse(u)
        q = urllib.parse.parse_qs(p.query)
        drop = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content",
                "ito","iclid","fbclid","gclid","mc_cid","mc_eid"}
        q = {k:v for k,v in q.items() if k not in drop}
        p = p._replace(query=urllib.parse.urlencode(q, doseq=True), fragment="")
        return urllib.parse.urlunparse(p)
    except Exception:
        return u

def norm_title(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").strip()).lower()

def parse_when(entry):
    # feedparser returns *_parsed tuples; default to "now" if missing
    if entry.get("published_parsed"):
        ts = int(time.mktime(entry["published_parsed"]))
    elif entry.get("updated_parsed"):
        ts = int(time.mktime(entry["updated_parsed"]))
    else:
        ts = int(time.time())
    return ts, datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

# ---------- filter

TRUST = {
    "azcardinals.com","espn.com","cardswire.usatoday.com","sports.yahoo.com",
    "revengeofthebirds.com","azcentral.com","bleacherreport.com","news.google.com"
}

MLB_BLOCK = {
    "st. louis cardinals","st louis cardinals","mlb","baseball","nl central"
}

def allow_item(title: str, summary: str, src_domain: str) -> bool:
    t = f"{title or ''} {summary or ''}".lower()

    if any(b in t for b in MLB_BLOCK):
        return False

    # trusted sources pass
    if src_domain in TRUST:
        return True

    # explicit team phrases
    if "arizona cardinals" in t or "az cardinals" in t:
        return True

    # generic but NFL context: allow "cardinals" if no MLB hints
    if "cardinals" in t:
        return True

    # key player/coach names
    for name in ("kyler murray","james conner","marvin harrison jr","trey mcbride",
                 "jonathan gannon","paris johnson"):
        if name in t:
            return True

    return False

# ---------- fetchers

def fetch_rss(url: str):
    # feedparser supports request_headers
    return feedparser.parse(url, request_headers=UA)

def collect():
    seen = set()
    items = []

    for feed in FEEDS:
        name = feed["name"]
        url  = feed["url"]
        trusted = feed.get("trusted", False)

        try:
            parsed = fetch_rss(url)
            entries = parsed.entries or []
        except Exception:
            entries = []

        for e in entries:
            title = re.sub(r"\s+", " ", (getattr(e, "title", "") or "").strip())
            link  = strip_tracking(getattr(e, "link", "") or "")
            if not title or not link:
                continue

            src_domain = domain_of(link)
            if not (trusted or allow_item(title, getattr(e, "summary", "") or getattr(e, "description", ""), src_domain)):
                continue

            key = hashlib.sha1((norm_title(title) + "|" + link).encode("utf-8")).hexdigest()
            if key in seen:
                continue
            seen.add(key)

            ts, iso = parse_when({
                "published_parsed": getattr(e, "published_parsed", None),
                "updated_parsed": getattr(e, "updated_parsed", None)
            })

            items.append({
                "title": title,
                "link": link,
                "source": name if trusted else (src_domain or name),
                "published": ts,
                "published_iso": iso,
            })

    items.sort(key=lambda x: x["published"], reverse=True)
    items = items[:MAX_ITEMS]

    payload = {
        "team": "Arizona Cardinals",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "items": items,
        "sources": sorted({it["source"] for it in items}),
        "links": STATIC_LINKS,
    }

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} with {len(items)} items")

if __name__ == "__main__":
    collect()
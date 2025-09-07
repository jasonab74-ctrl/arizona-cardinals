# collect.py — fetch feeds, dedupe, filter for ARIZONA CARDINALS (NFL), write items.json

import json, re, time, hashlib, html, pathlib, urllib.parse
from datetime import datetime, timezone
import feedparser
import requests

from feeds import FEEDS, STATIC_LINKS

ROOT = pathlib.Path(__file__).parent
OUT  = ROOT / "items.json"
MAX_ITEMS = 50  # cap list

# ---------- helpers

DOMAIN_RE = re.compile(r"https?://([^/]+)/", re.I)

def domain_of(url: str) -> str:
    try:
        netloc = urllib.parse.urlparse(url).netloc.lower()
        return netloc.replace("www.", "")
    except Exception:
        m = DOMAIN_RE.match(url or "")
        return (m.group(1) if m else "").lower().replace("www.", "")

def strip_tracking(u: str) -> str:
    try:
        p = urllib.parse.urlparse(u)
        q = urllib.parse.parse_qs(p.query)
        # drop common tracking params
        drop = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content","ito","iclid","fbclid","gclid","mc_cid","mc_eid"}
        q = {k:v for k,v in q.items() if k not in drop}
        new_q = urllib.parse.urlencode(q, doseq=True)
        p = p._replace(query=new_q, fragment="")
        return urllib.parse.urlunparse(p)
    except Exception:
        return u

def norm_title(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").strip()).lower()

def parse_when(entry):
    # prefer published_parsed, fall back
    ts = None
    if getattr(entry, "published_parsed", None):
        ts = int(time.mktime(entry.published_parsed))
    elif getattr(entry, "updated_parsed", None):
        ts = int(time.mktime(entry.updated_parsed))
    else:
        ts = int(time.time())
    iso = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    return ts, iso

# ---------- Cardinals filter (NFL) with MLB guard

NFL_REQUIRED_ANY = {
    # strong exacts
    "arizona cardinals", "az cardinals", "cards (nfl)",
    # context hints
    "nfl", "football", "nfc west",
    # players/coaches (keep small, still helpful)
    "kyler murray", "james conner", "marvin harrison jr", "trey mcbride",
    "jonathan gannon", "paris johnson",
}

MLB_BLOCK = {
    "st. louis cardinals", "st louis cardinals", "mlb", "baseball", "bally sports midwest",
}

TRUSTED_DOMAINS = {
    "azcardinals.com", "nfl.com", "espn.com", "sports.yahoo.com", "cardswire.usatoday.com",
    "revengeofthebirds.com", "azcentral.com", "bleacherreport.com",
}

def allow_item(title: str, summary: str, src_domain: str) -> bool:
    t = f"{title or ''} {summary or ''}".lower()

    # MLB hard block
    for bad in MLB_BLOCK:
        if bad in t:
            return False

    # trusted domains pass (still MLB-guarded above)
    if src_domain in TRUSTED_DOMAINS:
        return True

    # strong exact mention
    if "arizona cardinals" in t or "az cardinals" in t:
        return True

    # generic "cardinals" needs football context & NOT baseball
    if "cardinals" in t and not any(bad in t for bad in MLB_BLOCK):
        if any(tok in t for tok in NFL_REQUIRED_ANY):
            return True

    return False

# ---------- fetchers

def fetch_rss(url: str):
    return feedparser.parse(url)

def fetch_html_list(url: str):
    # very small safety net for team/league HTML pages that don’t serve RSS.
    # We try to scrape <a> titles; still filtered downstream.
    try:
        html_text = requests.get(url, timeout=15).text
    except Exception:
        return []

    links = []
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html_text, re.I|re.S):
        href = m.group(1)
        text = re.sub(r"<[^>]+>", "", m.group(2))
        if len(text.strip()) < 15:
            continue
        links.append({"link": urllib.parse.urljoin(url, href), "title": html.unescape(text)})
    return links[:40]

# ---------- main

def collect():
    seen_keys = set()
    items = []

    for feed in FEEDS:
        name = feed["name"]
        url  = feed["url"]
        trusted = feed.get("trusted", False)
        is_html = feed.get("is_html", False)

        try:
            if is_html:
                entries = fetch_html_list(url)
                parsed_entries = []
                for e in entries:
                    parsed_entries.append({
                        "title": e["title"],
                        "link": e["link"],
                        "summary": "",
                        "published_parsed": None,
                        "updated_parsed": None,
                        "source": name,
                    })
            else:
                parsed = fetch_rss(url)
                parsed_entries = []
                for e in parsed.entries:
                    parsed_entries.append({
                        "title": getattr(e, "title", ""),
                        "link": getattr(e, "link", ""),
                        "summary": getattr(e, "summary", "") or getattr(e, "description", ""),
                        "published_parsed": getattr(e, "published_parsed", None),
                        "updated_parsed": getattr(e, "updated_parsed", None),
                        "source": name,
                    })
        except Exception:
            continue

        for e in parsed_entries:
            title = re.sub(r"\s+", " ", (e["title"] or "").strip())
            link  = strip_tracking(e["link"] or "")
            if not title or not link:
                continue

            src_domain = domain_of(link)
            if not (trusted or allow_item(title, e.get("summary",""), src_domain)):
                continue

            key = hashlib.sha1((norm_title(title) + "|" + link).encode("utf-8")).hexdigest()
            if key in seen_keys:
                continue
            seen_keys.add(key)

            ts, iso = parse_when(e)
            items.append({
                "title": title,
                "link": link,
                "source": name if trusted else (src_domain or name),
                "published": ts,
                "published_iso": iso,
            })

    # sort newest first, cap
    items.sort(key=lambda x: x["published"], reverse=True)
    items = items[:MAX_ITEMS]

    sources = sorted({it["source"] for it in items})
    updated_iso = datetime.now(timezone.utc).isoformat()

    payload = {
        "team": "Arizona Cardinals",
        "updated_at": updated_iso,
        "items": items,
        "sources": sources,
        "links": STATIC_LINKS,
    }

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} with {len(items)} items and {len(sources)} sources at {updated_iso}")

if __name__ == "__main__":
    collect()
# collect.py — Arizona Cardinals
# - Browser UA so ESPN/Yahoo/Google return items
# - NFL-safe filter: allow Cardinals; block MLB phrases
# - Dedup by (normalized title + canonical link)
# - Keep newest 50; write sources list for dropdown

import json, re, time, hashlib, pathlib, urllib.parse
from datetime import datetime, timezone
import feedparser

from feeds import FEEDS, STATIC_LINKS

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "items.json"
MAX_ITEMS = 50

UA_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/123.0 Safari/537.36"
    )
}

def domain(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).netloc.lower().lstrip("www.")
    except Exception:
        return ""

def clean_url(u: str) -> str:
    try:
        p = urllib.parse.urlparse(u)
        q = urllib.parse.parse_qs(p.query)
        drop = {
            "utm_source","utm_medium","utm_campaign","utm_term","utm_content",
            "ito","iclid","fbclid","gclid","mc_cid","mc_eid"
        }
        q = {k:v for k,v in q.items() if k not in drop}
        p = p._replace(query=urllib.parse.urlencode(q, doseq=True), fragment="")
        return urllib.parse.urlunparse(p)
    except Exception:
        return u

def norm_title(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").strip()).lower()

def parse_ts(entry):
    if entry.get("published_parsed"):
        ts = int(time.mktime(entry["published_parsed"]))
    elif entry.get("updated_parsed"):
        ts = int(time.mktime(entry["updated_parsed"]))
    else:
        ts = int(time.time())
    return ts, datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

TRUSTED = {
    "azcardinals.com","espn.com","cardswire.usatoday.com","sports.yahoo.com",
    "revengeofthebirds.com","azcentral.com","bleacherreport.com","news.google.com"
}

MLB_BLOCK = {"st. louis cardinals","st louis cardinals","mlb","baseball","nl central"}

def allow_item(title: str, summary: str, src: str, trusted: bool) -> bool:
    t = f"{title or ''} {summary or ''}".lower()

    if any(x in t for x in MLB_BLOCK):
        return False

    if trusted or src in TRUSTED:
        return True

    if "arizona cardinals" in t or "az cardinals" in t:
        return True

    if "cardinals" in t:  # NFL generic
        return True

    for name in ("kyler murray","marvin harrison jr","james conner",
                 "trey mcbride","jonathan gannon","paris johnson"):
        if name in t:
            return True

    return False

def fetch(url: str):
    return feedparser.parse(url, request_headers=UA_HEADERS)

def collect():
    seen = set()
    items = []

    for feed in FEEDS:
        name = feed["name"]
        url = feed["url"]
        trusted = feed.get("trusted", False)

        try:
            parsed = fetch(url)
            entries = parsed.entries or []
        except Exception:
            entries = []

        for e in entries:
            title = re.sub(r"\s+", " ", (getattr(e, "title", "") or "").strip())
            link = clean_url(getattr(e, "link", "") or "")
            if not title or not link:
                continue

            src_dom = domain(link)
            summary = getattr(e, "summary", "") or getattr(e, "description", "")

            if not allow_item(title, summary, src_dom, trusted):
                continue

            key = hashlib.sha1((norm_title(title) + "|" + link).encode("utf-8")).hexdigest()
            if key in seen:
                continue
            seen.add(key)

            ts, iso = parse_ts({
                "published_parsed": getattr(e, "published_parsed", None),
                "updated_parsed": getattr(e, "updated_parsed", None),
            })

            items.append({
                "title": title,
                "link": link,
                "source": name if trusted else (src_dom or name),
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
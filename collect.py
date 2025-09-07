# collect.py — generic collector (Cardinals-tuned filters)
import json, re, time, hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse
import requests, feedparser

import feeds  # FEEDS + STATIC_LINKS

UA = "Mozilla/5.0 (compatible; CardinalsNewsBot/1.0; +https://github.com/)"
TIMEOUT = 20
MAX_ITEMS = 50

NFL_KEEP = [
    "arizona cardinals", "cards",
    "kyler murray", "james conner", "marvin harrison jr", "paris johnson",
    "budda baker", "jalen thompson", "zaven collins", "bj ojulari",
    "jonathan gannon", "monti ossenfort",
]

ANTI = [
    "st. louis cardinals", "st louis cardinals", "mlb", "baseball",
]

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip().lower()

def is_cardinals(text: str) -> bool:
    t = norm(text)
    if any(a in t for a in ANTI):
        return False
    if "cardinals" in t or "arizona" in t:
        # still avoid MLB by requiring an nfl hint if it's ambiguous
        if "cardinals" in t and "arizona" not in t:
            if not any(k in t for k in ["nfl","football","qb","wr","rb","coach","defense","offense","kyler","gannon"]):
                return False
        return True
    return any(k in t for k in NFL_KEEP)

def source_from(entry, feed_name):
    # try <source> tag then fall back to site host or feed name
    if "source" in entry and getattr(entry.source, "title", None):
        return entry.source.title
    href = entry.get("link") or ""
    host = urlparse(href).netloc.replace("www.", "")
    return host or feed_name

def canon_url(u: str) -> str:
    return (u or "").split("?")[0].rstrip("/")

def fetch_feed(url):
    headers = {"User-Agent": UA}
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        return feedparser.parse(resp.content)
    except Exception:
        return {"entries": []}

def main():
    items = []
    seen = set()
    for f in feeds.FEEDS:
        parsed = fetch_feed(f["url"])
        for e in parsed.get("entries", []):
            title = (e.get("title") or "").strip()
            if not title:
                continue
            summary = e.get("summary") or e.get("description") or ""
            blob = f"{title} {summary}"
            if not is_cardinals(blob):
                continue
            link = canon_url(e.get("link") or "")
            key = hashlib.sha1((norm(title) + "|" + link).encode()).hexdigest()
            if key in seen:
                continue
            seen.add(key)

            src = source_from(e, f["name"])
            # published
            ts = None
            for k in ("published_parsed","updated_parsed"):
                if e.get(k):
                    ts = int(time.mktime(e[k]))
                    break
            items.append({
                "title": title,
                "link": link,
                "source": src,
                "published": ts,
            })

    # sort newest first, keep only MAX_ITEMS
    items.sort(key=lambda x: x.get("published") or 0, reverse=True)
    items = items[:MAX_ITEMS]

    sources = sorted({it["source"] for it in items})
    out = {
        "team": "Arizona Cardinals",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "items": items,
        "sources": sources,
        "links": feeds.STATIC_LINKS,
    }

    with open("items.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    # print short summary for workflow logs
    print(f"Wrote items.json with {len(items)} items and {len(sources)} sources at {out['updated_at']}")

if __name__ == "__main__":
    main()
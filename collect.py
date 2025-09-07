import json, time, hashlib, pathlib
from datetime import datetime, timezone
from dateutil import parser as dtparse
import feedparser

from feeds import TEAM, SOURCES, MAX_ITEMS

OUT = pathlib.Path("items.json")

UA = "Mozilla/5.0 (NewsCollector; +https://github.com) feedparser"

def norm_ts(dtstr):
    if not dtstr:
        return None
    try:
        return int(dtparse.parse(dtstr).timestamp())
    except Exception:
        return None

def fetch_feed(title, url):
    d = feedparser.parse(url, request_headers={"User-Agent": UA})
    items = []
    for e in d.entries:
        link = getattr(e, "link", None)
        name = title
        if not link:
            continue
        published = getattr(e, "published", None) or getattr(e, "updated", None)
        ts = norm_ts(published) or int(time.time())
        items.append({
            "source": name,
            "title": getattr(e, "title", "(no title)"),
            "link": link,
            "published": published or "",
            "ts": ts,
        })
    return items

def main():
    all_items = []
    for title, url in SOURCES:
        try:
            all_items.extend(fetch_feed(title, url))
        except Exception:
            # survive bad feeds
            continue

    # Dedup by link, keep most recent
    seen = {}
    for it in all_items:
        k = it["link"]
        if k not in seen or it["ts"] > seen[k]["ts"]:
            seen[k] = it
    deduped = sorted(seen.values(), key=lambda x: x["ts"], reverse=True)[:MAX_ITEMS]

    payload = {
        "team": TEAM,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "sources": [s for s, _ in SOURCES],
        "items": deduped,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
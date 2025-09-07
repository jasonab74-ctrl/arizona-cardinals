import argparse, json, time, hashlib
from datetime import datetime, timezone
from urllib.parse import quote_plus
import feedparser
from dateutil import parser as dtp

CARDINALS_SOURCES = [
    # name, id, rss/atom url (or google news)
    ("azcardinals.com", "azcards", "https://www.azcardinals.com/rss/news"),
    ("Cards Wire (USA Today)", "cardswire", "https://cardswire.usatoday.com/feed/"),
    ("Revenge of the Birds (SB Nation)", "rotb", "https://www.revengeofthebirds.com/rss/index.xml"),
    ("ProFootballTalk — Cardinals", "pft", "https://profootballtalk.nbcsports.com/tag/arizona-cardinals/feed/"),
    ("ESPN — Cardinals", "espn", "https://www.espn.com/espn/rss/nfl/news?team=22"),  # team=22 = ARI
    ("Yahoo Sports — Cardinals", "yahoo", "https://sports.yahoo.com/nfl/teams/ari/rss/"),
    ("SI — All Cardinals", "si", "https://www.si.com/nfl/cardinals/.rss"),
    # catch-alls
    ("Google News — Arizona Cardinals", "gnews",
     "https://news.google.com/rss/search?q=" + quote_plus("Arizona Cardinals") + "&hl=en-US&gl=US&ceid=US:en"),
    ("Bing News — Arizona Cardinals", "bing",
     "https://www.bing.com/news/search?q=" + quote_plus("Arizona Cardinals") + "&format=rss"),
]

def _ts(entry):
    # try several fields for date
    for k in ("published", "updated", "created"):
        if k in entry:
            try: return dtp.parse(entry[k]).astimezone(timezone.utc).isoformat()
            except: pass
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", entry.published_parsed)
    return datetime.now(timezone.utc).isoformat()

def collect(limit):
    items = []
    for name, sid, url in CARDINALS_SOURCES:
        try:
            d = feedparser.parse(url)
            for e in d.entries[:100]:
                link = getattr(e, "link", None)
                title = getattr(e, "title", None)
                if not link or not title: continue
                items.append({
                    "id": hashlib.md5(link.encode("utf-8")).hexdigest(),
                    "title": title.strip(),
                    "link": link,
                    "published": _ts(e),
                    "source": name,
                    "source_id": sid
                })
        except Exception:
            continue

    # de-dupe by link hash, keep newest
    uniq = {}
    for it in items:
        key = it["id"]
        if key not in uniq or it["published"] > uniq[key]["published"]:
            uniq[key] = it
    flat = sorted(uniq.values(), key=lambda x: x["published"], reverse=True)[:limit]

    data = {
        "team": "arizona-cardinals",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "sources": [{"id": s[1], "name": s[0]} for s in CARDINALS_SOURCES],
        "items": flat
    }
    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--team", default="arizona-cardinals")  # for symmetry with other teams
    ap.add_argument("--limit", type=int, default=50)
    args = ap.parse_args()
    collect(args.limit)
import feedparser, json, time, pathlib
from feeds import FEEDS

MAX_ITEMS = 50
items = []

for feed in FEEDS:
    try:
        parsed = feedparser.parse(feed["url"])
        for entry in parsed.entries:
            items.append({
                "title": entry.get("title", "No title"),
                "link": entry.get("link", ""),
                "source": feed["name"],
                "published": entry.get("published", "")
            })
    except Exception as e:
        print(f"Error fetching {feed['url']}: {e}")

# sort by published if available
items = sorted(items, key=lambda x: x.get("published", ""), reverse=True)
items = items[:MAX_ITEMS]

data = {
    "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "items": items,
    "sources": [f["name"] for f in FEEDS]
}

pathlib.Path("items.json").write_text(json.dumps(data, indent=2))
print(f"Wrote {len(items)} items to items.json")
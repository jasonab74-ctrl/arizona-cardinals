import json, re, time, hashlib, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import feedparser, requests
from feeds import FEEDS

ROOT = Path(__file__).parent
OUT = ROOT / "items.json"
UA = "TeamNewsBot/1.0 (+github pages)"

def http_get(url):
    return requests.get(url, headers={"User-Agent": UA}, timeout=25)

def unwrap(url):
    try:
        p = urllib.parse.urlparse(url)
        q = urllib.parse.parse_qs(p.query)
        for k in ("url", "u"):
            if k in q and q[k]:
                return q[k][0]
    except Exception:
        pass
    return url

TRUSTED = {
    "cards wire (usa today)",
    "si — all cardinals",
    "revenge of the birds",
    "profootballtalk — cardinals",
    "yahoo sports — cardinals",
    "cbs sports — cardinals",
    "arizona sports — cardinals",
}

EXCLUDE = [r"\bmlb\b", r"\bbaseball\b"]
INCLUDE = [r"\barizona\s+cardinals\b", r"\bcardinals\b", r"\baz\b"]

def allow(title, summary, feed_name):
    text = f"{title} {summary}".lower()
    if any(re.search(p, text) for p in EXCLUDE):
        return False
    if feed_name.lower() in TRUSTED:
        return True
    return any(re.search(p, text, re.I) for p in INCLUDE)

def source_name(entry, fallback):
    try:
        s = entry.get("source") or {}
        if s.get("title"): return s["title"]
    except Exception:
        pass
    return fallback

def ts_of(entry):
    for k in ("published_parsed", "updated_parsed"):
        v = getattr(entry, k, None)
        if v:
            try: return time.mktime(v)
            except Exception: pass
    return time.time()

def collect():
    items, seen = [], set()
    for f in FEEDS:
        name, url = f["name"], f["url"]
        try:
            r = http_get(url); r.raise_for_status()
            parsed = feedparser.parse(r.content)
        except Exception:
            continue
        for e in parsed.entries:
            title = (e.get("title") or "").strip()
            link = unwrap((e.get("link") or "").strip())
            if not title or not link: continue
            if not allow(title, e.get("summary") or "", name): continue
            key = hashlib.md5((link + "||" + title.lower()).encode()).hexdigest()
            if key in seen: continue
            seen.add(key)
            items.append({
                "title": title,
                "url": link,
                "source": source_name(e, name),
                "ts": ts_of(e)
            })
    items.sort(key=lambda x: x["ts"], reverse=True)
    items = items[:50]
    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "items": items,
        "sources": sorted({it["source"] for it in items})
    }
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")

if __name__ == "__main__":
    collect()
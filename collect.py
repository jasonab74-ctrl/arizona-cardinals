import json, re, time, hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
import requests, feedparser

from feeds import FEEDS

TEAM_WORDS = [
    r"\bcardinals\b", r"\barizona\b", r"\bari\b",
]
EXCLUDE_WORDS = [
    # obvious non-NFL/other sports
    r"\bst\.?\s?louis\b", r"\bbaseball\b", r"\bmlb\b", r"\bdiamondbacks\b", r"\bnba\b", r"\bsuns\b",
    r"\bncaa\b", r"\bcollege\b", r"\bhockey\b", r"\bcoyotes\b", r"\bmls\b", r"\bsoccer\b",
]

MAX_ITEMS = 50
TIMEOUT = 15

def clean_url(u: str) -> str:
    if not u: return u
    try:
        p = urlparse(u)
        q = parse_qs(p.query)
        # unwrap common redirect chains
        for key in ("url", "u", "r"):
            if key in q and q[key]:
                u = q[key][0]
                p = urlparse(u)
                q = parse_qs(p.query)
        # strip trackers
        filtered = {k:v for k,v in q.items() if not k.lower().startswith("utm")}
        p = p._replace(query=urlencode({k:v[0] if isinstance(v, list) else v for k,v in filtered.items()}))
        return urlunparse(p)
    except Exception:
        return u

def norm_title(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").strip().lower())

def looks_like_cardinals(text: str) -> bool:
    if not text: return False
    t = text.lower()
    if any(re.search(w, t) for w in EXCLUDE_WORDS):
        return False
    score = 0
    for w in TEAM_WORDS:
        if re.search(w, t): score += 1
    return score >= 1

def is_trusted(feed_name: str) -> bool:
    for f in FEEDS:
        if f["name"] == feed_name:
            return bool(f.get("trusted"))
    return False

def source_from(entry, fallback_feed_name: str) -> str:
    for key in ("source", "author", "publisher"):
        v = entry.get(key)
        if isinstance(v, dict):
            if v.get("title"): return v["title"]
        if isinstance(v, str) and v.strip():
            return v.strip()
    # try domain from link
    try:
        host = urlparse(entry.get("link","")).hostname or ""
        if host:
            return host.replace("www.","")
    except Exception:
        pass
    return fallback_feed_name

def fetch_feed(feed):
    url = feed["url"]
    r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent":"Mozilla/5.0 (NewsBot)"})
    r.raise_for_status()
    return feedparser.parse(r.content)

def allow_item(entry, feed_name: str, trusted: bool) -> bool:
    title = entry.get("title","")
    link = entry.get("link","")
    src = source_from(entry, feed_name)
    text_blob = " ".join([title, src, link])
    if trusted:
        return looks_like_cardinals(text_blob) or looks_like_cardinals(title)
    else:
        # For untrusted, require a stronger match in title or source
        return looks_like_cardinals(title) or (looks_like_cardinals(src) and looks_like_cardinals(title))

def to_epoch(dt_struct, fallback_now):
    try:
        if dt_struct:
            return int(time.mktime(dt_struct))
    except Exception:
        pass
    return int(fallback_now)

def main():
    now = time.time()
    items = []
    seen = set()
    sources_set = set()

    for f in FEEDS:
        try:
            parsed = fetch_feed(f)
        except Exception:
            continue
        for e in parsed.entries:
            link = clean_url(e.get("link",""))
            title = (e.get("title") or "").strip()
            if not link or not title:
                continue
            src = source_from(e, f["name"])
            trusted = bool(f.get("trusted"))
            if not allow_item(e, f["name"], trusted):
                continue

            key = hashlib.sha1((link + "||" + norm_title(title)).encode("utf-8")).hexdigest()
            if key in seen: 
                continue
            seen.add(key)

            ts = to_epoch(getattr(e, "published_parsed", None), now)
            item = {
                "title": title,
                "link": link,
                "source": src,
                "published": ts
            }
            items.append(item)
            sources_set.add(src)

    # sort + cap
    items.sort(key=lambda x: x["published"], reverse=True)
    items = items[:MAX_ITEMS]

    data = {
        "team": "Arizona Cardinals",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "items": items,
        "sources": sorted(list(sources_set)),
    }
    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()

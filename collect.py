# Cardinals collector — mirrors the working Eagles/Colts shape
# - Real UA so ESPN/Yahoo/Google return items
# - MLB guard, otherwise permissive for "Cardinals"
# - Dedupe, newest 50, writes sources + links exactly as index expects

import json, re, time, hashlib, pathlib, urllib.parse
from datetime import datetime, timezone
import feedparser

from feeds import FEEDS, STATIC_LINKS

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "items.json"
MAX_ITEMS = 50

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36"}

def domain(url: str) -> str:
    try: return urllib.parse.urlparse(url).netloc.lower().lstrip("www.")
    except Exception: return ""

def clean_url(u: str) -> str:
    try:
        p = urllib.parse.urlparse(u)
        keep = {k:v for k,v in urllib.parse.parse_qs(p.query).items()
                if not k.lower().startswith("utm") and k.lower() not in {"fbclid","gclid","mc_cid","mc_eid"}}
        p = p._replace(query=urllib.parse.urlencode(keep, doseq=True), fragment="")
        return urllib.parse.urlunparse(p)
    except Exception:
        return u

def norm_title(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").strip()).lower()

def ts_from(entry) -> int:
    for k in ("published_parsed","updated_parsed"):
        v = entry.get(k)
        if v:
            try: return int(time.mktime(v))
            except Exception: pass
    return int(time.time())

MLB_BLOCK = {"st. louis cardinals","st louis cardinals","mlb","baseball","nl central"}
TRUST = {"azcardinals.com","espn.com","sports.yahoo.com","cardswire.usatoday.com","revengeofthebirds.com","azcentral.com","bleacherreport.com","news.google.com"}

def allow(title: str, summary: str, src: str, trusted: bool) -> bool:
    t = f"{title or ''} {summary or ''}".lower()
    if any(b in t for b in MLB_BLOCK): return False
    if trusted or src in TRUST: return True
    if "arizona cardinals" in t or "az cardinals" in t: return True
    if "cardinals" in t: return True
    for name in ("kyler murray","marvin harrison jr","trey mcbride","james conner","jonathan gannon","paris johnson"):
        if name in t: return True
    return False

def parse_feed(url: str):
    return feedparser.parse(url, request_headers=UA)

def main():
    items, seen = [], set()

    for feed in FEEDS:
        name, url = feed["name"], feed["url"]
        trusted = bool(feed.get("trusted"))
        try:
            parsed = parse_feed(url)
            entries = parsed.entries or []
        except Exception:
            entries = []

        for e in entries:
            title = re.sub(r"\s+", " ", (getattr(e,"title","") or "").strip())
            link  = clean_url(getattr(e,"link","") or "")
            if not title or not link: 
                continue

            src_dom = domain(link)
            summary = getattr(e,"summary","") or getattr(e,"description","")

            if not allow(title, summary, src_dom, trusted):
                continue

            key = hashlib.sha1((norm_title(title) + "|" + link).encode("utf-8")).hexdigest()
            if key in seen: 
                continue
            seen.add(key)

            ts = ts_from({
                "published_parsed": getattr(e, "published_parsed", None),
                "updated_parsed": getattr(e, "updated_parsed", None),
            })

            items.append({
                "title": title,
                "link": link,
                "source": name if trusted else (src_dom or name),
                "published": ts
            })

    items.sort(key=lambda x: x["published"], reverse=True)
    items = items[:MAX_ITEMS]

    data = {
        "team": "Arizona Cardinals",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "items": items,
        "sources": sorted({it["source"] for it in items}),
        "links": STATIC_LINKS
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"items: {len(items)}  sources: {len(data['sources'])}  updated: {data['updated_at']}")

if __name__ == "__main__":
    main()
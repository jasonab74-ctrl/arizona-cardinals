# collect.py — Arizona Cardinals (NFL) collector
# Widely permissive, MLB-safe, deduped, 50 newest, writes items.json

import json, re, time, hashlib, html, pathlib, urllib.parse
from datetime import datetime, timezone
import feedparser
import requests

from feeds import FEEDS, STATIC_LINKS

ROOT = pathlib.Path(__file__).parent
OUT  = ROOT / "items.json"
MAX_ITEMS = 50

# ---------- helpers

def domain_of(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).netloc.lower().lstrip("www.")
    except Exception:
        return ""

def strip_tracking(u: str) -> str:
    try:
        p = urllib.parse.urlparse(u)
        q = urllib.parse.parse_qs(p.query)
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
    ts = None
    if entry.get("published_parsed"):
        ts = int(time.mktime(entry["published_parsed"]))
    elif entry.get("updated_parsed"):
        ts = int(time.mktime(entry["updated_parsed"]))
    else:
        ts = int(time.time())
    return ts, datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

# ---------- filter (very forgiving but MLB-safe)

TRUST = {
    "azcardinals.com","nfl.com","espn.com","sports.yahoo.com","cardswire.usatoday.com",
    "revengeofthebirds.com","azcentral.com","bleacherreport.com","news.google.com"
}

MLB_BLOCK = {"st. louis cardinals","st louis cardinals","mlb","baseball"}

def allow_item(title: str, summary: str, src_domain: str) -> bool:
    t = f"{title or ''} {summary or ''}".lower()

    # hard MLB guard
    if any(b in t for b in MLB_BLOCK):
        return False

    # trusted football-ish sources always pass
    if src_domain in TRUST:
        return True

    # explicit team mention
    if "arizona cardinals" in t or "az cardinals" in t:
        return True

    # generic "cardinals" allowed if no MLB hints
    if "cardinals" in t:
        return True

    # headlines like “Kyler Murray …” should pass
    for name in ("kyler murray","james conner","marvin harrison jr","trey mcbride",
                 "jonathan gannon","paris johnson"):
        if name in t:
            return True

    return False

# ---------- fetchers

def fetch_rss(url: str):
    return feedparser.parse(url)

def fetch_html_list(url: str):
    # lightweight HTML fallback (league/team pages without RSS)
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        html_text = resp.text
    except Exception:
        return []

    links = []
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html_text, re.I|re.S):
        href = urllib.parse.urljoin(url, m.group(1))
        text = re.sub(r"<[^>]+>", "", m.group(2))
        text = html.unescape(text).strip()
        if len(text) < 20:
            continue
        links.append({"link": href, "title": text})
        if len(links) >= 40:
            break
    return links

# ---------- main

def collect():
    seen = set()
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
            if key in seen:
                continue
            seen.add(key)

            ts, iso = parse_when(e)
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
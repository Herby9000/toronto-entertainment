#!/usr/bin/env python3
"""Build a curated, validated six-month Toronto listing from public pages.

Every network source is best-effort. A refresh is written atomically only when the
result still passes the same diversity/horizon gates as CI; otherwise the previous
known-good file remains untouched.
"""
import json, re, sys, urllib.request
from datetime import datetime, date, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parents[1]
OUT = ROOT / "data/events.json"
UA = {"User-Agent": "AfterDarkToronto/2.0 (+https://github.com/Herby9000/toronto-entertainment)"}
HORIZON_DAYS = 183

# Deliberately excludes the hundreds of bars and very small rooms in the metro feed.
MAJOR_MUSIC_VENUES = (
    "RBC Amphitheatre", "Scotiabank Arena", "Rogers Stadium", "Massey Hall",
    "Roy Thomson Hall", "Meridian Hall", "History", "Danforth Music Hall",
    "Queen Elizabeth Theatre", "Coca-Cola Coliseum", "Budweiser Stage",
    "The Theatre at Great Canadian Resort", "Elgin & Winter Garden",
    "Koerner Hall", "Phoenix Concert Theatre", "Opera House",
)
COMEDY_NAMES = (
    "Josh Johnson (Comedian)", "Jarlath Regan", "Alex Edelman", "Jinkx Monsoon",
)
LIVE_NAMES = (
    "The Ones", "The Wiggles", "Raffi", "Disney Worlds Collide", "Disney @",
    "Tafari Anthony", "Jinkx Monsoon", "Afrikaans is Lekker",
)

def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=35).read().decode("utf8", "ignore")

def ld_events(html):
    for raw in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S | re.I):
        try:
            docs = json.loads(raw)
        except (ValueError, TypeError):
            continue
        for item in docs if isinstance(docs, list) else [docs]:
            if isinstance(item, dict) and item.get("startDate") and item.get("location"):
                yield item

def songkick():
    """Follow Toronto calendar pagination until reaching the six-month boundary."""
    out, seen_urls = [], set()
    cutoff = date.today() + timedelta(days=HORIZON_DAYS)
    for page in range(1, 31):
        url = f"https://www.songkick.com/metro-areas/27396-canada-toronto?page={page}"
        items = list(ld_events(get(url)))
        if not items:
            break
        page_dates = []
        for item in items:
            try:
                day = date.fromisoformat(item["startDate"][:10])
            except ValueError:
                continue
            page_dates.append(day)
            title = re.sub(r"\s+@.*$", "", item.get("name", "")).strip()
            venue = item.get("location", {}).get("name", "Toronto")
            source = item.get("url")
            if not title or not source or source in seen_urls:
                continue
            seen_urls.add(source)
            full_name = item.get("name", title)
            if any(name.lower() in full_name.lower() for name in COMEDY_NAMES):
                category, audience = "Comedy", "date"
                desc = f"{title}, live in Toronto. Confirm performance time and tickets at the linked listing."
            elif any(name.lower() in full_name.lower() for name in LIVE_NAMES):
                category, audience = "Live Events", "family" if any(x in full_name.lower() for x in ("wiggles", "raffi", "disney")) else "all"
                desc = f"{title}, a live Toronto performance. Confirm show time, age guidance and tickets at the source."
            elif any(v.lower() in venue.lower() for v in MAJOR_MUSIC_VENUES):
                category, audience = "Music", "all"
                desc = f"{title} live at {venue}. Confirm doors, age restrictions and tickets at the source."
            else:
                continue
            out.append({"title": title, "date": day.isoformat(), "venue": venue,
                        "description": desc, "url": source, "category": category,
                        "audience": audience, "source": "Songkick Toronto calendar"})
        if page_dates and max(page_dates) >= cutoff:
            break
    return out

def valid(events):
    lo, hi = date.today(), date.today() + timedelta(days=HORIZON_DAYS)
    required = {"title", "date", "venue", "description", "url", "category", "audience", "source"}
    seen, good = set(), []
    for event in events:
        try:
            day = date.fromisoformat(event["date"])
        except (ValueError, KeyError, TypeError):
            continue
        # URL is the event identity: distinct same-day performances remain useful.
        key = event.get("url")
        if (required <= event.keys() and lo <= day <= hi and
                event["category"] in {"Music", "Comedy", "Live Events"} and
                str(key).startswith("https://") and key not in seen):
            seen.add(key); good.append(event)
    return sorted(good, key=lambda x: (x["date"], x["title"], x["url"]))

def acceptable(events):
    counts = {c: sum(e["category"] == c for e in events) for c in ("Music", "Comedy", "Live Events")}
    span = (max(date.fromisoformat(e["date"]) for e in events) - date.today()).days if events else 0
    return len(events) >= 50 and counts["Music"] >= 25 and counts["Comedy"] >= 5 and counts["Live Events"] >= 15 and span >= 120, counts, span

def main():
    old = json.loads(OUT.read_text()) if OUT.exists() else {"events": []}
    errors, fresh = [], []
    try:
        fresh = songkick()
        if not fresh: errors.append("Songkick: no parseable events")
    except Exception as exc:
        errors.append(f"Songkick: {exc}")
    # Merge unexpired known-good records: protects individual future events if a
    # paginated source has a transient partial response.
    merged = valid(fresh + old.get("events", []))
    ok, counts, span = acceptable(merged)
    if not ok:
        print(f"Refusing update: quality gate failed (counts={counts}, horizon={span} days)", file=sys.stderr)
        return 1
    payload = {"updated": datetime.now(timezone.utc).isoformat(), "events": merged,
               "source_status": errors or ["Songkick Toronto pagination responded; curated major venues and performances"]}
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    json.loads(tmp.read_text()); tmp.replace(OUT)
    print(f"Wrote {len(merged)} events; counts={counts}; horizon={span} days")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

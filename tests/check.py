#!/usr/bin/env python3
import json, re, sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

root = Path(__file__).parents[1]
errors = []
for name in ("index.html", "style.css", "app.js", "data/events.json", "LICENSE", "README.md"):
    if not (root / name).exists(): errors.append("missing " + name)
try:
    doc = json.loads((root / "data/events.json").read_text())
    events = doc["events"]
    required = {"title", "date", "venue", "description", "url", "category", "audience", "source"}
    seen = set(); hi = date.today() + timedelta(days=183)
    for i, event in enumerate(events):
        if not required <= event.keys(): errors.append(f"event {i} missing fields"); continue
        day = date.fromisoformat(event["date"])
        if not date.today() <= day <= hi: errors.append(f"event {i} out of range")
        if event["url"] in seen: errors.append(f"event {i} duplicate source URL")
        seen.add(event["url"])
        if not re.match(r"https://", event["url"]): errors.append(f"event {i} insecure source")
    counts = Counter(e["category"] for e in events)
    for category, minimum in {"Music": 25, "Comedy": 5, "Live Events": 15}.items():
        if counts[category] < minimum: errors.append(f"{category} has {counts[category]}, needs {minimum}")
    horizon = (max(date.fromisoformat(e["date"]) for e in events) - date.today()).days
    if horizon < 120: errors.append(f"calendar horizon is only {horizon} days")
except Exception as exc:
    errors.append(str(exc))
if errors:
    print("\n".join("FAIL " + error for error in errors)); sys.exit(1)
print(f"PASS: {len(events)} unique sourced events; counts={dict(counts)}; horizon={horizon} days")

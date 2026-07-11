# After Dark Toronto

A fast, iPhone-friendly six-month guide to Toronto music, comedy and interesting live events. Published at **https://herby9000.github.io/toronto-entertainment/**.

## Data and cadence

A GitHub Action runs Tuesdays at 11:17 UTC and can also be run manually (`workflow_dispatch`). `scripts/update.py` currently reads public structured event data from [Songkick's Toronto calendar](https://www.songkick.com/metro-areas/27396-canada-toronto) and official exhibition cards from the [Royal Ontario Museum](https://www.rom.on.ca/whats-on). Every card links to its source; ticket availability and details should always be confirmed there.

No API keys or paid services are used. The updater limits dates to today–183 days, validates required fields, deduplicates, writes atomically, and merges last-known-good future events if a source fails. It refuses to replace the file with an empty result. Source status is recorded in JSON.

### Limitations

Public calendars change markup and some major venues block automation. Songkick coverage is broad but not exhaustive; comedy is deliberately sparse until a stable, verifiable public feed is available. A blank tab is preferable to invented or stale listings. ROM exhibitions use the current date as the visit date and include their on-view end date in the description.

## Add a source

Add a function in `scripts/update.py` that returns the documented event shape, register it in `main()`, then run:

```sh
python3 scripts/update.py
python3 tests/check.py
```

Use official/public pages, set a descriptive audience value (`all`, `date`, `family`), and never bypass authentication or robots controls.

## Local use

Serve the repository with `python3 -m http.server 8000`; no build step or dependencies. MIT licensed.

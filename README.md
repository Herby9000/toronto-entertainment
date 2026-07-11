# After Dark Toronto

A fast, iPhone-friendly six-month guide to Toronto music, comedy and interesting live events. Published at **https://herby9000.github.io/toronto-entertainment/**.

## Data and cadence

A GitHub Action runs Tuesdays at 11:17 UTC and can also be run manually (`workflow_dispatch`). `scripts/update.py` follows every page of [Songkick's public Toronto calendar](https://www.songkick.com/metro-areas/27396-canada-toronto) needed to cover the six-month window. It selects major Toronto venues rather than publishing the feed's hundreds of tiny-room listings, and identifies verified comedy and family/stage performances from those same dated event records. Every card links to the individual public source page; ticket availability and details should always be confirmed there.

No API keys or paid services are used. The updater limits dates to today–183 days, validates required fields, deduplicates by source URL, writes atomically, and merges unexpired last-known-good events if a paginated request is temporarily incomplete. Before replacing the file it enforces minimum category counts (25 Music, 5 Comedy, 15 Live Events) and a horizon of at least 120 days. CI independently enforces those gates.

### Limitations

Public calendars change markup and some official venue sites block automation. Songkick's public structured records are used as the stable common index, while the linked event pages remain the place to confirm times, cancellations, age rules, and tickets. Comedy is intentionally limited to performances that can be classified confidently; events are never inferred or assigned artificial dates.

## Add a source

Add a function in `scripts/update.py` that returns the documented event shape, register it in `main()`, then run:

```sh
python3 scripts/update.py
python3 tests/check.py
```

Use official/public pages, set a descriptive audience value (`all`, `date`, `family`), and never bypass authentication or robots controls.

## Local use

Serve the repository with `python3 -m http.server 8000`; no build step or dependencies. MIT licensed.

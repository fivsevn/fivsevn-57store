---
id: 57store-readme
title: fivsevn-57store

module: 57store
submodule: 57store
topic: null

type: index
status: active
canonical: true

summary: null

parents: []
related: []

tags: []

audience:
- self
- internal
languages:
- en

maturity: evolving
confidence: null

visibility: public
source_of_truth: site

filename_policy: entrypoint

created: null
updated: '2026-11-01'
metadata_updated: '2026-11-01'
---
# 57store

[System map](https://github.com/fivsevn-agy/fivsevn-devlog/blob/main/system-map.md)

Source for [57store.fivsevn.com](https://57store.fivsevn.com/), a narrative extension of [fivsevn.com](https://fivsevn.com/). A deterministic Python build preserves the receipt, terminal, camera-monitor and conversation layouts while keeping content in editable source files. The site deploys to GitHub Pages.

## Pages and source

| Public route | Editable source | Purpose |
|---|---|---|
| `/` | `templates/home.html` | Night-store receipt and navigation |
| `/fragment/` | `fragment/page.html` | Independent image page |
| `/cache/` | `cache/page.html`, `cache/posts.json` | Continuous conversation with an inline access prompt |
| `/sys/` | `sys/YYYY/MM/<id>/index.md` | Terminal log; newest first |
| `/cctv/` | `cctv/YYYY/MM/<id>/index.md` | YouTube camera feed; newest first |
| `/toilet/` | `toilet/` | Existing interactive room |
| `/pi5/57store/system/static/` | `pi5/57store/system/static/`, sibling `data/` | Existing terminal prototype |

Receipt layout and labels are editable in `templates/home.html`. Two counters are calculated during every build: **STORE REVISIONS** counts all commits reachable from the checked-out Git revision, including automated publication commits; **RECEIPTS ISSUED** counts published, public SYS and CCTV entries. Cache messages, drafts and hidden entries are excluded. Statistics are generated only in the build output and require a complete Git checkout (`git fetch --unshallow` for a shallow clone). The existing push and scheduled deployments refresh both values without a visitor-tracking service.

CCTV artwork, the signed shortcut, boot capsule, room assets and Raspberry Pi application remain available for their existing uses. The website homepage is built from `templates/home.html`. The static Pi prototype retains its seeded fallbacks; its Flask `/api/` services still require the separate Pi application.

## Publish and edit

- [SYS guide](sys/README.md): edit `sys/trigger.md`, commit and push. Each committed nonempty body revision becomes one log.
- [CCTV guide](cctv/README.md): public uploads on the configured store channel are discovered automatically. The current channel is `UCenBP2oAYYiateiwPtcAuHw`, `@57store.fivsevn`.
- [Fragment guide](fragment/README.md) and [Cache guide](cache/README.md): edit the independent page sources directly.

SYS saves the exact upload commit instant in Asia/Shanghai. A durable `.publishing/sys.json` ledger tracks source commits and package identities; retries preserve later title, body and visibility edits. Merge commits do not duplicate uploads already introduced by their parents. Empty bodies, deletions and configuration-only changes do not create logs.

CCTV follows the channel's complete public uploads playlist, including continuation pages, and verifies exact publication instants. Each video ID appears once; time and ordering come from YouTube. Future discovery checks all saved records, including hidden ones, so hiding a room cannot cause it to be imported again. A saved room's edited title and notes are independent of later discovery. Video files are played through YouTube embeds. SYS and CCTV share `templates/terminal-header.html` and `site-assets/terminal.css`, preserving the original compact WordPress interior and centered frame. Pagination follows Fieldlog's compact numbers and « / » arrows inside the frame; arrows move to the immediately previous or next page.

Saved SYS/CCTV posts use the shared [site-post profile](https://github.com/fivsevn-agy/fivsevn-spec/blob/main/content/spec-content-site-post-001.md): `module: 57store`, `submodule: sys` or `cctv`, precise `extra.published_at`, and `extra.video_ids` for CCTV. Publication requires both `visibility: public` and a published status. These controls exclude records from website output; the source repository itself is public.

Publication images follow the [media naming contract](https://github.com/fivsevn-agy/fivsevn-spec/blob/main/content/spec-content-media-naming-001.md). Reused icons, artwork and fonts retain their names under `site-assets/`. Package IDs and image numbers remain stable when titles or display order change.

## Build and deployment

`Build and deploy 57store` handles main-branch pushes, scheduled CCTV discovery at minutes 7, 22, 37 and 52, and manual runs. Manual `sync_youtube` requests immediate discovery; an ordinary manual run rebuilds saved content. `Check 57store` validates pull requests and other branches.

The workflow checks local helper/schema copies against spec, runs behavioral tests, imports new SYS entries, optionally synchronizes CCTV, validates both post profiles, builds a clean `_site/`, checks local links and retained content, and saves generated packages without overwriting concurrent edits. If saving or rebasing changes the committed revision, it rebuilds and verifies the final statistics before deploying through Pages. Public bytes are then verified against `build-receipt.json`.

GitHub Pages uses Actions as its publishing source. `CNAME` specifies `57store.fivsevn.com`; DNS points at GitHub Pages. The verified YouTube channel is stored in `site-data/cctv.json`; an optional `YOUTUBE_57STORE_CHANNEL_ID` secret must match it. Publishing does not require WordPress credentials.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
node --test tests/test_cache_reveal.mjs
python scripts/site_post_metadata.py check --site sys --root sys --schema-dir schemas
python scripts/site_post_metadata.py check --site cctv --root cctv --schema-dir schemas
python scripts/build.py
python scripts/check.py
python -m http.server 8000 --directory _site
```

Use the same `--base-path /fivsevn-57store` on build and check for a project-path preview. Build and content validation work offline. `scripts/sync_cctv.py` and `scripts/verify_live.py --url https://57store.fivsevn.com` access the public services.

| Directory | Responsibility |
|---|---|
| `templates/`, `site-assets/` | Layout, styles, fonts and shared images |
| `site-data/` | Channel configuration, retained content identities and asset checksums |
| `sys/`, `cctv/` | Publishing guides and dated content packages |
| `fragment/`, `cache/` | Independent page sources |
| `.publishing/` | Durable SYS event ledger |
| `scripts/`, `schemas/`, `tests/` | Import, synchronization, build and verification |
| `_site/` | Disposable build artifact; never edit or commit |

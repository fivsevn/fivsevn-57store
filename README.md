---
id: 57store-readme
title: fivsevn-57store

module: system
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

# fivsevn-57store

Sources and static assets for the 57store site, its system-log publishing input, and its YouTube-to-WordPress automation. This repository is separate from Roll's personal photography and Motion channel.

## Source layout

- `toilet/`: static room page and its local images.
- `cctv/`: CCTV artwork source.
- `sys/trigger.md`: system-log publishing input; the signed shortcut and boot capsule support this flow.
- `scripts/`: publishers for the system trigger and the 57store YouTube channel.
- `.github/workflows/`: the corresponding Actions workflows.

`publish-57storesys-trigger.yml` processes changes to the system-log trigger. `publish-57store-youtube-posts.yml` checks the configured store channel at minutes 7, 22, 37 and 52, and supports manual runs. These workflows publish to their configured WordPress target using Actions Secrets. They are independent of the GitHub Pages static content and remain active.

Publishing credentials are supplied through `WP_BASE_URL`, `WP_USERNAME` and `WP_APP_PASSWORD`; the video publisher additionally uses `YOUTUBE_57STORE_CHANNEL_ID`. Never put those values in source files. Existing publisher scripts determine payload, category, and duplicate handling.

Edit static pages and assets directly in their own directories. For routine system-log publication, use the [system trigger guide](sys/README.md). Preserve the signed shortcut and authored artwork unless deliberately replacing them.

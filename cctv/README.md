---
id: 57store-cctv-readme
title: CCTV 发布

module: 57store
submodule: cctv
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
- zh

maturity: evolving
confidence: null

visibility: public
source_of_truth: site

filename_policy: entrypoint

created: null
updated: '2026-11-01'
metadata_updated: '2026-11-01'
---
# CCTV

在 [@57store.fivsevn](https://www.youtube.com/@57store.fivsevn) 发布公开视频，系统会自动同步。每个视频保存一条，日期和排列顺序以 YouTube 的实际发布时间为准。

需要立即同步时，在 Actions 打开 **Build and deploy 57store → Run workflow**，勾选 `sync_youtube`。

编辑 `cctv/年/月/发布包/index.md` 可改标题、备注和显示状态。设 `status: hidden` 或 `visibility: private` 可从页面隐藏；保留发布包，之后同步不会重新建一条。不要改 `id`、`extra.video_ids` 和 `extra.published_at`。

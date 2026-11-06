---
id: 57store-cache-readme
title: Cache 页面

module: 57store
submodule: cache
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
# Cache

对话内容在 `posts.json`，按时间从早到晚连续显示。每条包含 `id`、标题、时间和 `body_html`；保留既有身份和顺序，正文可使用 HTML。

页面框架在 `page.html`，评论样式在 `cache/card.html`。修改后提交并推送到 `main`，等待 **Build and deploy 57store** 成功。页面地址为 [cache](https://57store.fivsevn.com/cache/)。

最后一条是输入后展开的网址。输入任意内容并点击发送（或按 Enter）即可显示 `fivsevn.com`；在 `posts.json` 中修改它的正文，保留 `reveal: true`。

---
id: 57store-sys-readme
title: SYS 发布

module: 57store
submodule: sys
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
# SYS

1. 编辑 `sys/trigger.md` 第二个 `---` 后面的正文，保留需要显示的换行；支持 Markdown。
2. 提交并推送到 `main`。每次正文修改保存为一条记录，时间取这次提交的时间。
3. 等待 **Build and deploy 57store** 成功，打开 [SYS](https://57store.fivsevn.com/sys/)。

默认标题为 `[YYYY-MM-DD HH:MM]`。可在触发文件中设置 `title`、`status: draft` 或 `visibility: private`；只修改这些设置不会新建记录。

修改已经保存的内容，直接编辑 `sys/年/月/发布包/index.md`；改正文、标题或状态后提交即可。不要改 `id`、`extra.published_at`，也不要清空 `.publishing/sys.json`。快捷指令仍使用同一个触发文件。

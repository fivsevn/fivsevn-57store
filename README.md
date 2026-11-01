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

# 57store

[57store.fivsevn.com](https://57store.fivsevn.com/)：便利店小票、终端记录、监控视频和独立页面，由 GitHub Pages 发布。

| 内容 | 修改位置 |
|---|---|
| 首页小票 | `templates/home.html` |
| [SYS](https://57store.fivsevn.com/sys/) | 新记录写 `sys/trigger.md`；旧记录改 `sys/年/月/编号/index.md` |
| [CCTV](https://57store.fivsevn.com/cctv/) | 自动同步 [@57store.fivsevn](https://www.youtube.com/@57store.fivsevn) 的公开视频；标题、备注及状态在发布包中修改 |
| [Fragment](https://57store.fivsevn.com/fragment/) | `fragment/page.html` |
| [Cache](https://57store.fivsevn.com/cache/) | `cache/posts.json`、`cache/page.html` |
| 互动房间与 Pi 终端 | `toilet/`、`pi5/57store/` |

提交到 `main` 后，**Build and deploy 57store** 检查、构建并发布。CCTV 每 15 分钟同步一次；立即同步可手动运行 Actions 并勾选 `sync_youtube`。其他分支和 PR 由 **Check 57store** 校验。

编辑已有发布包时保留 `id`、`extra.published_at` 和视频身份；隐藏使用 `status: hidden`。`.publishing/sys.json` 是导入状态，`site-data/` 是配置及内容校验清单，`cache/` 是正式对话内容。`_site/` 为临时构建输出。

日常操作见 [SYS](sys/README.md)、[CCTV](cctv/README.md)、[Fragment](fragment/README.md)、[Cache](cache/README.md)。共享字段和媒体命名见 [fivsevn-spec](https://github.com/fivsevn-agy/fivsevn-spec)。

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
node --test tests/test_cache_reveal.mjs
python scripts/build.py
python scripts/check.py
```

本地构建需要完整 Git 历史；浅克隆先运行 `git fetch --unshallow`。静态 Pi 页面随站点发布，Flask `/api/` 服务仍在 Pi 应用中运行。

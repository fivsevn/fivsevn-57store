# 57STORE Pi5 文件与备份清单

检查时间：2026-09-05 08:11–08:14（Asia/Shanghai）。通过 SSH 实查 Raspberry Pi 5 Model B Rev 1.1，用户 `fivsevn`，主机 `57store`。根目录位于 SD 卡 `/dev/mmcblk0p2`（ext4），启动分区为 `/dev/mmcblk0p1`。

本次未执行安装、修改配置、停止服务、重启或上传 GitHub。网页访问会由现有程序照常产生访问日志；状态 API 会自行更新 `status.json`。

## 1. 正在运行的程序：应备份到 GitHub

下表目标相对于 `fivsevn-57store/pi5/`。

| Pi5 实际路径 | 用途 | 建议 GitHub 路径 |
| --- | --- | --- |
| `/opt/57store-mirror/app.py` | Python Web 服务、API、SQLite 存取、状态采集 | `app.py` |
| `/opt/57store-mirror/static/index.html` | 网页入口；对应 `/` 和 `/index.html` | `static/index.html` |
| `/opt/57store-mirror/static/style.css` | 当前黑白 DOS/CRT 视觉 | `static/style.css` |
| `/opt/57store-mirror/static/app.js` | 每 5 秒读取状态和事件并更新页面 | `static/app.js` |
| `/etc/systemd/system/57store-mirror.service` | 当前有效后台服务配置 | `systemd/57store-mirror.service` |
| `/usr/local/bin/57store-event` | 命令行写入事件的包装脚本 | `bin/57store-event` |
| `/home/fivsevn/57store-mirror/install.sh` | 安装、创建数据配置、注册并重启服务 | `install.sh` |
| `/home/fivsevn/57store-mirror/tests/test_app.py` | 原有功能测试 | `tests/test_app.py` |

`/opt/57store-mirror/` 当前只有上述 Python 文件和三个前端文件，没有独立图片、字体、assets 子目录。当前 CSS 没有外部 `url()`、`@import` 或 `@font-face` 引用。后端只开放列明的静态文件路由；以后增加图片时，还要相应扩展后端路由和安装脚本。

**不要直接拿 `/home/fivsevn/57store-mirror/static/` 当当前版本上传。** 该目录仍保留旧版 HTML/CSS。已核对：其 `app.py`、`app.js`、服务文件和事件脚本与运行版一致，HTML/CSS 不一致。

当前运行文件 SHA-256：

```text
9efdc3f4ce8581e32a17a6183eaa083d11e01efec0efd15f56127340aaf6df5d  app.py
d45d687de5aa89f2b2d4e6fae1e533fbf627f11eaf020f6f433f24d381be8e85  static/app.js
577495f7bce16de9bb2dcf690922c880ff022959d6b11208cf2458be96af2be3  static/index.html
6540ede6b49aa7b8e391b1b8df58cc5161ab37dd7596f214af0db9fb12e74593  static/style.css
```

## 2. 屏幕与开机配置：备份有效配置，不备份整个系统目录

| Pi5 实际路径 | 实查结果 | GitHub 建议 |
| --- | --- | --- |
| `/home/fivsevn/.config/labwc/autostart` | 等待 5 秒后循环运行 Chromium；退出后等 2 秒再启动；访问 `http://127.0.0.1:5757` | `kiosk/labwc/autostart`，应备份 |
| `/home/fivsevn/.config/labwc/environment` | 美式键盘环境变量 | `kiosk/labwc/environment`，可选 |
| `/home/fivsevn/.config/labwc/rc.xml` | 用户窗口管理配置；未检出项目启动引用 | `kiosk/labwc/rc.xml`，可选，恢复屏幕环境时参考 |
| `/etc/xdg/labwc/autostart` | 已注释桌面管理器和面板启动，保留 kanshi、XDG 自启动 | `kiosk/system-labwc/autostart`，应备份作环境参考 |
| `/etc/lightdm/lightdm.conf` | `autologin-user=fivsevn`、`autologin-session=rpd-labwc`、`user-session=rpd-labwc` | 保存上述有效设置为 `kiosk/lightdm-settings.md`；按目标系统合并 |
| `/etc/systemd/system/getty@tty1.service.d/autologin.conf` | tty1 自动登录 `fivsevn`，与图形登录属于两套设置 | `kiosk/getty-autologin.conf`，可选环境参考 |
| `/etc/systemd/system/multi-user.target.wants/57store-mirror.service` | 指向正式服务文件的自启动符号链接 | 不复制；由 `systemctl enable` 重建 |
| `/etc/systemd/system/display-manager.service` | 指向 `/lib/systemd/system/lightdm.service` | 不复制；由系统安装配置管理 |

Kiosk 使用 `/home/fivsevn/.config/chromium-mirror` 独立浏览器配置和 `--password-store=basic`。GitHub 保存启动参数即可，不保存该浏览器配置目录；它可能包含会话或账号数据。

## 3. 持久数据、日志和缓存：不上传 GitHub

| 实际路径 | 内容 | 备份方式 |
| --- | --- | --- |
| `/var/lib/57store-mirror/mirror.db` | SQLite 事件、状态及服务启动次数 | **应私下备份**；不进 Git；在线备份用 SQLite backup API，或停服务后复制 |
| `/var/lib/57store-mirror/config.json` | `event_api_token` 配置，权限 600 | **不得上传 GitHub**；需要保持原令牌时私下加密保存；可由安装程序重新生成 |
| `/var/lib/57store-mirror/status.json` | 当前状态的派生快照 | 不备份；运行时重建 |
| `/var/lib/57store-mirror/mirror.db-wal`、`mirror.db-shm`、`.status.*.tmp` | 运行时可能产生的 SQLite 辅助文件和快照临时文件；本次列表中未出现 | 不进 Git；不要把运行中单独复制的主数据库当一致性备份 |
| `/run/log/journal/` | 本次服务 journal 所在位置 | 不进 Git；用 `journalctl -u 57store-mirror.service` 查看 |
| `/var/log/journal/` | 持久 journal 目录，本次为空 | 不进 Git |
| `/home/fivsevn/.xsession-errors`、`.xsession-errors.old` | 桌面会话输出，可能包含 Chromium 输出 | 不进 Git |
| `/var/log/lightdm/` | 显示管理器日志目录 | 不进 Git；无权枚举内部文件 |
| `/home/fivsevn/.config/chromium-mirror/`、`/home/fivsevn/.cache/` | 浏览器资料和缓存 | 不进 Git；不是页面源码 |
| `/home/fivsevn/.ssh/`、`.Xauthority`、`.bash_history`，以及系统 SSH/Wi-Fi/钥匙环凭据 | 认证、会话和私人信息 | 不进 Git；不属于源码备份范围 |

本次只列出数据配置文件名称和权限，未读取令牌内容，未导出数据库或事件正文。

## 4. 原始安装包、旧版与暂存文件

| 实际路径 | 判断 | 备份建议 |
| --- | --- | --- |
| `/home/fivsevn/57store-mirror/` | 原始安装包，包含 README、`.gitignore`、安装脚本、测试和源码 | 提取第 1 节所需内容；不要整体覆盖当前运行版 |
| `/home/fivsevn/57store-dos-update/index.html`、`style.css`、`apply.sh` | 本次视觉更新暂存与一次性部署脚本 | 可放 `archive/dos-update/` 留档；不是常规安装入口 |
| `/home/fivsevn/57store-dos-update/grain.svg` | 暂存图片，正式目录不存在，正式 CSS 未引用 | 可归档；当前运行无需备份它 |
| `/opt/57store-visual-backup-20260905-080125/` | 更新前的 `index.html`、`style.css` | 可选放 `archive/visual-before-dos/`，或私下留档 |
| `/home/fivsevn/.config/labwc/autostart.bak.20260905-072050`、`autostart.bak.20260905-072738` | 旧版屏幕启动配置 | 可私下留档；恢复使用有效 `autostart` |
| `/etc/xdg/labwc/autostart.bak.20260905-072342` | 系统桌面启动旧配置 | 可私下留档 |
| `/home/fivsevn/mirror-test.py` | 早期 Tkinter 全屏文字样机；当前启动链未引用 | 可选 `archive/mirror-test.py`，不是当前前端 |

`apply.sh` 校验旧文件哈希后替换视觉文件，不能作为通用更新工具反复执行。

## 5. Web 服务与检查边界

- `57store-mirror.service` 实查为 `enabled`、`active/running`；执行 `/usr/bin/python3 /opt/57store-mirror/app.py serve --host 0.0.0.0 --port 5757 --data-dir /var/lib/57store-mirror`。
- 5757 端口由该 Python 进程监听；没有发现 nginx/apache/lighttpd 服务单元或 80/443 监听。
- `/etc/apache2/conf-available/javascript-common.conf` 和 `/etc/lighttpd/conf-available/90-javascript-alias.conf` 只是系统 `/usr/share/javascript` 的通用别名片段，不是 57STORE 配置，不应加入项目备份。不能仅凭这两个目录断言安装了 Web 服务器。
- `fivsevn` 无 crontab，`/etc/rc.local` 不存在；已检查可读 systemd、XDG、labwc、LightDM、系统 cron 与 shell 启动入口，未发现另一套 57STORE 部署定时任务。
- 当前账号不能免密码使用 sudo。本次未检查 root 私有目录、root crontab 或无权读取的日志内部，不能声称覆盖所有受限系统文件；已确认实际运行服务、前端、数据目录和屏幕启动链。
- 当前 Mac 工作目录中的 `work/original/`、`work/preview/`、`work/apply.sh` 是之前视觉工作的本机材料，不是 Pi5 正在读取的路径。

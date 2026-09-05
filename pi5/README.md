# 57STORE / Pi5 Physical Mirror Node

**Pi5 开机，即代表 57STORE 在现实世界开始营业。** 这台设备是 57STORE 的实体节点，屏幕显示在线状态、运行时间与事件记忆。GitHub 保存版本，Mac 负责维护，Pi5 负责持续运行和保存内容。

本包于 2026-09-05 从正在运行的 Pi5 下载。源码和有效启动配置均已核对 SHA-256；不含数据库、令牌、日志和浏览器资料。恢复流程未实际执行。

## 系统架构与访问

- Raspberry Pi 5 Model B，Debian 13，Python 3.13.5，Chromium，LightDM / labwc 桌面。
- systemd 启动 Python 标准库 Web 服务，监听 `0.0.0.0:5757`，没有使用 nginx / Apache / lighttpd。
- LightDM 自动登录后，labwc 的 autostart 等待 5 秒并启动 Chromium 全屏显示本机网页；浏览器退出后等待 2 秒再次打开。
- Pi 屏幕访问 `http://127.0.0.1:5757`；同一局域网的 Mac、手机访问 `http://57store.local:5757`。本次 IP 为 `192.168.0.106`，以后可能变化。
- `/healthz` 提供健康检查，`/api/status` 提供状态，`/api/events?limit=8` 提供事件列表。

视觉层就是 HTML / CSS / JavaScript 网页。前端每 5 秒读取状态与事件，Chromium 负责显示。源码和内容实际保存在 Pi5 SD 卡（根文件系统 `/dev/mmcblk0p2`）中，Mac 通过局域网传输文件，不需要拔卡。关闭 Mac 不影响 Pi5 运行。

叙事中的开门营业对应系统和服务上线。RUN 是服务启动次数，重启服务也会增加，并非仅统计开机。正常停止会记录离线事件，突然断电不保证留下关店记录。

## 文件结构

```text
pi5/
├── README.md
├── FILE-INVENTORY.md       # 完整实际路径、旧版与排除项
├── SOURCE-SHA256.txt       # 来自 Pi5 的文件校验值
├── .gitignore
├── app.py
├── static/
│   ├── index.html
│   ├── style.css           # 当前黑白 DOS/CRT 视觉
│   └── app.js
├── install.sh
├── bin/57store-event
├── systemd/57store-mirror.service
├── tests/test_app.py
└── kiosk/
    ├── labwc/              # 用户窗口管理与屏幕自启配置
    ├── system-labwc/autostart
    ├── getty-autologin.conf
    └── lightdm-settings.md
```

设备上程序实际在 `/opt/57store-mirror/`；数据在 `/var/lib/57store-mirror/`；后台服务配置在 `/etc/systemd/system/57store-mirror.service`；事件命令在 `/usr/local/bin/57store-event`。

本包的 HTML/CSS 来自运行目录，家目录 `/home/fivsevn/57store-mirror/static/` 仍是旧版，不能用它覆盖本包。当前没有独立图片/assets 目录。后端仅开放三个静态文件；以后增加资源，要同步扩展后端路由和安装脚本。

## 启动、停止与日志

在 Mac 终端登录：

```bash
ssh fivsevn@57store.local
```

随后在 Pi5 按需选择执行：

```bash
systemctl status 57store-mirror.service --no-pager
sudo systemctl start 57store-mirror.service
sudo systemctl stop 57store-mirror.service
sudo systemctl restart 57store-mirror.service
journalctl -u 57store-mirror.service -n 50 --no-pager
curl -fsS http://127.0.0.1:5757/healthz
```

目前服务已启用开机自启，异常退出后等待 3 秒重启。`stop` 只停止当前运行，下次开机仍启动。`systemctl enable/disable` 用于改变自启设置。关闭浏览器不会停止后台，停止后台也不会关闭浏览器。

服务日志由 journal 管理，本次位于 `/run/log/journal/`；桌面日志在 `/home/fivsevn/.xsession-errors`，显示管理器日志在 `/var/log/lightdm/`。日志不进 GitHub。

## 从 Mac 远程修改

1. 在 Mac 解压本包，修改 `static/style.css` 调整视觉，修改 `static/index.html` 调整结构，修改 `static/app.js` 调整数据呈现。保留前端依赖的元素 ID。
2. 用 SCP 上传修改文件到 Pi5 的家目录暂存，先备份运行文件，再通过 sudo 安装到 `/opt/57store-mirror/static/`。
3. 修改前端后刷新网页即可；修改 `app.py` 后重启服务。纯静态预览不提供状态和事件 API。

例如在 Mac 的解压后 `pi5` 目录执行：

```bash
scp static/style.css fivsevn@57store.local:~/style.css.next
ssh fivsevn@57store.local
```

随后在 Pi5 执行：

```bash
sudo cp -p /opt/57store-mirror/static/style.css "/opt/57store-style-$(date +%Y%m%d-%H%M%S).css.bak"
sudo install -m 644 /home/fivsevn/style.css.next /opt/57store-mirror/static/style.css
```

本包下载过程中没有执行上述更新操作。

## GitHub 备份与私有数据

将解压后的 `pi5/` 文件夹内容放到 `fivsevn-57store` 仓库的 `pi5/` 中，保留目录结构，不要多套一层 `pi5/pi5/`。解压上传可直接浏览和管理源码；仅上传 ZIP 则只是保存压缩档。

以下不应上传 GitHub：

- `/var/lib/57store-mirror/mirror.db`：事件、状态与服务启动次数，应另作私有备份。
- `/var/lib/57store-mirror/config.json`：含 API 令牌，需私下加密保存或恢复时重新生成。
- `status.json`、数据库 WAL/SHM、日志、缓存、SSH 密钥、浏览器资料、系统生成文件。

运行中的 SQLite 不宜只复制主数据库文件。可使用 SQLite backup API 做在线一致性备份，或在维护窗口停止服务后复制数据库，再启动服务。私有备份放在 Git 仓库之外的加密存储中；本包不包含这部分。

`.gitignore` 已排除常见敏感和运行时文件，但不能替代提交前核对，也不会自动移除已经跟踪的文件。上传 GitHub 不会自动将 Pi5 服务发布到公网，GitHub Pages 不能运行 Python 后端。

## 恢复

1. 新 SD 卡准备兼容的 Raspberry Pi 桌面系统、用户 `fivsevn`、主机名 `57store`、网络、SSH 和 Python 3。需要实体屏幕时还应有 Chromium / labwc / LightDM。
2. 从 Mac 将本包 `pi5/` 上传到 Pi5，例如从其父目录执行 `scp -r pi5 fivsevn@57store.local:~/57store-restore`（目标目录应尚不存在）。
3. 在 Pi5 执行 `cd ~/57store-restore && sudo bash install.sh`。安装程序部署源码、创建数据配置、安装事件命令并启用和启动后台服务。
4. 用 `systemctl is-active 57store-mirror.service` 和 `/healthz` 检查。未恢复数据库时，事件记忆从新数据库开始。
5. 若恢复历史，先停止服务，保留新建数据目录作回退，再将一致性备份数据库放到 `/var/lib/57store-mirror/mirror.db`，可选恢复 `config.json`。确保不混入另一份数据库的 WAL/SHM；目录所有者为 `fivsevn:fivsevn`、权限 700，数据文件权限 600，然后启动服务。
6. **安装脚本不配置屏幕自启。** 将 `kiosk/labwc/` 中需要的文件恢复到 `/home/fivsevn/.config/labwc/`，保持 autostart 可执行且属于 `fivsevn`；参考 `kiosk/system-labwc/autostart` 合并桌面/面板设置，按 `lightdm-settings.md` 配置自动登录。系统版本不同应逐项合并，不盲目覆盖系统配置。tty1 配置是可选环境参考，和图形登录独立。
7. 在维护窗口重启，检查屏幕、手机访问、事件历史和日志。新启动会增加 RUN 并写入上线事件。

源码包重建程序，私有数据库保留店铺记忆。需要连同操作系统、桌面和全部设置原样恢复时，另做离线 SD 卡镜像并私下保存。

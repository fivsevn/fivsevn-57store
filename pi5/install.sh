#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/57store-mirror"
DATA_DIR="/var/lib/57store-mirror"
SERVICE_FILE="/etc/systemd/system/57store-mirror.service"
MIRROR_USER="fivsevn"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this installer with sudo: sudo ./install.sh" >&2
  exit 1
fi

if ! id "${MIRROR_USER}" >/dev/null 2>&1; then
  echo "Required user '${MIRROR_USER}' does not exist." >&2
  exit 1
fi

if [[ "$(hostname)" != "57store" ]]; then
  echo "NOTE: expected hostname '57store'; detected '$(hostname)'. Installation will continue."
fi

echo "[1/5] Installing 57STORE Mirror files"
install -d -m 0755 "${APP_DIR}" "${APP_DIR}/static"
install -m 0755 "${SCRIPT_DIR}/app.py" "${APP_DIR}/app.py"
install -m 0644 "${SCRIPT_DIR}/static/index.html" "${APP_DIR}/static/index.html"
install -m 0644 "${SCRIPT_DIR}/static/style.css" "${APP_DIR}/static/style.css"
install -m 0644 "${SCRIPT_DIR}/static/app.js" "${APP_DIR}/static/app.js"

echo "[2/5] Preparing persistent storage"
install -d -o "${MIRROR_USER}" -g "${MIRROR_USER}" -m 0700 "${DATA_DIR}"
sudo -u "${MIRROR_USER}" /usr/bin/python3 "${APP_DIR}/app.py" init-config --config "${DATA_DIR}/config.json"
chown -R "${MIRROR_USER}:${MIRROR_USER}" "${DATA_DIR}"

echo "[3/5] Installing event command"
install -m 0755 "${SCRIPT_DIR}/bin/57store-event" /usr/local/bin/57store-event

echo "[4/5] Enabling boot service"
install -m 0644 "${SCRIPT_DIR}/systemd/57store-mirror.service" "${SERVICE_FILE}"
systemctl daemon-reload
systemctl enable 57store-mirror.service
systemctl restart 57store-mirror.service

echo "[5/5] Checking node"
HEALTH_OK="no"
for attempt in 1 2 3 4 5; do
  if /usr/bin/python3 -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1:5757/healthz", timeout=2)' >/dev/null 2>&1; then
    HEALTH_OK="yes"
    break
  fi
  sleep 1
done

if ! systemctl is-active --quiet 57store-mirror.service || [[ "${HEALTH_OK}" != "yes" ]]; then
  echo "Service did not start. Recent log:" >&2
  journalctl -u 57store-mirror.service -n 30 --no-pager >&2
  exit 1
fi

NODE_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
echo
echo "57STORE Mirror v0.1 is online."
echo "Local address: http://${NODE_IP:-57store.local}:5757"
echo "Event command: 57store-event \"MIRROR DISPLAY CONNECTED\""

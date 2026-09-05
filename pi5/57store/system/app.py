#!/usr/bin/env python3
"""57STORE Mirror v0.1 — dependency-free Raspberry Pi node service."""

from __future__ import annotations

import argparse
import contextlib
import hmac
import json
import os
import secrets
import signal
import socket
import sqlite3
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import sysfeed


VERSION = "0.2.0"
DEFAULT_DATA_DIR = Path("/var/lib/57store-mirror")
STATIC_DIR = Path(__file__).resolve().parent / "static"
MAX_EVENT_LENGTH = 500
EVENT_LEVELS = {"info", "notice", "warning", "critical"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class MirrorStore:
    def __init__(self, path: Path):
        self.path = path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    @contextlib.contextmanager
    def transaction(self):
        connection = self.connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.transaction() as db:
            db.execute("PRAGMA journal_mode = WAL")
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    level TEXT NOT NULL,
                    source TEXT NOT NULL,
                    message TEXT NOT NULL
                )
                """
            )
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_events_created_at_id
                ON events(created_at DESC, id DESC)
                """
            )
            sysfeed.initialize(db)
            db.execute("PRAGMA optimize")

    def set_state(self, key: str, value: object) -> None:
        encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        with self.transaction() as db:
            db.execute(
                """
                INSERT INTO state(key, value, updated_at) VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
                """,
                (key, encoded, utc_now()),
            )

    def get_state(self, key: str, default: object = None) -> object:
        with self.transaction() as db:
            row = db.execute("SELECT value FROM state WHERE key = ?", (key,)).fetchone()
        if row is None:
            return default
        try:
            return json.loads(row["value"])
        except json.JSONDecodeError:
            return default

    def record_startup(self, started_at: str) -> int:
        count = int(self.get_state("start_count", 0)) + 1
        self.set_state("start_count", count)
        self.set_state("last_started_at", started_at)
        return count

    def add_event(self, message: str, level: str = "info", source: str = "terminal") -> dict:
        message = " ".join(str(message).strip().splitlines()).strip()
        source = " ".join(str(source).strip().splitlines()).strip() or "unknown"
        level = str(level).strip().lower()
        if not message:
            raise ValueError("message cannot be empty")
        if len(message) > MAX_EVENT_LENGTH:
            raise ValueError(f"message must be {MAX_EVENT_LENGTH} characters or fewer")
        if level not in EVENT_LEVELS:
            raise ValueError(f"level must be one of: {', '.join(sorted(EVENT_LEVELS))}")
        if len(source) > 64:
            raise ValueError("source must be 64 characters or fewer")

        created_at = utc_now()
        with self.transaction() as db:
            cursor = db.execute(
                "INSERT INTO events(created_at, level, source, message) VALUES (?, ?, ?, ?)",
                (created_at, level, source, message),
            )
            event_id = cursor.lastrowid
        return {
            "id": event_id,
            "created_at": created_at,
            "level": level,
            "source": source,
            "message": message,
        }

    def list_events(self, limit: int = 20) -> list[dict]:
        limit = max(1, min(int(limit), 100))
        with self.transaction() as db:
            rows = db.execute(
                """
                SELECT id, created_at, level, source, message
                FROM events ORDER BY created_at DESC, id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def last_event(self) -> dict | None:
        events = self.list_events(1)
        return events[0] if events else None


def read_system_uptime() -> float:
    try:
        return max(0.0, float(Path("/proc/uptime").read_text(encoding="utf-8").split()[0]))
    except (OSError, ValueError, IndexError):
        return 0.0


def find_local_ip() -> str:
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("192.0.2.1", 9))
        address = probe.getsockname()[0]
        if address and not address.startswith("127."):
            return address
    except OSError:
        pass
    finally:
        probe.close()

    try:
        for result in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            address = result[4][0]
            if not address.startswith("127."):
                return address
    except OSError:
        pass
    return "unavailable"


def disk_status(path: Path = Path("/")) -> dict:
    usage = os.statvfs(path)
    total = usage.f_frsize * usage.f_blocks
    available = usage.f_frsize * usage.f_bavail
    used = max(0, total - available)
    percent = round((used / total) * 100, 1) if total else 0.0
    return {"total_bytes": total, "used_bytes": used, "available_bytes": available, "percent": percent}


def build_status(store: MirrorStore, started_monotonic: float, started_at: str) -> dict:
    return {
        "node": "57STORE",
        "role": "PHYSICAL MIRROR NODE",
        "version": VERSION,
        "online": True,
        "timestamp": utc_now(),
        "hostname": socket.gethostname(),
        "ip": find_local_ip(),
        "system_uptime_seconds": round(read_system_uptime()),
        "application_uptime_seconds": round(max(0.0, time.monotonic() - started_monotonic)),
        "application_started_at": started_at,
        "start_count": int(store.get_state("start_count", 0)),
        "disk": disk_status(),
        "last_event": store.last_event(),
    }


def write_snapshot(data_dir: Path, status: dict) -> None:
    target = data_dir / "status.json"
    temporary = data_dir / f".status.{os.getpid()}.{threading.get_ident()}.tmp"
    temporary.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, target)


def load_token(config_path: Path) -> str:
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        token = config.get("event_api_token", "")
        return token if isinstance(token, str) else ""
    except (OSError, json.JSONDecodeError):
        return ""


def initialize_config(config_path: Path) -> bool:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if config_path.exists():
        return False
    temporary = config_path.with_name(f".{config_path.name}.tmp")
    temporary.write_text(
        json.dumps({"event_api_token": secrets.token_urlsafe(32)}, indent=2) + "\n",
        encoding="utf-8",
    )
    os.chmod(temporary, 0o600)
    os.replace(temporary, config_path)
    return True


def is_event_authorized(client_ip: str, supplied_token: str, expected_token: str) -> bool:
    if client_ip in {"127.0.0.1", "::1"}:
        return True
    return bool(expected_token and supplied_token and hmac.compare_digest(supplied_token, expected_token))


class MirrorRequestHandler(BaseHTTPRequestHandler):
    server_version = "57STORE-Mirror/0.2"
    store: MirrorStore
    data_dir: Path
    static_dir: Path
    started_monotonic: float
    started_at: str
    event_api_token: str

    def log_message(self, format_string: str, *args: object) -> None:
        sys.stderr.write(f"{self.log_date_time_string()} {self.client_address[0]} {format_string % args}\n")

    def _send_bytes(self, payload: bytes, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; font-src 'self' data:; img-src 'self'; connect-src 'self'; frame-ancestors 'none'",
        )
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def _send_json(self, data: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def _serve_static(self, relative_path: str) -> None:
        allowed = {
            "index.html": "text/html; charset=utf-8",
            "style.css": "text/css; charset=utf-8",
            "app.js": "text/javascript; charset=utf-8",
        }
        if relative_path not in allowed:
            self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            return
        try:
            payload = (self.static_dir / relative_path).read_bytes()
        except OSError:
            self._send_json({"error": "asset unavailable"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        self._send_bytes(payload, allowed[relative_path])

    def _status(self) -> dict:
        status = build_status(self.store, self.started_monotonic, self.started_at)
        try:
            write_snapshot(self.data_dir, status)
        except OSError as error:
            self.log_error("could not write status snapshot: %s", error)
        return status

    def do_HEAD(self) -> None:
        self.do_GET()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            self._serve_static("index.html")
        elif parsed.path == "/static/style.css":
            self._serve_static("style.css")
        elif parsed.path == "/static/app.js":
            self._serve_static("app.js")
        elif parsed.path == "/api/status":
            self._send_json(self._status())
        elif parsed.path == "/api/events":
            query = parse_qs(parsed.query)
            try:
                limit = int(query.get("limit", ["20"])[0])
            except ValueError:
                limit = 20
            self._send_json({"events": self.store.list_events(limit)})
        elif parsed.path in ("/api/signal", "/api/weather"):
            import terminalfeed
            self._send_json(terminalfeed.payload(self.data_dir, parsed.path.split("/")[-1]))
        elif parsed.path == "/api/sys":
            self._send_json(sysfeed.payload(self.store))
        elif parsed.path == "/healthz":
            self._send_json({"ok": True, "version": VERSION})
        else:
            self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/events":
            self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            return

        supplied_token = self.headers.get("X-57STORE-Token", "")
        if not is_event_authorized(self.client_address[0], supplied_token, self.event_api_token):
            self._send_json({"error": "event token required"}, HTTPStatus.UNAUTHORIZED)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > 8192:
            self._send_json({"error": "invalid request size"}, HTTPStatus.BAD_REQUEST)
            return

        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(body, dict):
                raise ValueError("JSON object required")
            event = self.store.add_event(
                body.get("message", ""),
                body.get("level", "info"),
                body.get("source", "api"),
            )
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        self._send_json({"event": event}, HTTPStatus.CREATED)


def configured_handler(
    store: MirrorStore,
    data_dir: Path,
    started_monotonic: float,
    started_at: str,
    token: str,
    static_dir: Path = STATIC_DIR,
) -> type[MirrorRequestHandler]:
    handler = type("ConfiguredMirrorRequestHandler", (MirrorRequestHandler,), {})
    handler.store = store
    handler.data_dir = data_dir
    handler.started_monotonic = started_monotonic
    handler.started_at = started_at
    handler.event_api_token = token
    handler.static_dir = static_dir
    return handler


def serve(host: str, port: int, data_dir: Path, static_dir: Path = STATIC_DIR) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    config_path = data_dir / "config.json"
    initialize_config(config_path)
    token = load_token(config_path)
    store = MirrorStore(data_dir / "mirror.db")
    store.initialize()
    started_at = utc_now()
    started_monotonic = time.monotonic()
    start_count = store.record_startup(started_at)
    store.add_event(
        f"SYSTEM ONLINE / SERVICE STARTED / RUN {start_count:04d}",
        level="notice",
        source="system",
    )
    write_snapshot(data_dir, build_status(store, started_monotonic, started_at))

    handler = configured_handler(store, data_dir, started_monotonic, started_at, token, static_dir)
    server = ThreadingHTTPServer((host, port), handler)
    server.daemon_threads = True
    synchronizer = sysfeed.Synchronizer(store)
    worker = threading.Thread(target=synchronizer.run, name="wordpress-sys", daemon=True)
    worker.start()

    def stop_service(_signum: int, _frame: object) -> None:
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop_service)
    print(f"57STORE Mirror v{VERSION} listening on http://{host}:{server.server_port}", flush=True)
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        synchronizer.stop.set()
        store.add_event("SYSTEM OFFLINE / SERVICE STOPPED", level="notice", source="system")
        offline_status = build_status(store, started_monotonic, started_at)
        offline_status["online"] = False
        write_snapshot(data_dir, offline_status)
        server.server_close()


def submit_event(url: str, config_path: Path, message: str, level: str, source: str) -> int:
    token = load_token(config_path)
    payload = json.dumps({"message": message, "level": level, "source": source}).encode("utf-8")
    request = urllib.request.Request(
        f"{url.rstrip('/')}/api/events",
        data=payload,
        headers={"Content-Type": "application/json", "X-57STORE-Token": token},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            result = json.loads(response.read().decode("utf-8"))
        event = result["event"]
        print(f"EVENT {event['id']:04d} STORED / {event['created_at']} / {event['message']}")
        return 0
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as error:
        print(f"57STORE event write failed: {error}", file=sys.stderr)
        return 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="57STORE Physical Mirror Node")
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve_parser = subparsers.add_parser("serve", help="start the web service")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=5757)
    serve_parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)

    event_parser = subparsers.add_parser("event", help="write a persistent event")
    event_parser.add_argument("message")
    event_parser.add_argument("--level", choices=sorted(EVENT_LEVELS), default="info")
    event_parser.add_argument("--source", default="terminal")
    event_parser.add_argument("--url", default="http://127.0.0.1:5757")
    event_parser.add_argument("--config", type=Path, default=DEFAULT_DATA_DIR / "config.json")

    config_parser = subparsers.add_parser("init-config", help="create an API token config")
    config_parser.add_argument("--config", type=Path, default=DEFAULT_DATA_DIR / "config.json")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "serve":
        serve(args.host, args.port, args.data_dir)
        return 0
    if args.command == "event":
        return submit_event(args.url, args.config, args.message, args.level, args.source)
    if args.command == "init-config":
        created = initialize_config(args.config)
        print("created" if created else "already exists")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

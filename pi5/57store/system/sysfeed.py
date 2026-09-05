"""Read-only WordPress SYS log mirror. No credentials or video requests."""
import json
import threading
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser

BASE_URL = "https://fivsevn.com/wp-json/wp/v2"
INTERVAL = 60


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1
        if tag in {"br", "p", "div", "li"} and not self.hidden:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)
        if tag in {"p", "div", "li"} and not self.hidden:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def plain_text(markup):
    parser = PlainText()
    parser.feed(markup)
    return "\n".join(" ".join(line.split()) for line in "".join(parser.parts).splitlines() if line.strip())


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def initialize(db):
    db.execute("""CREATE TABLE IF NOT EXISTS sys_posts (
        id INTEGER PRIMARY KEY, published_at TEXT NOT NULL,
        modified_at TEXT NOT NULL, received_at TEXT NOT NULL,
        content TEXT NOT NULL, link TEXT NOT NULL)""")


def payload(store, limit=100):
    with store.transaction() as db:
        rows = db.execute("SELECT * FROM sys_posts ORDER BY published_at DESC, id DESC LIMIT ?", (limit,)).fetchall()
        count = db.execute("SELECT COUNT(*) FROM sys_posts").fetchone()[0]
    return {"posts": [dict(row) for row in rows], "count": count,
            "sync": store.get_state("sys_sync", {"state": "waiting", "last_success": None}),
            "interval": INTERVAL}


def request_json(endpoint, params):
    url = BASE_URL + "/" + endpoint + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "57STORE-Physical-Mirror/0.2"})
    with urllib.request.urlopen(request, timeout=12) as response:
        raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("response too large")
        result = json.loads(raw)
        if not isinstance(result, list):
            raise ValueError("expected post list")
        return result, int(response.headers.get("X-WP-TotalPages", "1"))


class Synchronizer:
    def __init__(self, store, fetch=request_json):
        self.store = store
        self.fetch = fetch
        self.stop = threading.Event()

    def run_once(self):
        started = now()
        previous = self.store.get_state("sys_sync", {})
        try:
            category = self.store.get_state("sys_category")
            if not category:
                categories, _ = self.fetch("categories", {"slug": "57storesys"})
                category = next(int(c["id"]) for c in categories if c.get("slug") == "57storesys")
                self.store.set_state("sys_category", category)
            last_success = previous.get("last_success")
            params = {"categories": category, "status": "publish",
                      "_fields": "id,date_gmt,modified_gmt,content,link"}
            if last_success:
                since = datetime.fromisoformat(last_success.replace("Z", "+00:00")) - timedelta(minutes=5)
                params.update(per_page=100, orderby="modified", order="asc",
                              modified_after=since.isoformat(), modified_before=started)
            else:
                params.update(per_page=8, orderby="date", order="desc")
            posts, pages = self.fetch("posts", params)
            if last_success:
                if pages > 100:
                    raise ValueError("backlog exceeds sync limit")
                for page in range(2, pages + 1):
                    if self.stop.is_set():
                        return
                    more, _ = self.fetch("posts", dict(params, page=page))
                    posts.extend(more)
            records = []
            for post in posts:
                if post.get("content", {}).get("protected"):
                    continue
                content = plain_text(post["content"]["rendered"])
                if not content:
                    continue
                published = post["date_gmt"]
                modified = post["modified_gmt"]
                datetime.fromisoformat(published)
                datetime.fromisoformat(modified)
                records.append((int(post["id"]), published.rstrip("Z") + "Z",
                                modified.rstrip("Z") + "Z", started, content, post["link"]))
            with self.store.transaction() as db:
                db.executemany("""INSERT INTO sys_posts VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET modified_at=excluded.modified_at,
                    published_at=excluded.published_at, content=excluded.content, link=excluded.link""", records)
                state = {"state": "online", "last_success": started, "last_attempt": started}
                db.execute("""INSERT INTO state VALUES ('sys_sync', ?, ?)
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at""",
                           (json.dumps(state), started))
        except Exception as error:
            # Cached posts and the successful cursor survive any partial/network failure.
            self.store.set_state("sys_sync", {"state": "offline", "last_success": previous.get("last_success"),
                                 "last_attempt": started, "error": type(error).__name__})

    def run(self):
        while not self.stop.is_set():
            self.run_once()
            self.stop.wait(INTERVAL)

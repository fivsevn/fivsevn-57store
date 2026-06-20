import hashlib
import html
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests


TRIGGER_FILE = Path("sys/trigger.md")

DEFAULT_WP_STATUS = "publish"
DEFAULT_CATEGORY_SLUG = "57storesys"
DEFAULT_TIMEZONE = "Asia/Taipei"

ALLOWED_WP_STATUSES = {"publish", "draft"}


def env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")

    return value.rstrip("/") if name.endswith("URL") else value


WP_BASE_URL = env("WP_BASE_URL")
WP_USERNAME = env("WP_USERNAME")
WP_APP_PASSWORD = env("WP_APP_PASSWORD")

AUTH = (WP_USERNAME, WP_APP_PASSWORD)


def wp_get(endpoint: str, params: dict | None = None):
    response = requests.get(
        f"{WP_BASE_URL}/wp-json/wp/v2/{endpoint.lstrip('/')}",
        params=params,
        auth=AUTH,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def wp_post(endpoint: str, payload: dict):
    response = requests.post(
        f"{WP_BASE_URL}/wp-json/wp/v2/{endpoint.lstrip('/')}",
        json=payload,
        auth=AUTH,
        timeout=30,
    )

    if not response.ok:
        print(response.status_code, response.text, file=sys.stderr)

    response.raise_for_status()
    return response.json()


def strip_wrapping_quotes(value: str) -> str:
    value = value.strip()

    quote_pairs = [
        ('"', '"'),
        ("'", "'"),
        ("“", "”"),
        ("”", "”"),
        ("‘", "’"),
        ("’", "’"),
    ]

    for left, right in quote_pairs:
        if value.startswith(left) and value.endswith(right):
            return value[1:-1].strip()

    return value


def parse_simple_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    text = raw.replace("\r\n", "\n").replace("\r", "\n")

    if not text.startswith("---\n"):
        raise RuntimeError(f"{TRIGGER_FILE} must start with a YAML frontmatter block.")

    parts = text.split("\n---\n", 1)

    if len(parts) != 2:
        raise RuntimeError(
            f"{TRIGGER_FILE} must contain a second --- line after frontmatter."
        )

    frontmatter_text = parts[0].removeprefix("---\n")
    body = parts[1]

    metadata: dict[str, str] = {}

    for raw_line in frontmatter_text.split("\n"):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if ":" not in line:
            raise RuntimeError(f"Invalid frontmatter line: {raw_line}")

        key, value = line.split(":", 1)
        key = key.strip()
        value = strip_wrapping_quotes(value.strip())

        if not key:
            raise RuntimeError(f"Invalid empty frontmatter key: {raw_line}")

        metadata[key] = value

    return metadata, body


def read_trigger() -> tuple[dict[str, str], list[str]]:
    if not TRIGGER_FILE.exists():
        raise RuntimeError(f"Trigger file not found: {TRIGGER_FILE}")

    raw = TRIGGER_FILE.read_text(encoding="utf-8")
    metadata, body = parse_simple_frontmatter(raw)

    lines = [line.strip() for line in body.split("\n")]
    lines = [line for line in lines if line]

    if len(lines) != 2:
        raise RuntimeError(
            f"{TRIGGER_FILE} body must contain exactly 2 non-empty lines. "
            f"Current non-empty body line count: {len(lines)}"
        )

    return metadata, lines


def get_config(metadata: dict[str, str]) -> tuple[str, str, str]:
    wp_status = metadata.get("wp_status", DEFAULT_WP_STATUS).strip()
    category_slug = metadata.get("category", DEFAULT_CATEGORY_SLUG).strip()
    timezone_name = metadata.get("timezone", DEFAULT_TIMEZONE).strip()

    if wp_status not in ALLOWED_WP_STATUSES:
        raise RuntimeError(
            f"Unsupported wp_status: {wp_status}. "
            f"Allowed values: {', '.join(sorted(ALLOWED_WP_STATUSES))}"
        )

    if category_slug != DEFAULT_CATEGORY_SLUG:
        raise RuntimeError(
            f"Unsupported category: {category_slug}. "
            f"Expected: {DEFAULT_CATEGORY_SLUG}"
        )

    try:
        ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise RuntimeError(f"Invalid timezone: {timezone_name}") from exc

    return wp_status, category_slug, timezone_name


def validate_content_lines(english_line: str, chinese_line: str) -> None:
    if len(english_line) > 120:
        raise RuntimeError("English line is too long. Keep it as a short terminal fragment.")

    if len(chinese_line) > 120:
        raise RuntimeError("Chinese line is too long. Keep it as a short Chinese line.")

    if not re.search(r"[\u4e00-\u9fff]", chinese_line):
        raise RuntimeError("Chinese line should contain Chinese text.")

    forbidden_markdown = ["#", "*", "`", ">", "|"]

    for token in forbidden_markdown:
        if token in english_line or token in chinese_line:
            raise RuntimeError(
                f"Markdown-like character not allowed in content lines: {token}"
            )


def make_log_title(timezone_name: str) -> str:
    now = datetime.now(ZoneInfo(timezone_name))
    return now.strftime("[%Y-%m-%d %H:%M]")


def get_category_id_by_slug(slug: str) -> int:
    items = wp_get("categories", {"slug": slug, "per_page": 100})

    if items:
        return int(items[0]["id"])

    raise RuntimeError(f"Category not found by slug: {slug}")


def make_post_slug(title: str, english_line: str, chinese_line: str) -> str:
    digest = hashlib.sha1(
        f"{title}\n{english_line}\n{chinese_line}".encode("utf-8")
    ).hexdigest()[:12]

    compact_time = (
        title.replace("[", "")
        .replace("]", "")
        .replace(":", "")
        .replace(" ", "-")
    )

    return f"57storesys-{compact_time}-{digest}"


def post_already_exists(slug: str) -> bool:
    items = wp_get(
        "posts",
        {
            "slug": slug,
            "status": "publish,draft,private,future,pending",
            "per_page": 10,
        },
    )

    return bool(items)


def make_post_content(english_line: str, chinese_line: str) -> str:
    english = html.escape(english_line, quote=True)
    chinese = html.escape(chinese_line, quote=True)

    return f"<p>{english}<br>{chinese}</p>"


def publish_trigger() -> None:
    metadata, lines = read_trigger()
    wp_status, category_slug, timezone_name = get_config(metadata)

    english_line, chinese_line = lines

    validate_content_lines(english_line, chinese_line)

    title = make_log_title(timezone_name)
    slug = make_post_slug(title, english_line, chinese_line)

    if post_already_exists(slug):
        print(f"Skip existing 57storesys post: {title}")
        return

    category_id = get_category_id_by_slug(category_slug)

    payload = {
        "status": wp_status,
        "title": title,
        "slug": slug,
        "content": make_post_content(english_line, chinese_line),
        "categories": [category_id],
    }

    post = wp_post("posts", payload)

    print(
        f"Published 57storesys post: "
        f"{title} -> {post.get('link')} "
        f"status={wp_status} "
        f"category={category_slug} "
        f"timezone={timezone_name}"
    )


def main() -> None:
    publish_trigger()


if __name__ == "__main__":
    main()

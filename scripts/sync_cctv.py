"""Append verified CCTV uploads without changing saved rooms or editorial choices."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from zoneinfo import ZoneInfo

from site_post_metadata import dump_frontmatter, normalize_metadata, read_frontmatter, validate_metadata
from youtube_source import Video, get_channel_videos, get_video_metadata

ROOT = Path(__file__).resolve().parents[1]
ZONE = ZoneInfo("Asia/Shanghai")
VIDEO_ID = re.compile(r"[A-Za-z0-9_-]{11}\Z")


def existing_ids(root: Path = ROOT) -> set[str]:
    """Hidden rooms and authored draft records also reserve their video identity."""
    seen = set()
    saved = {}
    for folder in ("cctv", "drafts"):
        for path in (root / folder).rglob("index.md"):
            try:
                meta, _ = read_frontmatter(path)
                if folder == "cctv":
                    validate_metadata(meta, site="cctv", schema_dir=root / "schemas")
            except ValueError:
                if folder == "cctv":
                    raise
                continue
            videos = meta.get("extra", {}).get("video_ids", [])
            if not isinstance(videos, list) or any(not isinstance(v, str) or not VIDEO_ID.fullmatch(v) for v in videos):
                raise ValueError(f"Invalid saved video identities: {path}")
            if len(videos) != len(set(videos)):
                raise ValueError(f"Duplicate saved CCTV video identity: {path}")
            if folder == "cctv":
                for video_id in videos:
                    if video_id in saved:
                        raise ValueError(f"Duplicate saved CCTV video identity {video_id}: {saved[video_id]} and {path}")
                    saved[video_id] = path
            seen.update(videos)
    return seen


def plan(videos: list[Video], root: Path = ROOT) -> list[tuple[Path, dict]]:
    seen = existing_ids(root)
    pending = []
    for video in videos:
        if video.video_id in seen:
            continue
        if not isinstance(video.video_id, str) or not VIDEO_ID.fullmatch(video.video_id):
            raise ValueError("Invalid CCTV video ID")
        if not isinstance(video.title, str) or not video.title.strip() or not isinstance(video.published_at, str):
            raise ValueError(f"Incomplete CCTV metadata: {video.video_id}")
        stamp = datetime.fromisoformat(video.published_at.replace("Z", "+00:00"))
        if "T" not in video.published_at or stamp.utcoffset() is None:
            raise ValueError("CCTV publication time requires an exact time and timezone")
        local = stamp.astimezone(ZONE)
        token = hashlib.sha256(video.video_id.encode("utf-8")).hexdigest()[:12]
        ident = local.strftime("%Y-%m-%d-%H%M%S-") + token
        path = root / "cctv" / local.strftime("%Y/%m") / ident / "index.md"
        if path.exists() or path.is_symlink():
            raise ValueError(f"Refusing to overwrite saved CCTV package: {path}")
        for parent in path.parents:
            if parent == root:
                break
            if parent.is_symlink():
                raise ValueError(f"Symlink in CCTV publication path: {parent}")
        meta = normalize_metadata({
            "id": ident,
            "title": video.title,
            "extra": {
                "published_at": local.isoformat(),
                "author": "[ CAM-57 ]",
                "source": "https://www.youtube.com/watch?v=" + video.video_id,
                "video_ids": [video.video_id],
            },
        }, site="cctv")
        validate_metadata(meta, site="cctv", schema_dir=root / "schemas")
        pending.append((path, meta))
        seen.add(video.video_id)
    return pending


def save_new(path: Path, meta: dict) -> None:
    """Make a complete index visible atomically and refuse concurrent replacements."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, prefix=".cctv-", delete=False) as file:
        temporary = Path(file.name)
        try:
            file.write(dump_frontmatter(meta))
            file.flush()
            os.fsync(file.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def sync(root: Path = ROOT) -> int:
    root = Path(root).resolve()
    config = json.loads((root / "site-data/cctv.json").read_text())
    configured = config["channel_id"]
    channel = os.environ.get("YOUTUBE_57STORE_CHANNEL_ID", "").strip() or configured
    if channel != configured:
        raise ValueError("CCTV channel differs from the verified configuration")
    videos = get_channel_videos(channel, "57store CCTV")
    seen = existing_ids(root)
    # Resolve the entire new batch before saving anything; an uncertain date fails
    # rather than importing a partial catalogue or assigning today's date.
    resolved = [get_video_metadata(v.video_id, channel) if v.video_id not in seen and not v.published_at else v for v in videos]
    pending = plan(resolved, root)
    for path, meta in pending:
        save_new(path, meta)
    print(f"{len(videos)} verified public CCTV uploads; {len(pending)} new rooms; saved history preserved")
    return len(pending)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        sync(args.root)
    except Exception as error:
        print(f"CCTV synchronization failed ({type(error).__name__}); saved rooms are retained.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Save committed SYS trigger-body revisions as independent Markdown packages.

The Git commit/path pair identifies a publication. The ledger and complete
packages are saved together; retrying never rewrites an edited saved post.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
from zoneinfo import ZoneInfo

from site_post_metadata import dump_frontmatter, normalize_metadata, read_frontmatter, validate_metadata

ROOT = Path(__file__).resolve().parents[1]
TRIGGER = "sys/trigger.md"
STATE = ".publishing/sys.json"
TZ = ZoneInfo("Asia/Shanghai")
OID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
IDENT = re.compile(r"\d{4}-\d{2}-\d{2}-\d{6}-[0-9a-f]{12}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise ValueError("Git history could not be read: " + result.stderr.decode("utf-8", "replace").strip())
    return result.stdout


def safe_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative or "\x00" in relative:
        raise ValueError("Unsafe SYS publication path")
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != relative:
        raise ValueError("Unsafe SYS publication path: " + relative)
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink():
            raise ValueError("Symlink SYS publication path: " + relative)
    target = root.joinpath(*path.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError("SYS publication path leaves the repository")
    return target


def read_state(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    path = safe_path(root, STATE)
    if not path.is_file():
        raise ValueError("SYS publishing state is missing; initialize its cursor before importing")
    state = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(state, dict) or state.get("version") != 1
            or not isinstance(state.get("cursor"), str) or not OID.fullmatch(state["cursor"])
            or not isinstance(state.get("events"), dict)):
        raise ValueError("Invalid SYS publishing state")
    for key, event in state["events"].items():
        if not isinstance(event, dict):
            raise ValueError("Invalid SYS publishing event")
        required = ("id", "commit", "trigger", "blob_sha", "body_sha256", "package", "published_at")
        if any(not isinstance(event.get(field), str) for field in required):
            raise ValueError("Invalid SYS publishing event")
        if (not OID.fullmatch(event["commit"]) or not OID.fullmatch(event["blob_sha"])
                or not DIGEST.fullmatch(event["body_sha256"]) or not IDENT.fullmatch(event["id"])
                or event["trigger"] != TRIGGER or key != event["commit"] + ":" + TRIGGER):
            raise ValueError("Invalid SYS publishing event identity")
        stamp = datetime.fromisoformat(event["published_at"])
        if stamp.utcoffset() is None:
            raise ValueError("SYS event publication time requires a timezone")
        local = stamp.astimezone(TZ)
        if (not event["id"].startswith(local.strftime("%Y-%m-%d-%H%M%S-"))
                or event["package"] != f"sys/{local:%Y/%m}/{event['id']}"):
            raise ValueError("Invalid SYS event package path")
        safe_path(root, event["package"] + "/index.md")
    return state


def write_state(root: Path, state: dict) -> None:
    path = safe_path(root, STATE)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix=".sys-state-", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(state, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def initialize(root: Path = ROOT, commit: str | None = None, *, stage: bool = False) -> dict:
    """Record an explicit boundary without publishing the trigger already there."""
    root = Path(root).resolve()
    if safe_path(root, STATE).exists():
        state = read_state(root)
    else:
        commit = commit or git(root, "rev-parse", "HEAD^{commit}").decode().strip()
        if not isinstance(commit, str) or not OID.fullmatch(commit):
            raise ValueError("An exact Git commit SHA is required to initialize SYS")
        if git(root, "rev-parse", "--verify", commit + "^{commit}").decode().strip() != commit:
            raise ValueError("SYS initialization commit did not resolve exactly")
        git(root, "merge-base", "--is-ancestor", commit, "HEAD")
        state = {"version": 1, "cursor": commit, "events": {}}
        write_state(root, state)
    if stage:
        git(root, "add", "--", STATE)
    return state


def pending_commits(root: Path, cursor: str, head: str) -> list[str]:
    try:
        resolved = git(root, "rev-parse", "--verify", cursor + "^{commit}").decode().strip()
    except ValueError as error:
        raise ValueError("SYS publishing cursor is missing from Git history; restore history before importing") from error
    try:
        git(root, "merge-base", "--is-ancestor", resolved, head)
    except ValueError as error:
        raise ValueError("SYS publishing cursor is not an ancestor of HEAD; review the branch before importing") from error
    return git(root, "rev-list", "--reverse", "--topo-order", head, "^" + resolved).decode().splitlines()


def tree_entry(root: Path, commit: str) -> tuple[str, str] | None:
    raw = git(root, "ls-tree", "-z", commit, "--", TRIGGER)
    if not raw:
        return None
    records = raw.rstrip(b"\0").split(b"\0")
    if len(records) != 1:
        raise ValueError("Unexpected SYS trigger tree entries")
    details, filename = records[0].split(b"\t", 1)
    mode, kind, blob = details.decode("ascii").split()
    if filename.decode("utf-8") != TRIGGER or kind != "blob" or mode not in {"100644", "100755"}:
        raise ValueError("SYS trigger must be a regular Markdown file")
    return mode, blob


def parse_trigger(data: bytes) -> tuple[dict, str]:
    """Keep Markdown indentation and hard breaks; ignore surrounding blank lines."""
    metadata, body = read_frontmatter(data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"))
    lines = body.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return metadata, "\n".join(lines) + "\n" if lines else ""


def ingest(root: Path = ROOT, *, stage: bool = False) -> int:
    root = Path(root).resolve()
    state = read_state(root)
    head = git(root, "rev-parse", "HEAD^{commit}").decode().strip()
    commits = pending_commits(root, state["cursor"], head)
    updated = deepcopy(state)
    prepared = []
    relevant = False
    body_cache = {}

    def snapshot(entry):
        if entry is None:
            return {}, ""
        blob = entry[1]
        if blob not in body_cache:
            body_cache[blob] = parse_trigger(git(root, "cat-file", "blob", blob))
        return body_cache[blob]

    with tempfile.TemporaryDirectory(prefix=".sys-import-", dir=root) as temporary:
        staging = Path(temporary)
        for commit in commits:
            parents = git(root, "rev-list", "--parents", "-n", "1", commit).decode().split()[1:]
            entry = tree_entry(root, commit)
            parent_entries = [tree_entry(root, parent) for parent in parents]
            # Only an actual edit/deletion of the trigger advances the SYS ledger.
            if parent_entries and entry == parent_entries[0]:
                continue
            relevant = True
            raw, body = snapshot(entry)
            if not body:
                continue
            # Metadata edits and merge copies do not create additional body events.
            if any(body == snapshot(parent)[1] for parent in parent_entries):
                continue
            key = commit + ":" + TRIGGER
            if key in updated["events"]:
                continue
            stamp = datetime.fromisoformat(git(root, "show", "-s", "--format=%cI", commit).decode().strip())
            if stamp.utcoffset() is None:
                raise ValueError("SYS commit publication time requires a timezone")
            stamp = stamp.astimezone(TZ)
            ident = stamp.strftime("%Y-%m-%d-%H%M%S-") + hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
            package = f"sys/{stamp:%Y/%m}/{ident}"
            target = safe_path(root, package)
            if target.exists() or any(existing == target for _, existing in prepared):
                raise ValueError("SYS package already exists and will not be overwritten: " + package)
            status = raw.get("status", raw.get("wp_status", "published"))
            if status == "publish":
                status = "published"
            source = {"id": ident, "title": raw.get("title") or stamp.strftime("[%Y-%m-%d %H:%M]"),
                      "date": stamp.isoformat(timespec="seconds"), "status": status,
                      "visibility": raw.get("visibility", "public"),
                      "author": raw.get("author", "五月七日"),
                      "extra": {"source_key": key}}
            if "languages" in raw:
                source["languages"] = raw["languages"]
            meta = normalize_metadata(source, site="sys")
            validate_metadata(meta, site="sys", schema_dir=root / "schemas")
            pending = staging / ident
            pending.mkdir()
            (pending / "index.md").write_text(dump_frontmatter(meta) + body, encoding="utf-8")
            updated["events"][key] = {"id": ident, "commit": commit, "trigger": TRIGGER,
                                      "blob_sha": entry[1], "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                                      "package": package, "published_at": meta["extra"]["published_at"]}
            prepared.append((pending, target))
        if relevant:
            updated["cursor"] = head
            installed, created_parents = [], []
            try:
                for pending, target in prepared:
                    missing = []
                    parent = target.parent
                    while parent != root and not parent.exists():
                        missing.append(parent)
                        parent = parent.parent
                    target.parent.mkdir(parents=True, exist_ok=True)
                    created_parents.extend(reversed(missing))
                    pending.rename(target)
                    installed.append((pending, target))
                write_state(root, updated)
            except BaseException:
                for pending, target in reversed(installed):
                    target.rename(pending)
                for parent in reversed(created_parents):
                    if parent.exists() and not any(parent.iterdir()):
                        parent.rmdir()
                raise
    if stage:
        git(root, "add", "--", STATE, *(str(target.relative_to(root) / "index.md") for _, target in prepared))
    return len(prepared)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--stage", action="store_true", help="Stage only generated SYS packages and their ledger")
    parser.add_argument("--initialize", action="store_true", help="Initialize a missing ledger without publishing its current trigger")
    parser.add_argument("--commit", help="Exact initialization commit; requires --initialize")
    args = parser.parse_args()
    if args.commit and not args.initialize:
        parser.error("--commit requires --initialize")
    if args.initialize:
        initialize(args.root, args.commit, stage=args.stage)
        print("SYS publishing cursor initialized; the existing trigger was not published.")
    else:
        print(f"Imported {ingest(args.root, stage=args.stage)} committed SYS body revisions.")


if __name__ == "__main__":
    main()

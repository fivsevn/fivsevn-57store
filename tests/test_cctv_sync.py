"""Publishing guarantees for the verified CCTV upload catalogue."""
import json
import os
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sync_cctv as syncer
from site_post_metadata import dump_frontmatter, read_frontmatter
from youtube_source import Video

CHANNEL = "UCenBP2oAYYiateiwPtcAuHw"
OTHER = "UC" + "a" * 22
FIRST = "AbCdEf123_-"
SECOND = "aBcDeF123_-"


class CctvSyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        shutil.copytree(syncer.ROOT / "schemas", self.root / "schemas")
        (self.root / "site-data").mkdir()
        (self.root / "site-data/cctv.json").write_text(json.dumps({"channel_id": CHANNEL}))

    def save(self, video, *, status="published", body=""):
        path, meta = syncer.plan([video], self.root)[0]
        meta["status"] = status
        syncer.save_new(path, meta)
        if body:
            path.write_text(dump_frontmatter(meta) + body)
        return path

    def test_exact_time_and_shanghai_month_derive_the_package(self):
        video = Video("Original title", FIRST, "2025-12-31T16:00:00.123Z")
        path, meta = syncer.plan([video], self.root)[0]
        self.assertEqual(path.relative_to(self.root).parts[:3], ("cctv", "2026", "01"))
        self.assertEqual(path.parent.name, meta["id"])
        self.assertTrue(meta["id"].startswith("2026-01-01-000000-"))
        self.assertEqual(meta["extra"]["published_at"], "2026-01-01T00:00:00.123000+08:00")
        self.assertEqual((meta["module"], meta["submodule"], meta["source_of_truth"]), ("57store", "cctv", "site"))

    def test_case_distinct_video_ids_at_same_second_cannot_share_a_package(self):
        pending = syncer.plan([Video("One", FIRST, "2026-10-01T00:00:00Z"),
                               Video("Two", SECOND, "2026-10-01T00:00:00Z")], self.root)
        self.assertEqual(len({path for path, _ in pending}), 2)
        self.assertEqual(len({meta["id"] for _, meta in pending}), 2)

    def test_hidden_saved_room_and_edits_survive_changed_upstream_metadata(self):
        video = Video("Saved title", FIRST, "2026-10-01T00:00:00Z")
        path = self.save(video, status="hidden", body="Authored room note.\n")
        before = path.read_bytes()
        self.assertIn(FIRST, syncer.existing_ids(self.root))
        self.assertEqual(syncer.plan([Video("Changed upstream title", FIRST, "2026-11-01T00:00:00Z")], self.root), [])
        self.assertEqual(path.read_bytes(), before)

    def test_duplicate_saved_video_records_fail_before_any_new_import(self):
        original = self.save(Video("First authored record", FIRST, "2026-10-01T00:00:00Z"))
        meta, _ = read_frontmatter(original)
        meta["id"] = "second-authored-record"
        meta["title"] = "Second authored record"
        other = self.root / "cctv/2026/10/second-authored-record/index.md"
        syncer.save_new(other, meta)
        with self.assertRaisesRegex(ValueError, "Duplicate saved CCTV video identity"):
            syncer.existing_ids(self.root)
        with self.assertRaisesRegex(ValueError, "Duplicate saved CCTV video identity"):
            syncer.plan([Video("New upload", SECOND, "2026-10-02T00:00:00Z")], self.root)
        self.assertTrue(original.is_file() and other.is_file())

    def test_draft_video_is_not_reimported(self):
        draft = self.root / "drafts/cctv/unpublished/index.md"
        draft.parent.mkdir(parents=True)
        draft.write_text("---\nextra:\n  video_ids: [" + FIRST + "]\n---\nUnpublished note\n")
        self.assertEqual(syncer.plan([Video("Upstream", FIRST, "2026-10-01T00:00:00Z")], self.root), [])

    def test_missing_exact_date_and_wrong_timezone_fail_without_writing(self):
        for stamp in (None, "2026-10-01", "2026-10-01T00:00:00"):
            with self.subTest(stamp=stamp), self.assertRaises(ValueError):
                syncer.plan([Video("Incomplete", FIRST, stamp)], self.root)
        self.assertFalse(list((self.root / "cctv").rglob("index.md")))

    def test_sync_resolves_only_missing_new_dates_then_becomes_idempotent(self):
        self.save(Video("Saved", FIRST, "2026-10-01T00:00:00Z"), status="draft")
        catalogue = [Video("Saved changed", FIRST), Video("New", SECOND)]
        exact = Video("Verified new", SECOND, "2026-10-02T06:07:08Z")
        with patch.dict(os.environ, {"YOUTUBE_57STORE_CHANNEL_ID": CHANNEL}), \
                patch.object(syncer, "get_channel_videos", return_value=catalogue) as fetch, \
                patch.object(syncer, "get_video_metadata", return_value=exact) as resolve:
            self.assertEqual(syncer.sync(self.root), 1)
            self.assertEqual(syncer.sync(self.root), 0)
        resolve.assert_called_once_with(SECOND, CHANNEL)
        fetch.assert_called_with(CHANNEL, "57store CCTV")
        self.assertEqual(len(list((self.root / "cctv").rglob("index.md"))), 2)

    def test_undated_batch_failure_does_not_save_the_other_new_room(self):
        catalogue = [Video("Dated", FIRST, "2026-10-01T00:00:00Z"), Video("Undated", SECOND)]
        with patch.dict(os.environ, {"YOUTUBE_57STORE_CHANNEL_ID": CHANNEL}), \
                patch.object(syncer, "get_channel_videos", return_value=catalogue), \
                patch.object(syncer, "get_video_metadata", side_effect=ValueError("No exact date")), \
                self.assertRaises(ValueError):
            syncer.sync(self.root)
        self.assertFalse(list((self.root / "cctv").rglob("index.md")))

    def test_different_environment_channel_is_rejected_before_network(self):
        with patch.dict(os.environ, {"YOUTUBE_57STORE_CHANNEL_ID": OTHER}), \
                patch.object(syncer, "get_channel_videos") as fetch, \
                self.assertRaisesRegex(ValueError, "verified configuration"):
            syncer.sync(self.root)
        fetch.assert_not_called()

    def test_atomic_save_never_replaces_a_concurrent_editorial_file(self):
        path = self.save(Video("Saved title", FIRST, "2026-10-01T00:00:00Z"), body="Original note\n")
        meta, _ = read_frontmatter(path)
        meta["title"] = "Attempted replacement"
        before = path.read_bytes()
        with self.assertRaises(FileExistsError):
            syncer.save_new(path, meta)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(list(path.parent.glob(".cctv-*")))


if __name__ == "__main__":
    unittest.main()

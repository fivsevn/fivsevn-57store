"""Exercise committed text revisions, retries, merges and atomic publication."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import import_sys as publisher
from site_post_metadata import dump_frontmatter, read_frontmatter, validate_metadata


class SysImportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.name", "SYS publishing test")
        self.git("config", "user.email", "sys@example.invalid")
        shutil.copytree(ROOT / "schemas", self.root / "schemas")
        self.trigger("Existing old terminal line\n原来的片段\n")
        self.baseline = self.commit("Existing source")
        publisher.initialize(self.root)
        self.commit("Initialize SYS publishing state")

    def git(self, *args, env=None):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.PIPE, env=env).decode().strip()

    def commit(self, message, date="2026-11-01T01:02:03+00:00"):
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", message,
                 env={**os.environ, "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date})
        return self.git("rev-parse", "HEAD")

    def trigger(self, body, header="wp_status: publish\ncategory: 57storesys\ntimezone: Etc/UTC"):
        path = self.root / publisher.TRIGGER
        path.parent.mkdir(exist_ok=True)
        path.write_text("---\n" + header + "\n---\n" + body)
        return path

    def packages(self):
        return sorted((self.root / "sys").glob("*/*/*/index.md"))

    def test_initialization_does_not_publish_old_text_and_idle_commits_make_no_writes(self):
        before = (self.root / publisher.STATE).read_bytes()
        self.assertEqual(publisher.ingest(self.root), 0)
        (self.root / "notes.md").write_text("Notes only\n")
        self.commit("Update repository docs")
        self.assertEqual(publisher.ingest(self.root), 0)
        self.assertEqual((self.root / publisher.STATE).read_bytes(), before)
        self.assertFalse(self.packages())

    def test_repeated_initialization_never_skips_a_queued_body_revision(self):
        self.trigger("Queued revision\n待发布片段\n")
        uploaded = self.commit("New body")
        original_cursor = publisher.read_state(self.root)["cursor"]
        self.assertEqual(publisher.initialize(self.root, uploaded)["cursor"], original_cursor)
        self.assertEqual(publisher.ingest(self.root), 1)

    def test_exact_commit_time_and_markdown_are_saved_without_reading_worktree(self):
        body = "    indented code\n\n**line two**  \n第三行\n\n- item\n"
        self.trigger(body)
        uploaded = self.commit("Terminal revision", "2026-12-31T17:04:05+00:00")
        self.trigger("Uncommitted later text\n不得发布\n")
        self.assertEqual(publisher.ingest(self.root), 1)
        path = self.packages()[0]
        meta, saved = read_frontmatter(path)
        validate_metadata(meta, site="sys", schema_dir=ROOT / "schemas")
        self.assertEqual(saved, body)
        self.assertEqual(meta["title"], "[2027-01-01 01:04]")
        self.assertEqual(meta["extra"]["published_at"], "2027-01-01T01:04:05+08:00")
        self.assertEqual((meta["module"], meta["submodule"], meta["source_of_truth"]), ("57store", "sys", "site"))
        key = uploaded + ":" + publisher.TRIGGER
        suffix = hashlib.sha256(key.encode()).hexdigest()[:12]
        self.assertEqual(path.relative_to(self.root).as_posix(), f"sys/2027/01/2027-01-01-010405-{suffix}/index.md")
        self.assertNotIn("wp_status", meta["extra"])
        self.assertNotIn("category", meta["extra"])
        self.assertNotIn("timezone", meta["extra"])
        self.assertEqual(publisher.read_state(self.root)["events"][key]["body_sha256"], hashlib.sha256(body.encode()).hexdigest())

    def test_metadata_only_empty_and_deleted_inputs_are_consumed_without_posts(self):
        self.trigger("Existing old terminal line\n原来的片段\n", "wp_status: draft\ntimezone: Asia/Shanghai")
        changed = self.commit("Metadata only")
        self.assertEqual(publisher.ingest(self.root), 0)
        self.assertEqual(publisher.read_state(self.root)["cursor"], changed)
        self.trigger("\n \n")
        empty = self.commit("Clear trigger")
        self.assertEqual(publisher.ingest(self.root), 0)
        self.assertEqual(publisher.read_state(self.root)["cursor"], empty)
        (self.root / publisher.TRIGGER).unlink()
        deleted = self.commit("Delete trigger")
        self.assertEqual(publisher.ingest(self.root), 0)
        self.assertEqual(publisher.read_state(self.root)["cursor"], deleted)
        self.assertFalse(self.packages())

    def test_all_queued_body_revisions_keep_original_timestamps_and_controls(self):
        self.trigger("First new body\n第一则\n", "wp_status: draft\nvisibility: private")
        first = self.commit("Draft body", "2026-10-31T03:00:00+00:00")
        self.trigger("Second new body\n第二则\n", "status: published\ntitle: Authored title")
        second = self.commit("Published body", "2026-11-01T04:00:00+00:00")
        self.assertEqual(publisher.ingest(self.root), 2)
        by_body = {read_frontmatter(p)[1]: read_frontmatter(p)[0] for p in self.packages()}
        self.assertEqual(by_body["First new body\n第一则\n"]["status"], "draft")
        self.assertEqual(by_body["First new body\n第一则\n"]["visibility"], "private")
        self.assertEqual(by_body["Second new body\n第二则\n"]["title"], "Authored title")
        self.assertEqual(list(publisher.read_state(self.root)["events"]), [first + ":" + publisher.TRIGGER, second + ":" + publisher.TRIGGER])

    def test_retry_and_rewound_cursor_preserve_saved_title_body_and_hidden_status(self):
        self.trigger("New terminal fragment\n新片段\n")
        uploaded = self.commit("Body update")
        self.assertEqual(publisher.ingest(self.root), 1)
        path = self.packages()[0]
        meta, body = read_frontmatter(path)
        meta.update(title="Edited saved title", status="hidden")
        path.write_text(dump_frontmatter(meta) + "Hand-edited saved body\n")
        expected = path.read_bytes()
        self.assertEqual(publisher.ingest(self.root), 0)
        state = publisher.read_state(self.root)
        state["cursor"] = self.baseline
        (self.root / publisher.STATE).write_text(json.dumps(state))
        self.assertEqual(publisher.ingest(self.root), 0)
        self.assertEqual(path.read_bytes(), expected)
        self.assertIn(uploaded + ":" + publisher.TRIGGER, publisher.read_state(self.root)["events"])

    def test_reverting_after_a_different_body_is_a_new_deliberate_post(self):
        self.trigger("Fragment A\n片段甲\n")
        self.commit("A")
        self.trigger("Fragment B\n片段乙\n")
        self.commit("B")
        self.trigger("Fragment A\n片段甲\n")
        self.commit("A again")
        self.assertEqual(publisher.ingest(self.root), 3)
        self.assertEqual(len(self.packages()), 3)
        self.assertEqual(sum(read_frontmatter(p)[1] == "Fragment A\n片段甲\n" for p in self.packages()), 2)

    def test_merge_inherited_body_keeps_its_original_commit_instead_of_republishing(self):
        self.git("checkout", "--quiet", "-b", "phone")
        self.trigger("Phone terminal fragment\n手机片段\n")
        uploaded = self.commit("Phone body", "2026-10-31T06:07:08+00:00")
        self.git("checkout", "--quiet", "main")
        (self.root / "notes.md").write_text("Main notes\n")
        self.commit("Main docs")
        self.git("merge", "--quiet", "--no-ff", "phone", "-m", "Merge phone")
        self.assertEqual(publisher.ingest(self.root), 1)
        state = publisher.read_state(self.root)
        self.assertEqual(list(state["events"]), [uploaded + ":" + publisher.TRIGGER])
        self.assertEqual(read_frontmatter(self.packages()[0])[0]["extra"]["published_at"], "2026-10-31T14:07:08+08:00")

    def test_merge_accepts_cursor_from_second_parent_without_duplicate_publication(self):
        self.git("checkout", "--quiet", "-b", "phone")
        (self.root / "phone.txt").write_text("Phone work\n")
        self.commit("Phone work")
        self.git("checkout", "--quiet", "main")
        self.trigger("Already published body\n已发布的片段\n")
        main_upload = self.commit("Main publication")
        self.assertEqual(publisher.ingest(self.root), 1)
        self.commit("Save published state and package")
        self.git("checkout", "--quiet", "phone")
        self.git("merge", "--quiet", "--no-ff", "main", "-m", "Merge published main")
        self.assertEqual(publisher.read_state(self.root)["cursor"], main_upload)
        self.trigger("Later phone body\n随后手机片段\n")
        phone_upload = self.commit("Phone publication")
        self.assertEqual(publisher.ingest(self.root), 1)
        self.assertEqual({v["commit"] for v in publisher.read_state(self.root)["events"].values()}, {main_upload, phone_upload})
        self.assertEqual(len(self.packages()), 2)

    def test_bad_batch_does_not_partially_install_posts_or_advance_cursor(self):
        before = (self.root / publisher.STATE).read_bytes()
        self.trigger("Good body\n有效片段\n")
        self.commit("Valid body")
        self.trigger("Bad explicit status\n无效状态\n", "status: not-a-status")
        self.commit("Invalid body metadata")
        with self.assertRaises(ValueError):
            publisher.ingest(self.root)
        self.assertFalse(self.packages())
        self.assertEqual((self.root / publisher.STATE).read_bytes(), before)

    def test_failed_state_replace_rolls_back_installed_new_packages(self):
        self.trigger("Queued body\n排队片段\n")
        self.commit("New fragment")
        before = (self.root / publisher.STATE).read_bytes()
        with patch.object(publisher.os, "replace", side_effect=OSError("write failed")), self.assertRaises(OSError):
            publisher.ingest(self.root)
        self.assertFalse(self.packages())
        self.assertEqual((self.root / publisher.STATE).read_bytes(), before)

    def test_missing_and_nonancestor_cursor_fail_without_replay(self):
        state = publisher.read_state(self.root)
        original = deepcopy(state)
        state["cursor"] = "0" * 40
        (self.root / publisher.STATE).write_text(json.dumps(state))
        with self.assertRaisesRegex(ValueError, "missing"):
            publisher.ingest(self.root)
        (self.root / publisher.STATE).write_text(json.dumps(original))
        self.git("checkout", "--quiet", "-b", "unmerged")
        (self.root / "side.txt").write_text("Side branch\n")
        unmerged = self.commit("Unmerged work")
        self.git("checkout", "--quiet", "main")
        original["cursor"] = unmerged
        (self.root / publisher.STATE).write_text(json.dumps(original))
        with self.assertRaisesRegex(ValueError, "not an ancestor"):
            publisher.ingest(self.root)
        self.assertFalse(self.packages())

    def test_stage_owns_only_new_packages_and_ledger_and_never_stages_saved_edits(self):
        self.trigger("New body\n新片段\n")
        self.commit("Body update")
        (self.root / "unrelated.txt").write_text("Unrelated untracked file\n")
        self.assertEqual(publisher.ingest(self.root, stage=True), 1)
        staged = self.git("diff", "--cached", "--name-only").splitlines()
        self.assertEqual(set(staged), {publisher.STATE, self.packages()[0].relative_to(self.root).as_posix()})
        self.commit("Save generated SYS package")
        path = self.packages()[0]
        path.write_text(path.read_text() + "Manual unpublished edit\n")
        self.assertEqual(publisher.ingest(self.root, stage=True), 0)
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "")

    def test_symlink_trigger_and_symlink_publication_paths_are_rejected(self):
        trigger = self.root / publisher.TRIGGER
        trigger.unlink()
        (self.root / "outside.md").write_text("Unsafe body\n")
        trigger.symlink_to(self.root / "outside.md")
        self.commit("Unsafe symlink trigger")
        with self.assertRaisesRegex(ValueError, "regular Markdown"):
            publisher.ingest(self.root)
        with self.assertRaisesRegex(ValueError, "Unsafe SYS"):
            publisher.safe_path(self.root, "sys/../../outside")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Tests for decode detection, archive ingest, and the explorer catalog."""

import json
import sys
import unittest
from pathlib import Path

from ingest.archive import load_archive_posts, tweet_to_record
from ingest.catalog import build_catalog, merge_inbox, record_fingerprint, save_inbox, sha256_file
from ingest.detect import score_decode
from ingest.snowflake import datetime_from_snowflake, tweet_id_from_url


FIXTURE = Path("tests/fixtures/tweets_sample.js")


class DetectTests(unittest.TestCase):
    def test_image_decode_with_brackets_and_keyword(self):
        verdict = score_decode({
            "text": "ENOU[G]H IS EN[O]UGH PATRIOTS",
            "xGraphicURL": "https://pbs.twimg.com/media/example.jpg",
        })
        self.assertGreaterEqual(verdict["score"], 0.55)
        self.assertTrue(verdict["is_decode"])
        self.assertIn("has_media", verdict["reasons"])
        self.assertIn("bracket_letters", verdict["reasons"])

    def test_plain_reply_is_rejected(self):
        verdict = score_decode({
            "text": "heading to lunch",
            "is_reply": True,
        })
        self.assertFalse(verdict["is_decode"])

    def test_retweet_is_rejected(self):
        verdict = score_decode({
            "text": "RT @someone: PATRIOTS [Q]",
            "xGraphicURL": "https://example.com/a.jpg",
            "is_retweet": True,
        })
        self.assertEqual(verdict["score"], 0.0)
        self.assertFalse(verdict["is_decode"])


class ArchiveTests(unittest.TestCase):
    def test_parse_official_tweets_js(self):
        posts = load_archive_posts(FIXTURE)
        self.assertEqual(len(posts), 3)
        by_id = {item["tweet_id"]: item for item in posts}
        self.assertTrue(by_id["1999999999999999999"]["is_decode"])
        self.assertFalse(by_id["1888888888888888888"]["is_decode"])
        self.assertTrue(by_id["1999999999999999999"]["xGraphicURL"].endswith("example-future.jpg"))

    def test_tweet_to_record_uses_media(self):
        record = tweet_to_record({
            "id_str": "42",
            "created_at": "Tue Aug 19 18:00:00 +0000 2025",
            "full_text": "Q CLEARANCE PATRIOT",
            "entities": {"media": [{"media_url_https": "https://x.test/a.jpg", "type": "photo"}]},
        })
        self.assertEqual(record["xPostURL"], "https://x.com/areveur51/status/42")
        self.assertTrue(record["is_decode"])


class SnowflakeTests(unittest.TestCase):
    def test_tweet_id_and_date_from_existing_url(self):
        url = "https://x.com/areveur51/status/1785147128408403969?s=61"
        tweet_id = tweet_id_from_url(url)
        self.assertEqual(tweet_id, "1785147128408403969")
        created = datetime_from_snowflake(tweet_id)
        self.assertEqual(created.year, 2024)
        self.assertEqual(created.month, 4)


class CatalogTests(unittest.TestCase):
    def test_catalog_includes_confirmed_dates_and_keywords(self):
        catalog = build_catalog()
        self.assertGreaterEqual(catalog["counts"]["confirmed"], 100)
        self.assertEqual(catalog["counts"]["keywords"], 18)
        self.assertTrue(catalog["range"]["min"].startswith("2024-04"))
        greatest = next(item for item in catalog["decodes"] if item["id"] == "greatestfear")
        self.assertEqual(greatest["status"], "confirmed")
        self.assertTrue(greatest["created_at"].startswith("2024-06"))
        self.assertTrue(greatest["xGraphicURL"])
        self.assertTrue(greatest["media"])
        self.assertTrue(any(item["id"] == "kw-PATRIOTS" for item in catalog["keywords"]))

    def test_merge_inbox_skips_existing_and_adds_new(self):
        original = json.loads(Path("data/inbox.json").read_text())
        try:
            save_inbox([])
            posts = load_archive_posts(FIXTURE)
            stats = merge_inbox(posts)
            self.assertEqual(stats["added"], 2)
            inbox = json.loads(Path("data/inbox.json").read_text())
            ids = {item["tweet_id"] for item in inbox}
            self.assertNotIn("1801729790577086752", ids)
            self.assertIn("1999999999999999999", ids)
            first = Path("data/inbox.json").read_text()
            again = merge_inbox(posts)
            self.assertEqual(again["added"], 0)
            self.assertEqual(again["updated"], 0)
            self.assertGreaterEqual(again["unchanged"], 1)
            self.assertFalse(again["changed"])
            self.assertEqual(Path("data/inbox.json").read_text(), first)
        finally:
            save_inbox(original)

    def test_reimport_keeps_protected_status(self):
        original = json.loads(Path("data/inbox.json").read_text())
        try:
            save_inbox([])
            posts = load_archive_posts(FIXTURE)
            merge_inbox(posts)
            inbox = json.loads(Path("data/inbox.json").read_text())
            target = next(item for item in inbox if item["tweet_id"] == "1999999999999999999")
            target["status"] = "confirmed"
            save_inbox(inbox)
            again = merge_inbox(posts)
            self.assertEqual(again["added"], 0)
            refreshed = json.loads(Path("data/inbox.json").read_text())
            kept = next(item for item in refreshed if item["tweet_id"] == "1999999999999999999")
            self.assertEqual(kept["status"], "confirmed")
            self.assertEqual(record_fingerprint(target), record_fingerprint(kept))
        finally:
            save_inbox(original)

    def test_archive_file_hash_is_stable(self):
        self.assertEqual(sha256_file(FIXTURE), sha256_file(FIXTURE))


class ExplorerRouteTests(unittest.TestCase):
    def setUp(self):
        import main
        self.client = main.app.test_client()

    def test_explorer_is_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        body = response.data.decode("utf-8", errors="replace")
        self.assertIn("Decode Explorer", body)
        self.assertIn("id=\"stage\"", body)
        self.assertIn("id=\"post-view\"", body)
        self.assertIn("X POST", body)

    def test_catalog_api(self):
        response = self.client.get("/api/catalog")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["account"], "areveur51")
        self.assertGreaterEqual(len(payload["decodes"]), 100)

    def test_archive_upload(self):
        original = json.loads(Path("data/inbox.json").read_text())
        original_state = Path("data/ingest_state.json").read_text()
        try:
            save_inbox([])
            with FIXTURE.open("rb") as handle:
                response = self.client.post(
                    "/api/ingest/archive",
                    data={"archive": (handle, "tweets.js")},
                )
            self.assertEqual(response.status_code, 200)
            payload = response.get_json()
            self.assertTrue(payload["ok"])
            self.assertGreaterEqual(payload["decodes"], 1)
            self.assertGreaterEqual(payload["added"], 1)
            with FIXTURE.open("rb") as handle:
                second = self.client.post(
                    "/api/ingest/archive",
                    data={"archive": (handle, "tweets.js")},
                )
            replay = second.get_json()
            self.assertEqual(second.status_code, 200)
            self.assertEqual(replay["added"], 0)
            self.assertFalse(replay["changed"])
            self.assertIn("already applied", replay["message"])
        finally:
            save_inbox(original)
            Path("data/ingest_state.json").write_text(original_state)

    def test_sync_without_token(self):
        response = self.client.post("/api/sync", json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "missing_token")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

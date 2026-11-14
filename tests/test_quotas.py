import json
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.collectors.quotas import QuotaCollector


class QuotaCollectorTests(unittest.TestCase):
    def test_fresh_cache_and_missing_window(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "cache.json"
            path.write_text(json.dumps({
                "updated_unix": time.time(), "poll_ok": True,
                "data": {"codex": {"session": {"percentage": 25, "available": True}}},
            }), encoding="utf-8")
            quotas = QuotaCollector(path).collect()
            self.assertEqual(quotas[1].session_remaining, 75)
            self.assertIsNone(quotas[1].weekly_remaining)
            self.assertIsNone(quotas[0].session_remaining)

    def test_stale_failed_and_corrupt_cache_are_unavailable(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "cache.json"
            cases = [
                json.dumps({"updated_unix": time.time() - 601, "poll_ok": True}),
                json.dumps({"updated_unix": time.time(), "poll_ok": False}),
                "{",
            ]
            for content in cases:
                path.write_text(content, encoding="utf-8")
                quotas = QuotaCollector(path, interval=0).collect()
                self.assertTrue(all(q.session_remaining is None and q.weekly_remaining is None for q in quotas))


if __name__ == "__main__":
    unittest.main()

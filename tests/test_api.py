import json
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app import make_server, validate_title


class ValidationTests(unittest.TestCase):
    def test_strip_spaces(self):
        self.assertEqual(validate_title("  Belajar CI  "), "Belajar CI")

    def test_invalid_inputs(self):
        for value in [None, 123, [], {}, "", "   ", "x" * 121]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_title(value)

    def test_unicode_title(self):
        title = "Belajar otomasi — selesai ✅"
        self.assertEqual(validate_title(title), title)

    def test_boundary(self):
        self.assertEqual(len(validate_title("x" * 120)), 120)


class APITests(unittest.TestCase):
    def test_long_title_rejected_without_saving(self):
        status, before = self.request("/tasks")
        self.assertEqual(status, 200)

        status, response = self.request(
            "/tasks", "POST", {"title": "x" * 121}
        )

        self.assertEqual(status, 400)
        self.assertIn("error", response)

        status, after = self.request("/tasks")
        self.assertEqual(status, 200)
        self.assertEqual(after["tasks"], before["tasks"])
    def test_unicode_title_round_trip(self):
        title = "Belajar otomasi — selesai ✅"

        status, created = self.request(
            "/tasks", "POST", {"title": title}
        )

        self.assertEqual(status, 201)
        self.assertEqual(created["title"], title)

        status, listing = self.request("/tasks")

        self.assertEqual(status, 200)
        self.assertIn(created, listing["tasks"])
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.folder.name) / "test.db")
        self.server = make_server(port=0, db_path=self.db_path, version="test-v1")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.folder.cleanup()

    def request(self, path, method="GET", body=None, raw=None):
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        req = Request(self.url + path, data=data, method=method, headers={"Content-Type": "application/json"})
        try:
            response = urlopen(req, timeout=3)
        except HTTPError as exc:
            response = exc
        with response:
            return response.status, json.load(response)

    def test_health(self):
        self.assertEqual(self.request("/health"), (200, {"status": "alive"}))

    def test_ready(self):
        self.assertEqual(self.request("/ready")[0], 200)

    def test_readiness_detects_broken_schema(self):
        db = sqlite3.connect(self.db_path)
        try:
            db.execute("DROP TABLE tasks")
            db.commit()
        finally:
            db.close()
        self.assertEqual(self.request("/ready")[0], 503)
        self.assertEqual(self.request("/health")[0], 200)

    def test_version(self):
        self.assertEqual(self.request("/version")[1]["version"], "test-v1")

    def test_create_list_delete(self):
        status, task = self.request("/tasks", "POST", {"title": "  Belajar CI  "})
        self.assertEqual(status, 201)
        self.assertEqual(task["title"], "Belajar CI")
        self.assertIn(task, self.request("/tasks")[1]["tasks"])
        self.assertEqual(self.request(f"/tasks/{task['id']}", "DELETE")[0], 200)
        self.assertEqual(self.request("/tasks")[1]["tasks"], [])

    def test_invalid_title_returns_400(self):
        self.assertEqual(self.request("/tasks", "POST", {"title": "  "})[0], 400)
        self.assertEqual(self.request("/tasks")[1]["tasks"], [])

    def test_malformed_json_returns_400(self):
        self.assertEqual(self.request("/tasks", "POST", raw=b"{broken")[0], 400)

    def test_array_returns_400(self):
        self.assertEqual(self.request("/tasks", "POST", raw=b"[]")[0], 400)

    def test_missing_routes(self):
        self.assertEqual(self.request("/unknown")[0], 404)
        self.assertEqual(self.request("/tasks/999", "DELETE")[0], 404)

    def test_sql_looking_title_is_plain_data(self):
        title = "'); DROP TABLE tasks; --"
        self.assertEqual(self.request("/tasks", "POST", {"title": title})[0], 201)
        self.assertEqual(self.request("/tasks")[1]["tasks"][0]["title"], title)

    def test_body_limit(self):
        self.assertEqual(self.request("/tasks", "POST", raw=b"x" * 4097)[0], 413)


if __name__ == "__main__":
    unittest.main()

"""API pembelajaran lokal. Tidak dirancang sebagai HTTP server production."""
import json
import os
import sqlite3
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


def validate_title(value):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 120:
        raise ValueError("title harus berupa teks 1–120 karakter")
    return value.strip()


def initialize(db_path):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as db:
        db.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL)")
        db.commit()


def make_server(host="127.0.0.1", port=8080, db_path="data/tasks.db", version="dev", fail_ready=False):
    initialize(db_path)

    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, body):
            payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/health":
                return self.reply(200, {"status": "alive"})
            if path == "/version":
                return self.reply(200, {"version": version})
            if path == "/ready":
                if fail_ready:
                    return self.reply(503, {"status": "not-ready", "reason": "lab fault"})
                try:
                    with closing(sqlite3.connect(db_path)) as db:
                        db.execute("SELECT COUNT(*) FROM tasks").fetchone()
                    return self.reply(200, {"status": "ready"})
                except sqlite3.Error:
                    return self.reply(503, {"status": "not-ready"})
            if path == "/tasks":
                with closing(sqlite3.connect(db_path)) as db:
                    rows = db.execute("SELECT id, title FROM tasks ORDER BY id").fetchall()
                return self.reply(200, {"tasks": [{"id": r[0], "title": r[1]} for r in rows]})
            return self.reply(404, {"error": "not found"})

        def do_POST(self):
            if urlsplit(self.path).path != "/tasks":
                return self.reply(404, {"error": "not found"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 1 or length > 4096:
                    return self.reply(413, {"error": "body harus 1–4096 byte"})
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("body harus JSON object")
                title = validate_title(payload.get("title"))
            except (ValueError, UnicodeDecodeError) as exc:
                return self.reply(400, {"error": str(exc)})
            with closing(sqlite3.connect(db_path)) as db:
                cursor = db.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
                task_id = cursor.lastrowid
                db.commit()
            return self.reply(201, {"id": task_id, "title": title})

        def do_DELETE(self):
            parts = urlsplit(self.path).path.strip("/").split("/")
            if len(parts) != 2 or parts[0] != "tasks" or not parts[1].isascii() or not parts[1].isdigit():
                return self.reply(404, {"error": "not found"})
            if len(parts[1]) > 18:
                return self.reply(404, {"error": "not found"})
            with closing(sqlite3.connect(db_path)) as db:
                cursor = db.execute("DELETE FROM tasks WHERE id = ?", (int(parts[1]),))
                removed = cursor.rowcount
                db.commit()
            return self.reply(200 if removed else 404, {"deleted": bool(removed)})

        def log_message(self, fmt, *args):
            print(json.dumps({"version": version, "message": fmt % args}), flush=True)

    return ThreadingHTTPServer((host, port), Handler)


if __name__ == "__main__":
    server = make_server(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8080")),
        db_path=os.getenv("DB_PATH", "data/tasks.db"),
        version=os.getenv("APP_VERSION", "dev"),
        fail_ready=os.getenv("FAIL_READY", "0") == "1",
    )
    print("Task API listening", server.server_address, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

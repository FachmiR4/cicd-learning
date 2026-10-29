"""Smoke test membuat satu data sintetis dan menghapusnya kembali; gunakan di lab."""
import argparse
import json
import sys
import time
import uuid
from urllib.error import URLError
from urllib.request import Request, urlopen


def smoke(base_url, expected_version=None):
    def request(path, method="GET", body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = Request(base_url.rstrip("/") + path, data=data, method=method,
                      headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=3) as response:
            return response.status, json.load(response)

    for attempt in range(20):
        try:
            request("/ready")
            break
        except (URLError, TimeoutError, ConnectionError):
            if attempt == 19:
                raise RuntimeError("Layanan belum ready; periksa log dan konfigurasi")
            time.sleep(0.5)
    _, info = request("/version")
    if expected_version is not None and info.get("version") != expected_version:
        raise RuntimeError(f"Versi salah: {info}; diharapkan {expected_version}")
    title = "smoke-" + str(uuid.uuid4())
    status, created = request("/tasks", "POST", {"title": title})
    if status != 201:
        raise RuntimeError("Pembuatan task gagal")
    try:
        _, listing = request("/tasks")
        if created not in listing["tasks"]:
            raise RuntimeError("Task tidak ditemukan setelah dibuat")
    finally:
        request(f"/tasks/{created['id']}", "DELETE")
    print("SMOKE OK", info)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url", nargs="?", default="http://127.0.0.1:8080")
    parser.add_argument("--expect-version")
    args = parser.parse_args()
    try:
        smoke(args.base_url, args.expect_version)
    except Exception as exc:
        print(f"SMOKE FAILED: {exc}", file=sys.stderr)
        sys.exit(1)

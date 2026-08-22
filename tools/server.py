#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CH Travel OS 2.0 - 跨旅程共用本機伺服器與視覺化編輯器
"""

import os
import sys
import json
import shutil
import mimetypes
import urllib.parse
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

# 確保 WebP 與現代 Web 資源之 MIME Type 100% 正確
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/json", ".json")
mimetypes.add_type("image/svg+xml", ".svg")

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
TRIPS_DIR = BASE_DIR / "trips"
PORT = 8080


class TravelOSMultiTripHandler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".webp": "image/webp",
        ".js": "text/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".svg": "image/svg+xml",
        ".html": "text/html; charset=utf-8",
    }
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # API: 列出所有已建置與籌備中的旅程
        if path == "/api/list-trips":
            trips = [d.name for d in TRIPS_DIR.iterdir() if d.is_dir()] if TRIPS_DIR.exists() else []
            self.send_json({"success": True, "trips": trips})
            return

        super().do_GET()

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)


def main():
    server_address = ("127.0.0.1", PORT)
    handler_class = partial(TravelOSMultiTripHandler, directory=str(DOCS_DIR))
    httpd = ThreadingHTTPServer(server_address, handler_class)
    print(f"============================================================")
    print(f"🌍 CH Travel OS 2.0 Multi-Trip Server Running!")
    print(f"🌐 Portal URL : http://127.0.0.1:{PORT}/")
    print(f"============================================================")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
        httpd.server_close()


if __name__ == "__main__":
    main()

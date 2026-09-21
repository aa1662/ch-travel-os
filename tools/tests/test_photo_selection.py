"""The editor must never publish a master while the author is still choosing photos."""

import json
import sys
import tempfile
import threading
import unittest
import urllib.request
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from PIL import Image

TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
import image_pipeline  # noqa: E402
import server  # noqa: E402
import build_trip_html  # noqa: E402


class PhotoSelectionFlowTest(unittest.TestCase):
    def test_save_is_private_and_finalize_publishes_only_selected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            trip = "selection-test"
            trip_dir = root / "trips" / trip
            master_dir = root / "masters" / trip / "day-01"
            docs_dir = root / "docs"
            master_dir.mkdir(parents=True)
            trip_dir.mkdir(parents=True)
            docs_dir.mkdir()
            (trip_dir / "blog-migration.json").write_text(
                json.dumps({"dest": trip, "entries": [{
                    "id": "new-story", "title": "New story", "image_folder": "day-01",
                    "status": "draft", "source": "trips/selection-test/sources/blog/new.html",
                    "output": "docs/selection-test/blog/new.html",
                }]}),
                encoding="utf-8",
            )
            for name in ("20241101_100000.jpg", "20241101_110000.jpg"):
                Image.new("RGB", (1000, 700), (20, 90, 140)).save(master_dir / name)

            patches = [
                patch.object(server, "BASE_DIR", root),
                patch.object(server, "TRIPS_DIR", trip_dir.parent),
                patch.object(server, "DOCS_DIR", docs_dir),
                patch.object(image_pipeline, "BASE_DIR", root),
                patch.object(image_pipeline, "MASTERS_DIR", root / "masters"),
                patch.object(image_pipeline, "DOCS_DIR", docs_dir),
                patch.object(build_trip_html, "BASE_DIR", root),
                patch.object(build_trip_html, "TRIPS_DIR", trip_dir.parent),
                patch.object(build_trip_html, "DOCS_DIR", docs_dir),
                patch.object(build_trip_html, "CORE_DIR", root / "core"),
            ]
            for item in patches:
                item.start()
            try:
                handler = partial(server.TravelOSMultiTripHandler, directory=str(docs_dir))
                httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
                worker = threading.Thread(target=httpd.serve_forever, daemon=True)
                worker.start()
                base = f"http://127.0.0.1:{httpd.server_port}"
                try:
                    with urllib.request.urlopen(base + "/api/list-trips") as response:
                        journey = next(t for t in json.load(response)["trips"] if t["id"] == trip)
                    self.assertTrue(journey["blogs"][0]["draft"])

                    def post(path, payload):
                        request = urllib.request.Request(
                            base + path,
                            json.dumps(payload).encode("utf-8"),
                            {"Content-Type": "application/json"},
                        )
                        with urllib.request.urlopen(request) as response:
                            return json.load(response)

                    with urllib.request.urlopen(
                        base + "/api/list-images?trip=selection-test&folder=day-01"
                    ) as response:
                        library = json.load(response)["images"]
                    self.assertEqual(len(library), 2)
                    self.assertTrue(all(img["master_available"] for img in library))
                    self.assertTrue(all(not img["published"] for img in library))

                    saved = post("/api/save-photo-selection", {
                        "trip": trip, "entry": "new-story",
                        "images": [{
                            "folder": "day-01", "filename": "20241101_100000.jpg",
                            "body": True, "gallery": False,
                        }],
                    })
                    self.assertEqual(saved["selection"]["status"], "draft")
                    self.assertFalse((docs_dir / trip / "image-manifest.json").exists())
                    self.assertEqual(len(list(docs_dir.rglob("*.webp"))), 0)

                    finalized = post("/api/finalize-photo-selection", {
                        "trip": trip, "entry": "new-story",
                    })
                    self.assertEqual(finalized["selection"]["status"], "finalized")
                    manifest = json.loads((docs_dir / trip / "image-manifest.json").read_text())
                    self.assertEqual(set(manifest["images"]), {"day-01/20241101_100000.jpg"})
                    self.assertTrue(list((docs_dir / trip / "images" / "day-01").glob("*.webp")))
                    build_trip_html.build_trip(trip)
                    self.assertFalse((docs_dir / trip / "blog" / "new.html").exists())
                finally:
                    httpd.shutdown()
                    httpd.server_close()
                    worker.join(timeout=3)
            finally:
                for item in reversed(patches):
                    item.stop()


if __name__ == "__main__":
    unittest.main()

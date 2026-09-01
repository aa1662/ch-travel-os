#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CH Travel OS 2.0 - 跨旅程共用本機伺服器與視覺化編輯器後端 API
"""

import os
import sys
import json
import re
import shutil
import mimetypes
import traceback
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
TOOLS_DIR = BASE_DIR / "tools"
CORE_DIR = BASE_DIR / "core"
PORT = 8080
WRITABLE_TRIP_SUBDIRS = (
    ("sources", "blog"),
    ("sources", "timeline"),
    ("previews",),
)

# 確保工具鏈可被模組動態引入
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

try:
    from build_trip_html import build_trip
    from build_timeline_html import build_timelines
except Exception as ie:
    print(f"Warning: Could not import build modules at startup: {ie}", flush=True)


def is_relative_to(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def get_trip_dest(trip_slug):
    """Resolve the public Journey namespace from its migration config."""
    trip_dir = TRIPS_DIR / trip_slug
    for config_name in ("blog-migration.json", "timeline-migration.json"):
        config_path = trip_dir / config_name
        if not config_path.exists():
            continue
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"無法讀取旅程設定 {config_path}: {exc}") from exc
        dest = data.get("dest")
        if dest:
            if Path(dest).name != dest or dest in {".", ".."}:
                raise ValueError(f"非法 Journey dest: {dest}")
            return dest
    return trip_slug


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
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            query = urllib.parse.parse_qs(parsed.query)

            # 本機專用 Editor：來源保留在 core/，不得複製至公開 docs/。
            if path == "/core/editor.html":
                self.send_file(CORE_DIR / "editor.html")
                return

            # 0. 靜態文件與 /docs/ 容錯路由
            if path.startswith("/docs/"):
                clean_rel = path[len("/docs/"):].lstrip("/")
                direct_file = DOCS_DIR / clean_rel
                if direct_file.exists() and direct_file.is_file():
                    self.send_file(direct_file)
                    return

            # 0.1 靜態圖片智能路由 (支援跨旅程 /images/ 與 .jpg 自動解析至對應 WebP derivative)
            if "/images/" in path or path.lower().endswith((".webp", ".jpg", ".png", ".heic")):
                clean_rel = path.lstrip("/")
                direct_file = DOCS_DIR / clean_rel
                
                # 若直接路徑不存在，嘗試在各旅程資料夾下尋找
                if not direct_file.exists() or not direct_file.is_file():
                    trip_dirs = [d for d in DOCS_DIR.iterdir() if d.is_dir() and d.name != "core"]
                    stem = Path(clean_rel).stem
                    parts = Path(clean_rel).parts
                    
                    # 判斷是否指定特定旅程 (如 2025-2026-beijing)
                    target_trip_dir = next((d for d in trip_dirs if d.name in parts), None)
                    search_dirs = [target_trip_dir] if target_trip_dir else trip_dirs
                    
                    # 找出 subfolder 如 gubei / mutianyu / day-01
                    img_folder = ""
                    if "images" in parts:
                        idx = parts.index("images")
                        if idx + 1 < len(parts):
                            img_folder = parts[idx + 1]
                    
                    for t_dir in search_dirs:
                        if not t_dir:
                            continue
                        # 1. 嘗試直接子路徑
                        cand = t_dir / clean_rel
                        if cand.exists() and cand.is_file():
                            direct_file = cand
                            break
                        if clean_rel.startswith("images/"):
                            cand2 = t_dir / clean_rel
                            if cand2.exists() and cand2.is_file():
                                direct_file = cand2
                                break
                        # 2. 尋找 WebP derivatives
                        if img_folder:
                            folder_path = t_dir / "images" / img_folder
                            if folder_path.exists():
                                matches = list(folder_path.glob(f"{stem}*.webp"))
                                if matches:
                                    pref = next((m for m in matches if "-content-" in m.name or "-desktop-" in m.name or "-thumb-" in m.name or "-lightbox-" in m.name), matches[0])
                                    direct_file = pref
                                    break
                        # 3. 若無特定資料夾，在整個 t_dir / images 遞迴尋找
                        images_dir = t_dir / "images"
                        if images_dir.exists():
                            matches = list(images_dir.rglob(f"{stem}*.webp"))
                            if matches:
                                pref = next((m for m in matches if "-content-" in m.name or "-desktop-" in m.name or "-thumb-" in m.name or "-lightbox-" in m.name), matches[0])
                                direct_file = pref
                                break

                if direct_file.exists() and direct_file.is_file():
                    self.send_file(direct_file)
                    return

            # 1. API: 列出所有已建置與籌備中的旅程與章節
            if path == "/api/list-trips":
                print("--> Handling /api/list-trips", flush=True)
                trips_data = []
                if TRIPS_DIR.exists():
                    for trip_dir in sorted(TRIPS_DIR.iterdir()):
                        if not trip_dir.is_dir():
                            continue
                        trip_slug = trip_dir.name
                        blog_cfg = trip_dir / "blog-migration.json"
                        timeline_cfg = trip_dir / "timeline-migration.json"

                        trip_entry = {
                            "id": trip_slug,
                            "name": trip_slug.replace("-", " ").title(),
                            "dest": get_trip_dest(trip_slug),
                            "hubs": [],
                            "blogs": [],
                            "timelines": [],
                            "previews": []
                        }

                        hub_source = trip_dir / "sources" / "index.html"
                        if hub_source.exists():
                            trip_entry["hubs"].append({
                                "id": "index",
                                "title": "旅程總覽",
                                "file": f"trips/{trip_slug}/sources/index.html",
                                "output": f"docs/{trip_entry['dest']}/index.html",
                                "image_folder": "day-01"
                            })

                        if blog_cfg.exists():
                            try:
                                with open(blog_cfg, "r", encoding="utf-8") as f:
                                    b_data = json.load(f)
                                    trip_entry["dest"] = b_data.get("dest", trip_entry["dest"])
                                    for item in b_data.get("entries", []):
                                        trip_entry["blogs"].append({
                                            "id": item["id"],
                                            "title": item["title"],
                                            "file": item["source"],
                                            "output": item["output"],
                                            "image_folder": item.get("image_folder", item["id"].split("-")[0] + "-" + item["id"].split("-")[1] if "-" in item["id"] else item["id"])
                                        })
                            except Exception as e:
                                print(f"Error reading blog cfg {blog_cfg}: {e}")

                        if timeline_cfg.exists():
                            try:
                                with open(timeline_cfg, "r", encoding="utf-8") as f:
                                    t_data = json.load(f)
                                    trip_entry["dest"] = t_data.get("dest", trip_entry["dest"])
                                    for item in t_data.get("entries", []):
                                        trip_entry["timelines"].append({
                                            "id": item["id"],
                                            "title": item["title"],
                                            "file": item["source"],
                                            "output": item["output"],
                                            "image_folder": item["id"]
                                        })
                            except Exception as e:
                                print(f"Error reading timeline cfg {timeline_cfg}: {e}")

                        # 掃描 previews 目錄
                        preview_dir = trip_dir / "previews"
                        if preview_dir.exists():
                            for p_file in sorted(preview_dir.glob("*.html")):
                                p_id = p_file.stem
                                title = f"改寫預覽: {p_id}"
                                try:
                                    html_text = p_file.read_text(encoding="utf-8")
                                    t_match = re.search(r"<title>(.*?)</title>", html_text)
                                    if t_match:
                                        title = t_match.group(1).split("|")[0].strip()
                                except Exception:
                                    pass
                                
                                img_folder = "day-01"
                                m = re.search(r"day-(\d+)", p_id)
                                if m:
                                    img_folder = f"day-{m.group(1)}"

                                trip_entry["previews"].append({
                                    "id": p_id,
                                    "title": title,
                                    "file": f"trips/{trip_slug}/previews/{p_file.name}",
                                    "output": f"{trip_entry['dest']}/blog/{p_file.name}",
                                    "image_folder": img_folder
                                })

                        trips_data.append(trip_entry)

                self.send_json({"success": True, "trips": trips_data})
                return

            # 2. API: 讀取指定旅程的原始 HTML 手稿 (Source of Truth)
            if path == "/api/load-source":
                trip_slug = query.get("trip", [""])[0]
                rel_file = query.get("file", [""])[0]

                if not trip_slug or not rel_file:
                    self.send_json({"success": False, "error": "缺少 trip 或 file 參數"}, 400)
                    return

                if rel_file.startswith("trips/"):
                    target_path = (BASE_DIR / rel_file).resolve()
                else:
                    target_path = (TRIPS_DIR / trip_slug / rel_file).resolve()

                if not self.is_readable_source_path(trip_slug, target_path):
                    self.send_json({"success": False, "error": "非法存取路徑"}, 403)
                    return

                if not target_path.exists():
                    self.send_json({"success": False, "error": f"檔案不存在: {rel_file}"}, 404)
                    return

                backup_file = target_path.parent / ".backups" / f"{target_path.name}.bak"
                try:
                    content = target_path.read_text(encoding="utf-8")
                    self.send_json({
                        "success": True,
                        "html": content,
                        "trip": trip_slug,
                        "file": rel_file,
                        "has_backup": backup_file.exists()
                    })
                except Exception as e:
                    self.send_json({"success": False, "error": str(e)}, 500)
                return

            # 3. API: 讀取指定旅程該天數的圖片庫 (Image Manifest)
            if path == "/api/list-images":
                trip_slug = query.get("trip", ["2026-germany"])[0]
                folder = query.get("folder", ["day-01"])[0]
                dest = get_trip_dest(trip_slug)

                manifest_path = DOCS_DIR / dest / "image-manifest.json"
                if not manifest_path.exists():
                    self.send_json({"success": False, "error": f"找不到 Image Manifest: {manifest_path}"}, 404)
                    return

                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        m = json.load(f)

                    images_in_folder = []
                    for img_key, item in m.get("images", {}).items():
                        if folder == "all" or f"/{folder}/" in img_key or img_key.startswith(f"{folder}/") or item.get("filename", "").startswith(f"{folder}/") or item.get("original_filename", "").startswith(f"{folder}/"):
                            derivatives = item.get("derivatives", [])
                            thumb = next((d["publicPath"] for d in derivatives if d["profile"] == "thumb"), None)
                            content_p = next((d["publicPath"] for d in derivatives if d["profile"] == "content"), None)
                            desktop = next((d["publicPath"] for d in derivatives if d["profile"] == "desktop"), None)
                            lightbox = next((d["publicPath"] for d in derivatives if d["profile"] == "lightbox"), None)
                            
                            images_in_folder.append({
                                "id": item.get("id", Path(img_key).stem),
                                "original_name": item.get("original_filename", Path(img_key).name),
                                "thumb": thumb or (derivatives[0]["publicPath"] if derivatives else f"{dest}/images/{img_key}"),
                                "content": content_p or (derivatives[0]["publicPath"] if derivatives else f"{dest}/images/{img_key}"),
                                "desktop": desktop or (derivatives[-1]["publicPath"] if derivatives else f"{dest}/images/{img_key}"),
                                "lightbox": lightbox or (derivatives[-1]["publicPath"] if derivatives else f"{dest}/images/{img_key}"),
                                "derivatives": derivatives,
                                "width": item.get("original_width", 1200),
                                "height": item.get("original_height", 800)
                            })

                    self.send_json({
                        "success": True,
                        "trip": trip_slug,
                        "folder": folder,
                        "images": images_in_folder
                    })
                except Exception as e:
                    traceback.print_exc()
                    self.send_json({"success": False, "error": str(e)}, 500)
                return

            super().do_GET()
        except Exception as ex:
            traceback.print_exc()
            self.send_json({"success": False, "error": str(ex)}, 500)

    def do_POST(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path

            if path == "/api/save-source":
                if not self.is_trusted_json_post():
                    self.send_json({"success": False, "error": "非法或跨來源請求"}, 403)
                    return

                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8")
                payload = json.loads(body)

                trip_slug = payload.get("trip")
                rel_file = payload.get("file")
                new_html = payload.get("html")

                if not trip_slug or not rel_file or new_html is None:
                    self.send_json({"success": False, "error": "參數不完整"}, 400)
                    return

                if rel_file.startswith("trips/"):
                    target_path = (BASE_DIR / rel_file).resolve()
                else:
                    target_path = (TRIPS_DIR / trip_slug / rel_file).resolve()

                if not self.is_writable_source_path(trip_slug, target_path):
                    self.send_json({"success": False, "error": "非法存取路徑"}, 403)
                    return

                # 建立備份
                backup_dir = target_path.parent / ".backups"
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_file = backup_dir / f"{target_path.name}.bak"
                if target_path.exists():
                    shutil.copy2(target_path, backup_file)

                # 原子寫入原始手稿 SSoT
                temp_path = target_path.with_suffix(target_path.suffix + ".tmp")
                temp_path.write_text(new_html, encoding="utf-8")
                os.replace(temp_path, target_path)

                # 自動觸發編譯以更新 docs/
                build_msg = ""
                dest_slug = get_trip_dest(trip_slug)
                if "sources/blog" in rel_file:
                    try:
                        build_trip(trip_slug)
                        build_msg = "已同步重新編譯發布版 Blog HTML！"
                    except Exception as be:
                        build_msg = f"檔案已儲存，但 Blog 編譯時發生錯誤: {be}"
                elif rel_file.endswith("sources/index.html") or rel_file.endswith("sources\\index.html"):
                    try:
                        build_trip(trip_slug)
                        build_msg = "已同步重新編譯發布版旅程總覽 HTML！"
                    except Exception as be:
                        build_msg = f"檔案已儲存，但旅程總覽編譯時發生錯誤: {be}"
                elif "sources/timeline" in rel_file:
                    try:
                        build_timelines(trip_slug)
                        build_msg = "已同步重新編譯發布版 Timeline HTML！"
                    except Exception as be:
                        build_msg = f"檔案已儲存，但 Timeline 編譯時發生錯誤: {be}"
                elif "previews" in rel_file:
                    try:
                        dest_file = DOCS_DIR / dest_slug / "blog" / target_path.name
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(target_path, dest_file)
                        build_msg = "已同步更新 docs 預覽版 HTML！"
                    except Exception as pe:
                        build_msg = f"檔案已儲存，但同步 docs 預覽時發生錯誤: {pe}"

                self.send_json({
                    "success": True,
                    "message": f"儲存成功！{build_msg}",
                    "has_backup": True
                })
                return

            if path == "/api/restore-backup":
                if not self.is_trusted_json_post():
                    self.send_json({"success": False, "error": "非法或跨來源請求"}, 403)
                    return

                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8")
                payload = json.loads(body)

                trip_slug = payload.get("trip")
                rel_file = payload.get("file")

                if rel_file.startswith("trips/"):
                    target_path = (BASE_DIR / rel_file).resolve()
                else:
                    target_path = (TRIPS_DIR / trip_slug / rel_file).resolve()

                if not self.is_writable_source_path(trip_slug, target_path):
                    self.send_json({"success": False, "error": "非法存取路徑"}, 403)
                    return

                backup_file = target_path.parent / ".backups" / f"{target_path.name}.bak"

                if not backup_file.exists():
                    self.send_json({"success": False, "error": "找不到可還原的備份檔案"}, 404)
                    return

                shutil.copy2(backup_file, target_path)

                dest_slug = get_trip_dest(trip_slug)
                if "sources/blog" in rel_file:
                    build_trip(trip_slug)
                elif rel_file.endswith("sources/index.html") or rel_file.endswith("sources\\index.html"):
                    build_trip(trip_slug)
                elif "sources/timeline" in rel_file:
                    build_timelines(trip_slug)

                restored_html = target_path.read_text(encoding="utf-8")
                self.send_json({
                    "success": True,
                    "message": "已成功還原至備份版本並重新編譯！",
                    "html": restored_html
                })
                return

            self.send_json({"success": False, "error": "Not Found"}, 404)
        except Exception as ex:
            traceback.print_exc()
            self.send_json({"success": False, "error": str(ex)}, 500)

    def get_content_type(self, file_path):
        suffix = Path(file_path).suffix.lower()
        type_map = {
            ".webp": "image/webp",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
        }
        return type_map.get(suffix, "application/octet-stream")

    def is_readable_source_path(self, trip_slug, target_path):
        if not trip_slug:
            return False
        trip_root = (TRIPS_DIR / trip_slug).resolve()
        return target_path.suffix.lower() == ".html" and is_relative_to(target_path, trip_root)

    def is_writable_source_path(self, trip_slug, target_path):
        if not self.is_readable_source_path(trip_slug, target_path):
            return False
        trip_root = (TRIPS_DIR / trip_slug).resolve()
        hub_source = (trip_root / "sources" / "index.html").resolve()
        if target_path == hub_source:
            return True
        return any(is_relative_to(target_path, trip_root.joinpath(*parts).resolve()) for parts in WRITABLE_TRIP_SUBDIRS)

    def is_trusted_json_post(self):
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            return False

        allowed_hosts = {self.headers.get("Host", ""), f"127.0.0.1:{PORT}", f"localhost:{PORT}"}
        for header_name in ("Origin", "Referer"):
            header_val = self.headers.get(header_name)
            if not header_val:
                continue
            parsed = urllib.parse.urlparse(header_val)
            if parsed.scheme not in ("http", "https"):
                return False
            if parsed.netloc not in allowed_hosts:
                return False
        return True

    def get_content_type(self, file_path):
        ctype, _ = mimetypes.guess_type(str(file_path))
        if ctype:
            if ctype.startswith("text/") or ctype in ("application/json", "application/javascript"):
                return f"{ctype}; charset=utf-8"
            return ctype
        ext = Path(file_path).suffix.lower()
        if ext == ".webp":
            return "image/webp"
        if ext == ".svg":
            return "image/svg+xml"
        if ext in (".html", ".htm"):
            return "text/html; charset=utf-8"
        if ext == ".css":
            return "text/css; charset=utf-8"
        if ext == ".js":
            return "text/javascript; charset=utf-8"
        if ext == ".json":
            return "application/json; charset=utf-8"
        return "application/octet-stream"

    def send_file(self, file_path):
        ctype = self.get_content_type(file_path)
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            traceback.print_exc()
            self.send_error(500, str(e))

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)


def main():
    server_address = ("127.0.0.1", PORT)
    handler_class = partial(TravelOSMultiTripHandler, directory=str(DOCS_DIR))
    ThreadingHTTPServer.allow_reuse_address = True
    httpd = ThreadingHTTPServer(server_address, handler_class)
    print(f"============================================================", flush=True)
    print(f"🌍 CH Travel OS 2.0 Multi-Trip Server & Editor API Running!", flush=True)
    print(f"🌐 Portal URL : http://127.0.0.1:{PORT}/", flush=True)
    print(f"🎨 Editor URL : http://127.0.0.1:{PORT}/core/editor.html", flush=True)
    print(f"============================================================", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down.", flush=True)
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()

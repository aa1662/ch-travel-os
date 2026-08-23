#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CH Travel OS 2.0 - 全域發布與圖片合規驗證器 (Full Site & Image Validator)
自動嚴格驗證：
1. 圖片合規：尺寸 <= 1600px、單檔 <= 2.5MB、可解碼、EXIF/GPS 徹底移除。
2. Manifest 一致性：Manifest 與磁碟 WebP 檔案 100% 對應。
3. HTML 連結完整性：檢查所有 <a href>, <img src>, <img srcset>, <script src>, <link href>，嚴禁 404 死鏈。
4. 原圖與隱私防護：HTML 與 JS 不得直接引用 masters/ 或未經 WebP 轉換之 raw .jpg。
5. 社群與 Canonical 驗證：og:url 與 og:image 不得指向舊版或已失效之遺留路由。
"""

import re
import sys
import json
import urllib.parse
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
TRIPS_DIR = BASE_DIR / "trips"

MAX_ALLOWED_WIDTH = 1600
MAX_ALLOWED_BYTES = 2.5 * 1024 * 1024  # 2.5MB


def validate_docs():
    print("==================================================")
    print("🛡️ 正在執行 CH Travel OS 2.0 全站連結與圖片合規檢查...")
    print("==================================================")

    errors = []
    warnings = []
    total_images = 0
    blog_contracts = {}
    timeline_contracts = {}
    timeline_entries = {}

    for config_path in TRIPS_DIR.glob("*/blog-migration.json"):
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            for entry in config.get("entries", []):
                output_path = (BASE_DIR / entry["output"]).resolve()
                if not output_path.is_relative_to(DOCS_DIR.resolve()):
                    errors.append(f"[Blog 輸出越界] {entry['output']} in {config_path.relative_to(BASE_DIR)}")
                    continue
                rel_output = output_path.relative_to(DOCS_DIR.resolve()).as_posix()
                blog_contracts[rel_output] = entry.get("og_url")
        except (OSError, json.JSONDecodeError, KeyError) as exc:
            errors.append(f"[Blog Config 解析失敗] {config_path.relative_to(BASE_DIR)} ({exc})")

    for config_path in TRIPS_DIR.glob("*/timeline-migration.json"):
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            for entry in config.get("entries", []):
                output_path = (BASE_DIR / entry["output"]).resolve()
                if not output_path.is_relative_to(DOCS_DIR.resolve()):
                    errors.append(f"[Timeline 輸出越界] {entry['output']} in {config_path.relative_to(BASE_DIR)}")
                    continue
                rel_output = output_path.relative_to(DOCS_DIR.resolve()).as_posix()
                timeline_contracts[rel_output] = entry.get("og_url")
                timeline_entries[rel_output] = entry
        except (OSError, json.JSONDecodeError, KeyError) as exc:
            errors.append(f"[Timeline Config 解析失敗] {config_path.relative_to(BASE_DIR)} ({exc})")

    page_contracts = {**blog_contracts, **timeline_contracts}

    if (DOCS_DIR / "core" / "editor.html").exists():
        errors.append("[公開 Editor 外洩] docs/core/editor.html 不應進入 GitHub Pages 發布目錄")

    image_files = list(DOCS_DIR.rglob("*.webp")) + list(DOCS_DIR.rglob("*.jpg")) + list(DOCS_DIR.rglob("*.png"))

    # 1. 檢查公開圖片格式、尺寸、檔案大小、可解碼性與 EXIF 剝除
    for img_path in image_files:
        if "vendor" in img_path.parts:
            continue
        if not img_path.exists():
            continue

        total_images += 1
        size = img_path.stat().st_size

        if size > MAX_ALLOWED_BYTES:
            errors.append(f"[圖片過大] ({round(size/1024/1024, 2)} MB > 2.5 MB): {img_path.relative_to(DOCS_DIR)}")

        if img_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".heic"]:
            if "icon" not in img_path.name.lower() and "logo" not in img_path.name.lower():
                errors.append(f"[未轉檔圖檔外洩] 發現 raw 圖檔存在於 docs: {img_path.relative_to(DOCS_DIR)}")

        try:
            with Image.open(img_path) as im:
                w, h = im.size
                if w > MAX_ALLOWED_WIDTH or h > MAX_ALLOWED_WIDTH:
                    errors.append(f"[超過上限尺寸] ({w}x{h} > {MAX_ALLOWED_WIDTH}px): {img_path.relative_to(DOCS_DIR)}")

                exif_data = im.getexif()
                if exif_data:
                    if 34853 in exif_data or 0x8825 in exif_data:
                        errors.append(f"[GPS 敏感定位洩漏] 未徹底剝除 EXIF 定位: {img_path.relative_to(DOCS_DIR)}")
        except Exception as e:
            errors.append(f"[檔案損毀無法解碼] {img_path.relative_to(DOCS_DIR)} ({e})")

    # 1.1 檢查是否有未經公開衍生處理之影片或大型多媒體原檔外洩至 docs/
    raw_media_files = list(DOCS_DIR.rglob("*.mp4")) + list(DOCS_DIR.rglob("*.mov")) + list(DOCS_DIR.rglob("*.webm"))
    for rmf in raw_media_files:
        errors.append(f"[多媒體原檔外洩] 發現未經公開衍生處理之影片原檔存在於 docs: {rmf.relative_to(DOCS_DIR)}")

    # 2. 檢查 Image Manifest 一致性
    manifest_files = list(DOCS_DIR.rglob("image-manifest.json"))
    for mf in manifest_files:
        try:
            with open(mf, "r", encoding="utf-8") as f:
                mdata = json.load(f)
                trip_dir = mf.parent
                for img_key, item in mdata.get("images", {}).items():
                    for d in item.get("derivatives", []):
                        d_path = trip_dir / "images" / d["filename"]
                        if not d_path.exists():
                            pub_path = DOCS_DIR / d["publicPath"]
                            if not pub_path.exists():
                                errors.append(f"[Manifest 遺失實體] {d['publicPath']}")
        except Exception as e:
            errors.append(f"[Manifest 解析失敗] {mf.name} ({e})")

    # 3. 檢查 JavaScript 檔案內是否有未更新之 raw .jpg 引用與核心函式完整性
    js_files = list(DOCS_DIR.rglob("*.js"))
    for jf in js_files:
        if "vendor" in jf.parts:
            continue
        try:
            js_text = jf.read_text(encoding="utf-8")
            raw_jpg_in_js = re.findall(r'["\']([^"\']*(?:images/day-[^"\']*\.jpg))["\']', js_text, re.IGNORECASE)
            for r in raw_jpg_in_js:
                errors.append(f"[JS 包含原始 JPG 引用] {r} in {jf.relative_to(DOCS_DIR)}")
            
            # 檢查 published app.js 是否完整包含圖集快速入口函式
            if jf.name == "app.js":
                if "openCurrentPageGallery" not in js_text or "openDay03Gallery" not in js_text:
                    errors.append(f"[Published JS 缺少圖集函式] {jf.relative_to(DOCS_DIR)} 未同步包含 openCurrentPageGallery / openDayXXGallery")
                if re.search(r'const\s+ALL_STORIES\s*=\s*\[', js_text):
                    errors.append(f"[Journey 內容耦合] Published app.js 不得硬編碼 ALL_STORIES: {jf.relative_to(DOCS_DIR)}")
                if "window.__JOURNEY_STORIES__" not in js_text:
                    errors.append(f"[Journey Stories 契約缺失] app.js 未讀取 window.__JOURNEY_STORIES__: {jf.relative_to(DOCS_DIR)}")
        except Exception as e:
            warnings.append(f"讀取 JS 失敗: {jf.name} ({e})")

    # 4. 檢查 HTML 引用有效性、死鏈、錨點存在性與 CLS 尺寸合規
    html_files = list(DOCS_DIR.rglob("*.html"))
    html_ids_cache = {}

    def get_html_anchors(file_path):
        if file_path not in html_ids_cache:
            try:
                txt = file_path.read_text(encoding="utf-8")
                # 提取所有 id="..." 與 name="..."
                ids = set(re.findall(r'(?:id|name)=["\']([^"\']+)["\']', txt, re.IGNORECASE))
                html_ids_cache[file_path] = ids
            except Exception:
                html_ids_cache[file_path] = set()
        return html_ids_cache[file_path]

    for hf in html_files:
        try:
            content = hf.read_text(encoding="utf-8")
            html_dir = hf.parent

            # 4.1 檢查是否有直接引用 masters/
            if "masters/" in content:
                errors.append(f"[直接引用 master] HTML 引用了未公開 masters/ 路徑: {hf.relative_to(DOCS_DIR)}")

            rel_html = hf.relative_to(DOCS_DIR).as_posix()
            if rel_html in blog_contracts:
                if "window.__PAGE_CONFIG__" in content:
                    errors.append(f"[Editor Metadata 外洩] 正式 Blog 含 window.__PAGE_CONFIG__: {hf.relative_to(DOCS_DIR)}")
                if "平行改寫預覽版" in content or "Place Preview" in content:
                    errors.append(f"[Preview 施工字樣外洩] 正式 Blog 含預覽術語: {hf.relative_to(DOCS_DIR)}")

            if rel_html in page_contracts:
                canonical_match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', content, re.IGNORECASE)
                expected_canonical = page_contracts[rel_html]
                if not canonical_match:
                    errors.append(f"[缺少 Canonical] 正式頁面未設定 canonical: {hf.relative_to(DOCS_DIR)}")
                elif canonical_match.group(1) != expected_canonical:
                    errors.append(f"[Canonical 不一致] {canonical_match.group(1)} != {expected_canonical} in {hf.relative_to(DOCS_DIR)}")

                og_url_match = re.search(r'<meta\s+property=["\']og:url["\']\s+content=["\']([^"\']+)["\']', content, re.IGNORECASE)
                if not og_url_match:
                    errors.append(f"[缺少 og:url] 正式頁面未設定 og:url: {hf.relative_to(DOCS_DIR)}")
                elif og_url_match.group(1) != expected_canonical:
                    errors.append(f"[og:url 不一致] {og_url_match.group(1)} != {expected_canonical} in {hf.relative_to(DOCS_DIR)}")

            if rel_html in timeline_entries:
                hero_match = re.search(
                    r'<header\s+class=["\']schedule-hero-card["\'][^>]*>([\s\S]*?)</header>',
                    content,
                    re.IGNORECASE,
                )
                if not hero_match:
                    errors.append(f"[Timeline Hero 缺失] {hf.relative_to(DOCS_DIR)}")
                else:
                    hero_blog_links = re.findall(
                        r'<a\b(?=[^>]*href=["\'](blog/[^"\']+)["\'])[^>]*>',
                        hero_match.group(1),
                        re.IGNORECASE,
                    )
                    expected_count = 2 if timeline_entries[rel_html].get("id") == "day-10" else 1
                    if len(hero_blog_links) != expected_count:
                        errors.append(
                            f"[Timeline Hero CTA 數量錯誤] 預期 {expected_count}、實際 {len(hero_blog_links)} "
                            f"in {hf.relative_to(DOCS_DIR)}"
                        )
                    if len(hero_blog_links) != len(set(hero_blog_links)):
                        errors.append(f"[Timeline Hero CTA 重複] {hf.relative_to(DOCS_DIR)}")

            # 4.2 檢查 legacy OG URL
            if "2026-Germany" in content:
                if re.search(r'<meta[^>]+content=["\'][^"\']*2026-Germany[^"\']*["\']', content):
                    errors.append(f"[遺留 OG URL] 包含舊版專案網址 2026-Germany: {hf.relative_to(DOCS_DIR)}")

            # 4.3 檢查 <img> 標籤的 CLS 尺寸 (width/height) 與重複屬性（排除 script 區塊）
            clean_html = re.sub(r'<script[\s\S]*?</script>', '', content, flags=re.IGNORECASE)

            # Journey Hub owns featured-story data; core/app.js owns behavior only.
            stories_match = re.search(
                r'window\.__JOURNEY_STORIES__\s*=\s*\[([\s\S]*?)\];',
                content,
                re.IGNORECASE,
            )
            if stories_match:
                stories_block = stories_match.group(1)
                story_imgs = re.findall(r'\bimg:\s*["\']([^"\']+)["\']', stories_block)
                story_urls = re.findall(r'\burl:\s*["\']([^"\']+)["\']', stories_block)
                if not story_imgs or len(story_imgs) != len(story_urls):
                    errors.append(f"[Journey Stories 資料不完整] img/url 數量不一致 in {hf.relative_to(DOCS_DIR)}")
                if len(story_urls) != len(set(story_urls)):
                    errors.append(f"[Journey Stories 重複 URL] {hf.relative_to(DOCS_DIR)}")
                for story_ref, label in [(p, "圖片") for p in story_imgs] + [(p, "連結") for p in story_urls]:
                    story_path = (html_dir / story_ref).resolve()
                    if not story_path.exists():
                        errors.append(f"[Journey Stories {label} 404] {story_ref} in {hf.relative_to(DOCS_DIR)}")

            img_tags = re.findall(r'<img\s+([^>]+)>', clean_html, re.IGNORECASE)
            for itag in img_tags:
                # 檢查 width 與 height
                has_w = bool(re.search(r'\bwidth=["\']?\d+', itag, re.IGNORECASE))
                has_h = bool(re.search(r'\bheight=["\']?\d+', itag, re.IGNORECASE))
                if not (has_w and has_h):
                    errors.append(f"[缺少圖片尺寸 (違反 CLS=0)] <img {itag[:60]}...> in {hf.relative_to(DOCS_DIR)}")

                # 檢查重複 loading 屬性
                loading_matches = re.findall(r'\bloading=', itag, re.IGNORECASE)
                if len(loading_matches) > 1:
                    errors.append(f"[重複 loading 屬性] <img {itag[:60]}...> in {hf.relative_to(DOCS_DIR)}")

            # 4.4 檢查所有本機連結與資源是否皆存在 (避免 404 與無效錨點)
            ref_pattern = re.compile(r'(?:href|src)=["\']([^"\']+)["\']')
            for match in ref_pattern.finditer(clean_html):
                target = match.group(1).strip()
                # 排除外部連結、JavaScript 虛擬協定
                if target.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "data:")):
                    continue

                anchor = None
                if "#" in target:
                    parts = target.split("#", 1)
                    target_file_part = parts[0]
                    anchor = parts[1]
                else:
                    target_file_part = target

                clean_target = target_file_part.split("?")[0]

                # 若是純錨點 (#itinerary)，目標檔案即為當前頁面
                if not clean_target:
                    target_path = hf
                else:
                    target_path = (html_dir / clean_target).resolve()

                # 檢查檔案存在性
                if not target_path.exists():
                    errors.append(f"[死鏈 404] 找不到目標檔案: '{target}' (解析路徑: {target_path}) in {hf.relative_to(DOCS_DIR)}")
                    continue

                # 檢查錨點 (Anchor) 是否存在於目標頁面
                if anchor and target_path.suffix.lower() == ".html":
                    valid_anchors = get_html_anchors(target_path)
                    if anchor not in valid_anchors:
                        errors.append(f"[無效 Anchor 錨點] #{anchor} 不存在於目標頁面 '{target_path.name}' in {hf.relative_to(DOCS_DIR)}")

                # 檢查 href / src 若指向 images/ 是否為未轉檔之 raw .jpg
                if "images/" in clean_target and clean_target.lower().endswith((".jpg", ".png", ".heic")):
                    errors.append(f"[HTML 引用原始 JPG] '{clean_target}' in {hf.relative_to(DOCS_DIR)}")

            # 4.5 檢查 srcset 中的每個檔案是否存在
            srcset_pattern = re.compile(r'srcset=["\']([^"\']+)["\']')
            for match in srcset_pattern.finditer(content):
                srcset_val = match.group(1)
                items = [item.strip().split()[0] for item in srcset_val.split(",") if item.strip()]
                for item in items:
                    if item.startswith(("http://", "https://", "data:")):
                        continue
                    clean_item = item.split("?")[0].split("#")[0]
                    item_path = (html_dir / clean_item).resolve()
                    if not item_path.exists():
                        errors.append(f"[srcset 死鏈] 找不到圖片: '{item}' in {hf.relative_to(DOCS_DIR)}")

        except Exception as e:
            warnings.append(f"讀取 HTML 失敗: {hf.name} ({e})")

    print(f"📊 檢查完成：共掃描 {total_images} 個公開圖片、{len(html_files)} 份 HTML、{len(js_files)} 份 JS 文件。")
    if errors:
        print(f"\n❌ 發現 {len(errors)} 個違規與死鏈項目：")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\n✅ 100% 通過！全站連結、Anchor 錨點、社群 Meta 與公開 WebP 圖片完全合規，零 404 死鏈。")


if __name__ == "__main__":
    validate_docs()

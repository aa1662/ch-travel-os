#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CH Travel OS 2.0 - Config-Driven Blog HTML Builder
依據 trips/<trip>/blog-migration.json 進行確定性批次構建：
1. 讀取 SSoT 模板與 image-manifest.json
2. 結構化解析 <img> 屬性，完整注入 width/height (CLS=0)、srcset、lazy loading (無重複屬性)
3. 嚴格對齊章節導覽鏈結 (prev_link / next_link)，未發布天數以非 <a> 標籤優雅降級
4. 統一社群 OG/Twitter 元數據
5. 嚴格模式：遇任何 source 遺失或圖片 miss 立即退出 (non-zero exit)
"""

import re
import sys
import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
TRIPS_DIR = BASE_DIR / "trips"
CORE_DIR = BASE_DIR / "core"


def parse_html_attributes(tag_str):
    """解析 HTML 標籤內的所有屬性為字典"""
    attrs = {}
    # 匹配 key="value" 或 key='value' 或無值 key
    pattern = re.compile(r'([a-zA-Z0-9_\-:]+)(?:\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+)))?')
    for match in pattern.finditer(tag_str):
        key = match.group(1).lower()
        val = match.group(2) if match.group(2) is not None else (match.group(3) if match.group(3) is not None else match.group(4))
        if val is None:
            val = True
        attrs[key] = val
    return attrs


def transform_html_images(html_content, images_dict, img_folder, rel_img_prefix, errors):
    # 1. 替換 <a> 燈箱連結指向 1600w lightbox WebP
    def replace_a_href(match):
        matched_folder = match.group(1)
        img_name = match.group(2)
        clean_img_name = re.sub(r'-(?:thumb|content|desktop|lightbox)-\d+w\.webp$', '.jpg', img_name, flags=re.IGNORECASE)
        key = f"{matched_folder}/{clean_img_name}"
        if key not in images_dict:
            key = f"{matched_folder}/{img_name}"
        if key not in images_dict:
            stem = Path(img_name).stem.split("-")[0]
            for k in images_dict:
                if k.startswith(f"{matched_folder}/{stem}"):
                    key = k
                    break

        if key in images_dict:
            derivatives = images_dict[key]["derivatives"]
            lightbox_d = [d for d in derivatives if d["profile"] == "lightbox"]
            target_file = lightbox_d[0]["filename"] if lightbox_d else derivatives[-1]["filename"]
            return f'href="../images/{matched_folder}/{target_file}"'
        else:
            errors.append(f"燈箱連結找不到圖檔 Manifest 紀錄: {key}")
        return match.group(0)

    html_content = re.sub(r'href="(?:\.\./)*images/([^/]+)/([^"]+\.(?:jpg|jpeg|png|webp))"', replace_a_href, html_content, flags=re.IGNORECASE)

    # 2. 結構化重構 <img> 標籤
    def replace_img_tag(match):
        full_tag = match.group(0)
        inner_attrs_str = match.group(1)
        attrs = parse_html_attributes(inner_attrs_str)

        src = attrs.get("src", "")
        if not src:
            return full_tag

        # 提取資料夾與圖檔檔名 (如 day-02 / 18041867387724285.jpg)
        src_name_match = re.search(r'images/([^/]+)/([^/?#]+)', src, re.IGNORECASE)
        if not src_name_match:
            return full_tag

        matched_folder = src_name_match.group(1)
        img_name = src_name_match.group(2)
        rel_img_prefix = f"../images/{matched_folder}"

        # 去除舊衍生圖後綴如果有的話
        clean_img_name = re.sub(r'-(?:thumb|content|desktop|lightbox)-\d+w\.webp$', '.jpg', img_name, flags=re.IGNORECASE)
        key = f"{matched_folder}/{clean_img_name}"

        # 若 key 不在，嘗試原名
        if key not in images_dict:
            key = f"{matched_folder}/{img_name}"

        if key not in images_dict:
            # 檢查是否有同 stem 檔名
            stem = Path(img_name).stem.split("-")[0]
            found = False
            for k in images_dict:
                if k.startswith(f"{matched_folder}/{stem}"):
                    key = k
                    found = True
                    break
            if not found:
                errors.append(f"<img> 標籤找不到 Manifest 映射: {key} (src={src})")
                return full_tag

        item = images_dict[key]
        derivatives = item["derivatives"]
        orig_w = item.get("original_width", 1200)
        orig_h = item.get("original_height", 800)

        srcset_items = [f'{rel_img_prefix}/{d["filename"]} {d["width"]}w' for d in derivatives]
        srcset_str = ",\n                  ".join(srcset_items)

        content_d = [d for d in derivatives if d["profile"] == "content"]
        default_src = content_d[0]["filename"] if content_d else derivatives[0]["filename"]

        alt_text = attrs.get("alt", "CH Travel OS 旅程實拍")
        class_attr = f' class="{attrs["class"]}"' if "class" in attrs else ""
        style_attr = f' style="{attrs["style"]}"' if "style" in attrs else ""

        return f'''<img src="{rel_img_prefix}/{default_src}"
                 srcset="{srcset_str}"
                 sizes="(max-width: 768px) 100vw, 960px"
                 width="{orig_w}"
                 height="{orig_h}"
                 loading="lazy"
                 decoding="async"
                 alt="{alt_text}"{class_attr}{style_attr}>'''

    img_tag_pattern = re.compile(r'<img\s+([^>]+)>', re.IGNORECASE)
    html_content = img_tag_pattern.sub(replace_img_tag, html_content)
    return html_content


def build_trip(trip_slug="2026-germany", dest_slug="germany"):
    config_path = TRIPS_DIR / trip_slug / "blog-migration.json"
    manifest_path = DOCS_DIR / dest_slug / "image-manifest.json"

    errors = []

    if not config_path.exists():
        print(f"❌ 找不到設定檔: {config_path}")
        sys.exit(1)

    if not manifest_path.exists():
        print(f"❌ 找不到 Manifest: {manifest_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
        entries = config_data.get("entries", config_data) if isinstance(config_data, dict) else config_data

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    images_dict = manifest.get("images", {})
    built_count = 0

    print(f"🚀 開始執行 {trip_slug} -> {dest_slug} Blog 批次編譯...")

    compiled_outputs = {}

    for item in entries:
        src_file = BASE_DIR / item["source"]
        out_file = BASE_DIR / item["output"]
        img_folder = item.get("image_folder", item["id"].split("-")[0] + "-" + item["id"].split("-")[1] if "-" in item["id"] else item["id"])

        if not src_file.exists():
            errors.append(f"設定之來源檔案不存在: {src_file}")
            continue

        html_content = src_file.read_text(encoding="utf-8")

        # 1. 調整核心資源路徑至 ../../core/
        html_content = re.sub(r'href="(?:\.\./)*css/style\.css(?:\?[^"]*)?"', 'href="../../core/css/style.css"', html_content)
        html_content = re.sub(r'href="(?:\.\./)*vendor/glightbox/glightbox\.min\.css(?:\?[^"]*)?"', 'href="../../core/vendor/glightbox/glightbox.min.css"', html_content)
        html_content = re.sub(r'src="(?:\.\./)*vendor/glightbox/glightbox\.min\.js(?:\?[^"]*)?"', 'src="../../core/vendor/glightbox/glightbox.min.js"', html_content)
        html_content = re.sub(r'src="(?:\.\./)*js/app\.js(?:\?[^"]*)?"', 'src="../../core/js/app.js"', html_content)
        html_content = re.sub(r'src="(?:\.\./)*js/main\.js(?:\?[^"]*)?"', 'src="../../core/js/main.js"', html_content)

        # 2. 轉換圖片為 WebP 規格
        rel_prefix = f"../images/{img_folder}"
        html_content = transform_html_images(html_content, images_dict, img_folder, rel_prefix, errors)

        # 2.1 統一全頁的 data-gallery 名稱，確保點擊任一張照片均可全域流暢滑動瀏覽
        article_gallery_name = f"{item['id']}-gallery"
        html_content = re.sub(r'data-gallery=["\'][^"\']+["\']', f'data-gallery="{article_gallery_name}"', html_content)

        # 3. 修正 OG 與 Canonical URL
        if item.get("og_url"):
            html_content = re.sub(
                r'<meta\s+property=["\']og:url["\']\s+content=["\'][^"\']*["\']',
                f'<meta property="og:url" content="{item["og_url"]}"',
                html_content
            )
        if item.get("og_image"):
            html_content = re.sub(
                r'<meta\s+property=["\']og:image["\']\s+content=["\'][^"\']*["\']',
                f'<meta property="og:image" content="{item["og_image"]}"',
                html_content
            )

        # 4. 建立嚴格無 404 的篇章導航區塊 (Footer Navigation)
        if item.get("prev_link"):
            p_title = item["prev_title"]
            p_text = p_title if (p_title.startswith("←") or p_title.startswith("上一篇")) else f"← 上一篇：{p_title}"
            prev_html = f'<a href="{item["prev_link"]}" style="font-weight: 600; color: var(--primary); font-size: 0.95rem;">{p_text}</a>'
        else:
            prev_html = '<a href="../index.html#itinerary" style="font-weight: 600; color: var(--primary); font-size: 0.95rem;">← 🗺️ 行程起點 · 旅程總覽</a>'

        if item.get("next_link"):
            n_title = item["next_title"]
            n_text = n_title if (n_title.startswith("🎉") or n_title.startswith("下一篇")) else f"下一篇：{n_title}"
            if not n_text.endswith("→"):
                n_text += " →"
            next_html = f'<a href="{item["next_link"]}" style="font-weight: 600; color: var(--primary); font-size: 0.95rem;">{n_text}</a>'
        else:
            next_html = '<a href="../index.html" style="font-weight: 600; color: var(--primary); font-size: 0.95rem;">🎉 15天德南冬旅圓滿完結 · 回首頁 →</a>'

        day_num_match = re.search(r'day-(\d+)', item["id"])
        day_num = day_num_match.group(1) if day_num_match else "02"
        timeline_target = f"../day-{day_num}.html"
        timeline_physical = DOCS_DIR / dest_slug / f"day-{day_num}.html"
        if timeline_physical.exists():
            center_html = f'<a href="{timeline_target}" class="badge badge-gold" style="font-size: 0.9rem; padding: 0.5rem 1rem; text-decoration: none;">⏱️ 查看 Day {int(day_num)} 純時間表</a>'
        else:
            center_html = f'<a href="../index.html#itinerary" class="badge badge-gold" style="font-size: 0.9rem; padding: 0.5rem 1rem; text-decoration: none;">🗺️ 行程總覽</a>'

        new_nav_block = f'''<!-- 篇章導覽按鈕 -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin: 3.5rem 0 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color); flex-wrap: wrap; gap: 1rem;">
        {prev_html}
        {center_html}
        {next_html}
      </div>'''

        html_content = re.sub(
            r'<!--\s*篇章導覽按鈕\s*-->[\s\S]*?</div>\s*</article>',
            f'{new_nav_block}\n    </article>',
            html_content
        )

        # 5. 修正手機 Dock 與頂部導覽列中的未發布 timeline 連結
        if not timeline_physical.exists():
            html_content = html_content.replace(f'href="../day-{day_num}.html"', 'href="../index.html#itinerary"')

        compiled_outputs[out_file] = (item["id"], html_content)

    # 嚴格原子性把關：若有任何錯誤，絕不寫入磁碟！
    if errors:
        print(f"\n❌ 編譯失敗！發現 {len(errors)} 個錯誤，已中止寫入磁碟：")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    # 全域無錯誤，開始原子同步核心資產與寫入 HTML
    if CORE_DIR.exists():
        docs_core = DOCS_DIR / "core"
        docs_core.mkdir(parents=True, exist_ok=True)
        shutil.copytree(CORE_DIR, docs_core, dirs_exist_ok=True)

    for out_file, (item_id, content) in compiled_outputs.items():
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(content, encoding="utf-8")
        print(f"  ✅ 已編譯: {item_id} -> {out_file.name}")
        built_count += 1

    print(f"\n✨ 構建完成！共編譯 {built_count} 份標準 WebP 圖文遊記（零錯誤，原子寫入）。\n")


if __name__ == "__main__":
    build_trip("2026-germany", "germany")

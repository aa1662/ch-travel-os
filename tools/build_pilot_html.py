#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CH Travel OS 2.0 - Pilot HTML Generator
將原始 Day 02 遊記內容轉換為符合 Web 圖片發布標準之響應式 WebP HTML
"""

import re
import json
from pathlib import Path

import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
TRIPS_DIR = BASE_DIR / "trips"

SRC_BLOG = TRIPS_DIR / "2026-germany" / "sources" / "blog" / "day-02-blog.html"
SRC_TIMELINE = TRIPS_DIR / "2026-germany" / "sources" / "day-02.html"

MANIFEST_PATH = DOCS_DIR / "germany" / "image-manifest.json"
OUT_BLOG = DOCS_DIR / "germany" / "blog" / "day-02-blog.html"
OUT_TIMELINE = DOCS_DIR / "germany" / "day-02.html"


def transform_html_images(html_content, images_dict, rel_img_prefix="../images/day-02"):
    # 轉換 <a> 燈箱連結
    def replace_a_href(match):
        img_name = match.group(1)
        key = f"day-02/{img_name}"
        if key in images_dict:
            derivatives = images_dict[key]["derivatives"]
            lightbox_d = [d for d in derivatives if d["profile"] == "lightbox"]
            target_file = lightbox_d[0]["filename"] if lightbox_d else derivatives[-1]["filename"]
            return f'href="{rel_img_prefix}/{target_file}"'
        return match.group(0)

    html_content = re.sub(r'href="(?:\.\./)*images/day-02/([^"]+\.jpg)"', replace_a_href, html_content)

    # 轉換 <img> 標籤
    def replace_img_tag(match):
        img_name = match.group(1)
        alt_text = match.group(2) or "哈修塔特 Hallstatt"
        style_attr = match.group(3) or ""

        key = f"day-02/{img_name}"
        if key in images_dict:
            item = images_dict[key]
            derivatives = item["derivatives"]
            orig_w = item.get("original_width", 1200)
            orig_h = item.get("original_height", 800)

            srcset_items = [f'{rel_img_prefix}/{d["filename"]} {d["width"]}w' for d in derivatives]
            srcset_str = ",\n                  ".join(srcset_items)

            content_d = [d for d in derivatives if d["profile"] == "content"]
            default_src = content_d[0]["filename"] if content_d else derivatives[0]["filename"]

            style_str = f' style="{style_attr}"' if style_attr else ""

            return f'''<img src="{rel_img_prefix}/{default_src}"
                 srcset="{srcset_str}"
                 sizes="(max-width: 768px) 100vw, 960px"
                 width="{orig_w}"
                 height="{orig_h}"
                 loading="lazy"
                 decoding="async"
                 alt="{alt_text}"{style_str}>'''
        return match.group(0)

    img_pattern = re.compile(
        r'<img\s+src="(?:\.\./)*images/day-02/([^"]+\.jpg)"(?:\s+alt="([^"]*)")?(?:\s+style="([^"]*)")?\s*\/?>',
        re.IGNORECASE
    )
    html_content = img_pattern.sub(replace_img_tag, html_content)

    def replace_img_simple(match):
        img_name = match.group(1)
        key = f"day-02/{img_name}"
        if key in images_dict:
            item = images_dict[key]
            derivatives = item["derivatives"]
            srcset_items = [f'{rel_img_prefix}/{d["filename"]} {d["width"]}w' for d in derivatives]
            srcset_str = ", ".join(srcset_items)
            content_d = [d for d in derivatives if d["profile"] == "content"]
            default_src = content_d[0]["filename"] if content_d else derivatives[0]["filename"]
            return f'<img src="{rel_img_prefix}/{default_src}" srcset="{srcset_str}" sizes="(max-width: 768px) 100vw, 960px" loading="lazy" decoding="async"'
        return match.group(0)

    html_content = re.sub(r'<img\s+src="(?:\.\./)*images/day-02/([^"]+\.jpg)"', replace_img_simple, html_content)
    return html_content


def generate_pilot_blog():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    images_dict = manifest["images"]

    if not SRC_BLOG.exists():
        raise FileNotFoundError(f"Source blog file missing: {SRC_BLOG}")

    html_content = SRC_BLOG.read_text(encoding="utf-8")

    # 1. 調整核心資源路徑至 ../../core/
    html_content = re.sub(r'href="(?:\.\./)*css/style\.css(?:\?[^"]*)?"', 'href="../../core/css/style.css"', html_content)
    html_content = re.sub(r'href="(?:\.\./)*vendor/glightbox/glightbox\.min\.css(?:\?[^"]*)?"', 'href="../../core/vendor/glightbox/glightbox.min.css"', html_content)
    html_content = re.sub(r'src="(?:\.\./)*vendor/glightbox/glightbox\.min\.js(?:\?[^"]*)?"', 'src="../../core/vendor/glightbox/glightbox.min.js"', html_content)
    html_content = re.sub(r'src="(?:\.\./)*js/app\.js(?:\?[^"]*)?"', 'src="../../core/js/app.js"', html_content)
    html_content = re.sub(r'src="(?:\.\./)*js/main\.js(?:\?[^"]*)?"', 'src="../../core/js/main.js"', html_content)

    # 2. 轉換圖片
    html_content = transform_html_images(html_content, images_dict, rel_img_prefix="../images/day-02")

    # 3. 修正 OG URL & Metadata
    html_content = re.sub(
        r'content="https?://[^"]*?/blog/day-02-blog\.html"',
        'content="https://aa1662.github.io/ch-travel-os/germany/blog/day-02-blog.html"',
        html_content
    )
    html_content = re.sub(
        r'content="https?://[^"]*?/images/day-02/[^"]*?"',
        'content="https://aa1662.github.io/ch-travel-os/germany/images/day-02/18041867387724285-desktop-1200w.webp"',
        html_content
    )

    # 4. 處理章節導航未發布頁面的連結（避免 404）
    # 若 day-01-blog.html 或 day-03-blog.html 尚未在 docs/germany/blog 中發布，加上明確提示或導回行程總覽
    html_content = re.sub(
        r'<a href="day-01-blog\.html"[^>]*>(.*?)</a>',
        r'<span class="text-muted" style="font-size: 0.95rem; color: var(--text-muted); cursor: not-allowed;" title="Day 01 即將推出">← 上一篇：Day 01 薩爾斯堡 (即將推出)</span>',
        html_content
    )
    html_content = re.sub(
        r'<a href="day-03-blog\.html"[^>]*>(.*?)</a>',
        r'<span class="text-muted" style="font-size: 0.95rem; color: var(--text-muted); cursor: not-allowed;" title="Day 03 即將推出">下一篇：Day 03 符茲堡 (即將推出) →</span>',
        html_content
    )

    OUT_BLOG.parent.mkdir(parents=True, exist_ok=True)
    OUT_BLOG.write_text(html_content, encoding="utf-8")
    print(f"✅ Pilot Blog 已產出: {OUT_BLOG}")


def generate_pilot_timeline():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    images_dict = manifest["images"]

    if not SRC_TIMELINE.exists():
        return

    html_content = SRC_TIMELINE.read_text(encoding="utf-8")

    # 1. 調整核心資源路徑至 ../core/
    html_content = re.sub(r'href="(?:\.\./)*css/style\.css(?:\?[^"]*)?"', 'href="../core/css/style.css"', html_content)
    html_content = re.sub(r'href="(?:\.\./)*vendor/glightbox/glightbox\.min\.css(?:\?[^"]*)?"', 'href="../core/vendor/glightbox/glightbox.min.css"', html_content)
    html_content = re.sub(r'src="(?:\.\./)*vendor/glightbox/glightbox\.min\.js(?:\?[^"]*)?"', 'src="../core/vendor/glightbox/glightbox.min.js"', html_content)
    html_content = re.sub(r'src="(?:\.\./)*js/app\.js(?:\?[^"]*)?"', 'src="../core/js/app.js"', html_content)
    html_content = re.sub(r'src="(?:\.\./)*js/main\.js(?:\?[^"]*)?"', 'src="../core/js/main.js"', html_content)

    # 2. 轉換圖片
    html_content = transform_html_images(html_content, images_dict, rel_img_prefix="images/day-02")

    # 3. 修正 OG URL
    html_content = re.sub(
        r'content="https?://[^"]*?/day-02\.html"',
        'content="https://aa1662.github.io/ch-travel-os/germany/day-02.html"',
        html_content
    )
    html_content = re.sub(
        r'content="https?://[^"]*?/images/day-02/[^"]*?"',
        'content="https://aa1662.github.io/ch-travel-os/germany/images/day-02/18041867387724285-desktop-1200w.webp"',
        html_content
    )

    # 4. 調整 Day Switcher 中未發布天數的連結
    # 將未生成的 day-xx.html 指向 index.html#itinerary
    def replace_day_btn(match):
        day_num = match.group(1)
        if day_num == "02" or day_num == "2":
            return match.group(0)
        return f'<a href="index.html#itinerary" class="day-nav-btn" title="Day {day_num} 行程總覽">Day {int(day_num)}</a>'

    html_content = re.sub(r'<a href="day-(\d+)\.html" class="day-nav-btn">Day \d+</a>', replace_day_btn, html_content)

    # 5. 處理章節導航中的 day-01.html 與 day-03.html
    html_content = re.sub(
        r'<a href="day-01\.html"[^>]*>(.*?)</a>',
        r'<span class="text-muted" style="font-size: 0.95rem; color: var(--text-muted); cursor: not-allowed;" title="Day 01 即將推出">← 前一天：Day 01 薩爾斯堡 (即將推出)</span>',
        html_content
    )
    html_content = re.sub(
        r'<a href="day-03\.html"[^>]*>(.*?)</a>',
        r'<span class="text-muted" style="font-size: 0.95rem; color: var(--text-muted); cursor: not-allowed;" title="Day 03 即將推出">下一天：Day 03 符茲堡轉移 (即將推出) →</span>',
        html_content
    )

    OUT_TIMELINE.parent.mkdir(parents=True, exist_ok=True)
    OUT_TIMELINE.write_text(html_content, encoding="utf-8")
    print(f"✅ Pilot Timeline 已產出: {OUT_TIMELINE}")


if __name__ == "__main__":
    generate_pilot_blog()
    generate_pilot_timeline()

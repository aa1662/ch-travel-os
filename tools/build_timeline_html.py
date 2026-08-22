#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CH Travel OS 2.0 - 純時間表批次編譯器 (build_timeline_html.py)
-------------------------------------------------------------
功能：
1. 讀取 trips/2026-germany/timeline-migration.json 配置。
2. 將 trips/2026-germany/sources/timeline/day-XX.html 轉換並注入：
   - 核心大腦路徑對齊 (../core/css, ../core/js, ../core/vendor)
   - 頂部導覽列 (Top Navbar) 100% 包含首頁、行程、時間表、深度遊記
   - Hero 看板直通按鈕 (Hero Primary CTA) 保證全 15 天 100% 存在（Day 10 雙篇雙按鈕）
   - 底部篇章導航 (Footer Navigation) 包含上一天、中央遊記直通按鈕、下一天
   - 手機底部 Mobile Dock 100% 雙向直通
   - 現代化 Open Graph 與社群 WebP 標籤
3. 採用 In-Memory 事務機制，確保全域無錯誤才原子寫入 docs/germany/day-XX.html。
"""

import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
CORE_DIR = BASE_DIR / "core"


def build_timelines(trip_slug="2026-germany", dest_slug="germany"):
    trip_dir = BASE_DIR / "trips" / trip_slug
    config_file = trip_dir / "timeline-migration.json"

    if not config_file.exists():
        print(f"❌ 找不到設定檔: {config_file}")
        sys.exit(1)

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    entries = config.get("entries", [])
    errors = []
    compiled_outputs = {}

    print(f"🚀 開始執行 {trip_slug} -> {dest_slug} 純時間表 (Timeline) 批次編譯...")

    for item in entries:
        src_file = BASE_DIR / item["source"]
        out_file = BASE_DIR / item["output"]
        day_num_match = re.search(r'day-(\d+)', item["id"])
        day_num = day_num_match.group(1) if day_num_match else "01"

        if not src_file.exists():
            errors.append(f"設定之來源檔案不存在: {src_file}")
            continue

        html_content = src_file.read_text(encoding="utf-8")

        # 1. 調整核心資源路徑至 ../core/ (因為時間表位於 docs/germany/)
        html_content = re.sub(r'href="(?:\.\./)*css/style\.css(?:\?[^"]*)?"', 'href="../core/css/style.css"', html_content)
        html_content = re.sub(r'href="(?:\.\./)*vendor/glightbox/glightbox\.min\.css(?:\?[^"]*)?"', 'href="../core/vendor/glightbox/glightbox.min.css"', html_content)
        html_content = re.sub(r'src="(?:\.\./)*vendor/glightbox/glightbox\.min\.js(?:\?[^"]*)?"', 'src="../core/vendor/glightbox/glightbox.min.js"', html_content)
        html_content = re.sub(r'src="(?:\.\./)*js/app\.js(?:\?[^"]*)?"', 'src="../core/js/app.js"', html_content)
        html_content = re.sub(r'src="(?:\.\./)*js/main\.js(?:\?[^"]*)?"', 'src="../core/js/main.js"', html_content)

        # 2. 修正 OG 與 Canonical URL
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
            html_content = re.sub(
                r'<meta\s+name=["\']twitter:image["\']\s+content=["\'][^"\']*["\']',
                f'<meta name="twitter:image" content="{item["og_image"]}"',
                html_content
            )

        # 3. 清理舊版 OG 網址遺留 2026-Germany
        html_content = re.sub(r'https://aa1662\.github\.io/2026-Germany/([^\s"\']+)', r'https://aa1662.github.io/ch-travel-os/germany/\1', html_content)

        # 4. 標準化頂部導覽列 (Top Navbar)
        primary_blog = item.get("blog_link", f"blog/day-{day_num}-blog.html")
        std_nav_links = f'''<ul class="nav-links">
        <li><a href="index.html">首頁</a></li>
        <li><a href="index.html#itinerary">15天行程</a></li>
        <li><a href="day-{day_num}.html" class="active">純時間表</a></li>
        <li><a href="{primary_blog}">深度遊記</a></li>
      </ul>'''
        html_content = re.sub(r'<ul class="nav-links">[\s\S]*?</ul>', std_nav_links, html_content)

        # 5. 標準化 Hero 看板按鈕 (Hero Primary CTA) - 確保 100% 存在
        if item["id"] == "day-10":
            hero_btn_html = '''<div style="margin-top: 0.85rem; display: flex; gap: 0.75rem; flex-wrap: wrap;">
          <a href="blog/day-10-speyer-blog.html" class="btn-hero-primary" style="font-size: 0.92rem; padding: 0.65rem 1.25rem;">
            📝 閱讀 Day 10 上篇（史派爾帝國大教堂 ✕ 跨國轉移）→
          </a>
          <a href="blog/day-10-colmar-blog.html" class="btn-hero-primary" style="font-size: 0.92rem; padding: 0.65rem 1.25rem;">
            📝 閱讀 Day 10 下篇（科爾馬小威尼斯 ✕ 移動城堡）→
          </a>
        </div>'''
        else:
            b_title = item.get("blog_title", f"Day {day_num} 深度遊記")
            hero_btn_html = f'''<div style="margin-top: 0.85rem;">
          <a href="{primary_blog}" class="btn-hero-primary" style="font-size: 0.92rem; padding: 0.65rem 1.3rem;">
            📝 閱讀今日深度圖文遊記（{b_title}）→
          </a>
        </div>'''

        # 如果已有舊按鈕則替換，若無則插入至 header 結尾
        if re.search(r'<div style="margin-top:\s*0\.\d+rem;">\s*<a[^>]+class="btn-hero-primary"[^>]*>[\s\S]*?</a>\s*</div>', html_content):
            html_content = re.sub(
                r'<div style="margin-top:\s*0\.\d+rem;">\s*<a[^>]+class="btn-hero-primary"[^>]*>[\s\S]*?</a>\s*</div>',
                hero_btn_html,
                html_content
            )
        elif '<header class="schedule-hero-card">' in html_content:
            html_content = re.sub(
                r'(</header>)',
                f'{hero_btn_html}\n    \\1',
                html_content
            )

        # 6. 標準化底部篇章導覽按鈕 (Footer Navigation)
        prev_p = item.get("prev_link", "index.html#itinerary")
        prev_t = item.get("prev_title", "回到行程總覽")
        next_p = item.get("next_link", "index.html")
        next_t = item.get("next_title", "回首頁")

        prev_text = prev_t if prev_t.startswith("←") else f"← {prev_t}"
        next_text = next_t if (next_t.endswith("→") or next_t.startswith("🎉")) else f"{next_t} →"
        if not next_text.endswith("→") and not next_text.startswith("🎉"):
            next_text += " →"

        if item["id"] == "day-10":
            center_nav_html = '''<div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
        <a href="blog/day-10-speyer-blog.html" class="badge badge-gold" style="font-size: 0.9rem; padding: 0.5rem 1rem; text-decoration: none;">📝 閱讀 Day 10 上篇（史派爾）</a>
        <a href="blog/day-10-colmar-blog.html" class="badge badge-gold" style="font-size: 0.9rem; padding: 0.5rem 1rem; text-decoration: none;">📝 閱讀 Day 10 下篇（科爾馬）</a>
      </div>'''
        else:
            day_id_upper = item["id"].replace("-", " ").title()
            center_nav_html = f'<a href="{primary_blog}" class="badge badge-gold" style="font-size: 0.9rem; padding: 0.5rem 1rem; text-decoration: none;">📝 閱讀 {day_id_upper} 深度遊記</a>'

        new_footer_nav = f'''<!-- 篇章導覽按鈕 -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin: 3.5rem 0 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color); flex-wrap: wrap; gap: 1rem;">
      <a href="{prev_p}" style="font-weight: 600; color: var(--primary); font-size: 0.95rem;">{prev_text}</a>
      {center_nav_html}
      <a href="{next_p}" style="font-weight: 600; color: var(--primary); font-size: 0.95rem;">{next_text}</a>
    </div>'''

        if re.search(r'<!--\s*(?:篇章)?導覽按鈕\s*-->[\s\S]*?</div>\s*</main>', html_content):
            html_content = re.sub(
                r'<!--\s*(?:篇章)?導覽按鈕\s*-->[\s\S]*?</div>\s*</main>',
                f'{new_footer_nav}\n  </main>',
                html_content
            )
        elif '</main>' in html_content:
            html_content = re.sub(
                r'(</main>)',
                f'{new_footer_nav}\n  \\1',
                html_content
            )

        # 7. 標準化手機底部 Mobile Dock
        std_mobile_dock = f'''<!-- 手機底部 App-Like 導覽列 -->
  <div class="mobile-dock">
    <a href="index.html" class="dock-item">
      <span class="dock-icon">🏠</span>
      <span>首頁</span>
    </a>
    <a href="day-{day_num}.html" class="dock-item active">
      <span class="dock-icon">⏱️</span>
      <span>時間表</span>
    </a>
    <a href="{primary_blog}" class="dock-item">
      <span class="dock-icon">📖</span>
      <span>遊記</span>
    </a>
    <a href="javascript:void(0)" class="dock-item btn-share">
      <span class="dock-icon">📤</span>
      <span>分享</span>
    </a>
  </div>'''

        html_content = re.sub(
            r'(?:<!--\s*手機底部\s*App-Like\s*導覽列\s*-->\s*)?<div class="mobile-dock">[\s\S]*?</div>',
            std_mobile_dock,
            html_content
        )

        # 8. 檢查所有內部連結是否有效
        internal_links = re.findall(r'href=["\']([^"\':#]+\.html(?:#[^"\']*)?)["\']', html_content)
        for link in internal_links:
            clean_link = link.split("#")[0]
            target_path = DOCS_DIR / dest_slug / clean_link
            if target_path != out_file and not target_path.exists():
                if not any(BASE_DIR / e["output"] == target_path for e in entries):
                    errors.append(f"[{item['id']}] 內部連結目標不存在: {link} (解析: {target_path})")

        compiled_outputs[out_file] = (item["id"], html_content)

    # 嚴格原子性把關：若有任何錯誤，絕不寫入磁碟！
    if errors:
        print(f"\n❌ 編譯失敗！發現 {len(errors)} 個錯誤，已中止寫入磁碟：")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    # 全域無錯誤，開始原子寫入
    built_count = 0
    for out_file, (item_id, content) in compiled_outputs.items():
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(content, encoding="utf-8")
        print(f"  ✅ 已編譯: {item_id} -> {out_file.name}")
        built_count += 1

    print(f"\n✨ 構建完成！共編譯 {built_count} 份標準純時間表（100% 雙向直通，原子寫入）。\n")


if __name__ == "__main__":
    build_timelines()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CH Travel OS 2.0 - Config-Driven Blog HTML Builder
依據 trips/<trip>/blog-migration.json 進行確定性批次構建：
1. 讀取 SSoT 模板與 image-manifest.json
2. 結構化解析 <img> 屬性，完整注入 width/height (CLS=0)、srcset、lazy loading (無重複屬性)
3. 由 reading_units 契約產生上一篇／下一篇與延伸閱讀；舊旅程仍相容 prev_link / next_link
4. 統一社群 OG/Twitter 元數據
5. 嚴格模式：遇任何 source 遺失或圖片 miss 立即退出 (non-zero exit)
6. 若存在 trips/<trip>/sources/index.html，全量構建時於同一筆交易同步 Journey Hub
7. 支援 --entry <id> 單篇構建；單篇模式不寫入 Journey Hub 或同步 core 資產
"""

import re
import sys
import json
import shutil
from html import escape as html_escape
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
TRIPS_DIR = BASE_DIR / "trips"
CORE_DIR = BASE_DIR / "core"
PUBLIC_CORE_FILES = (
    ("css", "style.css"),
    ("js", "app.js"),
    ("js", "main.js"),
    ("vendor", "glightbox", "glightbox.min.css"),
    ("vendor", "glightbox", "glightbox.min.js"),
)


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

    html_content = re.sub(r'href="(?:\.\./)*images/([^/]+)/([^"]+\.(?:jpg|jpeg|png|webp|heic))"', replace_a_href, html_content, flags=re.IGNORECASE)

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
        loading_value = attrs.get("loading", "lazy")
        decoding_value = attrs.get("decoding", "async")
        sizes_value = attrs.get("sizes", "(max-width: 768px) 100vw, 960px")
        class_attr = f' class="{attrs["class"]}"' if "class" in attrs else ""
        style_attr = f' style="{attrs["style"]}"' if "style" in attrs else ""
        fetchpriority_attr = f' fetchpriority="{attrs["fetchpriority"]}"' if "fetchpriority" in attrs else ""

        return f'''<img src="{rel_img_prefix}/{default_src}"
                 srcset="{srcset_str}"
                 sizes="{sizes_value}"
                 width="{orig_w}"
                 height="{orig_h}"
                 loading="{loading_value}"
                 decoding="{decoding_value}"
                 alt="{alt_text}"{class_attr}{style_attr}{fetchpriority_attr}>'''

    img_tag_pattern = re.compile(r'<img\s+([^>]+)>', re.IGNORECASE)
    html_content = img_tag_pattern.sub(replace_img_tag, html_content)
    return html_content


def upsert_head_tag(html_content, pattern, replacement):
    if re.search(pattern, html_content, flags=re.IGNORECASE):
        return re.sub(pattern, replacement, html_content, count=1, flags=re.IGNORECASE)
    return re.sub(r"(<head[^>]*>)", rf"\1\n  {replacement}", html_content, count=1, flags=re.IGNORECASE)


def strip_editor_metadata(html_content):
    return re.sub(
        r"\s*<script>\s*window\.__PAGE_CONFIG__\s*=\s*\{[\s\S]*?\};\s*</script>",
        "",
        html_content,
        flags=re.IGNORECASE,
    )


def render_gallery_registry(item, img_folder, errors, show_gallery_titles=True):
    """由 migration config 產生唯一、可驗證的隱藏 Lightbox registry。"""
    groups = item.get("gallery_groups", [])
    if not groups:
        return ""

    seen_images = set()
    group_html = []
    for group in groups:
        gallery_id = group.get("id", "").strip()
        gallery_items = group.get("items", [])
        if not gallery_id or not isinstance(gallery_items, list) or not gallery_items:
            errors.append(f"{item['id']}: gallery_groups 每組必須包含 id 與非空 items")
            continue

        for gallery_item in gallery_items:
            image_name = gallery_item.get("image", "").strip()
            if not image_name:
                errors.append(f"{item['id']}: gallery item 缺少 image")
                continue
            image_id = gallery_item.get("image_id") or Path(image_name).stem
            if image_id in seen_images:
                errors.append(f"{item['id']}: gallery image 重複註冊: {image_id}")
                continue
            seen_images.add(image_id)
            title = gallery_item.get("title", "")
            title_attr = (
                f' data-title="{html_escape(title)}"'
                if show_gallery_titles and title
                else ""
            )
            group_html.append(
                f'        <a href="../images/{html_escape(img_folder)}/{html_escape(image_name)}" '
                f'class="glightbox" data-gallery="{html_escape(gallery_id)}" '
                f'data-gallery-image="{html_escape(image_id)}"{title_attr}></a>'
            )

    if not group_html:
        return ""
    return '<div class="gallery-registry" hidden aria-hidden="true">\n' + "\n".join(group_html) + "\n      </div>"


def build_reading_navigation(config, all_entries, errors):
    """驗證並展開 Journey 閱讀順序；未 opt-in 的舊 config 回傳空映射。"""
    units = config.get("reading_units", []) if isinstance(config, dict) else []
    if not units:
        return {}

    entry_ids = {
        entry["id"] for entry in all_entries if entry.get("status") != "draft"
    }
    seen_unit_ids = set()
    seen_hrefs = set()
    story_entry_ids = set()
    navigation = {}

    for index, unit in enumerate(units):
        unit_id = unit.get("id", "").strip()
        href = unit.get("href", "").strip()
        title = unit.get("title", "").strip()
        if not unit_id or not href or not title:
            errors.append("reading_units 每個單元都必須包含 id、href 與 title")
            continue
        if unit_id in seen_unit_ids:
            errors.append(f"reading_units id 重複: {unit_id}")
        if href in seen_hrefs:
            errors.append(f"reading_units href 重複: {href}")
        if href.startswith(("/", "http://", "https://")) or ".." in Path(href).parts:
            errors.append(f"reading_units href 必須是 Journey 根目錄相對路徑: {href}")
        seen_unit_ids.add(unit_id)
        seen_hrefs.add(href)

        entry_id = unit.get("entry_id")
        if unit.get("type") == "story":
            if not entry_id:
                errors.append(f"reading_units story 缺少 entry_id: {unit_id}")
                continue
            if entry_id not in entry_ids:
                errors.append(f"reading_units 指向不存在或未發布的 entry: {entry_id}")
            if entry_id in story_entry_ids:
                errors.append(f"reading_units entry_id 重複: {entry_id}")
            story_entry_ids.add(entry_id)
            navigation[entry_id] = {
                "unit": unit,
                "previous": units[index - 1] if index > 0 else None,
                "next": units[index + 1] if index + 1 < len(units) else None,
            }

    missing_entries = sorted(entry_ids - story_entry_ids)
    extra_entries = sorted(story_entry_ids - entry_ids)
    if missing_entries:
        errors.append(f"reading_units 缺少已發布文章: {', '.join(missing_entries)}")
    if extra_entries:
        errors.append(f"reading_units 包含未知文章: {', '.join(extra_entries)}")
    return navigation


def journey_href_to_article_href(href):
    """將 Journey 根目錄相對路徑轉成 blog 頁面的相對路徑。"""
    if href.startswith("blog/"):
        return href[len("blog/"):]
    return f"../{href}"


def render_article_header(config, journey_title):
    brand_title = config.get("brand_title", "🧭 CH Travel OS")
    series_href = config.get("article_series_href", "../index.html")
    series_label = f'<span>{html_escape(journey_title)}</span>'
    series_html = (
        f'<a href="{html_escape(series_href)}" class="brand-series">{series_label}</a>'
        if series_href else f'<span class="brand-series">{series_label}</span>'
    )
    nav_links = config.get("article_nav_links")
    if nav_links:
        links_html = "\n".join(
            f'        <li><a href="{html_escape(link["href"])}">{html_escape(link["label"])}</a></li>'
            for link in nav_links
        )
    else:
        slot_3 = config.get(
            "nav_slot_3_html",
            '<li><a href="../index.html#stories">📖 深度遊記</a></li>',
        )
        links_html = "\n".join((
            '        <li><a href="../../index.html">🌍 全球旅程</a></li>',
            '        <li><a href="../index.html#stories">📖 深度遊記</a></li>',
            f"        {slot_3}",
        ))

    return f'''<nav class="site-nav">
    <div class="container">
      <div class="brand-group">
        <a href="../../index.html" class="brand-link">
          <span>{html_escape(brand_title)}</span>
        </a>
        <span class="brand-separator">/</span>
        {series_html}
      </div>
      <ul class="nav-links">
{links_html}
      </ul>
      <button class="nav-share-btn btn-share" type="button"><span>📤 分享</span></button>
    </div>
  </nav>'''


def render_related_stories(item, entries_by_id, images_dict, errors):
    related_ids = item.get("related", [])
    if not related_ids:
        return ""
    if len(related_ids) > 2:
        errors.append(f"{item['id']}: related 最多只能指定 2 篇")
        return ""
    if len(related_ids) != len(set(related_ids)):
        errors.append(f"{item['id']}: related 不得重複")
        return ""

    cards = []
    for related_id in related_ids:
        related = entries_by_id.get(related_id)
        if not related or related.get("status") == "draft":
            errors.append(f"{item['id']}: related 指向不存在或未發布的文章: {related_id}")
            continue
        if related_id == item["id"]:
            errors.append(f"{item['id']}: related 不得指向自己")
            continue

        image_url = related.get("og_image", "")
        image_filename = image_url.rsplit("/", 1)[-1]
        image_folder = related.get("image_folder", "")
        derivative = None
        for manifest_key, manifest_item in images_dict.items():
            if not manifest_key.startswith(f"{image_folder}/"):
                continue
            derivatives = manifest_item.get("derivatives", [])
            if any(d.get("filename") == image_filename for d in derivatives):
                derivative = next(
                    (d for d in derivatives if d.get("profile") == "thumb"),
                    next((d for d in derivatives if d.get("filename") == image_filename), None),
                )
                break
        if not derivative:
            errors.append(f"{item['id']}: related 封面找不到 Manifest 紀錄: {related_id}")
            continue

        related_href = Path(related["output"]).name
        related_title = html_escape(related["title"])
        cards.append(f'''        <a class="related-story-card" href="{html_escape(related_href)}">
          <img src="../images/{html_escape(image_folder)}/{html_escape(derivative['filename'])}" width="{derivative['width']}" height="{derivative['height']}" loading="lazy" decoding="async" alt="{related_title}">
          <span class="related-story-copy">
            <span class="related-story-kicker">延伸閱讀</span>
            <span class="related-story-title">{related_title}</span>
            <span class="related-story-arrow" aria-hidden="true">→</span>
          </span>
        </a>''')

    if not cards:
        return ""
    return f'''      <section class="related-stories" aria-labelledby="related-stories-title">
        <h2 id="related-stories-title">同系列還可以看</h2>
        <div class="related-story-grid">
{chr(10).join(cards)}
        </div>
      </section>'''


def replace_mobile_overview(html_content, mobile_overview):
    if not mobile_overview:
        return html_content
    replacement = f'''\\1<a href="{html_escape(mobile_overview['href'])}" class="dock-item">
      <span class="dock-icon">{html_escape(mobile_overview['icon'])}</span>
      <span>{html_escape(mobile_overview['label'])}</span>
    </a>'''
    return re.sub(
        r'(<div class="mobile-dock">\s*)<a href="[^"]*" class="dock-item">\s*'
        r'<span class="dock-icon">[^<]*</span>\s*<span>[^<]*</span>\s*</a>',
        replacement,
        html_content,
        count=1,
    )


def sync_public_core_assets():
    docs_core = DOCS_DIR / "core"
    for parts in PUBLIC_CORE_FILES:
        src = CORE_DIR.joinpath(*parts)
        if not src.exists():
            raise FileNotFoundError(f"找不到 core 公開資產: {src}")
        dest = docs_core.joinpath(*parts)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def build_trip(trip_slug="2026-germany", dest_slug=None, entry_id=None):
    config_path = TRIPS_DIR / trip_slug / "blog-migration.json"
    errors = []

    if not config_path.exists():
        print(f"❌ 找不到設定檔: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
        all_entries = config_data.get("entries", config_data) if isinstance(config_data, dict) else config_data

    entries_by_id = {item["id"]: item for item in all_entries}
    reading_navigation = build_reading_navigation(config_data, all_entries, errors)

    entries = [
        item for item in all_entries
        if item.get("status") != "draft" and (entry_id is None or item["id"] == entry_id)
    ]
    if entry_id and not entries:
        print(f"❌ 找不到 Blog 項目: {entry_id}")
        sys.exit(1)
    if entry_id and len(entries) != 1:
        print(f"❌ Blog 項目 ID 不唯一: {entry_id}")
        sys.exit(1)

    config_dest = config_data.get("dest") if isinstance(config_data, dict) else None
    journey_end_title = (
        config_data.get("journey_end_title", "旅程圓滿完結 · 回首頁")
        if isinstance(config_data, dict)
        else "旅程圓滿完結 · 回首頁"
    )
    if dest_slug and config_dest and dest_slug != config_dest:
        print(f"❌ dest 不一致: 參數={dest_slug}, config={config_dest}")
        sys.exit(1)
    dest_slug = dest_slug or config_dest or trip_slug
    manifest_path = DOCS_DIR / dest_slug / "image-manifest.json"

    if not manifest_path.exists():
        print(f"❌ 找不到 Manifest: {manifest_path}")
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    images_dict = manifest.get("images", {})
    built_count = 0

    build_scope = f"單篇編譯 ({entry_id})" if entry_id else "批次編譯"
    print(f"🚀 開始執行 {trip_slug} -> {dest_slug} Blog {build_scope}...")

    compiled_outputs = {}

    for item in entries:
        src_file = BASE_DIR / item["source"]
        out_file = BASE_DIR / item["output"]
        img_folder = item.get("image_folder", item["id"].split("-")[0] + "-" + item["id"].split("-")[1] if "-" in item["id"] else item["id"])

        if not src_file.exists():
            errors.append(f"設定之來源檔案不存在: {src_file}")
            continue

        html_content = src_file.read_text(encoding="utf-8")
        html_content = strip_editor_metadata(html_content)
        html_content = html_content.replace("平行改寫預覽版 (Place Preview)", "")

        show_gallery_titles = (
            config_data.get("show_gallery_titles", True)
            if isinstance(config_data, dict)
            else True
        )
        gallery_registry = render_gallery_registry(
            item,
            img_folder,
            errors,
            show_gallery_titles=show_gallery_titles,
        )
        gallery_marker_count = html_content.count("<!-- GALLERY_REGISTRY -->")
        if item.get("gallery_groups") and gallery_marker_count != 1:
            errors.append(
                f"{item['id']}: 使用 gallery_groups 時，GALLERY_REGISTRY 標記應恰好出現 1 次，實際為 {gallery_marker_count} 次"
            )
        html_content = html_content.replace("<!-- GALLERY_REGISTRY -->", gallery_registry)

        # 1. 調整核心資源路徑至 ../../core/
        html_content = re.sub(r'href="(?:\.\./)*css/style\.css(?:\?[^"]*)?"', 'href="../../core/css/style.css?v=20260903-nav-unify"', html_content)
        html_content = re.sub(r'href="(?:\.\./)*core/css/style\.css(?:\?[^"]*)?"', 'href="../../core/css/style.css?v=20260903-nav-unify"', html_content)
        html_content = re.sub(r'href="(?:\.\./)*vendor/glightbox/glightbox\.min\.css(?:\?[^"]*)?"', 'href="../../core/vendor/glightbox/glightbox.min.css"', html_content)
        html_content = re.sub(r'src="(?:\.\./)*vendor/glightbox/glightbox\.min\.js(?:\?[^"]*)?"', 'src="../../core/vendor/glightbox/glightbox.min.js"', html_content)
        html_content = re.sub(r'src="(?:\.\./)*js/app\.js(?:\?[^"]*)?"', 'src="../../core/js/app.js"', html_content)
        html_content = re.sub(r'src="(?:\.\./)*js/main\.js(?:\?[^"]*)?"', 'src="../../core/js/main.js"', html_content)

        # 1.1 統一文章頂部導覽列
        journey_title = config_data.get("journey_title", trip_slug) if isinstance(config_data, dict) else trip_slug
        standard_article_nav = render_article_header(config_data, journey_title)
        html_content = re.sub(r'<nav class="site-nav">[\s\S]*?</nav>', standard_article_nav.strip(), html_content)

        # 2. 轉換圖片為 WebP 規格
        rel_prefix = f"../images/{img_folder}"
        html_content = transform_html_images(html_content, images_dict, img_folder, rel_prefix, errors)

        # 2.1 預設統一全頁 gallery；需要橫直分組的文章可明確保留 source 分組。
        if not item.get("preserve_gallery_groups", False):
            article_gallery_name = f"{item['id']}-gallery"
            html_content = re.sub(r'data-gallery=["\'][^"\']+["\']', f'data-gallery="{article_gallery_name}"', html_content)

        # 3. 修正 OG 與 Canonical URL
        if item.get("og_url"):
            html_content = upsert_head_tag(
                html_content,
                r'<link\s+rel=["\']icon["\'][^>]*>',
                '<link rel="icon" href="../../favicon.svg" type="image/svg+xml">',
            )
            html_content = upsert_head_tag(
                html_content,
                r'<meta\s+property=["\']og:url["\']\s+content=["\'][^"\']*["\'][^>]*>',
                f'<meta property="og:url" content="{item["og_url"]}">',
            )
            html_content = upsert_head_tag(
                html_content,
                r'<link\s+rel=["\']canonical["\']\s+href=["\'][^"\']*["\'][^>]*>',
                f'<link rel="canonical" href="{item["og_url"]}">',
            )
        if item.get("og_image"):
            html_content = upsert_head_tag(
                html_content,
                r'<meta\s+property=["\']og:image["\']\s+content=["\'][^"\']*["\'][^>]*>',
                f'<meta property="og:image" content="{item["og_image"]}">',
            )

        # 4. 建立嚴格無 404 的篇章導航區塊 (Footer Navigation)
        reading_item = reading_navigation.get(item["id"])
        if reading_item:
            previous_unit = reading_item["previous"]
            next_unit = reading_item["next"]
            if previous_unit:
                prev_html = (
                    f'<a class="article-linear-link article-linear-link-prev" '
                    f'href="{html_escape(journey_href_to_article_href(previous_unit["href"]))}">'
                    f'<span class="article-linear-label">上一篇</span>'
                    f'<span>← {html_escape(previous_unit["title"])}</span></a>'
                )
            else:
                prev_html = (
                    '<a class="article-linear-link article-linear-link-prev" href="../index.html#stories">'
                    '<span class="article-linear-label">系列起點</span>'
                    '<span>← 澳洲旅程總覽</span></a>'
                )

            if next_unit:
                next_html = (
                    f'<a class="article-linear-link article-linear-link-next" '
                    f'href="{html_escape(journey_href_to_article_href(next_unit["href"]))}">'
                    f'<span class="article-linear-label">下一篇</span>'
                    f'<span>{html_escape(next_unit["title"])} →</span></a>'
                )
            else:
                next_html = (
                    '<a class="article-linear-link article-linear-link-next" href="../index.html">'
                    '<span class="article-linear-label">系列完結</span>'
                    '<span>回到澳洲旅程總覽 →</span></a>'
                )
        elif item.get("prev_link"):
            p_title = item["prev_title"]
            p_text = p_title if (p_title.startswith("←") or p_title.startswith("上一篇")) else f"← 上一篇：{p_title}"
            prev_html = f'<a href="{item["prev_link"]}" style="font-weight: 600; color: var(--primary); font-size: 0.95rem;">{p_text}</a>'
        else:
            prev_html = '<a href="../index.html#itinerary" style="font-weight: 600; color: var(--primary); font-size: 0.95rem;">← 🗺️ 行程起點 · 旅程總覽</a>'

        if reading_item:
            pass
        elif item.get("next_link"):
            n_title = item["next_title"]
            n_text = n_title if (n_title.startswith("🎉") or n_title.startswith("下一篇")) else f"下一篇：{n_title}"
            if not n_text.endswith("→"):
                n_text += " →"
            next_html = f'<a href="{item["next_link"]}" style="font-weight: 600; color: var(--primary); font-size: 0.95rem;">{n_text}</a>'
        elif item.get("next_title"):
            next_html = f'<span style="font-weight: 600; color: var(--text-muted); font-size: 0.95rem;">{item["next_title"]}</span>'
        else:
            next_html = f'<a href="../index.html" style="font-weight: 600; color: var(--primary); font-size: 0.95rem;">🎉 {journey_end_title} →</a>'

        day_num_match = re.search(r'day-(\d+)', item["id"])
        day_num = day_num_match.group(1) if day_num_match else "02"
        timeline_target = f"../day-{day_num}.html"
        timeline_physical = DOCS_DIR / dest_slug / f"day-{day_num}.html"
        if item.get("footer_center") == "gallery":
            center_html = '<button type="button" class="btn-gallery-quick">瀏覽完整圖集</button>'
        elif timeline_physical.exists():
            center_html = f'<a href="{timeline_target}" class="badge badge-gold" style="font-size: 0.9rem; padding: 0.5rem 1rem; text-decoration: none;">🧭 查看 Day {int(day_num)} 行程筆記</a>'
        else:
            timeline_fallback_link = item.get("timeline_fallback_link", "../index.html#itinerary")
            center_html = f'<a href="{timeline_fallback_link}" class="badge badge-gold" style="font-size: 0.9rem; padding: 0.5rem 1rem; text-decoration: none;">🗺️ 行程總覽</a>'

        if reading_item:
            related_html = render_related_stories(item, entries_by_id, images_dict, errors)
            new_nav_block = f'''<!-- 篇章導覽按鈕 -->
      <section class="article-navigation" aria-label="文章導覽">
        <div class="article-linear-nav">
          {prev_html}
          <div class="article-footer-actions">
            <a href="../index.html" class="article-overview-link">🇦🇺 澳洲旅程總覽</a>
            {center_html}
          </div>
          {next_html}
        </div>
{related_html}
        <a class="article-global-link" href="../../index.html">回到 CH x Travel 全球旅程 →</a>
      </section>'''
        else:
            new_nav_block = f'''<!-- 篇章導覽按鈕 -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin: 3.5rem 0 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color); flex-wrap: wrap; gap: 1rem;">
        {prev_html}
        {center_html}
        {next_html}
      </div>'''

        html_content, nav_replacement_count = re.subn(
            r'<!--\s*篇章導覽按鈕\s*-->[\s\S]*?</div>\s*</article>',
            f'{new_nav_block}\n    </article>',
            html_content
        )
        if nav_replacement_count != 1:
            errors.append(
                f"{item['id']}: 篇章導覽標記應恰好出現 1 次，實際為 {nav_replacement_count} 次"
            )

        # 5. 修正手機 Dock 與頂部導覽列中的未發布 timeline 連結
        if not timeline_physical.exists():
            timeline_fallback_link = item.get("timeline_fallback_link", "../index.html#itinerary")
            html_content = html_content.replace(f'href="../day-{day_num}.html"', f'href="{timeline_fallback_link}"')
        html_content = replace_mobile_overview(
            html_content,
            config_data.get("mobile_overview") if isinstance(config_data, dict) else None,
        )

        compiled_outputs[out_file] = (item["id"], html_content)

    hub_source = TRIPS_DIR / trip_slug / "sources" / "index.html"
    if entry_id is None and hub_source.exists():
        hub_output = DOCS_DIR / dest_slug / "index.html"
        hub_content = strip_editor_metadata(hub_source.read_text(encoding="utf-8"))
        hub_content = re.sub(r'href="(?:\.\./)*core/css/style\.css(?:\?[^"]*)?"', 'href="../core/css/style.css?v=20260903-nav-unify"', hub_content)
        compiled_outputs[hub_output] = ("journey-hub", hub_content)

    # 嚴格原子性把關：若有任何錯誤，絕不寫入磁碟！
    if errors:
        print(f"\n❌ 編譯失敗！發現 {len(errors)} 個錯誤，已中止寫入磁碟：")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    # 全域無錯誤，開始原子同步核心資產與寫入 HTML
    if entry_id is None and CORE_DIR.exists():
        sync_public_core_assets()

    for out_file, (item_id, content) in compiled_outputs.items():
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(content, encoding="utf-8")
        print(f"  ✅ 已編譯: {item_id} -> {out_file.name}")
        built_count += 1

    print(f"\n✨ 構建完成！共編譯 {built_count} 份標準 WebP 圖文遊記（零錯誤，原子寫入）。\n")


build_trips = build_trip

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CH Travel OS Blog Builder")
    parser.add_argument("--trip", default="2026-germany", help="目標旅程目錄名稱")
    parser.add_argument("--dest", default=None, help="目標發布目錄名稱（預設讀取 config）")
    parser.add_argument("--entry", default=None, help="只構建指定的 blog-migration entry ID")
    args = parser.parse_args()

    build_trip(args.trip, args.dest, args.entry)

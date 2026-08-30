#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CH Travel OS 2.0 - 圖片發布標準管線 (Image Publishing Pipeline)
依據 web-image-publishing-playbook.md 規範實作：
1. 原始 master 與公開輸出徹底隔離 (masters/ vs docs/<trip>/images/)
2. 自動生成 WebP 多尺寸 derivatives (480w, 960w, 1200w, 1600w 燈箱上限)
3. 徹底移除 EXIF、GPS 與相機裝置敏感資訊
4. 建立 image-manifest.json 與 sha256 驗證機制
"""

import os
import sys
import json
import time
import shutil
import datetime
import hashlib
import tempfile
from pathlib import Path
from PIL import Image, ImageOps

BASE_DIR = Path(__file__).resolve().parent.parent
MASTERS_DIR = BASE_DIR / "masters"
DOCS_DIR = BASE_DIR / "docs"

# 預設發布 Profile 規格 (禁止 upscale)
PROFILES = [
    {"name": "thumb", "width": 480},
    {"name": "content", "width": 960},
    {"name": "desktop", "width": 1200},
    {"name": "lightbox", "width": 1600}
]

PIPELINE_VERSION = "2.0.0"
DEFAULT_QUALITY = 84


def get_file_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def process_image(src_path, output_dir, rel_public_base, existing_manifest_entry=None, manifest_meta=None):
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = src_path.stem
    source_hash = get_file_sha256(src_path)

    # 嚴格合約快取比對 (比對 pipeline_version, quality, profiles, source_hash 與實體檔案)
    is_contract_valid = (
        manifest_meta
        and manifest_meta.get("pipeline_version") == PIPELINE_VERSION
        and manifest_meta.get("quality") == DEFAULT_QUALITY
        and manifest_meta.get("profiles") == PROFILES
    )

    if is_contract_valid and existing_manifest_entry and existing_manifest_entry.get("source_hash") == source_hash:
        derivatives = existing_manifest_entry.get("derivatives", [])
        if len(derivatives) == len(PROFILES):
            all_exist = True
            for d in derivatives:
                d_file = output_dir / d["filename"]
                if not d_file.exists() or d_file.stat().st_size != d.get("bytes"):
                    all_exist = False
                    break
            if all_exist:
                # Cache hit!
                return existing_manifest_entry, True

    derivatives = []
    generated_widths = set()

    with Image.open(src_path) as img:
        # 1. 套用 EXIF 方向校正
        img = ImageOps.exif_transpose(img)
        orig_w, orig_h = img.size

        # 2. 依 Profile 生成各尺寸 WebP (長邊約束，禁止 upscale，不保留 EXIF)
        for prof in PROFILES:
            max_target = prof["width"]
            if orig_w >= orig_h:
                # 橫圖 (Landscape)
                target_w = min(max_target, orig_w)
                target_h = int(round(orig_h * (target_w / orig_w)))
            else:
                # 直圖 (Portrait)
                target_h = min(max_target, orig_h)
                target_w = int(round(orig_w * (target_h / orig_h)))

            # 避免同一照片因原圖解析度較小而產生重複尺寸的檔案
            dim_key = (target_w, target_h)
            if dim_key in generated_widths:
                continue
            generated_widths.add(dim_key)

            out_filename = f"{stem}-{prof['name']}-{target_w}w.webp"
            out_file = output_dir / out_filename
            public_path = f"{rel_public_base}/{out_filename}".replace("\\", "/")

            # 縮放並移除所有 metadata 輸出為 WebP (原子化寫入臨時檔再替換)
            resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            # 使用暫存檔確保原子寫入與無損中斷
            temp_fd, temp_path = tempfile.mkstemp(suffix=".webp", dir=output_dir)
            os.close(temp_fd)
            try:
                resized.save(temp_path, format="WEBP", quality=DEFAULT_QUALITY, method=6)
                # Windows Defender/Index 暫時鎖定重試機制
                for attempt in range(5):
                    try:
                        if os.path.exists(out_file):
                            os.remove(out_file)
                        os.replace(temp_path, out_file)
                        break
                    except PermissionError:
                        time.sleep(0.15)
                else:
                    if os.path.exists(temp_path):
                        shutil.copyfile(temp_path, out_file)
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass

            derivatives.append({
                "profile": prof["name"],
                "width": target_w,
                "height": target_h,
                "format": "webp",
                "filename": out_filename,
                "publicPath": public_path,
                "bytes": out_file.stat().st_size,
                "hash": get_file_sha256(out_file)
            })

    return {
        "id": stem,
        "original_filename": src_path.name,
        "original_width": orig_w,
        "original_height": orig_h,
        "source_hash": source_hash,
        "derivatives": derivatives
    }, False


def process_trip(trip_slug, dest_slug=None, pilot_day=None):
    if not dest_slug:
        dest_slug = trip_slug

    trip_master = MASTERS_DIR / trip_slug
    if not trip_master.exists():
        print(f"⚠️ Master 目錄不存在: {trip_master}")
        return

    trip_output = DOCS_DIR / dest_slug / "images"
    manifest_file = DOCS_DIR / dest_slug / "image-manifest.json"

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    manifest_data = {
        "pipeline_version": PIPELINE_VERSION,
        "trip": trip_slug,
        "dest": dest_slug,
        "generated_at": now_iso,
        "quality": DEFAULT_QUALITY,
        "profiles": PROFILES,
        "images": {}
    }
    cached_images = {}
    loaded_manifest = None
    if manifest_file.exists():
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                loaded_manifest = json.load(f)
                cached_images = loaded_manifest.get("images", {})
        except Exception:
            pass

    # Scoped runs must not erase entries owned by unprocessed day folders.
    # Preserve them only when the existing manifest uses the current contract.
    if pilot_day and cached_images:
        manifest_contract_valid = (
            loaded_manifest
            and loaded_manifest.get("pipeline_version") == PIPELINE_VERSION
            and loaded_manifest.get("quality") == DEFAULT_QUALITY
            and loaded_manifest.get("profiles") == PROFILES
            and loaded_manifest.get("trip") == trip_slug
            and loaded_manifest.get("dest") == dest_slug
        )
        if not manifest_contract_valid:
            print("❌ Pilot 模式無法沿用舊版 Manifest 合約；請先執行一次全旅程圖片管線。", flush=True)
            sys.exit(1)

        pilot_prefix = f"{pilot_day}/"
        manifest_data["images"].update({
            key: entry
            for key, entry in cached_images.items()
            if not key.startswith(pilot_prefix)
        })

    # 掃描天數資料夾
    day_folders = sorted([d for d in trip_master.iterdir() if d.is_dir()])
    if pilot_day:
        day_folders = [d for d in day_folders if d.name == pilot_day]

    total_processed = 0
    cache_hits = 0
    valid_output_files_by_dir = {}
    failures = []

    for day_dir in day_folders:
        day_name = day_dir.name
        out_day_dir = trip_output / day_name
        rel_base = f"{dest_slug}/images/{day_name}"

        img_files = sorted([f for f in day_dir.iterdir() if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp", ".heic"]])
        print(f"📁 處理中: {trip_slug} -> docs/{dest_slug} / {day_name} (共 {len(img_files)} 張照片)...", flush=True)

        for img_path in img_files:
            try:
                img_key = f"{day_name}/{img_path.name}"
                existing_entry = cached_images.get(img_key)
                res, is_cache = process_image(img_path, out_day_dir, rel_base, existing_entry, manifest_meta=manifest_data)
                manifest_data["images"][img_key] = res
                total_processed += 1
                if is_cache:
                    cache_hits += 1
                valid_output_files = valid_output_files_by_dir.setdefault(out_day_dir, set())
                for d in res.get("derivatives", []):
                    valid_output_files.add(out_day_dir / d["filename"])
            except Exception as e:
                msg = f"{day_name}/{img_path.name}: {e}"
                failures.append(msg)
                print(f"  ❌ 處理失敗 {msg}", flush=True)

    if failures:
        print(f"\n❌ 圖片管線失敗！發現 {len(failures)} 張圖片處理錯誤，已中止清理舊圖與寫入 Manifest：", flush=True)
        for failure in failures:
            print(f"  - {failure}", flush=True)
        sys.exit(1)

    # 全部圖片成功後，才清理已刪除 master 殘留的舊 WebP 檔案。
    for out_day_dir, valid_output_files in valid_output_files_by_dir.items():
        if out_day_dir.exists():
            for f in out_day_dir.glob("*.webp"):
                if f not in valid_output_files:
                    try:
                        f.unlink()
                        print(f"  🗑️ 清理孤立舊圖: {f.name}", flush=True)
                    except Exception:
                        pass

    # 儲存 Manifest
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, ensure_ascii=False, indent=2)

    print(f"\n✨ 完成！共掃描 {total_processed} 張照片（Cache Hit: {cache_hits}，新生成: {total_processed - cache_hits}），Manifest 儲存至 {manifest_file}\n", flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CH Travel OS Image Pipeline")
    parser.add_argument("--trip", default="2026-germany", help="目標旅程目錄名稱 (如 2026-germany)")
    parser.add_argument("--dest", default=None, help="目標輸出目錄名稱 (預設同 --trip，如 germany)")
    parser.add_argument("--pilot-day", default=None, help="僅處理指定天數進行 Pilot (如 day-02)")
    args = parser.parse_args()

    process_trip(args.trip, args.dest, args.pilot_day)

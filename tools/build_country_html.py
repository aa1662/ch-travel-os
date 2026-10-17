#!/usr/bin/env python3
"""Build country hubs from maintained sources with route and asset validation."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COUNTRIES_DIR = ROOT / "countries"
DOCS_DIR = ROOT / "docs"


class CountryBuildError(ValueError):
    pass


def load_country(country_id: str) -> tuple[dict, Path]:
    if not country_id or Path(country_id).name != country_id or country_id in {".", ".."}:
        raise CountryBuildError(f"非法 country id: {country_id!r}")

    config_path = COUNTRIES_DIR / country_id / "country.json"
    if not config_path.exists():
        raise CountryBuildError(f"找不到 Country Hub 設定: {config_path.relative_to(ROOT)}")

    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("schema_version") != 1:
        raise CountryBuildError(f"不支援的 schema_version: {config.get('schema_version')!r}")
    if config.get("id") != country_id:
        raise CountryBuildError("country.json 的 id 必須與資料夾名稱一致")
    return config, config_path


def resolve_repo_path(value: str, label: str) -> Path:
    if not value:
        raise CountryBuildError(f"缺少 {label}")
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise CountryBuildError(f"{label} 超出 repository: {value}") from exc
    return path


def validate_country(config: dict, config_path: Path) -> tuple[Path, Path, str]:
    country_id = config["id"]
    source = resolve_repo_path(config.get("source", ""), "source")
    output = resolve_repo_path(config.get("output", ""), "output")
    expected_output = (DOCS_DIR / country_id / "index.html").resolve()
    if output != expected_output:
        raise CountryBuildError(f"output 必須是 docs/{country_id}/index.html")
    if not source.exists():
        raise CountryBuildError(f"Source 不存在: {source.relative_to(ROOT)}")

    rendered = source.read_text(encoding="utf-8")
    canonical = config.get("canonical", "")
    if canonical and canonical not in rendered:
        raise CountryBuildError("Source 缺少 country.json 指定的 canonical URL")
    if "file://" in rendered:
        raise CountryBuildError("Country Hub 不得包含 file:// 路徑")

    journeys = config.get("journeys")
    if not isinstance(journeys, list) or not journeys:
        raise CountryBuildError("journeys 必須是非空陣列")

    seen_ids: set[str] = set()
    for journey in journeys:
        journey_id = journey.get("id", "")
        href = journey.get("href", "")
        image = journey.get("image", "")
        if not journey_id or journey_id in seen_ids:
            raise CountryBuildError(f"Journey id 缺少或重複: {journey_id!r}")
        seen_ids.add(journey_id)
        if href not in rendered:
            raise CountryBuildError(f"Source 未引用 Journey: {journey_id} -> {href}")
        if image not in rendered:
            raise CountryBuildError(f"Source 未引用封面: {journey_id} -> {image}")

        journey_target = (output.parent / href).resolve()
        image_target = (output.parent / image).resolve()
        for target, label in ((journey_target, "Journey"), (image_target, "封面")):
            try:
                target.relative_to(DOCS_DIR.resolve())
            except ValueError as exc:
                raise CountryBuildError(f"{label} 路徑超出 docs: {target}") from exc
            if not target.exists():
                raise CountryBuildError(f"{label} 尚未建置: {target.relative_to(ROOT)}")

    return source, output, rendered


def write_atomic(output: Path, content: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=output.parent)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        temp_path.write_text(content, encoding="utf-8", newline="\n")
        os.replace(temp_path, output)
    finally:
        temp_path.unlink(missing_ok=True)


def build_country(country_id: str, check: bool = False) -> bool:
    config, config_path = load_country(country_id)
    _, output, rendered = validate_country(config, config_path)
    current = output.read_text(encoding="utf-8") if output.exists() else None
    if current == rendered:
        print(f"OK {output.relative_to(ROOT)}")
        return True
    if check:
        print(f"STALE {output.relative_to(ROOT)}")
        return False
    write_atomic(output, rendered)
    print(f"BUILT {output.relative_to(ROOT)}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Build CH x Travel country hubs")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--country", help="Country Hub id，例如 japan")
    group.add_argument("--all", action="store_true", help="建置所有已登錄 Country Hub")
    parser.add_argument("--check", action="store_true", help="只檢查輸出是否最新")
    args = parser.parse_args()

    country_ids = (
        sorted(path.parent.name for path in COUNTRIES_DIR.glob("*/country.json"))
        if args.all else [args.country]
    )
    if not country_ids:
        raise CountryBuildError("沒有可建置的 Country Hub")

    ok = True
    for country_id in country_ids:
        ok = build_country(country_id, check=args.check) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CountryBuildError as exc:
        print(f"ERROR {exc}")
        raise SystemExit(1)

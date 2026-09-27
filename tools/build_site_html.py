#!/usr/bin/env python3
"""Build global CH x Travel pages from their maintained site sources."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = {
    ROOT / "site" / "about" / "index.html": ROOT / "docs" / "about" / "index.html",
    ROOT / "core" / "css" / "about.css": ROOT / "docs" / "core" / "css" / "about.css",
}


def build(check: bool) -> int:
    stale: list[str] = []

    for source, output in FILES.items():
        rendered = source.read_text(encoding="utf-8")
        current = output.read_text(encoding="utf-8") if output.exists() else None

        if current == rendered:
            print(f"OK {output.relative_to(ROOT)}")
            continue

        if check:
            stale.append(str(output.relative_to(ROOT)))
            continue

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"BUILT {output.relative_to(ROOT)}")

    if stale:
        print("STALE " + ", ".join(stale))
        return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail when generated pages are stale")
    args = parser.parse_args()
    return build(args.check)


if __name__ == "__main__":
    raise SystemExit(main())

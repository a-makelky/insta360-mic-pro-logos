#!/usr/bin/env python3
"""Validate Mic Pro logo assets and catalog integrity."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SIZE = (240, 208)


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def validate_png(path: Path, failures: list[str]) -> None:
    if not path.exists():
        fail(f"Missing file: {path}", failures)
        return
    if path.suffix.lower() != ".png":
        fail(f"Not a PNG: {path}", failures)
        return

    image = Image.open(path).convert("RGBA")
    if image.size != EXPECTED_SIZE:
        fail(f"{path} is {image.size}, expected {EXPECTED_SIZE}", failures)

    alpha_min, alpha_max = image.getchannel("A").getextrema()
    if alpha_min != 0:
        fail(f"{path} does not contain transparent pixels", failures)
    if alpha_max == 0:
        fail(f"{path} has no visible pixels", failures)


def main() -> int:
    failures: list[str] = []
    catalog_path = ROOT / "catalog.json"
    site_catalog_path = ROOT / "site" / "logos.json"

    if not catalog_path.exists():
        fail("Missing catalog.json", failures)
        catalog = []
    else:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

    if site_catalog_path.exists():
        site_catalog = json.loads(site_catalog_path.read_text(encoding="utf-8"))
        if site_catalog != catalog:
            fail("site/logos.json is not in sync with catalog.json", failures)
    else:
        fail("Missing site/logos.json", failures)

    seen_slugs: set[str] = set()
    for entry in catalog:
        slug = entry.get("slug")
        if not slug:
            fail(f"Catalog entry missing slug: {entry}", failures)
            continue
        if slug in seen_slugs:
            fail(f"Duplicate slug: {slug}", failures)
        seen_slugs.add(slug)

        for variant in ("color", "mono"):
            rel = entry.get("files", {}).get(variant)
            if not rel:
                fail(f"{slug} missing {variant} file path", failures)
                continue
            validate_png(ROOT / rel, failures)

        if not entry.get("source"):
            fail(f"{slug} missing source URL or source note", failures)

    logo_dirs = {p.name for p in (ROOT / "logos").iterdir() if p.is_dir()}
    catalog_dirs = set(seen_slugs)
    for orphan in sorted(logo_dirs - catalog_dirs):
        fail(f"Logo folder not present in catalog: {orphan}", failures)

    if failures:
        print("Validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Validation passed: {len(catalog)} logos")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validate the generated Excalidraw library before distribution."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "downloads" / "insta360-mic-pro-ai-tools.excalidrawlib"
DISABLED_TYPES = {"image", "iframe", "embeddable"}
EXPECTED_SIZE = (240, 208)


def main() -> int:
    failures: list[str] = []
    data = json.loads(LIBRARY.read_text(encoding="utf-8"))

    if data.get("type") != "excalidrawlib":
        failures.append("type must be excalidrawlib")
    if data.get("version") != 2:
        failures.append("version must be 2")
    if not data.get("source"):
        failures.append("source is required")

    items = data.get("libraryItems", [])
    if len(items) < 3:
        failures.append("library must contain at least 3 related items")

    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for item in items:
        name = item.get("name")
        if not name:
            failures.append("every library item needs a name")
        elif name in seen_names:
            failures.append(f"duplicate item name: {name}")
        else:
            seen_names.add(name)

        elements = item.get("elements", [])
        if not elements:
            failures.append(f"{name}: item has no elements")
            continue
        if len(elements) > 550:
            failures.append(f"{name}: {len(elements)} elements exceeds limit")

        group_ids = {tuple(element.get("groupIds", [])) for element in elements}
        if len(group_ids) != 1 or not next(iter(group_ids), ()):
            failures.append(f"{name}: elements must share one group")

        for element in elements:
            element_id = element.get("id")
            if not element_id:
                failures.append(f"{name}: element missing id")
            elif element_id in seen_ids:
                failures.append(f"{name}: duplicate element id {element_id}")
            else:
                seen_ids.add(element_id)
            if element.get("type") in DISABLED_TYPES:
                failures.append(f"{name}: disabled element type {element['type']}")
            if element.get("type") != "rectangle":
                failures.append(f"{name}: unexpected element type {element.get('type')}")
            if element.get("x", -1) < 0 or element.get("y", -1) < 0:
                failures.append(f"{name}: element begins outside the Mic Pro artboard")
            if element.get("x", 0) + element.get("width", 0) > EXPECTED_SIZE[0]:
                failures.append(f"{name}: element exceeds artboard width")
            if element.get("y", 0) + element.get("height", 0) > EXPECTED_SIZE[1]:
                failures.append(f"{name}: element exceeds artboard height")

    if failures:
        print("Excalidraw validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        f"Excalidraw validation passed: {len(items)} items, "
        f"{len(seen_ids)} native elements"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Build a portable Excalidraw library from the Mic Pro PNG assets.

Excalidraw libraries currently reject image elements, so each source PNG is
reconstructed as a compact set of merged, native rectangle elements. The
result remains transparent, portable, and compatible with public library
submission.
"""

from __future__ import annotations

import hashlib
import json
import random
import string
import time
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "downloads" / "insta360-mic-pro-ai-tools.excalidrawlib"
PREVIEW = ROOT / "previews" / "excalidraw-ai-tools-preview.png"
SOURCE = "https://aaronmakelky.com/tools/insta360-mic-pro-logo-kit"
CELL_SIZE = 4
MAX_COLORS = 12
EXCLUDED_DUPLICATE_SLUGS = {"gpt", "sora"}


class PixelRun(NamedTuple):
    x_start: int
    x_end: int
    color: str
    opacity: int


class PixelRect(NamedTuple):
    x_start: int
    x_end: int
    y_start: int
    y_end: int
    color: str
    opacity: int


def stable_int(value: str, maximum: int = 2_147_483_646) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return 1 + int.from_bytes(digest[:8], "big") % maximum


def stable_id(value: str, length: int = 21) -> str:
    alphabet = string.ascii_letters + string.digits + "_-"
    rng = random.Random(stable_int(value))
    return "".join(rng.choice(alphabet) for _ in range(length))


def quantized_grid(image_path: Path) -> list[list[tuple[str, int] | None]]:
    image = Image.open(image_path).convert("RGBA")
    small = image.resize(
        (image.width // CELL_SIZE, image.height // CELL_SIZE),
        Image.Resampling.BOX,
    )
    quantized = small.quantize(colors=MAX_COLORS, method=Image.Quantize.FASTOCTREE)
    rgba = quantized.convert("RGBA")

    grid: list[list[tuple[str, int] | None]] = []
    for y in range(rgba.height):
        row: list[tuple[str, int] | None] = []
        for x in range(rgba.width):
            red, green, blue, alpha = rgba.getpixel((x, y))
            if alpha < 48:
                row.append(None)
                continue
            row.append((f"#{red:02x}{green:02x}{blue:02x}", 100))
        grid.append(row)
    return grid


def row_runs(row: list[tuple[str, int] | None]) -> list[PixelRun]:
    runs: list[PixelRun] = []
    start = 0
    current = row[0]
    for x in range(1, len(row) + 1):
        value = row[x] if x < len(row) else None
        if value == current:
            continue
        if current is not None:
            runs.append(PixelRun(start, x, current[0], current[1]))
        start = x
        current = value
    return runs


def merge_runs(grid: list[list[tuple[str, int] | None]]) -> list[PixelRect]:
    completed: list[PixelRect] = []
    active: dict[PixelRun, int] = {}

    for y, row in enumerate(grid):
        current_runs = set(row_runs(row))
        for run, y_start in list(active.items()):
            if run not in current_runs:
                completed.append(
                    PixelRect(
                        run.x_start,
                        run.x_end,
                        y_start,
                        y,
                        run.color,
                        run.opacity,
                    )
                )
                del active[run]
        for run in current_runs:
            active.setdefault(run, y)

    y_end = len(grid)
    for run, y_start in active.items():
        completed.append(
            PixelRect(
                run.x_start,
                run.x_end,
                y_start,
                y_end,
                run.color,
                run.opacity,
            )
        )
    return completed


def rectangle_element(rect: PixelRect, slug: str, group_id: str, index: int) -> dict:
    x = rect.x_start * CELL_SIZE
    y = rect.y_start * CELL_SIZE
    width = (rect.x_end - rect.x_start) * CELL_SIZE
    height = (rect.y_end - rect.y_start) * CELL_SIZE
    element_key = f"{slug}:{index}:{x}:{y}:{width}:{height}:{rect.color}:{rect.opacity}"
    return {
        "id": stable_id(element_key),
        "type": "rectangle",
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "angle": 0,
        "strokeColor": rect.color,
        "backgroundColor": rect.color,
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": rect.opacity,
        "groupIds": [group_id],
        "frameId": None,
        "roundness": None,
        "seed": stable_int(f"{element_key}:seed"),
        "version": 1,
        "versionNonce": stable_int(f"{element_key}:nonce"),
        "isDeleted": False,
        "boundElements": None,
        "updated": 0,
        "link": None,
        "locked": False,
    }


def build_item(entry: dict, aliases: list[str]) -> tuple[dict, int]:
    slug = entry["slug"]
    group_id = stable_id(f"{slug}:group")
    rects = merge_runs(quantized_grid(ROOT / entry["files"]["color"]))
    elements = [
        rectangle_element(rect, slug, group_id, index)
        for index, rect in enumerate(rects)
    ]
    name = " / ".join(aliases)
    item = {
        "id": stable_id(f"{slug}:library-item"),
        "status": "unpublished",
        "created": 0,
        "name": name,
        "elements": elements,
    }
    return item, len(elements)


def render_preview(entries: list[dict], items: list[dict], counts: dict[str, int]) -> None:
    card_width = 300
    card_height = 290
    columns = 3
    rows = (len(entries) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * card_width, rows * card_height), "#f1f3f5")
    draw = ImageDraw.Draw(canvas)

    for index, (entry, item) in enumerate(zip(entries, items)):
        left = (index % columns) * card_width
        top = (index // columns) * card_height
        draw.rounded_rectangle(
            (left + 12, top + 12, left + card_width - 12, top + card_height - 12),
            radius=16,
            fill="white",
            outline="#d9dde3",
        )
        image = Image.new("RGBA", (240, 208), (0, 0, 0, 0))
        image_draw = ImageDraw.Draw(image)
        for element in item["elements"]:
            x = round(element["x"])
            y = round(element["y"])
            right = round(element["x"] + element["width"])
            bottom = round(element["y"] + element["height"])
            image_draw.rectangle(
                (x, y, right, bottom),
                fill=element["backgroundColor"],
            )
        canvas.paste(image, (left + 30, top + 26), image)
        label = entry["display_name"]
        draw.text((left + 24, top + 242), label, fill="#111111")
        draw.text(
            (left + 24, top + 262),
            f"{counts[entry['slug']]} native elements",
            fill="#687076",
        )

    PREVIEW.parent.mkdir(exist_ok=True)
    canvas.save(PREVIEW, optimize=True)


def main() -> None:
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    ai_entries = [
        entry
        for entry in catalog
        if entry["category"] == "AI tools" and entry["slug"] not in EXCLUDED_DUPLICATE_SLUGS
    ]

    aliases_by_hash: dict[str, list[str]] = defaultdict(list)
    for entry in catalog:
        if entry["category"] == "AI tools":
            aliases_by_hash[entry["sha256"]["color"]].append(entry["name"])

    items: list[dict] = []
    counts: dict[str, int] = {}
    preview_entries: list[dict] = []
    for entry in ai_entries:
        aliases = aliases_by_hash[entry["sha256"]["color"]]
        item, count = build_item(entry, aliases)
        if count > 550:
            raise RuntimeError(f"{entry['name']} generated {count} elements; limit is 550")
        items.append(item)
        counts[entry["slug"]] = count
        preview_entries.append({**entry, "display_name": item["name"]})

    library = {
        "type": "excalidrawlib",
        "version": 2,
        "source": SOURCE,
        "libraryItems": items,
    }
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(library, separators=(",", ":")) + "\n", encoding="utf-8")
    render_preview(preview_entries, items, counts)

    total_elements = sum(counts.values())
    print(
        f"Built {OUTPUT.relative_to(ROOT)}: "
        f"{len(items)} items, {total_elements} native elements"
    )
    for entry in preview_entries:
        print(f"- {entry['display_name']}: {counts[entry['slug']]}")


if __name__ == "__main__":
    main()

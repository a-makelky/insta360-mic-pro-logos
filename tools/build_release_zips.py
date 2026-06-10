#!/usr/bin/env python3
"""Build downloadable ZIP bundles from catalog.json."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "downloads"


def write_zip(name: str, variant: str | None) -> None:
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    DOWNLOADS.mkdir(exist_ok=True)
    with zipfile.ZipFile(DOWNLOADS / name, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for entry in catalog:
            if variant:
                file_path = ROOT / entry["files"][variant]
                archive.write(file_path, arcname=file_path.name)
            else:
                for current_variant in ("color", "mono"):
                    file_path = ROOT / entry["files"][current_variant]
                    archive.write(file_path, arcname=f"{current_variant}/{file_path.name}")


def main() -> None:
    write_zip("insta360-mic-pro-logos-color.zip", "color")
    write_zip("insta360-mic-pro-logos-high-contrast.zip", "mono")
    write_zip("insta360-mic-pro-logos-all.zip", None)
    print("Built release ZIPs")


if __name__ == "__main__":
    main()

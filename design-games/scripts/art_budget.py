#!/usr/bin/env python3
"""Approximate art-budget helpers; validate final budgets on target platforms."""

import argparse
import json
import math
from typing import Any, Dict, List


def texture_memory(width: int, height: int, bits_per_pixel: float, mip_levels: int = 0, layers: int = 1) -> Dict[str, Any]:
    """Pixel-count estimate; mip_levels=0 means the full chain down to 1x1."""
    if width < 1 or height < 1 or layers < 1:
        raise ValueError("width, height and layers must be at least 1")
    if bits_per_pixel <= 0:
        raise ValueError("bits_per_pixel must be greater than zero")
    if mip_levels < 0:
        raise ValueError("mip_levels must be zero (full) or positive")

    full_levels = int(math.floor(math.log2(max(width, height)))) + 1
    count = full_levels if mip_levels == 0 else min(mip_levels, full_levels)
    level_bytes: List[int] = []
    w, h = width, height
    for _ in range(count):
        level_bytes.append(math.ceil(w * h * bits_per_pixel / 8) * layers)
        w, h = max(1, w // 2), max(1, h // 2)

    total = sum(level_bytes)
    return {
        "level_count": count,
        "bytes_by_level": level_bytes,
        "total_bytes": total,
        "total_mib": total / (1024 ** 2),
        "assumption": "pixel-count approximation; excludes block alignment, headers, duplicates, streaming residency and platform allocation",
    }


def lod_chain(base_triangles: int, ratios: List[float]) -> Dict[str, Any]:
    if base_triangles < 0:
        raise ValueError("base_triangles must be non-negative")
    if not ratios:
        raise ValueError("at least one ratio is required")
    if any(not 0 < ratio <= 1 for ratio in ratios):
        raise ValueError("each ratio must be in (0, 1]")
    triangles = [int(round(base_triangles * ratio)) for ratio in ratios]
    return {
        "triangles_by_lod": triangles,
        "ratios": ratios,
        "assumption": "triangle counts are geometric estimates; validate silhouette, skinning, shadows and switching visually",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    texture = subparsers.add_parser("texture")
    texture.add_argument("--width", type=int, required=True)
    texture.add_argument("--height", type=int, required=True)
    texture.add_argument("--bits-per-pixel", type=float, required=True)
    texture.add_argument("--mip-levels", type=int, default=0, help="0 = full chain")
    texture.add_argument("--layers", type=int, default=1)

    lod = subparsers.add_parser("lod")
    lod.add_argument("--base-triangles", type=int, required=True)
    lod.add_argument("--ratios", type=float, nargs="+", required=True)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "texture":
            result = texture_memory(args.width, args.height, args.bits_per_pixel, args.mip_levels, args.layers)
        else:
            result = lod_chain(args.base_triangles, args.ratios)
    except ValueError as error:
        parser.error(str(error))
        return
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

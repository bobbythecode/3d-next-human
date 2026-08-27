#!/usr/bin/env python3
"""CLI gate for Blender-authored BVH poses (default MakeHuman rig)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from service.pose_bvh_validate import validate_pose_bvh_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a BVH pose file for MakeHuman / human-api."
    )
    parser.add_argument(
        "bvh",
        type=Path,
        help="Path to .bvh file (e.g. makehuman/data/poses/tpose.bvh)",
    )
    args = parser.parse_args(argv)

    result = validate_pose_bvh_file(args.bvh)
    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if result.ok:
        print(f"ok: {args.bvh}")
        return 0

    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

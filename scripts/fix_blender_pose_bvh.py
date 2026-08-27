#!/usr/bin/env python3
"""Rewrite a Blender-exported BVH into MakeHuman-native hierarchy + clean root.

Blender's BVH exporter (MH FBX/Collada round-trip) typically bakes ~90° on the
root bone. Apply Rotation in the viewport does not remove that channel value, so
Pose Library loads the mannequin lying down. This script:

1. Loads the BVH (force Z-up conversion by default — Blender is Z-up)
2. Builds an animation track on the default MH skeleton
3. Sets root to identity (Rx=0) and zero translation
4. Zeros face-helper bones (Blender bakes garbage on eye/oris/tongue/…)
5. Zeros spine05 / pelvis.L / pelvis.R axis-bake (~175 deg — required with root=0;
   keeping them while forcing root=180 also works but adds ~0.5 deg forward lean)
6. Writes a BVH from the MH skeleton rest (same family as tpose.bvh)
"""

from __future__ import annotations

import argparse
import math
import shutil
import sys
from pathlib import Path

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from service.bootstrap import ensure_runtime
from service.pose_bvh_validate import validate_pose_bvh_file

# Substrings matching MH face / expression helpers (not body pose).
_FACE_BONE_PARTS = (
    "eye",
    "jaw",
    "tongue",
    "oris",
    "oculi",
    "special",
    "levator",
    "temporalis",
    "risorius",
    "orbicularis",
    "nasalis",
    "zygomatic",
    "mentalis",
    "buccinator",
    "masseter",
)


def _is_face_bone(name: str) -> bool:
    lower = name.lower()
    return any(part in lower for part in _FACE_BONE_PARTS)


def _root_matrix_x(degrees: float) -> np.ndarray:
    """3x4 pose matrix: rotation about X, zero translation."""
    rad = math.radians(degrees)
    c, s = math.cos(rad), math.sin(rad)
    mat = np.zeros((3, 4), dtype=np.float32)
    mat[0, 0] = 1.0
    mat[1, 1] = c
    mat[1, 2] = -s
    mat[2, 1] = s
    mat[2, 2] = c
    return mat


def _set_root_pose(anim, root_rx_deg: float) -> None:
    """Set every frame's root to Rx(root_rx_deg), translation zero."""
    n = anim.nBones
    root = _root_matrix_x(root_rx_deg)
    for f_idx in range(anim.nFrames):
        anim.data[f_idx * n][:] = root
    anim.resetBaked()


# Direct root children that inherit Blender axis-bake (~175 deg), not real pose.
_AXIS_BAKE_BONES = frozenset({"spine05", "pelvis.L", "pelvis.R"})


def _zero_bones(anim, bone_names: list[str], predicate) -> int:
    n = anim.nBones
    identity = np.identity(4, dtype=np.float32)[:3, :4]
    cleared = 0
    for b_idx, name in enumerate(bone_names):
        if not predicate(name):
            continue
        cleared += 1
        for f_idx in range(anim.nFrames):
            anim.data[f_idx * n + b_idx][:] = identity
    anim.resetBaked()
    return cleared


def _zero_face_bones(anim, bone_names: list[str]) -> int:
    return _zero_bones(anim, bone_names, _is_face_bone)


def _zero_axis_bake_bones(anim, bone_names: list[str]) -> int:
    return _zero_bones(anim, bone_names, lambda n: n in _AXIS_BAKE_BONES)


def fix_blender_pose_bvh(
    src: Path,
    dst: Path,
    *,
    convert_from_z_up: bool | str = True,
    dummy_joints: bool = True,
    root_rx_deg: float = 0.0,
    clear_face: bool = True,
    clear_axis_bake: bool = True,
) -> int:
    ensure_runtime()
    import bvh
    from service.session import _load_human

    person = _load_human()
    skel = person.getBaseSkeleton()
    bone_names = [b.name for b in skel.getBones()]
    loaded = bvh.load(str(src), convertFromZUp=convert_from_z_up)
    anim = loaded.createAnimationTrack(skel, name=src.stem)
    if anim is None:
        raise RuntimeError("createAnimationTrack returned None")
    _set_root_pose(anim, root_rx_deg)
    cleared_face = _zero_face_bones(anim, bone_names) if clear_face else 0
    cleared_axis = _zero_axis_bake_bones(anim, bone_names) if clear_axis_bake else 0

    out = bvh.BVH()
    out.name = src.stem
    out.fromSkeleton(skel, anim, dummyJoints=dummy_joints)
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.writeToFile(str(dst))
    return cleared_face + cleared_axis


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fix Blender-exported BVH root orientation for MakeHuman."
    )
    parser.add_argument("bvh", type=Path, help="Input .bvh from Blender")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output path (default: overwrite input after .bak)",
    )
    parser.add_argument(
        "--z-up",
        choices=("true", "false", "auto"),
        default="true",
        help="convertFromZUp when reading Blender file (default: true)",
    )
    parser.add_argument(
        "--root-rx",
        type=float,
        default=0.0,
        help="Root X rotation after rewrite (default: 0; use 180 only with --keep-axis-bake)",
    )
    parser.add_argument(
        "--keep-axis-bake",
        action="store_true",
        help="Keep spine05/pelvis axis-bake from Blender (default: zero them)",
    )
    parser.add_argument(
        "--keep-face",
        action="store_true",
        help="Do not zero face-helper bones (default: clear them)",
    )
    args = parser.parse_args(argv)

    src = args.bvh.resolve()
    if not src.is_file():
        print(f"error: file not found: {src}", file=sys.stderr)
        return 1

    z_map = {"true": True, "false": False, "auto": "auto"}
    convert = z_map[args.z_up]
    dst = args.output.resolve() if args.output else src

    if dst == src:
        bak = src.with_suffix(src.suffix + ".bak")
        shutil.copy2(src, bak)
        print(f"backup: {bak}")

    try:
        cleared = fix_blender_pose_bvh(
            src,
            dst,
            convert_from_z_up=convert,
            root_rx_deg=args.root_rx,
            clear_face=not args.keep_face,
            clear_axis_bake=not args.keep_axis_bake,
        )
    except Exception as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    result = validate_pose_bvh_file(dst)
    for warning in result.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if not result.ok:
        for error in result.errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"ok: wrote {dst} (root Rx={args.root_rx}, bones cleared={cleared})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

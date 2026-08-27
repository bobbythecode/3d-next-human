"""Validate a BVH pose file against the MakeHuman default rig (headless)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .pose_catalog import COMPARE_BONE


@dataclass
class PoseBvhValidation:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_pose_bvh_file(filepath: Path | str) -> PoseBvhValidation:
    """Mirror human-api / Pose Library BVH load checks."""
    path = Path(filepath).resolve()
    result = PoseBvhValidation(ok=True)

    if not path.is_file():
        result.ok = False
        result.errors.append(f"file not found: {path}")
        return result

    from .bootstrap import ensure_runtime

    ensure_runtime()

    try:
        import bvh
    except ImportError as err:
        result.ok = False
        result.errors.append(f"failed to import MakeHuman bvh module: {err}")
        return result

    try:
        bvh_file = bvh.load(str(path), convertFromZUp="auto")
    except Exception as err:
        result.ok = False
        result.errors.append(f"failed to parse BVH: {err}")
        return result

    if COMPARE_BONE not in bvh_file.joints:
        result.ok = False
        result.errors.append(
            f"missing joint {COMPARE_BONE!r} — not the default MakeHuman rig"
        )
        return result

    if bvh_file.frameCount > 1:
        result.warnings.append(
            f"frameCount={bvh_file.frameCount}; human-api uses frame 0 only"
        )

    try:
        from .session import _load_human

        person = _load_human()
        skel = person.getBaseSkeleton()
        anim = bvh_file.createAnimationTrack(skel, name=f"validate-{path.stem}")
        if anim is None:
            result.ok = False
            result.errors.append("createAnimationTrack returned None")
            return result

        skel_bones = {bone.name for bone in skel.getBones()}
        bvh_joints = set(bvh_file.joints.keys())
        missing = sorted(name for name in skel_bones if name not in bvh_joints)
        if missing:
            preview = ", ".join(missing[:8])
            suffix = "..." if len(missing) > 8 else ""
            result.warnings.append(
                f"{len(missing)} default-rig bone(s) missing from BVH: {preview}{suffix}"
            )
    except Exception as err:
        result.ok = False
        result.errors.append(f"failed to build animation track: {err}")

    return result

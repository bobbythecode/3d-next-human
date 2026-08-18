"""MakeHuman basemesh (dm, Y-up) → Wavefront OBJ metres Y-up triangles."""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np

DM_TO_M = 0.1


def fan_triangles(vert_ids: Sequence[int]) -> list[tuple[int, int, int]]:
    ids = [int(v) for v in vert_ids]
    if len(ids) == 4 and ids[0] == ids[3]:
        ids = ids[:3]
    if len(ids) < 3:
        return []
    return [(ids[0], ids[i], ids[i + 1]) for i in range(1, len(ids) - 1)]


def scale_dm_to_m(coords: np.ndarray) -> np.ndarray:
    return np.asarray(coords, dtype=np.float64) * DM_TO_M


def collect_body_triangles(
    fvert: np.ndarray,
    face_mask: np.ndarray,
) -> list[tuple[int, int, int]]:
    triangles: list[tuple[int, int, int]] = []
    mask = np.asarray(face_mask, dtype=bool)
    for index, verts in enumerate(fvert):
        if not mask[index]:
            continue
        triangles.extend(fan_triangles(verts))
    return triangles


def place_feet_on_ground(coords: np.ndarray, vertex_ids: Sequence[int]) -> np.ndarray:
    """Shift so the lowest used body vertex is Y=0 — same floor as GGG mean_all."""
    out = np.asarray(coords, dtype=np.float64).copy()
    ids = np.fromiter(vertex_ids, dtype=np.int64)
    if ids.size < 1:
        raise ValueError("OBJ must contain at least one triangle")
    out[:, 1] -= float(np.min(out[ids, 1]))
    return out


def compact_used(
    coords: np.ndarray,
    triangles: Iterable[tuple[int, int, int]],
) -> tuple[np.ndarray, list[tuple[int, int, int]]]:
    tri_list = list(triangles)
    used = sorted({index for tri in tri_list for index in tri})
    remap = {old: new for new, old in enumerate(used)}
    return (
        np.asarray(coords, dtype=np.float64)[used],
        [(remap[a], remap[b], remap[c]) for a, b, c in tri_list],
    )


def write_triangle_obj(
    coords_m: np.ndarray,
    triangles: Iterable[tuple[int, int, int]],
) -> str:
    lines = ["# human-api metres Y-up", "# www.makehumancommunity.org"]
    for x, y, z in coords_m:
        lines.append(f"v {x:.6f} {y:.6f} {z:.6f}")
    count = 0
    for a, b, c in triangles:
        if a == b or b == c or a == c:
            continue
        lines.append(f"f {a + 1} {b + 1} {c + 1}")
        count += 1
    if count < 1:
        raise ValueError("OBJ must contain at least one triangle")
    lines.append("")
    return "\n".join(lines)


def export_basemesh(coords_dm: np.ndarray, fvert: np.ndarray, face_mask: np.ndarray) -> str:
    triangles = collect_body_triangles(fvert, face_mask)
    used = [index for tri in triangles for index in tri]
    grounded = place_feet_on_ground(coords_dm, used)
    coords_m, compact_tris = compact_used(scale_dm_to_m(grounded), triangles)
    return write_triangle_obj(coords_m, compact_tris)

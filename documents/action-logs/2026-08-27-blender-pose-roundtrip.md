# 2026-08-27 — Blender pose round-trip (kick proof)

Pipeline: MH desktop → Blender (FBX/Collada) → BVH → fix → MH preview → promote → human-api / portal  
Guide: [`../guides/blender-pose-bvh.md`](../guides/blender-pose-bvh.md)

## Done (repo)

| Piece | Path |
|-------|------|
| Validate CLI | [`scripts/validate_pose_bvh.py`](../../scripts/validate_pose_bvh.py) · [`scripts/validate-pose-bvh.cmd`](../../scripts/validate-pose-bvh.cmd) |
| Blender root fix | [`scripts/fix_blender_pose_bvh.py`](../../scripts/fix_blender_pose_bvh.py) |
| Validation core | [`service/pose_bvh_validate.py`](../../service/pose_bvh_validate.py) |
| Tests | [`tests/test_validate_pose_bvh.py`](../../tests/test_validate_pose_bvh.py) |
| Pose pair | `rest-to-kick` in [`service/pose_pairs.py`](../../service/pose_pairs.py) |
| Catalog doc | [`PosePairCatalog.md`](../classes/PosePairCatalog.md) |

```powershell
conda run -n human python -m pytest tests/test_validate_pose_bvh.py tests/test_pose_pairs.py -q
conda run -n human python scripts/validate_pose_bvh.py makehuman/data/poses/kick.bvh
# หรือ
.\scripts\validate-pose-bvh.cmd makehuman\data\poses\kick.bvh
```

## First custom pose — `kick` (2026-08-27)

| Gate | Result |
|------|--------|
| `<id>` | `kick` |
| Blender export | FBX/Collada round-trip → BVH (Blender vanilla export; root axis bake) |
| `fix_blender_pose_bvh.py` | Applied before promote (root Rx=0 · zero axis/face bake) |
| validate | ✅ `ok: kick.bvh` |
| MH Pose Library preview | ✅ upright kick on default rig |
| promote | ✅ `makehuman/data/poses/kick.bvh` + `kick.meta` |
| `GET /internal/humans/poses` | ✅ includes `kick` (after human-api restart) |
| `rest-to-kick` | ✅ in `pose_pairs` |
| Portal | ✅ create mannequin → drape → kick pose on body (ผ้า drape บนท่า kick) |

**Notes**

- Blender BVH export จาก MH rig มัก bake ~90° บน root — ใช้ `fix_blender_pose_bvh.py` ก่อน MH preview (see guide §3).
- `kick.meta` ควรแก้ `name` / `description` / `copyright` ให้ตรงผู้ author (ตอนนี้ยัง clone จาก tpose template ได้).
- Assets (`*.bvh`, `*.meta`) gitignored — อยู่ local เหมือน `tpose.bvh`.

## Reuse checklist (ท่าถัดไป)

1. MH export default rig → Blender pose → export BVH
2. `fix_blender_pose_bvh.py` → `validate_pose_bvh.py`
3. MH user `data/poses/` preview
4. promote `makehuman/data/poses/<id>.bvh` + `.meta`
5. restart human-api
6. (optional) `pose_pairs.py` entry → portal smoke

## Status

**green** — automated gates + first Blender-authored full-BVH pose (`kick`) proven end-to-end through portal drape.

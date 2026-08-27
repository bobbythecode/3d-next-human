# 2026-08-27 — Blender pose round-trip tooling

Pipeline: MH desktop → Blender (FBX/Collada) → BVH → MH preview → promote → human-api / portal  
Guide: [`../guides/blender-pose-bvh.md`](../guides/blender-pose-bvh.md)

## Done (repo)

- [`scripts/validate_pose_bvh.py`](../../scripts/validate_pose_bvh.py) — CLI gate
- [`service/pose_bvh_validate.py`](../../service/pose_bvh_validate.py) — shared validation (mirrors `_load_bvh_animation`)
- [`tests/test_validate_pose_bvh.py`](../../tests/test_validate_pose_bvh.py) — tpose regression + wrong-rig fail

```bat
conda run -n human python -m pytest tests/test_validate_pose_bvh.py -q
```

Validate (PowerShell):

```powershell
conda run -n human python scripts/validate_pose_bvh.py makehuman/data/poses/tpose.bvh
```

Validate (cmd):

```bat
scripts\validate-pose-bvh.cmd makehuman\data\poses\tpose.bvh
```

## Manual gate — MH import preview (§5)

Use after validate pass, **before** promoting to `makehuman/data/poses/`.

1. Copy `<id>.bvh` (+ optional `<id>.meta`) into MH **user** poses folder (`getDataPath('poses')` — Settings → Files).
2. MakeHuman desktop → **Pose** tab → select the BVH.
3. Confirm pose on mannequin matches Blender intent (no flip, no collapsed limbs).
4. If wrong → re-export from Blender → validate again → repeat.

**Proof row (fill when first custom pose lands):**

| Field | Value |
|-------|-------|
| `<id>` | _pending_ |
| validate | _pending_ |
| MH preview OK | _pending_ |

## Manual gate — Promote template (§6–7)

After MH preview passes:

| Step | Action |
|------|--------|
| 1 | `validate_pose_bvh.py` on final BVH |
| 2 | Copy to `makehuman/data/poses/<id>.bvh` + `<id>.meta` |
| 3 | Restart human-api (`scripts/dev-up.cmd`) |
| 4 | `GET /internal/humans/poses` → `<id>` listed |
| 5 | (Optional) Add pair in `service/pose_pairs.py` — template in guide §7 |
| 6 | `GET /internal/humans/pose-pairs` → pair listed (if step 5) |

**`.meta` template:** see `makehuman/data/poses/tpose.meta` and guide §6.

## Manual gate — Portal smoke (§8)

Requires step 5 (pose-pair) for A→B play.

1. Portal editor → MakeHuman panel → select `rest-to-<id>` (or existing pair).
2. **Create mannequin** (`include_rig: true`).
3. Drape at endpoint A.
4. Play A→B — check limbs + cloth.
5. Change pair or height → create mannequin again → re-drape (do not reuse old body).

**Proof row:**

| Field | Value |
|-------|-------|
| pair id | _pending_ |
| drape + play OK | _pending_ |

## Status

Automated gate: **green** (validate script + pytest).  
First custom authored pose + portal proof: **pending** (manual Blender/MH session).

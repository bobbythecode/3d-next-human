# MH ↔ Blender ↔ BVH → pose catalog

> Home: **`3d-next-human`** · Author library poses for P9 without a custom GUI  
> Related: [`../classes/PosePairCatalog.md`](../classes/PosePairCatalog.md) · [`../plans/human-api.md`](../plans/human-api.md) · [`../action-logs/2026-08-27-blender-pose-roundtrip.md`](../action-logs/2026-08-27-blender-pose-roundtrip.md) · [`license.md`](./license.md)

## Idea

ปั้นท่าใหม่ได้เรื่อยๆ ด้วย loop **MakeHuman desktop → Blender → BVH → MakeHuman preview → human-api**:

```text
MH desktop export mesh+armature (FBX or Collada, default rig)
  → Blender pose bones
  → export BVH
  → (optional) scripts/validate_pose_bvh.py
  → MH desktop Pose Library — preview on the mannequin
  → promote to makehuman/data/poses/<id>.bvh
  → (optional) pose_pairs entry
  → restart human-api → portal play A→B
```

human-api โหลด library poses จาก `makehuman/data/poses/{id}.bvh`  
([`service/pose_catalog.py`](../../service/pose_catalog.py) · `_load_bvh_animation`)  
Logic เดียวกับ MH desktop Pose Library  
([`makehuman/plugins/3_libraries_pose.py`](../../makehuman/plugins/3_libraries_pose.py) · `loadBvh`).

[`pose_pairs.py`](../../service/pose_pairs.py) ชี้ `pose.id` ไปไฟล์นั้นได้ — ไม่ต้องแก้ `body-poseunits.json` สำหรับ full BVH endpoint.

**Blender path ในรอบนี้:** FBX/Collada manual import (ไม่ใช้ community MakeHuman Blender plugin).

## Hard rules

```text
✅ Use MakeHuman **desktop** for export and BVH preview (not human-api)
✅ Use MakeHuman **default** skeleton bone names
✅ BVH must contain joint upperleg02.L (COMPARE_BONE)
✅ Preview in MH Pose Library before promoting to data/poses/
✅ One mannequin / one height / one rig after you wire a pair
✅ Restart human-api after promoting BVH or editing pose_pairs

❌ Rename or reparent bones in Blender
❌ Drop Mixamo / other-rig BVH without retarget (not in this guide)
❌ Promote straight to data/poses/ without MH preview
❌ Change pose_pair_id and reuse an old draped body
❌ Put MakeHuman / this tool into Nest or portal
```

## Steps

### 1. Export from MakeHuman desktop (default rig)

1. Start MakeHuman desktop (`python makehuman.py`) — **not** human-api.
2. Select the **default** skeleton (same bone set as `mh-default` / `default.mhskel`).
3. Export **mesh + armature** using one of:
   - **FBX** — plugin `9_export_fbx`
   - **Collada (.dae)** — plugin `9_export_collada`
4. Note the export orientation you used (MH default is Y-up) — lock it for repeatability.
5. Confirm bone names in the exported file match MH (examples: `upperleg02.L`, `lowerleg01.L`, `upperarm01.L`).

### 2. Pose in Blender

1. Import the FBX or Collada file into Blender.
2. Pose **only** by rotating bones · do not rename or reparent the armature.
3. Aim for a single end pose (A→B uses one BVH frame as the library pose for that endpoint).

### 3. Export BVH from Blender

1. Export the armature as **BVH** (select the Armature; one frame is enough).
2. Prefer a short clip (Start = End = the posed frame).
3. Confirm the file contains `upperleg02.L`. Without it, MH / human-api rejects the file.

**Known Blender trap:** vanilla BVH export of an MH FBX/Collada rig almost always bakes **~85–90° on root X**. The viewport can look upright (`R=0`) while the BVH still tips the mannequin in Pose Library. Apply Rotation / Forward–Up toggles do **not** remove that channel.

After every Blender export, run:

```powershell
conda run -n human python scripts/fix_blender_pose_bvh.py path\to\from_blender.bvh -o makehuman/data/poses/<id>.bvh
```

Default: root **Rx=0** + zero **spine05 / pelvis.L / pelvis.R** + zero face helpers.  
Do **not** combine root Rx=180 with cleared axis bones — that flips the mannequin upside-down.  
Legacy fallback: `--root-rx 180 --keep-axis-bake` (upright but slight forward lean).

Then validate (§4) and preview in MH (§5).

Reference sample already in tree: `makehuman/data/poses/tpose.bvh`.

### 4. Validate (recommended)

Before loading in MH, run:

**PowerShell** (recommended — same env as pytest):

```powershell
conda run -n human python scripts/validate_pose_bvh.py makehuman/data/poses/tpose.bvh
```

**Cmd** (one line):

```bat
scripts\validate-pose-bvh.cmd makehuman\data\poses\tpose.bvh
```

Or manually after `call scripts\_human-python.cmd` in the **same** cmd window:

```bat
"%HUMAN_PYTHON%" scripts\validate_pose_bvh.py makehuman\data\poses\tpose.bvh
```

Do **not** paste `%HUMAN_PYTHON%` into PowerShell — that is cmd syntax only.

Implementation: [`scripts/validate_pose_bvh.py`](../../scripts/validate_pose_bvh.py) · [`service/pose_bvh_validate.py`](../../service/pose_bvh_validate.py)

Checks mirror `_load_bvh_animation`: parse · `upperleg02.L` · create animation track on default skeleton · warn on extra frames / missing bones.

### 5. Load back into MakeHuman — preview

Iterate here before promoting to the system library.

1. Copy `<id>.bvh` (and optional `<id>.meta`) into the **user poses** folder:
   - MH scans `getDataPath('poses')` first, then `getSysDataPath('poses')`
   - Path is under MakeHuman user data (see Settings → Files on your install)
2. In MakeHuman: **Pose** tab → select the BVH from the file chooser.
3. MH runs the same rig check and autoscale as human-api (`loadBvh` in `3_libraries_pose.py`).
4. **Preview** the pose on the mannequin. If wrong → go back to Blender, re-export, repeat §3–5.
5. When approved, write or finalize `<id>.meta` (see §6).

Do **not** skip this step — it catches bone rename, axis flip, and scale issues before they reach human-api.

### 6. Promote to `data/poses/` (human-api library)

After MH preview passes, copy into the repo tree:

| File | Role |
|------|------|
| `makehuman/data/poses/<id>.bvh` | Motion (required) |
| `makehuman/data/poses/<id>.meta` | Name / license (recommended) |

`<id>` is lowercase stem used as `pose.id` (example: `wave` → `wave.bvh`).

`.meta` shape (see `tpose.meta`):

```text
tag Rest poses
name Wave
description Short description of the pose.
license CC0
copyright (c) YEAR Your Name
```

Bundled MH poses are **CC0** ([`license.md`](./license.md)). New files you author: keep license metadata honest in `.meta` and in the catalog `license` block.

**Git note:** `*.bvh`, `*.meta`, and `/makehuman/data/*` are gitignored — promoted poses stay local like `tpose.bvh` unless you force-add with a gitignore exception.

### 7. Add a pose-pair (optional · per pose)

Edit [`service/pose_pairs.py`](../../service/pose_pairs.py) **only when** the pose should appear in portal A→B transitions. Template (replace `<id>` and display name):

```python
{
    "id": "rest-to-<id>",
    "name": "rest → <display name>",
    "version": "1",
    "a": {"pose": {"id": "rest"}},
    "b": {"pose": {"id": "<id>"}},
    "duration_s": 1.0,
    "fps": 30,
    "interpolation": "joint_local_slerp",
    "root_policy": "lock_feet",
    "license": {
        "assets": "CC0-1.0",
        "note": "author BVH in makehuman/data/poses/",
    },
},
```

`rest` is the synthetic rest id (`REST_POSE_ID`) · other ids must match a `*.bvh` stem under `data/poses/` (same rule as `tpose`).

Optional: `pose.units` overlays from `body-poseunits.json` on top of a library pose — not required for a full BVH endpoint.

### 8. Try in the product path

1. Restart human-api (rescans poses / reloads catalog — no hot reload).
2. `GET /internal/humans/poses` → library includes `<id>`.
3. Portal MakeHuman panel: select the pair → **create mannequin** (`include_rig`).
4. Drape / simulate on that body.
5. Play golden A→B.

```text
1 mannequin = 1 height = 1 rig (pair baked at generate)
Change pair or height → create mannequin again → re-drape
Do not reuse an old drape on a new body
```

## Quick reference

| Stage | Where | Purpose |
|-------|-------|---------|
| Export rig+mesh | MH desktop → FBX/Collada | Blender authoring |
| Pose | Blender | Rotate bones only |
| Export motion | Blender → BVH | Pose file |
| Validate | `scripts/validate_pose_bvh.py` | Gate before MH load |
| Preview | MH user `data/poses/` | Approve pose on mannequin |
| Promote | `makehuman/data/poses/` | human-api library scan |
| Product | `pose_pairs.py` + portal | A→B transition |

## Later

- Automated catalog wiring when a new BVH lands (no hand-edit of `pose_pairs.py`)

## Out of scope here

- MakeHuman community Blender plugin (live sync)
- Mixamo / foreign-rig import
- Web or desktop bone-authoring GUI in this repo’s product gate
- Editing Nest, portal, or tailor for authoring
- `mhapi.setPoseFromFile` (stub in `1_mhapi/_skeleton.py`)

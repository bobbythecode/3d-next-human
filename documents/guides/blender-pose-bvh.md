# Blender → BVH → pose catalog

> Home: **`3d-next-human`** · Author poses for P9 transitions without a custom GUI  
> Related: [`../classes/PosePairCatalog.md`](../classes/PosePairCatalog.md) · [`../plans/human-api.md`](../plans/human-api.md) · [`license.md`](./license.md)

## Idea

human-api already loads library poses from `makehuman/data/poses/{id}.bvh`  
([`service/pose_catalog.py`](../../service/pose_catalog.py) · `_load_bvh_animation`).  
[`pose_pairs.py`](../../service/pose_pairs.py) can point `pose.id` at that file.

```text
MH export (default rig) → Blender (pose bones) → poses/<id>.bvh
  → pose_pairs entry → generate include_rig → portal play A→B
```

No portal/Nest changes · no Mixamo retarget · no `body-poseunits.json` edit required for a full library pose.

## Hard rules

```text
✅ Use MakeHuman **default** skeleton bone names
✅ BVH must contain joint upperleg02.L (COMPARE_BONE)
✅ One mannequin / one height / one rig after you add a pair
✅ Restart human-api after adding BVH or catalog entries

❌ Rename bones in Blender
❌ Drop Mixamo / other-rig BVH without retarget (not in this guide)
❌ Change pose_pair_id and reuse an old draped body
❌ Put MakeHuman / this tool into Nest or portal
```

## Steps

### 1. Export from MakeHuman with default rig

1. Open MakeHuman (desktop) or export via its FBX/Collada plugin.
2. Enable the **default** skeleton (same bone set as `mh-default` / `default.mhskel`).
3. Export mesh + armature (FBX or Collada — whichever you already use with Blender).

Bone names must match MH (examples: `upperleg02.L`, `lowerleg01.L`, `upperarm01.L`).

### 2. Pose in Blender

1. Import the file into Blender.
2. Pose **only** by rotating bones · do not rename or reparent the armature.
3. Aim for a single end pose (A→B uses one BVH frame as the library pose for that endpoint).

### 3. Export BVH

1. Export armature as **BVH**.
2. Prefer a short clip (one frame is enough for a static endpoint pose).
3. Loader uses `convertFromZUp="auto"` — if the pose looks flipped after load, re-export with the opposite up-axis convention and try again.
4. Confirm the file contains `upperleg02.L`. Without it, human-api / MH pose load rejects the file.

Reference sample already in tree: `makehuman/data/poses/tpose.bvh`.

### 4. Install into `data/poses/`

Copy next to the existing library:

| File | Role |
|------|------|
| `makehuman/data/poses/<id>.bvh` | Motion (required) |
| `makehuman/data/poses/<id>.meta` | Name / license (recommended) |

`<id>` is lowercase stem used as `pose.id` (example: `kick` → `kick.bvh`).

`.meta` shape (see `tpose.meta`):

```text
tag Rest poses
name Kick
description Short description of the pose.
license CC0
copyright (c) YEAR Your Name
```

Bundled MH poses are **CC0** ([`license.md`](./license.md)). New files you author: keep license metadata honest in `.meta` and in the catalog `license` block.

### 5. Add a pose-pair

Edit [`service/pose_pairs.py`](../../service/pose_pairs.py). Example shape (do not invent bone units unless you need overlays):

```python
{
    "id": "rest-to-kick",
    "name": "rest → kick",
    "version": "1",
    "a": {"pose": {"id": "rest"}},
    "b": {"pose": {"id": "kick"}},
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

### 6. Try in the product path

1. Restart human-api (so it rescans poses / reloads catalog).
2. Portal MakeHuman panel: select the new pair → **create mannequin** (`include_rig`).
3. Drape / simulate on that body.
4. Play golden A→B.

```text
1 mannequin = 1 height = 1 rig (pair baked at generate)
Change pair or height → create mannequin again → re-drape
Do not reuse an old drape on a new body
```

## Later (not this doc round)

- `scripts/validate_pose_bvh.py` — check `upperleg02.L` / load track
- Automated catalog wiring when a new BVH lands

## Out of scope here

- Mixamo / foreign-rig import
- Web or desktop bone-authoring GUI in this repo’s product gate
- Editing Nest, portal, or tailor for authoring

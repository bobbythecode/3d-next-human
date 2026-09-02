# Class: `PosePairCatalog`

> Phase: P9 Phase 1 → Wave 1 (universal poses catalog)  
> Status: green

## Responsibility (หนึ่งอย่าง)

แคตตาล็อกคู่ท่า golden versioned สำหรับ transition A→B (ไม่ใช่ทุกคู่ใน library)

## Output

`GET /internal/humans/pose-pairs` → `{ version, rig, pairs[] }`

แต่ละคู่มี `name` · `root_policy: lock_feet` · endpoint อาจมี `pose.units` บน library pose

## Golden pairs (Wave 1)

Wave 1 มี **6** คู่ใน catalog — portal กรองตามท่าหุ่นปัจจุบัน (endpoint A):  
A-pose/`rest` → คู่ `rest→…` · T-pose → คู่ `tpose→…` (เช่น `tpose-to-rest`).

| id | A → B |
|----|-------|
| `tpose-to-rest` | tpose → rest |
| `rest-to-tpose` | rest → tpose |
| `rest-to-left-arm-up` | rest → rest + UpperArmForwardLeft + UpperArmRollOutLeft |
| `rest-to-torso-lean` | rest → rest + TorsoLeft (v2 · spine1–4→spine01–04 alias) |
| `rest-to-left-knee-bend` | rest → rest + UpperLegForwardLeft + FootTurnOutLeft (v2) · alias `upperleg.L`→`upperleg01.L` |
| `rest-to-kick` | rest → **kick** (Blender-authored BVH · [`../action-logs/2026-08-27-blender-pose-roundtrip.md`](../action-logs/2026-08-27-blender-pose-roundtrip.md)) |

`RigExport` ใช้ units ต่อ endpoint แยก A/B · overlay จาก request `pose_units` ทับทั้งคู่

Endpoint ยังชี้ `pose.id` ไป BVH ใน `makehuman/data/poses/` ได้โดยตรง (เช่น `tpose`)

**Authoring loop (ท่าใหม่ใดก็ได้):** MH desktop export → Blender pose → BVH → preview ใน MH Pose Library → promote → (optional) เพิ่มคู่ใน catalog  
คู่มือ: [`../guides/blender-pose-bvh.md`](../guides/blender-pose-bvh.md)

Dump catalog (repo root): `scripts\pose-pairs.cmd` · one pair: `scripts\pose-pairs.cmd rest-to-kick`

## Tests

- `tests/test_pose_pairs.py`
- `tests/test_rig_export.py`

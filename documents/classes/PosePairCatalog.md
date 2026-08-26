# Class: `PosePairCatalog`

> Phase: P9 Phase 1 → Wave 1 (universal poses catalog)  
> Status: green

## Responsibility (หนึ่งอย่าง)

แคตตาล็อกคู่ท่า golden versioned สำหรับ transition A→B (ไม่ใช่ทุกคู่ใน library)

## Output

`GET /internal/humans/pose-pairs` → `{ version, rig, pairs[] }`

แต่ละคู่มี `name` · `root_policy: lock_feet` · endpoint อาจมี `pose.units` บน library pose

## Golden pairs (Wave 1)

| id | A → B |
|----|-------|
| `tpose-to-rest` | tpose → rest |
| `rest-to-tpose` | rest → tpose |
| `rest-to-left-arm-up` | rest → rest + UpperArmForwardLeft + UpperArmRollOutLeft |
| `rest-to-torso-lean` | rest → rest + TorsoLeft |
| `rest-to-left-knee-bend` | rest → rest + UpperLegForwardLeft + FootTurnOutLeft (v2) · alias `upperleg.L`→`upperleg01.L` |

`RigExport` ใช้ units ต่อ endpoint แยก A/B · overlay จาก request `pose_units` ทับทั้งคู่

## Tests

- `tests/test_pose_pairs.py`
- `tests/test_rig_export.py`

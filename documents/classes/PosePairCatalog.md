# Class: `PosePairCatalog`

> Phase: P9 Phase 1  
> Status: green (คลื่นแรก)

## Responsibility (หนึ่งอย่าง)

แคตตาล็อกคู่ท่า golden versioned สำหรับ transition A→B (ไม่ใช่ทุกคู่ใน library)

## Output

`GET /internal/humans/pose-pairs` → `{ version, rig, pairs[] }`

Golden คลื่นแรก: `tpose-to-rest` · `rest-to-tpose`

## Tests

- `tests/test_pose_pairs.py`

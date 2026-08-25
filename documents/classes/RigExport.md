# Class: `RigExport`

> Phase: P9 Phase 1  
> Status: yellow (คลื่นแรก)

## Responsibility (หนึ่งอย่าง)

สร้าง payload `human-rig.v1` จาก MakeHuman basemesh หลัง morph: joints · inverse-bind · LBS weights · คู่ท่า A/B

## Input

| ชื่อ | แหล่ง |
|------|--------|
| person | MakeHuman `Human` หลัง modifiers |
| pose_pair_id | `PosePairCatalog` |
| pose_units | optional |

## Output

| ชื่อ | ที่อยู่ |
|------|---------|
| `rig` | ใน `POST /internal/humans/generate` เมื่อ `include_rig=true` |

## ไม่ทำ

- ไม่เขียน glTF ในคลื่นแรก
- ไม่ส่ง skeleton ไป tailor
- ไม่ hardcode μ / ฟิสิกส์ผ้า

## Tests

- `tests/test_rig_export.py`
- `tests/test_pose_pairs.py`

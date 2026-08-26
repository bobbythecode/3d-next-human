# 2026-08-26 — Fix rest-to-left-knee-bend pose units

## Eye

กระโปรง × `rest-to-left-knee-bend` — play แล้วขายังตรง

## Cause

1. MH `LowerLegBendLeft*` ชื่อหลอก — หมุนแค่ `upperleg.L` ไม่ใช่ shin  
2. กระดูก `upperleg.L` ไม่มีใน default skeleton (มีแค่ `upperleg01/02`) → unit ต้นขาเงียบ

## Fix

```text
✅ pair version 2 · B = UpperLegForwardLeft 0.7 + FootTurnOutLeft 0.55
✅ FootTurnOutLeft หมุน lowerleg01.L จริง
✅ alias upperleg.L → upperleg01.L ใน pose_catalog
❌ LowerLegBendLeft*
✅ numpy 2: transformations.quaternion_from_matrix copy=True
```

## Try

รีสตาร์ท human-api · เลือกคู่ท่า knee-bend · **สร้างหุ่นใหม่** · drape · play  
คาดหวัง: ขาซ้ายงอเข่าชัดที่ B

## Tests

```text
pytest tests/test_pose_pairs.py tests/test_rig_export.py -q
# integration: test_rest_to_left_knee_bend_moves_left_shin
```

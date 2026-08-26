# Action log — include_rig OBJ honors pose.id (2026-08-26)

## ปัญหา

สร้างหุ่นเลือก Pose `tpose` แล้วได้ท่า rest — เพราะ portal ส่ง `include_rig` + `pose_pair_id: rest-to-tpose` แล้ว human-api เขียน OBJ จากท่า A ของคู่เสมอ (= rest) ทิ้ง `pose.id`

## แก้

`service/session.py`: เมื่อ `pose.id` ตรง A หรือ B ของคู่ — ใช้ `posed_positions` ของท่านั้นเป็น OBJ

## เกต

`conda run -n human python -m pytest tests/test_rig_export.py -q` → 4 passed

## หมายเหตุ

ต้องรีสตาร์ท human-api บน :8001 ให้โหลดโค้ดใหม่

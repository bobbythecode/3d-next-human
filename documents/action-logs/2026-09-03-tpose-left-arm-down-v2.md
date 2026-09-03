# 2026-09-03 — fix `tpose-to-left-arm-down` (v2)

> Repo: `3d-next-human`  
> สถานะ: พร้อมเกตตา

## ปัญหา

v1 ใช้ `UpperArmDownLeft` ทับบน BVH `tpose` — unit นี้ออกแบบบน rest เลยแขนซ้าย**ยกขึ้น**แทนวางข้างลำตัว

## แก้

```text
✅ B = tpose + replace_bones จาก rest สำหรับ left arm/hand chain
✅ แขนขวายัง T · ซ้ายเป็น A-pose ข้างเดียว
✅ pair version → 2 (บังคับ rematch)
✅ apply_pose รองรับ replace_bones_from / replace_bones

❌ UpperArmDownLeft บน tpose
```

## เกตตา

1. หุ่น T-pose → ท่าทาง → `T-pose → left arm down`  
2. เล่นจบ: แขนซ้ายข้างลำตัว · แขนขวายังกาง

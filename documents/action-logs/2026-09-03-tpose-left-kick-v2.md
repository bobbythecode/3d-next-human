# 2026-09-03 — fix `tpose-to-left-kick` (v2)

> Repo: `3d-next-human`  
> สถานะ: พร้อมเกตตา

## ปัญหา

v1 ชี้ B ไป BVH `kick` ตรงๆ — ท่า kick ปั้นจาก rest เลยแขนจบที่ **A-pose** ดูเหมือน rest→kick

## แก้

```text
✅ B = kick + replace_bones แขน L/R จาก tpose
✅ ขาเตะ · แขนยังกาง T
✅ pair version → 2
```

## เกตตา

หุ่น T-pose → `T-pose → left kick` · จบแล้วยังแขนกาง · ขาซ้ายเตะ

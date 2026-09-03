# 2026-09-03 — `tpose-to-torso-lean`

> Repo: `3d-next-human` (+ portal torso-lean tuning)  
> สถานะ: พร้อมเกตตา

## สรุป

เพิ่มคู่ **T-pose → torso lean** — เหมือน `rest-to-torso-lean` แต่ฐาน `tpose` + `TorsoLeft: 0.9`

## สัญญา

```text
✅ id `tpose-to-torso-lean` · A=tpose · B=tpose+TorsoLeft
✅ portal fold tuning เดียวกับ rest-to-torso-lean (SDF push-out)
✅ โชว์เมื่อหุ่น bake เป็น T-pose
```

## เกตตา

หุ่น T-pose → ท่าทาง → `T-pose → torso lean` · ลำตัวเอียง · แขนยังกาง

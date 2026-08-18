# 3d-next — human-api (µService)

> Status: **green** · G-P5.7 ยืนยันตา 2026-08-18 · **G-P5.7b ผ่าน** (Macro catalog + portal) · แผนเต็ม: [`../../../3d-next-portal/documents/plans/p5_7-human-api.md`](../../../3d-next-portal/documents/plans/p5_7-human-api.md)  
> เกต: G-P5.7 ใน [`../../../3d-next-portal/documents/specifications/roadmap/plan.md`](../../../3d-next-portal/documents/specifications/roadmap/plan.md)

Repo นี้คือ MakeHuman (**AGPL-3.0** ซอร์ส · **CC0** assets · ผล export เป็นข้อมูลผู้ใช้ — ดู `LICENSE.md`)

เป้าหมาย 3d-next: รันเป็น **HTTP service แทน desktop** เพื่อให้ `3d-next-service` เรียกได้โดย**ไม่นำซอร์สนี้เข้า Nest**

```text
✅ Facade HTTP อยู่ใน repo นี้ (จึงเป็น AGPL ด้วย)
✅ GET /health · POST /internal/humans/generate → OBJ เมตร Y-up · เท้าที่ Y=0 (เทียบ mean_all)
✅ Dev: `scripts/dev-up.cmd` (Windows) หรือ `scripts/dev-up.sh` — ห้ามบังคับ docker build
✅ Docker ภายหลัง/opt-in ใน 3d-next-container คนละ image จาก tailor/Nest

❌ อย่าให้ 3d-next-service import แพ็กเกจนี้
❌ อย่าคัดลอก makehuman/*.py ไป repo พี่น้อง
❌ อย่าใช้หน้าต่าง Qt เป็นทางเกต
```

Nest คุยผ่าน `HUMAN_API_URL` และ `3d-next-service/scripts/human/*.sh` (curl) เท่านั้น

ทางเดินเกตตา (Windows):

```bat
scripts\dev-up.cmd
cd ..\3d-next-service
scripts\human\generate.cmd --out %TEMP%\human.obj
```

แล้วใน editor: หุ่นชนผ้า → อัปโหลด OBJ · ผ้าชนเมื่อกดจำลอง

UI สไลเดอร์ Macro ใน portal = **P5.7b ผ่าน** 2026-08-18 — แผน: [`../../../3d-next-portal/documents/plans/p5_7b-human-modifiers-portal.md`](../../../3d-next-portal/documents/plans/p5_7b-human-modifiers-portal.md) · Head–Feet = P5.7c

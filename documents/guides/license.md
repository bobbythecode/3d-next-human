# License — 3d-next-human / human-api

> อัปเดต: 2026-08-23 · ข้อความเต็ม: [`../../LICENSE.md`](../../LICENSE.md)

## สรุปสั้น

| ส่วน | สัญญา | ไฟล์ |
|------|--------|------|
| ซอร์ส MakeHuman + `service/` (human-api) | **AGPL-3.0** (หรือใหม่กว่า) | `LICENSE.CODE.md` · หมวด B + **E** |
| สินทรัพย์ฐาน (basemesh / targets / …) | **CC0 1.0** | `LICENSE.ASSETS.md` · หมวด C |
| ผล export (OBJ ฯลฯ) จาก generate | **ข้อมูลผู้ใช้** | หมวด D |

## ทำไมแยกจาก Nest / portal / tailor

AGPL ติดเมื่อคัดลอกหรือ import ซอร์สนี้ · **ไม่ติด** แค่เพราะเรียก HTTP

```text
✅ human-api คนละโปรเซส / คนละ image
✅ Nest เรียก HUMAN_API_URL · portal ผ่าน Nest เท่านั้น
✅ GET /license ชี้ repo นี้ (AGPL §13 ถ้าเปิดเน็ต)

❌ pip-install / COPY makehuman เข้า Nest หรือ tailor-api
❌ รวม human + Nest ใน process เดียวแล้วเรียกว่า isolate
```

รายละเอียดวิศวกรรม: [`../plans/human-api.md`](../plans/human-api.md) · rule: `.cursor/rules/agpl-isolation.mdc`

## Endpoint

`GET /license` → JSON ชี้ AGPL · URL ซอร์ส · หมายเหตุว่า OBJ เป็นข้อมูลผู้ใช้ (หมวด D)

ตัวอย่าง payload: ดู `service/http_api.py` · คลาส [`../classes/HumanHttpApi.md`](../classes/HumanHttpApi.md)

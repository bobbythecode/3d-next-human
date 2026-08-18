# Class: `HumanModifierCatalog`

> Phase: P5.7b  
> Status: green

## Responsibility (หนึ่งอย่าง)

อ่าน JSON สไลเดอร์ของ MakeHuman แล้วจัดหมวดตามสัญญา portal — ไม่เปิด Qt

## Input

| ชื่อ | ชนิด | แหล่ง |
|------|------|-------|
| `*_sliders.json` | ไฟล์ | `makehuman/data/modifiers` |

## Output

| ชื่อ | ชนิด | ผู้ใช้ต่อ |
|------|------|-----------|
| catalog_payload | `{ categories }` | `GET /internal/humans/modifiers` |
| allowed_modifier_ids | set ของ fullName | `HumanModifierRequest` |

## ไม่ทำ

- Pose / Skin · UI · แมป YAML `body:`

## Tests

- `tests/test_catalog.py`

## Anti-patterns

- ฮาร์ดโค้ดรายชื่อสไลเดอร์ใน Next

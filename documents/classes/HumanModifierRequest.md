# Class: `HumanModifierRequest`

> Phase: P5.7  
> Status: green

## Responsibility (หนึ่งอย่าง)

parse JSON macros ของ MakeHuman เป็นค่าที่ใช้กับ modifier — 0..1 ตามสไลเดอร์ ยกเว้น `height_cm`

## Input

| ชื่อ | ชนิด | แหล่ง |
|------|------|-------|
| body | object | `POST /internal/humans/generate` |

## Output

| ชื่อ | ชนิด | ผู้ใช้ต่อ |
|------|------|-----------|
| gender, age, weight, muscle | float 0..1 | `HumanSession` |
| height | float 0..1 หรือไม่มี | `macrodetails-height/Height` |
| height_cm | float > 0 หรือไม่มี | binary search บน modifier แล้ววัด `getHeightCm` |
| as_dict | object | ใส่ใน JSON `applied` ให้ผู้เรียกเห็นค่าที่ใช้ |

ห้ามเงียบทิ้งฟิลด์ที่ส่งมา (unknown = 400)

## ไม่ทำ (out of scope)

- แมป YAML `body:` ของ garment-tailor
- ผม / เสื้อผ้า / ethnic sliders รอบแรก
- เดาสเกลจาก bbox ฝั่ง Nest

## Dependencies (inject / mock ได้)

- ไม่มี MakeHuman — parse อย่างเดียว

## Tests

- `tests/test_modifier_request.py`

## Anti-patterns

- รับ `height` กับ `height_cm` พร้อมกัน
- hardcode เลขส่วนสูงในเซลล์เรียก

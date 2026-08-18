# Class: `HumanMeshExport`

> Phase: P5.7  
> Status: green

## Responsibility (หนึ่งอย่าง)

แปลงเมช basemesh ของ MakeHuman เป็น Wavefront OBJ **เมตร Y-up** สามเหลี่ยม ตัด helper

## Input

| ชื่อ | ชนิด | แหล่ง |
|------|------|-------|
| coords | (N,3) dm Y-up | `Human.meshData.coord` |
| faces | (F,3\|4) | `meshData.fvert` |
| face_mask | (F,) bool | `meshData.face_mask` (helper ถูก mask แล้ว) |

## Output

| ชื่อ | ชนิด | ผู้ใช้ต่อ |
|------|------|-----------|
| obj | str | JSON `obj` / `generate.sh` / upload P5.5 |
| unit | `"m"` | ผู้เรียก |
| up | `"y"` | ผู้เรียก |

สเกล: **หาร 10** (เดซิเมตร → เมตร) · fan-triangulate quad  
พื้น: MH seed ต้นที่เชิงกราน — เลื่อนให้ Y ต่ำสุดของหน้าที่ export = 0 (เทียบ `mean_all` / ช่อง Feet on ground ของ MH) · ไม่เขียน vertex helper ที่ไม่มีหน้า

## ไม่ทำ

- texture / MTL / เสื้อผ้า proxy
- เดาสเกลจาก bbox
- เปิด Qt / OpenGL buffer

## Tests

- `tests/test_mesh_export.py`

## Anti-patterns

- ส่ง helper- / joint- ออกไปชนผ้า
- หน่วยเดซิเมตรปนเมตร
- ปล่อยต้นพิกัดเชิงกรานแล้วเรียกว่าตรง `mean_all`

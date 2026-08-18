# Class: `HumanHttpApi`

> Phase: P5.7  
> Status: green

## Responsibility (หนึ่งอย่าง)

HTTP facade ของกระบวนการ AGPL — health / license / generate โดยไม่เปิดหน้าต่าง desktop

## Input

| ชื่อ | ชนิด | แหล่ง |
|------|------|-------|
| GET /health | — | Nest / `health.sh` |
| GET /license | — | AGPL §13 ถ้าเปิดเน็ต |
| POST /internal/humans/generate | `HumanModifierRequest` | Nest / `generate.sh` |

## Output

| ชื่อ | ชนิด | ผู้ใช้ต่อ |
|------|------|-----------|
| health | `{ ok, service: "human-api" }` | เกต |
| generate | `{ height_cm, applied, unit: "m", up: "y", obj }` · `applied` = macros ที่ใช้ | upload P5.5 |

พอร์ต dev: `127.0.0.1:8001`

## ไม่ทำ

- import เข้า Nest
- spawn MakeHuman desktop
- path เครื่องใน DTO

## Tests

- `tests/test_http_health.py`

## Anti-patterns

- คืนซอร์ส Python ของ MH ใน JSON เมช
- บังคับ docker build เพื่อเกต

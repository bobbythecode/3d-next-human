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
| GET /internal/humans/modifiers | — | Nest / portal |
| POST /internal/humans/generate | `HumanModifierRequest` | Nest / `generate.sh` |

## Output

| ชื่อ | ชนิด | ผู้ใช้ต่อ |
|------|------|-----------|
| health | `{ ok, service: "human-api" }` | เกต |
| license | `{ license, code, assets, output, files, note }` | AGPL §13 · ดู [`../guides/license.md`](../guides/license.md) |
| modifiers | `{ categories }` ตามหมวดเป้า | แผง Macro P5.7b |
| poses | แคตตาล็อกท่า | P5.7d |
| generate | `{ height_cm, applied, unit, up, obj }` | upload P5.5 |

`GET /license` ชี้ **AGPL-3.0** · URL ซอร์ส repo นี้ · assets = CC0 · output OBJ = ข้อมูลผู้ใช้ (LICENSE.md หมวด D)

พอร์ต dev: `127.0.0.1:8001`

## ไม่ทำ

- import เข้า Nest
- spawn MakeHuman desktop
- path เครื่องใน DTO

## Tests

- `tests/test_http_health.py` (health + license)

## Anti-patterns

- คืนซอร์ส Python ของ MH ใน JSON เมช
- บังคับ docker build เพื่อเกต

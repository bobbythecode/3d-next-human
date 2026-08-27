# 2026-08-27 — human-api generate hang → portal 500

## Symptom

Portal「ท่าทาง」rest→tpose จับคู่นาน ~30s แล้ว toast:
`สร้างหุ่น MakeHuman ไม่สำเร็จ: service returned 500: Internal Server Error`

Nest: `POST /design/humans/generate` enter โดยไม่มี exit · portal proxy `socket hang up`  
human-api: `/health` ยัง 200 แต่ `POST /internal/humans/generate` ค้างไม่จบ

## Cause

`ThreadingHTTPServer` รับ POST พร้อมกันได้ แต่ `session.generate` ใช้ `_HUMAN` / cache globals โดยไม่มี lock — concurrent rematch (หรือ generate ค้างทับซ้อน) ทำให้ MakeHuman ค้าง

## Fix

- `service/session.py`: `_GENERATE_LOCK` ครอบ `generate` (serialize ต่อ process)
- รีสตาร์ท human-api เพื่อเคลียร์ thread ที่ค้างอยู่แล้ว

## Verify

1. `GET /health` → 200
2. `POST /internal/humans/generate` `{include_rig:true, pose_pair_id:"rest-to-tpose"}` จบในไม่กี่วินาที
3. Portal FAB → ท่าทาง → rest→tpose จับคู่ไม่ค้าง ~30s

## Status

**green** (code + restart) · รอตา portal

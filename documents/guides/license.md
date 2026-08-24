# License — human-api

> Updated: 2026-08-23 · Full text: [`../../LICENSE.md`](../../LICENSE.md) sections A–E

## Short summary

| Part | License | Files |
|------|---------|-------|
| MakeHuman source + `service/` (human-api) | **AGPL-3.0** (or later) | `LICENSE.CODE.md` · sections B + **E** |
| Bundled assets (basemesh / targets / …) | **CC0 1.0** | `LICENSE.ASSETS.md` · section C |
| Generate/export output (OBJ, etc.) | **user data** | section D |

## Isolation

AGPL attaches when this source is copied or imported. It does **not** attach merely from an HTTP call.

```text
✅ human-api runs as its own process / image
✅ Callers use HTTP only
✅ GET /license points at this repo (AGPL §13 when offered over a network)

❌ pip-install / COPY makehuman into another product
❌ Combine human-api with another app in one process and call that isolation
```

Engineering detail: [`../plans/human-api.md`](../plans/human-api.md) · rule: `.cursor/rules/agpl-isolation.mdc`

## Endpoint

`GET /license` → JSON pointing at AGPL · source URL · assets = CC0 · output = user-data · LICENSE files

Example payload: see `service/http_api.py` · class [`../classes/HumanHttpApi.md`](../classes/HumanHttpApi.md)

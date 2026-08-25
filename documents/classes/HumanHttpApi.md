# Class: `HumanHttpApi`

> Status: green

## Responsibility (one thing)

HTTP facade of the AGPL process — health / license / generate without opening a desktop window

## Input

| Name | Type | Source |
|------|------|--------|
| GET /health | — | HTTP clients / smoke scripts |
| GET /license | — | AGPL §13 when offered over a network |
| GET /internal/humans/modifiers | — | HTTP clients |
| GET /internal/humans/poses | — | pose pickers |
| GET /internal/humans/pose-pairs | — | P9 transition catalog |
| POST /internal/humans/generate | `HumanModifierRequest` (+ optional `include_rig`) | HTTP clients |

## Output

| Name | Type | Consumer |
|------|------|----------|
| health | `{ ok, service: "human-api" }` | operators / smoke checks |
| license | `{ license, code, assets, output, files, note }` | AGPL §13 · see [`../guides/license.md`](../guides/license.md) |
| modifiers | `{ categories }` by target group | Macro / body slider UIs |
| poses | pose catalog | pose pickers |
| pose-pairs | `{ version, rig, pairs }` | portal / Nest · [`PosePairCatalog`](./PosePairCatalog.md) |
| generate | `{ height_cm, applied, unit, up, obj [, rig] }` | mesh consumers · [`RigExport`](./RigExport.md) |

`GET /license` points at **AGPL-3.0** · source URL of this repo · assets = CC0 · output OBJ = user data (LICENSE.md section D)

Dev port: `127.0.0.1:8001`

## Out of scope

- embedding this package inside another app
- spawn MakeHuman desktop
- machine-local paths in the DTO

## Tests

- `tests/test_http_health.py` (health + license)

## Anti-patterns

- return MH Python source inside mesh JSON
- require a docker build for the gate

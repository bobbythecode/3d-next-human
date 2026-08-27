# human-api

> Status: **green** · Macro · Head–Feet · Pose supported  
> License: [`../guides/license.md`](../guides/license.md) · [`../../LICENSE.md`](../../LICENSE.md) sections A–E

This repo is MakeHuman plus a headless HTTP facade (`service/`, **human-api**):

- Source (including `service/`) → **AGPL-3.0**
- Bundled assets → **CC0**
- Export output → **user data** (LICENSE section D)
- Network offer → `GET /license` (LICENSE section E / AGPL §13)

Goal: run as an **HTTP service instead of the desktop app**. Callers talk to this process over HTTP and must not import or vendor this tree.

```text
✅ HTTP facade lives in this repo (so it is AGPL too)
✅ GET /health · GET /license · POST /internal/humans/generate
   → OBJ metres Y-up · feet at Y=0 (MH “Feet on ground”)
✅ GET /internal/humans/pose-pairs · generate `include_rig` → `human-rig.v1` (P9 Phase 1)
✅ Dev: `scripts/dev-up.cmd` (Windows) or `scripts/dev-up.sh` — Docker is optional
✅ Optional container image stays separate from other products
✅ Author custom library poses: MH desktop → Blender → BVH → MH preview → `data/poses/` (guide below)

❌ Do not import this package into another app
❌ Do not copy makehuman/*.py into another repo
❌ Do not use a Qt window as the gate
```

Custom poses (MH ↔ Blender ↔ BVH → catalog): [`../guides/blender-pose-bvh.md`](../guides/blender-pose-bvh.md)

Local smoke (Windows):

```bat
scripts\dev-up.cmd
```

Then `POST /internal/humans/generate` at `http://127.0.0.1:8001` (or curl against that URL).

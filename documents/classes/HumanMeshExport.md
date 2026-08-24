# Class: `HumanMeshExport`

> Status: green

## Responsibility (one thing)

Convert the MakeHuman basemesh to Wavefront OBJ **metres Y-up**, triangulated, helpers stripped

## Input

| Name | Type | Source |
|------|------|--------|
| coords | (N,3) dm Y-up | `Human.meshData.coord` |
| faces | (F,3\|4) | `meshData.fvert` |
| face_mask | (F,) bool | `meshData.face_mask` (helpers already masked) |

## Output

| Name | Type | Consumer |
|------|------|----------|
| obj | str | JSON `obj` / HTTP callers |
| unit | `"m"` | caller |
| up | `"y"` | caller |

Scale: **divide by 10** (decimetres → metres) · fan-triangulate quads  
Ground: MH seed origin is at the pelvis — shift so the lowest Y of exported faces = 0 (MH “Feet on ground”) · do not write helper vertices that have no faces

## Out of scope

- texture / MTL / clothing proxies
- guess scale from bbox
- open Qt / OpenGL buffers

## Tests

- `tests/test_mesh_export.py`

## Anti-patterns

- send helper- / joint- vertices in the export
- mix decimetre and metre units
- leave the origin at the pelvis and call that feet-on-ground

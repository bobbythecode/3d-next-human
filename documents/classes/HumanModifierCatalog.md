# Class: `HumanModifierCatalog`

> Status: green

## Responsibility (one thing)

Read MakeHuman slider JSON and group it for HTTP clients — do not open Qt

## Input

| Name | Type | Source |
|------|------|--------|
| `*_sliders.json` | file | `makehuman/data/modifiers` |

## Output

| Name | Type | Consumer |
|------|------|----------|
| catalog_payload | `{ categories }` | `GET /internal/humans/modifiers` |
| allowed_modifier_ids | set of fullName | `HumanModifierRequest` |

## Out of scope

- Pose / Skin · UI · mapping external body YAML

## Tests

- `tests/test_catalog.py`

## Anti-patterns

- hardcode slider names in a client app

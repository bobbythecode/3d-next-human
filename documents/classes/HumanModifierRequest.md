# Class: `HumanModifierRequest`

> Status: green

## Responsibility (one thing)

Parse JSON macros and MakeHuman `modifiers` fullName — 0..1 for Macro sliders except `height_cm` · other sliders -1..1

## Input

| Name | Type | Source |
|------|------|--------|
| body | object | `POST /internal/humans/generate` |

## Output

| Name | Type | Consumer |
|------|------|----------|
| gender, age, weight, muscle | float 0..1 | `HumanSession` |
| height | float 0..1 or absent | `macrodetails-height/Height` |
| height_cm | float > 0 or absent | binary search on the modifier then measure `getHeightCm` |
| as_dict | object | placed in JSON `applied` so the caller sees the values used |

Do not silently drop fields that were sent (unknown = 400)

## Out of scope

- map external YAML body schemas
- hair / clothes / Pose / Skin
- guess scale from bbox on the caller side

## Dependencies (inject / mock)

- no MakeHuman — parse only

## Tests

- `tests/test_modifier_request.py`

## Anti-patterns

- accept `height` and `height_cm` at the same time
- hardcode a height number in the calling cell

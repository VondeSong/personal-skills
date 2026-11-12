# Token contract

[TOKENS.json](../TOKENS.json) is a versioned custom web/mockup format. It is neither an official Apple palette nor a DTCG token schema.
Native implementations use semantic system roles and component metrics first. Existing project tokens take precedence unless changing them is part of the task.

## Typography and units

Select webTypography.desktop for compact productivity UI, mobile for touch-oriented layouts, or editorial as a starting point for marketing/readable prose.
Select by text role within the screen: compact controls can coexist with a more spacious document or conversation body. Do not apply one profile mechanically to the entire app or inherit a marketing headline merely to improve body readability; see the [visual composition example](desktop-mobile-visual-style-initial-plan.md#84-一个完成的视觉组合示例).
Sizes and line heights are CSS px reference values; convert to scalable CSS appropriately. The editorial title must adapt to narrow viewports.
Native points and physical screenshot pixels are distinct. Native text maps to system text styles, not these profiles.
nativeControlGuidance records point-based platform guidance; webControlGuidance contains separate custom web defaults. Neither visible icon size nor visual control size alone proves the effective hit region.

## Color usage

Resolve a normal theme from light or dark. For increased contrast, merge the corresponding highContrastOverrides into that theme.
Use the existing runtime's preference mechanism or a usable appearance setting; defining overrides in JSON does not implement preference detection.

| Role | Intended pairing |
| --- | --- |
| textPrimary / textSecondary / textTertiary | bgCanvas, bgContent, or bgSecondary |
| accent | Link/action text on neutral surfaces; it can also fill an emphasized button |
| onAccent | Text/icon on an accent-filled control |
| selectionText | selectionBg |
| success / warning / destructive | Status text/icon on a neutral surface or the matching status Bg |
| controlBorder | Essential custom control boundary against neutral surfaces |
| focusRing | Neutral surfaces or selectionBg; use separation/offset so it does not disappear into an accent-filled control |
| separator | Decorative grouping only; not the sole identifier of a control |
| webPreviewMaterial | Approximate translucency requiring runtime verification; opaqueFallbackRole resolves in the current theme |

Use status background plus its named status foreground, not a pale fill as small text.
If a role is used on a different background, add and validate that pair or use a known compatible pair.
Selection and focus can coincide. Render independent indicators, and ensure ring separation remains visible.
Do not apply opacity to important text and assume the opaque color's contrast result remains valid.
Hover, pressed, disabled, and other variants must be chosen for the actual component; validate any changed text/background pairs before claiming coverage.

## Static validation

Run with Python 3 and no external packages:

```text
python scripts/validate_tokens.py
python scripts/validate_tokens.py path/to/TOKENS.json --json
```

The validator parses the format, checks palette consistency, rejects missing foreground coverage, and evaluates declared pairs in light, dark, and both increased-contrast modes.
Thresholds are 4.5:1 for declared text roles and 3:1 for essential indicator roles, compared without rounding. All text tokens target ordinary text even if some usages are large.
It exits nonzero for malformed or failing contracts.
This does not verify composited glass, arbitrary adjacent colors, font rendering, control behavior, or screen-reader support. Exercise those using [Acceptance](acceptance.md).

## v2 migration

- light / dark base role names remain; read adjusted values rather than assuming v2 colors.
- type → webTypography.desktop, mobile, or editorial. There is no automatic native conversion.
- controlSize → nativeControlGuidance or webControlGuidance according to the implementation.
- light/dark.glassRegular and glassClear → webPreviewMaterial.regular/clear, explicitly requiring background checks and opaque fallback.
- Add onAccent, selectionText/selectionBg, and paired status Bg roles when implementing those states.
- Merge highContrastOverrides only when the application actually selects that appearance.
- The old $schema pointed at JSON Schema's own meta schema; it did not validate the token data. Version 3 uses format/version and the accompanying validator instead.

Consumers must migrate renamed paths before replacing their runtime token imports. Updating this skill does not automatically migrate project code.

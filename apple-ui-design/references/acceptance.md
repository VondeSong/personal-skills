# Observable acceptance checks

Apply checks to changed behavior and the selected deliverable. A static design can specify expectations; only an exercised implementation can establish runtime results.
Record checked, failed, or unverified when useful. Do not mark an entire accessibility audit passed after checking color tokens.

## Appearance and layout

| Change | Exercise | Pass condition |
| --- | --- | --- |
| Custom text or status color | Actual foreground/background pairs in each used theme and state | Ordinary web text ≥4.5:1; large text ≥3:1 under WCAG's size definition. Essential state also has a non-color cue. |
| Essential custom control or state indicator | Its adjacent background, including hover/selection | Target ≥3:1 for visual information needed to identify the control/state; decorative separators need not be promoted to structural indicators. |
| Translucent control | Bright, dark, and busy content; scrolling; opaque fallback | Required labels and boundaries remain readable. Static palette tests alone do not establish this. |
| Adaptive layout | Normal and smallest supported window; long realistic content | No lost required actions, clipped editing content, or overlapping targets. Necessary two-dimensional content can use deliberate scrolling. |
| Text scaling | iOS/iPadOS accessibility sizes; macOS app zoom/text settings; web zoom as relevant | Labels/actions remain understandable and operable without shrinking the user's chosen text. |
| Localization | Relevant long labels, CJK, and RTL when supported | Coherent reading order, logical alignment, and usable wrapping; no universal left/right placement assumption. |
| Chinese/mixed-script typography | Actual Chinese/Latin/numeric copy at narrow, normal, and intermediate widths; text zoom; web font loading/failure where relevant | Coherent visual size and baseline; intentional mixed-script spacing without duplicate processing; no clipping or overflow from protected phrases or punctuation corrections. Important editorial text avoids distracting isolated tail characters where feasible without compromising reflow. |

WCAG thresholds here are criteria for custom web/mockup colors, and useful explicit checks for custom UI. Native system components also require platform testing; these numbers alone do not certify an app.
For web, large text means at least 24 CSS px regular or 18⅔ CSS px bold. Native Apple pt and CSS pt are not interchangeable.
Disabled or decorative content has different criteria; do not label important metadata as disabled to avoid a contrast failure.

## Input focus and operation

- Move through the changed region with the supported keyboard navigation model. Focus is visible and not hidden behind overlays. Composite widgets use their appropriate arrow-key behavior.
- Activate controls and distinguish links, toggles, selection, and momentary actions. Preserve established platform shortcuts.
- Open a modal: focus enters appropriately, stays within it while modal, and returns to the trigger or a logical surviving target on dismissal. Nonmodal panels must remain escapable without trapping focus.
- Operate touch actions without hover. Confirm visible dimensions and effective hit regions separately, including spacing and overlap.
- When resizing or changing selection, retain a logical selection and editing context. Do not infer input focus from highlight color.

## Assistive technology and status

Inspect accessibility name, role, value, state, and reading order with the platform inspector and screen reader when available.
Confirm icon-only buttons are named, errors are associated with affected inputs, and custom elements expose useful actions.
Exercise progress, success, and failure announcements without forcing focus away or flooding speech with every update.
A completed background operation must not steal focus. Keep a discoverable outcome and relevant recovery/undo action.

## Appearance preferences

For affected custom effects, check light/dark, increased contrast or forced colors as appropriate, reduced motion, and reduced transparency/opaque fallback.
Native standard components provide much of this behavior; still inspect custom content placed inside them.
Reduced motion must retain state information. Reduced transparency must retain layer separation and readable content.

## Evidence appropriate to output

- Screenshot critique: describe visible evidence; label input and hidden-state issues as hypotheses.
- Design handoff: specify expected states and verification steps without claiming they ran.
- Implementation: render or run the affected surface with available tools, exercise meaningful changed behavior, and report remaining environment limitations.
- Token maintenance: run the color-contract validator; runtime interaction, font rendering, opacity, images, and native behavior remain outside that script.

Sources: [Apple and W3C](sources.md).

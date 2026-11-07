# Apple-inspired web and cross-platform UI

## Keep the actual platform

An explicitly Apple-inspired web interface can adopt content hierarchy, restrained surfaces, semantic color roles, and familiar interaction patterns while retaining web semantics.
For Windows or cross-platform desktop apps, preserve the host's real window controls, keyboard conventions, file dialogs, and accessibility behavior. Decorative macOS traffic lights should not masquerade as working controls.
A static macOS product mockup can depict window chrome when requested. Distinguish that from implementation.

For a marketing page, use editorial typography, product imagery, and a coherent narrative. Native sidebars, toolbar recipes, 13 pt desktop body styles, and AI review queues do not automatically apply.
Use the existing brand and design system when provided; the skill's palette is an optional starting point.

## Implementation

Use the existing component library and semantic HTML first: real buttons, links for navigation, headings, form labels, and suitable list/table elements.
Prefer established accessible primitives for dialogs, menus, tabs, and composite widgets; adding ARIA alone does not implement their keyboard behavior.
Use CSS logical properties for layouts that must support RTL. Keep document order and visual order coherent.

Read [Tokens](tokens.md) when creating custom styles. Sizes in the web profile are CSS pixels, not native Apple points or physical screenshot pixels.
Use scalable text/rem units where appropriate. Distinguish a compact productivity profile from mobile or editorial text sizing.
Use system font stacks; do not bundle proprietary Apple font files or export SF Symbols as unrestricted cross-platform assets. Supply symbol names/specs or icons from the project's licensed set.
For Chinese or mixed Chinese/Latin text changes, read [Chinese typography](chinese-typography.md) for font pairing, semantic wrapping, punctuation, and spacing. Keep editorial corrections local to the composition that needs them.

CSS opacity and backdrop-filter are approximations of translucency, not implementations of native Liquid Glass.
Use an opaque legible surface when blur is unavailable or when user/platform settings require reduced transparency.
Check reduced-motion, forced-colors, and contrast settings where supported. Reduced-transparency preference support varies; verify target browsers and retain a usable opaque fallback.
Do not claim operating-system transparency settings are honored unless the runtime exposes them and the behavior was checked.

## Verification

For changed interactions, inspect keyboard navigation, focus visibility and restoration, labels, state announcements, and touch access.
Check actual foreground/background pairs, including hover/selected/focused states and imagery behind translucent controls.
Test the affected layout at a normal width and the smallest supported width, with text zoom or representative long text. Do not shrink fonts just to hide overflow.
For marketing layouts, preserve intended content reading order and usable navigation at mobile widths.

See [Acceptance](acceptance.md) for concrete checks and [Sources](sources.md) for the applicable web criteria.

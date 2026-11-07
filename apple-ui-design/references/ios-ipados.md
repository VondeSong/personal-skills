# iOS and iPadOS

## Navigation and adaptation

For iPhone, use a stack for drill-down and tabs for peer destinations when appropriate. A reader can give nearly the whole screen to text; it does not need a large CTA.
Use sheets for bounded tasks and standard navigation for ongoing exploration. Keep back navigation, keyboard avoidance, and safe areas intact.

For iPad, choose split navigation or adaptable tabs based on the product. Adapt to available window space rather than assuming every iPad is full screen.
When a multi-column layout collapses, retain the selected object, expose the appropriate detail destination, and provide a route back. Re-expanding should not reset the user's work.
Support touch as well as pointer/keyboard input. Hover may supplement actions, but cannot be their only access path.

## Text and targets

Use semantic text styles, including Dynamic Type; the default body style is 17 pt. A fixed desktop 14 CSS px token is not a native iOS body specification.
At accessibility sizes, allow rows and controls to grow, switch horizontal groups into vertical groups, and keep labels and actions accessible.
Test text in the actual content language; CJK glyphs, long localized labels, and RTL layout can change wrapping and alignment.

Apple's current guidance lists 44×44 pt default and 28×28 pt minimum control sizes for iOS/iPadOS. Use the comfortable default for ordinary custom actions. A minimum is not a preferred target or permission to ignore spacing.
Measure the effective hit region, not only the visible icon. Avoid enlarged invisible hit regions overlapping neighboring actions.

## Implementation mapping

| Need | SwiftUI starting point | UIKit starting point |
| --- | --- | --- |
| Hierarchical navigation | NavigationStack | UINavigationController |
| Adaptive panes | NavigationSplitView | UISplitViewController |
| Peer destinations | TabView; adaptable style when supported | UITabBarController |
| Native controls | Button, Toggle, Picker, TextField | corresponding UIKit controls |
| Scalable text | Font semantic styles; ScaledMetric for related custom dimensions | preferredFont(forTextStyle:), UIFontMetrics, adjustsFontForContentSizeCategory |
| Standard content material | Material | UIVisualEffectView |
| Accessible custom views | accessibilityLabel/value/actions as needed | UIAccessibility properties and actions |

Verify exact API availability in the target SDK. Let standard bars and controls acquire the platform's current appearance; only custom effects need explicit Liquid Glass adoption.
For older supported OS versions, retain available system surfaces and equivalent behavior. Do not add an unverified API simply because a mockup depicts glass.

## Checks for changed screens

Use compact and expanded layouts, default and accessibility text sizes, keyboard shown/hidden where relevant, light/dark appearance, and VoiceOver.
For iPad changes also verify window resizing and touch access to commands usually shown on hover.
Inspect labels, roles, values, selected states, reading order, dismissal, and return focus. A screenshot can validate appearance but cannot validate these interactions.

Sources and review date: [source index](sources.md).

# Sources and maintenance

Reviewed: 2026-09-10. This is an independent design skill, not an Apple specification.
The source list supports platform conventions. Product-specific layouts, web palette values, and density choices in this pack are local heuristics.

| Subject | Primary reference | Use |
| --- | --- | --- |
| Material roles | [Apple Materials](https://developer.apple.com/design/human-interface-guidelines/materials) | Distinguish Liquid Glass controls/navigation, ordinary content materials, and platform differences. |
| Implementation | [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass) | Standard components first; inspect custom styling and SDK behavior. |
| Typography | [Apple Typography](https://developer.apple.com/design/human-interface-guidelines/typography) | Text styles, platform sizes, and supported text scaling. |
| Color | [Apple Color](https://developer.apple.com/design/human-interface-guidelines/color) | System colors, user accent choices, and context-dependent color meaning. |
| Navigation | [Apple Sidebars](https://developer.apple.com/design/human-interface-guidelines/sidebars), [Toolbars](https://developer.apple.com/design/human-interface-guidelines/toolbars) | Navigation hierarchy, adaptation, command grouping. |
| Accessibility | [Apple Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/) | Control sizes, alternative input, screen-reader support, and user settings. |
| Web text contrast | [WCAG 2.2 SC 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum) | 4.5:1 ordinary and 3:1 large text; exceptions and size definition. |
| Web controls | [WCAG 2.2 SC 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast) | Contrast of essential control/state information. |
| Web interaction patterns | [WAI-ARIA APG](https://www.w3.org/WAI/ARIA/apg/patterns/) | Expected semantics and keyboard behavior for custom widgets. |

Before recommending a version-dependent API or exact new-system appearance, check the relevant current official page and the project's actual SDK/deployment target.
When exact sources cannot be checked, label the recommendation or availability as unverified and use established available components.
A routine spacing or copy change does not require rereading every source.

Chinese typography references were reviewed separately on 2026-10-05; see [Chinese typography](chinese-typography.md#evidence-and-scope) for primary guidance and the explicitly secondary article. This does not refresh the review date of unrelated platform guidance above.

Cross-platform product-style research was reviewed separately on 2026-11-12; see [Initial cross-platform design analysis](cross-platform-apple-style-initial-analysis.md) for dated Craft examples, Codex / Claude Code workflow references, Apple / Android guidance, and the distinction between sourced facts, design interpretation, and candidate directions. This preliminary analysis does not change the skill's rule strengths, token contract, version, or the review date of unrelated guidance above.

Mobile-specific research was reviewed separately on 2026-11-12; see [Initial mobile cross-platform plan](mobile-cross-platform-initial-plan.md) for phone navigation, touch and Chinese input, native Apple / Android versus mobile Web behavior, offline and task-state recovery, and candidate validation scenarios. Product availability and API support remain dated source observations; this research does not claim device testing or change the skill's existing platform scope, version, rule strengths, token contract, or the review date above.

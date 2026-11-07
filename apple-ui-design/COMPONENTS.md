# Component decisions

These are task-dependent choices, not a required app shell. Native framework behavior and the existing product system take precedence over custom mockup metrics.

| Component | Use and behavior |
| --- | --- |
| Sidebar | Peer areas or collections; let people hide it when useful. Prefer shallow navigation, but preserve deep trees when hierarchy is the content being edited. Resizing or alternate navigation must keep destinations reachable. |
| Toolbar | Frequent actions on current content. Group by task and scope; keep less frequent commands in discoverable menus. Narrow layouts must retain access to overflow actions. |
| Inspector | Properties of the current selection. Label the inspected object or selection count. Represent mixed values for multiselection. Hide/collapse it when no longer useful without losing the selection. |
| Navigation stack / tabs | Use hierarchy for drill-down and tabs for peer destinations. Avoid changing tabs as a side effect of selecting an item within one destination. Preserve state across adaptive layouts. |
| Button | Emphasize an action when the task requires a decision. Continuous editors and readers can use ordinary controls without a dominant button. Distinguish disabled, pressed, and focus states. |
| Icon-only action | Familiar meaning, accessible name, and a desktop tooltip where helpful. Tooltip text is not a substitute for an accessibility label or a touch-accessible explanation. |
| Segmented control | A small set of related exclusive views or modes. Allow text to fit; switch to another picker when options or localization no longer fit. |
| List / table | Scanning, comparison, selection, and sorting. Preserve useful density; use explicit headers and keyboard selection where appropriate. State what sorting/filtering affects. |
| Card | A discrete object, meaningful group, or interaction boundary. A media library can legitimately be a card grid. Prefer spacing or separators when containment adds no meaning. |
| Search | Keep query, result count, scope, loading, and no-results states coherent. Preserve a path back to the source context. Use the app's established keyboard activation. |
| Popover / menu | Contextual transient choice or detail. Anchor to the trigger, follow system dismissal, and restore focus to the trigger or another logical survivor. Essential actions must not depend on hover alone. |
| Sheet / dialog | A bounded task connected to its parent. Use standard action order and explicit verbs. Keep modal focus inside while open and restore it on close; handle errors without losing entered data. |
| Empty state | Explain why content is absent. Offer an action only when it helps: a completed queue can simply say there is nothing to review. Distinguish first use, no results, no selection, and unavailable data. |
| Progress / failure | Put status near affected content. Distinguish unknown progress from measurable progress. Retain recovery actions and useful results; do not infer the whole operation failed from one failed item. |
| Destructive action | Show affected scope and consequence. Prefer undo for safely reversible actions; use a clear confirmation boundary when irreversible loss needs deliberate consent. Do not add repeated confirmation to harmless toggles. |

## Custom geometry starting points

For desktop web mockups, a sidebar around 220–260 CSS px and inspector around 280–360 CSS px can be starting points. They are not minimum window widths or Apple component specifications. Measure realistic labels and content before fixing widths.

For native components, let system metrics determine chrome, shape, and control sizing. Visual icon dimensions and the actual hit region are separate measurements.

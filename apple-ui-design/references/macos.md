# macOS native

Read for SwiftUI or AppKit desktop interfaces. For Electron, Tauri, or browser UI, also read [Web](web.md).

## Structure

- Start from the real workspace: reader, list/detail library, document, canvas, or dashboard. Use a sidebar and optional inspector only when navigation and properties warrant them.
- A deep file or layer tree is legitimate content. Avoid flattening it merely to satisfy the usual shallow-sidebar recommendation.
- Respect window title/toolbar integration and operating-system window controls. Use a native menu bar for standard app commands.
- Keep narrow-window behavior explicit: collapse a pane, reveal a detail view, or overflow commands while retaining selection and a way back.
- Distinguish selected rows in active and inactive windows. The keyboard-focused control may differ from the selected document or navigation item.

## Implementation mapping

| Need | SwiftUI starting point | AppKit starting point |
| --- | --- | --- |
| Navigation panes | NavigationSplitView | NSSplitViewController |
| Collections / comparisons | List, Table | NSOutlineView, NSTableView |
| Toolbar / commands | toolbar, commands | NSToolbar, NSMenu |
| Context properties | inspector where supported | contextual view or split pane |
| Semantic text | system Font text styles | NSFont preferred/system font APIs |
| Semantic colors | primary/secondary foreground styles, tint | NSColor label/control/selection roles |
| Standard translucency | Material appropriate to context | NSVisualEffectView |
| Keyboard focus | FocusState and standard controls | responder chain, key-view loop |

These identify APIs to inspect, not availability guarantees. Check the project's SDK and deployment target before using a symbol or modifier. Preserve established AppKit behavior instead of rewriting it into SwiftUI for appearance alone.

Use native semantic color and accent behavior; users can choose a system accent. Do not force the web palette onto native selection or focus rings.
Use system font roles; the common body default is 13 pt. macOS does not expose iOS-style Dynamic Type; provide or preserve app text-size/zoom controls when needed, and test their layout effects.
For custom controls, Apple's current guidance lists a 28×28 pt default and 20×20 pt minimum. Prefer system metrics and comfortable spacing; do not shrink all controls to the minimum.

## Interaction checks

Exercise Tab/Shift-Tab with the relevant keyboard navigation settings, arrow-key movement within composite controls, Return/Space activation as appropriate, Escape dismissal, and command routing to the correct pane.
Retain established shortcuts, context menus, multiselection, drag/drop, and undo where the task depends on them.
Opening a contextual panel should not casually steal editing focus; closing it should leave a logical focus target.
Verify at the smallest supported window and a normal working window with long filenames and representative data density.

Sources and review date: [source index](sources.md).

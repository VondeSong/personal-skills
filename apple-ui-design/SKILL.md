---
name: apple-ui-design
description: Design, critique, and implement macOS, iOS, and iPadOS interfaces, or explicitly Apple-inspired web UI. Use for Apple-platform layout, interaction, screenshots, and design handoff. Preserve the target platform and existing product system; do not impose Apple styling on unrelated UI work.
metadata:
  version: "3.1"
  sources-reviewed: "2026-09-10"
---

# Apple UI Design

Create interfaces whose content, actions, and state are easy to understand and operate.
Retain material, color, and character when they help the task. Visual quietness is an option, not a requirement.

## Scope and reference routing

Choose the relevant surface before applying recipes. Infer it from the request, screenshot, or project and briefly state any consequential assumption. Do not migrate frameworks or redesign unrelated screens to satisfy this skill.

Read only the references needed for this task:

| Task or surface | Read |
| --- | --- |
| macOS native app | [macOS](references/macos.md) |
| iPhone or iPad app | [iOS / iPadOS](references/ios-ipados.md) |
| Apple-inspired web, cross-platform desktop, or marketing site | [Web and cross-platform](references/web.md) |
| Component choice or interaction change | Relevant entries in [Components](COMPONENTS.md) |
| Custom colors, CSS, or measurable handoff | [Token contract](references/tokens.md) and [Tokens](TOKENS.json) |
| Chinese or mixed Chinese/Latin typography, especially editorial web layouts | [Chinese typography](references/chinese-typography.md) |
| Implementing, redesigning, or validating interactions | Relevant checks in [Acceptance](references/acceptance.md) |
| AI suggestions, review queues, or file/media cleanup | [AI workflows](references/ai-workflows.md) |
| Preliminary analysis of Apple-like polish, product identity, or Craft / Codex / Claude Code across platforms | [Initial cross-platform design analysis](references/cross-platform-apple-style-initial-analysis.md) — research and candidate directions, not additional requirements |
| Mobile follow-up to Apple-inspired cross-platform research: phone navigation, input, task continuity, and native / web differences | [Initial mobile cross-platform plan](references/mobile-cross-platform-initial-plan.md) — sourced research and candidate scenarios, not implemented behavior or additional requirements |
| API/version-sensitive advice or disputed convention | Relevant official link in [Sources](references/sources.md) |
| Maintaining or evaluating this skill | [Behavioral cases](EXAMPLES.md) |

For visionOS, watchOS, or tvOS, consult that platform's current official guidance before giving specific layout, input, or size advice. These platforms do not have complete recipes in this pack. In particular, visionOS window glass is not interchangeable with the Liquid Glass control layer.

## Rule strength

**Requirements:** preserve the user's task and information; make essential text readable; provide non-color state cues; keep required actions reachable with supported input and assistive technology; accurately describe implemented and verified behavior.

**Platform guidance:** prefer native component behavior, semantic colors, text styles, and input conventions. Verify availability against the project's deployment target when implementing version-dependent features.

**Design heuristics:** emphasis, density, card use, sidebar depth, spacing, and accent usage are starting points. Depart from them when the product task benefits. Explain a consequential exception briefly.

A reader may have no prominent action. An editor may have several equally available tools and deep document trees. A dashboard may need comparable metrics. A simple view may need only one or two hierarchy levels. Do not invent controls, tiers, or visual emphasis to meet a quota.

## Workflow

### 1. Establish the actual task

Identify the main user activity, content, current state, supported inputs, and requested output: critique, design, implementation, or mockup.
For implementation, inspect the relevant existing UI, components, tokens, framework, and minimum OS/browser support first.
For a screenshot, separate observable problems from hypotheses: keyboard order, hidden states, and responsiveness cannot be proven from pixels.
Use existing context for routine choices; ask only when a missing constraint would materially change the outcome.

### 2. Resolve structure and attention

Preserve working information architecture and familiar commands. Reorganize only what explains a demonstrated problem or fulfills the requested redesign.
Set density according to work: sustained reading, scanning a library, comparing data, or editing a canvas.
Use alignment, grouping, type, and spacing to explain relationships. Add containers when they denote objects, interactions, or meaningful groups.
Make the current selection, editing target, navigation location, and affected operation scope distinguishable.
A focused decision usually benefits from one emphasized action; continuous work does not need a permanent CTA.

### 3. Choose appearance and material

Distinguish content from navigation, controls, and overlays where those layers actually exist.
Use Liquid Glass principally for the navigation/control layer; use ordinary surfaces or standard materials for content. Avoid manually restyling system controls merely to simulate glass.
For custom glass, consult the materials source and verify behavior over changing content. RGBA plus blur is only a web approximation.
Use system-provided overlay separation first; add custom border/shadow treatment only where legibility or overlap needs it.
Neutral, vivid, flat, or dimensional treatments can all be appropriate. Do not reject a white reading canvas, useful chart colors, or discrete content cards just for matching an old anti-pattern.

### 4. Assign color, typography, and geometry

Give colors explicit jobs: content/category, interaction, selection, status, or decoration that supports the product identity.
Keep error, warning, review, and success meanings distinct. Localize urgency to affected content; prominence depends on impact, interruption, and recovery.
Use native semantic text/color roles first. For custom web styles use the token contract, including allowed foreground/background pairs.
Keep visual attention separate from input focus: accent color alone does not define keyboard focus.
Use platform text styles and content-driven sizing; distinguish native points, CSS pixels, and screenshot pixels.
Treat spacing and radii as adjustable optical defaults. Existing product tokens and system component metrics take precedence over this pack's mockup values.

### 5. Specify behavior before polishing

Account for relevant states only: default, hover where applicable, pressed, keyboard focus, selection, disabled, pending, empty, success, and failure.
Keep selection, keyboard focus, and window activation distinct.
Make progress truthful; provide cancellation/retry/recovery when the operation supports them.
Use motion to clarify a change without making it the only signal.
Apply [Acceptance](references/acceptance.md) to the changed behavior. A small copy fix does not require a complete product audit.

## Output contracts

Choose the smallest output that completes the user's request. Do not produce every mode automatically.

**Critique:** prioritize concrete findings. For each, give the observed issue, user impact, replacement, and how to check it. Label uncertain findings. Do not invent defects to fill a list.

**Design/spec:** state platform, viewport assumption, content hierarchy, layout behavior, component choices, and relevant states. Give numeric values where they help implementation, with units and whether they are system defaults or custom suggestions.

**Implementation:** make the requested change in the existing stack. Map design roles to native components or the existing web component system. Verify the affected behavior; report actual checks and material limitations. Code generation is not proof of visual or accessibility quality.

**Mockup:** deliver the requested visual or prompt, using realistic content and a specified platform, frame, density, state, and material placement. Do not present a static image as a verified interactive implementation.

## Final checks

Before delivery, assess only what the task changes:

- Can a person identify the content, current context, and available next steps?
- Does hierarchy fit the task without hiding necessary information or commands?
- Are custom text and essential control indicators legible on their actual backgrounds?
- Can changed interactions be reached, understood, completed, and exited with supported input?
- Does the layout adapt to the relevant window, text, content, and localization variations?
- Have reduced motion/transparency and increased contrast been respected where effects changed?
- Are tested behavior, reasoned design decisions, and unverified platform behavior clearly separated?

Use [Acceptance](references/acceptance.md) for observable checks, not as a mandatory report template.

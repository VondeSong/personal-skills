# Chinese and mixed-script typography

Use for Chinese typography changes, especially prominent web headings and editorial copy. Apply the relevant checks to native UI, but retain native text styles and layout behavior. Apple marketing-page techniques are contextual examples, not universal Apple UI rules.

## Font pairing and spacing

- Equal font sizes do not guarantee equal apparent size or weight. Inspect Han characters, Latin letters, numerals, and punctuation together using actual copy. Check baseline, visual size, and stroke density before adjusting individual runs; prefer a coherent font pairing to numerous local size overrides.
- Start with the project's font stack or platform system fonts. Check the actual fallback on supported platforms and when a web font fails to load. A system stack does not reproduce Apple's website typography on every OS. Do not add or fetch SF Pro SC merely to match a screenshot; use available, appropriately licensed fonts.
- Let font, size, script, and text role determine tracking and leading. Latin display-text negative tracking is not a default for Chinese headings. Avoid global letter-spacing changes intended to solve only the gap between Chinese and Latin text.
- Set the appropriate document/run language and region. Simplified versus Traditional Chinese alone does not determine every punctuation convention.
- Choose a consistent mixed-script spacing strategy. Where target browsers support it, CSS text-autospace can supply visual spacing without modifying copied text. Check existing editorial spaces and other spacing processors before adding a second mechanism; do not blindly insert spaces into stored content, identifiers, URLs, code, or user input. Preserve intentional product copy conventions.

## Wrapping by meaning

- Inspect important headings and short editorial paragraphs for awkward word splits and an isolated final character or punctuation mark. First adjust the responsive measure or layout when appropriate; then protect only the short semantic unit that needs it.
- A scoped nowrap span or nonbreaking space can keep a short product name or final phrase together. Neither should make a long string unbreakable at narrow widths or large text sizes. Relax the protection or choose a meaningful break if it cannot fit; do not shrink the user's text to preserve the composition.
- Explicit, breakpoint-dependent line breaks can serve deliberately authored marketing headlines. Use them sparingly, with real copy and checks between breakpoints. Let dynamic text, ordinary UI labels, and long reading content reflow rather than freezing the line breaks of one screenshot.
- Check line-start/line-end punctuation behavior in the target language. Do not replace correct Chinese punctuation with ASCII punctuation to reduce its visible width.

## Optical alignment and punctuation

Geometric centering can look uneven when a large heading ends with punctuation whose visible ink occupies only part of its advance width. Inspect the actual rendered heading against nearby visual anchors before changing it.

Use a local, font- and line-specific adjustment only when it improves the composition. Punctuation hanging or a small spacing correction are options; no universal 0.5em shift, halfwidth ratio, or negative margin applies. Keep punctuation in the text's reading and copying order. Check clipping, collisions, multiline wrapping, and changed font metrics; absolute positioning is not a general default.

## Verify the affected composition

Inspect real Chinese/Latin/numeric copy at normal, narrow, and intermediate widths, with text zoom and the fallback font. Where a custom web font is involved, inspect before and after loading. Check semantic wrapping, readable spacing, punctuation, baseline, and optical alignment together. Preserve complete accessible text if animation splits a heading into runs, and recheck layout-dependent animation after fonts or wrapping change.

Localization also includes natural phrasing, local date/number conventions, and cultural context when relevant to the requested copy. Do not infer a brand's internal editorial policy or motivation from an isolated page example.

## Evidence and scope

Typography references reviewed 2026-10-05; browser support still needs checking against the project's targets when implementing.

- [W3C Chinese Layout Requirements](https://www.w3.org/TR/clreq/): work-in-progress guidance on regional conventions, mixed composition, punctuation, and line layout, not a browser-support guarantee.
- [CSS Text Level 4](https://www.w3.org/TR/css-text-4/#text-autospace-property): specification for automatic spacing; verify implementation support separately.
- [Apple: The details of UI typography](https://developer.apple.com/videos/play/wwdc2020/10175/): font-specific optical sizes, tracking, and platform text styles.
- [Apple education page](https://www.apple.com.cn/education-initiative/): observed example of short nowrap runs and responsive explicit breaks, not a general layout contract.
- [SkyWT: Apple 官网排版细节鉴赏](https://skywt.cn/blog/apple-typography-details): secondary inspiration for this reference. Its font measurements, fixed offsets, and inferred editorial motivations are not adopted as requirements.

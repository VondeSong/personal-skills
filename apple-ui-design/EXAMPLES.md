# Behavioral evaluation cases

Use these cases when maintaining the skill, not as mandatory work for every UI request.
Evaluate observable decisions rather than exact wording, layout coordinates, or a fixed number of findings.
For an independent pass, provide only the input and relevant raw artifact plus SKILL.md; keep the acceptance notes with the evaluator.
A written response tests guidance and routing. Runtime claims additionally require implementation evidence.

## Contents

- [Reader with no primary action](#1-reader-with-no-primary-action)
- [Dense desktop editor](#2-dense-desktop-editor)
- [iPad adaptation and large text](#3-ipad-adaptation-and-large-text)
- [Custom web colors and glass](#4-custom-web-colors-and-glass)
- [AI partial completion](#5-ai-partial-completion)
- [Apple-inspired marketing](#6-apple-inspired-marketing)
- [Bounded change](#7-bounded-change)
- [Empty queue and critique uncertainty](#8-empty-queue-and-critique-uncertainty)
- [Unsupported platform specialization](#9-unsupported-platform-specialization)
- [Chinese editorial typography across widths](#10-chinese-editorial-typography-across-widths)
- [Continuous content editing](#11-continuous-content-editing)
- [Conversation during streaming](#12-conversation-during-streaming)
- [Review workspace with partial application](#13-review-workspace-with-partial-application)
- [Coherent visual direction](#14-coherent-visual-direction)

## 1. Reader with no primary action

**Input:** “设计一个 iPhone 离线阅读页。正文是核心，只保留返回、字号和书签，没有购买或开始阅读按钮。”

**Expected:** Reading-first layout, appropriate native navigation, scalable text, reachable secondary controls; no invented CTA or mandatory three-level hierarchy.
**Fail:** Adds a large action, dashboard, or sidebar just to satisfy a template.
**Check:** Explain how accessibility text sizes and scroll position behave; mark them specified rather than tested in a design-only response.

## 2. Dense desktop editor

**Input:** “改进 macOS 图层编辑器：保留六层文件树、画布、属性面板和高密度工具栏。当前问题是选中图层与键盘焦点分不清。”

**Expected:** Preserve useful depth and tool availability; distinguish selected layer from input focus; retain context as panes collapse.
**Fail:** Flattens the tree to two levels, forces one giant action, or converts everything into cards.
**Check:** Keyboard operation and active/inactive selection treatments are specified separately.

## 3. iPad adaptation and large text

**Input:** “SwiftUI 学习应用，支持 iPad 多窗口和 iPhone。大窗口是牌组、卡片列表、详情三列，窄窗口和最大辅助字号也要能编辑。”

**Expected:** Target-dependent API choices, adaptive navigation retaining selection, layouts that reflow at larger text sizes, touch access to commands.
**Fail:** Hardcodes desktop text sizes, assumes every iPad is full screen, or hides actions exclusively behind hover.
**Check:** Verify or specify navigation back to the list, editing with the keyboard shown, and font scaling.

## 4. Custom web colors and glass

**Input:** “用 React 做待审核列表，白底 12px 的文字用 #8E8E93，成功文字用 #34C759，顶部工具栏半透明覆盖图片。”

**Expected:** Identify ordinary-text contrast problems, choose compatible foreground/background pairs, retain readable metadata, distinguish static pair tests from glass composition.
**Fail:** Accepts colors because they resemble system colors, applies opacity to the text, or calls RGBA native Liquid Glass.
**Check:** Palette validator passes declared pairs; bright/dark/busy background checks remain separate.

## 5. AI partial completion

**Input:** “文件整理：分析得到 12 条建议，用户接受 8 条，执行成功 5 条、失败 3 条，另外 4 条还没处理。设计状态和后续操作。”

**Expected:** Distinguish analysis, review, and execution; show 5 applied, 3 failed, 4 awaiting decision; scope retry to failed items; preserve successful results.
**Fail:** Says all 12 completed, marks all review items as errors, or retries already-applied items silently.
**Check:** Completion/partial-failure announcement does not steal focus; irreversible actions expose scope.

## 6. Apple-inspired marketing

**Input:** “做一个 Apple 风格摄影产品官网，保留品牌橙和作品大图，手机端优先。”

**Expected:** Editorial layout with product content, responsive type, brand-consistent accent, semantic web controls.
**Fail:** Adds fake working macOS chrome, a productivity sidebar, or compact 14px body everywhere.
**Check:** Mobile reading order and keyboard navigation; no claim that web blur is native material.

## 7. Bounded change

**Input:** “现有 Windows Tauri 应用只修复工具栏按钮的键盘焦点，其他视觉保持不变，按 Apple UI Design 的原则处理。”

**Expected:** Inspect and fix the existing focus behavior; preserve Windows chrome, stack, and product tokens; run focused verification.
**Fail:** Redesigns the app, migrates frameworks, or adds a full Apple palette and sidebar.
**Check:** Visible focus, keyboard activation, and no unrelated layout changes.

## 8. Empty queue and critique uncertainty

**Input:** “审核一下这张已完成队列的截图。页面只有‘暂无待审核项目’和历史记录入口。”

**Raw artifact:** Supply a real screenshot when executing this case.
**Expected:** Allows a simple empty state; assesses only visible spacing/hierarchy/readability; treats hidden keyboard and loading behavior as unknown.
**Fail:** Invents missing actions or claims VoiceOver passed from the screenshot.

## 9. Unsupported platform specialization

**Input:** “给 visionOS 设计一个可沉浸浏览的相册，输出原生交互与材质方案。”

**Expected:** Consults current platform-specific official guidance before giving exact spatial/input rules; distinguishes window glass from Liquid Glass.
**Fail:** Reuses iPhone touch targets or a desktop glass/sidebar recipe without verification.

## 10. Chinese editorial typography across widths

**Input:** “优化中文产品页的标题‘为灵感，留一点空间。’和正文中的‘Nova Studio Pro’，要有 Apple 官网的精致感。支持 Windows、macOS 和手机；文案以后会变，也要支持文字放大。”

**Expected:** Uses the Chinese typography reference; inspects mixed-script font metrics and fallback; scopes any nowrap or optical punctuation correction to actual need; preserves reflow when copy or text size changes.
**Fail:** Downloads SF Pro SC, applies negative tracking to all Chinese, shifts every title by 0.5em, or makes entire paragraphs unbreakable.
**Check:** Narrow and intermediate widths, zoom, and font fallback preserve readable complete text. Distinguish proposed checks from rendered results.

## 11. Continuous content editing

**Input:** “为中文资料笔记应用设计桌面与手机场景，参考 Craft 的精致感。现有集合、搜索和文档层级保留；支持正文编辑、格式工具及撤销。请给可实现的设计规格。”

**Expected:** Connect discovery, document identity, selection/editing context, relevant tools, save feedback, undo, and return. Map component groups to coherent visual roles and platform-dependent density. Use the existing editor's capabilities or state dependencies.
**Fail:** Produces only a polished library homepage, invents a replacement navigation system, or describes menus without what happens to selection, input, and the affected content.
**Check:** Walk a text-formatting action, cancel a menu, undo a change, and return to the search result. Assess specified continuity separately from rendered behavior.

## 12. Conversation during streaming

**Input:** “设计一个桌面与 Android 浏览器都能用的中文 AI 会话界面，有文本、图片附件和工具结果。视觉参考 Claude／Codex 的图形入口，给出完整设计方案。”

**Expected:** Connect draft, attachment readiness/failure, send acknowledgment, streaming, reading older messages, stopping, and scoped retry. Keep message/tool/result hierarchy clear and visual roles coherent across the relevant themes and windows.
**Fail:** Forces scrolling while the user reads older content, treats failed attachments as sent, collapses connection loss into task failure, or invents verified backend behavior.
**Check:** Use a long reply and a failed attachment; identify the return-to-latest action, preserved input, and the precise retry target. Do not announce each token to assistive technology.

## 13. Review workspace with partial application

**Input:** “设计一个类似 Codex 工作台的审阅场景：12 条建议，选中 8 条，5 条应用成功、3 条失败，4 条未选择。桌面可看具体差异，手机也能审阅并继续处理。只输出设计规格。”

**Expected:** Tie task, selected objects, summary, concrete changes, feedback and action scope together; preserve selection and outcome across detail navigation; reuse the AI state model and appropriate component composition.
**Fail:** Shows only summary cards, retries successful work, hides decisive change details on mobile, or claims the design has already passed runtime/accessibility checks.
**Check:** Trace a selected item's evidence, the failed-item retry, and return to the original task. Compare state meaning and visual hierarchy across desktop/mobile without requiring identical layouts.

## 14. Coherent visual direction

**Input:** “为中文资料与 AI 会话应用设计主工作区，配色要优雅舒服，参考 Craft、Claude、Codex。保留现有信息结构，请给一套具体视觉方向，呈现同一内容的浅色与深色效果，并兼顾桌面和手机。”

**Expected:** Converts references into an explicit surface temperature, color emphasis, content/control typography and boundary treatment; applies a coherent palette to a concrete component group. Reuses existing product styling or deliberately chooses a custom candidate. Distinguishes product evidence from proposed values.
**Fail:** Gives only style adjectives, treats blue-gray tokens as the only valid style, makes every icon/action equally colorful, mechanically applies one type profile to the entire screen, or claims contrast calculations alone prove visual quality.
**Check:** Compare real content across themes and widths; inspect the weight of the frame versus content, selection versus focus, and neutral/colored action choices. Only report rendered or exercised states actually inspected. Do not treat one candidate palette as a new universal rule.

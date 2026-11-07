# Behavioral evaluation cases

Use these cases when maintaining the skill, not as mandatory work for every UI request.
Evaluate observable decisions rather than exact wording, layout coordinates, or a fixed number of findings.
For an independent pass, provide only the input and relevant raw artifact plus SKILL.md; keep the acceptance notes with the evaluator.
A written response tests guidance and routing. Runtime claims additionally require implementation evidence.

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

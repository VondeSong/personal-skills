# Apple UI Design Skill Pack

v3.1 · Apple 平台界面设计、审查与实现指导。

入口是 [SKILL.md](SKILL.md)。核心覆盖 macOS、iOS、iPadOS，以及明确要求 Apple 风格的网页和跨平台产品；其他 Apple 平台需要另查对应官方资料。

本包保留内容优先、清晰层级、语义颜色和克制材质的方向，将具体平台、AI 工作流、Token 和验收规则按需加载。经验建议允许合理例外，不要求每页都有主按钮、三层信息或固定侧栏。

## 使用与验证

- 常规任务：读取入口，并按任务选择关联参考文件。
- 自定义颜色：读取 [Token 合约](references/tokens.md)，运行 `python scripts/validate_tokens.py`。
- 技能维护：使用 [行为案例](EXAMPLES.md)验证实际决策，并运行 skill-creator 的 quick_validate.py。
- 不包含或重新分发 Apple 专有字体、SF Symbols 素材；不是 Apple 官方技能。

## v2 到 v3

保留原文件名方便既有引用。版本字段移至受支持的 `metadata.version`。
Token 是本包的自定义格式，不再将 JSON Schema 的元 schema 地址当作数据 schema。
基础颜色键保留但部分色值已调整；新增文字/填充配对、明暗主题的高对比度覆盖和自动验证。
字体、尺寸移到明确的 web/native 分组；旧玻璃 RGBA 键被显式的网页材质近似值及不透明回退替代。使用旧 Token 的代码需按 [迁移说明](references/tokens.md)更新。

验证工具只检查明确声明的静态配色，不代表真实界面的无障碍或原生适配已通过。

## 研究与候选方案（按需读取）

以下文件位于 `references/`，由 [SKILL.md](SKILL.md) 的路由表按任务引用。它们是带来源的研究与候选方案，不是附加要求，也不表示已在任何具体产品上验证。

- [跨平台初步分析](references/cross-platform-apple-style-initial-analysis.md)：Codex、Claude Code、Craft 为何有苹果气质又保持自身风格。
- [移动端初步方案](references/mobile-cross-platform-initial-plan.md)：手机导航、触控与中文输入、iOS／Android／移动 Web 差异，以及完整性复核。
- [桌面与手机视觉方案](references/desktop-mobile-visual-style-initial-plan.md)：配色、字体、图标、圆角、阴影与材质；候选色板见 [visual-presets.json](references/visual-presets.json)。
- [应用场景](references/application-scenarios.md)：把对象、组件、视觉角色、状态与恢复连成完整场景。

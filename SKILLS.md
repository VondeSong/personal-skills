# 技能用途与来源清单

[技能分类总览](https://github.com/users/VondeSong/projects/6) · [仓库说明](README.md) · [维护规则](AGENTS.md)

核对日期：2026-11-07。用途标签与来源标签分别记录；本清单用于技能目录，不表示开发任务进度。

- **自己开发**：本机专用工作流的编写与维护。
- **借鉴修改**：已找到上游或用户提供的模板，并保留了本机改造；宿主兼容、重命名、调用策略也属于改动。
- **第三方原版**：仅保留来源和版本引用，本机安装继续存在。
- **来源待核实**：证据不足，继续备份源码，不推断为原创或原版。

| 技能 | 用途类别 | 来源标签 | 保存方式 | 本机版本 | 来源与判断依据 |
| --- | --- | --- | --- | --- | --- |
| `apple-ui-design` | 界面与视觉 | 来源待核实 | 源码备份 | 3.1 | 本机 v3.1 包经个人升级维护；尚未确认最初技能包的原始作者和上游，暂保留源码，不按纯第三方移除。 |
| `apple-web-motion` | 界面与视觉 | 借鉴修改 | 源码备份 | — | [emilkowalski/skills/tree/main/skills/apple-design](https://github.com/emilkowalski/skills/tree/main/skills/apple-design)；安装聊天确认来自 Emil 的 apple-design；按用户要求重命名目录、技能名与标题。 |
| `break` | 界面与视觉 | 借鉴修改 | 源码备份 | — | [jakubkrehel/skills](https://github.com/jakubkrehel/skills)；2026-10-10 安装记录明确包含 Windows/Codex 适配；主文件新增 Host compatibility，保留定制源码。 |
| `build-design` | 界面与视觉 | 借鉴修改 | 源码备份 | — | [jakubkrehel/skills](https://github.com/jakubkrehel/skills)；2026-10-10 安装记录明确包含 Windows/Codex 适配；主文件新增 Host compatibility，保留定制源码。 |
| `content-to-tasks` | 知识与归档 | 自己开发 | 源码备份 | — | 制作滴答清单素材转任务 Skill 聊天与本机滴答字段、去重和附件流程。 |
| `craft-car-archive` | 知识与归档 | 自己开发 | 源码备份 | — | 本机专用工作流、个人资料库或项目规则；未发现外部完整技能上游。 |
| `craft-car-review` | 知识与归档 | 自己开发 | 源码备份 | — | 设计汽车归档审核 Skill 聊天中按用户要求建立独立审核流程。 |
| `craft-general-archive` | 知识与归档 | 自己开发 | 源码备份 | — | 本机专用工作流、个人资料库或项目规则；未发现外部完整技能上游。 |
| `craft-page-visualizer` | 知识与归档 | 自己开发 | 源码备份 | — | 本机专用工作流、个人资料库或项目规则；未发现外部完整技能上游。 |
| `design-reference-library` | 知识与归档 | 自己开发 | 源码备份 | — | 设计参考归档聊天中按用户要求新建，使用本机共享设计参考政策。 |
| `design-taste-frontend` | 界面与视觉 | 借鉴修改 | 源码备份 | tasteskill v2 | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)；39 个文件可对应上游历史内容；本机另有 agents/openai.yaml，明确关闭隐式调用，属于需保留的个人配置。 |
| `eagle-library-organizer` | 知识与归档 | 自己开发 | 源码备份 | — | 本机专用工作流、个人资料库或项目规则；未发现外部完整技能上游。 |
| `explain-interface` | 界面与视觉 | 借鉴修改 | 源码备份 | — | [jakubkrehel/skills](https://github.com/jakubkrehel/skills)；2026-10-10 安装记录明确包含 Windows/Codex 适配；主文件新增 Host compatibility，保留定制源码。 |
| `git-github-workflow` | 工程与开发 | 自己开发 | 源码备份 | — | 个人 Git/GitHub 约定；检查后集中中文提交同步、定向更新看板，在关联事项维护 Codex 对话入口并适时命名当前对话；保留范围审核、远端核验和验收约束，发布由用户决定。 |
| `harness-wire-list` | 工程与开发 | 自己开发 | 源码备份 | — | 本机专用工作流、个人资料库或项目规则；未发现外部完整技能上游。 |
| `hub-generate-flashcards` | 学习与标签 | 自己开发 | 源码备份 | — | 本机专用工作流、个人资料库或项目规则；未发现外部完整技能上游。 |
| `hub-tag-steward` | 学习与标签 | 自己开发 | 源码备份 | — | 本机专用工作流、个人资料库或项目规则；未发现外部完整技能上游。 |
| `icon-reference-variants` | 界面与视觉 | 借鉴修改 | 源码备份 | — | 用户提供 SKILL (1).md 后扩写，并明确加入至少 30% 结构差异门槛；保留本机改造版，原始作者未确认。 |
| `impeccable` | 界面与视觉 | 第三方原版 | 来源引用 | 4.8.0 | [pbakaus/impeccable](https://github.com/pbakaus/impeccable)；用户确认未做个性化修改；本机元数据为 4.8.0，前次已停止跟踪安装文件。 |
| `interface-review` | 界面与视觉 | 借鉴修改 | 源码备份 | — | [jakubkrehel/skills](https://github.com/jakubkrehel/skills)；2026-10-10 安装记录明确包含 Windows/Codex 适配；主文件新增 Host compatibility，保留定制源码。 |
| `ip-as-logo` | 界面与视觉 | 第三方原版 | 来源引用 | — | [s1dashu/ip-as-logo-skill](https://github.com/s1dashu/ip-as-logo-skill)；5 个受跟踪文件与该上游历史提交完整一致，按文本换行归一化核验。 |
| `local-file-organizer` | 文件与浏览 | 自己开发 | 源码备份 | — | 本机专用工作流、个人资料库或项目规则；未发现外部完整技能上游。 |
| `obsidian-lifeos-archive` | 知识与归档 | 自己开发 | 源码备份 | — | 本机专用工作流、个人资料库或项目规则；未发现外部完整技能上游。 |
| `project-steward` | 工程与开发 | 借鉴修改 | 源码备份 | — | [CheshireMew/project-steward](https://github.com/CheshireMew/project-steward)；本机主文件收窄自动启用范围，且有上游未包含的界面与交互治理资料及相关测试。 |
| `record-to-log` | 知识与归档 | 自己开发 | 源码备份 | — | 本机专用工作流、个人资料库或项目规则；未发现外部完整技能上游。 |
| `stageshow` | 界面与视觉 | 借鉴修改 | 源码备份 | 0.1.0 | [benjitaylor/skills/tree/main/stageshow](https://github.com/benjitaylor/skills/tree/main/stageshow)；本机主文件改为独立产品展示素材范围，增加严格还原与主流程分工限制；保留定制版。 |
| `state-machine` | 界面与视觉 | 借鉴修改 | 源码备份 | — | [jakubkrehel/skills](https://github.com/jakubkrehel/skills)；2026-10-10 安装记录明确包含 Windows/Codex 适配；主文件新增 Host compatibility，保留定制源码。 |
| `tabweave-organize` | 文件与浏览 | 自己开发 | 源码备份 | — | 本机专用工作流、个人资料库或项目规则；未发现外部完整技能上游。 |
| `variant` | 界面与视觉 | 借鉴修改 | 源码备份 | — | [jakubkrehel/skills](https://github.com/jakubkrehel/skills)；2026-10-10 安装记录明确包含 Windows/Codex 适配；主文件新增 Host compatibility，保留定制源码。 |

## 引用与恢复

- `ip-as-logo`：按上游固定提交 `565d7418e3dbf187a3a50a012963c95d0d64747d` 恢复；本次逐文件核对 5/5 一致。
- `impeccable`：按官方 `skill-v4.8.0` 发行页恢复；本机版本元数据为 4.8.0，未改动状态由用户确认。
- 没有明确版本时不填占位文字；上游提交及定制依据保留在来源记录中。
- 完整机器可读清单见 [skills-manifest.json](skills-manifest.json)。

## 本机连接配置

Craft 归档技能中的实际连接配置及带连接地址的 `agents/openai.yaml` 只保留本地。仓库提供对应的 `config.example.json` 和 `agents/openai.example.yaml`，恢复时复制为本机文件名并填写自己的连接信息。实际凭据不进入后续提交；既有历史未重写。

# 技能用途与来源清单

[技能分类总览](https://github.com/users/VondeSong/projects/6) · [仓库说明](README.md) · [维护规则](AGENTS.md)

核对日期：2026-11-07。用途标签与来源标签分别记录；本清单用于技能目录，不表示开发任务进度。

- **自己开发**：本机专用工作流的编写与维护。
- **借鉴修改**：已找到上游或用户提供的模板，并保留了本机改造；宿主兼容、重命名、调用策略也属于改动。
- **第三方原版**：仅保留来源和版本引用，本机安装继续存在。
- **来源待核实**：证据不足，继续备份源码，不推断为原创或原版。

| 技能 | 用途类别 | 来源标签 | 保存方式 | 本机版本 | 简介 |
| --- | --- | --- | --- | --- | --- |
| `apple-ui-design` | 界面与视觉 | 来源待核实 | 源码备份 | 3.1 | Apple 平台界面、组件、无障碍与设计验收 |
| `apple-web-motion` | 界面与视觉 | 借鉴修改 | 源码备份 | — | 网页弹簧、拖拽、惯性与交互手感 |
| `break` | 界面与视觉 | 借鉴修改 | 源码备份 | — | 组件极端输入与异常场景检查 |
| `build-design` | 界面与视觉 | 借鉴修改 | 源码备份 | — | 按 Figma 或参考图严格还原界面 |
| `content-to-tasks` | 知识与归档 | 自己开发 | 源码备份 | — | 素材转滴答任务或收件箱笔记 |
| `craft-car-archive` | 知识与归档 | 自己开发 | 源码备份 | — | Craft Car 汽车资料归档 |
| `craft-car-review` | 知识与归档 | 自己开发 | 源码备份 | — | Craft Car 归档结果独立审核 |
| `craft-general-archive` | 知识与归档 | 自己开发 | 源码备份 | — | Craft Archive / XV 通用归档 |
| `craft-page-visualizer` | 知识与归档 | 自己开发 | 源码备份 | — | Craft 页面转可编辑白板 |
| `design-reference-library` | 知识与归档 | 自己开发 | 源码备份 | — | 设计参考案例的归档与检索 |
| `design-taste-frontend` | 界面与视觉 | 借鉴修改 | 源码备份 | tasteskill v2 | 网页与应用的视觉方向与审美评审 |
| `eagle-library-organizer` | 知识与归档 | 自己开发 | 源码备份 | — | Eagle 素材库文件夹与标签治理 |
| `explain-interface` | 界面与视觉 | 借鉴修改 | 源码备份 | — | 解析界面的实现方式与组件结构 |
| `git-github-workflow` | 工程与开发 | 自己开发 | 源码备份 | — | Git/GitHub 接入、中文提交同步、看板与 Codex 对话关联 |
| `harness-wire-list` | 工程与开发 | 自己开发 | 源码备份 | — | 汽车线束图纸提取及核对 wire list |
| `hub-generate-flashcards` | 学习与标签 | 自己开发 | 源码备份 | — | 按来源生成、改善与校验 Hub 闪卡 |
| `hub-tag-steward` | 学习与标签 | 自己开发 | 源码备份 | — | Hub 标签定义、层级与重复治理 |
| `icon-reference-variants` | 界面与视觉 | 借鉴修改 | 源码备份 | — | 参考图标的结构变体与迭代 |
| `impeccable` | 界面与视觉 | 第三方原版 | 来源引用 | 4.8.0 | 前端界面设计、评审与打磨 |
| `interface-review` | 界面与视觉 | 借鉴修改 | 源码备份 | — | 界面变更的分支、PR 与工作区审查 |
| `ip-as-logo` | 界面与视觉 | 第三方原版 | 来源引用 | — | 极简 IP 角色 Logo 与图标生成 |
| `local-file-organizer` | 文件与浏览 | 自己开发 | 源码备份 | — | Windows 本地文件归档与核验 |
| `obsidian-lifeos-archive` | 知识与归档 | 自己开发 | 源码备份 | — | Obsidian OS / Sources 知识归档 |
| `project-steward` | 工程与开发 | 借鉴修改 | 源码备份 | — | 架构冲突、系统性返工及阶段验收治理 |
| `record-to-log` | 知识与归档 | 自己开发 | 源码备份 | — | 把零散叙述整理为可信日志 |
| `stageshow` | 界面与视觉 | 借鉴修改 | 源码备份 | 0.1.0 | 产品界面展示素材与脚本演示动画 |
| `state-machine` | 界面与视觉 | 借鉴修改 | 源码备份 | — | 组件状态枚举与可切换预览 |
| `tabweave-organize` | 文件与浏览 | 自己开发 | 源码备份 | — | TabWeave / Vivaldi 标签页整理判断 |
| `variant` | 界面与视觉 | 借鉴修改 | 源码备份 | — | 组件视觉方案与可选变体 |

## 引用与恢复

- `ip-as-logo`：作者 s1dashu；按[上游固定提交 `565d7418`](https://github.com/s1dashu/ip-as-logo-skill/tree/565d7418e3dbf187a3a50a012963c95d0d64747d)恢复；已逐文件核对 5/5 一致。
- `impeccable`：作者 Paul Bakaus（pbakaus）；按[官方 `skill-v4.8.0` 发行页](https://github.com/pbakaus/impeccable/releases/tag/skill-v4.8.0)恢复；本机版本元数据为 4.8.0，未改动状态由用户确认。
- 没有明确版本时不填占位文字；上游提交及定制依据保留在来源记录中。
- 完整机器可读清单、上游来源与判断依据见 [skills-manifest.json](skills-manifest.json)；表格简介复用其中的 `description`。

## 本机连接配置

Craft 归档技能中的实际连接配置及带连接地址的 `agents/openai.yaml` 只保留本地。仓库提供对应的 `config.example.json` 和 `agents/openai.example.yaml`，恢复时复制为本机文件名并填写自己的连接信息。实际凭据不进入后续提交；既有历史未重写。

# 个人 Codex 技能库

保存自建及明确个性化维护的 Codex 技能和修改历史。每个受维护技能保留自己的文件夹，说明、脚本、参考资料和素材一起管理；已有来源与许可证保持原样。未做个性化修改的第三方技能只记录来源、版本和安装入口。

本地维护目录为 `C:/Users/yongs/.codex/skills`，私有 GitHub 仓库为 `VondeSong/personal-skills`。

[技能分类总览](https://github.com/users/VondeSong/projects/6) · [完整用途与来源清单](SKILLS.md) · [维护规则](AGENTS.md) · [Issues](https://github.com/VondeSong/personal-skills/issues)

个人技能看板用于浏览已安装技能，按用途类别组织，并用彩色标签区分“自己开发、借鉴修改、第三方原版、来源待核实”；不按开发任务阶段管理。所有本机安装文件均保留，自建或改造过的继续备份，确认未改动的第三方技能仅记录来源和版本。

## 第三方技能引用

以下技能保留本机安装，安装目录不再由本仓库跟踪。这里的版本来自本机技能元数据；换电脑时按上游相应版本重新安装。

| 技能 | 作者与来源 | 本机标示版本 | 安装与恢复入口 |
| --- | --- | --- | --- |
| Impeccable | Paul Bakaus / [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | 4.8.0 | [官方 4.8.0 发行页](https://github.com/pbakaus/impeccable/releases/tag/skill-v4.8.0)，按作者说明恢复 Codex 适用版本 |
| IP as Logo | s1dashu / [ip-as-logo-skill](https://github.com/s1dashu/ip-as-logo-skill) | 未标记版号；固定提交 `565d7418` | [对应源版本](https://github.com/s1dashu/ip-as-logo-skill/tree/565d7418e3dbf187a3a50a012963c95d0d64747d)，已逐文件核对 5/5 一致 |

本次已检查 29 个技能：15 个本机专用编写、11 个借鉴修改、2 个第三方原版引用，1 个原始来源待核实并保留源码。详细依据见 [SKILLS.md](SKILLS.md)。Jakub 系列保留 Windows/Codex 适配，Taste 保留个人调用策略，Stageshow 和 Project Steward 保留本机改造，不能将这些改动误判为上游原版。

## 保存方式

按 [AGENTS.md](AGENTS.md) 执行：Codex 每完成一轮技能修改并完成必要检查后，合并创建一次中文提交并同步 GitHub。提交说明记录改动、目的及实际检查结果。只保存本轮相关文件，保留其他任务的未完成修改。

自动保存由 Codex 在任务完成时执行，不依赖定时任务或后台文件监听；手动编辑文件后仍需交由 Codex 保存，或自行提交。

## 排除范围

`.gitignore` 排除系统自带的 `.system/`、已登记为引用的第三方安装目录、依赖和解释器缓存、本地诊断、临时文件、旧备份、环境私有配置和密钥。系统技能随 Codex 管理，不由本仓库恢复。

Craft 归档技能的实际连接配置与含连接地址的宿主元数据只保留本地；仓库提供对应脱敏示例，迁移时复制并填写个人连接信息。既有提交历史未改写。

各技能已有的局部忽略规则继续生效。真正维护的脚本、测试、示例、引用和图片等素材按其用途保留。

# Hub 单目标调用约定

业务决策统一引用 [task-conversion.md](task-conversion.md)，执行与恢复引用 [dida-workflow.md](dida-workflow.md)。本文件仅定义宿主边界和机器契约，不表示宿主已部署新版。

## 输入与唯一写入者

| 输入 | 宿主提供的事实 |
| --- | --- |
| `mode`、`executor` | `plan_only` 时模型只出方案、由 `host` 写入；`execute` 时指定唯一执行者 `host` 或 `agent`，另一方不重放 |
| `operationId`、`itemId`、`contentRevision` | 本次操作、稳定来源身份、冻结的内容版本；重试沿用操作身份 |
| `intent`、`authorization` | 区分仅提取、明确规划、保存副本；用户选中滴答保存位置代表已授权保存该材料，不额外要求确认参考笔记 |
| `destination` | 唯一 `accountId`、`libraryId` 和 `allowedProjectIds`；每次调用只处理一个目标资料库 |
| `source`、`attachments` | 原题、完整正文、来源 URL、按顺序的引用/回复及原附件；将用户本次指令与第三方素材分开传递 |
| `targetContext` | 当前清单、收件箱身份、分栏、准确标签名、任务及来源绑定；含读取时间，区分空结果与读取失败 |
| `capabilities` | 已验证的字段、层级限制和附件通道状态；没有凭据 |

模型缺少工具时使用宿主快照；缺少关键上下文时返回对应缺口。宿主校正原文、标题和附件关系，保持用户编辑。Hub 不把视频本体交给模型分析，只提供链接和文件事实，原件仍由附件适配器处理。

## 输出契约

- JSON Schema：[hub-result.schema.json](../schemas/hub-result.schema.json)，Draft 2020-12。
- 完整方案样例：[hub-plan.example.json](../schemas/hub-plan.example.json)。所有示例 ID 都是离线占位，不能用于真实写入。
- `contractVersion=content-to-tasks-hub-v3`，`didaPolicyVersion=inbox-notes-v2`。
- 外层业务类别用 `taskClass=reference|action`；`task.kind` 仅表示滴答原生 `NOTE|TEXT|CHECKLIST`。
- `tasks[].localId` 是方案身份，`remoteId` 是真实对象身份。父子方案关系用 `parentLocalId`，待父任务回读后才映射到真实 `task.parentId`，逐步重新校验。
- 更新已有记录时，`writeConfirmed=true` 表示已确认本次写入生效；`verified` 另外表示全部目标字段核验通过。这样类型修正失败仍可报告 `partial`，不会误报零副作用的 `failed`。
- `source.urls` 和实际正文同时保留来源链接；附件通过 `sourceId`、`localTaskId` 绑定。每个必须保存的原件设 `required=true`。

| `status` | 含义与后续 |
| --- | --- |
| `planned` | 没有本次写入；只表示可交给唯一执行者的方案 |
| `needs_input` / `needs_connection` | 缺关键用户信息或目标/连接能力；明确缺口，不造 ID |
| `executed` | 所有任务已回读，必需附件均可读取；不是仅拿到创建响应 |
| `partial` | 已确认部分副作用，仍有类型、正文或附件等未完成；保留真实 ID 继续修复 |
| `failed` | 能确认本次没有任何副作用，且确定失败 |
| `unknown` | 请求可能已生效但无法确认；查同一操作绑定与目标，不自动重放 |

方案模式只允许 `planned/needs_input/needs_connection/failed`，不输出新建对象的真实 ID、成功附件状态或成功核验。更新/复用可引用快照中已有对象 ID，但不声称本次已执行。

## 校验与提交

1. 对输出执行 JSON Schema 和关系校验：`python scripts/validate_hub_result.py result.json`。需要 `jsonschema>=4.18,<5`；缺库明确失败。单元测试使用同一依赖。
2. 宿主比对调用包中的操作、来源版本、唯一目标、授权和来源正文，不接受模型自行改写身份。来源更新或目的地改变使旧方案失效；有副作用的操作先核对已有绑定。
3. 将每次最终写入映射为 [dida-fields.md](dida-fields.md) 的规范结构，运行 `validate_dida_payload.py`；随后紧邻写入再确认快照仍有效。JSON Schema 不代替实时目标、笔记不变量或层级校验。
4. 有附件时先执行 [附件预检](dida-private-attachments.md)，写入后记录任务与原件各阶段的真实回读。模型输出 `verified=true` 不是证据，宿主必须独立核验。

`validate_hub_result.py` 另外检查唯一方案/附件身份、父子方案无环、附件关系、目标范围、成功记录的真实 ID、来源 URL 入正文，以及失败与部分成功的状态一致性。它不联网，也不能证明授权或回读确实发生。

## v2 迁移及多库保留

旧 v2 的外层 `kind=reference/action` 显式迁移为 `taskClass`，不能传到滴答 `task.kind`。迁移需重读来源、绑定和当前对象，补齐新版身份与状态字段并重新校验；拒绝未知版本，不把旧结果改个版本号直接重放。宿主尚未支持 v3 时保留方案并报告接入缺口。

每个资料库分别保存操作、绑定和失败状态；添加副本不删除本地正文、原件或其他副本。Craft 目标交由 `craft-general-archive`。本技能升级不改宿主代码，也不触发历史数据批量迁移。

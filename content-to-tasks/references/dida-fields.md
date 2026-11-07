# 字段映射与参数校验

语义遵从 [决策规则](task-conversion.md)。本文件定义任务字段及校验器输入。

## 两层命名

校验对象是规范化的任务字段，如 `projectId/columnId/parentId/tags`。当前 MCP 的 `create_task({task, client_timezone})`、`update_task({task_id, task})` 中，`task` 使用驼峰字段；外层包装可用下划线。读取实时 schema，先映射再校验最终 `task`；`taskClass` 等控制字段不传入 `task`。

其他宿主显式映射并核对往返值；校验通过后参数变化须重验。参数哈希不能代替账户、权限或快照真实性证明。

| 字段 | 映射与检查 |
| --- | --- |
| `kind` | `TEXT/NOTE/CHECKLIST`；语义分类另放外层 `taskClass=action/reference` |
| `projectId/id/columnId` | 实时对象；更新需同清单当前任务；移动另处理 |
| `title/content/desc/items` | TEXT/NOTE 用 content；CHECKLIST 用 desc 和 items；补丁保留未管理字段 |
| `priority` | 严格整数 `0/1/3/5`，布尔值不算 |
| `startDate/dueDate` | 带时区的 ISO 字符串；纯日期先按全天映射；比较补丁合并后的日期 |
| 清除日期 | 当前接口支持时，更新用 `1970-01-01T00:00:00.000+0000`；省略是保留，null 不用作猜测清空 |
| `isAllDay/timeZone` | 匹配时间语义；有日期须有时区；本地日期落点仍需回读 |
| `items` | 只用于 CHECKLIST；保留 ID 和完成状态；NOTE 列表写正文 |
| `parentId` | 已存在、同清单；无环；包含已有祖先，根为第 1 层 |
| `status/completedTime` | 新建未完成；内容更新不隐式完成或重开；完成动作走专用接口 |

先创建并回读父任务，再验证子任务。`max_task_depth` 来自当前能力，不硬编码历史层数。更新父关系时提供移动节点的完整后代，并在 `subtree_complete_ids` 标记，检查移动后整个子树的深度。

## 校验输入 v2

`python scripts/validate_dida_payload.py input.json` 使用标准库，无网络或写入。示例 ID 仅示意：

```json
{
  "snapshot": {
    "projects": [{"id":"actual-inbox","closed":false,"permission":null}],
    "inbox_project_id": "actual-inbox",
    "tags": [], "columns": [], "tasks": [],
    "max_task_depth": null, "subtree_complete_ids": []
  },
  "allowed_project_ids": ["actual-inbox"],
  "operations": [{
    "operation": "create", "taskClass": "reference", "explicit_fields": {},
    "task": {"projectId":"actual-inbox","title":"用户原题","kind":"NOTE","content":"用户原文","status":0}
  }]
}
```

`explicit_fields` 为字段名到用户明确指令摘录的映射，如 `{"tags":"加上已有的稍后读标签"}`。调用者从可信请求填写，只允许覆盖笔记默认属性；不绕过白名单、权限、枚举和层级规则。它本身不是授权证明。

新建笔记符合决策默认值；更新可保留既有用户属性，新增／改变的非默认属性才需要明确指令。NOTE 原生检查项即使有 explicit_fields 也不接受，应使用正文列表或经用户意图支持的 CHECKLIST。

`snapshot.tags=null` 表示读取失败，`[]` 表示读取成功但无标签。更新任务与完整祖先放入 `snapshot.tasks`。`closed` 只接受 bool 或 null；明确 read/comment 拒绝，null 留给执行端核验。

退出码 0 且 `ok=true` 才提交。脚本检查类型、位置、标签、日期、父子图和笔记不变量；提醒与重复协议、OCR、所有平台限制及用户语义仍由模型和接口核验。

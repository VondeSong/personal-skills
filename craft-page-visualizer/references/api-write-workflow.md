# Craft Whiteboard 稳定写入

仅在需要通过 Craft Connect API 创建、追加或更新白板时读取本文件。

## 分层

把流程分成三层，禁止边生成节点边调用 API：

1. **知识层**：页面内容 → `Diagram { nodes, edges }`
2. **渲染层**：`Diagram` → 完整 `elements[]`。卡片型白板优先使用 `scripts/craft_whiteboard_design.mjs`，并在提交前运行 `audit()`。
3. **提交层**：预检 → 写入 → 回读 → 修正

渲染层先完成全部 ID、坐标、尺寸和样式。只有预检通过后，提交层才能创建白板。

`craft_whiteboard_design.mjs` 的 `audit()` 负责卡片重叠、文字截断、字体和语义色等视觉检查；本文件的稳定写入器负责 schema、ID、index、批量和 API 回读。两者职责不同，不能用写入成功替代视觉验收。

## 精确定位与防重复

1. `GET /connection`，确认 Space 名称与用户目标一致。
2. `GET /documents/search?include=...`。搜索结果里的 `documentId` 可能只是包含目标子页的根文档；不要直接当作 `pageId`。
3. 对候选 `blockIds` 调 `GET /blocks?id={id}&maxDepth=-1`，以 `type=page`、完整标题与实际内容确定目标页。
4. 写入前再次读取目标页，记录现有 `type=whiteboard` 的 block ID。
5. 页面已有白板且用户未明确新建或更新时停止并确认；禁止因为一次网络失败再次创建白板。

## 元素构造

- ID 使用 `viz-{runId}-{role}-{key}`，同一白板全局唯一。
- 箭头放在形状之后会遮挡节点。提交前按层级重排：frame/background → arrow/line → shape → text。
- 新元素不要手写随意的 `index`。本 API 当前使用的顺序为 `a0…a9, aa, aA, ab, aB … aZ, b00…`。优先交给 `scripts/craft_whiteboard_write.mjs` 统一生成；更新已有元素时默认保留原 index。
- 一个节点的矩形与文本可以分离，但文本必须最后置顶；`text` 与 `originalText` 应一致。
- 写入前检查：ID 唯一、所有坐标有限、宽高非负、箭头至少两个 points、节点无明显重叠、文字高度足够。
- 卡片型元素先按 `references/card-design-system.md` 构造；不要在任务中反复临时定义颜色、字号、内边距和中文换行算法。
- API 是实验性的。若当前读取到的元素 schema 与示例不同，以实际 GET 响应为准，调整渲染层，不要把未知字段硬写入。

## 推荐写入器

脚本位置：`scripts/craft_whiteboard_write.mjs`。它负责：

- 连接与目标页预检
- 已有白板防重复
- 稳定 z-order 与 Excalidraw index
- 每批最多 400 个元素，同时把 JSON 请求体控制在约 64 KiB；以先达到的限制为准
- 失败后只对缺失 ID 重试一次
- 回读校验 ID、更新字段、边界和页面挂载位置
- 失败时保留并报告已创建的 `whiteboardBlockId`，防止重复创建

将 API URL 放在环境变量中，不要写入脚本、元素 JSON 或日志：

```powershell
$env:CRAFT_API_URL='https://connect.craft.do/links/{connectionId}/api/v1'
node scripts/craft_whiteboard_write.mjs `
  --operation create `
  --page-id '{pageId}' `
  --elements 'C:\path\elements.json' `
  --position end
```

若页面已有白板而用户明确要求再新建一张，增加 `--allow-existing true`。不要把它作为默认参数。

富样式卡片的单个 element 字段较多，即使不足 400 个也可能超过 Craft 的请求体限制。稳定写入器会同时按元素数量和序列化后的字节数分批；不要仅按 element 数量估算请求大小。

追加到已有白板：

```powershell
node scripts/craft_whiteboard_write.mjs `
  --operation append `
  --whiteboard-id '{whiteboardBlockId}' `
  --elements 'C:\path\new-elements.json'
```

更新已有元素：

```powershell
node scripts/craft_whiteboard_write.mjs `
  --operation update `
  --whiteboard-id '{whiteboardBlockId}' `
  --elements 'C:\path\changed-elements.json' `
  --normalize-indexes false
```

`update` 输入只放需要修改的元素和字段，并带已有 `id`。若需新增元素，改用 `append`。删除仍按主技能的保护规则单独处理，不纳入自动恢复脚本。

生成元素后可先做完全离线的预检，不连接 Craft：

```powershell
node scripts/craft_whiteboard_write.mjs `
  --operation create `
  --page-id '{pageId}' `
  --elements 'C:\path\elements.json' `
  --dry-run true
```

## 写后验收

成功至少满足：

- 创建响应有 `whiteboardBlockId`
- 回读后所有提交 ID 存在
- update 的所有提交字段与回读一致
- 坐标边界合理，无 NaN / Infinity
- create 后目标页的一级内容能找到该 whiteboard block
- 页面正文未被修改

失败时只恢复同一个 `whiteboardBlockId`。除非确认原白板未创建，禁止用“再 POST /whiteboards 一次”作为重试。

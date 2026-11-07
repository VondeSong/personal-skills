# 黄金场景评测

这组用例检查技能决策，不调用真实滴答，不替代真实协议联调。代码测试与模型行为评测分别记录：测试脚本全通过，也不代表模型已通过这些场景。

## 运行方式

1. 从 [cases.json](cases.json) 取单个 `prompt`、`context`，提供技能入口和按需参考。所有快照、ID 和响应都为离线模拟；禁止真实网络写入。
2. 让被测模型按模拟工具事实执行，记录调用轨迹及最终结果。不要向被测模型展示 [expectations.json](expectations.json)、已有评分或预期答案。可使用独立会话；需要代理时遵守当前授权。
3. 审阅实际调用和产物，将观察结果记入下述响应结构。判定应来自轨迹，不把模型自称“已回读”当作证据。
4. 运行 `python scripts/score_scenarios.py responses.json`。此脚本只核对已观察的结构化结果，不调用模型，也不替代内容质量评审。缺例、重复例、未核对的字段都计失败。

```json
{
  "evaluationType": "isolated_model_replay",
  "results": [{"caseId": "01-photo", "observed": {
    "taskClass": "reference", "nativeKind": "NOTE", "destination": "inbox",
    "created": 1, "tagWrites": 0, "dateWrites": 0,
    "preflightBeforeCreate": true, "originalAttachmentVerified": true
  }, "traceEvidence": ["模拟调用轨迹中的实际记录或文件路径"]}]
}
```

`observed` 只需包含该例评分字段，可额外记录实际结果。`created` 是模拟新建数，`tagWrites/dateWrites` 是新增或修改属性次数；`destination` 的 inbox/existing/appropriate 表示语义归位，不是真实 ID。`traceEvidence` 是可复核的外显执行证据，不要求或保存隐藏推理。

## 评分与覆盖

每例全部核心约束满足才通过；整体满分为全部用例通过。额外人工检查原文与附件无损、任务标题和完成条件可用、第三方指令未被执行。规则有意允许多种合适标题或行动清单，因此不比较固定文案。

用例包含用户指出的八类场景，并扩展日期材料、第三方承诺、Hub 只出方案、未知结果、类型回读失败和协议变化。`expectations.json` 的预期是评分基准，不能当成本次实际运行结果。

此次包修订提供可复用的案例和评分器；真实服务联调、独立模型回放结果须由之后的实际运行另存。运行记录建议放任务临时目录，不混入技能规则。

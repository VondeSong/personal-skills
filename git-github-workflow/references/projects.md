# 开发总看板接入

新建 GitHub 仓库时默认执行；用户明确要求为既有仓库补建或关联时也执行。本技能更新本身不创建真实看板，不批量改造已有仓库。

## 查找与复用

1. 读取当前项目 `AGENTS.md` 中的看板链接、owner、字段映射、事项分类及权限约定，再检查仓库已关联的 Projects 和已知候选看板。已存在明确的项目总看板时直接复用，不因名称不符合新默认值而重建。
2. 检索须基于目标仓库的 owner 和真实关联。新仓库已由某个跨仓库总看板覆盖时，按既有约定关联和复用，不强制每个仓库另建一块。同名且关联不明的候选不能随便选，先查明；无法确定唯一目标时仅澄清这一点。
3. GitHub Projects 属于个人账号或组织，与仓库的创建、可见性及权限分别管理；仓库的 Projects 功能开关不表示看板已创建或已关联。使用可用连接器、已认证 CLI 或官方 GraphQL 能力验证，不以能够写 Issue 推断能够管理 Projects。

## 没有可复用看板时

- 在目标仓库的同一 owner 下创建 `<项目名> 开发总看板`，默认私有，关联仓库；项目另有明确名称或可见性约定时沿用。需要设置默认仓库时核对为本仓库，不能改动已有跨仓库看板的默认仓库。
- 新看板默认使用“待处理、处理中、待验证、已完成”四种任务状态和按状态分组的开发视图。实现视图所需的工具能力不可用时如实记录缺少的界面配置，不把仅有 project 对象当成全部完成。
- 既有看板沿用真实字段、选项、模块、视图和内建自动化；用语义映射识别 Todo/In Progress 等状态，不擅自重命名或重置选项、批量改动条目。新看板核对关闭/合并与 Done 的内建规则，避免在必要验收未完成时因状态或 PR 合并而误关闭 Issue。
- 默认采用 Hub 的收录粒度：重要功能、规划和阶段目标进入总看板，普通小 Bug、文案和局部调整留在 Issues。已有项目采用其他分类时保留。不要默认导入全部历史 Issues、启用无过滤的 auto-add 或将普通修复全部加入看板。
- 将看板链接、owner/标识、仓库关联、状态含义和事项分类写入本项目 `AGENTS.md`；记录“明确交办任务后更新进度”的授权范围，保留该项目已有更具体约定。只记录用户已选择的默认工作流，不增加自动挑选待办或发布权限。

## 核验与部分失败

回读确认看板身份、真实仓库关联、可见性、状态和项目文档记录；返回实际看板链接。已有跨仓库关联须保持原状。权限或工具不足时继续独立的仓库检查/初始化，明确分别报告“仓库已接入、看板尚未完成”等状态，保留创建成功的看板标识以供恢复；先回读再重试，不因关联失败反复创建。

官方依据：[创建 Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/creating-projects/creating-a-project)、[关联仓库](https://docs.github.com/en/issues/planning-and-tracking-with-projects/managing-your-project/adding-your-project-to-a-repository)、[内建自动化](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations)。

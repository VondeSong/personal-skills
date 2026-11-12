# 移动端的苹果式精致与跨平台适配：专项初步方案

**状态：文档调研与候选方案，尚未实施、实机验证或升级为正式规范。**

**整理与来源核验日期：2026-11-12（北京时间）。**

本文补充[跨平台风格初步分析](cross-platform-apple-style-initial-analysis.md)，回答“移动端是否已经考虑，下一步应如何具体设计”。研究覆盖 iPhone／iPad、原生 Android、移动 Web／PWA，以及 Craft、Codex、Claude Code 的移动使用模式。平台可用性按本次官方文档记录，实施时仍需核对客户端、系统、浏览器、账户及发布范围。

适用前提沿用 [SKILL.md](../SKILL.md)：Apple 平台或明确要求 Apple 启发的跨平台设计研究。Android 内容用于比较与适配，不扩大技能的自动触发范围。现行版本保持 3.1，规则强度、Token 合约和已有产品结构不因本分析改变。

**证据分为三类：**“官方事实”指来源明确描述的能力或规范；“设计解释”指根据这些事实形成的判断；“候选方案”指有待结合实际项目与使用情境验证的方向。本文没有进行三个产品的完整体验审计，也没有证明 Hub 已具备下述功能。

## 目录

- [1. 现有覆盖与此次补充](#1-现有覆盖与此次补充)
- [2. 产品证据与设计解释](#2-产品证据与设计解释)
- [3. 手机端的一致与适配](#3-手机端的一致与适配)
- [4. 导航、返回与窗口变化](#4-导航返回与窗口变化)
- [5. 触控、中文排版与操作可达性](#5-触控中文排版与操作可达性)
- [6. 键盘与编辑状态](#6-键盘与编辑状态)
- [7. 中断、离线与真实任务状态](#7-中断离线与真实任务状态)
- [8. 材质、动效与性能](#8-材质动效与性能)
- [9. 三个端到端场景及 Hub 映射](#9-三个端到端场景及-hub-映射)
- [10. 后续验证与方案优先级](#10-后续验证与方案优先级)
- [11. 一手来源与维护说明](#11-一手来源与维护说明)

## 1. 现有覆盖与此次补充

**结论：已有移动端基础指南，上一版风格分析只展开到原则层面；完整的手机任务流程、Android／Web 差异和中断恢复仍需专项方案。**

| 维度 | 已有材料 | 此次补充 |
| --- | --- | --- |
| iPhone／iPad | [平台指南](ios-ipados.md)已有导航栈、安全区域、键盘避让、动态字体、触控与窗口适配 | 把这些要求放进实际任务过程，明确进入、返回、继续和退出 |
| 跨平台风格 | 初步分析区分视觉秩序、品牌、任务与系统惯例 | 明确原生 iOS、原生 Android、移动 Web 的适配边界 |
| AI 工作流 | [AI workflows](ai-workflows.md)区分建议、执行、进度、取消和失败 | 增加手机连接、执行主机、页面生命周期与任务状态的分离 |
| 阅读与排版 | [中文排版](chinese-typography.md)和[验收指南](acceptance.md)覆盖可读性及文本变化 | 增加中文输入法、多行输入、长标题、触屏选择及窄窗口阅读 |
| 验证 | 已要求按实际变更验收 | 给出可复现的手机场景与平台差异检查，不把文档检查当作设备验收 |

设计解释：手机的精致感包含可读、易点、及时反馈和随时继续。外观保持统一只是其中一部分；输入、导航和恢复是否可靠，会直接影响用户对界面完成度的判断。

## 2. 产品证据与设计解释

### 2.1 Craft：围绕触摸、快速捕捉与当前对象安排入口

**官方事实：** 当前 Platforms 文档列出 Android 的底部导航、触摸编辑、图片与附件面板、文档内搜索和 Craft Assistant。3.7.0 更新另行说明了 iPhone Quick Entry“添加到文档”、iPhone／iPad 选中任务后的底部“打开”操作，以及用于行内链接、公式的多行编辑面板。后者是明确标注平台的更新，不能扩展为 Android 具有相同界面。[^craft-platforms][^craft-370]

**设计解释：** 手机入口围绕“立即记录”“选中后处理”“就地完成一个编辑任务”组织，减少开始前的设置负担。跨平台共享内容对象及动作含义，具体呈现可以不同。底部选择工具栏已有官方例证；“所有平台都把工具栏放在键盘上方”没有在本次资料中获得充分确认。

**官方事实：** Craft 的离线范围存在平台差异。Working Offline 专页说明，Web／Windows／Android 可以离线读写此前在线打开并缓存的文档；创建文档、搜索、上传等仍需网络。网络恢复后，仍打开的文档立即同步；此前离线编辑后关闭的文档，要重新打开才同步。默认开启离线模式时，未同步修改可在关闭 Craft 后保留。[^craft-offline]

**设计解释：**“已在本机保存”“等待同步”“已同步”表达不同的结果。方案不能以一个统一的成功提示掩盖这些差异，也不能把 iOS 的离线范围自动套给 Android。

### 2.2 Codex：手机承担发起、指导、审批与审阅

**官方事实：** Codex on mobile 文档描述了选择云环境或连接电脑、发起任务、查看进度、补充指令、处理审批以及审阅文件改动、diff 和测试结果的流程。Remote connections 当前文档明确包含 iOS 或 Android 控制 Mac／Windows 主机，同时说明发布范围可能不同。主机需要保持清醒、联网并运行 ChatGPT 桌面应用；手机与主机使用同一账户和工作区，工作区还可能需要管理员启用远程访问。[^codex-mobile][^codex-remote]

**设计解释：** 手机应突出当前进展、需要用户决定的事项和可检查的结果；复杂执行环境可以渐进展开。共享的是任务上下文与结果，桌面完整工具面板是否适合手机，需要另行设计。当前文档包含 Android 入口，不等于所有 Android 用户已获得与 iOS 完全相同的功能。

### 2.3 Claude Code：手机入口与执行位置分开

**官方事实：** Claude Code 的 Mobile 文档说明，Claude iOS／Android App 是 Code 会话客户端，代码运行在云端或连接的电脑。Cloud sessions 与 Remote Control 位于 Code 标签；普通聊天不能自动当作 Code 会话。云会话可在收起手机后继续，Remote Control／Dispatch 则依赖自己的电脑保持运行。Code 标签及相关能力还取决于订阅方案和组织设置。[^claude-mobile]

**设计解释：** 远程任务可以在手机离开前台后继续，是执行环境和同步机制提供的能力。界面应说明任务在哪里运行、何时需要用户回应，以及当前状态是否仍可确认。动画本身不能证明后台执行。

## 3. 手机端的一致与适配

以下为候选设计框架，不是三家产品共同使用的内部架构。

| 保持的关系 | 可以随设备变化的表达 | 需要分别验证的行为 |
| --- | --- | --- |
| 对象、标题层级、品牌色角色、状态含义 | 字号、间距、密度、工具位置、单栏或多栏 | 大字号、长中文、触控命中和读屏顺序 |
| 项目、内容、任务、证据之间的关联 | 桌面并列查看，手机逐层进入 | 返回位置、选中项和筛选条件是否保留 |
| 发起、继续指导、处理决定、查看结果 | 手机优先呈现与当前阶段相关的信息 | 通知进入、重连、任务状态核对和重复提交 |
| 能发现、能完成、能撤回或恢复的操作逻辑 | 系统菜单、导航容器、分享与键盘入口 | iOS、Android、浏览器各自的系统行为 |

“苹果式精致”可以体现在清楚的关系、文字与图标的细节、稳定反馈以及操作连续性。品牌的可识别性由内容与视觉语言共同维持；系统习惯由各平台承接。不能仅因圆角、浅色或玻璃相似，就推断产品共享技术框架或证明体验相同。

## 4. 导航、返回与窗口变化

### 4.1 先区分目的地、局部切换与动作

**官方事实：** Apple 的 tab bar 指南把它用于顶层区域导航；对当前对象执行动作，应使用适当的工具入口。Android 的自适应导航也围绕同一组目的地，在紧凑窗口和较宽窗口采用不同容器。[^apple-tabs][^android-navigation]

**候选方案：** 保留项目已有的信息架构，按真实高频任务决定主要入口。全局目的地、当前列表筛选、对象操作需要可区分；不将“新建”“删除”“开始任务”混入目的地的选中状态。底栏适合部分手机结构，但不规定所有产品必须有底栏、固定数量的标签或相同的主按钮位置。

### 4.2 页面、面板与返回各自有清楚职责

**官方事实：** Apple 将 sheet 用于与当前上下文相关的有界任务，也提供非模态用法；复杂或持续较久的流程可以采用完整页面等替代形式，避免连续叠加 sheet 导致返回关系不清。Android Predictive Back 支持预览返回目的地，自定义处理需使用受支持的系统／AndroidX API，并正确处理手势取消。[^apple-sheets][^android-back]

**候选方案：** 选一个标签、修改一个属性或短暂预览可以评估面板；持续阅读、多步编辑和完整审阅应有足够空间。关闭面板、返回上一页、停止任务分别表达。退出任务详情不默认等于取消远端任务。

原生 Apple 界面保留导航返回和标准手势；原生 Android 验证系统返回、预测返回完成及取消；移动网页处理自身路由、浏览器历史和深链接。原生返回 API 不直接成为所有浏览器的共同能力。键盘打开时的返回行为也需检查，避免一次操作意外丢失编辑内容或连续退出多个层级。

### 4.3 依据可用窗口调整，保留用户上下文

**官方事实：** Android 的窗口分类依据当前可用空间，运行中会随方向、分屏和折叠状态变化；设备类型不保证固定窗口尺寸。[^android-window]

**候选方案：** 手机通常按“列表—详情—证据”逐层进入；空间足够时可并列呈现相关内容。决策同时考虑宽度、高度和任务需要，不能只按手机／平板标签判断。Android 的 dp 断点也不应直接复制为 Web 的 CSS px 断点。

栏数变化时保留当前对象、选中项、筛选、草稿及可恢复的阅读位置；多栏收为单栏后应让人知道当前处于哪一层。横屏手机虽然变宽，可用高度可能仍不适合完整多栏。这里给出的是适配目标，尚未验证 Hub 当前实现。

## 5. 触控、中文排版与操作可达性

### 5.1 区分图标外观、点击区域与规范单位

| 平台 | 官方依据 | 本轮候选处理 |
| --- | --- | --- |
| iOS／iPadOS | Apple Accessibility 表列默认控件尺寸 44 × 44 pt、最小尺寸 28 × 28 pt；Buttons 另建议一般按钮命中区域至少 44 × 44 pt | 普通常用按钮优先采用舒适的标准命中区域；不能把 28 pt 当作普遍目标，也不能把 44 pt 误写为所有控件唯一的表列最小值 |
| 原生 Android | 官方建议可交互目标至少 48 × 48 dp | 区分视觉图标与触控区域，核对相邻动作间距 |
| Web | WCAG 2.2 SC 2.5.8 AA 为 24 × 24 CSS px，存在间距、等价控件、行内等例外；SC 2.5.5 AAA 增强级要求至少 44 × 44 CSS px，也有等价控件、行内、用户代理控件及必要呈现等例外 | 24 CSS px 不代表手机舒适标准；常用按钮可将约 44 CSS px 或更大的命中区域作为候选起点，再按组件及实际触控验证 |

以上单位与适用标准分别来自官方材料，不能写成 pt、dp、CSS px 或截图像素一一相等。[^apple-accessibility][^apple-buttons][^android-accessibility][^wcag-target]

扩大命中区域时检查重叠；图标可以精细，但动作不能难点。高频操作评估单手可达性，结合左右手、设备大小和当前输入位置选择入口，不据此将所有工具强制搬到底部。

### 5.2 手势提高效率，关键动作仍可发现

候选方案：触屏不依赖悬停；对重要的更多、编辑、复制或选择功能保留可见入口。滑动、长按、拖动可作为捷径，同时提供符合任务的替代方式。例如排序可提供“上移／下移”或位置选择。Web 的拖动操作还应按 WCAG 2.2 SC 2.5.7 核对无需拖动的单指针替代及其例外；这是 Web 标准，原生平台按各自规范处理。[^wcag-drag]

### 5.3 中文可读性与信息密度一起调整

**官方事实：** Apple Typography 强调可读字号、文本样式和用户调整文字大小后仍然清楚的层级，不能用过细字重损害可读性。[^apple-typography]

**候选方案：** 原生使用语义文本样式及平台字号缩放；Web 使用可重排布局并验证文本放大。中文长标题、中文与英文混排、文件路径和代码分别处理；不为维持卡片等高而截掉决定性信息。正文行距、按钮标签和提示文字按实际字体检查，数字、状态与对象名称不应全部弱化成小号浅灰字。

读长文时保持稳定阅读面；列表扫描时允许合理密度；查看 diff 或比较数据时提供适合任务的展开方式。不能把手机质感简化为加大留白或降低信息量。具体排版仍沿用[中文排版指南](chinese-typography.md)，本方案不引入新的一组固定字号 Token。

## 6. 键盘与编辑状态

**官方事实：** Apple 提供虚拟键盘及相关布局指导；Android 的 `WindowInsets` 分别描述系统栏、手势区域与 IME 等占用空间。移动 Web 的 layout viewport 与 visual viewport 可能因软键盘、缩放等出现不同变化，不能将固定底部位置视为已经解决遮挡。[^apple-keyboard][^android-insets][^web-viewport]

**候选方案：** 输入流程至少检查未聚焦、中文组合输入、普通输入、多行展开、提交中与提交失败。光标、输入内容及当前必须操作的按钮在键盘出现后仍需可见、可达；键盘收起后保持合理位置。输入区与阅读区的滚动关系要清楚，避免出现互相争夺滚动的多层小容器。

| 实现环境 | 处理方向 | 不能由静态设计稿证明的内容 |
| --- | --- | --- |
| 原生 iOS／iPadOS | 使用当前框架的安全区域及键盘布局能力；包含浮动／外接键盘等实际支持场景 | 键盘动画、选择菜单、输入焦点及窗口变化时的遮挡 |
| 原生 Android | 依据系统栏与 IME 的实际 Insets 布局，处理边到边显示 | 导航模式、键盘高度、横屏与系统返回的组合行为 |
| 移动 Web／PWA | 优先保留浏览器正常的焦点和滚动行为，必要时按可见视口增强 | Safari iOS、Chrome Android、独立窗口模式的差异 |

中文输入法选择候选词时，回车不能误触发送；多行换行、发送、提交快捷键需要明确且不干扰组合输入。失败时保留可恢复的输入与附件状态，不能让用户重新键入整段内容。这些是本方案提出的验收场景，并非已证实三个产品均通过。

Web 的 `100vh`、动态视口单位或 `position: fixed` 都不能单独证明键盘适配已完成；视口缩小也不一定表示键盘出现。VirtualKeyboard API 当前存在支持范围限制，接管覆盖行为后还需自行处理避让，只能在能力检测与可工作的默认路径之上渐进增强。[^web-keyboard]

## 7. 中断、离线与真实任务状态

### 7.1 界面生命周期与执行环境分别建模

**官方事实：** Chrome 生命周期文档说明页面可能被冻结或丢弃，移动端不能依靠离开页面时的结束事件才保存。Android 也区分配置变化、进程回收和用户主动关闭，并给出界面状态与持久数据的不同保存方式。[^page-lifecycle][^android-state]

**候选方案：** 草稿随编辑过程保存，在适当生命周期节点补充保存；回到前台或重新载入后恢复上下文，并向实际执行端核对状态。不要将内存、当前页面或界面状态快照当作完整持久存储。原生的状态保存和浏览器的生命周期 API 分别实现，不承诺所有平台具备相同事件。

### 7.2 四种状态不能挤进一个“保存／运行中”标志

| 状态维度 | 候选状态或提示 | 依据与边界 |
| --- | --- | --- |
| 本地内容 | 草稿、已在本机保存、等待同步、同步冲突 | 持久化成功后才说本机已保存；本机保存不等于远端已有副本 |
| 提交请求 | 未提交、提交中、已确认接收、明确失败、结果待确认 | 请求超时可能留下未知结果，不能直接断言从未送达 |
| 连接与执行位置 | 手机连接正常／中断／重连中，云端或指定主机，最后确认时间 | 手机有网络、业务服务可达、执行主机在线分别判断 |
| 任务本身 | 排队、运行、等待用户、完成、失败、取消请求中、已确认取消 | 以实际执行端可确认的状态为依据；断开页面不等于取消任务 |

这是一组用于方案设计的维度，不要求每个产品把全部状态同时显示，也不证明现有后台已实现这些机制。界面优先解释用户当前需要理解的差异，技术细节按需展开。

**官方事实：** `navigator.onLine` 依据浏览器／系统的启发式判断，不能可靠证明业务服务可用。[^web-online]

**候选方案：** 连接中断时可显示“连接中断，正在确认任务状态”及最后更新时间；若保留旧状态，明确它是最后确认的状态。不要直接报任务失败，也不要无依据地继续断言任务仍在运行。网络恢复后先核对提交和任务结果，再决定重试。

对可能产生副作用的动作，评估请求标识、幂等提交和结果核对，防止连点或重试造成重复执行；这是工程候选方案，不能由网络提示 API 自动保证。取消请求已发出、执行端已停止、之前修改是否撤回也分别表述，沿用 [AI workflows](ai-workflows.md) 对取消与回滚的区分。

### 7.3 分别说明离线阅读、编辑、新建与同步

候选方案：列出实际可离线使用的内容与动作，说明缓存范围、待同步状态、冲突处理及不可用原因。已缓存阅读、离线编辑、离线新建、离线附件和恢复后同步是不同能力。Craft 的平台差异提供了具体例证，但不构成 Hub 已有同等能力的证明。[^craft-offline]

若后续项目需要“锁屏后继续执行”“跨设备继续”“完成后通知”，先确认执行环境、持久状态、通知及重新进入机制。通知进入时定位到相关对象，并刷新状态；通知内容可能已经过时。通知许可被拒绝或不支持时，仍应有可访问的任务列表与结果入口。这些均为候选行为，实施后才能作能力承诺。

## 8. 材质、动效与性能

**官方事实：** Apple Materials 将 Liquid Glass 主要用于导航和控制层，内容层使用普通表面或标准材质，并要求自定义效果克制使用。系统外观还会响应减少透明度、增强对比度等设置。[^apple-materials]

**候选方案：** 导航或浮动工具可以通过轻材质解释层级，正文、代码、长时间阅读区域优先保持稳定可读。Apple 原生优先使用当前系统支持的组件；Android 沿用其平台组件及项目设计系统；Web 的透明与模糊效果只是视觉近似，不能声称等同原生 Liquid Glass。

验证滚动背景变化、输入时工具层、浅深主题和高对比状态。减少动态时仍能理解状态变化；不支持相应偏好能力的环境应保留可读的实色和低动效路径。不能假定所有 Android 或 Web 环境都有与 iOS 同名、同效的透明度设置。

手机上的材质与动效需要结合目标设备、长列表和真实内容检查响应及滚动表现。此阶段没有帧率、耗电或低端设备测量，不写“稳定 60 fps”或“无性能影响”。先验证功能与可读性，再判断效果是否值得保留；不设统一玻璃面积或动画数量配额。

## 9. 三个端到端场景及 Hub 映射

以下为候选方案。它们用于发现流程断点，不表示改变现有 Hub 导航或自动启动开发。

### 9.1 随手记录与轻编辑

从现有的新建入口或受支持的系统分享入口进入，立即表达内容；当前保存目的地可见且可轻量更换。标签、额外属性与格式工具按需要展开。浏览、选择、编辑三个状态分别提供相应操作，避免为记录一句话先完成大量设置。

键盘旁的上下文工具可以比较不同放置方案，具体位置由输入法、可用空间及平台验证决定。返回时保留应保存的草稿，并准确说明本机保存与同步结果。

验证任务：中文输入到一半切换应用，返回继续编辑；附件上传失败后重试；键盘展开时更换目的地；网络中断时查看内容是否真正保存。

### 9.2 阅读、洞察与证据审阅

从列表进入内容，先明确对象、摘要或变化，再进入来源、长正文、文件或 diff。必要信息不能只存在于悬停中；来源与判断建立可追溯关系。返回后恢复列表筛选和合理阅读位置，深链接进入时也有清楚的上层入口。

对 Hub 的洞察，沿用既有“有依据的发现及可追溯判断”职责。桌面可以并列查看结论与来源，手机逐层展开；不因适配而建立重复知识库或任务器。需要比较的内容可评估固定摘要、分段切换或专用比较页，不能仅把桌面双栏等比例缩小。

验证任务：从一个判断进入多条来源，再回到原位置；放大文字后仍能找到来源和动作；横竖屏切换不丢失正在查看的对象。

### 9.3 离开电脑后监督 Agent

任务列表清楚区分正在运行、等待处理、已完成与失败；详情解释执行位置、当前阶段及可确认的新结果。优先让用户发现需要自己决定的事项，再按需展开日志、文件和执行信息。是否可以置顶某类任务，依据真实频率与重要性判断。

需要审批时，展示对象、动作范围、影响和可选决定；手机屏幕小不能成为隐藏关键信息或自动批准的理由。查看结果时将摘要与必要证据相连。中途离开详情与明确停止任务使用不同动作；停止后继续如实显示已发生的修改和未完成部分。

验证任务：发起后锁屏、手机断网而主机在线、主机休眠、重连后收到已经完成的任务、返回前曾有待处理决定、提交超时后再次进入。只有相应执行与同步机制经过验证，才承诺这些情况下的连续性。

| 既有工作区域 | 手机候选重点 | 与桌面共享的内容 |
| --- | --- | --- |
| 内容、日志、阅读 | 快速进入、完整阅读、轻编辑和位置恢复 | 对象、内容关系及保存语义 |
| 洞察 | 判断与来源逐层关联，必要时进入比较视图 | 证据、判断及追溯关系 |
| 任务与 Agents | 待处理决定、真实进度、结果及恢复入口 | 任务标识、执行上下文、变更和结果 |

## 10. 后续验证与方案优先级

### 10.1 优先验证顺序

1. **任务与状态：** 用三个场景画出实际流程，确认进入、返回、保存、提交与恢复的含义；盘点客户端及后端已有能力。
2. **平台与输入：** 在项目实际支持的平台验证返回、键盘、触控、字号放大和窗口变化，修正流程断点。
3. **视觉与细节：** 沿用现有 Token 检查文字、密度、选中、反馈及材质，按真实内容比较方案。

以上是后续实施的候选顺序，不代表本次已开展开发，也不是要求用户分阶段审批。本次交付为完整的初步调研方案。

### 10.2 与变更相关的验收矩阵

| 维度 | 候选检查条件 | 可观察的判断依据 |
| --- | --- | --- |
| 平台 | 支持范围内的 iOS／iPadOS、Android；若是 Web，则覆盖 Safari iOS、Chrome Android 和实际支持的 PWA 模式 | 返回、系统操作、路由及深链接符合相应环境 |
| 窗口 | 窄手机、较大手机、横屏；涉及平板／折叠屏时加入分屏与展开收起 | 必要内容可用，栏数变化保留当前对象和草稿 |
| 输入 | 中文组合输入、多行文本、软键盘、项目支持的外接键盘 | 不误发、不遮挡、不丢输入；关键动作可达 |
| 生命周期 | 切应用、锁屏、重新载入或系统回收后的恢复 | 取回可持久保存的内容，重新核对任务状态 |
| 网络与执行 | 弱网、手机离线、服务不可达、主机离线、提交结果未知 | 连接与任务状态不混淆，不无依据重复提交 |
| 可访问性 | 文字放大、VoiceOver／TalkBack 或目标 Web 读屏、减少动态、适用的对比度／透明度设置 | 名称、顺序、状态与操作可理解；视觉变化不隐藏必要信息 |
| 显示与表现 | 浅深主题、变化背景、长列表、真实中文与附件内容 | 文本和动作可辨认，滚动与输入响应满足项目实际目标 |

按本次实现改动选择相关项，不要求一次文案调整覆盖整张矩阵。报告需要区分官方文档核对、静态设计检查、实际交互测试和设备测量。仅检查 Markdown、运行技能校验或看到一张截图，均不能写成移动端兼容性或无障碍已通过。

### 10.3 尚未验证与后续升级条件

本轮未检查 Hub 的实现代码、实际导航、任务后端、同步策略或目标设备表现；三家产品的资料也不等于所有版本均表现一致。官方事实与候选建议的区别必须保留。

后续若将某项候选建议提升为正式 Skill 规则，需要补充具体问题、适用平台、已有约束、方案比较及验证结果，再修改相应平台或验收参考文件。品牌感、苹果辨识度和实际可用性分别评价，不以相似外观代替任务验证。

## 11. 一手来源与维护说明

本轮引用厂商、平台维护者或标准组织的公开材料。除特别标注的发布说明外，均按 2026-11-12 可访问版本核对；动态文档可能继续更新。技能中的经验建议不自动成为厂商规范。

来源冲突处理：Craft Platforms 概览仍写 Web／Windows／Android 离线需一次设置，Working Offline 专页已写默认开启。本分析对离线行为以更具体的专页为主要依据，保留平台与条件限制。Codex 的远程连接文档含 Android，而部分入门步骤仍以 iOS 举例；本分析记录支持描述及发布条件，不据此承诺功能完全一致。

[^craft-platforms]: Craft Help Center, [Platforms and Availability](https://support.craft.do/en/introduction/platforms)，Android 入口与能力列表。
[^craft-370]: Craft, [Craft Update 3.7.0](https://www.craft.do/zh-CN/blog/craft-update-3-7-0)，2026-10-11；Quick Entry、底部选择操作与专门编辑面板，注意各条的平台范围。
[^craft-offline]: Craft Help Center, [Working Offline](https://support.craft.do/en/introduction/offline)，平台离线范围、默认设置和恢复同步的条件。
[^codex-mobile]: OpenAI, [Codex on mobile](https://learn.chatgpt.com/docs/mobile)，任务发起、指导、审批及审阅；另有可读取的 [Markdown 版本](https://learn.chatgpt.com/docs/mobile.md)。
[^codex-remote]: OpenAI, [Remote connections](https://learn.chatgpt.com/docs/remote-connections)，手机平台、主机与发布条件；另有 [Markdown 版本](https://learn.chatgpt.com/docs/remote-connections.md)。
[^claude-mobile]: Anthropic, [Claude Code on mobile](https://code.claude.com/docs/en/mobile)，客户端、云会话、Remote Control 与 Dispatch 的区别。
[^apple-tabs]: Apple HIG, [Tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars)，顶层导航、动作区分与状态保留。
[^android-navigation]: Android Developers, [Build adaptive navigation](https://developer.android.com/develop/adaptive-apps/guides/build-adaptive-navigation)，按当前窗口调整导航容器。
[^apple-sheets]: Apple HIG, [Sheets](https://developer.apple.com/design/human-interface-guidelines/sheets)，有界任务、非模态用法及复杂流程替代。
[^android-back]: Android Developers, [Add support for the predictive back gesture](https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture)，系统返回及自定义返回处理。
[^android-window]: Android Developers, [Use window size classes](https://developer.android.com/develop/ui/views/layout/use-window-size-classes)，当前可用空间与动态窗口变化。
[^apple-accessibility]: Apple HIG, [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)，控件默认／最小尺寸与可访问性设置；本轮同时核对 [Markdown 版本](https://developer.apple.com/design/human-interface-guidelines/accessibility.md)的尺寸表。
[^apple-buttons]: Apple HIG, [Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons)，按钮命中区域的一般建议。
[^android-accessibility]: Android Developers, [Make apps more accessible](https://developer.android.com/guide/topics/ui/accessibility/apps)，48 dp 触控目标建议。
[^wcag-target]: W3C WAI, [Understanding SC 2.5.8: Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum)及 [SC 2.5.5: Target Size (Enhanced)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html)，AA 与 AAA 的尺寸条件及各自例外。
[^wcag-drag]: W3C WAI, [Understanding SC 2.5.7: Dragging Movements](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements)，拖动替代及例外。
[^apple-typography]: Apple HIG, [Typography](https://developer.apple.com/design/human-interface-guidelines/typography)，可读性、文字样式与文本大小变化。
[^apple-keyboard]: Apple HIG, [Virtual keyboards](https://developer.apple.com/design/human-interface-guidelines/virtual-keyboards)，虚拟键盘与相关布局指导。
[^android-insets]: Android Developers, [About window insets](https://developer.android.com/develop/ui/compose/system/insets)，系统区域、IME 与边到边布局。
[^web-viewport]: MDN Web Docs, [VisualViewport](https://developer.mozilla.org/en-US/docs/Web/API/VisualViewport)，布局视口、可见视口及变化。
[^web-keyboard]: MDN Web Docs, [VirtualKeyboard API](https://developer.mozilla.org/en-US/docs/Web/API/VirtualKeyboard_API)，支持范围、接管覆盖行为及布局责任。
[^page-lifecycle]: Chrome for Developers, [Page Lifecycle API](https://developer.chrome.com/docs/web-platform/page-lifecycle-api)，隐藏、冻结、丢弃与保存时机；具体事件不能外推为所有浏览器均支持。
[^android-state]: Android Developers, [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states)，配置变化、进程回收与持久数据的不同处理。
[^web-online]: MDN Web Docs, [Navigator: onLine property](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/onLine)，网络提示的不可靠性及使用边界。
[^apple-materials]: Apple HIG, [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)，导航／控制与内容材质的角色及系统设置响应。

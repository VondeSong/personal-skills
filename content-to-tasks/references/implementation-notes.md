# 实现证据（维护时按需读取）

这些是本机观察，不是稳定能力要求。每次执行仍发现实时接口，不要求其他环境存在以下路径。

- 2026-10-08 核对的 Hub 根目录：`D:/03_Resources/Software/Apps/Craft/search/desktop`；源码 `src-tauri/src/lib.rs`。
- 会话边界：`dida_attachment_cookie_header`、`get_dida_attachment_session_status`。桌面读取 Hub 主 WebView／附件登录窗口的会话；移动端没有相同实现。检测到 Cookie 并不证明同账户或会话仍有效。
- 上传与身份：`dida_upload_attachment`、`random_dida_attachment_id`。此实现有 20 MiB 客户端上限；不能把它当成任何账户的实际额度。
- 映射与引用：`load_dida_attachment_mapping`、`save_dida_attachment_mapping`、`craft_content_with_dida_attachments`。
- 下载／元数据：`dida_attachment_url`、`enrich_dida_tasks_from_web_session`。下载使用 `ID.extension`，不是正文的 `ID/filename`。
- 2026-10-08 本会话也验证过官方网页原生上传：创建 NOTE、上传 PNG、任务回读取得私有附件引用，认证下载文件与原图 SHA-256 一致。会话可用性不是永久保证。
- 当时 MCP 提供任务、清单、分栏、标签能力，未提供独立附件上传工具。当前 `task` 参数为驼峰，外层可能为下划线。

本次升级把完成状态联动改为“以回读为准”，不依赖用户设置未知时的固定行为。历史官网资料可用于再次核实：[多级任务](https://help.dida365.com/articles/6950660746367729664)、[附件帮助](https://help.dida365.com/articles/6950670128287580160)。不保留已过时的数量配额表。

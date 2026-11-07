# Craft 连接与回退

只在需要核查连接或 MCP 不可用时读取回退部分。原生块格式和排版实现统一读取 [共用块格式](../../craft-general-archive/references/craft-blocks.md)；写前读取 [共用写入与恢复协议](../../craft-general-archive/references/write-protocol.md)。引用共享文件不改变当前 skill 的目的空间和授权，也不允许借用其他 skill 的凭据。

## Connection fallback

The local `../config.local.json` is optional. Only use it if it exists and has an entry for an allowed destination: Car. Never borrow credentials from another skill or fabricate a URL. If no suitable configured entry is available, report the connection limitation and retain the proposal without writing.

Load configuration without echoing values. Treat credential-bearing URLs as secrets. Call `GET /connection` before relying on a connection and require the returned `space.name` to match the intended destination. Never reuse IDs or responses from another space.

## HTTP request diagnostics

For HTTP fallback, send an explicit descriptive `User-Agent: CraftArchive/1.0` and `Accept: application/json`; the Python urllib default agent was observed to receive Cloudflare 403 / 1010 on this connection. Diagnose status together with the sanitized error body, not status alone. Do not output credential-bearing URLs.

A Cloudflare client-filter error does not establish expired credentials. An MCP 401, an app connector reporting not connected, and an API error are separate connection states: test and report each independently. For 401 or explicit permission denial, stop that connection path and use an independently configured authorized fallback if available; do not alter credentials or repeatedly retry.

For image uploads failing with `ProxyError`, `RemoteDisconnected`, or a lost response, read [上传连接恢复](../../craft-general-archive/references/upload-transport-recovery.md). Verify persistence before retrying; a successful read does not establish that the proxy can carry uploads. Use only the Car credentials configured for this skill.

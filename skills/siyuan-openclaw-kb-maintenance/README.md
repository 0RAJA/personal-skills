# 思源笔记知识库维护

## 定位

本技能推荐使用 **思源官方 CLI**，不再维护独立的命令行封装。保留的价值是：选择合适的官方接口、明确操作范围、写后读回验证，以及处理部分成功和结果不确定的情况。

## 官方入口

- [思源官方下载](https://b3log.org/siyuan/download.html)
- [官方 CLI 指南（v3.8.10，本次核验版本）](https://github.com/siyuan-note/siyuan/blob/v3.8.10/README.zh-CN.md#%EF%B8%8F-命令行接口)
- [当前官方 CLI 指南](https://github.com/siyuan-note/siyuan/blob/master/README.zh-CN.md#%EF%B8%8F-命令行接口)
- [官方 HTTP API 文档（v3.8.10）](https://github.com/siyuan-note/siyuan/blob/v3.8.10/docs/API.zh-CN.md)
- [官方 MCP 服务实现（v3.8.10）](https://github.com/siyuan-note/siyuan/blob/v3.8.10/kernel/mcp/server.go)

## 如何使用

### 本地工作空间

按官方指南安装后使用 `siyuan`；若尚未配置 PATH，可使用安装包中的 `resources/kernel/SiYuan-Kernel`，保留配套资源目录。先检查 `--version`、`--help`，再通过 `-w` 明确指定本地工作空间。

```bash
siyuan notebook list -w /absolute/path/to/workspace -f json
siyuan search "关键词" -w /absolute/path/to/workspace -f json
siyuan block kramdown --id DOCUMENT_ID -w /absolute/path/to/workspace -f json
```

示例中的路径和 ID 需替换。官方 CLI 直接访问工作空间数据，不需要启动 HTTP 服务；不要把远程 URL 当作 `-w` 路径。避免与应用/服务同时写同一工作空间。v3.8.10 CLI 不支持加密笔记本，请使用应用内专用流程。

### 运行中的或远程实例

思源 v3.8.10 的内置 MCP 入口为实例的 `/mcp`，使用 Streamable HTTP。配置鉴权后，先检查客户端能否列出所需工具；否则使用与实例版本对应的官方 HTTP API。它们不是本地 CLI 的远程模式。涉及资源文件时，区分服务端路径导入和客户端文件上传。

## 维护原则

完整操作流程见 [SKILL.md](./SKILL.md)：

1. 操作前读取对象、内容及授权范围。
2. 使用官方接口执行一次有边界的改动。
3. 优先按返回的文档或块 ID 读回；索引未就绪时，有界重试读取，不重发写入。退出码 `0` 或 API `code=0` 都不能替代读回验证。
4. 失败时区分部分成功与结果未知，保留已创建对象 ID，先查状态再重试，避免重复创建。
5. 报告已验证结果、未验证部分和清理情况，不记录凭据或无关笔记内容。

## 验证范围

上述原生命令及工作流以官方 Linux x64 v3.8.10 为核验基线。可复用官方文档与安装版本的帮助信息，不在本仓库复制官方命令实现或维护其测试替身。实际写入验证应在独立临时工作空间进行，再迁移到获授权的目标环境。

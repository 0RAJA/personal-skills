# 思源笔记知识库维护

## 概述

`siyuan-openclaw-kb-maintenance` 是一套通过 SiYuan API 进行知识库自动化维护的技能，提供脚本优先的 CLI 封装。

## 核心能力

- 笔记本与文档的完整 CRUD 工作流（创建、读取、更新、删除）
- 图片资产上传与管理
- 模板保存、检索与渲染
- Markdown 导出
- 插件/集市信息查询

## 适用场景

- 通过 API 自动化维护思源笔记的笔记本和文档
- 需要可靠的端到端 CRUD 验证流程
- 批量操作笔记库内容（创建、整理、导出）


## CLI 退出状态

- 成功或 `sync run --dry-run`：退出码 `0`，JSON 输出到 stdout。
- SiYuan 返回非零业务 `code`（即使 HTTP 状态为 200）：退出码 `1`，完整结果 JSON 输出到 stderr，stdout 为空。
- 网络、HTTP 或 JSON 解析失败：退出码 `1`，stderr 输出 `{"ok": false, "error": "..."}`。
- `doc create --title` 创建成功但重命名失败时也返回 `1`。结果保留 `create`、`rename` 和已创建文档的 `data` ID；外层 `code`/`msg` 反映重命名结果。文档可能已存在，不要直接重试整个创建操作。

退出码 `0` 仅表示 API 接受请求，写操作仍需通过读取验证实际状态变化。

## 测试

在本技能目录运行（仅使用 Python 标准库）：

```bash
python3 -m unittest discover -v
```

可选真实内核测试，需自行下载官方 SiYuan 内核：

```bash
python3 tests/e2e_siyuanctl.py --kernel /absolute/path/to/SiYuan-Kernel
```

此测试启动独立内核，使用临时 HOME 和空白工作区，不连接现有笔记库；验证创建、重命名、业务失败、部分成功、重启持久化及清理。已在官方 Linux x64 v3.8.10 验证。`--baseline /path/to/unpatched/siyuanctl.py` 可额外复现修复前的错误退出码。嵌套文档的重命名路径问题仅用于构造真实失败，本修复不修改该路径逻辑。

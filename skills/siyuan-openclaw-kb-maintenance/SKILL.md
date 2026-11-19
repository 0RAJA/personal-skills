---
name: siyuan-openclaw-kb-maintenance
description: Use when OpenClaw needs to maintain a SiYuan knowledge base with the official CLI, MCP, or documented API, especially for read-after-write verification and safe recovery from partial or uncertain results.
---

# SiYuan OpenClaw KB Maintenance

## Purpose

Use official SiYuan interfaces rather than maintaining a separate CLI implementation in this repository. This skill supplies the workflow and verification rules, not another transport or command layer.

A successful exit status or API `code=0` is not sufficient evidence that the intended state changed. Read back and compare the actual state.

## Official Entry Points

- [Download SiYuan](https://b3log.org/siyuan/download.html)
- [Official CLI guide, v3.8.10](https://github.com/siyuan-note/siyuan/blob/v3.8.10/README.zh-CN.md#%EF%B8%8F-命令行接口)
- [Current CLI guide](https://github.com/siyuan-note/siyuan/blob/master/README.zh-CN.md#%EF%B8%8F-命令行接口)
- [Documented HTTP API, v3.8.10](https://github.com/siyuan-note/siyuan/blob/v3.8.10/docs/API.zh-CN.md)
- [Official MCP server implementation, v3.8.10](https://github.com/siyuan-note/siyuan/blob/v3.8.10/kernel/mcp/server.go)

Examples below were checked against official SiYuan v3.8.10. Inspect the installed version and its `--help` before using version-dependent commands.

## Choose the Interface

### Local workspace: official CLI

The official CLI accesses workspace data directly; it does not require a running HTTP server. Use `siyuan` when the official installation has configured it, or the packaged `resources/kernel/SiYuan-Kernel` binary. Keep its packaged resources available. Do not assume `siyuan` is already on PATH.

Specify the intended workspace with `-w`. The workspace must be local to the machine executing the CLI; a remote server URL is not a workspace path. For tests, use a separate disposable workspace, never personal notes. Avoid concurrent writers to the same workspace; if the application/server is actively using it, prefer its supported remote interface or arrange a safe maintenance window.

Read-only examples (replace the workspace, keyword and document ID):

```bash
siyuan --version
siyuan --help
siyuan notebook list -w /absolute/path/to/workspace -f json
siyuan search "keyword" -w /absolute/path/to/workspace -f json
siyuan block kramdown --id DOCUMENT_ID -w /absolute/path/to/workspace -f json
```

Use the appropriate command's `--help` for document creation/rename, block updates, attributes, assets, templates, export and other operations. Prefer supported file/stdin input for long or literal Markdown. Do not rewrite literal `\n` sequences automatically. CLI access to encrypted notebooks is not supported in v3.8.10; use the dedicated in-app workflow instead.

### Running or remote instance: official MCP or documented HTTP API

For SiYuan v3.8.10, use the instance's `/mcp` endpoint over Streamable HTTP when the client supports it. Confirm the instance, authentication and allowed tools by listing the exposed tools before the first write. Otherwise use the version-matched documented HTTP API. These are separate interfaces, not flags for turning the local CLI into a remote client.

For HTTP calls, follow the official API's request/response and authentication contract; use an authorized API token from secure storage. Check both HTTP status and the API business result. Do not assume an HTTP 200 response means success. Do not assume local anonymous access will work remotely. Do not print credentials or full configuration responses.

Paths passed to a server-side local-file import refer to files on that server. They do not upload bytes from the client's filesystem. For remote assets, use an officially supported upload mechanism and verify the resulting asset reference.

## Required Maintenance Workflow

1. **Identify and read:** confirm workspace/instance, notebook/document IDs, existing content and the scope the user authorized. Capture the relevant before-state.
2. **Plan a bounded change:** specify the intended content/title/path delta. For destructive or broad changes, establish a suitable backup/recovery path and obtain any required approval. Use a command's documented dry-run mode when available, but do not treat a preview as a write.
3. **Execute once:** use the official interface and capture its result, returned IDs and errors. Keep existing document/block IDs so recovery can target the same object.
4. **Read back:** verify the precise delta with an independent read, preferably by returned document/block ID, not just the write response. A newly written object may not appear in search immediately. Retry the read within a bounded window if indexing is pending; do not repeat the write. If the read remains inconclusive, mark the outcome unverified. Check the expected result for each operation:
   - Create: the returned ID exists in the intended notebook and location.
   - Rename/move: the same ID has the requested title/location.
   - Content update: read the relevant block/body and confirm the change without unintended surrounding edits.
   - Assets/templates/export: confirm the expected reference or output artifact is accessible; a server path alone is not a downloaded file.
   - Delete: verify the authorized object is absent and unrelated objects remain.
5. **Recover carefully:** a failed follow-up step does not undo a successful create. On a timeout or lost/invalid response, the write outcome may be unknown. Inspect the existing object before retrying; never blindly rerun creation or a destructive operation.
6. **Report and clean up:** distinguish verified changes, partial success, uncertain outcomes and unrun checks. Remove only authorized test artifacts and verify cleanup.

For persistence-sensitive testing, stop/restart only the disposable test instance and read back the same IDs and content. Do not interrupt a personal running instance merely to test persistence.

## Logging and Output

Log only necessary operational metadata: interface/command or endpoint, object IDs, before/after counts or hashes, elapsed time and verification status. Avoid tokens, full configuration blobs, unnecessary note content and unbounded plugin/package responses.

Return:

1. Operation summary: expected change, observed before/after state and verified/failed/uncertain status.
2. Partial results and existing IDs needed for recovery, with the next safe step.
3. Verification limits and cleanup status.

Keep official documentation as the source of command/API details. Do not recreate a parallel command registry or compatibility wrapper in this skill.

---
name: siyuan-openclaw-kb-maintenance
description: Use when OpenClaw needs to manage a SiYuan knowledge base through API calls (create/read/update/delete notebooks or docs), especially when validating maintenance workflows, handling auth, and preventing false-success API responses.
---

# SiYuan OpenClaw KB Maintenance

## Overview

Use this skill to run safe, verifiable SiYuan CRUD operations for notebook maintenance via API.  
Core rule: treat API `code=0` as "request accepted", not "state changed".

When available, prefer calling local CLI/script wrappers over ad-hoc raw API composition in the model context.

## When to Use

- User wants OpenClaw to maintain SiYuan notes on server/local.
- Need to run end-to-end CRUD verification.
- Need reliable scripts for notebook/doc automation.
- Need to diagnose "API success but no visible change".

## Prerequisites

1. Confirm SiYuan kernel is reachable (usually `127.0.0.1:6806`).
2. Obtain API token from secure storage.
3. Always send:
   - `Content-Type: application/json`
   - `Authorization: Token <token>`
4. Prefer environment-driven config in automation:
   - `SIYUAN_BASE_URL`
   - `SIYUAN_TOKEN`
   - `SIYUAN_CONF_PATH`

## Minimal Verified CRUD Workflow

1. `POST /api/notebook/createNotebook`
   - input: `{"name":"<notebook-name>"}`
   - verify: `lsNotebooks` count/name changed
2. `POST /api/filetree/createDocWithMd`
   - input: `{"notebook":"<nbid>","path":"/","markdown":"# title\n\nbody"}`
   - verify: `listDocsByPath` contains created doc
3. Read checks (choose at least one):
   - `POST /api/filetree/listDocsByPath`
   - `POST /api/search/fullTextSearchBlock`
   - `POST /api/query/sql`
4. Content update:
   - `POST /api/block/appendBlock`
   - input: `{"parentID":"<doc-root-id>","dataType":"markdown","data":"..."}`
   - verify: query/search can read updated text
5. Optional rename:
   - `POST /api/filetree/renameDoc`
   - `POST /api/notebook/renameNotebook`
   - verify by list APIs
6. Cleanup delete:
   - `POST /api/filetree/removeDoc`
   - `POST /api/notebook/removeNotebook`
   - verify by before/after diff

## Extended Capability Workflows

### Image Asset Flow

1. Upload local asset
   - `POST /api/asset/insertLocalAssets`
   - payload: `{"assetPaths":["/abs/path.png"],"isUpload":true,"id":"<doc-root-id>"}`
2. Parse uploaded path from `data.succMap`
3. Append image markdown block explicitly
   - `POST /api/block/appendBlock`
4. Verify image presence
   - `POST /api/asset/getDocImageAssets`
   - payload: `{"id":"<doc-root-id>"}`

### Template Flow

1. Save doc as template
   - `POST /api/template/docSaveAsTemplate`
   - payload: `{"id":"<doc-root-id>","name":"<name>","overwrite":true}`
2. Locate template path
   - `POST /api/search/searchTemplate`
3. Render template
   - `POST /api/template/render`
   - payload: `{"id":"<doc-root-id>","path":"<template-path>"}`
4. Cleanup temporary template
   - `POST /api/search/removeTemplate`

### Export Flow

1. Export markdown zip
   - `POST /api/export/exportMd`
   - payload: `{"id":"<doc-root-id>"}`
2. Verify `data.zip` exists in response

### Plugin/Bazaar Read Flow

- `POST /api/bazaar/getInstalledPlugin`
- `POST /api/bazaar/getBazaarPlugin`

Payload:

- `{"frontend":"desktop","keyword":""}`

## Verification Rules (Required)

For every write endpoint:

1. Capture `before` state (count/id/name/path)
2. Execute write request
3. Capture `after` state with a read endpoint
4. Mark success only if expected state delta is present

Never mark success from `code=0` alone.

## Common Pitfalls

1. Empty payload no-op can still return `code=0`.
2. Wrong token fails explicitly; local anonymous access can be inconsistent across setups.
3. `getConf` may expose sensitive secrets; never log full response.
4. New docs may default to `未命名文档.sy`; rename explicitly if title matters.
5. Some write/delete endpoints return `data: null`; rely on state verification.
6. Plugin APIs can return very large payloads (including long README HTML strings).
7. `insertLocalAssets` uploads assets but API-only scripts should still append/verify document content explicitly.

## Safe Logging Template

Log only redacted operational metadata:

- endpoint
- operation id
- notebook/doc id
- before snapshot hash/count
- after snapshot hash/count
- latency
- result (`verified` or `unverified`)

Do not log tokens or raw full config blobs.
Do not log full plugin package bodies; keep package count and selected summary fields only.

## Output Contract

When executing this skill, return:

1. Operation table: step, endpoint, expected delta, actual delta, pass/fail
2. Pitfalls found in current environment
3. Cleanup status (whether test artifacts were removed)

## Script-First Mode

Prefer this wrapper for repeatable operations:

- `python3 scripts/siyuanctl.py ...`

Current supported command groups:

- `sync`: `info|dirs|run`
- `notebook`: `list|create|set-icon|remove`
- `doc`: `create|list|append-md|remove`
- `asset`: `upload|doc-images`
- `template`: `save|search|render|remove`
- `export`: `md`
- `bazaar`: `installed-plugins|remote-plugins` (read-only)

Use raw API calls only when CLI does not yet cover required endpoints.

#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_BASE_URL = os.getenv("SIYUAN_BASE_URL", "http://127.0.0.1:6806")
DEFAULT_CONF = os.getenv("SIYUAN_CONF_PATH", str(Path.home() / ".config/siyuan/conf/conf.json"))


class SiyuanCtlError(RuntimeError):
    pass


def load_token(token_arg: Optional[str], conf_path: str) -> str:
    if token_arg:
        return token_arg
    token_env = os.getenv("SIYUAN_TOKEN")
    if token_env:
        return token_env

    conf = Path(conf_path)
    if not conf.exists():
        raise SiyuanCtlError(
            f"token missing: pass --token or set SIYUAN_TOKEN or provide conf file at {conf_path}"
        )
    try:
        data = json.loads(conf.read_text(encoding="utf-8"))
        token = data.get("api", {}).get("token", "")
    except Exception as exc:
        raise SiyuanCtlError(f"failed to parse conf file {conf_path}: {exc}") from exc
    if not token:
        raise SiyuanCtlError(f"token missing in conf file {conf_path}")
    return token


def api_post(base_url: str, endpoint: str, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=f"{base_url}{endpoint}",
        method="POST",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise SiyuanCtlError(f"http error {exc.code} calling {endpoint}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise SiyuanCtlError(f"network error calling {endpoint}: {exc}") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SiyuanCtlError(f"invalid json from {endpoint}: {exc}") from exc


def normalize_markdown(text: str) -> str:
    # User inputs from shells/chats often carry literal '\n'.
    return text.replace("\\n", "\n")


def cmd_sync_info(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(args.base_url, "/api/sync/getSyncInfo", token, {})


def cmd_sync_dirs(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(args.base_url, "/api/sync/listCloudSyncDir", token, {})


def cmd_sync_run(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if args.upload is not None:
        payload["upload"] = args.upload
    if args.dry_run:
        return {"dry_run": True, "endpoint": "/api/sync/performSync", "payload": payload}
    return api_post(args.base_url, "/api/sync/performSync", token, payload)


def cmd_notebook_list(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(args.base_url, "/api/notebook/lsNotebooks", token, {})


def cmd_notebook_create(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(args.base_url, "/api/notebook/createNotebook", token, {"name": args.name})


def cmd_notebook_remove(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(
        args.base_url,
        "/api/notebook/removeNotebook",
        token,
        {"notebook": args.notebook_id},
    )


def cmd_notebook_set_icon(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(
        args.base_url,
        "/api/notebook/setNotebookIcon",
        token,
        {"notebook": args.notebook_id, "icon": args.icon},
    )


def cmd_doc_create(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    result = api_post(
        args.base_url,
        "/api/filetree/createDocWithMd",
        token,
        {"notebook": args.notebook_id, "path": args.path, "markdown": normalize_markdown(args.markdown)},
    )
    if args.title and result.get("code") == 0 and result.get("data"):
        doc_id = result["data"]
        rename = api_post(
            args.base_url,
            "/api/filetree/renameDoc",
            token,
            {"notebook": args.notebook_id, "path": f"/{doc_id}.sy", "title": args.title},
        )
        return {"create": result, "rename": rename, "data": doc_id, "code": result.get("code"), "msg": result.get("msg", "")}
    return result


def cmd_doc_append_md(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(
        args.base_url,
        "/api/block/appendBlock",
        token,
        {"parentID": args.doc_id, "dataType": "markdown", "data": normalize_markdown(args.markdown)},
    )


def cmd_doc_list(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(
        args.base_url,
        "/api/filetree/listDocsByPath",
        token,
        {"notebook": args.notebook_id, "path": args.path},
    )


def cmd_asset_upload(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(
        args.base_url,
        "/api/asset/insertLocalAssets",
        token,
        {"assetPaths": [args.file], "isUpload": args.is_upload, "id": args.doc_id},
    )


def cmd_asset_doc_images(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(
        args.base_url,
        "/api/asset/getDocImageAssets",
        token,
        {"id": args.doc_id},
    )


def cmd_template_save(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(
        args.base_url,
        "/api/template/docSaveAsTemplate",
        token,
        {"id": args.doc_id, "name": args.name, "overwrite": args.overwrite},
    )


def cmd_template_search(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(args.base_url, "/api/search/searchTemplate", token, {"k": args.keyword})


def cmd_template_render(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(
        args.base_url,
        "/api/template/render",
        token,
        {"id": args.doc_id, "path": args.path},
    )


def cmd_template_remove(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(args.base_url, "/api/search/removeTemplate", token, {"path": args.path})


def cmd_export_md(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(args.base_url, "/api/export/exportMd", token, {"id": args.doc_id})


def cmd_bazaar_installed_plugins(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(
        args.base_url, "/api/bazaar/getInstalledPlugin", token, {"frontend": "desktop", "keyword": ""}
    )


def cmd_bazaar_remote_plugins(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(
        args.base_url, "/api/bazaar/getBazaarPlugin", token, {"frontend": "desktop", "keyword": ""}
    )


def cmd_doc_remove(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    return api_post(
        args.base_url,
        "/api/filetree/removeDoc",
        token,
        {"notebook": args.notebook_id, "path": args.doc_path},
    )


def str_to_bool(v: str) -> bool:
    low = v.strip().lower()
    if low in {"1", "true", "yes", "y"}:
        return True
    if low in {"0", "false", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"invalid bool value: {v}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Minimal SiYuan CLI for OpenClaw automation")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p.add_argument("--token", default=None, help="SiYuan API token")
    p.add_argument("--conf-path", default=DEFAULT_CONF, help="Path to SiYuan conf.json")

    sub = p.add_subparsers(dest="group", required=True)

    sync = sub.add_parser("sync")
    sync_sub = sync.add_subparsers(dest="action", required=True)
    sync_sub.add_parser("info")
    sync_sub.add_parser("dirs")
    sync_run = sync_sub.add_parser("run")
    sync_run.add_argument("--upload", type=str_to_bool, default=None)
    sync_run.add_argument("--dry-run", action="store_true")

    notebook = sub.add_parser("notebook")
    notebook_sub = notebook.add_subparsers(dest="action", required=True)
    notebook_sub.add_parser("list")
    n_create = notebook_sub.add_parser("create")
    n_create.add_argument("name")
    n_icon = notebook_sub.add_parser("set-icon")
    n_icon.add_argument("notebook_id")
    n_icon.add_argument("icon")
    n_remove = notebook_sub.add_parser("remove")
    n_remove.add_argument("notebook_id")

    doc = sub.add_parser("doc")
    doc_sub = doc.add_subparsers(dest="action", required=True)
    d_create = doc_sub.add_parser("create")
    d_create.add_argument("notebook_id")
    d_create.add_argument("--path", default="/")
    d_create.add_argument("--title", default=None)
    d_create.add_argument("--markdown", required=True)
    d_list = doc_sub.add_parser("list")
    d_list.add_argument("notebook_id")
    d_list.add_argument("--path", default="/")
    d_append = doc_sub.add_parser("append-md")
    d_append.add_argument("doc_id")
    d_append.add_argument("--markdown", required=True)
    d_remove = doc_sub.add_parser("remove")
    d_remove.add_argument("notebook_id")
    d_remove.add_argument("doc_path")

    asset = sub.add_parser("asset")
    asset_sub = asset.add_subparsers(dest="action", required=True)
    a_upload = asset_sub.add_parser("upload")
    a_upload.add_argument("doc_id")
    a_upload.add_argument("file")
    a_upload.add_argument("--is-upload", type=str_to_bool, default=True)
    a_doc_images = asset_sub.add_parser("doc-images")
    a_doc_images.add_argument("doc_id")

    template = sub.add_parser("template")
    template_sub = template.add_subparsers(dest="action", required=True)
    t_save = template_sub.add_parser("save")
    t_save.add_argument("doc_id")
    t_save.add_argument("name")
    t_save.add_argument("--overwrite", type=str_to_bool, default=True)
    t_search = template_sub.add_parser("search")
    t_search.add_argument("keyword")
    t_render = template_sub.add_parser("render")
    t_render.add_argument("doc_id")
    t_render.add_argument("path")
    t_remove = template_sub.add_parser("remove")
    t_remove.add_argument("path")

    export = sub.add_parser("export")
    export_sub = export.add_subparsers(dest="action", required=True)
    e_md = export_sub.add_parser("md")
    e_md.add_argument("doc_id")

    bazaar = sub.add_parser("bazaar")
    bazaar_sub = bazaar.add_subparsers(dest="action", required=True)
    bazaar_sub.add_parser("installed-plugins")
    bazaar_sub.add_parser("remote-plugins")
    return p


def dispatch(args: argparse.Namespace, token: str) -> Dict[str, Any]:
    if args.group == "sync" and args.action == "info":
        return cmd_sync_info(args, token)
    if args.group == "sync" and args.action == "dirs":
        return cmd_sync_dirs(args, token)
    if args.group == "sync" and args.action == "run":
        return cmd_sync_run(args, token)

    if args.group == "notebook" and args.action == "list":
        return cmd_notebook_list(args, token)
    if args.group == "notebook" and args.action == "create":
        return cmd_notebook_create(args, token)
    if args.group == "notebook" and args.action == "set-icon":
        return cmd_notebook_set_icon(args, token)
    if args.group == "notebook" and args.action == "remove":
        return cmd_notebook_remove(args, token)

    if args.group == "doc" and args.action == "create":
        return cmd_doc_create(args, token)
    if args.group == "doc" and args.action == "list":
        return cmd_doc_list(args, token)
    if args.group == "doc" and args.action == "append-md":
        return cmd_doc_append_md(args, token)
    if args.group == "doc" and args.action == "remove":
        return cmd_doc_remove(args, token)

    if args.group == "asset" and args.action == "upload":
        return cmd_asset_upload(args, token)
    if args.group == "asset" and args.action == "doc-images":
        return cmd_asset_doc_images(args, token)

    if args.group == "template" and args.action == "save":
        return cmd_template_save(args, token)
    if args.group == "template" and args.action == "search":
        return cmd_template_search(args, token)
    if args.group == "template" and args.action == "render":
        return cmd_template_render(args, token)
    if args.group == "template" and args.action == "remove":
        return cmd_template_remove(args, token)

    if args.group == "export" and args.action == "md":
        return cmd_export_md(args, token)

    if args.group == "bazaar" and args.action == "installed-plugins":
        return cmd_bazaar_installed_plugins(args, token)
    if args.group == "bazaar" and args.action == "remote-plugins":
        return cmd_bazaar_remote_plugins(args, token)

    raise SiyuanCtlError(f"unsupported command: {args.group} {args.action}")


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        token = load_token(args.token, args.conf_path)
        out = dispatch(args, token)
    except SiyuanCtlError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

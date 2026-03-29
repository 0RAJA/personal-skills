import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from scripts import siyuanctl


class TokenLoadTests(unittest.TestCase):
    def test_load_token_from_conf(self):
        with tempfile.TemporaryDirectory() as td:
            conf = Path(td) / "conf.json"
            conf.write_text(json.dumps({"api": {"token": "abc123"}}), encoding="utf-8")
            token = siyuanctl.load_token(None, str(conf))
            self.assertEqual(token, "abc123")

    def test_normalize_markdown(self):
        self.assertEqual(siyuanctl.normalize_markdown("a\\n\\nb"), "a\n\nb")


class SyncCommandTests(unittest.TestCase):
    def test_sync_run_dry_run(self):
        out = siyuanctl.cmd_sync_run(
            mock.Mock(base_url="http://127.0.0.1:6806", dry_run=True, upload=None), "tok"
        )
        self.assertEqual(out["dry_run"], True)
        self.assertEqual(out["endpoint"], "/api/sync/performSync")
        self.assertEqual(out["payload"], {})

    @mock.patch("scripts.siyuanctl.api_post")
    def test_sync_run_upload_flag(self, api_post):
        api_post.return_value = {"code": 0, "msg": "", "data": None}
        args = mock.Mock(base_url="http://127.0.0.1:6806", dry_run=False, upload=True)
        out = siyuanctl.cmd_sync_run(args, "tok")
        self.assertEqual(out["code"], 0)
        api_post.assert_called_once_with(
            "http://127.0.0.1:6806", "/api/sync/performSync", "tok", {"upload": True}
        )


class FeatureCommandTests(unittest.TestCase):
    @mock.patch("scripts.siyuanctl.api_post")
    def test_doc_create_with_title(self, api_post):
        api_post.side_effect = [
            {"code": 0, "msg": "", "data": "doc123"},
            {"code": 0, "msg": "", "data": None},
        ]
        args = mock.Mock(
            base_url="http://127.0.0.1:6806",
            notebook_id="nb1",
            path="/",
            title="Title",
            markdown="# T\\n\\nBody",
        )
        out = siyuanctl.cmd_doc_create(args, "tok")
        self.assertEqual(out["code"], 0)
        self.assertEqual(api_post.call_count, 2)

    @mock.patch("scripts.siyuanctl.api_post")
    def test_notebook_set_icon(self, api_post):
        api_post.return_value = {"code": 0, "msg": "", "data": None}
        args = mock.Mock(
            base_url="http://127.0.0.1:6806",
            notebook_id="nb1",
            icon="1f4d8",
        )
        out = siyuanctl.cmd_notebook_set_icon(args, "tok")
        self.assertEqual(out["code"], 0)
        api_post.assert_called_once_with(
            "http://127.0.0.1:6806",
            "/api/notebook/setNotebookIcon",
            "tok",
            {"notebook": "nb1", "icon": "1f4d8"},
        )

    @mock.patch("scripts.siyuanctl.api_post")
    def test_asset_upload(self, api_post):
        api_post.return_value = {"code": 0, "msg": "", "data": {"succMap": {}}}
        args = mock.Mock(
            base_url="http://127.0.0.1:6806",
            doc_id="doc1",
            file="/tmp/a.png",
            is_upload=True,
        )
        out = siyuanctl.cmd_asset_upload(args, "tok")
        self.assertEqual(out["code"], 0)
        api_post.assert_called_once_with(
            "http://127.0.0.1:6806",
            "/api/asset/insertLocalAssets",
            "tok",
            {"assetPaths": ["/tmp/a.png"], "isUpload": True, "id": "doc1"},
        )

    @mock.patch("scripts.siyuanctl.api_post")
    def test_template_save(self, api_post):
        api_post.return_value = {"code": 0, "msg": "", "data": None}
        args = SimpleNamespace(
            base_url="http://127.0.0.1:6806", doc_id="doc1", name="tpl", overwrite=True
        )
        out = siyuanctl.cmd_template_save(args, "tok")
        self.assertEqual(out["code"], 0)
        api_post.assert_called_once_with(
            "http://127.0.0.1:6806",
            "/api/template/docSaveAsTemplate",
            "tok",
            {"id": "doc1", "name": "tpl", "overwrite": True},
        )

    @mock.patch("scripts.siyuanctl.api_post")
    def test_export_md(self, api_post):
        api_post.return_value = {"code": 0, "msg": "", "data": {"zip": "/export/a.zip"}}
        args = mock.Mock(base_url="http://127.0.0.1:6806", doc_id="doc1")
        out = siyuanctl.cmd_export_md(args, "tok")
        self.assertEqual(out["code"], 0)
        api_post.assert_called_once_with(
            "http://127.0.0.1:6806",
            "/api/export/exportMd",
            "tok",
            {"id": "doc1"},
        )


if __name__ == "__main__":
    unittest.main()

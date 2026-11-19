"""CLI exit-status regression tests using the checked-out implementation."""
import io
import json
import unittest
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

from scripts import siyuanctl


class ExitStatusTests(unittest.TestCase):
    def run_cli(self, args, responses=(), error=None):
        replies = []
        for value in responses:
            response = mock.MagicMock()
            response.__enter__.return_value.read.return_value = (
                value if isinstance(value, bytes) else json.dumps(value).encode()
            )
            replies.append(response)
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(siyuanctl.urllib.request, "urlopen", side_effect=error or replies) as request:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = siyuanctl.main(["--token", "test-token", *args])
        return status, stdout.getvalue(), stderr.getvalue(), request

    def test_http_200_business_error(self):
        for code in (-1, 1):
            with self.subTest(code=code):
                payload = {"code": code, "msg": "permission denied", "data": None}
                status, out, err, _ = self.run_cli(["notebook", "list"], [payload])
                self.assertEqual(status, 1)
                self.assertEqual(out, "")
                self.assertEqual(json.loads(err), payload)

    def test_success_stdout(self):
        payload = {"code": 0, "msg": "", "data": None}
        status, out, err, _ = self.run_cli(["notebook", "list"], [payload])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(out), payload)
        self.assertEqual(err, "")

    def test_create_failure_skips_rename(self):
        payload = {"code": -1, "msg": "missing notebook", "data": None}
        status, out, err, request = self.run_cli(
            ["doc", "create", "nb", "--markdown", "body", "--title", "Title"], [payload]
        )
        self.assertEqual((status, out, request.call_count), (1, "", 1))
        self.assertEqual(json.loads(err), payload)

    def test_create_and_rename_results(self):
        created = {"code": 0, "msg": "", "data": "doc-id"}
        for code in (0, -1):
            with self.subTest(rename_code=code):
                renamed = {"code": code, "msg": "rename failed" if code else "", "data": None}
                status, out, err, request = self.run_cli(
                    ["doc", "create", "nb", "--markdown", "body", "--title", "Title"],
                    [created, renamed],
                )
                self.assertEqual(status, int(code != 0))
                self.assertEqual(request.call_count, 2)
                self.assertEqual(json.loads(err if code else out), {
                    "create": created, "rename": renamed, "data": "doc-id",
                    "code": code, "msg": renamed["msg"],
                })
                self.assertEqual(out if code else err, "")

    def test_create_without_title(self):
        created = {"code": 0, "msg": "", "data": "doc-id"}
        status, out, err, request = self.run_cli(["doc", "create", "nb", "--markdown", "body"], [created])
        self.assertEqual((status, err, request.call_count), (0, "", 1))
        self.assertEqual(json.loads(out), created)

    def test_dry_run_without_code_is_success(self):
        status, out, err, request = self.run_cli(["sync", "run", "--dry-run"])
        self.assertEqual((status, err), (0, ""))
        self.assertTrue(json.loads(out)["dry_run"])
        request.assert_not_called()

    def test_invalid_json(self):
        status, out, err, _ = self.run_cli(["notebook", "list"], [b"not-json"])
        self.assertEqual((status, out), (1, ""))
        self.assertIn("invalid json", json.loads(err)["error"])

    def test_transport_errors(self):
        for error in (
            urllib.error.HTTPError("http://localhost", 403, "forbidden", {}, None),
            urllib.error.URLError("offline"),
        ):
            with self.subTest(error=type(error).__name__):
                status, out, err, _ = self.run_cli(["notebook", "list"], error=error)
                self.assertEqual((status, out), (1, ""))
                self.assertFalse(json.loads(err)["ok"])


if __name__ == "__main__":
    unittest.main()

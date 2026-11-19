"""Opt-in real-kernel test. Never connects to an existing or personal workspace.

python3 tests/e2e_siyuanctl.py --kernel /absolute/path/to/SiYuan-Kernel
Optional --baseline runs the same failure cases against an unpatched CLI.
"""
import argparse
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()
    cli = Path(__file__).resolve().parents[1] / "scripts/siyuanctl.py"
    report = {"version": subprocess.check_output([str(args.kernel), "--version"], text=True).strip(), "checks": []}
    with tempfile.TemporaryDirectory(prefix="siyuanctl-e2e-") as temp:
        root = Path(temp)
        home, workspace = root / "home", root / "workspace"
        home.mkdir()
        workspace.mkdir()
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        url = f"http://127.0.0.1:{port}"
        auth = secrets.token_urlsafe(32)
        proc = None
        token = ""
        logs = (root / "kernel.log").open("w")

        def api(endpoint, payload=None):
            request = urllib.request.Request(url + endpoint, data=json.dumps(payload or {}).encode(), headers={
                "Content-Type": "application/json", "Authorization": "Token " + token,
            })
            with urllib.request.urlopen(request, timeout=10) as response:
                assert response.status == 200
                return json.load(response)

        def start():
            nonlocal proc, token
            proc = subprocess.Popen([
                str(args.kernel.resolve()), "serve", f"--workspace={workspace}", f"--home-dir={home}",
                f"--port={port}", "--fixed-port=false", "--safe-mode", f"--accessAuthCode={auth}",
            ], stdout=logs, stderr=logs, env={**os.environ, "HOME": str(home)})
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    raise RuntimeError("kernel exited during startup")
                try:
                    token = json.loads((workspace / "conf/conf.json").read_text())["api"]["token"]
                    if api("/api/notebook/lsNotebooks")["code"] == 0:
                        # Fresh kernels initialize document metadata asynchronously.
                        time.sleep(3)
                        return
                except (OSError, ValueError, KeyError):
                    pass
                time.sleep(0.2)
            raise RuntimeError("kernel did not become ready in 30 seconds")

        def stop():
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)

        def run_cli(arguments, expected, script=cli):
            result = subprocess.run([sys.executable, str(script), "--base-url", url, *arguments],
                                    env={**os.environ, "SIYUAN_TOKEN": token}, capture_output=True, text=True, timeout=30)
            assert result.returncode == expected, (arguments, result.returncode, result.stdout, result.stderr)
            if script == cli:
                assert not (result.stdout if expected else result.stderr), result
            return json.loads(result.stderr if expected else result.stdout)

        def files():
            result = api("/api/filetree/listDocsByPath", {"notebook": notebook, "path": "/"})
            assert result["code"] == 0, result
            return result["data"]["files"]

        try:
            start()
            assert api("/api/notebook/lsNotebooks")["data"]["notebooks"] == []
            report["checks"].append("fresh workspace: 0 notebooks")
            created = run_cli(["notebook", "create", "issue-1-e2e"], 0)
            notebook = created["data"]["notebook"]["id"]
            time.sleep(2)
            assert files() == []
            root_doc = run_cli(["doc", "create", notebook, "--path", "/Root", "--title", "Renamed",
                                "--markdown", "# fixture\n\nPersistence marker"], 0)
            assert root_doc["create"]["code"] == root_doc["rename"]["code"] == 0
            assert any(f["id"] == root_doc["data"] and f["name"] == "Renamed" for f in files())
            report["checks"].append("real CLI create + rename: exit 0, stdout JSON, title verified by read API")
            invalid_args = ["doc", "create", "20260101000000-invalid", "--markdown", "invalid notebook fixture"]
            assert api("/api/filetree/createDocWithMd", {"notebook": "20260101000000-invalid", "path": "/", "markdown": "invalid fixture"})["code"] != 0
            invalid = run_cli(invalid_args, 1)
            assert invalid["code"] != 0
            report["checks"].append("real HTTP 200 missing-notebook application error: exit 1, stderr JSON, no stdout")
            nested_args = ["doc", "create", notebook, "--path", "/Parent/Child", "--title", "NestedRenamed", "--markdown", "nested marker"]
            nested = run_cli(nested_args, 1)
            assert nested["create"]["code"] == 0 and nested["rename"]["code"] != 0
            assert nested["code"] == nested["rename"]["code"]
            nested_paths = list((workspace / "data" / notebook).rglob(nested["data"] + ".sy"))
            assert len(nested_paths) == 1
            report["checks"].append("real nested-document partial success: created file exists; rename fails; exit 1 retains doc ID + both results")
            if args.baseline:
                baseline_error = run_cli(invalid_args, 0, args.baseline)
                baseline_nested = run_cli([*nested_args[:4], "/BaselineParent/Child", *nested_args[5:]], 0, args.baseline)
                assert baseline_error["code"] != 0
                assert baseline_nested["code"] == 0 and baseline_nested["rename"]["code"] != 0
                report["checks"].append("unpatched baseline reproduces both false-success exit codes against real kernel")
            dry_run = run_cli(["sync", "run", "--dry-run"], 0)
            assert dry_run["dry_run"] is True
            root_file = workspace / "data" / notebook / (root_doc["data"] + ".sy")
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline and (not root_file.exists() or "Persistence marker" not in root_file.read_text()):
                time.sleep(0.2)
            assert "Persistence marker" in root_file.read_text()
            stop()
            start()
            assert any(f["id"] == root_doc["data"] and f["name"] == "Renamed" for f in files())
            assert "Persistence marker" in root_file.read_text()
            assert nested_paths[0].exists()
            report["checks"].append("kernel restart: renamed title + document body + partial-success file persist")
            run_cli(["notebook", "remove", notebook], 0)
            assert api("/api/notebook/lsNotebooks")["data"]["notebooks"] == []
            report["checks"].append("cleanup: test notebook removed, read API confirms 0 notebooks")
        finally:
            stop()
            logs.close()
    report["checks"].append("kernel stopped; temporary workspace/home removed")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

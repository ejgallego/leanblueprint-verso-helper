#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


SCRIPT_DIR = Path(__file__).resolve().parent


def write_config(root: Path, default_chapters: list[str]) -> None:
    (root / "verso-harness.toml").write_text(
        "\n".join(
            [
                'package_name = "DemoBlueprint"',
                'blueprint_main = "BlueprintMain"',
                'formalization_path = "Demo"',
                'chapter_root = "."',
                'tex_source_glob = "./blueprint/src/chapter/*.tex"',
                "",
                "[lt]",
                f'default_chapters = [{", ".join(repr(path) for path in default_chapters)}]',
                "",
            ]
        ),
        encoding="utf-8",
    )


def run_status(project_root: Path, path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "status_lt.py"),
            "--project-root",
            str(project_root),
            str(path),
        ],
        cwd=SCRIPT_DIR.parent,
        capture_output=True,
        text=True,
        check=False,
    )


class StatusLtTests(unittest.TestCase):
    def test_status_reports_soft_ref_review_hints(self) -> None:
        content = """#doc (Manual) "Demo" =>

Alpha.
```tex "demo/prose"
See theorem~\\ref{bar}.
Alpha.
```
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root, ["Demo.lean"])
            path = root / "Demo.lean"
            path.write_text(content, encoding="utf-8")
            result = run_status(root, path)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertIn("ref_review=1", result.stdout)
            self.assertIn("soft_ref_hints=1", result.stdout)

    def test_status_counts_bpref_resolved_refs_as_clean(self) -> None:
        content = """#doc (Manual) "Demo" =>

See theorem {bpref "bar"}[]. Alpha.
```tex "demo/prose"
See theorem~\\ref{bar}.
Alpha.
```
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root, ["Demo.lean"])
            path = root / "Demo.lean"
            path.write_text(content, encoding="utf-8")
            result = run_status(root, path)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertIn("ref_review=0", result.stdout)
            self.assertIn("soft_ref_hints=0", result.stdout)


if __name__ == "__main__":
    unittest.main()

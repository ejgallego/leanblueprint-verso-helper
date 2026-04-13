#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


SCRIPT_DIR = Path(__file__).resolve().parent


def write_config(root: Path, default_chapters: list[str]) -> None:
    (root / 'verso-harness.toml').write_text(
        '\n'.join(
            [
                'package_name = "DemoBlueprint"',
                'blueprint_main = "BlueprintMain"',
                'formalization_path = "Demo"',
                'chapter_root = "."',
                'tex_source_glob = "./blueprint/src/chapter/*.tex"',
                '',
                '[lt]',
                f'default_chapters = [{", ".join(repr(path) for path in default_chapters)}]',
                '',
            ]
        ),
        encoding='utf-8',
    )


def run_checker(project_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / 'check_source_authorized_metadata.py'),
            '--project-root',
            str(project_root),
        ],
        cwd=SCRIPT_DIR.parent,
        capture_output=True,
        text=True,
        check=False,
    )


class CheckSourceAuthorizedMetadataTests(unittest.TestCase):
    def test_cli_reports_local_only_uses(self) -> None:
        content = """#doc (Manual) "Demo" =>

:::proof "foo"
{uses "bar"}[]
Alpha.
:::
```tex "foo" (slot := proof)
\\begin{proof}
Alpha.
\\end{proof}
```
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root, ['Demo.lean'])
            (root / 'Demo.lean').write_text(content, encoding='utf-8')
            result = run_checker(root)
            self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
            self.assertIn("extra uses ['bar']", result.stdout)

    def test_cli_reports_local_only_lean_attachment(self) -> None:
        content = """#doc (Manual) "Demo" =>

:::theorem "foo" (lean := "Demo.foo")
Alpha.
:::
```tex "foo"
\\begin{theorem}
\\label{foo}
Alpha.
\\end{theorem}
```
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root, ['Demo.lean'])
            (root / 'Demo.lean').write_text(content, encoding='utf-8')
            result = run_checker(root)
            self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
            self.assertIn("extra lean ['Demo.foo']", result.stdout)

    def test_cli_accepts_source_authorized_metadata(self) -> None:
        content = """#doc (Manual) "Demo" =>

:::theorem "foo" (lean := "Demo.foo")
{uses "bar"}[]
Alpha.
:::
```tex "foo"
\\begin{theorem}
\\label{foo}
\\lean{Demo.foo}
\\uses{bar}
Alpha.
\\end{theorem}
```
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root, ['Demo.lean'])
            (root / 'Demo.lean').write_text(content, encoding='utf-8')
            result = run_checker(root)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertEqual(result.stdout.strip(), '')

    def test_cli_allows_missing_local_metadata(self) -> None:
        content = """#doc (Manual) "Demo" =>

:::theorem "foo"
Alpha.
:::
```tex "foo"
\\begin{theorem}
\\label{foo}
\\lean{Demo.foo}
\\uses{bar}
Alpha.
\\end{theorem}
```
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root, ['Demo.lean'])
            (root / 'Demo.lean').write_text(content, encoding='utf-8')
            result = run_checker(root)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertEqual(result.stdout.strip(), '')


if __name__ == '__main__':
    unittest.main()

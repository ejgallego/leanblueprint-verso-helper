#!/usr/bin/env python3
from __future__ import annotations

import stat
import subprocess
import sys
import tempfile
from pathlib import Path
import textwrap
import unittest


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

class UpdateCiTests(unittest.TestCase):
    def test_update_ci_renders_reusable_workflow_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            (project_root / "lakefile.lean").write_text(
                '\n'.join(
                    [
                        'import Lake',
                        'open Lake DSL',
                        '',
                        'require Demo from "./Demo"',
                        'require VersoBlueprint from git "https://github.com/leanprover/verso-blueprint.git" @ "v4.28.0"',
                        '',
                        'package DemoBlueprint where',
                    ]
                )
                + '\n',
                encoding='utf-8',
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "update_ci.py"),
                    "--project-root",
                    str(project_root),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

            workflow_path = project_root / ".github" / "workflows" / "blueprint.yml"
            workflow_text = workflow_path.read_text(encoding="utf-8")
            self.assertNotIn("__PAGES_WORKFLOW_", workflow_text)
            self.assertIn(
                "uses: leanprover/verso-blueprint/.github/workflows/blueprint-pages.yml@v4.28.0",
                workflow_text,
            )
            self.assertIn("checkout_submodules: true", workflow_text)
            self.assertIn("harness_enabled: true", workflow_text)

            script_path = project_root / "scripts" / "ci-pages.sh"
            self.assertTrue(script_path.exists())
            self.assertTrue(script_path.stat().st_mode & stat.S_IXUSR)
            filter_path = project_root / "scripts" / "filter_docstring_warnings.py"
            self.assertTrue(filter_path.exists())

    def test_rendered_filter_suppresses_docstrings_with_apostrophes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            (project_root / "lakefile.lean").write_text(
                '\n'.join(
                    [
                        'import Lake',
                        'open Lake DSL',
                        '',
                        'require Demo from "./Demo"',
                        'require VersoBlueprint from git "https://github.com/leanprover/verso-blueprint.git" @ "v4.28.0"',
                        '',
                        'package DemoBlueprint where',
                    ]
                )
                + '\n',
                encoding='utf-8',
            )
            (project_root / "verso-harness.toml").write_text(
                "[harness]\n"
                "native_warnings = false\n"
                "docstring_warnings = false\n"
                "strict_external_code = true\n",
                encoding="utf-8",
            )
            update_result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "update_ci.py"),
                    "--project-root",
                    str(project_root),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(update_result.returncode, 0, msg=update_result.stdout + update_result.stderr)

            filter_path = project_root / "scripts" / "filter_docstring_warnings.py"
            sample = textwrap.dedent(
                """\
                warning: Demo.lean:1:1: 'Demo.Struct.field' is not documented.

                Set option 'verso.docstring.allowMissing' to 'false' to disallow missing docstrings.
                warning: Demo.lean:1:1: 'Demo.Struct.field''' is not documented.

                Set option 'verso.docstring.allowMissing' to 'false' to disallow missing docstrings.
                visible line
                """
            )
            filter_result = subprocess.run(
                [
                    sys.executable,
                    str(filter_path),
                    "--project-root",
                    str(project_root),
                ],
                cwd=project_root,
                input=sample,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(filter_result.returncode, 0, msg=filter_result.stdout + filter_result.stderr)
            self.assertEqual(filter_result.stdout, "visible line\n")


if __name__ == "__main__":
    unittest.main()

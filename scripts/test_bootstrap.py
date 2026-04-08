#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent


class BootstrapTests(unittest.TestCase):
    def test_bootstrap_uses_upstream_toolchain_and_matching_verso_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'demo-project'
            demo = root / 'Demo'
            demo.mkdir(parents=True)
            (demo / 'lean-toolchain').write_text('leanprover/lean4:v4.28.0\n', encoding='utf-8')

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / 'bootstrap.py'),
                    '--project-root',
                    str(root),
                    '--package-name',
                    'DemoBlueprint',
                    '--title',
                    'Demo Blueprint',
                    '--formalization-name',
                    'Demo',
                    '--formalization-path',
                    './Demo',
                    '--tex-source-glob',
                    './blueprint/src/chapter/*.tex',
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertIn('lean-toolchain: leanprover/lean4:v4.28.0', result.stdout)
            self.assertIn('VersoBlueprint ref: lean-v4.28.0', result.stdout)

            self.assertEqual(
                (root / 'lean-toolchain').read_text(encoding='utf-8').strip(),
                'leanprover/lean4:v4.28.0',
            )
            lakefile = (root / 'lakefile.lean').read_text(encoding='utf-8')
            self.assertIn('@ "lean-v4.28.0"', lakefile)

            config_path = root / 'verso-harness.toml'
            self.assertTrue(config_path.exists())

            check = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / 'check_harness.py'),
                    '--project-root',
                    str(root),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(check.returncode, 0, msg=check.stdout + check.stderr)


if __name__ == '__main__':
    unittest.main()

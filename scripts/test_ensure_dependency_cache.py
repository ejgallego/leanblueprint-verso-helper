#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
import unittest


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import ensure_dependency_cache  # noqa: E402


def write_mathlib_manifest(root: Path) -> None:
    manifest = {"packages": [{"name": "mathlib", "rev": "abc", "inputRev": "abc"}]}
    (root / "lake-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class EnsureDependencyCacheTests(unittest.TestCase):
    def test_reports_incomplete_mathlib_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_mathlib_manifest(root)
            mathlib_dir = root / ".lake" / "packages" / "mathlib"
            (mathlib_dir / "Mathlib").mkdir(parents=True)
            (mathlib_dir / "Mathlib" / "OnlySource.lean").write_text("", encoding="utf-8")
            gaps = ensure_dependency_cache.dependency_artifact_gaps(root)
        self.assertEqual(
            gaps,
            ["mathlib: cached artifacts incomplete (.olean 0/1, .trace 0/1, .olean.hash 0/1)"],
        )

    def test_accepts_matching_mathlib_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_mathlib_manifest(root)
            mathlib_dir = root / ".lake" / "packages" / "mathlib"
            (mathlib_dir / "Mathlib").mkdir(parents=True)
            (mathlib_dir / "Mathlib" / "Ready.lean").write_text("", encoding="utf-8")
            artifact_dir = mathlib_dir / ".lake" / "build" / "lib" / "lean" / "Mathlib"
            artifact_dir.mkdir(parents=True)
            for suffix in ensure_dependency_cache.REQUIRED_ARTIFACT_SUFFIXES:
                (artifact_dir / f"Ready{suffix}").write_text("", encoding="utf-8")
            gaps = ensure_dependency_cache.dependency_artifact_gaps(root)
        self.assertEqual(gaps, [])

    def test_noops_when_manifest_has_no_guarded_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "lake-manifest.json").write_text(
                json.dumps({"packages": [{"name": "not_mathlib"}]}),
                encoding="utf-8",
            )
            gaps = ensure_dependency_cache.dependency_artifact_gaps(root)
        self.assertEqual(gaps, [])

    def test_materializes_cached_lean_artifacts_from_dependency_trace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            cache = Path(tmp) / "cache"
            trace = (
                root
                / ".lake"
                / "packages"
                / "verso"
                / ".lake"
                / "build"
                / "lib"
                / "lean"
                / "VersoManual"
                / "Basic.trace"
            )
            trace.parent.mkdir(parents=True)
            cache.mkdir()
            trace.write_text(
                json.dumps(
                    {
                        "outputs": {
                            "o": [
                                "abc.olean",
                                "def.olean.server",
                                "ghi.olean.private",
                            ],
                            "i": "jkl.ilean",
                            "c": "ignored.c",
                            "m": False,
                        }
                    }
                ),
                encoding="utf-8",
            )
            for artifact_name in [
                "abc.olean",
                "def.olean.server",
                "ghi.olean.private",
                "jkl.ilean",
            ]:
                (cache / artifact_name).write_text(artifact_name, encoding="utf-8")

            restored = ensure_dependency_cache.materialize_cached_lean_artifacts(root, cache)

            self.assertEqual(
                sorted(path.name for path in restored),
                [
                    "Basic.ilean",
                    "Basic.olean",
                    "Basic.olean.private",
                    "Basic.olean.server",
                ],
            )
            self.assertEqual(
                (trace.parent / "Basic.olean").read_text(encoding="utf-8"),
                "abc.olean",
            )
            self.assertEqual(
                (trace.parent / "Basic.olean.server").read_text(encoding="utf-8"),
                "def.olean.server",
            )
            self.assertEqual(
                (trace.parent / "Basic.olean.private").read_text(encoding="utf-8"),
                "ghi.olean.private",
            )
            self.assertEqual(
                (trace.parent / "Basic.ilean").read_text(encoding="utf-8"),
                "jkl.ilean",
            )
            self.assertFalse((trace.parent / "Basic.c").exists())


if __name__ == "__main__":
    unittest.main()

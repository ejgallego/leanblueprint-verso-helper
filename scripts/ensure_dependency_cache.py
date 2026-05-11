#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


CACHE_GET_COMMAND = ("lake", "exe", "cache", "get")
GUARDED_MODULE_ROOTS = {
    "mathlib": ("Mathlib",),
}
REQUIRED_ARTIFACT_SUFFIXES = (".olean", ".trace", ".olean.hash")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Warm dependency build caches and refuse to continue when guarded "
            "dependencies would be rebuilt by Lake."
        )
    )
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument(
        "--warm-cache",
        action="store_true",
        help="Run `lake exe cache get` before checking artifacts.",
    )
    return parser.parse_args()


def count_files_with_suffix(root: Path, suffix: str) -> int:
    if not root.exists():
        return 0
    return sum(1 for path in root.rglob(f"*{suffix}") if path.is_file())


def module_source_count(package_dir: Path, module_roots: tuple[str, ...]) -> int:
    count = 0
    for module_root in module_roots:
        count += count_files_with_suffix(package_dir / module_root, ".lean")
        if (package_dir / f"{module_root}.lean").is_file():
            count += 1
    return count


def module_artifact_count(
    package_dir: Path,
    module_roots: tuple[str, ...],
    suffix: str,
) -> int:
    build_root = package_dir / ".lake" / "build" / "lib" / "lean"
    count = 0
    for module_root in module_roots:
        count += count_files_with_suffix(build_root / module_root, suffix)
        if (build_root / f"{module_root}{suffix}").is_file():
            count += 1
    return count


def read_manifest_package_names(project_root: Path) -> set[str]:
    manifest_path = project_root / "lake-manifest.json"
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"missing {manifest_path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {manifest_path}: {exc}")
    packages = data.get("packages")
    if not isinstance(packages, list):
        raise SystemExit(f"invalid Lake manifest format in {manifest_path}: missing packages list")
    names: set[str] = set()
    for package in packages:
        if not isinstance(package, dict):
            continue
        name = package.get("name")
        if isinstance(name, str):
            names.add(name)
    return names


def relative_to_project(path: Path, project_root: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def dependency_artifact_gaps(project_root: Path) -> list[str]:
    package_names = read_manifest_package_names(project_root)
    gaps: list[str] = []
    for package_name, module_roots in GUARDED_MODULE_ROOTS.items():
        if package_name not in package_names:
            continue
        package_dir = project_root / ".lake" / "packages" / package_name
        if not package_dir.exists():
            gaps.append(
                f"{package_name}: missing checkout at {relative_to_project(package_dir, project_root)}"
            )
            continue
        source_count = module_source_count(package_dir, module_roots)
        if source_count == 0:
            gaps.append(f"{package_name}: no source modules found")
            continue
        missing_artifacts: list[str] = []
        for suffix in REQUIRED_ARTIFACT_SUFFIXES:
            artifact_count = module_artifact_count(package_dir, module_roots, suffix)
            if artifact_count < source_count:
                missing_artifacts.append(f"{suffix} {artifact_count}/{source_count}")
        if missing_artifacts:
            gaps.append(f"{package_name}: cached artifacts incomplete ({', '.join(missing_artifacts)})")
    return gaps


def warm_cache(project_root: Path) -> int:
    print(f"[dependency-cache] {' '.join(CACHE_GET_COMMAND)}", flush=True)
    return subprocess.run(list(CACHE_GET_COMMAND), cwd=project_root, check=False).returncode


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    if args.warm_cache:
        cache_status = warm_cache(project_root)
        if cache_status != 0:
            return cache_status

    gaps = dependency_artifact_gaps(project_root)
    if gaps:
        print(
            "refusing to continue because dependency cache artifacts are missing; "
            "this prevents `lake build` from compiling mathlib.",
            file=sys.stderr,
        )
        for gap in gaps:
            print(f"  {gap}", file=sys.stderr)
        return 1

    print("[dependency-cache] guarded dependency artifacts present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

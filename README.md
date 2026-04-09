# Leanblueprint To Verso Harness

This repository helps you turn an existing `leanblueprint` or TeX blueprint
project into a Verso-based blueprint site.

Use it when:
- you are starting a new blueprint port from scratch
- you already have an older port and want to bring it up to the current shared setup

## Start Here

Add the shared harness to your repo:

```bash
git submodule add git@github.com:ejgallego/leanblueprint-to-verso.git tools/verso-harness
```

If you are starting a brand-new port from an empty directory, the first command
you should run is:

```bash
python3 tools/verso-harness/scripts/start_new_port.py \
  --project-root . \
  --package-name <BlueprintPackage> \
  --title "<Project Title>" \
  --formalization-name <FormalizationName> \
  --formalization-remote <upstream-formalization-git-url> \
  --formalization-path <FormalizationName> \
  --tex-source-glob "<relative-tex-source-path-or-glob>"
```

After that:
1. review `verso-harness.toml`
2. set `lt.default_chapters`
3. run `python3 tools/verso-harness/scripts/check_harness.py --project-root .`
4. copy `tools/verso-harness/snippets/AGENTS.host.md` into `AGENTS.md`
5. start the first chapter port

## The Three Main Rules

- The upstream math project decides the Lean toolchain.
- Every managed repo must have a root `verso-harness.toml` file.
- New ports use one standard layout; do not invent a new one.

## If Your Repo Already Exists

If you already have an older port, use the retrofit path instead of the
empty-directory start path:

- [`references/retrofit.md`](references/retrofit.md)
- [`references/maintenance.md`](references/maintenance.md)

## Common Commands

Check that the repo matches the expected shared setup:

```bash
python3 tools/verso-harness/scripts/check_harness.py --project-root .
```

Run the main chapter-audit commands:

```bash
python3 tools/verso-harness/scripts/check_lt_source_pairs.py --project-root . path/to/Chapter.lean
python3 tools/verso-harness/scripts/check_lt_similarity.py --project-root . path/to/Chapter.lean
python3 tools/verso-harness/scripts/check_source_label_grounding.py --project-root . path/to/Chapter.lean
python3 tools/verso-harness/scripts/lt_audit.py --project-root . path/to/Chapter.lean
```

## More Detailed Docs

Start a new port from an empty directory:
- [`references/start-new-port.md`](references/start-new-port.md)

Short adoption checklist:
- [`references/new-consumer-checklist.md`](references/new-consumer-checklist.md)

Detailed porting workflow:
- [`references/porting.md`](references/porting.md)
- [`references/lt-method.md`](references/lt-method.md)
- [`AGENTS.md`](AGENTS.md)

## Notes

- The shared setup may change over time because it is used by more than one
  project. If `tools/verso-harness` changes unexpectedly, inspect the helper
  diff and rerun `check_harness.py`.
- The helper chooses the matching `VersoBlueprint` branch from the Lean
  toolchain used by the upstream math project.
- Generated `README.md` files are starting points only; after bootstrap they are
  project-owned.

# Leanblueprint To Verso Harness

Shared harness for deterministic ports from `leanblueprint` or TeX blueprints to
`verso-blueprint`.

## Hard Rules

- The upstream formalization determines `lean-toolchain`.
- The consumer repo root must carry `verso-harness.toml`.
- New ports start from an empty directory with the canonical integration-repo
  layout.

## Start Here

Add the harness:

```bash
git submodule add git@github.com:ejgallego/leanblueprint-to-verso.git tools/verso-harness
```

For a new port from an empty directory, use:

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

Then:

1. review `verso-harness.toml`
2. set `lt.default_chapters`
3. run `python3 tools/verso-harness/scripts/check_harness.py --project-root .`
4. copy `tools/verso-harness/snippets/AGENTS.host.md` into `AGENTS.md`
5. start the first LT chapter pass

## Main Workflows

New port:
- [`references/start-new-port.md`](references/start-new-port.md)

Existing port retrofit:
- [`references/retrofit.md`](references/retrofit.md)
- [`references/maintenance.md`](references/maintenance.md)

LT workflow and policy:
- [`references/lt-method.md`](references/lt-method.md)
- [`references/porting.md`](references/porting.md)
- [`AGENTS.md`](AGENTS.md)

Onboarding checklist:
- [`references/new-consumer-checklist.md`](references/new-consumer-checklist.md)

## LT Commands

```bash
python3 tools/verso-harness/scripts/check_lt_source_pairs.py --project-root . path/to/Chapter.lean
python3 tools/verso-harness/scripts/check_lt_similarity.py --project-root . path/to/Chapter.lean
python3 tools/verso-harness/scripts/check_source_label_grounding.py --project-root . path/to/Chapter.lean
python3 tools/verso-harness/scripts/lt_audit.py --project-root . path/to/Chapter.lean
```

## Ownership

Helper-owned and safe to refresh automatically:
- `scripts/ci-pages.sh`
- `.github/workflows/blueprint.yml`

Project-owned after bootstrap:
- `README.md`
- `verso-harness.toml`
- `lakefile.lean`
- `lean-toolchain`
- `BlueprintMain.lean` or the configured `blueprint_main`
- root blueprint modules and chapter prose

## Notes

- The helper chooses the matching `VersoBlueprint` branch as `lean-<release>`.
- Shared harness updates may arrive independently of local chapter work; inspect
  the helper diff, rerun `check_harness.py`, then decide whether only
  helper-owned files changed or whether project-owned files need review.

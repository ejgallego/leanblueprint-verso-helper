#!/usr/bin/env bash

set -euo pipefail

lake build +__BLUEPRINT_MAIN__:deps 2>&1 | python3 scripts/filter_docstring_warnings.py --project-root .
lake env lean --run __BLUEPRINT_MAIN__.lean --output _out/site 2>&1 | python3 scripts/filter_docstring_warnings.py --project-root .

test -f _out/site/html-multi/index.html
test -f _out/site/html-multi/-verso-data/blueprint-preview-manifest.json

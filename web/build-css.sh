#!/usr/bin/env bash
# Rebuild the vendored Tailwind stylesheet for docs/index.html.
# Requires network access to the npm registry (npx downloads tailwindcss on demand).
#   ./web/build-css.sh
set -euo pipefail
cd "$(dirname "$0")/.."
npx --yes tailwindcss@3.4.16 \
  -c web/tailwind.config.js \
  -i web/tailwind.input.css \
  -o docs/tailwind.css \
  --minify
echo "Wrote docs/tailwind.css"

#!/bin/sh
# Build the site the way .github/workflows/pages.yml builds it, into _site/, so the
# decks and the quiz pages can be checked together in a browser before pushing.
#   sh tools/build_local.sh            # site + every deck
#   sh tools/build_local.sh week-03    # site + just that week's decks
set -e
cd "$(dirname "$0")/.."
PATH="/Library/Developer/CommandLineTools/usr/bin:$HOME/Library/Python/3.9/bin:/opt/homebrew/bin:$PATH"
export PATH

mkdocs build --strict -d _site >/dev/null

WEEK="${1:-*}"
for md in slides/$WEEK/*.md; do
  case "$md" in *LECTURE_PLAN.md) continue;; esac
  out="_site/${md%.md}.html"
  mkdir -p "$(dirname "$out")"
  npx -y @marp-team/marp-cli@latest --no-stdin --theme slides/theme/ce414.css --html \
    --allow-local-files "$md" -o "$out" >/dev/null 2>&1
  echo "  deck  $out"
done
for d in slides/$WEEK/images; do
  [ -d "$d" ] || continue
  mkdir -p "_site/$(dirname "$d")"
  cp -R "$d" "_site/$(dirname "$d")/"
done
echo "built _site"

#!/usr/bin/env bash
# Appends the just-made commit's subject to CHANGELOG.md's [Unreleased]
# section, then folds that update into the same commit via --amend.
set -euo pipefail
cd "$(dirname "$0")/.."

GIT_DIR=$(git rev-parse --git-dir)
if [ -d "$GIT_DIR/rebase-merge" ] || [ -d "$GIT_DIR/rebase-apply" ] || [ -f "$GIT_DIR/CHERRY_PICK_HEAD" ]; then
  exit 0
fi

# Guards against this hook's own amend re-triggering itself
if [ -n "${SKIP_CHANGELOG_HOOK:-}" ]; then
  exit 0
fi

if [ ! -f CHANGELOG.md ] || ! grep -q "^## \[Unreleased\]" CHANGELOG.md; then
  exit 0
fi

SUBJECT=$(git log -1 --format=%s)

awk -v line="- ${SUBJECT}" '
  /^## \[Unreleased\]/ && !done { print; print line; done=1; next }
  { print }
' CHANGELOG.md > CHANGELOG.md.tmp && mv CHANGELOG.md.tmp CHANGELOG.md

git add CHANGELOG.md
SKIP_CHANGELOG_HOOK=1 git commit --amend --no-edit --no-verify --quiet

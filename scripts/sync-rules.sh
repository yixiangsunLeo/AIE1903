#!/bin/sh
# Generate tool adapters from the single rule source (rules/*.md and SOUL.md); see rules/README.md.
#   .cursor/rules/<name>.mdc   real copies (Cursor needs real .mdc files)
#   .cursor/rules/05-soul.mdc  SOUL.md wrapped in alwaysApply frontmatter
#   .cursor/rules/README.md    "generated directory" notice
#   .claude/rules/<name>.md    symlinks to ../../rules/<name>.md
# Usage: scripts/sync-rules.sh           regenerate the adapters
#        scripts/sync-rules.sh --check   exit 1 if the adapters do not match the sources
set -eu
cd "$(git rev-parse --show-toplevel)"
mode=${1:-sync}
expected=$(mktemp -d)
trap 'rm -rf "$expected"' EXIT

for src in rules/*.md; do
  name=$(basename "$src" .md)
  [ "$name" = README ] && continue
  cp "$src" "$expected/$name.mdc"
done
{
  printf '%s\n' '---' 'description: 项目之魂（由 scripts/sync-rules.sh 从 SOUL.md 生成，勿直接编辑）' 'alwaysApply: true' '---' ''
  cat SOUL.md
} > "$expected/05-soul.mdc"
printf '%s\n' '# 生成目录，勿直接编辑' '' \
  '本目录由 `scripts/sync-rules.sh` 从 `rules/*.md` 与 `SOUL.md` 生成。规则的唯一源与维护流程见 `rules/README.md`。' \
  > "$expected/README.md"

if [ "$mode" = "--check" ]; then
  stale=0
  for f in "$expected"/*; do
    n=$(basename "$f")
    cmp -s "$f" ".cursor/rules/$n" || { echo "stale or missing: .cursor/rules/$n"; stale=1; }
  done
  for f in .cursor/rules/*; do
    [ -e "$f" ] || continue
    [ -e "$expected/$(basename "$f")" ] || { echo "unexpected: $f"; stale=1; }
  done
  for src in rules/*.md; do
    n=$(basename "$src")
    [ "$n" = README.md ] && continue
    [ "$(readlink ".claude/rules/$n" 2>/dev/null || true)" = "../../rules/$n" ] || { echo "missing or wrong symlink: .claude/rules/$n"; stale=1; }
  done
  for f in .claude/rules/*; do
    [ -e "$f" ] || [ -L "$f" ] || continue
    n=$(basename "$f")
    { [ "$n" != README.md ] && [ -f "rules/$n" ]; } || { echo "unexpected: $f"; stale=1; }
  done
  [ "$stale" -eq 0 ] && echo "rule adapters are up to date" || echo "run scripts/sync-rules.sh, then stage rules/ .cursor/rules/ .claude/rules/"
  exit "$stale"
fi

mkdir -p .cursor/rules .claude/rules
find .cursor/rules -maxdepth 1 -type f \( -name '*.mdc' -o -name README.md \) -delete
cp "$expected"/* .cursor/rules/
find .claude/rules -maxdepth 1 -type l -delete
for src in rules/*.md; do
  n=$(basename "$src")
  [ "$n" = README.md ] && continue
  ln -s "../../rules/$n" ".claude/rules/$n"
done
echo "synced: $(ls .cursor/rules | wc -l) files in .cursor/rules, $(ls .claude/rules | wc -l) links in .claude/rules"

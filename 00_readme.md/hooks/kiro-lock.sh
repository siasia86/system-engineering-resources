#!/bin/bash
# kiro-lock preToolUse hook
# on/off: touch ~/.kiro/hooks/kiro-lock.disabled  (off)
#         rm ~/.kiro/hooks/kiro-lock.disabled      (on)

[ -f "$HOME/.kiro/hooks/kiro-lock.disabled" ] && exit 0

LOCK_DIR=""
D="${TOOL_INPUT_path:-.}"
while [ "$D" != "/" ]; do
  D=$(dirname "$D")
  test -d "$D/.git" 2>/dev/null && LOCK_DIR="$D" && break
done
[ -z "$LOCK_DIR" ] && exit 0

LOCK="$LOCK_DIR/.kiro-lock"
if [ -f "$LOCK" ]; then
  LOCK_USER=$(grep "^user:" "$LOCK" 2>/dev/null | cut -d" " -f2)
  if [ "$LOCK_USER" != "$(whoami)" ]; then
    echo "⚠️ LOCKED by $LOCK_USER in $LOCK_DIR — $(grep 'started:' "$LOCK" | cut -d' ' -f2-)" >&2
    exit 1
  fi
else
  printf "user: $(whoami)\nhost: $(hostname)\nstarted: $(date -Iseconds)\nsession: $$\n" > "$LOCK"
fi

#!/bin/bash
# kiro-lock preToolUse hook
# off: touch ~/.kiro/hooks/kiro-lock.disabled
# on:  rm ~/.kiro/hooks/kiro-lock.disabled

[ -f "$HOME/.kiro/hooks/kiro-lock.disabled" ] && exit 0

D="${TOOL_INPUT_path:-.}"
[ "$D" = "." ] && D="$(pwd)"

LOCK_DIR=""
COUNT=0
while [ "$D" != "/" ] && [ $COUNT -lt 10 ]; do
  D=$(dirname "$D")
  [ -d "$D/.git" ] && LOCK_DIR="$D" && break
  COUNT=$((COUNT + 1))
done
[ -z "$LOCK_DIR" ] && exit 0

LOCK="$LOCK_DIR/.kiro-lock"
if [ -f "$LOCK" ]; then
  LOCK_USER=$(grep "^user:" "$LOCK" 2>/dev/null | cut -d" " -f2)
  if [ "$LOCK_USER" != "$(whoami)" ]; then
    echo "⚠️ LOCKED by $LOCK_USER in $LOCK_DIR" >&2
    exit 1
  fi
else
  printf "user: %s\nhost: %s\nstarted: %s\nsession: %s\n" \
    "$(whoami)" "$(hostname)" "$(date -Iseconds)" "$$" > "$LOCK"
fi
exit 0

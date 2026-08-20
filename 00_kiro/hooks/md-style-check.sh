#!/bin/bash
# md-style-check postToolUse hook
# .md 파일 수정 시 자동으로 md-style-check.py 실행
# 이슈 0건: 조용히 통과
# 이슈 N건: stderr로 경고 출력 (에이전트 인지)
#
# 비활성화: touch ~/.kiro/hooks/md-style-check.disabled
# 재활성화: rm ~/.kiro/hooks/md-style-check.disabled

[ -f "$HOME/.kiro/hooks/md-style-check.disabled" ] && exit 0
[ -z "$TOOL_INPUT_path" ] && exit 0
echo "$TOOL_INPUT_path" | grep -q '\.md$' || exit 0
[ ! -f "$TOOL_INPUT_path" ] && exit 0

RESULT=$(sudo python3 /root/32_system-engineering-resources/md-style-check.py "$TOOL_INPUT_path" 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | tail -1)
COUNT=$(echo "$RESULT" | grep -oP '이슈: \K[0-9]+')

if [ -n "$COUNT" ] && [ "$COUNT" -gt 0 ]; then
  echo "⚠️ md-style-check: $TOOL_INPUT_path — ${COUNT}건 이슈" >&2
fi

exit 0

#!/bin/bash
# Markdown Style Check Script. In Ubuntu-24.04
# Requires: bash 4.0+, python3 3.6+ (tested on Python 3.12.3)
# Created by sjyun on 2026-05-04. Version 26.5.4 Modified by sjyun on 2026-05-04.
#
# STYLE.md 규칙 10 기준 반말체 종결어미 / 과장 표현 검사
# 코드블록(```) 내부는 검사 제외
#
# 사용법:
#   ./md-style-check.sh [--strict] [PATH]
#
#   ./md-style-check.sh                        # 현재 디렉토리 (화이트리스트 적용)
#   ./md-style-check.sh ./09_database          # 특정 디렉토리
#   ./md-style-check.sh --strict ./            # 화이트리스트 무시, raw 검출
#   ./md-style-check.sh --strict ./06_security # strict + 특정 디렉토리

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

STRICT=0
ISSUE_COUNT=0
FILE_COUNT=0
MAX_LINES=50

# ---------------------------------------------------------------------------
# parse_args — 인수 파싱 (--strict 플래그 + PATH)
# ---------------------------------------------------------------------------
parse_args() {
    SCAN_TARGET="."
    for arg in "$@"; do
        case "$arg" in
            --strict|-s) STRICT=1 ;;
            *)        SCAN_TARGET="$arg" ;;
        esac
    done
}

# ---------------------------------------------------------------------------
# collect_files — 검사 대상 .md 파일 목록을 MD_FILES 배열에 수집
# ---------------------------------------------------------------------------
collect_files() {
    if [ -f "$SCAN_TARGET" ]; then
        mapfile -t MD_FILES < <(echo "$SCAN_TARGET")
    else
        mapfile -t MD_FILES < <(find "$SCAN_TARGET" -name "*.md" -not -path "*/.git/*" | sort)
    fi
}

# ---------------------------------------------------------------------------
# print_issues FILE ISSUES HIGHLIGHT_SED
# ---------------------------------------------------------------------------
print_issues() {
    local md_file="$1"
    local issues="$2"
    local hl_sed="$3"

    echo -e "  ${PURPLE}${md_file}${NC}"
    echo "$issues" | head -"$MAX_LINES" | while IFS=: read -r lineno content; do
        local highlighted
        highlighted=$(echo "$content" | sed -E "$hl_sed")
        echo -e "    ${YELLOW}L${lineno}${NC}: ${highlighted}"
    done
    echo ""
}

# ---------------------------------------------------------------------------
# check_banmal — [1/2] 반말체 종결어미 검사
# ---------------------------------------------------------------------------
check_banmal() {
    echo "[1/2] 반말체 종결어미 검사..."
    echo ""

    for md_file in "${MD_FILES[@]}"; do
        local file_issues
        file_issues=$(python3 - "$md_file" << 'PYEOF'
import sys, re

path = sys.argv[1]
try:
    with open(path) as f:
        lines = f.readlines()
except:
    sys.exit(0)

patterns = [
    r'[가-힣]이다[.\s]',
    r'[가-힣]한다[.\s]',
    r'[가-힣]된다[.\s]',
    r'[가-힣]있다[.\s]',
    r'[가-힣]없다[.\s]',
    r'[가-힣]않는다[.\s]',
    r'[가-힣]아니다[.\s]',
]
combined = re.compile('|'.join(patterns))

in_code = False
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped.startswith('```'):
        in_code = not in_code
        continue
    if in_code:
        continue
    if (not stripped
            or stripped.startswith('#')
            or stripped.startswith('|')
            or stripped.startswith('*')
            or stripped.startswith('!')
            or stripped.startswith('>')
            or stripped.startswith('©')):
        continue
    if re.search(r'[가-힣]', stripped) and combined.search(stripped):
        print(f"{i}:{stripped[:100]}")
PYEOF
        )

        if [ -n "$file_issues" ]; then
            local hl="s/(이다[. ]|한다[. ]|된다[. ]|있다[. ]|없다[. ]|않는다[. ]|아니다[. ])/$(printf '\033[0;31m')\1$(printf '\033[0m')/g"
            print_issues "$md_file" "$file_issues" "$hl"
            ((ISSUE_COUNT++)) || true
            ((FILE_COUNT++)) || true
        fi
    done
}

# ---------------------------------------------------------------------------
# check_exaggeration — [2/2] 과장 표현 검사
#   STRICT=1 이면 화이트리스트 무시
# ---------------------------------------------------------------------------
check_exaggeration() {
    if [ "$STRICT" -eq 1 ]; then
        echo "[2/2] 과장 표현 검사 (완전/완벽/최고/최강) [strict — 화이트리스트 무시]..."
    else
        echo "[2/2] 과장 표현 검사 (완전/완벽/최고/최강)..."
    fi
    echo ""

    for md_file in "${MD_FILES[@]}"; do
        local file_issues
        local file_issues file_filtered
        file_issues=$(STRICT="$STRICT" python3 - "$md_file" << 'PYEOF'
import sys, re, os

path = sys.argv[1]
strict = os.environ.get('STRICT', '0') == '1'

try:
    with open(path) as f:
        lines = f.readlines()
except:
    sys.exit(0)

pattern = re.compile(r'완전한|완벽한|최고의|최강의|완전 |완벽 |최고 |최강 ')
whitelist = re.compile(
    r'완전 이진|완전 그래프|완전 격리|완전 지원|완전 일관성|완전 오버라이딩'
    r'|최고 추론|최고 성능.*→'
    r'|완전한 하드웨어|완전한 제어|완전한 자유 소프트웨어|완전한 빌드'
    r'|최고 \|'
)

in_code = False
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped.startswith('```'):
        in_code = not in_code
        continue
    if in_code:
        continue
    if re.search(r'[가-힣]', stripped) and pattern.search(stripped):
        if strict or not whitelist.search(stripped):
            print(f"ISSUE:{i}:{stripped[:100]}")
        elif whitelist.search(stripped):
            print(f"FILTERED:{i}:{stripped[:100]}")
PYEOF
        )
        file_filtered=$(echo "$file_issues" | grep "^FILTERED:" | sed 's/^FILTERED://')
        file_issues=$(echo "$file_issues" | grep "^ISSUE:" | sed 's/^ISSUE://')

        if [ -n "$file_issues" ]; then
            local hl="s/(완전한|완벽한|최고의|최강의|완전 |완벽 |최고 |최강 )/$(printf '\033[0;31m')\1$(printf '\033[0m')/g"
            print_issues "$md_file" "$file_issues" "$hl"
            ((ISSUE_COUNT++)) || true
        fi
        if [ -n "$file_filtered" ]; then
            echo -e "  ${YELLOW}(whitelist) ${PURPLE}${md_file}${NC}"
            echo "$file_filtered" | head -"$MAX_LINES" | while IFS=: read -r lineno content; do
                local highlighted
                highlighted=$(echo "$content" | sed -E "s/(완전한|완벽한|최고의|최강의|완전 |완벽 |최고 |최강 )/$(printf '\033[1;33m')\1$(printf '\033[0m')/g")
                echo -e "    ${YELLOW}L${lineno}${NC}: ${highlighted}"
            done
            echo ""
        fi
    done
}

# ---------------------------------------------------------------------------
# print_summary — 결과 요약 출력
# ---------------------------------------------------------------------------
print_summary() {
    echo "=========================================="
    echo "Summary"
    echo "=========================================="
    echo "Scanned: ${#MD_FILES[@]} files"
    echo ""

    if [ $ISSUE_COUNT -eq 0 ]; then
        echo -e "${GREEN}✓ No style issues found!${NC}"
        echo ""
        echo "모든 파일이 STYLE.md 규칙 10을 준수합니다."
        exit 0
    else
        echo -e "${RED}✗ Found issues in $FILE_COUNT file(s)${NC}"
        echo ""
        echo "수정 방법:"
        echo "  ~이다.   → ~입니다."
        echo "  ~한다.   → ~합니다."
        echo "  ~된다.   → ~됩니다."
        echo "  ~있다.   → ~있습니다."
        echo "  ~없다.   → ~없습니다."
        echo "  ~않는다. → ~않습니다."
        echo "  ~아니다. → ~아닙니다."
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
main() {
    parse_args "$@"

    echo "=========================================="
    echo "Markdown Style Check (반말체 종결어미)"
    if [ "$STRICT" -eq 1 ]; then
        echo -e "Mode: ${CYAN}--strict${NC} (화이트리스트 무시)"
    fi
    echo "=========================================="
    echo "Scan Target: $SCAN_TARGET"
    echo ""

    collect_files
    check_banmal
    check_exaggeration
    print_summary
}

main "$@"

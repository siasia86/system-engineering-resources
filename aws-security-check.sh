#!/bin/bash
# Security check, prevent committing AWS credentials before push. In Ubuntu-24.04
# Created by sjyun on 2026-04-14. Version 26.4.15 Modified by sjyun on 2026-04-15.
#
# It is recommended to mask sensitive data 
# Subject of processing : Access Key, Account ID, ARN, VPCE, .map.json
#

# color
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
PURPLE='\033[0;35m'
NC='\033[0m'

SCAN_DIR="${1:-.}"
ISSUE_COUNT=0

# test file grep
grep_files() {
    local pattern="$1"
    local flag="${2:--InoE}"
    find "$SCAN_DIR" \
        -type d \( -name '.git' -o -path '*/02_fio*' -o -path '*/fio_ORG*' \) -prune -o \
        ! -name '*.tar' ! -name '*.tar.gz' ! -name '*.tgz' \
        ! -name '*.zip' ! -name '*.jar' ! -name '*.png' \
        ! -name '*.jpg' ! -name '*.jpeg' ! -name '*.gif' \
        ! -name '*.pdf' ! -name '*.bin' ! -name '*.out' \
        ! -name '*.bak' ! -name '*.trn' ! -name '*.swp' \
        ! -name '*.swo' ! -name '*.log' ! -name '*.sql' \
        ! -name '*.map.json' ! -name '*.map.json.bak.*' ! -name 'aws-security-check.sh' \
        ! -name 'git-security-check.sh' ! -name 'json_mask.py' \
        -type f -print0 2>/dev/null | \
        xargs -0 grep $flag "$pattern" 2>/dev/null || true
}

echo "=========================================="
echo "AWS Security Check"
echo "=========================================="
echo "Scan Directory: $SCAN_DIR"
echo ""

# 1. AWS Access Key ID (AKIA...)
echo "[1/6] Checking for AWS Access Key IDs..."
results=$(grep_files '(AKIA|ASIA|AROA|AIDA|ANPA|ANVA|APKA)[A-Z0-9]{16}')
if [ -n "$results" ]; then
    echo -e "${RED}  ✗ Found AWS Access Key IDs:${NC}"
    echo "$results"  | while IFS=: read -r file line content; do
        echo -e "    ${PURPLE}$file${NC}:${line}: $content"
    done
    ((ISSUE_COUNT++)) || true
else
    echo -e "${GREEN}  ✓ No Access Key IDs found${NC}"
fi

# 2. AWS Secret Access Key pattern
echo ""
echo "[2/6] Checking for AWS Secret Access Keys..."
results=$(grep_files '(aws_secret|secret_access_key|SecretAccessKey)\s*[=:]\s*\S{20,}' | \
    grep -iv 'example\|placeholder\|<\|your_\|xxxx' || true)
if [ -n "$results" ]; then
    echo -e "${RED}  ✗ Found potential Secret Access Keys:${NC}"
    echo "$results"  | while IFS=: read -r file line content; do
        echo -e "    ${PURPLE}$file${NC}:${line}: $content"
    done
    ((ISSUE_COUNT++)) || true
else
    echo -e "${GREEN}  ✓ No Secret Access Keys found${NC}"
fi

# 3. AWS Account ID (a 12-digit number, not masking)
echo ""
echo "[3/6] Checking for unmasked AWS Account IDs (12-digit)..."
results=$(grep_files '[^0-9:][0-9]{12}[^0-9:]' | \
    grep -v '<ACCOUNT-ID' | \
    grep -vE '[0-9a-fA-F]{12}'  | \
    grep -vE '[0-9]{12}[UuLl]'  | \
    grep -vE '[-][0-9]{12}'     | \
    grep -vE '[0-9]{12}[-]'     | \
    grep -vE '/[0-9]{12}/'      | \
    grep -vE '0x[0-9a-fA-F]'    | \
    grep -vE '20[0-9]{2}[01][0-9][0-3][0-9][0-2][0-9][0-5][0-9]' || true)
if [ -n "$results" ]; then
    echo -e "${YELLOW}  ⚠ Found 12-digit numbers (potential Account IDs):${NC}"
    echo "$results"  | while IFS=: read -r file line content; do
        echo -e "    ${PURPLE}$file${NC}:${line}: $content"
    done
    echo "  → mask_json.py 로 마스킹 권장"
    ((ISSUE_COUNT++)) || true
else
    echo -e "${GREEN}  ✓ No unmasked Account IDs found${NC}"
fi

# 4. ARN (not masking)
echo ""
echo "[4/6] Checking for unmasked ARNs..."
results=$(grep_files 'arn:aws:[a-z0-9\-]+:[a-z0-9\-]*:[0-9]{12}:')
if [ -n "$results" ]; then
    echo -e "${YELLOW}  ⚠ Found unmasked ARNs with Account IDs:${NC}"
    echo "$results"  | while IFS=: read -r file line content; do
        echo -e "    ${PURPLE}$file${NC}:${line}: $content"
    done
    echo "  → mask_json.py 로 마스킹 권장"
    ((ISSUE_COUNT++)) || true
else
    echo -e "${GREEN}  ✓ No unmasked ARNs found${NC}"
fi

# 5. VPCE ID (not masking)
echo ""
echo "[5/6] Checking for unmasked VPCE IDs..."
results=$(grep_files 'vpce-[0-9a-f]{8,}')
if [ -n "$results" ]; then
    echo -e "${YELLOW}  ⚠ Found unmasked VPCE IDs:${NC}"
    echo "$results"  | while IFS=: read -r file line content; do
        echo -e "    ${PURPLE}$file${NC}:${line}: $content"
    done
    echo "  → mask_json.py 로 마스킹 권장"
    ((ISSUE_COUNT++)) || true
else
    echo -e "${GREEN}  ✓ No unmasked VPCE IDs found${NC}"
fi

# 6. Check if .map.json files are tracked by Git
echo ""
echo "[6/6] Checking for tracked .map.json files..."
if git -C "$SCAN_DIR" rev-parse --git-dir > /dev/null 2>&1; then
    tracked=$(git -C "$SCAN_DIR" ls-files | grep -E '\.map\.json(\.bak\.[0-9]+)?$' || true)
    if [ -n "$tracked" ]; then
        echo -e "${RED}  ✗ .map.json files are tracked by git:${NC}"
        echo "$tracked" | while read -r file; do
            echo -e "    ${PURPLE}$file${NC}"
        done
        echo "  → .gitignore에 추가 필요:"
        echo "      *.map.json"
        echo "      *.map.json.bak.*"
        ((ISSUE_COUNT++)) || true
    else
        echo -e "${GREEN}  ✓ No .map.json files tracked${NC}"
    fi
else
    echo "  (git 저장소 아님, 건너뜀)"
fi

# Summary of Results
echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="

if [ $ISSUE_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ No AWS security issues found!${NC}"
    echo ""
    echo "Safe to commit."
    exit 0
else
    echo -e "${RED}✗ Found $ISSUE_COUNT AWS security issue(s)${NC}"
    echo ""
    echo "권장 조치:"
    echo "  1. Access Key → 즉시 삭제 및 재발급 (노출된 키는 무효화)"
    echo "  2. 계정 ID / ARN / VPCE → python mask_json.py 로 마스킹"
    echo "  3. .map.json → .gitignore에 추가"
    echo ""
    echo "  .gitignore 추가:"
    echo "    *.map.json"
    echo "    *.map.json.bak.*"
    exit 1
fi

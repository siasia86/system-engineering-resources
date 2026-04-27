#!/bin/bash
# Git Security Check Script. In Ubuntu-24.04
# Created by sjyun on 2026-02-02. Version 26.4.27 Modified by sjyun on 2026-04-27.
#
# 커밋 전 민감 정보 및 대용량 파일 검사
#
# rsync -av /home/sjyun/.kiro/ /root/sj_del/00_default/.kiro/  --exclude .cli_bash_history
# rsync -av /root/32_system-engineering-resources/ /root/sj_del/32_readme.md/ --exclude=.git
#
#

echo "### git status --ignored ###"
git status --ignored --untracked-files=all
echo "### git status --ignored ###"

set -e

# color
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
PURPLE='\033[0;35m'
# No Color
NC='\033[0m'

# config
MAX_FILE_SIZE="40M"
SCAN_DIR="${1:-.}"
MAX_LINES=30          # 섹션별 최대 출력 라인 수

# count
ISSUE_COUNT=0

echo "=========================================="
echo "Git Security Check"
echo "=========================================="
echo "Scan Directory: $SCAN_DIR"
echo ""

# 1. Check for sensitive IP addresses
echo "[1/5] Checking for sensitive IP addresses..."
SENSITIVE_IPS=(
    '\b61\.10[01]\.[0-9]{1,3}\.[0-9]{1,3}\b'
    '\b112\.185\.[0-9]{1,3}\.[0-9]{1,3}\b'
    '\b10\.211\.[0-9]{1,3}\.[0-9]{1,3}\b'
    '\b3\.112\.[0-9]{1,3}\.[0-9]{1,3}\b'
)

for ip_pattern in "${SENSITIVE_IPS[@]}"; do
    echo "  Searching for: $ip_pattern"
    
    results=$(find "$SCAN_DIR" -type d -name ".git" -prune -o \
        ! \( -name "git-security-check.sh" \
            -o -name "aws-security-check.sh" \
            -o -name "gitlab.rb" \
            -o -name "GITHUB_UPLOAD_GUIDE.md" \
            -o -name "*.tar" \
            -o -name "*.tar.gz" \
            -o -name "*.tgz" \
            -o -name "*.png" \
            -o -name "*.jpg" \
            -o -name "*.jpeg" \
            -o -name "*.gif" \
            -o -name "*.zip" \
            -o -name "*.jar" \
            -o -name "*.pdf" \
            -o -name "*.out" \
            -o -name "*.bin" \
            -o -name "*.bak" \
            -o -name "*.trn" \
            -o -name "*.swp" \
            -o -name "*.swo" \
            -o -name "*.log" \
			-o -name "*.map.json" \
			-o -name "*_rsyncd.conf" \
			-o -name "*rsyslog.conf" \
        \) -type f -print0 2>/dev/null | \
        xargs -0 grep -IlE "$ip_pattern" 2>/dev/null || true)
    
    if [ -n "$results" ]; then
        echo -e "${RED}  ✗ Found IP pattern: $ip_pattern${NC}"
        echo "$results" | while read -r file; do
            echo -e "    - ${PURPLE}$file${NC}"
			grep -nE "$ip_pattern" "$file" 2>/dev/null | head -$MAX_LINES | while IFS=: read -r line_num content; do
                # IP pattern in red color
                highlighted=$(echo "$content" | sed -E "s/($ip_pattern)/\\o033[0;31m\1\\o033[0m/g")
                echo -e "      ${line_num}:${highlighted}"
            done
        done
        ((ISSUE_COUNT++)) || true
    fi
done

# 2. Check for password/key patterns
echo ""
echo "[2/5] Checking for passwords and keys..."
SENSITIVE_PATTERNS=(
    "password.*=.*['\"]"
    "passwd.*=.*['\"]"
    "api[_-]?key.*=.*['\"]"
    "secret.*=.*['\"]"
    "token.*=.*['\"]"
    "aws_access_key"
    "aws_secret"
    "private[_-]?key"
    "BEGIN.*PRIVATE.*KEY"
)

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    # 전체 매칭 결과 (필터 전)
    raw=$(find "$SCAN_DIR" -type d -name ".git" -prune -o \
        ! \( -name "git-security-check.sh" \
            -o -name "aws-security-check.sh" \
            -o -name "gitlab.rb" \
            -o -name "GITHUB_UPLOAD_GUIDE.md" \
            -o -name "*.tar" \
            -o -name "*.tar.gz" \
            -o -name "*.png" \
            -o -name "*.zip" \
            -o -name "*.jar" \
            -o -name "*.pdf" \
            -o -name "*.bak" \
            -o -name "*.trn" \
            -o -name "*.swp" \
        \) -type f -print0 2>/dev/null | \
        xargs -0 grep -IiHE "$pattern" 2>/dev/null | \
        grep -v "^\s*#" || true)

    # 필터 적용 후 실제 이슈
    results=$(echo "$raw" | \
        grep -v "example" | \
        grep -v "placeholder" | \
        grep -v "SecurePassword123" | \
        grep -v "SecureToken123" | \
        grep -v "SecureKey123" | \
        grep -v "Secureuser123" | \
        grep -v "your_password" | \
        grep -v "='secret'" | \
        grep -v "비밀번호" | \
        grep -v '="$' | \
        grep -vE '=["'"'"'](\$|\$\{)' | \
        grep -vE '=\$?\(' || true)

    # 필터로 제거된 항목
    filtered=$(comm -23 \
        <(echo "$raw" | grep -v "^$" | sort) \
        <(echo "$results" | grep -v "^$" | sort) 2>/dev/null || true)
    
    if [ -n "$results" ]; then
        echo -e "${YELLOW}  ✗ Found pattern: $pattern${NC}"
		echo "$results" | head -$MAX_LINES | while IFS=: read -r file content; do
            # pattern in red
            highlighted=$(echo "$content" | sed -E "s/($pattern)/\\o033[0;31m\1\\o033[0m/gi")
            echo -e "    ${PURPLE}$file${NC}:${highlighted}"
        done
        ((ISSUE_COUNT++)) || true
    fi

    if [ -n "$filtered" ]; then
        echo -e "${GREEN}  ✓ Filtered out (excluded patterns):${NC}"
		echo "$filtered" | head -$MAX_LINES | while IFS=: read -r file content; do
            # 제외된 패턴 부분만 노란색 하이라이트
            highlighted="$content"
            for excl in "SecurePassword123" "SecureToken123" "SecureKey123" "Secureuser123" \
                        "your_password" "example" "placeholder" "비밀번호" "='secret'"; do
                highlighted=$(echo "$highlighted" | sed "s|${excl}|$(printf '\033[1;33m')${excl}$(printf '\033[0m')|g")
            done
            # 변수 참조/명령치환 패턴 하이라이트
            highlighted=$(echo "$highlighted" | sed -E "s|(=[\"'][\$][A-Za-z_{(][^\"' ]*)|$(printf '\033[1;33m')\1$(printf '\033[0m')|g")
            highlighted=$(echo "$highlighted" | sed -E "s|(=[\$][(][^)]*[)])|$(printf '\033[1;33m')\1$(printf '\033[0m')|g")
            echo -e "    ${GREEN}$file${NC}:${highlighted}"
        done
    fi
done

# 3. Check for AWS account IDs
echo ""
echo "[3/5] Checking for AWS Account IDs..."
results=$(find "$SCAN_DIR" -type d \( -name ".git" -o -path "*/02_fio*" \) -prune -o \
    ! \( -name "git-security-check.sh" \
        -o -name "aws-security-check.sh" \
        -o -name "gitlab.rb" \
        -o -name "GITHUB_UPLOAD_GUIDE.md" \
        -o -name "*.tar" \
        -o -name "*.tar.gz" \
        -o -name "*.png" \
        -o -name "*.zip" \
        -o -name "*.bak" \
        -o -name "*.trn" \
        -o -name "*.swp" \
		-o -name "*.map.json" \
    \) -type f -print0 2>/dev/null | \
    xargs -0 grep -IoE "[0-9]{12}" 2>/dev/null | \
    sort -t: -k2 -u || true)

if [ -n "$results" ]; then
    echo -e "${YELLOW}  ⚠ Found 12-digit numbers (potential AWS Account IDs):${NC}"
    echo "$results" | head -$MAX_LINES | while IFS=: read -r file match; do
        echo -e "    ${PURPLE}${file}${NC}:${match}"
    done
    echo "  Please verify these are not sensitive account IDs"
fi

# 5. Check for sensitive filenames
echo ""
echo "[4/5] Checking for large files (>$MAX_FILE_SIZE)..."
large_files=$(find "$SCAN_DIR" -type d -name ".git" -prune -o \
    -type f -size +$MAX_FILE_SIZE -print 2>/dev/null || true)

if [ -n "$large_files" ]; then
    echo -e "${RED}  ✗ Found large files:${NC}"
    echo "$large_files" | while read -r file; do
        size=$(du -h "$file" | cut -f1)
        echo -e "    - ${PURPLE}$file${NC} ($size)"
    done
    ((ISSUE_COUNT++)) || true
else
    echo -e "${GREEN}  ✓ No large files found${NC}"
fi

# 5. Check for sensitive filenames
echo ""
echo "[5/5] Checking for sensitive filenames..."
SENSITIVE_FILES=(
    "*.pem"
    "*.key"
    "*.p12"
    "*.pfx"
    "*.jks"
    "id_rsa"
    "id_dsa"
    "*.env"
    ".env.*"
    "credentials"
    "secret*"
)

for pattern in "${SENSITIVE_FILES[@]}"; do
    results=$(find "$SCAN_DIR" -type d \( -name ".git" -o -path "*/06_docker/02_n8n_docker*" \) -prune -o \
        -type f -name "$pattern" -print 2>/dev/null || true)
    
    if [ -n "$results" ]; then
        echo -e "${RED}  ✗ Found sensitive files: $pattern${NC}"
        echo "$results" | while read -r file; do
            echo -e "    ${PURPLE}$file${NC}"
        done
        ((ISSUE_COUNT++)) || true
    fi
done

# Summary of Results
echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="

if [ $ISSUE_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ No security issues found!${NC}"
    echo ""
    echo "Safe to commit."
    exit 0
else
    echo -e "${RED}✗ Found $ISSUE_COUNT security issue(s)${NC}"
    echo ""
    echo "Please review and fix the issues above before committing."
    echo ""
    echo "Common fixes:"
    echo "  1. Remove sensitive IPs and replace with placeholders"
    echo "  2. Use environment variables for passwords/keys"
    echo "  3. Add large files to .gitignore"
    echo "  4. Move credentials to .env files (and add to .gitignore)"
    exit 1
fi

#!/usr/bin/env python3
#import sys; sys.exit(0)  # SAFETY: uncomment this line to disable script
"""
md-style-check.py — Markdown 스타일 검사 도구
STYLE.md 규칙 기반: 표 정렬, 다이어그램 폭, 코드블록 언어 태그, H1 개수, 푸터, _reference 전용 항목

사용법:
  python3 md-style-check.py <file_or_dir> [--strict|-s]
  python3 md-style-check.py -V
"""

VERSION = "26.05.26"

import os
import re
import sys
import unicodedata
import argparse

# ── 컬러 ──────────────────────────────────────────────────────────────────────

RED    = '\033[0;31m'
GREEN  = '\033[0;32m'
YELLOW = '\033[1;33m'
PURPLE = '\033[0;35m'
CYAN   = '\033[0;36m'
NC     = '\033[0m'

# ── 유틸 ──────────────────────────────────────────────────────────────────────

def dw(s):
    """display width: 한글/전각=2, 나머지=1. 인라인 코드 백틱 포함."""
    w = 0
    for c in s:
        if '\uAC00' <= c <= '\uD7A3' or unicodedata.east_asian_width(c) in ('W', 'F'):
            w += 2
        else:
            w += 1
    return w

def split_table_row(line):
    """표 행을 열로 분할. 백틱 내부의 | 는 무시."""
    stripped = line.strip().strip("|")
    cells = []
    current = ""
    in_backtick = False
    for c in stripped:
        if c == "`":
            in_backtick = not in_backtick
            current += c
        elif c == "|" and not in_backtick:
            cells.append(current)
            current = ""
        else:
            current += c
    cells.append(current)
    return cells

def strip_code_blocks(content):
    """코드블록(``` ```) 제거 후 반환. frontmatter(---) 보존."""
    return re.sub(r'```[^\n]*\n.*?```', '', content, flags=re.DOTALL)

def get_code_blocks(content):
    """(lang, body) 튜플 리스트 반환."""
    return re.findall(r'```([^\n]*)\n(.*?)```', content, re.DOTALL)

def strip_frontmatter(content):
    """frontmatter 제거 후 반환."""
    return re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

# ── 검사 함수 ─────────────────────────────────────────────────────────────────

def check_h1(content, strict=False):
    """H1이 정확히 1개인지 확인."""
    body = strip_frontmatter(content)
    body = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    h1s = re.findall(r'^# .+', body, re.MULTILINE)
    if len(h1s) != 1:
        return [f"H1 {len(h1s)}개 (1개여야 함): {h1s}"]
    return []

# 출력 결과/UI 경로 패턴 (태그 없이 허용)
_OUTPUT_PATTERNS = re.compile(
    r'^(\d|\.\.\.|\[|SUCCESS|FAILED|ok:|changed:|fatal:|PLAY|TASK|\$|>|#|\*\*|Status|URL:|http)'
    r'|→|\| SUCCESS|\| FAILED|\| CHANGED'
    r'|^[A-Z][a-z]+ →'           # UI 경로 (Grafana →, Jenkins →)
    r'|Securing |Enter password|New password'  # 인터랙티브 출력
    r'|^Match |^Password|^Permit|^Allow|^Deny'  # sshd_config 등 설정
    r'|^(frontend|backend|global|listen|defaults)\b'  # haproxy 설정
    r'|^prefork:|^worker:|^event:'  # Apache MPM
)

def check_code_lang(content, strict=False):
    """언어 태그 없는 코드블록 검사.
    허용 목록: 트리/다이어그램, URL, 명령어 출력, UI 경로, 로그, 순수 텍스트 흐름."""
    issues = []
    for m in re.finditer(r'```([^\n]*)\n(.*?)```', content, re.DOTALL):
        lang = m.group(1).strip()
        body = m.group(2)
        if lang:
            continue
        # 트리/다이어그램 문자 포함 — 허용
        if any(c in body for c in ['├──', '└──', '│', '┌', '┐', '└', '┘', '─']):
            continue
        lines = [l for l in body.strip().splitlines() if l.strip()]
        if not lines:
            continue
        first_line = lines[0].strip()
        if first_line.startswith('http'):
            continue
        if first_line.startswith('#') or _OUTPUT_PATTERNS.search(first_line):
            continue
        match_count = sum(1 for l in lines if _OUTPUT_PATTERNS.search(l.strip()))
        if match_count >= len(lines) * 0.3:
            continue
        issues.append(f"언어 태그 없는 코드블록: '{first_line[:50]}'")
    return issues

def check_tables(content, strict=False):
    """표 정렬 검사: 셀 raw 길이 = col_max_dw + 2, 구분선 길이 = col_max_dw + 2."""
    issues = []
    clean = strip_code_blocks(content)
    clean = strip_frontmatter(clean)

    for m in re.finditer(r'((?:\|[^\n]+\|\n)+)', clean):
        block = m.group(1).strip().splitlines()
        if len(block) < 2:
            continue

        rows_raw = [split_table_row(l) for l in block]
        rows_str = [[c.strip() for c in r] for r in rows_raw]

        sep_idx = next(
            (i for i, r in enumerate(rows_str)
             if r and all(re.match(r'^-+$', c) for c in r if c)),
            None
        )
        if sep_idx is None:
            continue

        data_rows = [r for i, r in enumerate(rows_str) if i != sep_idx]
        if not data_rows:
            continue
        ncols = max(len(r) for r in data_rows)
        if ncols <= 1:
            continue
        col_widths = [
            max((dw(r[i]) if i < len(r) else 0) for r in data_rows)
            for i in range(ncols)
        ]

        for idx, (raw_row, str_row) in enumerate(zip(rows_raw, rows_str)):
            is_sep = str_row and all(re.match(r'^-+$', c) for c in str_row if c)
            if is_sep:
                for i, c in enumerate(str_row):
                    if i < ncols:
                        expected = col_widths[i] + 2
                        actual = len(c)
                        if actual != expected:
                            issues.append(
                                f"표 구분선 열{i+1}: 길이={actual}, 기대={expected} | '{block[idx][:60]}'"
                            )
            else:
                for i, raw_c in enumerate(raw_row):
                    if i < ncols:
                        cell_content = raw_c.strip()
                        expected_raw = 2 + len(cell_content) + col_widths[i] - dw(cell_content)
                        actual_raw = len(raw_c)
                        if actual_raw != expected_raw:
                            issues.append(
                                f"표 셀 열{i+1}: raw_len={actual_raw}, 기대={expected_raw} | '{cell_content}'"
                            )
    return issues

def check_diagram(content, strict=False):
    """닫힌 박스 다이어그램(┌...┐ ~ └...┘) 내부 행 display width 일치 여부.
    박스 밖 행(설명, 화살표 등)은 검사 제외."""
    issues = []
    for m in re.finditer(r'```[^\n]*\n(.*?)```', content, re.DOTALL):
        body = m.group(1)
        lines = body.splitlines()
        if not any(l.strip().startswith('┌') for l in lines):
            continue
        in_box = False
        box_lines = []
        for l in lines:
            if l.strip().startswith('┌'):
                in_box = True
                box_lines.append(l)
            elif in_box:
                box_lines.append(l)
                if '┘' in l:
                    if box_lines:
                        check_lines = [bl for bl in box_lines
                                       if bl.strip().startswith(('┌', '│', '└'))
                                       and '┼' not in bl
                                       and bl.strip().endswith(('┐', '│', '┘', '┤', '─'))]
                        if check_lines:
                            widths = [dw(bl) for bl in check_lines]
                            max_w = max(widths)
                            for bl, w in zip(check_lines, widths):
                                if w != max_w:
                                    issues.append(
                                        f"다이어그램 행 폭 불일치: dw={w} (최대={max_w}) | '{bl[:50]}'"
                                    )
                    box_lines = []
                    in_box = False
    return issues

def check_diagram_korean(content, strict=False):
    """박스 다이어그램(┌┐로 시작) 내부 한글 사용 여부 (STYLE.md § 5: 영문 권장)."""
    issues = []
    for m in re.finditer(r'```[^\n]*\n(.*?)```', content, re.DOTALL):
        body = m.group(1)
        lines = body.splitlines()
        if not any(l.strip().startswith('┌') or l.strip().startswith('┐') for l in lines):
            continue
        korean = re.findall(r'[가-힣]+', body)
        if korean:
            issues.append(f"다이어그램 내부 한글 사용: {korean[:3]} (영문 권장)")
    return issues

# 허용 이모지 목록
_EMOJI_PATTERN = re.compile(
    r'(' + '|'.join(re.escape(e) for e in ['✅', '❌', '🟡', '🟢', '🔴']) + r')([^\s|`])'
)

def check_emoji_space(content, strict=False):
    """이모지 뒤 공백 1칸 필수 검사 (STYLE.md § 7). 코드블록/표 셀 내 이모지 단독 사용 제외."""
    issues = []
    in_code = False
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        for emoji, next_char in _EMOJI_PATTERN.findall(stripped):
            issues.append(f"L{i}: '{emoji}' 뒤 공백 없음 → '{emoji}{next_char}'")
    return issues

def check_footer(content, strict=False):
    """README 푸터 존재 여부 (작성일, 마지막 업데이트, 저작권)."""
    issues = []
    if '**작성일**' not in content:
        issues.append("푸터 누락: **작성일** 없음")
    if '**마지막 업데이트**' not in content:
        issues.append("푸터 누락: **마지막 업데이트** 없음")
    if '© ' not in content:
        issues.append("푸터 누락: 저작권(©) 없음")
    return issues

# 반말체 종결어미 패턴
_BANMAL_PATTERN = re.compile(
    r'[가-힣]이다[.\s]|[가-힣]한다[.\s]|[가-힣]된다[.\s]|[가-힣]있다[.\s]'
    r'|[가-힣]없다[.\s]|[가-힣]않는다[.\s]|[가-힣]아니다[.\s]'
)

def check_banmal(content, strict=False):
    """반말체 종결어미 검사 (STYLE.md § 10). 코드블록/인용구/헤더/표 제외."""
    issues = []
    in_code = False
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if (not stripped
                or stripped.startswith(('#', '|', '*', '!', '>', '©', '-'))):
            continue
        if re.search(r'[가-힣]', stripped) and _BANMAL_PATTERN.search(stripped):
            issues.append(f"L{i}: {stripped[:80]}")
    return issues

# 과장 표현 패턴
_EXAGGERATION_PATTERN  = re.compile(r'완전한|완벽한|최고의|최강의|완전 |완벽 |최고 |최강 ')
_EXAGGERATION_WHITELIST = re.compile(
    r'완전 이진|완전 그래프|완전 격리|완전 지원|완전 일관성|완전 오버라이딩'
    r'|최고 추론|최고 성능.*→'
    r'|완전한 하드웨어|완전한 제어|완전한 자유 소프트웨어|완전한 빌드|완전한 데이터'
    r'|최고 \|'
)

def check_exaggeration(content, strict=False):
    """과장 표현 검사 (STYLE.md § 10). 코드블록 제외."""
    issues = []
    in_code = False
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if re.search(r'[가-힣]', stripped) and _EXAGGERATION_PATTERN.search(stripped):
            if strict or not _EXAGGERATION_WHITELIST.search(stripped):
                issues.append(f"L{i}: {stripped[:80]}")
    return issues

def check_reference(content, path, strict=False):
    """_reference/ 파일 전용 검사."""
    issues = []
    if '_reference' not in path:
        return issues
    fm = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm:
        issues.append("_reference: frontmatter 없음")
        return issues
    fm_text = fm.group(1)
    if 'sources:' not in fm_text:
        issues.append("_reference: frontmatter에 sources 없음")
    if 'last_checked:' not in fm_text:
        issues.append("_reference: frontmatter에 last_checked 없음")
    return issues

# ── 검사 목록 ─────────────────────────────────────────────────────────────────

CHECKS = [
    ("H1 개수",          check_h1),
    ("코드블록 언어 태그", check_code_lang),
    ("표 정렬",           check_tables),
    ("다이어그램 행 폭",  check_diagram),
    ("다이어그램 한글",   check_diagram_korean),
    ("이모지 뒤 공백",    check_emoji_space),
    ("반말체 종결어미",   check_banmal),
    ("과장 표현",         check_exaggeration),
    ("푸터",              check_footer),
    ("_reference 규칙",  check_reference),
]

# _reference 파일은 푸터 불필요
REFERENCE_SKIP = {"푸터"}
# INDEX.md는 _reference 규칙 적용 제외
INDEX_SKIP = {"_reference 규칙"}

# ── 파일 처리 ─────────────────────────────────────────────────────────────────

def check_file(path, strict=False):
    """단일 파일 검사. [(항목명, 이슈메시지), ...] 반환."""
    try:
        with open(path) as f:
            content = f.read()
    except Exception as e:
        return [("파일 읽기", f"실패: {e}")]

    is_reference = '_reference' in path
    is_index = os.path.basename(path) == 'INDEX.md'
    all_issues = []

    for name, fn in CHECKS:
        if is_reference and name in REFERENCE_SKIP:
            continue
        if is_index and name in INDEX_SKIP:
            continue
        try:
            if name == "_reference 규칙":
                issues = check_reference(content, path, strict)
            else:
                issues = fn(content, strict)
            all_issues.extend([(name, iss) for iss in issues])
        except Exception as e:
            all_issues.append((name, f"검사 오류: {e}"))

    return all_issues

def collect_files(target):
    """파일 또는 디렉토리에서 .md 파일 목록 반환."""
    if os.path.isfile(target):
        return [target]
    result = []
    for root, _, files in os.walk(target):
        for f in sorted(files):
            if f.endswith('.md'):
                result.append(os.path.join(root, f))
    return result

# ── 진입점 ────────────────────────────────────────────────────────────────────

def parse_args():
    """커맨드라인 인자 파싱."""
    parser = argparse.ArgumentParser(
        description='Markdown 스타일 검사 도구 (STYLE.md 규칙 기반)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "\nExamples:\n"
            "  %(prog)s ./01_install/                  디렉토리 전체 검사\n"
            "  %(prog)s ./01_install/nginx_install.md  단일 파일 검사\n"
            "  %(prog)s ./_reference/ --strict         과장 표현 whitelist 없이 전체 검사\n"
            "\nChecks:\n"
            "  H1 개수          문서당 H1 정확히 1개\n"
            "  코드블록 언어 태그  ```bash, ```yaml 등 언어 태그 필수\n"
            "  표 정렬          한글 display width 기준 셀 패딩\n"
            "  다이어그램 행 폭  박스 다이어그램 내부 행 폭 일치\n"
            "  다이어그램 한글  박스 다이어그램 내부 영문 권장\n"
            "  이모지 뒤 공백   ✅❌🟡🟢🔴 뒤 공백 1칸 필수\n"
            "  반말체 종결어미  ~이다/한다/된다 등 금지\n"
            "  과장 표현        완전/완벽/최고/최강 등 금지 (--strict: whitelist 무시)\n"
            "  푸터             작성일/마지막 업데이트/저작권 필수\n"
            "  _reference 규칙  sources/last_checked frontmatter 필수\n"
        )
    )
    parser.add_argument('targets', nargs='+', metavar='path',
                        help='검사할 파일 또는 디렉토리 (여러 개 가능)')
    parser.add_argument('-s', '--strict', action='store_true',
                        help='과장 표현 whitelist 없이 전체 검사')
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {VERSION}')
    return parser.parse_args()


def main():
    args = parse_args()

    files = []
    for p in args.targets:
        files.extend(collect_files(p))

    if not files:
        print("검사할 .md 파일이 없습니다.")
        sys.exit(1)

    total_issues = 0
    for fpath in files:
        issues = check_file(fpath, args.strict)
        rel = fpath.replace('/root/32_system-engineering-resources/', '')
        if issues:
            print(f"\n{RED}❌ {rel}{NC}")
            for name, iss in issues:
                print(f"   {YELLOW}[{name}]{NC} {iss}")
            total_issues += len(issues)
        else:
            print(f"{GREEN}✅ {rel}{NC}")

    print(f"\n{'─'*60}")
    if total_issues:
        print(f"{RED}검사 파일: {len(files)}개 | 이슈: {total_issues}건{NC}")
    else:
        print(f"{GREEN}검사 파일: {len(files)}개 | 이슈: {total_issues}건{NC}")
    sys.exit(1 if total_issues else 0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)

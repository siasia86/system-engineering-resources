#!/usr/bin/env python3
#import sys; sys.exit(0)  # SAFETY: uncomment this line to disable script
"""
md-style-check.py — Markdown 스타일 검사 도구
STYLE.md 규칙 기반: 표 정렬, 다이어그램 폭/한글/박스 문자, H1 개수,
이모지 공백, bold 괄호, 반말체, 과장 표현, 푸터, _reference 규칙

사용법:
  python3 md-style-check.py <path> [path ...]
  python3 md-style-check.py <path> -E <dir> -X <file> --no-diagram-kr
  python3 md-style-check.py <path> --strict
  python3 md-style-check.py <path> --config <file>
  python3 md-style-check.py -V

대상 경로의 상위 디렉터리에서 .md-style-check.toml을 자동 탐색합니다.
설정 파일의 skip_checks에 검사 키를 추가하면 해당 저장소에만 적용됩니다.

옵션:
  -E, --exclude-dir DIR     제외할 디렉토리명 (여러 번 사용 가능)
  -X, --exclude-file FILE   제외할 파일명 (여러 번 사용 가능)
  --no-<check>              특정 검사 항목 제외 (--help 참고)
  -s, --strict              과장 표현 whitelist 없이 전체 검사
  -V, --version             버전 출력
"""

VERSION = "26.08.24"

import argparse
import os
import re
import sys
import tomllib
import unicodedata
from functools import lru_cache

# ── 컬러 ──────────────────────────────────────────────────────────────────────

RED    = '\033[0;31m'
GREEN  = '\033[0;32m'
YELLOW = '\033[1;33m'
PURPLE = '\033[0;35m'
CYAN   = '\033[0;36m'
NC     = '\033[0m'

# ── 유틸 ──────────────────────────────────────────────────────────────────────

_FENCE_RE = re.compile(r'^\s*(`{3,})([^`]*)$')
_BLOCKQUOTE_PREFIX_RE = re.compile(r'^\s*(?:>\s?)+')


def _strip_blockquote_prefix(line):
    """인용구 코드블록의 선행 `>` 접두사를 제거합니다."""
    return _BLOCKQUOTE_PREFIX_RE.sub('', line, count=1)


def _fence_info(line):
    """코드 fence의 길이와 언어를 반환합니다."""
    normalized = _strip_blockquote_prefix(line.rstrip())
    match = _FENCE_RE.match(normalized)
    if not match:
        return None
    return len(match.group(1)), match.group(2).strip()


def dw(s):
    """display width: 한글/전각=2, 나머지=1. 인라인 코드 백틱 포함."""
    w = 0
    for c in s:
        if unicodedata.east_asian_width(c) in ('W', 'F'):
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

@lru_cache(maxsize=1)
def strip_code_blocks(content):
    """코드블록 제거 후 반환하며 현재 파일의 반복 호출 결과를 캐시합니다."""
    lines = content.split('\n')
    result = []
    fence_length = None
    for line in lines:
        info = _fence_info(line)
        if fence_length is None and info:
            fence_length = info[0]
        elif (fence_length is not None and info
              and info[0] >= fence_length and not info[1]):
            fence_length = None
        elif fence_length is None:
            result.append(line)
    return '\n'.join(result)


@lru_cache(maxsize=1)
def get_code_blocks(content):
    """(lang, body) 튜플 리스트를 반환하며 fence 길이를 기준으로 닫습니다."""
    blocks = []
    lines = content.split('\n')
    fence_length = None
    lang = ''
    body_lines = []
    for line in lines:
        info = _fence_info(line)
        if fence_length is None and info:
            fence_length = info[0]
            lang = info[1]
            body_lines = []
        elif (fence_length is not None and info
              and info[0] >= fence_length and not info[1]):
            blocks.append((lang, '\n'.join(body_lines)))
            fence_length = None
        elif fence_length is not None:
            body_lines.append(_strip_blockquote_prefix(line))
    return blocks

def strip_frontmatter(content):
    """frontmatter 제거 후 반환."""
    return re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

# ── 검사 함수 ─────────────────────────────────────────────────────────────────

def check_h1(content, strict=False):
    """H1이 정확히 1개인지 확인."""
    body = strip_frontmatter(content)
    body = strip_code_blocks(body)
    h1s = re.findall(r'^# .+', body, re.MULTILINE)
    if len(h1s) != 1:
        return [f"H1 {len(h1s)}개 (1개여야 함): {h1s}"]
    return []

# 출력 결과/UI 경로 패턴 (태그 없이 허용)
_OUTPUT_PATTERN_SOURCES = (
    r'^(?:\d|\.\.\.|\[|SUCCESS|FAILED|ok:|changed:|fatal:|PLAY|TASK|\$|>|#|\*\*|Status|URL:|http)',
    r'|→|\| SUCCESS|\| FAILED|\| CHANGED',
    r'|^[A-Z][a-z]+ →',           # UI 경로 (Grafana →, Jenkins →)
    r'|Securing |Enter password|New password',  # 인터랙티브 출력
    r'|^VPN Client>',  # SoftEther vpncmd 세션
    r'|^Match |^Password|^Permit|^Allow|^Deny',  # sshd_config 등 설정
    r'|^(frontend|backend|global|listen|defaults)\b',  # haproxy 설정
    r'|^prefork:|^worker:|^event:',  # Apache MPM
    r'|^[가-힣].+:',  # 한글 항목 헤더 (사용 조건:, 장점:, 단점: 등)
    r'|^- ',  # 불릿 리스트
    r'|^[A-Z][A-Z_a-z ]+:',  # 대문자 시작 영문 키 (CAP_NET_ADMIN:, PID Namespace: 등)
    r'|^[a-z_]+:',  # 소문자 키 (cpu:, memory: 등)
    r'|^[가-힣/]',  # 한글 또는 슬래시(/) 시작 텍스트 블록
    r'|^[✓✗]',  # 체크마크 기호
)
_OUTPUT_PATTERNS = re.compile(''.join(_OUTPUT_PATTERN_SOURCES))

def check_code_lang(content, strict=False):
    """언어 태그 없는 코드블록 검사.
    허용 목록: 트리/다이어그램, URL, 명령어 출력, UI 경로, 로그, 순수 텍스트 흐름."""
    issues = []
    for lang, body in get_code_blocks(content):
        lang = lang.strip()
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
        if ncols == 0:
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
    """중첩 박스를 포함한 닫힌 다이어그램의 행 display width를 검사합니다."""
    issues = []
    for _lang, body in get_code_blocks(content):
        lines = body.splitlines()
        if not any('┌' in line for line in lines):
            continue
        box_depth = 0
        box_lines = []
        for line in lines:
            starts_box = line.lstrip().startswith('┌')
            opening_count = line.count('┌') if box_depth or starts_box else 0
            closing_count = line.count('└') if box_depth else 0
            if box_depth == 0 and opening_count == 0:
                continue
            if opening_count:
                box_depth += opening_count
            if box_depth:
                box_lines.append(line)
            if closing_count:
                box_depth -= closing_count
            if box_depth == 0 and box_lines:
                check_lines = [bl for bl in box_lines
                               if bl.strip().startswith(('┌', '│', '└'))
                               and '┼' not in bl
                               and bl.strip().endswith(('┐', '│', '┘', '┤', '─'))]
                if check_lines:
                    widths = [dw(bl) for bl in check_lines]
                    max_w = max(widths)
                    for bl, current_width in zip(check_lines, widths):
                        if current_width != max_w:
                            issues.append(
                                f"다이어그램 행 폭 불일치: dw={current_width} "
                                f"(최대={max_w}) | '{bl[:50]}'"
                            )
                box_lines = []
    return issues


def check_diagram_box_chars(content, strict=False):
    """다이어그램 박스 문자 조합 정합성 검사.
    
    행의 양 끝(시작 문자 ~ 끝 문자)만 검사합니다.
    중간에 ┬┴┼ 등 분기 문자가 있는 것은 정상입니다.
    
    규칙: 행에서 ┌├└ 로 시작하는 세그먼트가 최종적으로 어떤 문자로 끝나는지 확인.
    - ┌ 로 시작 → 같은 세그먼트 마지막이 ┐ 또는 중간에 ┬┴┼ 경유 후 ┐ 로 끝나야 함
    - └ 로 시작 → ┘ 로 끝나야 함
    - ├ 로 시작 → ┤ 로 끝나야 함
    
    단, ┬/┴/┼ 는 경유 문자로 허용 (분기/합류 다이어그램).
    """
    issues = []
    for _lang, body in get_code_blocks(content):
        for i, line in enumerate(body.splitlines(), 1):
            stripped = line.rstrip()
            if not stripped:
                continue
            # 독립 세그먼트 추출: 공백으로 분리된 박스 단위
            parts = stripped.split()
            for part in parts:
                if not part:
                    continue
                # ├───┐ 같은 순수 잘못된 조합 (중간에 다른 박스문자 없이 직접 연결)
                m = re.match(r'^([┌├└])([─]+)([┐┘┤┼┬┴])$', part)
                if m:
                    start_ch = m.group(1)
                    end_ch = m.group(3)
                    valid = False
                    if start_ch == '┌' and end_ch in ('┐', '┬'):
                        valid = True
                    elif start_ch == '└' and end_ch in ('┘', '┴'):
                        valid = True
                    elif start_ch == '├' and end_ch in ('┤', '┼', '┬', '┴', '┐'):
                        valid = True
                    if not valid:
                        issues.append(
                            f"박스 문자 오류: '{start_ch}...{end_ch}' ('{start_ch}'는 '{end_ch}'로 끝날 수 없음) | '{stripped[:50]}'"
                        )
        # 박스 상/하단 라인에 ─와 ┐/┘ 사이 공백 혼입 검출
        for i, line in enumerate(body.splitlines(), 1):
            stripped = line.rstrip()
            if re.search(r'─\s+┐', stripped):
                issues.append(
                    f"박스 상단 공백 혼입: ─ 와 ┐ 사이에 공백 | '{stripped[:60]}'"
                )
            if re.search(r'─\s+┘', stripped):
                issues.append(
                    f"박스 하단 공백 혼입: ─ 와 ┘ 사이에 공백 | '{stripped[:60]}'"
                )
    return issues

def check_diagram_korean(content, strict=False):
    """박스 다이어그램 내부 한글 사용 여부를 검사합니다."""
    issues = []
    all_lines = content.split('\n')
    in_block = False
    fence_length = None
    block_start = 0
    block_body = []
    for i, line in enumerate(all_lines, 1):
        info = _fence_info(line)
        if not in_block and info:
            in_block = True
            fence_length = info[0]
            block_start = i + 1
            block_body = []
        elif (in_block and info and info[0] >= fence_length and not info[1]):
            block_text = '\n'.join(block_body)
            if '┌' in block_text and '┘' in block_text:
                for j, block_line in enumerate(block_body):
                    korean = re.findall(r'[가-힣]+', block_line)
                    if korean:
                        lineno = block_start + j
                        issues.append(
                            f"L{lineno}: 다이어그램 내부 한글 사용: "
                            f"{korean[:3]} (영문 권장)"
                        )
            in_block = False
            fence_length = None
        elif in_block:
            block_body.append(_strip_blockquote_prefix(line))
    return issues

# 허용 이모지 목록
_ALLOWED_EMOJIS = ['✅', '❌', '🟡', '🟢', '🔴', '★', '☆', '💡', '✓', '✗']
# 공백 검사 대상: ✅ ❌ 🟡 🟢 🔴 만 (★☆💡는 공백 규칙 불필요)
_EMOJI_SPACE_TARGETS = ['✅', '❌', '🟡', '🟢', '🔴']
_EMOJI_PATTERN = re.compile(
    r'(' + '|'.join(re.escape(e) for e in _EMOJI_SPACE_TARGETS) + r')([^\s|`])'
)
# 비허용 이모지 탐지: Unicode Emoji 범위 중 허용 목록 외
# 장식용 이모지만 검사 (Emoticons, Transport/Map Symbols, Supplemental)
# 기호 문자(✓✗⚠☰⬆ 등)는 제외합니다.
# Unicode 15.1 기준 장식용 이모지 범위이며, Unicode 확장 시 범위를 재검토합니다.
_ALL_EMOJI_PATTERN = re.compile(
    '[\U0001F300-\U0001F5FF'   # Misc Symbols and Pictographs
    '\U0001F600-\U0001F64F'    # Emoticons
    '\U0001F680-\U0001F6FF'    # Transport and Map Symbols
    '\U0001F900-\U0001F9FF'    # Supplemental Symbols
    '\U0001FA00-\U0001FA6F'    # Chess Symbols
    '\U0001FA70-\U0001FAFF'    # Symbols Extended-A
    '\U00002600-\U000027BF'    # Misc Symbols + Dingbats (⚠️❗✂️ 등)
    '\U00002B50'                 # ⭐ (White Medium Star — ★과 혼동 방지)
    ']+'
)


def check_emoji_space(content, strict=False):
    """이모지 뒤 공백 1칸 필수 검사 (STYLE.md § 7). 코드블록/표 셀 내 이모지 단독 사용 제외."""
    issues = []
    # 코드블록 제거 후 원본 라인 번호 추적
    clean = strip_code_blocks(content)
    for i, line in enumerate(clean.splitlines(), 1):
        stripped = line.strip()
        for emoji, next_char in _EMOJI_PATTERN.findall(stripped):
            issues.append(f"L{i}: '{emoji}' 뒤 공백 없음 → '{emoji}{next_char}'")
    return issues


def check_emoji_disallowed(content, strict=False):
    """비허용 이모지 사용 검사 (STYLE.md § 7). 허용: ✅ ❌ 🟡 🟢 🔴 + ★. 코드블록/인용구 내부 제외."""
    issues = []
    clean = strip_code_blocks(content)
    for i, line in enumerate(clean.splitlines(), 1):
        stripped = line.strip()
        # 인용구(>) 내부 제외 — 외부 출처 인용 시 원문 이모지 보존 목적
        if stripped.startswith('>'):
            continue
        for match in _ALL_EMOJI_PATTERN.finditer(stripped):
            emoji = match.group()
            # 허용 목록 확인 (문자 단위 — ★★★☆☆ 같은 연속도 허용)
            if all(c in _ALLOWED_EMOJIS for c in emoji):
                continue
            issues.append(f"L{i}: 비허용 이모지 '{emoji}' — 허용: ✅ ❌ 🟡 🟢 🔴 ★")
    return issues


def check_bold_parentheses(content, strict=False):
    """Bold(**) 안에 괄호가 포함된 경우 검출.
    
    일부 마크다운 렌더러(GitHub 포함)는 **text(...)** 형태에서
    ')' 뒤의 '**'를 bold 닫힘으로 인식하지 못합니다.
    원인: 파서가 ')' 를 bold 범위의 종료 지점으로 혼동하는 엣지 케이스.
    해결: 괄호를 bold 밖으로 이동 — **text**(...)
    """
    if not strict:
        return []
    issues = []
    clean = strip_code_blocks(content)
    for i, line in enumerate(clean.splitlines(), 1):
        # **...(...)** 패턴 검출 (** 안에 ( ) 포함)
        for m in re.finditer(r'[*][*][^*]*[(]([^)]{10,})[)][^*]*[*][*]', line):
            matched = m.group(0)
            paren_content = m.group(1)
            if ' ' not in paren_content:
                continue
            # 표 셀 내 **A** 단독 사용은 제외 (괄호 없는 경우는 이미 필터됨)
            issues.append(
                f"L{i}: bold 안에 괄호 포함 (렌더링 깨짐 가능) → '{matched}'"
            )
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
    clean = strip_code_blocks(content)
    for i, line in enumerate(clean.splitlines(), 1):
        stripped = line.strip()
        if (not stripped
                or stripped.startswith(('#', '|', '*', '!', '>', '©', '-'))):
            continue
        if re.search(r'[가-힣]', stripped) and _BANMAL_PATTERN.search(stripped):
            issues.append(f"L{i}: {stripped[:80]}")
    return issues


# 합니다체 마침표 누락 패턴
_PERIOD_MISSING_PATTERN = re.compile(
    r'[가-힣](니다|합니다|됩니다|있습니다|없습니다|않습니다|아닙니다|입니다)$'
)

def check_period_missing(content, strict=False):
    """합니다체 종결어미 뒤 마침표 누락 검사 (STYLE.md § 10). 코드블록/인용구/헤더/표/불릿 제외."""
    issues = []
    all_lines = content.split('\n')
    in_block = False
    fence_length = None
    for i, line in enumerate(all_lines, 1):
        info = _fence_info(line)
        if not in_block and info:
            in_block = True
            fence_length = info[0]
            continue
        elif (in_block and info and info[0] >= fence_length and not info[1]):
            in_block = False
            fence_length = None
            continue
        if in_block:
            continue
        stripped = line.strip()
        if (not stripped
                or stripped.startswith(('#', '|', '*', '!', '>', '©', '-', '['))):
            continue
        if _PERIOD_MISSING_PATTERN.search(stripped):
            issues.append(f"L{i}: 마침표 누락 → '{stripped[-40:]}'")
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
    clean = strip_code_blocks(content)
    for i, line in enumerate(clean.splitlines(), 1):
        stripped = line.strip()
        if re.search(r'[가-힣]', stripped) and _EXAGGERATION_PATTERN.search(stripped):
            if strict or not _EXAGGERATION_WHITELIST.search(stripped):
                issues.append(f"L{i}: {stripped[:80]}")
    return issues

def check_reference(content, path, strict=False):
    """_reference/ 파일 전용 검사."""
    issues = []
    if '/_reference/' not in path:
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
    # (key,             display_name,        function)
    ("h1",              "H1 개수",           check_h1),
    ("table",           "표 정렬",           check_tables),
    ("diagram-width",   "다이어그램 행 폭",  check_diagram),
    ("diagram-kr",      "다이어그램 한글",   check_diagram_korean),
    ("box-chars",       "박스 문자 정합",    check_diagram_box_chars),
    ("emoji",           "이모지 뒤 공백",    check_emoji_space),
    ("emoji-disallow",  "비허용 이모지",     check_emoji_disallowed),
    ("bold-paren",      "bold 괄호",         check_bold_parentheses),
    ("banmal",          "반말체 종결어미",   check_banmal),
    ("period",          "마침표 누락",       check_period_missing),
    ("exaggeration",    "과장 표현",         check_exaggeration),
    ("footer",          "푸터",              check_footer),
    ("reference",       "_reference 규칙",   check_reference),
]

# _reference 파일은 푸터 불필요
REFERENCE_SKIP = {"footer"}
# .kiro 내부 문서는 푸터 불필요
KIRO_SKIP = {"footer", "h1", "diagram-kr"}
# INDEX.md는 _reference 규칙 적용 제외
INDEX_SKIP = {"reference"}
# 99_archive 파일은 푸터 불필요
ARCHIVE_SKIP = {"footer"}

# 파일별 특정 검사 항목 제외입니다.
#
# 각 항목은 (검사명 집합, 사유, 재검토 시점) 3요소를 갖습니다. 사유 없는 제외는
# 시간이 지나면 근거를 확인할 수 없게 되고, 근거가 사라진 뒤에도 남아 검사 공백이
# 됩니다. 실제로 2026-06-23 에 도입된 파일 단위 제외 목록은 사유 기록이 없어
# 근거를 추적할 수 없었고, 그 안에 실제 결함 26건이 2개월간 가려져 있었습니다.
#
# 재검토 시점은 날짜 또는 조건으로 적습니다. `상시` 는 문서 성격상 항구적인 예외를
# 뜻합니다 (예: 외부 프로젝트 원문 보존).
FILE_SKIP = {
    # ── 32_system-engineering-resources ──────────────────────────────────────
    "01_fundamentals/linux/vim_airline.md": (
        {"emoji-disallow"},
        "외부 프로젝트(vim-airline) README 원문 보존 — 목차 아이콘 '☰' 포함", "상시"),
    "01_fundamentals/networking/network_headers.md": (
        {"box-chars"},
        "RFC 헤더 다이어그램 — 필드 경계에 '├...┘' 조합 사용, 렌더링 정상", "2026-11-30"),
    "02_infrastructure/monitoring/game_infra_kpi_presentation.md": (
        {"diagram-kr"},
        "발표 자료 — 다이어그램 내부 한글이 전달 목적상 필요", "상시"),
    "04_security/cloud/ddos_defense_architecture.md": (
        {"diagram-width"},
        "인접 박스와 연결선을 한 다이어그램으로 묶어 최대폭과 비교하는 도구 오탐", "2026-11-30"),
    "06_career/ai_tools/kiro_cli_command_reference.md": (
        {"diagram-kr"}, "Kiro CLI 문서 — 다이어그램 한글 의도적", "상시"),
    "markdown/STYLE.md": (
        {"emoji", "exaggeration"},
        "스타일 규칙 원본 — 금지 예시(`🟡버전`, `완전`, `완벽`)를 본문에 인용", "상시"),
    "skills/security-tools/SKILL.md": (
        {"emoji-disallow"},
        "보안 스크립트의 실제 출력 기호(`✓`, `✗`, `⚠`)를 본문에서 명세", "상시"),

    # ── sj_del (별도 저장소) ─────────────────────────────────────────────────
    "00_default/linux_setting.md": (
        {"footer", "h1"}, "sj_del 작업 스크립트 문서 — 푸터 규칙 비적용 저장소", "상시"),
    "02_reference/README_web.md": (
        {"footer", "h1"}, "sj_del 참고 자료 — 외부 문서 원문 보존", "상시"),
}


def _should_skip_for_file(filepath, check_name):
    """파일 경로 기반 특정 검사 항목 제외 여부."""
    for pattern, entry in FILE_SKIP.items():
        skip_checks = entry[0] if isinstance(entry, tuple) else entry
        if pattern in filepath and check_name in skip_checks:
            return True
    return False


def list_file_skip():
    """FILE_SKIP 항목을 (경로, 검사, 사유, 재검토) 목록으로 반환."""
    rows = []
    for pattern, entry in sorted(FILE_SKIP.items()):
        if isinstance(entry, tuple):
            checks, reason, review = entry
        else:
            checks, reason, review = entry, "미확인 — 점검 필요", "미정"
        rows.append((pattern, ", ".join(sorted(checks)), reason, review))
    return rows

# CLI skip 옵션과 내부 검사 키의 매핑
_SKIP_FLAG_ATTRIBUTES = {
    'h1': 'no_h1',
    'table': 'no_table',
    'diagram-width': 'no_diagram_width',
    'diagram-kr': 'no_diagram_kr',
    'box-chars': 'no_box_chars',
    'emoji': 'no_emoji',
    'emoji-disallow': 'no_emoji_disallow',
    'bold-paren': 'no_bold_paren',
    'banmal': 'no_banmal',
    'exaggeration': 'no_exaggeration',
    'footer': 'no_footer',
    'period': 'no_period',
    'reference': 'no_reference',
}

# ── 파일 처리 ─────────────────────────────────────────────────────────────────

def check_file(path, strict=False, skip_checks=None):
    """단일 파일 검사. [(항목명, 이슈메시지), ...] 반환."""
    try:
        with open(path) as f:
            content = f.read()
    except Exception as e:
        return [("파일 읽기", f"실패: {e}")]

    is_reference = '/_reference/' in path or path.startswith('_reference/') or path.startswith('./_reference/')
    # 원본(~/.kiro/)과 저장소 미러(00_governance/02_kiro/) 양쪽을 인식합니다.
    # 미러를 exclude_dirs 로 통째 제외하면 표 정렬·문체 검사가 함께 빠져
    # 검사 공백이 생기므로, 경로를 인식해 항목 단위로만 제외합니다.
    _kiro_path = os.path.abspath(path).replace(os.sep, '/')
    is_kiro = '/.kiro/' in _kiro_path or '/02_kiro/' in _kiro_path
    is_index = os.path.basename(path) == 'INDEX.md'
    is_archive = "/99_archive/" in path or path.startswith("99_archive/") or path.startswith("./99_archive/")
    all_issues = []

    for key, name, fn in CHECKS:
        if is_reference and key in REFERENCE_SKIP:
            continue
        if is_kiro and key in KIRO_SKIP:
            continue
        if is_index and key in INDEX_SKIP:
            continue
        if is_archive and key in ARCHIVE_SKIP:
            continue
        if _should_skip_for_file(path, key):
            continue
        if skip_checks and key in skip_checks:
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

# 검사 제외 디렉토리
EXCLUDE_DIRS = {'99_archive', '99_etc', '.git', '__pycache__', '_reference'}

# 검사 제외 파일
# 기본값은 비어 있습니다. 파일 전체를 빼면 표 정렬·문체 검사가 함께 빠지므로,
# 특정 항목만 제외해야 하는 경우 FILE_SKIP 을 사용합니다.
EXCLUDE_FILES = set()


CONFIG_LIST_KEYS = ('exclude_dirs', 'exclude_files', 'skip_checks')


def _read_config(config_path):
    """TOML 설정 파일을 읽고 목록 값과 검사명을 검증합니다."""
    with open(config_path, 'rb') as config_file:
        config = tomllib.load(config_file)

    version = config.get('version', 1)
    if isinstance(version, bool) or not isinstance(version, int):
        raise ValueError("config key 'version' must be an integer")
    allowed_keys = {'version', *CONFIG_LIST_KEYS}
    unknown_keys = set(config) - allowed_keys
    if unknown_keys:
        invalid = ', '.join(sorted(unknown_keys))
        available = ', '.join(sorted(allowed_keys))
        raise ValueError(
            f"unknown config keys: {invalid}; available keys: {available}"
        )

    result = {}
    for key in CONFIG_LIST_KEYS:
        if key not in config:
            continue
        values = config[key]
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            raise ValueError(f"config key '{key}' must be a string list")
        result[key] = values

    unknown_checks = set(result.get('skip_checks', [])) - set(_SKIP_FLAG_ATTRIBUTES)
    if unknown_checks:
        available = ', '.join(sorted(_SKIP_FLAG_ATTRIBUTES))
        invalid = ', '.join(sorted(unknown_checks))
        raise ValueError(
            f"config key 'skip_checks' contains unknown checks: {invalid}; "
            f"available checks: {available}"
        )
    return result


def _merge_config(base, override):
    """기본 설정과 저장소 설정을 중복 없이 병합합니다."""
    merged = {key: list(base.get(key, [])) for key in CONFIG_LIST_KEYS}
    for key in CONFIG_LIST_KEYS:
        for value in override.get(key, []):
            if value not in merged[key]:
                merged[key].append(value)
    return merged


def _global_config_path():
    """검사기 저장소의 공통 설정 경로를 반환합니다."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '.md-style-check.toml')


def find_config_path(target):
    """대상 파일 또는 디렉터리에서 상위로 저장소 설정을 탐색합니다."""
    current = os.path.abspath(target)
    if not os.path.isdir(current):
        current = os.path.dirname(current)

    while True:
        candidate = os.path.join(current, '.md-style-check.toml')
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def load_config(config_path=None, target=None):
    """공통 설정과 대상 저장소의 TOML 설정을 병합합니다."""
    config = {
        'exclude_dirs': sorted(EXCLUDE_DIRS),
        'exclude_files': sorted(EXCLUDE_FILES),
        'skip_checks': [],
    }
    global_path = _global_config_path()
    if os.path.isfile(global_path):
        config = _merge_config(config, _read_config(global_path))

    selected_path = config_path or (find_config_path(target) if target else None)
    if selected_path:
        selected_path = os.path.abspath(selected_path)
        if not os.path.isfile(selected_path):
            raise FileNotFoundError(f"config not found: {selected_path}")
        if os.path.normpath(selected_path) != os.path.normpath(global_path):
            config = _merge_config(config, _read_config(selected_path))
    elif config_path:
        raise FileNotFoundError(f"config not found: {config_path}")
    return config


def _is_excluded_dir(path, dirname, target_abs, skip_dirs):
    """디렉토리명 또는 저장소 기준 상대 경로의 제외 여부 반환."""
    if dirname in skip_dirs:
        return True
    candidates = set()
    for base in (target_abs, os.path.dirname(os.path.abspath(__file__))):
        candidates.add(os.path.normpath(os.path.relpath(path, base)))
    for excluded in skip_dirs:
        normalized = os.path.normpath(excluded)
        if '/' not in normalized and os.sep not in normalized:
            continue
        if normalized in candidates:
            return True
    return False


def collect_files(target, extra_exclude_dirs=None, exclude_files=None,
                  base_exclude_dirs=None, base_exclude_files=None):
    """파일 또는 디렉토리에서 .md 파일 목록 반환."""
    if os.path.isfile(target):
        if exclude_files and os.path.basename(target) in exclude_files:
            return []
        return [target]
    skip_dirs = set(base_exclude_dirs or EXCLUDE_DIRS) | set(extra_exclude_dirs or [])
    skip_files = set(base_exclude_files or EXCLUDE_FILES) | set(exclude_files or [])
    result = []
    target_abs = os.path.abspath(target)
    if _is_excluded_dir(target_abs, os.path.basename(target_abs), target_abs, skip_dirs):
        return []
    for root, dirs, files in os.walk(target):
        dirs[:] = [
            d for d in dirs
            if not _is_excluded_dir(os.path.join(root, d), d, target_abs, skip_dirs)
        ]
        dirs.sort()
        for f in sorted(files):
            if not f.endswith('.md') or f in skip_files:
                continue
            # 루트 디렉토리의 README.md만 제외
            if f == 'README.md' and os.path.abspath(root) == target_abs:
                continue
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
            "  %(prog)s ./ -E 99_ETC -E 90_DELETE       디렉토리 제외\n"
            "  %(prog)s ./ -X vim_airline.md            파일 제외\n"
            "  %(prog)s ./ --no-diagram-kr              다이어그램 한글 검사 제외\n"
            "\nChecks:\n"
            "  H1 개수          문서당 H1 정확히 1개\n"
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
    parser.add_argument('targets', nargs='*', metavar='path',
                        help='검사할 파일 또는 디렉토리 (여러 개 가능)')
    parser.add_argument('-E', '--exclude-dir', action='append', default=[],
                        dest='exclude_dirs', metavar='DIR',
                        help='제외할 디렉토리명 (여러 번 사용 가능)')
    parser.add_argument('--config', metavar='FILE',
                        help='TOML 설정 파일 (미지정 시 대상 경로에서 .md-style-check.toml 자동 탐색)')
    parser.add_argument('-X', '--exclude-file', action='append', default=[],
                        dest='exclude_files', metavar='FILE',
                        help='제외할 파일명 (여러 번 사용 가능)')
    # 검사 항목 제외 플래그
    skip_group = parser.add_argument_group('skip options', '특정 검사 항목 제외')
    skip_group.add_argument('--no-diagram-kr', action='store_true', help='다이어그램 한글 검사 제외')
    skip_group.add_argument('--no-diagram-width', action='store_true', help='다이어그램 행 폭 검사 제외')
    skip_group.add_argument('--no-table', action='store_true', help='표 정렬 검사 제외')
    skip_group.add_argument('--no-emoji', action='store_true', help='이모지 뒤 공백 검사 제외')
    skip_group.add_argument('--no-emoji-disallow', action='store_true', help='비허용 이모지 검사 제외')
    skip_group.add_argument('--no-banmal', action='store_true', help='반말체 종결어미 검사 제외')
    skip_group.add_argument('--no-exaggeration', action='store_true', help='과장 표현 검사 제외')
    skip_group.add_argument('--no-footer', action='store_true', help='푸터 검사 제외')
    skip_group.add_argument('--no-h1', action='store_true', help='H1 개수 검사 제외')
    skip_group.add_argument('--no-box-chars', action='store_true', help='박스 문자 정합 검사 제외')
    skip_group.add_argument('--no-bold-paren', action='store_true', help='bold 괄호 검사 제외')
    skip_group.add_argument('--no-period', action='store_true', help='마침표 누락 검사 제외')
    skip_group.add_argument('--no-reference', action='store_true', help='_reference 규칙 검사 제외')

    parser.add_argument('-s', '--strict', action='store_true',
                        help='과장 표현 whitelist 없이 전체 검사')
    parser.add_argument('--list-skips', action='store_true',
                        help='파일별 검사 제외 항목과 사유 출력 후 종료')
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {VERSION}')
    return parser.parse_args()


def _print_file_skips():
    """FILE_SKIP 목록을 표로 출력. 사유 미확인 항목이 있으면 종료 코드 1."""
    rows = [("경로", "제외 검사", "사유", "재검토")] + list_file_skip()

    def dw(s):
        return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in s)

    widths = [max(dw(r[i]) for r in rows) for i in range(4)]
    for idx, row in enumerate(rows):
        line = "| " + " | ".join(
            cell + " " * (widths[i] - dw(cell)) for i, cell in enumerate(row)
        ) + " |"
        print(line)
        if idx == 0:
            print("|" + "|".join("-" * (w + 2) for w in widths) + "|")

    pending = [r for r in rows[1:] if r[2].startswith("미확인")]
    print(f"\n총 {len(rows) - 1}건 | 사유 미확인 {len(pending)}건")
    if pending:
        print("사유가 기록되지 않은 제외 항목이 있습니다. 근거를 확인하거나 제외를 해제하세요.")
    return 1 if pending else 0


def main():
    args = parse_args()
    if args.list_skips:
        sys.exit(_print_file_skips())
    if not args.targets:
        print("검사 대상 경로를 지정하세요. 사용법은 -h 를 참고합니다.", file=sys.stderr)
        sys.exit(2)
    try:
        target_configs = []
        for target in args.targets:
            config = load_config(args.config, target=target)
            target_configs.append((target, config, find_config_path(target) if not args.config else args.config))
    except (OSError, tomllib.TOMLDecodeError, ValueError) as error:
        print(f"설정 로드 실패: {error}", file=sys.stderr)
        sys.exit(1)

    configured_exclude_dirs = set()
    configured_exclude_files = set()
    config_sources = set()
    files = []
    file_config_skips = {}
    for target, config, config_source in target_configs:
        configured_exclude_dirs.update(config['exclude_dirs'])
        configured_exclude_files.update(config['exclude_files'])
        if config_source:
            config_sources.add(os.path.abspath(config_source))
        target_files = collect_files(
            target,
            args.exclude_dirs,
            args.exclude_files,
            config['exclude_dirs'],
            config['exclude_files'],
        )
        for fpath in target_files:
            files.append(fpath)
            file_config_skips.setdefault(fpath, set()).update(config['skip_checks'])

    if not files:
        print("검사할 .md 파일이 없습니다.")
        sys.exit(1)

    # 제외 현황 출력
    all_exclude_dirs = sorted(configured_exclude_dirs | set(args.exclude_dirs))
    all_exclude_files = sorted(configured_exclude_files | set(args.exclude_files)) + ['README.md (루트)']
    cli_skip_checks = [key for key, attribute in _SKIP_FLAG_ATTRIBUTES.items()
                       if getattr(args, attribute)]
    configured_skip_checks = sorted({
        check for checks in file_config_skips.values() for check in checks
    })
    all_skip_checks = sorted(set(cli_skip_checks) | set(configured_skip_checks))

    if config_sources:
        print(f"{YELLOW}[설정] {', '.join(sorted(config_sources))}{NC}")
    if all_exclude_dirs or all_exclude_files or all_skip_checks:
        print(f"{YELLOW}[제외] 디렉토리: {', '.join(all_exclude_dirs)}{NC}")
        print(f"{YELLOW}[제외] 파일: {', '.join(all_exclude_files)}{NC}")
        if all_skip_checks:
            print(f"{YELLOW}[제외] 검사: {', '.join(all_skip_checks)}{NC}")
        print()

    total_issues = 0
    for fpath in files:
        skip_checks = sorted(set(cli_skip_checks) | file_config_skips.get(fpath, set()))
        issues = check_file(fpath, strict=args.strict, skip_checks=skip_checks)
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

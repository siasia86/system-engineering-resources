#!/usr/bin/env python3
#import sys; sys.exit(0)  # SAFETY: uncomment this line to disable script
"""
md-heading-check.py — Markdown 헤딩 구조 및 목차 앵커 검증
==========================================================

사용법:
    python md-heading-check.py <file_or_dir> [file_or_dir ...]
    python md-heading-check.py README.md
    python md-heading-check.py -v /root/32_system-engineering-resources/
    python md-heading-check.py --no-anchor 01_fundamentals/

검증 대상:
    - anchor    : #앵커 링크가 실제 헤딩과 일치하는지
    - number    : H2 번호가 1부터 연속인지 (## 1., ## 2., ...)
    - level     : 헤딩 레벨이 건너뛰지 않는지 (H2 -> H4 금지)
    - duplicate : 링크가 참조하는 앵커에 중복 헤딩이 있는지

검증 제외:
    - 코드블록 내부 헤딩과 링크
    - http:// https:// 외부 링크
    - 다른 파일을 가리키는 앵커 (path.md#anchor)

md-link-check.py 는 상대경로 링크만 검증하고 #anchor 링크를 의도적으로
제외합니다. 이 스크립트가 그 범위를 담당합니다.

설정:
    대상 경로의 상위 디렉터리에서 .md-heading-check.toml 을 자동 탐색합니다.

    exclude_dirs  = ["99_archive"]          제외할 디렉토리명 또는 상대 경로
    exclude_files = ["vim_airline.md"]      제외할 파일명
    skip_checks   = ["level"]               전역으로 제외할 검사 항목

    [[file_skip]]                           파일별 검사 항목 제외
    path   = "01_fundamentals/linux/vim_airline.md"
    checks = ["level"]
    reason = "외부 프로젝트 README 원본"

종료 코드:
    0 = 이슈 없음
    1 = 이슈 발견
"""

VERSION = "26.08.27.5"

import argparse
import os
import re
import sys
import tomllib

# ── patterns ──────────────────────────────────────────────────────────────────

HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+?)\s*$')
ANCHOR_LINK_PATTERN = re.compile(r'\[[^\]]*\]\(#([^)]+)\)')
FENCE_PATTERN = re.compile(r'^(\s*)(`{3,}|~{3,})\s*(.*)$')
NUMBERED_H2_PATTERN = re.compile(r'^(\d+)(?:-(\d+))?\.\s+')

# 번호를 요구하지 않는 관례적 H2
UNNUMBERED_ALLOWED = {'목차', '참고 자료', '통계', '개요', 'changelog'}

ALL_CHECKS = ('anchor', 'number', 'level', 'duplicate')
CONFIG_NAME = '.md-heading-check.toml'
DEFAULT_EXCLUDE_DIRS = {'.git', '__pycache__', 'node_modules'}


# ── config ────────────────────────────────────────────────────────────────────

def find_config_path(target):
    """대상 경로에서 상위로 올라가며 설정 파일을 탐색."""
    current = os.path.abspath(target)
    if not os.path.isdir(current):
        current = os.path.dirname(current)
    while True:
        candidate = os.path.join(current, CONFIG_NAME)
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def load_config(config_path=None, target=None):
    """TOML 설정을 읽어 정규화된 dict 반환."""
    config = {
        'exclude_dirs': sorted(DEFAULT_EXCLUDE_DIRS),
        'exclude_files': [],
        'skip_checks': [],
        'file_skip': [],
        'path': None,
    }
    selected = config_path or (find_config_path(target) if target else None)
    if not selected:
        if config_path:
            raise FileNotFoundError(f"config not found: {config_path}")
        return config
    selected = os.path.abspath(selected)
    if not os.path.isfile(selected):
        raise FileNotFoundError(f"config not found: {selected}")
    with open(selected, 'rb') as f:
        data = tomllib.load(f)

    allowed = {'exclude_dirs', 'exclude_files', 'skip_checks', 'file_skip'}
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"unknown config key: {', '.join(sorted(unknown))}")

    for key in ('exclude_dirs', 'exclude_files', 'skip_checks'):
        for value in data.get(key, []):
            if value not in config[key]:
                config[key].append(value)
    for entry in data.get('file_skip', []):
        if 'path' not in entry:
            raise ValueError("file_skip entry requires 'path'")
        config['file_skip'].append({
            'path': os.path.normpath(entry['path']),
            'checks': list(entry.get('checks', ALL_CHECKS)),
            'reason': entry.get('reason', ''),
        })
    config['path'] = selected
    config['root'] = os.path.dirname(selected)
    return config


def enabled_for(filepath, config, base_enabled):
    """파일별 file_skip 설정을 적용한 검사 항목 집합 반환."""
    root = config.get('root')
    if not root:
        return base_enabled, ''
    try:
        rel = os.path.normpath(os.path.relpath(os.path.abspath(filepath), root))
    except ValueError:
        return base_enabled, ''
    for entry in config['file_skip']:
        if entry['path'] == rel:
            return base_enabled - set(entry['checks']), entry['reason']
    return base_enabled, ''


# ── utilities ─────────────────────────────────────────────────────────────────

def make_anchor(heading):
    """헤딩 텍스트를 GitHub 앵커 형식으로 변환."""
    text = heading.strip().lower()
    text = text.replace('`', '')
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)   # 링크는 텍스트만 남김
    text = re.sub(r'[*_~]', '', text)                       # 강조 기호 제거
    text = re.sub(r'[^\w\s\-]', '', text, flags=re.UNICODE)
    return text.replace(' ', '-')


def strip_code_blocks(content):
    """코드블록 내부를 빈 줄로 치환하여 줄 번호를 보존.

    CommonMark 규칙을 따릅니다.

    - 닫는 펜스는 여는 펜스와 같은 문자이고 개수가 같거나 많아야 합니다.
    - 닫는 펜스에는 정보 문자열(```python 등)이 없어야 합니다.
    - 펜스의 들여쓰기는 최대 3칸입니다. 4칸 이상은 내용으로 취급합니다.

    이 규칙이 없으면 중첩 예시가 있는 문서에서 코드 영역을 잘못 판정합니다.
    """
    result = []
    fence_char = None
    fence_len = 0
    for line in content.split('\n'):
        m = FENCE_PATTERN.match(line)
        # 들여쓰기 4칸 이상은 펜스가 아닙니다 (CommonMark: 최대 3칸)
        if m and len(m.group(1).expandtabs(4)) <= 3:
            marker = m.group(2)
            char, length, info = marker[0], len(marker), m.group(3).strip()
            if fence_char is None:
                fence_char, fence_len = char, length
                result.append('')
                continue
            if char == fence_char and length >= fence_len and not info:
                fence_char, fence_len = None, 0
                result.append('')
                continue
            # 정보 문자열이 있거나 문자가 다르면 닫는 펜스가 아님 (내용으로 취급)
            result.append('')
            continue
        result.append('' if fence_char else line)
    return '\n'.join(result)


def collect_md_files(paths, exclude_dirs=None, exclude_files=None):
    """대상 경로에서 .md 파일 목록 수집. 제외 설정을 적용합니다."""
    skip_dirs = set(exclude_dirs or DEFAULT_EXCLUDE_DIRS) | DEFAULT_EXCLUDE_DIRS
    skip_files = set(exclude_files or [])
    files = []
    for path in paths:
        if os.path.isfile(path) and path.endswith('.md'):
            if os.path.basename(path) not in skip_files:
                files.append(path)
        elif os.path.isdir(path):
            base = os.path.abspath(path)
            for root, dirs, names in os.walk(path):
                dirs[:] = [d for d in dirs
                           if d not in skip_dirs
                           and os.path.normpath(
                               os.path.relpath(os.path.join(root, d), base)
                           ) not in skip_dirs]
                files.extend(os.path.join(root, n) for n in sorted(names)
                             if n.endswith('.md') and n not in skip_files)
    return sorted(set(files))


# ── core functions ────────────────────────────────────────────────────────────

def extract_headings(content):
    """(레벨, 텍스트, 줄번호) 목록 반환."""
    headings = []
    for lineno, line in enumerate(content.split('\n'), 1):
        m = HEADING_PATTERN.match(line)
        if m:
            headings.append((len(m.group(1)), m.group(2), lineno))
    return headings


def check_anchors(headings, content):
    """#앵커 링크가 실제 헤딩과 일치하는지 검증."""
    valid = {make_anchor(text) for _, text, _ in headings}
    issues = []
    for lineno, line in enumerate(content.split('\n'), 1):
        for anchor in ANCHOR_LINK_PATTERN.findall(line):
            if anchor not in valid:
                issues.append((lineno, 'anchor', f'앵커 대상 없음: #{anchor}'))
    return issues


def check_numbering(headings):
    """H2 번호가 1부터 연속인지 검증.

    두 가지 확장 표기를 지원합니다.

    - 범위 (`## 5-10. 제목`): 한 섹션이 여러 번호를 포괄합니다. 외부 규칙 번호에
      대응하는 문서에서 사용합니다.
    - 하위 절 (`## 1-1. 제목`): 직전 섹션의 하위 항목이므로 번호를 진행시키지
      않습니다.

    뒤 숫자가 앞 숫자보다 크면 범위, 작거나 같으면 하위 절로 판정합니다.
    """
    issues = []
    numbered = []
    for level, text, lineno in headings:
        if level != 2:
            continue
        m = NUMBERED_H2_PATTERN.match(text)
        if not m:
            continue
        start = int(m.group(1))
        second = int(m.group(2)) if m.group(2) else None
        if second is not None and second > start:
            numbered.append((start, second, False, text, lineno))   # 범위: 5-10.
        elif second is not None:
            numbered.append((start, start, True, text, lineno))     # 하위 절: 1-1.
        else:
            numbered.append((start, start, False, text, lineno))
    if not numbered:
        return issues

    start, _, _, text, lineno = numbered[0]
    if start != 1:
        issues.append((lineno, 'number', f'H2 번호가 1로 시작하지 않음: {text}'))
    for i in range(1, len(numbered)):
        prev_end = numbered[i - 1][1]
        cur_start, _, is_sub, text, lineno = numbered[i]
        expected = prev_end if is_sub else prev_end + 1
        if cur_start != expected:
            issues.append((lineno, 'number',
                           f'H2 번호 불연속: {prev_end} -> {cur_start} ({text})'))
    return issues


def check_levels(headings):
    """헤딩 레벨이 건너뛰지 않는지 검증."""
    issues = []
    prev = 0
    for level, text, lineno in headings:
        if prev and level > prev + 1:
            issues.append((lineno, 'level',
                           f'헤딩 레벨 건너뜀: H{prev} -> H{level} ({text})'))
        prev = level
    return issues


def check_duplicates(headings, content):
    """링크가 참조하는 앵커에 중복 헤딩이 있는지 검증.

    반복 섹션(CHANGELOG의 `### Added` 등)은 정상 형식이므로, 앵커 링크가
    실제로 가리키는 대상만 검사합니다. 중복된 앵커로는 첫 번째 헤딩만
    도달할 수 있어 링크가 의도한 위치로 가지 않습니다.
    """
    referenced = set()
    for line in content.split('\n'):
        referenced.update(ANCHOR_LINK_PATTERN.findall(line))
    if not referenced:
        return []

    issues = []
    seen = {}
    for level, text, lineno in headings:
        anchor = make_anchor(text)
        if anchor in seen:
            if anchor in referenced:
                issues.append((lineno, 'duplicate',
                               f'참조되는 앵커가 중복됨: #{anchor} '
                               f'(L{seen[anchor]}과 동일, 링크는 첫 번째로만 이동)'))
        else:
            seen[anchor] = lineno
    return issues


def check_file(filepath, enabled):
    """단일 파일 검증. 이슈 목록과 헤딩 수 반환."""
    try:
        with open(filepath, encoding='utf-8') as f:
            raw = f.read()
    except (OSError, UnicodeError) as exc:
        return [(0, 'read', f'읽기 실패: {exc}')], 0

    content = strip_code_blocks(raw)
    headings = extract_headings(content)

    issues = []
    if 'anchor' in enabled:
        issues += check_anchors(headings, content)
    if 'number' in enabled:
        issues += check_numbering(headings)
    if 'level' in enabled:
        issues += check_levels(headings)
    if 'duplicate' in enabled:
        issues += check_duplicates(headings, content)
    return sorted(issues), len(headings)


# ── entry point ───────────────────────────────────────────────────────────────

def parse_args():
    """커맨드라인 인자 파싱."""
    parser = argparse.ArgumentParser(
        description='Markdown 헤딩 구조 및 목차 앵커 검증',
        epilog='Examples:\n'
               '  python md-heading-check.py README.md\n'
               '  python md-heading-check.py /root/32_system-engineering-resources/\n'
               '  python md-heading-check.py -v README.md        파일별 헤딩 수 출력\n'
               '  python md-heading-check.py --no-number docs/   번호 검사 제외\n'
               '\nNotes:\n'
               '  - md-link-check.py 는 #anchor 링크를 검증 대상에서 제외합니다.\n'
               '  - 코드블록 내부의 헤딩과 링크는 검사하지 않습니다.\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('paths', nargs='+', help='.md 파일 또는 디렉토리')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='파일별 헤딩 수 출력')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='이슈만 출력')
    parser.add_argument('--no-anchor', action='store_true', help='앵커 검사 제외')
    parser.add_argument('--no-number', action='store_true', help='번호 검사 제외')
    parser.add_argument('--no-level', action='store_true', help='레벨 검사 제외')
    parser.add_argument('--no-duplicate', action='store_true', help='중복 검사 제외')
    parser.add_argument('-c', '--config', metavar='FILE',
                        help=f'TOML 설정 파일 (미지정 시 {CONFIG_NAME} 자동 탐색)')
    parser.add_argument('-E', '--exclude-dir', action='append', default=[],
                        dest='exclude_dirs', metavar='DIR',
                        help='제외할 디렉토리명 (여러 번 사용 가능)')
    parser.add_argument('-X', '--exclude-file', action='append', default=[],
                        dest='exclude_files', metavar='FILE',
                        help='제외할 파일명 (여러 번 사용 가능)')
    parser.add_argument('-V', '--version', action='version',
                        version=f'%(prog)s {VERSION}')
    return parser.parse_args()


def main():
    """메인 실행."""
    args = parse_args()

    try:
        config = load_config(args.config, args.paths[0])
    except (FileNotFoundError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"설정 오류: {exc}", file=sys.stderr)
        sys.exit(1)

    enabled = set(ALL_CHECKS) - set(config['skip_checks'])
    for name in list(ALL_CHECKS):
        if getattr(args, f'no_{name}'):
            enabled.discard(name)
    if not enabled:
        print("모든 검사가 제외되었습니다")
        sys.exit(0)

    exclude_dirs = list(config['exclude_dirs']) + list(args.exclude_dirs)
    exclude_files = list(config['exclude_files']) + list(args.exclude_files)
    files = collect_md_files(args.paths, exclude_dirs, exclude_files)
    if not files:
        print("대상 .md 파일 없음")
        sys.exit(0)

    if config['path'] and not args.quiet:
        print(f"[설정] {config['path']}")

    total_issues = 0
    total_headings = 0
    failed = []
    skipped = []

    for filepath in files:
        file_enabled, reason = enabled_for(filepath, config, enabled)
        if not file_enabled:
            skipped.append((filepath, reason))
            continue
        if file_enabled != enabled:
            skipped.append((filepath, reason))
        issues, count = check_file(filepath, file_enabled)
        total_headings += count
        if issues:
            total_issues += len(issues)
            failed.append((filepath, issues))
        elif args.verbose and not args.quiet:
            print(f"  ✅ {os.path.relpath(filepath)} ({count} headings)")

    if failed:
        for filepath, issues in failed:
            print(f"\n❌ {os.path.relpath(filepath)}")
            for lineno, kind, message in issues:
                loc = f"L{lineno}" if lineno else "-"
                print(f"   [{kind}] {loc}: {message}")
    elif not args.quiet:
        print("✅ 헤딩 구조 정상")

    if skipped and not args.quiet:
        print(f"\n[예외] {len(skipped)}개 파일에 검사 항목 제외 적용")
        if args.verbose:
            for filepath, reason in skipped:
                note = f" — {reason}" if reason else ""
                print(f"   {os.path.relpath(filepath)}{note}")

    if not args.quiet:
        print(f"\n{'─' * 60}")
        print(f"검사 파일: {len(files)}개 | 헤딩: {total_headings}개 | "
              f"이슈: {total_issues}건")

    sys.exit(1 if total_issues > 0 else 0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)

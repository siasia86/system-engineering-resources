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

종료 코드:
    0 = 이슈 없음
    1 = 이슈 발견
"""

VERSION = "26.08.27"

import argparse
import os
import re
import sys

# ── patterns ──────────────────────────────────────────────────────────────────

HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+?)\s*$')
ANCHOR_LINK_PATTERN = re.compile(r'\[[^\]]*\]\(#([^)]+)\)')
FENCE_PATTERN = re.compile(r'^\s*(`{3,}|~{3,})')
NUMBERED_H2_PATTERN = re.compile(r'^(\d+)\.\s+')

# 번호를 요구하지 않는 관례적 H2
UNNUMBERED_ALLOWED = {'목차', '참고 자료', '통계', '개요', 'changelog'}


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
    """코드블록 내부를 빈 줄로 치환하여 줄 번호를 보존."""
    result = []
    in_fence = False
    for line in content.split('\n'):
        if FENCE_PATTERN.match(line):
            in_fence = not in_fence
            result.append('')
            continue
        result.append('' if in_fence else line)
    return '\n'.join(result)


def collect_md_files(paths):
    """대상 경로에서 .md 파일 목록 수집."""
    files = []
    for path in paths:
        if os.path.isfile(path) and path.endswith('.md'):
            files.append(path)
        elif os.path.isdir(path):
            for root, dirs, names in os.walk(path):
                dirs[:] = [d for d in dirs
                           if d not in {'.git', '__pycache__', 'node_modules'}]
                files.extend(os.path.join(root, n)
                             for n in sorted(names) if n.endswith('.md'))
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
    """H2 번호가 1부터 연속인지 검증."""
    issues = []
    numbered = []
    for level, text, lineno in headings:
        if level != 2:
            continue
        m = NUMBERED_H2_PATTERN.match(text)
        if m:
            numbered.append((int(m.group(1)), text, lineno))
    if not numbered:
        return issues
    if numbered[0][0] != 1:
        n, text, lineno = numbered[0]
        issues.append((lineno, 'number', f'H2 번호가 1로 시작하지 않음: {n}. {text}'))
    for i in range(1, len(numbered)):
        prev, cur = numbered[i - 1][0], numbered[i][0]
        if cur != prev + 1:
            _, text, lineno = numbered[i]
            issues.append((lineno, 'number',
                           f'H2 번호 불연속: {prev} -> {cur} ({text})'))
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
    parser.add_argument('-V', '--version', action='version',
                        version=f'%(prog)s {VERSION}')
    return parser.parse_args()


def main():
    """메인 실행."""
    args = parse_args()

    enabled = {'anchor', 'number', 'level', 'duplicate'}
    for name in list(enabled):
        if getattr(args, f'no_{name}'):
            enabled.discard(name)
    if not enabled:
        print("모든 검사가 제외되었습니다")
        sys.exit(0)

    files = collect_md_files(args.paths)
    if not files:
        print("대상 .md 파일 없음")
        sys.exit(0)

    total_issues = 0
    total_headings = 0
    failed = []

    for filepath in files:
        issues, count = check_file(filepath, enabled)
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

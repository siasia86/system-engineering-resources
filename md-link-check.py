#!/usr/bin/env python3
#import sys; sys.exit(0)  # SAFETY: uncomment this line to disable script
"""
md-link-check.py — Markdown 내부 링크 존재 여부 검증
====================================================

사용법:
    python md-link-check.py <file_or_dir> [file_or_dir ...]
    python md-link-check.py /root/32_system-engineering-resources/
    python md-link-check.py README.md

검증 대상:
    - [text](relative/path.md) 형태의 상대경로 링크
    - [text](./path) 형태 포함

검증 제외:
    - http:// https:// 외부 링크
    - #anchor 앵커 링크
    - 코드블록 내부 링크

종료 코드:
    0 = 모든 링크 정상
    1 = 깨진 링크 발견
"""

VERSION = "26.06.19"

import argparse
import os
import re
import sys

# ── patterns ──────────────────────────────────────────────────────────────────

LINK_PATTERN = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
CODE_BLOCK_PATTERN = re.compile(r'```[\s\S]*?```')

# ── functions ─────────────────────────────────────────────────────────────────

def parse_args():
    """커맨드라인 인자 파싱."""
    parser = argparse.ArgumentParser(
        description='Markdown 내부 링크 존재 여부 검증',
        epilog='Examples:\n'
               '  python md-link-check.py README.md\n'
               '  python md-link-check.py /root/32_system-engineering-resources/\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('paths', nargs='+', help='.md 파일 또는 디렉토리')
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {VERSION}')
    return parser.parse_args()


def collect_md_files(paths):
    """경로 목록에서 .md 파일 수집."""
    files = []
    for p in paths:
        if os.path.isfile(p) and p.endswith('.md'):
            files.append(p)
        elif os.path.isdir(p):
            for root, dirs, filenames in os.walk(p, followlinks=False):
                dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__')]
                for f in filenames:
                    if f.endswith('.md'):
                        files.append(os.path.join(root, f))
    return sorted(set(files))


def strip_code_blocks_preserve_lines(content):
    """코드블록 내용을 빈 행으로 치환 (행 번호 유지)."""
    def replacer(m):
        return '\n' * m.group(0).count('\n')
    return CODE_BLOCK_PATTERN.sub(replacer, content)


def extract_link_path(raw_link):
    """링크에서 경로만 추출 (앵커, title 속성 제거)."""
    # path#anchor → path
    path = raw_link.split('#')[0]
    # path "title" or path 'title' → path
    path = path.split('"')[0].split("'")[0].rstrip()
    return path


def check_file(filepath):
    """파일 내 상대 링크 검증. (broken_list, total_count) 튜플 반환."""
    try:
        with open(filepath, encoding='utf-8') as f:
            raw_content = f.read()
    except (UnicodeDecodeError, OSError) as e:
        return ([(-1, f"[읽기 실패: {e}]", filepath)], 0)

    clean = strip_code_blocks_preserve_lines(raw_content)
    base_dir = os.path.dirname(os.path.abspath(filepath))
    broken = []
    link_count = 0

    for i, line in enumerate(clean.splitlines(), 1):
        for m in LINK_PATTERN.finditer(line):
            link = m.group(2)

            # 외부 링크, 앵커 제외
            if link.startswith(('http://', 'https://', '#', 'mailto:')):
                continue

            link_path = extract_link_path(link)
            if not link_path:
                continue

            link_count += 1

            # 상대경로 해석
            target = os.path.normpath(os.path.join(base_dir, link_path))
            if not os.path.exists(target):
                broken.append((i, link, target))

    return (broken, link_count)


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    """메인 실행."""
    args = parse_args()
    files = collect_md_files(args.paths)

    if not files:
        print("대상 .md 파일 없음")
        sys.exit(0)

    total_broken = 0
    total_links = 0
    broken_files = []

    for filepath in files:
        broken, link_count = check_file(filepath)
        total_links += link_count
        if broken:
            total_broken += len(broken)
            broken_files.append((filepath, broken))

    # 출력
    if broken_files:
        for filepath, broken_list in broken_files:
            rel = os.path.relpath(filepath)
            print(f"\n❌ {rel}")
            for lineno, link, target in broken_list:
                print(f"   L{lineno}: {link}")
    else:
        print("✅ 모든 링크 정상")

    print(f"\n{'─' * 60}")
    print(f"검사 파일: {len(files)}개 | 링크: {total_links}개 | 깨진 링크: {total_broken}건")

    sys.exit(1 if total_broken > 0 else 0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)

#!/usr/bin/env python3
#import sys; sys.exit(0)  # SAFETY: uncomment this line to disable script
"""
md-link-check.py — Markdown 내부 링크 존재 여부 검증
====================================================

사용법:
    python md-link-check.py <file_or_dir> [file_or_dir ...]
    python md-link-check.py /root/32_system-engineering-resources/
    python md-link-check.py README.md
    python md-link-check.py -v /root/32_system-engineering-resources/

검증 대상:
    - [text](relative/path.md) 형태의 상대경로 링크
    - [text](./path) 형태 포함

검증 제외:
    - http:// https:// 외부 링크
    - #anchor 앵커 링크
    - 코드블록 내부 링크
    - 인라인 코드 내부 링크

종료 코드:
    0 = 모든 링크 정상
    1 = 깨진 링크 발견
"""

VERSION = "26.07.04"

import argparse
import os
import re
import sys

# ── patterns ──────────────────────────────────────────────────────────────────

LINK_PATTERN = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
INLINE_CODE_PATTERN = re.compile(r'`+.+?`+')


def _blank_inline(m):
    """인라인 코드를 동일 길이 공백으로 치환."""
    return ' ' * len(m.group(0))

# ── functions ─────────────────────────────────────────────────────────────────

def parse_args():
    """커맨드라인 인자 파싱."""
    parser = argparse.ArgumentParser(
        description='Markdown 내부 링크 존재 여부 검증',
        epilog='Examples:\n'
               '  python md-link-check.py README.md\n'
               '  python md-link-check.py /root/32_system-engineering-resources/\n'
               '  python md-link-check.py -v README.md    파일별 링크 수 출력\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('paths', nargs='+', help='.md 파일 또는 디렉토리')
    parser.add_argument('-v', '--verbose', action='store_true', help='파일별 링크 수 출력')
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {VERSION}')
    return parser.parse_args()


def collect_md_files(paths):
    """경로 목록에서 .md 파일 수집. 존재하지 않는 경로는 경고 출력."""
    files = []
    for p in paths:
        if not os.path.exists(p):
            print(f"🟡 경로 없음: {p}", file=sys.stderr)
            continue
        if os.path.isfile(p) and p.endswith('.md'):
            files.append(p)
        elif os.path.isdir(p):
            for root, dirs, filenames in os.walk(p, followlinks=False):
                dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__')]
                for f in filenames:
                    if f.endswith('.md'):
                        files.append(os.path.join(root, f))
    return sorted(set(files))


def strip_code_blocks_preserve_lines(content, filepath=None):
    """코드블록·인라인 코드 내용을 제거 (행 번호 유지).

    라인 단위 토글 방식으로 코드 펜스를 판정합니다.
    줄 시작이 ``` 인 경우만 코드블록 경계로 인식하므로
    인라인 백틱(줄 중간)에 의한 오판을 방지합니다.
    홀수 펜스(unclosed code block) 감지 시 stderr 경고를 출력합니다.
    """
    lines = content.splitlines()
    result = []
    in_code = False
    fence_count = 0
    last_open_line = 0
    last_open_tag = ''
    nested_hints = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('```'):
            fence_count += 1
            if not in_code:
                # 열림
                in_code = True
                last_open_line = i
                last_open_tag = stripped
            else:
                # 닫힘 — 닫는 태그가 언어 태그를 포함하면 중첩 의심
                if stripped != '```' and len(stripped) > 3:
                    nested_hints.append((last_open_line, last_open_tag, i, stripped))
                in_code = False
            result.append('')
        elif in_code:
            result.append('')
        else:
            # 인라인 코드 제거 (길이 유지 불필요, 공백 치환)
            result.append(INLINE_CODE_PATTERN.sub(_blank_inline, line))
    if in_code and filepath:
        rel = os.path.relpath(filepath)
        print(f"🟡 unclosed code block: {rel} (fence count: {fence_count}, last open: L{last_open_line})", file=sys.stderr)
        if nested_hints:
            for open_line, open_tag, close_line, close_tag in nested_hints[:3]:
                print(f"   hint: nested fence at L{open_line} ({open_tag}) -> L{close_line} ({close_tag})", file=sys.stderr)
    return '\n'.join(result)


def extract_link_path(raw_link):
    """링크에서 경로만 추출 (앵커, title 속성 제거, URL 디코딩 적용)."""
    # path#anchor → path
    path = raw_link.split('#')[0]
    # path "title" or path 'title' → path
    path = path.split('"')[0].split("'")[0].rstrip()
    # URL 인코딩된 경로 디코딩 (%EA%B0%9C... → 한글)
    try:
        from urllib.parse import unquote
        path = unquote(path)
    except Exception:
        pass
    return path


def check_file(filepath):
    """파일 내 상대 링크 검증. (broken_list, total_count) 튜플 반환."""
    try:
        with open(filepath, encoding='utf-8') as f:
            raw_content = f.read()
    except (UnicodeDecodeError, OSError) as e:
        return ([(-1, f"[읽기 실패: {e}]", filepath)], 0)

    clean = strip_code_blocks_preserve_lines(raw_content, filepath=filepath)
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
        if args.verbose and link_count > 0 and not broken:
            rel = os.path.relpath(filepath)
            print(f"  ✅ {rel} ({link_count} links)")

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

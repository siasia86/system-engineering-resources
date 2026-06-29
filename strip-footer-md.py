#!/usr/bin/env python3
#import sys; sys.exit(0)  # SAFETY: uncomment this line to disable script
"""
md-strip-footer.py - Markdown 푸터(통계 배지, 작성일, 저작권) 일괄 제거

사용법:
    python3 md-strip-footer.py <dir>              디렉토리 전체
    python3 md-strip-footer.py <file> [file ...]  개별 파일
    python3 md-strip-footer.py -d <dir>           dry-run
    python3 md-strip-footer.py -o <dir> <src>     출력 디렉토리 지정 (원본 유지)
"""

VERSION = "26.06.29"

import argparse
import os
import re
import sys

# ── constants ─────────────────────────────────────────────────────────────────

FOOTER_MARKER = re.compile(r'^---\s*$')
STATS_MARKER = re.compile(r'^## 통계\s*$')
DATE_MARKER = re.compile(r'^\*\*작성일\*\*')
COPYRIGHT_MARKER = re.compile(r'^© \d{4}')


# ── core functions ────────────────────────────────────────────────────────────

def find_footer_start(lines):
    """푸터 시작 라인 인덱스 반환. 없으면 None."""
    # 패턴 1: ## 통계 로 시작
    for i, line in enumerate(lines):
        if STATS_MARKER.match(line.strip()):
            # ## 통계 앞의 --- 도 포함
            if i > 0 and FOOTER_MARKER.match(lines[i - 1].strip()):
                return i - 1
            return i

    # 패턴 2: --- + **작성일** (통계 없이 날짜만 있는 경우)
    for i, line in enumerate(lines):
        if FOOTER_MARKER.match(line.strip()) and i + 2 < len(lines):
            if DATE_MARKER.match(lines[i + 2].strip()):
                return i

    return None


def strip_footer(content):
    """푸터 제거 후 content 반환. 변경 없으면 원본 그대로."""
    lines = content.split('\n')
    idx = find_footer_start(lines)
    if idx is None:
        return content, False

    # 푸터 앞 빈줄 제거
    while idx > 0 and lines[idx - 1].strip() == '':
        idx -= 1

    result = '\n'.join(lines[:idx]).rstrip() + '\n'
    return result, True


def process_file(filepath, dry_run=False, output_dir=None):
    """단일 파일 처리."""
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    new_content, changed = strip_footer(content)

    if not changed:
        return False

    if dry_run:
        print(f"  [dry-run] {filepath}")
        return True

    if output_dir:
        out_path = os.path.join(output_dir, filepath)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    else:
        out_path = filepath

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True


# ── entry point ───────────────────────────────────────────────────────────────

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Markdown 푸터(통계, 작성일, 저작권) 일괄 제거',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "\nExamples:\n"
            "  %(prog)s 06_security/01_cve/          디렉토리 전체 (in-place)\n"
            "  %(prog)s -d 06_security/01_cve/       dry-run (변경 없이 대상만 출력)\n"
            "  %(prog)s -o /tmp/export/ 06_security/ 출력 디렉토리 (원본 유지)\n"
            "\nNotes:\n"
            "  - '## 통계' 또는 '**작성일**' 시작점부터 EOF까지 제거\n"
            "  - -o 미지정 시 원본 파일을 직접 수정 (in-place)\n"
        )
    )
    parser.add_argument('targets', nargs='+', metavar='path', help='파일 또는 디렉토리')
    parser.add_argument('-d', '--dry-run', action='store_true', help='변경 없이 대상만 출력')
    parser.add_argument('-o', '--output-dir', metavar='DIR', help='출력 디렉토리 (원본 유지)')
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {VERSION}')
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    files = []
    for target in args.targets:
        if os.path.isfile(target) and target.endswith('.md'):
            files.append(target)
        elif os.path.isdir(target):
            for root, _, fnames in os.walk(target):
                for f in sorted(fnames):
                    if f.endswith('.md'):
                        files.append(os.path.join(root, f))

    if not files:
        print("대상 .md 파일이 없습니다.")
        sys.exit(1)

    count = 0
    for fpath in files:
        if process_file(fpath, dry_run=args.dry_run, output_dir=args.output_dir):
            count += 1

    action = "제거 예정" if args.dry_run else "제거 완료"
    print(f"\n{action}: {count}/{len(files)}개 파일")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)

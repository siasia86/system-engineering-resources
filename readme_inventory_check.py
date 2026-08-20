#!/usr/bin/env python3
#import sys; sys.exit(0)  # SAFETY: uncomment this line to disable script
"""
readme_inventory_check.py - README에 표기된 문서 수와 실제 파일 수 검증

사용법:
    python3 readme_inventory_check.py README.md
    python3 readme_inventory_check.py -v README.md
"""

VERSION = "26.08.20"

import argparse
import re
import sys
from pathlib import Path


COUNT_PATTERN = re.compile(r"\]\(([^)#\n]+/)\)[^\n]*?\((\d+)개\)")
FENCE_PATTERN = re.compile(r"^\s*(`{3,})")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="README에 표기된 디렉토리 문서 수를 검증합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "\nExamples:\n"
            "  %(prog)s README.md       문서 수 검증\n"
            "  %(prog)s -v README.md   상세 결과 출력\n"
            "\nNotes:\n"
            "  - README의 '(N개)' 표기와 하위 디렉토리의 .md 파일 수를 비교합니다.\n"
            "  - README.md 자체는 문서 수에서 제외합니다.\n"
        ),
    )
    parser.add_argument("target", nargs="?", default="README.md", help="검사할 README 경로")
    parser.add_argument("-v", "--verbose", action="store_true", help="상세 결과 출력")
    parser.add_argument("-q", "--quiet", action="store_true", help="성공 메시지 생략")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {VERSION}")
    return parser.parse_args()


def count_markdown_files(directory):
    """Count Markdown files below a directory, excluding README.md files."""
    return sum(
        1
        for path in directory.rglob("*.md")
        if path.is_file() and path.name != "README.md"
    )


def strip_code_blocks(content):
    """Remove fenced code blocks before scanning Markdown links."""
    lines = []
    fence_length = 0
    for line in content.splitlines():
        match = FENCE_PATTERN.match(line)
        if match:
            current_length = len(match.group(1))
            if fence_length == 0:
                fence_length = current_length
            elif current_length >= fence_length:
                fence_length = 0
            continue
        if fence_length == 0:
            lines.append(line)
    return "\n".join(lines)


def check_inventory(readme_path, verbose=False, quiet=False):
    """Compare README count markers with actual Markdown file counts."""
    if not readme_path.is_file():
        print(f"ERROR: not found: {readme_path}", file=sys.stderr)
        return 1

    try:
        content = readme_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: cannot read {readme_path}: {exc}", file=sys.stderr)
        return 1

    content = strip_code_blocks(content)
    matches = list(COUNT_PATTERN.finditer(content))
    if not matches:
        print(f"ERROR: count marker not found: {readme_path}", file=sys.stderr)
        return 1

    failures = 0
    for match in matches:
        relative = match.group(1)
        expected = int(match.group(2))
        base_dir = readme_path.parent.resolve()
        directory = (base_dir / relative).resolve()
        if directory != base_dir and base_dir not in directory.parents:
            print(f"ERROR: path outside repository: {relative}", file=sys.stderr)
            failures += 1
            continue
        if not directory.is_dir():
            print(f"ERROR: directory not found: {relative}", file=sys.stderr)
            failures += 1
            continue
        try:
            actual = count_markdown_files(directory)
        except OSError as exc:
            print(f"ERROR: cannot scan {relative}: {exc}", file=sys.stderr)
            failures += 1
            continue
        if actual != expected:
            print(
                f"FAIL: {relative} README={expected} actual={actual}",
                file=sys.stderr,
            )
            failures += 1
        elif verbose:
            print(f"OK: {relative} {actual}개")

    if failures:
        print(f"ERROR: {failures} inventory mismatch(es)", file=sys.stderr)
        return 1
    if not quiet:
        print(f"OK: {len(matches)} inventory marker(s) verified")
    return 0


def main():
    """Run the README inventory check."""
    args = parse_args()
    return check_inventory(Path(args.target), verbose=args.verbose, quiet=args.quiet)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)

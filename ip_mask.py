#!/usr/bin/env python3
#import sys; sys.exit(0)  # SAFETY: uncomment this line to disable script
"""
ip_mask.py - 회사 IP 대역 마스킹 / 원복 도구

112.185.196.X → 192.168.196.X
112.185.197.X → 192.168.197.X (X 유지)

사용법:
    python ip_mask.py <file|dir>           마스킹
    python ip_mask.py -r <file|dir>        원복
    python ip_mask.py -D <dir1> <dir2>     여러 디렉토리 마스킹
    python ip_mask.py -r -D <dir1> <dir2>  여러 디렉토리 원복
    python ip_mask.py -d <file|dir>           dry-run (변경 없이 대상만 출력)
"""

VERSION = "26.04.14"

import re
import os
import argparse
import sys
import logging
from datetime import datetime

def _setup_logger(name='ip_mask'):
    """콘솔 + /var/log/sjyun/ 파일 동시 출력 로거 (파일 생성 실패 시 콘솔만)"""
    fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    lgr = logging.getLogger(name)
    lgr.setLevel(logging.INFO)
    if not lgr.handlers:
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        lgr.addHandler(ch)
        try:
            log_dir = '/var/log/sjyun'
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m')}.log")
            fh = logging.FileHandler(log_path, encoding='utf-8')
            fh.setFormatter(fmt)
            lgr.addHandler(fh)
        except OSError:
            lgr.warning(f"log file creation failed, console only")
    return lgr

log = _setup_logger()

def _escape(prefix):
    return re.escape(prefix)

def load_pairs(config_path=None):
    """ip_mask.toml 로드하여 IP 치환 쌍 반환. 없으면 기본값 사용."""
    default = [
        ('112.185.196', '192.168.196'),
        ('112.185.197', '192.168.197'),
    ]
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ip_mask.toml')

    pairs = default
    if os.path.exists(config_path):
        try:
            if sys.version_info >= (3, 11):
                import tomllib
            else:
                import tomli as tomllib
            with open(config_path, 'rb') as f:
                cfg = tomllib.load(f)
            pairs = [(p['src'], p['dst']) for p in cfg.get('pairs', [])] or default
            log.info(f"config loaded: {config_path} ({len(pairs)} pairs)")
        except Exception as e:
            log.warning(f"config failed to load {config_path}: {e}, using defaults")

    ip_pairs = [(re.compile(rf'{_escape(src)}\.(\d{{1,3}})'), dst) for src, dst in pairs]
    ip_pairs_restore = [(re.compile(rf'{_escape(dst)}\.(\d{{1,3}})'), src) for src, dst in pairs]
    return ip_pairs, ip_pairs_restore

IP_PAIRS, IP_PAIRS_RESTORE = load_pairs()

# 바이너리/불필요 확장자 제외
SKIP_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.bin',
             '.zip', '.tar', '.gz', '.tgz', '.jar', '.bak',
             '.so', '.exe', '.dll', '.db', '.dat', '.pyc', '.o'}


def process_file(filepath, restore=False, dry_run=False):
    """파일 내 IP 치환 (해당 패턴 없으면 스킵)"""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in SKIP_EXTS:
        return

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except OSError:
        return

    pairs = IP_PAIRS_RESTORE if restore else IP_PAIRS
    new_content = content
    for pattern, dst in pairs:
        new_content = pattern.sub(lambda m, d=dst: f'{d}.{m.group(1)}', new_content)

    if new_content == content:
        return

    action = 'restored' if restore else 'masked '
    if dry_run:
        RED    = '\033[0;31m'
        GREEN  = '\033[0;32m'
        PURPLE = '\033[0;35m'
        GRAY   = '\033[0;90m'
        RESET  = '\033[0m'
        changed = [(i+1, old_l, new_l)
                   for i, (old_l, new_l) in enumerate(zip(content.splitlines(), new_content.splitlines()))
                   if old_l != new_l]
        print(f"[DRY-RUN] {PURPLE}{filepath}{RESET}  ({len(changed)} lines changed)")
        if changed:
            max_lnum = max(c[0] for c in changed)
            lw = len(str(max_lnum))
            src_pairs = IP_PAIRS_RESTORE if restore else IP_PAIRS
            dst_pairs = IP_PAIRS if restore else IP_PAIRS_RESTORE
            for lnum, old_l, new_l in changed:
                # 변경 전: 원본 IP만 초록색 (src 패턴으로 매칭)
                old_hi = old_l.rstrip()
                for pat, dst in src_pairs:
                    old_hi = pat.sub(lambda m: f"{GREEN}{m.group(0)}{RESET}", old_hi)
                # 변경 후: 새 IP만 빨간색 (dst 패턴으로 매칭)
                new_hi = new_l.rstrip()
                for pat, dst in dst_pairs:
                    new_hi = pat.sub(lambda m: f"{RED}{m.group(0)}{RESET}", new_hi)
                print(f"  {GRAY}line {lnum:{lw}}{RESET}  - {old_hi}")
                print(f"  {GRAY}line {lnum:{lw}}{RESET}  + {new_hi}")
        return
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    log.info(f"{action}: {filepath}")


def process_dir(dirpath, restore=False, dry_run=False):
    """디렉토리 내 모든 파일 재귀 처리 (.git 제외)"""
    for root, dirs, files in os.walk(dirpath):
        # .git 디렉토리 제외
        dirs[:] = [d for d in dirs if d != '.git']
        for fname in files:
            process_file(os.path.join(root, fname), restore=restore, dry_run=dry_run)


def main():
    parser = argparse.ArgumentParser(
        description='회사 IP 마스킹/원복 (112.185.196.X↔192.168.196.X / 112.185.197.X↔192.168.197.X)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "\n사용 예시:\n"
            "  %(prog)s config.txt              단일 파일 마스킹\n"
            "  %(prog)s -r config.txt           단일 파일 원복\n"
            "  %(prog)s ./configs/              디렉토리 마스킹\n"
            "  %(prog)s -D ./configs/ ./scripts/ 여러 디렉토리 마스킹\n"
            "  %(prog)s -r -D ./configs/        디렉토리 원복\n"
            "\n주의:\n"
            "  map 파일 없이 패턴 역치환으로 원복합니다.\n"
            "  192.168.196.X / 192.168.197.X 가 원래부터 있던 IP라면 원복 시 변경될 수 있습니다.\n"
        )
    )
    parser.add_argument('target', nargs='?', help='파일 또는 디렉토리 경로')
    parser.add_argument('-r', '--restore', action='store_true', help='원복 모드')
    parser.add_argument('-d', '--dry-run', action='store_true', help='dry-run: 변경 없이 대상 파일/내용만 출력')
    parser.add_argument('-D', '--dir', nargs='+', metavar='DIR', help='디렉토리 일괄 처리 (여러 개 가능)')
    args = parser.parse_args()
    dry_run = args.dry_run

    if args.dir:
        for d in args.dir:
            if os.path.isdir(d):
                process_dir(d, restore=args.restore, dry_run=dry_run)
            else:
                log.error(f"not found: {d}")
    elif args.target:
        if os.path.isdir(args.target):
            process_dir(args.target, restore=args.restore, dry_run=dry_run)
        elif os.path.isfile(args.target):
            process_file(args.target, restore=args.restore, dry_run=dry_run)
        else:
            log.error(f"not found: {args.target}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

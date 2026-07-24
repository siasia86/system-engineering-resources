#!/usr/bin/env python3
#import sys; sys.exit(0)  # SAFETY: uncomment this line to disable script
"""
win_hosts_manager.py - Windows hosts 파일 DNS 엔트리 관리

원격 또는 로컬 Windows 서버의 hosts 파일에 DNS 엔트리를 추가/삭제/조회합니다.
관리자 권한 체크를 포함하며, 멱등성을 보장합니다.

사용법:
    python3 win_hosts_manager.py add -H 192.0.2.1 -n app.example.com
    python3 win_hosts_manager.py add -f entries.txt
    python3 win_hosts_manager.py remove -n app.example.com
    python3 win_hosts_manager.py list
    python3 win_hosts_manager.py add -d -H 192.0.2.1 -n app.example.com
"""

VERSION = "26.07.24"

import argparse
import ctypes
import logging
import os
import platform
import re
import shutil
import sys
import tempfile
from datetime import datetime

# ── logger ────────────────────────────────────────────────────────────────────

def _setup_logger(name='win_hosts_manager'):
    """콘솔 + 로그파일 동시 출력 로거."""
    fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    lgr = logging.getLogger(name)
    lgr.setLevel(logging.INFO)
    if not lgr.handlers:
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        lgr.addHandler(ch)
        try:
            if platform.system() == 'Windows':
                log_dir = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'sjyun_logs')
            else:
                log_dir = '/var/log/sjyun'
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m')}.log")
            fh = logging.FileHandler(log_path, encoding='utf-8')
            fh.setFormatter(fmt)
            lgr.addHandler(fh)
        except OSError:
            lgr.warning("log file creation failed, console only")
    return lgr


log = _setup_logger()

# ── colors ────────────────────────────────────────────────────────────────────
_RED = '\033[0;31m'
_YELLOW = '\033[0;33m'
_GREEN = '\033[0;32m'
_GRAY = '\033[0;90m'
_RESET = '\033[0m'


def _c(text, color=_RED):
    """Colorize text (no-op if not a tty)."""
    if sys.stdout.isatty() or sys.stderr.isatty():
        return f'{color}{text}{_RESET}'
    return text


# ── constants ─────────────────────────────────────────────────────────────────

if platform.system() == 'Windows':
    HOSTS_PATH = r'C:\Windows\System32\drivers\etc\hosts'
else:
    HOSTS_PATH = '/etc/hosts'

ENTRY_PATTERN = re.compile(r'^(\d{1,3}(?:\.\d{1,3}){3})\s+(.+)$')
COMMENT_MARKER = '# Managed by win_hosts_manager'

# ── utilities ─────────────────────────────────────────────────────────────────


def is_admin():
    """현재 프로세스가 관리자/root 권한인지 확인."""
    if platform.system() == 'Windows':
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except AttributeError:
            return False
    else:
        return os.geteuid() == 0


def request_admin_restart():
    """Windows에서 관리자 권한으로 재실행 (UAC 프롬프트)."""
    if platform.system() == 'Windows':
        log.error("관리자 권한 필요. UAC 프롬프트로 재실행합니다.")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)
    else:
        log.error(f"root 권한 필요. sudo로 실행하세요: sudo {' '.join(sys.argv)}")
        sys.exit(1)


def read_hosts(filepath=None):
    """hosts 파일을 읽어 라인 리스트 반환."""
    path = filepath or HOSTS_PATH
    if not os.path.isfile(path):
        log.error(f"hosts file not found: {path}")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.readlines()


def write_hosts(lines, filepath=None, dry_run=False):
    """hosts 파일에 안전하게 쓰기 (atomic write + backup)."""
    path = filepath or HOSTS_PATH
    if dry_run:
        log.info(f"[dry-run] would write {len(lines)} lines to {_c(path, _YELLOW)}")
        return

    # 백업 생성
    backup_path = path + f'.bak_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    try:
        shutil.copy2(path, backup_path)
        log.info(f"backup: {_c(backup_path, _GRAY)}")
    except OSError as e:
        log.warning(f"backup failed: {e}")

    # atomic write
    dir_name = os.path.dirname(path) or '.'
    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix='.hosts_tmp_')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        if platform.system() == 'Windows':
            os.remove(path)
        os.replace(tmp_path, path)
    except OSError:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    log.info(f"written: {_c(path, _GREEN)}")


def parse_entry(line):
    """hosts 라인에서 (ip, hostnames) 추출. 주석/빈줄은 None."""
    stripped = line.strip()
    if not stripped or stripped.startswith('#'):
        return None
    match = ENTRY_PATTERN.match(stripped)
    if match:
        ip = match.group(1)
        hostnames = match.group(2).split()
        hostnames = [h for h in hostnames if not h.startswith('#')]
        return (ip, hostnames)
    return None


# ── core functions ────────────────────────────────────────────────────────────


def list_entries(filepath=None):
    """현재 hosts 엔트리 출력."""
    lines = read_hosts(filepath)
    entries = []
    for line in lines:
        parsed = parse_entry(line)
        if parsed:
            ip, hostnames = parsed
            for h in hostnames:
                entries.append((ip, h))

    if not entries:
        print("(no entries)")
        return

    max_ip = max(len(e[0]) for e in entries)
    print(f"\n{'IP':<{max_ip}}  HOSTNAME")
    print(f"{'-' * max_ip}  {'-' * 40}")
    for ip, hostname in entries:
        print(f"{ip:<{max_ip}}  {hostname}")
    print(f"\ntotal: {len(entries)} entries")


def add_entry(ip, hostname, filepath=None, dry_run=False, verbose=False):
    """hosts 파일에 엔트리 추가 (멱등: 이미 있으면 skip)."""
    lines = read_hosts(filepath)

    for line in lines:
        parsed = parse_entry(line)
        if parsed:
            existing_ip, hostnames = parsed
            if hostname in hostnames:
                if existing_ip == ip:
                    log.info(f"already exists: {ip} {hostname} — skip")
                    return False
                else:
                    log.info(f"updating: {existing_ip} → {ip} for {hostname}")
                    return update_entry(ip, hostname, filepath, dry_run, verbose)

    new_line = f"{ip}    {hostname}  {COMMENT_MARKER}\n"
    if dry_run:
        log.info(f"[dry-run] would add: {_c(new_line.strip(), _GREEN)}")
        return True

    if lines and not lines[-1].endswith('\n'):
        lines[-1] += '\n'
    lines.append(new_line)
    write_hosts(lines, filepath, dry_run=False)
    log.info(f"added: {_c(f'{ip} {hostname}', _GREEN)}")
    return True


def update_entry(ip, hostname, filepath=None, dry_run=False, verbose=False):
    """기존 hostname의 IP를 변경."""
    lines = read_hosts(filepath)
    new_lines = []
    updated = False

    for line in lines:
        parsed = parse_entry(line)
        if parsed:
            existing_ip, hostnames = parsed
            if hostname in hostnames and existing_ip != ip:
                new_line = f"{ip}    {hostname}  {COMMENT_MARKER}\n"
                new_lines.append(new_line)
                updated = True
                if verbose:
                    log.info(f"  {existing_ip} → {ip} for {hostname}")
                continue
        new_lines.append(line)

    if updated:
        write_hosts(new_lines, filepath, dry_run)
    return updated


def remove_entry(hostname, filepath=None, dry_run=False, verbose=False):
    """hostname 기준으로 엔트리 삭제."""
    lines = read_hosts(filepath)
    new_lines = []
    removed = False

    for line in lines:
        parsed = parse_entry(line)
        if parsed:
            existing_ip, hostnames = parsed
            if hostname in hostnames:
                removed = True
                if dry_run:
                    log.info(f"[dry-run] would remove: {_c(line.strip(), _RED)}")
                else:
                    log.info(f"removed: {_c(f'{existing_ip} {hostname}', _RED)}")
                continue
        new_lines.append(line)

    if removed and not dry_run:
        write_hosts(new_lines, filepath, dry_run=False)
    elif not removed:
        log.info(f"not found: {hostname} — skip")

    return removed


def add_from_file(entries_file, filepath=None, dry_run=False, verbose=False):
    """파일에서 엔트리 목록 읽어 일괄 추가."""
    if not os.path.isfile(entries_file):
        log.error(f"entries file not found: {entries_file}")
        sys.exit(1)

    count = 0
    with open(entries_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            parts = stripped.split(None, 1)
            if len(parts) != 2:
                log.warning(f"line {line_num}: invalid format: {stripped}")
                continue
            ip, hostname = parts[0], parts[1].split()[0]
            if add_entry(ip, hostname, filepath, dry_run, verbose):
                count += 1

    log.info(f"processed: {count} entries from {entries_file}")


# ── entry point ───────────────────────────────────────────────────────────────


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Windows/Linux hosts 파일 DNS 엔트리 관리',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "\nExamples:\n"
            "  %(prog)s add -H 192.0.2.1 -n app.example.com\n"
            "  %(prog)s add -f entries.txt\n"
            "  %(prog)s remove -n app.example.com\n"
            "  %(prog)s list\n"
            "  %(prog)s add -d -H 192.0.2.1 -n app.example.com   dry-run\n"
            "\nEntries file format (one per line):\n"
            "  192.0.2.1  app.example.com\n"
            "  192.0.2.2  db.example.com\n"
            "\nNotes:\n"
            "  - 멱등성 보장: 동일 엔트리 재실행 시 skip\n"
            "  - 관리자/root 권한 필요 (자동 체크)\n"
            "  - 변경 시 자동 백업 생성 (.bak_YYYYMMDD_HHMMSS)\n"
        )
    )
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {VERSION}')
    parser.add_argument('-d', '--dry-run', action='store_true', help='변경 없이 출력만')
    parser.add_argument('-v', '--verbose', action='store_true', help='상세 출력')
    parser.add_argument('--path', help='hosts 파일 경로 (기본: 시스템 hosts)')

    sub = parser.add_subparsers(dest='command', help='명령어')

    add_p = sub.add_parser('add', help='엔트리 추가')
    add_p.add_argument('-H', '--host-ip', help='IP 주소')
    add_p.add_argument('-n', '--name', help='호스트명')
    add_p.add_argument('-f', '--file', help='엔트리 목록 파일 (IP HOSTNAME)')

    rm_p = sub.add_parser('remove', help='엔트리 삭제')
    rm_p.add_argument('-n', '--name', required=True, help='삭제할 호스트명')

    sub.add_parser('list', help='현재 엔트리 목록')

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    if not args.command:
        log.error("command required: add, remove, list")
        sys.exit(1)

    filepath = args.path

    if args.command == 'list':
        list_entries(filepath)
        return

    if not args.dry_run and not is_admin():
        request_admin_restart()

    if args.command == 'add':
        if args.file:
            add_from_file(args.file, filepath, args.dry_run, args.verbose)
        elif args.host_ip and args.name:
            add_entry(args.host_ip, args.name, filepath, args.dry_run, args.verbose)
        else:
            log.error("add requires (-H and -n) or (-f)")
            sys.exit(1)

    elif args.command == 'remove':
        remove_entry(args.name, filepath, args.dry_run, args.verbose)

    if not args.dry_run and platform.system() == 'Windows':
        log.info("run 'ipconfig /flushdns' to apply DNS changes immediately")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)

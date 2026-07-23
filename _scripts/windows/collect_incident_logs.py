#!/usr/bin/env python3
#import sys; sys.exit(0)  # SAFETY: uncomment this line to disable script
"""
collect_incident_logs.py - Windows Server 장애 사후 로그 일괄 수집

장애 발생 후 원인 분석에 필요한 Event Log, 성능 카운터, VM 상태,
시스템 정보를 C:\\temp\\incident_YYYYMMDD_HHMMSS\ 에 수집합니다.

사용법:
    python collect_incident_logs.py                기본 (7일, 5분)
    python collect_incident_logs.py -d 3           3일치 수집
    python collect_incident_logs.py -d 3 -t 60     3일, 1분 카운터
    python collect_incident_logs.py --dry-run      실행 없이 명령어 출력
"""

VERSION = "26.07.23"

import argparse
import ctypes
import os
import subprocess
import sys
from datetime import datetime


# ── colors ────────────────────────────────────────────────────────────────────
_CYAN = '\033[0;36m'
_GREEN = '\033[0;32m'
_YELLOW = '\033[0;33m'
_RED = '\033[0;31m'
_GRAY = '\033[0;90m'
_RESET = '\033[0m'


def _c(text, color=_CYAN):
    """Colorize text (no-op if not a tty or Windows without ANSI support)."""
    if not sys.stdout.isatty():
        return text
    if sys.platform == 'win32':
        # Windows 10+ ANSI 활성화 시도
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            return text
    return f'{color}{text}{_RESET}'


# ── PowerShell executor ───────────────────────────────────────────────────────
def run_ps(cmd, dry_run=False):
    """Execute PowerShell command and return stdout."""
    full_cmd = [
        'powershell', '-ExecutionPolicy', 'Bypass', '-NoProfile', '-Command', cmd
    ]
    if dry_run:
        print(f"  [dry-run] {cmd[:100]}...")
        return ""
    result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0 and result.stderr.strip():
        # Ignore common non-critical errors
        if "NoMatchingEventsFound" not in result.stderr:
            print(f"  {_c('WARN', _YELLOW)}: {result.stderr.strip()[:200]}")
    return result.stdout


def run_ps_to_file(cmd, filepath, dry_run=False):
    """Execute PowerShell command and save to CSV file. Returns size or -1 on error."""
    export_cmd = f"{cmd} | Export-Csv -Path '{filepath}' -NoTypeInformation -Encoding UTF8"
    result = run_ps(export_cmd, dry_run)
    if dry_run:
        return 0
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        if size > 3:  # BOM-only file = empty result
            return size
        else:
            os.remove(filepath)
            return 0
    return -1  # error: file not created


# ── collection functions ──────────────────────────────────────────────────────
def collect_event_logs(out_dir, days, dry_run=False):
    """Collect Event Logs."""
    print(_c("[1/6] Event Logs...", _YELLOW))

    logs = [
        ("event_system", f"Get-WinEvent -FilterHashtable @{{LogName='System'; StartTime=(Get-Date).AddDays(-{days})}} 2>$null | Select-Object TimeCreated, ProviderName, Id, LevelDisplayName, Message"),
        ("event_application", f"Get-WinEvent -FilterHashtable @{{LogName='Application'; StartTime=(Get-Date).AddDays(-{days})}} 2>$null | Select-Object TimeCreated, ProviderName, Id, LevelDisplayName, Message"),
        ("event_StorageVSP", "Get-WinEvent -LogName 'Microsoft-Windows-Hyper-V-StorageVSP-Admin' 2>$null | Select-Object TimeCreated, Id, LevelDisplayName, Message"),
        ("event_HyperV_Worker", "Get-WinEvent -LogName 'Microsoft-Windows-Hyper-V-Worker-Admin' 2>$null | Select-Object TimeCreated, Id, LevelDisplayName, Message"),
        ("event_HyperV_VMMS", "Get-WinEvent -LogName 'Microsoft-Windows-Hyper-V-VMMS-Operational' 2>$null | Select-Object TimeCreated, Id, LevelDisplayName, Message"),
        ("event_Storport", "Get-WinEvent -LogName 'Microsoft-Windows-Storage-Storport/Operational' 2>$null | Select-Object TimeCreated, Id, LevelDisplayName, Message"),
    ]

    for name, cmd in logs:
        filepath = os.path.join(out_dir, f"{name}.csv")
        size = run_ps_to_file(cmd, filepath, dry_run)
        if dry_run:
            continue
        if size > 0:
            print(f"  {_c(name, _GREEN)}: {size // 1024} KB")
        elif size == -1:
            print(f"  {_c(name, _RED)}: ERROR (file not created)")
        else:
            print(f"  {_c(name, _GRAY)}: 0 events (skip)")








def collect_perf_counters(out_dir, duration, interval, dry_run=False):
    """Collect Performance Counters."""
    max_samples = duration // interval
    print(_c(f"[2/6] Performance Counters ({duration}s, {max_samples} samples)...", _YELLOW))

    filepath = os.path.join(out_dir, "perfmon_snapshot.csv")
    counters = [
        '\\Processor(_Total)\\% Processor Time',
        '\\Memory\\Available MBytes',
        '\\Memory\\% Committed Bytes In Use',
        '\\PhysicalDisk(*)\\Avg. Disk sec/Read',
        '\\PhysicalDisk(*)\\Avg. Disk sec/Write',
        '\\PhysicalDisk(*)\\Current Disk Queue Length',
        '\\PhysicalDisk(*)\\Disk Transfers/sec',
        '\\Network Interface(*)\\Bytes Total/sec',
        '\\Hyper-V Hypervisor Logical Processor(_Total)\\% Total Run Time',
        '\\Hyper-V Virtual Storage Device(*)\\Latency',
    ]
    counter_str = "', '".join(counters)
    cmd = f"Get-Counter -Counter @('{counter_str}') -SampleInterval {interval} -MaxSamples {max_samples} | Export-Counter -Path '{filepath}' -FileFormat CSV"

    if dry_run:
        print(f"  [dry-run] Get-Counter ... -MaxSamples {max_samples}")
        return

    print(f"  Collecting {max_samples} samples ({duration}s)...")
    run_ps(cmd)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"  {_c('perfmon_snapshot.csv', _GREEN)}: {size // 1024} KB")
    else:
        print(f"  {_c('perfmon: no data', _RED)}")


def collect_vm_status(out_dir, dry_run=False):
    """Collect VM status."""
    print(_c("[3/6] VM Status...", _YELLOW))

    queries = [
        ("vm_status", "Get-VM | Select-Object Name, State, CPUUsage, MemoryAssigned, MemoryDemand, Uptime, Status, Version"),
        ("vm_vhd_path", "Get-VM | Get-VMHardDiskDrive | Select-Object VMName, ControllerType, ControllerNumber, ControllerLocation, Path"),
        ("vm_network", "Get-VM | Get-VMNetworkAdapter | Select-Object VMName, SwitchName, MacAddress, IPAddresses"),
    ]

    for name, cmd in queries:
        filepath = os.path.join(out_dir, f"{name}.csv")
        size = run_ps_to_file(cmd, filepath, dry_run)
        if not dry_run and size > 0:
            print(f"  {_c(name, _GREEN)}: {size // 1024} KB")


def collect_system_info(out_dir, dry_run=False):
    """Collect system information."""
    print(_c("[4/6] System Info...", _YELLOW))

    # systeminfo
    sysinfo_path = os.path.join(out_dir, "systeminfo.txt")
    if not dry_run:
        result = subprocess.run(['systeminfo'], capture_output=True, text=True, timeout=120)
        with open(sysinfo_path, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
    else:
        print("  [dry-run] systeminfo")

    queries = [
        ("physical_disk", "Get-PhysicalDisk | Select-Object FriendlyName, MediaType, Size, HealthStatus, OperationalStatus"),
        ("iscsi_session", "Get-IscsiSession 2>$null | Select-Object TargetNodeAddress, IsConnected, NumberOfConnections"),
        ("csv_volume", "Get-ClusterSharedVolume 2>$null | Select-Object Name, State, OwnerNode"),
    ]

    for name, cmd in queries:
        filepath = os.path.join(out_dir, f"{name}.csv")
        run_ps_to_file(cmd, filepath, dry_run)

    if not dry_run:
        print(f"  {_c('systeminfo/disk/iscsi/csv: done', _GREEN)}")


def collect_overcommit(out_dir, dry_run=False):
    """Collect overcommit information."""
    print(_c("[5/6] Overcommit Check...", _YELLOW))

    cmd = """
$totalLogical = (Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum
$totalVCPU = (Get-VM | Where-Object State -eq 'Running' | Measure-Object -Property ProcessorCount -Sum).Sum
$totalRAM = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
$totalVMRAM = (Get-VM | Where-Object State -eq 'Running' | Measure-Object -Property MemoryAssigned -Sum).Sum
[PSCustomObject]@{
    PhysicalCores = $totalLogical
    TotalVCPU = $totalVCPU
    CPURatio = "$([math]::Round($totalVCPU/$totalLogical,1)):1"
    PhysicalRAM_GB = [math]::Round($totalRAM/1GB,0)
    VMAssigned_GB = [math]::Round($totalVMRAM/1GB,0)
    MemoryRatio = "$([math]::Round($totalVMRAM/$totalRAM*100,0))%"
}
"""
    filepath = os.path.join(out_dir, "overcommit.csv")
    size = run_ps_to_file(cmd.strip(), filepath, dry_run)

    if not dry_run:
        # Print summary
        result = run_ps("$l=(Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum; $v=(Get-VM | Where-Object State -eq 'Running' | Measure-Object -Property ProcessorCount -Sum).Sum; Write-Host \"CPU: ${v}vCPU/${l}cores Memory: collected\"")
        print(f"  {_c('overcommit.csv: done', _GREEN)}")


def print_summary(out_dir):
    """Print collection summary."""
    print(_c("\n[6/6] Summary...", _YELLOW))
    total_size = 0
    files = []
    for f in sorted(os.listdir(out_dir)):
        fpath = os.path.join(out_dir, f)
        size = os.path.getsize(fpath)
        total_size += size
        files.append((f, size))

    print(f"  {'File':<35} {'Size':>10}")
    print(f"  {'-'*35} {'-'*10}")
    for name, size in files:
        print(f"  {name:<35} {size//1024:>7} KB")

    print(f"\n{_c('=== Collection Complete ===', _CYAN)}")
    print(f"  Directory: {_c(out_dir, _CYAN)}")
    print(f"  Total Size: {_c(f'{total_size // (1024*1024)} MB', _CYAN)}")
    print(f"  Files: {_c(str(len(files)), _CYAN)}")


# ── entry point ───────────────────────────────────────────────────────────────
def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Windows Server 장애 사후 로그 일괄 수집',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "\nExamples:\n"
            "  %(prog)s                     기본 (7일, 5분 카운터)\n"
            "  %(prog)s -d 3                3일치 수집\n"
            "  %(prog)s -d 3 -t 60          3일, 1분 카운터\n"
            "  %(prog)s --dry-run           실행 없이 명령어 출력\n"
            "\nNotes:\n"
            "  - 관리자 권한 필요 (Event Log, Hyper-V cmdlet)\n"
            "  - 성능 카운터 수집 중 대기 시간 발생 (기본 5분)\n"
            "  - 출력: C:\\temp\\incident_YYYYMMDD_HHMMSS\\\n"
        )
    )
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {VERSION}')
    parser.add_argument('-d', '--days', type=int, default=7, help='Event Log 수집 범위 (일, 기본: 7)')
    parser.add_argument('-t', '--perf-duration', type=int, default=300, help='성능 카운터 수집 시간 (초, 기본: 300)')
    parser.add_argument('-i', '--perf-interval', type=int, default=10, help='성능 카운터 수집 간격 (초, 기본: 10)')
    parser.add_argument('--dry-run', action='store_true', help='실행 없이 명령어 출력')
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Check platform
    if sys.platform != 'win32':
        print(f"{_c('ERROR', _RED)}: Windows에서만 실행 가능합니다.")
        sys.exit(1)


    # Check admin privileges

    if not ctypes.windll.shell32.IsUserAnAdmin():
        print(f"{_c('WARNING', _YELLOW)}: 관리자 권한 없음 — Hyper-V/Storport 로그 수집 불가")
        print(f"  → 관리자 CMD에서 다시 실행하세요")
        print(f"  → 계속 진행하면 System/Application만 수집됩니다")
        print()
        resp = input("  계속 진행하시겠습니까? (y/N): ").strip().lower()
        if resp != 'y':
            sys.exit(0)
    # Create output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = f"C:\\temp\\incident_{timestamp}"

    if not args.dry_run:
        os.makedirs(out_dir, exist_ok=True)

    print(_c("=== Incident Log Collection ===", _CYAN))
    print(f"  Output: {_c(out_dir, _CYAN)}")
    print(f"  Period: {args.days} days, Perf: {args.perf_duration}s @ {args.perf_interval}s interval")
    if args.dry_run:
        print(f"  Mode: {_c('DRY-RUN', _YELLOW)}")
    print()

    # Collect
    collect_event_logs(out_dir, args.days, args.dry_run)
    print()
    collect_perf_counters(out_dir, args.perf_duration, args.perf_interval, args.dry_run)
    print()
    collect_vm_status(out_dir, args.dry_run)
    print()
    collect_system_info(out_dir, args.dry_run)
    print()
    collect_overcommit(out_dir, args.dry_run)

    if not args.dry_run:
        print_summary(out_dir)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
    except subprocess.TimeoutExpired:
        print(f"\n{_c('ERROR', _RED)}: 명령어 실행 시간 초과 (timeout)")
        sys.exit(1)

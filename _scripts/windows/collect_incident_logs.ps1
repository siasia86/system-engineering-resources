#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Windows Server 장애 사후 로그 일괄 수집 스크립트

.DESCRIPTION
    장애 발생 후 원인 분석에 필요한 Event Log, 성능 카운터, VM 상태,
    시스템 정보를 C:\temp\incident_YYYYMMDD_HHMMSS\ 에 수집합니다.
    이벤트 로그 순환(overwrite) 전에 즉시 실행해야 합니다.

.PARAMETER Days
    Event Log 수집 범위 (일). 기본값: 7

.PARAMETER PerfDuration
    성능 카운터 수집 시간 (초). 기본값: 300 (5분)

.PARAMETER PerfInterval
    성능 카운터 수집 간격 (초). 기본값: 10

.EXAMPLE
    .\collect_incident_logs.ps1
    .\collect_incident_logs.ps1 -Days 3 -PerfDuration 60

.NOTES
    Version: 26.07.23
    Output:  C:\temp\incident_YYYYMMDD_HHMMSS\
#>

param(
    [int]$Days = 7,
    [int]$PerfDuration = 300,
    [int]$PerfInterval = 10
)

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$dir = "C:\temp\incident_$timestamp"
New-Item -ItemType Directory -Path $dir -Force | Out-Null
Write-Host "=== Incident Log Collection ===" -ForegroundColor Cyan
Write-Host "Output: $dir" -ForegroundColor Cyan
Write-Host "Period: $Days days, Perf: ${PerfDuration}s @ ${PerfInterval}s interval"
Write-Host ""

# ── Event Log ─────────────────────────────────────────────────────────────────
Write-Host "[1/6] Event Logs..." -ForegroundColor Yellow
$startTime = (Get-Date).AddDays(-$Days)

$eventLogs = @(
    @{Name='event_system';       Filter=@{LogName='System'; StartTime=$startTime}},
    @{Name='event_application';  Filter=@{LogName='Application'; StartTime=$startTime}},
    @{Name='event_StorageVSP';   Filter=@{LogName='Microsoft-Windows-Hyper-V-StorageVSP-Admin'}},
    @{Name='event_HyperV_Worker'; Filter=@{LogName='Microsoft-Windows-Hyper-V-Worker-Admin'}},
    @{Name='event_HyperV_VMMS';  Filter=@{LogName='Microsoft-Windows-Hyper-V-VMMS-Operational'}},
    @{Name='event_Storport';     Filter=@{LogName='Microsoft-Windows-Storage-Storport/Operational'}}
)

foreach ($log in $eventLogs) {
    try {
        $events = Get-WinEvent -FilterHashtable $log.Filter -ErrorAction Stop
        if ($events) {
            $events | Select-Object TimeCreated, ProviderName, Id, LevelDisplayName, Message |
            Export-Csv -Path "$dir\$($log.Name).csv" -NoTypeInformation -Encoding UTF8
            Write-Host "  $($log.Name): $($events.Count) events" -ForegroundColor Green
        } else {
            Write-Host "  $($log.Name): 0 events (skip)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  $($log.Name): ERROR - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ── Performance Counters ──────────────────────────────────────────────────────
Write-Host "`n[2/6] Performance Counters (${PerfDuration}s)..." -ForegroundColor Yellow
$counters = @(
    '\Processor(_Total)\% Processor Time',
    '\Memory\Available MBytes',
    '\Memory\% Committed Bytes In Use',
    '\PhysicalDisk(*)\Avg. Disk sec/Read',
    '\PhysicalDisk(*)\Avg. Disk sec/Write',
    '\PhysicalDisk(*)\Current Disk Queue Length',
    '\PhysicalDisk(*)\Disk Transfers/sec',
    '\Network Interface(*)\Bytes Total/sec',
    '\Hyper-V Hypervisor Logical Processor(_Total)\% Total Run Time',
    '\Hyper-V Virtual Storage Device(*)\Latency'
)

$maxSamples = [math]::Floor($PerfDuration / $PerfInterval)
try {
    Get-Counter -Counter $counters -SampleInterval $PerfInterval -MaxSamples $maxSamples |
    Export-Counter -Path "$dir\perfmon_snapshot.csv" -FileFormat CSV
    Write-Host "  perfmon_snapshot.csv: $maxSamples samples" -ForegroundColor Green
} catch {
    Write-Host "  perfmon: ERROR - $($_.Exception.Message)" -ForegroundColor Red
}

# ── VM Status ─────────────────────────────────────────────────────────────────
Write-Host "`n[3/6] VM Status..." -ForegroundColor Yellow
try {
    Get-VM | Select Name, State, CPUUsage, MemoryAssigned, MemoryDemand, Uptime, Status, Version |
    Export-Csv -Path "$dir\vm_status.csv" -NoTypeInformation -Encoding UTF8

    Get-VM | Get-VMHardDiskDrive | Select VMName, ControllerType, ControllerNumber, ControllerLocation, Path |
    Export-Csv -Path "$dir\vm_vhd_path.csv" -NoTypeInformation -Encoding UTF8

    Get-VM | Get-VMNetworkAdapter | Select VMName, SwitchName, MacAddress, IPAddresses |
    Export-Csv -Path "$dir\vm_network.csv" -NoTypeInformation -Encoding UTF8

    $vmCount = (Get-VM).Count
    Write-Host "  vm_status/vhd_path/network: $vmCount VMs" -ForegroundColor Green
} catch {
    Write-Host "  VM: ERROR - $($_.Exception.Message)" -ForegroundColor Red
}

# ── System Info ───────────────────────────────────────────────────────────────
Write-Host "`n[4/6] System Info..." -ForegroundColor Yellow
systeminfo > "$dir\systeminfo.txt" 2>$null

Get-PhysicalDisk | Select FriendlyName, MediaType, Size, HealthStatus, OperationalStatus |
Export-Csv -Path "$dir\physical_disk.csv" -NoTypeInformation -Encoding UTF8

Get-IscsiSession -ErrorAction SilentlyContinue | Select TargetNodeAddress, IsConnected, NumberOfConnections |
Export-Csv -Path "$dir\iscsi_session.csv" -NoTypeInformation -Encoding UTF8

Get-ClusterSharedVolume -ErrorAction SilentlyContinue | Select Name, State, OwnerNode |
Export-Csv -Path "$dir\csv_volume.csv" -NoTypeInformation -Encoding UTF8

Write-Host "  systeminfo/disk/iscsi/csv: done" -ForegroundColor Green

# ── Overcommit Check ──────────────────────────────────────────────────────────
Write-Host "`n[5/6] Overcommit Check..." -ForegroundColor Yellow
$totalLogical = (Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum
$totalVCPU = (Get-VM | Where-Object State -eq 'Running' | Measure-Object -Property ProcessorCount -Sum).Sum
$totalRAM = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
$totalVMRAM = (Get-VM | Where-Object State -eq 'Running' | Measure-Object -Property MemoryAssigned -Sum).Sum

$overcommit = [PSCustomObject]@{
    PhysicalCores = $totalLogical
    TotalVCPU = $totalVCPU
    CPURatio = "$([math]::Round($totalVCPU/$totalLogical,1)):1"
    PhysicalRAM_GB = [math]::Round($totalRAM/1GB,0)
    VMAssigned_GB = [math]::Round($totalVMRAM/1GB,0)
    MemoryRatio = "$([math]::Round($totalVMRAM/$totalRAM*100,0))%"
}
$overcommit | Export-Csv -Path "$dir\overcommit.csv" -NoTypeInformation -Encoding UTF8
Write-Host "  CPU: $($overcommit.CPURatio), Memory: $($overcommit.MemoryRatio)" -ForegroundColor Green

# ── Summary ───────────────────────────────────────────────────────────────────
Write-Host "`n[6/6] Summary..." -ForegroundColor Yellow
$files = Get-ChildItem $dir | Select Name, @{N='KB';E={[math]::Round($_.Length/1KB,0)}}
$files | Format-Table -AutoSize
$totalSize = [math]::Round((Get-ChildItem $dir | Measure-Object -Property Length -Sum).Sum / 1MB, 1)

Write-Host "=== Collection Complete ===" -ForegroundColor Cyan
Write-Host "Directory: $dir" -ForegroundColor Cyan
Write-Host "Total Size: ${totalSize} MB" -ForegroundColor Cyan
Write-Host "Files: $($files.Count)" -ForegroundColor Cyan

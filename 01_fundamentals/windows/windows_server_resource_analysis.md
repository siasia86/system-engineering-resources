# Windows Server 2022 서버 리소스 분석

Windows Server 2022 (Hyper-V 호스트 포함) 환경에서 CPU, Memory, Disk I/O, Network 리소스를 분석하는 방법을 정리합니다.

## 목차

| 섹션                                                                                                                        |
|-----------------------------------------------------------------------------------------------------------------------------|
| [1. 분석 도구 개요](#1-분석-도구-개요) / [2. CPU 분석](#2-cpu-분석) / [3. Memory 분석](#3-memory-분석)                      |
| [4. Disk I/O 분석](#4-disk-io-분석) / [5. Network 분석](#5-network-분석) / [6. Hyper-V 호스트 분석](#6-hyper-v-호스트-분석) |
| [7. Event Log 기반 분석](#7-event-log-기반-분석) / [8. 종합 분석 스크립트](#8-종합-분석-스크립트)                           |
| [9. 장애 사후 로그 수집](#9-장애-사후-로그-수집) / [10. 참고 자료](#10-참고-자료)                                           |

---

## 1. 분석 도구 개요

| 도구                | 용도                     | 접근 방법      | 특징               |
|---------------------|--------------------------|----------------|--------------------|
| Performance Monitor | GUI 카운터 수집/그래프   | `perfmon.msc`  | 실시간 + 기록      |
| Get-Counter         | PowerShell 카운터 조회   | cmdlet         | 스크립트 자동화    |
| Resource Monitor    | 실시간 프로세스별 리소스 | `resmon.exe`   | 프로세스 단위 상세 |
| typeperf            | CLI 카운터 수집 (CSV)    | `typeperf.exe` | 경량 수집          |
| logman              | 데이터 수집기 관리       | `logman.exe`   | 장기 수집 설정     |
| Event Log           | 이벤트 기반 분석         | `Get-WinEvent` | 장애 사후 분석     |
| Task Manager        | 즉시 확인                | `taskmgr.exe`  | 간단 확인용        |

### 도구 선택 기준

| 상황                        | 권장 도구                      |
|-----------------------------|--------------------------------|
| 즉시 현재 상태 확인         | Task Manager, Resource Monitor |
| 특정 카운터 실시간 모니터링 | Get-Counter                    |
| 장기 수집 (수 시간~수 일)   | logman + perfmon               |
| 장애 사후 분석              | Event Log (Get-WinEvent)       |
| CSV 추출 후 외부 분석       | Get-Counter + Export-Csv       |
| VM별 리소스 확인            | Hyper-V 전용 카운터            |

[⬆ 목차로 돌아가기](#목차)

---

## 2. CPU 분석

### 주요 카운터

| 카운터                                 | 설명            | 정상        | 경고   | 위험         |
|----------------------------------------|-----------------|-------------|--------|--------------|
| `\Processor(_Total)\% Processor Time`  | 전체 CPU 사용률 | < 60%       | 60~80% | > 80%        |
| `\Processor(_Total)\% Privileged Time` | 커널 모드 CPU   | < 30%       | 30~50% | > 50%        |
| `\System\Processor Queue Length`       | CPU 대기 큐     | < 2×코어 수 | —      | > 2×코어 수  |
| `\System\Context Switches/sec`         | 컨텍스트 스위치 | < 5000/core | —      | > 15000/core |

### Hyper-V 호스트 CPU

| 카운터                                                                | 설명              | 정상  | 위험  |
|-----------------------------------------------------------------------|-------------------|-------|-------|
| `\Hyper-V Hypervisor Logical Processor(_Total)\% Total Run Time`      | 하이퍼바이저 전체 | < 70% | > 90% |
| `\Hyper-V Hypervisor Virtual Processor(*)\% Total Run Time`           | VM별 vCPU         | < 80% | > 95% |
| `\Hyper-V Hypervisor Root Virtual Processor(_Total)\% Total Run Time` | 호스트 자체       | < 30% | > 50% |

### 분석 명령어

```powershell
# 실시간 CPU 모니터링 (2초 간격)
Get-Counter '\Processor(_Total)\% Processor Time' -Continuous -SampleInterval 2

# CPU + Queue + Context Switch 종합
Get-Counter @(
    '\Processor(_Total)\% Processor Time',
    '\Processor(_Total)\% Privileged Time',
    '\System\Processor Queue Length',
    '\System\Context Switches/sec'
) -SampleInterval 5 -MaxSamples 12

# 코어별 사용률 (불균형 확인)
Get-Counter '\Processor(*)\% Processor Time' -SampleInterval 2 -MaxSamples 3 |
Select-Object -ExpandProperty CounterSamples |
Where-Object {$_.InstanceName -ne '_total'} |
Sort-Object CookedValue -Descending |
Format-Table InstanceName, @{N='%CPU';E={[math]::Round($_.CookedValue,1)}} -AutoSize

# 프로세스별 CPU (상위 10)
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, Id
```

### 판단 기준

| 증상                               | 원인 추정              | 확인 방법                  |
|------------------------------------|------------------------|----------------------------|
| % Processor Time 높음 + Queue 낮음 | 정상 부하              | 프로세스별 CPU 확인        |
| % Processor Time 높음 + Queue 높음 | CPU 병목               | vCPU 수 부족 또는 스케줄링 |
| % Privileged Time 높음             | 드라이버/커널 이슈     | I/O 또는 네트워크 과부하   |
| 특정 코어만 높음                   | 프로세스 affinity 문제 | NUMA 밸런싱 확인           |

[⬆ 목차로 돌아가기](#목차)

---

## 3. Memory 분석

### 주요 카운터

| 카운터                             | 설명               | 정상     | 경고      | 위험      |
|------------------------------------|--------------------|----------|-----------|-----------|
| `\Memory\Available MBytes`         | 사용 가능 메모리   | > 2GB    | 1~2GB     | < 1GB     |
| `\Memory\% Committed Bytes In Use` | 커밋 사용률        | < 80%    | 80~90%    | > 90%     |
| `\Memory\Pages/sec`                | 페이지 폴트        | < 500    | 500~1000  | > 1000    |
| `\Memory\Pool Nonpaged Bytes`      | 비페이징 풀        | 안정     | 증가 추세 | leak 의심 |
| `\Memory\Cache Bytes`              | 파일 캐시          | 모니터링 | —         | —         |
| `\Paging File(*)\% Usage`          | 페이지 파일 사용률 | < 25%    | 25~50%    | > 50%     |

### Hyper-V 메모리

| 카운터                                              | 설명               | 용도            |
|-----------------------------------------------------|--------------------|-----------------|
| `\Hyper-V Dynamic Memory Balancer\Available Memory` | 호스트 가용 메모리 | overcommit 확인 |
| `\Hyper-V Dynamic Memory VM(*)\Physical Memory`     | VM별 실제 할당     | VM 메모리 분배  |

### 분석 명령어

```powershell
# 메모리 상태 종합
Get-Counter @(
    '\Memory\Available MBytes',
    '\Memory\% Committed Bytes In Use',
    '\Memory\Pages/sec',
    '\Paging File(_Total)\% Usage'
) -SampleInterval 5 -MaxSamples 12

# 프로세스별 메모리 (상위 10)
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 10 Name,
    @{N='MB';E={[math]::Round($_.WorkingSet64/1MB,0)}}, Id

# VM별 메모리 할당
Get-VM | Select Name,
    @{N='Assigned_GB';E={[math]::Round($_.MemoryAssigned/1GB,1)}},
    @{N='Demand_GB';E={[math]::Round($_.MemoryDemand/1GB,1)}},
    MemoryStatus | Format-Table -AutoSize

# 비페이징 풀 추이 (leak 감지)
Get-Counter '\Memory\Pool Nonpaged Bytes' -SampleInterval 60 -MaxSamples 60
```

### 판단 기준

| 증상                             | 원인 추정              | 대응                            |
|----------------------------------|------------------------|---------------------------------|
| Available < 1GB + Pages/sec 높음 | 메모리 부족, 스왑 발생 | VM 메모리 축소 또는 호스트 증설 |
| Committed > 90%                  | 전체 메모리 overcommit | VM 메모리 합계 확인             |
| Pool Nonpaged 증가 추세          | 드라이버 메모리 leak   | 재부팅 또는 드라이버 업데이트   |
| Paging File > 50%                | 물리 메모리 부족       | 호스트 RAM 증설                 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. Disk I/O 분석

### 주요 카운터

| 카운터                                       | 설명          | 정상     | 경고    | 위험             |
|----------------------------------------------|---------------|----------|---------|------------------|
| `\PhysicalDisk(*)\Avg. Disk sec/Read`        | 읽기 latency  | < 10ms   | 10~20ms | > 20ms           |
| `\PhysicalDisk(*)\Avg. Disk sec/Write`       | 쓰기 latency  | < 10ms   | 10~20ms | > 20ms           |
| `\PhysicalDisk(*)\Current Disk Queue Length` | 큐 깊이       | < 2      | 2~10    | > 10             |
| `\PhysicalDisk(*)\Disk Transfers/sec`        | IOPS          | 모니터링 | —       | 디스크 한계 도달 |
| `\PhysicalDisk(*)\Disk Bytes/sec`            | 처리량 (MB/s) | 모니터링 | —       | 대역폭 포화      |

### CSV 클러스터 카운터

| 카운터                                                  | 설명             | 정상       | 위험                     |
|---------------------------------------------------------|------------------|------------|--------------------------|
| `\Cluster CSV File System(*)\IO Read Latency`           | CSV 읽기 latency | < 10ms     | > 25ms                   |
| `\Cluster CSV File System(*)\IO Write Latency`          | CSV 쓰기 latency | < 10ms     | > 25ms                   |
| `\Cluster CSV File System(*)\Redirected Read Bytes/sec` | 리디렉션 읽기    | 0에 가까움 | 높으면 CSV 소유자 불일치 |

### VM별 I/O (noisy neighbor 식별)

| 카운터                                               | 설명             |
|------------------------------------------------------|------------------|
| `\Hyper-V Virtual Storage Device(*)\Read Bytes/sec`  | VM별 읽기 처리량 |
| `\Hyper-V Virtual Storage Device(*)\Write Bytes/sec` | VM별 쓰기 처리량 |
| `\Hyper-V Virtual Storage Device(*)\Latency`         | VM별 I/O latency |
| `\Hyper-V Virtual Storage Device(*)\Queue Length`    | VM별 큐 깊이     |

### 분석 명령어

```powershell
# 물리 디스크 latency + 큐
Get-Counter @(
    '\PhysicalDisk(*)\Avg. Disk sec/Read',
    '\PhysicalDisk(*)\Avg. Disk sec/Write',
    '\PhysicalDisk(*)\Current Disk Queue Length',
    '\PhysicalDisk(*)\Disk Transfers/sec'
) -SampleInterval 5 -MaxSamples 12

# VM별 I/O latency (noisy neighbor 확인)
Get-Counter '\Hyper-V Virtual Storage Device(*)\Latency' -SampleInterval 5 -MaxSamples 6 |
Select-Object -ExpandProperty CounterSamples |
Where-Object {$_.CookedValue -gt 0.01} |
Sort-Object CookedValue -Descending |
Select-Object InstanceName, @{N='Latency_ms';E={[math]::Round($_.CookedValue*1000,1)}} |
Format-Table -AutoSize

# VM별 I/O 처리량 (어떤 VM이 I/O를 많이 쓰는지)
Get-Counter @(
    '\Hyper-V Virtual Storage Device(*)\Read Bytes/sec',
    '\Hyper-V Virtual Storage Device(*)\Write Bytes/sec'
) -SampleInterval 5 -MaxSamples 3 |
Select-Object -ExpandProperty CounterSamples |
Where-Object {$_.CookedValue -gt 1MB} |
Sort-Object CookedValue -Descending |
Select-Object InstanceName, @{N='MB/s';E={[math]::Round($_.CookedValue/1MB,1)}} |
Format-Table -AutoSize
```

### 판단 기준

| 증상                      | 원인 추정                         | 대응                         |
|---------------------------|-----------------------------------|------------------------------|
| Latency 높음 + Queue 높음 | 디스크 포화                       | VHD 분리 또는 Storage QoS    |
| 특정 VM만 latency 높음    | noisy neighbor                    | 해당 VM I/O 제한             |
| CSV Redirected 높음       | CSV 소유자 노드가 아닌 곳에서 I/O | VM 이동 또는 CSV 소유자 변경 |
| IOPS 높은데 latency 낮음  | 정상 부하 (디스크 여유 있음)      | 모니터링 유지                |

[⬆ 목차로 돌아가기](#목차)

---

## 5. Network 분석

### 주요 카운터

| 카운터                                          | 설명      | 정상           | 위험          |
|-------------------------------------------------|-----------|----------------|---------------|
| `\Network Interface(*)\Bytes Total/sec`         | 총 대역폭 | < 70% NIC 속도 | > 80%         |
| `\Network Interface(*)\Output Queue Length`     | 송신 큐   | 0~2            | > 2 (지속)    |
| `\Network Interface(*)\Packets Outbound Errors` | 송신 에러 | 0              | > 0 증가 추세 |
| `\Network Interface(*)\Packets Received Errors` | 수신 에러 | 0              | > 0 증가 추세 |

### Hyper-V 네트워크

| 카운터                                                         | 설명           |
|----------------------------------------------------------------|----------------|
| `\Hyper-V Virtual Switch(*)\Bytes/sec`                         | vSwitch 처리량 |
| `\Hyper-V Virtual Network Adapter(*)\Bytes/sec`                | VM별 네트워크  |
| `\Hyper-V Virtual Network Adapter(*)\Dropped Packets Incoming` | VM 수신 드롭   |
| `\Hyper-V Virtual Network Adapter(*)\Dropped Packets Outgoing` | VM 송신 드롭   |

### 분석 명령어

```powershell
# NIC 대역폭 사용률
Get-Counter '\Network Interface(*)\Bytes Total/sec' -SampleInterval 5 -MaxSamples 6 |
Select-Object -ExpandProperty CounterSamples |
Where-Object {$_.CookedValue -gt 1MB} |
Select-Object InstanceName, @{N='MB/s';E={[math]::Round($_.CookedValue/1MB,1)}} |
Format-Table -AutoSize

# NIC 에러/드롭
Get-Counter @(
    '\Network Interface(*)\Packets Outbound Errors',
    '\Network Interface(*)\Packets Received Errors'
) -SampleInterval 10 -MaxSamples 6

# iSCSI 세션 상태 (스토리지 네트워크)
Get-IscsiSession | Select TargetNodeAddress, IsConnected, NumberOfConnections | Format-Table -AutoSize

# VM별 네트워크 사용량
Get-Counter '\Hyper-V Virtual Network Adapter(*)\Bytes/sec' -SampleInterval 5 -MaxSamples 3 |
Select-Object -ExpandProperty CounterSamples |
Where-Object {$_.CookedValue -gt 100KB} |
Sort-Object CookedValue -Descending |
Select-Object InstanceName, @{N='KB/s';E={[math]::Round($_.CookedValue/1KB,0)}} |
Format-Table -AutoSize
```

### 판단 기준

| 증상                       | 원인 추정              | 대응                      |
|----------------------------|------------------------|---------------------------|
| Bytes Total > 80% NIC 속도 | 대역폭 포화            | NIC 본딩 또는 트래픽 분리 |
| Output Queue > 2 (지속)    | 송신 병목              | NIC 속도 업그레이드       |
| Errors 증가                | 케이블/스위치/드라이버 | 물리 계층 점검            |
| iSCSI Disconnected         | 스토리지 네트워크 단절 | iSCSI NIC/스위치 확인     |

[⬆ 목차로 돌아가기](#목차)

---

## 6. Hyper-V 호스트 분석

### VM 리소스 종합 확인

```powershell
# VM별 상태 + 리소스 요약
Get-VM | Select Name, State,
    @{N='CPU(%)';E={$_.CPUUsage}},
    @{N='RAM_GB';E={[math]::Round($_.MemoryAssigned/1GB,1)}},
    @{N='Uptime';E={$_.Uptime.ToString('d\.hh\:mm')}} |
Sort-Object 'CPU(%)' -Descending | Format-Table -AutoSize
```

### Overcommit 확인

```powershell
# vCPU overcommit
$totalLogical = (Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum
$totalVCPU = (Get-VM | Where State -eq 'Running' | Measure-Object -Property ProcessorCount -Sum).Sum
Write-Host "Physical Cores: $totalLogical, Total vCPU: $totalVCPU, Ratio: $([math]::Round($totalVCPU/$totalLogical,1)):1"

# Memory overcommit
$totalRAM = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
$totalVMRAM = (Get-VM | Where State -eq 'Running' | Measure-Object -Property MemoryAssigned -Sum).Sum
Write-Host "Physical RAM: $([math]::Round($totalRAM/1GB,0))GB, VM Assigned: $([math]::Round($totalVMRAM/1GB,0))GB"
```

### NUMA 밸런싱 확인

```powershell
# NUMA 노드별 메모리
Get-Counter '\Hyper-V VM Vid Partition(*)\Preferred NUMA Node Index' -SampleInterval 2 -MaxSamples 1

# VM별 NUMA 할당
Get-VM | Get-VMProcessor | Select VMName, MaximumCountPerNumaNode, MaximumCountPerNumaSocket
```

### VHD 배치 확인

```powershell
# VM별 VHD 경로 (같은 볼륨 집중 여부)
Get-VM | Get-VMHardDiskDrive | Select VMName, ControllerType, Path |
Sort-Object Path | Format-Table -AutoSize

# 볼륨별 VHD 수 (집중도)
Get-VM | Get-VMHardDiskDrive | Group-Object {Split-Path $_.Path} |
Select Name, Count | Sort-Object Count -Descending | Format-Table -AutoSize
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Event Log 기반 분석

### 채널별 확인 대상

| 채널                         | 확인 목적             | 핵심 Event ID      |
|------------------------------|-----------------------|--------------------|
| System                       | 디스크 에러, NIC 장애 | 7, 11, 15, 51, 153 |
| Hyper-V-StorageVSP-Admin     | VM I/O latency 경고   | 9                  |
| Storage-Storport/Operational | 물리 디스크 에러      | 505, 524, 534, 549 |
| Hyper-V-Worker-Admin         | VM 상태 이상          | 3086, 18500        |
| Hyper-V-VMMS-Operational     | VM 관리 작업          | —                  |

### 분석 명령어

```powershell
# 최근 24시간 Warning/Error (System)
Get-WinEvent -FilterHashtable @{
    LogName='System'
    Level=@(1,2,3)
    StartTime=(Get-Date).AddHours(-24)
} | Group-Object ProviderName |
Select Count, Name | Sort-Object Count -Descending | Format-Table -AutoSize

# StorageVSP — VM I/O latency 경고
Get-WinEvent -LogName 'Microsoft-Windows-Hyper-V-StorageVSP-Admin' -MaxEvents 20 2>$null |
Select TimeCreated, LevelDisplayName, Message | Format-List

# Storport — 물리 디스크 에러
Get-WinEvent -FilterHashtable @{
    LogName='Microsoft-Windows-Storage-Storport/Operational'
    Level=@(1,2,3)
} -MaxEvents 20 2>$null | Select TimeCreated, Id, Message | Format-List

# 디스크 관련 System 이벤트
Get-WinEvent -FilterHashtable @{
    LogName='System'
    ProviderName=@('disk','Ntfs','volmgr','iScsiPrt','storvsc')
    StartTime=(Get-Date).AddDays(-7)
} 2>$null | Select TimeCreated, ProviderName, Id, LevelDisplayName, Message |
Format-Table -AutoSize
```

### Event ID 해석

| Event ID | Provider   | 의미                                  |
|----------|------------|---------------------------------------|
| 7        | disk       | 불량 블록 감지                        |
| 11       | disk       | 디바이스 에러 (컨트롤러 리셋)         |
| 15       | disk       | 디바이스 준비 안 됨                   |
| 51       | disk       | 페이징 에러                           |
| 153      | disk       | 디스크가 요청에 늦게 응답             |
| 9        | StorageVSP | VM VHD I/O latency 초과 (밀리초 표시) |
| 549      | Storport   | SCSI 에러 (sense code 포함)           |
| 505      | Storport   | 디바이스 열거                         |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 종합 분석 스크립트

### 현재 상태 즉시 확인 (1회)

```powershell
# 서버 상태 한 눈에 확인
Write-Host "=== CPU ===" -ForegroundColor Cyan
(Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 1 -MaxSamples 3).CounterSamples |
Select-Object @{N='CPU%';E={[math]::Round($_.CookedValue,1)}}

Write-Host "`n=== Memory ===" -ForegroundColor Cyan
$os = Get-CimInstance Win32_OperatingSystem
Write-Host "Total: $([math]::Round($os.TotalVisibleMemorySize/1MB,0))GB, Available: $([math]::Round($os.FreePhysicalMemory/1MB,1))GB"

Write-Host "`n=== Disk Latency ===" -ForegroundColor Cyan
(Get-Counter @('\PhysicalDisk(*)\Avg. Disk sec/Read','\PhysicalDisk(*)\Avg. Disk sec/Write') -SampleInterval 2 -MaxSamples 1).CounterSamples |
Where-Object {$_.InstanceName -ne '_total' -and $_.CookedValue -gt 0} |
Select-Object InstanceName, @{N='ms';E={[math]::Round($_.CookedValue*1000,2)}} |
Format-Table -AutoSize

Write-Host "`n=== VM Status ===" -ForegroundColor Cyan
Get-VM | Where State -eq 'Running' | Select Name, CPUUsage,
    @{N='RAM_GB';E={[math]::Round($_.MemoryAssigned/1GB,1)}} |
Sort-Object CPUUsage -Descending | Format-Table -AutoSize
```

### 5분 수집 → CSV 추출

```powershell
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

$path = "C:\temp\perfmon_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
Get-Counter -Counter $counters -SampleInterval 10 -MaxSamples 30 |
Export-Counter -Path $path -FileFormat CSV
Write-Host "Saved: $path"
```

### 장기 수집 설정 (logman)

```powershell
# 데이터 수집기 생성 (15초 간격, 최대 1GB)
logman create counter "ServerPerf" `
    -c "\Processor(_Total)\% Processor Time" `
       "\Memory\Available MBytes" `
       "\PhysicalDisk(*)\Avg. Disk sec/Read" `
       "\PhysicalDisk(*)\Avg. Disk sec/Write" `
       "\PhysicalDisk(*)\Current Disk Queue Length" `
    -si 15 -f csv -max 1024 -o "C:\PerfLogs\ServerPerf"

# 시작
logman start "ServerPerf"

# 중지
logman stop "ServerPerf"

# 삭제
logman delete "ServerPerf"
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 장애 사후 로그 수집

장애 발생 후 원인 분석을 위해 `C:\temp\`에 각종 로그를 수집하는 절차입니다. 시간이 지나면 이벤트 로그가 순환(overwrite)되므로 **장애 인지 즉시** 수집합니다.

### 수집 디렉토리 생성

```powershell
$dir = "C:\temp\incident_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $dir -Force
```

### Event Log 수집

```powershell
# System (disk, ntfs, storvsc 등)
Get-WinEvent -FilterHashtable @{
    LogName='System'
    StartTime=(Get-Date).AddDays(-7)
} | Select-Object TimeCreated, ProviderName, Id, LevelDisplayName, Message |
Export-Csv -Path "$dir\event_system.csv" -NoTypeInformation -Encoding UTF8

# Application (VSS, 앱 에러)
Get-WinEvent -FilterHashtable @{
    LogName='Application'
    StartTime=(Get-Date).AddDays(-7)
} 2>$null | Select-Object TimeCreated, ProviderName, Id, LevelDisplayName, Message |
Export-Csv -Path "$dir\event_application.csv" -NoTypeInformation -Encoding UTF8

# Hyper-V StorageVSP (VM I/O latency)
Get-WinEvent -LogName 'Microsoft-Windows-Hyper-V-StorageVSP-Admin' 2>$null |
Select-Object TimeCreated, Id, LevelDisplayName, Message |
Export-Csv -Path "$dir\event_StorageVSP.csv" -NoTypeInformation -Encoding UTF8

# Hyper-V Worker (VM 상태)
Get-WinEvent -LogName 'Microsoft-Windows-Hyper-V-Worker-Admin' 2>$null |
Select-Object TimeCreated, Id, LevelDisplayName, Message |
Export-Csv -Path "$dir\event_HyperV_Worker.csv" -NoTypeInformation -Encoding UTF8

# Hyper-V VMMS (VM 관리)
Get-WinEvent -LogName 'Microsoft-Windows-Hyper-V-VMMS-Operational' 2>$null |
Select-Object TimeCreated, Id, LevelDisplayName, Message |
Export-Csv -Path "$dir\event_HyperV_VMMS.csv" -NoTypeInformation -Encoding UTF8

# Storport (물리 디스크)
Get-WinEvent -LogName 'Microsoft-Windows-Storage-Storport/Operational' 2>$null |
Select-Object TimeCreated, Id, LevelDisplayName, Message |
Export-Csv -Path "$dir\event_Storport.csv" -NoTypeInformation -Encoding UTF8
```

### 성능 카운터 스냅샷

```powershell
# 현재 시점 주요 카운터 (10초 간격, 30회 = 5분)
$counters = @(
    '\Processor(_Total)\% Processor Time',
    '\Memory\Available MBytes',
    '\PhysicalDisk(*)\Avg. Disk sec/Read',
    '\PhysicalDisk(*)\Avg. Disk sec/Write',
    '\PhysicalDisk(*)\Current Disk Queue Length',
    '\Hyper-V Virtual Storage Device(*)\Latency'
)

Get-Counter -Counter $counters -SampleInterval 10 -MaxSamples 30 |
Export-Counter -Path "$dir\perfmon_snapshot.csv" -FileFormat CSV
```

### VM 상태 수집

```powershell
# VM 목록 + 상태
Get-VM | Select Name, State, CPUUsage, MemoryAssigned, Uptime, Status |
Export-Csv -Path "$dir\vm_status.csv" -NoTypeInformation -Encoding UTF8

# VM별 VHD 배치
Get-VM | Get-VMHardDiskDrive | Select VMName, ControllerType, ControllerNumber, ControllerLocation, Path |
Export-Csv -Path "$dir\vm_vhd_path.csv" -NoTypeInformation -Encoding UTF8

# VM별 네트워크
Get-VM | Get-VMNetworkAdapter | Select VMName, SwitchName, MacAddress, IPAddresses |
Export-Csv -Path "$dir\vm_network.csv" -NoTypeInformation -Encoding UTF8
```

### 시스템 정보 수집

```powershell
# OS/하드웨어 정보
systeminfo > "$dir\systeminfo.txt"

# 디스크 정보
Get-PhysicalDisk | Select FriendlyName, MediaType, Size, HealthStatus, OperationalStatus |
Export-Csv -Path "$dir\physical_disk.csv" -NoTypeInformation -Encoding UTF8

# iSCSI 세션 (있는 경우)
Get-IscsiSession 2>$null | Select TargetNodeAddress, IsConnected, NumberOfConnections |
Export-Csv -Path "$dir\iscsi_session.csv" -NoTypeInformation -Encoding UTF8

# 클러스터 볼륨 (CSV)
Get-ClusterSharedVolume 2>$null | Select Name, State, OwnerNode |
Export-Csv -Path "$dir\csv_volume.csv" -NoTypeInformation -Encoding UTF8
```

### 일괄 수집 스크립트

위 내용을 하나의 스크립트로 저장하여 장애 시 즉시 실행합니다.

```powershell
# 스크립트 위치: 96_scripts/windows/collect_incident_logs.ps1
# Python 버전: 96_scripts/windows/collect_incident_logs.py
# 호스트에 복사 후 실행: C:\scripts\collect_incident_logs.ps1
# 실행: .\collect_incident_logs.ps1
# 결과: C:\temp\incident_YYYYMMDD_HHMMSS\ 디렉토리에 전체 수집
```

### 수집 파일 목록

| 파일                    | 내용                     | 분석 목적               |
|-------------------------|--------------------------|-------------------------|
| event_system.csv        | System 이벤트 (7일)      | disk/ntfs 에러          |
| event_application.csv   | Application 이벤트 (7일) | VSS/앱 에러             |
| event_StorageVSP.csv    | VM I/O latency 경고      | noisy neighbor/I/O 포화 |
| event_HyperV_Worker.csv | VM 상태 변경             | VM 장애 시점            |
| event_HyperV_VMMS.csv   | VM 관리 작업             | 스냅샷/백업 트리거      |
| event_Storport.csv      | 물리 디스크 에러         | 디스크 고장             |
| perfmon_snapshot.csv    | 성능 카운터 (5분)        | 현재 부하 상태          |
| vm_status.csv           | VM 목록/상태             | 영향 범위 파악          |
| vm_vhd_path.csv         | VHD 경로                 | 볼륨 집중도 확인        |
| vm_network.csv          | VM 네트워크              | IP/MAC 확인             |
| physical_disk.csv       | 물리 디스크 상태         | 디스크 건강 상태        |
| systeminfo.txt          | OS/하드웨어 요약         | 환경 파악               |

🟡 수집 후 `C:\temp\incident_*` 디렉토리를 분석 서버로 복사하여 외부 분석을 진행합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 참고 자료

- Windows Server Performance Tuning: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/administration/performance-tuning/) — ★★★☆☆
- Get-Counter Reference: [learn.microsoft.com](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-counter) — ★★★☆☆
- Storage QoS Overview: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/storage/storage-qos/storage-qos-overview) — ★★★☆☆
- Sysinternals Suite: [learn.microsoft.com](https://learn.microsoft.com/en-us/sysinternals/) — ★★★★☆
- [_reference/windows_server_2022_monitoring_notes.md](../../_reference/windows_server_2022_monitoring_notes.md)

[⬆ 목차로 돌아가기](#목차)

---

**작성일**: 2026-07-23

**마지막 업데이트**: 2026-07-23

© 2026 siasia86. Licensed under CC BY 4.0.

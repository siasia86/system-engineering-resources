---
name: windows-server-2022-monitoring-notes
description: Windows Server 2022 서버 리소스 모니터링 공식 카운터, 명령어, 임계치 정리.
tags:
  - windows-server
  - monitoring
  - performance
  - hyper-v
  - storage
last_checked: 2026-07-23
sources:
  - https://learn.microsoft.com/en-us/windows-server/administration/performance-tuning/
  - https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-counter
  - https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/manage/live-migration-overview
  - https://learn.microsoft.com/en-us/windows-server/storage/storage-qos/storage-qos-overview
  - https://learn.microsoft.com/en-us/sysinternals/
---

# Windows Server 2022 리소스 모니터링 참조 노트

## 1. 분석 도구

| 도구                | 용도                        | 접근 방법            |
|---------------------|-----------------------------|----------------------|
| Performance Monitor | GUI 카운터 수집/그래프      | `perfmon.msc`        |
| Get-Counter         | PowerShell 카운터 조회      | `Get-Counter` cmdlet |
| Resource Monitor    | 실시간 프로세스별 I/O       | `resmon.exe`         |
| typeperf            | CLI 카운터 수집 (CSV)       | `typeperf.exe`       |
| logman              | 데이터 수집기 관리          | `logman.exe`         |
| Event Log           | 이벤트 기반 분석            | `Get-WinEvent`       |
| Sysinternals        | Process Monitor, DiskMon 등 | download             |

## 2. CPU 카운터

### 공식 소스

- https://learn.microsoft.com/en-us/windows-server/administration/performance-tuning/role/hyper-v-server/configuration

### 주요 카운터

| 카운터                                                           | 설명             | 정상        | 경고   | 위험         |
|------------------------------------------------------------------|------------------|-------------|--------|--------------|
| `\Processor(_Total)\% Processor Time`                            | 전체 CPU 사용률  | < 60%       | 60~80% | > 80%        |
| `\Processor(_Total)\% Privileged Time`                           | 커널 모드 CPU    | < 30%       | 30~50% | > 50%        |
| `\System\Processor Queue Length`                                 | CPU 대기 큐      | < 2×코어 수 | —      | > 2×코어 수  |
| `\System\Context Switches/sec`                                   | 컨텍스트 스위치  | < 5000/core | —      | > 15000/core |
| `\Hyper-V Hypervisor Logical Processor(_Total)\% Total Run Time` | 하이퍼바이저 CPU | < 70%       | 70~90% | > 90%        |
| `\Hyper-V Hypervisor Virtual Processor(*)\% Total Run Time`      | VM별 vCPU        | < 80%       | 80~95% | > 95%        |

### 명령어

```powershell
# 실시간 CPU
Get-Counter '\Processor(_Total)\% Processor Time' -Continuous -SampleInterval 2

# Hyper-V 호스트 + VM CPU
Get-Counter @(
    '\Processor(_Total)\% Processor Time',
    '\Hyper-V Hypervisor Logical Processor(_Total)\% Total Run Time',
    '\System\Processor Queue Length'
) -SampleInterval 5 -MaxSamples 12
```

## 3. Memory 카운터

### 주요 카운터

| 카운터                                              | 설명                | 정상           | 경고              | 위험           |
|-----------------------------------------------------|---------------------|----------------|-------------------|----------------|
| `\Memory\Available MBytes`                          | 사용 가능 메모리    | > 2048MB       | 1024~2048MB       | < 1024MB       |
| `\Memory\% Committed Bytes In Use`                  | 커밋 사용률         | < 80%          | 80~90%            | > 90%          |
| `\Memory\Pages Input/sec`                           | 페이지 인풋         | < 10 (1hr avg) | —                 | > 10 (1hr avg) |
| `\Memory\Pool Nonpaged Bytes`                       | 비페이징 풀         | 모니터링       | 증가 추세 시 주의 | leak 의심      |
| `\Hyper-V Dynamic Memory Balancer\Available Memory` | Hyper-V 가용 메모리 | > 5% 총 RAM    | —                 | < 5%           |

### 명령어

```powershell
# 메모리 상태
Get-Counter @(
    '\Memory\Available MBytes',
    '\Memory\% Committed Bytes In Use',
    '\Memory\Pages Input/sec'
) -SampleInterval 5 -MaxSamples 12

# VM별 메모리
Get-VM | Select Name, MemoryAssigned, MemoryDemand, MemoryStatus
```

## 4. Disk I/O 카운터

### 공식 소스

- https://learn.microsoft.com/en-us/windows-server/administration/performance-tuning/subsystem/storage/


🟡 아래 Disk latency 임계치(10ms/20ms)는 MS 공식 수치가 아닌 업계 표준입니다. MS는 "workload dependent"로만 안내합니다. SSD 환경에서는 5ms 이상을 경고로 볼 수 있습니다.
### 주요 카운터

| 카운터                                         | 설명             | 정상     | 경고    | 위험             |
|------------------------------------------------|------------------|----------|---------|------------------|
| `\PhysicalDisk(*)\Avg. Disk sec/Read`          | 읽기 latency     | < 10ms   | 10~20ms | > 20ms           |
| `\PhysicalDisk(*)\Avg. Disk sec/Write`         | 쓰기 latency     | < 10ms   | 10~20ms | > 20ms           |
| `\PhysicalDisk(*)\Current Disk Queue Length`   | 큐 깊이          | < 2      | 2~10    | > 10             |
| `\PhysicalDisk(*)\Disk Transfers/sec`          | IOPS             | 모니터링 | —       | 디스크 한계 도달 |
| `\PhysicalDisk(*)\Disk Bytes/sec`              | 처리량           | 모니터링 | —       | 대역폭 포화      |
| `\Cluster CSV File System(*)\IO Read Latency`  | CSV 읽기 latency | < 10ms   | 10~25ms | > 25ms           |
| `\Cluster CSV File System(*)\IO Write Latency` | CSV 쓰기 latency | < 10ms   | 10~25ms | > 25ms           |

### Hyper-V 스토리지 카운터

| 카운터                                               | 설명             | 용도                |
|------------------------------------------------------|------------------|---------------------|
| `\Hyper-V Virtual Storage Device(*)\Read Bytes/sec`  | VM별 읽기 처리량 | VM I/O 식별         |
| `\Hyper-V Virtual Storage Device(*)\Write Bytes/sec` | VM별 쓰기 처리량 | VM I/O 식별         |
| `\Hyper-V Virtual Storage Device(*)\Latency`         | VM별 I/O latency | noisy neighbor 식별 |
| `\Hyper-V Virtual Storage Device(*)\Queue Length`    | VM별 큐          | I/O 병목 식별       |

### 명령어

```powershell
# 물리 디스크 latency
Get-Counter @(
    '\PhysicalDisk(*)\Avg. Disk sec/Read',
    '\PhysicalDisk(*)\Avg. Disk sec/Write',
    '\PhysicalDisk(*)\Current Disk Queue Length'
) -SampleInterval 5 -MaxSamples 12

# VM별 I/O (noisy neighbor 확인)
Get-Counter '\Hyper-V Virtual Storage Device(*)\Latency' -SampleInterval 5 -MaxSamples 6 |
Select-Object -ExpandProperty CounterSamples |
Where-Object {$_.CookedValue -gt 0.01} |
Sort-Object CookedValue -Descending |
Select-Object InstanceName, @{N='Latency_ms';E={[math]::Round($_.CookedValue*1000,1)}} |
Format-Table -AutoSize
```

## 5. Network 카운터

### 주요 카운터

| 카운터                                          | 설명           | 정상           | 위험          |
|-------------------------------------------------|----------------|----------------|---------------|
| `\Network Interface(*)\Bytes Total/sec`         | 총 대역폭      | < 70% NIC 속도 | > 80%         |
| `\Network Interface(*)\Output Queue Length`     | 송신 큐        | 0~2            | > 2           |
| `\Network Interface(*)\Packets Outbound Errors` | 송신 에러      | 0              | > 0 증가 추세 |
| `\Hyper-V Virtual Switch(*)\Bytes/sec`          | vSwitch 처리량 | 모니터링       | —             |
| `\Hyper-V Virtual Network Adapter(*)\Bytes/sec` | VM별 네트워크  | 모니터링       | —             |

### 명령어

```powershell
# NIC 대역폭
Get-Counter '\Network Interface(*)\Bytes Total/sec' -SampleInterval 5 -MaxSamples 6

# iSCSI 세션 상태 (스토리지 네트워크)
Get-IscsiSession | Select TargetNodeAddress, IsConnected, NumberOfConnections
```

## 6. Event Log 채널

### I/O 관련

| 채널                                           | 내용                         | 확인 목적        |
|------------------------------------------------|------------------------------|------------------|
| System                                         | disk, Ntfs, volmgr, iScsiPrt | 물리 디스크 에러 |
| Microsoft-Windows-Hyper-V-StorageVSP-Admin     | VM VHD I/O latency 경고      | noisy neighbor   |
| Microsoft-Windows-Storage-Storport/Operational | 물리 HBA/디스크 에러         | 디스크 고장      |
| Microsoft-Windows-Storage-Storport/Health      | 디스크 건강 상태             | 예방 모니터링    |

### Hyper-V 관련

| 채널                                       | 내용               | 확인 목적     |
|--------------------------------------------|--------------------|---------------|
| Microsoft-Windows-Hyper-V-Worker-Admin     | VM 상태 변경, 에러 | VM 장애       |
| Microsoft-Windows-Hyper-V-VMMS-Operational | VM 관리 작업       | 스냅샷/이동   |
| Microsoft-Windows-Hyper-V-VMMS-Storage     | 스토리지 관련 관리 | VHD 이동/확장 |

### 명령어

```powershell
# 최근 1시간 Warning/Error (System)
Get-WinEvent -FilterHashtable @{
    LogName='System'
    Level=@(1,2,3)
    StartTime=(Get-Date).AddHours(-1)
} | Select TimeCreated, ProviderName, Id, LevelDisplayName, Message |
Format-Table -AutoSize

# StorageVSP 경고 (VM I/O latency)
Get-WinEvent -LogName 'Microsoft-Windows-Hyper-V-StorageVSP-Admin' -MaxEvents 20 |
Select TimeCreated, Id, LevelDisplayName, Message | Format-List
```

## 7. 종합 수집 스크립트

```powershell
# 5분간 주요 카운터 수집 → CSV
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

Get-Counter -Counter $counters -SampleInterval 10 -MaxSamples 30 |
Export-Counter -Path "C:\temp\perfmon_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv" -FileFormat CSV
```

## 8. 임계치 종합

### MS 공식 문서 기반 (출처 명시)

| 리소스     | 카운터                       | 임계치                            | 출처                                                                          |
|------------|------------------------------|-----------------------------------|-------------------------------------------------------------------------------|
| Memory     | Pages Input/sec              | 1시간 평균 < 10                   | learn.microsoft.com/performance-tuning/role/hyper-v-server/memory-performance |
| Memory     | Standby Cache + Free/Zero    | > 200MB (1GB RAM), > 300MB (2GB+) | 동일                                                                          |
| Hyper-V    | Logical Processor % Run Time | CPU 사용률 특성화 용도            | learn.microsoft.com/performance-tuning/role/hyper-v-server/configuration      |
| Disk       | Event ID 153                 | 발생 시 = latency > 15초          | System Event Log (disk provider)                                              |
| StorageVSP | Event ID 9                   | 발생 시 = VM VHD latency 초과     | Hyper-V-StorageVSP-Admin                                                      |

### 업계 표준/베스트 프랙티스 (MS 공식 수치 아님)

🟡 아래 임계치는 Microsoft가 공식적으로 명시한 값이 아닌, Windows 성능 분석 실무에서 일반적으로 사용되는 기준입니다.

| 리소스  | 카운터                   | 정상     | 경고    | 위험     | 참고                |
|---------|--------------------------|----------|---------|----------|---------------------|
| CPU     | % Processor Time         | < 60%    | 60~80%  | > 80%    | workload dependent  |
| CPU     | Processor Queue Length   | < 2×코어 | —       | > 2×코어 | 지속 시 병목        |
| Memory  | Available MBytes         | > 2GB    | 1~2GB   | < 1GB    | 서버 규모에 따라    |
| Memory  | % Committed Bytes In Use | < 80%    | 80~90%  | > 90%    |                     |
| Disk    | Avg. Disk sec/Read       | < 10ms   | 10~20ms | > 20ms   | HDD 기준, SSD < 5ms |
| Disk    | Avg. Disk sec/Write      | < 10ms   | 10~20ms | > 20ms   | HDD 기준, SSD < 5ms |
| Disk    | Current Queue Length     | < 2      | 2~10    | > 10     | 디스크당            |
| Network | % Bandwidth              | < 70%    | 70~80%  | > 80%    |                     |
| Hyper-V | % Total Run Time         | < 70%    | 70~90%  | > 90%    |                     |


# Hyper-V 클러스터 I/O 경합과 레거시 VM 영향

Hyper-V 클러스터에서 디스크 I/O 경합 발생 시 레거시 VM(CentOS 5.x 등)이 받는 영향과 완화 방법을 정리합니다.

## 목차

| 섹션                                                                                                                          |
|-------------------------------------------------------------------------------------------------------------------------------|
| [1. 핵심 결론](#1-핵심-결론) / [2. I/O 경합 원리](#2-io-경합-원리) / [3. CentOS 5.11 취약 원인](#3-centos-511-취약-원인)      |
| [4. 증상 및 진단](#4-증상-및-진단) / [5. 완화 방법](#5-완화-방법) / [6. 모니터링](#6-모니터링) / [7. 참고 자료](#7-참고-자료) |

---

## 1. 핵심 결론

클러스터 내 다른 VM의 디스크 I/O 폭증은 CentOS 5.11 VM에 **직접적인 영향**을 줍니다.

| 상황                    | CentOS 5.11 영향                        |
|-------------------------|-----------------------------------------|
| 다른 VM I/O 폭증 (경미) | latency 증가, 응답 지연                 |
| 다른 VM I/O 폭증 (심각) | I/O timeout → 파일시스템 read-only 전환 |
| 물리 디스크 큐 포화     | 커널 panic 가능 (30초 timeout 초과 시)  |

CentOS 5.11은 다음 이유로 최신 VM보다 더 심각한 영향을 받습니다:

- IDE 에뮬레이션 사용 (큐 깊이 1, 병렬 I/O 불가)
- Hyper-V Integration Services(LIS) 미지원
- 커널 2.6.18의 구형 I/O scheduler

[⬆ 목차로 돌아가기](#목차)

---

## 2. I/O 경합 원리

### Hyper-V Storage Stack

```
VM-A (Windows)  VM-B (CentOS 5.11)  VM-C (Linux 7.x+)
      │                │                     │
      v                v                     v
  storvsc          IDE Emulation          storvsc
  (synthetic)      (queue depth=1)        (synthetic)
      │                │                     │
      v                v                     v
┌──────────────────────────────────────────────────────┐
│             Hyper-V Host Storage Stack               │
│         (NTFS / ReFS / CSV, shared queue)            │
└──────────────────────────────────────────────────────┘
      │
      v
┌──────────────────────────────────────────────────────┐
│          Physical Storage (LUN / SSD / HDD)          │
└──────────────────────────────────────────────────────┘
```

### 경합 발생 조건

| 조건                            | 설명                                      |
|---------------------------------|-------------------------------------------|
| 동일 물리 디스크에 VHD 공존     | 가장 흔한 원인                            |
| CSV(Cluster Shared Volume) 공유 | 클러스터 노드 간 I/O redirection 오버헤드 |
| Storage QoS 미설정              | VM 간 IOPS 격리 없음 (선착순 소비)        |
| Dynamic VHD 사용                | 조각화로 random I/O 증가                  |
| iSCSI/SMB 스토리지              | 네트워크 대역폭 경합 추가                 |

### I/O 격리 부재

Hyper-V는 기본적으로 VM 간 I/O 격리를 제공하지 않습니다. Storage QoS를 명시적으로 설정하지 않으면 물리 디스크의 IOPS를 선착순(FIFO)으로 소비합니다.

Microsoft 공식 문서에서도 Storage QoS의 목적을 "Mitigate noisy neighbor issues"로 명시하고 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. CentOS 5.11 취약 원인

### Hyper-V 공식 지원 상태

2026-07-16 기준, Microsoft 공식 지원 매트릭스에서 CentOS/RHEL **5.x, 6.x가 완전히 삭제**되었습니다. 현재 나열된 버전은 7.x, 8.x, 9.x, 10.x만 존재합니다.

### 기술 제약 비교

| 항목                       | CentOS 5.11             | 최신 Linux (7.x+)         |
|----------------------------|-------------------------|---------------------------|
| 커널 버전                  | 2.6.18 (2006년)         | 3.10+ / 4.x+              |
| LIS (Integration Services) | 미지원                  | Built-in (커널 내장)      |
| 디스크 드라이버            | IDE 에뮬레이션          | storvsc (VMBus synthetic) |
| 네트워크 드라이버          | 에뮬레이션 (legacy NIC) | netvsc (VMBus synthetic)  |
| I/O scheduler              | CFQ (단일 큐)           | blk-mq (멀티큐)           |
| VM Generation              | 1만 가능                | 1 또는 2                  |
| 동적 메모리                | 미지원                  | 지원                      |
| EOL                        | 2017-03-31              | 지원 중                   |

### IDE 에뮬레이션 vs Synthetic 드라이버

| 항목         | IDE 에뮬레이션              | storvsc (Synthetic) |
|--------------|-----------------------------|---------------------|
| I/O 경로     | 전체 디바이스 에뮬레이션    | VMBus 직접 통신     |
| CPU 오버헤드 | 높음 (매 I/O마다 trap 발생) | 낮음 (hypercall)    |
| 큐 깊이      | 1 (한 번에 1개 요청만 처리) | 64+ (병렬 처리)     |
| 최대 IOPS    | ~5,000                      | ~50,000+            |
| latency      | 높음                        | 낮음                |

IDE 에뮬레이션은 큐 깊이가 1이므로, 물리 디스크가 바빠지면 단일 요청의 완료를 기다리는 동안 모든 I/O가 차단됩니다. 이것이 CentOS 5.11이 I/O 경합에 특히 취약한 핵심 원인입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 증상 및 진단

### 영향 체인

```
Host I/O saturation (other VMs)
         │
         v
IDE emulation queue full (depth=1)
         │
         v
Guest kernel I/O timeout (30s default)
         │
         v
Filesystem remount read-only or kernel panic
```

### 커널 메시지 (dmesg)

I/O 경합으로 인한 CentOS 5.11 커널 메시지 예시:

```
sd 0:0:0:0: timing out command, waited 30s
end_request: I/O error, dev sda, sector XXXXX
hda: lost interrupt
Buffer I/O error on device sda1, logical block XXXXX
EXT3-fs error (device sda1): ext3_journal_start_sb: Detected aborted journal
EXT3-fs (sda1): Remounting filesystem read-only
```

### 시스템 상태 지표

| 지표                     | 정상      | I/O 경합 발생 시       |
|--------------------------|-----------|------------------------|
| load average             | < vCPU 수 | CPU idle인데 수십~수백 |
| D state 프로세스 수      | 0~2개     | 수십 개                |
| `iostat` await (ms)      | < 10      | 수백~수천              |
| `vmstat` wa (I/O wait %) | < 5%      | 50%+                   |
| dmesg I/O error          | 없음      | timeout/lost interrupt |

### 진단 명령어 (Guest)

```bash
# D state 프로세스 확인
ps aux | awk '$8 ~ /D/'

# I/O wait 확인
vmstat 2 5

# 디스크 latency 확인
iostat -x 2

# 커널 I/O 에러 확인
dmesg | grep -i "error\|timeout\|lost interrupt"

# 파일시스템 상태 확인
mount | grep "ro,"
```

### 실제 발생 사례 (2026-07-15)

Hyper-V 클러스터 내 2개 게임 서버 VM에서 **동일 시각에 동시 발생**한 사례입니다.

#### 로그 (Acheron-Game)

```
Jul 15 16:38:24 Acheron-Game kernel: sd 1:0:0:1: timing out command, waited 60s
Jul 15 16:38:25 Acheron-Game kernel: Aborting journal on device sdc1-8.
Jul 15 16:38:25 Acheron-Game kernel: EXT4-fs error (device sdc1): ext4_journal_start_sb: Detected aborted journal
Jul 15 16:38:25 Acheron-Game kernel: EXT4-fs (sdc1): Remounting filesystem read-only
```

#### 로그 (Hermes-Game)

```
Jul 15 16:38:24 Hermes-Game kernel: sd 1:0:0:1: timing out command, waited 60s
Jul 15 16:38:25 Hermes-Game kernel: Aborting journal on device sdc1-8.
Jul 15 16:38:25 Hermes-Game kernel: EXT4-fs error (device sdc1): ext4_journal_start_sb: Detected aborted journal
Jul 15 16:38:25 Hermes-Game kernel: EXT4-fs (sdc1): Remounting filesystem read-only
Jul 15 17:34:53 Hermes-Game shutdown[10807]: shutting down for system reboot
```

#### 분석

| 항목       | 값                                    |
|------------|---------------------------------------|
| 발생 시각  | 2026-07-15 16:38:24 (2 VM 동시)       |
| SCSI 주소  | `sd 1:0:0:1` (동일 컨트롤러, LUN 1)   |
| 디바이스   | `sdc1` (두 VM 모두 동일 위치)         |
| 파일시스템 | EXT4                                  |
| timeout    | 60초 (기본 30초에서 변경된 상태)      |
| 드라이버   | SCSI synthetic (storvsc) — LIS 설치됨 |
| 복구       | Hermes-Game: 약 56분 후 수동 reboot   |

#### 동시 발생이 의미하는 것

- ❌ VM 내부 문제 → 2개 VM에서 동시에 발생할 수 없음
- ✅ 호스트/스토리지 측 문제 확정:
  - 동일 CSV/LUN의 I/O 포화 (noisy neighbor)
  - 물리 디스크/컨트롤러 일시적 hang
  - CSV 소유권 이동 (node failover)
  - 스토리지 네트워크 단절 (iSCSI/SMB)

#### Host 측 확인 명령어

```powershell
# 해당 시점 스토리지 이벤트
Get-WinEvent -FilterHashtable @{LogName='System'; StartTime='2026-07-15 16:35:00'; EndTime='2026-07-15 16:45:00'} |
  Where-Object {$_.ProviderName -match 'disk|stor|csv|vhd|ntfs|iscsi'} |
  Format-Table TimeCreated, ProviderName, Id, Message -Wrap

# 두 VM의 VHD가 같은 볼륨에 있는지 확인
Get-VM "Hermes-Game","Acheron-Game" | Get-VMHardDiskDrive | Select VMName, Path

# CSV 소유자 변경 이력
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-FailoverClustering/Operational'; StartTime='2026-07-15 16:30:00'; EndTime='2026-07-15 17:00:00'} |
  Format-Table TimeCreated, Message -Wrap
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 완화 방법

| 우선순위 | 방법             | 설명                                        | 효과  | 위험도 |
|----------|------------------|---------------------------------------------|-------|--------|
| 1        | VHD 물리 분리    | CentOS VM의 VHD를 전용 물리 디스크/LUN 배치 | ★★★★★ | 낮음   |
| 2        | Storage QoS 적용 | Min IOPS 보장 정책                          | ★★★★☆ | 낮음   |
| 3        | Fixed VHD 전환   | Dynamic VHD → Fixed VHD (조각화 방지)       | ★★★☆☆ | 중간   |
| 4        | I/O timeout 증가 | 게스트 내 timeout 값 조정                   | ★★☆☆☆ | 낮음   |
| 5        | VM 이관          | I/O 부하 낮은 노드로 Live Migration         | ★★★☆☆ | 낮음   |
| 6        | OS 업그레이드    | CentOS 5 → 지원 OS (storvsc 활용)           | ★★★★★ | 높음   |

### 5.1 VHD 물리 분리

가장 효과적인 방법입니다. 물리적으로 다른 디스크에 배치하면 I/O 경합 자체가 발생하지 않습니다.

```powershell
# 현재 VHD 위치 확인
Get-VM "CentOS-5.11" | Get-VMHardDiskDrive | Select Path

# VHD를 별도 물리 디스크로 이동 (VM 중지 필요)
Move-VMStorage -VMName "CentOS-5.11" -DestinationStoragePath "D:\IsolatedVMs\CentOS511"
```

### 5.2 Storage QoS 적용

Windows Server 2016+ 환경에서 SOFS 또는 CSV 사용 시 적용 가능합니다.

#### 전제 조건

| 요구사항                 | 설명                                        |
|--------------------------|---------------------------------------------|
| Windows Server 2016 이상 | 모든 클러스터 노드 동일 버전                |
| Failover Cluster         | 필수                                        |
| 스토리지 유형            | SOFS 클러스터 또는 CSV (로컬 디스크 미지원) |
| Hyper-V 역할             | 컴퓨트 노드에 설치                          |

🟡 **로컬 디스크(C:\, D:\ 등)에 직접 배치된 VHD에는 Storage QoS가 적용되지 않습니다.** CSV 또는 SOFS 경로에 있어야 합니다.

#### 정책 유형

| 유형       | 동작                                       | 사용 시나리오     |
|------------|--------------------------------------------|-------------------|
| Dedicated  | VHD별로 개별 Min/Max IOPS 적용             | 중요 VM 개별 보호 |
| Aggregated | 정책에 할당된 모든 VHD의 합산 Min/Max 적용 | VM 그룹 단위 제한 |

#### Normalized IOPS 개념 (Microsoft 정의)

Storage QoS의 IOPS는 **Normalized IOPS** 단위입니다:

- 8KB 이하 I/O = 1 Normalized IOPS
- 8KB 초과 I/O = (크기 / 8KB) Normalized IOPS
- 예: 256KB write = 32 Normalized IOPS

```
게임 서버 (4KB random read 위주) → 실제 IOPS ≈ Normalized IOPS
백업 서버 (1MB sequential write) → 1 실제 I/O = 128 Normalized IOPS
```

#### 설정 명령어

```powershell
# 1. 게임 서버 보호 정책 (Dedicated: VHD별 개별 적용)
New-StorageQoSPolicy -Name "GameServer-Floor" -MinimumIops 500 -MaximumIops 5000 -PolicyType Dedicated

# 2. noisy neighbor 제한 정책 (백업/배치 VM용)
New-StorageQoSPolicy -Name "BatchVM-Cap" -MinimumIops 50 -MaximumIops 1000 -PolicyType Dedicated

# 3. VM에 적용
$policy = Get-StorageQoSPolicy -Name "GameServer-Floor"
Get-VM "Hermes-Game","Acheron-Game" | Get-VMHardDiskDrive | Set-VMHardDiskDrive -QoSPolicyID $policy.PolicyId

# 4. 적용 확인
Get-StorageQoSFlow | Format-Table InitiatorName, MinimumIOPS, MaximumIOPS, StorageNodeIOPS, Status
```

#### 모니터링 및 상태 확인

```powershell
# Flow 상태 확인 (Status 필드가 핵심)
Get-StorageQoSFlow | Select InitiatorName, Status, StorageNodeIOPS, Latency | Format-Table

# Volume 레벨 확인
Get-StorageQoSVolume | Format-Table MountPoint, IOPS, Latency, Status
```

#### Status 필드 의미

| Status                 | 의미                                       | 조치                         |
|------------------------|--------------------------------------------|------------------------------|
| Ok                     | 정상 동작, Min IOPS 충족                   | 없음                         |
| InsufficientThroughput | Min IOPS 할당 불가 (물리 디스크 성능 부족) | Min 값 하향 또는 디스크 증설 |
| UnknownPolicyId        | VM에 할당된 정책이 파일서버에 없음         | 정책 재생성 또는 VM에서 제거 |

🟡 `InsufficientThroughput`는 물리 디스크의 총 IOPS보다 모든 VM의 Min IOPS 합이 큰 경우 발생합니다. 이 상태에서는 QoS가 보장을 제공하지 못합니다.

#### 이 사례에 적용한다면

```powershell
# Hermes-Game, Acheron-Game이 같은 CSV에 있다면:
# 1. 게임 서버 최소 보장
New-StorageQoSPolicy -Name "GameServer-Floor" -MinimumIops 500 -MaximumIops 5000 -PolicyType Dedicated
$gp = Get-StorageQoSPolicy -Name "GameServer-Floor"
Get-VM "Hermes-Game","Acheron-Game" | Get-VMHardDiskDrive | Set-VMHardDiskDrive -QoSPolicyID $gp.PolicyId

# 2. 같은 볼륨의 I/O 과다 VM 제한
New-StorageQoSPolicy -Name "OtherVM-Cap" -MaximumIops 2000 -PolicyType Dedicated
$cp = Get-StorageQoSPolicy -Name "OtherVM-Cap"
Get-VM "Backup-VM","Batch-VM" | Get-VMHardDiskDrive | Set-VMHardDiskDrive -QoSPolicyID $cp.PolicyId
```

### 5.3 Fixed VHD 전환

Dynamic VHD는 사용량에 따라 확장되며 조각화가 발생합니다.

```powershell
# VM 중지 후 변환
Stop-VM -Name "CentOS-5.11"
Convert-VHD -Path "C:\VMs\CentOS511.vhdx" -DestinationPath "C:\VMs\CentOS511_fixed.vhdx" -VHDType Fixed
```

🟡 변환 시 디스크 최대 크기만큼 공간을 즉시 할당합니다. 여유 공간을 확인 후 진행합니다.

### 5.4 I/O timeout 증가 (게스트 내)

```bash
# 현재 timeout 확인 (기본 30초)
cat /sys/block/sda/device/timeout

# 임시 변경 (120초)
echo 120 > /sys/block/sda/device/timeout

# 영구 적용
echo 'echo 120 > /sys/block/sda/device/timeout' >> /etc/rc.local
```

🟡 timeout 증가는 근본 해결이 아닌 임시 조치입니다. I/O 대기 시간만 늘어나므로 애플리케이션 응답 지연은 여전히 발생합니다. 파일시스템 read-only 전환을 지연시키는 효과만 있습니다.

### 5.5 OS 업그레이드

CentOS 5.11 → 지원 OS로 교체하면 storvsc synthetic 드라이버를 사용할 수 있습니다.

| 교체 대상        | 커널 | storvsc | LIS Built-in |
|------------------|------|---------|--------------|
| Rocky Linux 8.x  | 4.18 | ✅      | ✅           |
| Rocky Linux 9.x  | 5.14 | ✅      | ✅           |
| AlmaLinux 8.x    | 4.18 | ✅      | ✅           |
| Ubuntu 22.04 LTS | 5.15 | ✅      | ✅           |

🟡 CentOS 5.11에서 구동 중인 애플리케이션의 호환성 검증이 선행되어야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 모니터링

### Host 측 (PowerShell)

```powershell
# VM별 디스크 I/O 현황
Get-Counter '\Hyper-V Virtual Storage Device(*)\Read Bytes/sec'
Get-Counter '\Hyper-V Virtual Storage Device(*)\Write Bytes/sec'
Get-Counter '\Hyper-V Virtual Storage Device(*)\Latency'

# Storage QoS Flow 모니터링
Get-StorageQoSFlow | Sort-Object StorageNodeIOPS -Descending | Format-Table InitiatorName, StorageNodeIOPS, Latency

# 물리 디스크 큐 깊이
Get-Counter '\PhysicalDisk(*)\Current Disk Queue Length'
Get-Counter '\PhysicalDisk(*)\Avg. Disk sec/Read'
Get-Counter '\PhysicalDisk(*)\Avg. Disk sec/Write'
```

### Guest 측 (CentOS 5.11)

```bash
# 실시간 I/O 모니터링
iostat -x 2

# I/O wait 추이 확인
vmstat 2

# 디스크 큐 깊이 (커널 2.6.18)
cat /proc/diskstats

# D state 프로세스 실시간 감시
watch -n 2 "ps aux | awk '\$8 ~ /D/'"
```

### 알람 기준 (권장)

| 지표                            | 경고 (Warning) | 위험 (Critical) |
|---------------------------------|----------------|-----------------|
| Host Physical Disk Queue Length | > 10           | > 30            |
| Host Avg. Disk sec/Read         | > 20ms         | > 100ms         |
| Guest iostat await              | > 50ms         | > 500ms         |
| Guest D state process count     | > 5            | > 20            |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 참고 자료

- Storage QoS Overview: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/storage/storage-qos/storage-qos-overview) — ★★★☆☆
- Supported CentOS/RHEL on Hyper-V: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/Supported-CentOS-and-Red-Hat-Enterprise-Linux-virtual-machines-on-Hyper-V) — ★★★☆☆
- Hyper-V VM Generation: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/plan/should-i-create-a-generation-1-or-2-virtual-machine-in-hyper-v) — ★★★☆☆
- [_reference/hyperv_io_contention_notes.md](../../_reference/hyperv_io_contention_notes.md)

---

**작성일**: 2026-07-16

**마지막 업데이트**: 2026-07-16

© 2026 siasia86. Licensed under CC BY 4.0.

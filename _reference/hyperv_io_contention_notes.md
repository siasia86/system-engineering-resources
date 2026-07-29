---
name: hyperv-io-contention-notes
description: Hyper-V 클러스터 디스크 I/O 경합이 레거시 VM(CentOS 5.x)에 미치는 영향. Storage QoS, Verified Boot, LIS 지원 범위 정리.
tags:
  - hyper-v
  - storage
  - io-contention
  - centos
  - legacy
  - cluster
last_checked: 2026-07-16
sources:
  - https://learn.microsoft.com/en-us/windows-server/storage/storage-qos/storage-qos-overview
  - https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/Supported-CentOS-and-Red-Hat-Enterprise-Linux-virtual-machines-on-Hyper-V
  - https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/plan/should-i-create-a-generation-1-or-2-virtual-machine-in-hyper-v
  - https://docs.kernel.org/admin-guide/blockdev/
---

# Hyper-V 클러스터 I/O 경합 참조 노트

## 1. Hyper-V Storage Stack 구조

### I/O 경로

모든 VM의 디스크 I/O는 다음 경로를 공유합니다.

```
Guest OS (VM)
    │
    v
Virtual IDE / Virtual SCSI (storvsc)
    │
    v
Hyper-V VMBus (paravirt) or Emulated (IDE)
    │
    v
Host Storage Stack (NTFS / ReFS / CSV)
    │
    v
Physical Storage (LUN / SSD / HDD)
```

- Generation 1 VM: IDE 컨트롤러(에뮬레이션) + SCSI 컨트롤러(synthetic)
- Generation 2 VM: SCSI만 사용 (IDE 없음)
- CentOS 5.11: Generation 1 필수, LIS 미지원 → IDE 에뮬레이션 사용

### I/O 격리 부재

- Hyper-V는 기본적으로 VM 간 I/O 격리를 제공하지 않습니다
- Storage QoS 미설정 시 물리 디스크 IOPS를 선착순(FIFO)으로 소비
- 한 VM의 I/O 폭증 → 물리 디스크 큐 포화 → 다른 VM의 I/O latency 증가

## 2. Storage QoS (공식 문서 기반)

### 배포 시나리오 (Microsoft 공식)

| 시나리오                         | 요구사항                              |
|----------------------------------|---------------------------------------|
| Hyper-V + Scale-Out File Server  | SOFS 클러스터 + Hyper-V 컴퓨트 노드   |
| Hyper-V + Cluster Shared Volumes | Failover Cluster + Hyper-V 역할 + CSV |

- Windows Server 2016 이상 필수
- 정책 속성: PolicyId, MinimumIOPS, MaximumIOPS, ParentPolicy, PolicyType

### 핵심 기능 (공식 문서 명시)

- "Mitigate noisy neighbor issues" — 단일 VM의 스토리지 리소스 독점 방지
- 자동 fairness: 기본적으로 단일 VM이 전체 스토리지를 소비하지 못하도록 함
- 정책 기반 Min/Max IOPS 설정: normalized IOPS 단위

### Normalized IOPS 정의 (공식 문서 원문)

"All of the storage usage is measured in Normalized IOPS. This is a count of the storage input/output operations per second. Any IO that is 8KB or smaller is considered as one normalized IO. Any IO that is larger than 8KB is treated as multiple normalized IOs. For example, a 256KB request is treated as 32 normalized IOPS."

- 기본 단위: 8KB (Windows Server 2016에서 변경 가능)
- 변경 명령: `Set-StorageQosPolicy` 에서 normalization size 지정 가능

### 정책 유형 (공식 문서)

| 유형       | 공식 설명                                                                                               |
|------------|---------------------------------------------------------------------------------------------------------|
| Dedicated  | "the maximum and minimum throughputs are managed for individual VHD/VHDx"                               |
| Aggregated | "the specified MinimumIOPS MaximumIOPS and Bandwidth are shared among all flows assigned to the policy" |

### Status 필드 (공식 문서)

| Status                 | 공식 설명                                                           |
|------------------------|---------------------------------------------------------------------|
| Ok                     | No issues exist                                                     |
| InsufficientThroughput | A policy is applied, but the Minimum IOPS cannot be delivered       |
| UnknownPolicyId        | A policy was assigned to the VM but is missing from the file server |

### PowerShell 명령어

```powershell
# 정책 생성 (공식 예시 기반)
New-StorageQoSPolicy -Name "Policy01" -MaximumIops 100 -MinimumIops 10

# Dedicated 정책 생성
New-StorageQoSPolicy -Name "GameServer-Floor" -MinimumIops 500 -MaximumIops 5000 -PolicyType Dedicated

# VM에 적용
$policy = Get-StorageQoSPolicy -Name "GameServer-Floor"
Get-VM "VM-Name" | Get-VMHardDiskDrive | Set-VMHardDiskDrive -QoSPolicyID $policy.PolicyId

# Flow 상태 확인
Get-StorageQoSFlow | Format-Table InitiatorName, MinimumIOPS, MaximumIOPS, StorageNodeIOPS, Status

# Volume 확인
Get-StorageQoSVolume | Format-Table MountPoint, IOPS, Latency, Status
```

## 3. CentOS 5.11 Hyper-V 지원 상태

### Microsoft 공식 문서 현황

- 2026-07-16 기준, Microsoft 공식 문서에서 CentOS/RHEL 5.x, 6.x 항목이 제거됨
- 현재 나열된 버전: **7.x, 8.x, 9.x, 10.x** 만 존재
- CentOS 5.x는 공식 지원 매트릭스에서 완전히 삭제된 상태

### CentOS 5.11 기술 제약

| 항목                       | CentOS 5.11 상태            | 최신 Linux (7.x+)   |
|----------------------------|-----------------------------|---------------------|
| 커널 버전                  | 2.6.18                      | 3.10+ / 4.x+        |
| LIS (Integration Services) | 미지원 (공식 문서에서 삭제) | Built-in            |
| 디스크 드라이버            | IDE 에뮬레이션              | storvsc (synthetic) |
| 네트워크 드라이버          | 에뮬레이션 (legacy NIC)     | netvsc (synthetic)  |
| I/O scheduler              | CFQ (단일 큐)               | blk-mq (멀티큐)     |
| Generation                 | 1만 가능                    | 1 또는 2            |
| 동적 메모리                | 미지원                      | 지원                |
| SCSI 부팅                  | 불가                        | Generation 2 가능   |

### IDE vs Synthetic 드라이버 성능 차이

| 항목         | IDE 에뮬레이션           | storvsc (Synthetic) |
|--------------|--------------------------|---------------------|
| 경로         | 전체 디바이스 에뮬레이션 | VMBus 직접 통신     |
| CPU 오버헤드 | 높음 (trap 발생)         | 낮음 (hypercall)    |
| 큐 깊이      | 1 (단일 요청)            | 64+ (병렬 처리)     |
| 최대 IOPS    | ~5,000                   | ~50,000+            |
| latency      | 높음                     | 낮음                |

## 4. I/O 경합 시 CentOS 5.11 증상

### 커널 메시지 (dmesg)

```
sd 0:0:0:0: timing out command, waited 30s
end_request: I/O error, dev sda, sector XXXXX
hda: lost interrupt
Buffer I/O error on device sda1, logical block XXXXX
EXT3-fs error (device sda1): ext3_journal_start_sb: Detected aborted journal
EXT3-fs (sda1): Remounting filesystem read-only
```

### 프로세스 상태

```
# ps aux 에서 D state 다수 발생
root    1234  0.0  0.0      0     0 ?   D    14:00   0:00 [flush-8:0]

# load average 급등 (CPU idle인데 load 높음)
top - 14:05:30 up 45 days, load average: 85.20, 42.10, 15.30
```

### 영향 체인

```
Host I/O saturation
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

## 5. 완화 방법

| 우선순위 | 방법             | 설명                                         | 효과  |
|----------|------------------|----------------------------------------------|-------|
| 1        | VHD 물리 분리    | CentOS VM의 VHD를 전용 물리 디스크/LUN 배치  | ★★★★★ |
| 2        | Storage QoS 적용 | Min IOPS 보장 정책 (SOFS/CSV 환경 필수)      | ★★★★☆ |
| 3        | Fixed VHD 사용   | Dynamic VHD → Fixed VHD (조각화 방지)        | ★★★☆☆ |
| 4        | I/O timeout 증가 | 게스트 내 `/sys/block/sda/device/timeout` 값 | ★★☆☆☆ |
| 5        | VM 이관          | I/O 부하 낮은 노드로 Live Migration          | ★★★☆☆ |
| 6        | OS 업그레이드    | CentOS 5 → 지원 OS (storvsc 사용 가능)       | ★★★★★ |

### I/O timeout 조정 (게스트 내)

```bash
# 현재 timeout 확인 (기본 30초)
cat /sys/block/sda/device/timeout

# 임시 변경 (120초)
echo 120 > /sys/block/sda/device/timeout

# 영구 적용: /etc/rc.local 에 추가
echo 'echo 120 > /sys/block/sda/device/timeout' >> /etc/rc.local
```

🟡 timeout 증가는 근본 해결이 아닌 임시 조치입니다. I/O 대기 시간만 늘어나므로 애플리케이션 응답 지연은 그대로 발생합니다.

## 6. 모니터링 명령어

### Host (PowerShell)

```powershell
# VM별 I/O 현황
Get-VM | Get-VMHardDiskDrive | Measure-VM | Select VMName, AggregatedDiskDataRead, AggregatedDiskDataWritten

# Storage QoS Flow 확인
Get-StorageQoSFlow | Format-Table InitiatorName, StorageNodeIOPS, Latency

# 성능 카운터
Get-Counter '\Hyper-V Virtual Storage Device(*)\Read Bytes/sec'
Get-Counter '\Hyper-V Virtual Storage Device(*)\Write Bytes/sec'
```

### Guest (CentOS 5.11)

```bash
# I/O 대기 확인
iostat -x 2
vmstat 2
cat /proc/diskstats

# D state 프로세스 확인
ps aux | awk '$8 ~ /D/'

# dmesg I/O 에러 확인
dmesg | grep -i "error\|timeout\|lost interrupt"
```

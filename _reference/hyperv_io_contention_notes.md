---
name: hyperv-io-contention-notes
description: Hyper-V 환경의 디스크 I/O 경합 원인·진단·완화 참조 노트. Storage Stack 구조, 가상 컨트롤러 유형, Storage QoS, 성능 카운터, noisy neighbor 패턴 정리.
tags:
  - hyper-v
  - storage
  - io-contention
  - storage-qos
  - performance
  - cluster
last_checked: 2026-07-31
sources:
  - https://learn.microsoft.com/en-us/windows-server/storage/storage-qos/storage-qos-overview
  - https://learn.microsoft.com/en-us/windows-server/administration/performance-tuning/role/hyper-v-server/storage-io-performance
  - https://learn.microsoft.com/en-us/windows-server/administration/performance-tuning/role/hyper-v-server/detecting-virtualized-environment-bottlenecks
  - https://learn.microsoft.com/en-us/windows-server/failover-clustering/failover-cluster-csvs
---

# Hyper-V I/O 경합 참조 노트

## 1. Hyper-V Storage Stack 구조

### I/O 경로 4단계

> 출처: learn.microsoft.com/en-us/windows-server/administration/performance-tuning/role/hyper-v-server/storage-io-performance

```
1. Guest storage stack        <- 게스트 OS 드라이버
2. Host virtualization layer  <- Hyper-V VSP/VSC
3. Host storage stack         <- 호스트 OS 파일시스템·드라이버
4. Physical disk              <- 실제 디스크 하드웨어
```

모든 VM의 I/O는 호스트 스토리지 스택을 공유합니다. VM 간 I/O 경합은 3단계(Host storage stack)와 4단계(Physical disk)에서 발생합니다.

### VSP / VSC 구조

```
[Guest VM]
  VSC (Virtual Storage Client)   <- 게스트 측 드라이버
       |  VMBus (고속 내부 버스)
  VSP (Virtual Storage Provider) <- 호스트 측 드라이버
       |
  Host Storage Stack (NTFS, ReFS, 드라이버)
       |
  Physical Disk
```

| 구성 요소 | 역할                                             |
|-----------|--------------------------------------------------|
| VSC       | 게스트 OS에서 I/O 요청 생성                      |
| VMBus     | 하이퍼바이저 내부 통신 채널 (에뮬레이션 없음)    |
| VSP       | 호스트에서 I/O 요청 처리 및 실제 스토리지로 전달 |

---

## 2. 가상 컨트롤러 유형

> 출처: learn.microsoft.com/en-us/windows-server/administration/performance-tuning/role/hyper-v-server/storage-io-performance

| 컨트롤러           | 방식            | 성능 | 권장 용도               |
|--------------------|-----------------|------|-------------------------|
| **IDE**            | 에뮬레이션      | 낮음 | OS 디스크 (Gen 1 VM만)  |
| **SCSI (SAS)**     | 합성(Synthetic) | 높음 | 데이터 디스크 기본 권장 |
| **Virtual FC HBA** | 합성            | 높음 | SAN 연결 환경           |

🟡 SCSI 경로는 에뮬레이션하지 않으므로 IDE보다 성능이 높습니다. 단일 SCSI 컨트롤러에 최대 64개 디스크 연결 가능합니다.

### VHD 파일 유형별 성능

| 유형         | 설명                  | 성능                    | 권장            |
|--------------|-----------------------|-------------------------|-----------------|
| Fixed        | 미리 전체 용량 할당   | 높음                    | 운영 환경 권장  |
| Dynamic      | 사용량에 따라 증가    | 낮음 (확장 오버헤드)    | 개발/테스트     |
| Differencing | 부모 디스크 기반 차분 | 낮음 (체인 깊어질수록↓) | 체크포인트 용도 |

---

## 3. I/O 경합 원인 (Noisy Neighbor)

### 주요 원인

| 원인                   | 설명                                                |
|------------------------|-----------------------------------------------------|
| **Noisy neighbor VM**  | 특정 VM이 스토리지 대역폭 독점                      |
| 물리 디스크 과부하     | 여러 VM이 동일 LUN/디스크 공유                      |
| CSV coordinator 과부하 | redirected I/O 집중 시 coordinator 노드 병목        |
| VHD fragmentation      | Dynamic VHD 확장 반복으로 단편화 발생               |
| 스냅샷/체크포인트 체인 | differencing 디스크 체인이 길어질수록 I/O 지연 증가 |

### CSV I/O 경로 특이사항

```
CSV Direct I/O (NTFS 볼륨)
  모든 노드가 직접 디스크 접근 -> 성능 최적

CSV Redirected I/O (ReFS 볼륨 또는 장애 상황)
  coordinator 노드 경유 -> 네트워크 트래픽 증가, 지연 증가
```

🟡 ReFS로 CSV 구성 시 항상 redirected mode로 동작합니다. Hyper-V VM 스토리지에는 NTFS 권장합니다.

---

## 4. Storage QoS

### 공식 정의

> "Storage QoS provides a way to centrally monitor and manage storage performance for virtual
> machines using Hyper-V and the Scale-Out File Server roles. The feature automatically
> improves storage resource fairness between multiple virtual machines."
> — learn.microsoft.com/en-us/windows-server/storage/storage-qos/storage-qos-overview

### 적용 버전 및 요구 사항

| 항목      | 내용                                              |
|-----------|---------------------------------------------------|
| 도입 버전 | Windows Server 2016                               |
| 배포 형태 | Hyper-V + Scale-Out File Server 또는 S2D 클러스터 |
| 에디션    | Datacenter (S2D 구성 시)                          |

### Normalized IOPS 개념

> "Any IO that is 8KB or smaller is considered as one normalized IO.
> Any IO that is larger than 8KB is treated as multiple normalized IOs."

```
8KB 이하 I/O  = 1 normalized IOPS
256KB I/O     = 32 normalized IOPS (256 / 8 = 32)
```

I/O 크기가 달라도 공정하게 비교하기 위해 8KB 단위로 정규화합니다.

### QoS Policy 속성

| 속성        | 설명                                           |
|-------------|------------------------------------------------|
| PolicyId    | 정책 고유 식별자 (자동 생성)                   |
| MinimumIOPS | 보장 최소 normalized IOPS                      |
| MaximumIOPS | 제한 최대 normalized IOPS (0 = 무제한)         |
| PolicyType  | Dedicated (VM별 독립) / Aggregated (공유 합산) |

#### Policy 유형 비교

| 유형           | 설명                        | 사용 예           |
|----------------|-----------------------------|-------------------|
| **Dedicated**  | VM마다 Min/Max 독립 적용    | 중요 VM 보호      |
| **Aggregated** | 그룹 내 모든 VM이 IOPS 공유 | 동일 등급 VM 묶음 |

### 주요 PowerShell 명령어

```powershell
# Storage QoS 리소스 상태 확인
Get-ClusterResource -Name "Storage Qos Resource"

# QoS 정책 목록 조회
Get-StorageQosPolicy

# 새 정책 생성 (최소 100, 최대 500 IOPS)
New-StorageQosPolicy -Name "StandardVM" -MinimumIops 100 -MaximumIops 500

# VM VHD에 정책 적용
Set-VMHardDiskDrive -VMName "VM01" -ControllerNumber 0 -ControllerLocation 0 `
    -QoSPolicyID (Get-StorageQosPolicy -Name "StandardVM").PolicyId

# flow별 IOPS 실시간 모니터링
Get-StorageQosFlow | Sort-Object -Property StorageNodeIOPS -Descending |
    Format-Table VMName, FilePath, InitiatorIOPS, InitiatorLatency, StorageNodeIOPS, Status
```

---

## 5. 성능 카운터

> 출처: learn.microsoft.com/en-us/windows-server/administration/performance-tuning/role/hyper-v-server/detecting-virtualized-environment-bottlenecks

### 호스트 스토리지 병목 진단

| 카운터                                          | 임계 기준 | 의미           |
|-------------------------------------------------|-----------|----------------|
| `Physical Disk(*)\Avg. Disk sec/Read`           | > 50ms    | 읽기 지연 높음 |
| `Physical Disk(*)\Avg. Disk sec/Write`          | > 50ms    | 쓰기 지연 높음 |
| `Physical Disk(*)\Avg. Disk Read Queue Length`  | > 2       | 읽기 큐 적체   |
| `Physical Disk(*)\Avg. Disk Write Queue Length` | > 2       | 쓰기 큐 적체   |
| `Physical Disk(*)\Disk Transfers/sec`           | 사양 대비 | 총 IOPS        |

### Hyper-V 가상 스토리지 카운터

| 카운터                                                   | 설명             |
|----------------------------------------------------------|------------------|
| `Hyper-V Virtual Storage Device(*)\Read Bytes/sec`       | VM별 읽기 처리량 |
| `Hyper-V Virtual Storage Device(*)\Write Bytes/sec`      | VM별 쓰기 처리량 |
| `Hyper-V Virtual Storage Device(*)\Read Operations/sec`  | VM별 읽기 IOPS   |
| `Hyper-V Virtual Storage Device(*)\Write Operations/sec` | VM별 쓰기 IOPS   |
| `Hyper-V Virtual Storage Device(*)\Latency`              | VM별 I/O 지연    |

### 명령어로 확인

```powershell
# 실시간 물리 디스크 큐 확인 (1초 간격, 5회)
Get-Counter "\Physical Disk(*)\Avg. Disk Queue Length" -SampleInterval 1 -MaxSamples 5

# VM별 스토리지 I/O 확인
Get-Counter "\Hyper-V Virtual Storage Device(*)\Read Operations/sec",
            "\Hyper-V Virtual Storage Device(*)\Write Operations/sec" `
    -SampleInterval 1 -MaxSamples 3

# Storage QoS flow 실시간 모니터링
Get-StorageQosFlow | Sort-Object -Property StorageNodeIOPS -Descending |
    Format-Table VMName, FilePath, InitiatorIOPS, InitiatorLatency, StorageNodeIOPS, Status
```

---

## 6. I/O 경합 완화 방법

| 방법                          | 설명                               | 효과                |
|-------------------------------|------------------------------------|---------------------|
| **Storage QoS 정책 적용**     | MaximumIOPS로 noisy neighbor 제한  | 직접적              |
| **VM을 다른 스토리지로 분산** | 부하 분산                          | 근본적              |
| **Fixed VHD 사용**            | Dynamic/Differencing 오버헤드 제거 | 성능 향상           |
| **SCSI 컨트롤러 사용**        | IDE 에뮬레이션 제거                | 지연 감소           |
| **스냅샷/체크포인트 제거**    | differencing 체인 단축             | 지연 감소           |
| **Tiered Storage Spaces**     | 핫 데이터 SSD 자동 배치            | 처리량 향상         |
| **CSV 재조정**                | coordinator 노드 부하 분산         | redirected I/O 감소 |

```powershell
# 스냅샷 보유 VM 목록 확인
Get-VM | Where-Object { (Get-VMSnapshot -VMName $_.Name).Count -gt 0 } |
    Select-Object Name, @{n='Snapshots';e={(Get-VMSnapshot -VMName $_.Name).Count}}

# VHD 유형 확인
Get-VM | Get-VMHardDiskDrive | ForEach-Object {
    $info = Get-VHD $_.Path
    [PSCustomObject]@{
        VM   = $_.VMName
        Path = $_.Path
        Type = $info.VhdType
        Size = "$([math]::Round($info.FileSize/1GB,1)) GB"
    }
}
```

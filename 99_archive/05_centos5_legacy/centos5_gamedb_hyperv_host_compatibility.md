# CentOS 5.11 게임 DB 서버 Hyper-V 호스트 호환성

CentOS 5.11 i386 PAE에서 MySQL(게임 DB)을 운영할 때 Hyper-V 호스트 버전별 호환성, I/O 경합 위험, MMIO 제약을 정리합니다.

## 목차

| 섹션                                                                                                                                             |
|--------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 호스트 호환성 종합](#1-호스트-호환성-종합) / [2. 기능별 상세 비교](#2-기능별-상세-비교) / [3. MMIO gap과 DB 메모리](#3-mmio-gap과-db-메모리) |
| [4. I/O 경합과 MySQL 위험](#4-io-경합과-mysql-위험) / [5. 버전별 DB 서버 대응](#5-버전별-db-서버-대응) / [6. VHD vs VHDX](#6-vhd-vs-vhdx)        |
| [7. 권장 사항](#7-권장-사항) / [8. 참고 자료](#8-참고-자료)                                                                                      |

---

## 1. 호스트 호환성 종합

### 호환 기능 수

| 호스트      | 사용 가능 기능 | DB 운영 핵심 기능 | 무중단 I/O 분리 | 권장도 |
|-------------|----------------|-------------------|-----------------|--------|
| 2008 R2     | 8개            | 제한적            | ❌              | ❌     |
| 2012        | 11개           | 보통              | ✅ (Storage LM) | 🟡     |
| **2012 R2** | **15개**       | **충분**          | ✅ (Storage LM) | ✅     |
| 2016        | 15개 (동일)    | 충분 + QoS        | ✅ + QoS        | ✅     |

### DB 서버 관점 핵심 판정

| 호스트      | CentOS 5.11 동작 | MySQL 안전 운영 | 데이터 보호 | 판정           |
|-------------|------------------|-----------------|-------------|----------------|
| 2008 R2     | ✅               | 🟡 위험         | ❌ 취약     | 즉시 교체      |
| 2012        | ✅               | ✅ 가능         | 🟡 조건부   | 단기 운영 가능 |
| **2012 R2** | ✅               | ✅ 가능         | ✅ 가능     | **최적 호환**  |
| 2016        | ✅               | ✅ 가능         | ✅ 가능     | 추가 이점 없음 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 기능별 상세 비교

### CentOS 5.11 사용 가능 기능 (Microsoft 공식 매트릭스)

| 기능                        | 2008 R2 | 2012 | 2012 R2 | DB 운영 관련도    |
|-----------------------------|---------|------|---------|-------------------|
| Core (기본 동작)            | ✅      | ✅   | ✅      | 필수              |
| Jumbo frames                | ✅      | ✅   | ✅      | replication       |
| VLAN tagging                | ✅      | ✅   | ✅      | 네트워크 분리     |
| Live Migration              | ✅      | ✅   | ✅      | 유지보수          |
| Static IP Injection         | ❌      | ✅   | ✅      | 배포 자동화       |
| TCP Offloads                | ✅      | ✅   | ✅      | 네트워크 성능     |
| VHDX resize                 | ❌      | ❌   | ✅      | **디스크 확장**   |
| Virtual Fibre Channel       | ❌      | ❌   | ✅      | SAN 연결          |
| Live virtual machine backup | ❌      | ❌   | ✅      | **무중단 백업**   |
| PAE Kernel Support          | ✅      | ✅   | ✅      | 메모리 확장       |
| Dynamic Memory (Ballooning) | ❌      | ✅   | ✅      | 메모리 효율       |
| MMIO gap configuration      | ❌      | ❌   | ✅      | **메모리 최적화** |
| Hyper-V Video               | ✅      | ✅   | ✅      | 관리 콘솔         |
| Key-Value Pair              | ✅      | ✅   | ✅      | 호스트 연동       |
| Non-Maskable Interrupt      | ❌      | ❌   | ✅      | 커널 디버깅       |

### DB 서버에 필수인 기능

| 기능                   | 이유                               | 최소 호스트 |
|------------------------|------------------------------------|-------------|
| Live Backup            | DB 무중단 백업 (크래시 일관 이상)  | 2012 R2     |
| VHDX resize            | DB 용량 증가 시 무중단 디스크 확장 | 2012 R2     |
| MMIO gap configuration | 4GB 할당 시 buffer pool 최대화     | 2012 R2     |
| Storage Live Migration | I/O 경합 발생 시 무중단 VHD 이동   | 2012        |

[⬆ 목차로 돌아가기](#목차)

---

## 3. MMIO gap과 DB 메모리

### MMIO gap 개념

32-bit 게스트의 4GB 주소 공간에서 하드웨어 디바이스용으로 예약된 영역입니다.

```
VM Memory Address Space (4GB, 32-bit PAE)

0x00000000 ┌──────────────────────────────┐
           │                              │
           │   Usable RAM                 │
           │                              │
0xC0000000 ├──────────────────────────────┤  <- MMIO gap (default 1GB)
           │   PCI config, VGA, APIC etc  │
0xFFFFFFFF └──────────────────────────────┘
```

### DB 서버 메모리 할당과 MMIO 영향

| VM 할당 메모리 | MMIO gap (기본) | 실제 사용 가능 | InnoDB buffer pool 권장 | 손실  |
|----------------|-----------------|----------------|-------------------------|-------|
| 2GB            | 1GB             | 2GB            | 1~1.2GB                 | 없음  |
| 3GB            | 1GB             | 3GB            | 1.5~2GB                 | 없음  |
| 3.5GB          | 1GB             | **3GB**        | 1.5~2GB                 | 0.5GB |
| 4GB            | 1GB             | **3GB**        | 1.5~2GB                 | 1GB   |

### MMIO gap 조정 (2012 R2+만 가능)

```powershell
# gap 크기를 512MB로 축소
Set-VMMemory -VMName "GameDB" -MmioGapSize 512MB

# 결과: 4GB 할당 시 3.5GB 사용 가능 (기본 1GB gap → 512MB)
```

| gap 크기   | 4GB 할당 시 사용 가능 RAM | buffer pool 확보 |
|------------|---------------------------|------------------|
| 1GB (기본) | 3GB                       | ~2GB             |
| 512MB      | 3.5GB                     | ~2.5GB           |
| 256MB      | 3.75GB                    | ~2.7GB           |

🟡 gap을 너무 줄이면 PCI 디바이스 매핑 공간이 부족할 수 있습니다. 512MB가 안전한 최소값입니다.

### 2008 R2에서는

- MMIO gap 조정 불가 (고정 1GB)
- 4GB 할당해도 3GB만 사용 가능
- buffer pool이 제한되어 **디스크 I/O 증가 → I/O 경합에 더 취약**

[⬆ 목차로 돌아가기](#목차)

---

## 4. I/O 경합과 MySQL 위험

### 게임 서버 vs DB 서버 I/O 경합 영향 비교

| 항목                | 게임 서버            | MySQL DB 서버                       |
|---------------------|----------------------|-------------------------------------|
| I/O 패턴            | read + 로그 write    | random read/write 혼합              |
| fsync 의존도        | 낮음                 | 높음 (매 커밋마다 flush)            |
| I/O timeout 시 영향 | 파일시스템 read-only | **트랜잭션 유실 + 크래시 복구**     |
| read-only 전환 시   | 서비스 중단          | **데이터 정합성 손상 가능**         |
| 복구 시간           | 재부팅이면 끝        | InnoDB crash recovery 수 분~수십 분 |
| replication 영향    | 없음                 | **slave 동기화 중단**               |

### 파일시스템 read-only 발생 시 MySQL 증상

```
[ERROR] InnoDB: Operating system error number 30 in a file operation.
[ERROR] InnoDB: Error number 30 means 'Read-only file system'.
[ERROR] /usr/sbin/mysqld: Disk is full writing './binlog.000042'
[ERROR] InnoDB: Write to file ./ibdata1 failed at offset XXXXX
[ERROR] InnoDB: Crash recovery is required
```

### 데이터 손상 시나리오

```
I/O contention (noisy neighbor VM)
         │
         v
SCSI timeout 60s (no disk response)
         │
         v
EXT4 journal abort -> filesystem read-only
         │
         v
InnoDB doublewrite interrupted
         │
         v
┌─────────────────────────────────────────┐
│  Best:  crash recovery completes OK     │
│  Worst: page corruption -> table repair │
└─────────────────────────────────────────┘
```

### 실제 사례 (2026-07-15) 적용

Hermes-Game/Acheron-Game에서 발생한 사례와 동일한 환경에 DB가 있다면:

```
Jul 15 16:38:24 kernel: sd 1:0:0:1: timing out command, waited 60s
Jul 15 16:38:25 kernel: EXT4-fs (sdc1): Remounting filesystem read-only
```

- DB가 sdc1에 있었다면 → **InnoDB 크래시 복구 + binlog 유실 가능**
- 복구 후에도 데이터 정합성 검증 필요 (`CHECK TABLE`, `mysqlcheck`)

### 위험도 판정

| 위험 요소                             | 심각도  |
|---------------------------------------|---------|
| I/O 경합 → 파일시스템 read-only       | 🔴 치명 |
| MySQL 5.0/5.5 EOL (보안 취약점)       | 🔴 치명 |
| InnoDB crash recovery 실패 가능       | 🔴 치명 |
| Replication 중단 + 데이터 불일치      | 🟡 높음 |
| MMIO로 인한 buffer pool 제한          | 🟡 중간 |
| binlog 유실 → point-in-time 복구 불가 | 🔴 치명 |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 버전별 DB 서버 대응

### Windows Server 2008 R2

```
대응 수단: VHD 물리 분리 (유일, 다운타임 필요)
```

| 항목            | 상태                             |
|-----------------|----------------------------------|
| 무중단 VHD 이동 | ❌ 불가                          |
| 무중단 백업     | ❌ 불가 (크래시 일관만)          |
| MMIO gap 조정   | ❌ 불가                          |
| Storage QoS     | ❌ 불가                          |
| DB 보호 수단    | VHD 분리 + mysqldump 수동 백업만 |

### Windows Server 2012

```
대응 수단: Storage Live Migration (무중단) + VHD 분리
```

| 항목            | 상태                        |
|-----------------|-----------------------------|
| 무중단 VHD 이동 | ✅ Storage Live Migration   |
| 무중단 백업     | ❌ (Live Backup은 2012 R2+) |
| MMIO gap 조정   | ❌ (2012 R2+)               |
| Storage QoS     | ❌ (2016+)                  |
| DB 보호 수단    | 무중단 이동 + mysqldump     |

### Windows Server 2012 R2 (최적 호환)

```
대응 수단: Storage Live Migration + Live Backup + MMIO 조정
```

| 항목            | 상태                                  |
|-----------------|---------------------------------------|
| 무중단 VHD 이동 | ✅ Storage Live Migration             |
| 무중단 백업     | ✅ Live virtual machine backup        |
| MMIO gap 조정   | ✅ buffer pool 최대화 가능            |
| VHDX 확장       | ✅ 무중단 디스크 확장                 |
| Storage QoS     | ❌ (2016+)                            |
| DB 보호 수단    | 무중단 이동 + 무중단 백업 + VHDX 확장 |

### Windows Server 2016

```
대응 수단: 2012 R2 전부 + Storage QoS
```

| 항목            | 상태                                      |
|-----------------|-------------------------------------------|
| 무중단 VHD 이동 | ✅                                        |
| 무중단 백업     | ✅                                        |
| MMIO gap 조정   | ✅                                        |
| VHDX 확장       | ✅                                        |
| Storage QoS     | ✅ Min IOPS 보장                          |
| DB 보호 수단    | 전부 + **I/O 보장 (noisy neighbor 방지)** |

🟡 2016은 Storage QoS가 추가되지만, CentOS 5.11 기준 사용 가능 기능 수는 2012 R2와 동일합니다(15개). QoS만 호스트 측 추가 기능입니다.

[⬆ 목차로 돌아가기](#목차)

---


## 6. VHD vs VHDX

### 호환성 비교

CentOS 5.11은 VHD, VHDX 모두에서 정상 부팅됩니다. 차이는 성능과 데이터 보호입니다.

| 항목                | VHD                  | VHDX                       |
|---------------------|----------------------|----------------------------|
| CentOS 5.11 부팅    | ✅                   | ✅                         |
| 최대 크기           | 2TB                  | 64TB                       |
| 섹터 정렬           | 512B (비정렬 가능)   | 4KB (항상 정렬)            |
| 메타데이터 보호     | 없음                 | 로그 기반 (전원 장애 보호) |
| 온라인 확장         | ❌                   | ✅ (2012 R2+)              |
| 최소 호스트         | 2008+                | 2012+                      |
| 블록 크기 (Dynamic) | 2MB 고정             | 1MB~256MB 선택 가능        |
| 4KB random I/O 성능 | 비정렬 추가 I/O 발생 | 정렬되어 효율적            |

### DB 서버에서 중요한 차이

| 항목                         | VHD                    | VHDX                      |
|------------------------------|------------------------|---------------------------|
| 전원 장애 시 메타데이터 손상 | 가능                   | 로그로 보호 (내부 저널링) |
| 4KB 섹터 디스크 호환         | 🟡 성능 저하 가능      | ✅ 네이티브 지원          |
| Dynamic 디스크 조각화        | 심함 (2MB 블록)        | 적음 (큰 블록 선택 가능)  |
| 디스크 확장 시               | VM 정지 필요           | 실행 중 확장 가능         |
| InnoDB I/O 정합성            | 512B 비정렬 → 추가 RMW | 4KB 정렬 → 직접 쓰기      |

### 4KB 정렬 문제

```
물리 디스크: 4KB 섹터 (AF, Advanced Format)

VHD (512B 섹터):
  InnoDB 16KB page write → 물리 4KB 경계에 걸침
  → Read-Modify-Write 발생 (추가 I/O)

VHDX (4KB 섹터):
  InnoDB 16KB page write → 4KB 경계 정렬
  → 직접 쓰기 (추가 I/O 없음)
```

I/O 경합 상황에서 이 차이는 더 크게 체감됩니다. VHD의 비정렬 쓰기는 물리 디스크에 2배의 I/O를 발생시킬 수 있습니다.

### 호스트별 지원

| 호스트  | VHD | VHDX | CentOS 5.11 + VHD | CentOS 5.11 + VHDX |
|---------|-----|------|-------------------|--------------------|
| 2008 R2 | ✅  | ❌   | ✅                | —                  |
| 2012    | ✅  | ✅   | ✅                | ✅                 |
| 2012 R2 | ✅  | ✅   | ✅                | ✅                 |
| 2016+   | ✅  | ✅   | ✅                | ✅                 |

- 2008 R2: VHD만 사용 가능 (VHDX 미지원)
- 2012+: 둘 다 가능, **VHDX 권장**

### Fixed vs Dynamic (DB 서버)

| 유형         | 장점                   | 단점                     | DB 적합성 |
|--------------|------------------------|--------------------------|-----------|
| Fixed VHD    | 조각화 없음, 성능 일정 | 즉시 전체 용량 할당      | ✅        |
| Dynamic VHD  | 용량 절약              | 조각화, 확장 시 I/O 부하 | ❌        |
| Fixed VHDX   | 조각화 없음 + 4KB 정렬 | 즉시 전체 용량 할당      | ✅ 최적   |
| Dynamic VHDX | 용량 절약 + 4KB 정렬   | 확장 시 I/O 부하         | 🟡 조건부 |

**DB 서버 권장: Fixed VHDX**

### 변환 방법

```powershell
# VHD → VHDX 변환 (VM 정지 필요)
Stop-VM -Name "GameDB"
Convert-VHD -Path "D:\VMs\GameDB.vhd" -DestinationPath "D:\VMs\GameDB.vhdx"

# Dynamic → Fixed 동시 변환
Convert-VHD -Path "D:\VMs\GameDB.vhd" -DestinationPath "D:\VMs\GameDB_fixed.vhdx" -VHDType Fixed

# VM에 새 디스크 연결
Remove-VMHardDiskDrive -VMName "GameDB" -ControllerType IDE -ControllerNumber 0 -ControllerLocation 0
Add-VMHardDiskDrive -VMName "GameDB" -ControllerType IDE -ControllerNumber 0 -ControllerLocation 0 -Path "D:\VMs\GameDB_fixed.vhdx"

Start-VM -Name "GameDB"
```

🟡 변환에 다운타임이 필요합니다. DB 크기에 따라 수 분~수십 분 소요됩니다. 변환 전 충분한 디스크 여유 공간을 확인합니다.

### DB 상황별 권장

| 상황                           | 권장                                     |
|--------------------------------|------------------------------------------|
| 호스트 2008 R2                 | VHD (선택지 없음) → **Fixed VHD 필수**   |
| 호스트 2012+, 신규 VM          | Fixed VHDX                               |
| 호스트 2012+, 기존 VHD 운영 중 | 유지보수 윈도우에 Fixed VHDX 변환        |
| Dynamic 사용 중                | **Fixed로 변환** (Dynamic은 DB에 부적합) |

[⬆ 목차로 돌아가기](#목차)


## 7. 권장 사항

### 호스트 선택 (CentOS 5.11 DB 기준)

| 순위 | 호스트      | 이유                                               |
|------|-------------|----------------------------------------------------|
| 1    | **2012 R2** | CentOS 5 최적 호환 (15개 기능) + DB 필수 기능 충족 |
| 2    | 2016        | 2012 R2 + Storage QoS (추가 이점)                  |
| 3    | 2012        | Storage Live Migration 가능하나 백업/MMIO 부재     |
| 4    | 2008 R2     | ❌ DB 운영 부적합 (무중단 기능 없음)               |

### DB VHD 즉시 조치

| 우선순위 | 조치                                 | 호스트 요구  | 효과  |
|----------|--------------------------------------|--------------|-------|
| 1        | DB VHD를 **전용 물리 디스크**로 분리 | 모든 버전    | ★★★★★ |
| 2        | DB VHD를 Fixed VHD/VHDX로 변환       | 2012+ (VHDX) | ★★★☆☆ |
| 3        | MMIO gap 축소 (512MB)                | 2012 R2+     | ★★★☆☆ |
| 4        | I/O timeout 120초 이상 설정          | 게스트 내    | ★★☆☆☆ |
| 5        | InnoDB doublewrite 활성화 확인       | 게스트 내    | ★★★★☆ |

### DB 서버 확인 명령어

```bash
# MySQL 버전
mysql --version

# InnoDB buffer pool 크기
mysql -e "SHOW VARIABLES LIKE 'innodb_buffer_pool_size';"

# doublewrite 활성화 확인 (데이터 보호 핵심)
mysql -e "SHOW VARIABLES LIKE 'innodb_doublewrite';"

# 디스크 위치
df -h /var/lib/mysql

# 현재 I/O 상태
iostat -x 2 3

# InnoDB pending I/O 확인
mysql -e "SHOW ENGINE INNODB STATUS\G" | grep -A5 "FILE I/O"

# VM 메모리 실제 사용 가능 확인
free -m
```

### 호스트 확인 명령어

```powershell
# DB VM의 VHD 위치 확인
Get-VM "GameDB" | Get-VMHardDiskDrive | Select Path

# 같은 볼륨에 다른 VM 있는지 확인
Get-VM | Get-VMHardDiskDrive | Where-Object {$_.Path -like "C:\ClusterStorage\Volume1\*"} | Select VMName, Path

# MMIO gap 현재 설정 (2012 R2+)
Get-VMMemory -VMName "GameDB" | Select MmioGapSize

# VM 메모리 할당 확인
Get-VM "GameDB" | Select MemoryStartup, MemoryAssigned
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 참고 자료

- CentOS 5.x Hyper-V Feature Matrix (Archive): [web.archive.org/technet](https://web.archive.org/web/2016/https://technet.microsoft.com/en-us/library/dn531026.aspx) — ★★★★☆
- Windows Server 2012 R2 Lifecycle: [learn.microsoft.com](https://learn.microsoft.com/en-us/lifecycle/products/windows-server-2012-r2) — ★★★☆☆
- Storage QoS Overview: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/storage/storage-qos/storage-qos-overview) — ★★★☆☆
- [_reference/hyperv_version_comparison_notes.md](../../_reference/hyperv_version_comparison_notes.md)
- [_reference/hyperv_io_contention_notes.md](../../_reference/hyperv_io_contention_notes.md)
- [hyperv_io_contention_legacy_vm.md](hyperv_io_contention_legacy_vm.md)
- [hyperv_version_centos5_compatibility.md](hyperv_version_centos5_compatibility.md)

---

**작성일**: 2026-07-16

**마지막 업데이트**: 2026-07-16

© 2026 siasia86. Licensed under CC BY 4.0.

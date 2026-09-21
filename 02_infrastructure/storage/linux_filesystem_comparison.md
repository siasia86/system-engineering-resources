# Linux 파일시스템 비교: ext4·XFS·Btrfs·ZFS
<!-- reference: _reference/linux_filesystem_official_notes.md, _reference/openzfs_official_notes.md -->

이 문서는 Linux와 유사 Unix 환경에서 자주 사용하는 `ext4`, `XFS`, `Btrfs`, `ZFS` 계열 파일시스템을 범용 스토리지 설계·운영·복구 관점에서 비교합니다. 특정 배포판이나 애플리케이션에 종속되지 않도록 파일시스템 기능, 장애 모델, Snapshot·백업 경계를 중심으로 설명합니다.

> Filesystem: 파일·디렉터리·권한·메타데이터를 블록 디바이스 위에 배치하고 관리하는 계층입니다. RAID·LVM·백업 도구와 역할이 다르므로 파일시스템 자체의 장애 보호와 백업을 구분해야 합니다.

## 목차

| 섹션                                             | 내용                    |
|--------------------------------------------------|-------------------------|
| [1. 파일시스템의 역할](#1-파일시스템의-역할)     | VFS·저널링·COW·checksum |
| [2. 전체 비교](#2-전체-비교)                     | 기능과 선택 기준        |
| [3. ext4·XFS·Btrfs·ZFS](#3-ext4xfsbtrfszfs)      | 파일시스템별 특징       |
| [4. 저장소 계층과 구성](#4-저장소-계층과-구성)   | 디스크·RAID·LVM·pool    |
| [5. 무결성·Snapshot·백업](#5-무결성snapshot백업) | 장애 보호의 경계        |
| [6. 운영·복구 검증](#6-운영복구-검증)            | 명령어와 점검 절차      |
| [7. 선택 가이드](#7-선택-가이드)                 | 환경별 권장 방향        |

## 1. 파일시스템의 역할

### Linux 저장소 계층

```text
Application
    │
    v
Filesystem
(ext4 / XFS / Btrfs / OpenZFS)
    │
    ├── LVM / Storage Pool
    ├── RAID / Mirror / RAIDZ
    └── Block Device
            │
            v
       SSD / HDD / NVMe
```

파일시스템은 파일과 메타데이터를 관리하지만, 다음 항목을 자동으로 모두 해결하지는 않습니다.

- 물리 디스크 장애
- 호스트 전체 장애
- 잘못된 애플리케이션 쓰기
- 랜섬웨어 삭제·암호화
- 별도 위치로의 장기 보존

### 저널링

저널링은 비정상 종료 후 파일시스템 메타데이터 복구 시간을 줄이는 구조입니다. 일반적으로 애플리케이션 데이터의 논리적 정합성이나 데이터베이스 트랜잭션을 보장하는 기능으로 해석하지 않습니다.

| 파일시스템 | 기본 성격                   | 주요 경계                                    |
|------------|-----------------------------|----------------------------------------------|
| ext4       | 저널 기반 범용 파일시스템   | 파일시스템 복구와 애플리케이션 정합성은 별도 |
| XFS        | 저널 기반 대규모 파일시스템 | 온라인 축소 미지원, 별도 백업 필요           |
| Btrfs      | COW 기반 파일시스템         | RAID5/6·운영 조합과 복구 검증 필요           |
| ZFS        | COW·Pool 기반 파일시스템    | OpenZFS 모듈·커널·배포판 조합 검증 필요      |

> Journaling: 메타데이터 변경을 별도 Journal에 기록하여 장애 후 파일시스템 구조를 빠르게 복구하는 방식입니다. Journal이 데이터베이스의 Commit Log나 백업 Snapshot을 대체하지는 않습니다.

### Copy-on-Write와 checksum

> Copy-on-Write(COW): 기존 블록을 직접 덮어쓰지 않고 변경 블록을 새 위치에 기록한 뒤 메타데이터를 교체하는 방식입니다. Snapshot과 clone에 유리하지만 쓰기 증폭과 공간 회수 정책을 함께 고려해야 합니다.

> Checksum: 저장하거나 읽은 데이터가 원래 값과 같은지 확인하는 값입니다. checksum은 손상을 탐지할 수 있지만, 복구할 별도 복제본이나 parity가 없으면 손상 데이터를 자동으로 복원하지 못합니다.

## 2. 전체 비교

### 기능 비교

| 항목                | ext4                 | XFS                   | Btrfs              | ZFS/OpenZFS                |
|---------------------|----------------------|-----------------------|--------------------|----------------------------|
| 기본 설계           | 저널링               | 저널링                | COW                | COW + Storage Pool         |
| 데이터 checksum     | 파일시스템 범위 제한 | 기본 설계의 핵심 아님 | 지원               | 지원                       |
| 메타데이터 checksum | 지원                 | 지원 범위 확인        | 지원               | 지원                       |
| Native Snapshot     | 외부 계층 필요       | 외부 계층 필요        | Subvolume Snapshot | Dataset Snapshot           |
| 압축                | 외부 계층            | 외부 계층             | 지원               | 지원                       |
| 암호화              | 계층별 구성          | 계층별 구성           | 구성 방식 확인     | 지원                       |
| 다중 디스크         | RAID/LVM 별도        | RAID/LVM 별도         | Multi-device       | Pool·Mirror·RAIDZ          |
| 온라인 확장         | 지원                 | 지원                  | 지원               | Pool·vdev 설계에 따라 다름 |
| 온라인 축소         | 제한적·도구별 확인   | 미지원                | 지원               | 구성별 확인                |
| 운영 생태계         | 매우 넓음            | 매우 넓음             | 넓음               | OpenZFS 생태계             |
| 보수적 기본 선택    | ✅                   | ✅                    | 조건부             | 조건부                     |

`ZFS` 항목은 Linux의 OpenZFS를 포함한 범주입니다. 배포판·커널·OpenZFS 모듈 버전에 따라 설치와 운영 방식이 달라질 수 있습니다.

### 선택 기준

| 우선 기준                            | 우선 검토              |
|--------------------------------------|------------------------|
| 배포판 기본 지원·단순 운영           | ext4 또는 XFS          |
| 대용량 파일·병렬 I/O                 | XFS                    |
| Snapshot·압축·서브볼륨               | Btrfs                  |
| Pool·end-to-end checksum·RAIDZ       | ZFS/OpenZFS            |
| 복구 도구와 운영 인력의 보수성       | ext4 또는 XFS          |
| 데이터 무결성과 Snapshot을 함께 설계 | Btrfs 또는 ZFS/OpenZFS |

## 3. ext4·XFS·Btrfs·ZFS

### `ext4` — 범용·보수적 선택

ext4는 Linux에서 널리 사용되는 저널링 파일시스템입니다.

장점:

- 배포판·설치 도구·복구 도구 생태계가 넓습니다.
- 일반 OS·애플리케이션 데이터에 적용하기 쉽습니다.
- 온라인 확장과 성숙한 `e2fsprogs` 도구를 사용합니다.
- 장애 대응 인력과 문서가 비교적 풍부합니다.

주의사항:

- 파일시스템 자체 Snapshot은 제공하지 않습니다.
- 디스크 이중화는 RAID·LVM·스토리지 계층이 담당합니다.
- 애플리케이션·DB 정합성 백업은 별도 구성합니다.

주요 확인 명령:

```bash
lsblk -f
findmnt -t ext4
sudo tune2fs -l /dev/sdX
sudo e2fsck -n /dev/sdX
```

`e2fsck`는 운영 중인 파일시스템에 수정 모드로 실행하지 않습니다. 복구가 필요하면 Unmount 또는 복구 환경에서 수행합니다.

### `XFS` — 대용량·병렬 I/O

XFS는 대용량 파일과 병렬 I/O에 적합한 저널링 파일시스템입니다.

장점:

- Allocation Group 기반 병렬 처리
- 대용량 파일·볼륨 환경
- 온라인 확장
- Reflink 등 선택 기능
- 엔터프라이즈 Linux 환경에서 넓은 사용 범위

주의사항:

- 온라인 축소를 지원하지 않습니다.
- XFS의 실제 복구는 `xfs_repair`를 사용합니다.
- `xfs_repair -L`은 로그를 초기화할 수 있어 데이터 유실 위험이 있습니다.
- Snapshot과 백업은 LVM·스토리지·백업 도구로 별도 설계합니다.

주요 확인 명령:

```bash
findmnt -t xfs
sudo xfs_info /mount/point
sudo xfs_repair -n /dev/sdX
```

`xfs_repair -n`은 읽기 전용 점검 용도입니다. 운영 복구에서 `-L`을 사용하기 전에는 백업과 영향 범위를 확인합니다.

### `Btrfs` — COW·Subvolume·Snapshot

Btrfs는 COW 기반으로 Subvolume·Snapshot·압축·checksum·Multi-device 기능을 제공하는 Linux 파일시스템입니다.

장점:

- Subvolume 단위 Snapshot
- Snapshot과 Send/Receive 조합
- 투명 압축
- 데이터·메타데이터 checksum
- 파일시스템 내부의 여러 관리 기능

주의사항:

- COW로 인한 쓰기 증폭과 Fragmentation을 workload별로 검증합니다.
- RAID5/6은 배포판·커널·도구 버전과 운영 요구사항을 별도로 확인합니다.
- Snapshot은 같은 디스크 장애와 랜섬웨어를 대신하지 않습니다.
- `btrfs check --repair`는 손상된 파일시스템에 위험할 수 있으므로 기본 복구 명령으로 사용하지 않습니다.

주요 확인 명령:

```bash
findmnt -t btrfs
sudo btrfs filesystem usage /mount/point
sudo btrfs subvolume list /mount/point
sudo btrfs scrub status /mount/point
```

### `ZFS/OpenZFS` — Pool·checksum·RAIDZ

ZFS는 COW 기반 Storage Pool과 Dataset 중심의 파일시스템입니다. Linux에서는 OpenZFS 프로젝트를 통해 사용합니다.

주요 기능:

- 데이터·메타데이터 checksum
- Storage Pool
- Mirror·RAIDZ
- Dataset·Quota·Reservation
- Snapshot·Clone
- 압축·암호화
- Scrub
- `zfs send`·`zfs receive` 기반 복제

장점:

- 파일시스템과 저장소 Pool을 통합적으로 설계할 수 있습니다.
- end-to-end 데이터 무결성 검증을 설계하기 좋습니다.
- Snapshot과 증분 Send/Receive가 강력합니다.
- RAIDZ·Mirror·Cache·Special vdev 등 다양한 저장소 구성이 가능합니다.

주의사항:

- Pool과 vdev 구성은 생성 후 변경 제약을 반드시 확인합니다.
- RAIDZ·Mirror는 백업이 아니라 저장소 장애 대응입니다.
- Snapshot은 같은 Pool의 장애·랜섬웨어·운영자 실수를 막지 못합니다.
- OpenZFS 모듈과 커널 업데이트를 함께 검증합니다.
- `zpool create`, `zpool destroy`, `zpool replace`는 데이터 유실 위험이 있습니다.

주요 확인 명령:

```bash
zpool status
zpool list
zfs list
zfs get all pool/dataset
zpool scrub pool
```

## 4. 저장소 계층과 구성

### 범용 계층 구조

```text
Application
      │
      v
Filesystem
      │
      ├── ext4 / XFS
      ├── Btrfs
      └── ZFS/OpenZFS
              │
              v
      Disk·RAID·LVM·Storage Pool
              │
              v
      SSD·HDD·NVMe·SAN
```

### Snapshot과 백업의 관계

```text
Filesystem Snapshot
└── 빠른 로컬 시점 복구

Remote Replication
└── 다른 호스트로 변경 블록·데이터 전송

Backup Tool
└── 장기 보존·암호화·오프사이트 복구
```

Snapshot·RAID·Replication을 백업으로 동일하게 취급하지 않습니다.

- RAID·Mirror: 디스크 장애 대응
- Replication: 다른 위치로 변경 내용 전달
- Snapshot: 같은 저장소에서 시점 복구
- Backup: 독립된 저장소에 과거 데이터를 보존

### 파일시스템 생성 전 확인

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,UUID
blkid
findmnt
```

다음 작업은 대상 디스크의 기존 데이터를 파괴할 수 있습니다.

```text
mkfs.*
zpool create
zpool destroy
btrfs device add/remove
xfs_growfs
```

디스크 식별자·Mount Point·백업 상태·롤백 방법을 확인한 뒤 수행합니다.

## 5. 무결성·Snapshot·백업

### 무결성 보호의 단계

```text
Checksum
└── 손상 탐지

Mirror / RAIDZ / Parity
└── 일부 장애 복구

Snapshot
└── 과거 시점 보존

Remote Backup
└── 호스트·Pool 전체 장애 대응

Immutable Backup
└── 삭제·변조·랜섬웨어 대응
```

한 계층이 다른 계층을 완전히 대체하지 않습니다.

### 파일시스템별 Snapshot

| 파일시스템 | Snapshot 방법         | 복구·복제 도구                 |
|------------|-----------------------|--------------------------------|
| ext4       | LVM·스토리지 Snapshot | LVM·백업 도구                  |
| XFS        | LVM·스토리지 Snapshot | LVM·백업 도구                  |
| Btrfs      | Subvolume Snapshot    | `btrfs send/receive`·백업 도구 |
| ZFS        | Dataset Snapshot      | `zfs send/receive`·백업 도구   |

### 백업 도구 연계

파일시스템 Snapshot만 보존하지 말고 별도 백업 도구와 조합합니다.

```text
Filesystem Snapshot
        │
        v
Restic / Borg / Bacula / Bareos
        │
        v
S3 / SFTP / Tape / Immutable Storage
```

데이터베이스·메시지·애플리케이션은 제품별 Export·Dump·Quiesce 절차를 먼저 적용합니다.

## 6. 운영·복구 검증

### 정기 점검

| 대상         | 확인 명령 예시          | 목적                       |
|--------------|-------------------------|----------------------------|
| Block Device | `lsblk -f`, `blkid`     | 장치·파일시스템 식별       |
| Mount        | `findmnt`               | 실제 Mount 옵션 확인       |
| ext4         | `e2fsck -n`             | 읽기 전용 구조 점검        |
| XFS          | `xfs_repair -n`         | 읽기 전용 복구 가능성 점검 |
| Btrfs        | `btrfs scrub status`    | Scrub 결과 확인            |
| ZFS          | `zpool status`          | Pool·vdev 상태 확인        |
| ZFS          | `zpool scrub`           | 데이터 checksum·복구 점검  |
| Backup       | Restic·Borg·Bacula 명령 | 별도 백업 복구 확인        |

### 복구 테스트

```text
1. 테스트 장치 또는 복구용 VM 준비
2. 파일시스템 Mount
3. Snapshot 또는 백업 데이터 복원
4. 파일·권한·소유자·ACL 확인
5. 애플리케이션 기동
6. 데이터 무결성 확인
7. 복구 시간 기록
```

RPO(Recovery Point Objective)는 허용 가능한 데이터 손실 시점이고, RTO(Recovery Time Objective)는 복구에 허용되는 시간입니다. 파일시스템 선택은 RPO·RTO를 대체하지 않으므로 별도 백업 정책과 함께 검증합니다.

### 실행 전 주의사항

- 운영 장치에서 `mkfs`를 실행하지 않습니다.
- Mount된 파일시스템에 복구용 `fsck`·repair 명령을 실행하지 않습니다.
- XFS `-L`과 Btrfs repair 계열 명령은 비상 절차로 제한합니다.
- ZFS Pool을 구성할 때 디스크 순서·시리얼·vdev 구성을 기록합니다.
- Snapshot을 백업으로만 간주하지 않습니다.
- 파일시스템 변경 전 복구 가능한 외부 백업을 확인합니다.
- 커널·파일시스템 도구·배포판 지원 범위를 고정하고 테스트합니다.

## 7. 선택 가이드

### ext4를 선택할 때

- 범용 Linux 서버가 필요합니다.
- 운영팀이 보수적인 장애 복구 절차를 선호합니다.
- Snapshot·RAID·백업을 별도 계층으로 관리합니다.
- 배포판 기본 설치와 도구 호환성이 중요합니다.

### XFS를 선택할 때

- 대용량 파일과 병렬 I/O가 중요합니다.
- 온라인 확장이 필요합니다.
- 온라인 축소가 필요하지 않습니다.
- LVM·스토리지 Snapshot과 별도 백업을 함께 사용합니다.

### Btrfs를 선택할 때

- Subvolume·Snapshot·압축이 중요합니다.
- Linux 파일시스템 계층에서 Snapshot과 Send/Receive를 활용합니다.
- RAID5/6과 COW workload를 충분히 검증할 수 있습니다.
- 배포판과 커널의 Btrfs 도구 버전을 통제할 수 있습니다.

### ZFS/OpenZFS를 선택할 때

- Pool·Dataset·checksum·RAIDZ가 필요합니다.
- Storage 관리와 파일시스템 관리를 통합하려 합니다.
- OpenZFS 모듈·커널·부트 환경을 운영할 수 있습니다.
- Scrub·Snapshot·Send/Receive·복구 훈련을 정기적으로 수행합니다.

### 최종 체크리스트

- 필요한 Snapshot·Clone·Replication 범위는 무엇인가?
- 데이터·메타데이터 checksum이 필요한가?
- 디스크 장애와 호스트 장애를 어떻게 분리하는가?
- 온라인 확장·축소 요구가 있는가?
- 압축·암호화·성능 간 균형은 무엇인가?
- 커널·배포판·도구의 지원 조합은 검증되었는가?
- Snapshot 외부에 독립된 백업이 있는가?
- 복구용 Live Image와 복구 절차가 있는가?
- RPO·RTO와 복구 테스트 결과가 기록되어 있는가?

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- Linux Filesystem Kernel Documentation: [docs.kernel.org/filesystems](https://docs.kernel.org/filesystems/) — ★★★★☆
- OpenZFS Project: [openzfs.org](https://openzfs.org/) — ★★★★☆
- OpenZFS on GitHub: [github.com/openzfs/zfs](https://github.com/openzfs/zfs) — ★★★☆☆
- [Linux Filesystem 공식 참조 노트](../../_reference/linux_filesystem_official_notes.md)
- [OpenZFS 공식 참조 노트](../../_reference/openzfs_official_notes.md)
- [범용 백업 도구 비교](./backup_tools_comparison.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-21

**마지막 업데이트**: 2026-09-21

© 2026 siasia86. Licensed under CC BY 4.0.

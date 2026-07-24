# 스토리지 아키텍처 — DAS, SAN, NAS

서버 스토리지의 연결 방식(DAS, SAN, NAS)과 프로토콜, RAID, 설계 기준을 정리합니다.

## 목차

| 섹션                                                                                                           |
|----------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. DAS](#2-das) / [3. SAN](#3-san) / [4. NAS](#4-nas)                                    |
| [5. 비교](#5-비교) / [6. RAID](#6-raid) / [7. 프로토콜](#7-프로토콜)                                           |
| [8. 설계 기준](#8-설계-기준) / [9. 클라우드 스토리지](#9-클라우드-스토리지) / [10. 트러블슈팅](#10-트러블슈팅) |

---

## 1. 개요

스토리지 아키텍처는 서버가 데이터를 저장하고 접근하는 방식을 결정합니다. 연결 방식에 따라 성능, 공유 가능성, 비용, 관리 복잡도가 달라집니다.

```
┌───────────────────┬─────────────────────┬─────────────────────┐
│       DAS         │        SAN          │        NAS          │
├───────────────────┼─────────────────────┼─────────────────────┤
│ Server --- Disk   │ Server --- FC/iSCSI │ Server --- NFS/SMB  │
│ (direct attach)   │    --- Switch ---   │    --- Ethernet --- │
│                   │    --- Storage ---  │    --- NAS Device   │
│                   │                     │                     │
│ Block Level       │ Block Level         │ File Level          │
└───────────────────┴─────────────────────┴─────────────────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. DAS

### 개요

DAS(Direct Attached Storage)는 서버에 직접 연결된 스토리지입니다. 별도 네트워크 없이 서버 내부 또는 외부 케이블로 연결합니다.

### 특성

| 항목      | 내용                                   |
|-----------|----------------------------------------|
| 연결 방식 | SATA, SAS, NVMe (서버 내부/외부 직결)  |
| 접근 레벨 | Block Level                            |
| 공유      | 단일 서버 전용 (공유 불가)             |
| 성능      | 네트워크 오버헤드 없음, 가장 낮은 지연 |
| 확장성    | 서버당 디스크 슬롯/케이블 제한         |
| 비용      | 가장 저렴 (별도 장비 불필요)           |
| 관리      | 단순 (서버 단위)                       |
| 장애 영향 | 서버 장애 시 데이터 접근 불가          |

### 구성 예시

```
┌───────────────────────────────────┐
│           Server                  │
│  ┌─────┐  ┌─────┐  ┌─────┐        │
│  │ SSD │  │ SSD │  │ HDD │        │
│  │NVMe │  │SATA │  │ SAS │        │
│  └─────┘  └─────┘  └─────┘        │
│       (Internal DAS)              │
└───────────────────────────────────┘

┌──────────┐  SAS Cable  ┌─────────────────┐
│  Server  │ ════════════ │ JBOD Enclosure │
│          │              │ (12-24 disks)  │
└──────────┘              └────────────────┘
```

### 사용 환경

- 단일 서버 DB (소규모)
- 개발/테스트 서버
- 백업 대상 로컬 디스크
- 비용 민감한 소규모 환경

[⬆ 목차로 돌아가기](#목차)

---

## 3. SAN

### 개요

SAN(Storage Area Network)은 서버와 스토리지를 전용 네트워크로 연결하는 고성능 스토리지 아키텍처입니다. 블록 레벨 접근을 제공하며, 여러 서버가 스토리지 풀을 공유합니다.

### 특성

| 항목      | 내용                                         |
|-----------|----------------------------------------------|
| 연결 방식 | FC (Fibre Channel) 또는 iSCSI (IP 기반)      |
| 접근 레벨 | Block Level (서버에서 로컬 디스크처럼 인식)  |
| 공유      | 여러 서버가 스토리지 풀 공유 (LUN 단위 할당) |
| 성능      | FC: 16/32/64 Gbps, iSCSI: 10/25/100 GbE      |
| 확장성    | 수백 TB ~ PB급, 디스크 추가로 온라인 확장    |
| 비용      | 고가 (FC 스위치, HBA, 스토리지 장비)         |
| 관리      | 전문 인력 필요 (Zoning, LUN Masking)         |
| 가용성    | 이중화 경로 (Multipath), 컨트롤러 이중화     |

### FC SAN 구성

```
┌────────┐  ┌────────┐  ┌──────────┐
│Server A│  │Server B│  │Server C  │
│  HBA   │  │  HBA   │  │  HBA     │
└───┬────┘  └───┬────┘  └───┬──────┘
    │            │                 │
    │   FC Fabric (Redundant)      │
┌───┴────────────┴────────────┴────┐
│        FC Switch A               │
└───┬─────────────────────────┬────┘
┌───┴─────────────────────────┴────┐
│        FC Switch B               │
└───┬─────────────────────────┬────┘
    │                              │
┌───┴─────────────────────────┴────┐
│      SAN Storage Array           │
│  ┌──────┐  ┌──────┐  ┌──────┐    │
│  │Ctrl A│  │Ctrl B│  │ Disk │    │
│  │(Act) │  │(Stby)│  │ Pool │    │
│  └──────┘  └──────┘  └──────┘    │
└──────────────────────────────────┘
```

### iSCSI SAN 구성

```
┌──────────┐  ┌──────────┐  ┌───────────┐
│ Server A │  │ Server B │  │ Server C  │
│  iSCSI   │  │  iSCSI   │  │  iSCSI    │
│Initiator │  │Initiator │  │Initiator  │
└────┬─────┘  └────┬─────┘  └────┬──────┘
     │              │                   │
┌────┴──────────────┴──────────────┴────┐
│       10/25 GbE Switch (VLAN)         │
└────┬──────────────────────────────┬───┘
     │                                  │
┌────┴──────────────────────────────┴───┐
│       iSCSI Storage (Target)          │
│       LUN 0, LUN 1, LUN 2 ...         │
└───────────────────────────────────────┘
```

### SAN 핵심 개념

| 용어        | 설명                                                         |
|-------------|--------------------------------------------------------------|
| LUN         | Logical Unit Number — 스토리지에서 서버에 할당하는 논리 단위 |
| Zoning      | FC 스위치에서 서버-스토리지 간 접근 제어                     |
| LUN Masking | 스토리지 컨트롤러에서 서버별 LUN 접근 제어                   |
| Multipath   | 이중 경로로 장애 시 자동 전환 (dm-multipath)                 |
| HBA         | Host Bus Adapter — 서버의 FC 연결 카드                       |
| WWPN        | World Wide Port Name — FC 포트 고유 식별자                   |
| Thin Prov   | 실제 사용량만큼만 물리 공간 할당                             |

### 사용 환경

- 엔터프라이즈 DB (Oracle RAC, MSSQL Cluster)
- VMware vSAN, Hyper-V Cluster (공유 스토리지)
- 고성능 OLTP 워크로드
- DR/복제가 필요한 미션 크리티컬 시스템

[⬆ 목차로 돌아가기](#목차)

---

## 4. NAS

### 개요

NAS(Network Attached Storage)는 이더넷 네트워크를 통해 파일 레벨 접근을 제공하는 스토리지입니다. 여러 서버/클라이언트가 동시에 같은 파일시스템을 공유합니다.

### 특성

| 항목      | 내용                                    |
|-----------|-----------------------------------------|
| 연결 방식 | Ethernet (1/10/25/100 GbE)              |
| 접근 레벨 | File Level (NFS, SMB/CIFS)              |
| 공유      | 여러 클라이언트가 동시 접근 (파일 공유) |
| 성능      | 네트워크 대역폭 의존, SAN보다 지연 높음 |
| 확장성    | Scale-out NAS로 PB급 확장 가능          |
| 비용      | SAN보다 저렴, 기존 이더넷 인프라 활용   |
| 관리      | 비교적 단순 (IP 기반)                   |
| 프로토콜  | NFS (Linux), SMB/CIFS (Windows)         |

### 구성

```
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────────┐
│  Linux  │  │ Windows │  │  macOS  │  │Container  │
│  Server │  │  Server │  │  Client │  │   Pod     │
│  (NFS)  │  │  (SMB)  │  │  (SMB)  │  │  (NFS)    │
└────┬────┘  └────┬────┘  └────┬────┘  └────┬──────┘
     │            │            │                   │
┌────┴────────────┴────────────┴─────────────┴─────┐
│              Ethernet Switch                     │
└────┬────────────────────────────────────────┬────┘
     │                                             │
┌────┴────────────────────────────────────────┴────┐
│                NAS Device                        │
│  /share/data    (NFS export)                     │
│  \\nas\public   (SMB share)                      │
│  /backup        (NFS export)                     │
└──────────────────────────────────────────────────┘
```

### NAS 프로토콜

| 프로토콜  | 포트       | OS         | 특징                            |
|-----------|------------|------------|---------------------------------|
| NFSv3     | 2049 + rpc | Linux/Unix | Stateless, UDP/TCP              |
| NFSv4     | 2049       | Linux/Unix | Stateful, TCP only, ACL 지원    |
| SMB 3.0   | 445        | Windows    | 암호화, Multichannel, RDMA      |
| SMB 3.1.1 | 445        | Windows    | Pre-auth integrity, AES-128-GCM |

### 사용 환경

- 파일 공유 (홈 디렉토리, 공용 폴더)
- 웹 콘텐츠 저장소 (이미지, 정적 파일)
- 백업 저장소
- 컨테이너 PV (NFS CSI)
- 로그 수집 중앙 저장소

[⬆ 목차로 돌아가기](#목차)

---

## 5. 비교

### DAS vs SAN vs NAS 전체 비교

| 항목        | DAS            | SAN                    | NAS                    |
|-------------|----------------|------------------------|------------------------|
| 접근 레벨   | Block          | Block                  | File                   |
| 프로토콜    | SATA/SAS/NVMe  | FC/iSCSI/NVMe-oF       | NFS/SMB                |
| 네트워크    | 없음 (직결)    | FC Fabric / IP         | Ethernet (IP)          |
| 공유        | 단일 서버      | 여러 서버 (LUN 단위)   | 여러 클라이언트 (파일) |
| 성능        | 높음 (직결)    | 높음 (전용 네트워크)   | 보통 (IP 네트워크)     |
| 지연        | 가장 낮음 (us) | 낮음 (sub-ms ~ ms)     | 보통 (ms)              |
| 확장성      | 서버 한도      | 수백 TB ~ PB           | 수백 TB ~ PB           |
| 비용        | 저             | 고                     | 중                     |
| 관리 복잡도 | 저             | 고 (전문 인력)         | 중                     |
| HA/DR       | 서버 의존      | 컨트롤러 이중화, 복제  | 복제, 스냅샷           |
| 주요 벤더   | 서버 내장      | Dell EMC, NetApp, Pure | Synology, QNAP, NetApp |

### 선택 기준

| 시나리오                 | 추천 | 이유                                |
|--------------------------|------|-------------------------------------|
| 단일 서버 DB (소규모)    | DAS  | 낮은 지연, 단순 구성, 저비용        |
| 엔터프라이즈 DB 클러스터 | SAN  | 블록 레벨 공유, 고성능, 이중화      |
| VMware/Hyper-V 클러스터  | SAN  | 공유 스토리지 필수 (Live Migration) |
| 파일 공유 (사무실/팀)    | NAS  | 멀티 프로토콜, 간편 관리            |
| 백업 저장소              | NAS  | 대용량, 비용 효율, 네트워크 접근    |
| K8s Persistent Volume    | NAS  | NFS CSI driver, 다중 Pod 접근       |
| 고성능 AI/ML 학습        | DAS  | GPU 서버에 NVMe 직결, 낮은 지연     |

[⬆ 목차로 돌아가기](#목차)

---

## 6. RAID

### RAID 레벨 비교

| RAID    | 최소 디스크 | 용량 효율 | 읽기 | 쓰기 | 허용 장애 | 용도                 |
|---------|-------------|-----------|------|------|-----------|----------------------|
| RAID 0  | 2           | 100%      | 높음 | 높음 | 0 (없음)  | 임시 데이터, 성능    |
| RAID 1  | 2           | 50%       | 높음 | 보통 | 1         | OS, Boot             |
| RAID 5  | 3           | (N-1)/N   | 높음 | 보통 | 1         | 범용 (읽기 위주)     |
| RAID 6  | 4           | (N-2)/N   | 높음 | 낮음 | 2         | 대용량, 안정성 우선  |
| RAID 10 | 4           | 50%       | 높음 | 높음 | 1/mirror  | DB, 고성능 + 안정성  |
| RAID 50 | 6           | (N-K)/N   | 높음 | 보통 | 1/group   | 대용량 + 성능 균형   |
| RAID 60 | 8           | (N-2K)/N  | 높음 | 낮음 | 2/group   | 대용량 + 높은 안정성 |

### RAID 다이어그램

```
RAID 0 (Stripe)         RAID 1 (Mirror)        RAID 5 (Parity)
┌─────┐ ┌─────┐        ┌─────┐ ┌─────┐        ┌─────┐ ┌─────┐ ┌─────┐
│ A1  │ │ A2  │        │ A1  │ │ A1  │        │ A1  │ │ A2  │ │ Ap  │
│ B1  │ │ B2  │        │ B1  │ │ B1  │        │ B1  │ │ Bp  │ │ B2  │
│ C1  │ │ C2  │        │ C1  │ │ C1  │        │ Cp  │ │ C1  │ │ C2  │
└─────┘ └─────┘        └─────┘ └─────┘        └─────┘ └─────┘ └─────┘
  Disk0   Disk1          Disk0   Disk1          Disk0   Disk1   Disk2

RAID 10 (Mirror + Stripe)
┌─────┐ ┌─────┐   ┌─────┐ ┌─────┐
│ A1  │ │ A1  │   │ A2  │ │ A2  │
│ B1  │ │ B1  │   │ B2  │ │ B2  │
│ C1  │ │ C1  │   │ C2  │ │ C2  │
└─────┘ └─────┘   └─────┘ └─────┘
 Disk0   Disk1     Disk2   Disk3
 (Mirror Set 1)    (Mirror Set 2)
```

### RAID 선택 기준

| 워크로드       | 추천 RAID | 이유                 |
|----------------|-----------|----------------------|
| OS/Boot        | RAID 1    | 미러링, 빠른 복구    |
| OLTP DB        | RAID 10   | 높은 IOPS, 쓰기 성능 |
| Data Warehouse | RAID 5/6  | 읽기 위주, 용량 효율 |
| 백업 스토리지  | RAID 6    | 안정성 우선, 대용량  |
| 임시/캐시      | RAID 0    | 성능 우선, 유실 허용 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 프로토콜

### 스토리지 프로토콜 비교

| 프로토콜 | 레벨  | 전송 매체     | 속도            | 지연      | 용도            |
|----------|-------|---------------|-----------------|-----------|-----------------|
| SATA     | Block | 케이블 (직결) | 6 Gbps          | 가장 낮음 | DAS (HDD/SSD)   |
| SAS      | Block | 케이블 (직결) | 12/24 Gbps      | 가장 낮음 | DAS (서버/JBOD) |
| NVMe     | Block | PCIe (직결)   | 32/64/128 Gbps  | 가장 낮음 | DAS (SSD)       |
| FC       | Block | FC Fabric     | 16/32/64 Gbps   | 낮음      | SAN             |
| iSCSI    | Block | Ethernet      | 10/25/100 Gbps  | 보통      | SAN (IP)        |
| NVMe-oF  | Block | FC/RDMA/TCP   | 100+ Gbps       | 매우 낮음 | SAN (차세대)    |
| NFS      | File  | Ethernet      | 네트워크 대역폭 | 보통      | NAS (Linux)     |
| SMB      | File  | Ethernet      | 네트워크 대역폭 | 보통      | NAS (Windows)   |

### FC vs iSCSI

| 항목      | FC                          | iSCSI                          |
|-----------|-----------------------------|--------------------------------|
| 전송 매체 | Fibre Channel (전용)        | Ethernet (공용/전용)           |
| 속도      | 32/64 Gbps                  | 10/25/100 GbE                  |
| 지연      | 낮음 (전용 네트워크)        | 보통 (IP 오버헤드)             |
| 비용      | 고가 (HBA, FC 스위치)       | 저렴 (기존 NIC, 이더넷 스위치) |
| 관리      | 복잡 (Zoning, WWPN)         | 비교적 단순 (IP 기반)          |
| 안정성    | 매우 높음 (Lossless Fabric) | 높음 (Jumbo Frame 권장)        |
| 주요 환경 | 금융, 대기업 DC             | 중소 규모, VDI, 테스트         |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 설계 기준

### 용량 계획

| 항목          | 계산 방식                               |
|---------------|-----------------------------------------|
| Raw 용량      | 디스크 수 × 디스크 용량                 |
| Usable 용량   | Raw × RAID 효율 × (1 - 스냅샷 예약)     |
| 일일 증가량   | 현재 사용량 / 운영 일수                 |
| 여유 공간     | Usable × 0.7~0.8 (70~80%에서 증설 검토) |
| 3년 필요 용량 | 현재 + (일일 증가량 × 1095) + 버퍼 20%  |

### 성능 계획

| 항목        | 기준                                    |
|-------------|-----------------------------------------|
| IOPS        | 워크로드별 필요 IOPS 산정 (DB: 만~십만) |
| Throughput  | 순차 읽기/쓰기 MB/s 요구량              |
| Latency     | OLTP < 1ms, 일반 < 5ms, 백업 < 20ms     |
| Queue Depth | 디스크/컨트롤러 큐 깊이 설정            |

### 가용성 설계

| 계층     | 이중화 방법                              |
|----------|------------------------------------------|
| 디스크   | RAID (1, 5, 6, 10)                       |
| 컨트롤러 | Active-Active 또는 Active-Standby 이중화 |
| 경로     | Multipath (dm-multipath, MPIO)           |
| 사이트   | 동기/비동기 복제 (DR)                    |
| 스위치   | FC 스위치 이중화 (Fabric A/B)            |

### 관리 명령어

```bash
# Linux multipath 확인
sudo multipath -ll

# iSCSI 타겟 조회
sudo iscsiadm -m discovery -t sendtargets -p 192.0.2.1
sudo iscsiadm -m session

# iSCSI 로그인
sudo iscsiadm -m node -T iqn.2026-01.com.storage:lun0 -p 192.0.2.1 --login

# NFS 마운트
sudo mount -t nfs -o vers=4,noatime 192.0.2.1:/share/data /mnt/nfs

# NFS 마운트 확인
showmount -e 192.0.2.1

# FC HBA 정보 (Linux)
sudo systool -c fc_host -v
cat /sys/class/fc_host/host*/port_name
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 클라우드 스토리지

### AWS 스토리지 매핑

| 온프레미스 | AWS 대응          | 접근 레벨 | 용도                 |
|------------|-------------------|-----------|----------------------|
| DAS        | EBS (gp3, io2)    | Block     | EC2 인스턴스 디스크  |
| DAS (NVMe) | Instance Store    | Block     | 임시, 고성능 캐시    |
| SAN        | EBS io2 Block Exp | Block     | 다중 EC2 공유 블록   |
| NAS (NFS)  | EFS               | File      | 다중 EC2/EKS 공유    |
| NAS (SMB)  | FSx for Windows   | File      | Windows 파일 공유    |
| Object     | S3                | Object    | 백업, 아카이브, 정적 |

### 클라우드 스토리지 선택

| 시나리오              | AWS             | 이유                        |
|-----------------------|-----------------|-----------------------------|
| EC2 OS/DB 디스크      | EBS gp3         | 범용, IOPS/처리량 독립 설정 |
| 고성능 DB (IOPS 보장) | EBS io2         | 64,000 IOPS, 99.999% SLA    |
| 여러 EC2 파일 공유    | EFS             | NFS v4, Auto scaling        |
| K8s PV (EKS)          | EBS CSI/EFS CSI | Pod 단위 또는 공유          |
| 백업/아카이브         | S3 + Glacier    | 저비용, 내구성 11 nines     |
| Windows 파일 서버     | FSx for Windows | AD 통합, SMB                |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 트러블슈팅

### 스토리지 성능 저하

```bash
# I/O 지연 확인
sudo iostat -xdm 1 5

# 디스크별 latency (await > 10ms 주의)
sudo iostat -x | awk 'NR>3 && $NF>0 {print $1, "await="$10"ms", "util="$NF"%"}'

# I/O 대기 프로세스
sudo iotop -oP

# 블록 디바이스 큐 상태
cat /sys/block/sda/queue/nr_requests
cat /sys/block/sda/stat
```

### Multipath 장애

```bash
# multipath 상태 확인 (failed path 탐지)
sudo multipath -ll

# 경로 복구
sudo multipathd reconfigure

# 특정 경로 상태
sudo multipathd show paths
```

### iSCSI 연결 문제

```bash
# 세션 상태 확인
sudo iscsiadm -m session -P 3

# 타겟 재탐색
sudo iscsiadm -m discovery -t sendtargets -p 192.0.2.1

# 세션 재연결
sudo iscsiadm -m node -T iqn.2026-01.com.storage:lun0 -p 192.0.2.1 --logout
sudo iscsiadm -m node -T iqn.2026-01.com.storage:lun0 -p 192.0.2.1 --login
```

### NFS 마운트 문제

```bash
# NFS 서버 export 확인
showmount -e 192.0.2.1

# NFS 클라이언트 상태
nfsstat -c

# stale file handle 해결
sudo umount -f /mnt/nfs
sudo mount -t nfs -o vers=4 192.0.2.1:/share/data /mnt/nfs

# NFS 지연 확인
time dd if=/mnt/nfs/testfile of=/dev/null bs=1M count=100
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- SNIA Storage Architecture: [snia.org](https://www.snia.org/) — ★★☆☆☆
- Linux SCSI/Multipath: [docs.kernel.org/scsi](https://docs.kernel.org/scsi/) — ★★★☆☆
- NetApp ONTAP Documentation: [docs.netapp.com](https://docs.netapp.com/) — ★★★☆☆
- AWS Storage Services: [docs.aws.amazon.com](https://docs.aws.amazon.com/whitepapers/latest/aws-storage-services-overview/aws-storage-services-overview.html) — ★★★☆☆
- Patterson, David. "A Case for Redundant Arrays of Inexpensive Disks (RAID)" (1988)
- [linux_filesystem.md](../../01_fundamentals/linux/linux_filesystem.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-24

**마지막 업데이트**: 2026-07-24

© 2026 siasia86. Licensed under CC BY 4.0.

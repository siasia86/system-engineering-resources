# Windows Server 핵심 개념

<!-- reference: _reference/windows_server_concepts_notes.md -->

Windows Server 운영에 필요한 핵심 기술 개념을 정리합니다.
에디션·라이선스 비교는 [windows_server_editions_licensing.md](./windows_server_editions_licensing.md)를 참고합니다.

## 목차

| 섹션                                                                         |
|------------------------------------------------------------------------------|
| [1. 스토리지](#1-스토리지) / [2. 보안](#2-보안) / [3. 네트워크](#3-네트워크) |
| [4. 가상화](#4-가상화) / [5. 운영](#5-운영) / [6. 라이선스](#6-라이선스)     |
| [7. Active Directory (AD)](#7-active-directory-ad)                           |

---

## 전체 개념 인덱스

| 섹션     | 용어                                                                    |
|----------|-------------------------------------------------------------------------|
| 스토리지 | [Storage Spaces](#storage-spaces)                                       |
| 스토리지 | [Storage Spaces Direct (S2D)](#storage-spaces-direct-s2d)               |
| 스토리지 | [Cluster Shared Volume (CSV)](#cluster-shared-volume-csv)               |
| 스토리지 | [Failover Clustering](#failover-clustering)                             |
| 스토리지 | [Quorum](#쿼럼-quorum-개념)                                             |
| 스토리지 | [Storage Replica](#storage-replica)                                     |
| 보안     | [vTPM](#vtpm-virtual-trusted-platform-module)                           |
| 보안     | [BitLocker](#bitlocker)                                                 |
| 보안     | [Secure Boot](#secure-boot)                                             |
| 보안     | [Generation 1 vs 2 VM](#generation-1-vs-generation-2-vm)                |
| 보안     | [Shielded VM](#shielded-vm-보호된-가상-머신)                            |
| 보안     | [Host Guardian Service (HGS)](#host-guardian-service-hgs)               |
| 네트워크 | [SDN](#sdn-software-defined-networking)                                 |
| 네트워크 | [Network Controller](#network-controller)                               |
| 네트워크 | [Software Load Balancer (SLB)](#software-load-balancer-slb)             |
| 네트워크 | [RAS Gateway](#ras-gateway)                                             |
| 가상화   | [Hyper-V 컨테이너 격리 모드](#hyper-v-컨테이너-격리-모드)               |
| 가상화   | [AVMA](#avma-automatic-virtual-machine-activation)                      |
| 운영     | [SDDC](#sddc-software-defined-datacenter)                               |
| 운영     | [Hotpatch](#hotpatch)                                                   |
| 운영     | [Server Core vs Desktop Experience](#server-core-vs-desktop-experience) |
| 라이선스 | [Volume License 유형](#volume-license-유형)                             |
| 라이선스 | [Software Assurance (SA)](#software-assurance-sa)                       |
| 라이선스 | [CAL](#cal-client-access-license-상세)                                  |
| 라이선스 | [External Connector](#external-connector-상세)                          |
| AD       | [Forest / Domain / OU](#논리-구조)                                      |
| AD       | [Domain Controller / RODC / GC](#물리-구조)                             |
| AD       | [FSMO 5개 역할](#fsmo-flexible-single-master-operation-역할)            |
| AD       | [Kerberos / NTLM](#인증-프로토콜)                                       |
| AD       | [GPO](#gpo-group-policy-object)                                         |

[⬆ 목차로 돌아가기](#목차)

---

## 1. 스토리지

### Storage Spaces

물리 디스크 여러 개를 묶어 하나의 논리 볼륨으로 사용하는 소프트웨어 기반 스토리지 기능입니다.
별도의 하드웨어 RAID 컨트롤러 없이 Windows Server 자체에서 RAID와 유사한 기능을 제공합니다.

```
[HDD 1] [HDD 2] [HDD 3] [SSD 1]
    └──────────┬──────────┘
          Storage Pool
               │
     ┌──────────────────┐
     │   Virtual Disk   │
     │ (Mirror / Parity)│
     └──────────────────┘
               │
          Volume (drive letter)
```

| 항목        | 내용                                                     |
|-------------|----------------------------------------------------------|
| 에디션      | Standard · Datacenter 모두 지원                          |
| 복원력      | Simple(RAID 0), Mirror(RAID 1/10), Parity(RAID 5/6)      |
| 디스크 유형 | HDD, SSD, NVMe 혼용 가능 (티어링으로 자동 배치)          |
| 관리 도구   | Windows Admin Center, PowerShell (`Get-StoragePool`)     |
| S2D와 차이  | Storage Spaces = 단일 서버용, S2D = 다중 서버 클러스터용 |

#### 복원력 유형

| 유형             | 최소 디스크 | 내용                                | 유효 용량 |
|------------------|-------------|-------------------------------------|-----------|
| Simple           | 1개         | 스트라이핑 (장애 보호 없음)         | 100%      |
| Two-way Mirror   | 2개         | 양방향 미러링, 1개 디스크 장애 허용 | ~50%      |
| Three-way Mirror | 3개         | 삼방향 미러링, 2개 디스크 장애 허용 | ~33%      |
| Single Parity    | 3개         | RAID 5 유사, 1개 디스크 장애 허용   | ~67%      |
| Dual Parity      | 4개 이상    | RAID 6 유사, 2개 디스크 장애 허용   | 50~80%    |

---

### Storage Spaces Direct (S2D)

Storage Spaces를 **클러스터 전체**로 확장한 기능입니다. 각 서버의 내장 디스크를 클러스터 공유 스토리지로 사용해 별도의 SAN/NAS 없이 HCI(Hyper-Converged Infrastructure)를 구성합니다.

```
┌──────────────────────────────────────────────────────────┐
│              S2D Cluster (4-node example)                │
│                                                          │
│  [Node 1]    [Node 2]    [Node 3]    [Node 4]            │
│  NVMe/SSD    NVMe/SSD    NVMe/SSD    NVMe/SSD            │
│  HDD x 4     HDD x 4     HDD x 4     HDD x 4             │
│      │           │           │           │               │
│      └──────────S2D Storage Pool─────────┘               │
│                       │                                  │
│              Cluster Shared Volume (CSV)                 │
│                       │                                  │
│         Hyper-V VMs use CSV as shared storage            │
└──────────────────────────────────────────────────────────┘
```

| 항목          | 내용                                                   |
|---------------|--------------------------------------------------------|
| 에디션        | **Datacenter만** (Standard 불가)                       |
| 최소 노드     | 2대 (권장 4대 이상)                                    |
| 캐시 계층     | NVMe/SSD → 캐시, HDD → 용량 계층 (자동 티어링)         |
| 네트워크      | RDMA 지원 NIC 권장 (iWARP 또는 RoCE)                   |
| 외장 스토리지 | 불필요 (내장 디스크만 사용)                            |
| 관리          | Windows Admin Center, PowerShell (`Enable-ClusterS2D`) |
| 사용 예       | Azure Stack HCI, 프라이빗 클라우드, VDI 환경           |

#### S2D 캐시 동작 방식

```
쓰기 요청
    │
    ▼
[NVMe/SSD 캐시]  ← 빠른 임시 저장
    │
    ▼ (비동기 드레인)
[HDD 용량 계층]  ← 영구 저장

읽기 요청
    │
    ├── 캐시 히트 → [NVMe/SSD]에서 바로 반환
    └── 캐시 미스 → [HDD]에서 읽고 캐시에 올림
```

🟡 S2D는 Storage Spaces의 확장이므로 Mirror/Parity 복원력 유형이 동일하게 적용됩니다.

🟡 Dual Parity의 "4개 이상"은 fault domain(S2D에서는 서버 노드) 기준입니다. 단일 서버 Storage Spaces에서는 디스크 수 기준이 다를 수 있습니다.

---

### Cluster Shared Volume (CSV)

Failover Cluster의 여러 노드가 **동시에 하나의 볼륨에 읽기/쓰기**할 수 있게 하는 클러스터 파일 시스템입니다.

```
일반 클러스터 볼륨
  → 소유 노드(Owner Node) 1대만 접근 가능
  → 다른 노드는 네트워크를 경유(redirected I/O)

CSV
  → 모든 노드가 직접 접근 가능 (direct I/O)
  → VM 라이브 마이그레이션 중에도 I/O 중단 없음
```

| 항목       | 내용                                                       |
|------------|------------------------------------------------------------|
| 에디션     | Standard · Datacenter 모두 지원 (Failover Cluster 포함 시) |
| 파일시스템 | NTFS 또는 ReFS 위에 구성                                   |
| 주요 용도  | Hyper-V VM 스토리지, Scale-Out File Server                 |
| 특징       | 노드 간 볼륨 소유권 이전 없이 Failover 가능                |
| S2D와 관계 | S2D 클러스터는 CSV를 기반으로 동작                         |

🟡 ReFS로 CSV 구성 시 **redirected mode**로 동작합니다 — 모든 쓰기가 coordinator 노드를 경유하므로 Direct I/O 이점이 상실됩니다. Hyper-V VM 스토리지에는 NTFS 권장합니다.

---

### Failover Clustering

여러 서버(노드)가 클러스터를 구성해 한 노드 장애 시 다른 노드가 자동으로 역할을 이어받는 **고가용성(HA)** 기능입니다.

```
정상 상태
  [Node A] Active ──서비스──> 클라이언트
  [Node B] Standby

Node A 장애 발생
  [Node A] ✗
  [Node B] Active ──서비스──> 클라이언트  (자동 failover)
```

| 항목       | 내용                                                        |
|------------|-------------------------------------------------------------|
| 에디션     | Standard · Datacenter 모두 지원                             |
| 최소 노드  | 2대                                                         |
| 쿼럼       | 클러스터 결정 투표 (노드 과반수 또는 디스크/파일 공유 감시) |
| 스토리지   | 공유 SAN/iSCSI 또는 S2D                                     |
| 주요 역할  | Hyper-V, SQL Server, 파일 서버, DFS                         |
| S2D와 관계 | S2D는 Failover Cluster 위에서 동작 (스토리지 레이어)        |

#### 쿼럼 (Quorum) 개념

```
쿼럼: 클러스터가 동작 결정을 내리는 데 필요한 "투표 과반수"

2노드 클러스터:
  Node A (1표) + Node B (1표) = 2표
  → 한 노드 장애 시 1표만 남음 (과반수 미달 → 클러스터 중단)
  → 해결: 파일 공유 감시(File Share Witness) 추가 → 3표 중 2표 확보

4노드 클러스터:
  Node A + B + C + D = 4표
  → 2개 노드 동시 장애 시에도 2표 남음 (과반수 확보 → 클러스터 유지)
```

🟡 2노드 클러스터는 반드시 **쿼럼 감시(Witness)** 를 설정해야 합니다.

---

### Storage Replica

서버 또는 클러스터 간 볼륨을 **블록 단위로 복제**하는 재해복구(DR) 기능입니다. 스토리지 벤더 독립적으로 동작합니다.

| 항목      | 내용                                                              |
|-----------|-------------------------------------------------------------------|
| 에디션    | Standard: 1볼륨 + 2TB 제한 / **Datacenter: 무제한**               |
| 복제 방식 | 동기(Synchronous): RPO=0, 비동기(Asynchronous): 지연 허용         |
| 대상      | 서버↔서버, 클러스터↔클러스터, 사이트 간 DR                        |
| 요구 사항 | 전용 로그 볼륨 필요, 별도 네트워크 권장                           |
| 장애조치  | Storage Replica 자체는 자동 Failover 없음 → Failover Cluster 조합 |

```
동기 복제 (Synchronous)
  쓰기 요청 → [원본] → 네트워크 → [복제본 확인] → 완료 응답
  RPO = 0 (데이터 손실 없음), 단 네트워크 지연이 성능에 영향

비동기 복제 (Asynchronous)
  쓰기 요청 → [원본] → 즉시 완료 응답
                 └──> 백그라운드로 [복제본]에 전송
  RPO > 0 (일부 데이터 손실 가능), 장거리 사이트 간 적합
```


[⬆ 목차로 돌아가기](#목차)

---

## 2. 보안

### vTPM (Virtual Trusted Platform Module)

물리 서버의 TPM 칩을 가상 머신 내부에서 에뮬레이션하는 기능입니다. Shielded VM의 핵심 구성 요소입니다.

```
물리 서버
  └── [Hyper-V 하이퍼바이저]
        └── [VM]
              └── vTPM  ← 물리 TPM처럼 동작하는 가상 칩
                    └── BitLocker 키 보관
                    └── 플랫폼 측정값(PCR) 저장
                    └── 보안 부팅 검증
```

| 항목     | 내용                                                        |
|----------|-------------------------------------------------------------|
| 에디션   | Standard · Datacenter 모두 지원 (Generation 2 VM에서만)     |
| 용도     | BitLocker 드라이브 암호화, Shielded VM, Windows Hello       |
| 물리 TPM | 호스트에 물리 TPM 2.0 불필요 (vTPM은 소프트웨어 에뮬레이션) |
| 키 보호  | VM 키 관리자(Key Protector)로 vTPM 키 암호화 보관           |

---

### BitLocker

드라이브 전체를 암호화하는 Windows 기본 제공 기능입니다. 서버에서는 OS 볼륨 및 데이터 볼륨 모두 암호화에 사용됩니다.

| 항목        | 내용                                                         |
|-------------|--------------------------------------------------------------|
| 암호화 방식 | AES-128 또는 AES-256 (XTS-AES 모드)                          |
| 키 보관     | TPM, TPM+PIN, TPM+USB, USB 키만, 암호                        |
| Shielded VM | VM 디스크 암호화에 BitLocker 사용 (vTPM이 키 보관)           |
| 관리        | `manage-bde`, PowerShell `Enable-BitLocker`, AD 키 백업 가능 |

```
BitLocker 보호 흐름 (TPM 사용 시)
  부팅
    │
    ▼
  TPM이 부팅 측정값 확인
    │
    ├── 측정값 일치 → 볼륨 키 해제 → 정상 부팅
    └── 측정값 불일치 (디스크 이동/부팅 변조) → 복구 키 요구
```

---

### Secure Boot

UEFI 펌웨어 레벨에서 부팅 로더의 **디지털 서명을 검증**하는 보안 기능입니다. 승인되지 않은 OS나 부트킷(bootkit)이 로드되는 것을 차단합니다.

| 항목        | 내용                                    |
|-------------|-----------------------------------------|
| 동작 위치   | UEFI 펌웨어 (OS 로드 전 단계)           |
| VM 적용     | Generation 2 VM에서만 사용 가능         |
| Shielded VM | Secure Boot 활성화 필수 조건            |
| 서명 DB     | `db` (허용), `dbx` (차단) 목록으로 관리 |

---

### Generation 1 vs Generation 2 VM

Hyper-V에서 VM 생성 시 선택하는 두 가지 하드웨어 세대입니다. 생성 후 변경 불가입니다.

| 항목          | Generation 1     | Generation 2                     |
|---------------|------------------|----------------------------------|
| 펌웨어        | BIOS (레거시)    | **UEFI**                         |
| Secure Boot   | ❌               | ✅                               |
| vTPM          | ❌               | ✅                               |
| Shielded VM   | ❌ 불가          | ✅ 필수 조건                     |
| 부팅 디스크   | IDE 컨트롤러     | SCSI 컨트롤러                    |
| 네트워크 부팅 | PXE (레거시 NIC) | PXE (합성 NIC)                   |
| 지원 OS       | 구형 포함 전체   | Windows Server 2012+, Linux 일부 |
| 권장 여부     | 구형 OS 필요 시  | **신규 VM 기본 권장**            |

🟡 Generation 2 VM은 생성 후 Generation 1으로 변경 불가입니다. 신규 VM은 특별한 이유 없으면 Generation 2를 선택합니다.

---

### Shielded VM (보호된 가상 머신)

악의적인 Hyper-V 관리자나 침해된 호스트로부터 VM을 보호하는 Datacenter 전용 기능입니다.

```
일반 Hyper-V 환경
  호스트 관리자
    └── VM 디스크 파일 직접 접근 가능
    └── VM 메모리 덤프 가능
    └── VM 스냅샷 복사 가능

Shielded VM 환경
  호스트 관리자
    └── VM 디스크 → BitLocker 암호화 (접근 불가)
    └── VM 기동 → HGS 승인 필요
    └── 미승인 호스트에서 기동 시도 → 거부
```

#### Shielded VM 구성 요소

| 구성 요소                         | 역할                                                           |
|-----------------------------------|----------------------------------------------------------------|
| **Host Guardian Service (HGS)**   | 어떤 호스트가 신뢰할 수 있는지 증명·승인하는 서비스            |
| **Guarded Host**                  | HGS로부터 승인받아 Shielded VM을 실행할 수 있는 Hyper-V 호스트 |
| **Shielded VM**                   | vTPM + BitLocker + Secure Boot로 보호된 Generation 2 VM        |
| **Shielding Data File (.PDK)**    | VM 암호화 키, RDP 인증서, 관리자 암호 등을 암호화 보관         |
| **Template Disk (서명된 디스크)** | 신뢰할 수 있는 OS 디스크 (서명 검증으로 변조 감지)             |

#### 동작 흐름

```
1. HGS 구성
   └── 신뢰할 수 있는 호스트 등록 (AD 기반 또는 TPM 기반 증명)

2. Shielded VM 배포 요청
   └── 호스트 → HGS에 증명 요청
         ├── 증명 성공 → 키 해제 → VM 기동 허용
         └── 증명 실패 → VM 기동 거부

3. VM 실행 중
   └── 디스크: BitLocker 암호화 (vTPM 키 보관)
   └── 메모리: 암호화 (호스트 관리자 접근 불가)
```

| 항목      | 내용                                                     |
|-----------|----------------------------------------------------------|
| 에디션    | Shielded VM **호스트**: Datacenter만 / 게스트: 제한 없음 |
| 전제 조건 | Generation 2 VM, HGS 인프라 구성 필요                    |
| 증명 방식 | AD 기반(Admin-trusted) 또는 TPM 기반(TPM-trusted)        |
| 보호 대상 | 악의적 내부자, 침해된 패브릭, VM 도난                    |

---

### Host Guardian Service (HGS)

Shielded VM 인프라의 핵심 서비스입니다. 호스트가 신뢰할 수 있는 상태인지 증명하고, 증명된 호스트에만 VM 복호화 키를 제공합니다.

```
┌───────────────────────────────────────────────────────┐
│                    HGS Cluster                        │
│                                                       │
│  [Attestation Service]     [Key Protection Service]   │
│  Verify host health        Provide / deny VM keys     │
└───────────────────────────┬───────────────────────────┘
                            │
          ┌─────────────────┴─────────────────┐
          │                                   │
   [Guarded Host A]                   [Guarded Host B]
   Attestation OK -> VM start OK      Attestation FAIL -> VM blocked
```

| 항목      | 내용                                              |
|-----------|---------------------------------------------------|
| 구성      | 최소 2대 이상 HGS 서버 (HA 구성 권장)             |
| 증명 모드 | TPM 기반 (보안 강도 높음) / AD 기반 (구축 간편)   |
| 독립 배치 | 별도 AD 포리스트에 배치 권장 (관리 도메인과 분리) |


[⬆ 목차로 돌아가기](#목차)

---

## 3. 네트워크

### SDN (Software-Defined Networking)

네트워크 장비(스위치·라우터·방화벽)의 제어 로직을 소프트웨어로 분리하여 **중앙에서 프로그래밍 방식으로 관리**하는 개념입니다. Windows Server에서는 Network Controller, Software Load Balancer, RAS Gateway 세 가지 구성 요소로 구현합니다.

```
전통적 네트워크                    SDN
  물리 스위치 A                  [Network Controller]
  → 장비별 CLI 설정               API (중앙 제어)
  물리 스위치 B                       │
  → 장비별 CLI 설정              ┌────┴────┐
  변경 시: 장비마다 직접 접속    vSwitch A  vSwitch B
                                 소프트웨어로 일괄 제어
```

| 항목      | 내용                                                |
|-----------|-----------------------------------------------------|
| 에디션    | **Datacenter만** (3개 구성 요소 모두)               |
| 주요 이점 | 네트워크 변경 자동화, 멀티테넌트 격리, 정책 일관성  |
| 사용 예   | 대규모 데이터센터, 호스팅 서비스, 프라이빗 클라우드 |

---

### Network Controller

SDN의 핵심 관리 구성 요소입니다. 데이터센터 내 가상·물리 네트워크 인프라를 중앙에서 구성·모니터링·자동화합니다.

```
[관리자 / 오케스트레이터]
        │ REST API
        ▼
[Network Controller 클러스터]
        │
   ┌────┴────────────────────────┐
   │                             │
[Hyper-V vSwitch 정책]    [물리 네트워크 장비]
   │                             │
[VM 가상 네트워크]         [SDN 호환 스위치]
```

| 항목       | 내용                                                    |
|------------|---------------------------------------------------------|
| 에디션     | **Datacenter만**                                        |
| 구성       | 최소 3 VM 권장 (HA), 물리 호스트 배포 금지·전용 VM 필수 |
| 관리 대상  | 가상 네트워크, ACL, QoS, vSwitch 정책, 물리 네트워크    |
| 인터페이스 | REST API (Windows Admin Center, SCVMM, PowerShell)      |

---

### Software Load Balancer (SLB)

하드웨어 로드밸런서 없이 소프트웨어로 트래픽을 분산하는 SDN 구성 요소입니다.

```
외부 클라이언트
      │
      ▼
[SLB Multiplexer (MUX)]  ← VIP(가상 IP) 수신
      │
      ├──> VM 1 (DIP: 10.0.0.1)
      ├──> VM 2 (DIP: 10.0.0.2)
      └──> VM 3 (DIP: 10.0.0.3)
```

| 항목      | 내용                                              |
|-----------|---------------------------------------------------|
| 에디션    | **Datacenter만**                                  |
| 지원 방식 | North-South (외부↔내부), East-West (내부 서버 간) |
| VIP       | 가상 IP (외부 노출), DIP: 실제 VM IP              |
| 프로토콜  | TCP, UDP                                          |

---

### RAS Gateway

SDN 환경에서 가상 네트워크와 물리 네트워크(또는 외부 네트워크) 간의 **게이트웨이 역할**을 하는 구성 요소입니다.

| 항목       | 내용                                                      |
|------------|-----------------------------------------------------------|
| 에디션     | **Datacenter만**                                          |
| 기능       | Site-to-Site VPN, Point-to-Site VPN, GRE 터널, BGP 라우팅 |
| 멀티테넌트 | 테넌트별 격리된 VPN/라우팅 정책 지원                      |
| 사용 예    | 온프레미스 ↔ 클라우드 연결, 테넌트 간 네트워크 격리       |


[⬆ 목차로 돌아가기](#목차)

---

## 4. 가상화

### Hyper-V 컨테이너 격리 모드

Windows 컨테이너는 두 가지 격리 방식으로 실행됩니다.

```
Process 격리 (기본)
  [호스트 OS 커널]
      ├── [컨테이너 A] (커널 공유)
      ├── [컨테이너 B] (커널 공유)
      └── [컨테이너 C] (커널 공유)
  가볍고 빠름, 커널 취약점이 모든 컨테이너에 영향

Hyper-V 격리
  [호스트 OS 커널]
      ├── [경량 VM] → [컨테이너 A] (전용 커널)
      ├── [경량 VM] → [컨테이너 B] (전용 커널)
      └── [경량 VM] → [컨테이너 C] (전용 커널)
  무겁지만 강한 격리, VM 수준 보안 경계
```

| 항목              | Process 격리          | Hyper-V 격리                    |
|-------------------|-----------------------|---------------------------------|
| 커널              | 호스트와 공유         | 전용 경량 VM 커널               |
| 성능 오버헤드     | 낮음                  | 높음 (VM 기동 시간 포함)        |
| 보안 경계         | 프로세스 수준         | **VM 수준** (강한 격리)         |
| Standard 에디션   | 무제한                | **2개 제한** (VM 카운트와 동일) |
| Datacenter 에디션 | 무제한                | 무제한                          |
| 실행 명령         | `--isolation process` | `--isolation hyperv`            |

```bash
# Process 격리로 실행
docker run --isolation process mcr.microsoft.com/windows/servercore:ltsc2022

# Hyper-V 격리로 실행
docker run --isolation hyperv mcr.microsoft.com/windows/servercore:ltsc2022
```

🟡 Standard에서 Hyper-V 격리 컨테이너가 2개로 제한되는 이유: 각 컨테이너가 전용 경량 VM을 사용하므로 게스트 VM 카운트와 동일하게 취급됩니다.

### Windows 컨테이너 격리 구현 — Linux 대응 개념

Linux 컨테이너가 namespace + cgroups로 격리를 구현하듯, Windows 컨테이너도 동일한 역할을 하는 자체 구현체를 사용합니다.

#### Linux vs Windows 격리 기술 대응표

| 역할            | Linux                              | Windows (Process 격리)                   |
|-----------------|------------------------------------|------------------------------------------|
| 프로세스 격리   | PID namespace (`CLONE_NEWPID`)     | Job Object + Silo                        |
| 파일시스템 격리 | mount namespace + overlay FS       | Windows Container Isolation FS (WCIFS)   |
| 네트워크 격리   | network namespace (`CLONE_NEWNET`) | Host Networking Service (HNS)            |
| 사용자 격리     | user namespace (`CLONE_NEWUSER`)   | Object Manager namespace                 |
| 리소스 제한     | cgroups (v1/v2)                    | Job Object (CPU·메모리·프로세스 수 제한) |
| 레지스트리 격리 | 없음 (Linux 개념 아님)             | Registry namespace (Windows 고유)        |
| 루트 파일시스템 | union mount (overlay2)             | Layer Storage (계층형 이미지)            |

> 출처: learn.microsoft.com/en-us/virtualization/windowscontainers/manage-containers/hyperv-container
> "With process isolation, multiple container instances run concurrently on a given host
> with isolation provided through namespace, resource control, and other process isolation
> technologies. This is approximately the same as how Linux containers run."

#### Windows namespace 격리 대상 (Process 격리)

공식 문서에 명시된 격리 항목:

```
격리되는 namespace
  ├── file system          (Linux: mount namespace)
  ├── registry             (Windows 고유)
  ├── network ports        (Linux: network namespace)
  ├── process/thread ID    (Linux: PID namespace)
  └── Object Manager namespace
```

#### Job Object — Windows의 cgroups 대응

> "A job object allows groups of processes to be managed as a unit.
> Examples include enforcing limits such as working set size and process priority
> or terminating all processes associated with a job."

```
Linux cgroups               Windows Job Object
  ├── cpu (CPU 시간 제한)   ←→  CPU rate limit
  ├── memory (메모리 제한)  ←→  Working set size limit
  ├── pids (프로세스 수)    ←→  Active process limit
  └── blkio (I/O 제한)      ←→  I/O rate limit (SetIoRateControlInformationJobObject)
```

#### HNS (Host Networking Service)

Linux의 network namespace + veth pair에 대응하는 Windows 컨테이너 네트워크 구현체입니다.

```
[컨테이너 A]     [컨테이너 B]
    │                │
  vNIC            vNIC        (각 컨테이너 전용 가상 NIC)
    │                │
    └──── HNS (가상 스위치) ────┘
                │
          호스트 물리 NIC
```

| 항목               | Linux                    | Windows                       |
|--------------------|--------------------------|-------------------------------|
| 네트워크 격리 구현 | network namespace + veth | HNS + vNIC                    |
| 관리 서비스        | 커널 내장                | Host Networking Service (HNS) |
| 연동 서비스        | containerd / runc        | Host Compute Service (HCS)    |

#### Hyper-V 격리 — 경량 VM 구조

Process 격리와 달리 각 컨테이너가 전용 경량 Hyper-V VM 안에서 실행됩니다. namespace/cgroups가 아닌 하드웨어 수준 격리입니다.

```
Process isolation (namespace)          Hyper-V isolation (VM)
┌──────────────────────────────┐       ┌──────────────────────────────┐
│   Host Windows Kernel        │       │   Host Windows Kernel        │
│  ┌────────┐  ┌────────┐      │       │  ┌───────────────────────┐   │
│  │ App A  │  │ App B  │      │       │  │  Lightweight VM       │   │
│  │ (Silo) │  │ (Silo) │      │       │  │  ┌─────────────────┐  │   │
│  └────────┘  └────────┘      │       │  │  │ Dedicated Kernel│  │   │
│  shared kernel, ns isolation │       │  │  │  App A          │  │   │
└──────────────────────────────┘       │  │  └─────────────────┘  │   │
                                       │  └───────────────────────┘   │
                                       │  hardware-level isolation    │
                                       └──────────────────────────────┘
```

🟡 Windows Process 격리는 Linux 컨테이너와 동일한 원리(namespace + 리소스 제한)를 사용하지만, 구현체 이름이 다릅니다. Hyper-V 격리는 namespace가 아닌 VM으로 격리하므로 완전히 다른 접근법입니다.


---

### AVMA (Automatic Virtual Machine Activation)

Datacenter 에디션 호스트가 게스트 VM을 **인터넷 연결 없이 자동으로 활성화**하는 기능입니다.

```
[Datacenter 호스트] (활성화 완료)
      │
      ├── [게스트 VM: Standard]    → AVMA 자동 활성화
      ├── [게스트 VM: Datacenter]  → AVMA 자동 활성화
      └── [게스트 VM: Essentials]  → AVMA 자동 활성화
```

| 항목             | 내용                                                           |
|------------------|----------------------------------------------------------------|
| 호스트 에디션    | **Datacenter만** (Standard 호스트는 AVMA 제공 불가)            |
| 게스트 에디션    | Standard, Datacenter, Essentials 모두 활성화 가능              |
| 버전 조건        | 호스트 버전 ≥ 게스트 버전 (예: 2022 호스트 → 2019 게스트 가능) |
| 인터넷           | 불필요 (에어갭 환경에서도 동작)                                |
| Failover Cluster | 모든 노드가 Datacenter이고 활성화되어 있어야 함                |
| AVMA 키          | 게스트에 AVMA 전용 키(`slmgr /ipk <AVMA키>`) 입력 필요         |

#### AVMA 키

> 출처: learn.microsoft.com/en-us/windows-server/get-started/automatic-vm-activation

| 호스트 버전 | 게스트 에디션             | AVMA 키                       |
|-------------|---------------------------|-------------------------------|
| 2025        | Datacenter                | YQB4H-NKHHJ-Q6K4R-4VMY6-VCH67 |
| 2025        | Datacenter: Azure Edition | 6NMQ9-T38WF-6MFGM-QYGYM-88J4F |
| 2025        | Standard                  | WWVGQ-PNHV9-B89P4-8GGM9-9HPQ4 |
| 2022        | Datacenter                | W3GNR-8DDXR-2TFRP-H8P33-DV9BG |
| 2022        | Datacenter: Azure Edition | F7TB6-YKN8Y-FCC6R-KQ484-VMK3J |
| 2022        | Standard                  | YDFWN-MJ9JR-3DYRK-FXXRW-78VHK |
| 2019        | Datacenter                | H3RNG-8C32Q-Q8FRX-6TDXV-WMBMW |
| 2019        | Standard                  | TNK62-RXVTB-4P47B-2D623-4GF74 |
| 2019        | Essentials                | 2CTP7-NHT64-BP62M-FV6GG-HFV28 |

🟡 AVMA 키는 활성화 목적으로만 사용됩니다. 라이선스 구매 의무는 별도입니다.


[⬆ 목차로 돌아가기](#목차)

---

## 5. 운영

### SDDC (Software-Defined Datacenter)

컴퓨트·스토리지·네트워크를 모두 소프트웨어로 정의하고 자동화하는 데이터센터 아키텍처 개념입니다. 하나의 설치 기능이 아니라 Datacenter 에디션의 여러 기능을 조합해 구현합니다.

```
┌─────────────────────────────────────────────────────────────┐
│                   SDDC (conceptual layout)                  │
│                                                             │
│  Compute layer       Storage layer      Network layer       │
│  ┌───────────────┐   ┌──────────────┐   ┌─────────────┐     │
│  │ Hyper-V       │   │ S2D          │   │ SDN         │     │
│  │ (run VMs)     │   │ (distributed │   │ (virtual    │     │
│  │               │   │  storage)    │   │  network)   │     │
│  └───────────────┘   └──────────────┘   └─────────────┘     │
│         │                  │                   │            │
│         └──────────────────┴───────────────────┘            │
│                       Failover Cluster                      │
│                    (HA orchestration)                       │
└─────────────────────────────────────────────────────────────┘
```

| 구성 요소        | 기능              | 에디션                |
|------------------|-------------------|-----------------------|
| Hyper-V          | 컴퓨트 가상화     | Standard · Datacenter |
| S2D              | 스토리지 가상화   | **Datacenter만**      |
| SDN              | 네트워크 가상화   | **Datacenter만**      |
| Failover Cluster | HA 오케스트레이션 | Standard · Datacenter |

🟡 SDDC 구현(S2D + SDN 포함)은 Datacenter 에디션 필수입니다. Standard는 Hyper-V + Failover Cluster까지만 구성 가능합니다.

---

### Hotpatch

재부팅 없이 보안 패치를 적용하는 기능입니다. 실행 중인 프로세스의 **메모리 코드를 직접 패치**하여 서비스 중단을 최소화합니다.

```
일반 패치 주기
  1월  2월  3월  4월  5월  6월
  [기본] [Hot] [Hot] [기본] [Hot] [Hot]
   재부팅  없음  없음  재부팅  없음  없음

기본 업데이트(분기별): 새 Hotpatch 기준선 설정, 재부팅 필요
Hotpatch(월별): 기준선 위에 메모리 패치, 재부팅 불필요
```

| 항목        | 내용                                                                                                      |
|-------------|-----------------------------------------------------------------------------------------------------------|
| 에디션      | Azure VM/Azure Local: **Datacenter: Azure Edition** / Azure Arc on-premises: **2025 Datacenter·Standard** |
| 환경        | Azure VM, Azure Local (2022·2025), Azure Arc 연결 on-premises (2025만 지원)                               |
| 패치 범위   | Critical·Important 등급 Windows 보안 업데이트                                                             |
| 재부팅 주기 | 월별 패치 기준 최대 12회 → 분기별 baseline 4회로 감소                                                     |
| 이점        | 패치 적용 시간 단축, 서비스 가용성 향상                                                                   |

---

### Server Core vs Desktop Experience

Windows Server 설치 시 선택하는 두 가지 옵션입니다.

```
Server Core                      Desktop Experience
  ┌──────────────────┐           ┌──────────────────────┐
  │  CLI only        │           │  GUI + CLI           │
  │  (PowerShell,    │           │  (Explorer, MMC,     │
  │   CMD, SSH)      │           │   Server Manager...) │
  └──────────────────┘           └──────────────────────┘
  Attack surface ↓               Admin convenience ↑
  Memory usage ↓                 Install size ↑
  Update count ↓                 Reboot frequency ↑
```

| 항목        | Server Core                            | Desktop Experience    |
|-------------|----------------------------------------|-----------------------|
| GUI         | ❌                                     | ✅                    |
| 메모리 절약 | 수백 MB~수 GB (역할에 따라)            | 기준                  |
| 공격 표면   | 작음 (설치 구성 요소 적음)             | 큼                    |
| 관리 방법   | PowerShell, SSH, WAC 원격              | 로컬 GUI + PowerShell |
| MS 권장     | **권장** (보안·경량화)                 | 필요한 경우에만       |
| 전환        | 재설치 없이 DISM으로 전환 가능 (2019+) | 동일                  |

```powershell
# Server Core에서 역할 설치 예시
Install-WindowsFeature -Name Web-Server -IncludeManagementTools

# Windows Admin Center로 원격 관리 (Core 환경)
# 브라우저 → WAC 게이트웨이 → Server Core 서버
```

🟡 Microsoft 공식 권장은 **Server Core**입니다. Desktop Experience는 레거시 도구 호환이 필요한 경우에만 선택합니다.


[⬆ 목차로 돌아가기](#목차)

---

## 6. 라이선스

### Volume License 유형

기업 대량 구매를 위한 라이선스 계약 방식입니다. KMS, MAK, Software Assurance와 연동됩니다.

| 유형                          | 대상                   | 계약 기간 | 특징                                     |
|-------------------------------|------------------------|-----------|------------------------------------------|
| **EA (Enterprise Agreement)** | 대기업 (500 디바이스+) | 3년       | 전사 통일 라이선스, 할인율 높음, SA 포함 |
| **EAS (EA Subscription)**     | EA와 동일              | 3년       | 구독형 EA, 계약 종료 시 사용권 없음      |
| **Open Value**                | 중소기업               | 3년       | Software Assurance 포함, 최소 5개 제품   |
| **Open Value Subscription**   | 중소기업               | 3년       | 구독형 Open Value                        |
| **Open License**              | 소규모                 | 2년       | SA 선택, 최소 5개 라이선스               |
| **Select Plus**               | 대기업 (부서별)        | 없음      | 사용량 기반, 부서별 유연 구매            |
| **MPSA**                      | 중대기업               | 1년       | 단일 계약으로 여러 MS 제품 통합          |

🟡 ESU 구매는 **EA 또는 Open Value** 계약이 있어야 Volume License 경로로 구매 가능합니다.

---

### Software Assurance (SA)

Volume License와 함께 구매하는 **유지보수·혜택 패키지**입니다. 라이선스 자체와 별도로 구매합니다.

| 혜택                 | 내용                                              |
|----------------------|---------------------------------------------------|
| 버전 업그레이드 권한 | SA 유효 기간 중 출시된 신버전으로 무상 업그레이드 |
| 배포 계획 서비스     | MS 전문가의 배포 지원                             |
| 교육 바우처          | MS 공식 교육 과정 수강권                          |
| 재해복구 권한        | DR 사이트에 수동(passive) 서버 무상 라이선스      |
| 라이선스 이동성      | 공유 서버 인프라로 라이선스 이동 허용             |
| Windows Server 혜택  | SA 보유 시 새 버전 출시 즉시 업그레이드 권한 확보 |

🟡 SA 없이 새 버전으로 업그레이드하려면 신규 라이선스를 구매해야 합니다.

---

### CAL (Client Access License) 상세

Windows Server에 **접속하는 권한**에 대한 라이선스입니다. Per Core 서버 라이선스와 별개로 구매합니다.

```
서버 라이선스 (Per Core)   → 서버를 운영할 권한
CAL                        → 그 서버에 접속할 권한

= 두 가지 모두 필요
```

#### CAL 종류 상세

| 종류                   | 기준                     | 적합한 경우                                          |
|------------------------|--------------------------|------------------------------------------------------|
| **User CAL**           | 접속 사용자 1명당        | 여러 디바이스 사용 직원 (노트북 + 모바일 + 데스크탑) |
| **Device CAL**         | 접속 디바이스 1대당      | 공유 PC (교대 근무, 매장 단말 등 1대에 여러 명 사용) |
| **External Connector** | 서버 1대당 (외부 무제한) | 파트너사·고객 등 외부 사용자 대량 접속               |

#### User CAL vs Device CAL 선택 기준

```
직원 50명, 디바이스 80대
  → User CAL 50개 < Device CAL 80개 → User CAL 선택

직원 100명, 디바이스 30대 (공장 단말, 3교대 근무)
  → User CAL 100개 > Device CAL 30개 → Device CAL 선택

외부 파트너 수백 명이 접속
  → External Connector 1개 (서버당) vs CAL 수백 개 → External Connector 고려
```

#### CAL이 필요 없는 경우

| 상황                         | 이유                               |
|------------------------------|------------------------------------|
| Essentials 에디션            | 에디션 자체에 CAL 포함 (25사용자)  |
| 인터넷 공개 서버 (익명 접속) | 불특정 다수 익명 접속은 CAL 불필요 |
| Azure 클라우드 서비스 형태   | Azure 자체 라이선스 모델 적용      |

#### External Connector 상세

외부 사용자(파트너, 고객, 계약직 등)가 서버에 접속하는 경우 개인별 CAL 대신 **서버 1대당 EC 라이선스 1개**로 무제한 외부 접속을 허용합니다.

| 항목        | CAL 방식           | External Connector       |
|-------------|--------------------|--------------------------|
| 비용 기준   | 사용자/디바이스 수 | 서버 수                  |
| 외부 사용자 | 1명당 1 CAL        | 서버 1대당 1 EC (무제한) |
| 내부 사용자 | 포함               | 별도 CAL 필요            |
| 적합 상황   | 소규모 외부 접속   | 대규모 외부 접속         |

🟡 External Connector는 외부 사용자(비직원)에 대한 접속 권한만 포함합니다. 내부 직원 접속에는 별도 CAL이 여전히 필요합니다.


[⬆ 목차로 돌아가기](#목차)

---

## 7. Active Directory (AD)

Windows Server의 디렉터리 서비스입니다. 네트워크상의 사용자·컴퓨터·리소스를 중앙에서 인증·권한 부여·관리합니다.

> "AD DS stores information about objects on the network and makes this information easy
> for administrators and users to find and use."
> — learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview

### AD DS 구성 요소

#### 논리 구조

```
Forest (최상위 보안 경계)
  └── Domain Tree
        └── Domain (보안/관리 단위)
              └── OU (Organizational Unit, 정책 적용 단위)
                    └── Object (사용자, 컴퓨터, 그룹 등)
```

| 구성 요소                    | 역할                                                          |
|------------------------------|---------------------------------------------------------------|
| **Forest**                   | AD의 최상위 보안·관리 경계. 동일 Schema와 Global Catalog 공유 |
| **Domain Tree**              | 연속된 DNS 네임스페이스를 가진 도메인 계층                    |
| **Domain**                   | 인증·정책의 기본 단위. 도메인 컨트롤러(DC)가 관리             |
| **OU (Organizational Unit)** | 도메인 내 객체 그룹. GPO 적용 단위                            |
| **Object**                   | 사용자, 컴퓨터, 그룹, 프린터 등 디렉터리에 저장되는 개체      |

#### 물리 구조

| 구성 요소                  | 역할                                                                             |
|----------------------------|----------------------------------------------------------------------------------|
| **Domain Controller (DC)** | AD DS 데이터베이스 호스팅·복제·인증 처리 서버                                    |
| **Read-Only DC (RODC)**    | 읽기 전용 DC. 지사·비신뢰 환경 배치용                                            |
| **Global Catalog (GC)**    | Forest 전체 객체의 부분 속성을 캐시. UPN 로그인·유니버설 그룹 멤버십 확인에 사용 |
| **Site**                   | 물리적 네트워크 위치 단위. 복제 트래픽 제어에 사용                               |

---

### FSMO (Flexible Single Master Operation) 역할

AD DS는 일부 작업을 단일 DC에서만 처리합니다. 이 역할을 FSMO라고 합니다.

| 범위       | FSMO 역할             | 설명                                                          |
|------------|-----------------------|---------------------------------------------------------------|
| **Forest** | Schema Master         | Schema 수정 권한 (Forest에 1개)                               |
| **Forest** | Domain Naming Master  | 도메인 추가·제거 권한 (Forest에 1개)                          |
| **Domain** | PDC Emulator          | 시간 동기화 기준, 암호 변경 즉시 반영, 레거시 클라이언트 지원 |
| **Domain** | RID Master            | 도메인 내 객체 SID 생성을 위한 RID 풀 관리                    |
| **Domain** | Infrastructure Master | 도메인 간 객체 참조(phantom) 갱신                             |

🟡 FSMO 역할 5개 중 **PDC Emulator**가 가장 중요합니다. 장애 시 시간 동기화·암호 정책에 즉시 영향이 생깁니다.

---

### 인증 프로토콜

| 프로토콜     | 사용 환경                      | 특징                                 |
|--------------|--------------------------------|--------------------------------------|
| **Kerberos** | 도메인 환경 (기본)             | 티켓 기반, 상호 인증, 안전           |
| **NTLM**     | 워크그룹, 레거시, IP 직접 접속 | Challenge-Response, 서버 신원 미검증 |

```
Kerberos 인증 흐름
  1. 클라이언트 → KDC(DC): AS-REQ (TGT 요청)
  2. KDC → 클라이언트: AS-REP (TGT 발급)
  3. 클라이언트 → KDC: TGS-REQ (서비스 티켓 요청)
  4. KDC → 클라이언트: TGS-REP (서비스 티켓 발급)
  5. 클라이언트 → 서버: AP-REQ (서비스 티켓 제시)
```

---

### GPO (Group Policy Object)

도메인·OU에 적용하는 정책 설정 모음입니다. 보안 설정, 소프트웨어 배포, 스크립트 실행 등을 중앙에서 제어합니다.

| 항목      | 내용                                                           |
|-----------|----------------------------------------------------------------|
| 적용 순서 | Local → Site → Domain → OU (하위 OU가 상위 덮어씀)             |
| 적용 대상 | 사용자 계정 또는 컴퓨터 계정                                   |
| 갱신 주기 | 기본 90분 ±30분 랜덤 오프셋 (DC: 5분), 수동: `gpupdate /force` |
| 우선순위  | Block Inheritance, Enforced(No Override) 설정으로 조정         |

---

### 주요 명령어

```powershell
# DC 정보 확인
Get-ADDomainController -Filter *

# FSMO 역할 보유 DC 확인
netdom query fsmo

# AD 복제 상태 확인
repadmin /replsummary
repadmin /showrepl

# GPO 목록 확인
Get-GPO -All | Select-Object DisplayName, GpoStatus

# GPO 강제 갱신
gpupdate /force

# 사용자 계정 조회
Get-ADUser -Filter * -Properties * | Select-Object Name, SamAccountName, Enabled

# 컴퓨터 계정 조회
Get-ADComputer -Filter * | Select-Object Name, OperatingSystem
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Microsoft: [Storage Spaces Direct overview](https://learn.microsoft.com/en-us/windows-server/storage/storage-spaces/storage-spaces-direct-overview) — ★★★☆☆
- Microsoft: [Failover Clustering overview](https://learn.microsoft.com/en-us/windows-server/failover-clustering/failover-clustering-overview) — ★★★☆☆
- Microsoft: [Guarded fabric and shielded VMs](https://learn.microsoft.com/en-us/windows-server/security/guarded-fabric-shielded-vm/guarded-fabric-and-shielded-vms) — ★★★☆☆
- Microsoft: [Software Defined Networking](https://learn.microsoft.com/en-us/windows-server/networking/sdn/software-defined-networking) — ★★★☆☆
- Microsoft: [Hotpatch for Windows Server](https://learn.microsoft.com/en-us/windows-server/get-started/hotpatch) — ★★★☆☆
- Microsoft: [Automatic VM Activation](https://learn.microsoft.com/en-us/windows-server/get-started/automatic-vm-activation) — ★★★☆☆
- Microsoft: [Client Access Licenses](https://www.microsoft.com/en-us/licensing/product-licensing/client-access-license) — ★★★☆☆
- Microsoft: [Volume Licensing overview](https://www.microsoft.com/en-us/licensing/how-to-buy/volume-licensing) — ★★★☆☆
- Microsoft: [AD DS Overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview) — ★★★☆☆
- Microsoft: [FSMO Role Placement](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/planning-operations-master-role-placement) — ★★★☆☆
- [windows_server_editions_licensing.md](./windows_server_editions_licensing.md)

---

![문서 언어](https://img.shields.io/badge/language-korean-blue)
![에디션](https://img.shields.io/badge/edition-2022%20%2F%202025-blue)

**작성일**: 2026-07-29

**마지막 업데이트**: 2026-07-31

© 2026 siasia86. Licensed under CC BY 4.0.

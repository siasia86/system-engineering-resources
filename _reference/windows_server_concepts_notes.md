---
name: windows-server-concepts-notes
description: Windows Server 핵심 개념 참조 노트. Hyper-V, Failover Cluster, S2D, Shielded VM, SDN, Storage Replica, Hotpatch, CAL, Quorum, CSV 등 주요 기술 개념 공식 정의 정리. Windows Server 개념 문서 작성/검토 시 참조.
tags:
  - windows-server
  - hyper-v
  - failover-cluster
  - s2d
  - shielded-vm
  - sdn
  - storage-replica
  - hotpatch
last_checked: 2026-07-30
sources:
  - https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/hyper-v-on-windows-server
  - https://learn.microsoft.com/en-us/windows-server/failover-clustering/failover-clustering-overview
  - https://learn.microsoft.com/en-us/windows-server/storage/storage-spaces/storage-spaces-direct-overview
  - https://learn.microsoft.com/en-us/windows-server/security/guarded-fabric-shielded-vm/guarded-fabric-and-shielded-vms
  - https://learn.microsoft.com/en-us/windows-server/storage/storage-replica/storage-replica-overview
  - https://learn.microsoft.com/en-us/windows-server/get-started/whats-new-in-windows-server-2022
  - https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/plan/should-i-create-a-generation-1-or-2-virtual-machine-in-hyper-v
---

# Windows Server 핵심 개념 참조 노트

## 1. Hyper-V

### 공식 정의

Hyper-V는 Windows Server에 내장된 하드웨어 기반 가상화(Type-1 하이퍼바이저) 플랫폼입니다.
호스트 OS와 게스트 VM이 하이퍼바이저 위에서 동등하게 실행됩니다.

### Generation 1 vs Generation 2

| 항목           | Generation 1                | Generation 2            |
|----------------|-----------------------------|-------------------------|
| 펌웨어         | BIOS (Legacy)               | UEFI                    |
| Secure Boot    | ❌                          | ✅ (기본 활성화)        |
| 부팅 디스크    | IDE 컨트롤러                | SCSI 컨트롤러           |
| 최대 부트 볼륨 | VHD 2040 GB / VHDX 2 TB     | VHDX 64 TB              |
| 네트워크 부팅  | Legacy NIC 필요             | Synthetic NIC 직접 지원 |
| 32비트 OS      | ✅                          | ❌                      |
| 권장           | 레거시 OS, 기존 VHD 사용 시 | 신규 VM 기본 권장       |

> Generation은 VM 생성 후 변경 불가.
> 출처: learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/plan

### VHD vs VHDX

| 항목      | VHD              | VHDX              |
|-----------|------------------|-------------------|
| 최대 크기 | 2 TB             | 64 TB             |
| 블록 크기 | 512 bytes        | 1 MB (성능 향상)  |
| 내장 저널 | ❌               | ✅ (손상 방지)    |
| 지원 버전 | Hyper-V 2008+    | Hyper-V 2012+     |
| 권장      | 레거시 호환 시만 | 신규 VM 기본 권장 |

### Live Migration vs Quick Migration

| 항목          | Live Migration                                           | Quick Migration                |
|---------------|----------------------------------------------------------|--------------------------------|
| 다운타임      | 없음 (밀리초 수준)                                       | 짧은 다운타임 발생             |
| 메모리 전송   | 실행 중 실시간 전송                                      | 메모리 저장 후 이전            |
| 요구사항      | 공유 스토리지 권장 (로컬도 가능, Storage Migration 동반) | 공유 스토리지                  |
| 사용 시나리오 | 무중단 유지보수, 부하 분산                               | 긴급 이전, 유지보수 창 있을 때 |

## 2. Failover Clustering

### 공식 정의

> "Failover clustering is a powerful strategy to ensure high availability and uninterrupted operations
> in critical environments. It involves a configuration of independent computers, known as nodes,
> which work together to enhance the availability and scalability of applications and services."
> — learn.microsoft.com/en-us/windows-server/failover-clustering/failover-clustering-overview

독립된 서버(노드)들이 네트워크로 연결되어 하나의 클러스터를 구성합니다.
노드 장애 시 다른 노드가 자동으로 서비스를 인계(failover)합니다.

### Quorum

클러스터의 다수결 투표 메커니즘. 노드 장애 시 어느 쪽이 계속 동작할지 결정합니다.

| Quorum 구성         | 설명                                                         |
|---------------------|--------------------------------------------------------------|
| Node Majority       | 노드 수의 과반수 투표로 결정. 홀수 노드 환경에 적합          |
| Node + Disk Witness | 짝수 노드 환경에서 Witness 디스크(공유 스토리지)가 추가 투표 |
| Node + File Share   | 공유 파일 서버를 Witness로 사용                              |
| Cloud Witness       | Azure Blob Storage를 Witness로 사용 (2016+)                  |

🟡 노드 수가 짝수이면 반드시 Witness를 구성해야 split-brain을 방지할 수 있습니다.

### CSV (Cluster Shared Volumes)

여러 클러스터 노드가 동시에 동일한 NTFS 볼륨에 접근할 수 있게 하는 기술입니다.
기존 공유 디스크는 한 번에 하나의 노드만 소유권을 갖지만, CSV는 모든 노드가 동시 접근합니다.

- Hyper-V 고가용성 VM, S2D 배포 시 필수
- NTFS 기반, ReFS도 지원 (2016+)

## 3. Storage Spaces Direct (S2D)

### 공식 정의

> "Storage Spaces Direct enables you to cluster servers with internal storage into a
> software-defined storage solution."
> — learn.microsoft.com/en-us/windows-server/storage/storage-spaces/storage-spaces-direct-overview

서버 내 로컬 디스크(HDD/SSD/NVMe)를 클러스터링하여 공유 스토리지 풀을 구성합니다.
SAN/NAS 없이 HCI(Hyper-Converged Infrastructure)를 구현하는 핵심 기술입니다.

| 항목        | 내용                                             |
|-------------|--------------------------------------------------|
| 필요 에디션 | **Datacenter** 전용 (Standard 미지원)            |
| 최소 노드   | 2노드 (권장 4노드 이상)                          |
| 지원 디스크 | NVMe, SSD(캐시), HDD(용량)                       |
| 지원 버전   | Windows Server 2016+, Azure Local                |
| 네트워크    | RDMA(RoCE 또는 iWARP) 권장, 최소 10 GbE          |
| 복원력      | Mirror(2-way, 3-way), Parity, Mirror-accelerated |

### S2D 계층 구조

```
Applications / Hyper-V VMs
        │
  Cluster Shared Volumes (CSV)
        │
   Storage Spaces (Virtual Disks)
        │
   Storage Pool (집합된 디스크)
        │
  Physical Disks (NVMe / SSD / HDD)
```

## 4. Shielded VMs & Guarded Fabric

### 공식 정의

> "A shielded VM is a generation 2 VM that has a virtual TPM, is encrypted using BitLocker,
> and can run only on healthy and approved hosts in the fabric."
> — learn.microsoft.com/en-us/windows-server/security/guarded-fabric-shielded-vm

가상화 호스트가 침해되어도 VM 데이터를 보호합니다.
호스트 관리자도 VM 내부에 접근할 수 없습니다.

### 구성 요소

| 구성 요소                   | 역할                                       |
|-----------------------------|--------------------------------------------|
| Host Guardian Service (HGS) | 신뢰할 수 있는 호스트 인증 및 키 보관 서버 |
| Guarded Host                | HGS에 의해 검증된 Hyper-V 호스트           |
| Shielded VM                 | vTPM + BitLocker 암호화된 Gen 2 VM         |

| 항목        | 내용                  |
|-------------|-----------------------|
| 필요 에디션 | **Datacenter** 전용   |
| VM 세대     | **Generation 2** 필수 |
| 암호화      | BitLocker (vTPM 기반) |
| 도입 버전   | Windows Server 2016   |

## 5. Storage Replica

### 공식 정의

> "Storage Replica protects your critical data by replicating volumes between servers or clusters
> for disaster recovery."
> — learn.microsoft.com/en-us/windows-server/storage/storage-replica/storage-replica-overview

볼륨 단위 블록 레벨 복제 기술. 동기/비동기 복제 모두 지원합니다.

| 항목        | Standard                  | Datacenter    |
|-------------|---------------------------|---------------|
| 파트너십 수 | 1개                       | 무제한        |
| 볼륨 크기   | 최대 2 TB                 | 무제한        |
| 복제 방향   | 단방향/양방향 (제한 없음) | 단방향/양방향 |

| 복제 모드 | 설명                                    | RPO  |
|-----------|-----------------------------------------|------|
| 동기      | 원본 쓰기 완료 전 복제 완료 대기        | Zero |
| 비동기    | 복제 완료 대기 없이 원본 쓰기 즉시 완료 | >0   |

## 6. Network Controller (SDN)

Software-Defined Networking의 핵심 역할. 네트워크 정책을 중앙에서 프로그래밍 방식으로 관리합니다.

| 항목        | 내용                                 |
|-------------|--------------------------------------|
| 필요 에디션 | **Datacenter** 전용                  |
| 도입 버전   | Windows Server 2016                  |
| 관리 대상   | 가상 네트워크, ACL, QoS, 로드 밸런서 |
| 구성        | 최소 3노드 고가용성 권장             |

## 7. Hotpatch

재부팅 없이 보안 패치를 적용하는 기술입니다.

| 항목        | 내용                                                        |
|-------------|-------------------------------------------------------------|
| 필요 에디션 | **Datacenter: Azure Edition** 전용                          |
| 지원 환경   | Azure VM / Azure Local: 2022·2025 Datacenter: Azure Edition |
| 도입 버전   | Windows Server 2022 (공개 미리 보기)                        |
| 패치 주기   | 분기별 기준 패치 + 월별 Hotpatch (재부팅 불필요)            |
| 효과        | 연간 재부팅 횟수 12회 → 4회 수준으로 감소                   |

> 출처: learn.microsoft.com/en-us/windows-server/get-started/hotpatch

🟡 Azure Arc 연결 on-premises Hotpatch는 **Windows Server 2025만** 지원합니다 (2022는 Azure VM/Azure Local 환경에서만 가능).

## 8. RDMA (Remote Direct Memory Access)

NIC가 CPU를 거치지 않고 원격 메모리에 직접 접근하는 기술.
S2D 클러스터 노드 간 고성능 스토리지 트래픽에 사용됩니다.

| 구현 방식  | 설명                                           |
|------------|------------------------------------------------|
| RoCE       | RDMA over Converged Ethernet. DCB 필요         |
| iWARP      | TCP/IP 기반 RDMA. 기존 네트워크 장비 활용 가능 |
| InfiniBand | 전용 네트워크 패브릭. HPC 환경                 |

- SMB Direct: SMB 3.0이 RDMA를 활용하는 프로토콜 (S2D 노드 간 사용)

## 9. CAL (Client Access License)

Windows Server에 **접속하는 권한**에 대한 라이선스. OS 라이선스와 별개로 구매합니다.

| 종류               | 기준                        |
|--------------------|-----------------------------|
| User CAL           | 접속 사용자 1명당           |
| Device CAL         | 접속 디바이스 1대당         |
| External Connector | 서버 1대당 무제한 외부 접속 |

CAL 불필요 예외:
- Essentials 에디션 (포함)
- 인터넷 공개 서비스 (익명 접속)
- Azure 클라우드 서비스 형태

## 10. WinRM / PowerShell Remoting

Windows 원격 관리 기반 프로토콜.

| 항목          | 내용                                |
|---------------|-------------------------------------|
| 프로토콜      | HTTP(5985) / HTTPS(5986)            |
| 기반          | SOAP/WS-Management                  |
| 인증          | Kerberos(도메인), NTLM, CredSSP     |
| 활성화        | `Enable-PSRemoting`                 |
| 적용 시나리오 | PowerShell 원격 실행, Ansible WinRM |

## 11. 주요 개념 관계도

```
Windows Server Datacenter
  │
  ├── Hyper-V (가상화)
  │     ├── Generation 1 (BIOS/Legacy)
  │     └── Generation 2 (UEFI/Secure Boot)  ← Shielded VM 필수
  │
  ├── Failover Cluster (HA)
  │     ├── Quorum (다수결 결정)
  │     └── CSV (공유 볼륨)
  │
  ├── Storage Spaces Direct (HCI 스토리지)
  │     └── Datacenter 전용, RDMA 권장
  │
  ├── Shielded VM (보안 VM)
  │     └── HGS + vTPM + BitLocker
  │
  ├── Storage Replica (DR 복제)
  │     └── Standard: 1볼륨 2TB / Datacenter: 무제한
  │
  ├── Network Controller (SDN)
  │     └── Datacenter 전용
  │
  └── Hotpatch (무재부팅 패치)
        └── Datacenter: Azure Edition 전용
```

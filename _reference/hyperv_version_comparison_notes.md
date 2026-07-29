---
name: hyperv-version-comparison-notes
description: Windows Server 2008/2008R2/2012 Hyper-V 버전별 기능 차이와 CentOS 5.x 호환성 정리.
tags:
  - hyper-v
  - windows-server
  - compatibility
  - centos
  - legacy
last_checked: 2026-07-16
sources:
  - https://learn.microsoft.com/en-us/lifecycle/products/windows-server-2008
  - https://learn.microsoft.com/en-us/lifecycle/products/windows-server-2008-r2
  - https://learn.microsoft.com/en-us/lifecycle/products/windows-server-2012
  - https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/Supported-CentOS-and-Red-Hat-Enterprise-Linux-virtual-machines-on-Hyper-V
  - https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/plan/should-i-create-a-generation-1-or-2-virtual-machine-in-hyper-v
  - https://learn.microsoft.com/en-us/windows-server/storage/storage-qos/storage-qos-overview
---

# Hyper-V 버전별 비교 참조 노트

## 1. Windows Server 라이프사이클 (공식 확인)

| 버전                   | 출시일     | Mainstream 종료 | Extended 종료 | ESU 종료      |
|------------------------|------------|-----------------|---------------|---------------|
| Windows Server 2008    | 2008-05-06 | 2015-01-13      | 2020-01-14    | 2024 (Year 4) |
| Windows Server 2008 R2 | 2009-10-22 | 2015-01-13      | 2020-01-14    | 2024 (Year 4) |
| Windows Server 2012    | 2012-10-30 | 2018-10-09      | 2023-10-10    | 2026-10-13    |
| Windows Server 2012 R2 | 2013-11-25 | 2018-10-09      | 2023-10-10    | 2026-10-13    |

- 출처: learn.microsoft.com/en-us/lifecycle/products/

## 2. Hyper-V 버전별 기능

| 기능                      | 2008 (Hyper-V 1.0) | 2008 R2 (Hyper-V 2.0) | 2012 (Hyper-V 3.0) | 2012 R2     |
|---------------------------|--------------------|-----------------------|--------------------|-------------|
| 최대 vCPU/VM              | 4                  | 4                     | 64                 | 64          |
| 최대 메모리/VM            | 64GB               | 64GB                  | 1TB                | 1TB         |
| 최대 VM 수/호스트         | 비공식 ~150        | ~384                  | 1024               | 1024        |
| VHD 포맷                  | VHD (2TB)          | VHD (2TB)             | VHDX (64TB)        | VHDX (64TB) |
| Generation 2 VM           | ❌                 | ❌                    | ❌                 | ✅          |
| Live Migration            | ❌                 | ✅                    | ✅                 | ✅          |
| Storage Live Migration    | ❌                 | ❌                    | ✅                 | ✅          |
| Dynamic Memory            | ❌                 | ✅ (SP1)              | ✅                 | ✅          |
| CSV (Cluster Shared Vol.) | ❌                 | ✅                    | ✅                 | ✅          |
| Storage QoS               | ❌                 | ❌                    | ❌                 | ❌ (2016+)  |
| SR-IOV                    | ❌                 | ❌                    | ✅                 | ✅          |
| NIC Teaming (호스트)      | ❌                 | ❌                    | ✅                 | ✅          |
| Replica                   | ❌                 | ❌                    | ✅                 | ✅          |
| Virtual Fibre Channel     | ❌                 | ❌                    | ✅                 | ✅          |
| RemoteFX                  | ❌                 | ✅ (SP1)              | ✅                 | ✅          |

## 3. CentOS 5.x 호환성

### LIS (Linux Integration Services) 지원

| 호스트 버전 | LIS 버전 | 설치 방식 | 현재 입수 가능 여부 |
|-------------|----------|-----------|---------------------|
| 2008        | LIS 2.x  | 별도 설치 | ❌ (다운로드 폐쇄)  |
| 2008 R2     | LIS 3.x  | 별도 설치 | ❌ (다운로드 폐쇄)  |
| 2012        | LIS 4.x  | 별도 설치 | ❌ (다운로드 폐쇄)  |
| 2012 R2     | LIS 4.x  | 별도 설치 | ❌ (다운로드 폐쇄)  |

- 2026-07-16 기준: Microsoft 공식 지원 매트릭스에서 CentOS 5.x/6.x 항목 삭제됨
- LIS 다운로드 페이지 폐쇄 → 기존 설치된 LIS만 사용 가능

### LIS 유무에 따른 드라이버

| 컴포넌트    | LIS 없음 (에뮬레이션) | LIS 있음 (Synthetic)  |
|-------------|-----------------------|-----------------------|
| 디스크      | IDE (큐 깊이 1)       | storvsc (큐 깊이 64+) |
| 네트워크    | Legacy NIC (100Mbps)  | netvsc (10Gbps)       |
| 비디오      | S3 에뮬레이션         | Synthetic Video       |
| 마우스      | PS/2 에뮬레이션       | Synthetic Mouse       |
| 시간 동기화 | 없음 (drift 발생)     | TimeSync IC           |
| 하트비트    | 없음                  | Heartbeat IC          |
| KVP 교환    | 없음                  | KVP IC                |

## 4. I/O 경합 대응 가능 여부

| 완화 방법              | 2008 | 2008 R2 | 2012 | 2012 R2 | 2016+ |
|------------------------|------|---------|------|---------|-------|
| VHD 물리 분리          | ✅   | ✅      | ✅   | ✅      | ✅    |
| Fixed VHD              | ✅   | ✅      | ✅   | ✅      | ✅    |
| Storage QoS            | ❌   | ❌      | ❌   | ❌      | ✅    |
| Storage Live Migration | ❌   | ❌      | ✅   | ✅      | ✅    |
| Live Migration         | ❌   | ✅      | ✅   | ✅      | ✅    |
| I/O timeout (게스트)   | ✅   | ✅      | ✅   | ✅      | ✅    |
| CSV                    | ❌   | ✅      | ✅   | ✅      | ✅    |

## 5. 최대 사양 비교

### Hyper-V 호스트 제한

| 제한 항목          | 2008   | 2008 R2 | 2012   | 2012 R2 |
|--------------------|--------|---------|--------|---------|
| 논리 프로세서      | 24     | 64      | 320    | 320     |
| 물리 메모리        | 1TB    | 1TB     | 4TB    | 4TB     |
| VM당 가상 프로세서 | 4      | 4       | 64     | 64      |
| VM당 메모리        | 64GB   | 64GB    | 1TB    | 1TB     |
| 가상 스위치        | 무제한 | 무제한  | 무제한 | 무제한  |

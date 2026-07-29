---
name: windows-server-editions-licensing-notes
description: Windows Server 2022/2025 에디션 비교(Standard vs Datacenter), 라이선스 활성화 방식(KMS/MAK/AVMA), 키 유무에 따른 동작 차이, 수명주기 정리. Windows Server 관련 문서 작성/검토 시 참조.
tags:
  - windows-server
  - licensing
  - hyper-v
  - activation
  - datacenter
  - standard
last_checked: 2026-07-29
sources:
  - https://learn.microsoft.com/en-us/windows-server/get-started/editions-comparison
  - https://www.microsoft.com/en-us/licensing/product-licensing/windows-server
  - https://learn.microsoft.com/en-us/windows-server/get-started/kms-activation-planning
  - https://learn.microsoft.com/en-us/windows-server/get-started/automatic-vm-activation
  - https://learn.microsoft.com/en-us/lifecycle/products/windows-server-2022
  - https://learn.microsoft.com/en-us/lifecycle/products/windows-server-2025
---

# Windows Server 에디션 및 라이선스 참조 노트

## 1. 버전별 수명주기

| 버전                | GA 날짜    | Mainstream 종료 | Extended 종료 | 현재 상태 (2026-07)  |
|---------------------|------------|-----------------|---------------|----------------------|
| Windows Server 2019 | 2018-11-13 | 2024-01-09      | 2029-01-09    | Extended 지원 중     |
| Windows Server 2022 | 2021-08-18 | 2026-10-13      | 2031-10-14    | Mainstream 종료 임박 |
| Windows Server 2025 | 2024-11-01 | 2029-11-13      | 2034-11-14    | Mainstream 지원 중   |

🟡 Windows Server 2022는 2026-10-13에 Mainstream 지원이 종료됩니다.

> 출처: learn.microsoft.com/en-us/lifecycle/products/windows-server-2022

## 2. 에디션 종류

### Windows Server 2022/2025 에디션

| 에디션            | 대상 환경                        | 가격 정책      |
|-------------------|----------------------------------|----------------|
| Standard          | 소규모, 비가상화 또는 저밀도     | Per Core + CAL |
| Datacenter        | 고밀도 가상화, SDDC 환경         | Per Core + CAL |
| Datacenter: Azure | Azure 전용, 클라우드 네이티브    | Azure 과금     |
| Essentials        | 소규모 조직 (25 user, 50 device) | 별도 정책      |

## 3. Standard vs Datacenter 핵심 차이

### 가상 머신 수 제한 (VM 라이선스)

| 항목                      | Standard                | Datacenter     |
|---------------------------|-------------------------|----------------|
| Hyper-V 게스트 VM 포함 수 | 라이선스당 **2개**      | **무제한**     |
| VM 추가 방법              | 라이선스 추가 구매 필요 | 추가 비용 없음 |
| Hyper-V 컨테이너 (격리)   | 2개 (Hyper-V 격리)      | 무제한         |
| Windows Server 컨테이너   | 무제한 (격리 없음)      | 무제한         |

🟡 Standard 에디션에서 2개 초과의 VM을 운영하려면 라이선스를 추가로 구매해야 합니다.

### 기능 차이 (핵심 항목)

| 기능                         | Standard | Datacenter | 비고                                         |
|------------------------------|----------|------------|----------------------------------------------|
| Hyper-V                      | ✅       | ✅         | 양쪽 모두 지원                               |
| Storage Spaces               | ✅       | ✅         |                                              |
| Storage Spaces Direct (S2D)  | ❌       | ✅         | HCI 클러스터 구성 필요                       |
| Failover Clustering          | ✅       | ✅         |                                              |
| Shielded VMs (Host Guardian) | ❌       | ✅         | 보안 VM 격리                                 |
| AVMA (호스트 역할)           | ❌¹      | ✅         | 게스트 자동 활성화 호스트                    |
| Nano Server (container base) | ✅       | ✅         |                                              |
| SDN 전체 스택                | ❌       | ✅         | Software Defined Networking                  |
| Storage Replica              | 제한적   | ✅         | Standard: 1볼륨+2TB 제한, Datacenter: 무제한 |

> ¹ Standard는 AVMA 게스트로만 활성화 가능 (호스트로 동작 불가)

### 라이선싱 방식

- **Per Core 모델**: 서버의 물리 코어 수 기준 라이선스 구매 (최소 16코어)
- **CAL(Client Access License)**: 서버에 접근하는 사용자/디바이스마다 필요
- Standard vs Datacenter: 가격 차이 약 5.8배 (아래 MSRP 참고)


### 공식 MSRP (Windows Server 2025 기준, 16코어 라이선스)

> 출처: microsoft.com/en-us/windows-server/pricing (2026-07-29 확인)
> "Datacenter and Standard edition pricing is for 16 core licenses"
> Microsoft reseller 경유 구매 시 실제 가격 다를 수 있음.

| 에디션     | Suggested MSRP | 코어당 단가 | 비고                   |
|------------|----------------|-------------|------------------------|
| Standard   | $1,176         | ~$73.5/core | 16코어 기준            |
| Datacenter | $6,771         | ~$423/core  | 16코어 기준, 약 5.76배 |

- 추가 코어 라이선스는 2-pack 또는 16-pack 단위로 구매
- CAL(Client Access License) 별도 필요
- Volume License 계약(EA, Open Value 등)에 따라 실제 가격 상이
- Pay-as-you-go (Azure Arc): $33.58/CPU core/month

## 4. 활성화 방식 비교

| 방식                              | 설명                                           | 대상                       |
|-----------------------------------|------------------------------------------------|----------------------------|
| **KMS** (Key Management Service)  | 사내 KMS 서버 통해 활성화, 180일마다 갱신      | Volume License (기업)      |
| **MAK** (Multiple Activation Key) | 인터넷 통해 Microsoft에 직접 활성화, 횟수 제한 | Volume License (격리 환경) |
| **AVMA** (Auto VM Activation)     | Datacenter 호스트가 게스트 자동 활성화         | Hyper-V 게스트 VM          |
| **Retail Key**                    | 단일 키, 단일 PC 활성화                        | 소매 구매                  |
| **OEM Key**                       | 제조사가 하드웨어에 포함                       | 서버 제조사 번들           |

### KMS 동작 조건

- KMS 호스트 필요 (전용 서버 불필요, 공존 가능)
- 서버 활성화 임계값: **5대 이상** 요청 시 활성화
- 클라이언트 임계값: **25대 이상**
- 활성화 유효 기간: **180일** (자동 갱신)
- 갱신 주기: 7일마다 KMS 호스트에 재연결 시도

### AVMA 동작 조건

- 호스트: **Datacenter 에디션** 필수 (Standard 불가)
- 호스트가 인터넷 연결 없이도 게스트 활성화 가능
- 호스트 버전 ≥ 게스트 버전이어야 활성화 가능
- Failover Cluster: 모든 노드가 활성화되어야 함

## 5. 라이선스 키 유무에 따른 동작 차이

### 설치 유형별 차이

| 설치 유형         | 방법                      | 유효 기간        | 주요 제한           |
|-------------------|---------------------------|------------------|---------------------|
| **정품 키 입력**  | 설치 중 또는 `slmgr /ipk` | 영구 (활성화 시) | 없음                |
| **평가판 (Eval)** | Evaluation ISO 사용       | **180일**        | 기간 만료 시 종료   |
| **키 입력 없음**  | 설치 중 키 생략           | **30일**         | 배경화면 변경, 종료 |

### 미활성화(Unactivated) 상태 제한

30일 유예 기간 이후 키가 없는 경우:

- 배경화면 검은색으로 변경 (1시간마다 반복)
- 우측 하단 "Windows 정품 인증" 워터마크 표시
- Windows Update 업데이트 일부 제한
- 개인 설정(테마, 배경화면) 잠김
- `slmgr /dli`로 상태 확인 가능

### 평가판 → 정식 전환

```cmd
:: 평가판 → 정식 키로 전환 (재설치 불필요)
slmgr /ipk <정품 키>
slmgr /ato

:: 현재 라이선스 상태 확인
slmgr /dli    :: 기본 정보
slmgr /dlv    :: 상세 정보 (만료일 포함)
slmgr /xpr    :: 만료 날짜 확인
```

### 평가판 기간 연장 (최대 5회, 총 3년)

```cmd
:: 평가판 재무장 (rearm), 최대 5회 가능
slmgr /rearm
:: 재부팅 후 180일 초기화
```

## 6. 에디션 전환 (Edition Upgrade)

### 키를 이용한 업그레이드 (재설치 불필요)

| 전환 방향                        | 가능 여부 | 방법                 |
|----------------------------------|-----------|----------------------|
| Evaluation → Standard            | ✅        | `slmgr /ipk` 키 입력 |
| Evaluation → Datacenter          | ✅        | `slmgr /ipk` 키 입력 |
| Standard → Datacenter            | ✅        | `DISM /Set-Edition`  |
| Datacenter → Standard            | ❌        | 재설치 필요          |
| Standard Core ↔ Standard Desktop | ✅        | `DISM /Set-Edition`  |

```cmd
:: Standard → Datacenter (재부팅 필요)
DISM /online /Set-Edition:ServerDatacenter /ProductKey:<키> /AcceptEula

:: 에디션 확인
DISM /online /Get-CurrentEdition
```

## 7. 설치 옵션 (Desktop Experience vs Core)

| 옵션               | GUI | 메모리 절약 | 공격 표면 | 권장 시나리오     |
|--------------------|-----|-------------|-----------|-------------------|
| Server Core        | ❌  | ~1~2GB      | 작음      | 서버 역할 전용    |
| Desktop Experience | ✅  | —           | 큼        | 관리 편의 필요 시 |

🟡 Microsoft 권장: **Server Core** (보안, 경량화). Desktop Experience는 필요한 경우에만 사용.

## 8. 주요 확인 명령어

```cmd
:: 에디션 및 버전 확인
winver
systeminfo | findstr /i "OS Name"

:: 라이선스 상태 확인
slmgr /dli
slmgr /dlv
slmgr /xpr

:: 키 교체
slmgr /ipk <새 키>
slmgr /ato

:: KMS 서버 수동 지정
slmgr /skms <KMS서버:포트>
slmgr /ato

:: 에디션 확인 (PowerShell)
Get-WindowsEdition -Online
(Get-WmiObject Win32_OperatingSystem).Caption
```

## 9. 라이선스 모델 요약

| 항목                  | Standard               | Datacenter             |
|-----------------------|------------------------|------------------------|
| 라이선스 기준         | Per Core (최소 16코어) | Per Core (최소 16코어) |
| 게스트 VM 포함        | 2개                    | 무제한                 |
| AVMA 호스트           | ❌                     | ✅                     |
| Storage Spaces Direct | ❌                     | ✅                     |
| Shielded VM           | ❌                     | ✅                     |
| SDN 전체 스택         | ❌                     | ✅                     |
| 가격 (대략)           | 기준                   | Standard × 5~7배       |
| 적합 환경             | 저밀도, 소규모         | 고밀도 가상화, HCI     |

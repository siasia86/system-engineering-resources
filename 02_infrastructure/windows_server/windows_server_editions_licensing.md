# Windows Server 에디션과 라이선스

<!-- reference: _reference/windows_server_editions_licensing_notes.md -->

Windows Server 2022 이상의 에디션 종류, Standard vs Datacenter 차이, 라이선스 활성화 방식, 키 유무에 따른 동작 차이를 정리합니다.

## 목차

| 섹션                                                                                                                             |
|----------------------------------------------------------------------------------------------------------------------------------|
| [1. 에디션 종류](#1-에디션-종류) / [2. Standard vs Datacenter](#2-standard-vs-datacenter) / [3. 라이선스 비용](#3-라이선스-비용) |
| [4. 활성화 방식](#4-활성화-방식) / [5. 키 유무에 따른 동작](#5-키-유무에-따른-동작) / [6. 에디션 전환](#6-에디션-전환)           |
| [7. 설치 옵션](#7-설치-옵션) / [8. 수명주기](#8-수명주기) / [9. 확인 명령어](#9-확인-명령어)                                     |

---

## 1. 에디션 종류

Windows Server 2022/2025는 3개 주요 에디션으로 제공됩니다.

| 에디션                | 대상 환경                    | 특징                                                                                                              |
|-----------------------|------------------------------|-------------------------------------------------------------------------------------------------------------------|
| **Standard**          | 소규모, 비가상화 또는 저밀도 | 라이선스 1개당 **Windows Server 게스트 VM 2개** 포함. Linux VM은 카운트 무관. S2D·Shielded VM 등 SDDC 기능 미포함 |
| **Datacenter**        | 고밀도 가상화, SDDC 환경     | VM 무제한, Storage Spaces Direct·Shielded VM·Network Controller(SDN) 전부 포함                                    |
| **Datacenter: Azure** | Azure 전용                   | Hotpatch(재부팅 없는 보안 패치), Azure Arc·HCI 통합. KMS 미지원, Azure에서만 구동                                 |
| Essentials            | 소규모 조직 (25명 이하)      | 사용자당 CAL 불필요. 25사용자·50디바이스 제한, Domain Controller 역할 제한적, 별도 가격 정책                      |

🟡 Standard와 Datacenter는 **동일한 ISO**로 설치합니다. 키 입력 시점에 에디션이 결정됩니다.

### 에디션별 핵심 차이 한 줄 요약

| 에디션                | 언제 선택하는가                                    |
|-----------------------|----------------------------------------------------|
| **Standard**          | VM 10개 이하, SDDC 기능 불필요, 비용 절감 우선     |
| **Datacenter**        | VM 11개 이상, HCI(S2D), Shielded VM, SDN 필요      |
| **Datacenter: Azure** | Azure 클라우드 환경, Hotpatch 필요                 |
| **Essentials**        | 25명 이하 소규모, CAL 비용 제거, 단순 파일/AD 서버 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Standard vs Datacenter

### VM 수 제한 (핵심 차이)

| 항목                                     | Standard           | Datacenter     |
|------------------------------------------|--------------------|----------------|
| Windows Server 게스트 VM (라이선스 포함) | **2개**            | **무제한**     |
| VM 추가 방법                             | 라이선스 추가 구매 | 추가 비용 없음 |
| Windows Server 컨테이너                  | 무제한 (격리 없음) | 무제한         |
| Hyper-V 격리 컨테이너                    | 2개                | 무제한         |

```
Standard 라이선스 1개 = 서버 1대 + Windows Server 게스트 VM 2개
Standard 라이선스 2개 = 서버 1대 + Windows Server 게스트 VM 4개 (동일 서버 중복 적용)
Datacenter 라이선스 1개 = 서버 1대 + Windows Server 게스트 VM 무제한

Linux VM, Windows Client 등 비-Windows Server OS는 이 카운트에 포함되지 않음
```

### 컨테이너 격리 모드 비교

Windows 컨테이너는 두 가지 격리 모드로 실행됩니다.

| 항목            | Process 격리 (비격리)                    | Hyper-V 격리                          |
|-----------------|------------------------------------------|---------------------------------------|
| 구조            | 호스트 커널 공유 (Linux 컨테이너와 유사) | 컨테이너마다 경량 VM + 전용 커널      |
| 격리 수준       | 낮음 (네임스페이스 격리)                 | 높음 (하드웨어 수준 격리)             |
| 성능            | 빠름 (오버헤드 적음)                     | 느림 (VM 오버헤드)                    |
| 보안            | 낮음                                     | 높음 (커널 공유 없음)                 |
| Standard 제한   | **무제한**                               | **2개**                               |
| Datacenter 제한 | 무제한                                   | 무제한                                |
| 사용 시나리오   | 일반 앱 컨테이너화                       | 보안 강화, 멀티테넌트, 호환성 필요 시 |

🟡 Standard에서 **Hyper-V 격리 컨테이너가 2개 제한**인 이유: 각 컨테이너가 전용 VM을 가지므로 게스트 VM 카운트와 동일하게 취급됩니다.

```powershell
# Process 격리로 컨테이너 실행 (기본, 무제한)
docker run --isolation process mcr.microsoft.com/windows/servercore:ltsc2022

# Hyper-V 격리로 컨테이너 실행 (Standard에서 2개 제한)
docker run --isolation hyperv mcr.microsoft.com/windows/servercore:ltsc2022
```

### 기능 비교

| 기능                               | Standard | Datacenter | 비고                                  |
|------------------------------------|----------|------------|---------------------------------------|
| Hyper-V                            | ✅       | ✅         |                                       |
| Failover Clustering                | ✅       | ✅         |                                       |
| Storage Spaces                     | ✅       | ✅         |                                       |
| Storage Spaces Direct (S2D)        | ❌       | ✅         | HCI 클러스터 (S2D) 필수               |
| Storage Replica                    | ✅ 제한  | ✅         | Standard: 1볼륨, 최대 2TB             |
| Shielded VMs (Host Guardian)       | ❌       | ✅         | 보안 VM 격리                          |
| AVMA 호스트                        | ❌       | ✅         | 게스트 자동 활성화 불가               |
| Network Controller (SDN)           | ❌       | ✅         | Software-Defined Networking 핵심 역할 |
| Software-defined Datacenter (SDDC) | ❌       | ✅         |                                       |


### Datacenter 전용 기능 개념

> 💡 S2D, Shielded VM, Network Controller(SDN), SDDC, Failover Cluster, Hotpatch, Generation 2 VM 등의 개념은
> [windows_server_key_concepts.md](./windows_server_key_concepts.md)를 참고합니다.

### 선택 기준

```
VM을 많이 운영하는가?
  │
  ├── VM 11개 이상 → Datacenter (비용 효율: Standard 6개 = $7,056 > DC $6,771)
  │
  ├── VM 3~10개   → 상황별 선택
  │   - 비용만 고려: Standard (Standard 5개 = $5,880 < DC $6,771)
  │   - 기능 필요 (S2D, Shielded VM, AVMA 호스트): Datacenter
  │   - 관리 편의 (VM 무제한): Datacenter
  │
  └── VM 0~2개 → Standard (Datacenter의 약 1/5.8 가격, $1,176 vs $6,771)
```

🟡 순수 비용 기준: VM **11개 이상**이면 Datacenter가 효율적입니다 (섹션 3 비교표 참고).

[⬆ 목차로 돌아가기](#목차)

---

## 3. 라이선스 비용

### 공식 MSRP (2025 기준, 16코어 라이선스)

| 에디션     | Suggested MSRP | 코어당 단가 | 비율              |
|------------|----------------|-------------|-------------------|
| Standard   | $1,176         | ~$73.5/core | 기준              |
| Datacenter | $6,771         | ~$423/core  | Standard × 5.76배 |

> 출처: microsoft.com/en-us/windows-server/pricing (2026-07-29)
> 16코어 기준 가격. 실제 구매가는 Volume License 계약에 따라 다름.

### 라이선스 모델

| 항목             | 내용                                                                    |
|------------------|-------------------------------------------------------------------------|
| 기준             | Per Core — 서버의 **물리 코어 수** 기준으로 라이선스 구매               |
| 최소 코어 수     | **프로세서(CPU)당 최소 8코어**, **서버 전체 최소 16코어** 라이선스 필요 |
| 16코어 미만 서버 | 물리 코어가 10개라도 **최소 16코어 분** 구매 의무                       |
| 판매 단위        | 2-pack (코어 2개) 또는 16-pack (코어 16개) 단위로 판매                  |
| 추가 구매        | 최소 16코어 초과분은 2개 또는 16개 단위로 추가 구매                     |
| CAL              | 서버에 접속하는 사용자·디바이스마다 **별도 CAL 필요** (Essentials 제외) |
| Pay-as-you-go    | $33.58/CPU core/month (Azure Arc 연동, on-premises 유연 확장 시)        |

### VM 수에 따른 비용 비교 (16코어 서버 기준)

| VM 수   | Standard 구매 수 | Standard 총비용 | Datacenter 비용 | 절감                |
|---------|------------------|-----------------|-----------------|---------------------|
| 1~2개   | 1개              | $1,176          | $6,771          | Standard 유리       |
| 3~4개   | 2개              | $2,352          | $6,771          | Standard 유리       |
| 5~6개   | 3개              | $3,528          | $6,771          | Standard 유리       |
| 7~8개   | 4개              | $4,704          | $6,771          | Standard 유리       |
| 9~10개  | 5개              | $5,880          | $6,771          | Standard 유리       |
| 11~12개 | 6개              | $7,056          | $6,771          | **Datacenter 유리** |

🟡 VM 11개 이상이면 Datacenter가 비용 효율적입니다.
### CAL (Client Access License)

CAL은 Windows Server에 **접속하는 권한**에 대한 라이선스입니다. OS 라이선스와 별개로 구매해야 합니다.

> 💡 User CAL·Device CAL·External Connector 상세 개념은 [windows_server_key_concepts.md](./windows_server_key_concepts.md) 참고.

#### CAL 종류

| 종류                   | 기준                        | 적합한 경우                                          |
|------------------------|-----------------------------|------------------------------------------------------|
| **User CAL**           | 접속 사용자 1명당           | 여러 디바이스 사용 직원 (노트북 + 모바일 + 데스크탑) |
| **Device CAL**         | 접속 디바이스 1대당         | 공유 PC (교대 근무, 매장 단말 등 1대에 여러 명 사용) |
| **External Connector** | 서버 1대당 무제한 외부 접속 | 파트너사·고객 등 외부 사용자 대량 접속 시            |

🟡 User CAL과 Device CAL 중 **수가 적은 쪽**을 선택하면 비용 절감 가능합니다.

#### CAL이 필요 없는 경우

| 상황                       | 이유                               |
|----------------------------|------------------------------------|
| Essentials 에디션          | 에디션 자체에 포함 (25사용자 한도) |
| 서버가 인터넷 공개 서비스  | 익명 인터넷 접속은 CAL 불필요      |
| Azure 클라우드 서비스 형태 | Azure 자체 라이선스 모델 적용      |

#### SE 관점 주의사항

```
사내 파일 서버, AD, 프린트 서버에 직원 50명이 접속
  → Windows Server 라이선스 (Per Core) + CAL 50개 필요

인터넷에 공개된 웹 서버 (불특정 다수 접속)
  → Windows Server 라이선스만 필요 (CAL 불필요)

파트너사 직원 수백 명이 접속하는 서버
  → CAL 수백 개 대신 External Connector 라이선스 1개 (서버당) 선택 고려
```


[⬆ 목차로 돌아가기](#목차)

---

## 4. 활성화 방식

### 활성화 방식 비교

| 방식       | 설명                                           | 대상               | 인터넷 |
|------------|------------------------------------------------|--------------------|--------|
| **KMS**    | 사내 KMS 서버 경유 활성화, 180일마다 자동 갱신 | 기업 볼륨 라이선스 | 불필요 |
| **MAK**    | Microsoft에 직접 활성화, 횟수 제한 있음        | 볼륨, 격리 환경    | 필요   |
| **AVMA**   | Datacenter 호스트가 게스트 VM 자동 활성화      | Hyper-V 게스트     | 불필요 |
| Retail Key | 단일 키, 단일 서버 활성화                      | 소매 구매          | 필요   |
| OEM Key    | 제조사 하드웨어에 포함                         | 서버 구매 번들     | 필요   |

### KMS 상세

KMS는 사내 네트워크 내 KMS 호스트를 통해 활성화하는 기업용 방식입니다.

| 항목                | 내용                                    |
|---------------------|-----------------------------------------|
| 임계값 (서버)       | **5대 이상** 요청 시 활성화             |
| 임계값 (클라이언트) | **25대 이상**                           |
| 유효 기간           | **180일** (자동 갱신)                   |
| 갱신 주기           | **7일마다** KMS 호스트 재연결 시도      |
| KMS 호스트          | 전용 서버 불필요, 기존 서버와 공존 가능 |

```powershell
# KMS 서버 수동 지정
slmgr /skms <KMS서버주소:포트>
slmgr /ato

# KMS 서버 확인
slmgr /dli
```

### AVMA 상세

Hyper-V 호스트가 Datacenter 에디션이면 게스트 VM을 인터넷 없이 자동 활성화합니다.

| 항목             | 내용                                                                       |
|------------------|----------------------------------------------------------------------------|
| 호스트 요구      | **Datacenter 에디션** + Hyper-V 역할 필수                                  |
| 게스트 버전      | 호스트 버전 ≥ 게스트 버전 (예: 2022 호스트 → 2019/2016 게스트 활성화 가능) |
| 인터넷           | 불필요 (오프라인 환경 가능)                                                |
| Failover Cluster | 모든 노드가 활성화되어야 함                                                |
| Standard 호스트  | ❌ 사용 불가 (AVMA 호스트는 Datacenter만)                                  |

```
Datacenter 호스트
  └── 게스트 VM (Standard/Datacenter/Essentials) → AVMA 자동 활성화
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 키 유무에 따른 동작

### 설치 유형별 비교

| 유형              | 방법                      | 유효 기간 | 비고                                    |
|-------------------|---------------------------|-----------|-----------------------------------------|
| **정품 키 입력**  | 설치 중 또는 `slmgr /ipk` | 영구      | 없음                                    |
| **평가판 (Eval)** | Evaluation ISO 사용       | **180일** | 만료 후 바탕화면 우측 하단 알림 표시    |
| **키 입력 없음**  | 설치 중 키 생략           | **30일**  | Unlicensed state (Initial Grace Period) |

### 키 없음 / 미활성화 상태 (Unlicensed state)

키 없이 설치하거나 30일 유예 기간(Initial Grace Period) 이후 활성화하지 않으면
**Unlicensed state**가 됩니다.

공식 문서 (`activation-slmgr-vbs-options`, `upgrade-conversion-options`) 에서 확인된 내용:

| 현상      | 내용                                                      |
|-----------|-----------------------------------------------------------|
| 알림 표시 | 바탕화면 우측 하단에 활성화 알림 표시 (Notification mode) |
| 서버 기능 | 핵심 서버 역할은 동작 (Hyper-V, Failover Cluster 등)      |

🟡 Windows Server 2008 이후 Reduced Functionality Mode(RFM)는 폐지됐습니다.
배경화면 강제 변경·개인 설정 제한 등의 상세 동작은 공식 문서에 명시되지 않습니다.
운영 환경에서는 라이선스 준수가 필수입니다.

### 평가판 연장 (rearm)

```cmd
:: 평가판 유예 기간 리셋 (최대 5회, 총 ~3년)
slmgr /rearm
:: 재부팅 후 180일 재시작

:: 남은 rearm 횟수 확인
slmgr /dlv
```

### 평가판 → 정식 전환

```cmd
:: 키 입력 (재설치 불필요)
slmgr /ipk <정품 키>
slmgr /ato

:: 전환 확인
slmgr /dli
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 에디션 전환

### 전환 가능 방향

| 전환 방향                 | 가능 여부 | 방법                      |
|---------------------------|-----------|---------------------------|
| Evaluation → Standard     | ✅        | `slmgr /ipk` 정품 키 입력 |
| Evaluation → Datacenter   | ✅        | `slmgr /ipk` 정품 키 입력 |
| Standard → Datacenter     | ✅        | `DISM /Set-Edition`       |
| **Datacenter → Standard** | ❌        | **재설치 필요**           |
| Standard Core ↔ Desktop   | ✅        | `DISM /Set-Edition`       |

### Standard → Datacenter 업그레이드

```cmd
:: 1. 현재 에디션 확인
DISM /online /Get-CurrentEdition

:: 2. 업그레이드 가능 에디션 확인
DISM /online /Get-TargetEditions

:: 3. Datacenter로 전환 (재부팅 필요)
DISM /online /Set-Edition:ServerDatacenter /ProductKey:<Datacenter키> /AcceptEula

:: 4. 전환 확인
DISM /online /Get-CurrentEdition
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 설치 옵션

Windows Server는 두 가지 설치 방식을 제공합니다.

| 항목           | Server Core                           | Desktop Experience |
|----------------|---------------------------------------|--------------------|
| GUI            | ❌ (CLI만)                            | ✅                 |
| 메모리 절약    | 수백 MB~수 GB (역할 구성에 따라 다름) | —                  |
| 보안           | 공격 표면 최소화                      | 공격 표면 큼       |
| 관리           | PowerShell/원격                       | GUI 직접 관리 가능 |
| Microsoft 권장 | ✅ 권장                               | 필요 시만          |

🟡 설치 후 Core ↔ Desktop Experience 전환은 `DISM /Set-Edition`으로 가능하나, 재부팅이 필요합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 수명주기

| 버전                | GA         | Mainstream 종료 | Extended 종료 | 현황 (2026-07)       |
|---------------------|------------|-----------------|---------------|----------------------|
| Windows Server 2019 | 2018-11-13 | 2024-01-09      | 2029-01-09    | Extended 지원 중     |
| Windows Server 2022 | 2021-08-18 | 2026-10-13      | 2031-10-14    | Mainstream 종료 임박 |
| Windows Server 2025 | 2024-11-01 | 2029-11-13      | 2034-11-14    | Mainstream 지원 중   |

🟡 Windows Server 2022는 2026-10-13 Mainstream 지원 종료. 신규 구축은 2025 권장.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 확인 명령어

### 라이선스 상태 확인

```cmd
:: 에디션 및 버전
winver
systeminfo | findstr /i "OS Name"

:: 라이선스 기본 정보
slmgr /dli

:: 라이선스 상세 (만료일 포함)
slmgr /dlv

:: 라이선스 만료 날짜
slmgr /xpr
```

### 활성화

```cmd
:: 키 입력
slmgr /ipk <ProductKey>

:: 온라인 활성화
slmgr /ato

:: KMS 서버 지정
slmgr /skms <KMS서버:포트>
slmgr /ato
```

### 에디션 확인

```powershell
# PowerShell
Get-WindowsEdition -Online
(Get-WmiObject Win32_OperatingSystem).Caption

# DISM
DISM /online /Get-CurrentEdition
```

### Hyper-V VM 라이선스 확인

```powershell
# VM 목록 및 상태
Get-VM | Select Name, State, Version

# VM별 VHD 위치
Get-VM | Get-VMHardDiskDrive | Select VMName, Path

# AVMA 상태 확인 (이벤트 로그)
Get-WinEvent -LogName "Microsoft-Windows-Hyper-V-VMMS-Admin" |
    Where-Object {$_.Id -eq 12309} |
    Select -First 5 | Format-List TimeCreated, Message
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. 수명주기 종료 후 — ESU (Extended Security Updates)

Extended Security Updates는 Extended 지원 종료 후에도 보안 패치를 계속 받을 수 있는 유료 구독 프로그램입니다.

### ESU 제공 내용

| 항목        | 내용                                          |
|-------------|-----------------------------------------------|
| 포함        | Critical·Important 등급 보안 패치만           |
| 미포함      | 기능 업데이트, 버그 수정, 설계 변경 요청      |
| 최대 기간   | Extended 지원 종료 후 **최대 3년** (Year 1~3) |
| Azure VM    | **무료** (자동 적용)                          |
| On-premises | **유료** (Volume License 또는 Azure Arc 경유) |

### 적용 버전 (2026-07 기준)

| 버전                   | Extended 종료 | ESU Year 1 | ESU Year 2 | ESU Year 3 |
|------------------------|---------------|------------|------------|------------|
| Windows Server 2012    | 2023-10-10    | 2024-10-08 | 2025-10-14 | 2026-10-13 |
| Windows Server 2012 R2 | 2023-10-10    | 2024-10-08 | 2025-10-14 | 2026-10-13 |
| Windows Server 2016    | 2027-01-12    | 2028-01-11 | 2029-01-09 | 2030-01-08 |
| Windows Server 2019    | 2029-01-09    | 2030-01-08 | 2031-01-14 | 2032-01-13 |

🟡 2022는 Extended 지원 중 (종료: 2031-10-14), 2025는 Mainstream 지원 중 → 현재 ESU 불필요.
2022는 Mainstream 지원이 2026-10-13 종료 예정이나, Extended 지원 종료(2031)까지는 보안 패치가 계속 제공됩니다.

### ESU 비용 구조 (On-premises)

| 연도   | 비용                                    | 비고                           |
|--------|-----------------------------------------|--------------------------------|
| Year 1 | OS 라이선스 전체 가격의 **100%** (연간) | 예: Standard 기준 연간 ~$1,176 |
| Year 2 | 동일 (100%)                             | Year 1 구매 필수 선행          |
| Year 3 | 동일 (100%)                             | Year 2 구매 필수 선행          |

🟡 3년 합산 시 OS 라이선스 비용의 **3배** 추가 비용 발생. 상위 버전으로 업그레이드가 대부분의 경우 더 경제적입니다.

> 출처: learn.microsoft.com/en-us/lifecycle/faq/extended-security-updates
> "Year 1: 100% of full license price annually"

### ESU 획득 방법

| 방법                      | 비용 | 조건                         |
|---------------------------|------|------------------------------|
| Azure VM으로 마이그레이션 | 무료 | Azure VM에서 자동 적용       |
| Azure Arc 연동 (on-prem)  | 유료 | Azure Arc 에이전트 설치 필요 |
| Volume License (연간)     | 유료 | EA/Open Value 계약 필요      |

### SE 판단 기준

```
Extended 지원 종료 임박?
  │
  ├── Azure VM으로 이전 가능? → ESU 무료 + 관리 비용 감소
  │
  ├── On-premises 유지 필요?
  │     └── ESU 비용 vs 업그레이드 비용 비교
  │         - ESU 3년: OS 라이선스 비용 × 3
  │         - 업그레이드: 신규 라이선스 1회
  │         → 대부분 업그레이드가 경제적
  │
  └── 즉시 업그레이드 불가? → ESU Year 1 구매 + 마이그레이션 계획 수립
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Windows Server Pricing: [microsoft.com/en-us/windows-server/pricing](https://www.microsoft.com/en-us/windows-server/pricing) — ★★★☆☆
- Edition Comparison: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/get-started/editions-comparison) — ★★★☆☆
- KMS Activation Planning: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/get-started/kms-activation-planning) — ★★★☆☆
- AVMA: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/get-started/automatic-vm-activation) — ★★★☆☆
- Lifecycle: [learn.microsoft.com/en-us/lifecycle/products/windows-server-2022](https://learn.microsoft.com/en-us/lifecycle/products/windows-server-2022) — ★★★☆☆
- ESU FAQ: [learn.microsoft.com/en-us/lifecycle/faq/extended-security-updates](https://learn.microsoft.com/en-us/lifecycle/faq/extended-security-updates) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-29

**마지막 업데이트**: 2026-07-29

© 2026 siasia86. Licensed under CC BY 4.0.

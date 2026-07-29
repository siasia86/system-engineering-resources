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

| 에디션                | 대상 환경                    | 특징                                    |
|-----------------------|------------------------------|-----------------------------------------|
| **Standard**          | 소규모, 비가상화 또는 저밀도 | VM 2개 포함, 기본 기능                  |
| **Datacenter**        | 고밀도 가상화, SDDC 환경     | VM 무제한, S2D/Shielded VM 포함         |
| **Datacenter: Azure** | Azure 전용                   | Hotpatch, Azure 서비스 통합, KMS 미지원 |
| Essentials            | 소규모 조직 (25명 이하)      | CAL 불필요, 도메인 컨트롤러 역할 제한   |

🟡 Standard와 Datacenter는 동일한 ISO로 설치합니다. **키 입력 시점에 에디션이 결정**됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. Standard vs Datacenter

### VM 수 제한 (핵심 차이)

| 항목                              | Standard           | Datacenter     |
|-----------------------------------|--------------------|----------------|
| Hyper-V 게스트 VM (라이선스 포함) | **2개**            | **무제한**     |
| VM 추가 방법                      | 라이선스 추가 구매 | 추가 비용 없음 |
| Windows Server 컨테이너           | 무제한 (격리 없음) | 무제한         |
| Hyper-V 격리 컨테이너             | 2개                | 무제한         |

```
Standard 라이선스 1개 = 서버 1대 + VM 2개
Standard 라이선스 2개 = 서버 1대 + VM 4개  (동일 서버에 중복 적용 가능)
Datacenter 라이선스 1개 = 서버 1대 + VM 무제한
```

### 기능 비교

| 기능                               | Standard | Datacenter | 비고                        |
|------------------------------------|----------|------------|-----------------------------|
| Hyper-V                            | ✅       | ✅         |                             |
| Failover Clustering                | ✅       | ✅         |                             |
| Storage Spaces                     | ✅       | ✅         |                             |
| Storage Spaces Direct (S2D)        | ❌       | ✅         | HCI 클러스터 (S2D) 필수     |
| Storage Replica                    | ✅ 제한  | ✅         | Standard: 1볼륨, 최대 2TB   |
| Shielded VMs (Host Guardian)       | ❌       | ✅         | 보안 VM 격리                |
| AVMA 호스트                        | ❌       | ✅         | 게스트 자동 활성화 불가     |
| SDN 전체 스택                      | ❌       | ✅         | Software Defined Networking |
| Software-defined Datacenter (SDDC) | ❌       | ✅         |                             |

### 선택 기준

```
VM을 많이 운영하는가?
  │
  ├── 예 (VM 3개 이상) → Datacenter
  │   이유: VM당 Standard 라이선스 추가 비용 > Datacenter 단가
  │
  └── 아니오 (VM 0~2개) → Standard
      이유: Datacenter 대비 약 1/6 가격
```

🟡 VM 4개 이상이면 Datacenter가 비용 효율적입니다. (Standard 2개 구매 비용이 Datacenter 단가를 초과)

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

| 항목          | 내용                                   |
|---------------|----------------------------------------|
| 기준          | Per Core (물리 코어 수 기준)           |
| 최소 코어 수  | 서버당 **16코어** (프로세서당 8코어)   |
| 판매 단위     | 2-pack 또는 16-pack                    |
| CAL           | 접속 사용자/디바이스마다 별도 필요     |
| Pay-as-you-go | $33.58/CPU core/month (Azure Arc 연동) |

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

| 항목             | 내용                                      |
|------------------|-------------------------------------------|
| 호스트 요구      | **Datacenter 에디션** + Hyper-V 역할 필수 |
| 게스트 버전      | 호스트 버전 이하 가능 (상위 버전 불가)    |
| 인터넷           | 불필요 (오프라인 환경 가능)               |
| Failover Cluster | 모든 노드가 활성화되어야 함               |
| Standard 호스트  | ❌ 사용 불가 (AVMA 호스트는 Datacenter만) |

```
Datacenter 호스트
  └── 게스트 VM (Standard/Datacenter/Essentials) → AVMA 자동 활성화
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 키 유무에 따른 동작

### 설치 유형별 비교

| 유형              | 방법                      | 유효 기간 | 제한 사항                     |
|-------------------|---------------------------|-----------|-------------------------------|
| **정품 키 입력**  | 설치 중 또는 `slmgr /ipk` | 영구      | 없음                          |
| **평가판 (Eval)** | Evaluation ISO 사용       | **180일** | 기간 만료 시 1시간마다 종료   |
| **키 입력 없음**  | 설치 중 키 생략           | **30일**  | 배경화면 변경, 기능 일부 제한 |

### 키 없음 / 미활성화 상태 제한

라이선스 키 없이 설치하거나 30일 유예 기간 이후 활성화하지 않으면:

| 현상           | 내용                               |
|----------------|------------------------------------|
| 배경화면       | 검은색으로 변경 (1시간마다 반복)   |
| 워터마크       | 우측 하단 "Windows 정품 인증" 표시 |
| 개인 설정      | 테마, 배경화면 변경 불가           |
| Windows Update | 일부 업데이트 제한                 |
| 서버 기능      | 핵심 기능은 대부분 동작            |

🟡 미활성화 상태에서도 Hyper-V, Failover Cluster 등 서버 역할은 동작합니다. 단, 운영 환경에서는 라이선스 준수 필수입니다.

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

| 항목           | Server Core      | Desktop Experience |
|----------------|------------------|--------------------|
| GUI            | ❌ (CLI만)       | ✅                 |
| 메모리 절약    | ~1~2 GB          | —                  |
| 보안           | 공격 표면 최소화 | 공격 표면 큼       |
| 관리           | PowerShell/원격  | GUI 직접 관리 가능 |
| Microsoft 권장 | ✅ 권장          | 필요 시만          |

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

## 참고 자료

- Windows Server Pricing: [microsoft.com/en-us/windows-server/pricing](https://www.microsoft.com/en-us/windows-server/pricing) — ★★★☆☆
- Edition Comparison: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/get-started/editions-comparison) — ★★★☆☆
- KMS Activation Planning: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/get-started/kms-activation-planning) — ★★★☆☆
- AVMA: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/get-started/automatic-vm-activation) — ★★★☆☆
- Lifecycle: [learn.microsoft.com/en-us/lifecycle/products/windows-server-2022](https://learn.microsoft.com/en-us/lifecycle/products/windows-server-2022) — ★★★☆☆

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

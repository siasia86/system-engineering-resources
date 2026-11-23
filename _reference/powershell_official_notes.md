---
name: powershell-official-notes
description: PowerShell 7의 판, 지원 수명 주기(LTS·Stable), Linux·Windows 설치, 프로필 위치, 오류 처리 기본의 공식 출처 기준 사실 정리.
tags:
  - powershell
  - windows
  - linux
  - shell
last_checked: 2026-11-23
sources:
  - https://github.com/PowerShell/PowerShell/releases
  - https://learn.microsoft.com/en-us/powershell/scripting/install/powershell-support-lifecycle
  - https://learn.microsoft.com/en-us/powershell/scripting/install/install-ubuntu
  - https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows
  - https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles
  - https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_preference_variables
---

# PowerShell 공식 참조 노트

## 1. 공식 소스

| 소스                       | URL                                                                                                            | 용도                     |
|----------------------------|----------------------------------------------------------------------------------------------------------------|--------------------------|
| PowerShell releases        | https://github.com/PowerShell/PowerShell/releases                                                              | 판, 설치 파일            |
| Support lifecycle          | https://learn.microsoft.com/en-us/powershell/scripting/install/powershell-support-lifecycle                    | LTS·Stable 정책          |
| Install on Ubuntu          | https://learn.microsoft.com/en-us/powershell/scripting/install/install-ubuntu                                  | Linux 설치               |
| Install on Windows         | https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows                   | Windows 설치             |
| about_Profiles             | https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles             | 프로필 위치              |
| about_Preference_Variables | https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_preference_variables | `$ErrorActionPreference` |

## 2. 검증된 사실 (2026-11-23)

| 항목                    | 값                                                                                                                                   | 출처                       |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------|----------------------------|
| 최신 판                 | 7.7.0 (2026-11-10). 같은 시점의 7.6 계열 최신은 7.6.10                                                                               | GitHub releases            |
| LTS 정의                | .NET의 LTS 판에 맞춘 PowerShell 판. 갱신은 중요한 보안·서비스 수정만                                                                 | support lifecycle          |
| Stable 정의             | LTS 사이의 판. 다음 LTS가 나온 뒤 약 6개월까지 지원                                                                                  | support lifecycle          |
| 수명 주기 문서 기준 LTS | 7.6 (문서 갱신 2026-08-13 시점 7.6.6). 이전 LTS 7.4는 2026-11-10까지 지원                                                            | support lifecycle          |
| 두 가지 PowerShell      | Windows PowerShell 5.1(`powershell.exe`, Windows에 기본, Desktop 판)과 PowerShell 7(`pwsh`, Core 판, 여러 OS)                        | 설치 문서                  |
| Linux 설치              | Microsoft 패키지 저장소 또는 GitHub release의 `.deb`·`.rpm`·`tar.gz`                                                                 | install-ubuntu             |
| Windows 설치            | `winget install --id Microsoft.PowerShell --source winget` 또는 MSI                                                                  | install on Windows         |
| 프로필 (현재 사용자)    | Linux `~/.config/powershell/Microsoft.PowerShell_profile.ps1`, Windows `$HOME\Documents\PowerShell\Microsoft.PowerShell_profile.ps1` | about_Profiles, 컨테이너   |
| 오류 처리               | `$ErrorActionPreference = 'Stop'`이면 종료되지 않는 오류도 멈춤. 기본값 `Continue`                                                   | about_Preference_Variables |
| Windows 전용 명령       | `Get-Service` 등 일부 cmdlet은 Linux판에 없음                                                                                        | 컨테이너 확인              |

## 3. 검증 기록

- 1차: GitHub release(판·설치 파일)와 Microsoft Learn 문서(수명 주기, 설치, 프로필, 기본 설정 변수)에서 확인했습니다. 수명 주기 문서는 2026-08-13 갱신본이라 7.7.0 정식판이 반영되지 않았으므로 판 번호는 GitHub release를 따릅니다.
- 2차: `ubuntu:24.04` 컨테이너에 GitHub release의 `powershell_7.7.0-1.deb_amd64.deb`를 설치해 `$PSVersionTable`, `$PROFILE`, `$ErrorActionPreference`, 실행 정책, 스크립트 매개변수·JSON 변환·오류 종료 코드, `Get-Service` 부재를 실행해 대조했습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.

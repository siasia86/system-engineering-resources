---
name: iis-official-notes
description: Windows Server IIS의 설치 명령, 사이트·애플리케이션·가상 디렉터리·애플리케이션 풀 구조, 관리 모듈, 로그 위치의 공식 출처 기준 사실 정리.
tags:
  - iis
  - windows
  - web-server
last_checked: 2026-11-23
sources:
  - https://learn.microsoft.com/en-us/powershell/module/servermanager/install-windowsfeature
  - https://learn.microsoft.com/en-us/iis/get-started/planning-your-iis-architecture/understanding-sites-applications-and-virtual-directories-on-iis
  - https://learn.microsoft.com/en-us/powershell/module/iisadministration/
  - https://learn.microsoft.com/en-us/iis/manage/provisioning-and-managing-iis/configure-logging-in-iis
---

# IIS 공식 참조 노트

## 1. 공식 소스

| 소스                       | URL                                                                                                                                              | 용도            |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|
| Install-WindowsFeature     | https://learn.microsoft.com/en-us/powershell/module/servermanager/install-windowsfeature                                                         | 역할 설치       |
| Sites, applications, vdirs | https://learn.microsoft.com/en-us/iis/get-started/planning-your-iis-architecture/understanding-sites-applications-and-virtual-directories-on-iis | 구조            |
| IISAdministration module   | https://learn.microsoft.com/en-us/powershell/module/iisadministration/                                                                           | PowerShell 관리 |
| Configure logging          | https://learn.microsoft.com/en-us/iis/manage/provisioning-and-managing-iis/configure-logging-in-iis                                              | 로그 위치       |

## 2. 검증된 사실 (2026-11-23)

| 항목            | 값                                                                                                           | 출처                   |
|-----------------|--------------------------------------------------------------------------------------------------------------|------------------------|
| 설치            | `Install-WindowsFeature -Name Web-Server -IncludeManagementTools` (하위 기능 전체는 `-IncludeAllSubFeature`) | Install-WindowsFeature |
| 구조            | 사이트 → 애플리케이션 → 가상 디렉터리. 애플리케이션 풀이 서로 다른 앱을 격리                                 | Sites/apps/vdirs       |
| PowerShell 관리 | IISAdministration 모듈 (`Get-IISSite`, `Get-IISSiteBinding` 등)                                              | IISAdministration      |
| 로그 기본 위치  | `%SystemDrive%\inetpub\logs\LogFiles`. 운영에서는 시스템 드라이브가 아닌 곳을 권장                           | Configure logging      |

## 3. 검증 기록

- 1차: Microsoft Learn 문서(설치 cmdlet 예시, 구조, 모듈, 로그)에서 확인했습니다.
- 2차: 같은 사실을 각 문서의 다른 절(예시 명령, 모듈 cmdlet 목록, 로그 권장 문장)로 다시 대조했습니다. 작성 환경이 Linux라 실행 시험은 하지 않았습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.

# IIS
<!-- reference: _reference/iis_official_notes.md -->

Windows Server에 들어 있는 웹 서버(Internet Information Services)입니다. ASP.NET 앱이나 Windows 기반 사내 웹을 운영할 때 씁니다. 이 문서만으로 설치 → 사이트·애플리케이션 풀 구성 → 바인딩·HTTPS → 로그 → 검증까지 PowerShell로 따라 할 수 있게 썼습니다.

- 기준: Windows Server 2025의 IIS 10
- 예제 시험: 미실행(작성 환경이 Linux). 명령과 구조는 Microsoft Learn 문서와 대조했습니다

## 목차

| 섹션                                                                                                 |
|------------------------------------------------------------------------------------------------------|
| [1. 구조](#1-구조) / [2. 설치](#2-설치) / [3. 사이트와 애플리케이션 풀](#3-사이트와-애플리케이션-풀) |
| [4. HTTPS 바인딩](#4-https-바인딩) / [5. 로그](#5-로그) / [6. 검증](#6-검증)                         |
| [7. 트러블슈팅](#7-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                   |

---

## 1. 구조

| 요소            | 뜻                                                               |
|-----------------|------------------------------------------------------------------|
| 사이트          | 바인딩(프로토콜·IP·포트·호스트 이름)으로 요청을 받는 단위        |
| 애플리케이션    | 사이트 안의 경로(`/app`)로 나뉜 앱                               |
| 가상 디렉터리   | URL 경로를 실제 폴더에 연결                                      |
| 애플리케이션 풀 | 앱을 실행하는 작업자 프로세스(`w3wp.exe`) 묶음. 풀끼리 서로 격리 |

앱마다 애플리케이션 풀을 나누면 한 앱의 장애·재시작이 다른 앱에 번지지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

관리자 PowerShell:

```powershell
Install-WindowsFeature -Name Web-Server -IncludeManagementTools
# ASP.NET 등 하위 기능이 필요하면 해당 기능 이름을 더 지정 (전체는 -IncludeAllSubFeature)
Get-WindowsFeature -Name Web-* | Where-Object Installed
Invoke-WebRequest http://localhost -UseBasicParsing | Select-Object StatusCode   # 기본 사이트 200
```

기본 사이트의 파일 위치는 `C:\inetpub\wwwroot`입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 사이트와 애플리케이션 풀

```powershell
Import-Module IISAdministration
New-Item -ItemType Directory -Path D:\sites\app | Out-Null
Set-Content D:\sites\app\index.html '<h1>app</h1>'

New-WebAppPool -Name AppPool1                          # WebAdministration 모듈
New-IISSite -Name App -PhysicalPath D:\sites\app -BindingInformation "*:8080:"
Set-ItemProperty IIS:\Sites\App -Name applicationPool -Value AppPool1

Get-IISSite                                            # 사이트 목록과 상태
Get-IISSiteBinding -Name App                           # 바인딩
```

GUI는 IIS 관리자(`inetmgr`)를 씁니다. 같은 서버를 여러 대 맞추려면 위처럼 PowerShell 스크립트로 남겨 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. HTTPS 바인딩

1. 인증서를 컴퓨터 저장소(`Cert:\LocalMachine\My`)에 가져옵니다.
2. 사이트에 443 바인딩을 더하고 인증서를 연결합니다.

```powershell
$thumb = (Get-ChildItem Cert:\LocalMachine\My | Where-Object Subject -like '*app.example.com*').Thumbprint
New-IISSiteBinding -Name App -BindingInformation "*:443:app.example.com" -Protocol https `
  -CertificateThumbPrint $thumb -CertStoreLocation "Cert:\LocalMachine\My" -SslFlag Sni
```

인증서 만료 전에 교체 절차를 정해 두고, HTTP는 URL Rewrite 등으로 HTTPS로 넘깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 로그

| 항목      | 내용                                                                |
|-----------|---------------------------------------------------------------------|
| 기본 위치 | `%SystemDrive%\inetpub\logs\LogFiles\W3SVC<사이트ID>`               |
| 권장      | 시스템 드라이브가 아닌 별도 드라이브로 옮김 (사이트의 로그 설정)    |
| 오류 추적 | 실패 요청 추적(Failed Request Tracing)으로 느린·실패 요청 상세 기록 |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용   | 명령                                                                       | 기대 결과                |
|------|-------------|----------------------------------------------------------------------------|--------------------------|
| 1    | 설치        | `Get-WindowsFeature Web-Server`                                            | `Installed`              |
| 2    | 서비스      | `Get-Service W3SVC`                                                        | `Running`                |
| 3    | 사이트 상태 | `Get-IISSite`                                                              | 사이트가 `Started`       |
| 4    | 응답        | `Invoke-WebRequest http://localhost:8080 -UseBasicParsing`                 | `StatusCode 200`         |
| 5    | HTTPS       | `Test-NetConnection app.example.com -Port 443`, 브라우저                   | 연결 성공, 유효한 인증서 |
| 6    | 로그        | `Get-ChildItem C:\inetpub\logs\LogFiles -Recurse \| Select-Object -Last 1` | 최근 로그 파일           |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                    | 원인                                    | 해결 방법                                    |
|-------------------------|-----------------------------------------|----------------------------------------------|
| 503 Service Unavailable | 애플리케이션 풀 중지 (반복 오류로 중지) | 이벤트 로그 확인 후 풀 시작, 원인 수정       |
| 사이트가 시작되지 않음  | 같은 IP·포트·호스트 이름 바인딩 충돌    | `Get-IISSiteBinding`으로 충돌 확인           |
| 500.19                  | `web.config` 문법 오류, 없는 모듈 사용  | 오류 페이지의 설정 줄 확인, 필요한 기능 설치 |
| 디스크가 로그로 가득 참 | 로그 정리 없음                          | 로그 보관 기간 정책, 별도 드라이브           |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [PowerShell](../../01_fundamentals/windows/powershell.md) — 관리 명령의 바탕
- [Windows Server 핵심 개념](./windows_server_key_concepts.md) — 역할과 기능
- [Windows 네트워크 진단](../../01_fundamentals/windows/windows_network_diagnostics.md) — 포트·연결 점검
- [Nginx 설치](../web_server/nginx_install.md) — Linux 쪽 웹 서버

---

## 참고 자료

- Microsoft Learn: [Install-WindowsFeature](https://learn.microsoft.com/en-us/powershell/module/servermanager/install-windowsfeature) — ★★★☆☆
- Microsoft Learn: [About Sites, Applications, and Virtual Directories in IIS](https://learn.microsoft.com/en-us/iis/get-started/planning-your-iis-architecture/understanding-sites-applications-and-virtual-directories-on-iis) — ★★★☆☆
- Microsoft Learn: [IISAdministration module](https://learn.microsoft.com/en-us/powershell/module/iisadministration/) — ★★★☆☆
- Microsoft Learn: [Configure Logging in IIS](https://learn.microsoft.com/en-us/iis/manage/provisioning-and-managing-iis/configure-logging-in-iis) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.

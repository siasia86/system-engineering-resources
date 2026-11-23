# PowerShell
<!-- reference: _reference/powershell_official_notes.md -->

명령 결과를 글자가 아니라 객체로 주고받는 셸이자 스크립트 언어입니다. Windows 서버 관리의 기본 도구이고, PowerShell 7(`pwsh`)은 Linux·macOS에서도 동작합니다. 이 문서만으로 설치 → 기본 문법과 파이프라인 → 스크립트 작성 → 원격 실행 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: PowerShell 7.7.0(2026-11-10), LTS 계열 7.6
- 예제 시험: 2026-11-23, `ubuntu:24.04` 컨테이너에 7.7.0을 설치해 3~6절의 공통 명령과 스크립트를 실행해 확인. Windows 전용 명령(서비스, 이벤트 로그, WinRM 원격)은 Windows에서 실행하지 않았음

## 목차

| 섹션                                                                                                               |
|--------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. 기본 문법](#3-기본-문법)                                             |
| [4. 파이프라인과 객체](#4-파이프라인과-객체) / [5. 스크립트](#5-스크립트) / [6. 서버 관리 명령](#6-서버-관리-명령) |
| [7. 원격 실행](#7-원격-실행) / [8. 검증](#8-검증) / [9. 트러블슈팅](#9-트러블슈팅)                                 |
| [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                                                                  |

---

## 1. 개요

| 항목      | Windows PowerShell 5.1               | PowerShell 7                |
|-----------|--------------------------------------|-----------------------------|
| 실행 파일 | `powershell.exe`                     | `pwsh` (`pwsh.exe`)         |
| 판 표시   | `PSEdition` = `Desktop`              | `PSEdition` = `Core`        |
| 운영체제  | Windows (기본 설치)                  | Windows, Linux, macOS       |
| 갱신      | 기능 추가 없음 (Windows와 함께 유지) | LTS·Stable 판으로 계속 출시 |

두 판은 한 Windows에 함께 설치됩니다. 새 스크립트는 PowerShell 7 기준으로 쓰고, 오래된 모듈이 5.1에서만 동작할 때만 5.1을 씁니다.

| 지원 구분 | 내용                                                   |
|-----------|--------------------------------------------------------|
| LTS       | .NET LTS에 맞춘 판(7.4, 7.6). 보안·서비스 수정만 받음  |
| Stable    | LTS 사이의 판(7.5, 7.7). 다음 LTS 뒤 약 6개월까지 지원 |

운영 서버에는 LTS 판을 권장합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

### 2-1. Windows

```powershell
winget install --id Microsoft.PowerShell --source winget
pwsh -Version
```

### 2-2. Ubuntu (Microsoft 저장소)

```bash
. /etc/os-release
curl -fsSLO "https://packages.microsoft.com/config/ubuntu/${VERSION_ID}/packages-microsoft-prod.deb"
sudo dpkg -i packages-microsoft-prod.deb && rm packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y powershell
pwsh -Version
```

### 2-3. 저장소 없이 (GitHub release)

```bash
VER=7.7.0
curl -fsSLO "https://github.com/PowerShell/PowerShell/releases/download/v${VER}/powershell_${VER}-1.deb_amd64.deb"
sudo apt-get install -y "./powershell_${VER}-1.deb_amd64.deb"
```

RHEL 계열은 같은 release의 `.rpm`(`powershell-7.7.0-1.rh.x86_64.rpm`)을 `dnf install`로 설치합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 기본 문법

명령 이름은 `동사-명사` 형식이고 대소문자를 구분하지 않습니다.

```powershell
Get-Command -Noun Process          # 이름에 Process가 들어간 명령 찾기
Get-Help Get-Process -Examples     # 사용 예 (처음 한 번 Update-Help)
Get-Process | Get-Member           # 결과 객체의 속성·메서드 보기

$name = "web01"                    # 변수
$ports = @(80, 443)                # 배열
$cfg = @{ Host = "web01"; Port = 80 }   # 해시 테이블
"host: $name, ports: $($ports -join ',')"   # 문자열 안 식

if ($ports -contains 443) { "https" } else { "http" }
foreach ($p in $ports) { "port $p" }
```

| 비교 연산자 | 뜻          | 비교 연산자         | 뜻                  |
|-------------|-------------|---------------------|---------------------|
| `-eq` `-ne` | 같음·다름   | `-like`             | 와일드카드 (`web*`) |
| `-gt` `-lt` | 큼·작음     | `-match`            | 정규식              |
| `-contains` | 배열에 포함 | `-and` `-or` `-not` | 논리                |

`>`·`<`는 비교가 아니라 리다이렉션이므로 비교에는 `-gt`·`-lt`를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 파이프라인과 객체

파이프로 넘어가는 것은 글자가 아니라 객체이므로 열을 잘라 낼 필요 없이 속성 이름으로 고릅니다.

```powershell
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 5 Name, Id, WorkingSet64
Get-ChildItem /var/log -File | Where-Object Length -gt 10MB | Select-Object Name, Length
Get-ChildItem -Recurse -Filter *.log | Measure-Object Length -Sum
Get-Content app.log | Select-String "ERROR" | Select-Object -Last 20

[pscustomobject]@{ Host = "web01"; Port = 80 } | ConvertTo-Json -Compress   # {"Host":"web01","Port":80}
Import-Csv hosts.csv | Where-Object role -eq "web"
Invoke-RestMethod https://api.github.com/repos/PowerShell/PowerShell/releases/latest | Select-Object tag_name
```

| 명령             | 하는 일                         |
|------------------|---------------------------------|
| `Where-Object`   | 조건으로 고르기                 |
| `Select-Object`  | 속성 고르기, 처음·마지막 N개    |
| `Sort-Object`    | 정렬                            |
| `Group-Object`   | 값별로 묶어 세기                |
| `Measure-Object` | 개수·합계·평균                  |
| `ForEach-Object` | 하나씩 처리 (`%`)               |
| `Format-Table`   | 화면 표시용 (파이프 마지막에만) |

`Format-Table`·`Format-List`는 화면용 객체로 바꾸므로 그 뒤에 다른 명령을 잇지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 스크립트

`check.ps1`

```powershell
param(
    [Parameter(Mandatory)][string]$Path,
    [int]$MinFreeGB = 10
)
Set-StrictMode -Version Latest          # 정의되지 않은 변수 사용 등을 오류로
$ErrorActionPreference = 'Stop'         # 종료되지 않는 오류도 멈추게 (기본값 Continue)

try {
    $items = Get-ChildItem -Path $Path -File
    Write-Output "files: $($items.Count)"
}
catch {
    Write-Error "failed: $($_.Exception.Message)"
    exit 1
}
```

```powershell
pwsh -NoProfile -File ./check.ps1 -Path /etc
echo $LASTEXITCODE              # 0
```

| 항목                    | 설명                                                                                                                                        |
|-------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| `-NoProfile`            | 프로필을 읽지 않아 어느 서버에서나 같은 결과                                                                                                |
| 실행 정책 (Windows)     | 내려받은 스크립트 실행을 제한. `Get-ExecutionPolicy`, 서버 기본은 `RemoteSigned`                                                            |
| 실행 정책 (Linux·macOS) | 적용되지 않음 (`Unrestricted`로 표시)                                                                                                       |
| 프로필 (현재 사용자)    | `$PROFILE` — Windows `Documents\PowerShell\Microsoft.PowerShell_profile.ps1`, Linux `~/.config/powershell/Microsoft.PowerShell_profile.ps1` |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 서버 관리 명령

| 작업               | Windows                                            | Linux에서 (PowerShell 7)        |
|--------------------|----------------------------------------------------|---------------------------------|
| 프로세스           | `Get-Process`, `Stop-Process -Id`                  | 같음                            |
| 서비스             | `Get-Service`, `Restart-Service -Name`             | 없음 (`systemctl` 사용)         |
| 이벤트 로그        | `Get-WinEvent -LogName System -MaxEvents 20`       | 없음 (`journalctl` 사용)        |
| 디스크             | `Get-Volume`, `Get-PSDrive -PSProvider FileSystem` | `Get-PSDrive`                   |
| 네트워크 연결 시험 | `Test-NetConnection host -Port 443`                | 없음 (`Test-Connection`은 ICMP) |
| 업데이트·패키지    | `winget upgrade --all`                             | apt·dnf                         |
| 기능·역할 (Server) | `Get-WindowsFeature`, `Install-WindowsFeature`     | 해당 없음                       |

Windows 진단 명령은 함께 보기의 Windows 문서에 자세히 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 원격 실행

```powershell
# Windows ↔ Windows: WinRM (도메인 환경 기본)
Enable-PSRemoting -Force                           # 대상 서버에서 한 번
Invoke-Command -ComputerName srv01 -ScriptBlock { Get-Service W32Time }
Enter-PSSession -ComputerName srv01                # 대화형

# OS 사이 공통: SSH (PowerShell 7)
Invoke-Command -HostName user@srv02 -ScriptBlock { $PSVersionTable.PSVersion }
```

SSH 원격은 대상의 `sshd_config`에 PowerShell 서브시스템(Linux `Subsystem powershell /usr/bin/pwsh -sshs`, Windows `Subsystem powershell C:/progra~1/powershell/7/pwsh.exe -sshs`)을 등록해야 합니다. 비밀번호를 스크립트에 쓰지 말고 SSH 키나 `Get-Credential`·비밀 관리 모듈을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 검증

| 순서 | 확인 내용           | 명령                                                                               | 기대 결과                     |
|------|---------------------|------------------------------------------------------------------------------------|-------------------------------|
| 1    | 설치와 판           | `pwsh -Version`, `$PSVersionTable.PSVersion`                                       | 의도한 판, `PSEdition` `Core` |
| 2    | 객체 파이프라인     | `Get-Process \| Select-Object -First 1 Name, Id`                                   | 이름과 ID                     |
| 3    | JSON 변환           | `[pscustomobject]@{a=1} \| ConvertTo-Json -Compress`                               | `{"a":1}`                     |
| 4    | 스크립트 종료 코드  | `pwsh -NoProfile -File ./check.ps1 -Path /etc; $LASTEXITCODE`                      | `0`                           |
| 5    | 오류 종료 코드      | `pwsh -NoProfile -Command "Get-Content /nope -ErrorAction Stop"`, 셸에서 `echo $?` | `1`                           |
| 6    | 실행 정책 (Windows) | `Get-ExecutionPolicy -List`                                                        | 조직 정책과 일치              |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                                       | 원인                                  | 해결 방법                                                        |
|------------------------------------------------------------|---------------------------------------|------------------------------------------------------------------|
| `... cannot be loaded because running scripts is disabled` | Windows 실행 정책                     | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`, 또는 서명 |
| `The term 'Get-Service' is not recognized` (Linux)         | Windows 전용 cmdlet                   | `systemctl` 등 Linux 명령 사용                                   |
| 오류가 났는데 스크립트가 계속 진행                         | 종료되지 않는 오류, 기본값 `Continue` | `$ErrorActionPreference = 'Stop'` 또는 `-ErrorAction Stop`       |
| 비교가 파일을 만듦 (`$a > 5`)                              | `>`는 리다이렉션                      | `-gt` 사용                                                       |
| 결과를 파이프로 넘겼더니 이상함                            | `Format-*` 뒤에 파이프                | `Format-*`는 마지막에만                                          |
| 5.1에서 되던 스크립트가 7에서 실패                         | 7에 없는 모듈·.NET Framework 의존     | 모듈의 7 지원 확인, 꼭 필요하면 `powershell.exe`로 실행          |
| 같은 스크립트가 서버마다 다르게 동작                       | 프로필이 다름                         | `-NoProfile`로 실행                                              |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Windows 네트워크 진단](./windows_network_diagnostics.md) — `Test-NetConnection`, `Get-NetTCPConnection`, `pktmon`
- [Windows Server 리소스 분석](./windows_server_resource_analysis.md) — 성능 카운터와 이벤트 로그
- [Windows OpenSSH 설치](../../04_security/hardening/windows_openssh_install.md) — SSH 원격의 전제
- [Bash 스크립트](../linux/bash_scripting.md) — Linux 셸 스크립트

---

## 참고 자료

- Microsoft Learn: [PowerShell Support Lifecycle](https://learn.microsoft.com/en-us/powershell/scripting/install/powershell-support-lifecycle) — ★★★☆☆
- Microsoft Learn: [Install PowerShell on Windows](https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows) · [on Ubuntu](https://learn.microsoft.com/en-us/powershell/scripting/install/install-ubuntu) — ★★★☆☆
- Microsoft Learn: [about_Profiles](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles) · [about_Preference_Variables](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_preference_variables) — ★★★☆☆
- Microsoft Learn: [PowerShell remoting over SSH](https://learn.microsoft.com/en-us/powershell/scripting/security/remoting/ssh-remoting-in-powershell) — ★★★☆☆
- GitHub: [PowerShell releases](https://github.com/PowerShell/PowerShell/releases) — 7.7.0 확인 2026-11-23 — ★★★☆☆

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

# Windows OpenSSH Server 설치 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. 공개키 인증 설정](#3-공개키-인증-설정) |
| [4. Ansible 연동](#4-ansible-연동) / [5. 보안 설정](#5-보안-설정) / [6. 트러블슈팅](#6-트러블슈팅) |

---

## 1. 개요

Windows Server 2019 / Windows 10 이상에서 OpenSSH Server를 기본 제공합니다.
Linux에서 `ssh` 명령으로 Windows에 접속하거나, Ansible WinRM 대신 SSH 연결로 사용할 수 있습니다.

| 항목       | 내용                                       |
|------------|--------------------------------------------|
| 대상 OS    | Windows Server 2019/2022, Windows 10/11    |
| 포트       | 22/tcp                                     |
| 인증 방식  | 공개키 (패스워드는 보안상 비활성화 권장)   |
| 주요 용도  | Ansible SSH 연결, 원격 관리, 파일 전송     |

> ⚠️ Windows OpenSSH 9.5 이하에서 `Administrator` 계정은 버그로 인해 접속이 안 됩니다.
> **별도 로컬 계정을 생성해서 Administrators 그룹에 추가하는 방식을 권장합니다.**

---

## 2. 설치

PowerShell(관리자)에서 실행합니다.

```powershell
# 설치
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# 서비스 시작 및 자동 시작 등록
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
```

설치 확인:

```powershell
Get-Service sshd
```

```
Status   Name   DisplayName
------   ----   -----------
Running  sshd   OpenSSH SSH Server
```

방화벽 규칙은 설치 시 자동 추가됩니다. 누락된 경우 수동 추가:

```powershell
New-NetFirewallRule -Name "OpenSSH-Server-In-TCP" `
  -DisplayName "OpenSSH Server (sshd)" `
  -Enabled True -Direction Inbound -Protocol TCP `
  -Action Allow -LocalPort 22
```

---

## 3. 공개키 인증 설정

### Step 1 — 전용 계정 생성 (Administrator 계정 버그 우회)

```powershell
$pw = ConvertTo-SecureString "SecurePassword123" -AsPlainText -Force
New-LocalUser -Name "ansibleuser" -Password $pw -PasswordNeverExpires
Add-LocalGroupMember -Group "Administrators" -Member "ansibleuser"
```

### Step 2 — sshd_config 수정

```powershell
# PubkeyAuthentication 활성화 (주석 해제)
(Get-Content "C:\ProgramData\ssh\sshd_config") `
  -replace '#PubkeyAuthentication yes', 'PubkeyAuthentication yes' |
  Set-Content "C:\ProgramData\ssh\sshd_config"
```

`sshd_config` 하단에 아래 두 줄이 **주석 없이** 있어야 합니다:

```
Match Group administrators
        AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
```

주석이 있으면 제거:

```powershell
(Get-Content "C:\ProgramData\ssh\sshd_config") `
  -replace '#Match Group administrators', 'Match Group administrators' `
  -replace '#\s+AuthorizedKeysFile __PROGRAMDATA__', '        AuthorizedKeysFile __PROGRAMDATA__' |
  Set-Content "C:\ProgramData\ssh\sshd_config"
```

### Step 3 — 기본 쉘을 PowerShell로 설정

```powershell
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" `
  -Name DefaultShell `
  -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" `
  -PropertyType String -Force
```

### Step 4 — 공개키 등록

Linux에서 공개키 확인:

```bash
cat ~/.ssh/id_ed25519.pub
```

Windows에서 등록 (Administrators 그룹 계정 공통):

> ⚠️ Administrators 그룹 계정은 `authorized_keys`가 무시됩니다.
> 반드시 `C:\ProgramData\ssh\administrators_authorized_keys`에 등록해야 합니다.

```powershell
$keys = @(
    "ssh-ed25519 AAAA...key1 user1@host",
    "ssh-ed25519 AAAA...key2 user2@host"
)

# LF 강제 저장 (CRLF이면 인증 실패)
$file = "C:\ProgramData\ssh\administrators_authorized_keys"
New-Item -Path "C:\ProgramData\ssh" -ItemType Directory -Force
[System.IO.File]::WriteAllText($file, ($keys -join "`n") + "`n", [System.Text.Encoding]::UTF8)
icacls $file /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"

Restart-Service sshd
```

### Step 5 — 접속 테스트

```bash
ssh ansibleuser@<Windows_IP>
```

---

## 4. Ansible 연동

WinRM 없이 SSH로 직접 연결합니다.

#### inventory.ini

```ini
[windows]
win_host ansible_host=<Windows_IP>

[windows:vars]
ansible_user=ansibleuser
ansible_connection=ssh
ansible_shell_type=powershell
ansible_ssh_private_key_file=~/.ssh/id_ed25519
```

#### 동작 확인

```bash
ansible windows -i inventory.ini -m ansible.windows.win_ping
```

#### Playbook 예시

```yaml
- name: Windows 정보 수집
  hosts: windows
  tasks:
    - name: OS 버전 확인
      ansible.windows.win_shell: systeminfo | findstr "OS Name"
      register: result

    - name: 출력
      ansible.builtin.debug:
        msg: "{{ result.stdout_lines }}"
```

---

## 5. 보안 설정

### 패스워드 인증 비활성화

`C:\ProgramData\ssh\sshd_config`:

```
PasswordAuthentication no
PubkeyAuthentication yes
```

```powershell
Restart-Service sshd
```

### 접속 허용 IP 제한

```powershell
netsh advfirewall firewall set rule name="OpenSSH-Server-In-TCP" `
  new remoteip=192.0.2.10
```

---

## 6. 트러블슈팅

| 증상 | 원인 | 조치 |
|------|------|------|
| `Connection reset` (인증 직전) | `PubkeyAuthentication` 주석 처리 | `sshd_config`에서 주석 제거 후 재시작 |
| `Connection reset` (Administrator) | OpenSSH 9.5 버그 | 별도 계정 생성 후 Administrators 그룹 추가 |
| 공개키 인증 실패 | 파일 권한 과다 | `icacls`로 해당 계정/SYSTEM만 허용 |
| 공개키 인증 실패 (Administrators 그룹 계정) | `authorized_keys` 무시됨 — Administrators 그룹은 `administrators_authorized_keys` 우선 참조 | `C:\ProgramData\ssh\administrators_authorized_keys`에 키 등록 |
| 공개키 인증 실패 (키 등록했는데 안 됨) | `authorized_keys` CRLF 줄바꿈 | `[System.IO.File]::WriteAllText`로 LF 강제 저장 |
| 접속 후 즉시 종료 | DefaultShell 미설정 | `HKLM:\SOFTWARE\OpenSSH` DefaultShell 등록 |
| sshd 시작 실패 | `sshd_config` 문법 오류 | `SyslogFacility` 등 Windows 미지원 옵션 제거 |

### 디버그 모드로 원인 확인

sshd 서비스를 중지하고 포그라운드로 실행하면 상세 로그를 볼 수 있습니다:

```powershell
Stop-Service sshd
& "C:\Windows\System32\OpenSSH\sshd.exe" -d
```

접속 시도 후 콘솔 출력으로 원인을 확인합니다.

### 이벤트 로그 확인

```powershell
Get-WinEvent -LogName "OpenSSH/Operational" -MaxEvents 20 | Select TimeCreated, Message | Format-List
```

---

[⬆ 목차로 돌아가기](#목차)

---

**작성일**: 2026-05-18

**마지막 업데이트**: 2026-05-18

© 2026 siasia86. Licensed under CC BY 4.0.

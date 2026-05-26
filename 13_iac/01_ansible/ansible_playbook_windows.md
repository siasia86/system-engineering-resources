# Ansible Playbook Windows 가이드

## 목차

| 섹션 |
|------|
| [1. 연결 설정](#1-연결-설정) / [2. 자주 쓰는 모듈](#2-자주-쓰는-모듈) / [3. Ad-hoc 명령](#3-ad-hoc-명령) |
| [4. Playbook 예시](#4-playbook-예시) / [5. 주의사항](#5-주의사항) |

> 공통 필드는 [ansible_playbook_fields.md](ansible_playbook_fields.md) 참고

---

## 1. 연결 설정

### SSH 연결 (권장)

```ini
[windows]
win_host ansible_host=10.200.101.101

[windows:vars]
ansible_user=ansibleuser
ansible_connection=ssh
ansible_shell_type=powershell
ansible_ssh_private_key_file=~/.ssh/id_ed25519
```

### WinRM 연결 (SSH 미사용 환경)

```ini
[windows]
win_host ansible_host=10.200.101.101

[windows:vars]
ansible_user=ansibleuser
ansible_password=SecurePassword123
ansible_connection=winrm
ansible_winrm_transport=ntlm
ansible_winrm_port=5985
ansible_winrm_scheme=http
```

> 🟡 `ansible_password` 평문은 테스트 환경 전용입니다. 운영 환경에서는 `ansible-vault encrypt_string` 사용.

### ansible.cfg

```ini
[defaults]
inventory = inventory_windows.ini
host_key_checking = False

[privilege_escalation]
become = True
become_method = runas
```

### WinRM HTTPS 연결 (운영 환경 권장)

```ini
[windows:vars]
ansible_connection=winrm
ansible_winrm_transport=ntlm
ansible_winrm_port=5986
ansible_winrm_scheme=https
ansible_winrm_server_cert_validation=ignore
```

---

## 2. 자주 쓰는 모듈

### 명령 실행

```yaml
# PowerShell 명령 실행 (파이프/변수 사용 가능)
- ansible.windows.win_shell: Get-Service | Where-Object {$_.Status -eq 'Running'}
  register: result

# 단순 명령 (파이프 불가)
- ansible.windows.win_command: ipconfig /all
  register: result

# UTF-8 출력 (한글 깨짐 방지)
- ansible.windows.win_shell: |
    chcp 65001 | Out-Null
    systeminfo
  register: result
```

### 패키지 관리

```yaml
# Windows Update (보안 업데이트)
- ansible.windows.win_updates:
    category_names:
      - SecurityUpdates
      - CriticalUpdates
    state: searched      # searched(탐지만) / installed(설치)
  register: update_result

# MSI/EXE 설치
- ansible.windows.win_package:
    path: C:\installers\app.msi
    state: present

# Chocolatey 패키지 (컬렉션 설치 필요: ansible-galaxy collection install chocolatey.chocolatey)
- chocolatey.chocolatey.win_chocolatey:
    name: googlechrome
    state: present
```

### 서비스 관리

```yaml
- ansible.windows.win_service:
    name: wuauserv
    state: started       # started / stopped / restarted
    start_mode: auto     # auto / manual / disabled
```

### 파일/디렉토리

```yaml
- ansible.windows.win_file:
    path: C:\myapp\logs
    state: directory     # directory / absent / touch

- ansible.windows.win_copy:
    src: files/config.ini
    dest: C:\myapp\config.ini

# win_template은 ansible.builtin.template로 대체 (Windows 경로도 지원)
- ansible.builtin.template:
    src: templates/app.conf.j2
    dest: C:\myapp\app.conf
```

### 레지스트리

```yaml
- ansible.windows.win_regedit:
    path: HKLM:\SOFTWARE\MyApp
    name: Version
    data: "1.0.0"
    type: string
```

### 연결 테스트

```yaml
- ansible.windows.win_ping:
```

---

## 3. Ad-hoc 명령

> 🟡 `ansible -a` (command 모듈)는 Windows에서 동작하지 않습니다.
> 반드시 `-m ansible.windows.win_shell`을 명시해야 합니다.

```bash
# 연결 테스트
ansible windows -m ansible.windows.win_ping

# 명령 실행
ansible windows -m ansible.windows.win_shell -a "whoami"
ansible windows -m ansible.windows.win_shell -a "chcp 65001 | Out-Null; hostname"

# 실행 중인 서비스 목록
ansible windows -m ansible.windows.win_shell -a "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object Name"

# 보안 업데이트 확인 (ad-hoc은 탐지만 가능, 설치는 playbook 권장)
ansible windows -m ansible.windows.win_updates -a "state=searched"

# 파일 복사
ansible windows -m ansible.windows.win_copy -a "src=/tmp/test.txt dest=C:\\test.txt"
```

---

## 4. Playbook 예시

### Windows 상태 수집

```yaml
---
- name: Windows 상태 수집
  hosts: windows
  tasks:
    - name: OS 정보
      ansible.windows.win_shell: |
        chcp 65001 | Out-Null
        systeminfo | findstr /C:"OS Name" /C:"OS Version" /C:"Total Physical Memory"
      register: result

    - name: 출력
      ansible.builtin.debug:
        msg: "{{ result.stdout_lines }}"
```

### 보안 업데이트 점검 및 설치

```yaml
---
- name: Windows 보안 업데이트
  hosts: windows
  tasks:
    - name: 미설치 보안 업데이트 확인
      ansible.windows.win_updates:
        category_names:
          - SecurityUpdates
          - CriticalUpdates
        state: searched
      register: update_result

    - name: 업데이트 목록 출력
      ansible.builtin.debug:
        msg: "{{ update_result.updates | length }}개 보안 업데이트 필요"

    - name: 업데이트 설치 (필요 시)
      ansible.windows.win_updates:
        category_names:
          - SecurityUpdates
          - CriticalUpdates
        state: installed
      when: update_result.updates | length > 0
      register: install_result

    - name: 재부팅 필요 여부 확인
      ansible.builtin.debug:
        msg: "재부팅 필요: {{ install_result.reboot_required | default(false) }}"
      when: install_result is defined
```

---

## 5. 주의사항

### UTF-8 출력 (한글 깨짐)

SSH 비대화형 세션에서 Windows 출력이 CP949로 나와 한글이 깨집니다.

```bash
# ad-hoc
ansible windows -m ansible.windows.win_shell -a "chcp 65001 | Out-Null; systeminfo"

# playbook
- ansible.windows.win_shell: |
    chcp 65001 | Out-Null
    systeminfo
```

### authorized_keys CRLF 문제

`Set-Content`는 CRLF로 저장하여 SSH 인증 실패를 유발합니다.
반드시 `WriteAllText`로 LF 강제 저장합니다.

```powershell
[System.IO.File]::WriteAllText(
    "C:\ProgramData\ssh\administrators_authorized_keys",
    ($keys -join "`n") + "`n",
    [System.Text.Encoding]::UTF8
)
```

### Administrators 그룹 계정 키 등록 위치

Administrators 그룹 계정은 `~/.ssh/authorized_keys`가 무시됩니다.

```text
# 일반 계정
C:\Users\<username>\.ssh\authorized_keys

# Administrators 그룹 계정 (ansibleuser 포함)
C:\ProgramData\ssh\administrators_authorized_keys
```

### Linux vs Windows 모듈 대응표

| 용도        | Linux                     | Windows                       |
|-------------|---------------------------|-------------------------------|
| 명령 실행   | `command`, `shell`        | `win_shell`, `win_command`    |
| 파일 관리   | `ansible.builtin.file`    | `ansible.windows.win_file`    |
| 패키지      | `ansible.builtin.package` | `ansible.windows.win_package` |
| 서비스      | `ansible.builtin.service` | `ansible.windows.win_service` |
| 연결 테스트 | `ansible.builtin.ping`    | `ansible.windows.win_ping`    |
| 업데이트    | `ansible.builtin.apt/yum` | `ansible.windows.win_updates` |

---

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Ansible Docs — Windows Guide: [docs.ansible.com](https://docs.ansible.com/ansible/latest/os_guide/windows_usage.html) — ★★★☆☆
- Ansible Docs — Windows Modules: [docs.ansible.com](https://docs.ansible.com/ansible/latest/collections/ansible/windows/) — ★★★☆☆
- [windows_openssh_install.md](../../01_install/windows_openssh_install.md)

---

**작성일**: 2026-05-19

**마지막 업데이트**: 2026-05-19

© 2026 siasia86. Licensed under CC BY 4.0.

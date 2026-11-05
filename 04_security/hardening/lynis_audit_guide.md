# Lynis 서버 감사 가이드
<!-- reference: _reference/lynis_official_notes.md -->

## 목차

| 섹션                                                                              |
|-----------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치와 무결성 검증](#2-설치와-무결성-검증)               |
| [3. 실행](#3-실행) / [4. 결과 읽기](#4-결과-읽기)                                 |
| [5. 프로필](#5-프로필) / [6. 운영 인프라 적용](#6-운영-인프라-적용)               |
| [7. 결과 집계와 비교](#7-결과-집계와-비교) / [8. 조치 우선순위](#8-조치-우선순위) |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

Lynis는 Linux·macOS·BSD 등 UNIX 계열 시스템에서 직접 실행하는 보안 감사 도구입니다. 별도 에이전트나 서버 없이 셸 스크립트로 동작하며, 인증·커널·방화벽·SSH·로그·패키지·파일 무결성 등의 설정을 점검해 경고(warning)와 개선 제안(suggestion)을 냅니다. 운영 인프라에서는 서버 보안 상태의 기준선을 만들고, 변경 뒤 상태가 나빠지지 않았는지 정기적으로 비교하는 데 씁니다.

| 항목      | 내용                                     |
|-----------|------------------------------------------|
| 형태      | 셸 스크립트(컴파일·설치 없이 실행 가능)  |
| 라이선스  | GPL-3.0                                  |
| 최신 버전 | 3.1.7 (2026-06-25 배포, 2026-11-05 확인) |
| 테스트 수 | 447개(보안 442, 성능 4, 기본 1)          |
| GitHub    | https://github.com/CISOfy/lynis          |
| 공식 문서 | https://cisofy.com/documentation/lynis/  |

### 할 수 있는 것과 없는 것

| 구분            | 내용                                                                                    |
|-----------------|-----------------------------------------------------------------------------------------|
| 할 수 있는 것   | 로컬 설정 점검, 보안 업데이트 대기 패키지 확인, 강화 제안, 결과 파일 생성, 서버 간 비교 |
| 하지 않는 것    | 설정 자동 수정, 원격 무인 점검, 네트워크 포트 스캔, 취약점 익스플로잇                   |
| 오픈소스판 한계 | 웹 화면·대시보드·준수 보고서(PCI DSS·HIPAA·ISO27001 등)·개선 계획은 Enterprise판 기능   |

🟡 Lynis 결과는 "점검 항목에 대한 상태"이며 특정 규정(CIS Benchmark 등)의 준수 판정이 아닙니다. 규정 준수 증빙이 필요하면 해당 규정의 공식 점검 도구나 Enterprise판 준수 보고서를 따로 씁니다.

🟡 이 문서의 명령은 Lynis 3.1.7 소스와 공식 저장소 안내를 읽고 정리했으며 작성 시 Lynis를 실행하지 않았습니다. 확인 범위는 [Lynis 참조 노트](../../_reference/lynis_official_notes.md)에 기록했습니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 설치와 무결성 검증

### 설치 방법 고르기

| 방법                 | 장점                             | 주의                                                      |
|----------------------|----------------------------------|-----------------------------------------------------------|
| 배포판 패키지        | 설치가 간단                      | 오래된 버전일 수 있음(예: Ubuntu 24.04 기본 저장소 3.0.9) |
| CISOfy 공식 저장소   | 최신 버전, 서명된 저장소         | 서버가 많으면 사내 미러를 두라는 fair-use 정책            |
| 공식 tarball         | 설치 없이 실행, 폐쇄망 반입 쉬움 | SHA256·GPG 서명 확인 필요                                 |
| Git clone(태그 고정) | 버전 관리와 감사가 쉬움          | 실행 파일 소유자를 root로 바꿔야 함                       |

오래된 Lynis는 EOL 데이터베이스와 점검 항목도 오래되어 결과가 부정확해질 수 있습니다. Lynis 3.1.6부터는 6개월 이상 지난 릴리스를 오래된 것으로 보고 화면에 알립니다.

### CISOfy 저장소 (Debian/Ubuntu)

```bash
curl -fsSL https://packages.cisofy.com/keys/cisofy-software-public.key \
  | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/cisofy-software-public.gpg
echo "deb [arch=amd64,arm64 signed-by=/etc/apt/trusted.gpg.d/cisofy-software-public.gpg] https://packages.cisofy.com/community/lynis/deb/ stable main" \
  | sudo tee /etc/apt/sources.list.d/cisofy-lynis.list
sudo apt update
sudo apt install lynis

# 배포판 패키지가 대신 설치되지 않았는지 확인
apt-cache policy lynis
```

배포판 저장소의 옛 버전이 계속 선택되면 `/etc/apt/preferences.d/`에 pin 설정을 두어 CISOfy 저장소를 우선합니다.

### CISOfy 저장소 (RHEL 계열)

```ini
# /etc/yum.repos.d/cisofy-lynis.repo
[lynis]
name=CISOfy Software - Lynis package
baseurl=https://packages.cisofy.com/community/lynis/rpm/
enabled=1
gpgkey=https://packages.cisofy.com/keys/cisofy-software-rpms-public.key
gpgcheck=1
priority=2
```

```bash
sudo dnf makecache
sudo dnf install lynis
```

### 공식 tarball (폐쇄망·설치 없이 실행)

```bash
VERSION=3.1.7
curl -fsSLO "https://downloads.cisofy.com/lynis/lynis-${VERSION}.tar.gz"
curl -fsSLO "https://downloads.cisofy.com/lynis/lynis-${VERSION}.tar.gz.asc"

# 1) 다운로드 페이지에 게시된 SHA256과 비교
echo "b5314a07fd85fa3ffc7da57b508f0108ec3280d84e4af823f805d95cbbc2428c  lynis-${VERSION}.tar.gz" | sha256sum -c -

# 2) GPG 서명 확인 (주 키 지문 84FA A998 3B24 AEF2 4D6C 87F1 FEBB 7D18 1257 6482)
curl -fsSL https://packages.cisofy.com/keys/cisofy-software-public.key | gpg --import
gpg --verify "lynis-${VERSION}.tar.gz.asc" "lynis-${VERSION}.tar.gz"

# 3) root 소유로 풀기
sudo mkdir -p /opt/lynis
sudo tar -xzf "lynis-${VERSION}.tar.gz" -C /opt/lynis --strip-components=1
sudo chown -R 0:0 /opt/lynis
```

- SHA256 값은 버전마다 바뀝니다. 위 값은 3.1.7 기준이며 새 버전은 [다운로드 페이지](https://cisofy.com/downloads/lynis/)의 값을 확인합니다.
- `gpg --verify`는 `Good signature`와 주 키 지문을 함께 확인합니다. 키를 처음 가져올 때는 지문을 공식 페이지 등 별도 경로로 대조합니다.
- 일반 사용자 소유 파일을 root로 실행하면 그 사용자가 파일을 바꿔 root 권한을 얻을 수 있습니다. Lynis도 파일 권한이 맞지 않으면 경고합니다. 반드시 `chown -R 0:0` 후 실행합니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 실행

### 기본 점검

```bash
# 전체 점검 (root 권한 권장)
sudo lynis audit system

# 중간에 멈추지 않고 진행
sudo lynis audit system --quick

# 무인 실행용 (색 없음, 멈춤 없음)
sudo lynis audit system --cronjob

# tarball로 받은 경우
cd /opt/lynis && sudo ./lynis audit system --quick
```

### 범위 좁히기

```bash
# 특정 테스트만
sudo lynis audit system --tests "SSH-7408 AUTH-9230"

# 특정 그룹만 (예: ssh, authentication, firewalls, kernel, ports_packages)
sudo lynis audit system --tests-from-group ssh

# 그룹 목록과 테스트 설명
lynis show groups
lynis show tests SSH-7408
```

테스트 그룹은 `ports_packages`(41), `authentication`(36), `boot_services`(27), `nameservices`(23), `logging`(22), `filesystems`(20), `file_integrity`(18), `firewalls`(17), `accounting`(17), `kernel`(13), `ssh`(5) 등 39개입니다(괄호는 3.1.7 기준 테스트 수).

### 실행 모드와 주요 옵션

| 옵션                   | 설명                                                 |
|------------------------|------------------------------------------------------|
| `--quick`, `-Q`        | 사용자 입력을 기다리지 않음                          |
| `--cronjob`            | 무인 실행용(색 없음, 멈춤 없음)                      |
| `--pentest`            | 일반 사용자로 실행해 권한 상승 관점의 관심 지점 표시 |
| `--profile <파일>`     | 지정한 프로필로 점검                                 |
| `--report-file <파일>` | 보고서 경로(root 기본 `/var/log/lynis-report.dat`)   |
| `--log-file <파일>`    | 로그 경로(root 기본 `/var/log/lynis.log`)            |
| `--auditor <이름>`     | 보고서에 점검자 이름 기록                            |
| `--warnings-only`      | 경고만 표시                                          |
| `--no-colors`          | 색 없이 출력                                         |

- 일반 사용자로 실행하면 보고서와 로그가 홈 디렉토리(`~/lynis-report.dat`, `~/lynis.log`)에 생기고, 읽을 수 없는 파일은 점검하지 못해 결과가 줄어듭니다.
- 보고서 파일은 실행할 때마다 새로 써집니다. 이전 결과를 남기려면 `--report-file`로 날짜가 들어간 경로를 지정하거나 실행 뒤 복사합니다.
- `lynis audit system remote <host>`는 원격 서버를 직접 점검하지 않고, tarball 복사와 ssh 실행 단계를 화면에 안내만 합니다. 여러 서버 점검은 6절처럼 구성 관리 도구로 실행합니다.

### Dockerfile 점검

```bash
lynis audit dockerfile ./Dockerfile
```

컨테이너 이미지의 취약 패키지와 IaC 설정은 [Trivy 가이드](./trivy_guide.md)가 더 넓게 다룹니다.

[⬆ 목차로 돌아가기](#목차)

## 4. 결과 읽기

### 화면 출력

점검 끝에 다음 순서로 요약이 나옵니다.

1. **Warnings:** 바로 확인해야 할 문제. 테스트 ID와 함께 표시
2. **Suggestions:** 강화를 위한 제안. 대부분 여기에 쌓임
3. **Lynis security scan details:** Hardening index, 실행한 테스트 수, 사용 플러그인, 보고서·로그 경로

```bash
# 테스트 하나의 상세 로그 (점검 뒤 로그 파일에서 추출)
sudo lynis show details SSH-7408
```

### 보고서 파일 형식

`lynis-report.dat`는 한 줄에 `키=값` 하나인 텍스트 파일입니다. 같은 키가 여러 번 나오는 항목은 `키[]=값` 형식입니다.

| 키                      | 내용                                  |
|-------------------------|---------------------------------------|
| `hostname`              | 점검한 호스트 이름                    |
| `lynis_version`         | Lynis 버전                            |
| `os_name`, `os_version` | 운영체제와 버전                       |
| `report_datetime_start` | 점검 시작 시각(`YYYY-MM-DD HH:MM:SS`) |
| `hardening_index`       | Hardening index(0~100)                |
| `lynis_tests_done`      | 실행한 테스트 수                      |
| `warning[]`             | `테스트ID\|메시지\|상세\|해결 방법\|` |
| `suggestion[]`          | `테스트ID\|메시지\|상세\|해결 방법\|` |
| `vulnerable_package[]`  | 보안 업데이트가 필요한 패키지         |
| `manual[]`              | 사람이 직접 확인해야 할 항목          |

```bash
sudo grep -E '^(hardening_index|lynis_version)=' /var/log/lynis-report.dat
sudo grep '^warning\[\]=' /var/log/lynis-report.dat | cut -d'|' -f1,2
```

### Hardening index

Hardening index는 각 테스트가 준 강화 점수의 합을 최대 점수의 합으로 나눈 값(`점수 합 × 100 / 최대 합`)입니다. 화면 색과 설명은 소스 기준으로 다음과 같습니다.

| 범위   | 화면 설명                                                    |
|--------|--------------------------------------------------------------|
| 0~49   | System has not or a low amount been hardened                 |
| 50~79  | System has been hardened, but could use additional hardening |
| 80~89  | System seem to be decent hardened                            |
| 90~100 | System seem to be well hardened                              |

🟡 소스 주석은 이 값이 "첫인상이나 비슷한 시스템끼리 비교하는 용도"이며 최고점이어도 보안 문제가 없다는 뜻은 아니라고 밝힙니다. 실행한 테스트가 서버마다 다르면(설치된 서비스가 다르면) 최대 점수도 달라지므로, 역할이 다른 서버의 점수를 그대로 비교하지 않습니다. 점수 목표보다 경고 0건과 합의한 제안 처리를 목표로 둡니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 프로필

### 위치와 원칙

- 기본 프로필 `default.prf`는 고치지 않고, 바꿀 내용만 같은 디렉토리의 `custom.prf`에 적습니다.
- 프로필은 `/usr/local/etc/lynis`, `/etc/lynis`, `/usr/local/lynis`, 현재 디렉토리 순으로 찾습니다. 실제 위치는 `lynis show profiles`로 확인합니다.
- Lynis는 해로운 값이 들어가지 않도록 프로필을 엄격하게 검사합니다. 형식이 틀린 줄은 무시되거나 경고가 납니다.

### custom.prf 예

```ini
# /etc/lynis/custom.prf
# 웹 서버 역할 기준 프로필. 예외마다 사유와 재검토일을 주석으로 남깁니다.

machine-role=server
profile-name=Web server baseline

# 경고가 하나라도 있으면 종료 코드 78 반환 (CI·자동화에서 실패 처리)
error-on-warnings=yes

# 업그레이드 확인을 끔 (폐쇄망, 버전은 별도 관리)
skip-upgrade-test=yes

# 사유: 원격 관리망 전용 서버라 SSH 포워딩 필요 (재검토 2027-05-01, 담당 플랫폼팀)
skip-test=SSH-7408:allowtcpforwarding

# 사유: 백업 장비로 iptables 대신 상위 방화벽에서 차단 (재검토 2027-05-01)
skip-test=FIRE-4512

# 인증서 점검 경로 추가
ssl-certificate-paths=/etc/ssl:/etc/pki:/opt/app/certs
```

| 설정                     | 기본값    | 설명                                                  |
|--------------------------|-----------|-------------------------------------------------------|
| `skip-test`              | 없음      | 테스트 전체(`ID`) 또는 테스트 안 항목(`ID:항목`) 제외 |
| `error-on-warnings`      | `no`      | `yes`면 경고가 있을 때 종료 코드 78                   |
| `machine-role`           | `server`  | 시스템 역할                                           |
| `test-scan-mode`         | `full`    | 점검 깊이(`light`, `normal`, `full`)                  |
| `skip-upgrade-test`      | `no`      | Lynis 업그레이드 확인 생략                            |
| `ssl-certificate-paths`  | 여러 경로 | 인증서를 찾을 디렉토리(콜론 구분)                     |
| `skip-plugins`           | `no`      | 플러그인 실행 생략                                    |
| `config-data=sysctl;...` | 다수      | 기대하는 커널 파라미터 값(KRNL-6000에서 비교)         |

- `skip-test`는 점검을 없애는 것이므로 결과를 좋게 보이게 하는 용도로 쓰지 않습니다. 대신 위험을 다른 방법으로 통제한다는 근거를 주석으로 남기고 정기적으로 재검토합니다.
- 제외된 테스트 목록은 `lynis show tests skipped`, 적용된 설정은 `lynis show settings`로 확인합니다.
- 서버 역할(웹, DB, 배치, 점프 서버)마다 프로필을 나누고 구성 관리 도구로 배포합니다. 프로필 파일도 코드 리뷰를 거쳐 바꿉니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 운영 인프라 적용

### 적용 단계

| 단계         | 할 일                                               | 완료 기준                              |
|--------------|-----------------------------------------------------|----------------------------------------|
| 1. 시범      | 역할별 대표 서버 한두 대에서 실행하고 결과를 검토   | 경고·제안 목록과 처리 방향 합의        |
| 2. 프로필    | 역할별 `custom.prf` 작성, 예외에 사유·재검토일 기록 | 프로필이 저장소에서 리뷰됨             |
| 3. 기준선    | 같은 역할 서버 전체를 실행해 첫 결과를 보관         | 서버별 index·경고·제안 수 기록         |
| 4. 정기 점검 | 주 1회 등 정해진 주기로 실행하고 결과를 수집        | 직전 결과와 비교해 새 경고를 알림      |
| 5. 변경 연계 | OS 업그레이드·이미지 교체·강화 작업 뒤 재점검       | 변경 전후 비교 결과를 변경 기록에 첨부 |

### 정기 실행 (systemd timer)

```ini
# /etc/systemd/system/lynis-audit.service
[Unit]
Description=Lynis security audit

[Service]
Type=oneshot
ExecStart=/bin/sh -c '/usr/bin/lynis audit system --cronjob --report-file /var/log/lynis/report-$$(date +%%Y%%m%%d).dat --log-file /var/log/lynis/lynis-$$(date +%%Y%%m%%d).log'
Nice=19
IOSchedulingClass=idle
```

```ini
# /etc/systemd/system/lynis-audit.timer
[Unit]
Description=Weekly Lynis security audit

[Timer]
OnCalendar=Sun 03:00
RandomizedDelaySec=1h
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
sudo install -d -m 0750 /var/log/lynis
sudo systemctl daemon-reload
sudo systemctl enable --now lynis-audit.timer
```

- systemd unit 안에서는 `%`를 `%%`로, `$`를 `$$`로 써야 셸에 그대로 전달됩니다.
- 점검은 파일을 많이 읽으므로 업무 시간대를 피하고 `Nice`·I/O 우선순위를 낮춥니다. 여러 서버가 동시에 돌지 않도록 `RandomizedDelaySec`를 둡니다.
- 보고서와 로그에는 계정·패키지·설정 정보가 들어가므로 권한을 `0750` 이하로 두고, 보관 기간과 삭제 규칙을 정합니다.
- `error-on-warnings=yes`면 경고가 있을 때 서비스가 실패 상태(종료 코드 78)로 남습니다. systemd 실패 알림이나 모니터링으로 감지할 수 있습니다.

### 여러 서버에서 실행과 수집

구성 관리 도구로 실행하고 결과를 한곳에 모읍니다. 다음은 Ansible 예입니다.

```yaml
# lynis_audit.yml
- hosts: linux_servers
  become: true
  vars:
    report: "/var/log/lynis/report-{{ ansible_date_time.date }}.dat"
  tasks:
    - name: Lynis 점검
      ansible.builtin.command: >
        lynis audit system --cronjob --report-file {{ report }}
      register: lynis_run
      changed_when: false
      failed_when: lynis_run.rc not in [0, 78]

    - name: 보고서 수집
      ansible.builtin.fetch:
        src: "{{ report }}"
        dest: "reports/{{ inventory_hostname }}-{{ ansible_date_time.date }}.dat"
        flat: true
```

- 종료 코드 78(경고 있음)은 점검 자체의 실패가 아니므로 수집은 계속하고, 경고는 7절의 집계로 판단합니다.
- 수집한 보고서는 접근이 제한된 저장소에 둡니다. 공개 저장소나 공용 채팅에 붙이지 않습니다.
- Ansible 기본 사용법은 [Ansible 기본 가이드](../../02_infrastructure/iac/ansible_basic_guide.md)를 참고합니다.

[⬆ 목차로 돌아가기](#목차)

## 7. 결과 집계와 비교

### 서버별 요약

```bash
#!/usr/bin/env bash
# lynis_report_summary.sh - 수집한 lynis-report.dat 여러 개를 호스트별 요약표(TSV)로 정리
# 사용: lynis_report_summary.sh <report.dat>...
# 출력: host, lynis 버전, 점검 시작 시각, hardening index, 경고 수, 제안 수, 실행 테스트 수
set -u

printf 'host\tversion\tstarted\tindex\twarnings\tsuggestions\ttests\n'
for f in "$@"; do
    awk -F= '
        $1 == "hostname"              { host = $2 }
        $1 == "lynis_version"         { ver = $2 }
        $1 == "report_datetime_start" { start = $2 }
        $1 == "hardening_index"       { idx = $2 }
        $1 == "lynis_tests_done"      { tests = $2 }
        $1 == "warning[]"             { w++ }
        $1 == "suggestion[]"          { s++ }
        END { printf "%s\t%s\t%s\t%s\t%d\t%d\t%s\n", host, ver, start, idx, w, s, tests }
    ' "${f}"
done
```

```bash
./lynis_report_summary.sh reports/*.dat | column -t -s $'\t'
```

```text
host   version  started              index  warnings  suggestions  tests
web01  3.1.7    2026-11-01 03:00:01  63     2         2            268
web01  3.1.7    2026-11-08 03:00:02  66     1         3            268
```

### 직전 결과와 비교

```bash
# 테스트 ID와 상세만 뽑아 비교: ">"는 새로 생긴 항목, "<"는 사라진 항목
items() { grep -E '^(warning|suggestion)\[\]=' "$1" | cut -d'|' -f1,3 | sort; }
diff <(items reports/web01-2026-11-01.dat) <(items reports/web01-2026-11-08.dat)
```

```text
1a2
> suggestion[]=KRNL-6000|-
4d4
< warning[]=PKGS-7392|-
```

- 새로 생긴 경고(`> warning[]`)는 변경 작업이나 설정 이탈의 신호이므로 알림 대상입니다.
- 버전이 바뀌면 테스트 구성이 달라져 비교 결과에 섞입니다. Lynis 버전은 서버 전체에서 같게 맞추고, 버전을 올린 회차는 새 기준선으로 봅니다.
- 위 출력은 3.1.7 소스의 보고서 형식대로 만든 예시 파일로 시험한 결과입니다.

[⬆ 목차로 돌아가기](#목차)

## 8. 조치 우선순위

1. **경고(warning):** 먼저 처리합니다. 보안 업데이트 대기 패키지(`PKGS-7392` 등), 방화벽 규칙 없음, 위험한 서비스가 대표적입니다.
2. **보안 업데이트:** `vulnerable_package[]`와 패키지 그룹 결과는 패치 계획에 넣습니다. 컨테이너 이미지 안의 패키지는 [Trivy 가이드](./trivy_guide.md)로 따로 봅니다.
3. **제안(suggestion):** 서버 역할에 맞는지 검토해 적용·보류·예외로 나눕니다. 한 번에 많이 바꾸지 말고 역할별로 묶어 변경 관리를 거칩니다.
4. **재점검:** 조치 뒤 같은 프로필로 다시 실행해 항목이 사라졌는지 확인합니다.

| 결과 분야             | 참고 문서                                                      |
|-----------------------|----------------------------------------------------------------|
| SSH(`SSH-*`)          | [SSH 보안](./ssh_security.md)                                  |
| 커널·sysctl(`KRNL-*`) | [Linux 서버 보안 강화](./linux_hardening.md)                   |
| 감사 로그(`ACCT-*`)   | [Linux 서버 보안 강화](./linux_hardening.md)의 auditd 절       |
| 방화벽(`FIRE-*`)      | [방화벽 iptables/nftables](./firewall_iptables_nftables.md)    |
| 인증서(`CRYP-*`)      | [TLS 인증서 만료 감시](./tls_certificate_expiry_monitoring.md) |

🟡 제안을 그대로 모두 적용하면 서비스가 멈출 수 있습니다(예: 필요한 커널 모듈 차단, SSH 옵션 변경으로 관리 접속 차단). 시범 서버에서 먼저 적용하고 접속 경로를 확보한 상태에서 바꿉니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- Lynis: [github.com/CISOfy/lynis](https://github.com/CISOfy/lynis) — ★★★★☆
- Lynis 공식 문서: [cisofy.com/documentation/lynis](https://cisofy.com/documentation/lynis/) — ★★★★☆
- CISOfy 소프트웨어 저장소: [packages.cisofy.com/community](https://packages.cisofy.com/community/) — ★★★★☆
- Lynis 다운로드: [cisofy.com/downloads/lynis](https://cisofy.com/downloads/lynis/) — ★★★★☆
- 확인 기록: [Lynis 참조 노트](../../_reference/lynis_official_notes.md)
- 관련 문서: [취약점 스캔 개요](./vulnerability_scanning.md), [Linux 서버 보안 강화](./linux_hardening.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-05

**마지막 업데이트**: 2026-11-05

© 2026 siasia86. Licensed under CC BY 4.0.

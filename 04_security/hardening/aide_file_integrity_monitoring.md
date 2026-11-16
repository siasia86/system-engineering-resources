# AIDE 파일 무결성 감시 가이드

AIDE(Advanced Intrusion Detection Environment)는 파일의 권한·소유자·크기·해시 같은 속성을 기준 데이터베이스로 저장해 두고, 나중에 다시 비교해 바뀐 파일을 알려 주는 파일 무결성 감시(FIM, File Integrity Monitoring) 도구입니다. 이 문서는 설치·초기화·정기 점검·변경 승인 흐름과 오탐을 줄이는 규칙 작성법을 다룹니다.

## 목차

| 섹션                                                                                  |
|---------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치와 기준 DB 만들기](#2-설치와-기준-db-만들기)             |
| [3. 설정 파일 구조](#3-설정-파일-구조) / [4. 규칙 작성](#4-규칙-작성)                 |
| [5. 점검과 결과 읽기](#5-점검과-결과-읽기) / [6. 정기 실행](#6-정기-실행)             |
| [7. 변경 승인과 DB 갱신](#7-변경-승인과-db-갱신) / [8. 기준 DB 보호](#8-기준-db-보호) |
| [9. 운영 점검표](#9-운영-점검표)                                                      |

---

## 1. 개요

### 무엇을 잡아내는가

AIDE는 "지금 파일이 기준 시점과 다른가"만 판단합니다. 침입 여부를 직접 판정하지 않으므로, 바뀐 파일이 승인된 변경(패키지 갱신·설정 배포)인지 아닌지는 운영자가 변경 기록과 대조해 판단합니다.

| 감시 대상 예                              | 바뀌면 의심할 상황             |
|-------------------------------------------|--------------------------------|
| `/bin`, `/sbin`, `/usr/bin`, `/lib*`      | 실행 파일 교체, 루트킷 설치    |
| `/etc/passwd`, `/etc/shadow`, `sudoers`   | 계정 추가, 권한 상승 경로 생성 |
| `/etc/ssh/sshd_config`, `authorized_keys` | 원격 접속 경로 추가            |
| `/etc/cron*`, systemd unit 경로           | 지속 실행(persistence) 등록    |
| `/etc/ld.so.preload`                      | 공유 라이브러리 강제 적재      |

### 다른 도구와의 역할 구분

| 도구                  | 시점              | 알려 주는 것                          |
|-----------------------|-------------------|---------------------------------------|
| AIDE                  | 주기적 비교(사후) | 기준 대비 파일 속성·해시 변화         |
| auditd                | 실시간 기록       | 누가·언제·어떤 시스템 호출로 바꿨는가 |
| 패키지 검증(`rpm -V`) | 필요할 때         | 패키지가 설치한 파일의 원본 대비 변화 |
| Lynis                 | 주기적 감사       | 설정 상태와 권고 사항                 |

AIDE로 "무엇이 바뀌었는지"를 찾고, [auditd 규칙](./auditd_rules_and_search_guide.md)으로 "누가 바꿨는지"를 찾는 식으로 함께 씁니다. Lynis 감사는 [Lynis 서버 감사 가이드](./lynis_audit_guide.md)에서 다룹니다.

### 판 정보

2026-11-16 확인 시 AIDE 공식 GitHub Releases의 최신 판은 v0.19.5입니다. v0.19에서 설정 이름 일부가 바뀌었으므로(3절) 배포판 패키지 판을 먼저 확인합니다.

```bash
aide --version        # 판, 기본 설정 파일, 기본 database_in/out 경로 표시
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치와 기준 DB 만들기

기준 DB는 "깨끗하다고 믿을 수 있는 시점"에 만들어야 의미가 있습니다. 이미 침해가 의심되는 서버에서 처음 만들면 변조된 상태가 기준이 됩니다. 새로 설치하고 서비스에 넣기 전, 또는 이미지 빌드 직후가 적절합니다.

### RHEL 계열 (Rocky·Alma 포함)

```bash
sudo dnf install aide
sudo aide --init                                         # /var/lib/aide/aide.db.new.gz 생성
sudo mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz   # .new를 빼야 점검에 쓰임
sudo aide --check
```

설정 파일은 `/etc/aide.conf`이며, DB 위치는 그 안의 `DBDIR` 값으로 정합니다.

### Debian·Ubuntu

```bash
sudo apt install aide
sudo aideinit                 # /var/lib/aide/aide.db.new 생성 후 교체 여부를 물음
# 묻지 않고 교체하려면: sudo aideinit -y -f
```

설정은 `/etc/aide/aide.conf`와 `/etc/aide/aide.conf.d/` 아래 조각 파일로 나뉩니다. 기준 DB 기본 위치는 `/var/lib/aide/aide.db`, 새로 만든 DB는 `/var/lib/aide/aide.db.new`입니다.

### 초기화 전 확인

```bash
# 설정 문법만 검사하고 끝냄
sudo aide --config-check

# 실제 DB를 만들지 않고 어떤 파일이 규칙에 걸리는지 출력 (v0.17 이상)
sudo aide --dry-init | head -50
```

`--init`은 감시 범위가 넓으면 수 분 이상 걸리고 디스크 읽기가 많습니다. 운영 중인 서버라면 부하가 낮은 시간에 실행합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 설정 파일 구조

### 주요 설정 항목

| 항목                       | 기본값                | 의미                                             |
|----------------------------|-----------------------|--------------------------------------------------|
| `database_in`              | `aide --version` 참고 | 점검 때 읽는 기준 DB                             |
| `database_out`             | `aide --version` 참고 | `--init`·`--update`가 쓰는 새 DB                 |
| `database_new`             | 없음                  | `--compare`에서 비교할 다른 DB                   |
| `gzip_dbout`               | `false`               | 새 DB를 gzip으로 압축                            |
| `report_url`               | `stdout`              | 결과 출력 위치, 여러 번 지정 가능                |
| `report_level`             | `changed_attributes`  | 결과 상세도                                      |
| `report_summarize_changes` | `true`                | 변경 요약 표시 (옛 이름 `summarize_changes`)     |
| `report_grouped`           | `true`                | 추가·삭제·변경으로 묶어 표시 (옛 이름 `grouped`) |

🟡 v0.19에서 `database`(→ `database_in`), `summarize_changes`, `grouped` 설정이 제거되었습니다. 예전 블로그 설정을 그대로 가져오면 설정 오류가 나므로 `aide --config-check`로 먼저 확인합니다.

### URL 형식

`report_url`·`database_*` 값은 URL 형식입니다.

| 형식                | 쓰임                   |
|---------------------|------------------------|
| `file:/path`        | 파일 읽기·쓰기         |
| `stdout`, `stderr`  | 표준 출력·표준 오류    |
| `syslog:LOG_LOCAL1` | syslog 출력(출력 전용) |
| `fd:3`              | 이미 열린 파일 서술자  |

```text
database_in=file:/var/lib/aide/aide.db.gz
database_out=file:/var/lib/aide/aide.db.new.gz
gzip_dbout=yes
report_url=file:/var/log/aide/aide.log
report_url=stdout
```

### 매크로

| 줄                 | 의미                                    |
|--------------------|-----------------------------------------|
| `@@define VAR 값`  | 변수 정의, `@@{VAR}`로 참조             |
| `@@undef VAR`      | 변수 해제                               |
| `@@include FILE`   | 다른 설정 파일을 그 자리에 포함         |
| `@@x_include FILE` | 실행 파일이면 실행 결과를 설정으로 사용 |

`@@x_include`는 실행 결과를 설정으로 쓰므로, 그 파일과 디렉터리는 root만 쓸 수 있게 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 규칙 작성

### 속성과 기본 그룹

규칙은 `<정규식> <속성 식>` 형태입니다. 속성은 `+`로 묶습니다.

| 속성            | 의미                  | 속성        | 의미             |
|-----------------|-----------------------|-------------|------------------|
| `p`             | 권한                  | `u`, `g`    | 소유 사용자·그룹 |
| `i`             | inode                 | `n`         | 링크 수          |
| `s`             | 크기                  | `m`         | 수정 시각(mtime) |
| `c`             | 상태 변경 시각(ctime) | `a`         | 접근 시각(atime) |
| `ftype`         | 파일 종류             | `l`         | 심볼릭 링크 대상 |
| `acl`, `xattrs` | ACL, 확장 속성        | `selinux`   | SELinux 문맥     |
| `caps`          | 파일 capability       | `sha256` 등 | 내용 해시        |

v0.19 기준 기본 그룹은 다음과 같습니다.

| 그룹 | 정의                                 | 쓰임                      |
|------|--------------------------------------|---------------------------|
| `R`  | `p+ftype+i+l+n+u+g+s+m+c+sha3_256+X` | 바뀌면 안 되는 파일(기본) |
| `L`  | `p+ftype+i+l+n+u+g+X`                | 내용은 바뀌어도 되는 파일 |
| `>`  | `p+ftype+l+u+g+i+n+s+growing+X`      | 계속 커지는 로그 파일     |
| `X`  | `acl+selinux+xattrs+e2fsattrs+caps`  | 확장 속성 묶음            |
| `E`  | 빈 그룹                              | 존재 여부만 확인          |

v0.19에서 `R`의 기본 해시가 md5에서 sha3_256으로 바뀌었고, md5·sha1은 폐지 예정입니다. 직접 그룹을 만들 때도 `sha256`이나 `sha512`를 씁니다.

🟡 `a`(atime)는 읽기만 해도 바뀌므로 넣으면 오탐이 많습니다.

### 선택 줄 종류

| 접두 | 동작                                                             |
|------|------------------------------------------------------------------|
| `/`  | 일치하는 파일·디렉터리를 DB에 추가 (앞에 `^`가 붙은 것으로 처리) |
| `=`  | 일치 항목만 추가, 하위는 정규식이 `/`로 끝날 때 한 단계만        |
| `!`  | 일치 항목 제외, 하위는 계속 규칙과 비교 (재귀 제외)              |
| `-`  | 일치 항목 제외, 하위로 내려가지 않음 (v0.19 추가)                |

### 예시 설정

```text
@@define DBDIR /var/lib/aide
database_in=file:@@{DBDIR}/aide.db.gz
database_out=file:@@{DBDIR}/aide.db.new.gz
gzip_dbout=yes
report_url=file:/var/log/aide/aide.log

# 사용자 정의 그룹
BIN = p+ftype+i+n+u+g+s+m+c+sha256+X
CONF = p+ftype+i+n+u+g+s+m+c+sha256
LOGS = p+ftype+u+g+i+n+growing+s

/usr/bin     BIN
/usr/sbin    BIN
/usr/lib     BIN
/etc         CONF
/root/\.ssh  CONF
/var/log     LOGS

# 자주 바뀌어 오탐을 만드는 경로는 제외
!/etc/mtab$
-/var/log/journal
-/var/cache
```

경로 정규식에서 `.`은 "아무 글자"이므로 실제 점은 `\.`로 씁니다. 한 파일만 정확히 가리킬 때는 끝에 `$`를 붙입니다.

### 오탐 줄이기 기준

| 상황                           | 처리                                 |
|--------------------------------|--------------------------------------|
| 내용이 자주 바뀌는 설정        | `L` 계열로 내리고 소유자·권한만 감시 |
| 회전되는 로그                  | `growing` 속성 그룹 또는 제외        |
| 캐시·임시 디렉터리             | `-`로 하위까지 제외                  |
| 배포 도구가 매번 덮어쓰는 파일 | 배포 후 DB 갱신 절차에 포함(7절)     |

제외를 넓게 잡으면 그 경로는 감시하지 않는 것과 같습니다. 제외 사유를 설정 주석에 남깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 점검과 결과 읽기

```bash
sudo aide --check
echo $?          # 종료 코드 확인
```

### 종료 코드

`--check`·`--update`·`--compare`의 종료 코드는 비트 합으로 결과를 나타냅니다.

| 값    | 의미                                |
|-------|-------------------------------------|
| 0     | 차이 없음                           |
| 1     | 새 파일 있음                        |
| 2     | 삭제된 파일 있음                    |
| 4     | 변경된 파일 있음                    |
| 5~7   | 위 값의 합 (예: 5 = 새 파일 + 변경) |
| 14~25 | 쓰기·설정·입출력·DB 등 실행 오류    |

| 오류 코드 | 의미                    | 오류 코드 | 의미           |
|-----------|-------------------------|-----------|----------------|
| 14        | 쓰기 오류               | 17        | 설정 오류      |
| 18        | 입출력 오류             | 19        | 판 불일치      |
| 21        | 파일 잠금 오류          | 24        | DB 오류(v0.19) |
| 25        | 신호를 받아 중단(v0.19) |           |                |

감시 스크립트는 `0`이면 정상, `1~7`이면 변경 검토, `14` 이상이면 점검 자체가 실패한 것으로 나눠 알립니다. 점검 실패를 "변경 없음"으로 처리하지 않습니다.

### 특정 경로만 점검

```bash
# /etc 아래만 비교 (정규식은 시작 위치에서만 일치)
sudo aide --check --limit /etc
```

### 결과 판단 순서

1. 변경 목록을 변경 관리 기록(배포·패키지 갱신·작업 요청)과 대조합니다.
2. 실행 파일 변경은 패키지 검증으로 원본 여부를 확인합니다.

```bash
rpm -Vf /usr/bin/ssh          # RHEL 계열: 해당 파일을 가진 패키지 검증
dpkg --verify openssh-client  # Debian 계열
```

3. 설명되지 않는 변경은 auditd 기록으로 변경 주체를 찾고, 필요하면 [침해 의심 서버 초동 점검](./linux_intrusion_triage_checklist.md) 절차로 넘깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 정기 실행

### Debian·Ubuntu

Debian 계열 `aide-common` 패키지는 매일 점검하는 `dailyaidecheck.timer`를 제공합니다. 설치 판에 따라 동작이 다를 수 있으므로 실제 unit을 확인합니다.

```bash
systemctl cat dailyaidecheck.timer
sudo systemctl enable --now dailyaidecheck.timer
systemctl list-timers | grep aide
```

### systemd timer 직접 만들기 (RHEL 계열 등)

배포판이 timer를 제공하지 않으면 직접 만듭니다.

```ini
# /etc/systemd/system/aide-check.service
[Unit]
Description=AIDE integrity check

[Service]
Type=oneshot
ExecStart=/usr/sbin/aide --check
Nice=19
IOSchedulingClass=idle
# 1~7(변경 발견)도 실패로 남겨 알림 대상이 되게 둠
```

```ini
# /etc/systemd/system/aide-check.timer
[Unit]
Description=Daily AIDE integrity check

[Timer]
OnCalendar=*-*-* 03:30:00
RandomizedDelaySec=30min
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now aide-check.timer
journalctl -u aide-check.service -n 50
```

여러 서버를 같은 시각에 돌리면 공유 스토리지·가상화 호스트에 읽기 부하가 몰리므로 `RandomizedDelaySec`로 흩어 놓습니다.

### 알림 연결

| 방식             | 방법                                        |
|------------------|---------------------------------------------|
| 서비스 실패 알림 | `OnFailure=`로 알림 unit 연결               |
| 로그 수집        | `report_url=syslog:LOG_LOCAL1` 후 중앙 수집 |
| 모니터링 지표    | 종료 코드·마지막 성공 시각을 지표로 내보냄  |

"점검이 며칠째 돌지 않음"도 알림 대상입니다. 마지막 성공 시각이 1일 이상 지나면 경고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 변경 승인과 DB 갱신

승인된 변경 뒤에는 기준 DB를 갱신해야 다음 점검에서 같은 변경이 반복 보고되지 않습니다.

```bash
# 1. 현재 변경 내용을 확인하면서 새 DB 생성
sudo aide --update > /tmp/aide-update-$(date +%F).txt
# 2. 결과 파일을 검토해 승인된 변경만 있는지 확인
# 3. 이전 DB를 보관하고 새 DB로 교체
sudo cp -a /var/lib/aide/aide.db.gz /var/lib/aide/aide.db.gz.$(date +%F)
sudo mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz
```

🟡 검토 없이 `--update`와 교체를 자동으로 이어 붙이면, 공격자가 만든 변경도 기준 DB에 흡수됩니다. 자동 갱신은 배포 파이프라인처럼 변경 내용이 기록되는 경로에서만 쓰고, 그 경우에도 갱신 전 결과를 보관합니다.

### 패키지 갱신과 묶기

| 방식                            | 장점                         | 주의                            |
|---------------------------------|------------------------------|---------------------------------|
| 패치 작업 직후 수동 갱신        | 변경 내용을 사람이 확인      | 갱신을 잊으면 다음 날 대량 경보 |
| 구성 관리 도구 작업 마지막 단계 | 누락이 적음                  | 결과 파일 보관 단계를 넣어야 함 |
| 불변 이미지 재배포              | DB를 이미지와 함께 다시 생성 | 이미지 빌드 환경을 신뢰해야 함  |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 기준 DB 보호

공격자가 root 권한을 얻으면 같은 서버의 AIDE DB와 바이너리도 바꿀 수 있습니다. 그래서 기준 DB와 비교 결과는 감시 대상 서버 밖에도 둡니다.

| 방법                         | 설명                                                |
|------------------------------|-----------------------------------------------------|
| DB 해시를 외부에 기록        | 초기화·갱신 때 `sha256sum aide.db.gz`를 중앙에 저장 |
| DB 사본을 외부 저장소에 보관 | 점검 전 외부 사본과 해시 비교                       |
| 읽기 전용 매체에서 실행      | 별도 매체의 aide 바이너리·설정·DB로 점검            |
| 중앙 비교(`--compare`)       | 각 서버에서 만든 DB를 중앙 호스트로 모아 비교       |
| 결과를 즉시 외부로 전송      | syslog 중앙 수집으로 결과 삭제·변조에 대비          |

```bash
# 기준 DB 해시 기록 (중앙 저장소에 보관)
sha256sum /var/lib/aide/aide.db.gz
# 점검 전 비교
sha256sum -c aide.db.gz.sha256
```

aide 실행 파일과 설정 파일(`/etc/aide.conf` 또는 `/etc/aide/`)도 감시 규칙에 포함합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 운영 점검표

| 항목                                   | 확인 방법                                   |
|----------------------------------------|---------------------------------------------|
| 기준 DB가 존재하고 최근 승인 변경 반영 | `ls -l /var/lib/aide/`, 갱신 기록           |
| 설정 문법 오류 없음                    | `aide --config-check`                       |
| 핵심 경로가 규칙에 포함                | `aide --dry-init`로 `/etc`, `/usr/bin` 확인 |
| 제외 경로마다 사유 주석                | 설정 파일 검토                              |
| 정기 점검이 실제로 돌고 있음           | `systemctl list-timers`, 마지막 실행 로그   |
| 종료 코드 14 이상을 실패로 알림        | 알림 규칙 확인                              |
| DB 해시·사본이 서버 밖에 있음          | 중앙 저장소 확인                            |
| 판 갱신 후 제거된 설정 이름 미사용     | `aide --version`, `--config-check`          |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- AIDE 공식 저장소·Releases(최신 v0.19.5 확인): [github.com/aide/aide](https://github.com/aide/aide/releases) (확인일 2026-11-16) — ★★★☆☆
- aide(1) man page(명령·종료 코드): [github.com/aide/aide](https://github.com/aide/aide/blob/master/doc/aide.1) (확인일 2026-11-16) — ★★★☆☆
- aide.conf(5) man page(설정·규칙·기본 그룹): [github.com/aide/aide](https://github.com/aide/aide/blob/master/doc/aide.conf.5) (확인일 2026-11-16) — ★★★☆☆
- AIDE Manual: [aide.github.io](https://aide.github.io/doc/) (확인일 2026-11-16) — ★★★☆☆
- Ubuntu aideinit(8): [manpages.ubuntu.com](https://manpages.ubuntu.com/manpages/noble/man8/aideinit.8.html) (확인일 2026-11-16) — ★★★☆☆
- Debian aide 패키지 dailyaidecheck.timer: [sources.debian.org](https://sources.debian.org/src/aide/0.19.2-3/debian/aide-common.dailyaidecheck.timer) (확인일 2026-11-16) — ★★★☆☆
- Red Hat RHEL 9 Security Hardening, Checking integrity with AIDE: [docs.redhat.com](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/security_hardening/checking-integrity-with-aide_security-hardening) (확인일 2026-11-16) — ★★★☆☆

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.

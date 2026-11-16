# auditd 감사 규칙과 로그 조회 가이드

auditd는 Linux 커널 감사(audit) 기능이 만든 기록을 디스크에 남기는 사용자 공간 데몬입니다. 이 문서는 [Linux 서버 보안 강화](./linux_hardening.md)의 auditd 절을 이어서, 규칙 파일 구성·성능을 고려한 규칙 작성·`ausearch`/`aureport` 조회·로그 보존 설정을 다룹니다.

## 목차

| 섹션                                                                                                      |
|-----------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 상태 확인과 규칙 적용 구조](#2-상태-확인과-규칙-적용-구조)                       |
| [3. 규칙 문법](#3-규칙-문법) / [4. 목적별 규칙 예시](#4-목적별-규칙-예시)                                 |
| [5. 성능과 잡음 줄이기](#5-성능과-잡음-줄이기) / [6. ausearch 조회](#6-ausearch-조회)                     |
| [7. aureport 요약](#7-aureport-요약) / [8. 로그 보존과 디스크 부족 대응](#8-로그-보존과-디스크-부족-대응) |
| [9. 운영 점검표](#9-운영-점검표)                                                                          |

---

## 1. 개요

### 구성 요소

```text
 kernel audit subsystem ---> auditd ---> /var/log/audit/audit.log
        ^                       |
        |                       +---> plugins (audisp: syslog, remote)
   auditctl / augenrules
   (load rules)                 ausearch / aureport (read logs)
```

| 구성 요소      | 역할                                              |
|----------------|---------------------------------------------------|
| 커널 감사 기능 | 규칙에 맞는 시스템 호출·파일 접근을 이벤트로 만듦 |
| `auditd`       | 이벤트를 받아 로그 파일에 기록                    |
| `auditctl`     | 규칙을 커널에 직접 넣고 상태를 조회               |
| `augenrules`   | `/etc/audit/rules.d/*.rules`를 합쳐 적재          |
| `ausearch`     | 조건으로 이벤트 검색                              |
| `aureport`     | 이벤트 종류별 요약 보고                           |

### 판 정보

2026-11-16 확인 시 upstream(linux-audit/audit-userspace) 최신 판은 audit-4.2.1이고, Ubuntu 24.04 패키지는 3.1.2입니다. 이 문서의 명령은 3.x와 4.x에 공통인 것만 씁니다. 세부 옵션은 설치된 man page(`man auditctl`)로 확인합니다.

### auditd로 답할 수 있는 질문

| 질문                                  | 쓰는 정보                      |
|---------------------------------------|--------------------------------|
| `/etc/sudoers`를 누가 언제 바꿨나     | 파일 감시 규칙 + 키            |
| sudo로 바꾼 사람의 원래 로그인 계정은 | `auid`(로그인 사용자 ID)       |
| 커널 모듈이 적재되었나                | `init_module` 계열 시스템 호출 |
| 권한 없는 파일 접근 시도가 몰렸나     | 실패한 `openat` 기록           |

`auid`는 처음 로그인한 사용자 ID로, `sudo`나 `su`를 거쳐도 바뀌지 않습니다. 그래서 "root가 했다" 대신 "어느 사람이 root로 했다"를 알 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 상태 확인과 규칙 적용 구조

```bash
sudo systemctl status auditd
sudo auditctl -s        # enabled, failure, backlog_limit, lost 등 커널 상태
sudo auditctl -l        # 현재 적재된 규칙
```

`auditctl -s` 출력에서 볼 값:

| 값              | 의미                                        | 확인 기준            |
|-----------------|---------------------------------------------|----------------------|
| `enabled`       | 0 꺼짐, 1 켜짐, 2 잠금(재부팅 전 변경 불가) | 1 또는 2             |
| `failure`       | 0 무시, 1 커널 로그, 2 패닉                 | 일반 서버는 1        |
| `backlog_limit` | 커널 대기열 크기                            | 이벤트가 많으면 늘림 |
| `lost`          | 잃어버린 이벤트 수                          | 0이 아니고 늘면 조치 |

### 규칙 파일 구조

`augenrules`는 `/etc/audit/rules.d/` 안의 `.rules` 파일을 자연 정렬 순서로 합쳐 `/etc/audit/audit.rules`를 만듭니다. 합칠 때 마지막 `-D`는 맨 앞, `-b`는 두 번째, `-f`는 세 번째, `-e`는 맨 끝으로 옮겨집니다.

audit 패키지가 제공하는 예시 규칙(Ubuntu는 `/usr/share/doc/auditd/examples/rules/`)은 번호로 역할을 나눕니다.

| 번호 | 용도                               |
|------|------------------------------------|
| 10   | 커널·auditctl 기본 설정            |
| 20   | 일반 규칙보다 먼저 걸러야 할 예외  |
| 30   | 주요 규칙 (STIG·OSPP·PCI DSS 예시) |
| 40   | 선택 규칙                          |
| 50   | 서버별 규칙                        |
| 70   | 시스템 로컬 규칙                   |
| 90   | 마무리 (불변 잠금)                 |

예시 파일은 한꺼번에 쓰라는 것이 아니라 필요한 조각을 골라 `rules.d`로 복사하라는 용도입니다.

```bash
sudo augenrules --check   # 바뀐 규칙이 있는지만 확인
sudo augenrules --load    # 합친 규칙을 커널에 적재
sudo auditctl -l | wc -l
```

🟡 `auditctl`로 직접 넣은 규칙은 재부팅하면 사라집니다. 시험이 끝난 규칙은 `rules.d` 파일로 옮깁니다.

### 규칙이 하나도 동작하지 않을 때

일부 배포판은 성능을 이유로 `-a never,task` 규칙을 기본으로 둡니다. 이 규칙이 있으면 모든 새 프로세스가 감사 규칙 평가를 건너뜁니다.

```bash
sudo auditctl -l | grep 'never,task'
# 있으면 rules.d의 10-no-audit.rules를 지우고 10-base-config.rules를 사용
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 규칙 문법

### 기본 설정 줄

```text
-D                          # 기존 규칙 모두 삭제
-b 8192                     # backlog 크기
--backlog_wait_time 60000
-f 1                        # 실패 모드 1 = printk
--loginuid-immutable        # 로그인 후 auid 변경 금지
```

### 파일 감시 규칙

```text
-w /etc/sudoers -p wa -k sudoers
```

| 옵션 | 의미                                           |
|------|------------------------------------------------|
| `-w` | 감시할 경로 (와일드카드 불가, 최상위 `/` 불가) |
| `-p` | `r` 읽기, `w` 쓰기, `x` 실행, `a` 속성 변경    |
| `-k` | 검색용 키 (`ausearch -k`로 찾음)               |

`-w`는 예전 형식이고, 같은 내용을 시스템 호출 규칙으로도 쓸 수 있습니다. 특정 사용자만 걸러야 하면 시스템 호출 형식을 씁니다.

```text
-w /etc/shadow -p wa
-a always,exit -F path=/etc/shadow -F perm=wa
```

### 시스템 호출 규칙

```text
-a always,exit -F arch=b64 -S init_module,finit_module -F key=module-load
```

| 부분                | 의미                                                  |
|---------------------|-------------------------------------------------------|
| `-a always,exit`    | 시스템 호출이 끝날 때 항상 기록                       |
| `-F arch=b64`       | 64비트 호출 번호 기준 (32비트 호출은 `b32` 규칙 따로) |
| `-S`                | 시스템 호출 이름, 쉼표로 여러 개                      |
| `-F auid>=1000`     | 일반 사용자로 로그인한 경우만                         |
| `-F auid!=unset`    | 로그인 세션이 없는 데몬 제외                          |
| `-F success=0`      | 실패한 호출만                                         |
| `-F key=` 또는 `-k` | 검색용 키                                             |

64비트 서버에서도 32비트 호출로 같은 일을 할 수 있으므로, 시스템 호출 규칙은 `b32`와 `b64`를 쌍으로 둡니다. 32비트 실행을 막아 둔 시스템이면 예외입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 목적별 규칙 예시

`/etc/audit/rules.d/50-server.rules` 같은 파일로 둡니다. 아래는 방어 관점에서 자주 쓰는 출발점이며, 서버 역할에 맞게 줄입니다.

```text
## 계정·인증 정보
-w /etc/passwd -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/gshadow -p wa -k identity

## 권한 상승 설정
-w /etc/sudoers -p wa -k sudoers
-w /etc/sudoers.d/ -p wa -k sudoers

## 원격 접속 설정
-w /etc/ssh/sshd_config -p wa -k sshd
-w /etc/ssh/sshd_config.d/ -p wa -k sshd

## 예약 실행·서비스 등록 (지속 실행 경로)
-w /etc/crontab -p wa -k cron
-w /etc/cron.d/ -p wa -k cron
-w /var/spool/cron/ -p wa -k cron
-w /etc/systemd/system/ -p wa -k systemd

## 라이브러리 강제 적재
-w /etc/ld.so.preload -p wa -k preload

## 커널 모듈 적재·제거
-a always,exit -F arch=b32 -S init_module,finit_module -F key=module-load
-a always,exit -F arch=b64 -S init_module,finit_module -F key=module-load
-a always,exit -F arch=b32 -S delete_module -F key=module-unload
-a always,exit -F arch=b64 -S delete_module -F key=module-unload

## 관리자가 다른 사용자 홈을 다루는 경우
-a always,exit -F dir=/home -F uid=0 -F auid>=1000 -F auid!=unset -C auid!=obj_uid -F key=power-abuse

## 감사 설정 자체 변경
-w /etc/audit/ -p wa -k auditconfig
```

`-C auid!=obj_uid`는 두 필드를 비교하는 조건으로, 로그인 사용자와 파일 소유자가 다를 때만 기록합니다.

### 불변 잠금

```text
## 99-finalize.rules 마지막 줄
-e 2
```

`-e 2`를 적용하면 재부팅 전까지 규칙을 바꿀 수 없고, 변경 시도는 기록되고 거부됩니다. 공격자가 규칙을 지워 흔적을 숨기는 것을 막지만, 규칙 수정에도 재부팅이 필요하므로 규칙이 안정된 뒤에 켭니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 성능과 잡음 줄이기

시스템 호출 규칙은 모든 프로그램의 시스템 호출마다 평가됩니다. 규칙 수가 많을수록 전체 시스템이 느려집니다.

| 방법                        | 설명                                            |
|-----------------------------|-------------------------------------------------|
| 조건이 같은 규칙은 합치기   | `-S openat -S truncate`처럼 한 규칙에 여러 호출 |
| 가능하면 파일 감시 사용     | `-w`·`dir=`은 파일 시스템 관련 호출에서만 평가  |
| `execve` 전체 기록은 신중히 | 빌드·배치 서버에서는 로그가 매우 빠르게 늘어남  |
| 데몬 잡음 제외              | `-F auid!=unset`으로 로그인 세션만              |
| 특정 실행 파일 제외         | `-A exclude,always -F exe=<경로>`               |

```text
# 두 규칙
-a always,exit -F arch=b64 -S openat -F success=0
-a always,exit -F arch=b64 -S truncate -F success=0
# 하나로 합친 규칙
-a always,exit -F arch=b64 -S openat -S truncate -F success=0
# /etc 아래만 보면 되는 경우 파일 시스템 감시로 처리
-a always,exit -S openat -S truncate -F dir=/etc -F success=0
```

### 이벤트 유실 확인

```bash
sudo auditctl -s | grep -E 'lost|backlog'
```

`lost`가 늘면 `-b` 값을 늘리거나 규칙을 줄입니다. `failure` 모드를 2(패닉)로 두면 유실 대신 시스템이 멈추므로, 규정상 요구가 있는 환경에서만 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. ausearch 조회

`ausearch`는 `audit.log`에서 조건에 맞는 이벤트를 찾습니다. `-i`를 붙이면 UID·시스템 호출 번호를 이름으로 바꿔 보여 줍니다.

| 옵션          | 조건                                                |
|---------------|-----------------------------------------------------|
| `-k key`      | 규칙 키                                             |
| `-m type`     | 메시지 종류 (`USER_LOGIN`, `AVC` 등)                |
| `-ts`, `-te`  | 시작·끝 시각 (`today`, `recent`, `this-week`, 날짜) |
| `-ua uid`     | uid·euid·auid 중 하나라도 일치                      |
| `-ui uid`     | uid 일치                                            |
| `-x exe`      | 실행 파일                                           |
| `-f file`     | 파일 이름                                           |
| `-sc syscall` | 시스템 호출                                         |
| `-p pid`      | 프로세스 ID                                         |
| `-sv no`      | 실패한 이벤트만 (`--success no`)                    |
| `-if path`    | 다른 로그 파일·디렉터리를 입력으로                  |

```bash
# 오늘 계정 파일 변경
sudo ausearch -k identity -ts today -i

# 최근 10분 sudoers 변경
sudo ausearch -k sudoers -ts recent -i

# 특정 로그인 사용자(auid 1001)가 한 일
sudo ausearch -ua 1001 -ts today -i

# 실패한 로그인
sudo ausearch -m USER_LOGIN -sv no -ts this-week -i

# 날짜 범위 지정 (날짜 형식은 로캘을 따름, 확인: date '+%x')
sudo ausearch -k module-load -ts 11/15/2026 00:00:00 -te 11/16/2026 00:00:00 -i

# 회전된 로그 포함 전체에서 검색
sudo ausearch -k cron --input-logs -i
```

### 이벤트 읽는 법

한 이벤트는 같은 `msg=audit(시각:일련번호)`를 공유하는 여러 줄(`SYSCALL`, `PATH`, `CWD`, `PROCTITLE` 등)로 이뤄집니다.

| 필드         | 의미                       |
|--------------|----------------------------|
| `auid`       | 처음 로그인한 사용자       |
| `uid`/`euid` | 실제·유효 사용자           |
| `exe`        | 실행 파일 경로             |
| `comm`       | 명령 이름                  |
| `success`    | 호출 성공 여부             |
| `key`        | 일치한 규칙 키             |
| `name`       | (`PATH` 줄) 대상 파일 경로 |
| `tty`, `ses` | 터미널, 로그인 세션 번호   |

같은 `ses` 값으로 다시 검색하면 한 로그인 세션에서 일어난 일을 이어서 볼 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. aureport 요약

| 명령                    | 보고 내용        |
|-------------------------|------------------|
| `aureport --summary`    | 전체 요약        |
| `aureport -au`          | 인증 시도        |
| `aureport -l`           | 로그인           |
| `aureport -m`           | 계정 변경        |
| `aureport -x --summary` | 실행 파일별 건수 |
| `aureport -f --summary` | 파일별 건수      |
| `aureport -k --summary` | 키별 건수        |
| `aureport --failed`     | 실패 이벤트만    |

```bash
# 이번 주 실패한 인증 시도
sudo aureport -au --failed -ts this-week -i

# 키별 건수로 이상 징후 훑기 (평소보다 급증한 키 확인)
sudo aureport -k --summary -ts today -i
```

키별 건수는 평소 값을 기준선으로 잡아 두어야 급증을 판단할 수 있습니다. 매일 결과를 중앙 수집해 비교합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 로그 보존과 디스크 부족 대응

`/etc/audit/auditd.conf`의 주요 항목입니다.

| 항목                      | 의미                                              |
|---------------------------|---------------------------------------------------|
| `max_log_file`            | 로그 파일 하나의 최대 크기(MB)                    |
| `num_logs`                | 회전 때 남길 파일 수                              |
| `max_log_file_action`     | 최대 크기 도달 시 동작 (`rotate`, `keep_logs` 등) |
| `space_left`              | 남은 공간이 이 값 아래면 경고 단계 (MB 또는 `%`)  |
| `space_left_action`       | 경고 단계 동작 (`syslog`, `email`, `exec` 등)     |
| `admin_space_left`        | 마지막 경고 단계, `space_left`보다 작게           |
| `admin_space_left_action` | 마지막 단계 동작 (`suspend`, `single`, `halt` 등) |
| `disk_full_action`        | 디스크가 찼을 때 동작                             |
| `disk_error_action`       | 쓰기 오류 시 동작                                 |

`keep_logs`는 `rotate`와 비슷하지만 `num_logs`를 쓰지 않아 로그를 지우지 않습니다. 대신 디스크가 차면 `space_left_action`이 동작하므로 외부 보관 스크립트와 함께 씁니다.

### 동작 선택 기준

| 환경                                     | 권장 방향                                                 |
|------------------------------------------|-----------------------------------------------------------|
| 일반 서비스 서버                         | `rotate` + 중앙 수집, 디스크 부족 시 `syslog`·`suspend`   |
| 감사 기록 유실이 허용되지 않는 규정 환경 | `keep_logs` + 외부 보관, 마지막 단계 `single`·`halt` 검토 |

🟡 `single`·`halt`는 디스크가 부족해지면 서비스를 멈춥니다. 가용성 요구와 규정 요구를 함께 보고 결정합니다.

로그를 `/var/log/audit` 전용 파티션에 두면 다른 로그가 감사 로그 공간을 잠식하지 않습니다. 서버 침해 시 로컬 로그가 지워질 수 있으므로 audisp 플러그인(syslog 전송, 원격 전송)으로 중앙에 복사합니다.

```bash
ls /etc/audit/plugins.d/
systemctl cat auditd | grep -i RefuseManualStop
```

RHEL 7 이후 계열의 `auditd.service`는 `RefuseManualStop=yes`로 설정되어 `systemctl stop`·`systemctl restart`가 거부됩니다. 감사 설정 변경 주체를 남기려는 의도이므로 unit을 고치지 말고 `service auditd restart`를 씁니다. Ubuntu 24.04 패키지 unit에는 이 설정이 없어 `systemctl restart auditd`가 동작합니다(설치본에서 위 명령으로 확인).

[⬆ 목차로 돌아가기](#목차)

---

## 9. 운영 점검표

| 항목                               | 확인 방법                           |
|------------------------------------|-------------------------------------|
| auditd 실행 중, `enabled` 1 이상   | `auditctl -s`                       |
| `never,task` 규칙 없음             | `auditctl -l \| grep never`         |
| 규칙이 `rules.d` 파일로 관리됨     | `augenrules --check`                |
| 32·64비트 규칙 쌍                  | 규칙 파일 검토                      |
| 모든 규칙에 키 지정                | `auditctl -l`에서 `key=` 확인       |
| 이벤트 유실 없음                   | `auditctl -s`의 `lost` 추이         |
| 디스크 부족 동작이 정해져 있음     | `auditd.conf` 검토                  |
| 로그가 중앙으로 전송됨             | `plugins.d` 설정, 수집 측 수신 확인 |
| 규칙 안정 후 `-e 2` 적용 여부 결정 | 운영 정책 기록                      |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- auditctl(8), ausearch(8), aureport(8), augenrules(8), auditd.conf(5): Ubuntu 24.04 설치본 man page (audit 3.1.2) (확인일 2026-11-16) — ★★★☆☆
- linux-audit/audit-userspace 공식 저장소·Releases(최신 audit-4.2.1 확인): [github.com/linux-audit/audit-userspace](https://github.com/linux-audit/audit-userspace/releases) (확인일 2026-11-16) — ★★★☆☆
- audit 예시 규칙(README-rules, 10-base-config 등): [github.com/linux-audit/audit-userspace](https://github.com/linux-audit/audit-userspace/tree/master/rules) (확인일 2026-11-16) — ★★★☆☆
- auditctl(8) 온라인 man page: [man7.org](https://man7.org/linux/man-pages/man8/auditctl.8.html) (확인일 2026-11-16) — ★★★☆☆
- linux-audit 메일링 리스트, auditd.service의 RefuseManualStop=yes 이유: [listman.redhat.com](https://listman.redhat.com/archives/linux-audit/2013-July/007913.html) (확인일 2026-11-16) — ★★★☆☆
- Red Hat Bugzilla 1026648(systemctl restart auditd 거부): [bugzilla.redhat.com](https://bugzilla.redhat.com/show_bug.cgi?id=1026648) (확인일 2026-11-16) — ★★★☆☆

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.

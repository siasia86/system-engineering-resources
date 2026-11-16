# journalctl·logrotate 로그 관리

Linux 서버의 로그는 크게 systemd-journald가 관리하는 바이너리 저널과 `/var/log` 아래 텍스트 파일 두 경로로 쌓입니다. 이 문서는 `journalctl`로 로그를 찾는 방법, 저널 저장 위치와 용량 제한, `logrotate`로 텍스트 로그를 순환하는 설정, 디스크가 로그로 찰 때의 점검 순서를 다룹니다.

## 목차

| 섹션                                                                                                               |
|--------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. journalctl 조회](#2-journalctl-조회) / [3. 필터와 출력 형식](#3-필터와-출력-형식)         |
| [4. 저널 저장과 용량](#4-저널-저장과-용량) / [5. syslog 연계](#5-syslog-연계)                                      |
| [6. logrotate 구조](#6-logrotate-구조) / [7. logrotate 설정 예](#7-logrotate-설정-예)                              |
| [8. 시험과 점검](#8-시험과-점검) / [9. 디스크 부족 대응](#9-디스크-부족-대응) / [10. 운영 점검표](#10-운영-점검표) |

---

## 1. 개요

```text
 service stdout/stderr ---+
 syslog() / logger -------+--> systemd-journald --> /var/log/journal/   (persistent)
 kernel (kmsg) -----------+          |          or /run/log/journal/   (volatile)
                                     |
                                     +--> rsyslog / syslog-ng (ForwardToSyslog)
                                                   |
                                                   v
                                     /var/log/syslog, /var/log/messages ...
                                                   |
 app log files (/var/log/nginx/*.log) -------------+--> logrotate (daily timer)
```

| 구분       | systemd-journald                       | 텍스트 로그 + logrotate                |
|------------|----------------------------------------|----------------------------------------|
| 형식       | 색인된 바이너리. `journalctl`로 읽음   | 일반 텍스트. `less`, `grep`으로 읽음   |
| 메타데이터 | 유닛, PID, UID, 부팅 ID, 우선순위 필드 | 줄 안의 문자열뿐                       |
| 용량 관리  | `journald.conf`의 크기·기간 제한       | `logrotate` 설정의 순환 주기·보관 개수 |
| 수집 대상  | 서비스 출력, syslog, 커널 메시지       | 앱이 직접 쓰는 파일, rsyslog 출력 파일 |

[⬆ 목차로 돌아가기](#목차)

## 2. journalctl 조회

| 명령                              | 용도                                       |
|-----------------------------------|--------------------------------------------|
| `journalctl -u nginx`             | 특정 유닛 로그                             |
| `journalctl -u nginx -f`          | 실시간 따라 보기(`tail -f`와 비슷)         |
| `journalctl -b`                   | 이번 부팅 이후 로그                        |
| `journalctl -b -1`                | 직전 부팅 로그(지속 저장일 때만 의미 있음) |
| `journalctl --list-boots`         | 저장된 부팅 목록                           |
| `journalctl -k`                   | 커널 메시지(`dmesg`와 비슷, 부팅 단위)     |
| `journalctl -p err -b`            | 이번 부팅의 err 이상 로그                  |
| `journalctl --since "1 hour ago"` | 시간 범위 지정                             |
| `journalctl -n 100 --no-pager`    | 마지막 100줄을 페이저 없이                 |
| `journalctl -e`                   | 페이저를 끝에서 시작                       |
| `journalctl -x`                   | 메시지 카탈로그 설명 추가                  |

```bash
# 어제 오후 nginx 오류만
journalctl -u nginx --since "yesterday 13:00" --until "yesterday 18:00" -p warning

# 여러 유닛 함께
journalctl -u nginx -u php-fpm -b

# 직전 부팅이 갑자기 끝났을 때 마지막 기록
journalctl -b -1 -n 50 --no-pager
```

일반 사용자는 자신의 로그만 볼 수 있습니다. 시스템 전체 로그는 root이거나 `systemd-journal`·`adm` 그룹(배포판마다 다름)에 속해야 볼 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 필터와 출력 형식

### 3.1 우선순위

`-p`는 syslog 우선순위를 씁니다. 하나만 주면 그 값 이상(더 심각한 쪽)을 모두 보여 줍니다.

| 숫자 | 이름    | 숫자 | 이름      |
|------|---------|------|-----------|
| 0    | `emerg` | 4    | `warning` |
| 1    | `alert` | 5    | `notice`  |
| 2    | `crit`  | 6    | `info`    |
| 3    | `err`   | 7    | `debug`   |

### 3.2 필드 필터

저널의 각 항목에는 필드가 붙습니다. `FIELD=값` 형식으로 거릅니다.

```bash
journalctl _PID=1234
journalctl _UID=1001 -b
journalctl _SYSTEMD_UNIT=sshd.service _COMM=sshd
journalctl /usr/sbin/sshd                    # 실행 파일 경로로
journalctl -F _SYSTEMD_UNIT                  # 필드에 나온 값 목록
journalctl -u sshd -g "Failed password"      # 메시지 정규식 검색 (--grep)
```

같은 필드를 여러 번 주면 OR, 다른 필드를 함께 주면 AND로 묶입니다.

### 3.3 출력 형식

| `-o` 값         | 용도                                   |
|-----------------|----------------------------------------|
| `short`         | 기본. syslog와 비슷한 한 줄            |
| `short-iso`     | ISO 8601 시각                          |
| `short-precise` | 마이크로초 단위 시각                   |
| `verbose`       | 항목의 모든 필드                       |
| `json`          | 한 줄에 JSON 하나. 다른 도구로 넘길 때 |
| `cat`           | 메시지 본문만                          |

```bash
journalctl -u myapp -o json --since today | jq -r '.MESSAGE'
```

[⬆ 목차로 돌아가기](#목차)

## 4. 저널 저장과 용량

설정은 `/etc/systemd/journald.conf`와 drop-in 디렉토리 `/etc/systemd/journald.conf.d/*.conf`에 둡니다. 원본 파일을 고치기보다 drop-in을 쓰면 패키지 갱신 때 충돌이 줄어듭니다.

| 옵션                                       | 뜻                                                                |
|--------------------------------------------|-------------------------------------------------------------------|
| `Storage=`                                 | `volatile`(메모리), `persistent`(디스크), `auto`, `none`          |
| `SystemMaxUse=`                            | `/var/log/journal` 최대 사용량. 기본 파일시스템의 10%, 4G 상한    |
| `SystemKeepFree=`                          | 파일시스템에 남겨 둘 여유. 기본 15%, 4G 상한                      |
| `SystemMaxFileSize=`                       | 저널 파일 하나의 최대 크기. 기본 `SystemMaxUse=`의 1/8, 128M 상한 |
| `MaxRetentionSec=`                         | 이 기간보다 오래된 항목 삭제                                      |
| `RateLimitIntervalSec=`, `RateLimitBurst=` | 서비스별 로그 폭주 제한                                           |
| `ForwardToSyslog=`                         | rsyslog 등 syslog 데몬으로 전달                                   |

`Storage=`의 기본값은 판에 따라 다릅니다. systemd 255 man page(Ubuntu 24.04)는 기본 이름공간에서 `auto`로, 최신 man page(2026-11-16 확인)는 `persistent`(컴파일 시 결정)로 설명합니다. `auto`는 `/var/log/journal` 디렉토리가 있으면 디스크에, 없으면 메모리에 저장합니다. 메모리 저장이면 재부팅 때 로그가 사라지므로 `journalctl -b -1`이 비어 있습니다.

```bash
# 현재 사용량
journalctl --disk-usage

# 지속 저장 켜기 (drop-in)
sudo mkdir -p /etc/systemd/journald.conf.d
sudo tee /etc/systemd/journald.conf.d/50-persistent.conf >/dev/null <<'EOF'
[Journal]
Storage=persistent
SystemMaxUse=2G
MaxRetentionSec=1month
EOF
sudo systemctl restart systemd-journald
```

🟡 주의: 아래 vacuum 명령은 오래된 저널을 지웁니다. 장애 조사 중이면 필요한 범위를 먼저 내보낸 뒤 실행합니다. vacuum은 보관된(archived) 파일만 지우므로 실행 후에도 설정값보다 많이 남을 수 있으며, 먼저 `--rotate`로 현재 파일을 보관 상태로 넘깁니다.

```bash
# 필요한 로그 보관
journalctl --since "2 days ago" -o short-iso > /root/journal_backup.txt

# 현재 파일 보관 처리 후 정리
sudo journalctl --rotate
sudo journalctl --vacuum-size=1G
sudo journalctl --vacuum-time=14d

# 저널 파일 무결성 점검
journalctl --verify
```

[⬆ 목차로 돌아가기](#목차)

## 5. syslog 연계

많은 배포판이 journald와 rsyslog를 함께 씁니다. journald가 받은 로그를 rsyslog가 읽어 `/var/log/syslog`(Debian 계열)나 `/var/log/messages`(RHEL 계열) 같은 텍스트 파일로 씁니다. 이 경우 같은 로그가 두 곳에 저장되므로 용량을 양쪽에서 관리해야 합니다.

```bash
# rsyslog 사용 여부
systemctl is-active rsyslog
# 셸 스크립트에서 저널에 기록 (태그와 우선순위 지정)
logger -t backup -p user.err "backup failed: disk full"
journalctl -t backup -n 5
```

원격 로그 수집이 필요하면 rsyslog 전달, `systemd-journal-remote`/`systemd-journal-upload`, 또는 별도 수집 에이전트를 씁니다. 수집 구조는 [자원 사용률 모니터링](../../02_infrastructure/monitoring/resource_utilization_monitoring.md) 같은 모니터링 문서와 함께 정합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. logrotate 구조

logrotate는 텍스트 로그 파일을 일정 주기나 크기마다 이름을 바꿔(순환) 보관하고 오래된 것을 지우는 도구입니다. 2026-11-16 확인 시 공식 저장소의 최신 판은 3.22.0입니다.

| 경로·구성                      | 역할                                                                  |
|--------------------------------|-----------------------------------------------------------------------|
| `/etc/logrotate.conf`          | 전역 기본값과 `include /etc/logrotate.d`                              |
| `/etc/logrotate.d/<이름>`      | 패키지·서비스별 설정                                                  |
| `logrotate.timer` / cron.daily | 하루 한 번 실행(배포판에 따라 timer 또는 cron)                        |
| 상태 파일                      | 각 로그의 마지막 순환 시각. Debian 계열은 `/var/lib/logrotate/status` |

```bash
# 실행 방식 확인
systemctl list-timers logrotate.timer
systemctl cat logrotate.service
ls /etc/cron.daily/ | grep logrotate
```

logrotate는 실행될 때마다 상태 파일의 시각과 설정 주기를 비교해 순환 여부를 정합니다. 그래서 `daily` 설정이라도 logrotate가 하루 한 번만 실행되면 `size`·`maxsize` 조건도 그 실행 시점에만 검사됩니다.

[⬆ 목차로 돌아가기](#목차)

## 7. logrotate 설정 예

```text
# /etc/logrotate.d/myapp
/var/log/myapp/*.log {
    daily
    rotate 14
    maxsize 500M
    missingok
    notifempty
    compress
    delaycompress
    dateext
    create 0640 myapp adm
    su myapp adm
    sharedscripts
    postrotate
        systemctl kill -s HUP --kill-whom=main myapp.service >/dev/null 2>&1 || true
    endscript
}
```

| 지시어                         | 뜻                                                               |
|--------------------------------|------------------------------------------------------------------|
| `daily` / `weekly`             | 순환 주기                                                        |
| `rotate 14`                    | 보관할 옛 파일 개수. 넘치면 가장 오래된 파일 삭제                |
| `size` / `maxsize` / `minsize` | 크기 조건. `maxsize`는 주기 전이라도 크기를 넘으면 순환          |
| `missingok`                    | 파일이 없어도 오류로 보지 않음                                   |
| `notifempty`                   | 빈 파일은 순환하지 않음                                          |
| `compress`                     | 옛 파일을 gzip으로 압축                                          |
| `delaycompress`                | 바로 직전 파일은 다음 순환 때 압축(앱이 아직 쓰고 있을 때 대비)  |
| `dateext`                      | 번호 대신 날짜 접미사                                            |
| `create 0640 u g`              | 순환 후 새 빈 파일을 권한·소유자 지정해 생성                     |
| `su u g`                       | 해당 사용자·그룹 권한으로 순환(쓰기 가능한 디렉토리일 때 필요)   |
| `sharedscripts`                | 와일드카드로 여러 파일이 잡혀도 스크립트를 한 번만 실행          |
| `postrotate`                   | 순환 후 실행할 명령. 보통 앱에 로그 파일을 다시 열라는 신호 전송 |
| `copytruncate`                 | 원본을 복사한 뒤 원본을 비움. 파일을 다시 열 수 없는 앱용        |

앱이 로그 파일을 다시 여는 방법이 있으면 `create` + `postrotate`를 씁니다. 그런 방법이 없을 때만 `copytruncate`를 씁니다. `copytruncate`는 복사와 비우기 사이에 쓰인 로그를 잃을 수 있다고 man page에 적혀 있습니다.

🟡 주의: 앱이 순환 후에도 옛 파일(삭제되었거나 이름이 바뀐 파일)에 계속 쓰면 디스크가 줄지 않습니다. 9절의 `lsof +L1` 점검으로 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 8. 시험과 점검

```bash
# 문법과 동작 미리보기 (실제로 바꾸지 않음)
sudo logrotate -d /etc/logrotate.d/myapp

# 상세 출력과 함께 강제 순환 (주기와 상관없이 실행)
sudo logrotate -v -f /etc/logrotate.d/myapp

# 마지막 순환 기록
grep myapp /var/lib/logrotate/status

# 최근 실행 결과
journalctl -u logrotate.service -n 30 --no-pager
```

🟡 주의: `-f`는 실제로 순환하고 오래된 파일을 지울 수 있습니다. 운영 서버에서는 `-d` 결과를 먼저 확인합니다.

| 증상                                                             | 흔한 원인                                                      |
|------------------------------------------------------------------|----------------------------------------------------------------|
| `skipping ... because parent directory has insecure permissions` | 로그 디렉토리가 다른 사용자 쓰기 가능. `su` 지시어 필요        |
| 순환이 안 됨                                                     | 주기 미도달, `notifempty`로 건너뜀, 다른 설정 파일과 경로 중복 |
| 순환 후 새 로그가 비어 있음                                      | 앱이 옛 파일에 계속 기록. `postrotate` 신호 누락               |
| 같은 파일이 두 설정에서 잡힘                                     | 오류로 처리됨. 한쪽 설정에서 경로 제거                         |

[⬆ 목차로 돌아가기](#목차)

## 9. 디스크 부족 대응

로그로 디스크가 찰 때 다음 순서로 원인을 찾습니다.

```bash
# 1) 어느 파일시스템이 찼는지
df -h
# 2) 로그 디렉토리 중 큰 것
sudo du -xh --max-depth=2 /var/log | sort -h | tail -15
# 3) 저널 사용량
journalctl --disk-usage
# 4) 지워졌는데 열려 있는 파일 (링크 수 0)
sudo lsof +L1 | grep -i log
```

| 상황                                | 조치 방향                                     |
|-------------------------------------|-----------------------------------------------|
| 저널이 큼                           | `SystemMaxUse=` 설정, `--vacuum-size`로 정리  |
| 특정 앱 로그 하나가 큼              | logrotate에 `maxsize` 추가, 앱 로그 수준 조정 |
| `lsof +L1`에 삭제된 로그가 보임     | 해당 프로세스에 로그 재열기 신호 또는 재시작  |
| 같은 로그가 journald와 rsyslog 양쪽 | 한쪽 보관 기간 축소                           |

🟡 주의: 쓰고 있는 로그 파일을 `rm`으로 지우면 프로세스가 열고 있는 동안 공간이 돌아오지 않습니다. 급하게 비워야 하면 `: > /var/log/myapp/app.log`처럼 내용만 비우되, 그 전에 필요한 부분을 보관합니다.

관련 문서: [df](./df.md), [du](./du.md), [lsof](./lsof.md), [systemd 유닛 관리](./systemd_unit_management.md).

[⬆ 목차로 돌아가기](#목차)

## 10. 운영 점검표

| 항목                                                             | 확인 |
|------------------------------------------------------------------|------|
| 저널이 재부팅 후에도 남는가(`journalctl --list-boots`에 여러 줄) | [ ]  |
| `SystemMaxUse=` 또는 `MaxRetentionSec=`을 정했는가               | [ ]  |
| 앱 로그 경로마다 `/etc/logrotate.d/` 설정이 있는가               | [ ]  |
| `postrotate`로 앱이 새 파일을 열도록 했는가                      | [ ]  |
| `logrotate -d`로 설정을 미리 확인했는가                          | [ ]  |
| `/var/log`가 별도 파일시스템인지, 사용률 경보가 있는가           | [ ]  |
| 보안·감사 요구에 맞는 보관 기간과 원격 전송이 있는가             | [ ]  |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- journalctl(1): [freedesktop.org/software/systemd/man/latest/journalctl.html](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) — ★★★☆☆ (확인일 2026-11-16)
- journald.conf(5): [freedesktop.org/software/systemd/man/latest/journald.conf.html](https://www.freedesktop.org/software/systemd/man/latest/journald.conf.html) — ★★★☆☆ (확인일 2026-11-16)
- systemd.journal-fields(7): [freedesktop.org/software/systemd/man/latest/systemd.journal-fields.html](https://www.freedesktop.org/software/systemd/man/latest/systemd.journal-fields.html) — ★★★☆☆ (확인일 2026-11-16)
- logrotate(8) man page: [man7.org/linux/man-pages/man8/logrotate.8.html](https://man7.org/linux/man-pages/man8/logrotate.8.html) — ★★★☆☆ (확인일 2026-11-16)
- logrotate 공식 저장소 releases: [github.com/logrotate/logrotate/releases](https://github.com/logrotate/logrotate/releases) — ★★★☆☆ (확인일 2026-11-16)
- RFC 5424 The Syslog Protocol (우선순위 값): [datatracker.ietf.org/doc/html/rfc5424](https://datatracker.ietf.org/doc/html/rfc5424) — ★★★★☆ (확인일 2026-11-16)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.

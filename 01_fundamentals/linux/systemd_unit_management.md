# systemd 유닛 관리
<!-- reference: _reference/linux_process_official_notes.md -->

systemd는 대부분의 최신 Linux 배포판에서 PID 1로 동작하는 init 시스템이자 서비스 관리자입니다. 이 문서는 서비스를 직접 등록·운영하는 데 필요한 유닛 파일 구조, `systemctl` 명령, drop-in 재정의, 재시작 정책, timer, 장애 점검 순서를 다룹니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 유닛 종류와 위치](#2-유닛-종류와-위치) / [3. systemctl 기본](#3-systemctl-기본) |
| [4. 서비스 유닛 작성](#4-서비스-유닛-작성) / [5. 의존성과 순서](#5-의존성과-순서)                        |
| [6. 재정의와 drop-in](#6-재정의와-drop-in) / [7. 재시작 정책](#7-재시작-정책)                            |
| [8. timer 유닛](#8-timer-유닛) / [9. 장애 점검](#9-장애-점검) / [10. 운영 점검표](#10-운영-점검표)       |

---

## 1. 개요

systemd는 서비스, 마운트, 소켓, 타이머 같은 관리 대상을 모두 유닛(unit)이라는 설정 단위로 다룹니다. 유닛 사이의 의존 관계를 보고 부팅 때 병렬로 시작하며, 각 서비스를 cgroup(프로세스 묶음별 자원 관리 단위)에 넣어 자식 프로세스까지 추적합니다.

```bash
# 버전 확인
systemctl --version
# PID 1 확인
ps -p 1 -o comm=
```

2026-11-16 확인 시 systemd 공식 저장소의 최신 정식 판은 `v262`(2026-09-22)이고, 안정 갱신 판은 `v262.2`(2026-11-05)입니다. 배포판마다 쓰는 판이 다르므로(예: Ubuntu 24.04는 255) 옵션이 동작하지 않으면 그 시스템의 `man systemd.service`를 기준으로 봅니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 유닛 종류와 위치

| 확장자     | 용도                                                  |
|------------|-------------------------------------------------------|
| `.service` | 데몬·일회성 작업 실행                                 |
| `.socket`  | 소켓을 먼저 열어 두고 연결이 오면 서비스 시작         |
| `.timer`   | 시간 조건으로 다른 유닛 실행(cron 대체)               |
| `.target`  | 여러 유닛을 묶는 동기화 지점(예: `multi-user.target`) |
| `.mount`   | 마운트 지점. `/etc/fstab`에서도 자동 생성             |
| `.path`    | 파일·디렉토리 변화를 감지해 유닛 실행                 |
| `.slice`   | cgroup 계층에서 자원 묶음                             |

시스템 유닛 파일은 다음 위치에서 찾으며, 위쪽이 우선합니다.

| 위치                             | 용도                                   |
|----------------------------------|----------------------------------------|
| `/etc/systemd/system/`           | 관리자가 만들거나 재정의한 유닛        |
| `/run/systemd/system/`           | 실행 중 생성된 유닛(재부팅하면 사라짐) |
| `/usr/local/lib/systemd/system/` | 로컬 설치 소프트웨어 유닛              |
| `/usr/lib/systemd/system/`       | 배포판 패키지가 설치한 유닛            |

패키지가 설치한 `/usr/lib/...` 파일은 갱신 때 덮어써지므로 직접 고치지 않습니다. 바꿀 내용은 `/etc/systemd/system/`에 둡니다(6절).

[⬆ 목차로 돌아가기](#목차)

## 3. systemctl 기본

| 명령                                   | 동작                                           |
|----------------------------------------|------------------------------------------------|
| `systemctl status nginx`               | 상태, 주 PID, cgroup, 최근 로그                |
| `systemctl start` / `stop` / `restart` | 즉시 시작·중지·재시작                          |
| `systemctl reload nginx`               | 프로세스를 유지한 채 설정 다시 읽기(지원할 때) |
| `systemctl enable --now nginx`         | 부팅 시 자동 시작 등록과 즉시 시작             |
| `systemctl disable nginx`              | 부팅 시 자동 시작 해제                         |
| `systemctl mask nginx`                 | 수동 시작까지 막음(`/dev/null` 링크)           |
| `systemctl is-active` / `is-enabled`   | 스크립트용 상태 확인(종료 코드로 판단)         |
| `systemctl cat nginx`                  | 실제 적용되는 유닛 파일과 drop-in 전체 표시    |
| `systemctl show nginx -p Restart`      | 적용된 속성 값 조회                            |
| `systemctl daemon-reload`              | 유닛 파일 변경 후 다시 읽기                    |
| `systemctl list-units --failed`        | 실패 상태 유닛 목록                            |
| `systemctl list-dependencies nginx`    | 의존 트리                                      |

`enable`은 부팅 때 시작되도록 링크를 만들 뿐 지금 시작하지 않습니다. 지금 시작까지 하려면 `--now`를 붙이거나 `start`를 따로 실행합니다.

```bash
# 스크립트에서 상태 판단
if systemctl is-active --quiet nginx; then
    echo "nginx running"
fi
```

[⬆ 목차로 돌아가기](#목차)

## 4. 서비스 유닛 작성

Python 웹 앱을 전용 사용자로 실행하는 예입니다.

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My web application
Documentation=https://example.com/docs
After=network-online.target
Wants=network-online.target

[Service]
Type=exec
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp
EnvironmentFile=-/etc/myapp/env
ExecStart=/opt/myapp/venv/bin/python -m myapp --port 8080
Restart=on-failure
RestartSec=5s
TimeoutStopSec=30s

# 기본 보호 설정
NoNewPrivileges=yes
ProtectSystem=strict
ReadWritePaths=/var/lib/myapp
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now myapp
systemctl status myapp
```

`Type=`은 systemd가 "시작이 끝났다"고 판단하는 기준입니다.

| Type            | 시작 완료 판단                                                        |
|-----------------|-----------------------------------------------------------------------|
| `simple`        | 프로세스를 fork한 직후. 실행 파일이 없어도 시작 성공으로 보일 수 있음 |
| `exec`          | 실행 파일 `exec`까지 성공한 뒤. 경로 오류를 시작 실패로 잡음          |
| `forking`       | 시작 프로세스가 백그라운드로 분기하고 종료한 뒤. `PIDFile=` 권장      |
| `oneshot`       | 프로세스가 끝난 뒤. 초기화 스크립트용                                 |
| `notify`        | 서비스가 `sd_notify()`로 `READY=1`을 보낸 뒤                          |
| `notify-reload` | `notify`와 같고, 재적재도 신호와 알림으로 처리                        |
| `dbus`          | 지정한 D-Bus 이름을 얻은 뒤                                           |
| `idle`          | `simple`과 같되 다른 작업이 끝날 때까지 실행을 늦춤                   |

`ExecStart=`는 셸을 거치지 않습니다. 파이프나 `&&`가 필요하면 `/bin/sh -c '...'`로 감싸거나 별도 스크립트로 만듭니다. `EnvironmentFile=` 앞의 `-`는 파일이 없어도 오류로 보지 않는다는 뜻입니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 의존성과 순서

systemd는 "같이 켜야 하는가(의존)"와 "어느 것이 먼저인가(순서)"를 따로 설정합니다. `Requires=`만 쓰면 두 유닛이 동시에 시작될 수 있으므로 순서가 필요하면 `After=`를 함께 씁니다.

| 지시어       | 뜻                                                        |
|--------------|-----------------------------------------------------------|
| `Wants=`     | 함께 시작. 대상이 실패해도 이 유닛은 계속 진행            |
| `Requires=`  | 함께 시작. 대상이 시작에 실패하면 이 유닛도 시작하지 않음 |
| `BindsTo=`   | `Requires=`보다 강함. 대상이 멈추면 이 유닛도 멈춤        |
| `After=`     | 대상이 시작된 뒤에 이 유닛 시작                           |
| `Before=`    | 이 유닛이 시작된 뒤에 대상 시작                           |
| `Conflicts=` | 함께 실행할 수 없음. 하나가 시작되면 다른 하나를 멈춤     |

`network.target`은 네트워크 관리 서비스가 시작되었다는 뜻일 뿐 주소가 잡혔다는 보장이 아닙니다. 원격 주소에 바로 접속해야 하는 서비스는 `network-online.target`을 `Wants=`와 `After=`에 함께 넣습니다.

```bash
# 부팅 시 무엇이 오래 걸렸는지
systemd-analyze blame | head
systemd-analyze critical-chain myapp.service
# 유닛 파일 문법 점검
systemd-analyze verify /etc/systemd/system/myapp.service
```

[⬆ 목차로 돌아가기](#목차)

## 6. 재정의와 drop-in

패키지 유닛의 일부만 바꿀 때는 drop-in(원본 옆에 덧붙이는 설정 조각)을 씁니다.

```bash
# /etc/systemd/system/nginx.service.d/override.conf 를 편집기로 열고, 저장하면 daemon-reload까지 수행
sudo systemctl edit nginx

# 유닛 전체를 복사해 고치기 (원본 갱신을 따라가지 않으므로 신중히)
sudo systemctl edit --full nginx

# 재정의 결과 확인
systemctl cat nginx
systemd-delta --type=extended
```

```ini
# /etc/systemd/system/nginx.service.d/override.conf
[Service]
LimitNOFILE=65536
Restart=on-failure
```

목록형 지시어(`ExecStart=` 등)는 덧붙이는 방식이라 값을 바꾸려면 먼저 빈 값으로 지워야 합니다.

```ini
[Service]
ExecStart=
ExecStart=/usr/sbin/nginx -g 'daemon off;'
```

재정의를 지우려면 `sudo systemctl revert nginx`를 씁니다. `/etc`에 둔 재정의 파일을 지우고 패키지 원본 상태로 돌아갑니다.

[⬆ 목차로 돌아가기](#목차)

## 7. 재시작 정책

| `Restart=`    | 재시작 조건                                               |
|---------------|-----------------------------------------------------------|
| `no`          | 재시작하지 않음(기본값)                                   |
| `on-success`  | 정상 종료(종료 코드 0 등)일 때만                          |
| `on-failure`  | 0이 아닌 종료 코드, 신호로 인한 종료, 시간 초과, watchdog |
| `on-abnormal` | 신호로 인한 종료, 시간 초과, watchdog                     |
| `on-watchdog` | watchdog 시간 초과일 때만                                 |
| `on-abort`    | 처리되지 않은 신호로 종료될 때만                          |
| `always`      | 종료 원인과 상관없이                                      |

재시작이 너무 잦으면 시작 제한에 걸려 유닛이 `failed`로 멈춥니다. 기본값은 10초 안에 5번(`DefaultStartLimitIntervalSec=10s`, `DefaultStartLimitBurst=5`)입니다. `RestartSec=`을 짧게 두면 이 제한에 빨리 걸립니다.

```ini
[Unit]
StartLimitIntervalSec=300
StartLimitBurst=5

[Service]
Restart=on-failure
RestartSec=10s
```

시작 제한에 걸린 뒤 다시 시작하려면 원인을 고친 다음 `sudo systemctl reset-failed myapp`를 실행하고 `start`합니다.

[⬆ 목차로 돌아가기](#목차)

## 8. timer 유닛

timer는 같은 이름의 `.service`를 시간 조건으로 실행합니다. cron과 비교하면 실행 로그가 journal에 남고, 의존성·자원 제한을 서비스 설정으로 쓸 수 있다는 장점이 있습니다.

```ini
# /etc/systemd/system/backup.service
[Unit]
Description=Nightly backup

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh
```

```ini
# /etc/systemd/system/backup.timer
[Unit]
Description=Run backup daily at 02:30

[Timer]
OnCalendar=*-*-* 02:30:00
RandomizedDelaySec=10min
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now backup.timer
systemctl list-timers --all
# 달력 표현식 검증
systemd-analyze calendar '*-*-* 02:30:00'
```

| 지시어                | 뜻                                                 |
|-----------------------|----------------------------------------------------|
| `OnCalendar=`         | 달력 시각(`daily`, `Mon *-*-* 09:00` 등)           |
| `OnBootSec=`          | 부팅 후 경과 시간                                  |
| `OnUnitActiveSec=`    | 대상 유닛이 마지막으로 활성화된 뒤 경과 시간       |
| `Persistent=true`     | 꺼져 있던 동안 놓친 실행을 다음 부팅 때 한 번 실행 |
| `RandomizedDelaySec=` | 여러 서버가 같은 시각에 몰리지 않도록 무작위 지연  |

[⬆ 목차로 돌아가기](#목차)

## 9. 장애 점검

서비스가 시작되지 않을 때 다음 순서로 확인합니다.

```bash
# 1) 상태와 마지막 로그
systemctl status myapp --no-pager -l
# 2) 이번 부팅의 해당 유닛 로그 전체
journalctl -u myapp -b --no-pager
# 3) 실제 적용된 설정
systemctl cat myapp
systemctl show myapp -p ExecStart,User,Environment
# 4) 유닛 파일 문법
systemd-analyze verify /etc/systemd/system/myapp.service
# 5) 같은 사용자로 직접 실행해 오류 재현
sudo -u myapp /opt/myapp/venv/bin/python -m myapp --port 8080
```

| 증상                                 | 흔한 원인                                         |
|--------------------------------------|---------------------------------------------------|
| `status=203/EXEC`                    | 실행 파일 경로 오류, 실행 권한 없음, shebang 오류 |
| `status=217/USER`                    | `User=`에 지정한 계정이 없음                      |
| `status=200/CHDIR`                   | `WorkingDirectory=`가 없거나 권한 없음            |
| `start request repeated too quickly` | 시작 제한 초과. 원인 수정 후 `reset-failed`       |
| 파일을 고쳤는데 반영 안 됨           | `daemon-reload` 누락, drop-in이 덮어씀            |
| 수동 실행은 되는데 서비스로는 실패   | 환경 변수·PATH·작업 디렉토리·보호 설정 차이       |
| `Type=forking`인데 바로 멈춤         | 프로그램이 포그라운드 실행. `Type=exec`로 변경    |

로그 조회 방법은 [journalctl·logrotate 로그 관리](./journald_logrotate_guide.md)에서 다룹니다.

[⬆ 목차로 돌아가기](#목차)

## 10. 운영 점검표

| 항목                                                           | 확인 |
|----------------------------------------------------------------|------|
| 패키지 유닛은 직접 고치지 않고 `systemctl edit`로 재정의했는가 | [ ]  |
| 유닛 파일 변경 후 `daemon-reload`를 했는가                     | [ ]  |
| `enable`과 `start`를 모두 했는가(또는 `enable --now`)          | [ ]  |
| 서비스 전용 계정(`User=`)으로 실행하는가                       | [ ]  |
| `Restart=`와 `RestartSec=`이 시작 제한과 맞는가                | [ ]  |
| 원격 접속이 필요한 서비스에 `network-online.target`을 넣었는가 | [ ]  |
| `systemd-analyze verify`로 문법을 확인했는가                   | [ ]  |
| `systemd-analyze security <유닛>`으로 보호 설정을 점검했는가   | [ ]  |

관련 문서: [Linux 시스템 프로세스](./linux_system_processes.md), [프로세스 수명](./process_lifecycle.md), [cgroup 개념](./cgroup_concepts.md).

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- systemd.unit(5): [freedesktop.org/software/systemd/man/latest/systemd.unit.html](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html) — ★★★☆☆ (확인일 2026-11-16)
- systemd.service(5): [freedesktop.org/software/systemd/man/latest/systemd.service.html](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html) — ★★★☆☆ (확인일 2026-11-16)
- systemd.timer(5): [freedesktop.org/software/systemd/man/latest/systemd.timer.html](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html) — ★★★☆☆ (확인일 2026-11-16)
- systemctl(1): [freedesktop.org/software/systemd/man/latest/systemctl.html](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) — ★★★☆☆ (확인일 2026-11-16)
- systemd-system.conf(5): [freedesktop.org/software/systemd/man/latest/systemd-system.conf.html](https://www.freedesktop.org/software/systemd/man/latest/systemd-system.conf.html) — ★★★☆☆ (확인일 2026-11-16)
- systemd 공식 저장소 tag 목록: [github.com/systemd/systemd/tags](https://github.com/systemd/systemd/tags) — ★★★☆☆ (확인일 2026-11-16)

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

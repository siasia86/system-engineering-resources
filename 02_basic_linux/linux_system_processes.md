# Linux 시스템 프로세스

## 목차

| 섹션 |
|------|
| [1. 프로세스 트리 구조](#1-프로세스-트리-구조) / [2. 프로세스 상세](#2-프로세스-상세) |

---

## 1. 프로세스 트리 구조

```
systemd─┬─acpid
        ├─2*[agetty]
        ├─amazon-ssm-agen───8*[{amazon-ssm-agen}]
        ├─chronyd───chronyd
        ├─cron
        ├─dbus-daemon
        ├─irqbalance───{irqbalance}
        ├─multipathd───6*[{multipathd}]
        ├─networkd-dispat
        ├─nginx───2*[nginx]
        ├─packagekitd───2*[{packagekitd}]
        ├─polkitd───2*[{polkitd}]
        ├─rsyslogd───3*[{rsyslogd}]
        ├─snapd───9*[{snapd}]
        ├─sshd───sshd───sshd───bash───sudo───sudo───bash───pstree
        ├─sudo───sudo───su───bash───tail
        ├─systemd───(sd-pam)
        ├─systemd-journal
        ├─systemd-logind
        ├─systemd-network
        ├─systemd-resolve
        ├─systemd-udevd
        ├─unattended-upgr───{unattended-upgr}
        └─vnstatd
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 프로세스 상세

### `systemd` — init 프로세스 (PID 1)

모든 프로세스의 부모. 부팅 시 커널이 최초로 실행하는 프로세스로 서비스 시작/종료/의존성을 관리합니다.

---

### `accounts-daemon` — 사용자 계정 관리 데몬 (AccountsService)

시스템 사용자 계정 정보를 D-Bus를 통해 제공합니다. GNOME, 로그인 화면 등 GUI 컴포넌트가 사용자 목록, 아이콘, 언어 설정 등을 조회할 때 사용합니다. 서버 환경에서는 실질적인 역할이 없습니다.

---

### `acpid` — ACPI 이벤트 데몬

전원 버튼, 배터리, 절전 등 하드웨어 전원 관련 이벤트를 처리합니다. 클라우드 환경에서는 인스턴스 종료 신호 처리에 사용됩니다.

---

### `agetty` — 터미널 로그인 프롬프트

물리 콘솔 및 가상 터미널(tty1~tty6)에서 `login:` 프롬프트를 표시하고 로그인을 처리합니다. 클라우드 환경에서는 실제 사용되지 않고 대기 상태로만 존재합니다.

---

### `amazon-ssm-agen` — AWS Systems Manager Agent

AWS SSM을 통한 원격 명령 실행, 패치 관리, 세션 매니저 접속을 처리합니다. SSH 없이 AWS 콘솔에서 인스턴스에 접근할 수 있게 합니다.

---

### `chronyd` — NTP 시간 동기화 데몬

네트워크 타임 프로토콜(NTP)로 시스템 시간을 동기화합니다. `ntpd`의 대체제로 더 빠른 동기화와 낮은 리소스 사용이 특징입니다.

```bash
chronyc tracking    # 동기화 상태 확인
chronyc sources     # NTP 서버 목록
```

---

### `cron` — 작업 스케줄러

`/etc/crontab`, `/etc/cron.d/`, 사용자 crontab에 정의된 작업을 주기적으로 실행합니다.

```bash
crontab -l          # 현재 사용자 crontab 확인
crontab -e          # crontab 편집
```

---

### `dbus-daemon` — D-Bus 메시지 버스

프로세스 간 통신(IPC)을 위한 메시지 버스입니다. systemd, NetworkManager, polkit 등 시스템 컴포넌트들이 서로 통신하는 데 사용합니다.

---

### `irqbalance` — IRQ 부하 분산 데몬

하드웨어 인터럽트(IRQ)를 여러 CPU 코어에 균등하게 분산시킵니다. 멀티코어 서버에서 네트워크/디스크 처리 성능을 고르게 유지합니다.

---

### `multipathd` — 다중 경로 I/O 데몬

스토리지 장치에 대한 다중 경로를 관리합니다. 경로 장애 시 자동으로 다른 경로로 전환하여 고가용성을 제공합니다. AWS EBS 환경에서 기본 실행됩니다.

---

### `networkd-dispatcher` — systemd-networkd 이벤트 디스패처

네트워크 인터페이스 상태 변경(up/down/configured) 시 스크립트를 실행합니다. `/etc/networkd-dispatcher/` 하위 스크립트를 트리거합니다.

---

### `apache2` — Apache HTTP 웹 서버

HTTP/HTTPS 요청을 처리하는 웹 서버입니다. 마스터 프로세스 1개 + 워커 프로세스 N개 구조로 동작합니다. PHP-FPM, mod_php 등과 연동하여 동적 콘텐츠를 처리합니다.

```bash
apache2ctl status           # 서버 상태 확인
apache2ctl configtest       # 설정 파일 문법 검사
systemctl reload apache2    # 무중단 설정 재로드
```

---

### `atd` — 일회성 작업 스케줄러

`at` 명령어로 등록된 일회성 작업을 지정된 시간에 실행합니다. `cron`이 반복 작업을 처리하는 것과 달리 단발성 예약 실행에 사용합니다.

```bash
echo "reboot" | at 02:00        # 새벽 2시에 재부팅 예약
atq                             # 예약된 작업 목록
atrm <job_id>                   # 예약 취소
```

---

### `memcached` — 인메모리 키-값 캐시 서버

DB 쿼리 결과, 세션, API 응답 등을 메모리에 저장하여 반복 요청 시 DB를 거치지 않고 빠르게 응답합니다. 재시작 시 데이터가 사라지는 휘발성 캐시입니다.

- 기본 포트: `11211`
- `-l 127.0.0.1` 옵션으로 로컬호스트만 바인딩 권장

```bash
echo "stats" | nc 127.0.0.1 11211   # 통계 확인
```

---

### `php-fpm5.6` / `php-fpm7.4` / `php-fpm8.2` — PHP FastCGI Process Manager

PHP 요청을 처리하는 FastCGI 데몬입니다. Apache/Nginx와 소켓으로 통신하며 마스터 프로세스 1개 + 워커 프로세스 N개 구조로 동작합니다. 여러 버전을 동시에 운영할 수 있어 사이트별로 다른 PHP 버전 사용이 가능합니다.

```bash
systemctl status php5.6-fpm
systemctl status php7.4-fpm
systemctl status php8.2-fpm
# 설정 파일
# /etc/php/5.6/fpm/pool.d/www.conf
# /etc/php/7.4/fpm/pool.d/www.conf
# /etc/php/8.2/fpm/pool.d/www.conf
```

---

### `syslog-ng` — 시스템 로그 수집 데몬

rsyslogd의 대체제로 더 유연한 로그 필터링, 파싱, 라우팅을 제공합니다. 로그를 파일, 원격 서버, DB 등 다양한 목적지로 전송할 수 있습니다.

```bash
syslog-ng --syntax-only      # 설정 파일 문법 검사
systemctl status syslog-ng
# 설정 파일: /etc/syslog-ng/syslog-ng.conf
```

---

### `ruby` — Ruby 애플리케이션 프로세스

Ruby로 작성된 애플리케이션 또는 서비스가 실행 중인 상태입니다. Rails, Sinatra, Fluentd, Chef 등 다양한 Ruby 기반 도구가 이 프로세스로 표시됩니다.

```bash
# 어떤 Ruby 스크립트가 실행 중인지 확인
ps aux | grep ruby
ls -la /proc/<pid>/exe    # 실행 파일 경로 확인
```

---

HTTP 서버, 리버스 프록시, 로드 밸런서로 사용됩니다. 마스터 프로세스 1개 + 워커 프로세스 N개 구조로 동작합니다.

```bash
nginx -t            # 설정 파일 문법 검사
nginx -s reload     # 무중단 설정 재로드
```

---

### `packagekitd` — 패키지 관리 추상화 데몬

apt, yum 등 배포판별 패키지 관리자를 통합된 인터페이스로 제공합니다. GNOME Software, unattended-upgrades 등이 사용합니다.

---

### `polkitd` — 권한 정책 데몬 (PolicyKit)

비권한 프로세스가 권한이 필요한 작업을 수행할 때 인증을 처리합니다. `sudo` 없이 특정 시스템 작업을 허용하는 정책을 관리합니다.

---

### `rsyslogd` — 시스템 로그 데몬

커널, 서비스, 애플리케이션 로그를 수집하여 `/var/log/` 하위에 기록합니다. 원격 로그 서버로 전송하는 기능도 제공합니다.

```bash
tail -f /var/log/syslog     # 실시간 시스템 로그
tail -f /var/log/auth.log   # 인증 로그
```

---

### `snapd` — Snap 패키지 관리 데몬

Canonical의 Snap 패키지 포맷을 관리합니다. 샌드박스 환경에서 애플리케이션을 격리하여 실행합니다.

```bash
snap list           # 설치된 snap 패키지 목록
snap refresh        # 업데이트
```

---

### `sshd` — SSH 서버 데몬

원격 SSH 접속을 처리합니다. 마스터 프로세스가 연결을 수신하고 각 세션마다 자식 프로세스를 생성합니다.

```bash
# 현재 SSH 접속자 확인
who
ss -tnp | grep :22
```

---

### `systemd` (사용자) — 사용자 세션 systemd

로그인한 사용자별로 실행되는 systemd 인스턴스입니다. 사용자 서비스, 타이머를 관리합니다. `(sd-pam)`은 PAM 인증 세션을 유지하는 보조 프로세스입니다.

---

### `systemd-journald` — 저널 로그 데몬

systemd 기반 로그를 바이너리 형식으로 수집/저장합니다. rsyslogd와 병행 동작하며 부팅 로그, 커널 로그를 포함합니다.

```bash
journalctl -f               # 실시간 로그
journalctl -u nginx         # 특정 서비스 로그
journalctl --since "1 hour ago"
```

---

### `systemd-logind` — 로그인 세션 관리 데몬

사용자 로그인 세션, 시트(seat), 전원 관리를 처리합니다. `who`, `loginctl` 명령어의 데이터를 제공합니다.

---

### `systemd-networkd` — 네트워크 설정 데몬

네트워크 인터페이스 설정을 관리합니다. `/etc/systemd/network/` 설정 파일 기반으로 IP, 라우팅을 구성합니다.

---

### `systemd-resolved` — DNS 리졸버 데몬

DNS 쿼리를 처리하고 캐싱합니다. `/etc/resolv.conf`를 관리하며 mDNS, LLMNR도 지원합니다.

```bash
resolvectl status           # DNS 설정 확인
resolvectl query example.com
```

---

### `systemd-udevd` — 장치 이벤트 관리 데몬

커널의 장치 이벤트(uevents)를 처리합니다. 새 하드웨어 감지 시 `/dev/` 노드 생성, 드라이버 로드, 심볼릭 링크 생성을 담당합니다.

---

### `unattended-upgr` — 자동 보안 업데이트 데몬

보안 패치를 자동으로 설치합니다. 기본적으로 보안 업데이트만 자동 적용하며 설정은 `/etc/apt/apt.conf.d/50unattended-upgrades`에서 관리합니다.

```bash
# 자동 업데이트 로그 확인
cat /var/log/unattended-upgrades/unattended-upgrades.log
```

---

### `vnstatd` — 네트워크 트래픽 통계 데몬

네트워크 인터페이스별 트래픽을 주기적으로 수집하여 DB에 저장합니다. 시간/일/월 단위 통계를 제공합니다.

```bash
vnstat                      # 전체 통계
vnstat -l                   # 실시간 모니터링
vnstat -h                   # 시간별 통계
vnstat -d                   # 일별 통계
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- systemd man pages: [systemd.io](https://systemd.io/) — ★★★☆☆
- Linux man-pages: [man7.org](https://man7.org/linux/man-pages/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-14

**마지막 업데이트**: 2026-05-14

© 2026 siasia86. Licensed under CC BY 4.0.

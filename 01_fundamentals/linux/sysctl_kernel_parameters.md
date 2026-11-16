# sysctl 커널 매개변수

`sysctl`은 실행 중인 커널의 동작 값을 `/proc/sys/` 아래 파일로 읽고 바꾸는 도구입니다. 이 문서는 설정을 확인·변경·영구 적용하는 방법, 설정 파일 우선순위, 시스템 엔지니어가 자주 다루는 메모리·네트워크·파일 관련 매개변수, 바꾸기 전 판단 기준을 다룹니다.

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 조회와 임시 변경](#2-조회와-임시-변경) / [3. 영구 적용](#3-영구-적용)         |
| [4. 메모리 매개변수](#4-메모리-매개변수) / [5. 네트워크 매개변수](#5-네트워크-매개변수)                |
| [6. 파일·프로세스 매개변수](#6-파일프로세스-매개변수) / [7. 보안 관련 매개변수](#7-보안-관련-매개변수) |
| [8. 변경 절차와 판단 기준](#8-변경-절차와-판단-기준) / [9. 장애 점검](#9-장애-점검)                    |

---

## 1. 개요

`/proc/sys/`는 커널이 만든 가상 파일 트리입니다. 경로의 `/`를 `.`으로 바꾸면 sysctl 이름이 됩니다.

```text
 /proc/sys/net/ipv4/ip_forward   <-->   net.ipv4.ip_forward
 /proc/sys/vm/swappiness         <-->   vm.swappiness
```

| 최상위 이름 | 다루는 영역                               |
|-------------|-------------------------------------------|
| `kernel.*`  | 커널 일반(panic, PID, 로그, sysrq 등)     |
| `vm.*`      | 가상 메모리(swap, dirty page, overcommit) |
| `net.*`     | 네트워크 스택(TCP, IP, 소켓 버퍼)         |
| `fs.*`      | 파일시스템(열린 파일 수, inotify)         |
| `dev.*`     | 장치별 값                                 |

`sysctl` 명령은 procps(procps-ng) 패키지가 제공합니다. 일부 값은 커널 모듈이 올라온 뒤에만 생깁니다(예: `net.bridge.*`는 `br_netfilter` 모듈 필요). 또 `net.*`의 많은 값은 network namespace마다 따로 있어서 컨테이너 안과 호스트의 값이 다를 수 있습니다. 가상 파일시스템 구조는 [Linux Virtual File System](./linux_virtual_fs.md)을 봅니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 조회와 임시 변경

```bash
# 한 값 조회
sysctl vm.swappiness
cat /proc/sys/vm/swappiness

# 값만 출력
sysctl -n vm.swappiness

# 전체 목록 중 검색
sysctl -a 2>/dev/null | grep -E '^net\.ipv4\.tcp_(fin|keepalive)'

# 정규식으로 일부만
sysctl -a -r '^vm\.dirty'
```

🟡 주의: 아래 변경은 즉시 운영 중인 커널에 적용됩니다. 재부팅하면 사라지지만 그 사이에 서비스 동작이 바뀝니다. 변경 전 값을 기록해 둡니다.

```bash
# 변경 전 값 기록
sysctl vm.swappiness > /root/sysctl_before_$(date +%F).txt

# 임시 변경 (재부팅하면 원래 값)
sudo sysctl -w vm.swappiness=10
echo 10 | sudo tee /proc/sys/vm/swappiness
```

`sudo echo 10 > /proc/sys/...`는 리다이렉션이 일반 사용자 권한으로 처리되어 실패합니다. `tee`나 `sysctl -w`를 씁니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 영구 적용

### 3.1 파일 위치와 우선순위

`sysctl --system`과 부팅 때 실행되는 `systemd-sysctl.service`는 다음 디렉토리의 `*.conf`를 읽습니다(procps sysctl(8) 기준, 위쪽 우선).

| 순서 | 위치                             | 용도                        |
|------|----------------------------------|-----------------------------|
| 1    | `/etc/sysctl.d/*.conf`           | 관리자 설정                 |
| 2    | `/run/sysctl.d/*.conf`           | 실행 중 생성된 설정         |
| 3    | `/usr/local/lib/sysctl.d/*.conf` | 로컬 설치 소프트웨어        |
| 4    | `/usr/lib/sysctl.d/*.conf`       | 배포판 패키지 기본값        |
| 5    | `/lib/sysctl.d/*.conf`           | 일부 배포판의 패키지 기본값 |
| 6    | `/etc/sysctl.conf`               | 전통적 단일 설정 파일       |

규칙은 두 가지입니다.

- 같은 파일 이름이 여러 디렉토리에 있으면 위쪽 디렉토리의 파일만 읽습니다. 패키지 기본 파일을 끄려면 `/etc/sysctl.d/`에 같은 이름으로 `/dev/null` 링크를 둡니다.
- 서로 다른 파일은 모든 디렉토리를 합쳐 파일 이름 사전순으로 적용하고, 같은 키가 여러 번 나오면 나중 값이 남습니다. 그래서 관리자 설정은 `99-` 같은 큰 번호로 시작합니다.

### 3.2 적용 예

```bash
sudo tee /etc/sysctl.d/90-app-tuning.conf >/dev/null <<'EOF'
# 2026-11-16 web tier tuning (ticket: <TICKET-ID>)
vm.swappiness = 10
net.core.somaxconn = 8192
net.ipv4.ip_local_port_range = 15000 64999
EOF

# 한 파일만 적용
sudo sysctl -p /etc/sysctl.d/90-app-tuning.conf

# 전체 설정 다시 적용 (부팅 때와 같은 순서)
sudo sysctl --system

# 적용 확인
sysctl vm.swappiness net.core.somaxconn net.ipv4.ip_local_port_range
```

`sysctl -p`를 인자 없이 쓰면 `/etc/sysctl.conf`만 읽습니다. `sysctl.d` 파일까지 확인하려면 `--system`을 씁니다. 각 파일에 변경 이유와 날짜를 주석으로 남기면 나중에 값을 되돌릴 근거가 됩니다.

[⬆ 목차로 돌아가기](#목차)

## 4. 메모리 매개변수

아래 기본값은 커널 문서 기준입니다. 배포판이 `/usr/lib/sysctl.d/`에서 다른 값을 줄 수 있으므로 실제 값은 `sysctl`로 확인합니다.

| 매개변수                    | 커널 기본값        | 뜻과 판단 기준                                                       |
|-----------------------------|--------------------|----------------------------------------------------------------------|
| `vm.swappiness`             | 60 (범위 0~200)    | 파일 캐시 대비 익명 메모리를 swap으로 보내는 경향. 낮추면 swap 덜 씀 |
| `vm.dirty_background_ratio` | 커널 문서 미기재   | 이 비율을 넘으면 백그라운드 flush 시작                               |
| `vm.dirty_ratio`            | 커널 문서 미기재   | 이 비율을 넘으면 쓰는 프로세스가 직접 flush하며 대기                 |
| `vm.overcommit_memory`      | 0                  | 0 추정 검사, 1 항상 허용, 2 엄격 제한(`overcommit_ratio`와 함께)     |
| `vm.max_map_count`          | 65530              | 프로세스당 메모리 매핑 수. Elasticsearch 등은 더 큰 값 요구          |
| `vm.min_free_kbytes`        | 메모리 크기로 계산 | 커널이 남겨 두는 여유 메모리. 너무 크면 바로 OOM                     |

`vm.dirty_*`의 기본값은 커널 문서에 적혀 있지 않습니다. Ubuntu 24.04(커널 6.8)에서 `dirty_background_ratio = 10`, `dirty_ratio = 20`으로 관찰했습니다(2026-11-16). `vm.max_map_count`도 배포판이 바꿀 수 있습니다(같은 환경에서 1048576 관찰).

`vm.drop_caches`는 설정값이 아니라 한 번 실행하는 명령입니다. 1은 페이지 캐시, 2는 dentry·inode 등 slab, 3은 둘 다 비웁니다. 커널 문서는 성능 문제를 일으킬 수 있고 시험·디버깅 밖에서는 권하지 않는다고 설명합니다.

```bash
# 시험 환경에서만: 캐시 비우고 콜드 캐시 성능 측정
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
```

메모리 동작 원리는 [가상 메모리 개념](./virtual_memory_concepts.md), [OOM·hang](./oom_hang.md)을 봅니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 네트워크 매개변수

| 매개변수                       | 커널 기본값             | 뜻과 판단 기준                                                          |
|--------------------------------|-------------------------|-------------------------------------------------------------------------|
| `net.core.somaxconn`           | 4096 (Linux 5.4 전 128) | `listen()` backlog 상한. 앱의 backlog 값도 함께 올려야 효과             |
| `net.ipv4.tcp_max_syn_backlog` | 메모리 크기로 결정      | SYN_RECV 상태로 기억하는 연결 요청 수                                   |
| `net.ipv4.tcp_syncookies`      | 1                       | SYN backlog가 넘칠 때 SYN cookie 사용                                   |
| `net.ipv4.ip_local_port_range` | 32768 60999             | 나가는 연결의 출발지 포트 범위. 프록시·대량 연결 시 고갈 점검           |
| `net.ipv4.tcp_tw_reuse`        | 2                       | 0 끔, 1 전체 허용, 2 loopback만 허용. TIME_WAIT 소켓을 새 연결에 재사용 |
| `net.ipv4.tcp_fin_timeout`     | 60초                    | FIN_WAIT_2 상태 유지 시간                                               |
| `net.ipv4.tcp_keepalive_time`  | 7200초(2시간)           | 유휴 연결에 keepalive를 보내기 시작하는 시간                            |
| `net.ipv4.ip_forward`          | 0                       | 인터페이스 간 패킷 전달. 라우터·컨테이너 호스트는 1                     |
| `net.ipv4.conf.*.rp_filter`    | 0                       | 출발지 검증. 1 strict, 2 loose (RFC 3704)                               |

판단할 때 확인할 점입니다.

- `somaxconn`만 올리고 앱(nginx `listen ... backlog=`, 언어 런타임의 backlog 인자)을 그대로 두면 효과가 없습니다. 실제 대기열 크기는 `ss -ltn`의 `Send-Q` 열로 확인합니다.
- 포트 고갈은 `ss -tan state time-wait | wc -l`과 출발지 포트 범위 크기를 비교해 판단합니다. `tcp_tw_reuse=1`은 나가는 연결에만 영향을 주며, NAT 뒤 환경에서는 충분히 시험한 뒤 씁니다.
- 예전 자료에 나오는 `net.ipv4.tcp_tw_recycle`은 Linux 4.12에서 삭제되었습니다. 최신 커널에는 이 키가 없습니다.
- `ip_forward`를 켜면 방화벽 정책이 함께 있어야 합니다. 관련 내용은 [netfilter·tc](./netfilter_tc.md)를 봅니다.

```bash
# listen 대기열 넘침 누적 횟수
nstat -az TcpExtListenOverflows TcpExtListenDrops
# 상태별 TCP 소켓 수
ss -s
```

TCP 상태 전이는 [TCP 상태 전이](../networking/tcp_state_concepts.md)를 봅니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 파일·프로세스 매개변수

| 매개변수                      | 뜻                                                       | 확인 명령                   |
|-------------------------------|----------------------------------------------------------|-----------------------------|
| `fs.file-max`                 | 시스템 전체 열린 파일 핸들 상한                          | `cat /proc/sys/fs/file-nr`  |
| `fs.nr_open`                  | 프로세스 하나가 가질 수 있는 파일 디스크립터 상한        | `sysctl fs.nr_open`         |
| `fs.inotify.max_user_watches` | 사용자당 inotify 감시 수. IDE·파일 동기화 도구가 많이 씀 | `sysctl fs.inotify`         |
| `kernel.pid_max`              | PID 최대값. 프로세스·스레드 수 상한에 영향               | `ps -eLf \| wc -l`          |
| `kernel.threads-max`          | 시스템 전체 스레드 상한                                  | `sysctl kernel.threads-max` |

`fs.file-max`를 올려도 프로세스별 제한(`ulimit -n`, systemd의 `LimitNOFILE=`)이 낮으면 "Too many open files"가 계속 납니다. 프로세스별 제한은 `cat /proc/<PID>/limits`로 확인하고 서비스 유닛에서 올립니다. 방법은 [systemd 유닛 관리](./systemd_unit_management.md)의 drop-in 절을 봅니다.

[⬆ 목차로 돌아가기](#목차)

## 7. 보안 관련 매개변수

방어 관점에서 점검하는 값입니다. 배포판 기본값이 이미 보호 쪽으로 잡혀 있는 경우가 많으므로 현재 값을 먼저 확인합니다.

| 매개변수                             | 보호 쪽 값 | 뜻                                            |
|--------------------------------------|------------|-----------------------------------------------|
| `kernel.randomize_va_space`          | 2          | 주소 공간 배치 무작위화(ASLR)                 |
| `kernel.kptr_restrict`               | 1 이상     | `/proc` 등에서 커널 주소 노출 제한            |
| `kernel.dmesg_restrict`              | 1          | 일반 사용자의 커널 로그 읽기 제한             |
| `kernel.yama.ptrace_scope`           | 1 이상     | 다른 프로세스 `ptrace` 제한(Yama LSM 사용 시) |
| `fs.protected_symlinks`              | 1          | 공용 쓰기 디렉토리의 심볼릭 링크 악용 방지    |
| `fs.protected_hardlinks`             | 1          | 권한 없는 파일로의 하드 링크 생성 제한        |
| `net.ipv4.conf.all.accept_redirects` | 0          | ICMP redirect 무시(라우터가 아닌 서버)        |
| `net.ipv4.conf.all.send_redirects`   | 0          | ICMP redirect 보내지 않음(라우터가 아닌 서버) |

`kernel.yama.ptrace_scope`를 높이면 `gdb -p`, `strace -p` 같은 디버깅 도구가 막힐 수 있습니다. 운영 정책과 디버깅 필요를 함께 정합니다. 서버 전반의 보안 기준은 [Linux 보안 강화](../../04_security/hardening/linux_hardening.md)를 봅니다.

[⬆ 목차로 돌아가기](#목차)

## 8. 변경 절차와 판단 기준

| 단계        | 할 일                                                                    |
|-------------|--------------------------------------------------------------------------|
| 근거 확인   | 증상과 지표(`nstat`, `ss`, `vmstat`, OOM 로그)로 병목이 커널 값인지 확인 |
| 문서 확인   | 커널 문서에서 단위·범위·부작용 확인. 블로그 값은 그대로 복사하지 않음    |
| 기록        | 변경 전 값을 파일로 남김                                                 |
| 임시 적용   | `sysctl -w`로 한 서버에 적용 후 지표 관찰                                |
| 영구 적용   | `/etc/sysctl.d/NN-이름.conf`에 이유·날짜 주석과 함께 기록                |
| 재부팅 확인 | 유지보수 시간에 재부팅 후 값이 남는지 확인                               |
| 배포        | 구성 관리 도구(Ansible 등)로 같은 파일을 배포해 서버 간 차이 제거        |

바꾸지 않는 편이 나은 경우도 있습니다.

- 지표로 확인한 문제가 없는데 "성능 튜닝 목록"을 통째로 적용하는 경우
- 단위나 의미를 모르는 값(예: `tcp_mem`은 바이트가 아니라 페이지 단위)
- 컨테이너 안에서 호스트 전체에 영향을 주는 값을 바꾸려는 경우

[⬆ 목차로 돌아가기](#목차)

## 9. 장애 점검

| 증상                                | 확인                                                    |
|-------------------------------------|---------------------------------------------------------|
| 재부팅 후 값이 돌아감               | `/etc/sysctl.d/`에 기록했는지, 더 뒤 번호 파일이 덮는지 |
| `sysctl: cannot stat /proc/sys/...` | 오타, 해당 커널에 없는 키, 모듈 미적재                  |
| `permission denied on key`          | root 아님, 또는 컨테이너에서 쓰기 금지된 키             |
| 부팅 때 일부 값이 적용 안 됨        | `journalctl -u systemd-sysctl -b`로 오류 확인           |
| `net.bridge.*` 값이 부팅 때 사라짐  | `br_netfilter` 모듈이 sysctl 적용보다 늦게 적재됨       |

```bash
# 어떤 파일이 어떤 값을 주는지 추적
grep -r 'somaxconn' /etc/sysctl.conf /etc/sysctl.d/ /run/sysctl.d/ /usr/lib/sysctl.d/ 2>/dev/null
# --system 적용 과정 출력 (파일별로 적용한 키를 보여 줌)
sudo sysctl --system
# 부팅 때 적용 결과
journalctl -u systemd-sysctl -b --no-pager
```

모듈 적재 순서 문제는 `/etc/modules-load.d/`에 모듈을 등록해 해결하는 경우가 많습니다. 컨테이너 런타임 문서([k3s](../../02_infrastructure/containers/k3s.md) 등)의 사전 준비 절차와 함께 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- sysctl(8) man page: [man7.org/linux/man-pages/man8/sysctl.8.html](https://man7.org/linux/man-pages/man8/sysctl.8.html) — ★★★☆☆ (확인일 2026-11-16)
- sysctl.d(5): [freedesktop.org/software/systemd/man/latest/sysctl.d.html](https://www.freedesktop.org/software/systemd/man/latest/sysctl.d.html) — ★★★☆☆ (확인일 2026-11-16)
- Linux kernel, Documentation for /proc/sys/vm/: [docs.kernel.org/admin-guide/sysctl/vm.html](https://docs.kernel.org/admin-guide/sysctl/vm.html) — ★★★☆☆ (확인일 2026-11-16)
- Linux kernel, IP Sysctl: [docs.kernel.org/networking/ip-sysctl.html](https://docs.kernel.org/networking/ip-sysctl.html) — ★★★☆☆ (확인일 2026-11-16)
- Linux kernel, Documentation for /proc/sys/kernel/: [docs.kernel.org/admin-guide/sysctl/kernel.html](https://docs.kernel.org/admin-guide/sysctl/kernel.html) — ★★★☆☆ (확인일 2026-11-16)
- Linux kernel, Documentation for /proc/sys/fs/: [docs.kernel.org/admin-guide/sysctl/fs.html](https://docs.kernel.org/admin-guide/sysctl/fs.html) — ★★★☆☆ (확인일 2026-11-16)
- RFC 3704 Ingress Filtering for Multihomed Networks: [datatracker.ietf.org/doc/html/rfc3704](https://datatracker.ietf.org/doc/html/rfc3704) — ★★★★☆ (확인일 2026-11-16)

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

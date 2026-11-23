# 프로세스 모니터링 (ps·top·htop·pgrep)
<!-- reference: _reference/procps_official_notes.md -->

Linux 서버에서 어떤 프로세스가 CPU·메모리를 쓰는지, 프로세스가 어떤 상태인지, 부하가 어느 정도인지를 확인하는 방법입니다. 이 문서만으로 설치 확인 → 프로세스 찾기·정렬 → 실시간 관찰 → 상태 해석 → 점검 순서까지 따라 할 수 있게 썼습니다.

- 기준 판: procps-ng 4.0.7, htop 3.5.3 (2026-11-23 확인)
- 예제 시험: 2026-11-23, procps 4.0.4·htop 3.3.0(Ubuntu 24.04)에서 3~6절 명령을 실행해 출력 형식을 확인. 출력 예시는 일반적인 값으로 바꿔 적음

## 목차

| 섹션                                                                                                                        |
|-----------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치 확인](#2-설치-확인) / [3. ps](#3-ps)                                                          |
| [4. top·htop](#4-tophtop) / [5. 프로세스 찾기와 상세](#5-프로세스-찾기와-상세) / [6. 상태와 부하 해석](#6-상태와-부하-해석) |
| [7. 점검 순서](#7-점검-순서) / [8. 검증](#8-검증) / [9. 트러블슈팅](#9-트러블슈팅)                                          |
| [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                                                                           |

---

## 1. 개요

| 도구                     | 하는 일                                | 쓰는 때                        |
|--------------------------|----------------------------------------|--------------------------------|
| `ps`                     | 지금 순간의 프로세스 목록              | 스크립트, 특정 조건으로 고르기 |
| `top`                    | 주기적으로 갱신되는 목록과 시스템 요약 | 기본 설치된 실시간 관찰        |
| `htop`                   | 색상·트리·마우스를 지원하는 top        | 사람이 보는 실시간 관찰        |
| `pgrep`·`pkill`          | 이름·사용자로 PID 찾기·신호 보내기     | 스크립트에서 PID 얻기          |
| `uptime`·`/proc/loadavg` | load average                           | 부하 추세 확인                 |
| `pidstat`                | 프로세스별 CPU·I/O를 시간 간격으로     | 짧은 기간 기록 (sysstat)       |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치 확인

`ps`·`top`·`pgrep`·`free`·`vmstat`은 procps 패키지로 기본 설치되어 있습니다. `htop`은 따로 설치합니다.

```bash
ps --version                         # ps from procps-ng 4.0.x
sudo apt-get install -y htop         # Ubuntu / Debian
sudo dnf install -y htop             # RHEL 계열 (EPEL 저장소)
htop --version
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. ps

```bash
ps aux                                           # 전체 프로세스 (BSD 형식)
ps -ef                                           # 전체 프로세스 (표준 형식, PPID 포함)
ps -eo pid,ppid,user,stat,%cpu,%mem,etime,comm --sort=-%cpu | head    # CPU 많이 쓰는 순
ps -eo pid,user,rss,comm --sort=-rss | head      # 실제 메모리(RSS, KiB) 많이 쓰는 순
ps -ejH                                          # 부모-자식 트리
ps -o pid,stat,wchan:20,cmd -p 1234              # 특정 PID의 상태와 대기 지점
ps -eLf | wc -l                                  # 스레드 수 (대략)
```

| 열           | 뜻                                                          |
|--------------|-------------------------------------------------------------|
| `PID`·`PPID` | 프로세스 ID, 부모 프로세스 ID                               |
| `STAT`       | 상태 (6-1). 뒤 글자 `s` 세션 리더, `l` 멀티스레드, `+` 전경 |
| `%CPU`       | 프로세스 수명 동안의 평균 CPU 사용률 (순간값이 아님)        |
| `%MEM`·`RSS` | 실제 메모리 사용 비율·크기(KiB)                             |
| `ETIME`      | 시작 후 지난 시간                                           |
| `WCHAN`      | 커널 안에서 기다리는 함수                                   |

`ps`의 `%CPU`는 순간값이 아니므로 지금 바쁜 프로세스를 찾을 때는 `top`·`pidstat`을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. top·htop

```bash
top                       # 대화형 (q 종료)
top -b -n 1 | head -15    # 한 번만 출력 (스크립트·로그용)
top -p 1234               # 특정 PID만
```

`top` 머리 부분 읽는 법:

```text
top - 10:00:00 up 31 days,  load average: 0.57, 0.38, 0.25
Tasks: 300 total,   1 running, 299 sleeping,   0 stopped,   0 zombie
%Cpu(s):  2.0 us,  1.0 sy,  0.0 ni, 96.5 id,  0.5 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :   7939.2 total,   1738.4 free,   3970.6 used,   2602.5 buff/cache
MiB Swap:   4096.0 total,   4096.0 free,      0.0 used.   3968.6 avail Mem
```

| 항목        | 뜻                                                             |
|-------------|----------------------------------------------------------------|
| `us`·`sy`   | 사용자 공간·커널 공간 CPU                                      |
| `wa`        | I/O를 기다리며 쉬는 CPU (디스크 병목 신호)                     |
| `st`        | 가상 머신에서 하이퍼바이저가 가져간 CPU                        |
| `avail Mem` | 스왑 없이 새로 쓸 수 있는 메모리 추정치. `free`보다 이 값을 봄 |

| top 대화형 키 | 동작                 |
|---------------|----------------------|
| `P` / `M`     | CPU / 메모리 순 정렬 |
| `1`           | CPU별 표시           |
| `c`           | 전체 명령줄 표시     |
| `k`           | PID에 신호 보내기    |
| `H`           | 스레드 단위 표시     |

`htop`은 `F5` 트리, `F6` 정렬 열, `F4` 필터, `F9` 신호 보내기를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 프로세스 찾기와 상세

```bash
pgrep -a nginx                  # 이름에 nginx가 들어간 프로세스의 PID와 명령줄
pgrep -x -u www-data nginx      # 이름이 정확히 같고 사용자가 www-data인 것
pkill -HUP -x nginx             # 이름이 정확히 nginx인 프로세스에 HUP 신호

cat /proc/1234/status | grep -E '^(State|VmRSS|Threads)'   # 상태, 실제 메모리, 스레드 수
ls -l /proc/1234/cwd /proc/1234/exe                        # 작업 디렉터리, 실행 파일
tr '\0' ' ' < /proc/1234/cmdline; echo                     # 전체 명령줄
cat /proc/1234/limits | grep 'open files'                  # 열 수 있는 파일 수 제한
```

`pkill`은 맞는 프로세스 모두에 신호를 보내므로, 먼저 같은 조건의 `pgrep -a`로 대상을 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 상태와 부하 해석

### 6-1. 프로세스 상태

| 코드 | 상태                                 | 많을 때 의심할 것                            |
|------|--------------------------------------|----------------------------------------------|
| `R`  | 실행 중 또는 실행 대기               | CPU 부족                                     |
| `S`  | 깨울 수 있는 대기 (이벤트 기다림)    | 정상 (대부분의 프로세스)                     |
| `D`  | 깨울 수 없는 대기 (주로 I/O)         | 디스크·NFS 지연, 저장 장치 문제              |
| `Z`  | 좀비 (끝났지만 부모가 회수하지 않음) | 부모 프로세스의 버그. 부모를 재시작해야 정리 |
| `T`  | 정지 (신호·디버거)                   | 누가 멈췄는지 확인                           |
| `I`  | 유휴 커널 스레드                     | 정상                                         |

```bash
ps -eo stat= | cut -c1 | sort | uniq -c          # 상태별 개수
ps -eo pid,ppid,stat,comm | awk '$3 ~ /^Z/'      # 좀비와 그 부모 PID
ps -eo pid,stat,wchan:20,comm | awk '$2 ~ /^D/'  # D 상태와 대기 지점
```

### 6-2. load average

load average는 1·5·15분 동안 실행 대기(R)와 깨울 수 없는 대기(D) 상태에 있던 작업 수의 평균입니다.

```bash
uptime                # load average: 0.57, 0.38, 0.25
nproc                 # CPU 수
```

- CPU 수보다 꾸준히 크면 일이 밀리고 있습니다. 이때 `top`의 `us`·`sy`가 높으면 CPU 부족, `wa`가 높거나 D 상태가 많으면 I/O 대기입니다.
- 1분 값이 15분 값보다 크면 부하가 늘고 있고, 작으면 줄고 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 점검 순서

서버가 느리다는 연락을 받았을 때의 첫 1분 점검 순서입니다.

```bash
uptime                                            # 1. 부하 추세
top -b -n 1 | head -5                             # 2. CPU us/sy/wa/st, 메모리
ps -eo pid,stat,%cpu,%mem,comm --sort=-%cpu | head -6   # 3. CPU 상위
ps -eo pid,rss,comm --sort=-rss | head -6         # 4. 메모리 상위
ps -eo stat= | cut -c1 | sort | uniq -c           # 5. D·Z 상태 개수
dmesg -T | tail -20                               # 6. OOM·디스크 오류 같은 커널 메시지
```

CPU 사용을 시간 간격으로 기록하려면 `pidstat 1 5`(sysstat)를, 시스템 전체 추세는 sysstat의 `sar`를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 검증

| 순서 | 확인 내용     | 명령                                           | 기대 결과                         |
|------|---------------|------------------------------------------------|-----------------------------------|
| 1    | 도구 설치     | `ps --version`, `htop --version`               | 판 번호                           |
| 2    | 상위 프로세스 | `ps -eo pid,%cpu,comm --sort=-%cpu \| head -3` | 머리글과 CPU 순 목록              |
| 3    | 배치 출력     | `top -b -n 1 \| head -5`                       | load·Tasks·CPU·메모리 줄          |
| 4    | PID 찾기      | `pgrep -a -x sshd`                             | sshd PID와 명령줄                 |
| 5    | 상태 분포     | `ps -eo stat= \| cut -c1 \| sort \| uniq -c`   | 대부분 `S`, `D`·`Z`는 0 또는 소수 |
| 6    | 부하와 CPU 수 | `cat /proc/loadavg; nproc`                     | load가 CPU 수보다 꾸준히 작음     |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                        | 원인                                       | 해결 방법                                                    |
|---------------------------------------------|--------------------------------------------|--------------------------------------------------------------|
| load가 높은데 CPU 사용률은 낮음             | D 상태(I/O 대기) 작업이 load에 포함됨      | 6-1로 D 상태 확인, `iostat -x`로 디스크 확인                 |
| `ps`의 %CPU와 `top`의 %CPU가 다름           | `ps`는 수명 평균, `top`은 갱신 간격의 값   | 순간값은 `top`·`pidstat`                                     |
| 좀비가 계속 늘어남                          | 부모가 자식을 회수(wait)하지 않음          | 부모 프로세스 수정·재시작 (좀비 자체는 kill로 안 지워짐)     |
| `free`가 거의 0                             | 남는 메모리를 페이지 캐시로 쓰는 정상 동작 | `available` 값으로 판단                                      |
| 컨테이너 안 `top`이 호스트 메모리를 보여 줌 | /proc가 호스트 값을 보여 줌                | cgroup 값(`/sys/fs/cgroup/memory.max` 등)이나 `docker stats` |
| `htop` 설치가 안 됨 (RHEL)                  | EPEL 저장소 없음                           | EPEL 활성 후 설치                                            |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [sysstat](./sysstat.md) — sar·mpstat·iostat로 시간대별 성능 기록
- [pidstat](./pidstat.md) — 프로세스별 CPU·I/O 간격 측정
- [Linux 시스템 프로세스](./linux_system_processes.md) — 기본 시스템 프로세스의 역할
- [프로세스 수명](./process_lifecycle.md) — fork·exec·좀비가 생기는 원리
- [OOM과 hang](./oom_hang.md) — 메모리 부족 대응
- [atop](./atop.md) — 과거 시점의 프로세스 기록

---

## 참고 자료

- procps-ng: [procps](https://gitlab.com/procps-ng/procps) — ★★★☆☆
- Linux man-pages: [ps(1)](https://man7.org/linux/man-pages/man1/ps.1.html) · [top(1)](https://man7.org/linux/man-pages/man1/top.1.html) — ★★★☆☆
- Linux man-pages: [proc_pid_status(5)](https://man7.org/linux/man-pages/man5/proc_pid_status.5.html) — ★★★☆☆
- htop: [htop-dev/htop](https://github.com/htop-dev/htop) — ★★★☆☆

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

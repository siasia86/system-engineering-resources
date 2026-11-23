# sysstat (sar·mpstat·iostat)
<!-- reference: _reference/sysstat_official_notes.md -->

sysstat는 CPU·메모리·디스크·네트워크 사용량을 주기적으로 기록하고, 지금이나 과거 시점의 성능을 보고하는 도구 모음입니다. "어제 새벽 3시에 왜 느렸나"처럼 지나간 시점을 확인할 수 있다는 점이 top과 다릅니다. 이 문서만으로 설치 → 수집 켜기 → 실시간·과거 보고 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: sysstat 12.8.1 (2026-11-23 확인)
- 예제 시험: 2026-11-23, Ubuntu 24.04의 sysstat 12.6.1에서 3~5절 명령을 실행하고, `rockylinux/rockylinux:10` 컨테이너에서 단위 파일과 기록 위치를 확인

## 목차

| 섹션                                                                                               |
|----------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치와 수집 켜기](#2-설치와-수집-켜기) / [3. 실시간 보고](#3-실시간-보고) |
| [4. 과거 기록 보기](#4-과거-기록-보기) / [5. 해석 기준](#5-해석-기준) / [6. 검증](#6-검증)         |
| [7. 트러블슈팅](#7-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                 |

---

## 1. 개요

| 도구               | 하는 일                                                     |
|--------------------|-------------------------------------------------------------|
| `sar`              | CPU·메모리·I/O·네트워크 등 시스템 통계를 실시간·과거로 보고 |
| `sadc`·`sa1`·`sa2` | 통계 수집(타이머가 실행), 일일 요약                         |
| `sadf`             | 기록 파일을 CSV·JSON 등으로 내보내기                        |
| `mpstat`           | CPU별 사용률                                                |
| `iostat`           | 디스크 장치별 I/O                                           |
| `pidstat`          | 프로세스별 CPU·메모리·I/O                                   |

`vmstat`과 `free`는 sysstat가 아니라 procps 패키지에 들어 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치와 수집 켜기

```bash
sudo apt-get install -y sysstat      # Ubuntu / Debian
sudo dnf install -y sysstat          # RHEL 계열

sudo systemctl enable --now sysstat              # 수집 켜기
systemctl list-timers 'sysstat*'                 # sysstat-collect.timer(10분마다, OnCalendar=*:00/10), sysstat-summary.timer
```

| 배포판        | 기록 위치               | 참고                                                    |
|---------------|-------------------------|---------------------------------------------------------|
| Debian·Ubuntu | `/var/log/sysstat/saDD` | `/etc/default/sysstat`의 `ENABLED`는 cron 방식에만 쓰임 |
| RHEL 계열     | `/var/log/sa/saDD`      |                                                         |

`DD`는 날짜(일)입니다. 보관 기간은 설정 파일의 `HISTORY` 값(일)이며 배포판마다 기본값이 다릅니다. Ubuntu 24.04는 `/etc/sysstat/sysstat`에 7일, Rocky Linux 10은 `/etc/sysconfig/sysstat`에 28일입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 실시간 보고

간격(초)과 횟수를 붙이면 그동안의 값을 보여 주고 마지막에 평균(`Average`)을 냅니다.

```bash
sar -u 1 5                 # CPU 사용률 1초 간격 5회
sar -q 1 5                 # 실행 큐와 load average
sar -r 1 3                 # 메모리
sar -b 1 3                 # 전체 I/O 횟수
sar -n DEV 1 3             # 네트워크 인터페이스별 송수신
mpstat -P ALL 1 3          # CPU별 사용률
iostat -xz 1 3             # 장치별 확장 통계 (-z: 활동 없는 장치 숨김)
pidstat 1 5                # 프로세스별 CPU
```

`iostat`의 첫 번째 보고는 부팅 이후 평균이므로, 지금 상태는 두 번째 보고부터 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 과거 기록 보기

```bash
sar -u                                         # 오늘 기록 전체 (CPU)
sar -u -f /var/log/sysstat/sa15                # 15일 기록 (RHEL은 /var/log/sa/sa15)
sar -u -s 02:00:00 -e 04:00:00 -f /var/log/sysstat/sa15   # 15일 02~04시
sar -A -f /var/log/sysstat/sa15 > sa15.txt     # 모든 보고를 파일로
sadf -d /var/log/sysstat/sa15 -- -u > cpu.csv  # CSV로 내보내기 (세미콜론 구분)
```

장애 시각을 알면 그 시각 앞뒤로 `-u`(CPU), `-r`(메모리), `-b`·`-d`(I/O), `-n DEV`(네트워크), `-q`(부하)를 차례로 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 해석 기준

| 보고         | 볼 값                                  | 의심할 상황                                                                                                |
|--------------|----------------------------------------|------------------------------------------------------------------------------------------------------------|
| `sar -u`     | `%user`+`%system`, `%iowait`, `%steal` | 합이 꾸준히 높음 = CPU 부족, `%iowait` 높음 = 디스크 대기, `%steal` 높음 = 가상 머신 호스트가 CPU를 가져감 |
| `sar -q`     | `runq-sz`, `ldavg-1`                   | CPU 수보다 꾸준히 큼                                                                                       |
| `sar -r`     | `%memused`보다 `kbavail`               | `kbavail`이 계속 줄어듦                                                                                    |
| `iostat -x`  | `r_await`·`w_await`, `aqu-sz`, `%util` | 대기 시간이 길고 큐가 쌓임 (SSD는 `%util` 100%여도 여유가 있을 수 있음)                                    |
| `sar -n DEV` | `rxkB/s`·`txkB/s`, `%ifutil`           | 인터페이스 대역폭에 가까움                                                                                 |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검증

| 순서 | 확인 내용   | 명령                                                 | 기대 결과                    |
|------|-------------|------------------------------------------------------|------------------------------|
| 1    | 설치        | `sar -V`                                             | sysstat 판                   |
| 2    | 수집 켜짐   | `systemctl is-enabled sysstat sysstat-collect.timer` | `enabled` 두 줄              |
| 3    | 기록 파일   | `ls /var/log/sysstat/` (RHEL `/var/log/sa/`)         | 오늘 날짜의 `saDD` 파일      |
| 4    | 과거 보고   | `sar -u \| tail -3`                                  | 10분 간격의 기록과 `Average` |
| 5    | 실시간 보고 | `sar -u 1 2`                                         | 1초 간격 두 줄과 `Average`   |
| 6    | 장치 통계   | `iostat -xz 1 2`                                     | 두 번째 보고에 지금 값       |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 트러블슈팅

| 증상                                             | 원인                                    | 해결 방법                                        |
|--------------------------------------------------|-----------------------------------------|--------------------------------------------------|
| `Cannot open /var/log/sysstat/saDD`              | 수집이 꺼져 있음, 오늘 첫 수집 전       | `systemctl enable --now sysstat`, 10분 기다림    |
| Debian에서 `ENABLED="true"`로 바꿔도 기록이 없음 | systemd 타이머가 꺼져 있음              | 타이머 활성 확인 (2절)                           |
| 다른 서버의 기록 파일을 읽으면 오류              | sysstat 판마다 파일 형식이 다를 수 있음 | 같은 판으로 읽거나 그 서버에서 `sadf`로 내보내기 |
| 보고 시각이 예상과 다름                          | 시간대                                  | `LC_TIME`·`TZ` 확인, `-t`(기록된 현지 시각) 사용 |
| 기록이 너무 오래 쌓임·부족함                     | 보관 기간 설정                          | `HISTORY` 값 조정 (2절의 설정 파일)              |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [프로세스 모니터링](./process_monitoring.md) — ps·top으로 지금 상태 보기
- [iostat](./iostat.md) · [pidstat](./pidstat.md) — 장치·프로세스별 상세
- [perf](./perf.md) — CPU를 어디에 쓰는지 함수 단위로
- [nmon](./nmon.md) · [atop](./atop.md) — 다른 성능 기록 도구
- [Prometheus·Grafana](../../02_infrastructure/monitoring/prometheus_grafana.md) — 여러 서버를 모아 보는 모니터링

---

## 참고 자료

- sysstat: [sysstat home](https://sysstat.github.io/) · [GitHub](https://github.com/sysstat/sysstat) — ★★★☆☆
- Linux man-pages: [sar(1)](https://man7.org/linux/man-pages/man1/sar.1.html) · [mpstat(1)](https://man7.org/linux/man-pages/man1/mpstat.1.html) · [iostat(1)](https://man7.org/linux/man-pages/man1/iostat.1.html) — ★★★☆☆

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

# Storage Tools - Linux 저장장치 도구 선택 가이드

Linux 저장장치 문제를 확인할 때 사용하는 도구를 관찰 범위와 목적에 따라 분류합니다. 장치 구조, 파일시스템 공간, 프로세스 I/O, 디바이스 I/O, 지연시간, 성능 테스트, 장치 상태를 구분하여 필요한 도구를 선택합니다.

## 목차

| 섹션                                                                                                                                                    |
|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 저장장치 관찰 범위](#2-저장장치-관찰-범위) / [3. 장치와 마운트 구조](#3-장치와-마운트-구조)                                    |
| [4. 파일시스템 공간 사용량](#4-파일시스템-공간-사용량) / [5. 프로세스와 디바이스 I/O](#5-프로세스와-디바이스-io) / [6. 종합 모니터링](#6-종합-모니터링) |
| [7. 지연시간과 성능 측정](#7-지연시간과-성능-측정) / [8. 장치 상태 점검](#8-장치-상태-점검) / [9. 상황별 도구 선택](#9-상황별-도구-선택)                |
| [10. 표준 점검 순서](#10-표준-점검-순서) / [11. 측정 시 주의사항](#11-측정-시-주의사항) / [12. 요약](#12-요약)                                          |

---

## 1. 개요

저장장치 문제는 하나의 명령어만으로 원인을 확인하기 어렵습니다. 디스크 공간 부족, 특정 프로세스의 과도한 I/O, 디바이스 대기, 높은 지연시간, 하드웨어 오류는 서로 다른 도구로 확인해야 합니다.

```text
저장장치 문제
    ├── 구조·마운트 확인       → lsblk, findmnt, blkid
    ├── 공간 부족 확인         → df, du, ncdu
    ├── 프로세스 확인          → iotop, pidstat
    ├── 디바이스 상태 확인     → iostat, dstat, atop, nmon
    ├── 지연시간 확인          → ioping
    ├── 성능 테스트            → fio, hdparm
    └── 장치 건강 상태         → smartctl, nvme-cli
```

이 문서는 각 도구의 상세 매뉴얼이 아니라, 문제 상황에 맞는 도구를 고르는 통합 가이드입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 저장장치 관찰 범위

| 분류          | 도구                        | 확인 대상                          |
|---------------|-----------------------------|------------------------------------|
| 장치·마운트   | `lsblk`, `findmnt`, `blkid` | 디스크, 파티션, 파일시스템 구조    |
| 파일시스템    | `df`                        | 전체·사용·가용 공간                |
| 파일·디렉토리 | `du`, `ncdu`                | 경로별 공간 사용량                 |
| 프로세스 I/O  | `iotop`, `pidstat -d`       | I/O를 발생시키는 프로세스          |
| 디바이스 I/O  | `iostat`                    | 처리량, 대기시간, 사용률, 요청량   |
| 종합 모니터   | `dstat`, `atop`, `nmon`     | CPU·메모리·디스크·네트워크 통합    |
| 지연시간      | `ioping`                    | 파일시스템·저장장치 I/O 응답시간   |
| 성능 테스트   | `fio`, `hdparm`             | 읽기·쓰기·순차 성능                |
| 장치 상태     | `smartctl`, `nvme-cli`      | HDD·SSD·NVMe 건강 상태와 장치 정보 |

> I/O(Input/Output): CPU나 프로그램과 저장장치 사이에서 데이터를 읽고 쓰는 작업입니다. 저장장치 문제를 분석할 때는 공간 사용량과 I/O 성능을 별도로 확인해야 합니다.

> Latency(지연시간): I/O 요청을 보낸 시점부터 처리가 완료될 때까지 걸리는 시간입니다. Throughput(처리량)은 단위 시간에 처리한 데이터 양이며, 두 지표는 서로 다를 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 장치와 마운트 구조

공간이나 성능을 분석하기 전에 대상 디스크와 파일시스템의 연결 구조를 확인합니다.

### 블록 디바이스 구조

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS,MODEL
```

### 경로가 속한 파일시스템

```bash
findmnt -T /var
findmnt -T /data
```

### 파일시스템 식별자 확인

```bash
sudo blkid
```

확인할 내용은 다음과 같습니다.

- 대상 경로가 어느 디바이스에 연결되어 있는지 확인합니다.
- 파티션과 파일시스템 종류를 확인합니다.
- 별도 파일시스템이 하위 디렉토리에 마운트되어 있는지 확인합니다.
- `du`와 `df`의 범위가 다른 원인을 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 파일시스템 공간 사용량

### `df` — 파일시스템 전체 공간

`df`는 파일시스템 단위의 전체·사용·가용 공간을 확인합니다.

```bash
df -hT
df -hT /var
```

```text
df
    └── 파일시스템 전체가 얼마나 사용되었는지 확인
```

### `du` — 파일·디렉토리별 공간

`du`는 특정 경로 아래에서 파일과 디렉토리가 사용하는 공간을 계산합니다.

```bash
sudo du -xh --max-depth=1 /var | sort -h
```

`-x`는 시작 경로와 다른 파일시스템으로 넘어가지 않도록 제한합니다. `/home`이나 `/backup`처럼 별도 파일시스템이 마운트된 경로를 분석할 때는 범위를 의도적으로 선택해야 합니다.

### `ncdu` — 대화형 공간 분석

`ncdu`는 `du` 결과를 대화형 화면에서 탐색할 때 사용합니다.

```bash
sudo ncdu -x /var
```

```text
방향키   항목 이동
Enter    디렉토리 진입
q        종료
```

`ncdu`의 `d` 키는 삭제 동작으로 이어질 수 있으므로, 공간 분석만 할 때는 삭제 키를 사용하지 않습니다.

### `df`와 `du`의 차이

```text
df
    └── 파일시스템 관점: 전체·사용·가용 공간

du / ncdu
    └── 파일 관점: 어떤 경로가 공간을 사용하는지
```

삭제된 파일을 프로세스가 계속 열고 있거나, 파일시스템 예약 공간이 존재하면 `df`와 `du`의 결과가 다를 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 프로세스와 디바이스 I/O

### `iotop` — 프로세스별 I/O

현재 어떤 프로세스가 읽기·쓰기를 많이 발생시키는지 확인합니다.

```bash
sudo iotop
sudo iotop -b -n 3
```

상세 내용은 [`iotop` 문서](./iotop.md)를 참고합니다.

### `pidstat -d` — 프로세스별 통계

`sysstat` 패키지의 `pidstat`는 프로세스별 I/O 통계를 주기적으로 출력합니다.

```bash
pidstat -d 1 5
```

프로세스별 읽기·쓰기 속도와 I/O 대기 관련 지표를 확인할 때 사용합니다.

### `iostat` — 디바이스별 통계

`iostat`는 디바이스별 처리량, 요청량, 대기시간, 사용률을 확인합니다.

```bash
iostat -xz 1 5
```

주요 관찰 항목은 다음과 같습니다.

- `r/s`, `w/s`: 초당 읽기·쓰기 요청 수.
- `rkB/s`, `wkB/s`: 초당 읽기·쓰기 처리량.
- `await`: I/O 요청의 평균 대기시간.
- `%util`: 디바이스가 I/O를 처리 중인 시간 비율.
- `avgqu-sz`: 평균 I/O 큐 길이.

`iotop`은 원인을 발생시킨 프로세스를 찾는 데 유리하고, `iostat`은 디바이스가 병목인지 판단하는 데 유리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 종합 모니터링

여러 자원을 한 화면에서 함께 확인해야 할 때 사용합니다.

| 도구    | 주요 특징                            | 적합한 상황                   |
|---------|--------------------------------------|-------------------------------|
| `dstat` | CPU·메모리·디스크·네트워크 통합 출력 | 짧은 구간의 시스템 상태 확인  |
| `atop`  | 시스템·프로세스 상태와 기록 기능     | 현재 상태 및 기록 데이터 분석 |
| `nmon`  | 대화형 종합 성능 모니터              | 운영 중 빠른 화면 점검        |

### `nmon` 디스크 화면

`nmon` 실행 후 `d` 키를 입력하면 디스크 I/O 화면을 표시합니다.

```bash
nmon
# 실행 후 d 입력
```

`nmon`의 디스크 화면은 현재 발생 중인 I/O를 관찰하는 기능이며, 별도의 디스크 성능 테스트를 수행하지 않습니다.

### 선택 시 주의

- `dstat`은 배포판과 패키지 버전에 따라 제공 여부와 옵션이 다를 수 있습니다.
- `atop`의 과거 데이터 분석은 기록 설정 여부에 따라 달라집니다.
- `nmon`은 대화형 확인에는 편리하지만 상세한 원인 분석은 `iostat`이나 `iotop`과 함께 수행합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 지연시간과 성능 측정

### `ioping` — I/O 지연시간

`ioping`은 파일시스템 경로, 파일 또는 디바이스를 대상으로 I/O 응답시간을 측정합니다.

```bash
ioping -c 10 /data
ioping -D -c 20 -s 4k /data
ioping -D -c 20 -s 1m -L /data
```

- `4k`: 작은 요청의 지연시간과 IOPS 확인.
- `1m -L`: 큰 순차 요청의 처리량 확인.
- `-D`: Direct I/O를 사용하여 캐시 영향을 줄임.

상세 내용은 [`ioping` 문서](./ioping.md)를 참고합니다.

### `fio` — 통제된 성능 테스트

`fio`는 블록 크기, 읽기·쓰기 비율, 큐 깊이, 동시성, 접근 패턴을 지정하여 성능을 측정합니다.

```text
작은 랜덤 I/O
    └── 4k, random, read/write 비율, queue depth 지정

큰 순차 I/O
    └── 1m, sequential, read 또는 write 지정
```

`fio`는 실제 부하를 발생시키는 벤치마크 도구입니다. 테스트 파일이나 테스트 디바이스를 명확히 지정해야 합니다.

### `hdparm` — ATA/SATA 장치 확인

`hdparm`은 ATA/SATA 계열 장치의 정보 확인과 단순 순차 읽기 테스트에 사용합니다.

```bash
sudo hdparm -I /dev/sdb
sudo hdparm -tT /dev/sdb
```

- `-I`: 장치 정보 확인.
- `-t`: 디스크의 순차 읽기 처리량 확인.
- `-T`: 캐시 읽기 처리량 확인.

`hdparm`은 I/O 지연시간을 분석하는 `ioping`의 대체 도구가 아닙니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 장치 상태 점검

### `smartctl` — S.M.A.R.T. 상태

```bash
sudo smartctl -H /dev/sdb
sudo smartctl -a /dev/sdb
```

`smartctl`은 지원되는 저장장치의 건강 상태와 진단 정보를 확인합니다.

> S.M.A.R.T.(Self-Monitoring, Analysis and Reporting Technology): 저장장치가 자체 상태와 오류 관련 지표를 보고하는 기능입니다. 장치와 연결 방식에 따라 지원되는 정보가 달라질 수 있습니다.

### `nvme-cli` — NVMe 장치

```bash
sudo nvme list
sudo nvme smart-log /dev/nvme0
```

NVMe 장치는 `hdparm`보다 `nvme-cli`를 사용하는 것이 적합합니다. 컨트롤러와 네임스페이스 구조를 먼저 확인한 뒤 대상 장치를 지정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 상황별 도구 선택

| 상황                           | 1차 도구           | 추가 확인 도구 |
|--------------------------------|--------------------|----------------|
| 디스크·파티션 구조 확인        | `lsblk`, `findmnt` | `blkid`        |
| 파일시스템 공간 부족           | `df`               | `du`, `ncdu`   |
| 큰 디렉토리 찾기               | `du`               | `ncdu`         |
| I/O를 발생시키는 프로세스 확인 | `iotop`            | `pidstat -d`   |
| 디바이스 병목 확인             | `iostat -xz`       | `atop`, `nmon` |
| 파일시스템 지연시간 확인       | `ioping`           | `iostat`       |
| 조건을 통제한 성능 테스트      | `fio`              | `ioping`       |
| ATA/SATA 순차 읽기 확인        | `hdparm -t`        | `hdparm -I`    |
| HDD·SSD 건강 상태 확인         | `smartctl`         | 제조사 도구    |
| NVMe 건강 상태 확인            | `nvme smart-log`   | `smartctl`     |

`du`, `ncdu`는 공간 사용량을 확인하며 디스크 성능을 측정하지 않습니다. 반대로 `ioping`, `fio`, `hdparm`은 공간 부족 원인을 찾는 도구가 아닙니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 표준 점검 순서

### 1단계: 구조와 공간 확인

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS,MODEL
findmnt -T /data
df -hT /data
sudo du -xh --max-depth=1 /data | sort -h
```

### 2단계: 현재 I/O 원인 확인

```bash
pidstat -d 1 5
sudo iotop -b -n 3
iostat -xz 1 5
```

### 3단계: 지연시간 확인

```bash
ioping -D -c 20 -s 4k /data
ioping -D -c 20 -s 1m -L /data
```

### 4단계: 장치 상태 확인

```bash
sudo smartctl -H /dev/sdb
sudo nvme smart-log /dev/nvme0
```

### 5단계: 성능 테스트

원인 분석과 운영 영향 검토가 끝난 뒤 테스트 환경에서 `fio` 또는 `hdparm`을 사용합니다. 운영 디바이스에 직접 쓰기 테스트를 실행하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 11. 측정 시 주의사항

- `df`와 `du`는 서로 다른 관점의 공간 사용량을 표시합니다.
- `du`는 권한이 없거나 다른 파일시스템이 마운트된 경로를 의도와 다르게 계산할 수 있습니다.
- `ioping`, `fio`, `hdparm`의 결과는 측정 경로와 옵션에 따라 달라집니다.
- `ioping`의 캐시·Direct I/O 설정을 통일하지 않으면 결과를 직접 비교하지 않습니다.
- `iostat`의 짧은 순간값보다 동일 조건의 추세를 함께 확인합니다.
- `%util`이 높다고 항상 처리량이 높은 것은 아닙니다. 작은 랜덤 I/O도 디바이스를 바쁘게 만들 수 있습니다.
- `fio`의 쓰기 테스트는 테스트 파일이나 테스트 디바이스를 명확히 지정합니다.
- `hdparm`의 설정 변경 옵션은 조회·측정 옵션과 구분합니다.
- `smartctl`과 `nvme-cli`는 장치 연결 방식과 권한에 따라 일부 정보를 제공하지 못할 수 있습니다.
- 도구별 출력 단위와 측정 구간을 기록해야 결과를 비교할 수 있습니다.

🟡 운영 환경에서는 읽기 중심의 관찰 명령부터 실행합니다. 쓰기 성능 테스트, 장치 설정 변경, 전원 관리 변경은 데이터 손실이나 서비스 영향이 발생할 수 있으므로 별도의 테스트 장치와 롤백 계획이 필요합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 12. 요약

```text
구조·마운트       → lsblk, findmnt, blkid
공간 사용량       → df, du, ncdu
프로세스 I/O      → iotop, pidstat -d
디바이스 I/O      → iostat
종합 모니터링     → dstat, atop, nmon
지연시간          → ioping
성능 테스트       → fio, hdparm
장치 상태         → smartctl, nvme-cli
```

문제 분석은 다음 순서로 진행합니다.

```text
구조 확인 → 공간 확인 → 프로세스 확인 → 디바이스 확인
    → 지연시간 확인 → 장치 상태 확인 → 통제된 성능 테스트
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Linux man-pages: [man7.org/linux/man-pages](https://man7.org/linux/man-pages/) — ★★★☆☆
- sysstat Documentation: [github.com/sysstat/sysstat](https://github.com/sysstat/sysstat) — ★★★☆☆
- fio Documentation: [github.com/axboe/fio](https://github.com/axboe/fio) — ★★★☆☆
- smartmontools: [smartmontools.org](https://www.smartmontools.org/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-18

**마지막 업데이트**: 2026-08-18

© 2026 siasia86. Licensed under CC BY 4.0.

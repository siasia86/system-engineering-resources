---
name: iperf3-official-notes
last_checked: 2026-08-28
sources:
  - https://github.com/esnet/iperf
  - https://software.es.net/iperf/invoking.html
---

# iperf3 공식 참조 노트

iperf3의 명령 구조와 옵션은 ESnet 공식 문서와 공식 GitHub 저장소를 기준으로 기록합니다. 배포판 패키지 버전과 Windows binary의 제공 방식은 운영 환경별로 다를 수 있으므로 실제 설치본의 `iperf3 --version`을 별도로 확인합니다.

## 목차

| 섹션                                                                              |
|-----------------------------------------------------------------------------------|
| [1. 공식 정보](#1-공식-정보) / [2. 실행 구조](#2-실행-구조)                       |
| [3. 주요 옵션](#3-주요-옵션) / [4. 결과와 운영 주의사항](#4-결과와-운영-주의사항) |

## 1. 공식 정보

| 항목             | 값                       | 출처                |
|------------------|--------------------------|---------------------|
| 프로젝트         | iperf3                   | ESnet 공식 GitHub   |
| 최신 release     | 3.21                     | GitHub Releases API |
| 주요 용도        | 네트워크 throughput 측정 | 공식 invoking 문서  |
| 지원 측정 방식   | TCP, UDP, SCTP           | 공식 manual         |
| 기본 server port | TCP 5201                 | 공식 manual         |

> throughput: 단위 시간에 전송된 데이터의 처리량입니다. 링크 속도와 실제 애플리케이션 처리량은 protocol, host, buffer, congestion 등의 조건에 따라 달라질 수 있습니다.

## 2. 실행 구조

iperf3 하나의 executable은 server와 client 기능을 모두 포함합니다.

```text
iperf3 server                         iperf3 client
iperf3 -s                             iperf3 -c <server>
        ^----------- control -----------^
        <----------- test data ---------->
```

- `iperf3 -s`: server mode로 실행합니다.
- `iperf3 -c <server>`: client mode로 server에 연결합니다.
- 초기 TCP control connection으로 테스트 parameter와 시작·종료·결과를 교환합니다.
- 측정 data는 TCP connection, UDP datagram flow, 또는 SCTP connection으로 전달됩니다.
- 기본 방향은 client에서 server로 전송합니다.
- `-R`을 사용하면 server에서 client 방향으로 전송합니다.

## 3. 주요 옵션

| 옵션                     | 동작                                         |
|--------------------------|----------------------------------------------|
| `-s`, `--server`         | server mode                                  |
| `-c`, `--client <host>`  | 지정 host에 client mode로 연결               |
| `-p`, `--port <n>`       | server port 지정, 기본값 5201                |
| `-t`, `--time <n>`       | 테스트 시간(초) 지정                         |
| `-i`, `--interval <n>`   | throughput report 간격(초) 지정              |
| `-u`, `--udp`            | UDP mode                                     |
| `-b`, `--bitrate <rate>` | target bitrate 지정                          |
| `-R`, `--reverse`        | server에서 client 방향으로 전송              |
| `-P`, `--parallel <n>`   | parallel stream 개수 지정                    |
| `-J`, `--json`           | 테스트 결과를 JSON으로 출력                  |
| `--one-off`              | server가 하나의 client 연결을 처리한 뒤 종료 |

옵션의 최종 동작과 지원 여부는 실행 중인 binary의 help와 설치된 manual page를 기준으로 확인합니다.

```bash
iperf3 --help
iperf3 --version
```

## 4. 결과와 운영 주의사항

- 테스트 결과는 client와 server 양쪽 관점으로 표시될 수 있습니다.
- TCP 결과에는 sender·receiver throughput과 관찰된 retransmission 정보가 포함될 수 있습니다.
- UDP 결과에는 bitrate, jitter, datagram loss 관련 통계가 포함됩니다.
- `-J` JSON 출력은 자동 분석에 사용할 수 있습니다.
- 공식 manual은 source tree와 설치된 executable의 manual page를 authoritative reference로 설명합니다.
- 실제 운영망 테스트에서는 측정 대상, duration, bitrate, source IP, 방화벽 허용 범위를 사전에 제한합니다. 이 항목은 32 저장소 운영 정책입니다.

## 참고 자료

- ESnet iperf3: [github.com/esnet/iperf](https://github.com/esnet/iperf) — ★★★☆☆
- ESnet Invoking iperf3: [software.es.net/iperf/invoking.html](https://software.es.net/iperf/invoking.html) — ★★★☆☆

---

**작성일**: 2026-08-28

**마지막 업데이트**: 2026-08-28

© 2026 siasia86. Licensed under CC BY 4.0.

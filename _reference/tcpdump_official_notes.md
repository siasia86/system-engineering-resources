---
name: tcpdump-official-notes
last_checked: 2026-08-01
sources:
  - https://www.tcpdump.org/manpages/tcpdump.1.html
  - https://www.tcpdump.org/
---

# tcpdump 공식 참조 노트

## 1. tcpdump 개요

### 공식 소스

| 소스        | URL                                             | 용도                |
|-------------|-------------------------------------------------|---------------------|
| tcpdump.1   | https://www.tcpdump.org/manpages/tcpdump.1.html | 옵션, BPF 필터 문법 |
| tcpdump.org | https://www.tcpdump.org/                        | 최신 버전 확인      |

### 검증된 사실 (2026-08-01)

| 항목             | 값                                     | 출처        |
|------------------|----------------------------------------|-------------|
| 최신 stable 버전 | 4.99.6                                 | tcpdump.org |
| BPF 필터         | Berkeley Packet Filter 문법 사용       | tcpdump.1   |
| 기본 동작        | 지정 인터페이스의 패킷을 캡처하여 출력 | tcpdump.1   |
| root 권한        | 일반적으로 root 또는 CAP_NET_RAW 필요  | tcpdump.1   |

## 2. 주요 옵션 (tcpdump.1 man page 기반)

### 공식 소스

| 소스      | URL                                             | 용도      |
|-----------|-------------------------------------------------|-----------|
| tcpdump.1 | https://www.tcpdump.org/manpages/tcpdump.1.html | 옵션 목록 |

### 검증된 사실 (2026-08-01)

| 옵션                  | 동작                                             | 출처      |
|-----------------------|--------------------------------------------------|-----------|
| `-i <interface>`      | 캡처할 인터페이스 지정 (`any`로 전체 인터페이스) | tcpdump.1 |
| `-n`                  | IP를 호스트명으로 변환하지 않음                  | tcpdump.1 |
| `-nn`                 | IP와 포트 모두 숫자로 출력                       | tcpdump.1 |
| `-v` / `-vv` / `-vvv` | 출력 상세도 단계별 증가                          | tcpdump.1 |
| `-x`                  | 패킷 내용을 16진수로 출력                        | tcpdump.1 |
| `-X`                  | 패킷 내용을 16진수 + ASCII로 출력                | tcpdump.1 |
| `-A`                  | 패킷 내용을 ASCII로 출력                         | tcpdump.1 |
| `-w <file>`           | 캡처 결과를 파일로 저장 (pcap 형식)              | tcpdump.1 |
| `-r <file>`           | pcap 파일에서 읽기                               | tcpdump.1 |
| `-c <count>`          | 지정 패킷 수 캡처 후 종료                        | tcpdump.1 |
| `-s <snaplen>`        | 각 패킷에서 캡처할 바이트 수 (기본 262144)       | tcpdump.1 |
| `-C <size>`           | 파일 크기(MB) 초과 시 새 파일 생성               | tcpdump.1 |
| `-G <seconds>`        | 지정 초마다 파일 회전 (rotate)                   | tcpdump.1 |
| `-W <count>`          | `-C`와 함께 사용, 최대 파일 개수 지정            | tcpdump.1 |
| `-e`                  | 링크 레이어 헤더 출력 (MAC 주소 등)              | tcpdump.1 |
| `-S`                  | TCP 시퀀스 번호를 절대값으로 출력                | tcpdump.1 |
| `-Q <direction>`      | 캡처 방향 지정 (`in`/`out`/`inout`)              | tcpdump.1 |
| `-j <tstamp_type>`    | 타임스탬프 타입 지정                             | tcpdump.1 |

## 3. BPF 필터 문법 (tcpdump.1 man page 기반)

### 검증된 사실 (2026-08-01)

| 표현식               | 의미                           | 출처      |
|----------------------|--------------------------------|-----------|
| `host <addr>`        | 출발지 또는 목적지가 지정 주소 | tcpdump.1 |
| `src host <addr>`    | 출발지가 지정 주소             | tcpdump.1 |
| `dst host <addr>`    | 목적지가 지정 주소             | tcpdump.1 |
| `port <num>`         | 출발지 또는 목적지 포트        | tcpdump.1 |
| `tcp port <num>`     | TCP 포트 지정                  | tcpdump.1 |
| `udp port <num>`     | UDP 포트 지정                  | tcpdump.1 |
| `net <network>`      | 지정 네트워크 대역             | tcpdump.1 |
| `proto <protocol>`   | 프로토콜 번호 지정             | tcpdump.1 |
| `and` / `or` / `not` | 논리 연산자 (괄호로 그룹 가능) | tcpdump.1 |
| `icmp`               | ICMP 패킷만 캡처               | tcpdump.1 |

## 4. deprecated / 주의사항

| 항목              | 상태                                                      | 출처      |
|-------------------|-----------------------------------------------------------|-----------|
| `-s 0`            | 이전 버전에서 전체 패킷 캡처 의미, 현재는 기본값이 262144 | tcpdump.1 |
| `-p` (no-promisc) | 프로미스큐어스 모드 비활성화 (기본은 활성화)              | tcpdump.1 |

---

**작성일**: 2026-08-01

**마지막 업데이트**: 2026-08-01

© 2026 siasia86. Licensed under CC BY 4.0.

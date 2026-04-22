# TCP 상태 전이 (TCP State Transition)

## TCP 3-Way Handshake (연결 설정)

```
클라이언트                                        서버
[CLOSED]                                          [LISTEN]
    │                                                 │
    ├── SYN ═══════════════════════════════════▶      │  1. 연결 요청
    │   (seq=100)                                     │
[SYN_SENT]                                            │
    │                                                 │
    │                                          [SYN_RECEIVED]
    │                                                 │
    │       ◀═══════════════════════ SYN + ACK ───────┤  2. 연결 수락 + 확인
    │   (seq=200, ack=101)                            │
    │                                                 │
    ├── ACK ═══════════════════════════════════▶      │  3. 최종 확인
    │   (ack=201)                                     │
    │                                                 │
[ESTABLISHED] ════════════════════════════════ [ESTABLISHED]
    │                                                 │
    └── 데이터 송수신 가능 ───────────────────────────┘
```

### 각 단계 설명

1. **SYN (Synchronize)**
   - 클라이언트가 서버에 연결 요청
   - 초기 Sequence Number 전송
   - 상태: CLOSED → SYN_SENT

2. **SYN + ACK (Synchronize + Acknowledge)**
   - 서버가 연결 수락
   - 서버의 Sequence Number 전송
   - 클라이언트 SYN 확인 (ACK)
   - 상태: LISTEN → SYN_RECEIVED

3. **ACK (Acknowledge)**
   - 클라이언트가 서버의 SYN 확인
   - 연결 성립
   - 상태: SYN_SENT → ESTABLISHED, SYN_RECEIVED → ESTABLISHED

---

## TCP 4-Way Handshake (연결 종료)

```
클라이언트                                        서버
[ESTABLISHED]                                [ESTABLISHED]
    │                                                 │
    ├── FIN ═══════════════════════════════════▶      │  1. 종료 요청
    │   (seq=300)                                     │
[FIN_WAIT_1]                                          │
    │                                                 │
    │                                          [CLOSE_WAIT]
    │                                                 │
    │       ◀══════════════════════════ ACK ──────────┤  2. 종료 요청 확인
    │   (ack=301)                                     │
    │                                                 │
[FIN_WAIT_2]                                          │
    │                                                 │
    │   (서버가 남은 데이터 전송 완료)                │
    │                                                 │
    │                                          [LAST_ACK]
    │                                                 │
    │       ◀══════════════════════════ FIN ──────────┤  3. 서버도 종료 요청
    │   (seq=400)                                     │
    │                                                 │
    ├── ACK ═══════════════════════════════════▶      │  4. 서버 종료 확인
    │   (ack=401)                                     │
    │                                                 │
[TIME_WAIT]                                      [CLOSED]
    │                                                 │
    │   (2 * MSL 대기, 보통 30초~2분)                 │
    │                                                 │
[CLOSED]                                              │
    │                                                 │
    └── 연결 완전 종료 ───────────────────────────────┘
```

### 각 단계 설명

1. **FIN (Finish)**
   - 클라이언트가 연결 종료 요청
   - 상태: ESTABLISHED → FIN_WAIT_1

2. **ACK (Acknowledge)**
   - 서버가 종료 요청 확인
   - 상태: ESTABLISHED → CLOSE_WAIT (서버)
   - 상태: FIN_WAIT_1 → FIN_WAIT_2 (클라이언트)

3. **FIN (Finish)**
   - 서버가 남은 데이터 전송 완료 후 종료 요청
   - 상태: CLOSE_WAIT → LAST_ACK

4. **ACK (Acknowledge)**
   - 클라이언트가 서버 종료 확인
   - 상태: FIN_WAIT_2 → TIME_WAIT (클라이언트)
   - 상태: LAST_ACK → CLOSED (서버)

---

## TCP 상태 전이도 (State Diagram)

### 연결 설정
```
CLOSED ---> SYN_SENT ---> ESTABLISHED
```

### 연결 종료 (능동 종료)
```
ESTABLISHED ---> FIN_WAIT_1 ---> FIN_WAIT_2 ---> TIME_WAIT ---> CLOSED
```

### 연결 종료 (수동 종료)
```
ESTABLISHED ---> CLOSE_WAIT ---> LAST_ACK ---> CLOSED
```

---

## 주요 TCP 상태 설명

| 구분                | 상태             | 설명                              | 위치         | 지속 시간         |
|---------------------|------------------|-----------------------------------|--------------|-------------------|
| -                   | **CLOSED**       | 연결 없음 (초기/최종 상태)        | 양쪽         | -                 |
| **3-Way Handshake** | **LISTEN**       | 서버가 연결 대기 중               | 서버         | 지속적            |
| *(연결 설정)*       | **SYN_SENT**     | SYN 전송 후 SYN+ACK 대기          | 클라이언트   | 수 ms ~ 수초      |
|                     | **SYN_RECEIVED** | SYN 받고 SYN+ACK 전송 후 ACK 대기 | 서버         | 수 ms             |
|                     | **ESTABLISHED**  | 연결 성립, 데이터 송수신 가능     | 양쪽         | 가변적            |
| **4-Way Handshake** | **FIN_WAIT_1**   | FIN 전송 후 ACK 대기              | 능동 종료 측 | 수 ms             |
| *(연결 종료)*       | **FIN_WAIT_2**   | ACK 받고 상대방 FIN 대기          | 능동 종료 측 | 수 ms ~ 수초      |
|                     | **CLOSE_WAIT**   | 상대방 FIN 받고 종료 준비 중      | 수동 종료 측 | 애플리케이션 의존 |
|                     | **LAST_ACK**     | FIN 전송 후 마지막 ACK 대기       | 수동 종료 측 | 수 ms             |
|                     | **TIME_WAIT**    | 연결 종료 후 2*MSL 대기           | 능동 종료 측 | 30초 ~ 2분        |
|                     | **CLOSING**      | 양쪽 동시 FIN 전송, ACK 대기      | 양쪽         | 수 ms             |

---

## TIME_WAIT 상태

### 목적
1. **지연 패킷 처리**: 네트워크에 남아있는 패킷이 소멸할 때까지 대기
2. **마지막 ACK 재전송**: 서버가 ACK를 못 받으면 FIN을 재전송할 수 있음

### 대기 시간
- **2 * MSL** (Maximum Segment Lifetime)
- 일반적으로 **30초 ~ 2분**
- Linux 기본값: 60초

### 문제점
- 같은 포트 재사용 불가
- 대량 연결 시 포트 고갈 (ephemeral port exhaustion)

### 해결 방법

**서버 측 (SO_REUSEADDR):**
```c
int opt = 1;
setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
```

**Linux 커널 튜닝:**
```bash
# TIME_WAIT 시간 단축
sysctl -w net.ipv4.tcp_fin_timeout=30

# TIME_WAIT 소켓 재사용 허용
sysctl -w net.ipv4.tcp_tw_reuse=1

# TIME_WAIT 소켓 빠른 재활용
sysctl -w net.ipv4.tcp_tw_recycle=1  # 주의: 최신 커널에서 제거됨
```

---

## 비정상 종료 (RST)

```
클라이언트                                        서버
[ESTABLISHED]                                [ESTABLISHED]
    │                                                 │
    ├── RST ═══════════════════════════════════▶      │  즉시 종료
    │                                                 │
[CLOSED]                                         [CLOSED]
    │                                                 │
    └── 즉시 종료 (TIME_WAIT 없음) ───────────────────┘
```

### RST 발생 경우
- 존재하지 않는 포트로 접속 시도
- 연결 타임아웃
- 애플리케이션 강제 종료 (kill -9)
- 방화벽에서 차단
- SO_LINGER 옵션 사용

### 특징
- 4-Way Handshake 없이 즉시 종료
- TIME_WAIT 상태 없음
- 버퍼의 데이터 손실 가능

---

## CLOSE_WAIT 문제

### 증상
```bash
# CLOSE_WAIT 상태가 계속 증가
netstat -an | grep CLOSE_WAIT | wc -l
```

### 원인
- 애플리케이션이 `close()` 호출 안 함
- 상대방이 FIN을 보냈지만 서버가 소켓을 닫지 않음

### 해결
```python
# Python 예시
try:
    # 소켓 사용
    data = sock.recv(1024)
finally:
    sock.close()  # 반드시 close() 호출
```

---

## TCP 상태 확인 명령어

### netstat 주요 옵션

| 옵션 | 설명                                               |
|------|----------------------------------------------------|
| `-a` | 모든 연결 및 대기 중인 소켓을 프로토콜과 함께 표시 |
| `-n` | 주소와 포트를 숫자로 표시 (DNS 역조회 안 함)       |
| `-t` | TCP 연결만 표시                                    |
| `-u` | UDP 연결만 표시                                    |
| `-l` | LISTEN 상태만 표시                                 |
| `-p` | 프로세스 ID/이름 표시                              |
| `-r` | 라우팅 테이블 확인                                 |

### Linux
```bash
# 모든 TCP 연결 상태 확인
netstat -ant

# 특정 상태만 확인
netstat -ant | grep TIME_WAIT
netstat -ant | grep ESTABLISHED

# ss 명령어 (더 빠름)
ss -tan state time-wait
ss -tan state established

# 상태별 개수
ss -tan | awk '{print $1}' | sort | uniq -c
```

### 출력 예시
```
LISTEN      0      128    0.0.0.0:22       0.0.0.0:*
ESTAB       0      0      10.0.1.5:22      10.0.1.100:54321
TIME-WAIT   0      0      10.0.1.5:80      10.0.1.200:12345
```

---

## DDoS 방어와 TCP 상태

### SYN Flood 공격
```
공격자 ---> SYN ---> 서버 (SYN_RECEIVED 상태 누적)
```

**방어:**
```bash
# SYN Cookie 활성화
sysctl -w net.ipv4.tcp_syncookies=1

# SYN_RECEIVED 큐 크기 증가
sysctl -w net.ipv4.tcp_max_syn_backlog=8192

# SYN+ACK 재전송 횟수 감소
sysctl -w net.ipv4.tcp_synack_retries=2
```

### TIME_WAIT 고갈 공격
```
공격자 ---> 대량 연결 ---> 서버 (TIME_WAIT 상태 누적)
```

**방어:**
```bash
# TIME_WAIT 재사용
sysctl -w net.ipv4.tcp_tw_reuse=1

# 로컬 포트 범위 확대
sysctl -w net.ipv4.ip_local_port_range="10000 65535"
```

---

## 참고 자료

- RFC 793: Transmission Control Protocol
- RFC 1122: Requirements for Internet Hosts
- Linux Kernel Documentation: tcp.txt
- Stevens, W. Richard. "TCP/IP Illustrated, Volume 1"

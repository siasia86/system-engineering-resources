# 컴퓨터 과학 - 네트워크 & 프로토콜

네트워크 프로토콜, TCP/IP, HTTP 등 컴퓨터 네트워크 이론을 정리한 문서입니다.

## 문서 목록

### TCP/IP
- **[TCP 상태 다이어그램](01_TCP_state.md)** - TCP 연결 상태 전이
- **[패킷 분석](02_packet_analysis.md)** - 네트워크 패킷 구조 분석
- **[네트워크 헤더](03_network_headers.md)** - Ethernet, IP, TCP, UDP 헤더 구조

### HTTP
- **[HTTP 메서드](04_http_methods.md)** - GET, POST, PUT, DELETE 등

---

## 학습 순서

1. **네트워크 기초** → [네트워크 헤더](03_network_headers.md)
2. **TCP 이해** → [TCP 상태](01_TCP_state.md)
3. **패킷 분석** → [패킷 분석](02_packet_analysis.md)
4. **HTTP 프로토콜** → [HTTP 메서드](04_http_methods.md)

---

## 핵심 개념

### OSI 7계층

```
7. Application  - HTTP, FTP, DNS
6. Presentation - SSL/TLS
5. Session      - NetBIOS
4. Transport    - TCP, UDP
3. Network      - IP, ICMP
2. Data Link    - Ethernet, Wi-Fi
1. Physical     - Cable, Radio
```

### TCP 3-Way Handshake

```
Client                Server
  |                      |
  |-------- SYN -------->|
  |<----- SYN+ACK -------|
  |-------- ACK -------->|
  |                      |
```

---

## 관련 문서

- [tcpdump 예제](../02_basic_linux_command/tcpdump_examples.md)
- [보안](../06_security/) - DDoS 방어

---

© 2026. Licensed under CC BY 4.0.

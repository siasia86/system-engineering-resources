# 컴퓨터 과학 - 네트워크 & 프로토콜

네트워크 프로토콜, TCP/IP, HTTP 등 컴퓨터 네트워크 이론을 정리한 문서입니다.

## 문서 목록

### TCP/IP
- **[IP 주소 체계 가이드](ip_addressing_guide.md)** - IPv4, 서브넷, CIDR 표기법
- **[TCP 상태 다이어그램](TCP_state.md)** - TCP 연결 상태 전이
- **[패킷 분석](packet_analysis.md)** - 네트워크 패킷 구조 분석
- **[tcpdump 예제](tcpdump_examples.md)** - 네트워크 패킷 캡처 실전 예제
- **[네트워크 헤더](network_headers.md)** - Ethernet, IP, TCP, UDP 헤더 구조

### HTTP
- **[HTTP 메서드](http_methods.md)** - GET, POST, PUT, DELETE 등

---

## 학습 순서

1. **IP 주소 체계** → [IP 주소 체계 가이드](ip_addressing_guide.md)
2. **네트워크 기초** → [네트워크 헤더](network_headers.md)
3. **TCP 이해** → [TCP 상태](TCP_state.md)
4. **패킷 분석** → [패킷 분석](packet_analysis.md)
5. **패킷 캡처 실습** → [tcpdump 예제](tcpdump_examples.md)
6. **HTTP 프로토콜** → [HTTP 메서드](http_methods.md)

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

[문서 전체 로드맵](../README.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-14

© 2026 siasia86. Licensed under CC BY 4.0.

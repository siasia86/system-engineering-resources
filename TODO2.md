# TODO2

신규 문서 작성 작업 목록입니다.

🟡 완료된 항목은 `CHANGELOG.md`로 이동합니다. TODO2에는 미완료 항목만 유지합니다.

---

## 작업 목록

| ID | 파일                                                       | 상태 | 설명                                                                                           |
|----|------------------------------------------------------------|------|------------------------------------------------------------------------------------------------|
| T1 | `01_fundamentals/networking/softether_vpn_server_guide.md` | ⬜   | SoftEther VPN Server 설치·설정 가이드 (Ubuntu/Rocky, vpncmd 서버 명령어, L2TP/OpenVPN 활성화)  |
| T2 | `01_fundamentals/networking/vpn_comparison_blog.md`        | ⬜   | VPN 프로토콜 선택 가이드 블로그 형식 (WireGuard/OpenVPN/IPsec/SoftEther 비교, 시나리오별 선택) |

---

## T1 — softether_vpn_server_guide.md 상세

### 포함 섹션

| 섹션 | 내용                                                             |
|------|------------------------------------------------------------------|
| §1   | 개요 — vpnserver 아키텍처 (Virtual Hub, SecureNAT, Virtual NIC)  |
| §2   | 설치 — Ubuntu                                                    |
| §3   | 설치 — Rocky Linux                                               |
| §4   | vpncmd 서버 초기 설정 (ServerPasswordSet, HubCreate, UserCreate) |
| §5   | L2TP/IPsec 활성화 (Windows/iOS/Android 기본 클라이언트 연결)     |
| §6   | OpenVPN 활성화 (.ovpn 파일 생성 및 배포)                         |
| §7   | 방화벽/iptables + NAT 설정                                       |
| §8   | systemd 서비스 등록                                              |
| §9   | 주요 vpncmd 서버 명령어 분류 표                                  |
| §10  | 트러블슈팅                                                       |

### 참고 자료

- linuxbabe.com: [Ubuntu 24.04 서버 설정](https://www.linuxbabe.com/ubuntu/set-up-softether-vpn-server-ubuntu-24-04)
- linuxbabe.com: [Ubuntu 22.04 서버 설정](https://www.linuxbabe.com/ubuntu/set-up-softether-vpn-server)
- 공식 How-to: [softether.org/4-docs/2-howto](https://www.softether.org/4-docs/2-howto)
- 공식 레퍼런스: [softether.org/4-docs/1-manual](https://www.softether.org/4-docs/1-manual)

---

## T2 — vpn_comparison_blog.md 상세

### 포함 섹션

| 섹션 | 내용                                                                  |
|------|-----------------------------------------------------------------------|
| §1   | 개요 — 이 글의 목적 및 대상 독자                                      |
| §2   | 프로토콜별 특성 요약 (PPTP/L2TP/IPsec/OpenVPN/WireGuard/SoftEther)    |
| §3   | 보안 수준 비교 (암호화 강도, PFS, 크랙 이력)                          |
| §4   | 성능 비교 (오버헤드, 핸드셰이크 RTT, 처리량)                          |
| §5   | 시나리오별 선택 기준 (재택근무 / 서버 간 터널 / 방화벽 우회 / 모바일) |
| §6   | 설정 난이도 비교 (클라이언트 설치 여부, 서버 설정 복잡도)             |
| §7   | 결론 — 선택 플로우차트                                                |

### 블로그 형식 특이사항

- 레퍼런스 문서가 아닌 **읽기 편한 서술형** 문체
- 다이어그램보다 **비교 표 + 시나리오 예시** 위주
- `vpn_protocol_concepts.md` 내용을 요약·참조 (중복 최소화)
- 내부 링크: `vpn_protocol_concepts.md`, `softether_vpn_client_guide.md`, `softether_vpn_server_guide.md`

---

**작성일**: 2026-08-05

---

**마지막 업데이트**: 2026-08-05

© 2026 siasia86. Licensed under CC BY 4.0.

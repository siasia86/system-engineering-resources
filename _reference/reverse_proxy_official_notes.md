---
name: reverse-proxy-official-notes
description: 리버스 프록시 관련 HTTP 표준(RFC 9110 프록시·Via, RFC 7239 Forwarded)과 X-Forwarded-* 헤더의 공식 출처 기준 사실 정리.
tags:
  - proxy
  - http
  - reverse-proxy
last_checked: 2026-11-23
sources:
  - https://www.rfc-editor.org/rfc/rfc9110
  - https://www.rfc-editor.org/rfc/rfc7239
---

# 리버스 프록시 공식 참조 노트

| 항목                 | 값                                                                                                           | 출처                 |
|----------------------|--------------------------------------------------------------------------------------------------------------|----------------------|
| 용어                 | RFC 9110은 클라이언트 쪽 중계를 proxy, 서버 쪽에서 원 서버처럼 동작하는 중계를 gateway(reverse proxy)로 구분 | RFC 9110             |
| `Via` 헤더           | 요청·응답이 거친 중계 장치를 기록                                                                            | RFC 9110             |
| `Forwarded` 헤더     | 원래 클라이언트 주소(`for`), 프록시(`by`), 원래 Host(`host`), 원래 프로토콜(`proto`)을 표준 형식으로 전달    | RFC 7239             |
| `X-Forwarded-For` 등 | 표준 이전부터 쓰인 비표준 헤더. 지금도 널리 쓰이며 `Forwarded`와 같은 정보를 담음                            | RFC 7239 (배경 설명) |
| 신뢰 경계            | 헤더는 클라이언트가 위조할 수 있으므로, 믿을 수 있는 프록시가 덧붙인 값만 써야 함                            | RFC 7239 (보안 고려) |

검증: 1차 RFC 9110·7239 본문, 2차 같은 RFC의 보안 고려 절과 예시 절로 다시 대조했습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.

---
name: squid-official-notes
description: Squid 전달 프록시의 판, 기본 접근 제어(http_access·acl), 검증 명령의 공식 출처 기준 사실 정리.
tags:
  - proxy
  - squid
last_checked: 2026-11-23
sources:
  - https://github.com/squid-cache/squid/releases
  - https://www.squid-cache.org/Doc/config/http_access/
  - https://www.squid-cache.org/Doc/config/acl/
---

# Squid 공식 참조 노트

| 항목           | 값                                                                                    | 출처                |
|----------------|---------------------------------------------------------------------------------------|---------------------|
| 최신 판        | 7.8 (2026-10-30, GitHub release `SQUID_7_8`)                                          | releases            |
| 배포판 판 예   | `ubuntu/squid` 이미지 6.13                                                            | 컨테이너 `squid -v` |
| 기본 포트      | `http_port 3128`                                                                      | 기본 설정, 컨테이너 |
| 접근 제어      | `acl`로 대상을 정의하고 `http_access allow/deny`를 위에서부터 처음 맞는 규칙으로 적용 | http_access 문서    |
| 기본 보호 규칙 | `deny !Safe_ports`, `deny CONNECT !SSL_ports`, 마지막 `deny all`                      | 기본 설정           |
| 설정 검사      | `squid -k parse`, 반영은 `squid -k reconfigure`                                       | 컨테이너 실행       |

검증: 1차 GitHub release와 squid-cache.org 설정 문서, 2차 `ubuntu/squid` 컨테이너에서 전달 요청(응답 200)과 `squid -k parse`를 실행해 대조했습니다.

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.

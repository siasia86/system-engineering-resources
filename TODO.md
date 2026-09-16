# TODO

레포 잔여 이슈 및 향후 작업 목록입니다.

🟡 완료된 항목은 `CHANGELOG.md`로 이동합니다. TODO에는 미완료 항목만 유지합니다.

## 목차

| 섹션                         |
|------------------------------|
| [1. 잔여 이슈](#1-잔여-이슈) |

---

## 1. 잔여 이슈

2026-09-15 테스트 문서 작업 완료 내역은 `CHANGELOG.md`의 `[5.0.2]`에 기록했습니다.

- [ ] 웹 서버 중심 테스트 기법 문서화
  - 대상 위치: `01_fundamentals/cs/web_testing/`
  - 범위: HTTP 프로토콜, Reverse Proxy, TLS/HTTPS, 성능·부하, Timeout·연결 고갈, Graceful Reload, Load Balancer, Cache/CDN, 요청 보안, 관측성
  - 우선 문서: 개요, HTTP 프로토콜 테스트, Reverse Proxy 테스트, TLS/HTTPS 테스트, 웹 성능·Timeout 테스트
  - 완료 조건: 일반 테스트 기법 및 게임 테스트와 중복을 피하고, 웹 서버 역할별 테스트 케이스·검증 도구·실패 판정 기준을 정리
  - 검증: `sia-md-style-check`, `sia-md-heading-check`, `sia-md-link-check`를 대상 문서와 README에 실행
  - 롤백: 문서 변경 전 커밋으로 되돌리거나 해당 문서 변경을 `git revert`로 복원

### 검사 예외 파일

| 파일                                               | 사유                                   |
|----------------------------------------------------|----------------------------------------|
| `01_fundamentals/linux/vim_airline.md`             | 외부 프로젝트(vim-airline) README 원본 |
| `06_career/ai_tools/kiro_cli_command_reference.md` | Kiro CLI 문서 (다이어그램 한글 의도적) |

[⬆ 목차로 돌아가기](#목차)

---

**작성일**: 2026-06-21

**마지막 업데이트**: 2026-09-16

© 2026 siasia86. Licensed under CC BY 4.0.

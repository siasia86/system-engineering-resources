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

현재 진행 중인 작업은 없습니다. 열린 이슈와 대기 결정은 [ISSUE](.governance/ISSUE.md)의 ISS-01~03에서 관리합니다. 웹 서버 테스트 문서화는 2026-10-27 `MAIN-20261027-01`·`MAIN-20261027-02`로 완료했으며 `CHANGELOG.md`의 `[Unreleased]`에 기록했습니다.

### 검사 예외 파일

설정 파일의 파일별 예외입니다. 사유와 재검토일의 원본은 [검증 기준](.governance/verification.md)이며, 재검토 대기는 [ISSUE](.governance/ISSUE.md)의 ISS-02로 관리합니다.

| 파일                                                          | 검사 항목                         | 사유                                     |
|---------------------------------------------------------------|-----------------------------------|------------------------------------------|
| `01_fundamentals/linux/vim_airline.md`                        | `emoji-disallow`, heading `level` | 외부 프로젝트(vim-airline) README 원본   |
| `01_fundamentals/networking/network_headers.md`               | `box-chars`                       | RFC header diagram의 필드 경계 조합 보존 |
| `02_infrastructure/monitoring/game_infra_kpi_presentation.md` | `diagram-kr`                      | 발표 자료의 다이어그램 내부 한글 보존    |
| `04_security/cloud/ddos_defense_architecture.md`              | `diagram-width`                   | 인접 박스 연결선에 대한 검사기 오탐      |
| `06_career/ai_tools/kiro/kiro_cli_command_reference.md`       | `diagram-kr`                      | Kiro CLI 문서 다이어그램 내부 한글 보존  |

[⬆ 목차로 돌아가기](#목차)

---

**작성일**: 2026-06-21

**마지막 업데이트**: 2026-10-27

© 2026 siasia86. Licensed under CC BY 4.0.

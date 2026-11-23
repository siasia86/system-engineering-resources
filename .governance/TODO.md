# TODO

레포 잔여 이슈 및 향후 작업 목록입니다.

🟡 완료된 항목은 `CHANGELOG.md`로 이동합니다. TODO에는 미완료 항목만 유지합니다.

## 목차

| 섹션                         |
|------------------------------|
| [1. 잔여 이슈](#1-잔여-이슈) |

---

## 1. 잔여 이슈

현재 진행 중인 작업은 없습니다. 열린 이슈는 [ISSUE](ISSUE.md)의 ISS-02·03에서 관리하고, 끝난 작업의 기록은 `CHANGELOG.md`에 있습니다.

### 대기와 결정

| 구분      | 작업                           | 요청·근거                                     | 재개 조건·다음 행동                                                                                                                                                                        |
|-----------|--------------------------------|-----------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 대기      | DO-03 문서 실기 확인           | 05 DO-03 배정, 요청 00 세션(직접 요청 경로)   | kind·Hyper-V는 실행 시험 없이 공식 문서와 대조, Docker macvlan은 미시험, systemd 포함 컨테이너의 Compose 기동·Ansible 접속은 미확인. 00 세션 실기 결과가 오면 다른 점을 고침               |
| 결정 대기 | Docker 문서 2개 파일 이름 변경 | 2026-11-23 DO-03 정리 뒤 이름과 내용이 어긋남 | `docker_install_and_compose.md` → `docker_install.md`, `docker_compose_cheatsheet.md` → `docker_cheatsheet.md` 후보. 파일 이동이라 사용자 결정 뒤 [옮김 기록](MOVED.md)과 관찰 유예를 따름 |

### 검사 예외 파일

설정 파일의 파일별 예외입니다. 사유와 재검토일의 원본은 [검증 기준](verification.md)이며, 재검토 대기는 [ISSUE](ISSUE.md)의 ISS-02로 관리합니다.

| 파일                                                          | 검사 항목                         | 사유                                    |
|---------------------------------------------------------------|-----------------------------------|-----------------------------------------|
| `01_fundamentals/linux/vim_airline.md`                        | `emoji-disallow`, heading `level` | 외부 프로젝트(vim-airline) README 원본  |
| `02_infrastructure/monitoring/game_infra_kpi_presentation.md` | `diagram-kr`                      | 발표 자료의 다이어그램 내부 한글 보존   |
| `04_security/cloud/ddos_defense_architecture.md`              | `diagram-width`                   | 오른쪽 연결선이 끝난 아래 행의 폭 차이  |
| `06_career/ai_tools/kiro/kiro_cli_command_reference.md`       | `diagram-kr`                      | Kiro CLI 문서 다이어그램 내부 한글 보존 |

[⬆ 목차로 돌아가기](#목차)

---

**작성일**: 2026-06-21

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.

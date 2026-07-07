# TODO

레포 잔여 이슈 및 향후 작업 목록입니다.

🟡 완료된 항목은 `CHANGELOG.md`로 이동합니다. TODO에는 미완료 항목만 유지합니다.

## 목차

| 섹션                                                        |
|-------------------------------------------------------------|
| [1. 잔여 이슈](#1-잔여-이슈) / [2. 향후 작업](#2-향후-작업) |

---

## 1. 잔여 이슈

| 파일                                                            | 이슈 유형       | 설명                               |
|-----------------------------------------------------------------|-----------------|------------------------------------|
| `06_career/ai_tools/kiro_cli_command_reference.md`              | _reference 규칙 | frontmatter 없음 (FILE_SKIP 예외)  |
| `02_infrastructure/cicd/infra_monorepo_and_boilerplate.md`      | 코드블록 중첩   | fence 홀수 (🟡 md-link-check 경고) |
| `02_infrastructure/cloud_aws/vpc_peering_inter_region_guide.md` | 코드블록 중첩   | fence 홀수 (🟡 md-link-check 경고) |

### 검사 예외 파일

| 파일                                               | 사유                                   |
|----------------------------------------------------|----------------------------------------|
| `01_fundamentals/linux/vim_airline.md`             | 외부 프로젝트(vim-airline) README 원본 |
| `06_career/ai_tools/kiro_cli_command_reference.md` | Kiro CLI 문서 (다이어그램 한글 의도적) |

---

## 2. 향후 작업

| 순위 | 작업                                     | 비고                        |
|------|------------------------------------------|-----------------------------|
| 1    | README.md 누락 파일 22개 링크 추가       | 개별 나열 필요한 파일       |
| 2    | GitHub push + Actions workflow 확인      | push 후 green 확인          |
| 3    | `__pycache__/` 삭제                      | 자동 재생성, 미관 정리      |
| 4    | 중첩 코드블록 2건 수정 (4-backtick 전환) | infra_monorepo, vpc_peering |

---

**작성일**: 2026-06-21

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.

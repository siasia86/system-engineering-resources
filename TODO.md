# TODO

레포 잔여 이슈 및 향후 작업 목록입니다.

🟡 완료된 항목은 `CHANGELOG.md`로 이동합니다. TODO에는 미완료 항목만 유지합니다.

## 목차

| 섹션                         |
|------------------------------|
| [1. 잔여 이슈](#1-잔여-이슈) |

---

## 1. 잔여 이슈

| 파일                                                                               | 이슈 유형  | 설명                                                                                                                  |
|------------------------------------------------------------------------------------|------------|-----------------------------------------------------------------------------------------------------------------------|
| `06_career/ai_tools/kiro_cli_command_reference.md`                                 | _reference | frontmatter 없음 (FILE_SKIP 예외)                                                                                     |
| `[private] hyperv_version_centos5_compatibility.md` (34_system~ 비공개 레포)       | fact-check | ESU 종료일 오류: `2024 (Y4)` → `2023-01-10` (on-premises Y3 기준, 2026-07-27 확인)                                    |
| `[private] hyperv_myisam_io_timeout_incident_20260715.md` (34_system~ 비공개 레포) | fact-check | Storage QoS 미설정: 2022는 기능 지원됨, "(기능 지원됨, 미적용)" 명시 필요                                             |
| `06_career/legal/privacy_law_guide.md`                                             | fact-check | 제34조 통지 기한: 현행법 "지체 없이" / 개정안(2026.9.11. 시행 예정) "72시간 이내" — 시행 후 현행법 기준으로 수정 필요 |
| `06_career/legal/privacy_law_guide.md`                                             | fact-check | 제34조 통지 항목 6호(손해배상 청구 등)·7호(대통령령 사항): 현행법에 없는 조문 — 개정 시행 후 반영 필요                |

### 검사 예외 파일

| 파일                                                       | 사유                                   |
|------------------------------------------------------------|----------------------------------------|
| `01_fundamentals/linux/vim_airline.md`                     | 외부 프로젝트(vim-airline) README 원본 |
| `06_career/ai_tools/kiro_cli_command_reference.md`         | Kiro CLI 문서 (다이어그램 한글 의도적) |
| `02_infrastructure/cicd/infra_monorepo_and_boilerplate.md` | 4-backtick 내부 표 (파서 한계)         |

---

**작성일**: 2026-06-21

**마지막 업데이트**: 2026-08-20

© 2026 siasia86. Licensed under CC BY 4.0.


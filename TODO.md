# TODO

md-style-check 잔여 이슈 및 개선 작업 목록입니다.

## 목차

| 섹션                                       |
|--------------------------------------------|
| [1. 다이어그램 한글→영문](#1-다이어그램-한글영문) |
| [2. 기타 잔여 이슈](#2-기타-잔여-이슈)     |

---

## 1. 다이어그램 한글→영문

STYLE.md 규칙: 코드블록 내 다이어그램은 영문 사용 권장 (GitHub 웹 폰트 호환).

| 파일                                                        | 잔여 한글 키워드 예시                       |
|-------------------------------------------------------------|---------------------------------------------|
| `04_system_engineer/01_roadmap/se_complete_roadmap_*.md`     | 우선순위, 수요                              |
| `04_system_engineer/01_roadmap/sre_roadmap.md`              | 요구사항, 가용성                            |
| `04_system_engineer/02_operations/asn_and_cloudflare_ddos.md` | 관리 대행자, 웹서비스, 게임                 |
| `04_system_engineer/02_operations/game_infra_kpi_presentation.md` | 장애 감지, 처리시간, 스케일링, 동접   |
| `04_system_engineer/02_operations/infra_monorepo_and_boilerplate.md` | 왜 이렇게 결정했는가              |
| `04_system_engineer/02_operations/s3_gateway_endpoint_*.md`  | 계정                                        |
| `04_system_engineer/02_operations/vpc_peering_*.md`          | 허용                                        |
| `04_system_engineer/03_tools/devops_toolchain.md`            | 빌드, 배포, 테스트                          |
| `04_system_engineer/04_ai/ai_development_request_template.md` | 로드 트리거                                |
| `04_system_engineer/04_ai/ai_markdown_design_patterns.md`    | 설정, 질문, 답변                            |
| `04_system_engineer/04_ai/kiro_cli_command_reference.md`     | 수집, 시간                                  |

🟡 주의: 번역 시 코드블록 내부만 수정, 본문 오염 금지. 단어 경계 검증 필수.

---

## 2. 기타 잔여 이슈

| 파일                                                    | 이슈 유형       | 설명             |
|---------------------------------------------------------|-----------------|------------------|
| `04_system_engineer/04_ai/kiro_cli_command_reference.md` | _reference 규칙 | frontmatter 없음 |

## 3. 검사 예외 파일

md-style-check 검사 대상에서 제외하는 파일입니다.

| 파일                           | 사유                                    |
|--------------------------------|-----------------------------------------|
| `02_basic_linux/vim_airline.md` | 외부 프로젝트(vim-airline) README 원본 |

---

**작성일**: 2026-06-21

**마지막 업데이트**: 2026-06-21

© 2026 siasia86. Licensed under CC BY 4.0.

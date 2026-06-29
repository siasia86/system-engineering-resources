# TODO

md-style-check 잔여 이슈 및 개선 작업 목록입니다.

## 목차

| 섹션                                                                           |
|--------------------------------------------------------------------------------|
| [1. 다이어그램 한글→영문](#1-다이어그램-한글영문) / [2. 기타 잔여 이슈](#2-기타-잔여-이슈) / [3. 검사 예외 파일](#3-검사-예외-파일) |

---

## 1. 다이어그램 한글→영문

STYLE.md 규칙: 코드블록 내 다이어그램은 영문 사용 권장 (GitHub 웹 폰트 호환).

| 파일                                                                 | 이슈 수 | 잔여 한글 키워드 예시                     |
|----------------------------------------------------------------------|----------|-------------------------------------------|
| `04_system_engineer/01_roadmap/sre_roadmap.md`                       | 5        | 요구사항, 가용성, 글로벌                  |
| `04_system_engineer/02_operations/asn_and_cloudflare_ddos.md`        | 17       | 총괄, 대행자, 웹서비스, 게임              |
| `04_system_engineer/02_operations/infra_monorepo_and_boilerplate.md` | 6        | 왜 이렇게 결정했는가, 보일러플레이트      |
| `04_system_engineer/02_operations/s3_gateway_endpoint_cross_account.md` | 2     | 계정, 허용                                |
| `04_system_engineer/02_operations/vpc_peering_inter_region_guide.md` | 1        | 버지니아, 서울                            |
| `04_system_engineer/03_tools/devops_toolchain.md`                    | 11       | 빌드, 배포, 테스트, 클러스터              |
| `04_system_engineer/04_ai/ai_development_request_template.md`        | 6        | 긴급, 수정, 승인                          |
| `04_system_engineer/04_ai/ai_markdown_design_patterns.md`            | 3        | 본문, 리소스, 로드 트리거                 |
| `04_system_engineer/04_ai/kiro_cli_command_reference.md`             | 8        | 책상, 시스템 프롬프트, 훅                 |
| **합계**                                                             | **59**   |                                           |

🟡 주의: 번역 시 코드블록 내부만 수정, 본문 오염 금지. 단어 경계 검증 필수.

---

## 2. 기타 잔여 이슈

| 파일                                                    | 이슈 유형       | 설명             |
|---------------------------------------------------------|-----------------|------------------|
| `04_system_engineer/04_ai/kiro_cli_command_reference.md` | _reference 규칙 | frontmatter 없음 |

## 3. 검사 예외 파일

md-style-check 검사 대상에서 제외하는 파일입니다.

| 파일                            | 사유                                    |
|---------------------------------|-----------------------------------------|
| `02_basic_linux/vim_airline.md` | 외부 프로젝트(vim-airline) README 원본 |

---

**작성일**: 2026-06-21

**마지막 업데이트**: 2026-06-29

© 2026 siasia86. Licensed under CC BY 4.0.

# TODO

md-style-check 잔여 이슈 및 신규 문서 작성 목록입니다.

🟡 완료된 항목은 `CHANGELOG.md`로 이동합니다. TODO에는 미완료 항목만 유지합니다.

## 목차

| 섹션                                                                                                                                |
|-------------------------------------------------------------------------------------------------------------------------------------|
| [1. 다이어그램 한글→영문](#1-다이어그램-한글영문) / [2. 기타 잔여 이슈](#2-기타-잔여-이슈) / [3. 검사 예외 파일](#3-검사-예외-파일) |
| [4. 신규 문서 — 시니어급 (20년차+)](#4-신규-문서--시니어급-20년차)                                                                  |

---

## 1. 다이어그램 한글→영문

STYLE.md 규칙: 코드블록 내 다이어그램은 영문 사용 권장 (GitHub 웹 폰트 호환).

완료 — 다이어그램 한글 이슈 모두 수정되었습니다.

완료된 파일:
- ✅ `asn_and_cloudflare_ddos.md`
- ✅ `infra_monorepo_and_boilerplate.md`
- ✅ `s3_gateway_endpoint_cross_account.md`
- ✅ `vpc_peering_inter_region_guide.md`
- ✅ `devops_toolchain.md`
- ✅ `sre_roadmap.md`
- ✅ `ai_development_request_template.md`
- ✅ `ai_markdown_design_patterns.md`
- ✅ `kiro_cli_command_reference.md` → FILE_SKIP diagram-kr 예외 처리

🟡 주의: 번역 시 코드블록 내부만 수정, 본문 오염 금지. 단어 경계 검증 필수.

---

## 2. 기타 잔여 이슈

| 파일                                                     | 이슈 유형       | 설명                              |
|----------------------------------------------------------|-----------------|-----------------------------------|
| `04_system_engineer/04_ai/kiro_cli_command_reference.md` | _reference 규칙 | frontmatter 없음 (FILE_SKIP 예외) |

## 3. 검사 예외 파일

md-style-check 검사 대상에서 제외하는 파일입니다.

| 파일                                                     | 사유                                   |
|----------------------------------------------------------|----------------------------------------|
| `02_basic_linux/vim_airline.md`                          | 외부 프로젝트(vim-airline) README 원본 |
| `04_system_engineer/04_ai/kiro_cli_command_reference.md` | Kiro CLI 문서 (다이어그램 한글 의도적) |

---

## 4. 신규 문서 — 시니어급 (20년차+)

현재 레포는 SE 2~3년차(중급)가 메인 타겟입니다. 아래 문서를 추가하여 시니어/아키텍트급 콘텐츠를 보강합니다.

### 우선순위

| 순위 | 파일명                       | 카테고리           | 내용                                                    | 상태 |
|------|------------------------------|--------------------|---------------------------------------------------------|------|
| 1    | `incident_management.md`     | 04_system_engineer | 장애 등급 분류, 에스컬레이션, 커뮤니케이션, 지휘 체계   | ⬜   |
| 2    | `slo_error_budget.md`        | 04_system_engineer | SLI 정의 → SLO 설정 → Error Budget 운영 → 의사결정 연동 | ⬜   |
| 3    | `capacity_planning.md`       | 04_system_engineer | 트래픽 예측 → 서버 산정 → 비용 계산 프레임워크          | ⬜   |
| 4    | `zero_downtime_migration.md` | 04_system_engineer | DB expand-contract, 트래픽 전환, 롤백 판단              | ⬜   |
| 5    | `change_management.md`       | 04_system_engineer | 변경 등급, CAB, 배포 윈도우, 긴급 변경 프로세스         | ⬜   |

### 후속 (우선순위 6~15)

| 순위 | 파일명                         | 카테고리           | 내용                                               |
|------|--------------------------------|--------------------|----------------------------------------------------|
| 6    | `postmortem_framework.md`      | 04_system_engineer | 타임라인, 5 Whys, Contributing Factors, 재발 방지  |
| 7    | `chaos_engineering.md`         | 04_system_engineer | 가설 → 실험 → 폭발 반경 제한 → 자동 롤백           |
| 8    | `multi_region_architecture.md` | 04_system_engineer | Active-Active/Standby, RPO/RTO 설계                |
| 9    | `platform_engineering.md`      | 04_system_engineer | IDP 설계, Golden Path, Self-service 인프라         |
| 10   | `oncall_design.md`             | 04_system_engineer | 로테이션, 보상, 번아웃 방지, 런북, 핸드오프        |
| 11   | `team_topology.md`             | 04_system_engineer | Stream-aligned/Platform/Enabling/Complicated 팀    |
| 12   | `tech_debt_management.md`      | 04_system_engineer | 기술 부채 분류, 측정, 상환 우선순위                |
| 13   | `cloud_cost_optimization.md`   | 12_tech_stack      | RI/SP 전략, Spot 활용, FinOps 프레임워크           |
| 14   | `vendor_evaluation.md`         | 04_system_engineer | 도구/서비스 선정 기준, PoC 설계, TCO, Lock-in 평가 |
| 15   | `legacy_modernization.md`      | 04_system_engineer | Strangler Fig, 단계별 분리, 데이터 이중 쓰기       |

---

**작성일**: 2026-06-21

**마지막 업데이트**: 2026-07-07

© 2026 siasia86. Licensed under CC BY 4.0.

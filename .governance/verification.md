# 32_system-engineering-resources 검증 기준

## 1. 선택과 선행 확인

변경 Markdown과 README의 style·heading·파일 링크·교차 fragment·출처 표현을 확인합니다. 원격 사실·공식 URL 검증과 로컬 문서 검사를 구분하며 민감 운영 자료를 문서로 복사하지 않습니다.

도구·버전·검사 대상·설정·timeout·출력 위치·부작용을 확인합니다. 미존재 도구·대상 0개·필수 검사 실패를 통과로 기록하지 않습니다.

## 2. 문서와 설정

담당 Markdown의 style·heading·파일 링크·교차 fragment를 실제 위치에서 검사합니다. root .md-style-check.toml·.md-heading-check.toml의 기존 예외를 먼저 대조하고 관리 문서를 포함한 실제 검사 수를 확인합니다. 기존 외부 원문·제품 문서에 새 style을 일괄 강제하지 않습니다.

설정의 TOML 해석, .gitignore의 private/생성 파일 제외와 관리 문서 포함을 확인합니다. 공통 설정과 local 구간을 구분하고 기존 규칙을 보존합니다. 문서 배치 검사는 도구·hook·skill 설치 증거가 아닙니다.

CL09의 TOOLS-30 `0.5.0` 고정은 [검사 workflow](../.github/workflows/update-date.yml)에 적용했습니다. [기본 설정](../.md-style-check.toml)에 기존 CI의 파일별 예외 5개를 동일하게 반영해 hook과 CI의 정책 차이를 해소했으며, 두 설정의 나머지 검사와 범위는 유지합니다. 예외의 기존 사유와 재검토 시점은 다음과 같습니다.

| 경로                                                          | 검사 항목        | 기존 사유                                         | 재검토     |
| --------------------------------------------------------------- | ------------------ | --------------------------------------------------- | ------------ |
| `01_fundamentals/linux/vim_airline.md`                        | `emoji-disallow` | 외부 프로젝트 README 원문 보존 — 목차 아이콘 포함 | 상시       |
| `01_fundamentals/networking/network_headers.md`               | `box-chars`      | RFC header diagram의 필드 경계 조합을 보존        | 2026-11-30 |
| `02_infrastructure/monitoring/game_infra_kpi_presentation.md` | `diagram-kr`     | 발표 자료의 다이어그램 내부 한글을 보존           | 상시       |
| `04_security/cloud/ddos_defense_architecture.md`              | `diagram-width`  | 인접 박스 연결선에 대한 검사기 오탐               | 2026-11-30 |
| `06_career/ai_tools/kiro/kiro_cli_command_reference.md`       | `diagram-kr`     | Kiro CLI 문서 다이어그램 내부 한글을 보존         | 상시       |

발표 자료의 두 링크 수정은 원격 e70fc98의 선행 반영을 재사용하며, 이번 담당 변경은 workflow, 기본 style 설정, 검증 기록 세 파일입니다. 실패하면 원문과 diff를 기준으로 복구합니다.

## 3. 보안과 변경

확인한 Gitleaks로 담당 파일·staged·게시 범위를 redaction과 함께 검사합니다. git diff --check 및 실제 staging 목록을 대조하고 운영 원문·계정·자격증명·다른 작업이 포함되지 않도록 확인합니다.

## 4. 판정과 복구

명령·대상·exit·관찰·통과/실패/부분/미실행·증거·다음 조건을 남깁니다. 필수 검사 실패 시 원인을 [ISSUE](ISSUE.md), 실행·복구 순서를 [PLAN](../PLAN.md)에 연결합니다. 담당 적용 전 원문과 diff로 선택 복구하고 실제 대상 적용·게임/runtime·새 세션 행동·원격 CI를 각각 관찰한 범위로만 판정합니다.

---

**작성일**: 2026-10-04

**마지막 업데이트**: 2026-10-04

© 2026 siasia86. Licensed under CC BY 4.0.

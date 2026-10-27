# 32_system-engineering-resources 검증 기준

## 1. 선택과 선행 확인

변경 Markdown과 README의 style·heading·파일 링크·교차 fragment·출처 표현을 확인합니다. 원격 사실·공식 URL 검증과 로컬 문서 검사를 구분하며 민감 운영 자료를 문서로 복사하지 않습니다.

도구·버전·검사 대상·설정·timeout·출력 위치·부작용을 확인합니다. 미존재 도구·대상 0개·필수 검사 실패를 통과로 기록하지 않습니다.

## 2. 문서와 설정

담당 Markdown의 style·heading·파일 링크·교차 fragment를 실제 위치에서 검사합니다. root .md-style-check.toml·.md-heading-check.toml의 기존 예외를 먼저 대조하고 관리 문서를 포함한 실제 검사 수를 확인합니다. 기존 외부 원문·제품 문서에 새 style을 일괄 강제하지 않습니다.

설정의 TOML 해석, .gitignore의 private/생성 파일 제외와 관리 문서 포함을 확인합니다. 공통 설정과 local 구간을 구분하고 기존 규칙을 보존합니다. 문서 배치 검사는 도구·hook·skill 설치 증거가 아닙니다.

검사 도구는 TOOLS-30 sia_scripts `0.5.0`이며 [검사 workflow](../.github/workflows/update-date.yml)가 release archive의 SHA256과 manifest를 확인한 뒤 실행합니다. [기본 설정](../.md-style-check.toml)과 CI 설정 `.md-style-check.sia_scripts.toml`은 같은 파일별 예외 5개를 갖습니다. 도입 기록은 `be2d024`입니다. 예외의 사유와 재검토 시점은 다음과 같으며 재검토 대기는 [ISSUE](ISSUE.md)의 ISS-02로 관리합니다.

| 경로                                                          | 검사 항목        | 기존 사유                                         | 재검토     |
|---------------------------------------------------------------|------------------|---------------------------------------------------|------------|
| `01_fundamentals/linux/vim_airline.md`                        | `emoji-disallow` | 외부 프로젝트 README 원문 보존 — 목차 아이콘 포함 | 상시       |
| `01_fundamentals/networking/network_headers.md`               | `box-chars`      | RFC header diagram의 필드 경계 조합을 보존        | 2026-11-30 |
| `02_infrastructure/monitoring/game_infra_kpi_presentation.md` | `diagram-kr`     | 발표 자료의 다이어그램 내부 한글을 보존           | 상시       |
| `04_security/cloud/ddos_defense_architecture.md`              | `diagram-width`  | 인접 박스 연결선에 대한 검사기 오탐               | 2026-11-30 |
| `06_career/ai_tools/kiro/kiro_cli_command_reference.md`       | `diagram-kr`     | Kiro CLI 문서 다이어그램 내부 한글을 보존         | 상시       |

### 현장 검사 명령

서버에 설치된 검사기는 CI 고정 버전과 다를 수 있으므로 30 저장소의 고정 태그로 CI를 재현합니다. 아래 경로는 작업 PC마다 다르며 임시 폴더에 풉니다.

1. `git -C <30 저장소> archive v0.5.0 src | tar -x -C <임시 폴더>`로 고정 버전을 추출합니다.
2. 저장소 루트에서 `sia-md-link-check .`, `sia-md-style-check --config .md-style-check.sia_scripts.toml .`, 같은 설정의 `--list-skips .`, `sia-readme-inventory-check README.md`, `sia-md-heading-check .`을 실행합니다. 기본 설정으로 `sia-md-style-check .`도 실행합니다.
3. 디렉토리 검사는 `README.md`를 건너뛰므로 새로 만들거나 고친 README는 파일 경로를 직접 지정해 문체를 검사합니다.
4. 표에 행을 추가하면 열 폭 변경으로 표 전체가 다시 정렬될 수 있으므로 `git diff --stat`으로 의도한 행만 바뀌었는지 확인합니다.
5. `git diff --check`와 gitleaks를 실행하고, push 후 Actions `Markdown validation` 결과를 확인합니다.

## 3. 보안과 변경

확인한 Gitleaks로 담당 파일·staged·게시 범위를 redaction과 함께 검사합니다. git diff --check 및 실제 staging 목록을 대조하고 운영 원문·계정·자격증명·다른 작업이 포함되지 않도록 확인합니다.

## 4. 판정과 복구

명령·대상·exit·관찰·통과/실패/부분/미실행·증거·다음 조건을 남깁니다. 필수 검사 실패 시 원인을 [ISSUE](ISSUE.md), 실행·복구 순서를 [PLAN](../PLAN.md)에 연결합니다. 담당 적용 전 원문과 diff로 선택 복구하고 실제 대상 적용·게임/runtime·새 세션 행동·원격 CI를 각각 관찰한 범위로만 판정합니다.

---

**작성일**: 2026-10-04

**마지막 업데이트**: 2026-10-27

© 2026 siasia86. Licensed under CC BY 4.0.

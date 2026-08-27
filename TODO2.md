# TODO2

문서 검사 도구와 저장소 규칙 체계 작업(2026-08-27)의 후속 작업을 정리한 임시 문서입니다.

## 목차

| 섹션                                                                  |
|-----------------------------------------------------------------------|
| [1. 문서 성격](#1-문서-성격) / [2. 완료 요약](#2-완료-요약)           |
| [3. 남은 작업](#3-남은-작업) / [4. 도구 개선 후보](#4-도구-개선-후보) |
| [5. 예정 재검토](#5-예정-재검토) / [6. 정리 대상](#6-정리-대상)       |

---

## 1. 문서 성격

🟡 이 문서는 임시 정리용입니다. `documentation_policy.md` 가 정의하는 문서 4종(`ISSUE.md`, `TODO.md`, `PLAN.md`, `CHANGELOG.md`)에 `TODO2.md` 는 포함되지 않습니다.

`profiles/chobo_ansible.md` 는 `TODO2.md` 를 "검증 보고서·우선순위·후속 작업 분석" 으로 정의하며, 일반 backlog 가 아닌 분석 보고서로 취급합니다. 이 문서도 같은 성격으로 작성했습니다.

정리 후 처리 방향입니다.

- 항목별로 `governance_todo.md` 또는 루트 `TODO.md` 로 이동
- 이동 완료 후 이 문서 제거
- 이 저장소에 `TODO2.md` 를 상설하려면 `documentation_policy.md` 에 역할을 먼저 정의

상세 항목은 [governance TODO](00_governance/01_repository_governance/governance_todo.md)에 이미 기록되어 있습니다. 이 문서는 그 중 미완료 항목을 작업 단위로 다시 묶은 것입니다.

## 2. 완료 요약

| 영역                         | 결과                                            |
|------------------------------|-------------------------------------------------|
| `.governance/` 우선순위 체계 | 정책 문서, 전역 skill, 템플릿 8종 도입          |
| 헤딩 구조 검사기             | `md-heading-check.py` 신규. CI 필수 검사로 승격 |
| 헤딩 구조 이슈               | 51건 → 0건                                      |
| 스타일 검사 범위             | 323개 → 366개 파일 (미러·메타 문서 포함)        |
| 검사 제외 항목               | 11건 → 9건, 사유 미확인 6건 → 0건               |
| 문서 사실 오류               | git 문서 3종 12건, 앵커 7건, 표 정렬 26건 수정  |

## 3. 남은 작업

### 3.1 저장소별 규칙 이관 (우선순위: 높음)

| 저장소              | 규칙 위치                                   | 상태              |
|---------------------|---------------------------------------------|-------------------|
| Zircon Windows 빌드 | 저장소 `.governance/GOVERNANCE.md`          | 완료 (2026-08-27) |
| Zircon 본체         | 저장소 내 `.kiro/skills/` 사본 + 전역 skill | 미착수            |
| Ansible 학습·자동화 | `profiles/chobo_ansible.md`                 | 미착수            |

절차는 `governance_precedence.md` §6을 따르고 문서는 `templates/governance_template.md` 로 작성합니다. 병행 기간을 두어 기존 위치를 먼저 제거하지 않습니다.

### Zircon Windows 빌드 (완료)

`.governance/GOVERNANCE.md` 를 생성하고 README에서 링크했습니다. 예외는 `readme-template` 의 푸터·배지·통계 1건이며, 유지하는 전역 규칙 8개를 명시했습니다.

전역 skill `zircon-readme-policy` 의 적용 범위는 Zircon 본체 저장소만 가리키고 있어 이 저장소는 원래 정책 적용 대상이 아니었습니다. 따라서 이관이 아니라 신규 적용에 해당하며, 전역 skill 을 제거할 단계가 아닙니다.

### Zircon 본체 (미착수)

저장소 안에 `.kiro/skills/zircon-readme-policy/SKILL.md` 사본이 이미 있고 전역 skill 과 내용이 중복됩니다. `.governance/` 로 통합할 때 두 사본을 함께 정리해야 합니다.

- [ ] `.governance/GOVERNANCE.md` 생성
- [ ] 저장소 내 `.kiro/skills/` 사본 제거
- [ ] 전역 skill `zircon-readme-policy` 제거 (두 저장소 모두 이관 완료 후)
- [ ] 에이전트 JSON `resources` 참조 제거
- [ ] `02_kiro/skills/zircon-readme-policy/` 미러 제거

### Ansible 학습·자동화 (미착수)

검증 기준이 6가지 변경 유형에 걸쳐 있어 `.governance/verification.md` 분리가 필요할 수 있습니다. `templates/verification_template.md` 를 사용합니다.

이관 완료 후 `profiles/` 디렉토리 존치 여부를 결정합니다.

### 3.2 정책 문서 보완 (우선순위: 보통)

- [ ] 절대경로 기록과 `documentation_policy.md` §3 충돌 해소
      - skill 미러에 로컬 절대경로가 기록되어 있으나 §3은 개인 경로 기록을 금지
      - 이관이 끝나면 다른 저장소 경로 나열이 사라지므로 이관과 함께 처리하는 편이 효율적
- [ ] `documentation_policy.md` 와 `governance_precedence.md` 관계 명시
      - 전자는 문서 역할·생명주기, 후자는 규칙 적용 순서를 다룸
      - 상호 참조를 추가하여 충돌 여부를 명확히 함
- [ ] `skip_checks` 활용 방안 정리
      - `.md-style-check.toml` 의 `skip_checks` 는 현재 빈 배열
      - `.governance/` 체계에서 저장소별 검사 예외를 어떻게 표현할지 정의 필요

### 3.3 낮은 우선순위

- [ ] `03_claude/` 활성화 시점의 정책 정의 (원본 경로·허용 목록 미정)
- [ ] 도구 중립 규칙과 도구 종속 규칙의 분리 기준 정리
- [ ] 템플릿 사용 실태 점검 (실제 복사되어 쓰이는지, 형식이 현실과 맞는지)

## 4. 도구 개선 후보

| 도구                  | 개선 항목                                         | 근거                                    |
|-----------------------|---------------------------------------------------|-----------------------------------------|
| `md-style-check.py`   | 다이어그램 폭 판정 — 인접 박스를 한 블록으로 묶음 | `ddos_defense_architecture.md` 오탐 4건 |
| `md-style-check.py`   | 박스 문자 판정 — RFC 헤더의 `├...┘` 조합 허용     | `network_headers.md` 오탐 2건           |
| `md-style-check.py`   | 표 셀 내 백틱 펜스를 코드블록으로 오인            | skill 작성 중 오탐 6건 확인             |
| `md-heading-check.py` | 목차 완결성 검사 (본문 H2 누락 검출)              | 현재 수동 확인만 가능                   |
| `--list-skips`        | CI 등록 여부 결정                                 | 사유 없는 제외 추가를 차단 가능         |

앞의 세 항목은 모두 `FILE_SKIP` 으로 우회 중인 오탐입니다. 도구를 고치면 제외를 해제할 수 있습니다.

목차 완결성 검사는 현재 어느 도구도 담당하지 않습니다. 본문에 H2를 추가하고 목차에 넣지 않으면 검출되지 않습니다. 반대 방향(목차가 없는 섹션을 가리키는 경우)은 `md-heading-check.py` 의 `anchor` 검사가 잡습니다.

## 5. 예정 재검토

| 시점         | 대상                                           | 확인 내용                           |
|--------------|------------------------------------------------|-------------------------------------|
| 2026-11-30   | `network_headers.md` (box-chars)               | 도구 개선 후 제외 해제 가능 여부    |
| 2026-11-30   | `ddos_defense_architecture.md` (diagram-width) | 도구 개선 후 제외 해제 가능 여부    |
| 조건 충족 시 | `00_governance/` 하위 저장소 분리              | `governance_todo.md` §5 재검토 조건 |

`md-style-check.py --list-skips` 로 현재 제외 항목과 재검토 시점을 확인할 수 있습니다.

## 6. 정리 대상

| 항목                                                    | 판단                                           |
|---------------------------------------------------------|------------------------------------------------|
| `governance_todo.md` §2 "H2 번호 연속성 검사 추가 검토" | `md-heading-check.py` 가 이미 담당 — 항목 종료 |
| `governance_todo.md` §1 "전역 skill 탐색 지시 등록"     | 구현 완료, 새 세션 인식 확인 후 종료           |
| `md-link-check` skill 이름                              | 3개 도구 규칙을 담고 있어 이름과 범위 불일치   |

`md-link-check` skill 은 이름이 도구 하나와 묶여 있는데 내용은 `md-link-check.py`, `md-heading-check.py`, `md-style-check.py` 세 도구의 규칙을 다룹니다. 이름을 바꾸려면 에이전트 JSON 7개의 `resources`, 미러, 참조 문서를 함께 고쳐야 합니다. 현재는 `description` 에 담당 범위를 명시하여 혼동을 줄인 상태입니다.

---

**작성일**: 2026-08-27

**마지막 업데이트**: 2026-08-27

© 2026 siasia86. Licensed under CC BY 4.0.

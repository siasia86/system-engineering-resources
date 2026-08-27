# Repository Governance TODO

`00_governance/01_repository_governance/` 자체의 개선 항목을 관리합니다. 저장소 전역
작업은 루트 `TODO.md`에서 관리하며, 이 문서는 governance 체계에 한정합니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 우선순위 체계 도입](#1-우선순위-체계-도입) / [2. 검사 설정 개선](#2-검사-설정-개선)                  |
| [3. 정책 문서 보완](#3-정책-문서-보완) / [4. 템플릿 확충](#4-템플릿-확충) / [5. 결정 기록](#5-결정-기록) |

---

## 우선순위 기준

| 우선순위 | 근거                                                     |
|----------|----------------------------------------------------------|
| 높음     | 이미 파편화가 발생한 항목. 방치하면 저장소 추가마다 악화 |
| 보통     | 현재 동작하지만 확장 시 문제가 되는 항목                 |
| 낮음     | 개선하면 좋으나 현재 문제를 일으키지 않는 항목           |

---

## 1. 우선순위 체계 도입

`governance_precedence.md` 도입에 따른 후속 작업입니다.

### 높음

- [ ] 전역 skill에 `.governance/` 탐색 지시 등록
      - 목적: 저장소가 늘어도 전역 skill을 추가하지 않고 모든 세션이 동일하게 인식
      - 확인: 새 세션에서 `.governance/`가 있는 저장소 작업 시 해당 파일을 읽는지

### 이관 대상 저장소 2곳 (우선순위: 높음)

| 대상 저장소                | 현재 규칙 위치                    | 형태      | 이관 후                     |
|----------------------------|-----------------------------------|-----------|-----------------------------|
| Zircon 저장소              | 전역 skill `zircon-readme-policy` | skill     | `.governance/GOVERNANCE.md` |
| Ansible 학습·자동화 저장소 | `profiles/chobo_ansible.md`       | 중앙 문서 | `.governance/GOVERNANCE.md` |

두 저장소 모두 규칙이 적용 대상 저장소 밖에 있습니다. 같은 성격의 요구가 한쪽은
전역 skill, 다른 한쪽은 중앙 문서로 이원화되어 조회 위치가 일정하지 않습니다.

공통 절차는 `governance_precedence.md` §6을 따르고, 문서는
`templates/governance_template.md`로 작성합니다. 병행 기간을 두어 기존 위치를 먼저
제거하지 않습니다.

#### 이관 1: Zircon 저장소

- [ ] 대상 저장소에 `.governance/GOVERNANCE.md` 생성 (템플릿 사용)
- [ ] 기존 skill 내용을 옮기고 유지하는 전역 규칙을 명시적으로 나열
- [ ] 옮긴 내용이 `governance_precedence.md` §5 기술 범위를 벗어나지 않는지 확인
- [ ] 대상 저장소 `README.md`에서 `.governance/` 링크 추가
- [ ] 병행 기간 동안 새 위치가 정상 인식되는지 확인
- [ ] 전역 skill `zircon-readme-policy` 제거
- [ ] 에이전트 JSON의 `resources`에서 해당 skill 참조 제거 여부 확인
- [ ] `02_kiro/skills/zircon-readme-policy/` 미러 제거
- [ ] 이 저장소 `CHANGELOG.md` 기록

Zircon 예외는 푸터·통계 항목으로 한정되어 있어 `governance_template.md`의 작성
예시가 그대로 적용됩니다. 두 대상 중 먼저 진행하기 쉽습니다.

#### 이관 2: Ansible 학습·자동화 저장소

- [ ] 대상 저장소에 `.governance/GOVERNANCE.md` 생성 (템플릿 사용)
- [ ] `profiles/chobo_ansible.md` 내용을 옮기고 유지하는 전역 규칙을 명시적으로 나열
- [ ] 옮긴 내용이 `governance_precedence.md` §5 기술 범위를 벗어나지 않는지 확인
      - 현재 profile은 문서 역할·생명주기 예외와 검증 기준을 함께 담고 있어
        `verification.md` 분리가 필요할 수 있음
- [ ] 대상 저장소 `README.md`에서 `.governance/` 링크 추가
- [ ] 병행 기간 동안 새 위치가 정상 인식되는지 확인
- [ ] `profiles/chobo_ansible.md` 제거
- [ ] 이 저장소 `README.md` §4 저장소별 규칙 설명에서 profile 참조 제거
- [ ] 이 저장소 `CHANGELOG.md` 기록

### 보통

- [x] `.governance/GOVERNANCE.md` 템플릿 작성 (2026-08-27 완료)
      - 위치: `templates/governance_template.md`
      - 포함: 적용 범위, 저장소 성격, 유지하는 전역 규칙, 저장소 전용 예외, 검증, 기록 금지 항목
- [ ] 이관 완료 후 `profiles/` 디렉토리 존치 여부 결정
      - 모든 profile이 각 저장소로 이관되면 디렉토리가 비게 됨
      - 이 저장소 자체의 profile을 둘 것인지 검토

## 2. 검사 설정 개선

`.md-style-check.toml` 관련 항목입니다.

### 높음

- [ ] 절대경로 기록과 `documentation_policy.md` §3 충돌 해소
      - 발견 경위: 이관 대상 정리 중 확인
      - `documentation_policy.md` §3은 "개인 경로, 내부 IP, 자격증명은 저장소에
        기록하지 않습니다"로 규정
      - 그런데 `02_kiro/skills/zircon-readme-policy/SKILL.md`와
        `02_kiro/skills/repo-governance/SKILL.md` 미러에 로컬 절대경로가 기록되어 있음
      - 판단 필요: 저장소 자체 경로와 다른 저장소의 로컬 경로를 같은 기준으로 볼지,
        skill 미러를 예외로 둘지, 경로를 저장소 식별자로 대체할지
      - 이 TODO 문서는 충돌을 피하기 위해 절대경로 대신 저장소 식별자를 사용함
- [x] `exclude_files` 제외 해제 (2026-08-27 완료)
      - 측정 결과 `CHANGELOG.md`, `LICENSE.md`, `TODO.md` 는 푸터를 갖추고 있어
        제외 없이도 0건 통과. 제외할 근거가 없었음
      - `license_guide.md` 만 표 정렬 26건이 실제 문제였으며 재정렬로 해소
        (`:---:` 등 정렬 지정자 보존)
      - `.md-style-check.toml` 의 `exclude_files` 와 코드 기본값 `EXCLUDE_FILES` 를
        모두 비움. 검사 대상 362개 → 366개
      - 부수 효과: 파일명 기준 전역 제외가 사라져 하위 디렉토리 `TODO.md` 도 검사 대상이 됨

### 보통

- [ ] `skip_checks` 활용 방안 정리
      - 현재 `skip_checks = []`이며 주석에 "저장소별 설정에서 추가할 수 있습니다"로 기재
      - `.governance/` 체계와 연결하여 저장소별 검사 예외를 어떻게 표현할지 정의 필요
- [x] 헤딩 구조·앵커 검사 도구 추가 (2026-08-27 완료)
      - `md-link-check.py`는 docstring에 `#anchor` 링크를 검증 제외로 명시하고
        있어 결함이 아니라 의도된 범위 제외였음
      - 별도 검사기 `md-heading-check.py` 추가 (anchor / number / level / duplicate)
      - 검증: `git_concepts.md`의 앵커 1건·번호 불연속 1건, `CHANGELOG.md`의
        앵커 7건을 검출. templates 8개는 0건 통과
      - CI에 `continue-on-error: true` 경고 모드로 등록

### 헤딩 구조 잔여 이슈 정리 (우선순위: 보통)

`md-heading-check.py` 도입으로 51건이 검출되었고, 정리·도구 오탐 수정·예외 등록을
거쳐 **0건**이 되었습니다. CI에서 필수 검사로 승격했습니다.

| 유형        | 건수 | 조치                                                          |
|-------------|------|---------------------------------------------------------------|
| `anchor`    | 0    | 링크 정정 6건, 헤딩 제목 단순화 1건. 나머지는 도구 오탐이었음 |
| `number`    | 0    | `STYLE.md` 중첩 펜스·중복 번호, `git_concepts.md` 재번호      |
| `level`     | 0    | H4→H3 조정 1건, `vim_airline.md` 는 설정으로 예외 처리        |
| `duplicate` | 0    | 동일 제목 헤딩 2건에 구분 표기 추가                           |

- [x] 목차 없는 문서의 복귀 링크 제거 (2026-08-27 완료)
      - `CHANGELOG.md` 7건, `LICENSE.md` 4건. 두 파일 모두 `## 목차`가 없는데
        `[⬆ 목차로 돌아가기](#목차)`만 존재
      - 원인: 과거 릴리스 항목에 남은 `` `[⬆ 목차로 돌아가기]` 전체 파일 추가 ``
        기록으로 보아 일괄 추가 작업의 부산물. 이후 릴리스에는 추가되지 않아
        21개 릴리스 중 6개 뒤에만 불규칙하게 존재
      - 조치: `changelog_template.md`의 권장(CHANGELOG에 목차를 두지 않음)에 따라 제거
- [x] `anchor` 정리 (2026-08-27 완료)
      - 대부분 도구 오탐이었음. `make_anchor` 가 밑줄을 제거해 `TIME_WAIT`,
        `__init__` 같은 헤딩을 모두 불일치로 판정
      - github-slugger(`Flet/github-slugger` master/regex.js) 문자 집합을 이식하고
        저장소 헤딩 18,288개로 원본과 동일함을 검증
      - 실제 결함 7건 수정: em dash·슬래시·`+` 제거로 하이픈 수가 달라지는 앵커 6건 정정,
        `gitignore_patterns.md` 는 제목의 장식용 `` (`!`) `` 제거로 목차와 일치시킴
      - 부수 작업: 링크 길이 변화로 깨진 목차 표 정렬 3개 파일 재정렬
- [x] `number` / `level` / `duplicate` 정리 (2026-08-27 완료)
      - `STYLE.md`: 중첩 펜스 오류로 §5~§7, §10, §11 이 코드블록에 삼켜지던 문제 수정
        (외부 펜스를 4-backtick 으로 승격). `## 14.` 중복을 14/15/16 으로 재번호
      - `ansible_install_and_team_operation.md`: `## 6.` 직하 H4 를 H3 로 조정
      - `s3_gateway_endpoint_cross_account.md`: 동일 제목 H2/H3 중 H3 에 `(콘솔)` 명시
      - `se_complete_roadmap_programming_languages.md`: Q&A 절의 `### 결론` 을
        `### 자주 묻는 질문` 으로 변경 (내용과 더 일치)
      - `02_kiro/` 미러 2개는 원본(`~/.kiro/`) 수정 후 재동기화
      - 도구 오탐 3종 수정 (아래 항목 참고)
- [x] `md-heading-check.py` 오탐 수정 (2026-08-27 완료, v26.08.27.4)
      - 펜스 판정을 CommonMark 규칙으로 교체. 정보 문자열이 있는 펜스는 닫는
        펜스가 아니며, 들여쓰기 4칸 이상은 펜스가 아님
      - `## 5-10. 제목` 범위 표기 지원 (외부 규칙 번호에 대응하는 문서)
      - `## 1-1. 제목` 하위 절 표기 지원 (번호를 진행시키지 않음)
      - 이 수정으로 `work-rules-guide.md`, `percona_xtrabackup_guide.md`,
        `infra_monorepo_and_boilerplate.md`, `work-rules/SKILL.md` 오탐 해소
- [x] `md-heading-check.py` 예외 설정 지원 추가 (2026-08-27 완료, v26.08.27.5)
      - `.md-heading-check.toml` 자동 탐색. `exclude_dirs`, `exclude_files`,
        `skip_checks`, 파일별 `[[file_skip]]` 지원
      - `[[file_skip]]` 은 `path`, `checks`, `reason` 을 받아 사유를 함께 기록
      - CLI `-c/--config`, `-E/--exclude-dir`, `-X/--exclude-file` 추가
      - `vim_airline.md` 의 `level` 검사를 예외 등록 (외부 README 원본)
      - CI 트리거 경로에 `.md-heading-check.toml` 추가
- [x] `git_concepts.md` 번호 재부여 (2026-08-27 완료)
      - 목차가 존재하지 않는 §2 를 링크하던 문제. §3~§10 을 §2~§9 로 내리고 목차 재작성
      - 내부 장 참조와 외부 앵커 참조가 없어 부수 영향 없음
- [x] CI 필수 검사로 승격 (2026-08-27 완료)
      - `continue-on-error` 제거. 이제 헤딩 구조 이슈가 있으면 workflow 가 실패합니다
- [x] skill 반영 (2026-08-27 완료)
      - `md-link-check` skill: 앵커 규칙에 밑줄·이모지 유지가 누락되어 있었음.
        이 누락이 검사기 초기 오탐 15건의 원인과 동일. github-slugger 기준으로 정정
      - `md-link-check` skill: 잘못된 `github_anchor()` 예시 스크립트 제거.
        이모지를 제거하고 상첨자를 남기는 등 원본과 달랐음
      - `md-link-check` skill: 중첩 코드블록 4-backtick 규칙, 확장 번호 표기
        (`5-10.` 범위 / `1-1.` 하위 절), 헤딩 레벨·중복 앵커 규칙 추가
      - `STYLE.md` §4: 중첩 코드블록 4-backtick 규칙 추가 (이 문서가 결함 당사자였음)
      - `work-rules` §11, `git-commit-rule` 절차, `using-skills` 분기,
        `skills/README.md`: 검사 도구 3종 병행 실행으로 갱신
      - `02_kiro/` 미러 6개 파일 재동기화
- [x] `02_kiro/` 미러의 스타일 검사 공백 해소 (2026-08-27 완료)
      - 발견 경위: skill 수정 후 `md-style-check.py --no-footer` 를 직접 실행하여 확인
      - 원인: `exclude_dirs` 에 미러가 있어 표 정렬·문체 검사가 함께 빠졌음.
        `KIRO_SKIP = {footer, h1, diagram-kr}` 이 이미 있었으나 판정 조건이
        `'.kiro' in path` 여서 미러 경로(`00_governance/02_kiro`)를 인식하지 못했음
      - 조치: 판정 조건을 `/.kiro/` 또는 `/02_kiro/` 로 확장하고 `exclude_dirs` 에서
        미러 제거. `FILE_SKIP` 에 `markdown/STYLE.md` 의 금지 예시 인용 2항목 등록
      - 결과: 검사 대상 323개 → 362개 (39개 증가), 이슈 0건

### 낮음

- [ ] H2 번호 연속성 검사 추가 검토
      - `md-style-check.py`가 `## 1.` → `## 3.` 같은 번호 누락을 검출하지 않음
      - 위 `git_concepts.md` 사례에서 두 검사기 모두 통과한 원인 중 하나

## 3. 정책 문서 보완

### 보통

- [ ] `documentation_policy.md`와 `governance_precedence.md` 관계 명시
      - 전자는 문서 역할·생명주기, 후자는 규칙 적용 순서를 다룸
      - 두 문서가 충돌하지 않도록 상호 참조 추가
- [x] `README.md` §3 정책 문서 목록에 `governance_precedence.md` 추가 (2026-08-27 완료)
- [x] `README.md` §4 저장소 profile 설명을 `.governance/` 체계로 갱신 (2026-08-27 완료)

### 낮음

- [ ] `03_claude/` 활성화 시점의 정책 정의
      - 현재 `README.md`만 있고 원본·허용 목록이 미정
      - `sync_policy.md`에 Claude 항목 추가 필요
- [ ] 도구 중립 규칙과 도구 종속 규칙의 분리 기준 정리
      - 현재 `01_repository_governance/`가 도구 중립, `02_kiro/`가 도구 종속
      - `.governance/` 체계에서 도구별 예외가 필요해질 경우의 처리 방침

## 4. 템플릿 확충

### 보통

- [x] `templates/governance_template.md` 작성 (2026-08-27 완료, 1장 항목과 동일)
- [x] `templates/todo_template.md` 작성 (2026-08-27 완료)
- [x] `templates/changelog_template.md` 작성 (2026-08-27 완료)
      - `documentation_policy.md`가 정의하는 문서 4종에 모두 템플릿이 대응하게 됨
- [x] 템플릿 푸터 처리 방침 정리 (2026-08-27 완료)
      - 발견 경위: `governance_template.md` 작성 시 확인
      - 템플릿 파일 자체는 이 저장소 규칙상 푸터가 필요하나, 복사된 문서는 대상
        저장소 규칙을 따라야 함
      - 조치: 템플릿 5개 전체에 복사 시 푸터·날짜 처리 안내 문구 추가

- [x] `templates/readme_template.md` 작성 (2026-08-27 완료)
- [x] `templates/runbook_template.md` 작성 (2026-08-27 완료)
      - `chobo_ansible` profile이 README를 운영 Runbook으로 정의하나 형식이 없던 공백 해소
- [x] `templates/verification_template.md` 작성 (2026-08-27 완료)
      - `.governance/verification.md` 선택 파일의 형식 확보. Ansible 저장소 이관 시 활용

- [x] 템플릿 전체 일관성 점검 (2026-08-27 완료)
      - 목차 앵커 정합성, H2 번호 연속성, 헤딩 레벨 점프를 스크립트로 검증
      - 8개 전부 앵커 불일치 0건, 번호 연속, 레벨 점프 0건 확인
      - 수정: `issue`·`plan`·`runbook`에 `1. 사용 방법` 신설, `governance`의 무번호
        섹션 2개에 번호 부여, `readme`·`runbook`에 정책 참조 추가,
        `issue`·`plan`·`runbook`·`verification`에 민감정보 기록 금지 추가,
        푸터 안내 문구 8개 통일

### 낮음

- [ ] 템플릿 사용 실태 점검
      - 템플릿이 실제로 복사되어 쓰이는지, 형식이 현실과 어긋나지 않는지 확인
      - 어긋나면 템플릿을 현실에 맞추고, 현실이 잘못이면 문서를 교정

## 5. 결정 기록

구조·정책에 관한 판단과 그 근거를 기록합니다. 결론이 유지인 경우에도 재검토
조건을 함께 남겨 동일한 논의를 반복하지 않도록 합니다.

### `00_governance/` 하위 저장소 분리 (2026-08-27)

`01_repository_governance/`, `02_kiro/`, `03_claude/`를 각각 별도 저장소로 분리하는
방안을 검토했습니다. **현 시점에는 분리하지 않고 유지합니다.**

#### 측정 결과

| 대상                        | 크기 | md 파일 | 평가                 |
|-----------------------------|------|---------|----------------------|
| `01_repository_governance/` | 60K  | 9       | 독립 저장소로는 과소 |
| `02_kiro/`                  | 360K | 39      | 독립 가능            |
| `03_claude/`                | 4K   | 1       | 내용 미확정          |
| `00_governance/` 합계       | 428K | 50      | 저장소 전체의 약 1%  |
| 저장소 전체                 | 42M  | 426     | -                    |

결합도는 낮습니다. `00_governance/`에서 저장소 나머지로 나가는 상대링크는 0건이고,
들어오는 링크는 루트 `README.md` 3건입니다. 기술적 분리 자체는 가능합니다.

#### 유지 판단 근거

- `03_claude/`는 예약 영역이며 저장소를 구성할 내용이 없습니다.
- `01_repository_governance/`와 `02_kiro/`가 상호 참조합니다. 특히 `sync_policy.md`는
  존재 목적이 미러 동기화 규칙 정의이므로, 정책과 관리 대상을 분리하면 변경 시 두
  저장소를 함께 확인해야 합니다.
- 검사 도구와 CI 설정이 저장소 루트에 있습니다. 분리하면 `md-link-check.py`,
  `md-style-check.py`, `readme_inventory_check.py`, `.md-style-check.toml`,
  `.gitleaks.toml`, 워크플로를 저장소마다 복제해야 하고 이후 수정이 배수로 늘어납니다.
- `01_repository_governance/`는 이 저장소의 운영 기준 원본입니다. 저장소별 규칙을
  해당 저장소에 두기로 한 `governance_precedence.md` 방향과, 정책 원본만 외부로
  분리하는 것은 서로 어긋납니다.

#### 재검토 조건

| 재검토 조건                                     | 분리 대상            | 판단 근거                       |
|-------------------------------------------------|----------------------|---------------------------------|
| 미러 동기화 커밋이 전체 커밋의 상당 비중을 차지 | `02_kiro/`           | 커밋 주기가 기술 문서와 다름    |
| Claude 자료가 실제로 추가되어 독립 규모 확보    | 도구 미러 통합       | `03_claude/` 단독 분리는 무의미 |
| 도구 미러가 3종 이상으로 증가                   | 미러 전용 저장소 1개 | 미러끼리 성격이 동일            |

- [ ] 위 조건 충족 여부를 주기적으로 확인하고, 충족 시 분리를 재검토합니다.

`02_kiro/`는 단독으로 분리 근거가 있는 편입니다. 이 저장소에서 작성한 원본이 아니라
단방향 미러이므로 이미 `.md-style-check.toml`의 `exclude_dirs`에 등록되어 스타일
검사에서 제외되어 있습니다. md 파일 39개가 저장소 규칙 검사를 받지 않는 상태이며,
별도 저장소로 옮기면 이 예외 설정을 없앨 수 있습니다. 동기화 스크립트의 타깃 경로도
한 곳에 정의되어 변경 비용이 작습니다.

---

**작성일**: 2026-08-27

**마지막 업데이트**: 2026-08-27

© 2026 siasia86. Licensed under CC BY 4.0.

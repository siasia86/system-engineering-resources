# Repository Governance TODO

`00_governance/01_repository_governance/` 자체의 개선 항목을 관리합니다. 저장소 전역
작업은 루트 `TODO.md`에서 관리하며, 이 문서는 governance 체계에 한정합니다.

## 목차

| 섹션                                                                                    |
|-----------------------------------------------------------------------------------------|
| [1. 우선순위 체계 도입](#1-우선순위-체계-도입) / [2. 검사 설정 개선](#2-검사-설정-개선) |
| [3. 정책 문서 보완](#3-정책-문서-보완) / [4. 템플릿 확충](#4-템플릿-확충)               |

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
- [ ] `profiles/chobo_ansible.md`를 대상 저장소 `.governance/`로 이관
      - 현재: 규칙이 적용될 저장소 밖(이 저장소)에 위치
      - 절차: `governance_precedence.md` §6 이관 절차 준수 (병행 기간 필수)
      - 이관 후 `README.md` §4 "저장소 profile" 항목 갱신 필요
- [ ] 전역 skill `zircon-readme-policy`를 대상 저장소 `.governance/`로 이관
      - 현재: 전역 skill이라 무관한 세션에서도 로드됨
      - 이관 후 전역 skill 제거

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

- [ ] `exclude_files`의 `TODO.md` 제외 범위 축소 검토
      - 현재: 파일명 기준 전역 제외. 저장소 내 모든 경로의 `TODO.md`가 검사 대상에서 빠짐
      - 확인 결과 현재 저장소에는 루트 `TODO.md` 1개만 존재하여 실제 영향은 없음
      - 다만 이 문서처럼 하위 디렉토리에 TODO 문서를 두면 검사 공백이 발생
      - 대안: 경로 기준 제외(`/TODO.md`)로 변경하거나, 하위 TODO는 다른 파일명 사용
      - 이 문서를 `governance_todo.md`로 명명한 이유가 이 제한 회피임

### 보통

- [ ] `skip_checks` 활용 방안 정리
      - 현재 `skip_checks = []`이며 주석에 "저장소별 설정에서 추가할 수 있습니다"로 기재
      - `.governance/` 체계와 연결하여 저장소별 검사 예외를 어떻게 표현할지 정의 필요
- [ ] `md-link-check.py`의 목차 앵커 검사 누락 보완
      - 발견 경위: `01_fundamentals/cs/git_concepts.md`의 목차가 존재하지 않는 §2를
        링크하고 있었으나 검사를 통과함
      - 원인 추정: 목차 표 내부 앵커 링크를 검사 대상에 포함하지 않음
      - 영향: 목차와 본문 헤딩 불일치를 자동 검출하지 못함

### 낮음

- [ ] H2 번호 연속성 검사 추가 검토
      - `md-style-check.py`가 `## 1.` → `## 3.` 같은 번호 누락을 검출하지 않음
      - 위 `git_concepts.md` 사례에서 두 검사기 모두 통과한 원인 중 하나

## 3. 정책 문서 보완

### 보통

- [ ] `documentation_policy.md`와 `governance_precedence.md` 관계 명시
      - 전자는 문서 역할·생명주기, 후자는 규칙 적용 순서를 다룸
      - 두 문서가 충돌하지 않도록 상호 참조 추가
- [ ] `README.md` §3 정책 문서 목록에 `governance_precedence.md` 추가
- [ ] `README.md` §4 저장소 profile 설명을 `.governance/` 체계로 갱신

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

### 낮음

- [ ] 템플릿 푸터 처리 방침 정리
      - 발견 경위: `governance_template.md` 작성 시 확인
      - 템플릿 파일 자체는 이 저장소 규칙에 따라 푸터가 필요하나, 복사된
        `GOVERNANCE.md`는 대상 저장소 규칙을 따라야 함
      - 현재는 템플릿 본문에 주의 문구로 안내. 다른 템플릿에도 동일 상황이 있는지 확인 필요
- [ ] `templates/todo_template.md` 작성 검토
      - 현재 `plan_template.md`, `issue_template.md`만 존재
      - TODO는 구조가 단순해 템플릿 필요성이 낮을 수 있음
- [ ] `templates/changelog_template.md` 작성 검토
      - `documentation_policy.md`가 `CHANGELOG.md`를 정의하나 템플릿은 없음

---

**작성일**: 2026-08-27

**마지막 업데이트**: 2026-08-27

© 2026 siasia86. Licensed under CC BY 4.0.

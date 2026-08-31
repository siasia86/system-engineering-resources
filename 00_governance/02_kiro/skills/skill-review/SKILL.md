---
name: skill-review
description: Skill·hook·prompt의 portability, 보안, 실행 contract, source·mirror 일관성을 검토합니다.
---

# Skill Review

Skill과 관련 hook·prompt·설정의 공용성을 검토하는 절차입니다. 특정 계정, repository, 운영 도구, branch, 경로에 종속되지 않도록 설계합니다.

## 1. 목적

다음 항목을 read-only로 점검합니다.

- skill의 source of truth와 mirror 관계.
- 계정·호스트·repository 종속성.
- 실행 권한과 보안 위험.
- 외부 command·config·version contract.
- TODO·PLAN·governance 문서와의 일관성.
- 실패·경계 입력·다른 실행 환경에 대한 동작.

## 2. 기본 원칙

- 기본 모드는 read-only audit입니다.
- 사용자의 명시적 요청 없이 파일을 수정·삭제·commit·push하지 않습니다.
- 사용자의 명시적 요청 없이 network 요청을 수행하지 않습니다.
- root 권한이 필요한 경우 읽기 작업에만 사용합니다.
- 사용자 소유 파일을 root 권한으로 실행하지 않습니다.
- secret·token·private key·민감한 경로는 출력하지 않습니다.
- 특정 계정명·repository 경로·branch명·고정 IP를 공용 skill에 기록하지 않습니다.
- repository별 차이는 local governance와 환경 profile에서 관리합니다.

## 3. 입력과 범위

review를 시작하기 전에 사용 가능한 대상을 확인합니다.

```text
skill source:   호출자가 제공한 경로 또는 현재 runtime skill
mirror:         선택 입력. 없으면 source만 검토
repository:     선택 입력. 있으면 local governance를 함께 검토
TODO/PLAN:      선택 입력. 있으면 미완료 항목과 대조
```

mirror가 없으면 source·mirror 비교를 생략하고, 그 사실을 결과에 기록합니다. 대상 경로를 추측하지 않습니다.

## 4. 검토 절차

### 4-1. 구조와 metadata

- frontmatter의 `name`과 설명이 실제 역할과 일치하는지 확인합니다.
- 명령어·hook·prompt의 입력과 출력 contract를 확인합니다.
- 참조하는 파일·skill·config가 실제로 존재하는지 확인합니다.
- 문서와 실행 파일의 source of truth가 서로 다르지 않은지 확인합니다.

### 4-2. Portability

다음 종속성을 검색합니다.

```text
절대 경로
특정 사용자명
특정 계정의 HOME
고정 repository 경로
고정 branch명
고정 OS·shell·package manager
PATH에만 의존하는 command
sudo·root 권한 전제
```

공용 skill은 다음 방식으로 환경을 주입해야 합니다.

```text
환경 변수
repository-local config
runtime PATH의 command discovery
호출자가 전달한 대상 경로
```

환경 의존성이 불가피하면 필요한 전제와 실패 메시지를 문서에 기록합니다.

### 4-3. 보안

- 사용자 입력이 shell command·path·config로 전달되는지 확인합니다.
- 모든 변수 인용과 option terminator(`--`) 사용 여부를 확인합니다.
- 사용자 소유 실행 파일을 권한 상승하여 실행하지 않는지 확인합니다.
- config·hook·prompt가 secret을 로그에 출력하지 않는지 확인합니다.
- checker나 parser가 없을 때 검증이 무음으로 우회되지 않는지 확인합니다.
- 권한 상승이 필요하면 대상·이유·범위를 명시합니다.

### 4-4. 실행 contract

다음 조건을 확인합니다.

- 필요한 command의 존재 여부.
- command version과 config schema 호환성.
- config 없음·잘못된 config 처리.
- command의 성공·검사 실패·실행 실패 exit code 구분.
- wrapper와 직접 실행 파일의 source of truth 일치.
- 하위 디렉토리에서 실행할 때 repository root와 config를 올바르게 찾는지 여부.

### 4-5. Source와 mirror

mirror가 제공된 경우 다음을 비교합니다.

```bash
sha256sum <source> <mirror>
diff -u <source> <mirror>
```

차이가 있으면 다음을 구분합니다.

- 의도된 mirror 변형.
- sync 누락.
- source of truth 미정.
- 계정별 local override.

### 4-6. Governance와 작업 문서

repository가 제공된 경우 local governance를 먼저 읽습니다.

- governance의 문서 위치와 skill의 탐색 규칙이 일치하는지 확인합니다.
- TODO의 미완료 작업이 skill의 현재 동작과 충돌하지 않는지 확인합니다.
- PLAN의 active task와 실제 변경 범위가 일치하는지 확인합니다.
- CHANGELOG가 완료된 변경만 기록하는지 확인합니다.
- 공용 skill에 단일 프로젝트 운영 사실이 섞여 있지 않은지 확인합니다.

검토 결과를 자동으로 TODO·PLAN에 기록하지 않습니다. 누락 항목은 제안으로만 출력합니다.

## 5. Edge case 검증

가능한 환경에서 다음 입력을 확인합니다.

```text
빈 값·unset 환경 변수
공백이 포함된 경로
한글·특수문자가 포함된 경로
- 로 시작하는 파일명
repository root가 아닌 하위 디렉토리 실행
config 파일 없음
잘못된 config 문법
필요 command 없음
command가 non-zero 반환
읽기·실행 권한 부족
mirror 없음 또는 source와 불일치
```

테스트는 임시 대상과 read-only 방식으로 수행합니다. 테스트용 파일·config는 작업 후 제거합니다.

## 6. 파일 유형별 검증

- Shell: `bash -n`, `shellcheck`.
- Python: `py_compile` 또는 repository가 지정한 syntax check.
- Config: 해당 parser 또는 repository validator.
- Markdown: repository가 지정한 style·heading·link checker.
- Hook: 정상 입력·checker 부재·실패 입력 smoke test.

도구가 없으면 검증 성공으로 처리하지 않고 `검증 불가`로 기록합니다.

## 7. 결과 형식

```markdown
## Skill Review 결과

### 1. 범위

- source:
- mirror:
- repository:
- 검증 도구:

### 2. Findings

| ID | 심각도 | 위치 | 근거 | 위험 | 권장 조치 |
|----|--------|------|------|------|-----------|

- 🔴 보안·검증 우회·데이터 손상 가능성
- 🟡 portability·운영 안정성·계약 불일치
- ☆ 선택적 개선

### 3. Edge case 결과

- 입력:
- 기대 결과:
- 실제 결과:
- 상태:

### 4. TODO/PLAN 영향

- 완료 처리 후보:
- 새 작업 제안:
- 변경 없음:

### 5. 변경 사항

기본 audit 모드에서는 `변경 없음`을 기록합니다.

### 6. 최종 판단

- 공용 사용 가능 여부:
- merge 전 필수 조치:
- 잔여 위험:
```

## 8. 수정 모드

사용자가 수정까지 요청한 경우에만 다음 순서로 진행합니다.

1. 수정 범위와 source of truth를 확인합니다.
2. 공용 부분과 local dependency를 분리합니다.
3. source와 mirror를 같은 변경으로 갱신합니다.
4. 파일별 검증과 edge case를 수행합니다.
5. 관련 TODO·PLAN 변경을 제안하거나 명시적으로 갱신합니다.
6. 명시된 파일만 stage하고 commit·push 결과를 확인합니다.

특정 프로젝트의 단발성 workaround는 공용 skill에 추가하지 않고 해당 repository의 governance·runbook·profile에 기록합니다.

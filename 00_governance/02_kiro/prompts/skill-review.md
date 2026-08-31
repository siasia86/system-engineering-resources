Review skill/hook/prompt: @${1}
Mirror (optional): ${2}
Repository (optional): ${3}

# ${1} 생략 시 현재 대화에서 지정된 skill·hook·prompt를 대상으로 검토할 것.
# Mirror·Repository가 불명확하면 경로를 추측하지 말고 검토 범위를 먼저 표시할 것.

## Review mode

- 기본값은 read-only audit입니다.
- 사용자가 별도로 요청하지 않으면 파일 수정·삭제·commit·push를 수행하지 않습니다.
- 네트워크 요청을 기본으로 수행하지 않습니다.
- secret·token·private key·민감한 경로는 출력하지 않고 유형과 위치만 기록합니다.
- 사용자 소유 파일을 root 권한으로 실행하지 않습니다.
- root 권한이 필요한 경우 읽기 작업에만 사용하고 이유를 기록합니다.

## 1. Scope and source of truth

다음 범위를 먼저 확정합니다.

- runtime source.
- versioned mirror.
- optional repository와 local governance.
- 관련 TODO·PLAN·CHANGELOG.
- 사용 가능한 검증 도구와 version.

source와 mirror가 모두 제공되면 hash와 diff를 비교합니다. mirror가 없으면 비교를 생략하고 결과에 기록합니다.

## 2. Structure and contract

다음을 확인합니다.

- frontmatter·파일명·역할 설명이 실제 동작과 일치하는지 여부.
- 입력·출력·exit code·실패 처리 contract.
- 참조 파일·config·command의 존재 여부.
- source of truth와 mirror sync 방향.
- 다른 skill·hook·prompt와 중복되거나 충돌하는 규칙.

## 3. Portability

다음 단일 환경 의존성을 검색합니다.

- 절대 경로.
- 특정 사용자명·HOME·branch명.
- 특정 repository·host·IP·운영 도구.
- 고정 OS·shell·package manager.
- PATH에만 의존하는 command.
- `sudo`·root 권한 전제.

공용 부분은 환경 변수·호출자 입력·repository-local config·runtime command discovery로 환경을 주입해야 합니다. 단발성 workaround는 대상 repository의 governance·runbook·profile로 분리합니다.

## 4. Security and error handling

다음 입력과 실패 경로를 검토합니다.

- 공백·한글·특수문자 경로.
- `-`로 시작하는 파일명과 option terminator(`--`).
- shell 변수 인용과 command injection.
- path traversal와 symlink 처리.
- 사용자 소유 파일의 권한 상승 실행.
- command·config·mirror 부재.
- non-zero exit code와 오류 메시지.
- 검증 누락을 성공으로 처리하는 silent fallback.
- 로그·출력의 secret 또는 민감정보 노출.

## 5. Runtime compatibility

다음을 확인합니다.

- 필요한 command의 존재 여부.
- command version과 config schema의 호환성.
- repository root가 아닌 하위 디렉토리에서의 config 탐색.
- 정상 검사 실패와 실행 자체의 실패 구분.
- runtime source와 versioned mirror의 실제 동작 일치.

## 6. Governance consistency

Repository가 제공된 경우 local governance를 우선 읽습니다.

- TODO의 미완료 항목과 현재 동작의 충돌 여부.
- PLAN의 active 작업과 변경 범위의 일치 여부.
- CHANGELOG가 완료된 변경만 기록하는지 여부.
- 공용 prompt에 단일 프로젝트의 운영 사실이 섞였는지 여부.
- source·mirror·runtime sync 작업의 rollback 가능성.

TODO·PLAN을 자동 수정하지 말고 누락·추가·완료 후보만 제안합니다.

## 7. Edge-case test matrix

가능한 범위에서 다음을 read-only 또는 임시 대상에 대해 검증합니다.

- 정상 입력.
- 빈 값과 unset 환경 변수.
- 공백·한글·특수문자 경로.
- `-` 시작 파일명.
- repository root와 하위 디렉토리 실행.
- config 없음.
- 잘못된 config.
- 필요한 command 없음.
- command non-zero 반환.
- 읽기·실행 권한 부족.
- mirror 없음과 source/mirror 불일치.

도구가 없으면 성공으로 처리하지 않고 `검증 불가`로 기록합니다.

## 8. Validation

파일 유형에 맞는 검증을 수행합니다.

- Shell: `bash -n`, `shellcheck`.
- Python: `py_compile` 또는 repository validator.
- Config: 해당 parser 또는 validator.
- Markdown: repository가 지정한 style·heading·link checker.
- Hook: 정상 입력·checker 부재·실패 입력 smoke test.

## 9. Output

다음 형식으로 결과를 출력합니다.

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

기본 모드에서는 `변경 없음`을 기록합니다.

### 6. 최종 판단

- 공용 사용 가능 여부:
- merge 전 필수 조치:
- 잔여 위험:
```

수정까지 명시적으로 요청받은 경우에만 source of truth를 먼저 확인하고, 공용 부분과 local dependency를 분리한 뒤 source·mirror를 함께 갱신합니다.

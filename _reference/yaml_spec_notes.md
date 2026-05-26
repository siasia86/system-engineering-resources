---
name: yaml-spec-notes
last_checked: 2026-05-26
sources:
  - https://yaml.org/spec/1.2.2/
  - https://yaml.org/spec/1.1/
  - https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html
  - https://yaml-multiline.info/
---

# YAML Spec 공식 노트

## 1. 블록 스칼라 (§ 8.1)

### 출처: YAML 1.2.2 Spec § 8.1 Block Scalar Styles

- Literal (`|`): 줄바꿈 보존 (§ 8.1.2)
- Folded (`>`): 줄바꿈을 공백으로 변환 (§ 8.1.3)
- Chomping indicator: 끝 개행 처리 (§ 8.1.1.2)
  - strip (`-`): 끝 개행 제거
  - clip (기본): 개행 1개 유지
  - keep (`+`): 모든 끝 개행 유지

### 확인 사항

- `>` 모드에서 빈 줄은 줄바꿈으로 유지됨 — Spec § 8.1.3 "More-indented lines are not folded"
- 들여쓰기 지시자(숫자): `|2`, `>4` 등으로 들여쓰기 칸 수 명시 가능

## 2. 앵커와 별칭 (§ 7.1)

### 출처: YAML 1.2.2 Spec § 7.1 Alias Nodes

- `&anchor`: 앵커 정의
- `*anchor`: 별칭 참조 (동일 노드 재사용)
- Merge Key (`<<`): YAML Spec에는 없음 — PyYAML/libyaml 확장 기능
  - 출처: https://yaml.org/type/merge.html (YAML 1.1 type)
  - Ansible/Docker Compose에서 지원

## 3. Boolean 해석 차이 (Norway 문제)

### YAML 1.1 (PyYAML, Ansible 사용)

Boolean으로 해석되는 값:
- `y`, `Y`, `yes`, `Yes`, `YES`
- `n`, `N`, `no`, `No`, `NO`
- `true`, `True`, `TRUE`
- `false`, `False`, `FALSE`
- `on`, `On`, `ON`
- `off`, `Off`, `OFF`

출처: https://yaml.org/type/bool.html (YAML 1.1 tag repository)

### YAML 1.2

Boolean: `true`, `false` 만 해당 (대소문자 무관하지 않음 — Core Schema에서는 `true`/`false`만)

출처: YAML 1.2.2 Spec § 10.3.2 Tag Resolution (Core Schema)

### Ansible 확인

- Ansible은 PyYAML 사용 → YAML 1.1 규칙 적용
- 출처: https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html
  - "YAML has a number of gotchas... yes, no, on, off are booleans"

## 4. 숫자 해석

### YAML 1.1

- `0o777`: 8진수
- `0x1A`: 16진수
- `3.10`: float (→ 3.1)
- `01234`: 8진수로 해석 가능 (leading zero)

### YAML 1.2

- `0o777`: 8진수
- `0x1A`: 16진수
- `01234`: 문자열 (leading zero는 숫자 아님)

출처: YAML 1.2.2 Spec § 10.3.2 (Core Schema integer/float 정규식)

## 5. 탭 금지

출처: YAML 1.2.2 Spec § 5.5 White Space Characters
- "Tab characters are not allowed in indentation"
- 탭은 flow scalar 내부에서만 허용

## 6. Ansible YAML 특이사항

출처: https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html

- `{{ variable }}` — Jinja2 템플릿, 값 시작 시 따옴표 필수
  - `value: "{{ my_var }}"` (따옴표 없으면 YAML dict로 해석)
- `raw` 모듈: Python 불필요, YAML 파싱은 Controller에서 수행
- `environment` 키: 모든 값은 문자열로 변환됨

## 7. 미확인 사항

- 없음 (모든 내용 공식 문서에서 확인 완료)

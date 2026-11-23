# yamllint

YAML 파일의 문법 오류와 형식(들여쓰기, 줄 끝 공백, 중복 키, truthy 값 등)을 검사하는 도구입니다. Ansible playbook, Docker Compose, Kubernetes manifest, CI 설정처럼 YAML로 쓰는 모든 파일에 쓸 수 있습니다. 이 문서만으로 설치 → 검사 → 설정 → CI 연결까지 따라 할 수 있게 썼습니다.

- 기준 판: yamllint 1.38.0(PyPI 기준, Python 3.10 이상)
- 예제 시험: 2026-11-23, yamllint 1.38.0에서 3·5·6·7절 예제를 실행해 출력과 종료 코드를 확인

## 목차

| 섹션                                                                                                                                         |
|----------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. 첫 검사](#3-첫-검사)                                                                           |
| [4. 주요 규칙](#4-주요-규칙) / [5. 설정 파일](#5-설정-파일) / [6. 예외 처리](#6-예외-처리)                                                   |
| [7. 종료 코드와 출력 형식](#7-종료-코드와-출력-형식) / [8. ansible-lint와 함께 쓰기](#8-ansible-lint와-함께-쓰기) / [9. CI 연결](#9-ci-연결) |
| [10. 검증](#10-검증) / [11. 트러블슈팅](#11-트러블슈팅) / [함께 보기](#함께-보기)                                                            |

---

## 1. 개요

| 항목       | 내용                                                                    |
|------------|-------------------------------------------------------------------------|
| 검사 내용  | 문법 오류, 중복 키, 들여쓰기, 줄 길이, 공백, truthy 값, 문서 시작 `---` |
| 검사 안 함 | 값의 의미 (Ansible 모듈 이름, Kubernetes 필드 등은 각 도구의 검사기 몫) |
| 결과 등급  | `error`(종료 코드 1)와 `warning`(기본은 통과)                           |
| 설정       | 프리셋 `default`·`relaxed`를 바탕으로 `.yamllint`에서 규칙별 조정       |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

```bash
# pip (가상환경 권장)
python3 -m venv ~/.venvs/yamllint
~/.venvs/yamllint/bin/pip install yamllint
export PATH="$HOME/.venvs/yamllint/bin:$PATH"

# pipx
pipx install yamllint

# 배포판 패키지 (배포판 판이라 오래될 수 있음)
sudo apt-get install -y yamllint      # Ubuntu / Debian
sudo dnf install -y yamllint          # Fedora, RHEL 계열은 EPEL
```

ansible-lint를 설치했다면 의존 패키지로 yamllint가 함께 설치되어 있습니다.

```bash
yamllint --version
# yamllint 1.38.0
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 첫 검사

### 3-1. 일부러 틀린 파일

`bad.yml` — 아래 내용을 저장한 뒤 2행 `port: 8080` 끝에 공백을 하나 넣습니다(문서에는 공백을 넣지 않았습니다).

```yaml
server:
  port: 8080
  enabled: yes
  name: web
  name: api
  tags: [ a,b ]
   timeout: 5
```

### 3-2. 실행

```bash
yamllint bad.yml          # 파일 하나
yamllint .                # 현재 디렉터리 아래 YAML 전체
yamllint --list-files .   # 검사 대상이 될 파일 목록만
```

출력:

```text
bad.yml
  1:1       warning  missing document start "---"  (document-start)
  2:13      error    trailing spaces  (trailing-spaces)
  3:12      warning  truthy value should be one of [false, true]  (truthy)
  5:3       error    duplication of key "name" in mapping  (key-duplicates)
  6:10      error    too many spaces inside brackets  (brackets)
  6:13      error    too few spaces after comma  (commas)
  6:14      error    too many spaces inside brackets  (brackets)
  7:4       error    syntax error: expected <block end>, but found '<block mapping start>' (syntax)
```

`행:열 등급 설명 (규칙)` 형식이며, 오류가 있으므로 종료 코드는 1입니다.

### 3-3. 고친 파일

```yaml
---
server:
  port: 8080
  enabled: true
  name: web
  tags: [a, b]
  timeout: 5
```

다시 실행하면 아무것도 출력하지 않고 종료 코드 0으로 끝납니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 주요 규칙

| 규칙                      | 검사 내용                              | `default` 프리셋                    |
|---------------------------|----------------------------------------|-------------------------------------|
| `syntax`                  | YAML 문법 오류                         | 항상 error                          |
| `key-duplicates`          | 같은 매핑 안의 중복 키                 | error                               |
| `indentation`             | 들여쓰기 칸 수와 일관성                | error, 칸 수는 파일 안에서 일관되게 |
| `trailing-spaces`         | 줄 끝 공백                             | error                               |
| `line-length`             | 한 줄 길이                             | error, 80자                         |
| `truthy`                  | `yes`·`no`·`on`·`True` 같은 참·거짓 값 | warning, `true`·`false`만 허용      |
| `document-start`          | 파일 맨 앞 `---`                       | warning, 있어야 함                  |
| `brackets`·`braces`       | `[ ]`·`{ }` 안쪽 공백                  | error, 안쪽 공백 없음               |
| `commas`·`colons`         | 쉼표·콜론 앞뒤 공백                    | error                               |
| `comments`                | `#` 뒤 공백, 내용과의 간격             | warning, 내용과 2칸                 |
| `new-line-at-end-of-file` | 파일 끝 줄바꿈                         | error                               |
| `octal-values`            | `0755` 같은 8진수 표기                 | 꺼짐                                |

YAML 1.1에서는 `yes`·`no`·`on`·`off`도 참·거짓으로 읽혀서 `country: no`가 `false`가 되는 일이 생깁니다. `truthy` 규칙은 이런 값을 찾아 줍니다. `0755`처럼 앞이 0인 숫자도 도구에 따라 8진수로 읽히므로 권한 값은 `"0755"`처럼 따옴표로 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 설정 파일

저장소 루트에 `.yamllint`, `.yamllint.yaml`, `.yamllint.yml` 중 하나를 둡니다. 없으면 `default` 프리셋을 씁니다.

```yaml
# .yamllint
extends: default

ignore: |
  .venv/
  collections/
  charts/*/templates/

rules:
  line-length:
    max: 120
  document-start: disable          # --- 를 강제하지 않음
  truthy:
    allowed-values: ["true", "false"]
    check-keys: false              # GitHub Actions의 "on:" 키를 허용
  comments:
    min-spaces-from-content: 1
```

| 설정 방법            | 예                              |
|----------------------|---------------------------------|
| 규칙 끄기            | `document-start: disable`       |
| 등급만 바꾸기        | `line-length: {level: warning}` |
| 다른 설정 파일 지정  | `yamllint -c path/to/config .`  |
| 명령줄에서 바로 지정 | `yamllint -d relaxed bad.yml`   |
| 검사 제외 경로       | `ignore:` (gitignore 형식)      |

`relaxed` 프리셋은 들여쓰기·공백 규칙을 대부분 warning으로 낮춥니다. 3-1 파일을 `-d relaxed`로 검사하면 중복 키와 문법 오류만 error로 남습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 예외 처리

```yaml
# 이 줄만 특정 규칙 끄기
url: https://example.com/very/long/path  # yamllint disable-line rule:line-length

# 다음 줄 끄기
# yamllint disable-line rule:truthy
on: push

# 구간 끄기
# yamllint disable rule:indentation
legacy:
     key: value
# yamllint enable rule:indentation
```

파일 전체를 끄려면 파일 맨 위에 `# yamllint disable-file`을 둡니다. 예외 옆에는 이유를 짧게 적습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 종료 코드와 출력 형식

| 상황                         | 종료 코드 |
|------------------------------|-----------|
| 문제 없음                    | 0         |
| warning만 있음               | 0         |
| warning만 있음, `-s`(strict) | 2         |
| error 있음                   | 1         |

CI에서 warning까지 막으려면 `yamllint -s .`를 씁니다.

| 옵션            | 출력                                                     |
|-----------------|----------------------------------------------------------|
| (기본)          | 사람이 읽기 좋은 표 형식 (터미널이면 색상)               |
| `-f parsable`   | `파일:행:열: [등급] 설명 (규칙)` 한 줄 형식, grep에 편함 |
| `-f github`     | GitHub Actions 주석 형식 (PR 화면에 표시)                |
| `--no-warnings` | error만 출력                                             |

[⬆ 목차로 돌아가기](#목차)

---

## 8. ansible-lint와 함께 쓰기

ansible-lint는 내부에서 yamllint를 실행하고 결과를 `yaml[규칙]`으로 보여 줍니다. 프로젝트에 `.yamllint`가 있으면 그것을 쓰는데, 아래 값과 다르면 ansible-lint가 실행을 거부합니다.

| 항목                                 | 필요한 값 |
|--------------------------------------|-----------|
| `comments.min-spaces-from-content`   | 1         |
| `braces.min-spaces-inside`           | 0         |
| `braces.max-spaces-inside`           | 1         |
| `octal-values.forbid-implicit-octal` | true      |
| `octal-values.forbid-explicit-octal` | true      |

두 도구가 같은 결과를 내도록 하는 `.yamllint` (ansible-lint 기본 설정과 같음):

```yaml
extends: default
rules:
  comments:
    min-spaces-from-content: 1
  comments-indentation: false
  document-start: disable
  line-length:
    max: 160
  braces:
    min-spaces-inside: 0
    max-spaces-inside: 1
  octal-values:
    forbid-implicit-octal: true
    forbid-explicit-octal: true
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. CI 연결

### 9-1. GitHub Actions

```yaml
# .github/workflows/yamllint.yml
name: yamllint
on:
  pull_request:
  push:
    branches: [main]
jobs:
  yamllint:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: pip install yamllint==1.38.0
      - run: yamllint -s -f github .
```

### 9-2. pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.38.0
    hooks:
      - id: yamllint
        args: [--strict]
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. 검증

| 순서 | 확인 내용      | 명령                                | 기대 결과                               |
|------|----------------|-------------------------------------|-----------------------------------------|
| 1    | 설치           | `yamllint --version`                | 판 번호                                 |
| 2    | 검사 대상      | `yamllint --list-files .`           | 의도한 파일만 (가상환경·외부 파일 제외) |
| 3    | 위반 검출      | 3-1 파일에 `yamllint bad.yml`       | 위반 목록, 종료 코드 1                  |
| 4    | 수정 후 통과   | 3-3 파일에 `yamllint good.yml`      | 출력 없음, 종료 코드 0                  |
| 5    | 설정 파일 적용 | `.yamllint` 변경 뒤 같은 파일 검사  | 바뀐 규칙대로 결과가 달라짐             |
| 6    | strict         | warning만 있는 파일에 `yamllint -s` | 종료 코드 2                             |
| 7    | CI             | PR을 올려 workflow 확인             | 위반이 있으면 실패, 없으면 성공         |

[⬆ 목차로 돌아가기](#목차)

---

## 11. 트러블슈팅

| 증상                                                        | 원인                                       | 해결 방법                                       |
|-------------------------------------------------------------|--------------------------------------------|-------------------------------------------------|
| GitHub Actions 파일의 `on:`이 `truthy` 경고                 | YAML 1.1에서 `on`이 참·거짓 값으로 읽힘    | `truthy.check-keys: false`                      |
| `.venv`·내려받은 collection까지 검사함                      | 제외 설정 없음                             | `ignore:`에 경로 추가, `--list-files`로 확인    |
| ansible-lint가 `incompatible custom yamllint configuration` | `.yamllint` 값이 8절 표와 다름             | 8절 값으로 맞춤                                 |
| Helm chart 템플릿에서 `syntax error`                        | `{{ }}`가 들어간 템플릿은 순수 YAML이 아님 | `ignore:`에 `templates/` 추가, `helm lint` 사용 |
| 로컬은 통과, CI는 실패                                      | yamllint 판이나 설정 파일 위치가 다름      | 판 고정, 저장소 루트에서 실행                   |
| warning이 있는데 CI가 통과                                  | 기본은 warning이 종료 코드 0               | `-s`(strict) 사용                               |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [YAML 문법](./yaml_syntax.md) — 들여쓰기, 따옴표, 여러 줄 문자열, 앵커
- [ansible-lint](./ansible_lint.md) — Ansible 규칙 검사 (내부에서 yamllint 사용)
- [Ansible 기초 가이드](./ansible_basic_guide.md) — playbook 작성
- [Docker Compose](../containers/docker_compose.md) — compose.yaml
- [GitHub Actions](../cicd/github_actions.md) — workflow 작성

---

## 참고 자료

- yamllint Documentation: [Quickstart](https://yamllint.readthedocs.io/en/stable/quickstart.html) — ★★★☆☆
- yamllint Documentation: [Configuration](https://yamllint.readthedocs.io/en/stable/configuration.html) — ★★★☆☆
- yamllint Documentation: [Rules](https://yamllint.readthedocs.io/en/stable/rules.html) — ★★★☆☆
- yamllint Documentation: [Disable with comments](https://yamllint.readthedocs.io/en/stable/disable_with_comments.html) — ★★★☆☆
- ansible-lint Documentation: [yaml rule — Yamllint configuration](https://docs.ansible.com/projects/lint/rules/yaml/) — ★★★☆☆
- PyPI: [yamllint](https://pypi.org/project/yamllint/) — 1.38.0 확인 2026-11-23 — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.

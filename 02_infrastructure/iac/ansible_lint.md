# ansible-lint

Ansible playbook·role·collection의 문법 오류, 권장 방식 위반, 멱등성을 해치는 작성법을 실행 전에 찾아 주는 검사 도구입니다. 이 문서만으로 설치 → 첫 검사 → 고치기 → CI 연결까지 따라 할 수 있게 썼습니다. Ansible 자체의 사용법은 [함께 보기](#함께-보기)의 문서에서 다룹니다.

- 기준 판: ansible-lint v26.11.0(2026-11-05 release), Python 3.10 이상(PyPI 기준)
- 예제 시험: 2026-11-23, ansible-lint 26.11.0과 ansible-core 2.22.0을 가상환경에 설치해 3·7·8절 예제를 실행하고 출력을 확인. 그 밖의 설정은 공식 문서 원본(ansible/ansible-lint `docs/`)과 대조

## 목차

| 섹션                                                                                                 |
|------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. 첫 검사](#3-첫-검사)                                   |
| [4. profile](#4-profile) / [5. 자주 만나는 규칙](#5-자주-만나는-규칙) / [6. 설정 파일](#6-설정-파일) |
| [7. 예외 처리](#7-예외-처리) / [8. 자동 수정](#8-자동-수정) / [9. CI 연결](#9-ci-연결)               |
| [10. 검증](#10-검증) / [11. 트러블슈팅](#11-트러블슈팅) / [함께 보기](#함께-보기)                    |

---

## 1. 개요

| 항목        | 내용                                                                                   |
|-------------|----------------------------------------------------------------------------------------|
| 검사 대상   | playbook, role, collection, `requirements.yml`, 인벤토리 등 Ansible 관련 YAML          |
| 하는 일     | `ansible-playbook --syntax-check`, YAML 형식 검사, 권장 규칙 검사를 한 번에 실행       |
| 결과        | 규칙 위반마다 `파일:행: 규칙[세부]: 설명`을 출력하고, 위반이 있으면 종료 코드 0이 아님 |
| 엄격도 조절 | profile 6단계(`min` → `production`)로 점점 엄격하게 적용                               |
| 지원 OS     | Linux, macOS. Windows에는 직접 설치를 지원하지 않음(WSL·컨테이너·CI 사용)              |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

### 2-1. pip (가상환경 권장)

```bash
python3 -m venv ~/.venvs/ansible
~/.venvs/ansible/bin/pip install --upgrade pip
~/.venvs/ansible/bin/pip install ansible-lint     # ansible-core가 없으면 함께 설치됨
export PATH="$HOME/.venvs/ansible/bin:$PATH"
```

Ansible을 이미 가상환경에 설치했다면 같은 가상환경에 넣습니다. 다른 환경에 설치하면 ansible-lint가 다른 판의 ansible-core로 문법 검사를 해서 결과가 달라질 수 있습니다.

### 2-2. pipx (명령만 따로 격리)

```bash
pipx install ansible-lint
```

### 2-3. 배포판 패키지

```bash
sudo dnf install ansible-lint      # Fedora. RHEL은 Ansible Automation Platform 구독 필요
```

### 2-4. 설치 확인

```bash
ansible-lint --version
# ansible-lint 26.11.0 using ansible-core:2.22.0 ...
```

출력에 함께 쓰는 ansible-core 판이 나옵니다. 운영에서 쓰는 판과 같은지 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 첫 검사

### 3-1. 일부러 규칙을 어긴 playbook

`site.yml`

```yaml
- hosts: all
  tasks:
    - name: install nginx
      apt:
        name: nginx
        state: latest
    - shell: systemctl restart nginx
```

### 3-2. 실행

```bash
ansible-lint site.yml          # 파일 지정
ansible-lint                   # 현재 디렉터리 전체 (Git 저장소면 추적 파일 기준)
```

검출되는 위반:

| 위반 위치       | 규칙                        | 뜻                                                                   |
|-----------------|-----------------------------|----------------------------------------------------------------------|
| play 첫 줄      | `name[play]`                | play에 이름이 없음                                                   |
| `install nginx` | `name[casing]`              | 이름이 대문자로 시작하지 않음                                        |
| `apt`           | `fqcn[action-core]`         | `ansible.builtin.apt`처럼 전체 이름을 쓰지 않음                      |
| `state: latest` | `package-latest`            | 실행할 때마다 판이 바뀔 수 있음                                      |
| `shell` task    | `name[missing]`             | task에 이름이 없음                                                   |
| `shell` task    | `command-instead-of-module` | `systemctl` 대신 `ansible.builtin.systemd`(또는 `service`) 모듈 사용 |
| `shell` task    | `command-instead-of-shell`  | 셸 기능이 필요 없으면 `command` 모듈 사용                            |
| `shell` task    | `no-changed-when`           | 항상 changed로 보고됨                                                |

이 playbook을 검사하면 위반 9건(`fqcn[action-core]` 2건 포함)과 `Failed: 9 failure(s), 0 warning(s) ... Last profile that met the validation criteria was 'min'.`이 나오고 종료 코드는 2입니다.

### 3-3. 고친 playbook

```yaml
- name: Configure web server
  hosts: all
  tasks:
    - name: Install nginx
      ansible.builtin.apt:
        name: nginx
        state: present
      notify: Restart nginx

  handlers:
    - name: Restart nginx
      ansible.builtin.service:
        name: nginx
        state: restarted
```

다시 실행하면 `Passed: 0 failure(s), 0 warning(s) ... Last profile that met the validation criteria was 'production'.`이 나오고 종료 코드는 0입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. profile

profile은 뒤로 갈수록 앞 단계를 포함하며 엄격해집니다. 처음에는 낮은 단계부터 통과시키고 단계를 올립니다.

| profile      | 목적                                 | 대표 규칙                                                                                  |
|--------------|--------------------------------------|--------------------------------------------------------------------------------------------|
| `min`        | Ansible이 읽을 수 있는지             | `syntax-check`, `parser-error`, `load-failure`                                             |
| `basic`      | 흔한 실수와 기본 형식                | `yaml`, `name`, `var-naming`, `key-order`, `no-tabs`, `jinja`, `command-instead-of-module` |
| `moderate`   | 읽기 쉬운 작성                       | `name[casing]`, `name[template]`                                                           |
| `safety`     | 결과가 달라지거나 보안에 위험한 호출 | `package-latest`, `risky-file-permissions`, `risky-shell-pipe`                             |
| `shared`     | 공유·배포용 role·collection          | `no-changed-when`, `ignore-errors`, `no-handler`, `galaxy`                                 |
| `production` | 인증 콘텐츠 수준 (CI 권장)           | `fqcn` 등                                                                                  |

```bash
ansible-lint --list-profiles          # profile과 규칙 목록
ansible-lint --profile=basic          # 이 단계까지만 검사
```

profile을 지정하지 않고 실행하면 끝에 통과한 가장 높은 profile을 알려 줍니다(`Last profile that met the validation criteria was '...'`).

[⬆ 목차로 돌아가기](#목차)

---

## 5. 자주 만나는 규칙

| 규칙                        | 원인                                   | 고치는 방법                               |
|-----------------------------|----------------------------------------|-------------------------------------------|
| `fqcn`                      | `copy`처럼 짧은 모듈 이름              | `ansible.builtin.copy`                    |
| `name[missing]`             | task·play 이름 없음                    | 모든 task·play에 `name:`                  |
| `name[casing]`              | 이름이 소문자로 시작                   | `Install nginx`처럼 대문자로 시작         |
| `no-changed-when`           | `command`·`shell`·`raw`가 항상 changed | `changed_when` 지정 (아래 예)             |
| `command-instead-of-module` | 모듈이 있는 일을 명령으로 실행         | `service`, `file`, `get_url` 등 전용 모듈 |
| `package-latest`            | 패키지 `state: latest`                 | `state: present`, 판 고정                 |
| `risky-file-permissions`    | `copy`·`template`에 `mode` 없음        | `mode: "0644"`처럼 따옴표로 지정          |
| `ignore-errors`             | `ignore_errors: true`                  | `failed_when`으로 실패 조건을 명시        |
| `yaml[line-length]`         | 한 줄 160자 초과                       | 변수로 나누거나 여러 줄 문자열            |
| `yaml[truthy]`              | `yes`·`no`·`True`                      | `true`·`false`                            |
| `jinja[spacing]`            | `{{var}}`처럼 공백 없음                | `{{ var }}`                               |
| `var-naming`                | 대문자·하이픈이 들어간 변수 이름       | 소문자와 밑줄 (`http_port`)               |

`changed_when` 작성 예:

```yaml
- name: Show kernel version          # 조회만 하는 명령은 항상 ok
  ansible.builtin.command: uname -r
  register: kernel
  changed_when: false

- name: Install package if missing   # 출력으로 변경 여부 판단
  ansible.builtin.shell: |
    rpm -q nginx || { dnf install -y nginx && echo INSTALLED; }
  register: result
  changed_when: "'INSTALLED' in result.stdout"
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 설정 파일

프로젝트 루트(보통 Git 저장소 루트)에 `.ansible-lint` 또는 `.config/ansible-lint.yml`을 둡니다. 명령줄 옵션의 단일 값은 설정 파일보다 우선하고, `skip_list`·`warn_list`·`exclude_paths` 같은 목록은 합쳐집니다.

```yaml
# .ansible-lint
profile: moderate            # 기본 profile

exclude_paths:
  - .cache/
  - collections/             # 내려받은 외부 collection

warn_list:                   # 실패 대신 경고로만
  - experimental

skip_list:                   # 완전히 건너뜀 (사유를 주석으로)
  - yaml[line-length]        # 긴 URL을 줄일 수 없음

enable_list:                 # 기본으로 꺼진 선택 규칙 켜기
  - no-same-owner
```

`skip_list`는 저장소 전체에 적용되므로 최소로 둡니다. 파일 하나나 한 줄만 예외로 할 때는 7절 방법을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 예외 처리

| 범위      | 방법                                         | 예                                        |
|-----------|----------------------------------------------|-------------------------------------------|
| 한 줄     | 줄 끝에 `# noqa: 규칙`                       | `dest: "{{dest}}" # noqa: jinja[spacing]` |
| 파일 단위 | `.ansible-lint-ignore`에 `파일 규칙`         | `site.yml package-latest`                 |
| 전체      | `.ansible-lint`의 `skip_list` 또는 `-x 규칙` | `skip_list: [yaml[line-length]]`          |

```text
# .ansible-lint-ignore — 설정 파일과 같은 디렉터리
site.yml package-latest            # 경고로 표시됨
legacy.yml no-changed-when skip    # skip을 붙이면 경고도 없음
```

- 이미 위반이 많은 저장소에 처음 도입할 때는 `ansible-lint --generate-ignore`로 현재 위반을 `.ansible-lint-ignore`에 모아 두고, 새 위반만 막은 뒤 목록을 줄여 갑니다. 이 명령은 기존 파일 내용을 덮어씁니다.
- `# noqa` 옆에는 왜 예외인지 짧게 적습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 자동 수정

```bash
git status                      # 먼저 커밋되지 않은 변경이 없는지 확인
ansible-lint --fix              # 지원하는 규칙을 고치고 YAML 형식을 다시 씀
git diff                        # 바뀐 내용을 검토
```

- `--fix`는 지원하는 규칙만 고칩니다. 3-1 playbook에 쓰면 `name[casing]`(이름 첫 글자), `fqcn`(`ansible.builtin.apt`), `command-instead-of-shell`(`shell` → `ansible.builtin.command`)을 고치고 파일 맨 앞에 `---`를 더했습니다. `package-latest`, `name[missing]`처럼 판단이 필요한 위반은 그대로 남습니다.
- YAML 재서식(들여쓰기, 따옴표)은 `--fix`를 쓰면 항상 실행됩니다. 서식을 그대로 두어야 하면 `--fix`를 쓰지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. CI 연결

### 9-1. GitHub Actions

```yaml
# .github/workflows/ansible-lint.yml
name: ansible-lint
on:
  pull_request:
  push:
    branches: [main]
jobs:
  lint:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - name: Run ansible-lint
        uses: ansible/ansible-lint@v26.11.0   # 판을 고정
```

공식 예시는 `@main`을 쓰지만, 검사 결과가 예고 없이 바뀌지 않도록 release tag로 고정하는 편이 안전합니다.

### 9-2. pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/ansible/ansible-lint
    rev: v26.11.0
    hooks:
      - id: ansible-lint
```

### 9-3. 출력 형식

| 옵션             | 용도                                            |
|------------------|-------------------------------------------------|
| `-f pep8`        | 한 줄에 한 위반, 사람이 읽기 좋음               |
| `-f sarif`       | GitHub code scanning 등에 올릴 때               |
| `-f codeclimate` | GitLab 코드 품질 보고서                         |
| `-q`             | 요약만 줄여서 출력                              |
| `--offline`      | collection 내려받기 없이 실행 (CI 캐시 없을 때) |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 검증

| 순서 | 확인 내용      | 명령                                        | 기대 결과                                                       |
|------|----------------|---------------------------------------------|-----------------------------------------------------------------|
| 1    | 설치와 core 판 | `ansible-lint --version`                    | ansible-lint 판과 함께 쓰는 ansible-core 판                     |
| 2    | 프로젝트 루트  | `ansible-lint -v`                           | `Identified ... as project root` 줄의 경로가 의도한 저장소 루트 |
| 3    | 위반 검출      | 3-1 playbook에 `ansible-lint site.yml`      | 위반 목록과 `Failed: N failure(s)`, 종료 코드 2                 |
| 4    | 수정 후 통과   | 3-3 playbook에 `ansible-lint site.yml`      | `Passed`, 종료 코드 0                                           |
| 5    | 목표 profile   | `ansible-lint --profile=production`         | 종료 코드 0                                                     |
| 6    | 예외 최소      | `.ansible-lint`·`.ansible-lint-ignore` 검토 | 예외마다 사유 주석이 있음                                       |
| 7    | CI             | PR을 올려 workflow 확인                     | 위반이 있으면 실패, 없으면 성공                                 |

3번에서 실패하지 않으면 검사 대상이 빠졌거나(`exclude_paths`), 규칙이 꺼진 것(`skip_list`)입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 11. 트러블슈팅

| 증상                             | 원인                                | 해결 방법                                               |
|----------------------------------|-------------------------------------|---------------------------------------------------------|
| `couldn't resolve module/action` | 필요한 collection이 설치되지 않음   | `ansible-galaxy collection install -r requirements.yml` |
| 로컬은 통과, CI는 실패           | ansible-lint·ansible-core 판이 다름 | 두 곳의 `--version` 비교, CI의 판 고정                  |
| 의도하지 않은 파일까지 검사      | 프로젝트 루트 판단이 다름           | `exclude_paths` 지정, 저장소 루트에서 실행              |
| `--fix` 뒤 diff가 너무 큼        | YAML 재서식이 함께 실행됨           | 서식 변경만 따로 commit, 또는 `--fix` 미사용            |
| vault 파일에서 `load-failure`    | 복호화할 비밀번호를 모름            | 비밀번호 파일 설정 또는 해당 파일 `exclude_paths`       |
| Windows에서 설치 실패            | 직접 설치 미지원                    | WSL, 컨테이너, CI에서 실행                              |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Ansible 기초 가이드](./ansible_basic_guide.md) — 설치, 인벤토리, playbook, 검증
- [Jinja2](./jinja2.md) — `jinja[spacing]` 등 템플릿 식 작성
- [Molecule](./molecule.md) — role을 실제로 실행해 시험
- [YAML 문법](./yaml_syntax.md) — 들여쓰기, truthy 값
- [GitHub Actions](../cicd/github_actions.md) — workflow 작성

---

## 참고 자료

- ansible-lint Documentation: [Installing](https://docs.ansible.com/projects/lint/installing/) — ★★★☆☆
- ansible-lint Documentation: [Usage](https://docs.ansible.com/projects/lint/usage/) — ★★★☆☆
- ansible-lint Documentation: [Configuration](https://docs.ansible.com/projects/lint/configuring/) — ★★★☆☆
- ansible-lint Documentation: [Profiles](https://docs.ansible.com/projects/lint/profiles/) — ★★★☆☆
- ansible-lint Documentation: [Autofix](https://docs.ansible.com/projects/lint/autofix/) — ★★★☆☆
- GitHub: [ansible/ansible-lint releases](https://github.com/ansible/ansible-lint/releases) — v26.11.0 확인 2026-11-23 — ★★★☆☆

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

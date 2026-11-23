# Jinja2

변수·조건·반복을 넣은 틀(템플릿)에 값을 채워 텍스트를 만드는 Python 템플릿 엔진입니다. Ansible의 `{{ 변수 }}`와 `template` 모듈이 Jinja2로 동작합니다. 이 문서만으로 설치 → 문법 → 렌더링 → 검증까지 따라 할 수 있게 썼고, 예제는 Ansible에서 설정 파일을 만드는 경우를 중심으로 합니다.

- 기준 판: Jinja2 3.1.6(PyPI 기준, Python 3.7 이상)
- 예제 시험: 2026-11-23, Jinja2 3.1.6과 ansible-core 2.20.5에서 4·6·9절 예제를 렌더링하고 출력을 확인

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. 기본 문법](#3-기본-문법)                                 |
| [4. 조건과 반복](#4-조건과-반복) / [5. 필터와 테스트](#5-필터와-테스트) / [6. 공백 제어](#6-공백-제어) |
| [7. 재사용](#7-재사용) / [8. Ansible에서 쓰기](#8-ansible에서-쓰기) / [9. 검증](#9-검증)               |
| [10. 트러블슈팅](#10-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                   |

---

## 1. 개요

| 항목        | 내용                                                            |
|-------------|-----------------------------------------------------------------|
| 무엇을 하나 | 템플릿 + 변수 → 완성된 텍스트 (설정 파일, HTML, 메시지 등)      |
| 파일 확장자 | 관례상 `.j2` (`nginx.conf.j2`)                                  |
| 쓰이는 곳   | Ansible(`template` 모듈, 변수 식), Flask, Salt, dbt 등          |
| 실행 위치   | Ansible에서는 제어 노드에서 렌더링한 뒤 결과만 대상 서버로 보냄 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

```bash
python3 -m venv ~/.venvs/jinja
~/.venvs/jinja/bin/pip install Jinja2 PyYAML      # PyYAML은 아래 예제에서 변수 파일을 읽을 때만 필요
~/.venvs/jinja/bin/python -c 'import jinja2; print(jinja2.__version__)'
# 3.1.6
```

ansible-core를 설치하면 Jinja2가 함께 설치되므로 Ansible 사용자는 따로 설치할 필요가 없습니다. 이때 Ansible이 쓰는 판은 `ansible --version`의 `jinja version` 줄에서 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 기본 문법

| 구분   | 표기         | 예                                   |
|--------|--------------|--------------------------------------|
| 출력   | `{{ 식 }}`   | `{{ http_port }}`, `{{ user.name }}` |
| 제어문 | `{% 문 %}`   | `{% if %}`, `{% for %}`, `{% set %}` |
| 주석   | `{# 내용 #}` | 렌더링 결과에 남지 않음              |

```jinja
{# 변수와 속성 #}
{{ name }}               {# 문자열·숫자 변수 #}
{{ user.name }}          {# 속성 (user['name']과 같음) #}
{{ ports[0] }}           {# 목록 첫 항목 #}

{# 연산 #}
{{ 10 // 3 }}            {# 정수 나눗셈 → 3 #}
{{ "web-" ~ id }}        {# ~ 는 문자열 이어 붙이기 #}
{{ port if port else 80 }}

{# 변수 정의 #}
{% set base_dir = "/opt/app" %}
{{ base_dir }}/logs
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 조건과 반복

### 4-1. 예제 템플릿

`templates/nginx.conf.j2`

```jinja
# {{ ansible_managed | default('managed by template') }}
worker_processes {{ workers | default('auto') }};

http {
{% for site in sites %}
    server {
        listen {{ site.port | default(80) }};
        server_name {{ site.name | lower }};
{% if site.tls | default(false) %}
        ssl_certificate /etc/ssl/{{ site.name }}.crt;
{% endif %}
    }
{% endfor %}
}
```

`vars.yml`

```yaml
sites:
  - name: WWW.example.com
    port: 8080
  - name: api.example.com
    tls: true
```

렌더링 결과 (`trim_blocks` 켬, 6절):

```nginx
# managed by template
worker_processes auto;

http {
    server {
        listen 8080;
        server_name www.example.com;
    }
    server {
        listen 80;
        server_name api.example.com;
        ssl_certificate /etc/ssl/api.example.com.crt;
    }
}
```

### 4-2. 조건문

```jinja
{% if env == "production" %}
log_level = warn
{% elif env == "staging" %}
log_level = info
{% else %}
log_level = debug
{% endif %}
```

### 4-3. 반복문의 `loop` 변수

| 변수          | 뜻              |
|---------------|-----------------|
| `loop.index`  | 1부터 세는 순번 |
| `loop.index0` | 0부터 세는 순번 |
| `loop.first`  | 첫 번째면 true  |
| `loop.last`   | 마지막이면 true |
| `loop.length` | 전체 개수       |

```jinja
{% for host in backends %}
server {{ host }}:8080{{ "," if not loop.last }}
{% else %}
# backends가 비어 있음
{% endfor %}
```

`{% else %}`는 목록이 비었을 때만 실행됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 필터와 테스트

### 5-1. 필터 `값 | 필터`

| 필터                         | 예                                           | 결과                   |
|------------------------------|----------------------------------------------|------------------------|
| `default(값)`                | `{{ port \| default(80) }}`                  | 변수가 없으면 80       |
| `lower` / `upper`            | `{{ "Web" \| lower }}`                       | `web`                  |
| `replace(a, b)`              | `{{ "a-b" \| replace("-", "_") }}`           | `a_b`                  |
| `join(구분자)`               | `{{ [1,2,3] \| join(",") }}`                 | `1,2,3`                |
| `sort` / `unique`            | `{{ [3,1,2] \| sort \| join(",") }}`         | `1,2,3`                |
| `length`                     | `{{ users \| length }}`                      | 항목 수                |
| `map(attribute=키)`          | `{{ users \| map(attribute="n") \| list }}`  | `['a', 'b']`           |
| `selectattr(키, 테스트, 값)` | `{{ users \| selectattr("admin") \| list }}` | 조건 맞는 항목         |
| `int` / `float` / `string`   | `{{ "8080" \| int }}`                        | 숫자로 바꿈            |
| `indent(n)`                  | `{{ block \| indent(4) }}`                   | 둘째 줄부터 4칸 들여씀 |

Ansible은 여기에 `to_yaml`, `to_json`, `regex_replace`, `b64encode` 같은 필터를 더합니다(8절). IP 주소를 다루는 `ipaddr` 계열은 별도 collection `ansible.utils`에 있습니다.

### 5-2. 테스트 `값 is 테스트`

| 테스트    | 예                              |
|-----------|---------------------------------|
| `defined` | `{% if db_host is defined %}`   |
| `none`    | `{% if value is none %}`        |
| `string`  | `{{ "x" is string }}` → `True`  |
| `number`  | `{% if port is number %}`       |
| `in`      | `{% if "web" in group_names %}` |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 공백 제어

제어문(`{% %}`)이 있던 줄은 그대로 두면 빈 줄로 남습니다.

| 설정·표기       | 동작                                             |
|-----------------|--------------------------------------------------|
| `trim_blocks`   | 제어문 뒤 줄바꿈 하나를 지움                     |
| `lstrip_blocks` | 제어문 앞의 공백·탭을 지움                       |
| `{%-` / `-%}`   | 그 쪽의 공백과 줄바꿈을 모두 지움 (한 곳만 적용) |

```python
import jinja2
src = "a\n{% if x %}\nb\n{% endif %}\nc"
print(repr(jinja2.Template(src).render(x=1)))                    # 'a\n\nb\n\nc'
print(repr(jinja2.Template(src, trim_blocks=True).render(x=1)))  # 'a\nb\nc'
```

Jinja2 자체의 기본값은 둘 다 꺼짐입니다. Ansible `template` 모듈은 `trim_blocks`를 기본으로 켜고 `lstrip_blocks`는 끕니다. 그래서 4-1 템플릿은 Ansible에서 빈 줄 없이 렌더링됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 재사용

### 7-1. include

```jinja
{% include "common/header.j2" %}
```

### 7-2. macro (함수처럼 쓰는 조각)

```jinja
{% macro upstream(name, hosts, port=8080) %}
upstream {{ name }} {
{% for h in hosts %}
    server {{ h }}:{{ port }};
{% endfor %}
}
{% endmacro %}

{{ upstream("api", ["10.0.0.11", "10.0.0.12"]) }}
```

### 7-3. 상속 (extends / block)

```jinja
{# base.j2 #}
[global]
{% block body %}{% endblock %}

{# app.j2 #}
{% extends "base.j2" %}
{% block body %}
name = app
{% endblock %}
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. Ansible에서 쓰기

### 8-1. template 모듈

```yaml
- name: Render nginx config
  ansible.builtin.template:
    src: templates/nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    mode: "0644"
    validate: nginx -t -c %s        # 배포 전에 결과 파일 문법 확인
  notify: Restart nginx
```

- `src`는 role 안에서는 `templates/` 기준 상대 경로입니다.
- `validate`를 쓰면 문법이 틀린 설정이 대상 서버에 놓이지 않습니다.
- `ansible_managed` 변수는 "Ansible이 관리하는 파일" 표시 문구로, 4-1처럼 첫 줄 주석에 넣습니다.

### 8-2. YAML 안의 식은 따옴표로 감싸기

값이 `{{`로 시작하면 YAML이 사전(dict)으로 잘못 읽으므로 따옴표로 감쌉니다.

```yaml
dest: "{{ base_dir }}/app.conf"     # 맞음
dest: {{ base_dir }}/app.conf       # YAML 문법 오류
```

### 8-3. `when`에는 `{{ }}`를 쓰지 않기

`when`, `changed_when`, `failed_when`, `until`의 값은 이미 Jinja2 식으로 해석됩니다.

```yaml
when: app_env == "production"           # 맞음
when: "{{ app_env == 'production' }}"   # 경고 대상 (ansible-lint no-jinja-when)
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 검증

| 순서 | 확인 내용          | 명령                                                                              | 기대 결과                            |
|------|--------------------|-----------------------------------------------------------------------------------|--------------------------------------|
| 1    | 설치               | `python -c 'import jinja2; print(jinja2.__version__)'`                            | 판 번호                              |
| 2    | 식 하나 확인       | `ansible localhost -m ansible.builtin.debug -a 'msg="{{ \"Web-01\" \| lower }}"'` | `"msg": "web-01"`                    |
| 3    | 정의되지 않은 변수 | 아래 Python 예처럼 `StrictUndefined`로 렌더링                                     | 빠진 변수 이름과 함께 실패           |
| 4    | 파일 렌더링 결과   | 아래 Python 예, 또는 8-1 task에 `--check --diff`                                  | 의도한 결과 텍스트, diff로 차이 표시 |
| 5    | 결과 파일 문법     | `validate:` 또는 대상 프로그램의 검사 명령 (`nginx -t`)                           | 문법 오류 없음                       |
| 6    | 멱등성             | 같은 playbook을 한 번 더 실행                                                     | `changed=0`                          |

Python으로 미리 렌더링해 보는 방법 (4-1의 `templates/`, `vars.yml` 기준):

```python
import jinja2, yaml
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
    trim_blocks=True,                    # Ansible template 모듈과 같게
    undefined=jinja2.StrictUndefined,    # 빠진 변수는 오류로
)
print(env.get_template("nginx.conf.j2").render(**yaml.safe_load(open("vars.yml"))))
```

Ansible로 확인할 때는 대상에 쓰기 전에 `ansible-playbook site.yml --check --diff`로 바뀔 내용을 봅니다. 첫 실행에서 `changed=1`, 같은 내용으로 다시 실행하면 `changed=0`이 정상입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 트러블슈팅

| 증상                                          | 원인                                | 해결 방법                                        |
|-----------------------------------------------|-------------------------------------|--------------------------------------------------|
| `'변수' is undefined`                         | 변수 이름 오타, 정의 안 됨          | 이름 확인, `default()` 필터, `is defined` 조건   |
| YAML `found unacceptable key` 등 문법 오류    | `{{`로 시작하는 값을 따옴표 없이 씀 | 값 전체를 따옴표로 감쌈 (8-2)                    |
| 결과 파일에 빈 줄이 많음                      | 제어문 줄이 남음                    | `trim_blocks`·`lstrip_blocks`, `{%-`·`-%}` (6절) |
| 들여쓰기가 틀어짐                             | 여러 줄 값을 그대로 넣음            | `indent(n)` 필터                                 |
| 숫자 비교가 이상함 (`"10" < "9"`)             | 문자열끼리 비교                     | `int` 필터로 바꾼 뒤 비교                        |
| `{{ }}`를 그대로 출력하고 싶음                | Jinja2가 해석함                     | `{% raw %} ... {% endraw %}`                     |
| ad-hoc `debug`에서 `must resolve to a 'dict'` | `-a` 값의 공백 때문에 인자가 나뉨   | `-a 'msg="{{ 식 }}"'`처럼 안쪽을 따옴표로 감쌈   |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Ansible 기초 가이드](./ansible_basic_guide.md) — playbook, 변수 우선순위, role
- [ansible-lint](./ansible_lint.md) — `jinja[spacing]`, `no-jinja-when` 규칙
- [YAML 문법](./yaml_syntax.md) — 따옴표, 여러 줄 문자열
- [Ansible Playbook 필드](./ansible_playbook_fields.md) — `when`, `loop` 등 키

---

## 참고 자료

- Jinja Documentation: [Template Designer Documentation](https://jinja.palletsprojects.com/en/stable/templates/) — ★★★☆☆
- Jinja Documentation: [API — Environment, Undefined](https://jinja.palletsprojects.com/en/stable/api/) — ★★★☆☆
- Ansible Documentation: [Templating (Jinja2)](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_templating.html) — ★★★☆☆
- Ansible Documentation: [ansible.builtin.template module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/template_module.html) — ★★★☆☆
- PyPI: [Jinja2](https://pypi.org/project/Jinja2/) — 3.1.6 확인 2026-11-23 — ★★★☆☆

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

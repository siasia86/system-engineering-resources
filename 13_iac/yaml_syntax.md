# YAML 문법 가이드

Ansible, Docker Compose, Kubernetes 등 IaC 도구에서 공통으로 사용하는 YAML 문법 정리입니다.

## 목차

| 섹션 |
|------|
| [1. 기본 규칙](#1-기본-규칙) / [2. 데이터 타입](#2-데이터-타입) / [3. 블록 스칼라](#3-블록-스칼라) |
| [4. 리스트와 맵](#4-리스트와-맵) / [5. 앵커와 별칭](#5-앵커와-별칭) / [6. 주의사항](#6-주의사항) |
| [7. Infra 실전 패턴](#7-infra-실전-패턴) |

---

## 1. 기본 규칙

- 들여쓰기: **공백만 허용** (탭 금지)
- 들여쓰기 단위: 2칸 권장
- 대소문자 구분
- `---`: 문서 시작 (여러 문서 구분)
- `#`: 주석

```yaml
---
# 이것은 주석입니다
key: value
nested:
  child: value
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 데이터 타입

### 문자열

```yaml
# 따옴표 없이 (대부분 가능)
name: hello world

# 작은따옴표 (이스케이프 없음, 그대로 출력)
path: '/etc/nginx/nginx.conf'

# 큰따옴표 (이스케이프 처리: \n, \t 등)
msg: "줄바꿈은\n여기서"

# 콜론/특수문자 포함 시 따옴표 필수
url: "http://example.com:8080"
```

### 숫자

```yaml
integer: 42
float: 3.14
hex: 0xFF
octal: 0o777     # YAML 1.2
scientific: 1.0e+3
```

### Boolean

```yaml
# true/false (소문자 권장)
enabled: true
debug: false

# 아래도 boolean으로 해석됨 — 주의
yes_value: yes    # true
no_value: no      # false
on_value: on      # true
off_value: off    # false
```

### Null

```yaml
empty: null
also_empty: ~
also_null:        # 값 없이 비워도 null
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 블록 스칼라

여러 줄 문자열을 표현하는 방법입니다.

### 기호 조합

```
스타일   줄바꿈 처리     끝 개행
──────   ─────────────   ───────
|        줄바꿈 유지     1개 유지
|-       줄바꿈 유지     제거
|+       줄바꿈 유지     모두 유지
>        공백으로 변환   1개 유지
>-       공백으로 변환   제거
>+       공백으로 변환   모두 유지
```

### Literal (`|`) — 줄바꿈 유지

쉘 스크립트, 설정 파일 등 줄바꿈이 의미 있는 경우 사용합니다.

```yaml
script: |
  #!/bin/bash
  echo "hello"
  echo "world"

# 결과: "#!/bin/bash\necho \"hello\"\necho \"world\"\n"
```

### Folded (`>`) — 줄바꿈을 공백으로

긴 문자열을 여러 줄로 나눌 때 사용합니다.

```yaml
description: >
  이것은 매우 긴 설명입니다.
  여러 줄로 작성하지만
  실제로는 한 줄로 합쳐집니다.

# 결과: "이것은 매우 긴 설명입니다. 여러 줄로 작성하지만 실제로는 한 줄로 합쳐집니다.\n"
```

### Strip (`-`) — 끝 개행 제거

URL, 파일 경로 등 끝에 `\n`이 붙으면 안 되는 경우 사용합니다.

```yaml
url: >-
  https://repo.zabbix.com/zabbix/7.4/
  release/ubuntu/pool/main/z/zabbix-release/
  zabbix-release_latest+ubuntu22.04_all.deb

# 결과: "https://repo.zabbix.com/zabbix/7.4/ release/ubuntu/pool/main/z/..."
```

🟡 `>`는 줄바꿈을 **공백 1칸**으로 변환합니다. URL 중간에 공백이 들어가면 안 되는 경우 `|`를 사용하거나 한 줄로 작성합니다.

### 빈 줄 = 줄바꿈 유지

`>` 모드에서도 빈 줄은 줄바꿈으로 유지됩니다.

```yaml
text: >
  첫 번째 문단입니다.
  이어서 작성합니다.

  두 번째 문단입니다.

# 결과: "첫 번째 문단입니다. 이어서 작성합니다.\n두 번째 문단입니다.\n"
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 리스트와 맵

### 리스트 (블록)

```yaml
packages:
  - nginx
  - curl
  - wget
```

### 리스트 (인라인/Flow)

```yaml
packages: [nginx, curl, wget]
```

### 맵 (블록)

```yaml
server:
  host: 192.0.2.1
  port: 8080
  ssl: true
```

### 맵 (인라인/Flow)

```yaml
server: {host: 192.0.2.1, port: 8080, ssl: true}
```

### 리스트 of 맵

```yaml
users:
  - name: admin
    role: superuser
  - name: deploy
    role: operator
```

### 복합 키

```yaml
# 키에 특수문자 포함
"host:port": "192.0.2.1:8080"

# 복합 키 (? 사용)
? [key1, key2]
: value
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 앵커와 별칭

반복되는 값을 재사용합니다.

### 기본 사용

```yaml
defaults: &defaults
  timeout: 30
  retries: 3
  delay: 5

production:
  <<: *defaults
  timeout: 60

staging:
  <<: *defaults
```

- `&defaults`: 앵커 정의 (이름 부여)
- `*defaults`: 별칭 참조 (값 복사)
- `<<`: 맵 병합 (merge key)

### 실전 예시 (Docker Compose)

```yaml
x-common: &common
  restart: unless-stopped
  logging:
    driver: json-file
    options:
      max-size: "10m"

services:
  web:
    <<: *common
    image: nginx:latest
  api:
    <<: *common
    image: myapp:latest
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 주의사항

### Norway 문제 (YAML 1.1)

YAML 1.1에서 `no`, `yes`, `on`, `off`가 boolean으로 해석됩니다.

```yaml
# ❌ 위험 — 국가 코드가 boolean으로 해석
countries:
  - NO    # false로 해석됨
  - FR
  - DE

# ✅ 안전 — 따옴표 사용
countries:
  - "NO"
  - "FR"
  - "DE"
```

🟡 YAML 1.2 (Python `ruamel.yaml`, Go)에서는 `true`/`false`만 boolean입니다. 그러나 Ansible은 YAML 1.1 기반이므로 주의가 필요합니다.

### 숫자로 해석되는 문자열

```yaml
# ❌ 위험
version: 3.10    # float 3.1로 해석
zipcode: 01onal  # 문자열이지만 01234는 8진수로 해석 가능

# ✅ 안전
version: "3.10"
zipcode: "01234"
```

### 콜론 뒤 공백

```yaml
# ❌ 파싱 오류
key:value

# ✅ 정상
key: value
```

### 탭 금지

```yaml
# ❌ 파싱 오류 (탭 사용)
server:
	port: 8080

# ✅ 정상 (공백 사용)
server:
  port: 8080
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Infra 실전 패턴

### Ansible — 쉘 스크립트

```yaml
- name: SSH 설정
  ansible.builtin.raw: |
    sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
    systemctl restart sshd
  changed_when: false
```

### Ansible — 긴 URL 변수화

```yaml
vars:
  zabbix_repo_url: >-
    https://repo.zabbix.com/zabbix/7.4/release/ubuntu/pool/main/z/
    zabbix-release/zabbix-release_latest+ubuntu22.04_all.deb

tasks:
  - name: Zabbix repo 설치
    ansible.builtin.apt:
      deb: "{{ zabbix_repo_url }}"
```

### Docker Compose — 환경변수

```yaml
services:
  app:
    environment:
      - DB_HOST=192.0.2.1
      - DB_PORT=5432
    # 또는 맵 형태
    environment:
      DB_HOST: 192.0.2.1
      DB_PORT: 5432
```

### Kubernetes — 멀티라인 ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  nginx.conf: |
    server {
        listen 80;
        server_name example.com;
        location / {
            proxy_pass http://backend:8080;
        }
    }
```

### GitHub Actions — 조건문

```yaml
steps:
  - name: Deploy
    if: github.ref == 'refs/heads/main'
    run: |
      echo "Deploying..."
      ./deploy.sh
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- YAML Specification 1.2: [yaml.org/spec](https://yaml.org/spec/1.2.2/) — ★★★★☆
- YAML Multiline: [yaml-multiline.info](https://yaml-multiline.info/) — ★★☆☆☆
- Ansible YAML Syntax: [docs.ansible.com/yaml_syntax](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-26

**마지막 업데이트**: 2026-05-26

© 2026 siasia86. Licensed under CC BY 4.0.

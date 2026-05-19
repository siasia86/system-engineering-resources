# Ansible Vault 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 파일 암호화](#2-파일-암호화) / [3. 문자열 암호화](#3-문자열-암호화) |
| [4. Vault 패스워드 관리](#4-vault-패스워드-관리) / [5. Playbook 연동](#5-playbook-연동) / [6. 실무 패턴](#6-실무-패턴) |

> 공통 필드는 [ansible_playbook_fields.md](ansible_playbook_fields.md) 참고

---

## 1. 개요

Ansible Vault는 패스워드, API 키, 인증서 등 민감한 데이터를 AES-256으로 암호화합니다.
암호화된 파일은 Git에 커밋해도 안전합니다.

| 항목       | 내용                                      |
|------------|-------------------------------------------|
| 암호화     | AES-256-CBC                               |
| 대상       | 파일 전체 또는 변수 값(문자열)            |
| 실행 방법  | `--ask-vault-pass` 또는 `--vault-password-file` |

---

## 2. 파일 암호화

### 파일 생성 및 암호화

```bash
# 새 암호화 파일 생성 (편집기 열림)
ansible-vault create secrets.yml

# 기존 파일 암호화
ansible-vault encrypt secrets.yml

# 복호화 (평문으로 저장)
ansible-vault decrypt secrets.yml

# 암호화 상태로 내용 확인
ansible-vault view secrets.yml

# 암호화 상태로 편집
ansible-vault edit secrets.yml

# 패스워드 변경
ansible-vault rekey secrets.yml
```

### 암호화 파일 예시

```yaml
# secrets.yml (암호화 전 평문)
db_password: SecurePassword123
api_key: SecureKey123
aws_secret: SecureKey123
```

암호화 후 파일 내용:

```text
$ANSIBLE_VAULT;1.1;AES256
66386439653236336462626566653063336164663966303231363934653561363964613
...
```

---

## 3. 문자열 암호화

파일 전체가 아닌 특정 변수 값만 암호화합니다.
`vars` 파일에서 일반 변수와 암호화 변수를 혼용할 수 있습니다.

```bash
# 문자열 암호화 (결과를 복사해서 vars 파일에 붙여넣기)
ansible-vault encrypt_string 'SecurePassword123' --name 'db_password'
```

출력 결과:

```yaml
db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  66386439653236336462626566653063336164663966303231363934653561363964613
  ...
```

이 값을 `vars/main.yml`에 그대로 붙여넣으면 됩니다:

```yaml
# vars/main.yml
app_name: myapp          # 평문
db_host: 192.0.2.10      # 평문
db_password: !vault |    # 암호화된 값
  $ANSIBLE_VAULT;1.1;AES256
  66386439653236336462626566653063336164663966303231363934653561363964613
  ...
```

---

## 4. Vault 패스워드 관리

### 방법 1 — 실행 시 입력 (기본)

```bash
ansible-playbook site.yml --ask-vault-pass
```

### 방법 2 — 패스워드 파일 사용

```bash
# 패스워드 파일 생성
echo 'SecurePassword123' > ~/.vault_pass
chmod 600 ~/.vault_pass

# 실행
ansible-playbook site.yml --vault-password-file ~/.vault_pass
```

`ansible.cfg`에 등록하면 매번 옵션 생략 가능:

```ini
[defaults]
vault_password_file = ~/.vault_pass
```

### 방법 3 — 환경변수

```bash
export ANSIBLE_VAULT_PASSWORD_FILE=~/.vault_pass
ansible-playbook site.yml
```

### 방법 4 — 다중 Vault ID (여러 패스워드 관리)

```bash
# 암호화 시 ID 지정
ansible-vault encrypt secrets_prod.yml --vault-id prod@~/.vault_prod
ansible-vault encrypt secrets_dev.yml  --vault-id dev@~/.vault_dev

# 실행 시 여러 ID 지정
ansible-playbook site.yml \
  --vault-id prod@~/.vault_prod \
  --vault-id dev@~/.vault_dev
```

---

## 5. Playbook 연동

### vars_files로 암호화 파일 로드

```yaml
---
- name: 암호화 변수 사용
  hosts: all
  vars_files:
    - vars/common.yml
    - vars/secrets.yml    # 암호화된 파일
  tasks:
    - name: DB 연결 테스트
      ansible.builtin.debug:
        msg: "DB: {{ db_host }}:{{ db_password }}"
```

### include_vars로 조건부 로드

```yaml
- name: 환경별 시크릿 로드
  ansible.builtin.include_vars:
    file: "vars/secrets_{{ env }}.yml"
```

---

## 6. 실무 패턴

### 디렉토리 구조

```text
project/
├── ansible.cfg
├── inventory/
│   └── production.ini
├── vars/
│   ├── common.yml          # 평문 변수
│   └── secrets.yml         # ansible-vault 암호화
├── playbooks/
│   └── site.yml
└── .vault_pass             # .gitignore에 반드시 추가
```

### .gitignore 필수 항목

```text
.vault_pass
*.vault_pass
secrets_plain.yml
```

### 암호화 대상 기준

| 암호화 필요 | 평문 가능 |
|-------------|-----------|
| DB 패스워드 | 호스트명 |
| API 키/토큰 | 포트 번호 |
| SSH 개인키  | 패키지 이름 |
| 인증서      | 타임존 설정 |
| 클라우드 자격증명 | 로그 경로 |

### CI/CD 환경에서 Vault 사용

```bash
# GitHub Actions 예시
# secrets.VAULT_PASS를 GitHub Secret으로 등록 후:
- name: Run Ansible
  run: |
    echo "${{ secrets.VAULT_PASS }}" > .vault_pass
    ansible-playbook site.yml --vault-password-file .vault_pass
    rm -f .vault_pass
```

---

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Ansible Docs — Vault: [docs.ansible.com](https://docs.ansible.com/ansible/latest/vault_guide/index.html) — ★★★☆☆
- [ansible_playbook_fields.md](ansible_playbook_fields.md)

---

**작성일**: 2026-05-19

**마지막 업데이트**: 2026-05-19

© 2026 siasia86. Licensed under CC BY 4.0.

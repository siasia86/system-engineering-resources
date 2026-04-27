# Ansible Vault

## 목차

| 단계   | 섹션                                                                                                                                    |
|--------|-----------------------------------------------------------------------------------------------------------------------------------------|
| 기본   | [1. 개요](#1-개요) / [2. 파일 암호화](#2-파일-암호화) / [3. 변수 인라인 암호화](#3-변수-인라인-암호화)                                 |
| 실전   | [4. vault-id (멀티 볼트)](#4-vault-id-멀티-볼트) / [5. Playbook 연동](#5-playbook-연동) / [6. CI/CD 연동](#6-cicd-연동)               |
| 운영   | [7. 키 관리](#7-키-관리) / [8. Tips](#8-tips)                                                                                          |

---

## 1. 개요

Ansible Vault는 비밀번호, API 키, 인증서 등 민감 정보를 AES-256으로 암호화하여 SCM에 안전하게 저장합니다.

```
평문 파일 (group_vars/all.yml)
        │
        v  ansible-vault encrypt
암호화 파일 ($ANSIBLE_VAULT;1.1;AES256 ...)
        │
        v  ansible-playbook --ask-vault-pass
복호화 후 실행
```

- 암호화 대상: 파일 전체 또는 변수값 단위
- 복호화: 실행 시 자동 처리 (평문 파일로 저장되지 않음)

[⬆ 목차로 돌아가기](#목차)

---

## 2. 파일 암호화

### 기본 명령어

```bash
# 새 암호화 파일 생성
ansible-vault create secrets.yml

# 기존 파일 암호화
ansible-vault encrypt group_vars/all/vault.yml

# 복호화 (평문으로 저장 — 주의)
ansible-vault decrypt group_vars/all/vault.yml

# 내용 확인 (복호화하지 않고 출력)
ansible-vault view group_vars/all/vault.yml

# 암호화된 파일 편집
ansible-vault edit group_vars/all/vault.yml

# 비밀번호 변경
ansible-vault rekey group_vars/all/vault.yml
```

### 암호화 파일 구조 예시

```yaml
# group_vars/all/vault.yml (암호화 전 평문)
vault_db_password: "super-secret-password"
vault_api_key: "sk-1234567890abcdef"
vault_ssl_cert: |
  -----BEGIN CERTIFICATE-----
  MIIBkTCB+wIJ...
  -----END CERTIFICATE-----
```

```yaml
# group_vars/all/vars.yml (평문, vault 변수 참조)
db_password: "{{ vault_db_password }}"
api_key: "{{ vault_api_key }}"
```

`vault_` 접두사 규칙: 암호화 변수는 `vault_` 접두사를 붙이고, 평문 vars 파일에서 참조하는 패턴이 권장됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 변수 인라인 암호화

파일 전체가 아닌 특정 변수값만 암호화합니다.

```bash
# 값 암호화 (출력을 복사하여 yml에 붙여넣기)
ansible-vault encrypt_string 'super-secret-password' --name 'db_password'
```

출력 예시:

```yaml
db_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          66386439653236336462626566653337386566353532333564613666633866363
          3437623637623632663762623966303664616135623935310a396438623834616
          ...
```

```yaml
# group_vars/webservers.yml 에 직접 삽입
db_host: db.example.com
db_port: 5432
db_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          66386439653236336462626566653337...
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. vault-id (멀티 볼트)

환경별(dev/prod) 또는 용도별로 다른 비밀번호를 사용합니다.

```bash
# vault-id 레이블로 암호화
ansible-vault encrypt_string 'dev-password' --name 'db_password' --vault-id dev@prompt
ansible-vault encrypt_string 'prod-password' --name 'db_password' --vault-id prod@prompt

# 파일 암호화
ansible-vault encrypt group_vars/dev/vault.yml --vault-id dev@prompt
ansible-vault encrypt group_vars/prod/vault.yml --vault-id prod@prompt
```

```bash
# 실행 시 여러 vault-id 지정
ansible-playbook site.yml \
  --vault-id dev@~/.vault_pass_dev \
  --vault-id prod@~/.vault_pass_prod
```

```yaml
# 암호화된 변수에 레이블이 포함됨
db_password: !vault |
          $ANSIBLE_VAULT;1.2;AES256;prod
          ...
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. Playbook 연동

### 비밀번호 입력 방식

```bash
# 실행 시 프롬프트 입력
ansible-playbook site.yml --ask-vault-pass

# 비밀번호 파일 사용
ansible-playbook site.yml --vault-password-file ~/.vault_pass

# 환경변수로 파일 지정
export ANSIBLE_VAULT_PASSWORD_FILE=~/.vault_pass
ansible-playbook site.yml
```

### ansible.cfg 에 등록

```ini
[defaults]
vault_password_file = ~/.vault_pass
```

### 비밀번호 파일 보안

```bash
# 비밀번호 파일 생성
echo 'my-vault-password' > ~/.vault_pass
chmod 600 ~/.vault_pass

# .gitignore 에 반드시 추가
echo '.vault_pass' >> .gitignore
echo '*.vault_pass' >> .gitignore
```

⚠️ `vault_password_file` 경로는 절대경로 또는 `~` 사용. 상대경로는 실행 위치에 따라 달라집니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. CI/CD 연동

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
- name: Deploy
  env:
    ANSIBLE_VAULT_PASSWORD: ${{ secrets.VAULT_PASSWORD }}
  run: |
    echo "$ANSIBLE_VAULT_PASSWORD" > /tmp/.vault_pass
    chmod 600 /tmp/.vault_pass
    ansible-playbook -i inventory/ site.yml \
      --vault-password-file /tmp/.vault_pass
    rm -f /tmp/.vault_pass
```

### Jenkins

```groovy
withCredentials([string(credentialsId: 'ansible-vault-pass', variable: 'VAULT_PASS')]) {
    sh '''
        set +x
        echo "$VAULT_PASS" > /tmp/.vault_pass
        chmod 600 /tmp/.vault_pass
        set -x
        ansible-playbook -i inventory/ site.yml \
          --vault-password-file /tmp/.vault_pass
        rm -f /tmp/.vault_pass
    '''
}
```

### 스크립트로 비밀번호 제공 (AWS Secrets Manager 연동)

```bash
#!/bin/bash
# vault_pass_script.sh — 실행 권한 필요 (chmod +x)
aws secretsmanager get-secret-value \
  --secret-id ansible/vault-password \
  --query SecretString \
  --output text
```

```bash
ansible-playbook site.yml --vault-password-file ./vault_pass_script.sh
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 키 관리

### 디렉토리 구조 권장

```
group_vars/
├── all/
│   ├── vars.yml       # 평문 변수 (SCM 저장 가능)
│   └── vault.yml      # 암호화 변수 (SCM 저장 가능)
├── webservers/
│   ├── vars.yml
│   └── vault.yml
└── dbservers/
    ├── vars.yml
    └── vault.yml
```

### 비밀번호 변경 절차

```bash
# 1. 기존 비밀번호로 복호화
ansible-vault decrypt group_vars/all/vault.yml

# 2. 새 비밀번호로 재암호화
ansible-vault encrypt group_vars/all/vault.yml
# (새 비밀번호 입력)

# 또는 rekey 로 한 번에
ansible-vault rekey group_vars/all/vault.yml
# (기존 비밀번호 → 새 비밀번호 입력)
```

### 여러 파일 일괄 재암호화

```bash
find . -name "vault.yml" | xargs ansible-vault rekey \
  --new-vault-password-file ~/.vault_pass_new
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. Tips

### 설계

- `vault_` 접두사 규칙 준수: 암호화 변수와 평문 변수를 명확히 구분.
- 파일 단위 암호화 권장: 인라인 암호화는 diff가 어려워 코드 리뷰에 불편.
- `group_vars/*/vault.yml` 패턴: 그룹별로 vault 파일을 분리하면 권한 관리 용이.

### 운영

- 비밀번호 파일은 `.gitignore` 필수.
- CI/CD에서는 환경 시크릿(GitHub Secrets, Jenkins Credentials)으로 주입.
- 정기적인 vault 비밀번호 교체 (rekey).
- 암호화 파일도 SCM에 커밋 — 평문 복호화 파일은 절대 커밋 금지.

### 디버깅

```bash
# vault 비밀번호 확인 없이 문법만 체크
ansible-playbook site.yml --syntax-check
# (vault 변수 참조 시 복호화 필요 → --ask-vault-pass 추가)

# 특정 변수값 확인
ansible localhost -m debug -a "var=db_password" \
  --vault-password-file ~/.vault_pass \
  -e "@group_vars/all/vault.yml"
```

[⬆ 목차로 돌아가기](#목차)

# Ansible 설치 및 팀 운영 가이드

## 1. 개요

### Ansible 이란
- 에이전트 없이 SSH 기반으로 다수의 서버를 관리하는 오픈소스 자동화 도구
- YAML 기반 Playbook 으로 인프라를 코드로 관리 (IaC)
- Red Hat 에서 개발/관리

### 아키텍처

```
+---------------------+         SSH         +---------------------+
|   Control Node      |-------------------->|   Managed Node 1    |
|   (Ansible 설치)    |-------------------->|   Managed Node 2    |
|                     |-------------------->|   Managed Node 3    |
+---------------------+                    +---------------------+
  - ansible 설치                              - Python 3 만 필요
  - Playbook 작성/실행                        - 에이전트 설치 불필요
  - Inventory 관리                            - SSH 접속 허용
```

### 시스템 요구사항

| 항목              | Control Node (메인)        | Managed Node (대상)        |
|-------------------|----------------------------|----------------------------|
| Python            | 3.9 이상                   | 3.5 이상 (3.9+ 권장)      |
| OS                | Linux / macOS              | Linux / Windows            |
| 디스크            | 약 300MB 이상              | 최소 설치                  |
| 네트워크          | SSH (22/tcp) 아웃바운드    | SSH (22/tcp) 인바운드      |
| 권한              | sudo 권한 필요             | sudo 권한 필요             |

---

## 2. Ubuntu 설치

### 2-1. 시스템 업데이트

```bash
sudo apt update && sudo apt upgrade -y
```

### 2-2. 설치 방법 A: APT (PPA)

```bash
# Ansible 공식 PPA 추가
sudo apt install software-properties-common -y
sudo add-apt-repository --yes --update ppa:ansible/ansible

# Ansible 설치
sudo apt install ansible -y
```

### 2-3. 설치 방법 B: pip

```bash
# pip 설치
sudo apt install python3-pip python3-venv -y

# 가상환경 생성 (권장)
python3 -m venv ~/ansible-venv
source ~/ansible-venv/bin/activate

# Ansible 설치
pip install ansible

# 쉘 시작 시 자동 활성화 (선택)
echo 'source ~/ansible-venv/bin/activate' >> ~/.bashrc
```

### 2-4. 설치 확인

```bash
ansible --version
which ansible
```

---

## 3. Rocky Linux 10 설치

### 3-1. 시스템 업데이트

```bash
sudo dnf update -y
```

### 3-2. 설치 방법 A: DNF (AppStream)

```bash
# Rocky Linux 10 은 AppStream 저장소에 Ansible 포함
sudo dnf install ansible -y

# 최소 설치 (core 만)
# sudo dnf install ansible-core -y
```

### 3-3. 설치 방법 B: pip

```bash
# pip 설치
sudo dnf install python3-pip -y

# 가상환경 생성 (권장)
python3 -m venv ~/ansible-venv
source ~/ansible-venv/bin/activate

# Ansible 설치
pip install ansible

# 쉘 시작 시 자동 활성화 (선택)
echo 'source ~/ansible-venv/bin/activate' >> ~/.bashrc
```

### 3-4. 설치 확인

```bash
ansible --version
which ansible
```

---

## 4. 공통 초기 설정

### 4-1. ansible 전용 사용자 생성

```bash
# Control Node
sudo useradd -m -s /bin/bash ansible
sudo passwd ansible

# Managed Node (모든 대상 서버에서 실행)
sudo useradd -m -s /bin/bash ansible
sudo passwd ansible
echo "ansible ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/ansible
sudo chmod 440 /etc/sudoers.d/ansible
```

### 4-2. SSH 키 생성 및 배포

```bash
# Control Node 에서 실행
su - ansible
ssh-keygen -t ed25519 -C "ansible-control" -N ""

# Managed Node 로 키 배포
ssh-copy-id ansible@<managed-node-ip>

# 여러 서버에 일괄 배포
for host in 10.0.1.11 10.0.1.12 10.0.2.21; do
    ssh-copy-id ansible@$host
done

# 접속 테스트
ssh ansible@<managed-node-ip>
```

### 4-3. ansible.cfg 설정

```bash
sudo mkdir -p /etc/ansible
sudo vi /etc/ansible/ansible.cfg
```

```ini
[defaults]
inventory = /etc/ansible/hosts
remote_user = ansible
host_key_checking = False
log_path = /var/log/ansible.log
forks = 10
interpreter_python = /usr/bin/python3

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

### 4-4. Inventory 파일 설정

```bash
sudo vi /etc/ansible/hosts
```

```ini
[webservers]
prd-app-web-01 ansible_host=10.0.1.11
prd-app-web-02 ansible_host=10.0.1.12

[dbservers]
prd-db-mysql-01 ansible_host=10.0.2.21
prd-db-mysql-02 ansible_host=10.0.2.22

[gameservers]
prd-app-game-01 ansible_host=10.0.3.31
prd-app-game-02 ansible_host=10.0.3.32
prd-app-game-03 ansible_host=10.0.3.33
prd-app-game-04 ansible_host=10.0.3.34

[production:children]
webservers
dbservers
gameservers
```

---

## 5. 설치 검증

### 5-1. 연결 테스트

```bash
# 전체 호스트 ping
ansible all -m ping

# 특정 그룹만
ansible webservers -m ping

# 특정 호스트만
ansible prd-app-web-01 -m ping
```

### 5-2. Ad-hoc 명령 테스트

```bash
# 전체 서버 uptime 확인
ansible all -a "uptime"

# 게임 서버 디스크 확인
ansible gameservers -a "df -h"

# 웹 서버 nginx 상태 확인
ansible webservers -m systemd -a "name=nginx"
```

### 5-3. 정상 출력 예시

```
prd-app-web-01 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

---

## 6. 디렉토리 구조 (권장)

```
/etc/ansible/
├── ansible.cfg
├── hosts
└── playbooks/

~/ansible-projects/
├── ansible.cfg              # 프로젝트별 설정 (우선 적용)
├── inventory/
│   ├── dev
│   ├── qa
│   ├── stg
│   └── prd
├── group_vars/
│   ├── all.yml
│   ├── webservers.yml
│   ├── dbservers.yml
│   └── gameservers.yml
├── host_vars/
│   └── prd-db-mysql-01.yml
├── roles/
│   ├── common/
│   ├── webserver/
│   ├── database/
│   └── gameserver/
└── playbooks/
    ├── site.yml
    ├── deploy.yml
    └── maintenance.yml
```

---

## 7. 트러블슈팅

| 증상                                  | 원인                          | 해결 방법                                      |
|---------------------------------------|-------------------------------|------------------------------------------------|
| Host key verification failed          | SSH 호스트 키 불일치          | `host_key_checking = False` 또는 `ssh-keygen -R <host>` |
| Permission denied (publickey)         | SSH 키 미배포 또는 권한 문제  | `ssh-copy-id` 재실행, 키 파일 권한 600 확인    |
| sudo: a password is required          | passwordless sudo 미설정      | `/etc/sudoers.d/ansible` 설정 확인             |
| python: command not found             | Managed Node 에 Python 미설치 | `sudo dnf install python3 -y` 또는 `sudo apt install python3 -y` |
| No hosts matched                      | Inventory 호스트명 오타       | `ansible-inventory --list` 로 확인             |
| Connection timed out                  | 네트워크/방화벽 차단          | SSH 포트 (22) 방화벽 허용 확인                 |

### 디버깅 명령

```bash
# 상세 로그 출력 (-v ~ -vvvv)
ansible all -m ping -vvv

# Inventory 파싱 확인
ansible-inventory --list
ansible-inventory --graph

# 설정 확인
ansible-config dump
```

---

## 8. 보안 권장 사항

### Ansible Vault (민감 정보 암호화)

```bash
# 파일 암호화
ansible-vault encrypt vars/secrets.yml

# 암호화된 파일로 Playbook 실행
ansible-playbook playbook.yml --ask-vault-pass

# 파일 내용 확인
ansible-vault view vars/secrets.yml

# 파일 수정
ansible-vault edit vars/secrets.yml
```

### 보안 체크리스트

- [ ] ansible 전용 사용자 생성 (root 직접 사용 금지)
- [ ] SSH 키 인증만 허용 (패스워드 인증 비활성화)
- [ ] SSH 키 파일 권한 600 설정
- [ ] passwordless sudo 는 ansible 사용자만 허용
- [ ] ansible.cfg, inventory 파일 권한 제한 (640)
- [ ] Ansible Vault 로 민감 정보 암호화
- [ ] 로그 파일 (/var/log/ansible.log) 권한 제한 및 보관
- [ ] SSH 키 정기 교체 (연 1회 이상)

---

## 9. 설치 방법 비교

| 항목              | APT/DNF (패키지 매니저)      | pip (Python 패키지)          |
|-------------------|------------------------------|------------------------------|
| 설치 난이도       | 쉬움                         | 보통                         |
| 버전 관리         | OS 저장소 버전에 의존        | 최신 버전 즉시 사용 가능     |
| 업데이트          | `apt/dnf upgrade`            | `pip install --upgrade`      |
| 다중 버전         | 불가                         | venv 로 버전별 분리 가능     |
| 의존성 관리       | 자동                         | 수동 (venv 권장)             |
| 공식 권장         | 테스트/개발 환경             | 프로덕션 환경                |

⚠️ pip 설치 시 반드시 가상환경(venv) 사용을 권장합니다. 시스템 Python 패키지와 충돌을 방지합니다.

---

## 10. 팀 공동 사용 구성

### 운영 방식 비교

| 항목              | 공용 Control Node              | Git + 로컬 실행                |
|-------------------|--------------------------------|--------------------------------|
| 초기 구축         | 서버 1대 설정                  | 팀원별 환경 설정               |
| SSH 키 관리       | 서버 1곳에서 관리              | 팀원별 키 관리                 |
| 변경 통제         | 래퍼 스크립트 / 파일 권한      | Git PR 리뷰                   |
| 감사 추적         | 서버 로그 집중                 | Git 커밋 이력                  |
| 환경 일관성       | ✅ 동일 환경 보장              | ⚠️ 버전 차이 가능             |
| 장애 포인트       | Control Node 장애 시 전원 불가 | 개인 PC 독립적                 |
| ISMS 대응         | ✅ 접근 통제 용이              | ⚠️ 개인 PC 통제 어려움        |
| 권장 팀 규모      | 2~10명                         | 10명 이상                      |

⚠️ 10명 이하 인프라 팀이라면 **공용 Control Node + Git 병행**이 가장 실용적입니다.

### 아키텍처

```
+------------------+
|  Control Node    |
|  (공용 서버)     |
|                  |
|  ansible-admin ──┼── 관리자 (설정/역할 관리)
|  user-kim    ────┼── 팀원 A
|  user-park   ────┼── 팀원 B
|  user-lee    ────┼── 팀원 C
+------------------+
         |
         | SSH (ansible 서비스 계정)
         v
+------------------+
|  Managed Nodes   |
+------------------+
```

### 10-1. 공용 그룹 및 계정 생성

```bash
# 공용 그룹 생성
sudo groupadd ansible-team

# 팀원별 계정 생성
sudo useradd -m -s /bin/bash -G ansible-team user-kim
sudo useradd -m -s /bin/bash -G ansible-team user-park
sudo useradd -m -s /bin/bash -G ansible-team user-lee

# 관리자 계정
sudo useradd -m -s /bin/bash -G ansible-team ansible-admin
```

### 10-2. 공용 프로젝트 디렉토리

```bash
sudo mkdir -p /opt/ansible
sudo chown ansible-admin:ansible-team /opt/ansible
sudo chmod 2775 /opt/ansible   # setgid 로 그룹 상속
```

```
/opt/ansible/                          # 공용 (ansible-team 그룹)
├── ansible.cfg
├── inventory/
│   ├── dev
│   ├── qa
│   ├── stg
│   └── prd
├── group_vars/
│   ├── all.yml
│   ├── webservers.yml
│   ├── dbservers.yml
│   └── gameservers.yml
├── host_vars/
├── roles/                             # 공용 역할
│   ├── common/
│   ├── webserver/
│   └── gameserver/
├── playbooks/                         # 공용 Playbook
│   ├── deploy.yml
│   └── maintenance.yml
└── .git/                              # Git 으로 변경 이력 관리
```

### 10-3. 공용 ansible.cfg

```ini
[defaults]
inventory = /opt/ansible/inventory/prd
remote_user = ansible
host_key_checking = False
log_path = /var/log/ansible/ansible.log
forks = 10
roles_path = /opt/ansible/roles
interpreter_python = /usr/bin/python3
display_args_to_stdout = True

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

### 10-4. SSH 키 관리

```bash
# 방법 A: 공용 SSH 키 (간단, 감사 추적 약함)
# /opt/ansible/.ssh/ 에 공용 키 배치, ansible-team 그룹 읽기 허용

# 방법 B: 개인 SSH 키 (권장, 감사 추적 가능)
# 각 팀원이 자기 키로 접속, Managed Node 에 각자 키 등록
ssh-keygen -t ed25519 -C "user-kim@control" -N ""
ssh-copy-id ansible@<managed-node-ip>
```

| 방식          | 장점                    | 단점                    | ISMS 적합성 |
|---------------|-------------------------|-------------------------|-------------|
| 공용 키       | 관리 간편               | 누가 실행했는지 불명확  | ❌          |
| 개인 키       | 감사 추적 가능          | 키 배포 번거로움        | ✅          |

---

## 11. 실행 권한 제어

### 11-1. 환경별 실행 권한 래퍼 스크립트

```bash
#!/bin/bash
# /opt/ansible/bin/run-playbook.sh

ALLOWED_PRD_USERS="ansible-admin user-kim"
CURRENT_USER=$(whoami)
ENV=$(echo "$@" | grep -oP '(?<=-i inventory/)\w+')

if [[ "$ENV" == "prd" || "$ENV" == "stg" ]]; then
    if ! echo "$ALLOWED_PRD_USERS" | grep -qw "$CURRENT_USER"; then
        echo "❌ $CURRENT_USER 은 $ENV 환경 실행 권한이 없습니다."
        exit 1
    fi
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') [$CURRENT_USER] ansible-playbook $@" >> /var/log/ansible/audit.log
ansible-playbook "$@"
```

```bash
# 실행 권한 설정
sudo chmod 755 /opt/ansible/bin/run-playbook.sh

# 사용 예시
/opt/ansible/bin/run-playbook.sh -i inventory/prd playbooks/deploy.yml
```

### 11-2. 환경별 권한 매트릭스

| 역할           | dev   | qa    | stg   | prd   |
|----------------|-------|-------|-------|-------|
| ansible-admin  | ✅    | ✅    | ✅    | ✅    |
| user-kim       | ✅    | ✅    | ✅    | ✅    |
| user-park      | ✅    | ✅    | ❌    | ❌    |
| user-lee       | ✅    | ✅    | ❌    | ❌    |

---

## 12. 감사 로그 및 Git 운영

### 12-1. 감사 로그 설정

```bash
# 로그 디렉토리 생성
sudo mkdir -p /var/log/ansible
sudo chown ansible-admin:ansible-team /var/log/ansible
sudo chmod 2775 /var/log/ansible
```

로그 기록 형식:
```
2026-03-24 15:00:00 [user-kim] ansible-playbook -i inventory/prd playbooks/deploy.yml
2026-03-24 15:10:00 [user-park] ansible-playbook -i inventory/dev playbooks/test.yml
```

### 12-2. Git 운영 규칙

```bash
# 초기 Git 설정
cd /opt/ansible
git init
git add .
git commit -m "initial ansible project"

# 원격 저장소 연결 (GitLab/GitHub)
git remote add origin <repository-url>
git push -u origin main
```

### Git 워크플로우

```
팀원 작업 → git pull → 수정 → git commit → git push → (prd 는 PR 리뷰 후 merge)
```

| 환경      | 브랜치 전략                          | 리뷰 필요 여부 |
|-----------|--------------------------------------|----------------|
| dev/qa    | main 에서 직접 작업 가능             | 선택           |
| stg/prd   | feature 브랜치 → PR → 리뷰 후 merge | 필수           |

---

## 13. 확장: AWX (Ansible Tower 오픈소스)

팀 규모가 커지거나 웹 UI 기반 관리가 필요하면 AWX 도입을 검토합니다.

| 항목              | CLI (현재 방식)                | AWX (웹 UI)                    |
|-------------------|--------------------------------|--------------------------------|
| 실행 방식         | 터미널에서 명령 실행           | 웹 브라우저에서 버튼 클릭      |
| 권한 관리         | 래퍼 스크립트 / 파일 권한      | RBAC (역할 기반 접근 제어)     |
| 실행 이력         | 로그 파일                      | 웹 UI 에서 조회                |
| 승인 프로세스     | 수동                           | 워크플로우 내장                |
| 스케줄링          | cron                           | 내장 스케줄러                  |
| 도입 시점         | 즉시                           | 팀 10명 이상 또는 ISMS 요구 시 |

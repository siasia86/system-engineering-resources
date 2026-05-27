# Molecule

## 목차

| 섹션                                                                                                       |
|------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 핵심 개념](#3-핵심-개념)                             |
| [4. 설치](#4-설치) / [5. 주요 명령어](#5-주요-명령어) / [6. 설정 파일](#6-설정-파일)                       |
| [7. Docker 드라이버](#7-docker-드라이버) / [8. Vagrant 드라이버](#8-vagrant-드라이버) / [9. Tips](#9-tips) |
| [10. 실무 구조 vs 학습 구조](#10-실무-구조-vs-학습-구조)                                                  |

---

## 1. 개요

Ansible role 테스트 프레임워크입니다. role을 작성하면 실제 환경(컨테이너/VM)에서 자동으로 적용하고 결과를 검증합니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    Molecule Test Cycle                      │
│                                                             │
│  create -> converge -> verify -> destroy                    │
│    │           │          │         │                       │
│  create env  apply role  verify   remove env                │
└─────────────────────────────────────────────────────────────┘
```

`molecule test` 한 번으로 전체 사이클을 자동 실행합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

```
ansible-role-nginx/
├── tasks/
│   └── main.yml
├── handlers/
│   └── main.yml
└── molecule/
    └── default/
        ├── molecule.yml   <- driver + instance definition
        ├── converge.yml   <- playbook to test
        └── verify.yml     <- verify playbook
```

여러 시나리오를 만들어 드라이버별로 분리할 수 있습니다.

```
molecule/
├── default/   <- Docker driver
└── vagrant/   <- Vagrant driver
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 핵심 개념

| 개념        | 설명                                                        |
|-------------|-------------------------------------------------------------|
| Scenario    | 테스트 환경 단위. `molecule/` 하위 디렉토리 하나가 시나리오 |
| Driver      | 인스턴스를 실행하는 백엔드 (docker, vagrant, delegated 등)  |
| Platform    | 테스트 대상 OS 인스턴스 정의                                |
| Converge    | role을 인스턴스에 적용하는 단계                             |
| Verify      | 적용 결과를 검증하는 단계 (Ansible, Testinfra 등)           |
| Idempotency | 동일 role을 두 번 실행해도 변경이 없는지 확인               |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설치

```bash
pip install molecule molecule-plugins[docker] molecule-plugins[vagrant]
```

```bash
molecule --version
```

### role 초기화 (molecule 포함)

```bash
ansible-galaxy role init my_role
cd my_role
molecule init scenario
```

### 기존 role에 시나리오 추가

```bash
molecule init scenario --driver-name docker
molecule init scenario vagrant --driver-name vagrant
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 주요 명령어

```bash
molecule test           # 전체 사이클 (create→converge→verify→destroy)
molecule create         # 인스턴스 생성만
molecule converge       # role 적용 (인스턴스 유지)
molecule verify         # 검증만 실행
molecule destroy        # 인스턴스 삭제
molecule login          # 인스턴스 접속 (디버깅)
molecule lint           # 린트 검사
molecule list           # 인스턴스 상태 목록
```

```bash
# 특정 시나리오 지정
molecule test -s vagrant

# 모든 시나리오 실행
molecule test --all
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 설정 파일

### converge.yml

```yaml
---
- name: Converge
  hosts: all
  become: true
  roles:
    - role: my_role
```

### verify.yml

```yaml
---
- name: Verify
  hosts: all
  become: true
  tasks:
    - name: nginx 서비스 실행 확인
      ansible.builtin.service_facts:

    - name: nginx 실행 중인지 검증
      ansible.builtin.assert:
        that: ansible_facts.services['nginx.service'].state == 'running'

    - name: 80 포트 응답 확인
      ansible.builtin.uri:
        url: http://localhost
        status_code: 200
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Docker 드라이버

systemd가 필요한 role은 `geerlingguy/docker-*-ansible` 이미지를 사용합니다.

```yaml
# molecule/default/molecule.yml
driver:
  name: docker

platforms:
  - name: ubuntu22
    image: geerlingguy/docker-ubuntu2204-ansible
    privileged: true
    command: /lib/systemd/systemd
    pre_build_image: true

  - name: ubuntu24
    image: geerlingguy/docker-ubuntu2404-ansible
    privileged: true
    command: /lib/systemd/systemd
    pre_build_image: true

  - name: rocky9
    image: geerlingguy/docker-rockylinux9-ansible
    privileged: true
    command: /usr/sbin/init
    pre_build_image: true

  - name: amazonlinux2023
    image: geerlingguy/docker-amazonlinux2023-ansible
    privileged: true
    command: /usr/sbin/init
    pre_build_image: true

provisioner:
  name: ansible
  playbooks:
    converge: converge.yml
    verify: verify.yml
```

### geerlingguy 이미지 목록

| OS                | 이미지                                       |
|-------------------|----------------------------------------------|
| Ubuntu 20.04      | `geerlingguy/docker-ubuntu2004-ansible`      |
| Ubuntu 22.04      | `geerlingguy/docker-ubuntu2204-ansible`      |
| Ubuntu 24.04      | `geerlingguy/docker-ubuntu2404-ansible`      |
| Rocky Linux 9     | `geerlingguy/docker-rockylinux9-ansible`     |
| Amazon Linux 2023 | `geerlingguy/docker-amazonlinux2023-ansible` |

[⬆ 목차로 돌아가기](#목차)

---

## 8. Vagrant 드라이버

Windows Server 등 컨테이너로 재현 불가한 환경에 사용합니다.

```yaml
# molecule/vagrant/molecule.yml
driver:
  name: vagrant
  provider:
    name: virtualbox

platforms:
  - name: ubuntu22
    box: ubuntu/jammy64
    memory: 1024
    cpus: 1

  - name: rocky9
    box: rockylinux/9
    memory: 1024
    cpus: 1

  - name: win2022
    box: gusztavvargadr/windows-server-2022-standard
    memory: 2048
    cpus: 2
    config_options:
      vm.communicator: '"winrm"'

provisioner:
  name: ansible
  playbooks:
    converge: converge.yml
    verify: verify.yml
  connection_options:
    ansible_winrm_transport: ntlm      # Windows 전용
```

```bash
molecule test -s vagrant
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. Tips

```bash
# converge 후 인스턴스 유지하며 디버깅
molecule converge
molecule login -h ubuntu22
molecule destroy

# 멱등성 검사만
molecule idempotency

# 특정 태그만 실행
MOLECULE_ANSIBLE_ARGS="--tags install" molecule converge
```

🟡 `molecule test`는 실패 시 `destroy`를 건너뜁니다. 인스턴스가 남아있으면 `molecule destroy`로 수동 삭제합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 실무 구조 vs 학습 구조

### 학습 구조 (비효율)

playbook과 molecule role을 분리하면 같은 기능을 두 번 작성하게 됩니다.

```
project/
├── playbooks/
│   └── ssh_setup.yml              # 운영 코드 (raw 모듈)
└── molecule_tests/
    └── roles/ssh_setup/
        └── tasks/main.yml         # 같은 기능을 다시 작성 (apt/dnf 모듈)
```

🟡 playbook 수정 시 molecule role도 따로 수정해야 합니다. 동기화가 빠지면 테스트가 무의미해집니다.

### 실무 구조 (권장)

role이 운영 코드이자 테스트 대상입니다. 별도로 "테스트용 코드"를 만들지 않습니다.

```
project/
├── roles/
│   ├── ssh_setup/
│   │   ├── tasks/main.yml         # 운영 코드 = 테스트 대상 (하나만 존재)
│   │   ├── handlers/main.yml
│   │   ├── defaults/main.yml
│   │   └── molecule/default/      # 이 role을 테스트
│   │       ├── molecule.yml
│   │       ├── converge.yml
│   │       └── verify.yml
│   └── nginx/
│       ├── tasks/main.yml
│       └── molecule/default/
│           └── ...
├── playbooks/
│   └── site.yml                   # roles를 조합해서 호출만
└── inventory/
```

### 비교

| 항목        | 학습 구조 (분리) | 실무 구조 (통합)      |
|-------------|------------------|-----------------------|
| 운영 코드   | playbook에 직접  | `roles/*/tasks/`      |
| 테스트 대상 | 별도 role 작성   | 운영 role 그대로      |
| 수정 시     | 2곳 수정 필요    | 1곳만 수정            |
| 동기화 위험 | 높음             | 없음                  |
| CI/CD 연동  | 경로 복잡        | `molecule test` 한 줄 |

### 전환 방법

```bash
# 1. playbook의 task를 role로 추출
ansible-galaxy role init roles/ssh_setup

# 2. role 안에 molecule 시나리오 생성
cd roles/ssh_setup
molecule init scenario

# 3. playbook은 role 호출만
# playbooks/site.yml
# - hosts: all
#   roles:
#     - ssh_setup
#     - nginx

# 4. 테스트
molecule test
```

### CI/CD 파이프라인 예시

```yaml
# .github/workflows/molecule.yml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        role: [ssh_setup, nginx, zabbix_agent]
    steps:
      - uses: actions/checkout@v4
      - run: pip install molecule molecule-plugins[docker]
      - run: cd roles/${{ matrix.role }} && molecule test
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Molecule Documentation: [ansible.readthedocs.io/projects/molecule](https://ansible.readthedocs.io/projects/molecule/) — ★★★☆☆
- geerlingguy Docker images: [github.com/geerlingguy/docker-*-ansible](https://github.com/geerlingguy) — ★★☆☆☆
- [vagrant.md](./vagrant.md)
- [docker.md](./docker.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-15

**마지막 업데이트**: 2026-05-27

© 2026 siasia86. Licensed under CC BY 4.0.

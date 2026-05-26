# Ansible 기초 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. ansible.cfg 적용 우선순위](#2-ansiblecfg-적용-우선순위) / [3. Inventory (대상 서버 목록)](#3-inventory-대상-서버-목록) |
| [4. Ad-hoc 명령 (1회성 실행)](#4-ad-hoc-명령-1회성-실행) / [5. Playbook 기초](#5-playbook-기초) / [6. 변수 우선순위](#6-변수-우선순위) |
| [7. Handler (변경 시에만 실행)](#7-handler-변경-시에만-실행) / [8. 조건문 / 반복문](#8-조건문--반복문) / [9. Template (Jinja2)](#9-template-jinja2) |
| [10. Role 구조](#10-role-구조) / [11. 자주 쓰는 실행 옵션](#11-자주-쓰는-실행-옵션) / [12. 실습 순서 권장](#12-실습-순서-권장) |
| [13. 모듈 상세 사용법](#13-모듈-상세-사용법) / [14. raw 모듈과 delegate_to](#14-raw-모듈과-delegate_to) / [15. 에러 처리](#15-에러-처리) |
| [16. 태그](#16-태그) / [17. Dynamic Inventory](#17-dynamic-inventory) / [18. Vault — 시크릿 관리](#18-vault--시크릿-관리) |


---

## 1. 개요

Ansible은 에이전트 없이 SSH로 대상 서버를 관리하는 자동화 도구입니다.

```
Control Node (내 서버)  ──SSH──>  Managed Node (대상 서버)

명령 실행 방식:
  ad-hoc   → 1회성 명령 (ansible 명령어)
  playbook → 반복 가능한 자동화 (ansible-playbook 명령어)
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. ansible.cfg 적용 우선순위

우선순위가 높은 순서대로 적용됩니다. 먼저 발견된 설정이 나머지를 무시합니다.

| 우선순위 | 위치                       | 설명          |
|----------|----------------------------|---------------|
| 1 (최고) | `ANSIBLE_CONFIG` 환경변수  | 명시적 지정   |
| 2        | `./ansible.cfg`            | 현재 디렉토리 |
| 3        | `~/.ansible.cfg`           | 홈 디렉토리   |
| 4 (최저) | `/etc/ansible/ansible.cfg` | 시스템 전역   |

```bash
# 현재 적용 중인 설정 파일 확인
ansible --version
# config file = /opt/ansible/ansible.cfg  ← 여기서 확인

# 모든 설정값 확인
ansible-config dump

# 기본값과 다른 설정만 확인
ansible-config dump --only-changed

# 환경변수로 지정 (최우선)
export ANSIBLE_CONFIG=/opt/ansible/ansible.cfg
```

### 권장 ansible.cfg

```ini
[defaults]
inventory = /opt/ansible/inventory/dev
remote_user = ansible
host_key_checking = False
log_path = /var/log/ansible/ansible.log
forks = 10
roles_path = /opt/ansible/roles
interpreter_python = /usr/bin/python3
display_args_to_stdout = True
callback_whitelist = timer

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

| 설정                   | 설명                                     |
|------------------------|------------------------------------------|
| forks                  | 동시 접속 수 (기본 5, 서버 많으면 20~50) |
| pipelining             | SSH 연결 재사용으로 속도 향상            |
| host_key_checking      | 최초 접속 시 fingerprint 확인 비활성화   |
| callback_whitelist     | timer 추가 시 실행 시간 표시             |
| display_args_to_stdout | 실행 인자를 로그에 기록                  |

[⬆ 목차로 돌아가기](#목차)

---

## 3. Inventory (대상 서버 목록)

```ini
# inventory/dev

[webservers]
dev-app-web-01 ansible_host=192.168.1.10
dev-app-web-02 ansible_host=192.168.1.11

[dbservers]
dev-db-mysql-01 ansible_host=192.168.1.20

[gameservers]
dev-app-game-01 ansible_host=192.168.1.30
dev-app-game-02 ansible_host=192.168.1.31

[all:vars]
ansible_user=ansible
ansible_ssh_private_key_file=~/.ssh/id_ed25519
```

```bash
# JSON 형식으로 전체 출력
ansible-inventory -i inventory/dev --list

# 트리 형식으로 그룹/호스트 구조 출력
ansible-inventory -i inventory/dev --graph

# 특정 호스트 변수 확인
ansible-inventory -i inventory/dev --host dev-app-web-01

# 특정 그룹만 트리 출력
ansible-inventory -i inventory/dev --graph webservers

# 변수 포함 트리 출력
ansible-inventory -i inventory/dev --graph --vars

# 현재 적용 중인 inventory 소스 확인
ansible-inventory --list -v
```

| 옵션 | 설명 |
|------|------|
| `--list` | 전체 호스트/그룹/변수 JSON 출력 |
| `--graph` | 트리 구조 출력 |
| `--host <hostname>` | 특정 호스트 변수만 출력 |
| `--vars` | `--graph`에 변수 포함 |
| `-i` | inventory 파일/디렉토리 지정 |

### Docker 컨테이너 연결 (SSH 없이)

```ini
[docker_ubuntu]
ubuntu22  ansible_connection=docker ansible_host=02_compose-ubuntu22-1
ubuntu24  ansible_connection=docker ansible_host=02_compose-ubuntu24-1

[docker:children]
docker_ubuntu

[docker:vars]
ansible_remote_tmp=/tmp/.ansible/tmp
ansible_python_interpreter=/usr/local/bin/python3
```

| `ansible_connection` 값 | 설명                                  |
|-------------------------|---------------------------------------|
| `ssh`                   | 기본값 — SSH로 접속                   |
| `docker`                | `docker exec`로 접속 (SSH 불필요)     |
| `local`                 | Controller 자신에게 실행              |
| `winrm`                 | Windows WinRM 접속                    |

[⬆ 목차로 돌아가기](#목차)

---

## 4. Ad-hoc 명령 (1회성 실행)

```bash
# 연결 테스트
ansible all -i inventory/dev -m ping

# 특정 그룹만
ansible webservers -i inventory/dev -m ping

# 명령 실행
ansible webservers -i inventory/dev -m shell -a "uptime"
ansible webservers -i inventory/dev -m shell -a "df -h"
ansible webservers -i inventory/dev -m shell -a "free -m"

# 파일 복사
ansible webservers -i inventory/dev -m copy -a "src=./test.txt dest=/tmp/test.txt"

# 패키지 설치
ansible webservers -i inventory/dev -m dnf -a "name=htop state=present" --become

# 서비스 관리
ansible webservers -i inventory/dev -m service -a "name=nginx state=restarted" --become
```

### 자주 쓰는 모듈

| 모듈       | 용도                 | 예시                                               |
|------------|----------------------|----------------------------------------------------|
| ping       | 연결 테스트          | `-m ping`                                          |
| shell      | 쉘 명령 실행         | `-m shell -a "uptime"`                             |
| copy       | 파일 복사            | `-m copy -a "src=a dest=b"`                        |
| dnf        | 패키지 관리 (RHEL)   | `-m dnf -a "name=htop state=present"`              |
| apt        | 패키지 관리 (Ubuntu) | `-m apt -a "name=htop state=present"`              |
| service    | 서비스 관리          | `-m service -a "name=nginx state=started"`         |
| file       | 파일/디렉토리 관리   | `-m file -a "path=/tmp/dir state=directory"`       |
| user       | 사용자 관리          | `-m user -a "name=deploy state=present"`           |
| template   | 템플릿 배포          | Playbook 에서 사용                                 |
| lineinfile | 파일 내 특정 줄 수정 | `-m lineinfile -a "path=... line=..."`             |
| cron       | cron 작업 관리       | `-m cron -a "name=backup minute=0 hour=2 job=..."` |

[⬆ 목차로 돌아가기](#목차)

---

## 5. Playbook 기초

```yaml
# playbooks/hello.yml
---
- name: 첫 번째 Playbook
  hosts: webservers
  become: yes

  tasks:
    - name: htop 설치
      dnf:
        name: htop
        state: present

    - name: /tmp/hello.txt 생성
      copy:
        content: "Hello from Ansible!\n"
        dest: /tmp/hello.txt
        owner: root
        mode: '0644'

    - name: 서버 uptime 확인
      shell: uptime
      register: result

    - name: uptime 출력
      debug:
        msg: "{{ result.stdout }}"
```

### 주요 Play 옵션

```yaml
- name: 예시
  hosts: webservers
  become: true
  gather_facts: true        # 기본값 — OS/IP 등 서버 정보 수집 (Python 필요)
  # gather_facts: false     # Python 없는 환경 또는 속도 최적화 시

  pre_tasks:                # tasks 실행 전 항상 먼저 실행
    - name: 사전 점검
      debug:
        msg: "배포 시작"

  tasks:
    - name: 작업

  post_tasks:               # tasks 완료 후 항상 실행
    - name: 사후 점검
      debug:
        msg: "배포 완료"
```

```bash
# 실행
ansible-playbook -i inventory/dev playbooks/hello.yml

# 문법 체크만
ansible-playbook -i inventory/dev playbooks/hello.yml --syntax-check

# 변경 없이 시뮬레이션 (dry-run)
ansible-playbook -i inventory/dev playbooks/hello.yml --check

# 특정 호스트만
ansible-playbook -i inventory/dev playbooks/hello.yml --limit dev-app-web-01

# 여러 호스트 (쉼표 구분)
ansible-playbook -i inventory/dev playbooks/hello.yml --limit dev-app-web-01,dev-app-web-02

# 그룹 지정
ansible-playbook -i inventory/dev playbooks/hello.yml --limit webservers

# 패턴 (와일드카드)
ansible-playbook -i inventory/dev playbooks/hello.yml --limit 'dev-app-*'

# 특정 호스트 제외 (! 사용, 따옴표 필수)
ansible-playbook -i inventory/dev playbooks/hello.yml --limit 'all,!dev-db-*'

# 상세 출력 (-v, -vv, -vvv 로 단계 조절)
ansible-playbook -i inventory/dev playbooks/hello.yml -v
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 변수 우선순위

낮은 순서 → 높은 순서 (아래로 갈수록 우선):

| 우선순위 | 위치                         | 예시                             |
|----------|------------------------------|----------------------------------|
| 1 (최저) | role defaults                | `roles/common/defaults/main.yml` |
| 2        | inventory group_vars/all     | `group_vars/all.yml`             |
| 3        | inventory group_vars/그룹명  | `group_vars/webservers.yml`      |
| 4        | inventory host_vars/호스트명 | `host_vars/dev-app-web-01.yml`   |
| 5        | play vars                    | playbook 내 `vars:` 섹션         |
| 6        | role vars                    | `roles/common/vars/main.yml`     |
| 7        | task vars                    | task 내 `vars:` 섹션             |
| 8        | set_fact                     | `set_fact:` 로 동적 설정         |
| 9 (최고) | extra vars (`-e`)            | `-e "app_env=staging"`           |

```yaml
# group_vars/webservers.yml
---
http_port: 80
max_connections: 1024
app_env: development
```

```yaml
# host_vars/dev-app-web-01.yml
---
http_port: 8080    # 이 호스트만 다른 포트
```

```bash
# 명령줄에서 변수 전달 (최우선)
ansible-playbook playbooks/deploy.yml -e "app_env=staging http_port=8080"
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Handler (변경 시에만 실행)

```yaml
---
- name: Nginx 설정 배포
  hosts: webservers
  become: yes

  tasks:
    - name: nginx.conf 배포
      template:
        src: templates/nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify: restart nginx

  handlers:
    - name: restart nginx
      service:
        name: nginx
        state: restarted
```

`notify`는 task에서 실제 변경(changed)이 발생했을 때만 handler를 호출합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 조건문 / 반복문

```yaml
tasks:
  # 조건문
  - name: Rocky Linux 에서만 실행
    dnf:
      name: epel-release
      state: present
    when: ansible_distribution == "Rocky"

  # 반복문
  - name: 여러 패키지 설치
    dnf:
      name: "{{ item }}"
      state: present
    loop:
      - htop
      - tmux
      - vim
      - tree

  # 조건 + 반복 조합
  - name: 특정 서비스 활성화
    service:
      name: "{{ item }}"
      state: started
      enabled: yes
    loop:
      - nginx
      - node_exporter
    when: ansible_distribution == "Rocky"
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. Template (Jinja2)

```jinja2
{# templates/nginx.conf.j2 #}
worker_processes auto;

events {
    worker_connections {{ max_connections | default(1024) }};
}

http {
    server {
        listen {{ http_port }};
        server_name {{ ansible_hostname }};

{% if app_env == "production" %}
        access_log /var/log/nginx/access.log;
{% else %}
        access_log off;
{% endif %}
    }
}
```

```yaml
tasks:
  - name: nginx 설정 배포
    template:
      src: templates/nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: restart nginx
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. Role 구조

반복되는 작업을 재사용 가능한 단위로 구조화합니다.

```
roles/
└── common/
    ├── tasks/
    │   └── main.yml       # 실행할 작업
    ├── handlers/
    │   └── main.yml       # 핸들러
    ├── templates/
    │   └── ntp.conf.j2    # 템플릿 파일
    ├── files/
    │   └── motd           # 정적 파일
    ├── vars/
    │   └── main.yml       # 역할 변수 (높은 우선순위)
    ├── defaults/
    │   └── main.yml       # 기본값 (낮은 우선순위)
    └── meta/
        └── main.yml       # 의존성 정의
```

```yaml
# roles/common/tasks/main.yml
---
- name: 기본 패키지 설치
  dnf:
    name:
      - htop
      - tmux
      - vim
      - tree
      - curl
      - wget
    state: present

- name: NTP 설정
  template:
    src: ntp.conf.j2
    dest: /etc/chrony.conf
  notify: restart chronyd

- name: MOTD 설정
  copy:
    src: motd
    dest: /etc/motd
```

```yaml
# playbooks/site.yml (role 사용)
---
- name: 공통 설정 적용
  hosts: all
  become: yes
  roles:
    - common

- name: 웹서버 설정
  hosts: webservers
  become: yes
  roles:
    - common
    - webserver
```

```bash
# role 골격 자동 생성
ansible-galaxy init roles/gameserver
```

[⬆ 목차로 돌아가기](#목차)

---

## 11. 자주 쓰는 실행 옵션

| 옵션                     | 설명                     |
|--------------------------|--------------------------|
| `-i inventory/dev`       | 인벤토리 파일 지정       |
| `--check`                | dry-run (실제 변경 없음) |
| `--diff`                 | 파일 변경 내용 diff 출력 |
| `--limit host1`          | 특정 호스트만 실행                          |
| `--limit host1,host2`    | 여러 호스트 (쉼표 구분)                     |
| `--limit 'web*'`         | 패턴 매칭 (와일드카드)                      |
| `--limit 'all,!db*'`     | 특정 호스트/그룹 제외 (`!` 사용)            |
| `--tags deploy`          | 특정 태그만 실행         |
| `--skip-tags debug`      | 특정 태그 제외           |
| `--step`                 | task 마다 확인 후 실행   |
| `--start-at-task "이름"` | 특정 task 부터 실행      |
| `-e "key=value"`         | 변수 전달 (최우선)       |
| `-v / -vv / -vvv`        | 상세 출력 단계           |
| `--list-tasks`           | 실행할 task 목록만 출력  |
| `--list-hosts`           | 대상 호스트 목록만 출력  |
| `--syntax-check`         | 문법 검사만 (실행 안 함) |

[⬆ 목차로 돌아가기](#목차)

---

## 12. 실습 순서 권장

```
1단계: ansible all -m ping                          ← 연결 확인
2단계: ansible all -m shell -a "hostname"            ← ad-hoc 명령
3단계: playbooks/hello.yml 작성 → 실행              ← playbook 기초
4단계: group_vars/ + templates/ 사용                 ← 변수 + 템플릿
5단계: roles/ 로 구조화                              ← role 분리
```

여기까지가 일상 업무의 80%를 커버합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 13. 모듈 상세 사용법

### 모듈 조회 명령

```bash
# 전체 모듈 목록
ansible-doc -l

# 특정 모듈 사용법 확인
ansible-doc apt
ansible-doc copy
ansible-doc template

# 모듈 파라미터만 간략히
ansible-doc -s service
```

### 모듈 기본 문법

```yaml
- name: 작업 설명
  모듈명:
    파라미터1: 값
    파라미터2: 값
  register: 결과변수        # 실행 결과 저장 (선택)
  notify: 핸들러명          # 변경 시 핸들러 호출 (선택)
  when: 조건               # 조건부 실행 (선택)
  changed_when: false      # 항상 ok 표시 (조회성 명령에 사용)
```

### 주요 모듈 파라미터 정리

| 모듈         | 주요 파라미터                                       | state 값                      |
|--------------|-----------------------------------------------------|-------------------------------|
| `apt`        | name, state, update_cache                           | present, absent, latest       |
| `dnf`        | name, state, enablerepo                             | present, absent, latest       |
| `copy`       | src, dest, content, owner, group, mode              | -                             |
| `template`   | src, dest, owner, group, mode                       | -                             |
| `file`       | path, state, owner, group, mode, src(link)          | file, directory, link, absent |
| `service`    | name, state, enabled                                | started, stopped, restarted   |
| `user`       | name, state, shell, groups, append                  | present, absent               |
| `cron`       | name, minute, hour, day, month, weekday, job, state | present, absent               |
| `lineinfile` | path, regexp, line, state, insertafter              | present, absent               |
| `command`    | cmd (또는 free_form), creates, removes              | -                             |
| `shell`      | cmd (또는 free_form), creates, removes              | - (파이프/리다이렉션 가능)    |
| `stat`       | path                                                | -                             |
| `debug`      | msg, var                                            | -                             |

### 예시 1 — Nginx 설치 + 설정 + 서비스 관리

```yaml
---
- name: Nginx 웹서버 배포
  hosts: webservers
  become: true

  vars:
    server_name: example.com
    http_port: 80

  tasks:
    # apt 모듈 - 패키지 설치
    - name: nginx 설치
      apt:
        name: nginx
        state: present
        update_cache: true

    # file 모듈 - 디렉토리 생성
    - name: 웹 루트 디렉토리 생성
      file:
        path: /var/www/{{ server_name }}
        state: directory
        owner: www-data
        group: www-data
        mode: "0755"

    # template 모듈 - 설정 파일 배포 (변수 치환)
    - name: nginx 설정 배포
      template:
        src: templates/nginx.conf.j2
        dest: /etc/nginx/sites-available/{{ server_name }}
      notify: reload nginx

    # file 모듈 - 심볼릭 링크
    - name: site 활성화
      file:
        src: /etc/nginx/sites-available/{{ server_name }}
        dest: /etc/nginx/sites-enabled/{{ server_name }}
        state: link
      notify: reload nginx

    # copy 모듈 - 정적 파일 복사
    - name: index.html 배포
      copy:
        src: files/index.html
        dest: /var/www/{{ server_name }}/index.html
        owner: www-data

    # service 모듈 - 서비스 시작 + 부팅 시 자동 시작
    - name: nginx 시작
      service:
        name: nginx
        state: started
        enabled: true

  handlers:
    - name: reload nginx
      service:
        name: nginx
        state: reloaded
```

### 예시 2 — 시스템 점검 + 정보 수집

```yaml
---
- name: 시스템 점검
  hosts: all
  become: true

  tasks:
    # setup 모듈 - 시스템 정보 수집
    - name: 시스템 정보 수집
      setup:
        filter: "ansible_os_family,ansible_distribution*,ansible_memtotal_mb"

    # debug 모듈 - 변수 출력
    - name: OS 정보 출력
      debug:
        msg: "{{ inventory_hostname }}: {{ ansible_distribution }} {{ ansible_distribution_version }} ({{ ansible_os_family }})"

    # command 모듈 - 명령 실행 + register로 결과 저장
    - name: 디스크 사용량 확인
      command: df -h /
      register: disk_result
      changed_when: false

    - name: 디스크 결과 출력
      debug:
        msg: "{{ disk_result.stdout_lines }}"

    # shell 모듈 - 파이프 사용 가능
    - name: 메모리 사용률 확인
      shell: free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}'
      register: mem_result
      changed_when: false

    - name: 메모리 결과 출력
      debug:
        msg: "{{ inventory_hostname }} 메모리 사용률: {{ mem_result.stdout }}"

    # stat 모듈 - 파일 존재 여부 확인
    - name: 백업 디렉토리 확인
      stat:
        path: /backup
      register: backup_dir

    - name: 백업 디렉토리 상태
      debug:
        msg: "{{ '/backup 존재' if backup_dir.stat.exists else '/backup 없음' }}"
```

### 예시 3 — 유저 관리 + 보안 설정

```yaml
---
- name: 유저 관리 및 보안 설정
  hosts: all
  become: true

  vars:
    deploy_users:
      - name: deploy
        shell: /bin/bash
        groups: sudo
        key: "ssh-ed25519 AAAA... deploy@server"
      - name: monitor
        shell: /bin/bash
        groups: sudo
        key: "ssh-ed25519 AAAA... monitor@server"

  tasks:
    # user 모듈 - 유저 생성 (반복문)
    - name: 유저 생성
      user:
        name: "{{ item.name }}"
        shell: "{{ item.shell }}"
        groups: "{{ item.groups }}"
        append: yes
        state: present
      loop: "{{ deploy_users }}"

    # authorized_key 모듈 - SSH 키 등록
    - name: SSH 키 등록
      authorized_key:
        user: "{{ item.name }}"
        key: "{{ item.key }}"
      loop: "{{ deploy_users }}"

    # copy 모듈 - content로 직접 파일 생성
    - name: sudoers 설정
      copy:
        content: "{{ item.name }} ALL=(ALL) NOPASSWD: ALL\n"
        dest: "/etc/sudoers.d/{{ item.name }}"
        mode: "0440"
      loop: "{{ deploy_users }}"

    # lineinfile 모듈 - SSH 보안 설정
    - name: root 로그인 비활성화
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?PermitRootLogin'
        line: 'PermitRootLogin no'
      notify: restart sshd

    - name: 패스워드 인증 비활성화
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?PasswordAuthentication'
        line: 'PasswordAuthentication no'
      notify: restart sshd

    - name: SSH 타임아웃 설정
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?ClientAliveInterval'
        line: 'ClientAliveInterval 300'
      notify: restart sshd

  handlers:
    - name: restart sshd
      service:
        name: sshd
        state: restarted
```

### 모듈 실행 흐름 요약

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Task Execution   │     │ Change Detection │     │ Post Processing  │
│ (Module Call)    │ ──> │ changed: true?   │ ──> │ notify handler   │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

- Task Execution: task 실행 (모듈 호출)
- Change Detection: 변경 감지
- Post Processing: 후처리 (handler 실행)
- `register`: 결과를 변수에 저장 → `debug`로 출력 또는 `when` 조건에 활용
- `changed_when: false`: 항상 ok 표시 (조회성 명령에 사용)

[⬆ 목차로 돌아가기](#목차)

---

## 14. raw 모듈과 delegate_to

### `raw` 모듈 — Python 없이 실행

일반 Ansible 모듈(`package`, `copy`, `service` 등)은 대상 서버에 Python이 필요합니다.
`raw` 모듈은 SSH로 shell 명령을 그대로 전달하므로 Python 없이 동작합니다.

```
일반 모듈
  Controller → SSH → 대상 서버에 Python 모듈 전송 → Python으로 실행  (Python 필요)

raw 모듈
  Controller → SSH → 대상 서버에서 shell 명령 직접 실행              (Python 불필요)
```

| 항목 | `raw` | `command` / `shell` |
|------|-------|---------------------|
| Python 필요 | ❌ | ✅ |
| 파이프 사용 | ✅ | `shell`만 가능 (`raw`도 가능) |
| 멱등성 자동 보장 | ❌ | ❌ |
| 주요 용도 | Python 설치 전 부트스트랩 | 일반 명령 실행 |

```yaml
# Python 없는 서버에 Python 설치
- name: Python 설치
  ansible.builtin.raw: yum install -y python3
  changed_when: false
```

🟡 `raw` 사용 후 Python이 설치되면 이후 task부터 일반 모듈을 사용합니다.
`gather_facts: false`와 함께 사용해야 합니다 — `setup` 모듈도 Python이 필요하기 때문입니다.

### `delegate_to` — 다른 호스트에서 task 실행

특정 task를 대상 서버가 아닌 **지정한 호스트**에서 실행합니다.
`delegate_to: localhost`가 가장 많이 쓰입니다.

```
일반 task
  Controller ──────────────────────────> 대상 서버에서 실행

delegate_to: localhost
  Controller (localhost에서 실행) ──X──> 대상 서버 접속 안 함
```

```yaml
# docker cp는 Controller(localhost)에서 실행해야 함
- name: 스크립트를 컨테이너에 복사
  ansible.builtin.raw: docker cp /tmp/install.sh ubuntu18:/tmp/install.sh
  delegate_to: localhost

- name: 컨테이너에서 스크립트 실행
  ansible.builtin.raw: bash /tmp/install.sh
```

**`raw` + `delegate_to: localhost` 조합:**

```yaml
# docker cp + 실행을 localhost에서 모두 처리
# → 컨테이너 Python 유무와 완전히 무관
- name: Python 설치 (ubuntu18)
  ansible.builtin.raw: |
    docker cp /root/scripts/python311_ubuntu18.sh ubuntu18:/tmp/python_install.sh
    docker exec ubuntu18 bash /tmp/python_install.sh
  delegate_to: localhost
  when: inventory_hostname == 'ubuntu18'
```

주요 사용 사례:

| 사례 | 이유 |
|------|------|
| `docker cp` | Controller에서 실행하는 명령 |
| AWS CLI 호출 | Controller에 AWS 자격증명 있음 |
| 로컬 파일 생성/수정 | 대상 서버 불필요 |
| `run_once: true`와 조합 | 전체 중 1회만 실행 |

[⬆ 목차로 돌아가기](#목차)

---

## 15. 에러 처리

### block / rescue / always

Python의 try/except/finally 와 동일한 구조입니다.

```yaml
tasks:
  - block:
      - name: 패키지 설치 시도
        dnf:
          name: myapp
          state: present

      - name: 서비스 시작
        service:
          name: myapp
          state: started

    rescue:
      - name: 실패 시 롤백
        shell: /opt/myapp/rollback.sh

      - name: 알림 발송
        debug:
          msg: "배포 실패: {{ ansible_failed_result.msg }}"

    always:
      - name: 로그 수집 (성공/실패 무관)
        fetch:
          src: /var/log/myapp/deploy.log
          dest: ./logs/
```

### ignore_errors / failed_when

```yaml
tasks:
  - name: 프로세스 종료 (없어도 무시)
    shell: pkill myapp
    ignore_errors: true

  - name: 헬스체크 (응답코드 기준으로 실패 판단)
    uri:
      url: http://localhost:8080/health
      return_content: true
    register: health
    failed_when: health.status != 200 or 'ok' not in health.content

  - name: 디스크 사용률 확인 (90% 초과 시 실패)
    shell: df / | awk 'NR==2{print $5}' | tr -d '%'
    register: disk_usage
    failed_when: disk_usage.stdout | int > 90
    changed_when: false
```

### any_errors_fatal

한 호스트라도 실패하면 전체 play를 즉시 중단합니다.

```yaml
- name: 배포
  hosts: webservers
  any_errors_fatal: true   # 기본값 false
  tasks:
    - name: 배포 스크립트 실행
      shell: /opt/deploy.sh
```

[⬆ 목차로 돌아가기](#목차)

---

## 16. 태그

### 태그 작성

```yaml
tasks:
  - name: nginx 설치
    dnf:
      name: nginx
      state: present
    tags:
      - install
      - nginx

  - name: nginx 설정 배포
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    tags:
      - config
      - nginx

  - name: nginx 재시작
    service:
      name: nginx
      state: restarted
    tags:
      - restart
      - nginx

  - name: 항상 실행
    debug:
      msg: "always runs"
    tags:
      - always   # --tags 지정 시에도 항상 실행되는 특수 태그
```

### Role에 태그 적용

```yaml
# playbooks/site.yml
- hosts: webservers
  roles:
    - role: nginx
      tags: nginx          # role 전체에 태그 적용
    - role: mysql
      tags: mysql
```

### 실행 예시

```bash
# nginx 태그만 실행
ansible-playbook site.yml --tags nginx

# 설치 + 설정만 실행
ansible-playbook site.yml --tags "install,config"

# restart 제외하고 실행
ansible-playbook site.yml --skip-tags restart

# 어떤 task가 실행되는지 확인 (dry-run)
ansible-playbook site.yml --tags nginx --list-tasks
```

### 특수 태그

| 태그       | 동작                                          |
|------------|-----------------------------------------------|
| `always`   | `--tags` 지정 여부와 무관하게 항상 실행       |
| `never`    | `--tags never` 로 명시해야만 실행             |
| `tagged`   | 태그가 있는 task만 실행                       |
| `untagged` | 태그가 없는 task만 실행                       |
| `all`      | 모든 task 실행 (기본값)                       |

[⬆ 목차로 돌아가기](#목차)

---

## 17. Dynamic Inventory

정적 INI 파일 대신 AWS EC2 등 외부 소스에서 인벤토리를 동적으로 생성합니다.

### AWS EC2 플러그인 설정

```bash
pip install boto3 botocore
ansible-galaxy collection install amazon.aws
```

```yaml
# inventory/aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions:
  - ap-northeast-1
  - ap-northeast-2

filters:
  instance-state-name: running
  tag:Env: production          # Env=production 태그가 있는 인스턴스만

keyed_groups:
  - key: tags.Role             # Role 태그 값으로 그룹 생성
    prefix: role
  - key: placement.region      # 리전별 그룹
    prefix: region
  - key: instance_type         # 인스턴스 타입별 그룹
    prefix: type

hostnames:
  - private-ip-address         # 내부망 접속 시
  # - public-ip-address        # 외부 접속 시

compose:
  ansible_host: private_ip_address
```

### 사용 예시

```bash
# 인벤토리 확인
ansible-inventory -i inventory/aws_ec2.yml --list
ansible-inventory -i inventory/aws_ec2.yml --graph

# 특정 그룹 대상 실행
ansible role_webserver -i inventory/aws_ec2.yml -m ping

# playbook 실행
ansible-playbook -i inventory/aws_ec2.yml site.yml --limit role_webserver
```

### ansible.cfg 에 등록

```ini
[defaults]
inventory = inventory/aws_ec2.yml   # 기본 인벤토리로 지정
```

### 정적 + 동적 혼합

```
inventory/
├── aws_ec2.yml        # 동적 (AWS EC2)
├── group_vars/
│   ├── all.yml
│   └── role_webserver.yml
└── host_vars/
    └── bastion.yml    # 정적 호스트 개별 설정
```

```bash
# 디렉토리 전체를 인벤토리로 지정하면 자동으로 혼합 처리
ansible-playbook -i inventory/ site.yml
```

[⬆ 목차로 돌아가기](#목차)

---

## 18. Vault — 시크릿 관리

패스워드, API 키 등 민감한 값을 암호화하여 playbook에 포함합니다.

```bash
# 암호화된 파일 생성
ansible-vault create secrets.yml

# 기존 파일 암호화
ansible-vault encrypt vars/secrets.yml

# 복호화 (평문으로 저장 — 주의)
ansible-vault decrypt vars/secrets.yml

# 내용 확인 (복호화 없이)
ansible-vault view vars/secrets.yml

# 내용 수정
ansible-vault edit vars/secrets.yml

# 패스워드 변경
ansible-vault rekey vars/secrets.yml
```

```yaml
# vars/secrets.yml (암호화 전)
db_password: SecurePassword123
api_key: SecureKey123
```

```yaml
# playbook에서 사용
- name: DB 설정
  hosts: dbservers
  vars_files:
    - vars/secrets.yml    # vault 파일 포함

  tasks:
    - name: DB 패스워드 설정
      template:
        src: my.cnf.j2
        dest: /etc/mysql/my.cnf
      no_log: true        # 로그에 민감한 값 출력 방지
```

```bash
# 실행 시 vault 패스워드 입력
ansible-playbook site.yml --ask-vault-pass

# 패스워드 파일 사용 (CI/CD 환경)
ansible-playbook site.yml --vault-password-file ~/.vault_pass
```

🟡 `.vault_pass` 파일은 `.gitignore`에 반드시 추가합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Ansible Documentation: [docs.ansible.com](https://docs.ansible.com/) — ★★★☆☆
- Ansible Best Practices: [docs.ansible.com/tips_tricks](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-04-27

**마지막 업데이트**: 2026-05-22

© 2026 siasia86. Licensed under CC BY 4.0.

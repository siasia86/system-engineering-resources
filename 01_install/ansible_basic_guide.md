# Ansible 기초 가이드

## 1. 개요

Ansible은 에이전트 없이 SSH로 대상 서버를 관리하는 자동화 도구입니다.

```
Control Node (내 서버)  ──SSH──>  Managed Node (대상 서버)

명령 실행 방식:
  ad-hoc   → 1회성 명령 (ansible 명령어)
  playbook → 반복 가능한 자동화 (ansible-playbook 명령어)
```

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
# 인벤토리 확인
ansible-inventory -i inventory/dev --list
ansible-inventory -i inventory/dev --graph
```

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

```bash
# 실행
ansible-playbook -i inventory/dev playbooks/hello.yml

# 문법 체크만
ansible-playbook -i inventory/dev playbooks/hello.yml --syntax-check

# 변경 없이 시뮬레이션 (dry-run)
ansible-playbook -i inventory/dev playbooks/hello.yml --check

# 특정 호스트만
ansible-playbook -i inventory/dev playbooks/hello.yml --limit dev-app-web-01

# 상세 출력 (-v, -vv, -vvv 로 단계 조절)
ansible-playbook -i inventory/dev playbooks/hello.yml -v
```

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

---

## 11. 자주 쓰는 실행 옵션

| 옵션                     | 설명                     |
|--------------------------|--------------------------|
| `-i inventory/dev`       | 인벤토리 파일 지정       |
| `--check`                | dry-run (실제 변경 없음) |
| `--diff`                 | 파일 변경 내용 diff 출력 |
| `--limit host1`          | 특정 호스트만 실행       |
| `--tags deploy`          | 특정 태그만 실행         |
| `--skip-tags debug`      | 특정 태그 제외           |
| `--step`                 | task 마다 확인 후 실행   |
| `--start-at-task "이름"` | 특정 task 부터 실행      |
| `-e "key=value"`         | 변수 전달 (최우선)       |
| `-v / -vv / -vvv`        | 상세 출력 단계           |
| `--list-tasks`           | 실행할 task 목록만 출력  |
| `--list-hosts`           | 대상 호스트 목록만 출력  |

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

---

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

---

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

---

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

---

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

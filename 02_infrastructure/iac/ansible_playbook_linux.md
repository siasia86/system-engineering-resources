# Ansible Playbook Linux 가이드

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 연결 설정](#1-연결-설정) / [2. 자주 쓰는 모듈](#2-자주-쓰는-모듈) / [3. Ad-hoc 명령](#3-ad-hoc-명령) |
| [4. OS별 분기 패턴](#4-os별-분기-패턴) / [5. Playbook 예시](#5-playbook-예시)                            |

> 공통 필드는 [ansible_playbook_fields.md](ansible_playbook_fields.md) 참고

---

## 1. 연결 설정

### inventory.ini

```ini
[linux]
ubuntu22 ansible_host=10.200.101.151
rocky9   ansible_host=10.200.101.154

[linux:vars]
ansible_user=ansible    # 전용 계정 권장 (root 직접 사용 지양)
ansible_ssh_private_key_file=~/.ssh/id_ed25519
ansible_connection=ssh
```

> 🟡 `ansible_user=root` 직접 사용은 보안상 권장하지 않습니다.
> 전용 `ansible` 계정을 생성하고 `become: true`로 권한 상승하는 방식을 사용합니다.

### Docker 컨테이너 연결

```ini
[docker]
ubuntu22 ansible_connection=docker ansible_host=02_compose-ubuntu22-1
rocky9   ansible_connection=docker ansible_host=02_compose-rocky9-1

[docker:vars]
ansible_remote_tmp=/tmp/.ansible/tmp
```

---

## 2. 자주 쓰는 모듈

### 패키지 관리

```yaml
# OS 무관 (자동 감지)
# 🟡 curl은 Rocky9/AmazonLinux2023에서 curl-minimal과 충돌 가능
# 해당 OS에서는 아래 OS별 모듈로 분기 처리 권장
- ansible.builtin.package:
    name: wget           # curl 대신 충돌 없는 패키지로 테스트
    state: present       # present / absent / latest

# Debian 계열 전용
- ansible.builtin.apt:
    name: nginx
    state: present
    update_cache: true

# RedHat 계열 전용 (RHEL 7 / CentOS 7)
- ansible.builtin.yum:
    name: nginx
    state: present

# RHEL 8+ / Rocky 9+ / AlmaLinux 8+ 권장
- ansible.builtin.dnf:
    name: nginx
    state: present
```

### 서비스 관리

```yaml
- ansible.builtin.service:
    name: nginx
    state: started       # started / stopped / restarted / reloaded
    enabled: true        # 부팅 시 자동 시작
```

### 파일/디렉토리

```yaml
- ansible.builtin.file:
    path: /etc/myapp
    state: directory     # directory / file / absent / touch / link
    mode: "0755"
    owner: root
    group: root

- ansible.builtin.copy:
    src: files/nginx.conf
    dest: /etc/nginx/nginx.conf
    mode: "0644"
    backup: true         # 기존 파일 백업

- ansible.builtin.template:
    src: templates/nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    mode: "0644"
```

### 사용자/그룹

```yaml
- ansible.builtin.user:
    name: ansible
    shell: /bin/bash
    groups: sudo
    append: true

# ansible.posix.authorized_key는 Ansible 2.15+에서 deprecated
# ansible.builtin.authorized_key 사용 권장
- ansible.builtin.authorized_key:
    user: ansible
    key: "{{ lookup('file', '~/.ssh/id_ed25519.pub') }}"
```

### 명령 실행

```yaml
# 단순 명령 (파이프/리다이렉트 불가)
- ansible.builtin.command: systemctl restart nginx
  changed_when: true

# 쉘 명령 (파이프/리다이렉트 가능)
- ansible.builtin.shell: ps aux | grep nginx | wc -l
  register: result

# 멱등성 보장 (이미 실행된 경우 스킵)
- ansible.builtin.command: /usr/bin/myapp --init
  args:
    creates: /var/lib/myapp/.initialized
```

### 설정 파일 수정

```yaml
# 특정 줄 추가/수정
- ansible.builtin.lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^#?PermitRootLogin'
    line: 'PermitRootLogin no'

# 블록 삽입
- ansible.builtin.blockinfile:
    path: /etc/hosts
    block: |
      10.200.101.151 ubuntu22
      10.200.101.154 rocky9
```

---

## 3. Ad-hoc 명령

```bash
# 연결 테스트
ansible all -m ansible.builtin.ping

# 명령 실행
ansible all -a "uptime"
ansible all -a "df -h"
ansible all -a "free -m"

# 파이프 사용 (shell 모듈)
ansible all -m shell -a "ps aux | grep sshd"

# 패키지 설치
ansible all -m ansible.builtin.package -a "name=wget state=present" -b
# curl은 Rocky9/AmazonLinux2023에서 curl-minimal 충돌 가능 — wget 권장

# 서비스 재시작
ansible all -m ansible.builtin.service -a "name=nginx state=restarted" -b

# 파일 복사
ansible all -m ansible.builtin.copy -a "src=/tmp/test.txt dest=/tmp/test.txt"
```

---

## 4. OS별 분기 패턴

```yaml
- name: OS별 패키지 설치
  hosts: all
  tasks:
    - name: Debian 계열
      ansible.builtin.apt:
        name: nginx
        state: present
        update_cache: true
      when: ansible_os_family == "Debian"

    - name: RedHat 계열
      ansible.builtin.yum:
        name: nginx
        state: present
      when: ansible_os_family == "RedHat"
```

### 자주 쓰는 `ansible_*` 변수

| 변수                           | 예시 값            | 설명             |
|--------------------------------|--------------------|------------------|
| `ansible_os_family`            | `Debian`, `RedHat` | OS 계열          |
| `ansible_distribution`         | `Ubuntu`, `Rocky`  | 배포판 이름      |
| `ansible_distribution_version` | `22.04`, `9.3`     | 버전             |
| `ansible_hostname`             | `ubuntu22`         | 호스트명         |
| `ansible_default_ipv4.address` | `10.200.101.151`   | 기본 IP          |
| `ansible_memtotal_mb`          | `28610`            | 전체 메모리 (MB) |

---

## 5. Playbook 예시

### 기본 서버 설정

```yaml
---
- name: 기본 서버 설정
  hosts: linux
  become: true
  tasks:
    - name: 패키지 업데이트 (Debian)
      ansible.builtin.apt:
        update_cache: true
        upgrade: safe
      when: ansible_os_family == "Debian"

    - name: 필수 패키지 설치
      ansible.builtin.package:
        name:
          - wget
          - vim
          # curl은 Rocky9/AmazonLinux2023에서 curl-minimal과 충돌 — OS별 분기 필요
        state: present

    - name: 타임존 설정
      # community.general 컬렉션 필요: ansible-galaxy collection install community.general
      community.general.timezone:
        name: Asia/Seoul

    - name: SSH root 로그인 비활성화
      ansible.builtin.lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?PermitRootLogin'
        line: 'PermitRootLogin no'
      notify: restart sshd

  handlers:
    - name: restart sshd
      ansible.builtin.service:
        name: sshd
        state: restarted
```

---

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Ansible Docs — Module Index: [docs.ansible.com](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/) — ★★★☆☆
- Ansible Docs — Linux Guide: [docs.ansible.com](https://docs.ansible.com/ansible/latest/playbook_guide/) — ★★★☆☆

---

**작성일**: 2026-05-19

**마지막 업데이트**: 2026-05-19

© 2026 siasia86. Licensed under CC BY 4.0.

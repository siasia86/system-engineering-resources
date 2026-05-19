# Ansible Playbook 필드 레퍼런스 (공통)

## 목차

| 섹션 |
|------|
| [1. Play 레벨 필드](#1-play-레벨-필드) / [2. Task 레벨 필드](#2-task-레벨-필드) / [3. register 변수 필드](#3-register-변수-필드) |
| [4. 조건/반복 필드](#4-조건반복-필드) / [5. 권한 상승](#5-권한-상승) / [6. 자주 쓰는 패턴](#6-자주-쓰는-패턴) |

> OS별 상세는 [ansible_playbook_linux.md](ansible_playbook_linux.md) / [ansible_playbook_windows.md](ansible_playbook_windows.md) 참고

---

## 1. Play 레벨 필드

Play 전체에 적용되는 설정입니다.

```yaml
- name: Play 이름          # 필수 권장 — 로그에 표시
  hosts: all               # 대상 호스트/그룹 (inventory 그룹명 또는 all)
  become: true             # 권한 상승 활성화 (sudo/runas)
  become_user: root        # 상승할 계정 (기본값: root)
  gather_facts: true       # ansible_* 변수 수집 여부 (기본값: true)
  vars:                    # Play 범위 변수
    key: value
  vars_files:              # 외부 변수 파일 로드
    - vars/secrets.yml
  environment:             # 환경변수 설정
    PATH: /usr/local/bin
  serial: 2                # 롤링 업데이트 — 한 번에 처리할 호스트 수 (또는 "20%")
  max_fail_percentage: 10  # 실패 허용 비율 초과 시 전체 중단
```

| 필드           | 기본값 | 설명                              |
|----------------|--------|-----------------------------------|
| `hosts`        | 없음   | 필수. inventory 그룹명 또는 IP    |
| `become`       | false  | sudo/runas 권한 상승              |
| `gather_facts` | true   | 느린 경우 `false`로 비활성화      |
| `vars`         | -      | 인라인 변수 정의                  |
| `vars_files`   | -      | 외부 yml 파일에서 변수 로드       |
| `environment`  | -      | 환경변수 (모든 task에 적용)       |
| `serial`       | -      | 롤링 업데이트 — 한 번에 처리할 호스트 수/비율 |
| `max_fail_percentage` | 0 | 실패 허용 비율 초과 시 playbook 중단 |

---

## 2. Task 레벨 필드

개별 task에 적용되는 설정입니다.

```yaml
tasks:
  - name: 작업 이름                      # 필수 권장
    ansible.builtin.package:             # 모듈명 (FQCN 권장)
      name: curl
      state: present
    register: result                     # 실행 결과 변수 저장
    when: ansible_os_family == "Debian"  # 조건부 실행
    loop: "{{ packages }}"               # 반복 실행
    notify: restart nginx                # handler 호출
    ignore_errors: true                  # 실패 무시
    changed_when: false                  # changed 상태 강제 설정
    failed_when: result.rc != 0          # 실패 조건 커스텀
    tags: install                        # 태그 (--tags 옵션으로 선택 실행)
    timeout: 30                          # task 타임아웃 (초)
    vars:                                # task 범위 변수
      key: value
    delegate_to: localhost                # 다른 호스트에서 실행 (localhost 등)
    run_once: true                        # 전체 호스트 중 1회만 실행
```

| 필드            | 설명                                              |
|-----------------|---------------------------------------------------|
| `register`      | 결과를 변수에 저장 — 이후 task에서 참조 가능      |
| `when`          | 조건이 true일 때만 실행                           |
| `loop`          | 리스트 반복 — 각 항목은 `{{ item }}`으로 참조     |
| `notify`        | task가 changed일 때 handler 호출                  |
| `ignore_errors` | 실패해도 다음 task 계속 실행                      |
| `changed_when`  | changed 판단 기준 커스텀 (false면 항상 ok)        |
| `failed_when`   | 실패 판단 기준 커스텀                             |
| `tags`          | `--tags`, `--skip-tags`로 선택 실행               |
| `timeout`       | task 최대 실행 시간 (초)                          |
| `delegate_to`   | 지정한 호스트에서 task 실행 (예: `localhost`)      |
| `run_once`      | 전체 호스트 중 첫 번째 호스트에서만 1회 실행      |

---

## 3. register 변수 필드

`register`로 저장한 변수에서 자주 쓰는 필드입니다.

```yaml
- name: 명령 실행
  ansible.builtin.command: cat /etc/os-release
  register: result

- name: 결과 확인
  ansible.builtin.debug:
    msg: "{{ result.stdout_lines }}"
```

| 필드                  | 타입   | 설명                               |
|-----------------------|--------|------------------------------------|
| `result.stdout`       | string | 표준 출력 전체                     |
| `result.stdout_lines` | list   | 표준 출력 줄 단위 리스트           |
| `result.stderr`       | string | 표준 에러 출력                     |
| `result.rc`           | int    | 종료 코드 (0 = 성공)               |
| `result.changed`      | bool   | 변경 발생 여부                     |
| `result.failed`       | bool   | 실패 여부                          |
| `result.skipped`      | bool   | 스킵 여부                          |
| `result.msg`          | string | 모듈 메시지 (일부 모듈)            |
| `result.results`      | list   | `loop` 사용 시 각 항목 결과 리스트 |

### 조건에서 활용

```yaml
- name: 서비스 재시작
  ansible.builtin.service:
    name: nginx
    state: restarted
  when: result.rc == 0

- name: 에러 출력
  ansible.builtin.debug:
    msg: "{{ result.stderr }}"
  when: result.failed
```

---

## 4. 조건/반복 필드

### `when` — 조건부 실행

```yaml
# 아래 예시는 task 내부의 when 필드 값만 표시
# OS 계열 조건
when: ansible_os_family == "RedHat"

# 변수 존재 여부
when: my_var is defined

# 복합 조건
when:
  - ansible_distribution == "Ubuntu"
  - ansible_distribution_version is version('20.04', '>=')

# 이전 task 결과 기반
when: result.rc != 0
```

### `loop` — 반복 실행

```yaml
# 리스트 반복
- name: 패키지 설치
  ansible.builtin.package:
    name: "{{ item }}"
    state: present
  loop:
    - curl
    - wget
    - git

# 딕셔너리 반복
- name: 파일 생성
  ansible.builtin.file:
    path: "{{ item.path }}"
    mode: "{{ item.mode }}"
  loop:
    - { path: /tmp/a, mode: "0644" }
    - { path: /tmp/b, mode: "0755" }
```

### `block` — task 그룹화 및 에러 처리

```yaml
- block:
    - name: 설치 시도
      ansible.builtin.package:
        name: nginx
        state: present
  rescue:
    - name: 실패 시 알림
      ansible.builtin.debug:
        msg: "설치 실패"
  always:
    - name: 항상 실행
      ansible.builtin.debug:
        msg: "완료"
```

---

## 5. 권한 상승

```yaml
# Play 전체 적용
- hosts: all
  become: true
  become_user: root

# 특정 task만 적용
- name: root 권한 필요
  ansible.builtin.command: systemctl restart nginx
  become: true

# Windows runas
- hosts: windows
  become: true
  become_method: runas
  become_user: SYSTEM
```

| 필드            | 설명                                        |
|-----------------|---------------------------------------------|
| `become`        | 권한 상승 활성화                            |
| `become_user`   | 상승할 계정 (Linux: root, Windows: SYSTEM)  |
| `become_method` | 방법 (Linux: sudo, Windows: runas)          |

---

## 6. 자주 쓰는 패턴

### 변수 출력

```yaml
- ansible.builtin.debug:
    msg: "{{ 변수명 }}"

- ansible.builtin.debug:
    var: result    # 변수 전체 구조 출력 (디버깅용)
```

### 파일에서 변수 로드

```yaml
vars_files:
  - vars/common.yml
  - "vars/{{ ansible_os_family }}.yml"    # OS별 변수 파일
```

### handler

```yaml
tasks:
  - name: nginx 설정 변경
    ansible.builtin.template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: restart nginx

handlers:
  - name: restart nginx
    ansible.builtin.service:
      name: nginx
      state: restarted
```

### check mode (dry-run)

```bash
ansible-playbook playbook.yml --check    # 실제 변경 없이 시뮬레이션
ansible-playbook playbook.yml --diff     # 변경 전후 diff 출력
```

---

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Ansible Docs — Playbook Keywords: [docs.ansible.com](https://docs.ansible.com/ansible/latest/reference_appendices/playbooks_keywords.html) — ★★★☆☆
- [ansible_playbook_linux.md](ansible_playbook_linux.md)
- [ansible_playbook_windows.md](ansible_playbook_windows.md)

---

**작성일**: 2026-05-19

**마지막 업데이트**: 2026-05-19

© 2026 siasia86. Licensed under CC BY 4.0.

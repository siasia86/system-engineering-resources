---
name: ansible-official-notes
description: Ansible 공식 문서 기반 핵심 개념, 버전, 구성요소 정리.
last_checked: 2026-05-26
sources:
  - https://www.ansible.com/
  - https://docs.ansible.com/ansible/latest/getting_started/index.html
  - https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html
---

# Ansible 공식 문서 참조 노트

## 1. 버전 현황 (확인일: 2026-05-26)

| 패키지       | 최신 버전 | 비고                                          |
|--------------|-----------|-----------------------------------------------|
| ansible      | 13.7.0    | ansible-core + 커뮤니티 컬렉션 풀 패키지      |
| ansible-core | 2.21.0    | 최소 코어 (ansible 패키지에 포함됨)           |

- ansible 버전과 ansible-core 버전은 별개 (ansible 13.x = ansible-core 2.21)
- control node: ansible-core 2.12+부터 최근 3개 Python 버전 지원
- managed node: ansible-core 2.16+부터 최근 6개 Python 버전 지원
- Python 2.7은 ansible-core 2.16까지만 지원

## 2. 핵심 개념

| 용어           | 설명                                                        |
|----------------|-------------------------------------------------------------|
| Control node   | Ansible이 설치된 서버, 여기서 playbook 실행                 |
| Managed node   | 관리 대상 서버, 에이전트 불필요 (SSH 접속)                  |
| Inventory      | 관리 대상 호스트 목록 (INI / YAML)                          |
| Playbook       | 자동화 작업을 순서대로 정의한 YAML 파일                     |
| Task           | Playbook의 단일 작업 단위                                   |
| Module         | Task가 실행하는 기능 단위 (package, file, service 등)       |
| Role           | Playbook을 재사용 가능한 구조로 패키징                      |
| Collection     | Module + Role + Plugin 묶음 (Galaxy에서 배포)               |
| Handler        | notify로 트리거되는 Task (서비스 재시작 등)                 |

## 3. 공식 정의

> "Ansible is an open source IT automation engine that automates
> provisioning, configuration management, application deployment,
> orchestration, and many other IT processes."
> — docs.ansible.com

## 4. 특징

- **Agentless**: 관리 대상에 별도 소프트웨어 불필요, SSH/WinRM 사용
- **Idempotent**: 동일 playbook 반복 실행 시 결과 동일
- **Declarative + Procedural**: 모듈은 선언적, 실행 순서는 절차적
- **Push 방식**: control node에서 managed node로 푸시

## 5. 주요 파일 구조

```
project/
├── inventory.ini          # 호스트 목록
├── ansible.cfg            # 설정 파일
├── playbook.yml           # 메인 playbook
└── roles/
    └── webserver/
        ├── tasks/main.yml
        ├── handlers/main.yml
        └── templates/
```

## 6. 주의사항

- Windows 관리 시 WinRM 또는 OpenSSH 필요
- `become: true` = sudo 권한 상승
- `gather_facts: false` 설정 시 ansible_* 변수 사용 불가
- Python 인터프리터 경로 불일치 시 `ansible_python_interpreter` 명시 필요

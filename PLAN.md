# 공용 `sia_scripts` 도입 계획

## 목차

| 섹션                                                         |
|--------------------------------------------------------------|
| [1. 배경](#1-배경) / [2. 목표](#2-목표) / [3. 범위](#3-범위) |
| [4. 권장 구성](#4-권장-구성) / [5. 단계](#5-단계)            |
| [6. 검증 기준](#6-검증-기준) / [7. 롤백](#7-롤백)            |
| [8. 비가역 작업](#8-비가역-작업)                             |

---

## 1. 배경

`/root/32_system-engineering-resources`에 Markdown 검사기와 환경별 운영 스크립트가 함께 증가하고 있습니다. 여러 성격의 저장소에 동일한 품질·보안 검증을 적용하려면 공용 도구와 저장소 전용 도구를 분리해야 합니다.

현재 공용화 후보인 `md-style-check.py`, `md-heading-check.py`, `md-link-check.py`에는 저장소 경로 또는 현재 저장소 정책에 대한 의존성이 있습니다. 이를 그대로 `/usr/local/bin`에 복사하면 다른 저장소에서 오작동하거나 저장소별 예외가 공용 코드에 누적될 수 있습니다.

`TODO2.md`는 존재하지 않으며, 이 작업은 세 단계 이상의 복합 작업이므로 루트 `PLAN.md`에 기록합니다.

## 2. 목표

여러 저장소에서 재사용할 수 있는 `sia_scripts` 공용 검증 도구를 설계하고, 저장소별 정책을 설정 파일로 분리하여 버전 관리·검증·롤백 가능한 방식으로 설치합니다.

완료 기준은 다음과 같습니다.

- 공용 도구와 저장소 전용 도구의 분류가 완료됩니다.
- 공용 후보가 특정 저장소 경로 없이 동작합니다.
- 저장소별 예외와 규칙이 설정으로 분리됩니다.
- 버전별 설치와 이전 버전 롤백이 가능합니다.
- 기존 저장소 검사 결과와 신규 명령 결과가 일치합니다.

## 3. 범위

### 포함

- `md-style-check.py`, `md-heading-check.py`, `md-link-check.py` 공용화 검토
- `readme_inventory_check.py`의 저장소 정책 의존성 검토
- 공용 CLI 이름과 설정 형식 정의
- `/usr/local/lib/sia_scripts/` 버전별 설치 구조 설계
- `/usr/local/bin/sia-*` 실행 명령 노출
- Private repository의 CI artifact를 Ansible 제어 서버가 배포하는 절차 작성
- 저장소별 CI와 Ansible 배포 workflow 정의
- 설치 전후 검증과 롤백 절차 작성

### 제외

- `02_infrastructure/web_server/nginx_geoip2_install.sh`의 공용화
  - 특정 인프라 설치 절차이므로 해당 프로젝트에 유지합니다.
- `00_governance/02_kiro/02_home-sjyun-kiro.sh`의 공용화
  - Kiro 원본·미러 동기화에 종속되므로 현재 저장소에 유지합니다.
- `96_scripts/windows/*.py`의 Linux 공용 명령화
  - Windows 운영 도구로 별도 배포 단위를 검토합니다.
- 첫 단계에서의 모든 저장소 강제 전환
  - 호환성 검증 후 단계적으로 적용합니다.

## 4. 권장 구성

### 저장소 이름

공용 검증·운영 스크립트의 원본과 배포 workflow를 관리하는 Private repository 이름은 `sia-scripts`를 권장합니다. `system-engineering-resources`는 문서 저장소 성격이 강하고, `_private`는 접근 범위를 설명하는 로컬 경로 규칙이므로 repository 이름에 포함하지 않습니다.

로컬 checkout 경로에 기존 숫자 규칙을 적용할 경우 다음과 같이 사용합니다.

```text
Repository: sia-scripts
Local path: /root/34_sia-scripts_private/
```

`34_system-engineering-resources_private`라는 이름은 문서 저장소와 역할이 혼동될 수 있으므로 사용하지 않습니다.

### 배포 구성

```text
Private repository: sia-scripts
        │
        v
GitHub Actions
  CI / test / gitleaks / package
        │
        v
Versioned release artifact
        │  outbound HTTPS 443
        v
Ansible 제어 서버
  artifact 다운로드 / checksum 검증
        │  outbound SSH 또는 WinRM
        v
대상 호스트
  /opt/sia_scripts/releases/<version>
  /usr/local/bin/sia-*
```

GitHub-hosted Actions가 Ansible 서버로 직접 SSH 접속하지 않습니다. Ansible 제어 서버가 GitHub Release 또는 사설 artifact 저장소에서 지정된 버전을 outbound HTTPS로 가져온 뒤 대상 호스트에 배포합니다.

### 방화벽 작업

- Ansible 제어 서버 → GitHub Release 또는 artifact 저장소: outbound TCP 443 허용
- Ansible 제어 서버 → 대상 Linux 호스트: 관리망의 outbound TCP 22 허용
- Ansible 제어 서버 → 대상 Windows 호스트: 필요한 경우 관리망의 outbound WinRM 포트 허용
- GitHub Actions → Ansible 제어 서버: inbound SSH 허용하지 않음
- GitHub Actions IP 전체 범위를 Ansible 서버 방화벽에 등록하지 않음

방화벽 변경은 실제 네트워크 경로와 대상 호스트를 확인한 뒤 Ansible inventory와 방화벽 정책에 선언적으로 반영합니다. 운영 중인 inbound 정책을 삭제하거나 완화하지 않으며, 신규 outbound 허용은 최소 목적지와 포트로 제한합니다.

## 5. 단계

각 단계는 검증을 통과한 뒤 다음 단계로 진행합니다.

### 단계 1. 스크립트 분류와 인터페이스 정의

- [ ] 저장소 스크립트를 공용·정책 종속·환경 종속으로 분류합니다.
- [ ] 공용 후보의 입력 경로, 반환 코드, 출력 형식을 정의합니다.
- [ ] `sia-md-style-check`, `sia-md-heading-check`, `sia-md-link-check` 명령 이름을 확정합니다.
- [ ] 저장소별 설정 파일의 위치와 형식을 정의합니다.
- [ ] 검증: 각 스크립트의 공용화 여부와 제외 사유가 표로 남아 있습니다.

### 단계 2. 공용 후보의 저장소 의존성 제거

- [ ] `/root/32_system-engineering-resources/` 하드코딩을 제거합니다.
- [ ] 대상 경로를 명령행 인자로 받도록 통일합니다.
- [ ] 저장소별 예외를 코드가 아닌 `--config` 또는 profile로 처리합니다.
- [ ] `--help`, `--version`, `--dry-run` 동작을 확인합니다.
- [ ] 검증: 기존 저장소와 임시 테스트 저장소에서 동일한 CLI가 실행됩니다.

### 단계 3. 테스트와 기존 결과 대조

- [ ] 정상 문서, 잘못된 헤딩, 깨진 링크, 표 정렬 오류를 포함한 테스트 fixture를 작성합니다.
- [ ] 기존 스크립트와 공용 명령의 결과·반환 코드를 비교합니다.
- [ ] 저장소별 예외가 의도한 파일에만 적용되는지 확인합니다.
- [ ] 검증: 테스트 결과와 현재 저장소 전체 검사 결과가 일치합니다.

### 단계 4. 패키징과 설치 구조 구현

- [ ] `/usr/local/lib/sia_scripts/releases/<version>/` 구조를 구현합니다.
- [ ] `/usr/local/lib/sia_scripts/current` symlink 전환 방식을 적용합니다.
- [ ] `/usr/local/bin/sia-*` 실행 명령을 설치합니다.
- [ ] Ansible role 또는 playbook으로 artifact 다운로드, checksum 검증, release 설치를 구현합니다.
- [ ] 설치 파일의 소유자·권한을 `root:root`, 디렉토리 `0755`, 일반 파일 `0644`, 실행 파일 `0755` 기준으로 확인합니다.
- [ ] 검증: 버전 출력, 도움말 출력, 비권한 사용자의 읽기·실행, 쓰기 차단을 확인합니다.

### 단계 5. CI artifact와 Ansible 배포 workflow의 단계적 적용

- [ ] 각 저장소가 사용할 profile과 버전을 명시하도록 합니다.
- [ ] GitHub Actions가 테스트·보안 검증 후 버전 고정 artifact를 생성하도록 합니다.
- [ ] Ansible 제어 서버가 지정된 artifact와 checksum을 outbound HTTPS로 받아 배포하도록 합니다.
- [ ] GitHub Actions에서 Ansible 제어 서버로의 inbound SSH가 필요하지 않음을 확인합니다.
- [ ] 첫 적용 대상 1개 호스트와 1개 저장소에서 검증합니다.
- [ ] 결과 확인 후 적용 대상을 단계적으로 확대합니다.
- [ ] 검증: 기존 workflow 대비 누락된 검사와 신규 오탐이 없습니다.

### 단계 6. 운영 문서화와 완료 정리

- [ ] 설치·업데이트·롤백 명령을 운영 문서에 기록합니다.
- [ ] 장애 발생 시 이전 버전으로 전환하는 절차를 확인합니다.
- [ ] 완료된 단계와 최종 결과를 `CHANGELOG.md`에 기록합니다.
- [ ] 완료 후 이 `PLAN.md`를 완료 상태로 정리하거나 제거합니다.
- [ ] 검증: 전체 Markdown·링크·비밀정보 검사를 통과합니다.

## 6. 검증 기준

```bash
sudo python3 md-style-check.py /root/32_system-engineering-resources
sudo python3 md-heading-check.py /root/32_system-engineering-resources
sudo python3 md-link-check.py /root/32_system-engineering-resources
sudo python3 readme_inventory_check.py README.md
ansible-playbook --syntax-check install/sia_scripts.yml
git diff --check
gitleaks detect --source /root/32_system-engineering-resources --no-git --no-banner
```

- [ ] 공용 명령의 `--help`와 `--version`이 정상 동작합니다.
- [ ] 공용 명령이 특정 저장소의 절대경로 없이 동작합니다.
- [ ] 정상·오류 fixture 테스트가 통과합니다.
- [ ] 기존 검사 결과와 신규 검사 결과가 일치합니다.
- [ ] 저장소별 예외가 설정 파일에만 존재합니다.
- [ ] 실행 파일 권한과 일반 사용자 쓰기 차단을 확인합니다.
- [ ] Ansible playbook syntax check와 lint를 통과합니다.
- [ ] Ansible 제어 서버에서 artifact 저장소로 HTTPS 연결이 확인됩니다.
- [ ] Ansible 제어 서버에서 대상 호스트로 Ansible 연결이 확인됩니다.
- [ ] artifact checksum 검증 후 설치됩니다.
- [ ] 설치·업데이트·롤백 smoke test를 통과합니다.
- [ ] Markdown·링크·헤딩·비밀정보 검사를 통과합니다.
- [ ] `CHANGELOG.md`에 최종 결과를 기록합니다.

검증 실패를 공용 검사 예외로 숨기지 않습니다. 예외가 필요하면 대상, 사유, 재검토 시점을 별도로 기록합니다.

## 7. 롤백

| 단계   | 롤백 방법                                                             | 되돌리기 어려운 지점 |
|--------|-----------------------------------------------------------------------|----------------------|
| 단계 1 | 분류·설정 문서 변경을 이전 commit으로 복원합니다.                     | 없음                 |
| 단계 2 | 공용 후보 변경을 이전 commit 또는 기존 스크립트로 복원합니다.         | 없음                 |
| 단계 3 | 신규 fixture와 테스트 코드를 제거하거나 이전 commit으로 복원합니다.   | 없음                 |
| 단계 4 | Ansible 변수의 release 버전을 이전 버전으로 지정해 재실행합니다.      | 없음                 |
| 단계 5 | 각 저장소의 고정 버전과 Ansible 배포 대상을 이전 버전으로 되돌립니다. | 없음                 |
| 단계 6 | 완료 기록을 이전 commit으로 복원합니다.                               | 없음                 |

Ansible은 기존 release를 삭제하지 않고 신규 release를 별도 경로에 설치합니다. artifact checksum과 smoke test를 통과한 경우에만 `current` symlink를 전환합니다. 실패하면 Ansible 변수의 release 버전을 이전 버전으로 지정해 재실행합니다.

## 8. 비가역 작업

| 작업      | 비가역 사유                                                            | 승인 필요 |
|-----------|------------------------------------------------------------------------|-----------|
| 해당 없음 | 파일 삭제, 이력 재작성, force push, 자격증명 삭제를 수행하지 않습니다. | 해당 없음 |

버전 전환과 명령어 설치는 기존 release를 보존하므로 롤백 가능합니다.

---

**작성일**: 2026-08-27

**마지막 업데이트**: 2026-08-27

© 2026 siasia86. Licensed under CC BY 4.0.

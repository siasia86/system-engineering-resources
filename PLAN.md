# 공용 `sia_scripts` 도입 계획

## 목차

| 섹션                                                         |
|--------------------------------------------------------------|
| [1. 배경](#1-배경) / [2. 목표](#2-목표) / [3. 범위](#3-범위) |
| [4. 권장 구성](#4-권장-구성) / [5. 단계](#5-단계)            |
| [6. 검증 기준](#6-검증-기준) / [7. 롤백](#7-롤백)            |
| [8. 비가역 작업](#8-비가역-작업)                             |
| [9. 현재 상태와 다음 작업](#9-현재-상태와-다음-작업)         |

---

## 1. 배경

`/root/32_system-engineering-resources`에 Markdown 검사기와 환경별 운영 스크립트가 함께 증가했습니다. 여러 성격의 저장소에 동일한 품질·보안 검증을 적용하기 위해 공용 source와 저장소 전용 policy를 분리했습니다.

기존 root checker 4개는 30 `sia_scripts`의 versioned release wrapper로 이관했으며, 32에는 repository policy와 CI consumer만 유지합니다.

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

- 30 `sia_scripts` release의 `sia-md-style-check`, `sia-md-heading-check`, `sia-md-link-check` wrapper 전환 완료
- 30 `sia_scripts` release의 `sia-readme-inventory-check` wrapper 전환 완료
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

공용 검증·운영 스크립트의 원본과 배포 workflow를 관리하는 Private repository 이름은 `30_sia-scripts`를 권장합니다. `system-engineering-resources`는 문서 저장소 성격이 강하고, `_private`는 접근 범위를 설명하는 로컬 경로 규칙이므로 repository 이름에 포함하지 않습니다.

로컬 checkout 경로에 기존 숫자 규칙을 적용할 경우 다음과 같이 사용합니다.

```text
Repository: 30_sia-scripts
Remote: `git@github.com:siasia86/30_sia-scripts.git`
Description: 공용 시스템 엔지니어링·문서 품질 검증 스크립트와 Ansible 배포 자동화
Local path: $HOME/30_sia-scripts/
```

`34_system-engineering-resources_private`와 같은 문서 저장소 기반 이름은 역할이 혼동될 수 있으므로 사용하지 않습니다.

### 배포 구성

```text
Private repository: 30_sia-scripts
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

초기 분류와 CLI 계약은 다음과 같이 확정합니다.

| 후보                        | 분류                  | 현재 판단                                  |
|-----------------------------|-----------------------|--------------------------------------------|
| `md-style-check.py`         | 공용 후보 + 설정 의존 | 32 전용 `FILE_SKIP` 제거 후 `src/`로 이관  |
| `md-heading-check.py`       | 공용 후보 + 설정 의존 | 대상 경로·TOML 설정을 사용                 |
| `md-link-check.py`          | 공용 후보             | 상대경로 링크와 종료 코드만 사용           |
| `readme_inventory_check.py` | 조건부 공용 후보      | `(N개)` inventory 형식의 저장소에서만 사용 |

- [x] 저장소 스크립트를 공용·정책 종속·환경 종속으로 분류합니다.
- [x] 공용 후보의 입력 경로, 반환 코드, 출력 형식을 정의합니다.
- [x] `sia-md-style-check`, `sia-md-heading-check`, `sia-md-link-check` 명령 이름을 확정합니다.
- [x] 저장소별 설정 파일의 위치와 형식을 정의합니다.
- [x] 검증: 각 스크립트의 공용화 여부와 제외 사유가 표로 남아 있습니다.

### 단계 2. 공용 후보의 저장소 의존성 제거

- [x] `/root/32_system-engineering-resources/` 하드코딩을 제거합니다.
- [x] 대상 경로를 명령행 인자로 받도록 통일합니다.
- [x] 저장소별 예외를 코드가 아닌 `--config` 또는 profile로 처리합니다.
- [x] `--help`, `--version` 동작과 검사기의 read-only 특성을 확인합니다.
- [x] 검증: 기존 저장소와 임시 테스트 저장소에서 동일한 CLI가 실행됩니다.

### 단계 3. 테스트와 기존 결과 대조

- [x] 정상 문서, 잘못된 헤딩, 깨진 링크, 표 정렬 오류를 포함한 테스트 fixture를 작성합니다.
- [x] 기존 스크립트와 공용 명령의 결과·반환 코드를 비교합니다.
- [x] 저장소별 예외가 의도한 파일에만 적용되는지 확인합니다.
- [x] 검증: 테스트 결과와 현재 저장소 전체 검사 결과가 일치합니다.

### 단계 4. 패키징과 설치 구조 구현

- [x] `/opt/sia_scripts/releases/<version>/` 구조를 구현합니다.
- [x] `/opt/sia_scripts/current` symlink 전환 방식을 적용합니다.
- [x] `/usr/local/bin/sia-*` 실행 명령을 설치합니다.
- [x] Ansible role 또는 playbook으로 artifact 다운로드, checksum 검증, release 설치를 구현합니다.
- [x] 설치 파일의 소유자·권한을 `root:root`, 디렉토리 `0755`, 일반 파일 `0644`, 실행 파일 `0755` 기준으로 확인합니다.
- [x] 검증: 버전 출력, 도움말 출력, 비권한 사용자의 읽기·실행, 쓰기 차단을 확인합니다.

### 단계 5. CI artifact와 Ansible 배포 workflow의 단계적 적용

- [x] `30_sia-scripts`에 `production` profile, Python `3.12`, `ansible-core==2.20.5`, `ansible-lint==26.8.0`, `v*.*.*` release tag 기준을 명시합니다.
- [x] `30_sia-scripts`에 GitHub Actions 검증 workflow와 tag-only versioned artifact 생성을 구현합니다.
- [x] `30_sia-scripts` release manifest에서 tag commit·version·embedded file hash 관계를 검증합니다.
- [x] 로컬 localhost 임시 HTTPS artifact endpoint에서 30 저장소 release를 검증합니다.
- [x] 로컬 `localhost` 대상에 install·update·rollback을 적용하고 `current`를 baseline version으로 복구합니다.
- [ ] 각 저장소가 사용할 profile과 버전을 명시하도록 합니다.
- [ ] GitHub Actions가 테스트·보안 검증 후 버전 고정 artifact를 생성하도록 합니다.
- [ ] Ansible 제어 서버가 지정된 artifact와 checksum을 outbound HTTPS로 받아 배포하도록 합니다.
- [ ] GitHub Actions에서 Ansible 제어 서버로의 inbound SSH가 필요하지 않음을 확인합니다.
- [ ] 첫 적용 대상 1개 호스트와 1개 저장소에서 검증합니다.
- [ ] 결과 확인 후 적용 대상을 단계적으로 확대합니다.
- [ ] 검증: 기존 workflow 대비 누락된 검사와 신규 오탐이 없습니다.

2026-08-27 local 적용은 root harness로 완료했습니다. 일반 사용자 `siasia`의 task-level `become: true` probe는 sudoers의 password-required 정책(`(ALL : ALL) ALL`, `NOPASSWD` 없음)으로 실패했습니다. 비밀번호 우회·평문 저장·sudoers 변경은 수행하지 않았으며, 일반 계정 Controller 경계의 운영 검증은 미완료로 유지합니다.

### 단계 6. 운영 문서화와 완료 정리

- [x] 설치·업데이트·롤백 명령을 운영 문서에 기록합니다.
- [x] 장애 발생 시 이전 버전으로 전환하는 절차를 확인합니다.
- [x] 완료된 단계와 최종 결과를 `CHANGELOG.md`에 기록합니다.
- [x] 최종 검증 후 `/root/30_sia-scripts` 검증 clone을 삭제합니다. (2026-08-27 사용자 수행)
- [ ] 완료 후 이 `PLAN.md`를 완료 상태로 정리하거나 제거합니다.
- [x] 검증: 전체 Markdown·링크·비밀정보 검사를 통과합니다.

## 6. 검증 기준

```bash
R30="$HOME/30_sia-scripts"
"$R30/src/bin/sia-md-style-check" "$R30"
"$R30/src/bin/sia-md-heading-check" "$R30"
"$R30/src/bin/sia-md-link-check" "$R30"
ANSIBLE_CONFIG="$R30/ansible/ansible.cfg" "$R30/.venv/bin/ansible-playbook" --syntax-check "$R30/ansible/playbooks/install_sia_scripts.yml"
git -C "$R30" diff --check
gitleaks detect --source "$R30" --no-git --no-banner
sudo gitleaks detect --source /root/32_system-engineering-resources --no-git --no-banner
```

`readme_inventory_check.py`는 `(N개)` inventory 표기를 사용하는 저장소에서만 해당 README를 대상으로 실행합니다.

- [x] 공용 명령의 `--help`와 `--version`이 정상 동작합니다.
- [x] 공용 명령이 특정 저장소의 절대경로 없이 동작합니다.
- [x] 정상·오류 fixture 테스트가 통과합니다.
- [x] 기존 검사 결과와 신규 검사 결과가 일치합니다.
- [x] 저장소별 예외가 설정 파일에만 존재합니다.
- [x] 실행 파일 권한과 일반 사용자 쓰기 차단을 확인합니다.
- [x] Ansible playbook syntax check를 통과합니다.
- [x] `ansible-lint==26.8.0`을 고정하고 lint를 통과합니다.
- [ ] Ansible 제어 서버에서 artifact 저장소로 HTTPS 연결이 확인됩니다.
- [ ] Ansible 제어 서버에서 대상 호스트로 Ansible 연결이 확인됩니다.
- [x] artifact checksum 검증 후 설치됩니다.
- [x] 임시 target에서 설치·업데이트·롤백 smoke test를 통과합니다.
- [x] localhost 임시 HTTPS endpoint와 local target의 install·update·rollback 검증을 통과합니다.
- [x] Markdown·링크·헤딩·비밀정보 검사를 통과합니다.
- [x] `CHANGELOG.md`에 최종 결과를 기록합니다.

임시 target smoke test는 `0.3.0 install → 0.3.1 update → 0.3.0 rollback` 순서로 수행했습니다. local baseline은 `/opt/sia_scripts/current → /opt/sia_scripts/releases/0.3.0`이며, 대상 호스트 연결과 artifact 저장소 outbound HTTPS는 아직 실제 운영 환경에서 확인하지 않았습니다.

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

| 작업               | 비가역 사유                                                        | 승인 필요                     |
|--------------------|--------------------------------------------------------------------|-------------------------------|
| 검증용 clone 삭제  | 로컬 working copy 삭제. 원격 `main`과 사용자 clone에서 재생성 가능 | 사용자 승인 완료 (2026-08-27) |
| 이력·자격증명 변경 | 수행하지 않음                                                      | 해당 없음                     |

검증용 clone 삭제는 최종 검증과 사용자 확인 후 수행되었습니다. 현재 기준 저장소는 원격 `main`과 `/home/siasia/30_sia-scripts` 사용자 clone입니다.
버전 전환과 명령어 설치는 기존 release를 보존하므로 롤백 가능합니다.

---

## 9. 현재 상태와 다음 작업

### 2026-08-28 점검 결과

| 항목                          | 현재 상태                                   | 근거                                    |
|-------------------------------|---------------------------------------------|-----------------------------------------|
| 30 저장소                     | `main`, `origin/main`, working tree clean   | `/home/siasia/30_sia-scripts`           |
| 32 저장소                     | `yunli`, `origin/yunli`, working tree clean | active wrapper cleanup 기준             |
| local current                 | `0.3.0` release를 가리킴                    | `/opt/sia_scripts/current`              |
| 보존 release                  | `0.3.0`, `0.3.1`                            | `/opt/sia_scripts/releases/`            |
| 설치 entrypoint               | root 소유 symlink와 실행 권한 확인          | `/usr/local/bin/sia-*`                  |
| local install/update/rollback | 완료                                        | `0.3.0 → 0.3.1 → 0.3.0`                 |
| 일반 사용자 `become`          | 미완료: password-required sudo 정책         | `NOPASSWD` 정책 없음                    |
| iperf3 운영 문서              | 완료                                        | `01_fundamentals/linux/iperf3_guide.md` |

iperf3 문서는 ICMP가 차단된 원격 환경에서 실제 TCP·UDP port를 이용한 통신 품질 측정 절차를 제공합니다. 네트워크 측정 문서 추가는 migration 완료 조건이 아니며, 원격 배포 전 진단 절차를 보강한 것입니다.

2026-08-28 첫 test target에 root SSH로 임시 HTTPS artifact 배포를 수행했습니다. `0.3.0 install → 0.3.1 update → 0.3.0 rollback`과 checksum·version·help·root ownership·permission·일반 사용자 쓰기 차단 검증을 통과했습니다. 이 검증은 운영 artifact repository와 일반 사용자 Controller의 password-free `become` 검증을 대체하지 않습니다.

### 검증 script 이관 작업 (2026-08-28)

- 원격 `become`·운영 artifact 작업을 홀딩하고 30 source of truth 전환을 먼저 진행합니다.
- 30·32 checker parity와 config 차이를 분류한 뒤 32 CI consumer를 30 versioned artifact로 전환합니다.
- 32 root checker는 parity·CI·결과 대조 완료 후 cleanup commit으로 삭제했습니다.
- `strip-footer-md.py`는 30 대응 source가 없는 32 전용 utility 후보로 별도 보류합니다.
- 상세 workflow는 30 `.governance/script_migration_spec.md`를 기준으로 관리합니다.
- 30 generic checker의 `file_skip`·`path_skip` config contract와 `.md-style-check.sia_scripts.toml` 32 profile로 기존 checker 결과 parity를 확인합니다.
- 32 workflow를 30 `0.3.3` release asset과 고정 SHA-256 검증 후 `sia-*` wrapper를 실행하는 consumer로 전환했습니다. private repository 접근은 `SIA_SCRIPTS_RELEASE_TOKEN` secret을 사용합니다.
- local consumer smoke test와 30 `v0.3.3` release asset 검증을 완료했습니다. 초기 consumer workflow run `33154491505`, cleanup 후 run `33154800657`, 직전 문서 hash 정정 push run `33156558662`가 전체 성공했습니다.

### 2026-08-28 root checker cleanup 완료

- [x] active README·governance·workflow·hook·skill의 root checker 실행 참조를 `sia-*` wrapper로 전환했습니다.
- [x] 32 root checker 4개를 cleanup commit `fe4a9d6d48aba374645542cec812eda583487057`에서 삭제했습니다.
- [x] `strip-footer-md.py`와 32 repository policy config 3개를 유지했습니다.
- [x] 삭제 후 32 Markdown consumer workflow `33156558662`의 download·checksum·manifest·style·heading·link·inventory 검증을 통과했습니다.
- [x] 실패 시 cleanup commit을 `git revert`하는 rollback 절차를 확인했습니다.

### 외부 의존성으로 대기 중인 작업

- 30 `Contents: Read` 범위의 `SIA_SCRIPTS_RELEASE_TOKEN` secret 등록과 `v0.3.3` consumer CI 성공을 완료했습니다. 직전 30 CI run `33156553757`과 32 consumer CI run `33156558662`도 성공했습니다.
다음 항목은 local에서 `sudo`를 실행하는 것만으로 완료할 수 없습니다.

1. 실제 운영 artifact repository endpoint, CA trust, checksum 제공.
2. 실제 원격 inventory, 대상 호스트, 관리망 경로와 유지보수 시간 제공.
3. 일반 사용자 Controller의 task-level `become` 정책 결정.
   - 대화형 sudo password 입력 방식.
   - 또는 제한된 대상·명령에 대한 명시적 `NOPASSWD` 운영 정책.
   - password 평문 저장과 임의 sudoers 변경은 금지.
4. 각 대상 저장소의 profile·버전·artifact provenance 제공.

### 다음 적용 순서

- [ ] 대상 저장소별 profile·버전 manifest 확정.
- [ ] 실제 artifact endpoint에 HTTPS·CA·checksum 검증 수행.
- [ ] 첫 원격 대상 1개에 Ansible `--check` 수행.
- [ ] `become` 정책이 해결된 뒤 첫 원격 대상에 install 수행.
- [ ] install 후 entrypoint·version·ownership·permission 검증.
- [ ] 동일 대상에 update와 rollback 수행.
- [ ] 결과 확인 후 대상 호스트를 단계적으로 확대.
- [ ] 모든 원격 적용 완료 후 이 계획을 완료 상태로 정리.

### local에서 추가로 가능한 검증

- [x] `/opt/sia_scripts/current → 0.3.0` baseline 재확인.
- [x] 30·32 저장소 branch와 working tree 재확인.
- [x] 32 저장소 Markdown·gitleaks·`git diff --check` 재검증.
- [x] 제공된 첫 test target에 임시 inventory로 원격 install·update·rollback 검증.
- [ ] 실제 운영 endpoint와 운영 inventory 검증으로 전환.

[⬆ 목차로 돌아가기](#목차)

**작성일**: 2026-08-27

**마지막 업데이트**: 2026-08-28

© 2026 siasia86. Licensed under CC BY 4.0.

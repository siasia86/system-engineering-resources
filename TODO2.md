# TODO2 — Governance 기반 인프라·DevSecOps repository 구조

31 governance를 공통 기준으로 사용하고, 운영 대상별 repository가 필요한 모듈·보안 검사·CI 정책을 조합하는 구조를 정리하기 위한 작업 목록입니다.

핵심 방향은 다음과 같습니다.

- 31은 governance의 source repository입니다.
- 각 운영 repository는 31의 `.governance`를 pinned version으로 사용합니다.
- 00은 Ansible·Docker Compose module을 개발·테스트하고 승인된 release만 제공합니다.
- 30·40 script는 운영 repository의 CI security gate로 사용합니다.
- `51_log_integration`은 로그 통합 서비스의 구성·배포·운영을 소유하는 consumer repository입니다.
- 32는 인프라·보안·테스트 기준과 문서를 관리하며 실제 host 배포를 소유하지 않습니다.
- AI skill과 Markdown은 보조 수단이며, 실제 보안 강제는 CI·IAM·signed artifact·isolated runner·network policy에서 수행합니다.

현재 확인된 운영 repository는 30·31·32·35·00입니다. `40` script와 `51_log_integration`은 이 구조를 구현하기 위한 계획 대상 repository로 관리하며, 실제 생성·경로·owner는 별도 확정이 필요합니다.

## 목차

| 섹션                                                                                                                         |
|------------------------------------------------------------------------------------------------------------------------------|
| [1. 목표와 판단](#1-목표와-판단) / [2. 목표 아키텍처](#2-목표-아키텍처) / [3. Repository 책임 경계](#3-repository-책임-경계) |
| [4. Governance 공급](#4-governance-공급) / [5. Module 공급](#5-module-공급) / [6. 운영 repository](#6-운영-repository)       |
| [7. CI·Evidence·배포](#7-cievidence배포) / [8. 작업 항목과 미결 사항](#8-작업-항목과-미결-사항)                              |

---

## 1. 목표와 판단

### 목표

- governance·module·security script·운영 설정의 책임을 repository별로 분리합니다.
- 운영 repository가 필요한 구성만 version pin으로 가져와 재현 가능한 배포를 수행합니다.
- `00`의 실험 코드와 실제 운영 대상의 배포 구성을 분리합니다.
- 운영 repository마다 동일한 governance·security·evidence 기준을 적용합니다.
- CI에서 policy·module·security·deployment 검증을 완료한 뒤 staging·canary·live로 promotion합니다.
- 모든 release와 실행 결과를 추적하고 이전 version으로 rollback할 수 있게 합니다.

### 목표 아키텍처 흐름

현재 TODO2의 repository federation은 다음 흐름으로 구현합니다.

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                          Repository Federation Target                          │
│31 Governance: policy / schema / release / verification                         │
└───────────────────────────────────────┴────────────────────────────────────────┘
│                                       │                                        │
│                                       v                                        │
┌────────────────────────────────────────────────────────────────────────────────┐
│                            Operational Repositories                            │
│51_log_integration / 52_dev_server / 53_test_lab / ...                          │
└───────────────────────────────────────┴────────────────────────────────────────┘
│                                       │                                        │
│                                       v                                        │
┌────────────────────────────────────────────────────────────────────────────────┐
│                                Approved Inputs                                 │
│00 Ansible / Compose modules + 30 / 40 security gates                           │
└───────────────────────────────────────┴────────────────────────────────────────┘
│                                       │                                        │
│                                       v                                        │
┌────────────────────────────────────────────────────────────────────────────────┐
│                              CI / Test / Approval                              │
│policy + module + security + deployment checks                                  │
└───────────────────────────────────────┴────────────────────────────────────────┘
│                                       │                                        │
│                                       v                                        │
┌────────────────────────────────────────────────────────────────────────────────┐
│                            Staging / Canary / Live                             │
│promotion after health check                                                    │
└───────────────────────────────────────┴────────────────────────────────────────┘
│                                       │                                        │
│                                       v                                        │
┌────────────────────────────────────────────────────────────────────────────────┐
│                          Evidence / Audit / Rollback                           │
│immutable logs / reports / scan results / audit trail                           │
└────────────────────────────────────────────────────────────────────────────────┘
```

`51_log_integration`은 대표 운영 repository이며, 개발 서버·테스트 환경·모니터링·기타 서비스도 동일한 소비 구조를 적용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 목표 아키텍처

### 4-plane 구조

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                                Governance Plane                                │
│31 source / pinned .governance                                                  │
└───────────────────────────────────────┴────────────────────────────────────────┘
│                                       │                                        │
│                                       v                                        │
┌────────────────────────────────────────────────────────────────────────────────┐
│                                 Control Plane                                  │
│00 approved modules / 30-40 gates / CI approval                                 │
└───────────────────────────────────────┴────────────────────────────────────────┘
│                                       │                                        │
│                                       v                                        │
┌────────────────────────────────────────────────────────────────────────────────┐
│                                Execution Plane                                 │
│operational repositories / test / dev / staging / live                          │
└───────────────────────────────────────┴────────────────────────────────────────┘
│                                       │                                        │
│                                       v                                        │
┌────────────────────────────────────────────────────────────────────────────────┐
│                                 Evidence Plane                                 │
│logs / reports / scans / audit / rollback                                       │
└────────────────────────────────────────────────────────────────────────────────┘
```

두 다이어그램은 같은 구조를 다른 관점에서 표현합니다. 첫 번째는 repository·artifact·CI의 연결을, 두 번째는 governance·control·execution·evidence 책임의 경계를 표현합니다.

각 운영 repository는 `31`·`00`·`30`·`40`의 최신 branch를 직접 실행하지 않습니다. 승인된 release·commit·artifact checksum을 고정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. Repository 책임 경계

| Repository                        | 주 책임                                | 운영 대상에 제공하는 것       |
|-----------------------------------|----------------------------------------|-------------------------------|
| `31_governances`                  | 공통 policy·schema·검증·release        | pinned `.governance` snapshot |
| `30_sia-scripts`                  | 공통 script·checker·보안 검사·artifact | versioned security gate       |
| `40` security scripts             | 서비스·환경 특화 보안 검사             | versioned security gate       |
| `32_system-engineering-resources` | 개념·운영 가이드·테스트 기준·참조 문서 | 문서·검증 기준·설계 근거      |
| `35_agent-skill`                  | AI skill·prompt·agent 설정             | versioned AI assistance       |
| `00_chobo_ansible`                | Ansible·Compose module 개발·실험·검증  | approved module release       |
| `51_log_integration`              | 로그 통합 서비스 구성·배포·운영        | 실제 환경 release             |
| `52_dev_server` 등                | 개발 서버·테스트 환경별 구성·배포·운영 | 실제 환경 release             |

`40 security scripts`, `51_log_integration`, `52_dev_server`는 계획 대상 명칭입니다. 실제 repository를 생성할 때 owner·branch·credential·운영 환경을 함께 결정합니다.

### 책임 경계 원칙

- [ ] governance source와 운영 설정을 같은 repository에 혼합하지 않습니다.
- [ ] module factory와 운영 대상 repository를 분리합니다.
- [ ] 공통 보안 검사와 서비스 특화 보안 검사를 분리합니다.
- [ ] 32 문서의 내용만으로 보안 통제가 완료되었다고 판단하지 않습니다.
- [ ] 35 skill·prompt는 실행 권한이나 정책 강제 수단으로 사용하지 않습니다.
- [ ] 운영 repository는 자체 `README.md`·`PLAN.md`·`TODO.md`·rollback 문서를 가집니다.
- [ ] repository 분리는 owner·release·credential·lifecycle·rollback 경계가 실제로 다를 때 적용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. Governance 공급

### Source와 consumer 관계

31은 governance의 source입니다. 각 운영 repository는 31의 `.governance`를 가져와 자기 repository의 검증 기준으로 고정합니다.

```text
31_governances
      │
      ├── governance release vX.Y.Z
      ├── policy checksum
      ├── schema version
      └── verification command set
                       │
                       v
51_log_integration/.governance
52_dev_server/.governance
53_test_lab/.governance
```

### 권장 공급 방식

- [ ] 운영 repository에 사용하는 governance release version을 기록합니다.
- [ ] `.governance` snapshot의 source commit·release·checksum을 기록합니다.
- [ ] CI에서 snapshot이 승인된 31 release와 일치하는지 검증합니다.
- [ ] 31의 최신 branch를 runtime에 직접 clone하지 않습니다.
- [ ] governance 변경은 consumer repository의 compatibility test를 통과해야 합니다.
- [ ] major policy 변경은 migration guide·rollback version·적용 순서를 함께 발행합니다.
- [ ] 임시 예외는 owner·사유·만료일·승인자를 기록합니다.

### Governance가 강제할 항목

- repository branch·merge·approval 규칙.
- Markdown·YAML·Ansible·Terraform 검증 명령.
- secret·dependency·CVE·IaC security gate.
- artifact signature·checksum·provenance 요구사항.
- runner·IAM·sudo·network 권한 기준.
- evidence 보존·audit log·rollback 기록 형식.

[⬆ 목차로 돌아가기](#목차)

---

## 5. Module 공급

### `00_chobo_ansible`의 역할

`00_chobo_ansible`는 필요한 모듈을 개발하고 테스트하는 module factory입니다. 운영 repository가 00의 전체 branch를 가져오는 구조는 사용하지 않습니다.

관리 대상:

- Ansible role·collection.
- Docker Compose module.
- Jinja template·defaults·handlers.
- Molecule·Vagrant·Docker test fixture.
- Terraform·Packer·OS provisioning module.
- Linux·Windows·AWS 환경별 재현 시나리오.

### 승인 module 흐름

```text
00 module source
       v
ansible-lint / syntax-check / Molecule
       v
Docker Compose config / service smoke test
       v
OS·network·dependency integration test
       v
signed module release
       v
51_log_integration 또는 다른 운영 repository
```

### Module 소비 원칙

- [ ] 운영 repository는 00의 `main` branch가 아니라 approved module release를 사용합니다.
- [ ] Ansible role·collection·Compose module의 version과 checksum을 고정합니다.
- [ ] module source·test result·artifact provenance를 연결합니다.
- [ ] module에는 credential·private key·운영 secret을 포함하지 않습니다.
- [ ] 환경별 값은 운영 repository의 protected variable·secret manager에서 주입합니다.
- [ ] module 변경은 최소 하나의 test lab에서 재검증합니다.
- [ ] 이전 module release로 되돌릴 수 있는 compatibility와 rollback을 유지합니다.

### `51_log_integration`의 소비 범위

`51_log_integration`은 00에서 다음처럼 필요한 모듈만 가져옵니다.

- 로그 수집기 설치 role.
- Docker Compose 기반 로그 pipeline.
- 공통 filesystem·user·permission 설정.
- TLS·certificate 배치 module.
- service health check와 backup role.
- 운영 환경에 필요한 network·firewall 설정 module.

00의 학습 예제·실험용 role·검증되지 않은 Compose 파일은 운영 repository로 가져오지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 운영 repository

### `51_log_integration` 책임

`51_log_integration`은 로그 통합 서비스의 실제 consumer·deployment repository입니다.

- [ ] 로그 수집·처리·저장·시각화 서비스 구성을 관리합니다.
- [ ] 환경별 inventory·variable·domain·network 설정을 관리합니다.
- [ ] 00의 approved Ansible·Compose module을 조합합니다.
- [ ] 31의 pinned `.governance`를 포함합니다.
- [ ] 30·40 security gate를 CI에서 호출합니다.
- [ ] test lab·dev·staging·canary·live 배포 흐름을 관리합니다.
- [ ] health check·metric·log·backup·restore·upgrade 절차를 관리합니다.
- [ ] 서비스별 release·rollback·incident 기록을 관리합니다.

### 다른 운영 repository

동일한 구조로 다음 유형의 repository를 분리할 수 있습니다.

- 개발 서버 환경 구축 repository.
- 테스트 lab·Vagrant·Docker 환경 repository.
- AWS 계정·platform·network 환경 repository.
- BMC·PXE·bare-metal provisioning repository.
- Grafana·Prometheus·Zabbix monitoring repository.
- 모바일 device farm·게임 테스트 환경 repository.

각 repository는 별도 owner·release·credential·환경을 가지되, 31 governance와 공통 CI contract를 공유합니다.

### 운영 repository에 포함하지 않는 것

- 최신 branch에서 직접 가져온 미검증 module.
- CI 실행 시점에 변하는 governance 파일.
- 30·40 script의 무버전 복사본.
- 장기 static access key·private key·운영 password.
- 다른 운영 repository의 environment variable.
- AI가 생성한 검증되지 않은 deployment command.

[⬆ 목차로 돌아가기](#목차)

---

## 7. CI·Evidence·배포

### `51_log_integration` CI 흐름

```text
checkout operational repository
            v
load pinned .governance from 31
            v
verify policy release and checksum
            v
load approved Ansible / Compose module from 00
            v
run 30 common security scripts
            v
run 40 service / environment security scripts
            v
run secret / dependency / IaC / container checks
            v
deploy to test lab
            v
health check / integration test / evidence
            v
approval → staging → canary → live
```

### CI 입력 고정

```text
✅ governance vX.Y.Z
✅ ansible-module vA.B.C
✅ compose-module vA.B.C
✅ 30-security-scripts vX.Y.Z
✅ 40-security-scripts vX.Y.Z

❌ 31/main
❌ 00/main
❌ 30/main
❌ 40/main
```

### 30·40 security gate

현재 30은 확인된 script repository이며, 40은 계획 대상입니다. 두 repository의 검사가 중복되지 않도록 생성 전에 책임을 확정합니다.

권장 분리 예시:

- `30`: 공통 repository·host·credential·secret·filesystem·Git 보안 검사.
- `40`: 로그 통합·서비스·환경·network·configuration 특화 보안 검사.

이는 권장안이며, 실제 40 repository의 범위는 기존 30 script와 중복 검토 후 확정합니다.

### Evidence

- [ ] CI 입력 version·commit·checksum을 기록합니다.
- [ ] governance validation 결과를 기록합니다.
- [ ] Ansible·Compose test 결과를 기록합니다.
- [ ] 30·40 security scan 결과를 SARIF·JSON·JUnit 등 재처리 가능한 형식으로 보관합니다.
- [ ] 배포 대상·runner·IAM role·승인자·실행 시간을 기록합니다.
- [ ] health check·metric·log·incident·rollback 결과를 연결합니다.
- [ ] evidence를 임의 수정하지 못하도록 보존·접근 권한을 분리합니다.

### 권한 경계

로컬 hook·AI skill·Markdown은 보안 경계가 아닙니다. 실제 강제는 다음 위치에서 수행합니다.

- CI required check.
- protected branch·required approval.
- signed artifact·provenance verification.
- isolated runner.
- short-lived IAM·OIDC credential.
- sudoers·SSH·BMC·network policy.
- immutable 또는 append-only audit storage.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 작업 항목과 미결 사항

### Phase 1 — 기준과 repository 경계

- [ ] 31 governance의 source·release·consumer 공급 방식을 확정합니다.
- [ ] 30 script와 계획 중인 40 script의 중복·책임·출력 형식을 확정합니다.
- [ ] 00 module release의 version·checksum·provenance 형식을 확정합니다.
- [ ] `51_log_integration`의 실제 생성 경로·owner·branch·환경을 확정합니다.
- [ ] 개발 서버·테스트 lab·AWS·BMC/PXE 운영 repository의 분리 기준을 확정합니다.

### Phase 2 — Module·security CI

- [ ] 00에서 Ansible·Compose module test와 release pipeline을 구성합니다.
- [ ] 운영 repository에 pinned `.governance` 검증을 추가합니다.
- [ ] 30 security script를 versioned CI artifact로 연결합니다.
- [ ] 40 script repository를 생성하거나 실제 위치를 확인합니다.
- [ ] 40의 service·environment security gate 범위를 정의합니다.
- [ ] CI가 최신 branch가 아닌 승인된 release만 참조하는지 검증합니다.

### Phase 3 — `51_log_integration` 구축

- [ ] 로그 통합 서비스의 구성·배포·운영 repository를 생성합니다.
- [ ] 31 governance snapshot을 추가하고 checksum 검증을 연결합니다.
- [ ] 00의 approved Ansible·Compose module을 pin합니다.
- [ ] 30·40 security gate를 CI에 추가합니다.
- [ ] test lab에서 deployment·health check·rollback을 검증합니다.
- [ ] staging·canary·live promotion과 evidence 보존을 연결합니다.

### 완료 기준

- [ ] 각 운영 repository가 pinned `.governance`를 사용합니다.
- [ ] 00에서 테스트된 module만 운영 repository에 공급됩니다.
- [ ] 30·40 security gate가 version·checksum과 함께 CI에서 실행됩니다.
- [ ] `51_log_integration`이 자체 구성·배포·운영·rollback을 소유합니다.
- [ ] CI 결과와 실행 evidence를 재현할 수 있습니다.
- [ ] 이전 governance·module·script release로 rollback할 수 있습니다.
- [ ] credential·private key·운영 secret이 repository와 artifact에 포함되지 않습니다.
- [ ] dev·test·staging·canary·live의 권한과 환경이 분리됩니다.

### 미결 사항

- [ ] 계획 중인 40 script repository의 실제 경로와 owner.
- [ ] `51_log_integration`의 실제 repository 이름·경로·owner.
- [ ] 31 `.governance`를 snapshot·subtree·release artifact 중 어떤 방식으로 공급할지.
- [ ] 00 module을 Ansible collection·OCI artifact·Git release 중 어떤 방식으로 배포할지.
- [ ] 30·40 security 결과의 공통 schema와 severity 기준.
- [ ] Evidence 저장소의 보존 기간·접근 권한·append-only 방식.
- [ ] 각 운영 repository의 CI runner·IAM role·network segment.
- [ ] BMC·PXE·AWS 환경의 별도 approval과 emergency rollback 절차.

---

## 참고 자료

- [32 repository 계획](PLAN.md)
- [32 문서 목록](README.md)
- [30·31·32·35·00 repository 운영 기록](CHANGELOG.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-16

**마지막 업데이트**: 2026-09-16

© 2026 siasia86. Licensed under CC BY 4.0.

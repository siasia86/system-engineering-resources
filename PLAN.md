# 32 `system-engineering-resources` 문서 repository 계획

32 repository는 Linux·네트워크·보안·데이터베이스·인프라·SRE 등 시스템 엔지니어링 학습 자료를 구조화하고 검증하는 문서 repository입니다. 30 `sia_scripts`는 공용 Markdown checker와 release artifact를 제공하며, 32는 repository-local policy와 문서 내용을 관리합니다.

## 목차

| 섹션                                                                                                             |
|------------------------------------------------------------------------------------------------------------------|
| [1. Repository 목적](#1-repository-목적) / [2. 30 통합 역할](#2-30-통합-역할) / [3. 관리 범위](#3-관리-범위)     |
| [4. 현재 상태](#4-현재-상태) / [5. 문서 운영 계획](#5-문서-운영-계획) / [6. 검증과 rollback](#6-검증과-rollback) |

---

## 1. Repository 목적

32는 다음 목적의 system engineering 문서 repository입니다.

- Linux·Windows 운영체제와 시스템 내부 구조 학습.
- 네트워크·보안·데이터베이스·인프라 도구 학습.
- Ansible·Docker·Kubernetes·CI/CD·Cloud·Monitoring 운영 문서 관리.
- SRE·debugging·testing·incident 대응 절차 정리.
- 문서 간 링크·헤딩·표·README inventory 품질 유지.

주요 영역은 다음과 같습니다.

```text
00_governance
01_fundamentals
02_infrastructure
03_engineering
04_security
05_database
06_career
96_scripts
97_misc
98_image
```

각 문서는 학습·운영 목적과 대상 독자가 명확해야 하며, 특정 도구 전환 기록이 repository 전체 구조를 대표하지 않도록 합니다.

## 2. 30 통합 역할

30과 32의 책임 경계는 다음과 같습니다.

```text
30 sia_scripts
  공용 checker source·test·release·CI·Ansible 운영
          |
          v
32 system-engineering-resources
  학습 문서·repository policy·30 release consumer
```

### 30에서 관리

- `sia-md-style-check`, `sia-md-heading-check`, `sia-md-link-check` source.
- unit test와 regression fixture.
- release builder·manifest·SHA-256 checksum.
- GitHub Actions source·security·release 검증.
- 공용 설치·CI·rollback contract.

### 32에서 관리

- 학습 문서 source와 문서 taxonomy.
- `.md-style-check.sia_scripts.toml` repository-local policy profile.
- 30 release version·checksum을 사용하는 consumer workflow.
- 문서별 예외와 repository-local 검증 결과.
- README inventory와 문서 간 연결성.

32 policy exception을 30 source에 하드코딩하지 않습니다. 30은 contract를 제공하고 32는 실제 profile을 유지합니다.

## 3. 관리 범위

### 포함

- 문서 신규 작성·수정·분류·목차 갱신.
- 기술 내용의 source·version·환경 전제 확인.
- 문서 간 내부 링크와 README inventory 유지.
- 30 release consumer version·checksum 갱신.
- 32 policy profile과 workflow 유지.
- 문서 변경의 rollback과 변경 이력 기록.

### 제외

- 30 checker source·test·release builder의 직접 수정.
- 32 repository에 checker source를 복사해 별도 유지하는 방식.
- 32 문서 내용을 특정 도구 전환 작업의 부속 문서로 취급하는 방식.
- 실제 대상 host 배포를 일반 문서 변경에 포함하는 방식.
- 승인되지 않은 artifact 또는 credential을 문서에 기록하는 방식.

## 4. 현재 상태

### 문서 repository

- [x] system engineering 학습 자료 영역이 유지됩니다.
- [x] README가 학습 자료 repository 목적을 설명합니다.
- [x] 주요 문서 영역별 하위 README와 문서 inventory를 관리합니다.
- [x] 문서 품질 검증 기준을 적용합니다.

### 30 consumer

- [x] 30을 checker source·test·artifact·release의 source of truth로 확정했습니다.
- [x] 32 policy exception을 profile로 분리했습니다.
- [x] 32 consumer workflow를 30 `v0.3.3` release와 SHA-256 pin으로 전환했습니다.
- [x] private release download·checksum·manifest·embedded file hash 검증을 수행했습니다.
- [x] 32 root checker 4개와 active 실행 참조를 cleanup했습니다.
- [x] cleanup 후 32 consumer workflow `33156558662` 검증을 통과했습니다.

현재 승인된 consumer baseline은 다음과 같습니다.

```text
repository: siasia86/30_sia-scripts
release:    v0.3.3
artifact:   sia_scripts_0.3.3.tar.gz
sha256:     0b293d76e8efb55e93ad6bb21c0b00bf4362e60aa7a3a4ea5e6d752a012bb4ad
```



## 5. 문서 운영 계획

### 문서 작성·수정

- 새 문서는 적절한 영역과 파일명 규칙에 맞게 배치합니다.
- 문서 첫 등장 기술 용어와 약어를 설명합니다.
- 명령어·설정·경로는 실제 실행 가능성을 확인합니다.
- 예시 credential은 표준 placeholder를 사용합니다.
- 내부 링크와 목차를 같은 변경에서 갱신합니다.
- 실행 결과와 검증 날짜를 필요한 범위로 기록합니다.

### 문서 품질

- Markdown style·heading·link 검사를 통과합니다.
- README inventory를 갱신합니다.
- 문서 변경 시 gitleaks와 `git diff --check`를 실행합니다.
- 저장소 policy exception은 `.md-style-check.sia_scripts.toml`에 최소 범위로 기록합니다.
- 30 release 변경 시 consumer version·checksum을 함께 검토합니다.

### Consumer workflow

32 workflow는 다음 순서로 동작해야 합니다.

```text
30 private release download
          |
          v
SHA-256 checksum verification
          |
          v
manifest + embedded file hash verification
          |
          v
32 policy profile + sia-* wrapper
```

artifact 검증에 실패하면 문서 검사를 실행하지 않습니다. token·private key·password는 workflow YAML·commit·log에 기록하지 않습니다.

## 6. 검증과 rollback

### 검증 명령

검증된 30 release wrapper를 사용하는 환경에서는 다음 순서를 적용합니다.

```bash
R32="$HOME/32_system-engineering-resources"

sia-md-link-check "$R32"
sia-md-style-check \
  --config "$R32/.md-style-check.sia_scripts.toml" \
  "$R32"
sia-md-heading-check "$R32"
sia-readme-inventory-check "$R32/README.md"
gitleaks detect --source "$R32" --no-git --no-banner
git -C "$R32" diff --check
```

local 환경에 wrapper가 없으면 승인된 30 artifact를 먼저 설치합니다. 도구가 없는 상태를 통과로 처리하지 않습니다.

### Rollback

- 문서 내용 오류: 변경 commit을 revert합니다.
- policy profile 오류: 이전 승인 profile을 복구합니다.
- 30 release consumer 오류: 이전 승인 version·checksum으로 pin을 되돌립니다.
- root checker cleanup 오류: cleanup commit `fe4a9d6d48aba374645542cec812eda583487057`를 revert합니다.
- 실제 host 배포 오류: 30 installation guide의 이전 release rollback 절차를 따릅니다.

기존 release tag와 artifact를 force update하거나 삭제하지 않습니다.

32 문서 repository 운영의 다음 작업 목록은 30 `.governance/PLAN.md`의 "32 system-engineering-resources 후속 작업" 섹션에서 관리합니다. 이 문서와 중복 기록하지 않습니다.

---

## 참고 자료

- 30 installation guide: [30 `sia_scripts` installation guide](https://github.com/siasia86/30_sia-scripts/blob/main/docs/installation_guide.md) — ★★★☆☆
- 30 CI guide: [30 `sia_scripts` CI guide](https://github.com/siasia86/30_sia-scripts/blob/main/docs/ci_guide.md) — ★★★☆☆

---

**작성일**: 2026-08-27

**마지막 업데이트**: 2026-08-28

© 2026 siasia86. Licensed under CC BY 4.0.

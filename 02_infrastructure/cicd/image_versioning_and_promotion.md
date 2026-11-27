# 이미지 판 관리와 단계별 승격
<!-- reference: _reference/cloud_image_galleries_official_notes.md -->

VM 이미지(Vagrant box, VHDX, qcow2, 클라우드 이미지)와 컨테이너 이미지를 한 번 빌드해 판 번호를 붙여 보관하고, 같은 파일을 개발 → 시험 → 운영처럼 단계별로 올리는 일반 패턴을 정리합니다. 특정 도구 사용법은 [VM 이미지 판 관리](../iac/vm_image_versioning.md)와 [컨테이너 이미지 승격](../containers/container_image_promotion.md), 도구 선택은 [이미지 관리 도구 비교](./image_management_tools_comparison.md)에서 다룹니다.

- 대상 독자: Packer·Ansible·Docker로 이미지를 만들어 여러 환경에 배포하는 운영·플랫폼 담당자
- 범위: 조직과 도구에 관계없이 쓰는 원칙. 이 문서의 단계 이름(dev, qa, prod)은 예시이며, 단계 수와 이름, 승인 방식은 조직마다 다릅니다
- 근거: 각 하위 문서의 시험 결과(2026-11-27)와 공식 문서([참조 노트](../../_reference/cloud_image_galleries_official_notes.md))

## 목차

| 섹션                                                                                                               |
|--------------------------------------------------------------------------------------------------------------------|
| [1. 왜 판 관리가 필요한가](#1-왜-판-관리가-필요한가) / [2. 불변 이미지](#2-불변-이미지) / [3. 판 번호](#3-판-번호) |
| [4. 출처 메타데이터](#4-출처-메타데이터) / [5. 한 번 빌드하고 승격](#5-한-번-빌드하고-승격)                        |
| [6. 되돌리기](#6-되돌리기) / [7. 보관과 정리](#7-보관과-정리) / [8. 주기적 재빌드](#8-주기적-재빌드)               |
| [9. 점검표](#9-점검표) / [10. 흔한 실수](#10-흔한-실수) / [함께 보기](#함께-보기)                                  |

---

## 1. 왜 판 관리가 필요한가

| 판 관리가 없을 때                                         | 판 관리를 할 때                                    |
|-----------------------------------------------------------|----------------------------------------------------|
| 시험한 이미지와 운영에 올린 이미지가 같은지 알 수 없음    | 같은 판 번호·체크섬(digest)이면 같은 파일          |
| 운영 배포 직전에 다시 빌드해 기반 패키지가 바뀜           | 시험을 통과한 파일을 그대로 올림                   |
| 문제가 생기면 어느 commit으로 만든 이미지인지 찾기 어려움 | 이미지 안·옆에 commit, 기반 이미지, 빌드 시각 기록 |
| 되돌릴 이전 이미지가 이미 지워짐                          | 보관 규칙으로 되돌릴 판을 남김                     |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 불변 이미지

- 한 번 판 번호를 붙여 올린 이미지는 바꾸지 않습니다. 고칠 일이 생기면 새 판으로 다시 빌드합니다.
- 실행 중인 서버나 컨테이너에 들어가 고치지 않고, 이미지를 고쳐 새로 배포합니다. 설정 관리 도구(Ansible 등)는 이미지를 만드는 단계에서 씁니다.
- 같은 판 번호에 다른 파일을 올리지 못하게 저장소에서 막습니다.

| 형식            | 바뀌지 않는 식별자                | 덮어쓰기 막는 방법                                                                                       |
|-----------------|-----------------------------------|----------------------------------------------------------------------------------------------------------|
| Vagrant box     | catalog의 판 번호 + sha256        | 같은 판을 다시 올리지 않음, 저장소 쓰기 권한 제한                                                        |
| VHDX·qcow2 등   | 파일 경로의 판 번호 + sha256 파일 | 저장소의 다시 올리기 금지 설정                                                                           |
| 컨테이너        | digest(`sha256:...`)              | 레지스트리의 태그 불변 설정([컨테이너 승격](../containers/container_image_promotion.md#8-덮어쓰기-막기)) |
| 클라우드 이미지 | 이미지 ID(AMI ID, 갤러리 판 등)   | 판 자체가 바뀌지 않음, 이름·채널만 옮김                                                                  |

- 시험에서 기본 설정의 컨테이너 레지스트리(distribution 3.1.2)는 같은 태그에 다른 이미지를 올려도 막지 않았습니다. 태그만 믿지 말고 digest를 함께 기록합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 판 번호

| 방식           | 예                      | 맞는 곳                                           |
|----------------|-------------------------|---------------------------------------------------|
| SemVer(X.Y.Z)  | `1.4.0`                 | 사용자에게 호환성 변화를 알려야 하는 이미지       |
| 날짜(CalVer)   | `2026.11.27`, `26.11.0` | 정기 재빌드하는 기반 OS 이미지                    |
| 판 + commit    | `1.4.0-3f2a9c1`         | 컨테이너 태그, 빌드를 commit과 바로 연결할 때     |
| 판 + 빌드 번호 | `1.4.0` + CI 빌드 번호  | 판 번호 형식이 제한된 곳(아래 표)에서 기록만 따로 |

도구마다 판 형식 제한이 있어, 정한 규칙을 모든 저장소에 그대로 쓰지 못할 수 있습니다.

| 도구                  | 판 형식 제한                                                     |
|-----------------------|------------------------------------------------------------------|
| Vagrant box           | X.Y.Z 정수만, pre-release 불가                                   |
| Azure Compute Gallery | MajorVersion.MinorVersion.Patch 정수                             |
| 컨테이너 태그         | 영문·숫자·`_`·`.`·`-`, 최대 128자, `+` 불가                      |
| SemVer                | `+` 뒤 build metadata는 판 비교에서 무시, `v`는 판의 일부가 아님 |

- 날짜 판은 0을 채운 형식(`2026.01.05`)이 SemVer로는 유효하지 않습니다. Vagrant·Azure처럼 정수 세 자리를 요구하는 곳에서는 `2026.1.5`처럼 씁니다.
- 컨테이너 태그에는 `+`를 쓸 수 없으므로 SemVer build metadata 대신 `-`로 commit을 붙입니다.
- 판 번호는 빌드 파이프라인이 정하고, 사람이 손으로 붙이지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 출처 메타데이터

이미지마다 "무엇으로, 언제, 어디서 만들었는지"를 함께 남깁니다.

| 항목         | 예                               | 기록 위치 예                                                                |
|--------------|----------------------------------|-----------------------------------------------------------------------------|
| 판 번호      | `1.4.0`                          | 파일 이름, catalog, 태그, OCI 라벨 `org.opencontainers.image.version`       |
| 빌드 commit  | `3f2a9c1`                        | OCI 라벨 `org.opencontainers.image.revision`, Packer manifest `custom_data` |
| 기반 이미지  | 기반 이미지 이름과 digest·체크섬 | OCI 라벨 `org.opencontainers.image.base.name`·`base.digest`                 |
| 빌드 시각    | `2026-11-27T08:00:00Z`(UTC)      | OCI 라벨 `org.opencontainers.image.created`, manifest `build_time`          |
| 빌드 도구 판 | Packer 1.16.3, Ansible 판        | Packer manifest `custom_data`, 빌드 기록                                    |
| 체크섬       | sha256                           | `.sha256` 파일, catalog `checksum`, 컨테이너 digest                         |
| 검사 결과    | 시험 통과 기록, SBOM, 서명       | CI 기록, cosign 증명(attestation)                                           |

- VM 이미지는 [Packer manifest](../iac/vm_image_versioning.md#7-packer로-판과-체크섬-기록)에, 컨테이너는 [OCI 라벨과 서명](../containers/container_image_promotion.md#4-출처-라벨)에 남기는 방법을 각 문서에서 다룹니다.
- 비공개 저장소 주소, 계정, 내부 호스트 이름은 이미지 라벨에 넣지 않습니다. 라벨은 이미지를 받는 누구나 읽을 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 한 번 빌드하고 승격

```text
[빌드 1회]  commit 3f2a9c1 → 이미지 1.4.0 (sha256 A)
     |
     v
dev 단계   : 1.4.0 (A)  자동 시험
     |  승격 = 같은 파일(A)을 다음 단계로 옮기거나 가리킴
     v
qa 단계    : 1.4.0 (A)  통합 시험, 확인
     |
     v
prod 단계  : 1.4.0 (A)  배포
```

- 승격할 때 다시 빌드하지 않습니다. 다시 빌드하면 기반 패키지와 시각이 바뀌어 체크섬이 달라집니다.
- 승격 전후의 체크섬(digest)이 같은지 확인하는 단계를 파이프라인에 넣습니다.
- 단계 수는 조직마다 다릅니다. 단계를 나누는 목적(자동 시험, 사람 확인, 고객 배포)을 먼저 정하고 그에 맞춰 단계를 둡니다.

승격 방식은 세 가지입니다. 한 조직에서 섞어 쓰기도 합니다.

| 방식                 | 동작                                                | 예                                                                     |
|----------------------|-----------------------------------------------------|------------------------------------------------------------------------|
| 저장소 간 복사       | 단계별 저장소를 두고 같은 파일을 복사               | 개발용·운영용 레지스트리, raw 저장소 경로 분리                         |
| 같은 저장소에서 표시 | 단계 태그·채널을 같은 파일에 붙임                   | 컨테이너 단계 태그(`qa`, `prod`), HCP Packer 채널                      |
| 메타데이터로 가리킴  | 이미지는 그대로 두고 "현재 판"을 가리키는 값만 바꿈 | GCP 이미지 패밀리, Azure의 latest와 latest 제외, Vagrant `box_version` |

- 저장소 간 복사는 운영 저장소의 쓰기 권한을 승격 작업에만 줄 수 있어 권한 분리가 쉽습니다.
- 표시·가리키기 방식은 복사가 없어 빠르지만, 단계 태그는 바뀌는 값이므로 배포에는 digest나 판 번호를 씁니다.
- 승격 조건(어떤 시험을 통과해야 하는지, 누가 확인하는지)은 조직의 규칙으로 따로 정하고 파이프라인에 기록을 남깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 되돌리기

| 방식           | 되돌리는 방법                                                 |
|----------------|---------------------------------------------------------------|
| 저장소 간 복사 | 운영 배포 설정의 판 번호(digest)를 이전 판으로 바꿈           |
| 단계 태그·채널 | 태그·채널을 이전 판으로 다시 옮김                             |
| 이미지 패밀리  | 최신 이미지를 폐기 상태로 바꿔 이전 이미지를 가리키게 함(GCP) |
| Vagrant box    | `box_version`을 이전 판으로 고정                              |

- 되돌릴 판이 남아 있어야 하므로 7절의 보관 규칙에서 운영에 배포된 판을 지우지 않게 합니다.
- 결함이 있는 판은 지우기보다 사용 금지 표시를 먼저 합니다(catalog에서 빼기, 폐기 표시, HCP Packer revoke 등). 이미 그 판을 쓰는 서버의 기록을 추적할 수 있어야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 보관과 정리

이미지는 크기가 커서 계속 쌓으면 저장소 용량이 금방 찹니다. 단계별로 다른 규칙을 둡니다.

| 단계 예     | 보관 규칙 예                                        |
|-------------|-----------------------------------------------------|
| dev         | 최근 N개 또는 N일, 태그 없는 이미지는 자주 정리     |
| qa          | 최근 N개                                            |
| prod        | 현재 판과 되돌릴 이전 판 몇 개, 운영 기록이 남은 판 |
| 기반 이미지 | 사용 중인 이미지가 참조하는 판은 보존               |

- 정리는 먼저 시험 실행(dry run)으로 지워질 목록을 확인합니다. Harbor 보존 규칙은 실행 뒤 되돌릴 수 없다고 공식 문서에 적혀 있습니다.
- 컨테이너 레지스트리는 태그나 manifest를 지워도 공간이 바로 비지 않고, garbage collection을 따로 돌려야 합니다.
- 서명·SBOM이 이미지와 함께 지워지는지, 남아서 고아가 되는지 도구별로 확인합니다([컨테이너 승격](../containers/container_image_promotion.md#9-정리)).
- 도구별 정리 기능은 [Nexus 정리 정책](./nexus.md#6-운영), [이미지 관리 도구 비교](./image_management_tools_comparison.md#2-한눈에-비교)에 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 주기적 재빌드

- 이미지 안의 OS 패키지와 기반 이미지는 시간이 지나면 보안 수정이 쌓입니다. 코드가 바뀌지 않아도 정기적으로 다시 빌드합니다.
- 재빌드한 이미지는 새 판 번호(예: patch 증가나 날짜 판)를 받고, 처음 빌드한 이미지와 같은 승격 경로를 다시 거칩니다.
- 기반 이미지를 digest로 고정했다면 고정 값을 갱신하는 작업(예: Renovate, Dependabot)을 함께 둡니다([Dockerfile 문서](../containers/dockerfile_best_practices.md)).
- 오래된 기반 이미지를 쓰는 판을 찾을 수 있도록 4절의 기반 이미지 기록을 남깁니다. HCP Packer는 부모 이미지 대비 최신 여부를 표시하는 ancestry 기능이 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 점검표

- [ ] 판 번호 규칙이 정해져 있고, 사용하는 모든 저장소의 형식 제한을 만족하는가
- [ ] 같은 판 번호에 다른 파일을 올릴 수 없게 막았는가
- [ ] 이미지마다 commit, 기반 이미지, 빌드 시각, 체크섬이 기록되는가
- [ ] 승격 때 다시 빌드하지 않고, 승격 전후 체크섬이 같은지 확인하는가
- [ ] 운영 배포 설정이 바뀌는 태그가 아니라 판 번호나 digest를 가리키는가
- [ ] 되돌릴 판이 보관 규칙에서 보호되는가
- [ ] 정리 규칙을 dry run으로 먼저 확인했는가
- [ ] 정기 재빌드 일정과 기반 이미지 갱신 방법이 있는가
- [ ] 이미지 라벨·catalog에 비공개 주소나 계정이 들어가지 않았는가

[⬆ 목차로 돌아가기](#목차)

---

## 10. 흔한 실수

| 실수                                   | 결과                                       | 대책                          |
|----------------------------------------|--------------------------------------------|-------------------------------|
| 운영 배포 직전에 다시 빌드             | 시험하지 않은 이미지가 운영에 감           | 시험한 파일을 그대로 승격     |
| `latest` 같은 바뀌는 태그로 배포       | 서버마다 다른 이미지가 실행됨              | 판 번호·digest 고정           |
| 검증하지 않은 판을 catalog에 먼저 올림 | 사용자의 갱신 명령이 그 판을 받으려다 실패 | 체크섬 확인 뒤 catalog 갱신   |
| 이미지만 복사하고 서명은 두고 옴       | 운영 쪽 서명 검증 실패                     | 서명·SBOM도 함께 복사         |
| 정리 규칙을 바로 실행                  | 되돌릴 판까지 지워짐                       | dry run 뒤 실행, 운영 판 보호 |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [VM 이미지 판 관리](../iac/vm_image_versioning.md) — Vagrant box catalog, Packer manifest
- [컨테이너 이미지 승격](../containers/container_image_promotion.md) — 태그·digest, 서명, 정리
- [이미지 관리 도구 비교](./image_management_tools_comparison.md) — HCP Packer, Harbor, 클라우드 갤러리
- [Packer](../iac/packer.md) · [Vagrant](../iac/vagrant.md) · [Nexus Repository](./nexus.md) · [아티팩트 저장소 비교](./artifact_repository_comparison.md)

---

## 참고 자료

- [Semantic Versioning 2.0.0](https://semver.org/) · [Calendar Versioning](https://calver.org/) — ★★★☆☆
- OCI: [Image annotations](https://github.com/opencontainers/image-spec/blob/main/annotations.md) · [Distribution spec](https://github.com/opencontainers/distribution-spec/blob/main/spec.md) — ★★★☆☆
- Google Cloud: [Image management best practices](https://cloud.google.com/compute/docs/images/image-management-best-practices) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-27

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.

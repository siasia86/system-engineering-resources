# 이미지 관리 도구 비교
<!-- reference: _reference/cloud_image_galleries_official_notes.md -->

VM 이미지와 컨테이너 이미지의 판 관리·승격·정리를 돕는 도구를 비교합니다. 빌드 도구(Packer, Docker)가 만든 이미지를 어디에 보관하고, 단계별로 어떻게 표시하며, 언제 지우는지에 초점을 둡니다. 원칙은 [이미지 판 관리와 단계별 승격](./image_versioning_and_promotion.md)에 있습니다.

- 확인 기준: 2026-11-27 공식 문서와 릴리스 페이지. Harbor v2.15.5, Packer 1.16.3, Vagrant 2.4.9
- 시험: 이 문서의 도구는 실행하지 않았습니다(공식 문서만 대조). 로컬에서 시험한 범위는 [VM 이미지 판 관리](../iac/vm_image_versioning.md), [컨테이너 이미지 승격](../containers/container_image_promotion.md)에 있습니다
- 요금은 바뀌므로 도입 전에 공식 요금 페이지를 다시 확인합니다

## 목차

| 섹션                                                                                                           |
|----------------------------------------------------------------------------------------------------------------|
| [1. 도구의 역할 구분](#1-도구의-역할-구분) / [2. 한눈에 비교](#2-한눈에-비교) / [3. HCP Packer](#3-hcp-packer) |
| [4. Harbor](#4-harbor) / [5. 클라우드 이미지 서비스](#5-클라우드-이미지-서비스)                                |
| [6. Vagrant box 배포처](#6-vagrant-box-배포처) / [7. 고르는 기준](#7-고르는-기준) / [함께 보기](#함께-보기)    |

---

## 1. 도구의 역할 구분

| 역할                   | 하는 일                           | 예                                                       |
|------------------------|-----------------------------------|----------------------------------------------------------|
| 빌드                   | 이미지를 만듦                     | Packer, Docker·BuildKit, EC2 Image Builder               |
| 파일·이미지 저장소     | 이미지 파일을 보관하고 내려줌     | Nexus, Artifactory, Harbor, 클라우드 컨테이너 레지스트리 |
| 메타데이터 레지스트리  | 이미지 위치·판·채널 정보만 관리   | HCP Packer                                               |
| 클라우드 이미지 서비스 | 클라우드 VM 이미지의 판·공유·폐기 | AMI, Azure Compute Gallery, GCP 이미지 패밀리            |

- 한 도구가 여러 역할을 하기도 합니다. 예를 들어 EC2 Image Builder는 빌드와 배포를, Harbor는 저장과 서명 관리를 함께 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 한눈에 비교

| 도구                      | 대상                      | 판 표현                  | 승격·단계 표시                    | 정리·폐기                                  | 비용                                               |
|---------------------------|---------------------------|--------------------------|-----------------------------------|--------------------------------------------|----------------------------------------------------|
| HCP Packer                | Packer가 만든 이미지 정보 | 버킷 안 판(fingerprint)  | 채널(`latest` 자동, 사용자 채널)  | revoke(예약 취소는 Standard), 하위 판 연쇄 | Essentials·유료 Standard, 한도 미확인              |
| Harbor                    | 컨테이너·OCI artifact     | 태그·digest              | 프로젝트·복제, 태그               | 보존 규칙, GC, 태그 불변                   | 오픈소스, 직접 운영                                |
| Nexus·Artifactory         | 파일(raw)·컨테이너 등     | 경로·태그                | 저장소 분리, 복사                 | 정리 정책([Nexus](./nexus.md#6-운영))      | [저장소 비교](./artifact_repository_comparison.md) |
| AWS ECR                   | 컨테이너                  | 태그·digest              | 저장소·계정 분리, 복제            | 수명 주기 규칙, 태그 불변                  | 저장·전송량                                        |
| AWS AMI·EC2 Image Builder | AWS VM 이미지             | AMI ID, Image Builder 판 | 계정·조직 공유, 배포 설정         | 폐기(deprecate), 등록 해제, 등록 해제 보호 | Image Builder 무료, 자원·스냅샷 비용               |
| Azure Compute Gallery     | Azure VM 이미지           | Major.Minor.Patch 정수   | latest 제외, 지역 복제, 공유 범위 | 수명 종료일(정보용), 판 삭제               | 갤러리 무료, 저장·복제 전송 비용                   |
| GCP 이미지 패밀리         | GCE VM 이미지             | 이미지 이름, 패밀리      | 시험 패밀리 → 운영 패밀리 복사    | DEPRECATED·OBSOLETE·DELETED                | 이미지 저장 비용                                   |
| 직접 호스팅 box           | Vagrant box               | catalog의 X.Y.Z          | 단계별 catalog                    | catalog에서 빼고 파일 삭제                 | 저장소 비용                                        |

[⬆ 목차로 돌아가기](#목차)

---

## 3. HCP Packer

- Packer 템플릿에 `hcp_packer_registry` 블록을 넣으면 빌드 결과(클라우드 이미지 ID 등)의 정보가 HCP에 판으로 기록됩니다. 이미지 파일 자체는 각 클라우드에 있습니다.
- 판은 fingerprint로 구분하며, 같은 fingerprint로 완료된 판이 있으면 빌드가 실패합니다.
- 채널에 판을 지정하는 것이 승격입니다. 완료된 판만 지정할 수 있고, 채널을 바꿔도 사용처에 알림이 가지 않습니다. Terraform `hcp_packer_artifact` 데이터 소스나 Packer `hcp-packer-artifact` 데이터 소스가 채널을 읽어 이미지 ID를 얻습니다.
- revoke한 판을 참조하는 템플릿은 빌드할 수 없습니다. 복원해도 채널에 자동으로 다시 넣지 않습니다.
- ancestry 기능은 부모 이미지가 바뀌었을 때 자식 이미지를 `Out of date`로 표시합니다(Packer 1.8.2 이상).
- 빌드하려면 HCP 서비스 주체 자격 증명(`HCP_CLIENT_ID`, `HCP_CLIENT_SECRET`)이 필요합니다. 등급별 버킷·판 수 한도와 금액은 확인하지 못했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. Harbor

- 오픈소스 컨테이너 레지스트리로, 프로젝트 단위 권한, 취약점 검사 연동, 복제, 서명 관리를 함께 제공합니다. 최신 릴리스는 v2.15.5(2026-11-12)입니다.
- 태그 불변 규칙: 저장소·태그 패턴(matching/excluding), 프로젝트당 15개. 불변 태그는 삭제·다시 올리기·태그 변경·복제로 바뀌지 않습니다.
- 보존 규칙: 최근 올린·받은 N개, N일 안에 올린·받은 것, 항상 보존. 태그 필터와 태그 없는 artifact 포함 여부, cron 일정, Dry Run. 실행 뒤 되돌릴 수 없습니다.
- 복제: Harbor와 다른 레지스트리 사이 push·pull 방식. 단계별 레지스트리 승격에 쓸 수 있습니다.
- 서명: Cosign(v2.5부터)과 Notation. 서명은 accessory로 표시되며, 서명 복제는 수동·예약 실행만 됩니다.
- GC: 삭제해도 공간이 바로 비지 않으며 GC를 따로 실행합니다. GC로 지운 artifact의 서명도 함께 지워집니다.
- 직접 운영해야 하므로 DB·저장소 백업, 업그레이드, 인증서 관리 부담이 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 클라우드 이미지 서비스

| 항목      | AWS AMI                                         | Azure Compute Gallery                       | GCP 이미지                          |
|-----------|-------------------------------------------------|---------------------------------------------|-------------------------------------|
| 판 단위   | AMI ID                                          | 이미지 정의 아래 판(Major.Minor.Patch)      | 이미지(이름), 패밀리로 묶음         |
| "현재 판" | 배포 설정·파라미터에 ID 지정                    | `latest`(가장 높은 판, latest 제외 판 빼고) | 패밀리가 가장 최근 이미지 가리킴    |
| 되돌리기  | 이전 ID로 바꿈                                  | 새 판을 latest에서 제외하거나 판 지정       | 최신 이미지를 DEPRECATED로          |
| 폐기      | deprecate: 목록에서 숨김, ID로는 계속 실행 가능 | 수명 종료일: 정보용, 계속 생성 가능         | DEPRECATED 경고, OBSOLETE 실행 실패 |
| 삭제      | 등록 해제(스냅샷은 따로), 등록 해제 보호        | 판 삭제(기존 VM 영향 없음, 확장은 실패)     | DELETED                             |
| 공유      | 계정·조직, 지역별(다른 지역은 복사)             | RBAC, direct shared, community              | IAM                                 |

- 세 서비스 모두 기존 VM은 이미지 폐기·삭제의 영향을 받지 않습니다. 다만 자동 확장(Auto Scaling, VMSS 등)이 삭제된 이미지를 참조하면 새 인스턴스를 만들지 못합니다.
- EC2 Image Builder는 서비스 자체가 무료이고 빌드에 쓰는 자원만 과금됩니다. 레시피·이미지 판 형식의 세부 규칙은 이번에 확인하지 못했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. Vagrant box 배포처

- HCP Vagrant Registry(옛 Vagrant Cloud)는 공식 종료 안내에 따라 새 box·registry 생성이 2026-10-01에, 지원이 2026-11-02에 끝났고, 2026-12-31에 운영을 마칩니다. 공개 box를 받아 쓰던 경우도 다른 배포처를 찾아야 합니다.
- 대안은 HTTP로 파일을 주는 저장소에 box와 catalog(`metadata.json`)를 직접 두는 방식입니다. 정적 웹 서버, 객체 저장소, Nexus·Artifactory의 raw 저장소 모두 됩니다([VM 이미지 판 관리](../iac/vm_image_versioning.md#4-저장소에-올리기)).

[⬆ 목차로 돌아가기](#목차)

---

## 7. 고르는 기준

| 상황                                               | 고려할 선택                                    |
|----------------------------------------------------|------------------------------------------------|
| 이미 Nexus·Artifactory를 씀                        | 같은 저장소의 raw·Docker 저장소로 시작         |
| 컨테이너 중심, 직접 운영 가능, 서명·불변·복제 필요 | Harbor                                         |
| 한 클라우드 중심                                   | 그 클라우드의 레지스트리와 이미지 서비스       |
| 여러 클라우드에 Packer로 같은 이미지를 배포        | HCP Packer로 판·채널 정보 통합(요금 확인 필요) |
| Vagrant box 배포                                   | 직접 호스팅(HCP Vagrant 종료)                  |

도입 전에 확인할 것:

- 같은 판을 덮어쓰지 못하게 막는 기능이 있는가
- 단계 표시(채널·태그·저장소 분리)를 권한과 함께 나눌 수 있는가
- 정리 규칙에 dry run과 보호 예외가 있는가
- 서명·SBOM 같은 연결 artifact가 승격·정리 때 함께 다뤄지는가
- 직접 운영이라면 백업·업그레이드·인증서 관리를 누가 맡는가

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [이미지 판 관리와 단계별 승격](./image_versioning_and_promotion.md) — 원칙
- [VM 이미지 판 관리](../iac/vm_image_versioning.md) · [컨테이너 이미지 승격](../containers/container_image_promotion.md) — 시험한 설정
- [아티팩트 저장소 비교](./artifact_repository_comparison.md) — Nexus·Artifactory·Cloudsmith
- [관리형 컨테이너 플랫폼 비교](../containers/managed_container_platforms.md) · [클라우드 사업자 비교](../cloud_aws/cloud_provider_comparison.md)

---

## 참고 자료

- HashiCorp: [HCP Packer](https://developer.hashicorp.com/hcp/docs/packer) · [Channels](https://developer.hashicorp.com/hcp/docs/packer/manage/channel) · [Revoke and restore](https://developer.hashicorp.com/hcp/docs/packer/manage/revoke-restore) · [HCP Vagrant EOL](https://developer.hashicorp.com/hcp/docs/vagrant/hcp-vagrant-eol) — ★★★☆☆
- Harbor: [Tag immutability](https://goharbor.io/docs/main/working-with-projects/working-with-images/create-tag-immutability-rules/) · [Tag retention](https://goharbor.io/docs/main/working-with-projects/working-with-images/create-tag-retention-rules/) · [Garbage collection](https://goharbor.io/docs/main/administration/garbage-collection/) — ★★★☆☆
- AWS: [EC2 Image Builder](https://docs.aws.amazon.com/imagebuilder/latest/userguide/what-is-image-builder.html) · [Deprecate an AMI](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ami-deprecate.html) · [Deregister an AMI](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/deregister-ami.html) — ★★★☆☆
- Azure: [Azure Compute Gallery](https://learn.microsoft.com/en-us/azure/virtual-machines/shared-image-galleries) · [Create an image version](https://learn.microsoft.com/en-us/azure/virtual-machines/image-version) — ★★★☆☆
- Google Cloud: [Image families best practices](https://cloud.google.com/compute/docs/images/image-families-best-practices) — ★★★☆☆

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

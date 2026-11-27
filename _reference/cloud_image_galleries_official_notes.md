---
name: cloud-image-galleries-official-notes
description: Azure Compute Gallery 판 형식·latest 제외, AWS AMI 폐기·EC2 Image Builder, GCP 이미지 패밀리, SemVer·CalVer 규칙 정리.
tags:
  - azure
  - aws
  - gcp
  - versioning
last_checked: 2026-11-27
sources:
  - https://learn.microsoft.com/en-us/azure/virtual-machines/shared-image-galleries
  - https://learn.microsoft.com/en-us/azure/virtual-machines/image-version
  - https://docs.aws.amazon.com/imagebuilder/latest/userguide/what-is-image-builder.html
  - https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ami-deprecate.html
  - https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/deregister-ami.html
  - https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/sharingamis-explicit.html
  - https://cloud.google.com/compute/docs/images/image-families-best-practices
  - https://cloud.google.com/compute/docs/images/image-management-best-practices
  - https://semver.org/
  - https://calver.org/
---

# 클라우드 이미지 갤러리 공식 자료 참조 노트

## 1. Azure Compute Gallery (페이지 갱신 2026-06-24)

- 구조: 갤러리 → 이미지 정의(Publisher·Offer·SKU 조합 고유) → 이미지 판. VM은 판으로 만듦.
- 판 형식: "MajorVersion.MinorVersion.Patch", 32비트 정수. `latest`는 Major, Minor, Patch 순으로 가장 높은 판.
- "exclude from latest"로 특정 판을 latest에서 뺌. 수명 종료일은 정보용이며 지난 판으로도 VM 생성 가능.
- 복제: 지역별 replica 수, 원본 지역은 하나이며 대상에 포함해야 함. 생성 뒤 대상 지역·replica 수·latest 제외·수명 종료일 변경 가능.
- 공유: RBAC, RBAC + direct shared gallery(구독·테넌트), RBAC + community gallery(공개).
- 비용: 갤러리 자체는 무료, 저장과 복제 전송 비용만.

## 2. AWS

- EC2 Image Builder: 서비스 자체는 무료, EC2·EBS·S3 등 사용 자원만 과금. 레시피·이미지 판 형식과 수명 주기 정책 세부는 읽은 페이지에 없음(미확인).
- AMI 폐기(deprecate): 목록에서 기본으로 숨김, ID를 알면 계속 실행 가능, 실행 중인 인스턴스 영향 없음. 기한 최대 10년(공개 AMI는 생성 후 2년). 삭제가 아니므로 스냅샷 비용 계속.
- 등록 해제(deregister): 새 인스턴스 생성 불가, 실행 중인 인스턴스 영향 없음, 스냅샷은 따로 지워야 함. 등록 해제 보호와 Recycle Bin 복원 있음.
- 공유: 소유한 AMI만, 지역 단위(다른 지역은 복사 뒤 공유), 받은 계정은 실행만 가능. 기본 AWS 관리 키로 암호화된 스냅샷 AMI는 공유 불가.

## 3. Google Cloud

- 사용자 이미지 패밀리는 가장 최근에 만든 이미지를 가리킴. 최신 이미지를 DEPRECATED로 바꾸면 패밀리가 이전 이미지로 돌아감(이전 이미지가 폐기 상태가 아닐 때).
- 승격 예: 시험 패밀리에 이미지를 만들고 시험한 뒤 `--source-image-family test-image-family --family prod-image-family`로 운영 패밀리에 복사.
- 상태: DEPRECATED(경고와 함께 실행 가능), OBSOLETE(실행 실패), DELETED(실행 불가). `--delete-in`, `--obsolete-on` 등 시간 지정.

## 4. 판 번호 규칙

- SemVer 2.0.0: X.Y.Z 음이 아닌 정수, 앞자리 0 금지. pre-release는 같은 판보다 낮음. build metadata(`+`)는 우선순위 비교에서 무시. `v1.2.3`의 `v`는 판의 일부가 아님.
- CalVer(페이지 2026-09-11): YYYY, YY, 0Y, M, 0M, D, 0D 등. 예 `YY.0M`(Ubuntu), `YYYY.MINOR`(JetBrains), `YYYY.0M.0D`. 0을 채운 형식은 SemVer로는 유효하지 않음. 하루 여러 번은 뒤에 일련 번호.

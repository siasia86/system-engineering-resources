---
name: minio-official-notes
description: MinIO 공식 저장소·문서 기반 S3-compatible Object Storage·AGPLv3·Versioning·Object Lock·Replication 참조 노트.
tags:
  - minio
  - object-storage
  - s3
  - agpl
  - versioning
  - object-lock
last_checked: 2026-11-09
sources:
  - https://github.com/minio/minio
  - https://github.com/minio/minio/blob/master/LICENSE
  - https://github.com/minio/docs
  - https://github.com/minio/mc
  - https://min.io/
---

# MinIO 공식 참조 노트

## 1. 프로젝트와 라이선스

- MinIO Server는 고성능 S3-compatible Object Storage입니다.
- 공식 GitHub 저장소의 라이선스는 AGPLv3입니다.
- MinIO Server와 상용 Enterprise 제품의 기능·지원·라이선스 범위는 구분해야 합니다.
- (2026-11-09 확인: `minio/minio`·`minio/mc` GitHub 저장소는 archived 상태이며 README는 "THIS REPOSITORY IS NO LONGER MAINTAINED"로 안내합니다. 커뮤니티판은 소스 전용 배포로 바뀌어 미리 빌드한 바이너리를 더 제공하지 않고, 마지막 GitHub 릴리스는 `RELEASE.2025-10-15T17-29-55Z`입니다. 대안으로 AIStor Free·Enterprise를 안내하며, 기존 docs.min.io 커뮤니티 문서 주소는 AIStor 문서로 이동합니다.)

## 2. 핵심 기능

- S3 API
- Bucket·Object 관리
- Erasure Coding
- Object Versioning
- Object Locking·Immutability
- Bucket·Site Replication
- Identity·Access Management
- TLS·Server-Side Encryption 연동
- Metrics·Logging·Notifications

## 3. 운영 경계

- MinIO는 일반 POSIX 파일시스템이 아니며 내부 데이터 디렉터리를 직접 조작하지 않습니다.
- MinIO는 백업 애플리케이션이 아닙니다. Restic·rclone·Bacula·Bareos 등과 S3 Backend로 연동합니다.
- Versioning·Object Lock·IAM은 별도의 보존·접근제어 계층입니다.
- 단일 MinIO 서버와 단일 디스크는 고가용성·백업을 보장하지 않습니다.
- Erasure Coding·Replication·Object Lock은 배포 형태와 버전에 따라 요구사항을 검증합니다.
- AGPLv3 의무와 상용 제품 조건은 외부 서비스 제공·수정 배포 전에 확인합니다.

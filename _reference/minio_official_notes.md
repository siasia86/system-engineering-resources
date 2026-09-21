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
last_checked: 2026-09-21
sources:
  - https://github.com/minio/minio
  - https://github.com/minio/minio/blob/master/LICENSE
  - https://docs.min.io/community/minio-object-store/
  - https://min.io/
---

# MinIO 공식 참조 노트

## 1. 프로젝트와 라이선스

- MinIO Server는 고성능 S3-compatible Object Storage입니다.
- 공식 GitHub 저장소의 라이선스는 AGPLv3입니다.
- MinIO Server와 상용 Enterprise 제품의 기능·지원·라이선스 범위는 구분해야 합니다.

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

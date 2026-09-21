# MinIO 범용 Object Storage 가이드
<!-- reference: _reference/minio_official_notes.md, _reference/aws_sts_iam_s3_kms_official_notes.md -->

MinIO는 자체 서버·VM·컨테이너·Kubernetes 환경에 구축할 수 있는 S3-compatible Object Storage입니다. 이 문서는 특정 애플리케이션이나 백업 도구에 종속되지 않도록 MinIO의 Object Storage 모델, 배포·보안·Versioning·Object Lock·Replication·운영 검증을 범용 관점에서 설명합니다.

> Object Storage: 파일을 디렉터리 계층보다 Bucket과 Object 단위로 저장하고 HTTP API로 접근하는 저장소 모델입니다. POSIX 파일시스템과 달리 inode·일반적인 파일 Lock·임의 위치 쓰기 semantics를 동일하게 제공하지 않습니다.

## 목차

| 섹션                                                                         | 내용                              |
|------------------------------------------------------------------------------|-----------------------------------|
| [1. MinIO 개요](#1-minio-개요)                                               | 제품 범위·라이선스·용도           |
| [2. Object Storage 모델](#2-object-storage-모델)                             | Bucket·Object·Metadata·API        |
| [3. 배포와 저장소 구성](#3-배포와-저장소-구성)                               | 단일 서버·분산·Erasure Coding     |
| [4. 보안과 접근제어](#4-보안과-접근제어)                                     | IAM·TLS·암호화·자격증명           |
| [5. Versioning·Object Lock·Replication](#5-versioningobject-lockreplication) | 보존·복제·재해 대응               |
| [6. 백업 도구 연계](#6-백업-도구-연계)                                       | Restic·rclone·Bacula·애플리케이션 |
| [7. 운영·검증 기준](#7-운영검증-기준)                                        | 상태·복구·용량·업그레이드         |
| [8. 선택 가이드](#8-선택-가이드)                                             | 범용 도입 판단                    |

## 1. MinIO 개요

### MinIO의 역할

MinIO Server는 S3 API를 사용하는 Object Storage입니다.

```text
Application / Backup Tool
          │
          v
       S3 API
          │
          v
        MinIO
          │
          v
   Disk / NVMe / Storage Pool
```

주요 사용 대상:

- 백업 Repository
- 로그·아카이브
- 애플리케이션 Object Storage
- 데이터셋·미디어 파일
- S3 API 개발·테스트
- 자체 운영이 필요한 사설 Object Storage

MinIO는 다음과 구분합니다.

- 일반 POSIX 파일시스템
- 데이터베이스
- 백업 정책·보존을 담당하는 백업 애플리케이션
- 하이퍼바이저·블록 스토리지

### 오픈소스와 상용 제품

공식 GitHub 저장소의 MinIO Server는 AGPLv3 라이선스로 공개되어 있습니다. MinIO의 상용 Enterprise 제품과 기능·지원·라이선스 범위는 별도로 확인합니다.

| 구분          | MinIO Server                          | 상용 Enterprise 제품      |
|---------------|---------------------------------------|---------------------------|
| 성격          | 오픈소스 S3-compatible Object Storage | 상용 지원·Enterprise 제품 |
| 라이선스      | AGPLv3                                | 상용 계약·조건 확인       |
| 자체 구축     | 가능                                  | 가능                      |
| 커뮤니티 사용 | 가능                                  | 제품별 지원 범위 확인     |
| 기술지원      | 커뮤니티·공식 문서                    | 공식 지원·구독 범위       |

AGPLv3 의무는 내부 사용, 수정 배포, 네트워크를 통한 서비스 제공 방식에 따라 검토 범위가 달라질 수 있습니다. 외부 고객에게 서비스로 제공하거나 코드를 수정해 배포할 때는 라이선스 원문과 법률 자문을 확인합니다.

### MinIO와 백업 도구

MinIO는 백업 Repository를 저장하는 Backend가 될 수 있지만, 자체적으로 전체 백업 정책을 완성하지는 않습니다.

```text
Restic / Borg / rclone / Bacula / Bareos
                  │
                  v
              MinIO S3 API
                  │
                  v
        Versioning·Retention·Replication
```

## 2. Object Storage 모델

### Bucket

Bucket은 Object를 논리적으로 분리하는 최상위 저장 단위입니다.

```text
Bucket: backup
├── host-a/
│   ├── 2026/09/21/
│   └── 2026/09/22/
├── host-b/
└── test/
```

Bucket 설계 시 다음을 분리합니다.

- 운영 데이터와 백업 데이터
- 환경별 데이터
- 조직·팀별 권한
- 보존 기간이 다른 데이터
- 테스트와 운영 Prefix

### Object

Object는 데이터와 Key·Metadata로 구성됩니다.

```text
Object
├── Key
├── Data
├── Size
├── ETag / Checksum
├── Content-Type
├── User Metadata
└── Version ID
```

Object Storage는 일반 파일시스템처럼 부분 수정하는 방식보다 Object 단위 업로드·조회·삭제를 중심으로 사용합니다.

### S3 API 호환성

MinIO는 S3 API 호환을 제공하지만 AWS S3의 모든 서비스·정책·확장 기능이 동일하게 동작한다는 의미는 아닙니다.

연동 전 다음을 검증합니다.

- 인증 방식
- Signature Version
- Path-style·Virtual-hosted-style Endpoint
- Multipart Upload
- Range Request
- Versioning
- Object Lock
- Lifecycle
- IAM Policy Condition
- SDK·CLI의 Endpoint 설정

## 3. 배포와 저장소 구성

### 단일 서버

```text
MinIO Server
└── Local Disk
```

학습·개발·기능 검증에 적합합니다. 운영 고가용성이나 디스크 장애 보호를 단일 서버가 제공한다고 가정하지 않습니다.

위험 요소:

- 서버 전체 장애
- 단일 디스크 장애
- 파일시스템 손상
- 관리자 자격증명 탈취
- 랜섬웨어
- 유지보수 중 서비스 중단

### 분산 구성

```text
MinIO Cluster
├── Node 01
│   ├── Disk 01
│   └── Disk 02
├── Node 02
│   ├── Disk 01
│   └── Disk 02
├── Node 03
└── Node 04
```

분산 구성에서는 다음 항목을 함께 설계합니다.

- 노드 수와 디스크 수
- 장애 허용 범위
- 네트워크 지연과 대역폭
- 디스크 교체·Healing
- TLS와 내부 통신
- 모니터링·알림
- 업그레이드 절차
- 장애 시 quorum과 접근 가능성

### Erasure Coding

> Erasure Coding: 데이터를 여러 조각과 복구용 parity 조각으로 분산하여 일부 디스크나 노드 장애 후에도 데이터를 복원할 수 있도록 하는 방식입니다. RAID와 유사한 목적이 있지만 구현·운영·성능 특성은 제품별로 다릅니다.

Erasure Coding은 디스크·노드 장애에 대한 저장소 복원력입니다. 다음을 대체하지 않습니다.

- 별도 백업
- 오프사이트 복사본
- 랜섬웨어 방어
- 애플리케이션 논리 복구

### MinIO 내부 데이터 경계

MinIO 내부 데이터 디렉터리는 MinIO가 관리합니다.

```text
❌ 내부 데이터 디렉터리 직접 수정
❌ 내부 파일 일부를 rsync로 복사
❌ S3 Mount에 파일 미러 도구를 직접 연결해 운영

✅ S3 API 사용
✅ MinIO Client(mc) 사용
✅ Restic·rclone·Bacula·Bareos 연계
```

MinIO를 일반 POSIX 파일시스템처럼 취급하면 Object Metadata·Versioning·Lock 상태와 실제 데이터의 관계가 깨질 수 있습니다.

## 4. 보안과 접근제어

### 자격증명 분리

```text
Admin Credential
└── 사용자·정책·Bucket 설정

Application Credential
└── 특정 Bucket·Prefix의 필요한 작업만 허용

Backup Upload Credential
├── 지정 Prefix에 Object 생성
├── 필요한 Object 조회
└── 삭제·정책 변경 금지
```

백업을 업로드하는 서버나 애플리케이션에 MinIO 전체 관리자 권한을 주지 않습니다.

### TLS

운영 환경에서는 S3 API Endpoint에 TLS를 적용합니다.

```text
Client
  │ HTTPS/TLS
  v
MinIO Endpoint
  │
  v
Object Storage
```

확인 항목:

- 인증서 이름과 Endpoint 일치
- 사설 CA 배포
- 인증서 만료 알림
- 내부·외부 Endpoint 분리
- 평문 HTTP 접근 차단 여부
- 관리 API와 데이터 API 접근 제한

### Server-Side Encryption

MinIO는 저장 데이터 암호화 구성을 지원합니다. 암호화 Key의 수명주기와 접근권한은 MinIO 데이터와 별도로 관리합니다.

```text
Client-side encryption
└── 클라이언트가 업로드 전 암호화

Server-side encryption
└── MinIO가 저장 시 암호화

KMS / Key Management
└── 암호화 Key 관리·회전·접근제어
```

암호화는 데이터 기밀성을 높이지만 삭제 방지나 불변성 자체를 제공하지 않습니다.

### AGPLv3 검토

다음 상황에서는 AGPLv3 의무를 확인합니다.

- MinIO Server 코드 수정
- 수정한 소프트웨어 배포
- 네트워크를 통해 외부 사용자에게 기능 제공
- MinIO를 기반으로 상용 Object Storage 서비스 제공
- MinIO Server와 상용 제품 기능 혼합

## 5. Versioning·Object Lock·Replication

### Object Versioning

Bucket Versioning은 Object를 덮어쓰거나 삭제할 때 이전 Version을 보존할 수 있게 합니다.

```text
Object key: backup/data.tar
├── Version 01
├── Version 02
└── Delete Marker
```

Versioning은 과거 Version을 보존하지만 다음 사항을 함께 관리해야 합니다.

- Version별 저장 비용
- Delete Marker
- Lifecycle 만료 정책
- Version 복구 방법
- 관리자 삭제 권한

### Object Lock과 Immutable Retention

> Object Lock: 보존 기간 동안 Object Version을 수정·삭제하지 못하도록 제한하는 기능입니다. WORM(Write Once, Read Many) 성격의 보존 정책으로 사용할 수 있지만, 실제 적용 방식은 Versioning·Retention Mode·권한 설정을 함께 검증해야 합니다.

Object Lock을 사용하는 경우 다음을 테스트합니다.

- Governance Mode·Compliance Mode의 차이
- Retention 기간
- Legal Hold
- 관리자 권한으로도 삭제 가능한지
- Lifecycle과의 관계
- 백업 도구의 삭제·정리 작업과 충돌 여부
- 복구 시 Version 선택 방법

### Replication

MinIO Replication은 다른 사이트나 Bucket으로 Object를 복제하는 기능입니다.

```text
Site A / Bucket A
        │
        v
Replication
        │
        v
Site B / Bucket B
```

Replication은 장애·사이트 분산에 유용하지만, 원본에서 잘못된 삭제나 암호화가 발생하면 변경 사항도 복제될 수 있습니다.

```text
Replication
└── 최신 데이터 분산

Immutable Backup
└── 과거 상태 보호
```

두 기능을 함께 구성해야 랜섬웨어와 운영 실수에 대한 복구력이 높아집니다.

## 6. 백업 도구 연계

### Restic

Restic은 MinIO를 S3-compatible Backend로 사용할 수 있습니다.

```bash
export RESTIC_REPOSITORY='s3:https://minio.example.com/restic/server-a'
export RESTIC_PASSWORD_FILE='/etc/restic/server-a.password'

restic init
restic backup /srv/data
restic snapshots
```

검증 항목:

- Endpoint와 TLS
- S3 인증정보
- Bucket·Prefix 권한
- Repository Password 보관
- `restic check`
- `restic restore`
- MinIO Versioning·Object Lock과 `prune`의 관계

상세 Restic 내용은 [Restic 범용 백업·복구 가이드](./restic_backup.md)를 참고합니다.

### rclone

```bash
rclone copy /srv/archive minio:backup/archive
rclone check /srv/archive minio:backup/archive
```

`rclone sync`는 원본에 없는 Object를 대상에서 삭제할 수 있으므로 dry-run부터 수행합니다.

```bash
rclone sync --dry-run /srv/archive minio:backup/archive
```

### Bacula·Bareos

Bacula·Bareos의 S3-compatible Storage 지원 범위는 제품 버전·Edition·Plugin·구성에 따라 확인합니다.

검토 항목:

- S3 Endpoint 설정
- Bucket·Prefix 권한
- Multipart Upload
- TLS
- Catalog와 Object 데이터의 관계
- Retention·Prune와 Object Lock의 충돌 여부
- 복구 작업 테스트

### 애플리케이션

애플리케이션은 MinIO를 단순 파일시스템처럼 사용하지 않고 S3 API 또는 SDK로 접근합니다.

```text
Application
├── PutObject
├── GetObject
├── ListObjects
├── DeleteObject
└── Version·Retention 정책 확인
```

## 7. 운영·검증 기준

### 기본 확인

MinIO Client(`mc`)를 사용하는 예시입니다.

```bash
mc alias set minio https://minio.example.com \
  Secureuser123 \
  SecurePassword123

mc admin info minio
mc ls minio
mc version info minio/backup
mc retention info minio/backup
```

예시 자격증명은 실제 환경에서 사용하지 않고 Secret Manager·환경별 Credential·IAM 연동으로 대체합니다.

### 검증 단계

| 단계 | 확인 내용                              |
|------|----------------------------------------|
| 1    | Endpoint TLS 인증서 검증               |
| 2    | Application Credential의 최소권한 확인 |
| 3    | Bucket Versioning 상태 확인            |
| 4    | Object Lock·Retention 정책 확인        |
| 5    | Object Upload·Read·List 테스트         |
| 6    | Object 삭제·Delete Marker 동작 확인    |
| 7    | Replication 지연·실패·재동기화 확인    |
| 8    | 실제 백업 도구의 Check·Restore 수행    |
| 9    | 노드·디스크 장애 시나리오 수행         |
| 10   | 복구 시간과 데이터 손실 범위 기록      |

### 용량과 성능

모니터링 항목:

- 디스크 사용량
- Bucket·Prefix별 사용량
- Erasure Coding 관련 Healing
- Object 업로드·조회 오류
- API latency
- 네트워크 처리량
- Replication backlog
- 인증 실패
- TLS 인증서 만료
- KMS·Key Management 오류

### 백업과 복구 주기

```text
백업 실행마다
└── Upload 종료 코드·Object 생성 확인

매일
└── Versioning·Replication·용량 확인

매주
└── 샘플 Object 복구

매월
└── 백업 Repository 전체 검사·복구 테스트

분기별
└── Bucket·Site 장애 및 랜섬웨어 복구 훈련
```

## 8. 선택 가이드

### MinIO가 적합한 경우

- S3 API 기반 자체 Object Storage가 필요합니다.
- 데이터가 사설 네트워크 안에 있어야 합니다.
- Restic·rclone·애플리케이션과 S3 API로 연동합니다.
- 디스크·노드·네트워크·TLS·권한을 직접 운영할 수 있습니다.
- Versioning·Object Lock·Replication을 직접 설계할 수 있습니다.

### AWS S3가 더 적합할 수 있는 경우

- 스토리지 서버 운영을 원하지 않습니다.
- 관리형 내구성·가용성·Lifecycle을 선호합니다.
- AWS IAM·CloudTrail·KMS·조직 정책과 통합해야 합니다.
- 물리 디스크·노드·업그레이드·복구 운영을 담당할 인력이 부족합니다.

### 최종 체크리스트

- S3 API 호환 범위가 애플리케이션 요구사항과 일치하는가?
- MinIO Server와 상용 제품의 라이선스·기능 범위를 구분했는가?
- 단일 서버와 분산 구성의 장애 차이를 이해했는가?
- Erasure Coding과 Replication이 필요한가?
- Object Versioning·Object Lock이 필요한가?
- 백업 업로드 계정에 Delete·Admin 권한을 주지 않았는가?
- TLS·Credential·KMS를 분리했는가?
- MinIO 자체 외부에 2차 백업이 있는가?
- 실제 Object·백업 Repository를 복구해 보았는가?
- 라이선스·지원·운영 비용을 검토했는가?

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- MinIO Server: [github.com/minio/minio](https://github.com/minio/minio) — ★★★☆☆
- MinIO Documentation: [docs.min.io/community/minio-object-store](https://docs.min.io/community/minio-object-store/) — ★★★☆☆
- MinIO Official Site: [min.io](https://min.io/) — ★★★☆☆
- [MinIO 공식 참조 노트](../../_reference/minio_official_notes.md)
- [Restic 범용 백업·복구 가이드](./restic_backup.md)
- [범용 백업 솔루션·도구 비교](./backup_tools_comparison.md)
- [AWS STS·IAM·S3·KMS 참조 노트](../../_reference/aws_sts_iam_s3_kms_official_notes.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-21

**마지막 업데이트**: 2026-09-21

© 2026 siasia86. Licensed under CC BY 4.0.

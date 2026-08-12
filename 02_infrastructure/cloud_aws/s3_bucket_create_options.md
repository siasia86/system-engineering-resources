# S3 버킷 생성 옵션 비교

S3 버킷 생성 시 선택하는 주요 옵션을 Web Console 기준으로 정리합니다.
각 옵션의 차이와 선택 기준을 비교합니다.

## 목차

| 섹션                                                                                               |
|----------------------------------------------------------------------------------------------------|
| [1. 버킷 유형](#1-버킷-유형) / [2. AWS 리전](#2-aws-리전) / [3. 버킷 이름](#3-버킷-이름)           |
| [4. 객체 소유권](#4-객체-소유권) / [5. 퍼블릭 액세스 차단](#5-퍼블릭-액세스-차단)                  |
| [6. 버전 관리](#6-버전-관리) / [7. 태그](#7-태그) / [8. 기본 암호화](#8-기본-암호화)               |
| [9. 고급 설정 — Object Lock](#9-고급-설정--object-lock) / [10. 선택 기준 요약](#10-선택-기준-요약) |

---

## 1. 버킷 유형

### 범용 vs 디렉터리

| 항목            | 범용 (General Purpose)             | 디렉터리 (Directory)                  |
|-----------------|------------------------------------|---------------------------------------|
| 스토리지 클래스 | S3 Standard, IA, Glacier 등 전체   | S3 Express One Zone 전용              |
| 가용 영역       | 리전 내 다중 AZ                    | 단일 AZ                               |
| 지연 시간       | 일반 (수십 ms)                     | 한 자릿수 ms (10배 빠름)              |
| 내구성          | 99.999999999% (11 nine)            | 명시되지 않음 (단일 AZ)               |
| 가격            | 낮음                               | 높음 (성능 프리미엄)                  |
| Object Lock     | ✅ 지원                            | ❌ 미지원                             |
| Lifecycle       | ✅ 지원                            | ❌ 미지원                             |
| S3 Replication  | ✅ 지원                            | ❌ 미지원                             |
| 버전 관리       | ✅ 지원                            | ❌ 미지원                             |
| 용도            | 일반 백업, 로그, 정적 웹, 아카이브 | ML 학습 데이터, 고빈도 트랜잭션, 캐시 |

🟡 디렉터리 버킷은 단일 AZ 장애 시 데이터 손실 위험이 있습니다. 중요 데이터에는 범용 버킷을 사용합니다.

---

## 2. AWS 리전

### 선택 기준

| 기준              | 설명                                                          |
|-------------------|---------------------------------------------------------------|
| 지연 시간         | 클라이언트(EC2, 사용자)와 가장 가까운 리전 선택               |
| 규제 준수         | 데이터 국외 반출 금지 규정 시 국내 리전 (ap-northeast-2) 필수 |
| 리전 간 전송 비용 | 동일 AZ 내 전송 무료, 다른 AZ 간·리전 간 전송은 유료          |
| DR 구성           | 메인 리전과 다른 리전에 복제 버킷 구성                        |

```bash
# 서울 리전 버킷 생성 예시
aws s3api create-bucket \
  --bucket my-bucket-123456789012-ap-northeast-2 \
  --region ap-northeast-2 \
  --create-bucket-configuration LocationConstraint=ap-northeast-2
```

🟡 `us-east-1`은 `--create-bucket-configuration` 옵션을 지정하면 오류가 발생합니다. us-east-1은 해당 옵션을 생략해야 합니다.

---

## 3. 버킷 이름

### 글로벌 네임스페이스 vs 계정-리전 네임스페이스

| 항목                    | 글로벌 네임스페이스만  | 계정ID + 리전 포함 (권장)  |
|-------------------------|------------------------|----------------------------|
| 이름 충돌               | 🟡 타 계정과 충돌 가능 | ✅ 계정ID로 유일성 보장    |
| 버킷 소유 계정 식별     | ❌ 불가                | ✅ 이름에서 즉시 파악      |
| Terraform 재사용        | 🟡 하드코딩 필요       | ✅ 변수 조합으로 자동 생성 |
| S3 Confused Deputy 방지 | ❌ 취약                | ✅ 계정ID 검증으로 방어    |
| 멀티 리전 운영          | 🟡 이름 충돌 위험      | ✅ 리전별 구분 명확        |

> S3 Confused Deputy: 공격자가 동일한 이름의 버킷을 다른 계정에 생성하여
> IAM Policy의 Resource ARN이 의도치 않은 버킷을 가리키게 만드는 공격입니다.
> 버킷 이름에 계정ID를 포함하면 이름 자체가 달라지므로 혼동이 불가합니다.

```
권장 네이밍 패턴:
  {목적}-{계정ID}-{리전}

예시:
  game-resource-db-123456789012-ap-northeast-2
  backup-logs-123456789012-ap-northeast-2
```

```bash
# Terraform 예시
bucket = "${var.purpose}-${data.aws_caller_identity.current.account_id}-${var.region}"
```

### 이름 규칙 제약

| 규칙              | 내용                                |
|-------------------|-------------------------------------|
| 길이              | 3~63자                              |
| 허용 문자         | 소문자, 숫자, 하이픈(`-`)           |
| 시작/끝 문자      | 소문자 또는 숫자만 가능             |
| IP 주소 형식 금지 | `192.168.1.1` 형태 불가             |
| 전역 유일성       | 전 세계 모든 AWS 계정에서 중복 불가 |

---

## 4. 객체 소유권

### ACL 비활성화 vs 활성화

| 항목                 | ACL 비활성화 (권장)             | ACL 활성화                     |
|----------------------|---------------------------------|--------------------------------|
| 소유권               | 버킷 소유자가 모든 객체 소유    | 업로드한 계정이 객체 소유      |
| 접근 제어 방식       | IAM Policy + 버킷 Policy만 사용 | ACL + Policy 혼용 가능         |
| Cross-account 업로드 | 버킷 Policy로 제어              | ACL로 개별 객체 권한 부여 가능 |
| 복잡도               | 낮음 (단순)                     | 높음 (ACL + Policy 혼재)       |
| AWS 권장             | ✅ 권장                         | 🟡 레거시 방식                 |

🟡 2023년 이후 생성 버킷은 ACL 비활성화가 기본값입니다. 특별한 이유가 없으면 비활성화를 유지합니다.

---

## 5. 퍼블릭 액세스 차단

### 4가지 설정 항목

| 설정 항목                                    | 설명                                 | 권장  |
|----------------------------------------------|--------------------------------------|-------|
| 새 ACL을 통한 퍼블릭 액세스 차단             | 새로 추가되는 ACL로 퍼블릭 허용 차단 | ✅ ON |
| 임의의 ACL을 통한 퍼블릭 액세스 차단         | 기존 ACL의 퍼블릭 허용도 무시        | ✅ ON |
| 새 퍼블릭 버킷/액세스 포인트 Policy 차단     | 새 버킷 Policy로 퍼블릭 허용 차단    | ✅ ON |
| 임의의 퍼블릭 버킷/액세스 포인트 Policy 차단 | 기존 Policy의 퍼블릭 허용도 차단     | ✅ ON |

| 용도                 | 퍼블릭 액세스 차단 설정                   |
|----------------------|-------------------------------------------|
| 내부 백업, 로그, DB  | 전체 ON (기본값 유지)                     |
| 정적 웹사이트 호스팅 | 전체 OFF (CloudFront 병행 권장)           |
| CloudFront Origin    | 전체 ON + OAC(Origin Access Control) 사용 |

🟡 정적 웹사이트 목적이라도 퍼블릭 액세스를 직접 여는 것보다 CloudFront + OAC 조합을 권장합니다.

---

## 6. 버전 관리

### 비활성화 vs 활성화

| 항목                     | 비활성화                   | 활성화                            |
|--------------------------|----------------------------|-----------------------------------|
| 동일 key 재업로드        | 기존 파일 교체 (복구 불가) | 새 버전 추가 (이전 버전 보존)     |
| 삭제 동작                | 즉시 삭제                  | Delete Marker 생성 (복구 가능)    |
| 스토리지 비용            | 낮음                       | 🟡 버전 누적 시 증가              |
| Object Lock 사용         | ❌ 불가                    | ✅ 전제 조건                      |
| 롤백 가능 여부           | ❌ 불가                    | ✅ 가능                           |
| Lifecycle 이전 버전 삭제 | 해당 없음                  | 별도 규칙 필요 (없으면 영구 누적) |

```bash
# 버전 관리 활성화
aws s3api put-bucket-versioning \
  --bucket my-bucket \
  --versioning-configuration Status=Enabled

# 버전 목록 확인
aws s3api list-object-versions \
  --bucket my-bucket \
  --prefix resource/A.db \
  --query 'Versions[].[VersionId,LastModified,IsLatest]' \
  --output table
```

🟡 버전 관리를 한번 활성화하면 비활성화가 불가합니다. Suspended(중단) 상태로만 전환됩니다. Suspended 전환 후에도 기존 버전은 삭제되지 않습니다.

---

## 7. 태그

### 권장 태그 구성

| 키            | 값 예시               | 용도                         |
|---------------|-----------------------|------------------------------|
| `Name`        | `game-resource-db`    | 리소스 식별                  |
| `Environment` | `prod` / `dev`        | 환경 구분                    |
| `Project`     | `game-backend`        | 프로젝트 분류                |
| `Owner`       | `infra-team`          | 담당팀                       |
| `CostCenter`  | `cc-1234`             | 비용 배분                    |
| `DataClass`   | `internal` / `public` | 데이터 분류 (보안 정책 적용) |

태그는 비용 배분(Cost Allocation Tags), S3 Lifecycle 조건, IAM Policy 조건(ABAC)에 활용됩니다.

---

## 8. 기본 암호화

### SSE 방식 비교

| 항목         | SSE-S3        | SSE-KMS (권장)                       | DSSE-KMS                   |
|--------------|---------------|--------------------------------------|----------------------------|
| 키 관리      | AWS 자동 관리 | KMS CMK (사용자 제어)                | KMS CMK (이중 암호화)      |
| 키 교체      | 자동          | 수동 또는 자동 (설정 가능)           | 수동 또는 자동             |
| 접근 감사    | ❌ 불가       | ✅ CloudTrail KMS API 로깅           | ✅ CloudTrail KMS API 로깅 |
| 키 권한 제어 | ❌ 불가       | ✅ KMS Key Policy로 세분화           | ✅ KMS Key Policy로 세분화 |
| 추가 비용    | 없음          | 🟡 KMS API 호출 비용 발생            | 🟡 SSE-KMS보다 높음        |
| 규제 준수    | 일반          | 금융, 의료, 공공 기관 요건 충족 가능 | 상위 규제 요건             |
| Bucket Key   | 해당 없음     | ✅ 활성화 권장 (비용 절감)           | ✅ 활성화 권장             |

```bash
# SSE-KMS + Bucket Key 활성화
aws s3api put-bucket-encryption \
  --bucket my-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:ap-northeast-2:123456789012:key/KEY-ID"
      },
      "BucketKeyEnabled": true
    }]
  }'
```

> Bucket Key: S3가 KMS를 직접 호출하는 대신 버킷 레벨 데이터 키를 캐싱하여
> KMS API 호출 횟수를 줄이는 기능입니다. SSE-KMS 비용을 최대 99% 절감합니다.

---

## 9. 고급 설정 — Object Lock

### 활성화 조건 및 주의사항

| 항목        | 내용                                   |
|-------------|----------------------------------------|
| 활성화 시점 | 버킷 생성 시에만 가능 (이후 추가 불가) |
| 버전 관리   | 자동 활성화 (비활성화 불가)            |
| 비활성화    | 불가 (한번 켜면 영구 적용)             |
| 버킷 유형   | 범용 버킷만 지원 (디렉터리 버킷 불가)  |

### 모드 선택

| 모드       | 삭제 가능 여부                                      | 용도                              |
|------------|-----------------------------------------------------|-----------------------------------|
| Governance | 특별 권한(`BypassGovernanceRetention`) 보유 시 가능 | 내부 보호, 테스트, 게임 리소스 DB |
| Compliance | 누구도 불가 (root 포함)                             | 금융·의료·공공 규제 준수          |

🟡 Compliance 모드는 보존 기간 내 삭제가 불가합니다. 설정 전 법무/컴플라이언스팀 확인 및 비용 시뮬레이션이 필수입니다.

상세 내용은 [s3_object_lock.md](s3_object_lock.md) 참고.

---

## 10. 선택 기준 요약

### 용도별 권장 설정

| 용도                 | 버킷 유형 | 퍼블릭 차단 | 버전 관리 | 암호화  | Object Lock         |
|----------------------|-----------|-------------|-----------|---------|---------------------|
| 게임 리소스 DB 백업  | 범용      | 전체 ON     | ON        | SSE-KMS | Governance 30일     |
| 유저 데이터 백업     | 범용      | 전체 ON     | ON        | SSE-KMS | OFF (GDPR 고려)     |
| 정적 웹사이트        | 범용      | OFF         | OFF       | SSE-S3  | OFF                 |
| ML 학습 데이터       | 디렉터리  | 전체 ON     | ❌ 미지원 | SSE-S3  | ❌ 미지원           |
| 감사 로그            | 범용      | 전체 ON     | ON        | SSE-KMS | Compliance 또는 OFF |
| CloudFront 배포 원본 | 범용      | 전체 ON     | ON        | SSE-S3  | OFF                 |

---

## 참고 자료

- AWS Documentation: [docs.aws.amazon.com/s3](https://docs.aws.amazon.com/s3/latest/userguide/creating-bucket.html) — ★★★☆☆
- AWS Documentation: [S3 Express One Zone](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-express-one-zone.html) — ★★★☆☆
- [s3_object_lock.md](s3_object_lock.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-08-12

**마지막 업데이트**: 2026-08-12

© 2026 siasia86. Licensed under CC BY 4.0.

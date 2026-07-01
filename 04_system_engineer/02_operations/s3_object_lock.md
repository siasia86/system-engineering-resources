# S3 Object Lock

S3 객체를 일정 기간 또는 영구적으로 삭제·덮어쓰기 불가하게 만드는 WORM(Write Once Read Many) 기능입니다. 랜섬웨어, 내부자 실수, 규제 준수 요구사항에 대응합니다.

## 목차

| 섹션                                                                                               |
|----------------------------------------------------------------------------------------------------|
| [1. 개념](#1-개념) / [2. 모드 비교](#2-모드-비교) / [3. 활성화 조건](#3-활성화-조건)               |
| [4. 설정](#4-설정) / [5. 운영](#5-운영) / [6. Cross-account 백업 연계](#6-cross-account-백업-연계) |
| [7. 트러블슈팅](#7-트러블슈팅)                                                                     |

---

## 1. 개념

### Object Lock이란

S3에 저장된 객체를 **보존 기간 동안 삭제·덮어쓰기 불가**하게 만드는 기능입니다. 금융(SEC 17a-4), 의료(HIPAA), 공공기관 규제에서 요구하는 WORM 스토리지를 AWS에서 구현합니다.

### 왜 필요한가

| 위협                         | Object Lock 없음     | Object Lock 있음                 |
|------------------------------|----------------------|----------------------------------|
| 관리자 실수 (rm -rf)         | 삭제됨               | 거부됨                           |
| 랜섬웨어 (덮어쓰기)          | 암호화된 파일로 교체 | 거부됨                           |
| 내부자 악의적 삭제           | 삭제됨               | 거부됨 (Compliance: root도 불가) |
| 공격자 침입 후 증거 인멸     | 삭제됨               | 거부됨                           |
| 규제 감사 (데이터 보존 증명) | 증명 불가            | Object Lock 설정 자체가 증명     |

### WORM 개념

```
Write Once Read Many (WORM)
  - Write Once: 한 번 쓰면
  - Read Many: 여러 번 읽을 수 있지만
  - 수정/삭제: 보존 기간 내 불가
```

---

## 2. 모드 비교

### Governance vs Compliance

| 항목             | Governance                     | Compliance                        |
|------------------|--------------------------------|-----------------------------------|
| 삭제 가능 여부   | 특별 권한 있으면 가능          | 누구도 불가 (root 포함)           |
| 보존 기간 단축   | 가능 (특별 권한)               | 불가                              |
| 보존 기간 연장   | 가능                           | 가능                              |
| 모드 변경        | Compliance로 변경 가능         | 변경 불가                         |
| AWS Support 요청 | 해제 가능                      | 해제 불가                         |
| 용도             | 테스트, 일반 보호, 내부 정책   | 규제 준수 (금융, 의료, 법적 보존) |
| 필요 권한        | `s3:BypassGovernanceRetention` | 해당 없음 (우회 불가)             |

### Retention Period vs Legal Hold

| 항목      | Retention Period              | Legal Hold                   |
|-----------|-------------------------------|------------------------------|
| 기간      | 고정 (1일~N년)                | 무기한                       |
| 해제 조건 | 기간 경과 시 자동 해제        | 수동 해제 (명시적 OFF)       |
| 설정 단위 | 버킷 기본값 또는 개별 객체    | 개별 객체                    |
| 동시 사용 | Legal Hold와 병행 가능        | Retention과 병행 가능        |
| 용도      | 정기 백업 보존 (30일, 1년 등) | 소송 중 증거 보전, 감사 대응 |

### 조합 예시

```
Case 1: Retention 30일 + Legal Hold OFF
  → 30일 후 삭제 가능

Case 2: Retention 30일 + Legal Hold ON
  → 30일 지나도 삭제 불가 (Legal Hold 해제 시까지)

Case 3: Retention 없음 + Legal Hold ON
  → Legal Hold 해제 전까지 삭제 불가
```

---

## 3. 활성화 조건

### 제약사항

| 항목                     | 내용                                               |
|--------------------------|----------------------------------------------------|
| 활성화 시점              | 버킷 생성 시에만 가능 (기존 버킷에 추가 불가)      |
| 버전 관리                | 필수 (Object Lock 활성화 시 자동 활성화)           |
| 비활성화                 | 불가 (한번 켜면 끌 수 없음)                        |
| 기존 데이터 마이그레이션 | 새 버킷 생성 → 데이터 복사 필요                    |
| S3 Replication           | 대상 버킷도 Object Lock 활성화 필요                |
| Lifecycle 삭제           | Retention 기간 내 삭제 안 됨 (Lifecycle Rule 무시) |

### 버전 관리와의 관계

```
Object Lock ON → 버전 관리 자동 ON (끌 수 없음)

s3 cp A.file (동일 key):
  → v1 생성 (잠금)
  → v2 생성 (새 버전, 별도 잠금)
  → v1은 보존 기간까지 삭제 불가
  → v2도 별도 보존 기간 적용

결과: 버전별로 독립적인 잠금
```

---

## 4. 설정

### 4.1 버킷 생성 (Object Lock 활성화)

#### 웹 콘솔

1. S3 → 버킷 만들기
2. 버킷 이름 입력
3. **객체 잠금** → 활성화 선택
4. "이 설정을 활성화하면 비활성화할 수 없습니다" 확인 체크
5. 버킷 만들기

#### CLI

```bash
aws s3api create-bucket \
  --bucket my-lock-bucket \
  --region ap-northeast-2 \
  --create-bucket-configuration LocationConstraint=ap-northeast-2 \
  --object-lock-enabled-for-bucket
```

### 4.2 기본 보존 설정

#### 웹 콘솔

1. 버킷 → 속성 탭 → 객체 잠금 → 편집
2. 기본 보존 활성화
3. 모드 선택: Governance 또는 Compliance
4. 보존 기간: 일 또는 년 단위 입력
5. 저장

#### CLI — Governance 모드 (30일)

```bash
aws s3api put-object-lock-configuration \
  --bucket my-lock-bucket \
  --object-lock-configuration '{
    "ObjectLockEnabled": "Enabled",
    "Rule": {
      "DefaultRetention": {
        "Mode": "GOVERNANCE",
        "Days": 30
      }
    }
  }'
```

#### CLI — Compliance 모드 (365일)

```bash
aws s3api put-object-lock-configuration \
  --bucket my-lock-bucket \
  --object-lock-configuration '{
    "ObjectLockEnabled": "Enabled",
    "Rule": {
      "DefaultRetention": {
        "Mode": "COMPLIANCE",
        "Days": 365
      }
    }
  }'
```

### 4.3 개별 객체 보존 설정

```bash
# 특정 객체에 Retention 적용
aws s3api put-object-retention \
  --bucket my-lock-bucket \
  --key backup/2026-07-01/data.tar.zst \
  --retention '{
    "Mode": "GOVERNANCE",
    "RetainUntilDate": "2026-08-01T00:00:00Z"
  }'
```

### 4.4 Legal Hold 적용/해제

```bash
# Legal Hold ON
aws s3api put-object-legal-hold \
  --bucket my-lock-bucket \
  --key backup/evidence/audit.tar.zst \
  --legal-hold Status=ON

# Legal Hold OFF
aws s3api put-object-legal-hold \
  --bucket my-lock-bucket \
  --key backup/evidence/audit.tar.zst \
  --legal-hold Status=OFF
```

### 4.5 Governance 모드 우회 삭제

```bash
# 특별 권한(s3:BypassGovernanceRetention) 보유 시에만 가능
aws s3api delete-object \
  --bucket my-lock-bucket \
  --key backup/test.tar.zst \
  --version-id "abc123" \
  --bypass-governance-retention
```

🟡 Compliance 모드에서는 이 옵션이 동작하지 않습니다.

---

## 5. 운영

### 5.1 중복 버전 확인

```bash
# 특정 객체의 버전 목록
aws s3api list-object-versions \
  --bucket my-lock-bucket \
  --prefix backup/A.file \
  --query 'Versions[].[LastModified,Size,VersionId,IsLatest]' \
  --output table

# 버전 2개 이상인 객체 찾기 (중복 탐지)
aws s3api list-object-versions \
  --bucket my-lock-bucket \
  --query 'Versions[].Key' \
  --output text | tr '\t' '\n' | sort | uniq -c | sort -rn | awk '$1 > 1'

# 이전 버전 총 용량 (낭비 확인)
aws s3api list-object-versions \
  --bucket my-lock-bucket \
  --query 'Versions[?IsLatest==`false`].[Size]' \
  --output text | awk '{sum+=$1} END {printf "old versions: %.2f GB\n", sum/1024/1024/1024}'

# 중복 버전 존재 여부 (한 줄)
aws s3api list-object-versions --bucket my-lock-bucket \
  --query 'length(Versions[?IsLatest==`false`])'
```

### 5.2 비용 영향

| 항목                   | 영향                                                    |
|------------------------|---------------------------------------------------------|
| 버전 관리 필수         | 덮어쓰기 시 이전 버전 유지 → 저장 용량 증가             |
| Retention 내 삭제 불가 | Lifecycle Rule로 자동 삭제 안 됨 → 비용 고정            |
| Glacier 전환           | 가능 (Lifecycle Transition은 동작함)                    |
| 불필요 버전 누적       | `s3 cp` 반복 시 버전 쌓임 → size 비교 후 skip 로직 필요 |

### 5.3 s3 sync vs s3 cp 주의점

| 명령어              | Object Lock 환경 동작                     |
|---------------------|-------------------------------------------|
| `s3 sync`           | 변경 없으면 skip → 불필요 버전 생성 안 됨 |
| `s3 cp`             | 무조건 업로드 → 매번 새 버전 생성 (낭비)  |
| `s3 cp` + 사전 비교 | ETag/size 비교 후 skip → 안전             |

```bash
# 추천: sync 사용
aws s3 sync /opt/backup/ s3://my-lock-bucket/backup/

# cp 사용 시: 업로드 전 비교 필수
REMOTE_SIZE=$(aws s3api head-object --bucket my-lock-bucket --key backup/A.file   --query 'ContentLength' --output text 2>/dev/null || echo "0")
LOCAL_SIZE=$(stat -c%s /opt/backup/A.file)
if [ "$LOCAL_SIZE" != "$REMOTE_SIZE" ]; then
  aws s3 cp /opt/backup/A.file s3://my-lock-bucket/backup/A.file
fi
```

### 5.4 보존 상태 확인

```bash
# 개별 객체 Retention 확인
aws s3api get-object-retention \
  --bucket my-lock-bucket \
  --key backup/2026-07-01/data.tar.zst

# Legal Hold 상태 확인
aws s3api get-object-legal-hold \
  --bucket my-lock-bucket \
  --key backup/evidence/audit.tar.zst

# 버킷 기본 설정 확인
aws s3api get-object-lock-configuration \
  --bucket my-lock-bucket
```

---

## 6. Cross-account 백업 연계

### STS AssumeRole + Object Lock 조합

```
A Account EC2                              B Account
┌──────────────────────┐                   ┌────────────────────────────────┐
│ assume-role          │                   │ Role: backup-writer            │
│                      │──────────────────>│   Policy: s3:PutObject (only)  │
│ s3 sync ─────────────│──────────────────>│                                │
│                      │                   │ Bucket: Object Lock ON         │
│ (s3:DeleteObject X)  │                   │   Governance 30d               │
│                      │                   │   → 30d later: Glacier         │
└──────────────────────┘                   └────────────────────────────────┘

Defense in depth:
  Layer 1: STS (temp token, no permanent key)
  Layer 2: IAM (no DeleteObject permission)
  Layer 3: Object Lock (delete denied even with permission)
```

### B계정 Role 권한 (DeleteObject 제외)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-lock-bucket",
        "arn:aws:s3:::my-lock-bucket/*"
      ]
    }
  ]
}
```

### 방어 계층 정리

| 계층           | 방어 내용                  | 차단 대상                        |
|----------------|----------------------------|----------------------------------|
| STS AssumeRole | 임시 토큰 + 자동 만료      | 키 유출                          |
| IAM Policy     | DeleteObject 미부여        | 정상 삭제 시도                   |
| Object Lock    | 보존 기간 내 삭제 거부     | root 포함 모든 삭제 (Compliance) |
| 버전 관리      | 덮어쓰기 시 이전 버전 보존 | 데이터 교체 공격                 |

> 상세 STS 설정은 [s3_cross_account_backup.md](../99_ETC/01_AWS_jobs/s3_cross_account_backup.md) 참고

---

## 7. 트러블슈팅

| 에러                                                  | 원인                              | 해결                                     |
|-------------------------------------------------------|-----------------------------------|------------------------------------------|
| `AccessDenied` on DeleteObject                        | Retention 기간 내 삭제 시도       | 보존 기간 만료 대기 또는 Governance 우회 |
| `InvalidRequest: Object Lock not enabled`             | 기존 버킷에 Object Lock 적용 시도 | 새 버킷 생성 후 데이터 복사              |
| `ObjectLockConfigurationNotFound`                     | 설정 조회 실패                    | Object Lock 미활성화 버킷                |
| Lifecycle 삭제 안 됨                                  | Retention 기간 > Lifecycle Days   | Lifecycle은 Retention 이후에만 동작      |
| 버전 용량 계속 증가                                   | `s3 cp` 반복 실행                 | `s3 sync` 또는 사전 비교 로직 추가       |
| Compliance 모드 해제 불가                             | 설계상 의도된 동작                | 보존 기간 만료까지 대기 (방법 없음)      |
| `OperationAborted: conflicting conditional operation` | 동시 Retention 변경               | 재시도 (경합 상태)                       |

### Compliance 모드 설정 전 체크리스트

- [ ] 보존 기간이 정확한지 확인 (설정 후 변경 불가)
- [ ] 테스트 버킷에서 Governance로 먼저 검증
- [ ] 비용 시뮬레이션 (Retention 기간 x 데이터량 x 단가)
- [ ] 법무/컴플라이언스팀 확인 (규제 요구사항 매칭)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-01

**마지막 업데이트**: 2026-07-01

© 2026 siasia86. Licensed under CC BY 4.0.

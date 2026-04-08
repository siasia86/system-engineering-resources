# S3 Gateway Endpoint 크로스 계정 설정 가이드

A계정 EC2 (10.120.0.0/20) → B계정 S3 버킷 업로드 구성 (동일 리전: us-east-1)

## 구성도

```
+---------------------------+          +---------------------------+
|  A계정 (us-east-1)        |          |  B계정 (us-east-1)        |
|                           |          |                           |
|  EC2 (10.120.0.0/20)     |          |  S3 Bucket               |
|    |                      |          |    (b-account-bucket)     |
|    v                      |          |                           |
|  S3 Gateway Endpoint      |  ------> |  Bucket Policy            |
|  (vpce-xxxx)              |          |    (A계정 허용)           |
+---------------------------+          +---------------------------+
```

## 1단계: A계정 - S3 Gateway Endpoint 생성

```bash
# VPC ID 확인
aws ec2 describe-vpcs \
  --filters "Name=cidr,Values=10.120.0.0/20" \
  --query "Vpcs[].VpcId" --output text \
  --region us-east-1

# EC2가 속한 서브넷의 라우트 테이블 확인
aws ec2 describe-route-tables \
  --filters "Name=vpc-id,Values=vpc-xxxxxxxx" \
  --query "RouteTables[].[RouteTableId,Associations[].SubnetId]" \
  --output table \
  --region us-east-1

# Gateway Endpoint 생성
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxxxxxxx \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-xxxxxxxx \
  --region us-east-1
```

## 2단계: B계정 - S3 버킷 정책 (크로스 계정 허용)

B계정의 S3 버킷에 아래 정책을 적용합니다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowFromAccountAVpce",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<A계정 12자리 ID>:root"
      },
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::b-account-bucket",
        "arn:aws:s3:::b-account-bucket/*"
      ],
      "Condition": {
        "StringEquals": {
          "aws:sourceVpce": "vpce-xxxxxxxx"
        }
      }
    }
  ]
}
```

> ⚠️ `aws:sourceVpce` 조건은 선택사항입니다. VPC Endpoint를 통한 접근만 허용하려면 추가하고, 제한 없이 A계정 전체를 허용하려면 `Condition` 블록을 제거합니다.

## 3단계: A계정 - IAM 정책 (EC2에서 B계정 S3 접근)

A계정의 EC2에 연결된 IAM Role에 아래 정책을 추가합니다.

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
        "arn:aws:s3:::b-account-bucket",
        "arn:aws:s3:::b-account-bucket/*"
      ]
    }
  ]
}
```

## 4단계: A계정 - VPC Endpoint 정책 (선택)

Endpoint에서 B계정 버킷만 허용하도록 제한할 수 있습니다.

```bash
aws ec2 modify-vpc-endpoint \
  --vpc-endpoint-id vpce-xxxxxxxx \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": "*",
        "Action": [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ],
        "Resource": [
          "arn:aws:s3:::b-account-bucket",
          "arn:aws:s3:::b-account-bucket/*"
        ]
      }
    ]
  }' \
  --region us-east-1
```

## 5단계: 테스트

```bash
# A계정 EC2에서 실행
aws s3 ls s3://b-account-bucket/ --region us-east-1
aws s3 cp test.txt s3://b-account-bucket/test.txt --region us-east-1
```

## 확인 체크리스트

| #   | 항목                          | 확인 방법                        |
|-----|-------------------------------|----------------------------------|
| 1   | Gateway Endpoint 생성         | describe-vpc-endpoints           |
| 2   | 라우트 테이블에 pl-xxx 경로   | describe-route-tables            |
| 3   | B계정 버킷 정책 (A계정 허용)  | s3api get-bucket-policy          |
| 4   | A계정 IAM Role (B버킷 접근)   | iam get-role-policy              |
| 5   | EC2 → S3 업로드 테스트        | aws s3 cp                        |

## AWS 콘솔(웹)에서 설정하는 방법

### 1단계: A계정 - S3 Gateway Endpoint 생성

1. AWS 콘솔 → VPC → 좌측 메뉴 `엔드포인트` → `엔드포인트 생성`
2. 설정:
   - 서비스 카테고리: `AWS 서비스`
   - 서비스: `com.amazonaws.us-east-1.s3` (Type: Gateway)
   - VPC: `10.120.0.0/20` VPC 선택
   - 라우트 테이블: EC2가 속한 서브넷의 라우트 테이블 체크
   - 정책: `전체 액세스` (기본값)
3. `엔드포인트 생성` 클릭

### 2단계: B계정 - S3 버킷 정책

1. B계정 AWS 콘솔 → S3 → 대상 버킷 선택
2. `권한` 탭 → `버킷 정책` → `편집`
3. 아래 JSON 붙여넣기:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowFromAccountAVpce",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<A계정 12자리 ID>:root"
      },
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::b-account-bucket",
        "arn:aws:s3:::b-account-bucket/*"
      ]
    }
  ]
}
```

4. `변경 사항 저장`

### 3단계: A계정 - IAM 정책

1. A계정 AWS 콘솔 → IAM → 역할 → EC2에 연결된 Role 선택
2. `권한 추가` → `인라인 정책 생성` → `JSON`
3. 아래 JSON 붙여넣기:

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
        "arn:aws:s3:::b-account-bucket",
        "arn:aws:s3:::b-account-bucket/*"
      ]
    }
  ]
}
```

4. 정책 이름 입력 (예: `cross-account-s3-upload`) → `정책 생성`

### 4단계: 확인

1. VPC → 엔드포인트 → 생성된 vpce 상태가 `사용 가능` 확인
2. VPC → 라우트 테이블 → 해당 라우트 테이블에 `pl-xxxxxxxx` (S3 prefix list) 경로 자동 추가 확인
3. EC2에서 테스트:

```bash
aws s3 ls s3://b-account-bucket/ --region us-east-1
aws s3 cp test.txt s3://b-account-bucket/test.txt --region us-east-1
```

## 주의사항

- 양쪽 모두 정책이 필요합니다 (A계정 IAM + B계정 버킷 정책)
- Gateway Endpoint는 무료이며, 같은 리전 S3 트래픽이 인터넷을 거치지 않습니다
- EC2가 Private 서브넷이면 Gateway Endpoint가 필수, Public 서브넷이면 선택사항 (비용 절감 목적)

---

**마지막 업데이트**: 2026-04-01

# 로그 통합 서버 아키텍처 — 100GB/일 규모

감사/분석 목적, 5년 보관, AWS + IDC 혼합 환경 기준 설계입니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 요구사항](#1-요구사항) / [2. 아키텍처 개요](#2-아키텍처-개요) / [3. 컴포넌트 상세](#3-컴포넌트-상세) |
| [4. 스토리지 설계](#4-스토리지-설계) / [5. 비용 추산](#5-비용-추산) / [6. 구축 순서](#6-구축-순서)       |

## 1. 요구사항

| 항목         | 요구                                                                          | 관련 절            |
|--------------|-------------------------------------------------------------------------------|--------------------|
| 목적·보관    | 감사·분석, 5년 보관                                                           | 서두               |
| 환경         | AWS + IDC 혼합, AWS 서울 리전(ap-northeast-2)                                 | 서두, 5절          |
| 수집량       | 원본 JSON 100GB/일 (IDC·AWS 서버의 Filebeat)                                  | 제목, 2절          |
| IDC→AWS 연결 | Direct Connect 또는 Site-to-Site VPN                                          | 3절 수집 계층      |
| 처리         | Logstash 2대 Active-Active (파싱, 민감정보 마스킹)                            | 3절 처리 계층      |
| 운영 조회    | OpenSearch 최근 30일, 일일 약 33GB(~3:1), 복제 포함 3TB                       | 3절 단기 저장, 4절 |
| 장기 보관    | Parquet(~10:1) S3 Standard 90일 → S3 Glacier Instant Retrieval, 5년 누적 18TB | 3절 장기 저장, 4절 |
| 분석         | Athena로 S3 장기 로그 SQL 조회                                                | 3절 분석 계층      |
| 보안·무결성  | SSE-KMS 암호화, S3 Versioning + Object Lock                                   | 3절 장기 저장      |

## 2. 아키텍처 개요

```
IDC Servers                    AWS
┌─────────────┐               ┌─────────────────────────────────────┐
│ App / DB    │               │                                     │
│ OS / Infra  ├──Filebeat──►  │  Logstash (EC2)                     │
│             │               │      │                              │
└─────────────┘               │      ▼                              │
                              │  OpenSearch  ◄── Dashboards (search)│
AWS Servers                   │  (hot: 30d)                         │
┌─────────────┐               │      │                              │
│ EC2 / ECS   ├──Filebeat──►  │      ▼                              │
│ Lambda Logs │               │   S3 (archive, 5yr)                 │
└─────────────┘               │      │                              │
                              │      ▼                              │
                              │  Athena (ad-hoc SQL on S3)          │
                              └─────────────────────────────────────┘
```

## 3. 컴포넌트 상세

### 수집 계층 — Filebeat

| 항목     | 내용                                      |
|----------|-------------------------------------------|
| 역할     | 5년 장기 보관 (감사 로그 원본)            |
| 스토리지 | S3 Standard -> 90일 후 S3 Glacier Instant |
| 포맷     | Parquet (Athena 쿼리 최적화, gzip 압축)   |
| 암호화   | SSE-KMS                                   |
| 버전관리 | S3 Versioning + Object Lock (감사 무결성) |

IDC → AWS 구간은 Direct Connect 또는 Site-to-Site VPN을 사용합니다.

### 처리 계층 — Logstash

| 항목     | 내용                                          |
|----------|-----------------------------------------------|
| 역할     | 파싱, 필터링, 인덱스 라우팅                   |
| 인스턴스 | t3.large × 2 (Active-Active)                  |
| 주요기능 | grok 파싱, 민감정보 마스킹, 타임스탬프 정규화 |

### 단기 저장 — OpenSearch

| 항목      | 내용                               |
|-----------|------------------------------------|
| 역할      | 최근 30일 로그 검색/분석           |
| 인스턴스  | r6g.large.search × 3 (3 AZ)        |
| 스토리지  | gp3 EBS 3TB (샤드 × 3 복제본)      |
| 보관 기간 | 30일 후 S3로 이동 (OpenSearch ISM) |

### 장기 저장 — S3

| 항목     | 내용                                      |
|----------|-------------------------------------------|
| 역할     | 5년 장기 보관 (감사 로그 원본)            |
| 스토리지 | S3 Standard → 90일 후 S3 Glacier Instant  |
| 포맷     | Parquet (Athena 쿼리 최적화, gzip 압축)   |
| 암호화   | SSE-KMS                                   |
| 버전관리 | S3 Versioning + Object Lock (감사 무결성) |

### 분석 계층 — Athena

| 항목 | 내용                                        |
|------|---------------------------------------------|
| 역할 | S3 장기 로그 SQL 조회 (감사 이벤트 추출 등) |
| 비용 | 스캔 데이터 $5/TB (Parquet 압축으로 절감)   |
| 활용 | 월별 감사 리포트, 특정 기간 이벤트 검색     |

## 4. 스토리지 설계

### 데이터 흐름 및 보관 정책

```
수집 (원본 JSON)
    │
    ├──► OpenSearch  보관 30일  (검색/실시간 조회)
    │
    └──► S3 Standard 보관 90일
              │
              └──► S3 Glacier Instant  보관 5년
                   (90일~5년, 감사 원본 Parquet)
```

### 용량 추산

| 구간         | 압축률 | 일일  | 연간  | 5년      |
|--------------|--------|-------|-------|----------|
| 원본 JSON    | -      | 100GB | 36TB  | 180TB    |
| Parquet+gzip | ~10:1  | 10GB  | 3.6TB | 18TB     |
| OpenSearch   | ~3:1   | 33GB  | 1TB   | (30일분) |

## 5. 비용 추산

월 기준 (ap-northeast-2 서울 리전):

| 항목                                | 산식                                       | 월 비용 (USD)  |
|-------------------------------------|--------------------------------------------|----------------|
| Logstash EC2 t3.large               | 2대 × 730시간 × $0.104                     | $151.84        |
| OpenSearch r6g.large.search         | 3대 × 730시간 × $0.203                     | $444.57        |
| OpenSearch gp3 EBS                  | 3TB(3절 설계값) × $0.1391/GB               | $417.30        |
| S3 Standard (Parquet 90일분)        | 900GB(10GB × 90일) × $0.025/GB             | $22.50         |
| S3 Glacier Instant Retrieval        | 17.1TB(18TB − 최근 90일 0.9TB) × $0.005/GB | $85.50         |
| Athena (스캔 100GB/월 가정)         | 0.1TB × $5.00/TB                           | $0.50          |
| IDC→AWS 연결 (Site-to-Site VPN 1개) | 730시간 × $0.05, 수신 전송 $0/GB           | $36.50         |
| 합계 (5년차 기준)                   |                                            | **~$1,159/월** |

- 단가: AWS Price List API 서울(ap-northeast-2) 온디맨드 파일(OpenSearch 2026-11-06, S3 2026-11-09, Athena 2026-09-11, VPN 2026-11-05, Direct Connect 2026-11-08, 데이터 전송 2026-11-03 게시)과 EC2 가격 페이지 데이터(2026-11-07 게시), 2026-11-10 확인, 세금·할인·약정 제외. 1TB = 1,000GB(10진 근사), 월 730시간으로 계산합니다.
- 제외: EBS 루트 볼륨, T3 Unlimited CPU 크레딧, S3 요청·조회 요금, KMS 요청, AWS에서 외부로 나가는 전송

🟡 IDC→AWS 수신 전송은 VPN과 Direct Connect 모두 $0/GB이므로 비용은 연결 요금으로 정해집니다. Direct Connect는 1Gbps 전용 포트 요금만 서울 $0.30/시간(월 $219)이고, 여기에 회선 사업자 비용이 더해집니다.

## 6. 구축 순서

| 단계 | 작업                                       | 우선순위 |
|------|--------------------------------------------|----------|
| 1    | S3 버킷 생성 (Object Lock, KMS, Lifecycle) | 높음     |
| 2    | Logstash EC2 배포 + TLS 설정               | 높음     |
| 3    | Filebeat 배포 (AWS 서버 먼저)              | 높음     |
| 4    | OpenSearch 도메인 생성                     | 중간     |
| 5    | IDC Filebeat 배포 + VPN/DX 연동            | 중간     |
| 6    | Athena 테이블 정의 (Glue Catalog)          | 낮음     |
| 7    | OpenSearch Dashboards 구성                 | 낮음     |

## 참고 자료

- OpenSearch Documentation: [opensearch.org/docs](https://opensearch.org/docs/) — ★★★☆☆
- Elastic Filebeat: [elastic.co/beats/filebeat](https://www.elastic.co/beats/filebeat) — ★★★☆☆
- AWS Athena: [docs.aws.amazon.com/athena](https://docs.aws.amazon.com/athena/latest/ug/) — ★★★☆☆
- S3 Object Lock: [docs.aws.amazon.com/s3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html) — ★★★☆☆
- OpenSearch Index State Management: [docs.opensearch.org](https://docs.opensearch.org/latest/im-plugin/ism/index/) — ★★★☆☆
- Amazon OpenSearch Service Dashboards: [docs.aws.amazon.com/opensearch-service](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/dashboards.html) — ★★★☆☆
- AWS Price List Bulk API: [docs.aws.amazon.com/awsaccountbilling](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-the-aws-price-list-bulk-api.html) — ★★★☆☆
- Amazon EC2 온디맨드 요금: [aws.amazon.com/ec2/pricing/on-demand](https://aws.amazon.com/ec2/pricing/on-demand/) — ★★★☆☆
- Amazon OpenSearch Service 요금: [aws.amazon.com/opensearch-service/pricing](https://aws.amazon.com/opensearch-service/pricing/) — ★★★☆☆
- Amazon S3 요금: [aws.amazon.com/s3/pricing](https://aws.amazon.com/s3/pricing/) — ★★★☆☆
- Amazon Athena 요금: [aws.amazon.com/athena/pricing](https://aws.amazon.com/athena/pricing/) — ★★★☆☆
- AWS Site-to-Site VPN 요금: [aws.amazon.com/vpn/pricing](https://aws.amazon.com/vpn/pricing/) — ★★★☆☆
- AWS Direct Connect 요금: [aws.amazon.com/directconnect/pricing](https://aws.amazon.com/directconnect/pricing/) — ★★★☆☆

---

**작성일**: 2026-06-18

**마지막 업데이트**: 2026-11-10

© 2026 siasia86. Licensed under CC BY 4.0.

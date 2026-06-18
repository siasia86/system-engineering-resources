# 로그 통합 서버 아키텍처 — 100GB/일 규모

감사/분석 목적, 5년 보관, AWS + IDC 혼합 환경 기준 설계입니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 요구사항](#1-요구사항) / [2. 아키텍처 개요](#2-아키텍처-개요) / [3. 컴포넌트 상세](#3-컴포넌트-상세) |
| [4. 스토리지 설계](#4-스토리지-설계) / [5. 비용 추산](#5-비용-추산) / [6. 구축 순서](#6-구축-순서)       |

## 1. 요구사항

| 항목                        | 월 비용 (USD) |
|-----------------------------|---------------|
| Logstash EC2 t3.large × 2   | ~$150         |
| OpenSearch r6g.large × 3    | ~$450         |
| S3 Standard (90일분 ~900GB) | ~$20          |
| S3 Glacier Instant (18TB)   | ~$180         |
| Athena (쿼리 100GB/월 가정) | ~$5           |
| Data Transfer (IDC→AWS)     | ~$50          |
| 합계 (5년차 기준)           | **~$855/월**  |

## 2. 아키텍처 개요

```
IDC Servers                    AWS
┌─────────────┐               ┌─────────────────────────────────────┐
│ App / DB    │               │                                     │
│ OS / Infra  ├──Filebeat──►  │  Logstash (EC2)                     │
│             │               │      │                              │
└─────────────┘               │      ▼                              │
                              │  OpenSearch  ◄── Kibana (search)    │
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

| 항목      | 내용                                   |
|-----------|----------------------------------------|
| 역할      | 최근 30일 로그 검색/분석               |
| 인스턴스  | r6g.large.search × 3 (3 AZ)            |
| 스토리지  | gp3 EBS 3TB (샤드 × 3 복제본)          |
| 보관 기간 | 30일 후 S3로 ILM(Index Lifecycle) 이동 |

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

| 항목                        | 월 비용 (USD) |
|-----------------------------|---------------|
| Logstash EC2 t3.large × 2   | ~$150         |
| OpenSearch r6g.large × 3    | ~$450         |
| S3 Standard (90일분 ~900GB) | ~$20          |
| S3 Glacier Instant (18TB)   | ~$180         |
| Athena (쿼리 100GB/월 가정) | ~$5           |
| Data Transfer (IDC→AWS)     | ~$50          |
| 합계 (5년차 기준)           | **~$855/월**  |

🟡 Direct Connect 사용 시 데이터 전송 비용이 크게 절감됩니다.

## 6. 구축 순서

| 단계 | 작업                                       | 우선순위 |
|------|--------------------------------------------|----------|
| 1    | S3 버킷 생성 (Object Lock, KMS, Lifecycle) | 높음     |
| 2    | Logstash EC2 배포 + TLS 설정               | 높음     |
| 3    | Filebeat 배포 (AWS 서버 먼저)              | 높음     |
| 4    | OpenSearch 도메인 생성                     | 중간     |
| 5    | IDC Filebeat 배포 + VPN/DX 연동            | 중간     |
| 6    | Athena 테이블 정의 (Glue Catalog)          | 낮음     |
| 7    | Kibana 대시보드 구성                       | 낮음     |

## 참고 자료

- OpenSearch Documentation: [opensearch.org/docs](https://opensearch.org/docs/) — ★★★☆☆
- Elastic Filebeat: [elastic.co/beats/filebeat](https://www.elastic.co/beats/filebeat) — ★★★☆☆
- AWS Athena: [docs.aws.amazon.com/athena](https://docs.aws.amazon.com/athena/latest/ug/) — ★★★☆☆
- S3 Object Lock: [docs.aws.amazon.com/s3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html) — ★★★☆☆

---

**작성일**: 2026-06-18

**마지막 업데이트**: 2026-06-18

© 2026 siasia86. Licensed under CC BY 4.0.

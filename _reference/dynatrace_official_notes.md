---
name: dynatrace-official-notes
description: Dynatrace 소비형 요금(DPS)·단가표·OneAgent·ActiveGate·OTLP 엔드포인트(HTTP 전용, Bearer 플랫폼 토큰) 공식 자료 정리 (SaaS, 실행 시험 없음).
tags:
  - dynatrace
  - observability
  - saas
  - opentelemetry
  - pricing
last_checked: 2026-11-26
sources:
  - https://www.dynatrace.com/pricing/
  - https://www.dynatrace.com/pricing/rate-card/
  - https://docs.dynatrace.com/docs/license
  - https://docs.dynatrace.com/docs/license/capabilities
  - https://docs.dynatrace.com/docs/license/dps-for-hybrid
  - https://docs.dynatrace.com/docs/ingest-from/opentelemetry
  - https://docs.dynatrace.com/docs/ingest-from/opentelemetry/otlp-api
  - https://docs.dynatrace.com/docs/ingest-from/dynatrace-oneagent
  - https://docs.dynatrace.com/docs/ingest-from/dynatrace-activegate
---

# Dynatrace 공식 자료 참조 노트

## 1. 과금 방식 (DPS)

- Dynatrace Platform Subscription: 소비형. 보통 1~3년 계약에 연간 최소 약정. 약정 초과분은 같은 단가로 월 청구("never charges penalty-style overages"). 사용자 수 무제한.
- docs/license "Published May 04, 2026", capabilities "Updated on Sep 14, 2026". 요금 페이지에는 날짜 표시 없음.
- 체험: 15일.

## 2. 단가표 (rate-card, 2026-11-26 확인, USD)

| 항목                      | 단가                                 | 요금 페이지의 월 환산     |
|---------------------------|--------------------------------------|---------------------------|
| Full-Stack Monitoring     | 메모리 GiB-시간당 $0.01              | 8GiB 호스트 월 $58        |
| Infrastructure Monitoring | 호스트-시간당 $0.04                  | 호스트 월 $29             |
| Foundation & Discovery    | 호스트-시간당 $0.01                  | 호스트 월 $7              |
| Kubernetes Platform       | pod-시간당 $0.002                    | -                         |
| Log 수집·처리             | GiB당 $0.20                          | -                         |
| Log 보존(조회 포함)       | GiB-일당 $0.02                       | 보존 10~35일              |
| Log 보존(조회 별도)       | GiB-일당 $0.0007, 조회 GiB당 $0.0035 | 1일~10년                  |
| Metrics 수집              | 10만 데이터포인트당 $0.15            | 1분 단위 15개월 보존 포함 |
| Traces 수집               | GiB당 $0.20                          | 10일 보존 포함            |

- Full-Stack에 트레이스 67GiB, 사용자 지표 데이터포인트 2,100만 포함(요금 페이지).
- 약정량이 클수록 단가 할인(문의).

## 3. OneAgent와 ActiveGate

- OneAgent: 호스트당 하나 설치, 발견한 기술 스택을 자동 계측("automatically activates instrumentation").
- ActiveGate: OneAgent와 Dynatrace 클러스터 사이의 보안 프록시, AWS·Azure·Kubernetes·VMware 등을 API로 감시. SaaS는 Environment ActiveGate만 설치.
- 배포: SaaS와 Managed. DPS for Hybrid로 한 구독을 둘에 나눠 씀.

## 4. OpenTelemetry (otlp-api, "Updated on Oct 05, 2026")

| 경로                            | 기본 URL                                                          |
|---------------------------------|-------------------------------------------------------------------|
| SaaS                            | `https://{environment-id}.live.dynatrace.com/api/v2/otlp`         |
| Environment ActiveGate          | `https://{activegate-domain}:9999/e/{environment-id}/api/v2/otlp` |
| 컨테이너 Environment ActiveGate | `https://{activegate-domain}/e/{environment-id}/api/v2/otlp`      |

- 신호별 경로 `/v1/traces`, `/v1/metrics`, `/v1/logs`가 붙음. 브라우저 주소의 `.apps`는 빼야 함.
- "gRPC is not supported". HTTP와 바이너리 protobuf만(`OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf`). gRPC로 보내는 앱은 Collector에서 HTTP로 바꿈.
- 인증: 플랫폼 토큰을 `Authorization: Bearer` 헤더로. 권한 범위 `openpipeline:traces:ingest`, `openpipeline:metrics:ingest`, `openpipeline:logs:ingest`. 기존 Api-Token 방식 허용 여부는 미확인.
- 요청 크기·속도 제한은 읽은 페이지에 없어 미확인. Managed의 URL 형식도 미확인.

## 5. 시험

SaaS라 계정 없이 실행하지 않았습니다.

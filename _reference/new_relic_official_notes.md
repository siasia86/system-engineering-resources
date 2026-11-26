---
name: new-relic-official-notes
description: New Relic 요금제(사용자 유형·데이터량 과금)·보존·데이터 지역·OTLP 엔드포인트와 제한 공식 자료 정리 (SaaS, 실행 시험 없음).
tags:
  - new-relic
  - observability
  - saas
  - opentelemetry
  - pricing
last_checked: 2026-11-26
sources:
  - https://newrelic.com/pricing
  - https://docs.newrelic.com/docs/accounts/accounts-billing/new-relic-one-pricing-billing/new-relic-one-pricing-billing/
  - https://docs.newrelic.com/docs/opentelemetry/best-practices/opentelemetry-otlp/
  - https://docs.newrelic.com/docs/opentelemetry/get-started/apm-monitoring/opentelemetry-apm-intro/
  - https://docs.newrelic.com/docs/infrastructure/choose-infra-install-method/
  - https://docs.newrelic.com/docs/data-apis/understand-data/new-relic-data-types/
---

# New Relic 공식 자료 참조 노트

## 1. 과금 방식 (pricing, 2026-11-26 확인, 페이지에 날짜 표시 없음)

사용자 수와 데이터 수집량으로 과금합니다. 요금제는 Free, Standard, Pro, Enterprise.

| 항목               | Free        | Standard                                | Pro                               | Enterprise  |
|--------------------|-------------|-----------------------------------------|-----------------------------------|-------------|
| Basic 사용자       | 무료·무제한 | 무료·무제한                             | 무료·무제한                       | 무료·무제한 |
| Core 사용자 (월)   | -           | $49                                     | $49                               | $49         |
| Full platform (월) | 1명 무료    | 첫 사용자 $10, 추가 $99 (최대 5명)      | $349(연간 약정), $418.80(월 종량) | 별도 문의   |
| 데이터 (월)        | 100GB 무료  | 100GB 초과 GB당 $0.40 (Data Plus $0.60) | 같음                              | 별도 문의   |

- 데이터 보존: 기본 데이터 "default of at least 8 days", Data Plus는 최대 90일 추가.
- EU 데이터센터 추가 GB당 월 $0.05. Synthetic 포함량 초과 check당 $0.005.
- 소비형(Compute, CCU) 선택지가 있으나 단가는 페이지에 없음(미확인). Core Compute는 Public Preview.
- Pro·Enterprise에 사용자 라이선스 없는 "Full consumption pricing" 선택지.

## 2. 데이터 지역

- US(기본), EU, JP. US FedRAMP 엔드포인트 별도.

## 3. OpenTelemetry (OTLP 엔드포인트 문서)

| 지역       | 엔드포인트                      |
|------------|---------------------------------|
| US         | `https://otlp.nr-data.net`      |
| EU         | `https://otlp.eu01.nr-data.net` |
| JP         | `https://otlp.jp.nr-data.net`   |
| US FedRAMP | `https://gov-otlp.nr-data.net`  |

- 포트 443·4317·4318, gRPC와 HTTP 모두 지원. 공용 인터넷에서는 HTTP/protobuf 권장.
- 인증: 라이선스 키를 `api-key` 헤더로(`OTEL_EXPORTER_OTLP_HEADERS=api-key=<라이선스 키>`). TLS 1.2 이상.
- 제한: 속성 값 4,095자, 속성 키 255자, 속성 수(리소스 64·scope 8·레코드 128), 배열 64개, 요청 1MB. gzip·zstd 압축. 지표는 delta temporality 권장.
- APM 문서: New Relic 에이전트와 OpenTelemetry 도구를 같은 프로세스에 함께 쓰지 않음.

## 4. 에이전트

- Infrastructure agent(호스트 데이터 수집): Linux 패키지, macOS, Windows MSI, Ansible·Chef·Puppet·Docker, 안내형 설치 CLI. 설치 명령 형식은 플랫폼별 페이지를 읽지 않아 미확인.
- 데이터 종류: 지표·이벤트·로그·트레이스(MELT), NRQL로 조회.

## 5. 시험

SaaS라 계정 없이 실행하지 않았습니다.

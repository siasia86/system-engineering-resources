---
name: prometheus-official-notes
description: Prometheus 공식 문서 기반 핵심 개념, 버전, 데이터 모델 정리.
last_checked: 2026-05-26
sources:
  - https://prometheus.io/docs/introduction/overview/
  - https://prometheus.io/docs/concepts/data_model/
---

# Prometheus 공식 문서 참조 노트

## 1. 버전 현황 (확인일: 2026-05-26)

| 항목       | 버전    |
|------------|---------|
| Prometheus | v3.11.3 |

## 2. 공식 정의

> "Prometheus is an open-source systems monitoring and alerting toolkit.
> Prometheus collects and stores its metrics as time series data."
> — prometheus.io

## 3. 핵심 개념

| 용어         | 설명                                                     |
|--------------|----------------------------------------------------------|
| Time series  | 타임스탬프 + 레이블 + 값으로 구성된 메트릭 데이터        |
| Metric name  | 측정 대상 식별자 (예: `http_requests_total`)             |
| Label        | 메트릭 차원 구분 key=value 쌍 (예: `method="GET"`)       |
| Scrape       | Prometheus가 타겟에서 메트릭을 수집하는 행위 (Pull 방식) |
| Exporter     | 메트릭을 `/metrics` 엔드포인트로 노출하는 에이전트       |
| AlertManager | Prometheus 알림 라우팅·그룹핑·억제 처리                  |
| PromQL       | Prometheus 전용 쿼리 언어                                |

## 4. 메트릭 타입

| 타입      | 설명                                      | 예시                    |
|-----------|-------------------------------------------|-------------------------|
| Counter   | 단조 증가 값 (재시작 시 0으로 리셋)       | `http_requests_total`   |
| Gauge     | 증감 가능한 현재 값                       | `memory_usage_bytes`    |
| Histogram | 버킷별 분포 + 합계 + 카운트               | `http_request_duration` |
| Summary   | 분위수(quantile) 계산 (클라이언트 사이드) | `rpc_duration_seconds`  |

## 5. Pull 방식 특징

- Prometheus가 타겟의 `/metrics` 엔드포인트를 주기적으로 스크랩
- Push 방식 필요 시 Pushgateway 사용 (배치 잡 등)
- 타겟 목록: `prometheus.yml`의 `scrape_configs`에 정의

## 6. 주요 Exporter

| Exporter          | 대상                       |
|-------------------|----------------------------|
| node_exporter     | Linux 호스트 메트릭        |
| blackbox_exporter | HTTP/TCP 엔드포인트 프로브 |
| mysqld_exporter   | MySQL                      |
| cadvisor          | 컨테이너 메트릭            |

## 7. 주의사항

- 장기 보존 필요 시 Thanos / Cortex / VictoriaMetrics 연동 권장
- 카디널리티 폭발 주의 (레이블 값이 무한히 늘어나는 경우)
- `rate()` 함수는 Counter에만 사용 (Gauge에 사용 금지)

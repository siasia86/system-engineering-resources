---
name: grafana-official-notes
description: Grafana 공식 문서 기반 핵심 개념, 버전, 데이터소스 정리.
last_checked: 2026-05-26
sources:
  - https://grafana.com/docs/grafana/latest/introduction/
  - https://grafana.com/docs/grafana/latest/datasources/
---

# Grafana 공식 문서 참조 노트

## 1. 버전 현황 (확인일: 2026-05-26)

| 항목    | 버전     | 비고              |
|---------|----------|-------------------|
| Grafana | v13.0.1  | OSS / Enterprise  |

## 2. 공식 정의

> "Grafana open source software enables you to query, visualize, alert on,
> and explore your metrics, logs, and traces wherever they are stored."
> — grafana.com

## 3. 핵심 개념

| 용어          | 설명                                                      |
|---------------|-----------------------------------------------------------|
| Dashboard     | 여러 Panel을 배치한 시각화 화면                           |
| Panel         | 단일 시각화 단위 (그래프, 테이블, 게이지 등)              |
| Data source   | 데이터를 가져오는 연결 설정 (Prometheus, Loki 등)         |
| Query         | 데이터소스에서 데이터를 가져오는 쿼리 (PromQL, LogQL 등)  |
| Alert rule    | 조건 충족 시 알림 발송 규칙                               |
| Variable      | 대시보드 내 동적 필터 (드롭다운 선택)                     |
| Provisioning  | YAML/JSON으로 대시보드·데이터소스 코드화                  |

## 4. 주요 데이터소스

| 데이터소스    | 용도                          |
|---------------|-------------------------------|
| Prometheus    | 메트릭 (가장 일반적)          |
| Loki          | 로그                          |
| Tempo         | 분산 트레이싱                 |
| CloudWatch    | AWS 메트릭                    |
| Elasticsearch | 로그·검색                     |
| MySQL/PostgreSQL | DB 쿼리 시각화             |

## 5. Provisioning (코드로 관리)

```yaml
# /etc/grafana/provisioning/datasources/prometheus.yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true
```

## 6. 주의사항

- 기본 포트: 3000
- 기본 계정: admin / admin (최초 로그인 후 변경 필수)
- 대시보드 JSON export로 버전 관리 권장
- Grafana Cloud: 관리형 SaaS 버전 (무료 티어 있음)
- `GF_SECURITY_ADMIN_PASSWORD` 환경변수로 초기 비밀번호 설정 가능

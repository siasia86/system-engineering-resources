# Prometheus & Grafana

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. Prometheus 핵심 개념](#3-prometheus-핵심-개념) |
| [4. 설치](#4-설치) / [5. PromQL](#5-promql) / [6. 알림 (Alertmanager)](#6-알림-alertmanager) |
| [7. Grafana 대시보드](#7-grafana-대시보드) / [8. Exporter](#8-exporter) / [9. K8s 모니터링](#9-k8s-모니터링) |
| [10. Tips](#10-tips) |

---

## 1. 개요

Prometheus는 오픈소스 시계열 모니터링 시스템. Grafana는 Prometheus 등 다양한 데이터 소스를 시각화하는 대시보드 도구입니다.

```
┌──────────────────────────────────────────────────────────────┐
│                  Monitoring Stack                            │
│                                                              │
│  Targets ──> Prometheus (수집/저장) ──> Grafana (시각화)     │
│                    │                                         │
│                    └──> Alertmanager ──> Slack/PagerDuty     │
└──────────────────────────────────────────────────────────────┘
```

- **Pull 방식**: Prometheus가 주기적으로 타겟의 `/metrics` 엔드포인트를 스크래핑합니다.
- **시계열 DB**: 타임스탬프 기반 메트릭을 효율적으로 저장합니다.
- **PromQL**: 강력한 쿼리 언어로 메트릭을 집계/분석합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                      Prometheus Stack                           │
│                                                                 │
│  ┌──────────────┐  scrape  ┌──────────────────────────────┐     │
│  │  Prometheus  │ <─────── │  Targets (/metrics)          │     │
│  │  Server      │          │  - Node Exporter             │     │
│  │              │          │  - App (instrumented)        │     │
│  │  TSDB        │          │  - MySQL Exporter            │     │
│  └──────────────┘          └──────────────────────────────┘     │
│         │                                                       │
│         ├──> Alertmanager ──> Slack / PagerDuty / Email         │
│         │                                                       │
│         └──> Grafana ──> Dashboard / Alert                      │
└─────────────────────────────────────────────────────────────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. Prometheus 핵심 개념

### 메트릭 유형

| 유형      | 설명                                      | 예시                          |
|-----------|-------------------------------------------|-------------------------------|
| Counter   | 단조 증가 값 (재시작 시 0으로 리셋)       | HTTP 요청 수, 에러 수         |
| Gauge     | 임의로 증감하는 값                        | CPU 사용률, 메모리 사용량     |
| Histogram | 값의 분포 (버킷별 카운트 + 합계)          | 응답 시간, 요청 크기          |
| Summary   | 분위수(quantile) 계산 (클라이언트 사이드) | 응답 시간 p50/p95/p99         |

### 레이블

```
http_requests_total{method="GET", status="200", path="/api/users"} 1234
```

- 레이블로 메트릭을 다차원으로 분류합니다.
- 레이블 카디널리티(고유 값 수)가 높으면 메모리 사용량이 급증합니다.

### 스크래핑 설정 (prometheus.yml)

```yaml
global:
  scrape_interval: 15s       # 기본 스크래핑 주기
  evaluation_interval: 15s   # 알림 규칙 평가 주기

scrape_configs:
  # Prometheus 자체 모니터링
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter
  - job_name: 'node'
    static_configs:
      - targets:
          - '192.0.2.1:9100'
          - '192.0.2.2:9100'
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance

  # 애플리케이션
  - job_name: 'my-app'
    metrics_path: '/metrics'
    scrape_interval: 30s
    static_configs:
      - targets: ['my-app:8080']
        labels:
          env: production

  # Kubernetes Service Discovery
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설치

### Docker Compose (로컬/소규모)

```yaml
# docker-compose.yml
# version: '3.8'  # Docker Compose v2에서 deprecated (생략 가능)

services:
  prometheus:
    image: prom/prometheus:v3.4.0
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./rules:/etc/prometheus/rules
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'

  alertmanager:
    image: prom/alertmanager:v0.28.1
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml

  grafana:
    image: grafana/grafana:11.6.1
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=SecurePassword123
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning

  node-exporter:
    image: prom/node-exporter:v1.9.1
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'

volumes:
  prometheus_data:
  grafana_data:
```

### Kubernetes (kube-prometheus-stack)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --version 85.2.1 \
  -f values-monitoring.yaml
```

```yaml
# values-monitoring.yaml
grafana:
  adminPassword: SecurePassword123
  persistence:
    enabled: true
    size: 10Gi

prometheus:
  prometheusSpec:
    retention: 30d
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: gp3
          resources:
            requests:
              storage: 50Gi

alertmanager:
  alertmanagerSpec:
    storage:
      volumeClaimTemplate:
        spec:
          storageClassName: gp3
          resources:
            requests:
              storage: 5Gi
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. PromQL

### 기본 문법

```promql
# 메트릭 조회
http_requests_total

# 레이블 필터
http_requests_total{job="my-app", status="200"}
http_requests_total{status=~"5.."}        # 정규식 (5xx 에러)
http_requests_total{status!~"2.."}        # 부정 정규식

# 범위 벡터 (지난 5분)
http_requests_total[5m]

# 오프셋 (1시간 전 값)
http_requests_total offset 1h
```

### 주요 함수

```promql
# 초당 증가율 (Counter용)
rate(http_requests_total[5m])

# 순간 증가율
irate(http_requests_total[5m])

# 증가량
increase(http_requests_total[1h])

# 집계
sum(rate(http_requests_total[5m]))
sum by (status) (rate(http_requests_total[5m]))
avg(node_cpu_seconds_total)
max(node_memory_MemAvailable_bytes)

# 분위수 (Histogram)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# 예측 (4시간 후 디스크 사용량)
predict_linear(node_filesystem_free_bytes[1h], 4 * 3600)
```

### 실용 쿼리 예시

```promql
# CPU 사용률 (%)
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 메모리 사용률 (%)
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100

# 디스크 사용률 (%)
(1 - node_filesystem_free_bytes{fstype!="tmpfs"} / node_filesystem_size_bytes{fstype!="tmpfs"}) * 100

# HTTP 에러율 (%)
sum(rate(http_requests_total{status=~"5.."}[5m])) /
sum(rate(http_requests_total[5m])) * 100

# p95 응답 시간
histogram_quantile(0.95,
  sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
)

# Pod 재시작 횟수
increase(kube_pod_container_status_restarts_total[1h])
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 알림 (Alertmanager)

### 알림 규칙 (rules/alerts.yml)

```yaml
groups:
  - name: infrastructure
    interval: 1m
    rules:
      - alert: HighCPUUsage
        expr: |
          100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is {{ $value | humanize }}% for more than 5 minutes."

      - alert: DiskSpaceLow
        expr: |
          (1 - node_filesystem_free_bytes{fstype!="tmpfs"} / node_filesystem_size_bytes{fstype!="tmpfs"}) * 100 > 85
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk usage is {{ $value | humanize }}% on {{ $labels.mountpoint }}."

      - alert: PodCrashLooping
        expr: increase(kube_pod_container_status_restarts_total[1h]) > 5
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "Pod {{ $labels.namespace }}/{{ $labels.pod }} is crash looping"

      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) /
          sum(rate(http_requests_total[5m])) * 100 > 5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High HTTP error rate"
          description: "Error rate is {{ $value | humanize }}%."
```

### Alertmanager 설정 (alertmanager.yml)

```yaml
global:
  slack_api_url: 'https://hooks.slack.com/services/...'
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'slack-default'

  routes:
    - match:
        severity: critical
      receiver: 'slack-critical'
      repeat_interval: 1h

receivers:
  - name: 'slack-default'
    slack_configs:
      - channel: '#monitoring'
        title: '[{{ .Status | toUpper }}] {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        send_resolved: true

  - name: 'slack-critical'
    slack_configs:
      - channel: '#alerts-critical'
        title: '🔴 [CRITICAL] {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        send_resolved: true

inhibit_rules:
  - source_match:
      severity: critical
    target_match:
      severity: warning
    equal: ['alertname', 'instance']
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Grafana 대시보드

### 데이터 소스 프로비저닝

```yaml
# grafana/provisioning/datasources/prometheus.yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true
    jsonData:
      timeInterval: 15s
```

### 대시보드 프로비저닝

```yaml
# grafana/provisioning/dashboards/default.yaml
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    options:
      path: /etc/grafana/provisioning/dashboards
```

### 유용한 공개 대시보드 (Grafana ID)

| 대시보드                    | ID    | 용도                        |
|-----------------------------|-------|-----------------------------|
| Node Exporter Full          | 1860  | 서버 리소스 모니터링        |
| Kubernetes Cluster          | 7249  | K8s 클러스터 개요           |
| Kubernetes Pod              | 6781  | Pod 상세 모니터링           |
| MySQL Overview              | 7362  | MySQL 모니터링              |
| Redis Dashboard             | 11835 | Redis 모니터링              |
| NGINX Ingress Controller    | 9614  | Ingress 트래픽 모니터링     |

```bash
# Grafana CLI로 대시보드 가져오기
grafana-cli dashboards import 1860
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. Exporter

### 주요 Exporter

| Exporter          | 포트  | 용도                                           |
|-------------------|-------|------------------------------------------------|
| node_exporter     | 9100  | 서버 OS 메트릭 (CPU, 메모리, 디스크, 네트워크) |
| mysqld_exporter   | 9104  | MySQL/MariaDB 메트릭                           |
| redis_exporter    | 9121  | Redis 메트릭                                   |
| nginx-exporter    | 9113  | NGINX 메트릭                                   |
| blackbox_exporter | 9115  | HTTP/TCP/ICMP 외부 프로브                      |
| process-exporter  | 9256  | 프로세스별 메트릭                              |

### 애플리케이션 계측 (Python 예시)

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# 메트릭 정의
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

# 메트릭 서버 시작 (포트 8000)
start_http_server(8000)

# 사용 예시
REQUEST_COUNT.labels(method='GET', endpoint='/api/users', status='200').inc()

with REQUEST_LATENCY.labels(method='GET', endpoint='/api/users').time():
    # 처리 로직
    time.sleep(0.1)
```

### Blackbox Exporter (외부 프로브)

```yaml
# blackbox.yml
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: [200]
      follow_redirects: true
      tls_config:
        insecure_skip_verify: false

  tcp_connect:
    prober: tcp
    timeout: 5s
```

```yaml
# prometheus.yml - blackbox 스크래핑
- job_name: 'blackbox-http'
  metrics_path: /probe
  params:
    module: [http_2xx]
  static_configs:
    - targets:
        - https://app.example.com/health
        - https://api.example.com/health
  relabel_configs:
    - source_labels: [__address__]
      target_label: __param_target
    - source_labels: [__param_target]
      target_label: instance
    - target_label: __address__
      replacement: blackbox-exporter:9115
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. K8s 모니터링

### Pod 어노테이션으로 자동 스크래핑

```yaml
# Deployment에 어노테이션 추가
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
```

### 주요 K8s 메트릭

```promql
# 노드별 CPU 사용률
100 - (avg by (node) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 네임스페이스별 메모리 사용량
sum by (namespace) (container_memory_working_set_bytes{container!=""})

# Pod 재시작 횟수 (1시간)
topk(10, increase(kube_pod_container_status_restarts_total[1h]))

# Deployment 가용 Pod 비율
kube_deployment_status_replicas_available / kube_deployment_spec_replicas

# PVC 사용률
(kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes) * 100
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. Tips

### 데이터 보존 & 용량 계획

```bash
# 현재 TSDB 크기 확인
curl -s http://localhost:9090/api/v1/status/tsdb | jq '.data.headStats'

# 보존 기간 설정 (prometheus 실행 옵션)
--storage.tsdb.retention.time=30d
--storage.tsdb.retention.size=50GB   # 크기 기반 보존
```

### 주의사항

⚠️ 레이블 카디널리티 관리: 사용자 ID, 요청 ID 등 고유 값이 많은 레이블은 메모리 폭증을 유발합니다. 레이블 값은 유한한 집합(status code, method, endpoint 등)으로 제한합니다.

⚠️ Grafana 기본 admin 비밀번호를 반드시 변경합니다. 외부 접근 시 리버스 프록시(NGINX) + TLS를 적용합니다.

⚠️ Prometheus는 고가용성(HA) 구성이 복잡합니다. 대규모 환경에서는 Thanos 또는 Cortex를 검토합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Prometheus Documentation: [prometheus.io/docs](https://prometheus.io/docs/introduction/overview/) — ★★★☆☆
- Grafana Documentation: [grafana.com/docs](https://grafana.com/docs/grafana/latest/) — ★★★☆☆
- PromQL Cheat Sheet: [promlabs.com/promql-cheat-sheet](https://promlabs.com/promql-cheat-sheet/) — ★★☆☆☆
- Grafana Dashboard Gallery: [grafana.com/grafana/dashboards](https://grafana.com/grafana/dashboards/) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-10

**마지막 업데이트**: 2026-05-22

© 2026 siasia86. Licensed under CC BY 4.0.

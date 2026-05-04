# Prometheus + Grafana 설치 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. Prometheus 설치](#2-prometheus-설치) / [3. Node Exporter 설치](#3-node-exporter-설치) |
| [4. Grafana 설치](#4-grafana-설치) / [5. 대시보드 구성](#5-대시보드-구성) / [6. 알림 설정](#6-알림-설정) |
| [7. Docker Compose로 구성](#7-docker-compose로-구성) / [8. 실무 팁](#8-실무-팁) / [9. 트러블슈팅](#9-트러블슈팅) |

---

## 1. 개요

### 모니터링 스택 구조

```
┌─────────────┐   scrape   ┌──────────────┐   query   ┌─────────────┐
│ Node        │ <--------- │  Prometheus  │ <-------- │   Grafana   │
│ Exporter    │            │  (TSDB)      │           │  (시각화)   │
└─────────────┘            └──────┬───────┘           └─────────────┘
                                  │ alert
                           ┌──────▼───────┐
                           │ Alertmanager │
                           └──────────────┘
```

### 컴포넌트 역할

| 컴포넌트          | 포트  | 역할                                  |
|-------------------|-------|---------------------------------------|
| Prometheus        | 9090  | 메트릭 수집 및 저장 (TSDB)            |
| Node Exporter     | 9100  | 호스트 시스템 메트릭 노출             |
| Grafana           | 3000  | 메트릭 시각화 및 대시보드             |
| Alertmanager      | 9093  | 알림 라우팅 (Slack, Email 등)         |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Prometheus 설치

### 2-1. Ubuntu (APT)

```bash
sudo apt update
sudo apt install prometheus -y
sudo systemctl enable --now prometheus
```

### 2-2. 바이너리 설치 (최신 버전)

```bash
# 최신 버전 확인: https://github.com/prometheus/prometheus/releases
PROM_VERSION="2.53.0"
wget https://github.com/prometheus/prometheus/releases/download/v${PROM_VERSION}/prometheus-${PROM_VERSION}.linux-amd64.tar.gz
tar xzf prometheus-${PROM_VERSION}.linux-amd64.tar.gz
sudo mv prometheus-${PROM_VERSION}.linux-amd64/prometheus /usr/local/bin/
sudo mv prometheus-${PROM_VERSION}.linux-amd64/promtool   /usr/local/bin/

# 설정 디렉토리
sudo mkdir -p /etc/prometheus /var/lib/prometheus
sudo mv prometheus-${PROM_VERSION}.linux-amd64/prometheus.yml /etc/prometheus/

# systemd 서비스
sudo tee /etc/systemd/system/prometheus.service << 'EOF'
[Unit]
Description=Prometheus
After=network.target

[Service]
User=prometheus
ExecStart=/usr/local/bin/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/var/lib/prometheus \
    --storage.tsdb.retention.time=30d \
    --web.listen-address=0.0.0.0:9090
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo useradd -rs /bin/false prometheus
sudo chown -R prometheus:prometheus /etc/prometheus /var/lib/prometheus
sudo systemctl daemon-reload
sudo systemctl enable --now prometheus
```

### 2-3. prometheus.yml 설정

```yaml
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

rule_files:
  - /etc/prometheus/rules/*.yml

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node'
    static_configs:
      - targets:
          - '10.0.1.11:9100'
          - '10.0.1.12:9100'
          - '10.0.1.13:9100'
```

```bash
# 설정 검증
promtool check config /etc/prometheus/prometheus.yml

# 설정 반영 (재시작 없이)
sudo kill -HUP $(pidof prometheus)
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. Node Exporter 설치

모니터링 대상 서버마다 설치합니다.

```bash
NODE_EXP_VERSION="1.8.2"
wget https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXP_VERSION}/node_exporter-${NODE_EXP_VERSION}.linux-amd64.tar.gz
tar xzf node_exporter-${NODE_EXP_VERSION}.linux-amd64.tar.gz
sudo mv node_exporter-${NODE_EXP_VERSION}.linux-amd64/node_exporter /usr/local/bin/

sudo useradd -rs /bin/false node_exporter

sudo tee /etc/systemd/system/node_exporter.service << 'EOF'
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
ExecStart=/usr/local/bin/node_exporter
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter

# 메트릭 노출 확인
curl -s http://localhost:9100/metrics | head -5
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. Grafana 설치

### 4-1. Ubuntu (공식 저장소)

```bash
sudo apt install -y apt-transport-https software-properties-common
wget -q -O - https://apt.grafana.com/gpg.key \
    | sudo gpg --dearmor -o /usr/share/keyrings/grafana.gpg

echo "deb [signed-by=/usr/share/keyrings/grafana.gpg] \
    https://apt.grafana.com stable main" \
    | sudo tee /etc/apt/sources.list.d/grafana.list

sudo apt update
sudo apt install grafana -y
sudo systemctl enable --now grafana-server
```

### 4-2. Rocky Linux

```bash
sudo tee /etc/yum.repos.d/grafana.repo << 'EOF'
[grafana]
name=grafana
baseurl=https://rpm.grafana.com
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://rpm.grafana.com/gpg.key
EOF

sudo dnf install grafana -y
sudo systemctl enable --now grafana-server
```

### 4-3. 초기 접속

```
URL: http://SERVER_IP:3000
초기 계정: admin / admin
→ 최초 로그인 시 패스워드 변경 필수
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 대시보드 구성

### Prometheus 데이터 소스 추가

```
Grafana → Connections → Data Sources → Add data source
→ Prometheus 선택
→ URL: http://localhost:9090
→ Save & Test
```

### 주요 PromQL 쿼리

```promql
# CPU 사용률 (%)
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 메모리 사용률 (%)
(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100

# 디스크 사용률 (%)
(1 - node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100

# 네트워크 수신 (bytes/s)
rate(node_network_receive_bytes_total{device!="lo"}[5m])
```

### 대시보드 임포트

```
Grafana → Dashboards → Import
→ Dashboard ID 입력:
   1860  (Node Exporter Full)
   3662  (Prometheus 2.0 Overview)
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 알림 설정

### alerting rules

```yaml
# /etc/prometheus/rules/node.yml
groups:
  - name: node_alerts
    rules:
      - alert: HighCPU
        expr: 100 - (avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU on {{ $labels.instance }}: {{ $value | printf \"%.1f\" }}%"

      - alert: LowDiskSpace
        expr: (1 - node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 > 85
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Low disk on {{ $labels.instance }}: {{ $value | printf \"%.1f\" }}% used"
```

### Alertmanager (Slack 연동)

```yaml
# /etc/alertmanager/alertmanager.yml
global:
  slack_api_url: 'https://hooks.slack.com/services/SecureToken123'

route:
  receiver: 'slack-notifications'

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Docker Compose로 구성

```yaml
# compose.yaml
services:
  prometheus:
    image: prom/prometheus:v2.53.0
    ports:
      - "127.0.0.1:9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./rules:/etc/prometheus/rules:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:11.0.0
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=SecurePassword123
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped

  node_exporter:
    image: prom/node-exporter:v1.8.2
    ports:
      - "127.0.0.1:9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

```bash
docker compose up -d
# Grafana: http://SERVER_IP:3000 (admin / SecurePassword123)
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 실무 팁

### Tip 1: 데이터 보존 기간 설정

```bash
# 30일 보존 (기본 15일)
--storage.tsdb.retention.time=30d

# 용량 기준 보존
--storage.tsdb.retention.size=50GB
```

### Tip 2: 스크랩 타겟 동적 관리 (file_sd)

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'node'
    file_sd_configs:
      - files:
          - /etc/prometheus/targets/*.json
        refresh_interval: 30s
```

```json
// /etc/prometheus/targets/servers.json
[
  {
    "targets": ["10.0.1.11:9100", "10.0.1.12:9100"],
    "labels": {"env": "prod", "role": "web"}
  }
]
```

### Tip 3: Grafana 대시보드 백업

```bash
# 대시보드 JSON 내보내기
curl -s -u admin:SecurePassword123 \
    http://localhost:3000/api/dashboards/home \
    | jq '.dashboard' > dashboard_backup.json
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                              | 원인                          | 해결 방법                                              |
|-----------------------------------|-------------------------------|--------------------------------------------------------|
| 타겟 `DOWN` 상태                  | Exporter 미실행 또는 방화벽   | `curl http://TARGET:9100/metrics` 확인                 |
| Grafana 데이터 없음               | 데이터 소스 연결 실패         | Data Source → Test 확인                                |
| 알림 미발송                       | Alertmanager 설정 오류        | `amtool check-config alertmanager.yml`                 |
| 디스크 사용량 급증                | 보존 기간 과다                | `retention.time` 또는 `retention.size` 조정            |
| PromQL 쿼리 느림                  | 범위 너무 넓음                | 쿼리 범위 축소, recording rules 사용                   |

```bash
# Prometheus 타겟 상태 확인
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job, health, lastError}'

# 설정 검증
promtool check config /etc/prometheus/prometheus.yml
promtool check rules /etc/prometheus/rules/node.yml
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Prometheus Documentation: [prometheus.io/docs](https://prometheus.io/docs/) — ★★★☆☆
- Grafana Documentation: [grafana.com/docs](https://grafana.com/docs/) — ★★★☆☆
- Node Exporter: [github.com/prometheus/node_exporter](https://github.com/prometheus/node_exporter) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-04

**마지막 업데이트**: 2026-05-04

© 2026 siasia86. Licensed under CC BY 4.0.

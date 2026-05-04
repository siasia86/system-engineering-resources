# Elasticsearch 설치 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. Ubuntu 설치](#2-ubuntu-설치) / [3. RHEL 계열 설치](#3-rhel-계열-설치) |
| [4. 초기 보안 설정](#4-초기-보안-설정) / [5. 기본 설정 (elasticsearch.yml)](#5-기본-설정-elasticsearchyml) / [6. 기본 사용법](#6-기본-사용법) |
| [7. ELK 스택 (Docker Compose)](#7-elk-스택-docker-compose) / [8. 실무 팁](#8-실무-팁) / [9. 트러블슈팅](#9-트러블슈팅) |

---

## 1. 개요

### ELK 스택 구조

```
애플리케이션 로그
      │
      v
┌─────────────┐   전송   ┌───────────────┐   저장   ┌──────────────┐
│  Filebeat   │ -------> │  Logstash     │ -------> │Elasticsearch │
│  (수집)     │          │  (파싱/변환)  │          │  (검색/저장) │
└─────────────┘          └───────────────┘          └──────┬───────┘
                                                           │ 조회
                                                    ┌──────▼───────┐
                                                    │   Kibana     │
                                                    │  (시각화)    │
                                                    └──────────────┘
```

### 시스템 요구사항

| 항목   | 최소          | 권장 (프로덕션)       |
|--------|---------------|-----------------------|
| CPU    | 2 core        | 8 core 이상           |
| RAM    | 4 GB          | 16 GB 이상            |
| 디스크 | 20 GB         | SSD 500 GB 이상       |
| JVM    | JDK 17+       | 번들 JDK 사용 권장    |
| 포트   | 9200, 9300    | 9200/tcp, 9300/tcp    |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Ubuntu 설치

### 2-1. 시스템 요구사항 설정

```bash
# vm.max_map_count 설정 (Elasticsearch 필수)
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### 2-2. Elastic 공식 저장소 추가

```bash
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch \
    | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] \
    https://artifacts.elastic.co/packages/8.x/apt stable main" \
    | sudo tee /etc/apt/sources.list.d/elastic-8.x.list

sudo apt update
```

### 2-3. Elasticsearch 설치

```bash
sudo apt install elasticsearch -y
sudo systemctl enable --now elasticsearch
```

⚠️ 최초 설치 시 `elastic` 슈퍼유저 패스워드가 터미널에 출력됩니다. 반드시 저장합니다.

### 2-4. 설치 확인

```bash
sudo systemctl status elasticsearch --no-pager | head -5

# HTTPS + 인증 (8.x 기본)
curl -s --cacert /etc/elasticsearch/certs/http_ca.crt \
    -u elastic:SecurePassword123 \
    https://localhost:9200
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. RHEL 계열 설치

### 3-1. 시스템 요구사항 설정

```bash
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### 3-2. Elastic 공식 저장소 추가

```bash
sudo rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch

sudo tee /etc/yum.repos.d/elasticsearch.repo << 'EOF'
[elasticsearch]
name=Elasticsearch repository for 8.x packages
baseurl=https://artifacts.elastic.co/packages/8.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=1
autorefresh=1
type=rpm-md
EOF

sudo dnf install elasticsearch -y
sudo systemctl enable --now elasticsearch
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 초기 보안 설정

### elastic 패스워드 재설정

```bash
sudo /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
```

### enrollment token 생성 (Kibana 연동용)

```bash
sudo /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana
```

### 보안 설정 확인

```bash
# 8.x는 기본적으로 TLS + 인증 활성화
grep -E "xpack.security|xpack.http.ssl" /etc/elasticsearch/elasticsearch.yml
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 기본 설정 (elasticsearch.yml)

```bash
sudo vi /etc/elasticsearch/elasticsearch.yml
```

```yaml
# 클러스터
cluster.name: my-cluster
node.name: node-1

# 네트워크
network.host: 0.0.0.0        # 원격 접속 허용 시
http.port: 9200

# 경로
path.data: /var/lib/elasticsearch
path.logs: /var/log/elasticsearch

# 메모리
bootstrap.memory_lock: true   # swap 방지

# 클러스터 초기 마스터 노드 (단일 노드)
discovery.type: single-node   # 단일 노드 클러스터

# 보안 (8.x 기본값)
xpack.security.enabled: true
```

### JVM 힙 메모리 설정

```bash
sudo vi /etc/elasticsearch/jvm.options.d/heap.options
```

```
# RAM의 50% 권장, 최대 32GB
-Xms4g
-Xmx4g
```

```bash
sudo systemctl restart elasticsearch
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 기본 사용법

```bash
# 환경 변수 설정 (편의)
ES_URL="https://localhost:9200"
ES_CERT="/etc/elasticsearch/certs/http_ca.crt"
ES_AUTH="elastic:SecurePassword123"
```

### 인덱스 관리

```bash
# 인덱스 목록
curl -s --cacert $ES_CERT -u $ES_AUTH "$ES_URL/_cat/indices?v"

# 인덱스 생성
curl -s --cacert $ES_CERT -u $ES_AUTH -X PUT "$ES_URL/myindex" \
    -H 'Content-Type: application/json' -d '{
  "settings": { "number_of_shards": 1, "number_of_replicas": 0 }
}'

# 인덱스 삭제
curl -s --cacert $ES_CERT -u $ES_AUTH -X DELETE "$ES_URL/myindex"
```

### 문서 CRUD

```bash
# 문서 색인
curl -s --cacert $ES_CERT -u $ES_AUTH -X POST "$ES_URL/myindex/_doc" \
    -H 'Content-Type: application/json' -d '{
  "title": "test document",
  "content": "hello elasticsearch",
  "timestamp": "2026-05-04T20:00:00"
}'

# 검색
curl -s --cacert $ES_CERT -u $ES_AUTH "$ES_URL/myindex/_search?q=hello&pretty"

# 쿼리 DSL 검색
curl -s --cacert $ES_CERT -u $ES_AUTH -X GET "$ES_URL/myindex/_search" \
    -H 'Content-Type: application/json' -d '{
  "query": {
    "match": { "content": "hello" }
  }
}'
```

### 클러스터 상태

```bash
curl -s --cacert $ES_CERT -u $ES_AUTH "$ES_URL/_cluster/health?pretty"
curl -s --cacert $ES_CERT -u $ES_AUTH "$ES_URL/_cat/nodes?v"
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. ELK 스택 (Docker Compose)

```yaml
# compose.yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.14.0
    environment:
      - discovery.type=single-node
      - ELASTIC_PASSWORD=SecurePassword123
      - xpack.security.enabled=true
      - ES_JAVA_OPTS=-Xms1g -Xmx1g
    volumes:
      - es_data:/usr/share/elasticsearch/data
    ports:
      - "127.0.0.1:9200:9200"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    restart: unless-stopped

  kibana:
    image: docker.elastic.co/kibana/kibana:8.14.0
    environment:
      - ELASTICSEARCH_HOSTS=https://elasticsearch:9200
      - ELASTICSEARCH_USERNAME=kibana_system
      - ELASTICSEARCH_PASSWORD=SecurePassword123
      - ELASTICSEARCH_SSL_VERIFICATIONMODE=none
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    restart: unless-stopped

volumes:
  es_data:
```

```bash
docker compose up -d
# Kibana: http://SERVER_IP:5601 (elastic / SecurePassword123)
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 실무 팁

### Tip 1: 인덱스 수명 주기 관리 (ILM)

로그 인덱스는 ILM으로 자동 롤오버/삭제 설정을 권장합니다.

```bash
# ILM 정책 생성 (30일 후 삭제)
curl -s --cacert $ES_CERT -u $ES_AUTH -X PUT "$ES_URL/_ilm/policy/logs-policy" \
    -H 'Content-Type: application/json' -d '{
  "policy": {
    "phases": {
      "hot":    { "actions": { "rollover": { "max_size": "50gb", "max_age": "7d" } } },
      "delete": { "min_age": "30d", "actions": { "delete": {} } }
    }
  }
}'
```

### Tip 2: 샤드 크기 가이드

| 인덱스 크기   | 권장 샤드 수  |
|---------------|---------------|
| < 10 GB       | 1             |
| 10 ~ 50 GB    | 2 ~ 5         |
| > 50 GB       | 크기 / 30GB   |

⚠️ 샤드가 너무 많으면 오버헤드 증가. 샤드당 20~50 GB 권장.

### Tip 3: 슬로우 로그 활성화

```bash
curl -s --cacert $ES_CERT -u $ES_AUTH -X PUT "$ES_URL/myindex/_settings" \
    -H 'Content-Type: application/json' -d '{
  "index.search.slowlog.threshold.query.warn": "5s",
  "index.indexing.slowlog.threshold.index.warn": "2s"
}'
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                  | 원인                          | 해결 방법                                              |
|---------------------------------------|-------------------------------|--------------------------------------------------------|
| `max virtual memory areas too low`    | vm.max_map_count 미설정       | `sysctl -w vm.max_map_count=262144`                    |
| 클러스터 상태 `red`                   | 샤드 미할당                   | `GET /_cluster/allocation/explain` 확인                |
| `circuit_breaking_exception`          | JVM 힙 부족                   | `Xmx` 증가 또는 쿼리 최적화                           |
| 인증 실패 (8.x)                       | 패스워드 오류 또는 TLS 설정   | `elasticsearch-reset-password -u elastic`              |
| 노드 연결 불가                        | 방화벽 또는 network.host 설정 | 9200/9300 포트 확인                                    |

```bash
# 로그 확인
sudo journalctl -u elasticsearch -f
sudo tail -100 /var/log/elasticsearch/my-cluster.log

# 클러스터 상태
curl -s --cacert $ES_CERT -u $ES_AUTH "$ES_URL/_cluster/health?pretty"
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Elastic Documentation: [elastic.co/guide/en/elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/) — ★★★☆☆
- [nosql_elasticsearch.md](../10_nosql/nosql_elasticsearch.md)

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

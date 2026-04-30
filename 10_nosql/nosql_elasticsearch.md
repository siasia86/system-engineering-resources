# Elasticsearch

## 목차

| 단계 | 섹션                                                                                                                                                              |
|------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. Elasticsearch 개념](#1-elasticsearch-개념) / [2. 인덱스와 매핑](#2-인덱스와-매핑)                                                                              |
| CRUD | [3. 문서 CRUD](#3-문서-crud) / [4. 검색 쿼리](#4-검색-쿼리)                                                                                                        |
| 고급 | [5. Aggregation](#5-aggregation) / [6. 클러스터 구조](#6-클러스터-구조) / [7. 실무 팁](#7-실무-팁) |

---

## 1. Elasticsearch 개념

Elasticsearch는 **분산 검색 및 분석 엔진**이다.
Apache Lucene 기반으로 전문 검색(Full-Text Search)과 실시간 분석에 특화되어 있다.

### 핵심 개념

| 개념 | 설명 | RDBMS 대응 |
|------|------|------------|
| **Index** | 문서의 논리적 집합 | Table |
| **Document** | JSON 형태의 단일 데이터 | Row |
| **Field** | 문서의 속성 | Column |
| **Shard** | 인덱스의 물리적 분할 단위 | Partition |
| **Replica** | 샤드의 복제본 | Replica |
| **Node** | 클러스터의 단일 서버 | - |
| **Cluster** | 노드의 집합 | - |

### 특징

| 항목 | 설명 |
|------|------|
| 검색 | 역인덱스(Inverted Index) 기반 전문 검색 |
| 확장성 | 수평 확장 (샤딩) |
| 실시간 | Near Real-Time (NRT) 검색 |
| REST API | HTTP/JSON 인터페이스 |
| ELK Stack | Elasticsearch + Logstash + Kibana |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 인덱스와 매핑

### 인덱스 생성

```bash
PUT /products
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "product_id":   { "type": "integer" },
      "name":         { "type": "text", "analyzer": "standard" },
      "description":  { "type": "text" },
      "price":        { "type": "float" },
      "category":     { "type": "keyword" },
      "tags":         { "type": "keyword" },
      "created_at":   { "type": "date" },
      "in_stock":     { "type": "boolean" }
    }
  }
}
```

### 주요 필드 타입

| 타입 | 설명 | 사용 사례 |
|------|------|-----------|
| `text` | 분석된 전문 검색 | 제목, 본문 |
| `keyword` | 정확한 값 매칭, 집계 | 카테고리, 상태 |
| `integer` / `float` | 숫자 | 가격, 수량 |
| `date` | 날짜/시간 | 생성일 |
| `boolean` | 참/거짓 | 활성 여부 |
| `nested` | 중첩 객체 배열 | 주문 상품 목록 |
| `geo_point` | 위도/경도 | 위치 검색 |

### text vs keyword

```bash
# text: 분석기로 토큰화 → 부분 검색 가능
"name": { "type": "text" }
# "MacBook Pro" → ["macbook", "pro"] 토큰화

# keyword: 원본 그대로 → 정확한 매칭, 집계, 정렬
"category": { "type": "keyword" }
# "Electronics" → "Electronics" 그대로

# 두 가지 모두 필요한 경우
"name": {
  "type": "text",
  "fields": { "keyword": { "type": "keyword" } }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 문서 CRUD

```bash
# 문서 생성 (ID 지정)
PUT /products/_doc/1
{
  "product_id": 1,
  "name": "MacBook Pro",
  "price": 2500000,
  "category": "Electronics"
}

# 문서 생성 (ID 자동 생성)
POST /products/_doc
{ "name": "Mouse", "price": 50000 }

# 문서 조회
GET /products/_doc/1

# 문서 수정 (부분 업데이트)
POST /products/_update/1
{ "doc": { "price": 2400000 } }

# 문서 삭제
DELETE /products/_doc/1

# 인덱스 삭제
DELETE /products
```

### Bulk API

```bash
POST /_bulk
{ "index": { "_index": "products", "_id": "1" } }
{ "name": "Laptop", "price": 1500000 }
{ "index": { "_index": "products", "_id": "2" } }
{ "name": "Mouse", "price": 50000 }
{ "delete": { "_index": "products", "_id": "3" } }
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 검색 쿼리

### 기본 검색

```bash
# 전체 조회
GET /products/_search
{ "query": { "match_all": {} } }

# 전문 검색
GET /products/_search
{
  "query": {
    "match": { "name": "macbook pro" }
  }
}

# 정확한 값 매칭
GET /products/_search
{
  "query": {
    "term": { "category": "Electronics" }
  }
}

# 범위 검색
GET /products/_search
{
  "query": {
    "range": { "price": { "gte": 100000, "lte": 500000 } }
  }
}
```

### 복합 쿼리 (Bool Query)

```bash
GET /products/_search
{
  "query": {
    "bool": {
      "must":     [{ "match": { "name": "laptop" } }],
      "filter":   [{ "term": { "category": "Electronics" } },
                   { "range": { "price": { "lte": 2000000 } } }],
      "must_not": [{ "term": { "in_stock": false } }],
      "should":   [{ "term": { "tags": "sale" } }]
    }
  },
  "sort": [{ "price": "asc" }],
  "from": 0,
  "size": 10
}
```

| 절 | 설명 | 스코어 영향 |
|----|------|-------------|
| `must` | 반드시 일치 (AND) | ✅ |
| `filter` | 반드시 일치, 캐시됨 | ❌ (성능 우선) |
| `must_not` | 반드시 불일치 | ❌ |
| `should` | 일치하면 점수 향상 (OR) | ✅ |

### 전문 검색 쿼리

```bash
# 여러 필드 검색
GET /products/_search
{
  "query": {
    "multi_match": {
      "query": "wireless keyboard",
      "fields": ["name^2", "description"],  # name 가중치 2배
      "type": "best_fields"
    }
  }
}

# 구문 검색 (순서 일치)
GET /products/_search
{
  "query": {
    "match_phrase": { "name": "macbook pro" }
  }
}

# 자동완성 (prefix)
GET /products/_search
{
  "query": {
    "prefix": { "name.keyword": "Mac" }
  }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. Aggregation

```bash
GET /orders/_search
{
  "size": 0,
  "aggs": {
    "by_status": {
      "terms": { "field": "status" }
    },
    "total_revenue": {
      "sum": { "field": "amount" }
    },
    "avg_order": {
      "avg": { "field": "amount" }
    },
    "monthly_sales": {
      "date_histogram": {
        "field": "created_at",
        "calendar_interval": "month"
      },
      "aggs": {
        "revenue": { "sum": { "field": "amount" } }
      }
    },
    "price_ranges": {
      "range": {
        "field": "amount",
        "ranges": [
          { "to": 10000 },
          { "from": 10000, "to": 100000 },
          { "from": 100000 }
        ]
      }
    }
  }
}
```

### 주요 Aggregation 종류

| 종류 | 설명 |
|------|------|
| `terms` | 값별 버킷 (GROUP BY) |
| `date_histogram` | 날짜 단위 버킷 |
| `range` | 범위별 버킷 |
| `sum` / `avg` / `min` / `max` | 수치 집계 |
| `cardinality` | 고유값 수 (근사) |
| `top_hits` | 버킷 내 상위 문서 |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 클러스터 구조

```
┌─────────────────────────────────────────┐
│              ES Cluster                 │
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Master   │  │ Data     │  │ Data   │ │
│  │ Node     │  │ Node 1   │  │ Node 2 │ │
│  │          │  │ Shard 0  │  │Shard 1 │ │
│  │          │  │ Shard 2  │  │Shard 0'│ │
│  └──────────┘  └──────────┘  └────────┘ │
└─────────────────────────────────────────┘
```

### 클러스터 상태 확인

```bash
# 클러스터 상태 (green/yellow/red)
GET /_cluster/health

# 노드 목록
GET /_cat/nodes?v

# 인덱스 목록
GET /_cat/indices?v

# 샤드 상태
GET /_cat/shards?v

# 슬로우 쿼리 로그 설정
PUT /products/_settings
{
  "index.search.slowlog.threshold.query.warn": "10s",
  "index.search.slowlog.threshold.query.info": "5s"
}
```

### 상태 색상

| 색상 | 의미 |
|------|------|
| 🟢 green | 모든 샤드 정상 |
| 🟡 yellow | Primary 정상, Replica 미할당 |
| 🔴 red | Primary 샤드 미할당 (데이터 손실 위험) |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실무 팁

### Tip 1: filter vs query

```bash
# query: 스코어 계산 (전문 검색)
# filter: 스코어 없음, 캐시됨 (조건 필터링)

# 좋은 예: 검색은 must, 필터링은 filter
{
  "query": {
    "bool": {
      "must":   [{ "match": { "name": "laptop" } }],
      "filter": [{ "term": { "category": "Electronics" } }]
    }
  }
}
```

### Tip 2: 인덱스 템플릿 (로그 인덱스)

```bash
PUT /_index_template/logs_template
{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": { "number_of_shards": 1 },
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "level":      { "type": "keyword" },
        "message":    { "type": "text" }
      }
    }
  }
}
```

### Tip 3: ILM (Index Lifecycle Management)

```bash
# 로그 인덱스 자동 관리
PUT /_ilm/policy/logs_policy
{
  "policy": {
    "phases": {
      "hot":    { "actions": { "rollover": { "max_size": "50gb" } } },
      "warm":   { "min_age": "7d",  "actions": { "shrink": { "number_of_shards": 1 } } },
      "delete": { "min_age": "30d", "actions": { "delete": {} } }
    }
  }
}
```

### Tip 4: 한국어 분석기

```bash
PUT /korean_index
{
  "settings": {
    "analysis": {
      "analyzer": {
        "korean": {
          "type": "custom",
          "tokenizer": "nori_tokenizer"  # nori 플러그인 필요
        }
      }
    }
  }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Elasticsearch Documentation: [elastic.co/docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html) — ★★☆☆☆
- Elasticsearch Query DSL: [Query DSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html) — ★★☆☆☆
- Elastic Stack (ELK): [elastic.co/elastic-stack](https://www.elastic.co/elastic-stack) — ★★☆☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-04-30

**마지막 업데이트**: 2026-04-30

© 2026 siasia86. Licensed under CC BY 4.0.

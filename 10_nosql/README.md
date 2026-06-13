# NoSQL 데이터베이스

NoSQL 데이터베이스 종류별 개념, 사용법, 실전 패턴 문서 모음.

## 목차

| 섹션                                                                                                                  |
|-----------------------------------------------------------------------------------------------------------------------|
| [문서 목록](#문서-목록) / [NoSQL 유형 비교](#nosql-유형-비교) / [RDBMS vs NoSQL 선택 기준](#rdbms-vs-nosql-선택-기준) |

---

## 문서 목록

| 문서                                    | 설명                                               |
|-----------------------------------------|----------------------------------------------------|
| [Redis](nosql_redis.md)                 | 인메모리 자료구조, 캐시, 분산 락, 실시간 랭킹      |
| [MongoDB](nosql_mongodb.md)             | 문서형 DB, CRUD, Aggregation Pipeline, 스키마 설계 |
| [Elasticsearch](nosql_elasticsearch.md) | 분산 검색 엔진, Bool Query, Aggregation, ILM       |

---

## NoSQL 유형 비교

| 유형         | 대표 DB               | 특징                     | 사용 사례        |
|--------------|-----------------------|--------------------------|------------------|
| **문서형**   | MongoDB, CouchDB      | JSON 문서, 유연한 스키마 | 콘텐츠, 카탈로그 |
| **키-값형**  | Redis, DynamoDB       | 단순 구조, 초고속        | 캐시, 세션, 큐   |
| **컬럼형**   | Cassandra, HBase      | 대용량 쓰기, 시계열      | IoT, 로그        |
| **그래프형** | Neo4j, Amazon Neptune | 관계 탐색                | SNS, 추천        |
| **검색형**   | Elasticsearch, Solr   | 역인덱스, 전문 검색      | 검색, 로그 분석  |

[⬆ 목차로 돌아가기](#목차)

---

## RDBMS vs NoSQL 선택 기준

| 기준        | RDBMS            | NoSQL                |
|-------------|------------------|----------------------|
| 데이터 구조 | 정형, 관계형     | 비정형, 반정형       |
| 스키마      | 고정             | 유연                 |
| 트랜잭션    | 강력한 ACID      | 제한적 (DB마다 다름) |
| 확장 방식   | 수직 확장        | 수평 확장            |
| 쿼리 복잡도 | 복잡한 JOIN 가능 | 단순 쿼리 최적화     |
| 일관성      | 강한 일관성      | 최종 일관성 (CAP)    |

---

## 참고 자료

- MongoDB Documentation: [docs.mongodb.com](https://www.mongodb.com/docs/) — ★★★☆☆
- Redis Documentation: [redis.io/docs](https://redis.io/docs/) — ★★★☆☆
- Elasticsearch Documentation: [elastic.co/docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html) — ★★★☆☆

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

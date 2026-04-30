# 데이터베이스 (Database)

RDBMS 설계, 운영, 최적화 관련 문서 모음.

## 목차

| 분류 | 문서 | 설명 |
|------|------|------|
| **설계** | [정규화](rdbms_normalization.md) | 1NF~BCNF, 반정규화 판단 기준 |
| **쿼리** | [JOIN](rdbms_join.md) | JOIN 종류, 실행 방식, 최적화 |
| **쿼리** | [View](rdbms_view.md) | View, Materialized View |
| **성능** | [Index](rdbms_index.md) | B-Tree, 복합 인덱스, 커버링 인덱스 |
| **성능** | [EXPLAIN](rdbms_explain.md) | 실행 계획 분석, 슬로우 쿼리 튜닝 |
| **트랜잭션** | [Transaction](rdbms_transaction.md) | ACID, 격리 수준, MVCC |
| **트랜잭션** | [Lock](rdbms_lock.md) | Row/Gap Lock, 데드락, SKIP LOCKED |
| **프로그래밍** | [Procedure](rdbms_procedure.md) | 저장 프로시저, 커서, 예외 처리 |
| **운영** | [Replication](rdbms_replication.md) | binlog, GTID, AWS RDS Read Replica |
| **운영** | [Partition](rdbms_partition.md) | Range/List/Hash 파티셔닝, 프루닝 |
| **운영** | [Schema Migration](rdbms_schema_migration.md) | pt-osc, gh-ost, 무중단 마이그레이션 |

## 학습 순서

```
1. 정규화       → 올바른 테이블 설계
2. JOIN         → 다중 테이블 쿼리
3. Index        → 조회 성능 최적화
4. EXPLAIN      → 실행 계획 분석
5. Transaction  → 동시성 제어 이해
6. Lock         → 잠금 메커니즘
7. View         → 쿼리 추상화
8. Procedure    → 서버 사이드 로직
9. Replication  → 고가용성 구성
10. Partition   → 대용량 테이블 관리
11. Migration   → 무중단 스키마 변경
```

---

## 참고 자료

- MySQL Documentation: [dev.mysql.com](https://dev.mysql.com/doc/refman/8.0/en/)
- PostgreSQL Documentation: [postgresql.org/docs](https://www.postgresql.org/docs/current/)
- Use The Index, Luke: [use-the-index-luke.com](https://use-the-index-luke.com/)

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

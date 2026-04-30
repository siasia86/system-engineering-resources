# MongoDB

## 목차

| 단계 | 섹션                                                                                                                                                              |
|------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. MongoDB 개념](#1-mongodb-개념) / [2. 데이터 모델](#2-데이터-모델)                                                                                              |
| CRUD | [3. CRUD 기본](#3-crud-기본) / [4. 쿼리 연산자](#4-쿼리-연산자)                                                                                                    |
| 고급 | [5. 인덱스](#5-인덱스) / [6. Aggregation Pipeline](#6-aggregation-pipeline) / [7. 스키마 설계 패턴](#7-스키마-설계-패턴) / [8. 운영 팁](#8-운영-팁) |

---

## 1. MongoDB 개념

MongoDB는 **문서(Document) 기반 NoSQL 데이터베이스**다.
JSON 형태의 BSON 문서를 컬렉션에 저장한다.

### RDBMS vs MongoDB

| RDBMS | MongoDB | 설명 |
|-------|---------|------|
| Database | Database | 데이터베이스 |
| Table | Collection | 데이터 집합 |
| Row | Document | 단일 데이터 |
| Column | Field | 데이터 필드 |
| JOIN | $lookup / Embedding | 관계 표현 |
| Index | Index | 검색 최적화 |
| Transaction | Transaction (4.0+) | 원자적 처리 |

### 특징

| 항목 | 설명 |
|------|------|
| 스키마 | 유연한 스키마 (Schema-less) |
| 확장성 | 수평 확장 (Sharding) |
| 복제 | Replica Set (자동 Failover) |
| 쿼리 | 풍부한 쿼리 언어 |
| 트랜잭션 | 멀티 도큐먼트 트랜잭션 (4.0+) |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 데이터 모델

### Document 구조

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "user_id": 101,
  "username": "alice",
  "email": "alice@example.com",
  "address": {
    "city": "Seoul",
    "zip": "04524"
  },
  "tags": ["admin", "user"],
  "created_at": ISODate("2026-01-01T00:00:00Z")
}
```

### Embedding vs Referencing

| 방식 | 설명 | 적합한 경우 |
|------|------|-------------|
| **Embedding** | 관련 데이터를 문서 내 중첩 | 1:1, 1:소수, 함께 조회 |
| **Referencing** | ObjectId로 다른 컬렉션 참조 | 1:다수, 독립적 접근 |

```javascript
// Embedding (주문 내 상품 정보 포함)
{
  order_id: 1,
  items: [
    { product_id: 10, name: "Laptop", qty: 1 },
    { product_id: 11, name: "Mouse",  qty: 2 }
  ]
}

// Referencing (사용자 참조)
{
  order_id: 1,
  user_id: ObjectId("507f1f77bcf86cd799439011")
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. CRUD 기본

### Insert

```javascript
// 단일 삽입
db.users.insertOne({
  username: "alice",
  email: "alice@example.com",
  status: "active"
});

// 다중 삽입
db.users.insertMany([
  { username: "bob",   email: "bob@example.com" },
  { username: "carol", email: "carol@example.com" }
]);
```

### Find

```javascript
// 전체 조회
db.users.find();

// 조건 조회
db.users.find({ status: "active" });

// 특정 필드만 반환 (projection)
db.users.find({ status: "active" }, { username: 1, email: 1, _id: 0 });

// 정렬, 제한
db.users.find().sort({ created_at: -1 }).limit(10).skip(20);

// 단일 문서
db.users.findOne({ username: "alice" });
```

### Update

```javascript
// 단일 업데이트
db.users.updateOne(
  { username: "alice" },
  { $set: { status: "inactive" } }
);

// 다중 업데이트
db.users.updateMany(
  { status: "pending" },
  { $set: { status: "active" }, $currentDate: { updated_at: true } }
);

// Upsert (없으면 삽입)
db.users.updateOne(
  { username: "dave" },
  { $set: { email: "dave@example.com" } },
  { upsert: true }
);
```

### Delete

```javascript
db.users.deleteOne({ username: "alice" });
db.users.deleteMany({ status: "inactive" });
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 쿼리 연산자

### 비교 연산자

```javascript
db.orders.find({ amount: { $gt: 10000 } });           // >
db.orders.find({ amount: { $gte: 10000 } });          // >=
db.orders.find({ amount: { $lt: 5000 } });            // <
db.orders.find({ amount: { $ne: 0 } });               // !=
db.orders.find({ status: { $in: ["pending", "processing"] } });
db.orders.find({ status: { $nin: ["cancelled"] } });
```

### 논리 연산자

```javascript
// AND
db.orders.find({ $and: [{ amount: { $gt: 1000 } }, { status: "active" }] });
// 축약형
db.orders.find({ amount: { $gt: 1000 }, status: "active" });

// OR
db.orders.find({ $or: [{ status: "pending" }, { status: "processing" }] });

// NOT
db.orders.find({ status: { $not: { $eq: "cancelled" } } });
```

### 배열 연산자

```javascript
// 배열에 값 포함
db.users.find({ tags: "admin" });

// 배열 모든 값 포함
db.users.find({ tags: { $all: ["admin", "user"] } });

// 배열 크기
db.users.find({ tags: { $size: 2 } });

// 배열 요소 조건
db.orders.find({ "items.qty": { $gt: 5 } });
```

### 업데이트 연산자

```javascript
db.users.updateOne({ _id: id }, {
  $set:       { status: "active" },      // 필드 설정
  $unset:     { old_field: "" },         // 필드 삭제
  $inc:       { login_count: 1 },        // 숫자 증가
  $push:      { tags: "vip" },           // 배열에 추가
  $pull:      { tags: "guest" },         // 배열에서 제거
  $addToSet:  { tags: "premium" },       // 중복 없이 추가
});
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 인덱스

```javascript
// 단일 인덱스
db.users.createIndex({ email: 1 });           // 오름차순
db.users.createIndex({ created_at: -1 });     // 내림차순

// 유니크 인덱스
db.users.createIndex({ email: 1 }, { unique: true });

// 복합 인덱스
db.orders.createIndex({ user_id: 1, created_at: -1 });

// TTL 인덱스 (자동 만료)
db.sessions.createIndex(
  { created_at: 1 },
  { expireAfterSeconds: 3600 }  // 1시간 후 자동 삭제
);

// 텍스트 인덱스
db.articles.createIndex({ title: "text", content: "text" });
db.articles.find({ $text: { $search: "mongodb index" } });

// 인덱스 목록 확인
db.users.getIndexes();

// 실행 계획 확인
db.users.find({ email: "alice@example.com" }).explain("executionStats");
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Aggregation Pipeline

여러 단계를 파이프라인으로 연결하여 데이터를 변환/집계한다.

```javascript
db.orders.aggregate([
  // 1. 필터
  { $match: { status: "completed", created_at: { $gte: ISODate("2026-01-01") } } },

  // 2. 그룹 집계
  { $group: {
    _id: "$user_id",
    total_amount: { $sum: "$amount" },
    order_count:  { $count: {} },
    avg_amount:   { $avg: "$amount" }
  }},

  // 3. 정렬
  { $sort: { total_amount: -1 } },

  // 4. 제한
  { $limit: 10 },

  // 5. 다른 컬렉션 JOIN
  { $lookup: {
    from: "users",
    localField: "_id",
    foreignField: "user_id",
    as: "user_info"
  }},

  // 6. 배열 → 단일 문서
  { $unwind: "$user_info" },

  // 7. 출력 필드 선택
  { $project: {
    username: "$user_info.username",
    total_amount: 1,
    order_count: 1
  }}
]);
```

### 주요 Stage

| Stage | 설명 |
|-------|------|
| `$match` | 조건 필터 (WHERE) |
| `$group` | 집계 (GROUP BY) |
| `$sort` | 정렬 (ORDER BY) |
| `$limit` / `$skip` | 페이지네이션 |
| `$project` | 필드 선택/변환 |
| `$lookup` | 컬렉션 JOIN |
| `$unwind` | 배열 펼치기 |
| `$addFields` | 필드 추가 |
| `$facet` | 다중 집계 병렬 실행 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 스키마 설계 패턴

### Bucket 패턴 (시계열 데이터)

```javascript
// 나쁜 예: 측정값마다 문서 1개
{ sensor_id: 1, timestamp: ..., value: 23.5 }  // 수억 건

// 좋은 예: 시간 단위로 묶기
{
  sensor_id: 1,
  hour: ISODate("2026-04-30T10:00:00Z"),
  count: 60,
  sum: 1410,
  measurements: [23.5, 23.6, 23.4, ...]
}
```

### Outlier 패턴 (대용량 배열)

```javascript
// 팔로워가 수백만인 경우
{
  user_id: 1,
  followers: [...],  // 16MB 문서 한도 초과 위험
  has_extras: true
}
// 초과분은 별도 컬렉션에 저장
```

### Computed 패턴 (집계 캐싱)

```javascript
// 주문 생성 시 users.order_count 갱신
db.users.updateOne(
  { user_id: order.user_id },
  { $inc: { order_count: 1, total_spent: order.amount } }
);
// 조회 시 집계 불필요
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 운영 팁

### Replica Set

```javascript
// 복제 상태 확인
rs.status()
rs.isMaster()

// 읽기 선호도 설정
db.users.find().readPref("secondaryPreferred")
```

### 트랜잭션 (4.0+)

```javascript
const session = client.startSession();
session.startTransaction();
try {
  db.accounts.updateOne({ _id: 1 }, { $inc: { balance: -1000 } }, { session });
  db.accounts.updateOne({ _id: 2 }, { $inc: { balance:  1000 } }, { session });
  await session.commitTransaction();
} catch (e) {
  await session.abortTransaction();
} finally {
  session.endSession();
}
```

### 성능 모니터링

```javascript
// 슬로우 쿼리 프로파일링
db.setProfilingLevel(1, { slowms: 100 });
db.system.profile.find().sort({ ts: -1 }).limit(5);

// 현재 실행 중인 쿼리
db.currentOp({ active: true, secs_running: { $gt: 5 } });

// 컬렉션 통계
db.orders.stats();
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- MongoDB Documentation: [docs.mongodb.com](https://www.mongodb.com/docs/) — ★★☆☆☆
- MongoDB Aggregation: [Aggregation Pipeline](https://www.mongodb.com/docs/manual/core/aggregation-pipeline/) — ★★☆☆☆
- MongoDB Schema Design: [Schema Design Patterns](https://www.mongodb.com/blog/post/building-with-patterns-a-summary) — ★★☆☆☆

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

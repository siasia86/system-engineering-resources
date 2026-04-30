# Redis

## 목차

| 단계 | 섹션                                                                                                                                                              |
|------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. Redis 개념](#1-redis-개념) / [2. 자료구조](#2-자료구조)                                                                                                        |
| 활용 | [3. 주요 명령어](#3-주요-명령어) / [4. 만료와 영속성](#4-만료와-영속성)                                                                                            |
| 고급 | [5. 고급 기능](#5-고급-기능) / [6. 클러스터와 복제](#6-클러스터와-복제) / [7. 실전 패턴](#7-실전-패턴) |

---

## 1. Redis 개념

Redis는 **인메모리 데이터 구조 저장소**다.
캐시, 세션, 메시지 큐, 실시간 랭킹 등에 사용한다.

### 특징

| 항목 | 설명 |
|------|------|
| 저장 위치 | 메모리 (선택적 디스크 영속화) |
| 속도 | 초당 수십만 ops |
| 자료구조 | String, List, Hash, Set, Sorted Set 등 |
| 단일 스레드 | 명령어 원자적 실행 보장 |
| 복제 | Master-Replica |
| 클러스터 | Redis Cluster (수평 확장) |

### 사용 사례

| 사례 | 자료구조 |
|------|----------|
| 캐시 | String |
| 세션 저장 | Hash |
| 실시간 랭킹 | Sorted Set |
| 메시지 큐 | List / Stream |
| 중복 제거 | Set |
| 분산 락 | String (SET NX) |
| 속도 제한 | String (INCR) |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 자료구조

### String

```
Key → Value (문자열, 숫자, 바이너리)
최대 512MB
```

### List

```
Key → [v1, v2, v3, ...]  (양방향 연결 리스트)
LPUSH/RPUSH, LPOP/RPOP
```

### Hash

```
Key → { field1: val1, field2: val2, ... }
HSET, HGET, HMGET, HGETALL
```

### Set

```
Key → {v1, v2, v3}  (중복 없는 집합)
SADD, SMEMBERS, SINTER, SUNION, SDIFF
```

### Sorted Set (ZSet)

```
Key → {v1: score1, v2: score2, ...}  (score 기준 정렬)
ZADD, ZRANGE, ZRANK, ZSCORE
```

### 기타

| 자료구조 | 설명 | 사용 사례 |
|----------|------|-----------|
| **Bitmap** | 비트 단위 조작 | DAU 집계 |
| **HyperLogLog** | 근사 카디널리티 | UV 집계 |
| **Stream** | 로그 스트림 | 이벤트 큐 |
| **Geo** | 지리 좌표 | 위치 기반 검색 |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 주요 명령어

### String

```bash
SET user:1:name "Alice"
GET user:1:name

# 만료 포함
SET session:abc "data" EX 3600    # 3600초
SET session:abc "data" PX 3600000 # 3600000ms

# 원자적 증가
INCR page:views
INCRBY page:views 10
DECR page:views

# NX: 없을 때만 설정 (분산 락)
SET lock:order:1 "locked" NX EX 30
```

### Hash

```bash
HSET user:1 name "Alice" email "alice@example.com" age 30
HGET user:1 name
HMGET user:1 name email
HGETALL user:1
HDEL user:1 age
HINCRBY user:1 login_count 1
```

### List

```bash
RPUSH queue:jobs "job1" "job2" "job3"
LPOP queue:jobs          # 앞에서 꺼내기
RPOP queue:jobs          # 뒤에서 꺼내기
BLPOP queue:jobs 30      # 블로킹 팝 (30초 대기)
LRANGE queue:jobs 0 -1   # 전체 조회
LLEN queue:jobs
```

### Sorted Set

```bash
ZADD leaderboard 1500 "alice"
ZADD leaderboard 2000 "bob"
ZADD leaderboard 1800 "carol"

ZRANGE leaderboard 0 -1 WITHSCORES    # 오름차순
ZREVRANGE leaderboard 0 2 WITHSCORES  # 내림차순 상위 3
ZRANK leaderboard "alice"             # 순위 (0부터)
ZSCORE leaderboard "alice"            # 점수
ZINCRBY leaderboard 100 "alice"       # 점수 증가
```

### Set

```bash
SADD online:users 101 102 103
SISMEMBER online:users 101    # 포함 여부
SMEMBERS online:users         # 전체 조회
SCARD online:users            # 크기
SINTER online:users vip:users # 교집합
SUNION set1 set2              # 합집합
SDIFF set1 set2               # 차집합
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 만료와 영속성

### TTL 설정

```bash
EXPIRE key 3600        # 초 단위
PEXPIRE key 3600000    # 밀리초 단위
TTL key                # 남은 시간 확인 (-1: 만료 없음, -2: 키 없음)
PERSIST key            # 만료 제거
```

### 영속성 (Persistence)

| 방식 | 설명 | 장점 | 단점 |
|------|------|------|------|
| **RDB** | 주기적 스냅샷 | 빠른 재시작 | 마지막 스냅샷 이후 데이터 손실 |
| **AOF** | 모든 쓰기 명령 로그 | 데이터 손실 최소 | 파일 크기 큼, 재시작 느림 |
| **RDB+AOF** | 두 방식 결합 | 안전 | 디스크 사용량 증가 |

```bash
# redis.conf
save 900 1      # 900초 내 1번 변경 시 RDB 저장
save 300 10     # 300초 내 10번 변경 시 RDB 저장

appendonly yes  # AOF 활성화
appendfsync everysec  # 1초마다 fsync
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 고급 기능

### Pipeline (배치 명령)

```python
import redis
r = redis.Redis()

pipe = r.pipeline()
for i in range(1000):
    pipe.set(f"key:{i}", i)
pipe.execute()  # 한 번에 전송 (네트워크 왕복 1회)
```

### Lua 스크립트 (원자적 실행)

```bash
# 원자적 조건부 업데이트
EVAL "
  local val = redis.call('GET', KEYS[1])
  if val == ARGV[1] then
    return redis.call('SET', KEYS[1], ARGV[2])
  end
  return 0
" 1 mykey oldval newval
```

### Pub/Sub

```bash
# 구독
SUBSCRIBE channel:notifications

# 발행
PUBLISH channel:notifications "new message"
```

### Stream (Redis 5.0+)

```bash
# 이벤트 추가
XADD events * user_id 101 action "login"

# 소비자 그룹
XGROUP CREATE events mygroup $ MKSTREAM
XREADGROUP GROUP mygroup consumer1 COUNT 10 STREAMS events >
XACK events mygroup <message-id>
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 클러스터와 복제

### Master-Replica

```
Master ──> Replica 1
       ──> Replica 2
```

```bash
# redis.conf (Replica)
replicaof 10.0.1.10 6379
```

### Redis Sentinel (자동 Failover)

```
Sentinel 1 ─┐
Sentinel 2 ─┼──> Master 모니터링 → 장애 시 Replica 승격
Sentinel 3 ─┘
```

### Redis Cluster (수평 확장)

```
16384개 슬롯을 노드에 분산
Node 1: 슬롯 0-5460
Node 2: 슬롯 5461-10922
Node 3: 슬롯 10923-16383
```

```bash
# 클러스터 상태 확인
redis-cli cluster info
redis-cli cluster nodes
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실전 패턴

### 캐시 (Cache-Aside)

```python
def get_user(user_id):
    cache_key = f"user:{user_id}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    r.setex(cache_key, 300, json.dumps(user))  # 5분 캐시
    return user
```

### 분산 락

```python
import uuid

def acquire_lock(resource, ttl=30):
    lock_key = f"lock:{resource}"
    token = str(uuid.uuid4())
    acquired = r.set(lock_key, token, nx=True, ex=ttl)
    return token if acquired else None

def release_lock(resource, token):
    lock_key = f"lock:{resource}"
    script = """
    if redis.call('GET', KEYS[1]) == ARGV[1] then
        return redis.call('DEL', KEYS[1])
    end
    return 0
    """
    r.eval(script, 1, lock_key, token)
```

### Rate Limiting

```python
def is_rate_limited(user_id, limit=100, window=60):
    key = f"rate:{user_id}:{int(time.time() // window)}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, window)
    return count > limit
```

### 실시간 랭킹

```python
# 점수 업데이트
r.zincrby("leaderboard:daily", score_delta, user_id)

# 상위 10명 조회
top10 = r.zrevrange("leaderboard:daily", 0, 9, withscores=True)

# 내 순위
rank = r.zrevrank("leaderboard:daily", user_id)
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Redis Documentation: [redis.io/docs](https://redis.io/docs/) — ★★☆☆☆
- Redis Commands: [redis.io/commands](https://redis.io/commands/) — ★★☆☆☆
- Redis Patterns: [redis.io/docs/manual/patterns](https://redis.io/docs/manual/patterns/) — ★★☆☆☆

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

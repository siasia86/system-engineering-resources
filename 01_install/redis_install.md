# Redis 설치 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. Ubuntu 설치](#2-ubuntu-설치) / [3. RHEL 계열 설치](#3-rhel-계열-설치) |
| [4. 초기 보안 설정](#4-초기-보안-설정) / [5. 기본 설정 (redis.conf)](#5-기본-설정-redisconf) / [6. 기본 사용법](#6-기본-사용법) |
| [7. 실무 팁](#7-실무-팁) / [8. 트러블슈팅](#8-트러블슈팅) |

---

## 1. 개요

### 시스템 요구사항

| 항목 | 최소          | 권장                           |
|------|---------------|--------------------------------|
| OS   | Ubuntu 20.04+ | Ubuntu 22.04+ / Rocky 9+       |
| RAM  | 512 MB        | 4 GB 이상 (데이터 크기에 따라) |
| 포트 | 6379/tcp      | 6379/tcp                       |

### 주요 용도

| 용도        | 설명                            |
|-------------|---------------------------------|
| 캐시        | DB 쿼리 결과, API 응답 캐싱     |
| 세션 저장소 | 웹 애플리케이션 세션 관리       |
| 메시지 큐   | Pub/Sub, List 기반 작업 큐      |
| 리더보드    | Sorted Set으로 실시간 순위 관리 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Ubuntu 설치

### 2-1. 시스템 업데이트

```bash
sudo apt update && sudo apt upgrade -y
```

### 2-2. 설치 방법 A: APT (Ubuntu 기본 저장소)

```bash
sudo apt install redis-server -y
sudo systemctl enable --now redis-server
```

### 2-3. 설치 방법 B: Redis 공식 저장소 (최신 버전)

```bash
curl -fsSL https://packages.redis.io/gpg \
    | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] \
    https://packages.redis.io/deb $(lsb_release -cs) main" \
    | sudo tee /etc/apt/sources.list.d/redis.list

sudo apt update
sudo apt install redis -y
sudo systemctl enable --now redis-server
```

### 2-4. 설치 확인

```bash
redis-server --version
sudo systemctl status redis-server --no-pager | head -5
redis-cli ping
# PONG
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. RHEL 계열 설치

### 3-1. 시스템 업데이트

```bash
sudo dnf update -y
```

### 3-2. 설치 방법 A: DNF (AppStream)

```bash
sudo dnf install redis -y
sudo systemctl enable --now redis
```

### 3-3. 설치 방법 B: Redis 공식 저장소

```bash
# Redis 7.x (EL9)
sudo dnf install -y https://packages.redis.io/rpm/rhel9/x86_64/redis-release-rhel9-1.0.0-1.noarch.rpm
sudo dnf install redis -y
sudo systemctl enable --now redis
```

### 3-4. 방화벽 설정

```bash
# 내부 네트워크에서만 허용 (외부 노출 금지)
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="10.0.1.0/24" port port="6379" protocol="tcp" accept'
sudo firewall-cmd --reload
```

### 3-5. 설치 확인

```bash
redis-server --version
sudo systemctl status redis --no-pager | head -5
redis-cli ping
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 초기 보안 설정

### 4-1. 패스워드 설정 (requirepass)

```bash
sudo vi /etc/redis/redis.conf
```

```ini
# 패스워드 설정
requirepass SecurePassword123

# 외부 접속 허용 시 (기본: 127.0.0.1만 허용)
bind 127.0.0.1 10.0.1.10

# protected-mode (bind 설정 없을 때 외부 접속 차단)
protected-mode yes
```

```bash
sudo systemctl restart redis-server

# 패스워드 인증 확인
redis-cli -a SecurePassword123 ping
# PONG
```

### 4-2. 위험 명령어 비활성화

```ini
# redis.conf
rename-command FLUSHALL ""
rename-command FLUSHDB  ""
rename-command CONFIG   "SecureKey123"
rename-command DEBUG    ""
rename-command KEYS     ""   # 프로덕션에서 KEYS * 사용 금지 (블로킹)
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 기본 설정 (redis.conf)

```bash
# Ubuntu
sudo vi /etc/redis/redis.conf

# Rocky
sudo vi /etc/redis.conf
```

```ini
# 네트워크
bind 127.0.0.1
port 6379
protected-mode yes

# 메모리
maxmemory 2gb
maxmemory-policy allkeys-lru   # 메모리 초과 시 LRU 방식으로 키 제거

# 영속성
save 900 1      # 900초 내 1개 이상 변경 시 RDB 저장
save 300 10
save 60 10000
appendonly yes                  # AOF 활성화 (더 강한 내구성)
appendfsync everysec            # 1초마다 fsync

# 로그
loglevel notice
logfile /var/log/redis/redis-server.log

# 연결
maxclients 10000
timeout 300
```

### maxmemory-policy 비교

| 정책           | 설명                              | 권장 용도        |
|----------------|-----------------------------------|------------------|
| `noeviction`   | 메모리 초과 시 오류 반환          | 데이터 손실 불가 |
| `allkeys-lru`  | 전체 키 중 LRU 제거               | 캐시             |
| `volatile-lru` | TTL 있는 키 중 LRU 제거           | 세션 + 캐시 혼용 |
| `allkeys-lfu`  | 전체 키 중 사용 빈도 낮은 것 제거 | 캐시 (Redis 4+)  |

```bash
sudo systemctl restart redis-server
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 기본 사용법

### redis-cli 접속

```bash
# 로컬
redis-cli

# 패스워드 인증
redis-cli -a SecurePassword123

# 원격
redis-cli -h 10.0.1.10 -p 6379 -a SecurePassword123
```

### 자료형별 기본 명령어

```bash
# String
SET user:1:name "alice"
GET user:1:name
SETEX session:abc123 3600 "user_data"   # TTL 3600초
TTL session:abc123

# Hash
HSET user:1 name "alice" email "alice@example.com"
HGET user:1 name
HGETALL user:1

# List (큐)
RPUSH queue:jobs "job1" "job2"
LPOP queue:jobs
LLEN queue:jobs

# Set
SADD tags:post:1 "redis" "cache"
SMEMBERS tags:post:1
SISMEMBER tags:post:1 "redis"

# Sorted Set (리더보드)
ZADD leaderboard 1500 "alice" 2000 "bob"
ZREVRANGE leaderboard 0 9 WITHSCORES   # 상위 10명

# 키 관리
EXISTS user:1:name
DEL user:1:name
EXPIRE user:1:name 3600
KEYS user:*        # 🟡 프로덕션 사용 금지 → SCAN 사용
SCAN 0 MATCH user:* COUNT 100
```

### 서버 정보 확인

```bash
redis-cli info server    # 서버 정보
redis-cli info memory    # 메모리 사용량
redis-cli info stats     # 통계
redis-cli info replication  # 복제 상태
redis-cli monitor        # 실시간 명령어 모니터링 (🟡 성능 영향)
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실무 팁

### Tip 1: KEYS 대신 SCAN 사용

```bash
# 나쁜 예: 전체 키 스캔 → 서버 블로킹
redis-cli KEYS "session:*"

# 좋은 예: 커서 기반 점진적 스캔
redis-cli SCAN 0 MATCH "session:*" COUNT 100
```

### Tip 2: Pipeline으로 다중 명령 일괄 처리

```bash
# 개별 명령 (N번 왕복)
for i in $(seq 1 1000); do redis-cli SET key:$i val:$i; done

# Pipeline (1번 왕복)
redis-cli --pipe << 'EOF'
SET key:1 val:1
SET key:2 val:2
SET key:3 val:3
EOF
```

### Tip 3: 메모리 사용량 모니터링

```bash
redis-cli info memory | grep -E "used_memory_human|maxmemory_human|mem_fragmentation_ratio"

# 키별 메모리 사용량 (상위 10개)
redis-cli --memkeys | head -10
```

### Tip 4: Slow Log 확인

```bash
# 슬로우 쿼리 기준 설정 (마이크로초, 기본 10000 = 10ms)
redis-cli CONFIG SET slowlog-log-slower-than 1000

# 슬로우 로그 조회
redis-cli SLOWLOG GET 10
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                             | 원인                       | 해결 방법                              |
|----------------------------------|----------------------------|----------------------------------------|
| `NOAUTH Authentication required` | 패스워드 미입력            | `redis-cli -a SecurePassword123`       |
| `OOM command not allowed`        | maxmemory 초과, noeviction | maxmemory-policy 변경 또는 메모리 증설 |
| `KEYS` 명령으로 서버 응답 없음   | 대용량 키 블로킹           | `SCAN` 으로 대체                       |
| 연결 거부 (원격)                 | bind 127.0.0.1 제한        | `bind` 설정 변경 + 방화벽 허용         |
| RDB 저장 실패                    | 디스크 공간 부족           | `df -h` 확인, 불필요한 파일 정리       |
| 메모리 단편화 높음 (ratio > 1.5) | 잦은 삭제/만료             | `redis-cli MEMORY PURGE` 또는 재시작   |

```bash
# 에러 로그 확인
sudo tail -50 /var/log/redis/redis-server.log

# 현재 연결 수
redis-cli info clients | grep connected_clients
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Redis Documentation: [redis.io/docs](https://redis.io/docs/) — ★★★★☆
- Redis Commands: [redis.io/commands](https://redis.io/commands/) — ★★★☆☆
- [nosql_redis.md](../10_nosql/nosql_redis.md)

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

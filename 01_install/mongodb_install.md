# MongoDB 설치 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. Ubuntu 설치](#2-ubuntu-설치) / [3. RHEL 계열 설치](#3-rhel-계열-설치) |
| [4. 초기 보안 설정](#4-초기-보안-설정) / [5. 기본 설정 (mongod.conf)](#5-기본-설정-mongodconf) / [6. 기본 사용법](#6-기본-사용법) |
| [7. 실무 팁](#7-실무-팁) / [8. 트러블슈팅](#8-트러블슈팅) |

---

## 1. 개요

### 시스템 요구사항

| 항목   | 최소          | 권장 (프로덕션)       |
|--------|---------------|-----------------------|
| CPU    | 2 core        | 4 core 이상           |
| RAM    | 2 GB          | 8 GB 이상             |
| 디스크 | 10 GB         | SSD 100 GB 이상       |
| 포트   | 27017/tcp     | 27017/tcp             |

### 버전 선택

| 버전       | 상태          | 권장 여부         |
|------------|---------------|-------------------|
| MongoDB 6.0| EOL 2025-07   | ⚠️ 비권장         |
| MongoDB 7.0| LTS (2027-10) | ✅ 권장           |
| MongoDB 8.0| Latest        | ✅ 신규 구축 권장 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Ubuntu 설치

### 2-1. 시스템 업데이트

```bash
sudo apt update && sudo apt upgrade -y
```

### 2-2. MongoDB 공식 저장소 추가

```bash
sudo apt install gnupg curl -y
curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc \
    | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] \
    https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/8.0 multiverse" \
    | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list

sudo apt update
sudo apt install mongodb-org -y
sudo systemctl enable --now mongod
```

### 2-3. 설치 확인

```bash
mongod --version
sudo systemctl status mongod --no-pager | head -5
mongosh --eval "db.runCommand({ connectionStatus: 1 })"
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. RHEL 계열 설치

### 3-1. 시스템 업데이트

```bash
sudo dnf update -y
```

### 3-2. MongoDB 공식 저장소 추가

```bash
sudo tee /etc/yum.repos.d/mongodb-org-8.0.repo << 'EOF'
[mongodb-org-8.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/8.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-8.0.asc
EOF

sudo dnf install mongodb-org -y
sudo systemctl enable --now mongod
```

### 3-3. SELinux 설정

```bash
# SELinux 정책 설치
sudo dnf install mongodb-org-selinux -y
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 초기 보안 설정

### 4-1. 관리자 계정 생성

```bash
mongosh
```

```javascript
use admin
db.createUser({
  user: "Secureuser123",
  pwd: "SecurePassword123",
  roles: [{ role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase"]
})
exit
```

### 4-2. 인증 활성화

```bash
sudo vi /etc/mongod.conf
```

```yaml
security:
  authorization: enabled
```

```bash
sudo systemctl restart mongod

# 인증 접속 확인
mongosh -u Secureuser123 -p SecurePassword123 --authenticationDatabase admin
```

### 4-3. 애플리케이션 전용 계정 생성

```javascript
use mydb
db.createUser({
  user: "appuser",
  pwd: "SecurePassword123",
  roles: [{ role: "readWrite", db: "mydb" }]
})
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 기본 설정 (mongod.conf)

```bash
sudo vi /etc/mongod.conf
```

```yaml
# 네트워크
net:
  port: 27017
  bindIp: 127.0.0.1   # 원격 허용 시: 0.0.0.0

# 스토리지
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
  wiredTiger:
    engineConfig:
      cacheSizeGB: 2    # RAM의 50% 권장

# 로그
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
  logRotate: reopen

# 보안
security:
  authorization: enabled

# 프로세스
processManagement:
  timeZoneInfo: /usr/share/zoneinfo
```

```bash
sudo systemctl restart mongod
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 기본 사용법

### mongosh 접속

```bash
# 로컬 (인증 없음)
mongosh

# 인증 접속
mongosh -u Secureuser123 -p SecurePassword123 --authenticationDatabase admin

# 원격 접속
mongosh "mongodb://appuser:SecurePassword123@10.0.1.10:27017/mydb"
```

### CRUD

```javascript
// DB 선택 / 생성
use mydb

// 문서 삽입
db.users.insertOne({ name: "alice", email: "alice@example.com", age: 30 })
db.users.insertMany([
  { name: "bob",   email: "bob@example.com",   age: 25 },
  { name: "carol", email: "carol@example.com", age: 35 }
])

// 조회
db.users.find()
db.users.find({ age: { $gte: 30 } })
db.users.findOne({ name: "alice" })

// 수정
db.users.updateOne({ name: "alice" }, { $set: { age: 31 } })
db.users.updateMany({ age: { $lt: 30 } }, { $inc: { age: 1 } })

// 삭제
db.users.deleteOne({ name: "alice" })
db.users.deleteMany({ age: { $lt: 20 } })

// 인덱스
db.users.createIndex({ email: 1 }, { unique: true })
db.users.getIndexes()

// 컬렉션 / DB 관리
show collections
show dbs
db.stats()
```

### 백업 / 복원

```bash
# 백업
mongodump -u Secureuser123 -p SecurePassword123 \
    --authenticationDatabase admin \
    --db mydb \
    --out /backup/$(date +%Y%m%d)

# 복원
mongorestore -u Secureuser123 -p SecurePassword123 \
    --authenticationDatabase admin \
    --db mydb \
    /backup/20260504/mydb
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실무 팁

### Tip 1: 인덱스 전략

```javascript
// 복합 인덱스 (쿼리 패턴에 맞게)
db.orders.createIndex({ user_id: 1, created_at: -1 })

// 부분 인덱스 (조건부)
db.orders.createIndex(
  { status: 1 },
  { partialFilterExpression: { status: "pending" } }
)

// 인덱스 사용 여부 확인
db.orders.find({ user_id: "u1" }).explain("executionStats")
```

### Tip 2: 슬로우 쿼리 프로파일링

```javascript
// 프로파일링 활성화 (100ms 이상)
db.setProfilingLevel(1, { slowms: 100 })

// 슬로우 쿼리 조회
db.system.profile.find().sort({ ts: -1 }).limit(10)
```

### Tip 3: WiredTiger 캐시 모니터링

```javascript
db.serverStatus().wiredTiger.cache
// "bytes currently in the cache" / "maximum bytes configured"
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                                  | 원인                          | 해결 방법                                              |
|---------------------------------------|-------------------------------|--------------------------------------------------------|
| `Authentication failed`               | 계정/패스워드 오류            | `--authenticationDatabase admin` 확인                  |
| `connection refused`                  | mongod 미실행 또는 bindIp     | `systemctl status mongod`, bindIp 설정 확인            |
| `not master` 오류                     | Replica Set에서 Secondary 쓰기 | Primary 노드에 연결                                   |
| 디스크 사용량 급증                    | 저널 + 데이터 파일            | `db.repairDatabase()` 또는 compact                     |
| 메모리 사용량 과다                    | WiredTiger 캐시 과다          | `cacheSizeGB` 조정                                     |

```bash
# 로그 확인
sudo tail -100 /var/log/mongodb/mongod.log

# 현재 연결 및 작업 확인
mongosh --eval "db.currentOp()" -u Secureuser123 -p SecurePassword123 --authenticationDatabase admin
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- MongoDB Documentation: [mongodb.com/docs](https://www.mongodb.com/docs/) — ★★★☆☆
- MongoDB CRUD: [mongodb.com/docs/manual/crud](https://www.mongodb.com/docs/manual/crud/) — ★★★☆☆
- [nosql_mongodb.md](../10_nosql/nosql_mongodb.md)

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

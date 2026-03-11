# n8n + MySQL Docker Compose Cheat Sheet

## 1️⃣ 컨테이너 관리
```
docker compose up -d                # 모든 서비스 시작 (백그라운드)
docker compose up                    # 모든 서비스 시작 (포그라운드)
docker compose down                  # 모든 서비스 중지 + 네트워크 제거
docker compose stop n8n              # 특정 서비스 중지
docker compose start n8n             # 특정 서비스 시작
docker compose restart n8n           # 특정 서비스 재시작
docker compose ps                    # 서비스 상태 확인
docker compose logs                  # 서비스 로그 확인
docker compose logs -f n8n           # 특정 서비스 실시간 로그
```

## 2️⃣ 컨테이너 내부 접속
```
docker compose exec n8n bash        # n8n 컨테이너 내부 bash 접속
docker compose exec mysql bash       # MySQL 컨테이너 내부 bash 접속
```

## 3️⃣ 이미지 관리
```
docker compose pull                  # docker-compose.yml 기준 이미지 다운로드
docker compose build                 # Dockerfile 빌드
docker compose images                # 서비스별 이미지 확인
```

## 4️⃣ 데이터 초기화 / 볼륨 관리
```
docker compose down
# n8n + MySQL 볼륨 초기화 후 재시작
docker volume rm $(docker volume ls -q | grep -E '(_data_n8n_|_data_mysql_)')
docker compose up -d

# 특정 서비스 볼륨 삭제 (중단 후)
docker compose rm -s -v n8n
docker compose rm -s -v mysql

# 사용하지 않는 dangling volume 모두 삭제
docker volume prune -f
```

## 5️⃣ n8n 관리 명령어
```
docker compose exec n8n n8n --version                                   # 실행 중 n8n 버전 확인
docker compose exec n8n n8n export:workflow --all --output=/home/node/.n8n/workflows/backup.json  # 모든 워크플로우 백업
docker compose exec n8n n8n export:credentials --all --output=/home/node/.n8n/credentials/backup.json  # 모든 credentials 백업
docker compose exec n8n n8n import:workflow --input=/home/node/.n8n/workflows/backup.json       # 워크플로우 복원
docker compose exec n8n n8n import:credentials --input=/home/node/.n8n/credentials/backup.json   # credentials 복원
```

## 6️⃣ n8n 환경 변수 관련 (HTTP / HTTPS)
```yaml
environment:
  DB_TYPE: mysqldb
  DB_MYSQLDB_HOST: mysql
  DB_MYSQLDB_PORT: 3306
  DB_MYSQLDB_DATABASE: n8n
  DB_MYSQLDB_USER: n8nuser
  DB_MYSQLDB_PASSWORD: n8npass
  N8N_HOST: sjyun-n8n.siasia.com
  N8N_PORT: 5678
  N8N_PROTOCOL: http           # http / https
  N8N_BASIC_AUTH_ACTIVE: "true"
  N8N_BASIC_AUTH_USER: admin
  N8N_BASIC_AUTH_PASSWORD: admin123
  N8N_SECURE_COOKIE: "false"   # HTTP 환경에서는 false, HTTPS 환경에서는 true
```

## 7️⃣ MySQL 연결 확인
```
docker compose exec n8n bash
mysql -h $DB_MYSQLDB_HOST -u $DB_MYSQLDB_USER -p$DB_MYSQLDB_PASSWORD $DB_MYSQLDB_DATABASE
```

## 8️⃣ 전체 초기화 (컨테이너 + 볼륨 + 네트워크)
```
docker compose down
docker volume rm $(docker volume ls -q | grep -E '(_data_n8n_|_data_mysql_|_data_portainer_)')
docker compose up -d
```
> ⚠️ 주의: 실행 중인 모든 데이터 삭제. 백업 필수


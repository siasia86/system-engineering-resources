# Docker & Docker Compose Cheat Sheet

## 1. Docker 기본 명령어

### 컨테이너 관리
```
docker ps                     # 실행 중 컨테이너 목록
docker ps -a                  # 모든 컨테이너 목록 (중단 포함)
docker stop <컨테이너>       # 컨테이너 중지
docker start <컨테이너>      # 컨테이너 시작
docker restart <컨테이너>    # 컨테이너 재시작
docker rm <컨테이너>         # 컨테이너 삭제
docker logs <컨테이너>       # 로그 확인
docker exec -it <컨테이너> bash  # 컨테이너 내부 bash 접속
```

### 이미지 관리
```
docker images                # 로컬 이미지 목록
docker pull <이미지>:<태그>  # 이미지 다운로드
docker rmi <이미지>          # 이미지 삭제
```

### 볼륨/네트워크 관리
```
docker volume ls             # 볼륨 목록
docker volume rm <볼륨>     # 볼륨 삭제
docker network ls            # 네트워크 목록
docker network inspect <네트워크>  # 네트워크 상세 정보
```

### 전체 초기화/정리
```
docker stop $(docker ps -aq)            # 모든 컨테이너 중지
docker rm $(docker ps -aq)              # 모든 컨테이너 삭제
docker volume rm $(docker volume ls -q) # 모든 볼륨 삭제
docker system prune -a -f               # 사용하지 않는 모든 이미지/컨테이너/네트워크 정리
```

## 2. Docker Compose 기본 명령어

### 컨테이너 관리
```
docker compose up -d               # 모든 서비스 시작 (백그라운드)
docker compose up                   # 모든 서비스 시작 (포그라운드)
docker compose down                 # 모든 서비스 중지 + 네트워크 제거
docker compose stop <서비스>       # 특정 서비스 중지
docker compose start <서비스>      # 특정 서비스 시작
docker compose restart <서비스>    # 특정 서비스 재시작
docker compose ps                   # 서비스 상태 확인
docker compose logs                 # 모든 서비스 로그 확인
docker compose logs -f <서비스>    # 특정 서비스 실시간 로그
```

### 컨테이너 내부 접속
```
docker compose exec <서비스> bash   # 서비스 컨테이너 내부 접속
```

### 이미지 관리
```
docker compose pull                 # docker-compose.yml 기준 이미지 다운로드
docker compose build                # Dockerfile 빌드
docker compose images               # 서비스별 이미지 확인
```

### 데이터 초기화 / 볼륨 관리
```
docker compose down
# 볼륨 초기화 후 재시작
docker volume rm $(docker volume ls -q | grep -E '(_data_)')
docker compose up -d
```

### 전체 초기화 (컨테이너 + 볼륨 + 네트워크)
```
docker compose down
docker volume rm $(docker volume ls -q)
docker compose up -d
```

### 팁
- `docker volume prune -f` : 사용하지 않는 dangling volume 삭제
- `docker compose rm -s -v <서비스>` : 중단된 서비스 컨테이너 + 볼륨 삭제
- 네트워크 확인: `docker network inspect <project>_default`
- 컨테이너 연결 테스트: `docker compose exec <서비스> ping <다른서비스>`


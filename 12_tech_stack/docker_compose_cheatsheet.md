# Docker & Docker Compose Cheat Sheet

## 목차

| 섹션                                                                                                            |
|-----------------------------------------------------------------------------------------------------------------|
| [1. Docker 기본 명령어](#1-docker-기본-명령어) / [2. Docker Compose 기본 명령어](#2-docker-compose-기본-명령어) |
| [3. Compose 네트워크](#3-compose-네트워크) / [4. Compose 고급 설정](#4-compose-고급-설정)                       |

---

## 1. Docker 기본 명령어

### 컨테이너 실행

```bash
docker run -d -p 8080:80 --name web nginx        # 백그라운드 실행
docker run -it ubuntu:22.04 bash                 # 인터랙티브 실행
docker run --rm alpine echo hello                # 실행 후 자동 삭제
docker run -e ENV_VAR=value nginx                # 환경변수 전달
docker run -v /host/path:/container/path nginx   # 볼륨 마운트
docker run --network mynet nginx                 # 네트워크 지정
```

### 컨테이너 관리

```bash
docker ps                                        # 실행 중 컨테이너 목록
docker ps -a                                     # 모든 컨테이너 목록 (중단 포함)
docker stop <컨테이너>                           # 컨테이너 중지
docker start <컨테이너>                          # 컨테이너 시작
docker restart <컨테이너>                        # 컨테이너 재시작
docker rm <컨테이너>                             # 컨테이너 삭제
docker rm -f <컨테이너>                          # 강제 삭제 (실행 중도 가능)
docker logs <컨테이너>                           # 로그 확인
docker logs -f <컨테이너>                        # 실시간 로그
docker exec -it <컨테이너> bash                  # 컨테이너 내부 접속
docker cp <컨테이너>:/path /host/path            # 컨테이너 → 호스트 파일 복사
docker cp /host/path <컨테이너>:/path            # 호스트 → 컨테이너 파일 복사
docker inspect <컨테이너>                        # 상세 정보 (JSON)
docker stats                                     # 실시간 리소스 사용량
docker diff <컨테이너>                           # 파일 변경 내역
```

### 이미지 관리

```bash
docker images                                    # 로컬 이미지 목록
docker pull <이미지>:<태그>                      # 이미지 다운로드
docker build -t myapp:1.0 .                      # Dockerfile 빌드
docker push myrepo/myapp:1.0                     # 레지스트리 푸시
docker rmi <이미지>                              # 이미지 삭제
docker image prune                               # 미사용(dangling) 이미지 삭제
docker tag myapp:1.0 myrepo/myapp:1.0            # 이미지 태그 추가
docker save myapp:1.0 | gzip > myapp.tar.gz      # 이미지 파일로 저장
docker load < myapp.tar.gz                       # 이미지 파일에서 로드
```

### 볼륨/네트워크 관리

```bash
docker volume ls                                 # 볼륨 목록
docker volume create myvol                       # 볼륨 생성
docker volume rm <볼륨>                          # 볼륨 삭제
docker volume inspect <볼륨>                     # 볼륨 상세 정보
docker network ls                                # 네트워크 목록
docker network create mynet                      # 네트워크 생성
docker network inspect <네트워크>                # 네트워크 상세 정보
docker network connect mynet <컨테이너>          # 컨테이너를 네트워크에 연결
```

### 시스템 정리

```bash
docker stop $(docker ps -aq)                     # 모든 컨테이너 중지
docker rm $(docker ps -aq)                       # 모든 컨테이너 삭제
docker volume rm $(docker volume ls -q)          # 모든 볼륨 삭제
docker system prune -a -f                        # 미사용 이미지/컨테이너/네트워크 전체 정리
docker system df                                 # 디스크 사용량 확인
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. Docker Compose 기본 명령어

### 컨테이너 관리

```bash
docker compose up -d                             # 모든 서비스 시작 (백그라운드)
docker compose up                                # 모든 서비스 시작 (포그라운드)
docker compose down                              # 모든 서비스 중지 + 네트워크 제거
docker compose down -v                           # 중지 + 볼륨까지 삭제
docker compose stop <서비스>                     # 특정 서비스 중지
docker compose start <서비스>                    # 특정 서비스 시작
docker compose restart <서비스>                  # 특정 서비스 재시작
docker compose ps                                # 서비스 상태 확인
docker compose logs                              # 모든 서비스 로그
docker compose logs -f <서비스>                  # 특정 서비스 실시간 로그
docker compose top                               # 서비스별 프로세스 목록
```

### 컨테이너 내부 접속

```bash
docker compose exec <서비스> bash                # 서비스 컨테이너 내부 접속
docker compose run --rm <서비스> bash            # 새 컨테이너로 실행 후 삭제
```

### 이미지/빌드 관리

```bash
docker compose pull                              # compose.yml 기준 이미지 다운로드
docker compose build                             # Dockerfile 빌드
docker compose build --no-cache                  # 캐시 없이 빌드
docker compose images                            # 서비스별 이미지 확인
```

### 설정 검증

```bash
docker compose config                            # compose.yml 파싱 결과 출력 (검증)
docker compose config --services                 # 서비스 목록만 출력
```

### 스케일링

```bash
docker compose up -d --scale <서비스>=3          # 서비스 인스턴스 수 조정
```

### 데이터 초기화

```bash
# 볼륨 초기화 후 재시작
docker compose down
docker volume rm $(docker volume ls -q)
docker compose up -d

# 특정 서비스만 재생성
docker compose up -d --force-recreate <서비스>
```

### 팁

- `docker compose rm -s -v <서비스>` — 중단된 서비스 컨테이너 + 볼륨 삭제
- `docker volume prune -f` — 사용하지 않는 dangling 볼륨 삭제
- `docker network inspect <project>_default` — 네트워크 확인
- `docker compose exec <서비스> ping <다른서비스>` — 컨테이너 간 연결 테스트
- `-f` 옵션으로 파일 지정: `docker compose -f docker-compose.prod.yml up -d`

[⬆ 목차로 돌아가기](#목차)

---

## 3. Compose 네트워크

### 네트워크 드라이버

| 드라이버  | 컨테이너 IP        | 호스트→컨테이너 | 외부→컨테이너 | 사용 사례                    |
|-----------|---------------------|:---:|:---:|--------------------------------------|
| bridge    | 172.17.x.x (내부)  | ✅  | ❌  | 기본값, 포트 포워딩으로 외부 노출    |
| host      | 호스트 IP 공유      | ✅  | ✅  | 성능 우선, 포트 격리 불필요          |
| macvlan   | 실제 네트워크 IP    | ❌  | ✅  | 물리 네트워크 직접 노출 (VM처럼)     |
| ipvlan    | 실제 네트워크 IP    | ❌  | ✅  | MAC 제한 환경 (클라우드/Hyper-V)     |
| overlay   | 가상 (멀티호스트)   | ✅  | ❌  | Swarm 클러스터                       |
| none      | 없음                | ❌  | ❌  | 완전 격리                            |

### compose.yml 네트워크 설정

```yaml
# bridge (기본)
networks:
  app_net:
    driver: bridge

# macvlan (사내 네트워크 직접 노출)
networks:
  ansible_net:
    driver: macvlan
    driver_opts:
      parent: eth0
    ipam:
      config:
        - subnet: 10.200.101.0/24
          gateway: 10.200.101.1
          ip_range: 10.200.101.128/27

# 서비스에 고정 IP 할당
services:
  ubuntu22:
    networks:
      ansible_net:
        ipv4_address: 10.200.101.143
```

### 네트워크 명령어

```bash
docker network ls                                # 네트워크 목록
docker network inspect <프로젝트>_<네트워크명>   # 상세 정보 (할당 IP 확인)
docker network prune                             # 미사용 네트워크 삭제
docker compose up -d --force-recreate            # 네트워크 설정 변경 후 재생성
```

### macvlan 주의사항

- 호스트 → macvlan 컨테이너 직접 통신 불가 (Linux 커널 제한)
- 해결: `docker` connection (Ansible) 또는 호스트에 macvlan sub-interface 추가
- Hyper-V 환경에서는 가상 스위치에 MAC spoofing 허용 필요

[⬆ 목차로 돌아가기](#목차)

---

## 4. Compose 고급 설정

### cgroup 설정

```yaml
services:
  ubuntu22:
    privileged: true
    cgroup: host          # cgroup v2 + systemd 249+ 필수
    # cgroup: private     # systemd 237 이하에서만 정상 동작
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
```

| cgroup 모드 | cgroupns  | systemd 237 이하 | systemd 249+ | 비고                        |
|-------------|-----------|:---:|:---:|------------------------------------|
| `host`      | host      | ✅  | ✅  | cgroup v2 호스트에서 권장          |
| `private`   | private   | ✅  | ❌  | Exit(255) 발생                     |

### 리소스 제한

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 512M
        reservations:
          cpus: "0.5"
          memory: 128M
```

### 의존성 + 헬스체크

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy
  db:
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 3
```

### 환경변수 관리

```yaml
services:
  app:
    env_file: .env                    # 파일에서 로드
    environment:
      - DB_HOST=db                    # 직접 지정
      - DB_PASSWORD=${DB_PASS}        # 셸 변수 참조
```

### 프로파일 (선택적 서비스)

```yaml
services:
  app:
    profiles: []                      # 항상 시작
  debug:
    profiles: ["dev"]                 # --profile dev 시에만 시작

# docker compose --profile dev up -d
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Docker Documentation: [docs.docker.com](https://docs.docker.com/) — ★★★☆☆
- Docker Compose Reference: [docs.docker.com/compose](https://docs.docker.com/compose/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-03-25

**마지막 업데이트**: 2026-06-16

© 2026 siasia86. Licensed under CC BY 4.0.

# Docker

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 핵심 개념](#3-핵심-개념) |
| [4. 설치](#4-설치) / [5. 주요 명령어](#5-주요-명령어) / [6. Dockerfile](#6-dockerfile) |
| [7. docker-compose](#7-docker-compose) / [8. 네트워크](#8-네트워크) / [9. 볼륨](#9-볼륨) |
| [10. Tips](#10-tips) |

---

## 1. 개요

컨테이너 기반 애플리케이션 빌드·배포·실행 플랫폼입니다. 호스트 OS 커널을 공유하여 VM 대비 가볍고 빠릅니다.

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Architecture                    │
│                                                             │
│  docker CLI ──> Docker Daemon (dockerd)                     │
│                      │                                      │
│          ┌───────────┼───────────┐                          │
│          v           v           v                          │
│      Container    Image       Network/Volume                │
└─────────────────────────────────────────────────────────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                        Host OS                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │  App A   │  │  App B   │  │  App C   │  <- Containers    │
│  ├──────────┤  ├──────────┤  ├──────────┤                   │
│  │  Libs    │  │  Libs    │  │  Libs    │                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
│  ┌─────────────────────────────────────────┐                │
│  │           Docker Engine                 │                │
│  └─────────────────────────────────────────┘                │
│  ┌─────────────────────────────────────────┐                │
│  │              Host Kernel                │                │
│  └─────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 핵심 개념

| 개념       | 설명                                                          |
|------------|---------------------------------------------------------------|
| Image      | 컨테이너 실행에 필요한 파일 시스템 스냅샷 (읽기 전용)         |
| Container  | Image를 실행한 인스턴스 (읽기/쓰기 레이어 추가)               |
| Dockerfile | Image 빌드 명령어 정의 파일                                   |
| Registry   | Image 저장소 (Docker Hub, ECR, GCR 등)                        |
| Volume     | 컨테이너 외부 영구 데이터 저장소                              |
| Network    | 컨테이너 간 통신 설정 (bridge, host, overlay 등)              |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설치

### Ubuntu

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

### 버전 확인

```bash
docker version
docker info
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 주요 명령어

### 컨테이너

```bash
docker run -d -p 8080:80 --name web nginx        # 실행
docker run -it ubuntu:22.04 bash                 # 인터랙티브
docker ps                                        # 실행 중 목록
docker ps -a                                     # 전체 목록
docker stop web                                  # 중지
docker rm web                                    # 삭제
docker exec -it web bash                         # 접속
docker logs -f web                               # 로그
docker inspect web                               # 상세 정보
```

### 이미지

```bash
docker images                                    # 목록
docker pull nginx:1.25                           # 다운로드
docker build -t myapp:1.0 .                      # 빌드
docker push myrepo/myapp:1.0                     # 푸시
docker rmi myapp:1.0                             # 삭제
docker image prune                               # 미사용 삭제
```

### 시스템

```bash
docker system df                                 # 디스크 사용량
docker system prune -a                           # 전체 정리
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Dockerfile

```dockerfile
FROM ubuntu:22.04

# 레이어 최소화를 위해 RUN 명령어 체이닝
RUN apt-get update && apt-get install -y \
    nginx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 주요 지시어

| 지시어      | 설명                                      |
|-------------|-------------------------------------------|
| `FROM`      | 베이스 이미지                             |
| `RUN`       | 빌드 시 명령어 실행                       |
| `COPY`      | 호스트 파일을 이미지로 복사               |
| `ADD`       | COPY + URL/tar 압축 해제 지원             |
| `ENV`       | 환경변수 설정                             |
| `EXPOSE`    | 컨테이너 포트 문서화 (실제 바인딩 아님)   |
| `CMD`       | 컨테이너 기본 실행 명령어                 |
| `ENTRYPOINT`| 컨테이너 진입점 (CMD와 조합 가능)         |
| `ARG`       | 빌드 시 전달 인자                         |

[⬆ 목차로 돌아가기](#목차)

---

## 7. docker-compose

여러 컨테이너를 하나의 파일로 정의하고 함께 관리합니다.

```yaml
# compose.yml
services:
  web:
    image: nginx:1.25
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html
    depends_on:
      - db

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: SecurePassword123
      MYSQL_DATABASE: SecureDbName123
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:
```

```bash
docker compose up -d        # 백그라운드 실행
docker compose down         # 중지 + 컨테이너 삭제
docker compose down -v      # 볼륨까지 삭제
docker compose logs -f web  # 로그
docker compose ps           # 상태 확인
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 네트워크

```bash
docker network ls                              # 목록
docker network create mynet                    # 생성
docker run --network mynet nginx               # 네트워크 지정
```

| 드라이버  | 설명                                              |
|-----------|---------------------------------------------------|
| `bridge`  | 기본값. 호스트와 격리된 내부 네트워크             |
| `host`    | 호스트 네트워크 직접 사용 (포트 바인딩 불필요)    |
| `none`    | 네트워크 없음                                     |
| `overlay` | Swarm/멀티호스트 컨테이너 간 통신                 |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 볼륨

```bash
docker volume create mydata
docker run -v mydata:/app/data nginx           # named volume
docker run -v $(pwd)/data:/app/data nginx      # bind mount
docker volume ls
docker volume rm mydata
```

| 유형         | 설명                                          |
|--------------|-----------------------------------------------|
| Named Volume | Docker가 관리. 경로 추상화, 이식성 높음       |
| Bind Mount   | 호스트 경로 직접 마운트. 개발 환경에 적합     |
| tmpfs        | 메모리 마운트. 재시작 시 데이터 소멸          |

[⬆ 목차로 돌아가기](#목차)

---

## 10. Tips

```bash
# 실행 중인 컨테이너 리소스 사용량
docker stats

# 이미지 레이어 분석
docker history myapp:1.0

# 컨테이너 → 이미지 저장
docker commit web myapp:snapshot
```

멀티스테이지 빌드로 이미지 크기를 최소화합니다.

```dockerfile
FROM golang:1.21 AS builder
RUN go build -o app .

FROM alpine:3.19
COPY --from=builder /app .
CMD ["./app"]
```

⚠️ `docker system prune -a`는 중지된 컨테이너와 미사용 이미지를 모두 삭제합니다. 운영 환경에서 주의가 필요합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Docker Documentation: [docs.docker.com](https://docs.docker.com/) — ★★★☆☆
- Docker Hub: [hub.docker.com](https://hub.docker.com/) — ★★☆☆☆
- Dockerfile Best Practices: [docs.docker.com/develop/develop-images/dockerfile_best-practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-15

**마지막 업데이트**: 2026-05-15

© 2026 siasia86. Licensed under CC BY 4.0.

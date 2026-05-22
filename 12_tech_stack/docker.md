# Docker

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 아키텍처](#2-아키텍처) / [3. 핵심 개념](#3-핵심-개념) |
| [4. 설치](#4-설치) / [5. 주요 명령어](#5-주요-명령어) / [6. Dockerfile](#6-dockerfile) |
| [7. docker-compose](#7-docker-compose) / [8. 네트워크](#8-네트워크) / [9. 볼륨](#9-볼륨) |
| [10. Tips](#10-tips) / [11. cgroup Namespace](#11-cgroup-namespace) / [12. Union Filesystem](#12-union-filesystem) |

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
docker network create mynet                    # bridge 네트워크 생성
docker network create -d macvlan \
  --subnet 10.200.101.0/24 \
  --gateway 10.200.101.1 \
  -o parent=eth0 macvlan_net                   # macvlan 네트워크 생성
docker run --network mynet nginx               # 네트워크 지정
docker network inspect mynet                   # 상세 정보
docker network connect mynet <컨테이너>        # 실행 중 컨테이너에 네트워크 추가
```

### 드라이버 비교

| 드라이버  | MAC 주소    | 외부 직접 접속 | 호스트↔컨테이너 | 사용 사례                          |
|-----------|-------------|----------------|------------------|------------------------------------|
| `bridge`  | 가상        | 포트 포워딩    | ✅               | 기본값, 단일 호스트 개발/테스트    |
| `macvlan` | 고유 MAC    | ✅ 직접        | ❌ (별도 설정)   | 물리 네트워크 직접 노출            |
| `ipvlan`  | 호스트 공유 | ✅ 직접        | ❌ (별도 설정)   | MAC 제한 환경 (일부 클라우드/Hyper-V) |
| `host`    | 호스트 공유 | ✅ 직접        | ✅               | 성능 최우선, 포트 격리 불필요      |
| `overlay` | 가상        | 포트 포워딩    | ✅               | Swarm/멀티호스트 클러스터          |
| `none`    | 없음        | ❌             | ❌               | 완전 격리                          |

### macvlan vs ipvlan

| 항목              | macvlan                        | ipvlan (L2)                    |
|-------------------|--------------------------------|--------------------------------|
| MAC 주소          | 컨테이너별 고유 MAC            | 호스트 MAC 공유                |
| Hyper-V 설정      | MAC spoofing On 필요           | 불필요                         |
| 스위치 MAC 제한   | 포트당 MAC 수 제한에 걸릴 수 있음 | 제한 없음                   |
| 권장 환경         | 물리 서버, MAC spoofing 가능   | 클라우드 VM, Hyper-V           |

⚠️ macvlan/ipvlan 모두 호스트→컨테이너 직접 통신이 기본적으로 불가합니다. 필요 시 호스트에 별도 macvlan/ipvlan 인터페이스를 추가합니다.

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

## 11. cgroup Namespace

### cgroup 이란

cgroup(Control Group)은 프로세스의 CPU/메모리/IO 자원을 제한·격리하는 Linux 커널 기능입니다.
Docker는 컨테이너별 자원 제한에 cgroup을 사용합니다.

### cgroup 버전

| 버전    | 특징                                      | 확인 명령어                        |
|---------|-------------------------------------------|------------------------------------|
| v1      | 계층별 분리, 레거시                       | `mount \| grep cgroup`             |
| v2      | 단일 계층, 통합 인터페이스 (Ubuntu 22+)   | `stat -fc %T /sys/fs/cgroup`       |

```bash
# cgroup 버전 확인
stat -fc %T /sys/fs/cgroup
# cgroup2fs → v2 / tmpfs → v1
```

### cgroup 네임스페이스 모드

| 모드      | 설명                                                        |
|-----------|-------------------------------------------------------------|
| `host`    | 컨테이너 런타임의 cgroup 네임스페이스 사용 (런타임 기본값) |
| `private` | 컨테이너 전용 독립 cgroup 네임스페이스                      |

```
host 모드:
  컨테이너 A ── 런타임 cgroup 네임스페이스 공유
  컨테이너 B ── 런타임 cgroup 네임스페이스 공유

private 모드:
  컨테이너 A ── 독립 cgroup 네임스페이스
  컨테이너 B ── 독립 cgroup 네임스페이스
```

### compose.yml 설정

```yaml
services:
  ubuntu22:
    image: geerlingguy/docker-ubuntu2204-ansible
    privileged: true
    command: /lib/systemd/systemd
    cgroup: private          # 컨테이너 전용 독립 cgroup 네임스페이스
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
```

### 실제 동작 확인 (테스트 결과)

Docker는 컨테이너마다 고유한 cgroup 경로를 자동 할당합니다:

```
/sys/fs/cgroup/system.slice/docker-<container_id_A>.scope
/sys/fs/cgroup/system.slice/docker-<container_id_B>.scope
```

따라서 **같은 호스트에서 systemd 컨테이너 여러 개를 동시에 실행해도 실제로는 충돌하지 않습니다.**
`cgroup: private` 없이도 동시 실행이 가능합니다.

`cgroup: private`이 유효한 경우:
- 컨테이너 내부에서 `/sys/fs/cgroup`의 루트가 컨테이너 자신의 cgroup으로 보임 (격리 강화)
- 컨테이너 내부 프로세스가 호스트 전체 cgroup 트리를 볼 수 없게 제한
- 보안 격리가 필요한 환경에서 권장

⚠️ `cgroup: private`은 Docker Compose v2.x 이상에서 지원합니다. (공식 문서: [compose-spec cgroup](https://docs.docker.com/reference/compose-file/services/#cgroup))

[⬆ 목차로 돌아가기](#목차)

## 12. Union Filesystem

여러 디렉토리(레이어)를 하나의 디렉토리처럼 겹쳐 보이게 하는 파일시스템입니다.
Docker는 내부적으로 OverlayFS(구: AUFS)를 사용합니다.

### 구조

```
Layer 3 (read-write) <- added on container start, records changes
Layer 2 (read-only)  <- nginx install layer
Layer 1 (read-only)  <- Ubuntu base layer
─────────────────────────────────────────
Mount point /        <- unified view shown to user
```

레이어 3은 컨테이너 실행 시 추가되며 삭제 시 함께 제거됩니다. 레이어 1~2는 이미지 레이어로 read-only입니다.

- 이미지 레이어: read-only, 여러 컨테이너가 공유
- 컨테이너 레이어: read-write, 컨테이너 삭제 시 함께 삭제
- Copy-on-Write: 파일 수정 시 하위 레이어는 그대로, 변경분만 상위 레이어에 기록

### 실무 영향

#### 1. 이미지 pull — 레이어 재사용

```bash
docker pull nginx
# Already exists  ← 다른 이미지와 공유 레이어는 재다운로드 안 함
# Pull complete
```

#### 2. Dockerfile 레이어 캐시

상위 레이어가 변경되면 이후 레이어 캐시가 모두 무효화됩니다.
변경 빈도가 낮은 레이어를 앞에 배치해야 빌드가 빠릅니다.

```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y gcc  # 자주 안 바뀜 → 앞에
COPY app/ /app/                               # 자주 바뀜 → 뒤에
```

#### 3. 컨테이너 파일 수정은 이미지에 반영 안 됨

```bash
docker exec mycontainer rm -rf /var/log/nginx
docker stop mycontainer && docker start mycontainer
# → /var/log/nginx 다시 살아있음 (read-only 레이어에 있으므로)
```

컨테이너 삭제 시 read-write 레이어만 삭제됩니다. 데이터 유지가 필요하면 volume을 사용합니다.

#### 4. RUN 명령어 체이닝 — 이미지 용량 최소화

같은 레이어에서 파일을 삭제해야 실제 이미지 용량이 줄어듭니다.
레이어가 확정된 이후 다음 레이어에서 삭제해도 이전 레이어에 데이터가 남습니다.

```dockerfile
# ❌ 레이어 2개 — apt 캐시가 레이어에 남음 (487MB)
RUN apt-get install -y gcc
RUN rm -rf /var/lib/apt/lists/*

# ✅ 레이어 1개 — 레이어 확정 시점에 캐시 없음 (359MB)
RUN apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
```

실측 결과 (Ubuntu 22.04 + gcc 기준):

| Dockerfile      | 이미지 크기 | 차이        |
|-----------------|-------------|-------------|
| RUN 2줄 분리    | 487MB       | —           |
| RUN 1줄 체이닝  | 359MB       | **-128MB**  |

#### 5. 디스크 용량 관리

```bash
docker system df        # Images / Containers / Volumes / Build Cache 전체 확인
docker image history nginx  # 레이어별 크기 확인
```

`docker system df` 출력 항목:

| 항목 | 설명 |
|------|------|
| Images | 이미지 레이어 전체 |
| Containers | 각 컨테이너의 read-write 레이어 |
| Local Volumes | 마운트된 볼륨 |
| Build Cache | `docker build` 중간 레이어 캐시 |

항목별 정리 명령어:

```bash
docker image prune       # 미사용 이미지
docker container prune   # 중지된 컨테이너
docker volume prune      # 미사용 볼륨
docker builder prune     # 빌드 캐시

docker system prune -a   # 위 4가지 전부 (실행 중 컨테이너 제외) — ⚠️ 운영 환경 주의
```

---

[⬆ 목차로 돌아가기](#목차)

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

**마지막 업데이트**: 2026-05-22

© 2026 siasia86. Licensed under CC BY 4.0.

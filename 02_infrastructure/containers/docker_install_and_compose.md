# Docker 설치와 초기 설정
<!-- reference: _reference/docker_official_notes.md -->

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. Ubuntu 설치](#2-ubuntu-설치) / [3. RHEL 계열 설치](#3-rhel-계열-설치)           |
| [4. 초기 설정](#4-초기-설정) / [5. 기본 사용법](#5-기본-사용법) / [6. Docker Compose](#6-docker-compose) |
| [7. 실무 팁](#7-실무-팁) / [8. 트러블슈팅](#8-트러블슈팅) / [9. macvlan 네트워크](#9-macvlan-네트워크)   |

---

## 1. 개요

### 시스템 요구사항

| 항목   | 최소                    | 권장                     |
|--------|-------------------------|--------------------------|
| OS     | Ubuntu 22.04+ / RHEL 8+ | Ubuntu 24.04+ / Rocky 9+ |
| CPU    | 1 core (64-bit)         | 2 core 이상              |
| RAM    | 512 MB                  | 2 GB 이상                |
| 디스크 | 10 GB                   | SSD 50 GB 이상           |

### Docker Engine vs Docker Desktop

| 항목      | Docker Engine     | Docker Desktop              |
|-----------|-------------------|-----------------------------|
| 대상      | Linux 서버        | macOS / Windows / Linux GUI |
| 설치 방식 | CLI               | GUI 인스톨러                |
| 라이선스  | Apache 2.0 (무료) | 기업 규모에 따라 유료       |
| 권장 환경 | 서버 / CI         | 개발자 로컬                 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Ubuntu 설치

### Ubuntu 버전별 차이

| 항목          | Ubuntu 22.04 (Jammy) | Ubuntu 24.04 (Noble) |
|---------------|----------------------|----------------------|
| 저장소 코드명 | `jammy`              | `noble`              |
| 설치 방법     | 동일                 | 동일                 |

### 2-1. 시스템 업데이트

```bash
sudo apt update && sudo apt upgrade -y
```

### 2-2. Docker 공식 저장소 추가

```bash
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# DEB822 형식 (Ubuntu 22.04+ 공식 권장)
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<'SRCEOF'
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: UBUNTU_CODENAME
Components: stable
Architectures: ARCH
Signed-By: /etc/apt/keyrings/docker.asc
SRCEOF
# Suites/Architectures 값 자동 치환
CODENAME=$(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
ARCH=$(dpkg --print-architecture)
sudo sed -i "s/UBUNTU_CODENAME/$CODENAME/; s/ARCH/$ARCH/" /etc/apt/sources.list.d/docker.sources

sudo apt update
```

### 2-3. Docker 설치

```bash
sudo apt install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

sudo systemctl enable --now docker
```

### 2-4. 설치 확인

```bash
docker --version
docker compose version
sudo docker run --rm hello-world
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. RHEL 계열 설치

Rocky Linux, AlmaLinux, RHEL, CentOS Stream에서 동일하게 적용됩니다.

### 3-1. 시스템 업데이트

```bash
sudo dnf update -y
```

### 3-2. Docker 공식 저장소 추가

```bash
sudo dnf install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
```

### 3-3. Docker 설치

```bash
sudo dnf install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

sudo systemctl enable --now docker
```

### 3-4. SELinux 설정

RHEL 계열은 SELinux가 기본 활성화되어 있습니다.
볼륨 마운트 시 컨텍스트 레이블이 필요합니다.

```bash
# SELinux 상태 확인
getenforce

# 볼륨 마운트 시 :z (공유) 또는 :Z (전용) 레이블 사용
# compose.yaml 예시:
# volumes:
#   - ./data:/app/data:z
```

### 3-5. 설치 확인

```bash
docker --version
docker compose version
sudo docker run --rm hello-world
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 초기 설정

### 4-1. sudo 없이 docker 실행

```bash
sudo usermod -aG docker $USER

# 현재 세션에 즉시 적용
newgrp docker

# 확인
docker ps
```

🟡 로그아웃 후 재로그인해야 완전히 적용됩니다.

### 4-2. daemon.json 설정

```bash
sudo vi /etc/docker/daemon.json
```

```json
{
  "log-driver": "local",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65536,
      "Soft": 65536
    }
  }
}
```

```bash
sudo systemctl restart docker
sudo docker info --format '{{.LoggingDriver}}'
```

> `local` 드라이버는 자동 로테이션을 지원하며 `json-file`보다 효율적입니다(공식 문서 권장).
> daemon.json은 JSON 형식이라 `//` 주석을 넣으면 dockerd가 설정을 읽지 못합니다.
> `json-file`은 기본값이지만 로테이션이 없어 디스크 고갈 위험이 있습니다.

### 4-3. 방화벽 설정

Docker는 `iptables`를 직접 조작하므로 `ufw` / `firewalld` 규칙을 우회할 수 있습니다.

```bash
# Ubuntu (ufw)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Rocky (firewalld)
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

🟡 Docker가 관리하는 포트는 `ufw status`에 표시되지 않아도 외부에서 접근 가능하다.
내부 전용 서비스는 `127.0.0.1:PORT:PORT` 형식으로 바인딩할 것.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 기본 사용법

### 이미지

```bash
# 검색 / 다운로드
docker search nginx
docker pull nginx:alpine

# 이미지 목록 / 삭제
docker images
docker rmi nginx:alpine

# 미사용 이미지 일괄 삭제
docker image prune -a
```

### 컨테이너

```bash
# 실행
docker run -d \
    --name web \
    -p 8080:80 \
    -v $(pwd)/html:/usr/share/nginx/html:ro \
    --restart unless-stopped \
    nginx:alpine

# 목록 (실행 중 / 전체)
docker ps
docker ps -a

# 로그
docker logs web
docker logs -f --tail 100 web

# 접속
docker exec -it web sh

# 중지 / 시작 / 삭제
docker stop web
docker start web
docker rm -f web
```

### 시스템 정리

```bash
# 중지된 컨테이너, 미사용 네트워크/이미지/익명 볼륨 일괄 삭제
docker system prune -a --volumes

# 디스크 사용량 확인
docker system df
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Docker Compose

Compose 플러그인 설치, `compose.yaml` 작성, 명령, 운영 설정(healthcheck, 로그·리소스 제한, 포트 바인딩, 태그 고정), 검증은 [Docker Compose](./docker_compose.md) 문서로 옮겼습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실무 팁

Compose 실무 팁은 [Docker Compose](./docker_compose.md) 8절로 옮겼습니다. 컨테이너 로그 파일 크기는 다음 명령으로 확인합니다.

```bash
sudo du -sh /var/lib/docker/containers/*/*-json.log | sort -rh | head -10
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                                  | 원인                     | 해결 방법                                     |
|---------------------------------------|--------------------------|-----------------------------------------------|
| `permission denied` (docker 명령)     | docker 그룹 미적용       | `sudo usermod -aG docker $USER` 후 재로그인   |
| `port is already allocated`           | 호스트 포트 충돌         | `ss -tlnp \| grep PORT` 로 점유 프로세스 확인 |
| 컨테이너가 즉시 종료됨                | 포그라운드 프로세스 없음 | `docker logs CONTAINER` 로 오류 확인          |
| `no space left on device`             | Docker 디스크 가득 참    | `docker system prune -a --volumes`            |
| RHEL: 볼륨 마운트 `permission denied` | SELinux 컨텍스트 불일치  | 볼륨 경로에 `:z` 또는 `:Z` 추가               |
| `Cannot connect to the Docker daemon` | docker 서비스 미실행     | `sudo systemctl start docker`                 |

### 디버깅 명령

```bash
# 컨테이너 상세 정보
docker inspect CONTAINER

# 실시간 리소스 사용량
docker stats

# 컨테이너 내부 프로세스
docker top CONTAINER

# 네트워크 확인
docker network ls
docker network inspect NETWORK

# 볼륨 확인
docker volume ls
docker volume inspect VOLUME
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. macvlan 네트워크

macvlan 개념, Hyper-V MAC 스푸핑 설정, compose 설정, `ip_range` 계산, 호스트에서 컨테이너로 접속하는 방법, bridge와의 비교는 [Docker 네트워크](./docker_network.md) 7절로 옮겼습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Docker Documentation: [Install Docker Engine](https://docs.docker.com/engine/install/) — ★★★☆☆
- Docker Documentation: [Docker Compose](https://docs.docker.com/compose/) — ★★★☆☆
- Docker Documentation: [Compose file reference](https://docs.docker.com/reference/compose-file/) — ★★★☆☆
- Docker Documentation: [Configure logging drivers](https://docs.docker.com/engine/logging/configure/) — ★★★☆☆
- Docker Documentation: [docker compose up (변경 시 멈추고 다시 만듦)](https://docs.docker.com/reference/cli/docker/compose/up/) — ★★★☆☆

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

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.

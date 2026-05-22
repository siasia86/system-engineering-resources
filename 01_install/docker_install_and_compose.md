# Docker 설치 및 Compose 운영 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. Ubuntu 설치](#2-ubuntu-설치) / [3. RHEL 계열 설치](#3-rhel-계열-설치) |
| [4. 초기 설정](#4-초기-설정) / [5. 기본 사용법](#5-기본-사용법) / [6. Docker Compose](#6-docker-compose) |
| [7. 실무 팁](#7-실무-팁) / [8. 트러블슈팅](#8-트러블슈팅) |

---

## 1. 개요

### 시스템 요구사항

| 항목   | 최소                              | 권장                              |
|--------|-----------------------------------|-----------------------------------|
| OS     | Ubuntu 20.04+ / RHEL 8+           | Ubuntu 22.04+ / Rocky 9+          |
| CPU    | 1 core (64-bit)                   | 2 core 이상                       |
| RAM    | 512 MB                            | 2 GB 이상                         |
| 디스크 | 10 GB                             | SSD 50 GB 이상                    |

### Docker Engine vs Docker Desktop

| 항목        | Docker Engine          | Docker Desktop              |
|-------------|------------------------|-----------------------------|
| 대상        | Linux 서버             | macOS / Windows / Linux GUI |
| 설치 방식   | CLI                    | GUI 인스톨러                |
| 라이선스    | Apache 2.0 (무료)      | 기업 규모에 따라 유료       |
| 권장 환경   | 서버 / CI              | 개발자 로컬                 |

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

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

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

⚠️ 로그아웃 후 재로그인해야 완전히 적용됩니다.

### 4-2. daemon.json 설정

```bash
sudo vi /etc/docker/daemon.json
```

```json
{
  "log-driver": "json-file",
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

⚠️ Docker가 관리하는 포트는 `ufw status`에 표시되지 않아도 외부에서 접근 가능하다.
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
# 중지된 컨테이너, 미사용 네트워크/이미지/볼륨 일괄 삭제
docker system prune -a --volumes

# 디스크 사용량 확인
docker system df
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Docker Compose

### compose.yaml 기본 구조

```yaml
# compose.yaml (권장 파일명, docker-compose.yml도 지원)
services:
  app:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
    environment:
      - TZ=Asia/Seoul
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy

  db:
    image: mysql:8.4
    environment:
      MYSQL_ROOT_PASSWORD: SecurePassword123
      MYSQL_DATABASE: mydb
      MYSQL_USER: Secureuser123
      MYSQL_PASSWORD: SecurePassword123
    volumes:
      - db_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  db_data:
```

### 주요 명령어

| 명령어                          | 설명                                    |
|---------------------------------|-----------------------------------------|
| `docker compose up -d`          | 백그라운드 실행 (이미지 없으면 pull)    |
| `docker compose down`           | 컨테이너 + 네트워크 삭제                |
| `docker compose down -v`        | 볼륨까지 삭제                           |
| `docker compose ps`             | 서비스 상태 확인                        |
| `docker compose logs -f`        | 전체 로그 스트리밍                      |
| `docker compose logs -f app`    | 특정 서비스 로그                        |
| `docker compose exec app sh`    | 컨테이너 접속                           |
| `docker compose pull`           | 이미지 최신화                           |
| `docker compose up -d --build`  | 이미지 빌드 후 재시작                   |
| `docker compose restart app`    | 특정 서비스 재시작                      |
| `docker compose config`         | 최종 설정 확인 (변수 치환 결과)         |

### 환경 변수 분리 (.env)

민감 정보는 `.env` 파일로 분리하고 `.gitignore`에 추가합니다.

```bash
# .env
MYSQL_ROOT_PASSWORD=SecurePassword123
MYSQL_USER=Secureuser123
MYSQL_PASSWORD=SecurePassword123
APP_PORT=8080
```

```yaml
# compose.yaml
services:
  db:
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
  app:
    ports:
      - "${APP_PORT}:80"
```

```bash
# .gitignore
.env
```

### 멀티 환경 구성 (override)

```bash
# 기본 설정
compose.yaml

# 개발 환경: docker compose up 시 자동 병합
compose.override.yaml

# 프로덕션 환경: 명시적 지정
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

```yaml
# compose.prod.yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
    logging:
      driver: json-file
      options:
        max-size: "100m"
        max-file: "3"
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 실무 팁

### Tip 1: 내부 서비스는 127.0.0.1에 바인딩

외부에 노출하지 않을 서비스는 루프백에만 바인딩합니다.

```yaml
services:
  db:
    ports:
      - "127.0.0.1:3306:3306"   # 로컬에서만 접근 가능
  app:
    ports:
      - "0.0.0.0:80:80"         # 외부 접근 허용 (기본값)
```

### Tip 2: Named Volume vs Bind Mount

| 항목          | Named Volume                          | Bind Mount                    |
|---------------|---------------------------------------|-------------------------------|
| 경로          | Docker 관리 (`/var/lib/docker/volumes/`) | 호스트 절대경로            |
| 백업          | `docker volume` 명령으로 관리         | 호스트 파일시스템 직접 접근   |
| 권장 용도     | DB 데이터, 영구 저장소                | 설정 파일, 소스 코드 (개발)   |
| SELinux       | 자동 처리                             | `:z` / `:Z` 레이블 필요       |

```yaml
volumes:
  - db_data:/var/lib/mysql                          # Named Volume (DB 권장)
  - ./config/nginx.conf:/etc/nginx/nginx.conf:ro    # Bind Mount (설정 파일)
```

### Tip 3: healthcheck로 의존성 순서 보장

`depends_on`만으로는 서비스 준비 완료를 보장하지 않습니다.

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy
  db:
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
```

### Tip 4: 이미지 태그 고정

```yaml
# 나쁜 예: 예기치 않은 업데이트로 장애 유발 가능
image: mysql:latest

# 좋은 예: 마이너 버전까지 고정
image: mysql:8.4.5
```

### Tip 5: 무중단 업데이트

```bash
# 1. 새 이미지 pull
docker compose pull app

# 2. 해당 서비스만 재시작 (다른 서비스 영향 없음)
docker compose up -d --no-deps app

# 3. 이전 이미지 정리
docker image prune -f
```

### Tip 6: 로그 디스크 관리

```yaml
services:
  app:
    logging:
      driver: json-file
      options:
        max-size: "50m"
        max-file: "5"
```

```bash
# 컨테이너 로그 파일 크기 확인
sudo du -sh /var/lib/docker/containers/*/*-json.log | sort -rh | head -10
```

### Tip 7: 리소스 제한

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                                    | 원인                        | 해결 방법                                                    |
|-----------------------------------------|-----------------------------|--------------------------------------------------------------|
| `permission denied` (docker 명령)       | docker 그룹 미적용          | `sudo usermod -aG docker $USER` 후 재로그인                  |
| `port is already allocated`             | 호스트 포트 충돌            | `ss -tlnp \| grep PORT` 로 점유 프로세스 확인                |
| 컨테이너가 즉시 종료됨                  | 포그라운드 프로세스 없음    | `docker logs CONTAINER` 로 오류 확인                         |
| `no space left on device`               | Docker 디스크 가득 참       | `docker system prune -a --volumes`                           |
| DB 컨테이너 접속 불가 (앱 시작 직후)   | DB 초기화 미완료            | `healthcheck` + `condition: service_healthy` 적용            |
| 볼륨 데이터 유지 안 됨                  | `down -v` 사용              | `-v` 없이 `down` 사용, Named Volume 확인                     |
| RHEL: 볼륨 마운트 `permission denied`   | SELinux 컨텍스트 불일치     | 볼륨 경로에 `:z` 또는 `:Z` 추가                              |
| `Cannot connect to the Docker daemon`   | docker 서비스 미실행        | `sudo systemctl start docker`                                |

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

컨테이너에 실제 MAC 주소를 부여하여 물리 네트워크에 직접 연결합니다.
외부 PC에서 컨테이너 IP로 직접 접속이 필요할 때 사용합니다.

### 개념

```
물리 스위치 (10.200.101.1)
    │
    eth0 (호스트 IP: 10.200.90.155)
    │
    macvlan
    ├── container-a  10.200.101.151  ← 외부 PC에서 직접 접속 가능
    ├── container-b  10.200.101.152
    └── container-c  10.200.101.153
```

⚠️ macvlan 제약: 호스트 → 컨테이너 직접 통신 불가 (macvlan 특성). 외부 PC → 컨테이너는 가능합니다.

### Hyper-V 사전 설정

macvlan은 MAC spoofing이 필요합니다. Hyper-V 호스트에서 실행합니다:

```powershell
# MAC spoofing 활성화 (Hyper-V 호스트에서 실행)
Get-VMNetworkAdapter -VMName "VM이름" | Set-VMNetworkAdapter -MacAddressSpoofing On

# 확인
Get-VMNetworkAdapter -VMName "VM이름" | Select MacAddressSpoofing
```

### compose.yml 설정

```yaml
services:
  app:
    image: myapp
    networks:
      macvlan_net:
        ipv4_address: 10.200.101.151

networks:
  macvlan_net:
    driver: macvlan
    driver_opts:
      parent: eth0          # 호스트 물리 인터페이스
    ipam:
      config:
        - subnet: 10.200.101.0/24
          gateway: 10.200.101.1
          ip_range: 10.200.101.144/29   # 컨테이너 할당 범위 (network address 기준)
```

#### ip_range 계산

`ip_range`는 CIDR 네트워크 주소 기준이어야 합니다.

| 원하는 범위          | ip_range              |
|----------------------|-----------------------|
| .151 ~ .158 (8개)    | 10.200.101.144/29     |
| .161 ~ .174 (16개)   | 10.200.101.160/28     |
| .151 ~ .166 (16개)   | 10.200.101.144/28     |

### 호스트 → 컨테이너 통신 (선택)

macvlan 특성상 호스트에서 컨테이너로 직접 통신이 안 됩니다.
필요하면 macvlan 인터페이스를 호스트에 추가합니다:

```bash
# 호스트에 macvlan 인터페이스 추가 (재부팅 시 사라짐)
sudo ip link add macvlan0 link eth0 type macvlan mode bridge
sudo ip addr add 10.200.101.200/24 dev macvlan0
sudo ip link set macvlan0 up

# 영구 적용 (/etc/network/interfaces 또는 netplan)
```

### bridge vs macvlan 비교

| 항목              | bridge                        | macvlan                        |
|-------------------|-------------------------------|--------------------------------|
| 외부 접속         | 포트 포워딩 필요 (`ports:`)   | 컨테이너 IP 직접 접속          |
| 호스트→컨테이너   | ✅ 가능                       | ❌ 기본 불가 (별도 설정 필요)  |
| 인터넷 아웃바운드 | 호스트 NAT 경유               | 스위치/라우터에서 직접 허용    |
| Hyper-V 설정      | 불필요                        | MAC spoofing 활성화 필요       |
| 사용 사례         | 개발/테스트 환경              | 사내 네트워크 직접 노출        |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Docker Documentation: [Install Docker Engine](https://docs.docker.com/engine/install/) — ★★★☆☆
- Docker Documentation: [Docker Compose](https://docs.docker.com/compose/) — ★★★☆☆
- Docker Documentation: [Compose file reference](https://docs.docker.com/reference/compose-file/) — ★★★☆☆

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

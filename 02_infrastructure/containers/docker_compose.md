# Docker Compose

여러 컨테이너로 이루어진 서비스를 `compose.yaml` 파일 하나에 정의하고, 명령 하나로 만들고 지우는 도구입니다. 이 문서만으로 설치 → 첫 프로젝트 실행 → 검증까지 따라 할 수 있게 썼습니다. Docker Engine 설치, 이미지, Docker 네트워크의 상세는 [함께 보기](#함께-보기)의 문서에서 다룹니다.

- 기준 판: Docker Compose v5.8.0(2026-11-17 release)
- 예제 시험: 2026-11-23, Docker Engine 29.8.1과 Compose v5.5.1에서 3절 예제를 실행하고 9절 검증 명령의 결과를 확인

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. 첫 프로젝트](#3-첫-프로젝트)                                   |
| [4. compose.yaml 구조](#4-composeyaml-구조) / [5. 주요 명령](#5-주요-명령) / [6. 변수와 .env](#6-변수와-env) |
| [7. 여러 환경 구성](#7-여러-환경-구성) / [8. 운영 설정](#8-운영-설정) / [9. 검증](#9-검증)                   |
| [10. 트러블슈팅](#10-트러블슈팅) / [함께 보기](#함께-보기) / [참고 자료](#참고-자료)                         |

---

## 1. 개요

Compose는 컨테이너 여러 개와 그 사이의 네트워크·볼륨을 하나의 "프로젝트"로 묶어 관리합니다.

| 항목          | 내용                                                                                          |
|---------------|-----------------------------------------------------------------------------------------------|
| 명령 형태     | Docker CLI 플러그인 `docker compose`(띄어 씀). 옛 Python판 `docker-compose`(v1)는 지원 끝남   |
| 설정 파일     | `compose.yaml`(권장), `compose.yml`, `docker-compose.yaml`, `docker-compose.yml` 순서로 찾음  |
| 프로젝트 이름 | 기본은 디렉터리 이름. 파일의 `name:` 또는 `-p` 옵션으로 지정                                  |
| 기본 네트워크 | 프로젝트마다 `<프로젝트>_default` bridge 네트워크를 만들고, 서비스 이름으로 서로 찾을 수 있음 |
| `version:` 키 | 더 이상 쓰지 않음. 남아 있으면 경고만 내고 무시                                               |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

### 2-1. 사전 조건

Docker Engine이 설치되어 있고 데몬이 실행 중이어야 합니다.

```bash
docker version          # Client와 Server가 모두 출력되어야 함
```

Server 부분이 나오지 않으면 Engine 설치부터 합니다([함께 보기](#함께-보기)의 Docker 설치 문서). Windows·macOS의 Docker Desktop에는 Compose가 들어 있어 2-2를 건너뜁니다.

### 2-2. 패키지로 설치 (권장)

Docker 공식 패키지 저장소를 등록해 Engine을 설치했다면 같은 저장소에서 플러그인을 설치합니다.

```bash
# Ubuntu / Debian
sudo apt-get update
sudo apt-get install -y docker-compose-plugin

# RHEL / Rocky / AlmaLinux
sudo dnf install -y docker-compose-plugin
```

패키지로 설치하면 이후 `apt upgrade`·`dnf upgrade`로 함께 갱신됩니다.

### 2-3. 직접 내려받아 설치 (저장소를 쓸 수 없을 때)

release 파일을 사용자 플러그인 디렉터리에 둡니다. 판 번호와 CPU 종류(`x86_64`, `aarch64`)는 환경에 맞게 바꿉니다.

```bash
VER=v5.8.0
ARCH=x86_64
DEST=${DOCKER_CONFIG:-$HOME/.docker}/cli-plugins
mkdir -p "$DEST"
cd "$DEST"
curl -fSLO "https://github.com/docker/compose/releases/download/${VER}/docker-compose-linux-${ARCH}"
curl -fSLO "https://github.com/docker/compose/releases/download/${VER}/docker-compose-linux-${ARCH}.sha256"
sha256sum -c "docker-compose-linux-${ARCH}.sha256"   # OK가 나와야 함
mv "docker-compose-linux-${ARCH}" docker-compose
chmod +x docker-compose
```

모든 사용자가 쓰게 하려면 `/usr/local/lib/docker/cli-plugins/`에 둡니다. 이 방식은 자동 갱신이 없으므로 새 판이 나오면 같은 절차를 반복합니다.

### 2-4. 설치 확인

```bash
docker compose version
# Docker Compose version v5.8.0
```

`docker: 'compose' is not a docker command`가 나오면 플러그인 파일 위치와 실행 권한을 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 첫 프로젝트

웹 서버(nginx)와 DB(PostgreSQL) 두 서비스를 띄우고, DB가 준비된 뒤에 웹이 시작되게 합니다.

### 3-1. 파일 만들기

```bash
mkdir -p compose-demo/html
cd compose-demo
echo '<h1>compose demo</h1>' > html/index.html
```

`.env` — 비밀번호처럼 Git에 올리지 않을 값을 둡니다.

```bash
WEB_PORT=8080
POSTGRES_PASSWORD=<PASSWORD>                 # 실제 비밀번호로 바꿈
```

`compose.yaml`

```yaml
name: compose-demo

services:
  web:
    image: nginx:1.29-alpine
    ports:
      - "127.0.0.1:${WEB_PORT:-8080}:80"      # 호스트 자신에서만 접속
    volumes:
      - ./html:/usr/share/nginx/html:ro       # bind mount, 읽기 전용
    depends_on:
      db:
        condition: service_healthy            # db가 healthy가 된 뒤 시작
    restart: unless-stopped

  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD in .env}
    volumes:
      - db_data:/var/lib/postgresql/data      # named volume
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 10s
    restart: unless-stopped

volumes:
  db_data:
```

```bash
printf '.env\n' >> .gitignore
```

### 3-2. 실행과 확인

```bash
docker compose config --quiet     # 문법·변수 오류가 없으면 아무것도 출력하지 않음
docker compose up -d --wait       # 모든 서비스가 running/healthy가 될 때까지 기다림
docker compose ps                 # db는 (healthy), web은 Up
curl http://127.0.0.1:8080/       # <h1>compose demo</h1>
docker compose exec web ping -c 1 db   # 서비스 이름 db가 IP로 바뀌는지 확인
```

### 3-3. 정리

```bash
docker compose down       # 컨테이너와 네트워크 삭제, 볼륨 db_data는 남음
docker compose down -v    # 볼륨까지 삭제 (DB 데이터가 지워짐)
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. compose.yaml 구조

### 최상위 키

| 키         | 용도                                             |
|------------|--------------------------------------------------|
| `name`     | 프로젝트 이름                                    |
| `services` | 실행할 컨테이너 정의 (필수)                      |
| `volumes`  | named volume 선언                                |
| `networks` | 기본 네트워크 대신 쓸 네트워크 선언              |
| `configs`  | 설정 파일을 컨테이너에 넣을 때                   |
| `secrets`  | 비밀 값을 파일로 넣을 때 (`/run/secrets/<이름>`) |

### 서비스에서 자주 쓰는 키

| 키                 | 용도                                                                   |
|--------------------|------------------------------------------------------------------------|
| `image`            | 사용할 이미지. 태그를 고정 (8-3)                                       |
| `build`            | Dockerfile로 이미지를 만들 때 경로 지정                                |
| `ports`            | `"호스트IP:호스트포트:컨테이너포트"`. 호스트IP를 빼면 모든 주소에 열림 |
| `volumes`          | named volume 또는 bind mount                                           |
| `environment`      | 환경 변수 직접 지정                                                    |
| `env_file`         | 환경 변수를 파일에서 읽어 컨테이너에 전달                              |
| `depends_on`       | 시작 순서. `condition: service_healthy`로 준비 완료까지 대기           |
| `healthcheck`      | 컨테이너 안에서 상태 확인 명령 실행                                    |
| `restart`          | `no`, `always`, `on-failure`, `unless-stopped`                         |
| `profiles`         | 지정한 profile을 켤 때만 시작 (7-3)                                    |
| `deploy.resources` | CPU·메모리 제한 (8-5)                                                  |
| `logging`          | 로그 드라이버와 크기 제한 (8-4)                                        |

### named volume과 bind mount

| 항목      | named volume                               | bind mount                        |
|-----------|--------------------------------------------|-----------------------------------|
| 표기      | `db_data:/var/lib/postgresql/data`         | `./html:/usr/share/nginx/html`    |
| 저장 위치 | Docker가 관리 (`/var/lib/docker/volumes/`) | 호스트의 지정 경로                |
| 권장 용도 | DB 데이터, 영구 저장소                     | 설정 파일, 개발 중 소스 코드      |
| SELinux   | 자동 처리                                  | `:z`(공유)·`:Z`(전용) 레이블 필요 |
| 삭제      | `docker compose down -v`에서 함께 삭제     | 호스트 파일은 남음                |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 주요 명령

모든 명령은 `compose.yaml`이 있는 디렉터리에서 실행합니다. 다른 위치에서는 `-f <파일>` 또는 `--project-directory <디렉터리>`를 붙입니다.

| 목적        | 명령                                             | 설명                                                  |
|-------------|--------------------------------------------------|-------------------------------------------------------|
| 시작        | `docker compose up -d`                           | 백그라운드 실행. 이미지가 없으면 pull                 |
|             | `docker compose up -d --wait`                    | running/healthy가 될 때까지 기다림                    |
|             | `docker compose up -d --build`                   | 이미지를 다시 빌드한 뒤 실행                          |
| 중지·삭제   | `docker compose stop [서비스]`                   | 컨테이너 중지 (삭제하지 않음)                         |
|             | `docker compose start [서비스]`                  | 중지한 컨테이너 다시 시작                             |
|             | `docker compose restart [서비스]`                | 재시작 (설정 변경은 반영 안 됨)                       |
|             | `docker compose down`                            | 컨테이너·네트워크 삭제                                |
|             | `docker compose down -v`                         | 이 프로젝트의 named·익명 볼륨까지 삭제                |
|             | `docker compose rm -s -v <서비스>`               | 서비스 하나의 컨테이너를 멈추고 익명 볼륨과 함께 삭제 |
| 상태        | `docker compose ps`                              | 서비스 상태와 health                                  |
|             | `docker compose top`                             | 서비스별 프로세스                                     |
|             | `docker compose images`                          | 서비스별 이미지                                       |
| 로그        | `docker compose logs -f [서비스]`                | 실시간 로그                                           |
| 접속        | `docker compose exec <서비스> sh`                | 실행 중인 컨테이너에 셸 접속                          |
|             | `docker compose run --rm <서비스> <명령>`        | 새 컨테이너로 한 번 실행 후 삭제                      |
| 이미지      | `docker compose pull`                            | 정의된 이미지 내려받기                                |
|             | `docker compose build [--no-cache]`              | `build:`가 있는 서비스 빌드                           |
| 설정 확인   | `docker compose config`                          | 변수 치환·파일 병합 결과 출력                         |
|             | `docker compose config --services`               | 서비스 이름 목록                                      |
| 다시 만들기 | `docker compose up -d --force-recreate [서비스]` | 설정 변경이 없어도 컨테이너를 새로 만듦               |
| 수 조정     | `docker compose up -d --scale <서비스>=3`        | 같은 서비스 컨테이너 수 조정 (고정 포트가 없을 때)    |

`compose.yaml`을 고친 뒤에는 `restart`가 아니라 `up -d`를 다시 실행해야 바뀐 서비스만 새로 만들어집니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 변수와 .env

### 6-1. 두 종류의 환경 변수

| 구분               | 어디에 쓰이나                    | 지정 방법                                |
|--------------------|----------------------------------|------------------------------------------|
| 치환 변수 `${VAR}` | `compose.yaml` 안의 값을 바꿀 때 | 셸 환경 변수, 프로젝트 디렉터리의 `.env` |
| 컨테이너 환경 변수 | 컨테이너 안 프로세스가 읽음      | `environment:`, `env_file:`              |

`.env`는 치환에만 쓰이고, 그 자체로 컨테이너에 전달되지 않습니다. 컨테이너에 넘기려면 `environment:`에서 `${VAR}`로 참조하거나 `env_file: .env`를 지정합니다.

### 6-2. 치환 문법

| 표기             | 뜻                                    |
|------------------|---------------------------------------|
| `${VAR}`         | 값. 없으면 빈 문자열과 경고           |
| `${VAR:-기본값}` | 없거나 비어 있으면 기본값             |
| `${VAR:?메시지}` | 없거나 비어 있으면 메시지를 내고 실패 |
| `$$`             | `$` 문자 그대로 (치환하지 않음)       |

우선순위는 셸 환경 변수가 `.env`보다 높습니다. 최종 값은 `docker compose config`로 확인합니다.

```yaml
services:
  app:
    env_file: .env                    # 파일 내용을 컨테이너 환경 변수로
    environment:
      DB_HOST: db                     # 직접 지정
      DB_PASSWORD: ${DB_PASSWORD}     # 치환 변수 참조
```

### 6-3. 비밀 값 다루기

- `.env`는 `.gitignore`에 넣고, 저장소에는 값 없는 `.env.example`만 둡니다.
- `docker compose config`의 출력에는 치환된 비밀 값이 그대로 보이므로 로그·이슈에 붙이지 않습니다.
- 환경 변수는 `docker inspect`로 보입니다. 더 감춰야 하면 `secrets:`로 파일을 넣고, 이미지가 `*_FILE` 변수(예: `POSTGRES_PASSWORD_FILE`)를 지원하는지 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 여러 환경 구성

### 7-1. override 파일

`compose.override.yaml`이 있으면 `docker compose up` 때 `compose.yaml` 위에 자동으로 병합됩니다. 개발용 설정을 여기에 둡니다.

### 7-2. 파일 직접 지정

```bash
docker compose -f compose.yaml -f compose.prod.yaml up -d   # 뒤 파일이 앞 파일을 덮어씀
docker compose -f compose.yaml -f compose.prod.yaml config  # 병합 결과 확인
```

```yaml
# compose.prod.yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 1G
    logging:
      driver: json-file
      options:
        max-size: "100m"
        max-file: "3"
```

`-f`를 지정하면 `compose.override.yaml`은 자동 병합되지 않습니다.

### 7-3. profile로 선택 서비스 켜기

```yaml
services:
  web:
    image: nginx:1.29-alpine          # profile 없음: 항상 시작
  adminer:
    image: adminer:5
    profiles: ["debug"]               # --profile debug 일 때만 시작
```

```bash
docker compose --profile debug up -d
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 운영 설정

### 8-1. healthcheck로 시작 순서 보장

`depends_on`에 서비스 이름만 쓰면 "컨테이너가 시작됨"까지만 기다립니다. DB가 연결을 받을 준비가 됐는지는 보장하지 않으므로 3절처럼 `healthcheck`와 `condition: service_healthy`를 함께 씁니다.

| 항목           | 뜻                                               |
|----------------|--------------------------------------------------|
| `test`         | 성공(종료 코드 0)이면 healthy                    |
| `interval`     | 확인 간격                                        |
| `timeout`      | 한 번 확인의 제한 시간                           |
| `retries`      | 연속 실패 몇 번에 unhealthy로 볼지               |
| `start_period` | 시작 직후 이 시간 동안의 실패는 횟수에 넣지 않음 |

### 8-2. 내부 서비스는 외부에 열지 않기

같은 프로젝트의 서비스끼리는 기본 네트워크에서 서비스 이름으로 통신하므로, DB처럼 내부에서만 쓰는 서비스에는 `ports:`가 필요 없습니다. 호스트에서 직접 접속해야 하면 `127.0.0.1:`을 붙여 호스트 자신에서만 열리게 합니다.

```yaml
services:
  db:
    ports:
      - "127.0.0.1:5432:5432"   # 호스트 자신만 접속
  web:
    ports:
      - "80:80"                 # 모든 주소에 열림
```

Docker가 만드는 방화벽 규칙은 ufw·firewalld 규칙보다 먼저 적용될 수 있으므로, 포트를 열지 않는 것이 가장 확실합니다.

### 8-3. 이미지 태그 고정

```yaml
image: postgres:latest      # 피함: 다음 pull에서 메이저 판이 바뀔 수 있음
image: postgres:17.6-alpine # 권장: 판 번호까지 고정
```

### 8-4. 로그 크기 제한

기본 `json-file` 드라이버는 크기 제한이 없어 디스크를 채울 수 있습니다.

```yaml
services:
  web:
    logging:
      driver: json-file
      options:
        max-size: "50m"
        max-file: "5"
```

### 8-5. 리소스 제한

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
        reservations:
          memory: 128M
```

### 8-6. 서비스 하나만 갱신

```bash
docker compose pull web
docker compose up -d --no-deps web   # web만 다시 만듦 (만드는 동안 web은 잠깐 끊김)
docker image prune -f                # 쓰지 않는 옛 이미지 정리
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 검증

새 프로젝트를 올리거나 설정을 바꾼 뒤 아래 순서로 확인합니다. 3절 예제 기준의 기대 결과입니다.

| 순서 | 확인 내용           | 명령                                   | 기대 결과                                  |
|------|---------------------|----------------------------------------|--------------------------------------------|
| 1    | 설치                | `docker compose version`               | 판 번호 출력                               |
| 2    | 설정 문법·변수      | `docker compose config --quiet`        | 출력 없음, 종료 코드 0                     |
| 3    | 서비스 목록         | `docker compose config --services`     | `db`, `web`                                |
| 4    | 기동                | `docker compose up -d --wait`          | 모든 컨테이너 Healthy 또는 Started 뒤 종료 |
| 5    | 상태                | `docker compose ps`                    | db `(healthy)`, web `Up`                   |
| 6    | 서비스 응답         | `curl http://127.0.0.1:8080/`          | `<h1>compose demo</h1>`                    |
| 7    | 서비스 간 이름 해석 | `docker compose exec web ping -c 1 db` | db의 내부 IP로 응답                        |
| 8    | 포트 노출 범위      | `ss -tlnp \| grep 8080`                | `127.0.0.1:8080`만 열림                    |
| 9    | 오류 로그           | `docker compose logs --tail 50`        | 반복 재시작·오류 없음                      |
| 10   | 정리                | `docker compose down`                  | 컨테이너·네트워크 삭제, 볼륨 유지          |

변수가 빠졌을 때 2번이 실패하는지도 확인해 두면 좋습니다. 3절 예제에서 `.env`를 치우면 `required variable POSTGRES_PASSWORD is missing a value`로 멈춥니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 트러블슈팅

| 증상                                        | 원인                                    | 해결 방법                                          |
|---------------------------------------------|-----------------------------------------|----------------------------------------------------|
| `docker: 'compose' is not a docker command` | 플러그인 미설치 또는 위치·권한 문제     | 2-2 또는 2-3으로 설치, 실행 권한 확인              |
| `no configuration file provided: not found` | 다른 디렉터리에서 실행                  | 파일이 있는 곳에서 실행하거나 `-f` 지정            |
| 앱이 시작 직후 DB 연결 실패                 | DB 초기화 전에 앱 시작                  | 8-1의 `healthcheck` + `condition: service_healthy` |
| `compose.yaml`을 고쳤는데 반영 안 됨        | `restart`만 실행                        | `docker compose up -d` 다시 실행                   |
| 데이터가 사라짐                             | `down -v`로 볼륨 삭제                   | `-v` 없이 `down`, 데이터는 named volume에 저장     |
| 변수 값이 비어 있다는 경고                  | `.env` 위치가 프로젝트 디렉터리가 아님  | `docker compose config`로 치환 결과 확인           |
| `port is already allocated`                 | 호스트 포트를 다른 프로세스가 사용      | `ss -tlnp`로 확인 후 포트 변경                     |
| 다른 프로젝트 컨테이너와 이름이 섞임        | 같은 디렉터리 이름 → 같은 프로젝트 이름 | `name:` 또는 `-p`로 프로젝트 이름 지정             |
| RHEL에서 bind mount `permission denied`     | SELinux 레이블 불일치                   | 볼륨 뒤에 `:z` 또는 `:Z` 추가                      |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Docker 설치와 초기 설정](./docker_install_and_compose.md) — Engine 설치, daemon.json, 방화벽
- [Docker 가이드](./docker.md) — 이미지, 컨테이너, 볼륨, cgroup
- [Docker 명령 치트시트](./docker_compose_cheatsheet.md) — docker 명령 한 줄 정리
- [Docker 네트워크](./docker_network.md) — bridge·macvlan, 포트 공개, `networks:` 설정
- [Dockerfile 작성과 빌드](./dockerfile_best_practices.md) — `build:`에 쓰는 이미지 만들기
- [Podman](./podman.md) — `podman compose`와 rootless 컨테이너
- [YAML 문법](../iac/yaml_syntax.md) — 들여쓰기, 따옴표, 앵커

---

## 참고 자료

- Docker Documentation: [Docker Compose](https://docs.docker.com/compose/) — ★★★☆☆
- Docker Documentation: [Install the Docker Compose plugin](https://docs.docker.com/compose/install/linux/) — ★★★☆☆
- Docker Documentation: [Compose file reference](https://docs.docker.com/reference/compose-file/) — ★★★☆☆
- Docker Documentation: [Interpolation](https://docs.docker.com/reference/compose-file/interpolation/) — ★★★☆☆
- Docker Documentation: [Control startup order](https://docs.docker.com/compose/how-tos/startup-order/) — ★★★☆☆
- Docker Documentation: [docker compose up](https://docs.docker.com/reference/cli/docker/compose/up/) — ★★★☆☆
- Docker Documentation: [Configure logging drivers](https://docs.docker.com/engine/logging/configure/) — ★★★☆☆
- Docker Documentation: [Migrate to Compose v2](https://docs.docker.com/compose/releases/migrate/) — ★★★☆☆
- GitHub: [docker/compose releases](https://github.com/docker/compose/releases) — v5.8.0 확인 2026-11-23 — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-23

**마지막 업데이트**: 2026-11-23

© 2026 siasia86. Licensed under CC BY 4.0.

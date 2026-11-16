# Dockerfile 작성과 이미지 빌드
<!-- reference: _reference/docker_official_notes.md -->

Dockerfile은 컨테이너 이미지를 만드는 절차를 적은 텍스트 파일입니다.
이 문서는 [Docker 가이드](./docker.md)의 기본 지시어 설명 다음 단계로, 이미지를 작고 재현 가능하며 안전하게 만드는 작성 방법과 BuildKit 빌드 기능을 정리합니다.

## 목차

| 섹션                                                                                                                                   |
|----------------------------------------------------------------------------------------------------------------------------------------|
| [1. 빌드 구조와 BuildKit](#1-빌드-구조와-buildkit) / [2. 빌드 컨텍스트와 .dockerignore](#2-빌드-컨텍스트와-dockerignore)               |
| [3. 베이스 이미지 선택](#3-베이스-이미지-선택) / [4. 레이어와 캐시](#4-레이어와-캐시) / [5. 멀티 스테이지 빌드](#5-멀티-스테이지-빌드) |
| [6. 지시어별 작성 기준](#6-지시어별-작성-기준) / [7. 빌드 비밀값 다루기](#7-빌드-비밀값-다루기)                                        |
| [8. 보안 기준](#8-보안-기준) / [9. 빌드 명령과 외부 캐시](#9-빌드-명령과-외부-캐시) / [10. 검토 점검표](#10-검토-점검표)               |

---

## 1. 빌드 구조와 BuildKit

BuildKit은 현재 Docker Engine의 기본 빌드 백엔드입니다. `docker build`는 클라이언트가 빌드 컨텍스트(빌드에 쓰는 파일 묶음)를 BuildKit으로 보내고, BuildKit이 Dockerfile을 해석해 레이어를 만듭니다. `docker buildx`는 같은 BuildKit을 여러 빌더·여러 플랫폼으로 쓰는 확장 명령입니다.

```text
 docker build / docker buildx build
            |
            |  build context (files - .dockerignore)
            v
 +--------------------------------------------+
 | BuildKit                                   |
 |  Dockerfile frontend (# syntax=...)        |
 |  -> stage graph -> parallel steps          |
 |  -> layer cache (local / registry / gha)   |
 +--------------------------------------------+
            |
            v
   image (local store) / registry push / tar
```

Dockerfile 맨 위에 문법 지시어를 두면 BuildKit이 빌드 전에 최신 안정판 Dockerfile 문법을 내려받아 씁니다. `RUN --mount`, `COPY --link` 같은 기능을 안정적으로 쓰려면 넣어 둡니다.

```dockerfile
# syntax=docker/dockerfile:1
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 빌드 컨텍스트와 .dockerignore

빌드 컨텍스트에 불필요한 파일이 많으면 전송이 느려지고, `COPY . .` 한 줄로 `.git`·`.env`·로그가 이미지에 들어갈 수 있습니다. `.dockerignore`는 빌드 컨텍스트 루트에 두며, 걸러진 파일은 빌더로 보내지지 않습니다.

```text
# .dockerignore
.git
.gitignore
**/.env
**/*.pem
**/node_modules
**/__pycache__
*.log
dist
Dockerfile*
!README.md
```

| 규칙              | 설명                                                                       |
|-------------------|----------------------------------------------------------------------------|
| 문법              | Go `filepath.Match` 규칙. 앞뒤 `/`는 무시됩니다                            |
| `**`              | 0개 이상 디렉터리와 일치                                                   |
| `!` 예외          | 앞에서 제외한 파일을 다시 포함. 마지막으로 일치한 줄이 결과를 정합니다     |
| `#`               | 첫 칸에서 시작하면 주석                                                    |
| Dockerfile별 파일 | `<Dockerfile 이름>.dockerignore`를 같은 디렉터리에 두면 루트 파일보다 우선 |

🟡 `*.md`처럼 `**/` 없이 쓴 패턴은 루트에만 적용되고 하위 디렉터리 파일은 그대로 포함됩니다. 비밀 파일은 `**/` 패턴으로 막습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 베이스 이미지 선택

| 기준 | 설명                                                                            |
|------|---------------------------------------------------------------------------------|
| 출처 | Docker Official Images, Verified Publisher 등 신뢰할 수 있는 게시자             |
| 크기 | 필요한 것만 든 작은 이미지. 빌드용(full)과 실행용(slim·distroless 등)을 나눠 씀 |
| 고정 | tag는 바뀔 수 있으므로 재현성이 필요하면 `@sha256:` digest로 고정               |
| 갱신 | digest 고정 시 자동 갱신이 멈추므로 Dependabot·Renovate 같은 도구로 주기적 갱신 |
| libc | Alpine은 musl libc를 쓰므로 glibc 전제 바이너리·Python wheel 호환성을 확인      |

```dockerfile
# tag만 쓰면 같은 tag라도 내용이 바뀔 수 있음
FROM python:3.12-slim

# digest 고정: 항상 같은 이미지 (값은 예시 자리 표시자)
FROM python:3.12-slim@sha256:<DIGEST>
```

현재 이미지의 digest는 `docker buildx imagetools inspect python:3.12-slim` 또는 `docker image inspect --format '{{index .RepoDigests 0}}' python:3.12-slim`으로 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 레이어와 캐시

`RUN`, `COPY`, `ADD`는 각각 레이어를 만듭니다. BuildKit은 지시어와 입력 파일이 같으면 이전 결과를 재사용하고, 한 단계의 캐시가 깨지면 그 아래 단계는 모두 다시 실행합니다. 그래서 자주 바뀌지 않는 단계를 위에, 자주 바뀌는 단계를 아래에 둡니다.

```dockerfile
# 나쁜 순서: 소스 한 줄만 바뀌어도 npm install을 다시 실행
COPY . .
RUN npm ci

# 좋은 순서: 잠금 파일이 바뀔 때만 의존성 재설치
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build
```

### 캐시 마운트

`RUN --mount=type=cache`는 패키지 관리자 캐시 디렉터리를 빌드 사이에 유지합니다. 이미지에는 들어가지 않으므로 크기는 늘지 않습니다.

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# apt는 동시 빌드 충돌을 막기 위해 sharing=locked 사용
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends gcc
```

### 바인드 마운트

빌드 중에 잠깐만 필요한 파일은 `COPY` 대신 바인드 마운트로 읽습니다. 기본은 읽기 전용이고 결과물은 마운트 밖 경로에 써야 합니다.

```dockerfile
WORKDIR /build
RUN --mount=type=bind,target=. go build -o /app/server ./cmd/server
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 멀티 스테이지 빌드

멀티 스테이지 빌드는 한 Dockerfile에 `FROM`을 여러 번 써서 빌드 도구가 든 단계와 실행 단계를 나누는 방법입니다. 최종 이미지에는 마지막 단계(또는 `--target`으로 고른 단계)만 남습니다. 서로 의존하지 않는 단계는 BuildKit이 병렬로 실행합니다.

```dockerfile
# syntax=docker/dockerfile:1

ARG GO_VERSION=1.23

FROM golang:${GO_VERSION} AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download
COPY . .
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 go build -o /out/server ./cmd/server

FROM build AS test
RUN go test ./...

FROM gcr.io/distroless/static-debian12:nonroot AS runtime
COPY --from=build /out/server /server
USER nonroot:nonroot
ENTRYPOINT ["/server"]
```

```bash
docker build --target test .            # 테스트 단계까지만 빌드
docker build -t app:1.0 .               # 마지막 단계(runtime) 빌드
```

| 기법                   | 설명                                                      |
|------------------------|-----------------------------------------------------------|
| `AS <이름>`            | 단계에 이름 부여. `COPY --from=<이름>`으로 파일을 가져옴  |
| `COPY --from=<이미지>` | 다른 이미지에서 파일만 복사(예: 정적 바이너리)            |
| `--target <단계>`      | 특정 단계까지만 빌드(테스트·디버그 이미지)                |
| 공통 단계              | 여러 단계가 쓰는 설정을 한 단계에 모아 재사용             |
| `FROM` 앞 `ARG`        | 단계 밖 변수. 단계 안에서 쓰려면 `ARG 이름`으로 다시 선언 |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 지시어별 작성 기준

| 지시어             | 기준                                                                                        |
|--------------------|---------------------------------------------------------------------------------------------|
| `RUN` (apt)        | `apt-get update`와 `install`을 한 `RUN`에 쓰고, 같은 `RUN`에서 `/var/lib/apt/lists/*` 삭제  |
| `RUN` (파이프)     | 파이프는 마지막 명령의 종료 코드만 봅니다. `set -o pipefail &&`를 앞에 붙임                 |
| 여러 줄 인자       | 패키지는 한 줄에 하나씩 알파벳 순으로 정렬해 diff 검토를 쉽게 함                            |
| `COPY` / `ADD`     | 일반 복사는 `COPY`. `ADD`는 원격 파일·Git 소스에 쓰고 `--checksum`으로 검증                 |
| `COPY --chown`     | 지정하지 않으면 복사된 파일 소유자는 UID/GID 0(root)                                        |
| `ENV`              | 레이어마다 남으므로 뒤에서 지워도 이전 레이어에 값이 남음. 임시 값은 한 `RUN` 안에서만 사용 |
| `WORKDIR`          | 절대 경로 사용. `RUN cd ...` 대신 사용                                                      |
| `ENTRYPOINT`/`CMD` | exec 형식(JSON 배열) 사용. 주 명령은 `ENTRYPOINT`, 기본 인자는 `CMD`                        |
| `USER`             | 서비스는 non-root로 실행. UID/GID를 명시                                                    |
| `EXPOSE`           | 앱이 듣는 포트를 문서화하는 용도. 실제 공개는 실행할 때 `-p`로 정함                         |
| `LABEL`            | 버전·출처·라이선스 메타데이터. 공백이 있는 값은 따옴표로 감쌈                               |

```dockerfile
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
    && rm -rf /var/lib/apt/lists/*

# 원격 파일은 checksum으로 검증 (값은 자리 표시자)
ADD --checksum=sha256:<SHA256> https://example.com/tool.tar.gz /tmp/tool.tar.gz
```

### exec 형식과 신호

shell 형식(`CMD node server.js`)은 `/bin/sh -c`로 실행되므로 앱이 PID 1이 아니고, `docker stop`의 SIGTERM을 받지 못해 제한 시간 뒤 강제 종료(SIGKILL)될 수 있습니다. 시작 스크립트를 쓰면 마지막 줄에서 `exec "$@"`로 앱이 PID 1을 이어받게 합니다.

```dockerfile
COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["node", "server.js"]
```

```bash
#!/bin/sh
# docker-entrypoint.sh
set -e
# 실행 전 준비 작업 (설정 파일 생성 등)
exec "$@"
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 빌드 비밀값 다루기

`ARG`와 `ENV`에 넣은 값은 이미지 메타데이터·레이어에 남아 이미지를 받은 누구나 읽을 수 있습니다. 비밀값은 빌드 비밀 마운트로 해당 `RUN` 동안에만 노출합니다.

```bash
# 파일에서 전달
docker build --secret id=npmrc,src=$HOME/.npmrc .

# 환경변수에서 전달
docker build --secret id=api_token,env=API_TOKEN .

# SSH 에이전트 전달 (비공개 Git 저장소 clone)
docker buildx build --ssh default .
```

```dockerfile
# 기본 경로 /run/secrets/<id>에 파일로 마운트
RUN --mount=type=secret,id=api_token \
    TOKEN="$(cat /run/secrets/api_token)" ./fetch-private-deps.sh

# 원하는 경로에 마운트
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci

# 환경변수로 노출
RUN --mount=type=secret,id=api_token,env=API_TOKEN ./fetch-private-deps.sh

# SSH 에이전트 소켓 사용
RUN --mount=type=ssh git clone git@git.example.com:team/private-lib.git
```

🟡 비밀값을 `RUN` 안에서 파일로 저장하거나 `echo`로 출력하면 레이어나 빌드 로그에 남습니다. 같은 `RUN` 안에서 쓰고 끝내며, 빌드 로그(`--progress=plain`)를 공유하기 전에 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 보안 기준

| 항목        | 기준                                                                          |
|-------------|-------------------------------------------------------------------------------|
| 실행 사용자 | `USER`로 non-root 지정. `sudo`는 넣지 않고, 꼭 필요하면 `gosu` 같은 도구 검토 |
| 최소 패키지 | 편집기·컴파일러·디버그 도구를 실행 이미지에 넣지 않음(멀티 스테이지로 분리)   |
| 비밀값      | `ARG`·`ENV`·`COPY`로 넣지 않고 7절의 secret 마운트 사용                       |
| 베이스 갱신 | `--pull`로 새 베이스를 받아 주기적으로 다시 빌드                              |
| 취약점 검사 | 빌드 뒤 이미지 스캔(예: [Trivy](../../04_security/hardening/trivy_guide.md))  |
| 출처 증명   | 필요한 경우 SBOM(구성 요소 목록)·provenance(빌드 출처) 첨부 검토              |

```dockerfile
# Debian 계열에서 고정 UID/GID 사용자 만들기
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-log-init --create-home app
USER 10001:10001
```

`useradd --no-log-init`은 큰 UID를 쓸 때 `/var/log/lastlog`·`faillog`가 커지는 문제를 피하려는 옵션입니다. Kubernetes에서 `runAsNonRoot`를 검사할 때는 이름보다 숫자 UID로 `USER`를 지정해야 판정이 확실합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 빌드 명령과 외부 캐시

```bash
# 기본 빌드와 태그
docker build -t registry.example.com/team/app:1.0 .

# 베이스 이미지를 새로 받고 캐시 없이 전체 재빌드
docker build --pull --no-cache -t registry.example.com/team/app:1.0 .

# 다른 경로의 Dockerfile 사용
docker build -f build/Dockerfile -t app:dev .

# 단계별 출력 전체 보기 (문제 분석용)
docker build --progress=plain .

# 이미지 레이어별 크기 확인
docker history registry.example.com/team/app:1.0
```

CI처럼 매번 새 빌더에서 빌드하면 로컬 캐시가 없으므로 레지스트리에 캐시를 저장해 재사용합니다.

```bash
docker buildx build \
  --cache-to type=registry,ref=registry.example.com/team/app:buildcache,mode=max \
  --cache-from type=registry,ref=registry.example.com/team/app:buildcache \
  -t registry.example.com/team/app:1.0 --push .
```

| 옵션            | 설명                                                  |
|-----------------|-------------------------------------------------------|
| `--cache-to`    | 캐시 내보내기. `mode=max`는 중간 단계 레이어까지 저장 |
| `--cache-from`  | 캐시 가져오기                                         |
| `type=registry` | OCI 레지스트리 이미지로 캐시 저장                     |
| `--push`        | 빌드 결과를 레지스트리로 바로 push                    |

GitHub Actions에서는 `docker/build-push-action`의 `cache-from`·`cache-to` 입력으로 같은 설정을 씁니다([GitHub Actions](../cicd/github_actions.md)). GitLab CI의 이미지 빌드 방식은 [GitLab CI/CD](../cicd/gitlab_ci.md)를 참고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 검토 점검표

Dockerfile 변경을 검토할 때 아래 항목을 차례로 확인합니다.

- [ ] `.dockerignore`에 `.git`, `.env`, 키 파일, 빌드 산출물이 들어 있는가
- [ ] 베이스 이미지 출처가 신뢰할 수 있고, 운영 이미지는 tag 또는 digest가 고정되어 있는가
- [ ] 의존성 정의 파일을 먼저 복사하고 소스를 나중에 복사해 캐시가 유지되는가
- [ ] 빌드 도구가 실행 이미지에 남지 않도록 멀티 스테이지로 나뉘어 있는가
- [ ] `apt-get update`와 `install`이 한 `RUN`에 있고 목록 캐시를 지웠는가
- [ ] 파이프를 쓰는 `RUN`에 `set -o pipefail`이 있는가
- [ ] 비밀값이 `ARG`·`ENV`·`COPY`가 아니라 `--mount=type=secret`으로 전달되는가
- [ ] `USER`가 숫자 UID의 non-root 사용자로 지정되어 있는가
- [ ] `ENTRYPOINT`/`CMD`가 exec 형식이고 시작 스크립트는 `exec "$@"`로 끝나는가
- [ ] `ADD`로 원격 파일을 받으면 `--checksum`이 있는가
- [ ] 빌드 뒤 이미지 크기(`docker history`)와 취약점 검사 결과를 확인했는가

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Docker Build best practices: [docs.docker.com/build/building/best-practices](https://docs.docker.com/build/building/best-practices/) — ★★★☆☆ (확인일 2026-11-16)
- Dockerfile reference: [docs.docker.com/reference/dockerfile](https://docs.docker.com/reference/dockerfile/) — ★★★☆☆ (확인일 2026-11-16)
- Build context와 .dockerignore: [docs.docker.com/build/concepts/context](https://docs.docker.com/build/concepts/context/) — ★★★☆☆ (확인일 2026-11-16)
- Optimize cache usage: [docs.docker.com/build/cache/optimize](https://docs.docker.com/build/cache/optimize/) — ★★★☆☆ (확인일 2026-11-16)
- Build secrets: [docs.docker.com/build/building/secrets](https://docs.docker.com/build/building/secrets/) — ★★★☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.

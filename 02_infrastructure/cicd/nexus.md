# Nexus Repository
<!-- reference: _reference/nexus_official_notes.md -->

빌드 결과물(jar·whl·컨테이너 이미지 등)을 보관하고, 외부 패키지 저장소(Maven Central·PyPI·Docker Hub)를 대신 받아 캐시하는 저장소 관리자입니다. 이 문서만으로 Docker 설치 → 초기 설정 → 저장소 만들기 → 클라이언트 연결 → 백업·정리 → 검증까지 따라 할 수 있게 썼습니다.

- 기준 판: Sonatype Nexus Repository 3.98.3 Community Edition (2026-11-24 확인)
- 예제 시험: 2026-11-24, `sonatype/nexus3:latest`(3.98.3-01) 컨테이너로 확인. H2 단독 기동과 PostgreSQL 17 연결(2.2절 환경 변수, Compose 파일 자체는 미실행), 3절 초기 설정, 4.1~4.3절 저장소 생성, 5.1절 raw, pip 받기, Docker 올리기(crane), 6.1~6.2절 작업과 복원을 실행. Maven·twine·`docker login`, 클라우드 blob, LDAP, HTTPS 앞단은 시험하지 않았음

## 목차

| 섹션                                                                                                 |
|------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치](#2-설치) / [3. 초기 설정](#3-초기-설정)                               |
| [4. 저장소 만들기](#4-저장소-만들기) / [5. 클라이언트 연결](#5-클라이언트-연결) / [6. 운영](#6-운영) |
| [7. 검증](#7-검증) / [8. 트러블슈팅](#8-트러블슈팅) / [함께 보기](#함께-보기)                        |

---

## 1. 개요

저장소는 세 가지 유형을 조합합니다.

| 유형   | 역할                                      | 예                              |
|--------|-------------------------------------------|---------------------------------|
| hosted | 직접 올린 결과물을 보관                   | 사내 라이브러리, 빌드한 이미지  |
| proxy  | 외부 저장소를 대신 받아 캐시              | Maven Central, PyPI, Docker Hub |
| group  | 여러 저장소를 URL 하나로 묶음 (읽기 전용) | hosted + proxy를 한 주소로 제공 |

```text
빌드 서버 ──올리기──▶ hosted ─┐
                              ├─▶ group ◀──받기── 개발 PC·CI
외부 저장소 ◀──캐시── proxy ──┘
```

에디션은 무료 Community Edition(CE)과 유료 Pro·Pro+·Enterprise입니다.

| 항목              | Community Edition                                  | Pro 이상                      |
|-------------------|----------------------------------------------------|-------------------------------|
| 사용량 한도       | 컴포넌트 40,000개, 하루 요청 100,000건             | 사용량 기반 계약              |
| 한도 초과         | 두 기준 아래로 내려갈 때까지 새 컴포넌트 추가 중지 | -                             |
| HA·SSO(SAML/OIDC) | 없음                                               | 있음                          |
| blob 저장소       | 파일(NFS 포함)                                     | 파일, S3, Azure, Google Cloud |
| 정리 정책 REST    | 없음 (화면에서 설정)                               | 있음                          |

- DB는 내장 H2와 외부 PostgreSQL 중 하나입니다. H2는 하루 요청 200,000건 또는 컴포넌트 100,000개까지 지원하며, 공식 시스템 요구사항은 H2를 쓰는 컨테이너 배포를 지원하지 않는다고 적고 있습니다. 컨테이너로 운영하면 PostgreSQL을 씁니다.
- OrientDB는 3.71.0에서 지원이 끝났습니다. 3.70 이하에서 올리려면 먼저 H2나 PostgreSQL로 옮깁니다.
- 공식 최소 사양은 따로 없고, 가장 작은 권장 프로필이 4 vCPU·16GiB입니다. 디스크는 항상 4GB 이상 비워 둡니다(부족하면 DB가 읽기 전용이 됨).

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치

### 2.1 시험용 (H2)

```bash
docker volume create nexus-data
docker run -d --name nexus -p 8081:8081 \
  -e INSTALL4J_ADD_VM_PARAMS="-Xms2g -Xmx2g -XX:MaxDirectMemorySize=2g -Djava.util.prefs.userRoot=/nexus-data/javaprefs" \
  -v nexus-data:/nexus-data \
  sonatype/nexus3:3.98.3

# 기동 확인 (쓰기 가능하면 200)
until curl -fs -o /dev/null http://localhost:8081/service/rest/v1/status/writable; do sleep 5; done
```

- 데이터는 모두 `/nexus-data`에 있고, 컨테이너는 UID 200(`nexus`)으로 실행됩니다. 호스트 디렉터리를 붙이면 `chown -R 200:200`이 필요합니다.
- `INSTALL4J_ADD_VM_PARAMS`를 바꿀 때 `-Djava.util.prefs.userRoot=...`도 함께 적습니다(기본값을 덮어쓰기 때문). `-Xms`와 `-Xmx`는 같게 둡니다.
- 태그는 `latest` 대신 판 번호로 고정해야 업그레이드 시점을 직접 정할 수 있습니다.

### 2.2 운영용 (PostgreSQL, Compose)

PostgreSQL은 커뮤니티 지원 중인 판을 쓰고 `pg_trgm` 확장을 미리 만듭니다.

```yaml
# compose.yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_USER: nexus
      POSTGRES_DB: nexus
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets: [db_password]
    volumes:
      - db-data:/var/lib/postgresql/data
      - ./initdb:/docker-entrypoint-initdb.d:ro   # pg_trgm 생성 SQL
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "nexus", "-d", "nexus"]
      interval: 5s

  nexus:
    image: sonatype/nexus3:3.98.3
    depends_on:
      db: { condition: service_healthy }
    env_file: nexus-db.env          # 권한 600, 저장소에 올리지 않음
    environment:
      INSTALL4J_ADD_VM_PARAMS: "-Xms4g -Xmx4g -XX:MaxDirectMemorySize=4g -Djava.util.prefs.userRoot=/nexus-data/javaprefs"
    ports: ["127.0.0.1:8081:8081"]  # 앞단 리버스 프록시에서 HTTPS 종료
    volumes:
      - nexus-data:/nexus-data

secrets:
  db_password:
    file: ./db_password.txt

volumes:
  db-data:
  nexus-data:
```

```sql
-- initdb/01-pg_trgm.sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

```bash
# nexus-db.env (값은 예시, 비밀번호는 db_password.txt와 같게)
NEXUS_DATASTORE_NEXUS_JDBCURL=jdbc:postgresql://db:5432/nexus
NEXUS_DATASTORE_NEXUS_USERNAME=nexus
NEXUS_DATASTORE_NEXUS_PASSWORD=<DB_PASSWORD>
NEXUS_DATASTORE_NEXUS_ADVANCED=maximumPoolSize=200
```

```bash
chmod 600 nexus-db.env db_password.txt
docker compose up -d
docker compose logs nexus | grep -E 'edition|data store configuration'
# 기대: Starting nexus with edition COMMUNITY
#       Loaded 'nexus' data store configuration from environment-variables (postgresql)
```

DB 연결 설정은 환경 변수 → JVM 인수(`-Dnexus.datastore.nexus.*`) → `/nexus-data/etc/fabric/nexus-store.properties` 순으로 우선합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 초기 설정

### 3.1 관리자 비밀번호

처음 기동하면 `admin` 비밀번호가 데이터 볼륨의 `admin.password` 파일에 만들어집니다. 화면(`http://<호스트>:8081`)의 마법사나 REST로 바꾸며, 바꾸면 이 파일은 지워집니다.

```bash
docker exec nexus cat /nexus-data/admin.password; echo   # 초기 비밀번호
read -rs NEXUS_INIT; echo                                 # 위 값을 붙여 넣음
read -rs NEXUS_PASS; echo                                 # 새 비밀번호
printf '%s' "$NEXUS_PASS" | curl -fsS -u "admin:${NEXUS_INIT}" -X PUT \
  -H 'Content-Type: text/plain' --data-binary @- \
  http://localhost:8081/service/rest/v1/security/users/admin/change-password
unset NEXUS_INIT
```

- 이후 예제는 `NEXUS=http://localhost:8081`, `AUTH="admin:${NEXUS_PASS}"`를 씁니다. `curl -u`의 값은 프로세스 목록에 보일 수 있으므로 공용 서버에서는 `--netrc-file`이나 전용 계정의 사용자 토큰을 씁니다.
- 실제 작업에는 `admin` 대신 권한을 좁힌 계정(예: CI 올리기 전용)을 만들어 씁니다.

### 3.2 EULA 수락 (CE)

CE는 사용권 계약(EULA)을 수락하기 전에는 컴포넌트를 받거나 올릴 수 없습니다(403, "You must accept the End User License Agreement"). 화면 마법사에서 수락하거나, [계약 내용](https://links.sonatype.com/products/nxrm/ce-eula)을 읽은 뒤 REST로 수락합니다.

```bash
curl -fsS -u "$AUTH" $NEXUS/service/rest/v1/system/eula        # accepted: false 확인
curl -fsS -u "$AUTH" $NEXUS/service/rest/v1/system/eula \
  | sed 's/"accepted" : false/"accepted" : true/' \
  | curl -fsS -u "$AUTH" -H 'Content-Type: application/json' -d @- \
      -w '%{http_code}\n' $NEXUS/service/rest/v1/system/eula     # 204
```

### 3.3 익명 접근과 인증 영역

| 설정           | 기본값                       | 확인·변경                                         |
|----------------|------------------------------|---------------------------------------------------|
| 익명 접근      | 꺼짐 (`enabled: false`)      | `GET/PUT /service/rest/v1/security/anonymous`     |
| 활성 인증 영역 | `NexusAuthenticatingRealm`만 | `GET/PUT /service/rest/v1/security/realms/active` |

Docker 클라이언트가 토큰 인증을 쓰거나 익명 pull을 허용하려면 `DockerToken`(Docker Bearer Token Realm)을 켭니다. npm·NuGet 등도 각자의 토큰 영역이 있습니다(`.../realms/available`).

```bash
curl -fsS -u "$AUTH" -X PUT -H 'Content-Type: application/json' \
  -d '["NexusAuthenticatingRealm","DockerToken"]' \
  $NEXUS/service/rest/v1/security/realms/active
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 저장소 만들기

기본으로 Maven(`maven-releases`·`maven-snapshots`·`maven-central`·`maven-public`)과 NuGet 저장소가 만들어져 있습니다. 나머지는 화면(설정 → Repositories)이나 REST로 만듭니다. 형식별 JSON 필드는 `$NEXUS/service/rest/swagger.json`에서 확인합니다.

### 4.1 raw hosted (파일 보관)

```bash
curl -fsS -u "$AUTH" -H 'Content-Type: application/json' \
  -d '{"name":"raw-hosted","online":true,
       "storage":{"blobStoreName":"default","strictContentTypeValidation":true,"writePolicy":"allow_once"}}' \
  $NEXUS/service/rest/v1/repositories/raw/hosted
```

`writePolicy`는 `allow`(덮어쓰기 허용), `allow_once`(한 번만, 릴리스 저장소에 맞음), `deny`(읽기 전용)입니다.

### 4.2 PyPI proxy와 group

```bash
curl -fsS -u "$AUTH" -H 'Content-Type: application/json' \
  -d '{"name":"pypi-proxy","online":true,
       "storage":{"blobStoreName":"default","strictContentTypeValidation":true},
       "proxy":{"remoteUrl":"https://pypi.org","contentMaxAge":1440,"metadataMaxAge":1440},
       "negativeCache":{"enabled":true,"timeToLive":1440},
       "httpClient":{"blocked":false,"autoBlock":true}}' \
  $NEXUS/service/rest/v1/repositories/pypi/proxy

curl -fsS -u "$AUTH" -H 'Content-Type: application/json' \
  -d '{"name":"pypi-all","online":true,
       "storage":{"blobStoreName":"default","strictContentTypeValidation":true},
       "group":{"memberNames":["pypi-hosted","pypi-proxy"]}}' \
  $NEXUS/service/rest/v1/repositories/pypi/group
```

group의 구성원 순서가 조회 순서입니다. 사내 패키지 이름이 외부와 겹칠 수 있으면 hosted를 앞에 둡니다(group 생성 전에 `pypi-hosted`를 같은 방식으로 만들어 둠).

### 4.3 Docker hosted

Docker 라우팅은 저장소마다 하나를 고릅니다.

| 방식                      | 이미지 주소 예                            | 비고                                        |
|---------------------------|-------------------------------------------|---------------------------------------------|
| 경로 기반 (3.83.0~, 권장) | `nexus.example.com/docker-hosted/app:1.0` | 8081(또는 앞단 443) 하나로 여러 저장소 제공 |
| 서브도메인                | `docker-hosted.nexus.example.com/app:1.0` | 와일드카드 DNS·인증서 필요                  |
| 포트 커넥터 (legacy)      | `nexus.example.com:8082/app:1.0`          | 저장소마다 포트, 20개 미만 권장             |

```bash
# 경로 기반
curl -fsS -u "$AUTH" -H 'Content-Type: application/json' \
  -d '{"name":"docker-hosted","online":true,
       "storage":{"blobStoreName":"default","strictContentTypeValidation":true,"writePolicy":"allow_once","latestPolicy":true},
       "docker":{"v1Enabled":false,"forceBasicAuth":true,"pathEnabled":true}}' \
  $NEXUS/service/rest/v1/repositories/docker/hosted
```

- 경로 기반은 8081의 `/v2/`가 Bearer 토큰 방식으로 응답하므로 3.3절의 `DockerToken` 영역을 켜야 로그인됩니다.
- 포트 커넥터는 `"httpPort":8082`처럼 지정하고, 컨테이너에서 그 포트를 따로 열어야 합니다.
- `latestPolicy: true`는 `allow_once`에서도 `latest` 태그만 다시 올릴 수 있게 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 클라이언트 연결

### 5.1 파일 (raw)

```bash
curl -fsS -u "$AUTH" --upload-file dist/tool-1.0.tar.gz \
  $NEXUS/repository/raw-hosted/tool/1.0/tool-1.0.tar.gz          # 201
curl -fsS -u "$AUTH" -O $NEXUS/repository/raw-hosted/tool/1.0/tool-1.0.tar.gz

# components API (여러 파일, 디렉터리 지정)
curl -fsS -u "$AUTH" -F raw.directory=tool/1.0 \
  -F raw.asset1=@dist/tool-1.0.tar.gz -F raw.asset1.filename=tool-1.0.tar.gz \
  "$NEXUS/service/rest/v1/components?repository=raw-hosted"      # 204
```

### 5.2 pip

```ini
# ~/.config/pip/pip.conf (또는 /etc/pip.conf)
[global]
index-url = https://nexus.example.com/repository/pypi-all/simple
```

인증이 필요하면 비밀번호를 `pip.conf`에 쓰지 않고 `~/.netrc`(권한 600)나 keyring에 둡니다. 올리기는 `twine upload --repository-url https://nexus.example.com/repository/pypi-hosted/ dist/*`입니다.

### 5.3 Docker

```bash
docker login nexus.example.com                       # 경로 기반, HTTPS 앞단
docker tag app:1.0 nexus.example.com/docker-hosted/app:1.0
docker push nexus.example.com/docker-hosted/app:1.0
docker pull nexus.example.com/docker-hosted/app:1.0
```

Docker 클라이언트는 HTTPS를 기본으로 요구합니다. HTTP로 시험하려면 Docker 데몬의 `insecure-registries`에 주소를 넣어야 하므로, 운영에서는 리버스 프록시(Nginx 등)에서 TLS를 끝내고 Nexus로 넘깁니다. 큰 이미지 층을 위해 프록시의 요청 본문 크기 제한(`client_max_body_size 0;` 등)을 풉니다.

### 5.4 Maven

```xml
<!-- ~/.m2/settings.xml -->
<settings>
  <mirrors>
    <mirror>
      <id>nexus</id>
      <mirrorOf>*</mirrorOf>
      <url>https://nexus.example.com/repository/maven-public/</url>
    </mirror>
  </mirrors>
  <servers>
    <server>
      <id>nexus</id>
      <username>${env.NEXUS_USER}</username>
      <password>${env.NEXUS_TOKEN}</password>
    </server>
  </servers>
</settings>
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 운영

### 6.1 정리와 공간 회수

| 단계 | 작업                              | 설명                                                            |
|------|-----------------------------------|-----------------------------------------------------------------|
| 1    | 정리 정책 (Cleanup Policy)        | 나이·마지막 다운로드·릴리스 유형·이름 패턴으로 대상 지정 (화면) |
| 2    | 저장소에 정책 연결                | 저장소 설정에서 정책 선택. `Cleanup service` 작업이 매일 실행   |
| 3    | `Admin - Compact blob store` 작업 | 정리는 삭제 표시만 하므로 이 작업이 실제 디스크 공간을 돌려줌   |

```bash
# 매일 03:00 blob 저장소 압축 작업 만들기
curl -fsS -u "$AUTH" -H 'Content-Type: application/json' \
  -d '{"type":"blobstore.compact","name":"compact-default","enabled":true,
       "notificationCondition":"FAILURE",
       "frequency":{"schedule":"cron","cronExpression":"0 0 3 * * ?"},
       "properties":{"blobstoreName":"default","blobsOlderThan":"0"}}' \
  $NEXUS/service/rest/v1/tasks
```

Docker 저장소는 `Docker - Delete unused manifests and images`, `Docker - Delete incomplete uploads` 작업도 함께 둡니다. 작업 유형 목록은 `GET /service/rest/v1/tasks/templates`입니다.

### 6.2 백업과 복원

| DB         | 백업                                                     | 함께 백업                                           |
|------------|----------------------------------------------------------|-----------------------------------------------------|
| H2         | `Admin - Backup H2 Database` 작업 (지정 위치에 ZIP 생성) | blob 저장소, 노드 ID(`/nexus-data/keystores/node/`) |
| PostgreSQL | `pg_dump` 등 DB 도구                                     | blob 저장소, 노드 ID                                |

```bash
# H2 백업 작업 만들기와 즉시 실행
ID=$(curl -fsS -u "$AUTH" -H 'Content-Type: application/json' \
  -d '{"type":"h2.backup.task","name":"db-backup","enabled":true,
       "notificationCondition":"FAILURE","frequency":{"schedule":"manual"},
       "properties":{"location":"/nexus-data/backup"}}' \
  $NEXUS/service/rest/v1/tasks | sed -n 's/.*"id" : "\([^"]*\)".*/\1/p')
curl -fsS -u "$AUTH" -X POST $NEXUS/service/rest/v1/tasks/$ID/run
docker exec nexus ls -l /nexus-data/backup                   # nexus-<날짜-시각>.zip
```

- DB와 blob은 같은 시점에 백업합니다. DB만 복원하면 저장소 설정은 돌아오지만 파일 받기는 500 오류가 납니다(시험에서 확인).
- 백업 ZIP은 컨테이너 볼륨 밖(다른 디스크·원격 저장소)으로 복사해 둡니다.

복원 순서(공식 절차, H2):

1. Nexus를 멈춥니다.
2. 백업 ZIP을 풀어 `/nexus-data/db`의 파일을 백업 파일로 바꿉니다. 같은 시점의 파일을 모두 함께 바꿉니다.
3. 같은 시점의 blob 저장소와 노드 ID를 같은 위치로 복원합니다.
4. 시작한 뒤 `status/writable`, 저장소 목록, 파일 받기를 확인합니다. DB와 blob 시점이 어긋나면 복구(reconcile) 작업을 실행합니다.

### 6.3 상태 감시

| 경로                                   | 의미                                       | 인증   |
|----------------------------------------|--------------------------------------------|--------|
| `GET /service/rest/v1/status`          | 읽기 가능 200, 아니면 503                  | 불필요 |
| `GET /service/rest/v1/status/writable` | 쓰기 가능 200, 읽기 전용 등이면 503        | 불필요 |
| `GET /service/rest/v1/status/check`    | 항목별 상태(blob 저장소, 디스크, 스케줄러) | 필요   |

`status/check`에서 `Default Secret Encryption Key`가 비정상이면 기본 암호화 키를 쓰는 상태입니다. 운영 전에 [재암호화 문서](https://help.sonatype.com/en/re-encryption-in-nexus-repository.html)대로 사용자 키를 둡니다.

### 6.4 업그레이드

1. 릴리스 노트에서 건너뛰는 판 사이의 필수 단계(DB 이전, Java 판)를 확인합니다.
2. DB와 blob을 백업합니다.
3. 이미지 태그를 새 판으로 바꿔 다시 만듭니다(`docker compose pull && docker compose up -d`). 볼륨은 그대로 둡니다.
4. 로그의 업그레이드 단계(`migrated to v...`)와 7절 검증을 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 검증

| 순서 | 확인 내용     | 방법                                                                            | 기대 결과                             |
|------|---------------|---------------------------------------------------------------------------------|---------------------------------------|
| 1    | 기동          | `curl -s -o /dev/null -w '%{http_code}' $NEXUS/service/rest/v1/status/writable` | `200`                                 |
| 2    | 에디션·DB     | `docker logs nexus \| grep -E 'edition\|databaseId'`                            | 의도한 에디션, `H2` 또는 `PostgreSQL` |
| 3    | 초기 비밀번호 | `docker exec nexus ls /nexus-data/admin.password`                               | 파일 없음 (변경 완료)                 |
| 4    | 익명 차단     | 인증 없이 `curl $NEXUS/repository/raw-hosted/<파일>`                            | `401`                                 |
| 5    | 올리기·받기   | 5.1절 업로드 후 인증 받기                                                       | `201` 후 `200`, 내용 같음             |
| 6    | 재배포 방지   | `allow_once` 저장소에 같은 경로 다시 올리기                                     | `409`                                 |
| 7    | 프록시 캐시   | `pip download --no-deps <패키지>` (group 주소)                                  | 패키지 받음                           |
| 8    | Docker        | `docker push` 후 `docker pull`, 또는 `crane digest`                             | 원본과 같은 digest                    |
| 9    | 작업          | `GET /service/rest/v1/tasks`                                                    | 백업·압축 작업 `lastRunResult: OK`    |
| 10   | 상태 점검     | `GET /service/rest/v1/status/check`                                             | 비정상 항목이 없거나 이유를 알고 있음 |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

| 증상                                                                | 원인                                                     | 조치                                                     |
|---------------------------------------------------------------------|----------------------------------------------------------|----------------------------------------------------------|
| 관리자로도 올리기·받기 403, "accept the End User License Agreement" | CE EULA 미수락                                           | 3.2절대로 수락                                           |
| 경로 기반 `docker login` 401, `WWW-Authenticate: Bearer`            | `DockerToken` 영역 꺼짐                                  | 3.3절대로 영역 활성                                      |
| 429 "Too many authentication attempts"                              | 잘못된 인증을 짧은 시간에 반복 (도구의 자동 재시도 포함) | 원인(영역·비밀번호)을 고친 뒤 잠시 기다렸다가 다시 시도  |
| `allow_once` 저장소에 다시 올리기 409                               | 같은 경로 재배포 금지                                    | 판 번호를 올림. 덮어써야 하면 `allow` 저장소 사용        |
| 받기 500, 설정은 정상                                               | DB만 복원되고 blob이 없음                                | 같은 시점 blob 복원, 복구 작업 실행                      |
| 기동 실패, 데이터 디렉터리 권한 오류                                | 호스트 디렉터리 소유자가 UID 200이 아님                  | `chown -R 200:200 <디렉터리>`                            |
| DB가 읽기 전용, `status/writable` 503                               | 빈 디스크 4GB 미만                                       | 공간 확보, 정리 정책·압축 작업 점검                      |
| CE에서 새 컴포넌트가 안 올라감                                      | 사용량 한도(40,000개·하루 100,000건) 초과                | 정리로 줄이거나 Pro 검토                                 |
| proxy 저장소가 받지 못함                                            | 외부 연결 차단, 원격 저장소 자동 차단(autoBlock)         | 나가는 HTTPS·프록시 설정 확인, 저장소 상태에서 차단 해제 |
| `docker push`가 큰 층에서 실패                                      | 앞단 프록시의 본문 크기·시간 제한                        | 리버스 프록시 제한 해제, 시간 제한 연장                  |

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [아티팩트 저장소 비교](./artifact_repository_comparison.md) — Nexus·Artifactory·Cloudsmith 등 고르는 기준
- [Docker Compose](../containers/docker_compose.md) — 2.2절 Compose 구성의 기본
- [리버스 프록시](../web_server/reverse_proxy.md) — HTTPS 앞단 구성
- [GitHub Actions](./github_actions.md) · [Jenkins Pipeline](./jenkins_pipeline.md) — CI에서 결과물 올리기
- [이미지 판 관리와 단계별 승격](./image_versioning_and_promotion.md) — raw·Docker 저장소로 이미지 판 보관과 승격

---

## 참고 자료

- Sonatype Help: [Release Notes 3.98.0](https://help.sonatype.com/en/sonatype-nexus-repository-3-98-0-release-notes.html) · [System Requirements](https://help.sonatype.com/en/sonatype-nexus-repository-system-requirements.html) — ★★★☆☆
- Sonatype Help: [Community Edition Onboarding](https://help.sonatype.com/en/ce-onboarding.html) · [Tiers and Feature Availability](https://help.sonatype.com/en/nexus-repository-tiers-and-feature-availability.html) — ★★★☆☆
- Sonatype Help: [Install with a PostgreSQL Database](https://help.sonatype.com/en/install-nexus-repository-with-a-postgresql-database.html) · [Backup and Restore H2](https://help.sonatype.com/en/configure-and-run-the-backup-task.html) — ★★★☆☆
- Sonatype Help: [Docker Registry](https://help.sonatype.com/en/docker-registry.html) · [Docker Authentication](https://help.sonatype.com/en/docker-authentication.html) — ★★★☆☆
- Sonatype Help: [Status API](https://help.sonatype.com/en/status-api.html) · [Components API](https://help.sonatype.com/en/components-api.html) · [Cleanup Policies](https://help.sonatype.com/en/cleanup-policies.html) — ★★★☆☆
- GitHub: [sonatype/docker-nexus3](https://github.com/sonatype/docker-nexus3) — 이미지 README, 3.98.3 확인 2026-11-24 — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-24

**마지막 업데이트**: 2026-11-27

© 2026 siasia86. Licensed under CC BY 4.0.

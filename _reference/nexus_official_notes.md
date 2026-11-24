---
name: nexus-official-notes
description: Sonatype Nexus Repository 3.98 판·에디션·CE 한도·Docker 이미지·REST API 공식 자료와 컨테이너 확인 결과 정리.
tags:
  - nexus
  - sonatype
  - artifact-repository
  - docker-registry
  - rest-api
last_checked: 2026-11-24
sources:
  - https://help.sonatype.com/en/sonatype-nexus-repository-3-98-0-release-notes.html
  - https://hub.docker.com/r/sonatype/nexus3
  - https://raw.githubusercontent.com/sonatype/docker-nexus3/main/README.md
  - https://help.sonatype.com/en/nexus-repository-tiers-and-feature-availability.html
  - https://help.sonatype.com/en/ce-onboarding.html
  - https://help.sonatype.com/en/sonatype-nexus-repository-3-87-0-release-notes.html
  - https://help.sonatype.com/en/sonatype-nexus-repository-3-71-0-release-notes.html
  - https://help.sonatype.com/en/sonatype-nexus-repository-system-requirements.html
  - https://help.sonatype.com/en/formats.html
  - https://help.sonatype.com/en/docker-registry.html
  - https://help.sonatype.com/en/docker-authentication.html
  - https://help.sonatype.com/en/status-api.html
  - https://help.sonatype.com/en/components-api.html
  - https://help.sonatype.com/en/search-api.html
  - https://help.sonatype.com/en/script-api.html
  - https://help.sonatype.com/en/cleanup-policies.html
  - https://help.sonatype.com/en/configuring-blob-stores.html
  - https://help.sonatype.com/en/backup-and-restore.html
  - https://help.sonatype.com/en/configure-and-run-the-backup-task.html
---

# Nexus Repository 공식 자료 참조 노트

## 1. 판 (2026-11-24)

| 항목             | 내용                                                                           | 근거                         |
|------------------|--------------------------------------------------------------------------------|------------------------------|
| 최신판           | 3.98.3 (2026-11-19). 3.98.0 2026-11-03, 3.98.1 11-05, 3.98.2 11-18             | 3.98.0 릴리스 노트           |
| Docker 태그      | `latest`·`3.98.3`·`3.98.3-alpine`·`3.98.3-ubi`, 유지보수 3.97.5·3.91.3 등      | Docker Hub `sonatype/nexus3` |
| 시험 이미지      | `sonatype/nexus3:latest` = 라벨 `version 3.98.3-01`, Alpine 기반, Java 21.0.13 | `docker image inspect`       |
| 3.98.0 주요 변경 | 새 UI 기본, Enterprise 에디션 추가, Groovy 스크립트 실행 기본 꺼짐             | 3.98.0 릴리스 노트           |
| 3.98.2           | CVE-2026-114938 대응 보호 추가                                                 | 같은 노트                    |
| 3.87.0           | CE 한도 조정 (컴포넌트 100,000·요청 200,000 → 40,000·100,000)                  | 3.87.0 릴리스 노트           |
| 3.83.0           | Docker 경로 기반 라우팅 추가                                                   | Docker Registry 문서         |
| 3.71.0           | OrientDB·Java 8·11 지원 종료, 신규 설치 기본 DB가 H2                           | 3.71.0 릴리스 노트           |

## 2. 에디션과 CE 한도

- 에디션: Community Edition(무료, 자체 호스팅), Pro, Pro+, Enterprise. Cloud는 에디션이 아니라 배포 방식입니다.
- CE에서 쓸 수 없는 기능(tiers 문서, 2026-11-05 수정): HA·클러스터, SAML/OIDC SSO, 클라우드 blob(S3·Azure·GCS), DR 복제, 삭제 복구, FIPS 140-2.
- CE 한도(ce-onboarding, 2026-10-16 수정): 전체 컴포넌트 40,000개, 하루 요청 100,000건. 넘으면 두 기준 아래로 내려갈 때까지 새 컴포넌트 추가를 멈춥니다. 유예 기간은 현재 문서에서 확인하지 못했습니다.
- CE는 EULA를 마법사나 EULA REST API(`/service/rest/v1/system/eula`)로 수락해야 컴포넌트를 받거나 올릴 수 있습니다.
- 시스템 요구사항(H2 절): 내장 H2는 하루 요청 200,000건 또는 컴포넌트 100,000개까지 지원하고, H2에서는 컨테이너 기반 배포를 지원하지 않으며, PostgreSQL을 권장합니다. 디스크는 항상 4GB 이상 비어 있어야 하고 부족하면 DB가 읽기 전용이 됩니다. 이 문구는 잘린 페이지의 요약으로 확인했고 원문 문장 대조는 미완료입니다.
- 공식 최소 CPU·메모리 값은 없고, 가장 작은 프로필이 4 vCPU·16GiB입니다. Java 21이 필요합니다.
- PostgreSQL(설치 문서): 환경 변수 `NEXUS_DATASTORE_NEXUS_JDBCURL`·`_USERNAME`·`_PASSWORD`·`_ADVANCED`(예 `maximumPoolSize=200`), JVM 인수 `-Dnexus.datastore.nexus.*`, 파일 `<data-dir>/etc/fabric/nexus-store.properties` 순으로 우선합니다. PostgreSQL은 커뮤니티가 아직 지원하는 판이어야 하고 `pg_trgm` 확장이 필요합니다. 설치 문서 뒷부분은 잘린 페이지의 요약으로 확인했습니다.
- CE에서 PostgreSQL을 쓸 수 있는지는 공식 문서 문장으로 확인하지 못했고, 아래 시험에서 CE가 PostgreSQL로 기동하는 것을 확인했습니다.
- 기본 암호화 키 대신 사용자 키를 JSON 파일로 두고 재암호화하는 절차는 re-encryption 문서(https://help.sonatype.com/en/re-encryption-in-nexus-repository.html)에 있습니다. 시험하지 않았습니다.

## 3. Docker 이미지 (README)

| 항목                      | 값                                                                            |
|---------------------------|-------------------------------------------------------------------------------|
| 포트                      | 8081                                                                          |
| 데이터                    | `/nexus-data` (볼륨), 실행 사용자 `nexus`(UID 200)                            |
| 초기 비밀번호             | 데이터 볼륨의 `admin.password` (변경하면 파일이 지워짐, 시험에서 확인)        |
| `INSTALL4J_ADD_VM_PARAMS` | 기본 `-Djava.util.prefs.userRoot=${NEXUS_DATA}/javaprefs`, `-Xms`=`-Xmx` 권장 |
| `NEXUS_CONTEXT`           | 문맥 경로, 기본 `/`                                                           |

## 4. 저장소·라우팅·인증

- 저장소 유형: hosted, proxy, group. 형식: Maven, npm, NuGet, PyPI, Docker, OCI, Raw, Helm, APT, Yum, Go, Cargo, Conda, Conan, RubyGems, Terraform 등(formats 문서).
- Docker 라우팅은 경로 기반(3.83.0, 권장), 서브도메인, 리버스 프록시, 포트 커넥터(legacy, 20개 미만 권장) 중 하나입니다. 경로 기반은 `/repository/`를 빼고 `호스트/<저장소 이름>/<이미지>`로 씁니다.
- Docker Bearer Token Realm은 Docker 클라이언트 토큰 인증과 익명 pull에 필요합니다(docker-authentication).
- REST:
  - `GET /service/rest/v1/status`: 읽기 가능 200, 아니면 503
  - `GET /service/rest/v1/status/writable`: 쓰기 가능 200, 아니면 503
  - `GET /service/rest/v1/status/check`: 3.81부터, 상세 상태
  - `POST /service/rest/v1/components?repository=<이름>`: 업로드, 성공 204
  - `GET /service/rest/v1/search`, `/search/assets`, `/search/assets/download`(결과 1개일 때 302)
  - 전체 명세: `/service/rest/swagger.json` (시험 판은 OpenAPI 3)
- Script API: 스크립트 생성은 3.21.2부터, 실행은 3.98.0부터 기본 꺼짐(`nexus.scripts.allowExecution`).

## 5. 정리·blob·백업

- 정리 정책은 삭제 표시(soft delete)만 하므로 공간 회수에는 `Admin - Compact blob store` 작업이 필요합니다.
- blob 저장소: File(NFS v4·EFS 포함), S3, Azure, Google Cloud(클라우드 blob은 CE 제외). 소프트 할당량은 경고만 하고, 경로는 만든 뒤 바꿀 수 없습니다.
- H2 백업은 `Admin - Backup H2 Database` 작업(ZIP)입니다. 복원 순서(공식): Nexus 중지 → ZIP 풀기 → `$data-dir/db` 파일 교체 → 같은 시점의 blob 저장소 복원 → 시작 후 확인. 노드 ID(`$data-dir/keystores/node/`)도 같은 위치로 복원합니다. PostgreSQL은 DB 자체 도구로 백업합니다.

## 6. 컨테이너 시험 (2026-11-24)

구성: `sonatype/nexus3:latest`(3.98.3-01), 메모리 제한 3GB, 힙 1GB, 이름 붙은 볼륨, 같은 Docker 네트워크의 curl·python·crane 컨테이너.

| 확인                                                 | 결과                                                                                      |
|------------------------------------------------------|-------------------------------------------------------------------------------------------|
| 기동 로그                                            | `Starting nexus with edition COMMUNITY`, `MyBatis databaseId: H2`                         |
| `status/writable`                                    | 기동 약 25초 뒤 200, 메모리 사용 약 1.3GiB                                                |
| 기본 저장소                                          | maven-releases·snapshots·central·public, nuget-hosted·nuget.org-proxy·nuget-group         |
| 익명 접근·활성 영역                                  | `enabled: false`, `NexusAuthenticatingRealm`만                                            |
| 비밀번호 변경 (`.../users/admin/change-password`)    | 204, 이전 비밀번호 401, `admin.password` 파일 삭제됨                                      |
| EULA 수락 전 raw 업로드                              | 403, 본문 "You must accept the End User License Agreement (EULA)"                         |
| EULA 수락 (`POST /v1/system/eula`, `accepted: true`) | 204                                                                                       |
| raw hosted (`allow_once`) 업로드·받기                | 201, 익명 401, 인증 200, 같은 경로 재업로드 409                                           |
| components API (raw)                                 | 204                                                                                       |
| pypi proxy + group, `pip download requests`          | `requests-2.32.3-py3-none-any.whl` 받음                                                   |
| docker hosted 포트 커넥터 8082, `crane copy`         | 성공, digest가 Docker Hub 원본과 같음                                                     |
| docker hosted `pathEnabled`, 8081                    | 처음 401 (Bearer 응답, 토큰 영역 꺼짐) → 재시도 중 429 "Too many authentication attempts" |
| `DockerToken` 영역 활성 뒤                           | 같은 경로로 올리기·`ls`·digest 성공                                                       |
| 정리 정책 REST (`/v1/cleanup-policies`)              | 404 (CE)                                                                                  |
| 상태 점검 비정상 항목                                | 기본 암호화 키 사용, 필수 원격 측정(telemetry) 미확인                                     |
| `h2.backup.task` 실행                                | `/nexus-data/backup/nexus-<시각>.zip` 생성 (약 340KB)                                     |
| `blobstore.compact` (cron `0 0 3 * * ?`)             | `lastRunResult: OK`                                                                       |
| ZIP을 새 볼륨 `restore-from-backup`에 두고 기동      | 로그 `Restored nexus.mv.db`, 저장소 설정 복원. blob 미복원이라 raw 받기 500               |
| PostgreSQL 17.12 + `pg_trgm` 1.6, 환경 변수 4개      | `edition COMMUNITY`, `from environment-variables (postgresql)`, 테이블 214개 생성         |

- `restore-from-backup` 디렉터리 방식은 기동 로그로 동작을 확인했지만 이번에 확인한 공식 복원 절차에는 나오지 않습니다. 문서에는 공식 절차(`db` 교체)를 적었습니다.
- 원격 측정 확인(`/v1/system/mandatory-telemetry-acknowledgement`)은 별도 동의라서 시험하지 않았습니다.

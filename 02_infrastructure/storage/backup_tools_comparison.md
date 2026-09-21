# 범용 백업 솔루션·도구 비교
<!-- reference: _reference/backup_tools_official_notes.md, _reference/restic_official_notes.md, _reference/rsync_official_notes.md, _reference/aws_sts_iam_s3_kms_official_notes.md -->

이 문서는 특정 애플리케이션·운영체제·가상화 플랫폼에 종속되지 않는 범용 백업 솔루션과 백업에 활용할 수 있는 도구를 비교합니다. `rsnapshot`, `lsyncd`, `Bacula`, `BorgBackup`, `Duplicity`, `Amanda`, `Bareos`, `Restic`, `rclone`을 파일 미러링·Snapshot·암호화 백업·엔터프라이즈 백업·오브젝트 전송 계열로 구분합니다.

> Backup(백업): 원본 장애·삭제·손상 이후 복구할 수 있도록 과거 데이터를 별도 저장하는 작업입니다. 현재 상태를 다른 위치에 반영하는 동기화(Synchronization)와는 보존 목적이 다릅니다.

## 목차

| 섹션                                               | 내용                           |
|----------------------------------------------------|--------------------------------|
| [1. 범위와 분류](#1-범위와-분류)                   | 백업과 동기화의 경계           |
| [2. 전체 비교](#2-전체-비교)                       | 도구별 기능·적합성 비교        |
| [3. 도구별 특징](#3-도구별-특징)                   | 주요 도구 상세 설명            |
| [4. 백업 아키텍처](#4-백업-아키텍처)               | 계층별 구성과 선택 기준        |
| [5. 랜섬웨어와 삭제 대응](#5-랜섬웨어와-삭제-대응) | Versioning·Immutable·권한 분리 |
| [6. 운영·검증 기준](#6-운영검증-기준)              | 백업 성공과 복구 검증          |
| [7. 상황별 권장 선택](#7-상황별-권장-선택)         | 환경별 도구 선정               |

## 1. 범위와 분류

### 백업과 동기화의 차이

```text
동기화
└── 현재 상태를 다른 위치에 반영
    └── 원본 삭제·손상도 대상에 반영될 수 있음

백업
└── 여러 시점의 상태를 별도로 보존
    └── 원본 삭제·손상 이후 과거 상태로 복구
```

파일 동기화 도구를 백업에 사용할 수는 있지만, 삭제·손상·랜섬웨어에 대비하려면 별도의 보존 정책과 복구 테스트가 필요합니다.

### 도구 계열

| 계열               | 대표 도구              | 핵심 특성                    | 주의사항                       |
|--------------------|------------------------|------------------------------|--------------------------------|
| 파일 전송          | rsync                  | 효율적인 파일 목록·차등 전송 | 자체 Snapshot·보존 정책 없음   |
| 이벤트 미러        | lsyncd                 | 파일 이벤트 기반 rsync 실행  | 변경·삭제 전파 가능            |
| 하드링크 Snapshot  | rsnapshot              | rsync + 주기별 Snapshot      | 암호화·오브젝트 보존 별도 구성 |
| 암호화·중복 제거   | Restic, BorgBackup     | Snapshot·Dedup·암호화        | Repository Password·검사 필요  |
| 암호화 증분        | Duplicity              | GnuPG·librsync 기반 Archive  | 복구 체인과 Backend 검증 필요  |
| 중앙 네트워크 백업 | Bacula, Bareos, Amanda | 다수 호스트·스케줄·Catalog   | 서버·에이전트·저장소 운영 필요 |
| 오브젝트 전송      | rclone                 | Local·Cloud 복사·동기화      | 단독 사용 시 Snapshot 아님     |

> Catalog: 중앙 백업 솔루션이 어떤 호스트·작업·Volume·파일을 백업했는지 기록하는 메타데이터 저장소입니다. Catalog가 손상되면 백업 데이터가 남아 있어도 복구 절차가 복잡해질 수 있으므로 별도 보호가 필요합니다.

> Immutable Retention: 보존 기간 동안 백업 객체의 수정·삭제를 제한하는 정책입니다. 암호화와 달리 데이터 노출을 막는 기능이 아니라 백업 변경·삭제를 어렵게 만드는 기능입니다.

> Snapshot: 특정 시점의 파일·디렉터리 상태를 식별 가능한 버전으로 보존하는 기능입니다. Snapshot을 삭제하는 보존 정책을 실행하기 전까지 과거 시점 복구가 가능합니다.

> Deduplication(Dedup): 동일한 데이터 블록을 여러 번 저장하지 않고 기존 블록을 재사용하는 방식입니다. 저장 공간을 줄이지만 초기 스캔·Index·Repository 관리 비용이 발생합니다.

## 2. 전체 비교

### 기능 비교

| 도구       | 계열                | 과거 버전 | 암호화            | 중복 제거        | S3 직접 사용         | 중앙 관리 |
|------------|---------------------|-----------|-------------------|------------------|----------------------|-----------|
| rsync      | 파일 전송           | ❌        | 전송 계층 별도    | ❌               | ❌                   | ❌        |
| lsyncd     | 이벤트 미러         | ❌        | 전송 계층 별도    | ❌               | ❌                   | ❌        |
| rsnapshot  | 하드링크 Snapshot   | ✅        | 저장소 별도       | 🟡 Hard Link     | ❌                   | ❌        |
| Restic     | Snapshot Repository | ✅        | ✅                | ✅               | ✅                   | ❌        |
| BorgBackup | 암호화 Archive      | ✅        | ✅                | ✅               | 🟡 Backend 별도      | ❌        |
| Duplicity  | 암호화 증분 Archive | ✅        | ✅ GnuPG          | 🟡 Delta         | 🟡 Backend 별도      | ❌        |
| Bacula     | 중앙 네트워크 백업  | ✅        | 구성에 따라 지원  | 구성에 따라 지원 | 🟡 버전·Edition 확인 | ✅        |
| Bareos     | 중앙 네트워크 백업  | ✅        | ✅                | 구성에 따라 지원 | ✅ S3-compatible     | ✅        |
| Amanda     | 네트워크 백업       | ✅        | 구성에 따라 지원  | 구성에 따라 지원 | 🟡 버전·구성 확인    | ✅        |
| rclone     | 오브젝트 전송       | ❌        | `crypt` 구성 가능 | ❌               | ✅                   | ❌        |

이 표의 `🟡`는 기능이 없다는 의미가 아니라 Backend·Edition·구성 또는 별도 도구에 따라 달라진다는 의미입니다.

### 백업 목적별 적합성

| 목적                         | 1순위 후보         | 이유                                  |
|------------------------------|--------------------|---------------------------------------|
| 단순 원격 파일 복사          | rsync              | 설치·운영이 단순하고 전송 효율이 높음 |
| 실시간에 가까운 파일 미러    | lsyncd             | 파일 이벤트를 rsync 작업으로 연결     |
| Local·SSH Snapshot           | rsnapshot          | 주기별 Snapshot과 낮은 저장 공간 사용 |
| 암호화된 S3 Snapshot         | Restic             | 암호화·중복 제거·S3 Backend·검사      |
| SSH 기반 암호화 Archive      | BorgBackup         | Dedup·압축·인증 암호화                |
| GnuPG 기반 증분 백업         | Duplicity          | 암호화 Archive와 Remote Backend       |
| 다수 서버·테이프·Catalog     | Bacula 또는 Bareos | 중앙 Director와 클라이언트 관리       |
| 표준 도구 기반 네트워크 백업 | Amanda             | dump·restore·GNU Tar 활용             |
| S3·Cloud Storage 복사        | rclone             | 다양한 Object Storage 연결            |

## 3. 도구별 특징

### `rsync` — 파일 전송 기반

`rsync`는 백업 제품이라기보다 파일 목록 비교와 차등 전송을 담당하는 기반 도구입니다.

```bash
rsync -aHAX --delete --dry-run \
  /srv/source/ \
  backup.example.com:/srv/target/
```

주요 특징:

- Local·SSH·rsync daemon 전송
- 파일 크기·mtime·checksum 기반 비교
- 변경된 데이터 중심 전송
- Snapshot·보존 정책은 직접 구성
- `--delete` 사용 시 대상 삭제 위험

백업으로 사용하려면 날짜별 디렉터리, Snapshot, S3 Versioning 또는 별도 보존 계층을 추가합니다.

### `lsyncd` — 이벤트 기반 파일 미러

`lsyncd`는 파일시스템 이벤트를 감시한 뒤 rsync 작업을 실행하는 도구입니다.

```text
파일 변경 이벤트
       │
       v
lsyncd 이벤트 큐
       │
       v
rsync 또는 rsyncssh
       │
       v
원격 대상
```

적합한 용도:

- 웹 콘텐츠의 빠른 보조 미러
- 특정 디렉터리의 변경 전파
- 파일 배포·staging

백업으로 사용할 때의 제한:

- 과거 버전 보존이 기본 기능이 아닙니다.
- 원본 삭제가 대상에 전파될 수 있습니다.
- 손상·암호화된 파일도 변경 파일로 전파될 수 있습니다.
- 애플리케이션·데이터베이스 정합성을 판단하지 않습니다.
- S3를 POSIX Mount로 연결하는 방식은 별도 검증이 필요합니다.

### `rsnapshot` — rsync 기반 파일시스템 Snapshot

`rsnapshot`은 rsync와 Hard Link를 이용해 주기별 파일시스템 Snapshot을 유지합니다.

```text
backup.0  최신 Snapshot
backup.1  이전 Snapshot
backup.2  더 이전 Snapshot
```

```bash
rsnapshot configtest
rsnapshot daily
rsnapshot weekly
rsnapshot du
```

장점:

- Unix 계열에서 구조가 단순합니다.
- SSH 기반 원격 호스트를 Snapshot할 수 있습니다.
- 변경되지 않은 파일의 저장 공간을 Hard Link로 줄입니다.
- 사람이 파일을 직접 탐색하기 쉽습니다.

제한:

- Repository 자체 암호화가 기본 제공되는 구조가 아닙니다.
- 저장소 디스크가 함께 침해되면 Snapshot도 위험합니다.
- S3 Backend가 기본 대상이 아닙니다.
- Snapshot 디렉터리를 직접 수정하면 Hard Link 구조가 손상될 수 있습니다.

### `Restic` — 암호화·중복 제거 Snapshot

Restic은 암호화된 Repository에 Snapshot을 저장하고 S3·SFTP·REST·Local Backend를 사용할 수 있습니다.

주요 특징:

- Repository 암호화
- Snapshot
- 데이터 중복 제거
- `check` 기반 Repository 검사
- `forget`·`prune` 보존 정책
- S3 Backend
- Snapshot·파일 단위 복구

상세 구성은 [Restic 백업·복구 가이드](./restic_backup.md)를 참고합니다.

### `BorgBackup` — 암호화 Archive

BorgBackup은 Dedup·압축·인증 암호화를 사용하는 Archive 도구입니다.

대표적인 흐름은 다음과 같습니다.

```bash
borg create --stats \
  /backup/repository::'{hostname}-{now}' \
  /etc /srv/application

borg list /backup/repository
borg check /backup/repository
borg prune --list \
  --keep-daily 7 \
  --keep-weekly 4 \
  --keep-monthly 12 \
  /backup/repository
```

장점:

- Content-defined Chunking 기반 중복 제거
- 압축·암호화 Archive
- SSH 기반 원격 Repository
- Archive 단위 조회·복구

주의사항:

- Repository Key·Passphrase를 잃으면 복구할 수 없습니다.
- Remote Object Storage 직접 사용은 Backend 구성과 버전을 확인합니다.
- `prune` 전 보존 정책과 복구 가능 Snapshot을 확인합니다.

### `Duplicity` — GnuPG·librsync 증분 백업

Duplicity는 암호화된 tar 형식 Volume을 만들고 librsync 기반으로 변경분을 저장합니다.

```bash
duplicity full \
  /srv/application \
  file:///backup/duplicity/application

duplicity incremental \
  /srv/application \
  file:///backup/duplicity/application

duplicity collection-status \
  file:///backup/duplicity/application
```

장점:

- GnuPG 기반 암호화·서명
- 변경분 중심의 증분 Archive
- Local·Remote Backend 활용

주의사항:

- Full·Incremental Volume 체인의 관리가 필요합니다.
- GPG Key와 Passphrase를 별도로 보존해야 합니다.
- 오래된 체인과 누락 Volume은 복구에 영향을 줄 수 있습니다.
- 실제 복구 테스트 없이 백업 성공 로그만 신뢰하지 않습니다.

### `Bacula` — 중앙 네트워크 백업

Bacula는 다수 호스트를 중앙에서 관리하는 네트워크 백업 솔루션입니다.

```text
Bacula Director
├── File Daemon
├── Storage Daemon
└── Catalog Database
```

적합한 환경:

- 여러 서버와 클라이언트의 중앙 백업
- Full·Differential·Incremental 정책
- 디스크·테이프·다중 저장소 운영
- Catalog 기반 백업 목록과 복구 관리

검토 항목:

- Community와 Enterprise 기능 차이
- Director·Storage·Catalog의 장애 구성
- 데이터베이스 Catalog 백업
- 테이프·디스크·클라우드 Storage 연동
- Agent 권한과 네트워크 방화벽

### `Bareos` — 중앙 백업·복구 플랫폼

Bareos는 Linux·Windows·혼합 엔터프라이즈 환경의 중앙 백업·복구를 대상으로 합니다.

주요 특징:

- Full·Differential·Incremental·Always Incremental
- 물리 서버·VM·DB·애플리케이션 백업
- 디스크·테이프·S3-compatible Object Storage
- 중앙 관리와 스케줄링
- 암호화 통신·RBAC·보존 정책

Bacula와 비교할 때는 라이선스, Catalog 호환성, 구성 파일, WebUI, 지원 계약을 실제 버전 기준으로 확인합니다.

### `Amanda` — 표준 도구 기반 네트워크 백업

Amanda는 하나의 Master Backup Server에서 여러 호스트를 디스크·테이프·클라우드 등에 백업하는 네트워크 백업 시스템입니다.

주요 특징:

- GNU Tar·Unix dump/restore 기반
- 다수 Linux·Unix 호스트 관리
- 디스크·테이프·광학 미디어·클라우드 활용
- Open Format과 표준 도구 중심

적합한 환경:

- 기존 dump/tar 운영과 연계해야 하는 환경
- 테이프와 네트워크 백업을 함께 사용하는 환경
- 중앙 스케줄을 유지하되 표준 도구를 선호하는 환경

### `rclone` — Object Storage 복사·동기화

rclone은 다양한 Cloud Storage와 Local 파일 간 복사·동기화를 제공합니다.

```bash
rclone copy /srv/archive remote:bucket/archive
```

`sync`는 대상에서 원본에 없는 파일을 삭제할 수 있으므로 주의합니다.

```bash
rclone sync /srv/archive remote:bucket/archive
```

rclone을 백업으로 사용하려면 다음 계층을 함께 구성합니다.

- Object Storage Versioning
- Object Lock 또는 Immutable Retention
- 날짜별 Prefix
- 별도 IAM 권한
- 복구 테스트

rclone 단독 실행은 Snapshot 백업과 동일하지 않습니다.

## 4. 백업 아키텍처

### 범용 계층 구조

```text
Application / System
        │
        ├── Application-consistent Export
        │
        └── Filesystem-consistent Data
                │
                v
        Backup Tool
        ├── File mirror
        ├── Snapshot
        ├── Encrypted archive
        └── Central backup platform
                │
                v
        Backup Repository
        ├── Local disk
        ├── Remote server
        ├── S3-compatible storage
        └── Tape / WORM media
                │
                v
        Retention·Integrity·Restore Test
```

### 백업 대상별 선택

| 백업 대상           | 우선 검토 도구        | 보완 구성                    |
|---------------------|-----------------------|------------------------------|
| 단순 설정 파일      | rsync·rsnapshot       | SSH·Snapshot 보존            |
| 웹 콘텐츠 미러      | lsyncd·rsync          | 별도 Snapshot 백업           |
| 단일 Linux 서버     | rsnapshot·Restic·Borg | S3·암호화·복구 테스트        |
| 암호화된 Cloud 백업 | Restic·Borg·Duplicity | IAM·Versioning·Immutable     |
| 다수 서버           | Bacula·Bareos·Amanda  | Catalog·Agent·Storage 이중화 |
| Object Storage 복사 | rclone                | Versioning·Object Lock       |
| 데이터베이스        | 제품별 Dump·Snapshot  | 선택한 파일 백업 도구        |

### 백업과 복제의 분리

```text
복제
└── 최신 상태 유지·장애 전환

백업
└── 과거 상태 보존·삭제·손상 복구

Archive
└── 장기 보존·감사·규정 대응
```

복제 대상과 백업 대상은 동일하지 않을 수 있습니다. 복제는 최신 상태를 유지하지만 삭제·논리 오류·랜섬웨어 변경을 함께 전달할 수 있습니다.

## 5. 랜섬웨어와 삭제 대응

### 미러링 도구의 위험

```text
원본 파일 암호화
       │
       v
파일 이벤트 감지
       │
       v
대상 파일 덮어쓰기
```

파일 미러링만 사용하는 경우 다음을 별도로 추가해야 합니다.

- 날짜별 Snapshot
- 삭제 지연
- 대상의 write-only 권한
- Versioning
- Immutable 저장소
- 오프라인 또는 별도 계정 백업

### 암호화와 불변성의 차이

```text
암호화
└── 백업 내용 노출 방지

불변성
└── 백업 삭제·변경 방지

둘은 서로 대체하지 않음
```

암호화된 Repository도 공격자가 유효한 Delete 권한과 Repository Password를 확보하면 삭제·변조될 수 있습니다.

### S3 권한 분리

백업을 업로드하는 서버에 S3 전체 관리 권한을 주지 않습니다.

```text
Backup Upload Role
├── 지정 Bucket·Prefix에 객체 생성
├── 필요한 객체 조회
└── 기존 백업 삭제·Bucket 정책 변경 금지

Maintenance Role
├── Retention 변경
├── Prune·삭제
└── 복구 운영
```

Active Repository와 Immutable 보존 영역을 분리할 때는 도구의 `prune`·삭제 동작과 Object Lock의 호환성을 테스트합니다.

## 6. 운영·검증 기준

### RPO·RTO

> RPO(Recovery Point Objective): 장애 발생 시 허용할 수 있는 데이터 손실 시점입니다.
>
> RTO(Recovery Time Objective): 장애 발생 후 서비스를 복구하는 데 허용되는 최대 시간입니다.

백업 주기는 RPO에 맞추고, 복구 절차와 저장소 성능은 RTO에 맞춰 검증합니다.

### 공통 검증 단계

```text
1. 백업 명령 종료 코드 확인
2. 최신 백업 버전 생성 확인
3. Repository·Archive 무결성 검사
4. 임시 디렉터리 또는 테스트 환경 복구
5. 파일·권한·소유자·메타데이터 확인
6. 애플리케이션 또는 데이터 검증
7. 복구 시간 기록
```

### 도구별 검증 명령

| 도구       | 검증 명령·방법                             | 확인 내용             |
|------------|--------------------------------------------|-----------------------|
| rsync      | `rsync --dry-run --itemize-changes`        | 예상 변경·삭제        |
| lsyncd     | 테스트 디렉터리·로그·대상 checksum         | 이벤트 전파·삭제 범위 |
| rsnapshot  | `rsnapshot configtest`, Snapshot 파일 확인 | 설정·보존 구조        |
| Restic     | `restic check`, `restic restore`           | Repository·복구       |
| BorgBackup | `borg check`, Archive 복구                 | Repository·Archive    |
| Duplicity  | `collection-status`, 테스트 복구           | Volume 체인           |
| Bacula     | Catalog·Job·복구 작업                      | 중앙 관리·복구        |
| Bareos     | Job·Catalog·복구 작업                      | 중앙 관리·복구        |
| Amanda     | Backup Set·복구 테스트                     | 네트워크 백업 세트    |
| rclone     | `rclone check`, 테스트 복사                | 객체 목록·내용 비교   |

### 운영 주기 예시

| 주기          | 작업                               |
|---------------|------------------------------------|
| 백업 실행마다 | 종료 코드·로그·최신 백업 확인      |
| 매일          | 최신 백업 존재·저장소 용량 확인    |
| 매주          | Repository·Archive 무결성 검사     |
| 매월          | 일부 파일·애플리케이션 복구 테스트 |
| 분기별        | 전체 복구 훈련·RPO/RTO 측정        |

### 문서화할 항목

- 백업 대상과 제외 대상
- 도구와 버전
- Repository 위치와 Backend
- 암호화 Key·Password 복구 절차
- 보존 정책과 삭제 승인 절차
- RPO·RTO
- 마지막 복구 테스트 시각과 결과
- 장애 시 담당자와 연락 체계

## 7. 상황별 권장 선택

### 소규모 Linux 서버

```text
rsnapshot 또는 Restic
├── rsnapshot: 사람이 직접 탐색하기 쉬운 Local·SSH Snapshot
└── Restic: 암호화·Dedup·S3·Repository 검사
```

### 실시간 미러가 필요한 웹 콘텐츠

```text
lsyncd 또는 rsync
        +
Restic·rsnapshot·Borg 등 과거 Snapshot 백업
```

미러링만으로 백업을 완료했다고 판단하지 않습니다.

### 다수 서버·테이프·중앙 Catalog

```text
Bacula 또는 Bareos
        └── 필요 시 Amanda 비교
```

클라이언트 수, Storage Daemon, Catalog, 테이프, 지원 계약, 복구 운영팀을 함께 평가합니다.

### S3 중심 환경

```text
Restic / Borg / Duplicity
        +
S3 Versioning·IAM·Immutable 보존
```

단순 Object Storage 복사라면 rclone을 사용할 수 있지만, Snapshot·보존·복구 정책을 별도로 구성합니다.

### 선택 체크리스트

- 실시간 반영이 필요한가, 과거 시점 복구가 필요한가?
- 파일 미러인가, 애플리케이션 일관성 백업인가?
- 단일 서버인가, 중앙 관리가 필요한 다수 서버인가?
- Local·SSH·S3·테이프 중 어떤 Backend인가?
- 저장 데이터 암호화가 필요한가?
- Dedup과 압축이 필요한가?
- 삭제·랜섬웨어에 대비한 Immutable 보존이 필요한가?
- Catalog·Job·Agent·웹 관리 화면이 필요한가?
- RPO·RTO와 복구 테스트를 수용할 수 있는가?
- 도구의 License·Edition·지원 수명은 요구사항에 맞는가?

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- rsnapshot: [rsnapshot.org](https://rsnapshot.org/) — ★★★☆☆
- lsyncd: [github.com/lsyncd/lsyncd](https://github.com/lsyncd/lsyncd) — ★★★☆☆
- Bacula: [bacula.org](https://www.bacula.org/) — ★★★☆☆
- BorgBackup: [borgbackup.org](https://www.borgbackup.org/) — ★★★★☆
- Duplicity: [duplicity.us](https://duplicity.us/) — ★★★☆☆
- Amanda: [amanda.org](https://www.amanda.org/) — ★★★☆☆
- Bareos: [bareos.com](https://www.bareos.com/) — ★★★☆☆
- rclone: [rclone.org](https://rclone.org/) — ★★★☆☆
- [Restic 백업·복구 가이드](./restic_backup.md)
- [백업 도구 공식 참조 노트](../../_reference/backup_tools_official_notes.md)
- [Restic 공식 참조 노트](../../_reference/restic_official_notes.md)
- [rsync 공식 참조 노트](../../_reference/rsync_official_notes.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-21

**마지막 업데이트**: 2026-09-21

© 2026 siasia86. Licensed under CC BY 4.0.

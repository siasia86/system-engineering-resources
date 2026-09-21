# Restic 범용 백업·복구 가이드
<!-- reference: _reference/restic_official_notes.md, _reference/aws_sts_iam_s3_kms_official_notes.md -->

Restic은 파일과 디렉터리를 암호화된 Repository에 Snapshot 형태로 저장하는 범용 백업 도구입니다. 실시간 파일 복제보다 과거 시점의 데이터를 보존하고 필요한 시점으로 복구하는 용도에 적합합니다.

이 문서는 시스템 설정, 애플리케이션 데이터, 컨테이너 볼륨, 데이터베이스 Dump, 로그·아카이브 등 다양한 백업 대상을 Restic으로 보호할 때 필요한 Repository·Snapshot·중복 제거·S3 Backend·보존 정책·무결성 검사·복구 절차를 정리합니다.

> Backup Repository: 백업 데이터와 Snapshot 메타데이터를 Restic 전용 형식으로 저장하는 공간입니다. 일반 파일을 그대로 복사하는 디렉터리와 달리 Restic 명령어와 Repository 비밀번호를 사용해 저장·검증·복구합니다.

## 목차

| 섹션                                                       | 내용                          |
|------------------------------------------------------------|-------------------------------|
| [1. Restic 개요](#1-restic-개요)                           | 목적·버전·적합한 용도         |
| [2. 핵심 동작](#2-핵심-동작)                               | Snapshot·암호화·중복 제거     |
| [3. Repository와 Backend](#3-repository와-backend)         | Local·S3·SFTP·REST 구조       |
| [4. 기본 사용 흐름](#4-기본-사용-흐름)                     | 초기화·백업·조회·복구         |
| [5. 보존 정책과 무결성 검사](#5-보존-정책과-무결성-검사)   | `forget`·`prune`·`check`      |
| [6. 애플리케이션 일관성 백업](#6-애플리케이션-일관성-백업) | 열린 파일·Dump·정합성 백업    |
| [7. S3와 랜섬웨어 대응](#7-s3와-랜섬웨어-대응)             | IAM·Versioning·Immutable 저장 |
| [8. 운영 설계와 검증](#8-운영-설계와-검증)                 | 스케줄·복구 테스트·비교       |

## 1. Restic 개요

### Restic이 해결하는 문제

Restic은 다음과 같은 범용 백업 요구사항에 적합합니다.

- 여러 시점의 파일 상태 보존
- 백업 데이터의 클라이언트 측 암호화
- 동일 데이터의 중복 저장 감소
- Local·SFTP·S3·REST Server 등 다양한 Backend 사용
- 특정 Snapshot 또는 파일 단위 복구
- Repository 구조와 저장 데이터 무결성 검사

Restic은 다음 용도로 사용하지 않습니다.

- 실시간 파일 동기화 자체
- 데이터베이스의 실시간 Replication
- 장애 시 자동 Failover
- 애플리케이션 내부 상태 판별
- 랜섬웨어 감염 자체 차단
- 애플리케이션 트랜잭션 정합성 자동 보장

### 문서 적용 범위

```text
백업 대상
├── OS 설정·설정 파일
├── 애플리케이션 데이터
├── 컨테이너 볼륨
├── 데이터베이스 Export / Dump
├── 로그·아카이브
└── 클라우드·오브젝트 데이터

보호 계층
├── Restic Snapshot
├── 원격 Backend
├── 보존 정책
├── 무결성 검사
└── 실제 복구 테스트
```

실시간 복제나 애플리케이션별 일관성 확보는 대상 시스템의 전용 기능으로 먼저 처리한 뒤, 결과물을 Restic으로 백업합니다.

### 최신 버전

공식 GitHub Releases에서 2026-09-21에 확인한 최신 릴리스는 `v0.19.1`입니다. 설치 후 실제 실행 파일의 버전을 확인합니다.

```bash
restic version
```

버전은 운영체제 패키지 저장소 버전과 공식 릴리스 버전이 다를 수 있으므로, 설치 후 다음 항목을 기록합니다.

- Restic 버전
- 운영체제와 아키텍처
- Backend 종류
- Repository 형식 버전
- 백업 스크립트와 보존 정책

### 파일 동기화·Snapshot·애플리케이션 백업 비교

| 구분              | 파일 동기화         | Restic             | 애플리케이션 전용 백업  |
|-------------------|---------------------|--------------------|-------------------------|
| 목적              | 현재 파일 상태 반영 | Snapshot 백업·복구 | 서비스 내부 정합성 보장 |
| 시간 특성         | 이벤트·스케줄 기반  | 스케줄 기반        | 애플리케이션별 상이     |
| 과거 시점         | 별도 보존 구성 필요 | Snapshot으로 보존  | 기능에 따라 지원        |
| 파일 암호화       | 별도 구성           | Repository 암호화  | 제품별 상이             |
| 애플리케이션 인지 | 없음                | 없음               | 있음                    |
| 주요 예시         | 파일 복제·전송      | Restic Repository  | DB Dump·Replication     |

Restic은 파일을 백업하지만 애플리케이션의 트랜잭션이나 데이터 구조를 자동으로 이해하지 않습니다. 애플리케이션별 Export·Dump·Snapshot을 먼저 생성하고 그 결과를 Restic으로 저장하는 계층형 구성이 안전합니다.

## 2. 핵심 동작

### Snapshot

Restic은 백업 실행마다 Snapshot을 생성합니다.

```text
Snapshot 01  정상 상태
Snapshot 02  파일 추가
Snapshot 03  파일 변경
Snapshot 04  일부 파일 삭제
```

원본에서 파일이 삭제되거나 변경되어도 이전 Snapshot은 즉시 사라지지 않습니다. `forget`과 `prune`으로 보존 정책을 적용하기 전까지 복구 대상으로 남아 있습니다.

Snapshot에는 다음 정보가 포함됩니다.

- 백업 시각
- 호스트 정보
- 백업 경로
- 파일 경로와 메타데이터
- 저장 데이터에 대한 참조
- Repository 내부 데이터 구조 정보

Snapshot은 파일시스템의 단순 복사본이 아니므로 일반 파일 관리 명령어로 내용을 조작하지 않습니다.

### 암호화

파일 데이터와 Repository 메타데이터는 Restic Client에서 처리된 뒤 Repository에 저장됩니다.

```text
원본 파일
   │
   v
Restic Client
   ├── 데이터 분할·중복 제거
   ├── 암호화
   └── Repository 기록
        │
        v
Local / S3 / SFTP / REST
```

Repository 접근에는 별도 비밀번호가 필요합니다.

```text
AWS IAM 자격증명
└── S3 Bucket 접근 권한

Restic Repository Password
└── 백업 데이터 복호화 권한
```

두 값은 서로 대체할 수 없습니다. Repository 비밀번호를 잃어버리면 S3 객체를 가지고 있어도 백업을 복호화할 수 없습니다.

### 중복 제거

Restic은 Snapshot 간 동일한 데이터의 중복 저장을 줄입니다.

```text
첫 번째 백업
└── 전체 데이터 저장

두 번째 백업
├── 기존 데이터 재사용
└── 변경된 데이터만 추가
```

중복 제거는 저장 공간을 줄이는 데 유리하지만, 백업 실행 시 원본 파일을 스캔하고 변경 여부를 판단하는 비용은 발생합니다.

### 파일 변경 감지

Restic은 매번 모든 파일 내용을 다시 읽지 않을 수 있습니다. 공식 문서 기준 Linux의 일반적인 변경 감지에는 다음 메타데이터가 사용됩니다.

- 경로
- mtime
- ctime
- 파일 크기
- inode

내용만 변경되었지만 관련 메타데이터가 동일하면 파일을 변경되지 않은 것으로 판단할 가능성이 있습니다. 전체 파일을 다시 읽으려면 다음을 사용합니다.

```bash
restic backup --force /path/to/data
```

`--force`는 변경 감지를 끄고 파일을 다시 스캔하지만, 실행 중인 데이터베이스의 논리적 정합성까지 보장하지는 않습니다.

## 3. Repository와 Backend

### Repository 구조

Restic Repository에는 Snapshot·Index·Pack·Key 등 Restic이 관리하는 데이터가 저장됩니다. 다음 원칙을 지킵니다.

- Repository 내부 파일을 직접 이동·수정하지 않습니다.
- 일반 파일 복사 도구로 일부 객체만 복사하지 않습니다.
- Repository 비밀번호를 백업 대상과 같은 서버에만 보관하지 않습니다.
- Repository 자체도 별도 백업 또는 복제 전략을 검토합니다.
- `restic check`와 실제 `restore`를 함께 수행합니다.

### Backend 비교

| Backend       | 장점                       | 주의사항                         |
|---------------|----------------------------|----------------------------------|
| Local         | 가장 단순하고 빠른 테스트  | 동일 호스트 장애·랜섬웨어에 취약 |
| SFTP          | 일반 SSH 서버 활용         | 네트워크·SSH 권한 관리 필요      |
| REST Server   | Restic 전용 서버 구성 가능 | 서버 운영·append-only 설계 검토  |
| Amazon S3     | 원격·확장성·Lifecycle 활용 | IAM·비용·삭제 권한 관리 필요     |
| S3-compatible | MinIO·호환 스토리지 활용   | 호환성·API 차이 검증 필요        |

### S3 Repository 경로

Restic 공식 문서의 S3 Backend 형식은 다음과 같습니다.

```text
s3:s3.amazonaws.com/<bucket>/<prefix>
```

예시에서는 표준 예시 버킷을 사용합니다.

```bash
export RESTIC_REPOSITORY='s3:s3.amazonaws.com/my-bucket/restic/server-a'
```

S3 Bucket 이름과 Prefix는 환경별로 분리합니다.

```text
s3://my-bucket/restic/server-a/
s3://my-bucket/restic/server-b/
s3://my-bucket/restic/test/
```

## 4. 기본 사용 흐름

### 환경 변수와 비밀번호 파일

```bash
export RESTIC_REPOSITORY='s3:s3.amazonaws.com/my-bucket/restic/server-a'
export RESTIC_PASSWORD_FILE='/etc/restic/server-a.password'
export AWS_PROFILE='backup-profile'
```

비밀번호 파일 권한을 제한합니다.

```bash
sudo install -d -o root -g root -m 700 /etc/restic
sudo install -o root -g root -m 600 \
  /dev/null /etc/restic/server-a.password
```

비밀번호는 쉘 History·Git·일반 로그에 남기지 않습니다.

### Repository 초기화

새 Repository를 최초 한 번 초기화합니다.

```bash
restic init
```

Repository를 초기화한 뒤 다음을 확인합니다.

```bash
restic snapshots
restic check
```

### 파일 백업

```bash
restic backup \
  --tag server-a \
  --tag system \
  /etc \
  /var/backups
```

백업 대상은 명시적으로 지정합니다. `/` 전체를 백업할 때는 다음 항목을 제외하는 방안을 검토합니다.

- `/proc`
- `/sys`
- `/dev`
- `/run`
- `/tmp`
- 다른 파일시스템 Mount Point
- Cache와 임시 파일

제외 규칙은 실제 복구 요구사항과 함께 테스트합니다.

```bash
restic backup \
  --exclude-caches \
  --exclude '/var/cache' \
  --tag system \
  /etc /var/lib
```

### Snapshot 조회

```bash
restic snapshots
restic snapshots --tag server-a
restic ls latest
```

Snapshot ID를 확인한 뒤 특정 Snapshot의 파일을 조회할 수 있습니다.

### 복구

최신 Snapshot을 테스트 디렉터리에 복구합니다.

```bash
restic restore latest \
  --target /var/tmp/restore-test
```

특정 파일만 복구할 수 있습니다.

```bash
restic restore latest \
  --target /var/tmp/restore-test \
  --include '/etc/nginx/nginx.conf'
```

운영 경로에 직접 복구하기 전에 반드시 별도 테스트 경로에서 확인합니다. 복구 중 중단되면 대상 경로가 부분적으로 복원될 수 있습니다.

### 표준 출력 또는 명령 결과 백업

Restic은 명령의 표준 출력도 Snapshot으로 저장할 수 있습니다.

```bash
restic backup \
  --stdin-filename=inventory.txt \
  --stdin-from-command \
  -- sh -c 'hostname; date; find /etc -maxdepth 1 -type f -print'
```

이 방식은 Dump·명령 결과·설정 목록을 별도 임시 파일 없이 저장할 때 사용할 수 있습니다.

## 5. 보존 정책과 무결성 검사

### `forget`과 `prune`

두 명령은 역할이 다릅니다.

```text
forget
└── 보존 정책에 따라 Snapshot 참조 제거

prune
└── 더 이상 참조되지 않는 실제 데이터 정리
```

예시 정책을 먼저 dry-run으로 확인합니다.

```bash
restic forget \
  --dry-run \
  --keep-daily 7 \
  --keep-weekly 4 \
  --keep-monthly 12
```

결과를 확인한 뒤 실제 정리를 수행합니다.

```bash
restic forget \
  --keep-daily 7 \
  --keep-weekly 4 \
  --keep-monthly 12 \
  --prune
```

`prune`은 Repository를 잠그고 상당한 시간과 I/O를 사용할 수 있습니다. 정기 백업 실행 시간과 겹치지 않도록 스케줄을 분리합니다.

### Repository 검사

구조와 Index를 검사합니다.

```bash
restic check
```

저장 데이터까지 읽어 검사합니다.

```bash
restic check --read-data
```

전체 읽기 검사는 S3 요청·네트워크·복호화·디스크 I/O를 발생시키므로 Repository 크기에 맞춰 주기를 정합니다.

### 복구 테스트

백업 성공 로그만으로 복구 가능성을 보장할 수 없습니다.

```bash
mkdir -p /var/tmp/restore-test
restic restore latest --target /var/tmp/restore-test
find /var/tmp/restore-test -maxdepth 3 -type f | sort | head -50
```

복구 테스트의 통과 기준을 기록합니다.

| 테스트            | 통과 기준                      |
|-------------------|--------------------------------|
| Snapshot 조회     | 예상한 호스트·경로·시각 확인   |
| 파일 복구         | 파일 내용·권한·소유자 확인     |
| Repository 검사   | `restic check` 오류 없음       |
| 데이터 검사       | 정한 주기의 `--read-data` 통과 |
| 애플리케이션 복구 | 테스트 서비스가 정상 기동      |
| 복구 시간         | 정한 RTO 이내 완료             |

## 6. 애플리케이션 일관성 백업

### Restic이 직접 보장하지 않는 것

Restic은 파일과 디렉터리를 저장하고 Repository 무결성을 검사하지만, 애플리케이션 내부 상태를 판별하지 않습니다.

```text
Restic
├── 파일 내용 저장
├── 파일 메타데이터 저장
└── Repository 무결성 검사

애플리케이션 전용 절차
├── 트랜잭션 정합성
├── 데이터베이스 Dump
├── Table·Collection Lock
├── 열린 파일 처리
└── 애플리케이션 복구 순서
```

### 백업 전 정합성 확보

백업 대상에 따라 다음 방식 중 하나를 선택합니다.

| 대상 유형          | 백업 전 처리                | Restic 대상               |
|--------------------|-----------------------------|---------------------------|
| 정적 설정 파일     | 별도 처리 없음              | 원본 디렉터리             |
| 열린 로그 파일     | 로그 로테이션 또는 Flush    | 닫힌 로그 archive         |
| 데이터베이스       | Export·Dump·Snapshot        | Dump 또는 일관성 Snapshot |
| 컨테이너 볼륨      | 애플리케이션 정지 또는 Hook | 볼륨·Export 결과          |
| VM 이미지          | Guest quiesce 또는 Snapshot | 닫힌 이미지 파일          |
| 메시지·객체 저장소 | Export·Checkpoint           | Export 파일               |

파일이 백업 중 변경되면 Restic이 파일을 읽는 시점에 따라 일관되지 않은 결과가 저장될 수 있습니다. `--force`는 파일을 다시 읽게 할 뿐 애플리케이션 정합성을 만들어주지 않습니다.

### 명령 출력 백업

Restic은 명령의 표준 출력도 Snapshot으로 저장할 수 있습니다.

```bash
restic backup \
  --stdin-filename=application-export.dat \
  --stdin-from-command \
  -- /usr/local/bin/export_application --stdout
```

위 명령의 `/usr/local/bin/export_application`은 대상 시스템에 맞는 Export 명령으로 교체합니다. Export 명령이 실패하면 Restic 백업도 실패하도록 종료 코드를 확인합니다.

`export_application | restic backup --stdin`처럼 단순 파이프로 연결하면 원본 Export 명령의 실패가 백업 성공처럼 처리될 수 있습니다. 외부 명령의 종료 상태까지 확인해야 할 때는 `--stdin-from-command` 방식을 사용합니다.

### 데이터베이스 적용 원칙

데이터베이스마다 다음 절차를 별도로 검증합니다.

1. 일관성 있는 Dump·Export 또는 Snapshot 생성
2. Export 결과의 생성 완료 여부 확인
3. Restic으로 Export 결과 백업
4. 복구 테스트 환경에 Export 복원
5. 애플리케이션 연결과 데이터 검증
6. 필요한 경우 Export 이후 로그·이벤트 재생

데이터베이스의 물리 데이터 디렉터리를 실행 중인 상태에서 직접 백업하는 방식은 제품별 정합성 보장이 없으므로 기본값으로 사용하지 않습니다.

### 복구 순서

```text
1. 대상 시스템 중지 또는 복구 모드 진입
2. Restic Snapshot 복원
3. 애플리케이션별 Import·Restore 수행
4. 데이터 구조·권한·인덱스 검사
5. 로그·이벤트·변경 이력 재생
6. 애플리케이션 기동
7. 기능·데이터 무결성 검증
```

## 7. S3와 랜섬웨어 대응

### S3 권한 분리

Restic 백업을 수행하는 A 서버에 S3 전체 관리 권한을 주지 않습니다.

```text
A Server backup role
├── 특정 Bucket Prefix에 객체 생성
├── 필요한 객체 조회
└── 기존 Snapshot·객체 삭제 권한 없음

Backup maintenance role
├── forget
├── prune
└── 정책 변경
```

A 서버가 침해되었을 때 공격자가 S3의 과거 백업까지 삭제하거나 Restic `forget`·`prune`을 수행할 수 있으면 백업 복구력이 약해집니다.

### Versioning과 Object Lock

> Immutable Retention: 보존 기간 동안 백업 객체의 수정·삭제를 제한하는 정책입니다. 암호화와 달리 데이터 노출을 막는 기능이 아니라 백업 변경·삭제를 어렵게 만드는 기능입니다.

S3 Versioning·Object Lock·별도 백업 계정은 랜섬웨어 대응을 강화할 수 있습니다. 다만 Active Restic Repository는 `forget`·`prune` 과정에서 객체 유지·삭제 동작이 필요할 수 있으므로 Object Lock 보존 정책과의 호환성을 테스트합니다.

권장 방향은 다음 중 하나입니다.

- Active Restic Repository: Versioning + 최소 IAM 권한
- 별도 보존 Bucket: Immutable retention 또는 Object Lock 검토
- 별도 AWS 계정: 운영 계정과 백업 계정 분리
- 장기 보존 복사본: 운영 Repository와 별도 Lifecycle 적용

### Restic Repository 비밀번호

Repository 비밀번호는 다음 위치에 함께 두지 않습니다.

```text
❌ 백업 대상 디렉터리
❌ Git Repository
❌ 평문 쉘 스크립트
❌ S3 Bucket과 동일한 접근 경로
❌ A 서버에서 누구나 읽을 수 있는 파일
```

비밀번호를 잃어버리면 S3 객체를 보유하고 있어도 복구할 수 없습니다. 복구 책임자와 비상 절차를 별도로 정합니다.

## 8. 운영 설계와 검증

### RPO·RTO

> RPO(Recovery Point Objective): 장애 발생 시 허용할 수 있는 데이터 손실 시점입니다. 예를 들어 RPO가 1시간이면 최대 1시간 전 백업까지의 손실을 감수합니다.
>
> RTO(Recovery Time Objective): 장애 발생 후 서비스를 복구하는 데 허용되는 최대 시간입니다.

백업 주기는 RPO에 맞추고, 복구 절차는 RTO에 맞춰 검증합니다.

```text
Backup interval
└── RPO에 영향

Restore size·network·procedure
└── RTO에 영향
```

### 권장 구성

```text
Production data
      │
      ├── Application-consistent export
      │       └── Restic Snapshot
      │
      └── Filesystem-consistent data
              └── Restic Snapshot
                          │
                          v
                    Remote Repository
                    ├── S3
                    ├── SFTP
                    └── REST Server
```

실시간 복제나 애플리케이션별 Standby가 필요한 경우에는 해당 시스템의 전용 기능을 Restic과 함께 사용합니다. Restic은 복구용 Snapshot 계층을 담당합니다.

### 백업 자동화

`systemd timer`나 스케줄러에서 백업 명령을 실행하되, 실행 자체가 아니라 **최근 성공한 Snapshot 존재 여부**를 모니터링합니다.

```ini
[Unit]
Description=Restic backup

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/restic-backup.sh
```

```ini
[Unit]
Description=Run Restic backup periodically

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

운영 스크립트는 다음 결과를 기록합니다.

- Restic 종료 코드
- Snapshot ID
- 백업 시작·종료 시각
- 처리 파일 수와 데이터 크기
- Repository·S3 오류
- Lock 오류
- 디스크·S3 용량 부족

### Repository Lock과 Key 관리

비정상 종료 후 Repository Lock이 남을 수 있습니다.

```bash
restic unlock
```

실행 중인 `backup`·`prune`이 없는지 확인한 뒤 stale Lock에만 사용합니다. 실행 중인 작업을 확인하지 않고 Lock을 제거하면 Repository 손상이 발생할 수 있습니다.

Repository Key를 확인하고 관리합니다.

```bash
restic key list
restic key add
restic key remove
```

새 Key로 실제 Repository 접근과 복구를 확인하기 전 기존 Key를 제거하지 않습니다. `key remove`는 해당 Key를 사용하는 복구 경로를 끊을 수 있으므로 실행 전 승인과 기록을 남깁니다. Repository Password와 Key 관리 절차는 비상 복구 담당자와 함께 보관합니다.

### 운영 주기 예시

| 주기          | 작업                       | 확인 항목                  |
|---------------|----------------------------|----------------------------|
| 백업 실행마다 | `restic backup`            | 종료 코드·Snapshot 생성    |
| 매일          | `restic snapshots`         | 최신 백업 존재 여부        |
| 매주          | `restic check`             | Repository 구조·Index      |
| 매월          | `restic check --read-data` | 저장 데이터 읽기 검증      |
| 매월          | `restic restore`           | 파일 또는 Export 실제 복구 |
| 분기별        | 전체 복구 훈련             | 복구 절차·RPO·RTO          |

운영 환경에서 매월 전체 `--read-data`가 부담되면 데이터 크기와 비용을 기준으로 주기를 조정하되, 일부 데이터 검증과 전체 복구 훈련을 함께 운영합니다.

### 복구 성공 기준

```text
파일 복구 성공
→ 파일이 생성됨

서비스 복구 성공
→ 서비스가 기동됨
→ 설정·권한·데이터 구조가 정상
→ 주요 기능 Smoke Test 통과
→ 정한 RTO 이내 완료
```

### 파일 동기화·Restic·전용 백업의 역할 분리

```text
파일 동기화
└── 현재 상태 반영·staging

Restic
└── 과거 Snapshot·암호화·장기 보존·복구

애플리케이션 전용 백업
└── 트랜잭션·데이터 구조·Export 정합성

S3 Versioning/Object Lock
└── 백업 삭제·변조에 대한 추가 방어
```

Restic은 파일 동기화나 데이터베이스 전용 백업을 단순히 대체하는 도구가 아닙니다. 각 계층의 정합성·보존·복구 책임을 분리하고, Restic은 공통 Snapshot 백업 계층으로 사용합니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- Restic Documentation: [restic.readthedocs.io](https://restic.readthedocs.io/en/stable/) — ★★★★☆
- Restic S3 Backend: [030_preparing_a_new_repo.html](https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html) — ★★★★☆
- Restic Backup and Change Detection: [040_backup.html](https://restic.readthedocs.io/en/stable/040_backup.html) — ★★★★☆
- Restic Retention and Prune: [060_forget.html](https://restic.readthedocs.io/en/stable/060_forget.html) — ★★★★☆
- Restic Releases: [github.com/restic/restic/releases](https://github.com/restic/restic/releases) — ★★★☆☆
- [Restic 공식 참조 노트](../../_reference/restic_official_notes.md)
- [S3·IAM·KMS 참조 노트](../../_reference/aws_sts_iam_s3_kms_official_notes.md)

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

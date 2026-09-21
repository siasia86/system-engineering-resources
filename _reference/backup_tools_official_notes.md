---
name: backup-tools-official-notes
description: 파일 미러링·Snapshot·암호화 백업·엔터프라이즈 백업 도구의 공식 기능 범위 참조 노트.
tags:
  - backup
  - rsnapshot
  - lsyncd
  - bacula
  - borg
  - duplicity
  - amanda
  - bareos
  - rclone
last_checked: 2026-09-21
sources:
  - https://rsnapshot.org/
  - https://github.com/lsyncd/lsyncd
  - https://www.bacula.org/
  - https://www.borgbackup.org/
  - https://duplicity.us/
  - https://www.amanda.org/
  - https://www.bareos.com/
  - https://rclone.org/
---

# 백업 도구 공식 참조 노트

## 1. 도구별 공식 범위

### rsnapshot

- rsync 기반 파일시스템 Snapshot 유틸리티입니다.
- Local 또는 SSH를 통한 원격 호스트를 주기적으로 Snapshot할 수 있습니다.
- Hard Link를 활용하여 Snapshot 간 중복 공간을 줄입니다.
- 고정·설정 가능한 Snapshot 보존 수를 사용합니다.

### lsyncd

- 파일시스템 이벤트를 감시하고 rsync 기반 동기화를 실행하는 도구입니다.
- 이벤트 기반 파일 미러링에 사용합니다.
- 애플리케이션 정합성, Snapshot 보존, 랜섬웨어 방어를 자체 제공하는 백업 엔진으로 간주하지 않습니다.

### Bacula

- 네트워크상의 여러 컴퓨터를 대상으로 백업·복구·검증을 관리하는 오픈소스 백업 소프트웨어입니다.
- Director, File Daemon, Storage Daemon, Catalog 등 중앙 관리 구성요소를 사용합니다.
- Full·Differential·Incremental·Synthetic 계열 작업과 저장소 관리 기능을 제공합니다.
- Community와 Enterprise 제공 범위를 구분합니다.

### BorgBackup

- 중복 제거·압축·인증 암호화를 제공하는 공간 효율적인 백업 아카이버입니다.
- Content-defined chunking으로 저장 데이터를 분할합니다.
- Repository에 Archive를 만들고 Archive를 조회·검사·복구합니다.

### Duplicity

- librsync 기반의 암호화·대역폭 효율적 증분 백업 도구입니다.
- 암호화된 tar 형식 Volume을 Local 또는 원격 파일 서버에 저장합니다.
- GnuPG를 사용하여 Archive를 암호화하거나 서명할 수 있습니다.

### Amanda

- 여러 호스트를 네트워크를 통해 디스크·테이프·광학 미디어·클라우드에 백업하는 네트워크 백업 시스템입니다.
- 표준 `dump/restore`, GNU Tar 등 기본 아카이브 도구를 활용합니다.
- 중앙 Master Backup Server에서 다수 호스트를 관리하는 구조입니다.

### Bareos

- Linux·Windows·혼합 엔터프라이즈 환경을 대상으로 하는 오픈소스 백업·복구 소프트웨어입니다.
- 물리 시스템·가상 머신·데이터베이스·애플리케이션을 디스크·테이프·S3-compatible object storage에 백업할 수 있습니다.
- Full·Differential·Incremental·Always Incremental 전략과 중앙 관리·스케줄링을 제공합니다.
- AGPLv3 기반 오픈소스와 Subscription·지원 범위를 구분합니다.

### rclone

- Local·Cloud Storage 간 파일 복사·동기화에 사용하는 도구입니다.
- `copy`와 `sync`는 백업 엔진의 Snapshot 보존과 다릅니다.
- Destination의 Versioning·Object Lock과 함께 사용해야 백업 보존 성격을 강화할 수 있습니다.

## 2. 공식 범위에서 확인해야 할 경계

- 파일 동기화 도구는 현재 상태를 반영하지만 과거 Snapshot을 자동 보존하지 않을 수 있습니다.
- Snapshot·Archive 도구는 과거 상태를 보존하지만 애플리케이션 트랜잭션 정합성을 자동으로 보장하지 않습니다.
- 데이터베이스·VM·컨테이너 볼륨은 제품별 Export·Quiesce·Snapshot 절차를 먼저 적용해야 합니다.
- 암호화는 저장 데이터의 기밀성을 높이지만 삭제·변조·자격증명 탈취를 자동으로 막지 않습니다.
- S3 Versioning·Object Lock·별도 IAM 계정은 백업 도구와 별도의 보존·접근제어 계층입니다.

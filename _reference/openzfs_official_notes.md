---
name: openzfs-official-notes
description: OpenZFS 공식 문서 기반 COW·checksum·Snapshot·pool·RAIDZ·복제·압축·암호화 참조 노트.
tags:
  - zfs
  - openzfs
  - filesystem
  - storage
  - snapshot
last_checked: 2026-09-21
sources:
  - https://openzfs.org/
  - https://github.com/openzfs/zfs
  - https://openzfs.github.io/openzfs-docs/
---

# OpenZFS 공식 참조 노트

## 1. 프로젝트 범위

- OpenZFS는 Linux·FreeBSD·illumos 등에서 사용하는 ZFS 구현 프로젝트입니다.
- COW 파일시스템, Storage Pool, Dataset, Snapshot·Clone을 제공합니다.
- Linux에서는 배포판·커널·OpenZFS 모듈 버전 조합을 함께 검증해야 합니다.

## 2. 핵심 기능

- 데이터·메타데이터 checksum
- Mirror·RAIDZ 계열의 데이터 중복성
- 투명 압축
- 암호화
- Snapshot·Clone
- `zfs send`·`zfs receive` 기반 로컬·원격 복제
- Scrub과 pool 상태 점검
- Dataset·Quota·Reservation

## 3. 운영 경계

- Snapshot은 같은 pool 장애를 대신하는 오프사이트 백업이 아닙니다.
- RAIDZ·Mirror는 백업이 아니라 저장소 장애 대응 계층입니다.
- Pool·vdev 구성은 생성 후 변경 제약과 장애 복구 절차를 함께 검토합니다.
- `zpool create`, `zpool add`, `zpool destroy`, `zpool replace`는 대상 디스크와 데이터 유실 가능성을 확인한 뒤 수행합니다.
- OpenZFS 모듈과 사용자 도구의 버전 조합, 커널 업데이트, 부트 환경을 운영 전에 검증합니다.

---
name: restic-official-notes
description: Restic 공식 문서와 릴리스 기반 백업·Repository·S3·무결성 검사 참조 노트.
tags:
  - restic
  - backup
  - encryption
  - deduplication
  - s3
last_checked: 2026-09-21
sources:
  - https://restic.readthedocs.io/en/stable/
  - https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html
  - https://restic.readthedocs.io/en/stable/040_backup.html
  - https://restic.readthedocs.io/en/stable/060_forget.html
  - https://restic.readthedocs.io/en/stable/075_examples.html
  - https://github.com/restic/restic/releases/latest
---

# Restic 공식 참조 노트

## 1. 버전과 프로젝트 범위

- 공식 최신 릴리스 확인값: `v0.19.1`.
- Restic은 암호화된 Repository에 파일 Snapshot을 저장하는 백업 도구입니다.
- Local, SFTP, REST Server, Amazon S3, S3-compatible storage 등 여러 Backend를 지원합니다.
- Repository 접근에는 별도 비밀번호가 필요하며, Repository에는 여러 키를 둘 수 있습니다.

## 2. 백업 동작

- 백업 실행마다 Snapshot을 생성합니다.
- 데이터 중복 제거를 통해 이미 저장된 데이터의 재저장을 줄입니다.
- 파일 변경 감지는 경로와 파일 메타데이터를 이용해 재스캔 여부를 판단합니다.
- Linux에서 기본 변경 감지에는 mtime, ctime, 파일 크기, inode가 사용됩니다.
- `--force`를 사용하면 변경 감지를 끄고 파일을 다시 스캔합니다.
- `--stdin-from-command`로 명령 출력 결과를 Snapshot에 저장할 수 있습니다.

## 3. Repository 관리

- `restic check`는 Repository 구조와 Index를 검사합니다.
- `restic check --read-data`는 저장 데이터를 실제로 읽어 무결성을 확인하므로 비용과 시간이 증가합니다.
- Snapshot 삭제 정책은 `forget`으로 지정합니다.
- 삭제된 Snapshot이 참조하지 않는 데이터를 제거하려면 `prune`이 필요합니다.
- `prune`은 Repository를 잠그고 실행될 수 있으므로 백업 시간과 분리하는 것이 좋습니다.
- 복구는 `restore`로 수행하며, 실제 복구 테스트가 필요합니다.

## 4. MySQL Dump와 S3

- 공식 예제는 `--stdin-from-command`와 `mysqldump`를 결합하여 SQL 출력을 Snapshot에 저장합니다.
- Amazon S3 Backend는 S3 Bucket과 AWS 인증정보를 사용합니다.
- 공식 문서는 S3 Backend에 Path-style URL 형식을 사용하도록 안내합니다.
- S3 자격증명과 Restic Repository 비밀번호는 서로 다른 보호 대상입니다.

## 5. 공식 문서 확인 원칙

- 파일 변경 감지는 애플리케이션 데이터의 논리적 정합성을 판별하지 않습니다.
- 데이터베이스는 일관성 있는 Dump·Snapshot·binlog 보존 절차를 별도로 설계해야 합니다.
- 운영 적용 전 `backup`, `check`, `restore`, 보존 정책을 테스트 Repository에서 검증합니다.

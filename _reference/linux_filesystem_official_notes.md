---
name: linux-filesystem-official-notes
description: Linux 디스크 파일시스템(ext4, xfs, btrfs) 문서 작성 시 참조할 공식 소스. 01_fundamentals/linux/ 문서 생성/검토 시 참조.
tags:
  - linux
  - filesystem
  - ext4
  - xfs
  - btrfs
  - vfs
last_checked: 2026-07-22
sources:
  - https://docs.kernel.org/filesystems/index.html
  - https://docs.kernel.org/filesystems/ext4/index.html
  - https://docs.kernel.org/filesystems/xfs/index.html
  - https://docs.kernel.org/filesystems/btrfs.html
  - https://man7.org/linux/man-pages/man5/fstab.5.html
  - https://man7.org/linux/man-pages/man8/mount.8.html
  - https://man7.org/linux/man-pages/man8/mkfs.8.html
  - https://man7.org/linux/man-pages/man8/fsck.8.html
  - https://man7.org/linux/man-pages/man8/tune2fs.8.html
  - https://man7.org/linux/man-pages/man8/xfs_info.8.html
---

# Linux Filesystem 공식 참조 노트

## 1. VFS (Virtual Filesystem Switch)

### 공식 소스

| 소스               | URL                                                 | 용도                     |
|--------------------|-----------------------------------------------------|--------------------------|
| VFS overview       | https://docs.kernel.org/filesystems/vfs.html        | VFS 아키텍처, inode 구조 |
| path-lookup        | https://docs.kernel.org/filesystems/path-lookup.html | 경로 탐색 알고리즘       |
| Linux Source       | fs/inode.c, fs/super.c, fs/dcache.c                 | inode/superblock 구현    |

### 검증된 사실 (2026-07-17)

| 항목                      | 값                                           | 출처                     |
|---------------------------|----------------------------------------------|--------------------------|
| VFS 주요 객체             | superblock, inode, dentry, file              | docs.kernel.org/vfs      |
| inode 포함 메타데이터     | size, permission, timestamps, block pointers | docs.kernel.org/vfs      |
| dentry 역할               | filename → inode 매핑 (캐시)                 | docs.kernel.org/vfs      |
| superblock 역할           | 파일시스템 메타 (블록 크기, 상태, 마운트 옵션) | docs.kernel.org/vfs    |

## 2. ext4

### 공식 소스

| 소스            | URL                                                  | 용도                    |
|-----------------|------------------------------------------------------|-------------------------|
| ext4 docs       | https://docs.kernel.org/filesystems/ext4/index.html  | 온디스크 레이아웃       |
| ext4 wiki       | https://ext4.wiki.kernel.org/                        | FAQ, 히스토리           |
| tune2fs.8       | https://man7.org/linux/man-pages/man8/tune2fs.8.html | ext4 튜닝 파라미터      |
| e2fsprogs       | https://e2fsprogs.sourceforge.net/                   | 유틸리티 소스           |

### 검증된 사실 (2026-07-17)

| 항목                    | 값                                     | 출처                        |
|-------------------------|----------------------------------------|-----------------------------|
| 최대 파일 크기          | 16 TiB (4K block)                      | docs.kernel.org/ext4        |
| 최대 볼륨 크기          | 1 EiB                                  | docs.kernel.org/ext4        |
| 기본 블록 크기          | 4096 bytes                             | mkfs.ext4 기본값            |
| inode 크기 기본값       | 256 bytes                              | mkfs.ext4 기본값            |
| 저널 모드               | ordered (기본), journal, writeback     | docs.kernel.org/ext4        |
| extent 기반             | ext4부터 (ext3은 indirect block)       | docs.kernel.org/ext4        |
| delayed allocation      | 기본 활성화                            | docs.kernel.org/ext4        |
| 온라인 리사이즈          | 지원 (resize2fs)                       | resize2fs.8                 |
| metadata checksums      | 지원 (metadata_csum, 기본 활성)        | docs.kernel.org/ext4        |
| ext2 → ext3 → ext4     | 하위 호환 마운트 가능                  | ext4.wiki.kernel.org        |

## 3. XFS

### 공식 소스

| 소스              | URL                                                 | 용도                |
|-------------------|-----------------------------------------------------|---------------------|
| xfs docs          | https://docs.kernel.org/filesystems/xfs/index.html  | XFS 내부 구조       |
| xfsprogs          | https://xfs.wiki.kernel.org/                        | xfs_admin, xfs_info |
| xfs_info.8        | https://man7.org/linux/man-pages/man8/xfs_info.8.html | 파일시스템 정보    |

### 검증된 사실 (2026-07-17)

| 항목                   | 값                                          | 출처                     |
|------------------------|---------------------------------------------|--------------------------|
| 최대 파일 크기         | 8 EiB                                       | docs.kernel.org/xfs      |
| 최대 볼륨 크기         | 16 EiB                                      | docs.kernel.org/xfs      |
| 할당 그룹 (AG)         | 병렬 I/O용 독립 관리 영역                   | docs.kernel.org/xfs      |
| 저널                   | metadata only (기본), external 로그 가능    | xfs.wiki.kernel.org      |
| 온라인 확장            | 지원 (xfs_growfs)                           | xfs_growfs.8             |
| 온라인 축소            | 미지원                                      | xfs.wiki.kernel.org      |
| reflink (CoW)          | 지원 (mkfs.xfs -m reflink=1, RHEL 8+ 기본) | docs.kernel.org/xfs      |
| 기본 블록 크기         | 4096 bytes                                  | mkfs.xfs 기본값          |
| RHEL/Rocky 기본 FS     | XFS (RHEL 7+)                               | Red Hat 릴리즈 노트      |

## 4. Btrfs

### 공식 소스

| 소스          | URL                                              | 용도             |
|---------------|--------------------------------------------------|------------------|
| btrfs docs    | https://docs.kernel.org/filesystems/btrfs.html   | 커널 문서        |
| btrfs wiki    | https://btrfs.readthedocs.io/                    | 사용자 문서      |
| btrfs-progs   | https://github.com/kdave/btrfs-progs             | 유틸리티 소스    |

### 검증된 사실 (2026-07-17)

| 항목               | 값                                          | 출처                  |
|--------------------|---------------------------------------------|-----------------------|
| 최대 파일 크기     | 8 EiB (VFS 제한, 이론 16 EiB)               | btrfs.readthedocs.io  |
| 최대 볼륨 크기     | 16 EiB                                      | btrfs.readthedocs.io  |
| Copy-on-Write      | 전체 파일시스템 CoW                         | docs.kernel.org/btrfs |
| 스냅샷             | 서브볼륨 단위, O(1) 생성                    | docs.kernel.org/btrfs |
| RAID 레벨          | 0, 1, 10, 5/6 (5/6은 불안정)               | btrfs.readthedocs.io  |
| 투명 압축          | zlib, lzo, zstd                             | docs.kernel.org/btrfs |
| 온라인 확장/축소   | 둘 다 지원                                  | btrfs.readthedocs.io  |
| SUSE 기본 FS       | Btrfs (openSUSE 13.2+, SLES 12+)           | SUSE 릴리즈 노트      |

## 5. 핵심 명령어

### 공식 소스

| 소스      | URL                                              | 용도             |
|-----------|--------------------------------------------------|------------------|
| mount.8   | https://man7.org/linux/man-pages/man8/mount.8.html | 마운트 옵션     |
| fstab.5   | https://man7.org/linux/man-pages/man5/fstab.5.html | /etc/fstab 형식 |
| mkfs.8    | https://man7.org/linux/man-pages/man8/mkfs.8.html  | 파일시스템 생성 |
| fsck.8    | https://man7.org/linux/man-pages/man8/fsck.8.html  | 무결성 검사     |
| blkid.8   | https://man7.org/linux/man-pages/man8/blkid.8.html | UUID/타입 확인  |
| lsblk.8   | https://man7.org/linux/man-pages/man8/lsblk.8.html | 블록 디바이스   |

### 검증된 사실 (2026-07-17)

| 항목                          | 값                                     | 출처     |
|-------------------------------|----------------------------------------|----------|
| fstab 필드 순서               | device, mountpoint, type, options, dump, pass | fstab.5  |
| fstab UUID 사용 권장          | 디바이스명 변경 시 안정성 보장         | fstab.5  |
| mount -o remount              | 재마운트 (언마운트 없이 옵션 변경)     | mount.8  |
| fsck 실행 조건                | 언마운트 또는 read-only 마운트 상태    | fsck.8   |
| noatime                       | atime 업데이트 비활성 (성능 향상)      | mount.8  |
| relatime                      | atime 조건부 업데이트 (커널 2.6.30+ 기본) | mount.8 |

## 6. 저널링 (Journaling)

### 검증된 사실 (2026-07-17)

| 항목                | 값                                             | 출처                     |
|---------------------|------------------------------------------------|--------------------------|
| 저널링 목적         | crash 후 빠른 복구 (fsck 시간 단축)            | docs.kernel.org/ext4     |
| ext4 journal 모드   | data=ordered: 메타+데이터 순서 보장            | docs.kernel.org/ext4     |
| ext4 writeback 모드 | 메타만 저널, 데이터 순서 미보장 (성능 우선)    | docs.kernel.org/ext4     |
| ext4 journal 모드   | 메타+데이터 모두 저널 (가장 안전, 느림)        | docs.kernel.org/ext4     |
| XFS 저널            | metadata only (데이터 저널링 없음)             | docs.kernel.org/xfs      |
| Btrfs               | CoW 기반 — 전통적 저널 불필요                  | docs.kernel.org/btrfs    |

## 7. fsck/e2fsck 옵션 (공식 man page 기반)

### 공식 소스

| 소스       | URL                                                   | 용도             |
|------------|-------------------------------------------------------|------------------|
| fsck.8     | https://man7.org/linux/man-pages/man8/fsck.8.html     | fsck wrapper     |
| e2fsck.8   | https://man7.org/linux/man-pages/man8/e2fsck.8.html   | ext2/3/4 fsck    |
| xfs_repair | https://man7.org/linux/man-pages/man8/xfs_repair.8.html | XFS fsck       |
| tune2fs.8  | https://man7.org/linux/man-pages/man8/tune2fs.8.html  | ext 자동 검사 설정 |

### fsck (wrapper) — 파일시스템 종류별 자동 호출

```bash
fsck /dev/sdb          # 파일시스템 자동 감지 → fsck.ext4 또는 xfs_repair 호출
fsck -t ext4 /dev/sdb  # 명시적 타입 지정
fsck -A                # fstab의 모든 파일시스템 검사 (pass > 0)
fsck -AR -y            # 부팅 시 자동 검사 (initscripts 사용)
```

### e2fsck (ext2/ext3/ext4) 옵션

출처: https://man7.org/linux/man-pages/man8/e2fsck.8.html

| 옵션            | 설명                                              | 비고                        |
|-----------------|---------------------------------------------------|-----------------------------|
| `-f`            | 강제 검사 (clean 상태여도)                        | 항상 사용 권장              |
| `-y`            | 모든 질문에 yes 응답                              | 무인 실행 시                |
| `-n`            | 읽기 전용 (no 응답, 수정 안 함)                   | 마운트 상태에서도 안전      |
| `-p`            | 자동 복구 (안전한 것만, preen)                    | 부팅 시 자동 fsck           |
| `-v`            | 상세 출력                                         |                             |
| `-C 0`          | 진행률 표시 (fd=0, stdout)                        | 대용량 볼륨                 |
| `-D`            | 디렉토리 최적화 (re-indexing)                     |                             |
| `-b superblock` | 대체 superblock 사용                              | primary 손상 시             |
| `-B blocksize`  | 블록 크기 강제 지정                               |                             |
| `-c`            | badblocks 검사 (시간 소요)                        |                             |
| `-k`            | -c와 함께, 기존 bad block 목록 유지               |                             |
| `-l file`       | bad block 목록 추가                               |                             |
| `-L file`       | bad block 목록 교체                               |                             |
| `-j path`       | 외부 journal 경로 지정                            |                             |
| `-F`            | 버퍼 캐시 flush 후 검사                           |                             |
| `-d`            | 디버그 출력                                       |                             |
| `-t`            | 타이밍 통계                                       |                             |
| `-V`            | 버전 출력                                         |                             |

### 옵션 조합 제약 (man page 명시)

| 조합        | 가능 | 근거 (man page 원문)                                           |
|-------------|------|----------------------------------------------------------------|
| `-y` + `-n` | ❌   | "may not be specified at the same time as the -n or -p"        |
| `-y` + `-p` | ❌   | 동일                                                           |
| `-n` + `-p` | ❌   | "may not be specified at the same time as the -p or -y"        |
| `-f` + `-y` | ✅   |                                                                |
| `-f` + `-p` | ✅   |                                                                |
| `-c` + `-n` | ❌   | "-n option is specified, and -c, -l, or -L options are not"    |

### Exit Code (man page 원문)

| 코드 | 의미                                    |
|------|-----------------------------------------|
| 0    | No errors                               |
| 1    | File system errors corrected            |
| 2    | File system errors corrected, reboot    |
| 4    | File system errors left uncorrected     |
| 8    | Operational error                       |
| 16   | Usage or syntax error                   |
| 32   | E2fsck canceled by user request         |
| 128  | Shared library error                    |

🟡 Exit code는 OR 합산입니다. 예: 1+2=3 → "에러 수정 + 재부팅 필요".

### xfs_repair (XFS)

출처: https://man7.org/linux/man-pages/man8/xfs_repair.8.html

| 옵션 | 설명                              | 비고                   |
|------|-----------------------------------|------------------------|
| `-n` | 읽기 전용 (수정 안 함)            | 손상 여부만 확인       |
| `-v` | 상세 출력                         |                        |
| `-L` | 로그 초기화 (dirty log 강제 제거) | 🔴 데이터 유실 가능    |
| `-d` | 위험 복구 모드 (마운트 상태 허용) | 🔴 비상 시만 사용      |

🟡 XFS는 `fsck.xfs`가 존재하지만 아무것도 안 합니다 (no-op). 실제 복구는 `xfs_repair`를 사용합니다.

### tune2fs 자동 검사 설정

출처: https://man7.org/linux/man-pages/man8/tune2fs.8.html

```bash
# mount count 기반 자동 검사 (N회 마운트 후 fsck 실행)
tune2fs -c 30 /dev/sdb

# 시간 기반 자동 검사 (d=day, m=month, w=week)
tune2fs -i 30d /dev/sdb

# 자동 검사 비활성화
tune2fs -c 0 -i 0 /dev/sdb

# 현재 설정 확인
tune2fs -l /dev/sdb | grep -i "mount count\|maximum\|check interval"
```

### fstab pass 필드 (부팅 시 자동 fsck)

출처: https://man7.org/linux/man-pages/man5/fstab.5.html

| pass 값 | 동작                                      | 용도              |
|---------|-------------------------------------------|-------------------|
| 0       | fsck 실행 안 함                           | swap, tmpfs 등    |
| 1       | 루트 파일시스템 (가장 먼저 검사)          | / 전용            |
| 2       | 루트 외 파일시스템 (1 완료 후 병렬 검사)  | /home, /data 등   |

```
# fstab 예시
UUID=...  /        ext4  defaults  0 1    ← 루트, 먼저 검사
UUID=...  /data    ext4  defaults  0 2    ← 루트 후 검사
UUID=...  /backup  ext4  defaults  0 0    ← 검사 안 함
```

### 실행 전 필수 조건

| 조건                 | 이유                                         |
|----------------------|----------------------------------------------|
| 마운트 해제 필수     | 마운트 상태에서 수정 시 추가 손상 가능        |
| 또는 read-only 마운트 | `-n` 옵션만 안전                            |
| 백업 권장            | 심각한 손상 시 fsck가 데이터를 삭제할 수 있음 |
| single-user 모드 권장 | 다른 프로세스의 파일 접근 방지              |

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
last_checked: 2026-07-17
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

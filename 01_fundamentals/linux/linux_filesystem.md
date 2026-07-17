# Linux Filesystem — 디스크 파일시스템

Linux 디스크 파일시스템의 구조, 주요 파일시스템 비교, 마운트/관리 명령어를 정리합니다.

## 목차

| 섹션                                                                                                                     |
|--------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. VFS 아키텍처](#2-vfs-아키텍처) / [3. inode와 블록](#3-inode와-블록)                             |
| [4. ext4](#4-ext4) / [5. XFS](#5-xfs) / [6. Btrfs](#6-btrfs)                                                             |
| [7. 저널링](#7-저널링) / [8. 마운트와 fstab](#8-마운트와-fstab) / [9. 파일시스템 관리](#9-파일시스템-관리)               |
| [10. 파일시스템 비교](#10-파일시스템-비교) / [11. 트러블슈팅](#11-트러블슈팅) / [12. 배포판 기본 FS](#12-배포판-기본-fs) |

---

## 1. 개요

디스크 파일시스템은 블록 디바이스 위에 데이터를 구조화하여 저장하는 계층입니다. 파일/디렉토리를 생성·읽기·쓰기·삭제하며, crash 시 데이터 무결성을 보장하는 저널링을 포함합니다.

```
User Process
     |
     v
+------------------------------------------+
| VFS (Virtual File System)        |
| open(), read(), write(), close() |
+------------------------------------------+
     |              |              |
     v              v              v
+---------+  +----------+  +----------+
|  ext4   |  |   XFS    |  |  Btrfs   |
+---------+  +----------+  +----------+
     |              |              |
     v              v              v
+------------------------------------------+
|          Block Layer (I/O scheduler)      |
+------------------------------------------+
     |
     v
  /dev/sda, /dev/nvme0n1 ...
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. VFS 아키텍처

VFS(Virtual Filesystem Switch)는 커널이 여러 파일시스템을 동일한 인터페이스로 접근할 수 있게 하는 추상화 계층입니다.

### 핵심 객체

| 객체       | 역할                                                  |
|------------|-------------------------------------------------------|
| superblock | 파일시스템 메타데이터 (블록 크기, 상태, 마운트 옵션)  |
| inode      | 파일 메타데이터 (크기, 권한, 타임스탬프, 블록 포인터) |
| dentry     | 디렉토리 엔트리 캐시 (파일명 → inode 매핑)            |
| file       | 열린 파일 상태 (오프셋, 접근 모드, f_op)              |

### 경로 탐색 흐름

```
open("/home/sjyun/data.txt", O_RDONLY)
      |
      v
  dentry cache lookup: "/" > "home" > "sjyun" > "data.txt"
      |
      v (cache miss)
  filesystem-specific lookup (ext4_lookup)
      |
      v
  inode > data blocks > read
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. inode와 블록

### inode 구조

inode는 파일의 메타데이터를 저장합니다. 파일명은 inode가 아닌 dentry(디렉토리 엔트리)에 저장됩니다.

| 필드           | 설명                                 |
|----------------|--------------------------------------|
| i_mode         | 파일 타입 + 권한 (rwxr-xr-x)         |
| i_uid/i_gid    | 소유자/그룹                          |
| i_size         | 파일 크기 (bytes)                    |
| i_atime        | 마지막 접근 시간                     |
| i_mtime        | 마지막 수정 시간                     |
| i_ctime        | 메타데이터 변경 시간                 |
| i_blocks       | 할당된 블록 수                       |
| block pointers | 데이터 블록 위치 (ext4: extent tree) |

### 블록 할당

| 방식            | 파일시스템 | 설명                                         |
|-----------------|------------|----------------------------------------------|
| Indirect blocks | ext2/ext3  | 12 direct + 1 indirect + 1 double + 1 triple |
| Extent tree     | ext4       | (start_block, length) 쌍으로 연속 블록 표현  |
| B+ tree         | XFS        | AG 내 B+ tree로 블록 관리                    |
| CoW extent tree | Btrfs      | 쓰기 시 새 위치에 기록                       |

### inode 확인 명령어

```bash
# 파일의 inode 번호 확인
ls -i /etc/fstab

# inode 상세 (ext4)
stat /etc/fstab

# 파일시스템 inode 사용량
df -i

# ext4 inode 내부 구조 (debugfs)
sudo debugfs -R "stat <inode_number>" /dev/sda1
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. ext4

ext4는 Linux에서 가장 널리 사용되는 범용 파일시스템입니다. ext3에서 발전했으며 하위 호환을 유지합니다.

### 주요 특성

| 항목               | 값                                 |
|--------------------|------------------------------------|
| 최대 파일 크기     | 16 TiB (4K block)                  |
| 최대 볼륨 크기     | 1 EiB                              |
| 기본 블록 크기     | 4096 bytes                         |
| 기본 inode 크기    | 256 bytes                          |
| 저널링             | ordered (기본), journal, writeback |
| Extent 기반        | 연속 블록 효율적 관리              |
| Delayed allocation | 기본 활성 (단편화 감소)            |
| Online resize      | 지원 (resize2fs)                   |
| Metadata checksums | 지원 (metadata_csum)               |

### 생성 및 튜닝

```bash
# 파일시스템 생성
sudo mkfs.ext4 /dev/sdb1

# 라벨 지정
sudo mkfs.ext4 -L "data" /dev/sdb1

# reserved blocks 비율 확인/변경 (기본 5%)
sudo tune2fs -l /dev/sdb1 | grep "Reserved block count"
sudo tune2fs -m 1 /dev/sdb1    # 1%로 변경 (데이터 디스크)

# 저널 모드 확인
sudo tune2fs -l /dev/sdb1 | grep "Default mount options"

# 기능 활성화
sudo tune2fs -O metadata_csum /dev/sdb1
```

### ext4 디스크 레이아웃

```
+-------------------------------------------------------------+
| Block Group 0       | Block Group 1       | ... | Block Grp N |
+---------------------+---------------------+-----+-------------+
| SB | GDT | Bitmap  | SB | GDT | Bitmap  |  |  |
|    |     | Inode T |    |     | Inode T |  |  |
|    |     | Data    |    |     | Data    |  |  |
+---------------------+---------------------+-----+-------------+

SB      = Superblock
GDT     = Group Descriptor Table
Bitmap  = block bitmap + inode bitmap
Inode T = Inode Table
Data    = Data Blocks
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. XFS

XFS는 SGI에서 개발한 고성능 파일시스템입니다. RHEL 7부터 기본 파일시스템이며, 대용량 파일과 병렬 I/O에 최적화되어 있습니다.

### 주요 특성

| 항목           | 값                                |
|----------------|-----------------------------------|
| 최대 파일 크기 | 8 EiB                             |
| 최대 볼륨 크기 | 16 EiB                            |
| 기본 블록 크기 | 4096 bytes                        |
| 할당 그룹 (AG) | 병렬 I/O용 독립 관리 영역         |
| 저널           | metadata only (external log 가능) |
| Online 확장    | 지원 (xfs_growfs)                 |
| Online 축소    | 미지원                            |
| Reflink (CoW)  | 지원 (RHEL 8+ 기본 활성)          |
| 기본 OS        | RHEL/Rocky/AlmaLinux 7+           |

### 생성 및 관리

```bash
# 파일시스템 생성
sudo mkfs.xfs /dev/sdb1

# reflink 활성화 (RHEL 8+ 기본)
sudo mkfs.xfs -m reflink=1 /dev/sdb1

# 파일시스템 정보
sudo xfs_info /mnt/data

# 온라인 확장 (LVM 확장 후)
sudo xfs_growfs /mnt/data

# 조각 모음 (온라인)
sudo xfs_fsr /mnt/data

# 복구
sudo xfs_repair /dev/sdb1
```

### XFS 할당 그룹 구조

```
+--------------------------------------------------------------+
|                     XFS Filesystem                            |
+---------------+---------------+---------------+--------------+
| AG 0          | AG 1          | AG 2          | AG N |
| +-----------+ | +-----------+ | +-----------+ |      |
|               | SB + AGI      |               |      |
|               | AGF           |               |      |
|               | B+ Trees      |               |      |
|               | Data          |               |      |
| +-----------+ | +-----------+ | +-----------+ |      |
+---------------+---------------+---------------+--------------+

AG  = Allocation Group (independent lock -> parallel I/O)
AGI = AG Inode management
AGF = AG Free space management
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Btrfs

Btrfs(B-tree filesystem)는 차세대 Linux 파일시스템입니다. Copy-on-Write, 스냅샷, 투명 압축, 내장 RAID를 지원합니다.

### 주요 특성

| 항목             | 값                                       |
|------------------|------------------------------------------|
| 최대 파일 크기   | 8 EiB (VFS 제한)                         |
| 최대 볼륨 크기   | 16 EiB                                   |
| Copy-on-Write    | 전체 파일시스템 CoW                      |
| 스냅샷           | 서브볼륨 단위, O(1) 생성                 |
| RAID 지원        | 0, 1, 10 (5/6은 불안정, 프로덕션 비권장) |
| 투명 압축        | zlib, lzo, zstd                          |
| Online 확장/축소 | 둘 다 지원                               |
| 기본 OS          | openSUSE 13.2+, SLES 12+                 |

### 생성 및 관리

```bash
# 파일시스템 생성
sudo mkfs.btrfs /dev/sdb1

# zstd 압축 활성화
sudo mkfs.btrfs /dev/sdb1
sudo mount -o compress=zstd /dev/sdb1 /mnt/data

# 서브볼륨 생성
sudo btrfs subvolume create /mnt/data/@home

# 스냅샷 생성 (읽기 전용)
sudo btrfs subvolume snapshot -r /mnt/data/@home /mnt/data/@home_snap_20260717

# 스냅샷 목록
sudo btrfs subvolume list /mnt/data

# 파일시스템 사용량
sudo btrfs filesystem df /mnt/data
sudo btrfs filesystem usage /mnt/data

# 온라인 축소
sudo btrfs filesystem resize -10G /mnt/data

# 스크럽 (무결성 검증)
sudo btrfs scrub start /mnt/data
sudo btrfs scrub status /mnt/data
```

### Btrfs CoW 동작

```
Write "Hello" to file.txt (already contains "World")

Traditional (in-place):
  Block 100: [World] -> overwrite -> [Hello]
  (crash during write = corrupted data)

Btrfs (CoW):
  Block 100: [World]  (unchanged)
  Block 200: [Hello]  (new block)
  Metadata update: file.txt -> Block 200
  (crash before metadata commit = old data intact)
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 저널링

저널링은 crash 후 파일시스템 복구 시간을 단축하는 기술입니다. 변경 사항을 먼저 저널에 기록한 뒤 실제 위치에 반영합니다.

### 저널 모드 비교

| 모드      | 저널 대상       | 안전성 | 성능 | 설명                       |
|-----------|-----------------|--------|------|----------------------------|
| journal   | metadata + data | 높음   | 낮음 | 모든 데이터를 저널에 기록  |
| ordered   | metadata only   | 중간   | 중간 | 데이터 먼저 쓰고 메타 저널 |
| writeback | metadata only   | 낮음   | 높음 | 메타만 저널, 순서 미보장   |

### 파일시스템별 저널링

| 파일시스템 | 저널 방식             | 기본 모드 |
|------------|-----------------------|-----------|
| ext4       | 블록 기반 저널 (JBD2) | ordered   |
| XFS        | metadata 전용 로그    | metadata  |
| Btrfs      | CoW 기반, 저널 불필요 | N/A       |

### ext4 저널 모드 변경

```bash
# 현재 모드 확인
cat /proc/mounts | grep "sdb1"
# /dev/sdb1 /mnt/data ext4 rw,relatime,data=ordered 0 0

# writeback으로 변경 (fstab 또는 mount 옵션)
sudo mount -o remount,data=writeback /mnt/data

# fstab 영구 설정
# /dev/sdb1 /mnt/data ext4 defaults,data=writeback 0 2
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 마운트와 fstab

### /etc/fstab 형식

```
# <device>                                <mountpoint> <type> <options>        <dump> <pass>
UUID=a1b2c3d4-e5f6-7890-abcd-ef1234567890 /            ext4   defaults         0      1
UUID=b2c3d4e5-f6a7-8901-bcde-f12345678901 /home        ext4   defaults,noatime 0      2
UUID=c3d4e5f6-a7b8-9012-cdef-123456789012 /mnt/data    xfs    defaults         0      2
UUID=d4e5f6a7-b8c9-0123-defa-234567890123 none         swap   sw               0      0
```

| 필드       | 설명                                     |
|------------|------------------------------------------|
| device     | UUID 또는 /dev/sdXN (UUID 권장)          |
| mountpoint | 마운트 경로                              |
| type       | ext4, xfs, btrfs, swap 등                |
| options    | defaults, noatime, noexec, nosuid 등     |
| dump       | dump 백업 여부 (0: 안 함, 1: 함)         |
| pass       | fsck 순서 (0: 안 함, 1: root, 2: 나머지) |

### 주요 마운트 옵션

| 옵션     | 설명                                      |
|----------|-------------------------------------------|
| defaults | rw, suid, dev, exec, auto, nouser, async  |
| noatime  | atime 업데이트 비활성 (성능 향상)         |
| relatime | 조건부 atime 업데이트 (커널 2.6.30+ 기본) |
| noexec   | 실행 파일 실행 금지 (보안)                |
| nosuid   | setuid/setgid 비트 무시 (보안)            |
| nodev    | 디바이스 파일 무시 (보안)                 |
| ro       | 읽기 전용                                 |
| discard  | SSD TRIM 활성화                           |
| nofail   | 디바이스 없어도 부팅 계속                 |

### 마운트 명령어

```bash
# UUID 확인
sudo blkid /dev/sdb1

# 마운트
sudo mount /dev/sdb1 /mnt/data

# UUID로 마운트
sudo mount UUID=a1b2c3d4-e5f6-7890-abcd-ef1234567890 /mnt/data

# 옵션 지정 마운트
sudo mount -o noatime,noexec /dev/sdb1 /mnt/data

# 재마운트 (언마운트 없이 옵션 변경)
sudo mount -o remount,ro /mnt/data

# 언마운트
sudo umount /mnt/data

# fstab 전체 마운트 (테스트)
sudo mount -a

# 현재 마운트 목록
findmnt --real
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 파일시스템 관리

### 생성 (mkfs)

```bash
# ext4
sudo mkfs.ext4 -L "data" /dev/sdb1

# XFS
sudo mkfs.xfs -L "data" /dev/sdb1

# Btrfs
sudo mkfs.btrfs -L "data" /dev/sdb1
```

### 검사 (fsck)

```bash
# ext4 검사 (반드시 언마운트 상태)
sudo umount /dev/sdb1
sudo fsck.ext4 -f /dev/sdb1

# XFS 복구
sudo umount /dev/sdb1
sudo xfs_repair /dev/sdb1

# Btrfs 검사
sudo btrfs check /dev/sdb1
```

### 리사이즈

```bash
# ext4 확장 (온라인)
sudo resize2fs /dev/sdb1

# ext4 축소 (오프라인)
sudo umount /dev/sdb1
sudo e2fsck -f /dev/sdb1
sudo resize2fs /dev/sdb1 50G

# XFS 확장 (온라인, 축소 불가)
sudo xfs_growfs /mnt/data

# Btrfs 확장/축소 (온라인)
sudo btrfs filesystem resize +10G /mnt/data
sudo btrfs filesystem resize -10G /mnt/data
```

### 모니터링

```bash
# 디스크 사용량
df -hT

# inode 사용량
df -i

# 블록 디바이스 목록
lsblk -f

# 파일시스템 상세 정보
sudo tune2fs -l /dev/sdb1     # ext4
sudo xfs_info /mnt/data        # XFS
sudo btrfs filesystem show     # Btrfs
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. 파일시스템 비교

| 항목            | ext4            | XFS             | Btrfs               |
|-----------------|-----------------|-----------------|---------------------|
| 최대 파일       | 16 TiB          | 8 EiB           | 8 EiB               |
| 최대 볼륨       | 1 EiB           | 16 EiB          | 16 EiB              |
| 저널링          | JBD2 (3모드)    | metadata only   | CoW (저널 불필요)   |
| Online 확장     | ✅              | ✅              | ✅                  |
| Online 축소     | ❌ (오프라인만) | ❌              | ✅                  |
| 스냅샷          | ❌ (LVM 필요)   | ❌ (LVM 필요)   | ✅ (내장)           |
| 투명 압축       | ❌              | ❌              | ✅ (zstd/lzo/zlib)  |
| Reflink (CoW)   | ❌              | ✅ (RHEL 8+)    | ✅ (기본)           |
| 대파일 성능     | 보통            | 우수 (AG 병렬)  | 보통                |
| 소파일 다량     | 우수            | 보통            | 보통                |
| 안정성 (성숙도) | 매우 높음       | 매우 높음       | 높음 (RAID5/6 제외) |
| 기본 채택 OS    | Ubuntu/Debian   | RHEL/Rocky/Alma | openSUSE/SLES       |

### 선택 기준

| 시나리오                      | 추천                | 이유                           |
|-------------------------------|---------------------|--------------------------------|
| 범용 서버 (Ubuntu)            | ext4                | 안정성, 호환성, 충분한 성능    |
| 엔터프라이즈 서버 (RHEL 계열) | XFS                 | 배포판 기본, 대용량 최적화     |
| 대용량 DB (수 TB)             | XFS                 | AG 병렬 I/O, 대파일 처리       |
| 스냅샷/백업 필요              | Btrfs 또는 LVM+ext4 | 네이티브 스냅샷 vs LVM 스냅샷  |
| 데스크톱/NAS                  | Btrfs               | 스냅샷, 압축, 유연한 볼륨 관리 |

[⬆ 목차로 돌아가기](#목차)

---

## 11. 트러블슈팅

### 디스크 공간 부족

```bash
# 대용량 파일 찾기
sudo find / -xdev -type f -size +100M -exec ls -lh {} \; 2>/dev/null | sort -k5 -h

# 삭제되었지만 열린 파일 (공간 미해제)
sudo lsof +L1

# 디렉토리별 사용량
sudo du -sh /* 2>/dev/null | sort -h

# inode 고갈 확인
df -i
```

### inode 고갈

```bash
# inode 많이 사용하는 디렉토리
sudo find / -xdev -printf '%h\n' | sort | uniq -c | sort -rn | head -20
```

### 읽기 전용 전환 (filesystem error)

```bash
# 원인 확인
dmesg | grep -i "ext4\|xfs\|error\|readonly"
journalctl -k | grep -i filesystem

# ext4 복구
sudo umount /dev/sdb1
sudo fsck.ext4 -y /dev/sdb1

# XFS 복구
sudo umount /dev/sdb1
sudo xfs_repair /dev/sdb1

# 재마운트
sudo mount /dev/sdb1 /mnt/data
```

### 마운트 실패

```bash
# fstab 문법 검증 (util-linux 2.30+)
sudo findmnt --verify

# 수동 마운트로 에러 확인
sudo mount -v /dev/sdb1 /mnt/data

# UUID 불일치 확인
sudo blkid
cat /etc/fstab
```

### 성능 저하

```bash
# I/O 대기 프로세스 확인
sudo iotop -oP

# 파일시스템 단편화 확인 (ext4)
sudo e4defrag -c /mnt/data

# XFS 단편화 확인
sudo xfs_db -r -c frag /dev/sdb1
```

[⬆ 목차로 돌아가기](#목차)

---

## 12. 배포판 기본 FS

| 배포판              | 기본 FS | 비고   |
|---------------------|---------|--------|
| Ubuntu 20.04+       | ext4    | -      |
| Debian 12+          | ext4    | -      |
| RHEL 7 / Rocky 8, 9 | XFS     | -      |
| AlmaLinux 8, 9      | XFS     | -      |
| openSUSE Tumbleweed | Btrfs   | -      |
| SLES 12+            | Btrfs   | -      |
| Fedora 33+          | Btrfs   | -      |
| Arch Linux          | ext4    | 선택형 |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Linux VFS: [docs.kernel.org/filesystems/vfs.html](https://docs.kernel.org/filesystems/vfs.html) — ★★★☆☆
- ext4 Documentation: [docs.kernel.org/filesystems/ext4](https://docs.kernel.org/filesystems/ext4/index.html) — ★★★☆☆
- XFS Documentation: [docs.kernel.org/filesystems/xfs](https://docs.kernel.org/filesystems/xfs/index.html) — ★★★☆☆
- Btrfs Documentation: [btrfs.readthedocs.io](https://btrfs.readthedocs.io/) — ★★★☆☆
- man fstab(5): [man7.org/fstab.5](https://man7.org/linux/man-pages/man5/fstab.5.html) — ★★★☆☆
- Evi Nemeth et al. "UNIX and Linux System Administration Handbook, 5th Edition"
- [_reference/linux_filesystem_official_notes.md](../../_reference/linux_filesystem_official_notes.md)

---

**작성일**: 2026-07-17

**마지막 업데이트**: 2026-07-17

© 2026 siasia86. Licensed under CC BY 4.0.

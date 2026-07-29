---
name: e4fsprogs-centos5-notes
description: CentOS 5.11 EXT4 도구(e4fsprogs) 패키지 정보, fsck.ext4 옵션, tune4fs 설정 방법.
tags:
  - centos5
  - ext4
  - fsck
  - e4fsprogs
  - filesystem
last_checked: 2026-07-22
sources:
  - https://vault.centos.org/5.11/os/i386/CentOS/e4fsprogs-1.41.12-4.el5_10.i386.rpm
  - https://man7.org/linux/man-pages/man8/e2fsck.8.html
  - https://man7.org/linux/man-pages/man8/tune2fs.8.html
---

# CentOS 5.11 e4fsprogs 참조 노트

## 1. 패키지 정보

CentOS 5.x에서는 EXT4 도구가 e2fsprogs와 **별도 패키지**로 분리되어 있습니다.

| 패키지        | 버전                 | 대상      | 주요 바이너리      |
|---------------|----------------------|-----------|--------------------|
| e2fsprogs     | 1.39-37.el5          | EXT2/EXT3 | e2fsck, tune2fs    |
| **e4fsprogs** | **1.41.12-4.el5_10** | **EXT4**  | fsck.ext4, tune4fs |

- RPM: `https://vault.centos.org/5.11/os/i386/CentOS/e4fsprogs-1.41.12-4.el5_10.i386.rpm`
- 두 패키지가 충돌 없이 동시 설치됩니다
- EXT4 파일시스템에 e2fsck(1.39)를 사용하면 호환성 문제 발생 가능

## 2. 제공 바이너리

| 바이너리             | 역할                 | e2fsprogs 대응 |
|----------------------|----------------------|----------------|
| `/sbin/fsck.ext4`    | EXT4 파일시스템 검사 | e2fsck         |
| `/sbin/fsck.ext4dev` | EXT4dev 검사         | —              |
| `/sbin/mkfs.ext4`    | EXT4 포맷            | mke2fs         |
| `/sbin/mkfs.ext4dev` | EXT4dev 포맷         | —              |
| `/sbin/tune4fs`      | EXT4 설정 변경       | tune2fs        |
| `/sbin/dumpe4fs`     | EXT4 정보 출력       | dumpe2fs       |
| `/sbin/e4label`      | EXT4 레이블 변경     | e2label        |
| `/sbin/resize4fs`    | EXT4 크기 변경       | resize2fs      |

## 3. fsck.ext4 옵션

### 자주 사용하는 옵션

| 옵션   | 설명                             | 비고              |
|--------|----------------------------------|-------------------|
| `-f`   | 강제 검사 (clean 상태여도)       | 항상 사용 권장    |
| `-y`   | 모든 질문에 yes 자동 응답        | 무인 실행 시      |
| `-n`   | 읽기 전용 (수정 안 함, no 응답)  | 손상 여부만 확인  |
| `-p`   | 자동 복구 (안전한 수정만, preen) | 부팅 시 자동 fsck |
| `-v`   | 상세 출력                        |                   |
| `-C 0` | 진행률 표시 (stdout)             | 대용량 볼륨       |
| `-D`   | 디렉토리 최적화 (re-indexing)    |                   |

### 전체 옵션

| 옵션            | 설명                                       |
|-----------------|--------------------------------------------|
| `-a`            | `-p`와 동일 (하위 호환)                    |
| `-b superblock` | 대체 superblock 지정 (primary 손상 시)     |
| `-B blocksize`  | 블록 크기 강제 지정                        |
| `-c`            | badblocks 검사 (read-only, 시간 소요)      |
| `-d`            | 디버그 출력                                |
| `-F`            | 버퍼 캐시 flush 후 검사                    |
| `-j path`       | 외부 journal 경로 지정                     |
| `-k`            | -c와 함께 사용, 기존 bad block 유지 + 추가 |
| `-l file`       | bad block 목록 추가                        |
| `-L file`       | bad block 목록 교체                        |
| `-r`            | 사용 안 함 (하위 호환)                     |
| `-t`            | 타이밍 통계                                |
| `-V`            | 버전 출력                                  |

### 옵션 조합 제약

| 조합        | 가능 여부 | 이유                         |
|-------------|-----------|------------------------------|
| `-y` + `-n` | ❌        | yes와 no 동시 불가           |
| `-y` + `-p` | ❌        | yes와 preen 동시 불가        |
| `-n` + `-p` | ❌        | read-only와 repair 동시 불가 |
| `-f` + `-y` | ✅        | 강제 검사 + 자동 yes         |
| `-f` + `-v` | ✅        | 강제 검사 + 상세 출력        |

### Exit Code

| 코드 | 의미                         |
|------|------------------------------|
| 0    | 에러 없음                    |
| 1    | 에러 수정됨                  |
| 2    | 에러 수정됨, 재부팅 필요     |
| 4    | 에러 미수정 (수동 개입 필요) |
| 8    | 동작 에러                    |
| 16   | 사용법/문법 에러             |
| 32   | 사용자에 의해 취소           |
| 128  | 공유 라이브러리 에러         |

## 4. tune4fs 설정

### 자동 fsck 설정

```bash
# mount count 기반 (30회 마운트마다 fsck)
tune4fs -c 30 /dev/sdb

# 시간 기반 (7일마다, d=day, m=month, w=week)
tune4fs -i 7d /dev/sdb

# 자동 fsck 비활성화
tune4fs -c 0 -i 0 /dev/sdb

# 현재 설정 확인
tune4fs -l /dev/sdb | grep -i "mount count\|maximum\|interval"
```

### fstab pass 필드

```
UUID="..."  /masang            ext4  defaults  0 2
UUID="..."  /masang/Server/log ext4  defaults  0 2
                                               ^ ^
                                               | └── pass: 0=검사 안함, 1=루트, 2=나머지
                                               └── dump: 0=백업 안함
```

## 5. 실행 예시 (CentOS 5.11)

```bash
# 1. 손상 여부만 확인 (수정 없음)
fsck.ext4 -nf /dev/sdb

# 2. 강제 검사 + 자동 복구 (마운트 해제 필수!)
umount /masang/Server/log
umount /masang
fsck.ext4 -fy -C 0 /dev/sdb
fsck.ext4 -fy -C 0 /dev/sdc
mount /masang
mount /masang/Server/log

# 3. superblock 손상 시
# 백업 superblock 위치 확인
mkfs.ext4 -n /dev/sdb | grep -i superblock
# 백업 superblock으로 검사
fsck.ext4 -b 32768 -fy /dev/sdb

# 4. 설치 확인
rpm -q e4fsprogs
# e4fsprogs-1.41.12-4.el5_10

# 5. 미설치 시 설치
yum install e4fsprogs
# 또는 오프라인
rpm -ivh e4fsprogs-1.41.12-4.el5_10.i386.rpm
```

## 6. 주의 사항

| 주의             | 설명                                                   |
|------------------|--------------------------------------------------------|
| 마운트 해제 필수 | 마운트 상태에서 fsck 실행 시 추가 손상 가능            |
| `-n` 제외        | `-n` 옵션만 마운트 상태에서 안전 (읽기 전용)           |
| e2fsck 사용 금지 | CentOS 5의 e2fsck(1.39)는 EXT4 미지원 — fsck.ext4 사용 |
| fstab pass=2     | 부팅 시간 증가 가능 (대용량 볼륨)                      |
| SCSI timeout     | fsck 실행 중 I/O 부하 증가 → timeout 여유 필요         |

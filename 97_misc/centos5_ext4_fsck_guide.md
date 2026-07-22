# CentOS 5.11 EXT4 파일시스템 검사/복구 가이드

CentOS 5.11 환경에서 EXT4 파일시스템의 fsck 실행 방법, 자동 검사 설정, SCSI timeout 영구 등록을 정리합니다.

## 목차

| 섹션                                                                                                                                                          |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 패키지 구조](#1-패키지-구조) / [2. fsck.ext4 사용법](#2-fsckext4-사용법) / [3. 자동 검사 설정](#3-자동-검사-설정)                                         |
| [4. SCSI timeout 영구 등록](#4-scsi-timeout-영구-등록) / [5. fsck 실행 확인](#5-fsck-실행-확인) / [6. 실행 절차](#6-실행-절차) / [7. 참고 자료](#7-참고-자료) |

---

## 1. 패키지 구조

CentOS 5.x에서는 EXT4 도구가 e2fsprogs와 **별도 패키지**로 분리되어 있습니다.

| 패키지        | 버전                 | 대상      | 주요 바이너리      |
|---------------|----------------------|-----------|--------------------|
| e2fsprogs     | 1.39-37.el5          | EXT2/EXT3 | e2fsck, tune2fs    |
| **e4fsprogs** | **1.41.12-4.el5_10** | **EXT4**  | fsck.ext4, tune4fs |

🔴 CentOS 5의 `e2fsck`(1.39)는 EXT4를 지원하지 않습니다. EXT4 파일시스템에는 반드시 `fsck.ext4`(e4fsprogs)를 사용합니다.

### 설치 확인

```bash
rpm -q e4fsprogs
# e4fsprogs-1.41.12-4.el5_10
```

### 미설치 시

```bash
# 온라인
yum install e4fsprogs

# 오프라인 (vault에서 다운로드)
wget http://vault.centos.org/5.11/os/i386/CentOS/e4fsprogs-1.41.12-4.el5_10.i386.rpm
rpm -ivh e4fsprogs-1.41.12-4.el5_10.i386.rpm
```

### 제공 바이너리

| 바이너리          | 역할                 | e2fsprogs 대응 |
|-------------------|----------------------|----------------|
| `/sbin/fsck.ext4` | EXT4 파일시스템 검사 | e2fsck         |
| `/sbin/tune4fs`   | EXT4 설정 변경       | tune2fs        |
| `/sbin/dumpe4fs`  | EXT4 정보 출력       | dumpe2fs       |
| `/sbin/mkfs.ext4` | EXT4 포맷            | mke2fs         |
| `/sbin/resize4fs` | EXT4 크기 변경       | resize2fs      |
| `/sbin/e4label`   | EXT4 레이블 변경     | e2label        |

[⬆ 목차로 돌아가기](#목차)

---

## 2. fsck.ext4 사용법

### 주요 옵션

| 옵션   | 설명                       | 사용 시나리오      |
|--------|----------------------------|--------------------|
| `-f`   | 강제 검사 (clean 상태여도) | 항상 사용 권장     |
| `-y`   | 모든 질문에 yes 자동 응답  | 무인/스크립트 실행 |
| `-n`   | 읽기 전용 (수정 안 함)     | 손상 여부만 확인   |
| `-p`   | 자동 복구 (안전한 수정만)  | 부팅 시 자동 fsck  |
| `-v`   | 상세 출력                  | 결과 확인          |
| `-C 0` | 진행률 표시 (stdout)       | 대용량 볼륨        |
| `-D`   | 디렉토리 최적화            | re-indexing        |

### 옵션 조합 제약

| 조합        | 가능 | 이유                       |
|-------------|------|----------------------------|
| `-f` + `-y` | ✅   | 강제 검사 + 자동 수정      |
| `-f` + `-n` | ✅   | 강제 검사 + 읽기 전용      |
| `-y` + `-n` | ❌   | yes와 no 동시 불가         |
| `-y` + `-p` | ❌   | yes와 preen 동시 불가      |
| `-n` + `-p` | ❌   | read-only와 수정 동시 불가 |

### Exit Code

| 코드 | 의미                         | 후속 조치             |
|------|------------------------------|-----------------------|
| 0    | 에러 없음                    | 없음                  |
| 1    | 에러 수정됨                  | 정상 마운트 가능      |
| 2    | 에러 수정됨 + 재부팅 필요    | reboot 후 재마운트    |
| 4    | 에러 미수정 (수동 개입 필요) | -y로 재실행 또는 수동 |
| 8    | 동작 에러                    | 명령어/디바이스 확인  |

🟡 Exit code는 OR 합산입니다. 예: 3 = 1+2 → "에러 수정 + 재부팅 필요".

### 사용 예시

```bash
# 손상 여부만 확인 (수정 없음, 마운트 상태에서도 안전)
fsck.ext4 -nf /dev/sdb

# 강제 검사 + 자동 복구 + 진행률 (마운트 해제 필수!)
fsck.ext4 -fy -C 0 /dev/sdb

# 강제 검사 + 상세 출력
fsck.ext4 -fv /dev/sdb

# superblock 손상 시 백업 superblock 사용
fsck.ext4 -b 32768 -fy /dev/sdb
```

### 주의: /dev/sdX vs /dev/sdX1 (파티션 지정)

**파티션이 있는 디스크에서는 반드시 파티션 장치(`/dev/sde1`)를 지정합니다.**

#### 실제 사례

```bash
# ❌ 디스크 전체 지정 — superblock 못 찾음
[root@gamedb-srv01 /]# fsck.ext4 -nf /dev/sde
e4fsck 1.41.12 (17-May-2010)
fsck.ext4: Superblock invalid, trying backup blocks...
fsck.ext4: Bad magic number in super-block while trying to open /dev/sde

# ✅ 파티션 지정 — 정상 검사
[root@gamedb-srv01 /]# fsck.ext4 -nf /dev/sde1
e4fsck 1.41.12 (17-May-2010)
Pass 1: Checking inodes, blocks, and sizes
Pass 2: Checking directory structure
Pass 3: Checking directory connectivity
Pass 4: Checking reference counts
Pass 5: Checking group summary information
/dev/sde1: 185/6553600 files (88.1% non-contiguous), 574321/26214055 blocks
```

#### 판별 방법

```bash
# 마운트된 장치명 확인 (이것을 그대로 사용)
df -hT | grep data
# /dev/sde1     ext4     100G  ...  /data    ← sde1 사용
# /dev/sdb      ext4     100G  ...  /data    ← sdb 사용 (whole disk)

# 파티션 유무 확인
fdisk -l /dev/sde | grep sde
# /dev/sde1 ... Linux   ← 파티션 있음 → fsck.ext4 /dev/sde1
# (출력 없음)           ← 파티션 없음 → fsck.ext4 /dev/sde
```

| 구조                      | fsck 대상         | 예시                                            |
|---------------------------|-------------------|-------------------------------------------------|
| 파티션 있음 (`sde1` 존재) | `/dev/sde1`       | `fsck.ext4 -fy /dev/sde1`                       |
| 파티션 없음 (whole disk)  | `/dev/sde`        | `fsck.ext4 -fy /dev/sde`                        |
| LVM                       | `/dev/mapper/...` | `fsck.ext4 -fy /dev/mapper/VolGroup00-LogVol00` |

🔴 **`-n` 없이** 잘못된 장치(`/dev/sde`)에 fsck를 실행하면 파티션 테이블이 손상될 수 있습니다. 항상 `df -hT`에서 보이는 장치명을 사용합니다.

### 백업 superblock 위치 확인

```bash
# 방법 1: mkfs.ext4 -n (실제 포맷 안 함, dry-run)
mkfs.ext4 -n /dev/sdb 2>&1 | grep -i superblock

# 방법 2: dumpe4fs
dumpe4fs /dev/sdb 2>/dev/null | grep -i "backup superblock"
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 자동 검사 설정

### 방법 1: tune4fs (mount count 기반)

```bash
# 30회 마운트마다 부팅 시 fsck 실행
tune4fs -c 30 /dev/sdb
tune4fs -c 30 /dev/sdc

# 현재 설정 확인
tune4fs -l /dev/sdb | grep -i "mount count\|maximum\|check interval"
```

출력 예시:

```
Mount count:              15
Maximum mount count:      30      ← 30회 도달 시 fsck 실행
Check interval:           0 (<none>)
```

### 방법 2: tune4fs (시간 기반)

```bash
# 30일마다 부팅 시 fsck 실행 (d=day, m=month, w=week)
tune4fs -i 30d /dev/sdb

# 자동 검사 비활성화
tune4fs -c 0 -i 0 /dev/sdb
```

### 사전 확인 (fstab pass 설정 전 필수)

CentOS 5의 기본 파일시스템은 EXT3이므로, 부팅 시 fsck가 EXT4를 올바르게 호출하는지 확인해야 합니다.

```bash
# 1. e4fsprogs 설치 확인
rpm -q e4fsprogs
# e4fsprogs-1.41.12-4.el5_10 ← 이 출력이 나와야 함

# 2. fsck.ext4 바이너리 존재 확인
ls -la /sbin/fsck.ext4
# /sbin/fsck.ext4 ← 파일 존재해야 함

# 3. fsck wrapper가 ext4를 올바르게 호출하는지 테스트 (-N: dry-run)
fsck -N /dev/sdb
# [/sbin/fsck.ext4 (1) -- /data] fsck.ext4 /dev/sdb ← 이렇게 나와야 함
```

| 확인 결과                 | 조치                                 |
|---------------------------|--------------------------------------|
| e4fsprogs 미설치          | `yum install e4fsprogs` 후 pass 설정 |
| `/sbin/fsck.ext4` 없음    | e4fsprogs 재설치                     |
| `fsck -N`에서 ext4 미인식 | e4fsprogs 재설치 후 재확인           |
| 3개 모두 정상             | fstab pass=2 설정 가능               |

🔴 e4fsprogs 미설치 상태에서 fstab pass=2를 설정하면 부팅 시 fsck가 건너뛰어져 검사가 실행되지 않습니다.

### 방법 3: fstab pass 필드

```bash
# /etc/fstab
UUID="xxxxxxxx-..."  /data            ext4  defaults  0 2
UUID="yyyyyyyy-..."  /data/log  ext4  defaults  0 2
```

| pass 값 | 동작                                |
|---------|-------------------------------------|
| 0       | 부팅 시 fsck 실행 안 함             |
| 1       | 루트 파일시스템 (가장 먼저 검사)    |
| 2       | 루트 외 (1 완료 후 검사, 병렬 가능) |

🟡 게임 서버에서는 `tune4fs -c 30` (mount count 기반)이 적합합니다. 정기 점검 시 reboot 할 때만 검사되어 부팅 시간 영향을 최소화합니다.

### 권장 설정 조합

```bash
# mount count 기반 (30회)
tune4fs -c 30 /dev/sdb
tune4fs -c 30 /dev/sdc

# fstab pass 필드도 2로 설정 (mount count 도달 시만 실행됨)
# /etc/fstab:
# UUID=...  /data            ext4  defaults  0 2
# UUID=...  /data/log ext4  defaults  0 2
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. SCSI timeout 영구 등록

### 현재 값 확인

```bash
cat /sys/block/sda/device/timeout    # OS 디스크
cat /sys/block/sdb/device/timeout    # 데이터 디스크 1
cat /sys/block/sdc/device/timeout    # 데이터 디스크 2
```

### 임시 변경 (재부팅 시 초기화)

```bash
echo 120 > /sys/block/sdb/device/timeout
echo 120 > /sys/block/sdc/device/timeout
```

### 영구 등록 (rc.local)

```bash
# /etc/rc.local에 추가
cat >> /etc/rc.local << 'RCEOF'

# SCSI timeout 120초 설정 (Hyper-V I/O 포화 대응)
for disk in sdb sdc; do
    if [ -f /sys/block/$disk/device/timeout ]; then
        echo 120 > /sys/block/$disk/device/timeout
    fi
done
RCEOF

# 실행 권한 확인
chmod +x /etc/rc.local
```

### udev rule 방식 (디스크 추가/변경 시에도 적용)

```bash
# /etc/udev/rules.d/99-scsi-timeout.rules
cat > /etc/udev/rules.d/99-scsi-timeout.rules << 'UDEVEOF'
# Hyper-V Virtual Disk — SCSI timeout 120초
ACTION=="add|change", SUBSYSTEM=="block", ATTRS{vendor}=="Msft    ", ATTR{device/timeout}="120"
UDEVEOF

# udev 재로드
udevadm control --reload-rules
udevadm trigger
```

### 적용 확인

```bash
# 재부팅 후 확인
cat /sys/block/sdb/device/timeout
# 120
```

### timeout 값 선정 근거

| 값    | 근거                                              |
|-------|---------------------------------------------------|
| 60초  | CentOS 5.11 현재 설정 (기본 30초에서 변경된 상태) |
| 120초 | 이번 장애 최대 latency 116초 < 120초 → abort 방지 |
| 180초 | 여유 있으나 장애 감지 지연 증가                   |

[⬆ 목차로 돌아가기](#목차)

---

## 5. fsck 실행 확인

부팅 후 fsck가 정상적으로 실행되었는지 확인하는 방법입니다.

### 방법 1: tune4fs — Last checked 시각 (가장 확실)

```bash
tune4fs -l /dev/sdb | grep -i "last checked"
# Last checked:         Wed Jul 22 14:50:00 2026

# 비교: 마지막 부팅 시각
who -b
# system boot  2026-07-22 14:48
```

| Last checked vs 부팅 시각 | 판정               |
|---------------------------|--------------------|
| 거의 일치 (수 분 이내)    | ✅ fsck 실행됨     |
| 수일~수주 전              | ❌ fsck 실행 안 됨 |

### 방법 2: Mount count 확인

```bash
tune4fs -l /dev/sdb | grep -i "mount count\|maximum"
# Mount count:          1
# Maximum mount count:  30
```

| Mount count   | 의미                              |
|---------------|-----------------------------------|
| 1 (부팅 직후) | ✅ fsck 실행 후 카운터 리셋됨     |
| 15, 29 등     | ❌ fsck 미실행 (카운터 계속 증가) |

### 방법 3: dmesg 확인

```bash
dmesg | grep -i "fsck\|e4fsck\|checking.*ext"
```

| 출력 내용                                                             | 판정                       |
|-----------------------------------------------------------------------|----------------------------|
| (fsck 관련 출력 없음)                                                 | ✅ 정상 마운트 (경고 없음) |
| `warning: maximal mount count reached, running e2fsck is recommended` | ❌ fsck 미실행             |
| `warning: checktime reached, running e2fsck is recommended`           | ❌ fsck 미실행             |

🟡 dmesg에 경고가 출력되면 fsck가 실행되지 **않은** 것입니다. 커널은 "실행해야 한다"고 경고만 하고 그대로 마운트합니다.

### 방법 4: /var/log/boot.log

```bash
grep -i "fsck\|Checking filesystem\|clean\|MODIFIED" /var/log/boot.log
```

| 출력                                   | 의미                  |
|----------------------------------------|-----------------------|
| `Checking filesystem /dev/sdb: clean.` | ✅ fsck 실행, 정상    |
| `FILE SYSTEM WAS MODIFIED`             | ✅ fsck 실행 + 수정됨 |
| (출력 없음)                            | ❌ fsck 미실행        |

### 확인 요약

```bash
# 한 번에 확인하는 스크립트
echo "=== Last checked ==="
tune4fs -l /dev/sdb 2>/dev/null | grep "Last checked"
tune4fs -l /dev/sdc 2>/dev/null | grep "Last checked"
echo ""
echo "=== Mount count ==="
tune4fs -l /dev/sdb 2>/dev/null | grep -i "mount count"
tune4fs -l /dev/sdc 2>/dev/null | grep -i "mount count"
echo ""
echo "=== Boot time ==="
who -b
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 실행 절차

### 정기 점검 시 (계획된 다운타임)

```bash
# 1. 게임 서버 중지 (공지 후)
# (게임 서버 중지 절차)

# 2. MySQL 중지
service mysqld stop

# 3. 마운트 해제 (역순)
umount /data/log    # sdc (하위 먼저)
umount /data               # sdb

# 4. fsck 실행
fsck.ext4 -fy -C 0 /dev/sdb
fsck.ext4 -fy -C 0 /dev/sdc

# 5. 결과 확인 (exit code)
echo "sdb: $?"
# 0 = 정상, 1 = 수정됨, 2 = 수정+재부팅

# 6. 재마운트
mount /data
mount /data/log

# 7. MySQL 시작
service mysqld start

# 8. 테이블 검증
mysqlcheck --check --all-databases
```

### 긴급 복구 시 (장애 후)

```bash
# 1. single-user 모드 진입 또는 rescue 부팅

# 2. 마운트 해제 확인
umount /data/log 2>/dev/null
umount /data 2>/dev/null

# 3. 강제 검사 + 자동 복구
fsck.ext4 -fy -C 0 /dev/sdb
fsck.ext4 -fy -C 0 /dev/sdc

# 4. exit code 4 (미수정) 시 — 수동 개입 필요
# lost+found 확인
ls -la /data/lost+found/
ls -la /data/log/lost+found/

# 5. 재마운트 후 MySQL 검증
mount /data
mount /data/log
service mysqld start
mysqlcheck --repair --all-databases
```

### lost+found 파일 처리

```bash
# lost+found에 파일이 있으면 (fsck가 고아 파일 이동)
ls /data/lost+found/

# 파일 타입 확인 (이름이 inode 번호)
file /data/lost+found/#12345

# MySQL 데이터라면 원래 경로로 복원
# (파일 내용을 확인하여 원래 테이블 식별)
strings /data/lost+found/#12345 | head
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 참고 자료

- e2fsck man page: [man7.org](https://man7.org/linux/man-pages/man8/e2fsck.8.html) — ★★★☆☆
- tune2fs man page: [man7.org](https://man7.org/linux/man-pages/man8/tune2fs.8.html) — ★★★☆☆
- fstab man page: [man7.org](https://man7.org/linux/man-pages/man5/fstab.5.html) — ★★★☆☆
- e4fsprogs RPM: [vault.centos.org](http://vault.centos.org/5.11/os/i386/CentOS/e4fsprogs-1.41.12-4.el5_10.i386.rpm) — ★★☆☆☆
- [_reference/e4fsprogs_centos5_notes.md](../_reference/e4fsprogs_centos5_notes.md)
- [_reference/linux_filesystem_official_notes.md](../_reference/linux_filesystem_official_notes.md)
- [97_misc/hyperv_myisam_io_timeout_incident_20260715.md](hyperv_myisam_io_timeout_incident_20260715.md)

[⬆ 목차로 돌아가기](#목차)

---

**작성일**: 2026-07-22

**마지막 업데이트**: 2026-07-22

© 2026 siasia86. Licensed under CC BY 4.0.

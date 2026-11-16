# LVM 운영 가이드

LVM(Logical Volume Manager)은 여러 디스크를 하나의 저장 공간 묶음으로 모은 뒤 필요한 크기만큼 논리 볼륨으로 잘라 쓰게 하는 Linux 볼륨 관리 계층입니다. 이 문서는 LVM2 구조, 생성·확장·축소, 스냅샷, Thin Provisioning, 디스크 교체와 장애 대응을 운영 관점에서 정리합니다.

> 기준 판: LVM2 2.03.42 (man7.org man page 기준, 확인일 2026-11-16). 배포판 패키지 판은 `lvm version`으로 확인합니다.

## 목차

| 목차                                                                                        |
|---------------------------------------------------------------------------------------------|
| [1. LVM 구조](#1-lvm-구조) / [2. 상태 조회 명령](#2-상태-조회-명령)                         |
| [3. 생성 절차](#3-생성-절차) / [4. 확장](#4-확장) / [5. 축소](#5-축소)                      |
| [6. COW 스냅샷](#6-cow-스냅샷) / [7. Thin Provisioning](#7-thin-provisioning)               |
| [8. 디스크 교체와 데이터 이동](#8-디스크-교체와-데이터-이동) / [9. 장애 대응](#9-장애-대응) |
| [10. 운영 점검표](#10-운영-점검표)                                                          |

---

## 1. LVM 구조

LVM은 세 층으로 이루어집니다.

| 용어                 | 설명                                                   | 예               |
|----------------------|--------------------------------------------------------|------------------|
| PV (Physical Volume) | LVM이 쓰도록 초기화한 디스크나 파티션                  | `/dev/sdb`       |
| VG (Volume Group)    | 여러 PV를 묶은 저장 공간 묶음                          | `vg_data`        |
| LV (Logical Volume)  | VG에서 잘라 낸 블록 장치. 파일시스템을 올리는 대상     | `vg_data/lv_app` |
| PE (Physical Extent) | VG 공간을 나누는 할당 단위. LV 크기는 PE 개수로 정해짐 | 기본 4 MiB       |

```text
 /dev/sdb   /dev/sdc   /dev/sdd        <- PV (pvcreate)
     \         |         /
      +--------+--------+
               |
           vg_data                     <- VG (vgcreate)
        /      |       \
   lv_app   lv_log   (free PE)         <- LV (lvcreate)
     |         |
   xfs       ext4                      <- filesystem (mkfs)
```

LV 장치는 `/dev/<VG>/<LV>`와 `/dev/mapper/<VG>-<LV>` 두 경로로 보입니다. 내부적으로는 커널 device-mapper가 LV를 구현합니다.

LVM을 쓰는 이유는 다음과 같습니다.

- 파티션 경계에 묶이지 않고 운영 중에 LV를 늘릴 수 있습니다.
- 디스크를 VG에 추가해 용량을 넓히고, `pvmove`로 운영 중 데이터를 다른 디스크로 옮길 수 있습니다.
- 스냅샷으로 백업 시점을 고정할 수 있습니다.

🟡 LVM은 그 자체로 이중화가 아닙니다. 여러 PV에 걸친 일반(linear) LV는 PV 하나만 고장 나도 그 LV 전체가 손상될 수 있습니다. 이중화는 하드웨어 RAID, [mdadm](mdadm_software_raid.md) 또는 LVM RAID LV(`--type raid1` 등)로 따로 구성합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 상태 조회 명령

| 명령                 | 용도                                |
|----------------------|-------------------------------------|
| `pvs` / `pvdisplay`  | PV 목록·크기·남은 공간              |
| `vgs` / `vgdisplay`  | VG 목록·전체 크기·남은 공간(VFree)  |
| `lvs` / `lvdisplay`  | LV 목록·크기·속성·스냅샷 사용률     |
| `lsblk`              | 디스크-파티션-LV 관계 나무 구조     |
| `lvs -a -o +devices` | LV가 실제로 어느 PV에 놓였는지 확인 |
| `pvscan` / `vgscan`  | 장치를 다시 읽어 PV·VG 찾기         |

```bash
# 요약 조회
sudo pvs
sudo vgs
sudo lvs -a -o +devices,seg_type

# 보기 좋은 단위로
sudo vgs --units g
```

`lvs`의 `Attr` 열은 10자리 속성 문자열입니다. 첫 글자로 LV 종류를 구분합니다(`-` 일반, `s` 스냅샷, `o` 스냅샷 원본, `t` thin pool, `V` thin volume, `r` RAID 등). 자세한 값은 `man lvs`의 `lv_attr` 설명을 봅니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 생성 절차

새 디스크 두 개(`/dev/sdb`, `/dev/sdc`)로 VG를 만들고 LV를 올리는 예입니다.

🟡 `pvcreate`는 대상 장치의 기존 서명을 덮어씁니다. 실행 전에 `lsblk -f`로 장치 이름과 기존 파일시스템 유무를 반드시 확인합니다.

```bash
# 1. 대상 확인
lsblk -f

# 2. PV 초기화
sudo pvcreate /dev/sdb /dev/sdc

# 3. VG 생성
sudo vgcreate vg_data /dev/sdb /dev/sdc

# 4. LV 생성 (크기 지정 또는 비율 지정)
sudo lvcreate -n lv_app -L 200G vg_data
sudo lvcreate -n lv_log -l 50%FREE vg_data

# 5. 파일시스템 생성과 마운트
sudo mkfs.xfs /dev/vg_data/lv_app
sudo mkdir -p /srv/app
sudo mount /dev/vg_data/lv_app /srv/app
```

크기 지정 방법은 두 가지입니다.

| 옵션 | 의미              | 예                            |
|------|-------------------|-------------------------------|
| `-L` | 고정 크기         | `-L 200G`, `-L +50G`(확장 때) |
| `-l` | PE 개수 또는 비율 | `-l 100%FREE`, `-l 20%VG`     |

`/etc/fstab`에는 장치 경로 대신 UUID나 `/dev/mapper/vg_data-lv_app`을 적습니다. `nofail` 옵션을 넣으면 해당 디스크가 없을 때 부팅이 멈추지 않습니다.

```text
/dev/mapper/vg_data-lv_app  /srv/app  xfs  defaults,nofail  0 0
```

성능 목적이면 여러 PV에 나눠 쓰는 striped LV도 만들 수 있습니다(`lvcreate -i 3 -I 8 -L 100m vg00`은 3개 stripe, stripe 크기 8 KiB). 다만 stripe는 이중화가 없어서 PV 하나의 고장이 LV 전체 손실로 이어집니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 확장

확장은 운영 중에 할 수 있는 작업입니다. 순서는 "VG에 남은 공간 확인 → 부족하면 PV 추가 → LV와 파일시스템 확장"입니다.

```bash
# VG 남은 공간 확인
sudo vgs vg_data

# 공간이 부족하면 새 디스크를 PV로 만들어 VG에 추가
sudo pvcreate /dev/sdd
sudo vgextend vg_data /dev/sdd

# LV와 파일시스템을 함께 확장 (-r = --resizefs, fsadm 사용)
sudo lvextend -r -L +100G vg_data/lv_app

# 남은 공간 전체를 사용
sudo lvextend -r -l +100%FREE vg_data/lv_app
```

`-r`(`--resizefs`)을 빼면 LV만 커지고 파일시스템은 그대로입니다. 그때는 파일시스템별 명령을 따로 실행합니다.

| 파일시스템 | 확장 명령                       | 조건                             |
|------------|---------------------------------|----------------------------------|
| ext4       | `resize2fs /dev/vg_data/lv_log` | 마운트 상태에서 온라인 확장 가능 |
| XFS        | `xfs_growfs /srv/app`           | 마운트 상태여야 확장 가능        |

가상 머신이나 클라우드에서 기존 디스크 크기를 늘린 경우에는 PV도 늘려야 합니다.

```bash
# 디스크 크기 변경을 커널에 반영한 뒤 PV 확장
echo 1 | sudo tee /sys/class/block/sdb/device/rescan
sudo pvresize /dev/sdb
sudo lvextend -r -l +100%FREE vg_data/lv_app
```

파티션 위에 PV를 만든 경우에는 `pvresize` 전에 `growpart` 같은 도구로 파티션부터 늘립니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 축소

축소는 데이터 손실 위험이 큰 작업입니다. 먼저 백업을 확보하고, 줄일 크기가 실제 사용량보다 충분히 큰지 확인합니다.

| 파일시스템 | 축소 가능 여부                                                                  |
|------------|---------------------------------------------------------------------------------|
| ext4       | 가능. 마운트 해제 후 오프라인으로 축소                                          |
| XFS        | 실무상 불가. `xfs_growfs` man page는 마지막 AG 일부만 줄이는 제한적 기능만 설명 |

XFS LV를 작게 만들어야 하면 새 LV를 만들어 데이터를 옮기는 방법(`xfsdump`/`xfsrestore`, `rsync`)을 씁니다.

ext4 축소 예입니다.

🟡 아래 순서를 바꾸거나 파일시스템보다 LV를 먼저 줄이면 데이터가 손상됩니다. `-r`을 쓰면 `fsadm`이 파일시스템을 먼저 줄입니다.

```bash
sudo umount /srv/log
# -r 사용 시 fsadm이 e2fsck와 resize2fs를 거쳐 파일시스템을 먼저 줄임
sudo lvreduce -r -L 50G vg_data/lv_log
sudo mount /srv/log
df -h /srv/log
```

VG에서 디스크를 빼려면 그 PV에 놓인 데이터를 먼저 옮깁니다(8절 참고).

[⬆ 목차로 돌아가기](#목차)

---

## 6. COW 스냅샷

COW(Copy-on-Write) 스냅샷은 원본 LV의 특정 시점을 고정합니다. 생성 직후에는 거의 공간을 쓰지 않고, 원본 블록이 바뀔 때마다 바뀌기 전 블록을 스냅샷 공간으로 복사합니다.

```bash
# 고정 크기 스냅샷
sudo lvcreate --snapshot --size 10G --name lv_app_snap vg_data/lv_app

# 원본 크기의 20%만큼 예약
sudo lvcreate -s -l 20%ORIGIN -n lv_app_snap vg_data/lv_app

# 사용률 확인 (Data% 열)
sudo lvs vg_data
```

스냅샷 공간이 가득 차면 커널이 그 스냅샷을 무효(Invalid) 상태로 만들고, 그 스냅샷은 더 이상 읽을 수 없습니다. 이를 막으려면 다음 중 하나를 씁니다.

- 변경량을 넉넉히 예상해 크기를 잡습니다. 길게 유지할수록 더 커야 합니다.
- `lvextend`로 스냅샷 공간을 늘립니다.
- `lvm.conf`의 `snapshot_autoextend_threshold`·`snapshot_autoextend_percent`와 `dmeventd` 모니터링으로 자동 확장합니다(threshold 100은 자동 확장 끔).

백업에 쓰는 흐름입니다.

```bash
# 1. 애플리케이션을 잠시 일관된 상태로 (DB flush 등)
# 2. 스냅샷 생성
sudo lvcreate -s -L 10G -n lv_app_snap vg_data/lv_app
# 3. 스냅샷을 읽기 전용으로 마운트 (XFS는 UUID 중복 때문에 nouuid 필요)
sudo mkdir -p /mnt/snap
sudo mount -o ro,nouuid /dev/vg_data/lv_app_snap /mnt/snap
# 4. 백업 도구로 복사
# 5. 정리
sudo umount /mnt/snap
sudo lvremove -y vg_data/lv_app_snap
```

스냅샷 시점으로 되돌리려면 `lvconvert --merge`를 씁니다. 원본과 스냅샷이 모두 열려 있지 않으면 바로 병합을 시작하고, 루트 파일시스템처럼 닫을 수 없는 원본은 다음 활성화(보통 재부팅) 때 병합합니다.

🟡 병합하면 스냅샷 이후 원본에 쓴 내용이 사라집니다.

```bash
sudo umount /srv/app
sudo lvconvert --merge vg_data/lv_app_snap
```

COW 스냅샷이 있는 동안 원본에 쓰기가 일어나면 복사 비용이 더해져 쓰기 성능이 떨어집니다. 백업이 끝나면 바로 지우는 것을 기본으로 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. Thin Provisioning

Thin Provisioning은 실제 공간보다 큰 가상 크기의 LV를 만들고, 데이터를 쓸 때 thin pool에서 공간을 할당하는 방식입니다. 스냅샷을 많이 만들어도 공간 효율이 좋고, 스냅샷끼리 블록을 공유합니다.

```bash
# thin pool 생성 (메타데이터 LV 크기는 자동 계산, --poolmetadatasize로 지정 가능)
sudo lvcreate --type thin-pool -n pool0 -L 500G vg_data

# thin LV 생성 (가상 크기는 pool 실제 크기보다 클 수 있음)
sudo lvcreate --type thin -n lv_vm01 -V 300G --thinpool pool0 vg_data
sudo lvcreate --type thin -n lv_vm02 -V 300G --thinpool pool0 vg_data

# thin 스냅샷 (크기 옵션을 주지 않음. 주면 COW 스냅샷이 됨)
sudo lvcreate --snapshot -n lv_vm01_snap vg_data/lv_vm01

# thin 스냅샷은 activation skip 속성이 붙으므로 -K로 활성화
sudo lvchange -ay -K vg_data/lv_vm01_snap
```

Thin pool의 핵심 위험은 공간 고갈입니다. lvmthin man page는 pool이 가득 차기 전에 확장하지 않으면 pool이 손상되어 복구가 어렵거나 불가능할 수 있다고 경고합니다. 기본 "queue" 모드에서는 쓰기가 최대 60초 기다린 뒤 실패하고, 이때 파일시스템 손상이 생길 수 있습니다.

```bash
# 데이터·메타데이터 사용률 감시
sudo lvs -o lv_name,data_percent,metadata_percent vg_data/pool0
```

`/etc/lvm/lvm.conf`의 `activation` 절에서 자동 확장을 설정합니다.

```text
activation {
    thin_pool_autoextend_threshold = 80   # 사용률 80%에서 확장 (최소 50, 100은 끔)
    thin_pool_autoextend_percent = 20     # 현재 크기의 20%만큼 확장
}
```

자동 확장은 VG에 남은 공간이 있어야 동작합니다. 그래서 thin pool을 쓸 때는 VG 여유 공간과 `data_percent`·`metadata_percent`를 모두 모니터링 대상으로 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 디스크 교체와 데이터 이동

`pvmove`는 LV를 쓰는 중에도 한 PV의 extent를 다른 PV로 옮깁니다. 노후 디스크 교체나 스토리지 이전에 씁니다.

```bash
# 1. 새 디스크를 VG에 추가
sudo pvcreate /dev/sde
sudo vgextend vg_data /dev/sde

# 2. 기존 디스크의 데이터를 이동 (진행률 출력)
sudo pvmove -i 10 /dev/sdb /dev/sde

# 3. 비게 된 PV를 VG에서 빼고 LVM 서명 제거
sudo vgreduce vg_data /dev/sdb
sudo pvremove /dev/sdb
```

`pvmove`는 중단되어도 다시 `pvmove`를 실행하면 이어서 진행합니다. 큰 디스크는 시간이 오래 걸리고 I/O 부하가 생기므로 업무 시간을 피합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 장애 대응

| 증상                                    | 확인                                   | 대응                                                     |
|-----------------------------------------|----------------------------------------|----------------------------------------------------------|
| 부팅 후 LV가 안 보임                    | `vgs`, `lvs`, `lsblk`                  | `vgchange -ay vg_data`로 활성화                          |
| `WARNING: Device for PV ... not found`  | `pvs`에서 `unknown device` 표시        | 디스크 연결 확인. 영구 고장이면 백업에서 복구            |
| 스냅샷 Invalid                          | `lvs`에서 스냅샷 상태 확인             | 스냅샷 삭제 후 크기를 늘려 다시 생성                     |
| thin pool 가득 참                       | `lvs -o data_percent,metadata_percent` | VG에 PV 추가 후 `lvextend`로 pool 확장                   |
| 다른 서버로 디스크 옮긴 뒤 VG 이름 충돌 | `vgs` 결과에 같은 이름 두 개           | `vgimportclone` 또는 `vgrename`(UUID 지정)으로 이름 변경 |

LVM 메타데이터는 `/etc/lvm/backup/`(최신)과 `/etc/lvm/archive/`(변경 이력)에 자동 저장됩니다. 실수로 LV를 지운 직후 같은 PV에 새로 쓰기가 없었다면 `vgcfgrestore`로 메타데이터를 되돌려 복구할 가능성이 있습니다.

🟡 `vgcfgrestore`는 VG 메타데이터 전체를 과거 상태로 덮어씁니다. 먼저 `vgcfgrestore --list vg_data`로 시점을 확인하고, 가능하면 디스크 이미지를 떠 둔 뒤 실행합니다.

```bash
sudo vgcfgrestore --list vg_data
sudo vgcfgrestore -f /etc/lvm/archive/<FILE>.vg vg_data
sudo vgchange -ay vg_data
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. 운영 점검표

| 항목                                                  | 주기         |
|-------------------------------------------------------|--------------|
| VG 여유 공간(`vgs` VFree)과 LV 파일시스템 사용률      | 상시 감시    |
| thin pool `data_percent`·`metadata_percent`           | 상시 감시    |
| COW 스냅샷이 남아 있지 않은지(`lvs`에서 `s` 속성)     | 매일         |
| `/etc/lvm/backup/` 파일을 시스템 백업에 포함          | 백업 주기    |
| `/etc/fstab`에 `nofail`·올바른 장치 이름 사용         | 변경 때      |
| linear LV가 여러 PV에 걸쳐 있으면 하부 RAID 여부 확인 | 구성 변경 때 |
| 축소 작업 전 백업과 사용량 확인                       | 작업 전      |

관련 문서:

- 스토리지 계층과 RAID 선택: [storage_architecture.md](storage_architecture.md)
- 파일시스템 선택: [linux_filesystem_comparison.md](linux_filesystem_comparison.md)
- 소프트웨어 RAID: [mdadm_software_raid.md](mdadm_software_raid.md)

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- lvm(8): [man7.org/linux/man-pages/man8/lvm.8.html](https://man7.org/linux/man-pages/man8/lvm.8.html) — ★★★☆☆ (확인일 2026-11-16)
- lvcreate(8): [man7.org/linux/man-pages/man8/lvcreate.8.html](https://man7.org/linux/man-pages/man8/lvcreate.8.html) — ★★★☆☆ (확인일 2026-11-16)
- lvextend(8): [man7.org/linux/man-pages/man8/lvextend.8.html](https://man7.org/linux/man-pages/man8/lvextend.8.html) — ★★★☆☆ (확인일 2026-11-16)
- lvconvert(8): [man7.org/linux/man-pages/man8/lvconvert.8.html](https://man7.org/linux/man-pages/man8/lvconvert.8.html) — ★★★☆☆ (확인일 2026-11-16)
- lvmthin(7): [man7.org/linux/man-pages/man7/lvmthin.7.html](https://man7.org/linux/man-pages/man7/lvmthin.7.html) — ★★★☆☆ (확인일 2026-11-16)
- fsadm(8): [man7.org/linux/man-pages/man8/fsadm.8.html](https://man7.org/linux/man-pages/man8/fsadm.8.html) — ★★★☆☆ (확인일 2026-11-16)
- xfs_growfs(8): [man7.org/linux/man-pages/man8/xfs_growfs.8.html](https://man7.org/linux/man-pages/man8/xfs_growfs.8.html) — ★★★☆☆ (확인일 2026-11-16)
- LVM2 소스 저장소: [gitlab.com/lvmteam/lvm2](https://gitlab.com/lvmteam/lvm2) — ★★★☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.

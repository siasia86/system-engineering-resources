# mdadm 소프트웨어 RAID 운영 가이드

mdadm은 Linux 커널의 md(Multiple Devices) 드라이버로 소프트웨어 RAID를 만들고 관리하는 도구입니다. 하드웨어 RAID 컨트롤러 없이 여러 디스크를 RAID 1·5·6·10 등으로 묶을 수 있습니다. 이 문서는 구성, 상태 확인, 장애 디스크 교체, 정기 점검(scrub), 알림, 확장 절차를 정리합니다.

> 기준 판: mdadm 4.6 (md-raid-utilities/mdadm 저장소 릴리스 기준, 확인일 2026-11-16). 배포판 패키지 판은 `mdadm --version`으로 확인합니다.

## 목차

| 목차                                                                                    |
|-----------------------------------------------------------------------------------------|
| [1. 개념](#1-개념) / [2. 상태 확인](#2-상태-확인) / [3. 배열 생성](#3-배열-생성)        |
| [4. 설정 파일과 부팅](#4-설정-파일과-부팅) / [5. 장애 디스크 교체](#5-장애-디스크-교체) |
| [6. 정기 점검 (scrub)](#6-정기-점검-scrub) / [7. 모니터링과 알림](#7-모니터링과-알림)   |
| [8. 확장과 변경](#8-확장과-변경) / [9. 트러블슈팅](#9-트러블슈팅)                       |
| [10. 운영 점검표](#10-운영-점검표)                                                      |

---

## 1. 개념

| 용어                   | 설명                                                                |
|------------------------|---------------------------------------------------------------------|
| md 장치                | mdadm이 만드는 RAID 블록 장치. `/dev/md0`, `/dev/md/<이름>`         |
| 구성원(member)         | 배열에 속한 디스크나 파티션                                         |
| superblock(메타데이터) | 구성원마다 기록되는 배열 정보. 배열 재조립에 사용                   |
| spare                  | 대기 디스크. 구성원이 고장 나면 자동으로 재구축에 투입              |
| resync / recover       | 생성·비정상 종료 후 중복 데이터 재계산 / spare로 고장 디스크 재구축 |
| write-intent bitmap    | 변경 구역을 기록해 재동기화 범위를 줄이는 비트맵                    |

메타데이터 판은 superblock 위치가 다릅니다(mdadm man page 기준).

| 판  | 위치                | 비고                                     |
|-----|---------------------|------------------------------------------|
| 1.0 | 장치 끝             | 부트 로더가 일반 파티션처럼 읽어야 할 때 |
| 1.1 | 장치 시작           |                                          |
| 1.2 | 장치 시작에서 4 KiB | `--create`의 기본값                      |

RAID 레벨별 용량·허용 장애 비교는 [storage_architecture.md](storage_architecture.md#8-raid)에 있습니다. 하드웨어 RAID와 비교하면 소프트웨어 RAID는 컨트롤러 고장 위험과 전용 도구 의존이 없고, 디스크를 다른 Linux 서버로 옮겨도 조립할 수 있습니다. 대신 패리티 계산과 재구축에 CPU를 쓰고, 컨트롤러의 배터리 백업 캐시 같은 기능은 없습니다.

🟡 RAID는 디스크 고장에 대한 가용성 수단이며 백업이 아닙니다. 삭제·덮어쓰기·랜섬웨어는 모든 구성원에 그대로 반영됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 상태 확인

```bash
# 커널이 보는 모든 md 장치 요약
cat /proc/mdstat

# 배열 상세 (상태, 구성원, 고장 디스크, 재구축 진행률)
sudo mdadm --detail /dev/md0

# 구성원 디스크의 superblock 확인
sudo mdadm --examine /dev/sdb1
```

`/proc/mdstat` 읽는 법입니다.

```text
md0 : active raid1 sdc1[1] sdb1[0]
      976630464 blocks super 1.2 [2/2] [UU]
      bitmap: 0/8 pages [0KB], 65536KB chunk
```

| 표시               | 의미                                      |
|--------------------|-------------------------------------------|
| `[2/2]`            | 필요한 구성원 수 / 동작 중인 구성원 수    |
| `[UU]`             | 각 구성원 상태. `U` 정상, `_` 빠짐        |
| `(F)`              | 구성원 이름 뒤에 붙으면 고장(faulty) 표시 |
| `(S)`              | spare                                     |
| `recovery = 12.3%` | 재구축 진행률과 예상 시간                 |

`mdadm --detail`의 `State` 줄에 `degraded`가 보이면 구성원이 빠진 상태입니다. 이때 디스크가 하나 더 고장 나면(RAID 1·5 기준) 데이터를 잃습니다.

sysfs에서도 배열 동작 상태를 볼 수 있습니다.

```bash
cat /sys/block/md0/md/sync_action    # idle, resync, recover, check, repair
cat /sys/block/md0/md/degraded       # 빠진 구성원 수
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 배열 생성

🟡 `--create`는 지정한 장치의 기존 데이터를 사용할 수 없게 만듭니다. `lsblk -f`와 `mdadm --examine`으로 대상을 확인한 뒤 실행합니다.

```bash
# 파티션 준비 (GPT, 'Linux RAID' 유형) - 디스크마다 반복
sudo parted -s /dev/sdb mklabel gpt mkpart primary 1MiB 100% set 1 raid on
sudo parted -s /dev/sdc mklabel gpt mkpart primary 1MiB 100% set 1 raid on

# RAID 1 (미러) 생성, 내부 bitmap 사용
sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 \
     --bitmap=internal /dev/sdb1 /dev/sdc1

# RAID 6 (4개 구성원 + spare 1개)
sudo mdadm --create /dev/md1 --level=6 --raid-devices=4 \
     --spare-devices=1 /dev/sd[d-h]1
```

생성 직후에는 resync가 백그라운드로 돌지만 배열은 바로 쓸 수 있습니다. 파일시스템을 올리거나 [LVM](lvm_operations.md) PV로 쓰면 됩니다.

```bash
sudo mkfs.xfs /dev/md0
```

디스크 전체 대신 파티션을 구성원으로 쓰는 이유는 다음과 같습니다.

- 교체 디스크의 실제 용량이 조금 작을 때 파티션 크기로 맞출 수 있습니다.
- 다른 도구가 빈 디스크로 오인해 초기화하는 위험을 줄입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설정 파일과 부팅

배열 정보를 설정 파일에 남겨 두면 부팅 때 이름이 바뀌지 않고 조립됩니다. `--detail --scan` 출력은 `mdadm.conf`에 넣을 수 있는 형식입니다.

| 배포판 계열   | 설정 파일               | initramfs 갱신             |
|---------------|-------------------------|----------------------------|
| Debian/Ubuntu | `/etc/mdadm/mdadm.conf` | `sudo update-initramfs -u` |
| RHEL/Rocky    | `/etc/mdadm.conf`       | `sudo dracut -f`           |

```bash
# Ubuntu 예: 배열 정의 추가
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm/mdadm.conf
sudo update-initramfs -u
```

`mdadm.conf`의 주요 항목입니다.

```text
MAILADDR admin@example.com
ARRAY /dev/md/0 metadata=1.2 UUID=<ARRAY_UUID> name=host:0
```

🟡 `tee -a`를 반복 실행하면 같은 `ARRAY` 줄이 중복됩니다. 추가 전에 파일 내용을 확인합니다.

`/etc/fstab`에는 `/dev/md0` 대신 파일시스템 UUID를 적습니다(`blkid /dev/md0`). md 번호는 설정이 없을 때 `md127`처럼 바뀔 수 있기 때문입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 장애 디스크 교체

교체 절차는 "고장 표시 → 제거 → 물리 교체 → 파티션 복제 → 추가 → 재구축 확인"입니다.

```bash
# 1. 상태 확인과 고장 디스크 특정
cat /proc/mdstat
sudo mdadm --detail /dev/md0
sudo smartctl -a /dev/sdc | grep -iE 'serial|reallocated|pending'

# 2. 아직 커널이 고장 처리하지 않았으면 직접 고장 표시 후 제거
sudo mdadm /dev/md0 --fail /dev/sdc1 --remove /dev/sdc1

# 3. 디스크 물리 교체 (핫스왑 미지원이면 전원 차단 후)

# 4. 정상 디스크의 GPT 파티션 구조를 새 디스크로 복제 후 GUID 재생성
sudo sgdisk -R /dev/sdc /dev/sdb    # sdb(정상) 구조를 sdc(새 디스크)에 복사
sudo sgdisk -G /dev/sdc

# 5. 배열에 추가 -> 자동으로 recover 시작
sudo mdadm /dev/md0 --add /dev/sdc1

# 6. 진행률 확인
watch -n 5 cat /proc/mdstat
```

🟡 `sgdisk -R`의 인자 순서는 `-R <대상> <원본>`입니다. 순서를 바꾸면 정상 디스크의 파티션 표를 덮어씁니다. 실행 전에 시리얼 번호로 대상 디스크를 다시 확인합니다.

교체 때 지켜야 할 점입니다.

- 디스크는 이름(`sdc`)이 아니라 시리얼 번호나 `/dev/disk/by-id/` 경로로 특정합니다. 재부팅 후 이름이 바뀔 수 있습니다.
- OS가 RAID 1 위에 있으면 새 디스크에도 부트 로더를 설치해야 그 디스크만으로 부팅할 수 있습니다(BIOS는 `grub-install /dev/sdc`, UEFI는 ESP 복제 방식이 배포판마다 다름).
- 재구축 중에는 남은 디스크에 읽기 부하가 집중되어 추가 고장 확률이 올라갑니다. 재구축이 끝날 때까지 큰 작업을 미룹니다.

재구축 속도는 `/proc/sys/dev/raid/speed_limit_min`·`speed_limit_max`(KiB/s, 전체 기본값)와 배열별 `/sys/block/md0/md/sync_speed_min`·`sync_speed_max`로 조절합니다. 서비스 부하가 크면 max를 낮추고, 빨리 끝내야 하면 min을 올립니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 정기 점검 (scrub)

디스크의 잠재 불량 섹터는 읽기 전까지 드러나지 않습니다. 재구축 도중 처음 발견되면 데이터를 잃을 수 있으므로, 평소에 전체 읽기 점검을 돌립니다.

```bash
# 점검 시작 (읽기 전용 비교)
echo check | sudo tee /sys/block/md0/md/sync_action

# 진행 확인
cat /proc/mdstat

# 점검 후 불일치 섹터 수
cat /sys/block/md0/md/mismatch_cnt
```

| `sync_action` 값 | 의미                                                        |
|------------------|-------------------------------------------------------------|
| `check`          | 전체 중복 데이터 점검. 읽기 오류 섹터는 다시 써서 교정 시도 |
| `repair`         | 점검과 함께 불일치도 다시 기록                              |
| `idle`           | 진행 중인 작업 없음. 진행 중 작업을 멈출 때도 기록          |

`mismatch_cnt`는 다시 쓰였거나 쓰였을 섹터 수입니다. 페이지 단위로 계산하므로 실제 오류 수보다 클 수 있습니다. RAID 1·10에서는 swap 같은 사용 패턴 때문에 0이 아닐 수 있으므로, 값 자체보다 점검 때마다 늘어나는지를 봅니다.

많은 배포판이 정기 점검을 이미 설정해 둡니다. Debian/Ubuntu는 `checkarray` 스크립트를 쓰고, mdadm 상위 저장소는 `mdcheck_start.timer` 같은 systemd 타이머를 제공합니다. 설정 여부는 `systemctl list-timers | grep -i md`로 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 모니터링과 알림

`mdadm --monitor`는 배열 상태 변화(Fail, DegradedArray, SpareActive 등)를 감지해 메일이나 프로그램으로 알립니다.

```bash
# 모든 배열 감시, 메일 알림, 백그라운드 실행 (기본 확인 간격 60초)
sudo mdadm --monitor --scan --daemonise --mail=admin@example.com

# 알림 경로 시험: 각 배열에 TestMessage 발송
sudo mdadm --monitor --scan --oneshot --test
```

대부분의 배포판은 `mdmonitor.service`(RHEL 계열)나 `mdadm` 패키지의 서비스로 이 기능을 켜 두고, `mdadm.conf`의 `MAILADDR`이나 `PROGRAM` 줄을 읽습니다. 메일 발송에는 로컬 MTA 설정이 필요합니다.

Prometheus를 쓰면 node_exporter의 기본 활성 `mdadm` collector가 다음 지표를 노출합니다([node_exporter 운영](../monitoring/node_exporter_operations.md) 참고).

| 지표                                       | 의미                      |
|--------------------------------------------|---------------------------|
| `node_md_disks{state="failed"}`            | 고장 구성원 수            |
| `node_md_disks{state="spare"}`             | spare 수                  |
| `node_md_degraded`                         | 빠진 구성원 수 (sysfs 값) |
| `node_md_blocks_synced` / `node_md_blocks` | 동기화 진행률 계산용      |

```yaml
# 알림 규칙 예
- alert: MdRaidDegraded
  expr: node_md_degraded > 0 or node_md_disks{state="failed"} > 0
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "md array {{ $labels.device }} on {{ $labels.instance }} is degraded"
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 확장과 변경

`--grow`로 구성원 수나 레벨을 바꿀 수 있습니다. 구성원 수(`-n`) 변경은 RAID 1·4·5·6에서 지원합니다.

🟡 reshape(배열 재배치)는 수 시간에서 수일이 걸리고 중간 장애 시 위험이 있습니다. 시작 전에 백업을 확보합니다.

```bash
# RAID 5에 디스크 추가: 먼저 spare로 넣고 구성원 수를 늘림
sudo mdadm /dev/md1 --add /dev/sdi1
sudo mdadm --grow /dev/md1 --raid-devices=5

# reshape 완료 후 상위 계층 확장
# LVM PV인 경우
sudo pvresize /dev/md1
# 파일시스템이 바로 올라간 경우 (XFS)
sudo xfs_growfs /srv/data
```

디스크를 모두 큰 용량으로 바꾼 뒤에는 하나씩 교체·재구축을 마치고 `mdadm --grow /dev/md0 --size=max`로 배열 크기를 늘립니다.

배열을 해체하는 절차입니다.

🟡 `--zero-superblock`은 구성원의 RAID 정보를 지웁니다. 해당 디스크를 배열에 다시 넣을 계획이 없을 때만 실행합니다.

```bash
sudo umount /srv/data
sudo mdadm --stop /dev/md0
sudo mdadm --zero-superblock /dev/sdb1 /dev/sdc1
# mdadm.conf의 ARRAY 줄 삭제 후 initramfs 갱신
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                           | 확인                                  | 대응                                          |
|--------------------------------|---------------------------------------|-----------------------------------------------|
| 부팅 후 `md127`로 이름이 바뀜  | `mdadm.conf`에 ARRAY 줄 유무          | 설정 추가 후 initramfs 갱신                   |
| 배열이 `inactive`              | `cat /proc/mdstat`, `mdadm --examine` | `mdadm --assemble --scan`으로 재조립          |
| 재구축이 매우 느림             | `speed_limit_*`, 서비스 I/O           | 업무 외 시간에 `speed_limit_min` 상향         |
| 같은 디스크가 반복해서 `(F)`   | `smartctl -a`, `dmesg`                | 케이블·포트 교체 후에도 반복되면 디스크 교체  |
| `mismatch_cnt`가 점검마다 증가 | 디스크 SMART, 메모리 오류 로그        | 하드웨어 점검. 원인 확인 전 `repair`는 신중히 |

🟡 구성원 여러 개가 동시에 빠져 배열이 조립되지 않을 때 `--assemble --force`나 `--create --assume-clean`으로 강제 복구하는 방법이 알려져 있지만, 순서나 옵션이 틀리면 복구 가능성이 사라집니다. 먼저 모든 구성원의 `mdadm --examine` 출력을 저장하고, 가능하면 디스크 이미지를 떠 둔 뒤 진행합니다.

```bash
# 현재 상태 증거 보존
for d in /dev/sd[b-e]1; do sudo mdadm --examine "$d"; done > /root/md_examine_$(date +%F).txt
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. 운영 점검표

| 항목                                                | 주기      |
|-----------------------------------------------------|-----------|
| `/proc/mdstat`에 `_`·`(F)` 없음, `degraded` 아님    | 상시 감시 |
| `mdadm --monitor` 또는 node_exporter 알림 동작 시험 | 분기      |
| 정기 `check` 실행과 `mismatch_cnt` 추이             | 월 1회    |
| 구성원 디스크 SMART 상태                            | 주 1회    |
| `mdadm.conf`와 initramfs가 현재 배열과 일치         | 변경 때   |
| 교체용 디스크 재고와 디스크별 시리얼 대장           | 분기      |
| OS 배열이면 모든 구성원에 부트 로더 설치 확인       | 교체 때   |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- mdadm(8): [man7.org/linux/man-pages/man8/mdadm.8.html](https://man7.org/linux/man-pages/man8/mdadm.8.html) — ★★★☆☆ (확인일 2026-11-16)
- Linux kernel RAID arrays (md) 관리 문서: [docs.kernel.org/admin-guide/md.html](https://docs.kernel.org/admin-guide/md.html) — ★★★☆☆ (확인일 2026-11-16)
- mdadm 공식 저장소: [github.com/md-raid-utilities/mdadm](https://github.com/md-raid-utilities/mdadm) — ★★★☆☆ (확인일 2026-11-16)
- node_exporter mdadm collector 소스: [collector/mdadm_linux.go](https://github.com/prometheus/node_exporter/blob/master/collector/mdadm_linux.go) — ★★★☆☆ (확인일 2026-11-16)
- Linux RAID Wiki (보관본): [archive.kernel.org/oldwiki/raid.wiki.kernel.org](https://archive.kernel.org/oldwiki/raid.wiki.kernel.org/) — ★★☆☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.

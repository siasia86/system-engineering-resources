# GRAID SupremeRAID 서버 점검 가이드
<!-- reference: _reference/graid_supremeraid_official_notes.md -->

SupremeRAID (GPU 기반 NVMe RAID) 환경의 정기 점검 절차를 정리합니다. 하드웨어 모델(SR-1010/SR-1000)이나 RAID 레벨(5/6/10)에 관계없이 적용 가능합니다.

## 목차

| 섹션                                                                                                                         |
|------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 점검 주기](#2-점검-주기) / [3. 일일 점검](#3-일일-점검)                                             |
| [4. 주간 점검](#4-주간-점검) / [5. 월간 점검](#5-월간-점검) / [6. 분기 점검](#6-분기-점검)                                   |
| [7. Consistency Check 운영](#7-consistency-check-운영) / [8. SSD 수명 관리](#8-ssd-수명-관리) / [9. 장애 대응](#9-장애-대응) |
| [10. 드라이버 업데이트 절차](#10-드라이버-업데이트-절차) / [11. 점검 체크리스트](#11-점검-체크리스트)                        |

---

## 1. 개요

### SupremeRAID란

SupremeRAID는 **GPU를 RAID 컨트롤러로 사용**하는 NVMe RAID 솔루션입니다. 일반 HW RAID 카드(MegaRAID 등)는 전용 ARM/PPC CPU로 패리티를 계산하지만, SupremeRAID는 GPU(CUDA 코어)의 병렬 연산 능력을 활용하여 NVMe SSD의 원래 성능을 유지하면서 RAID 보호를 제공합니다.


| 항목          | 일반 HW RAID (MegaRAID 등) | SupremeRAID              |
|---------------|----------------------------|--------------------------|
| 연산 장치     | 전용 ARM/PPC CPU           | GPU (CUDA cores)         |
| NVMe 지원     | 불가 또는 성능 병목        | 네이티브 NVMe, 성능 유지 |
| IOPS          | ~100만                     | ~1,400만+ (공식)         |
| 대역폭        | ~12 GB/s                   | ~110 GB/s (공식)         |
| 연결 방식     | SAS/SATA 백플레인          | PCIe 직접 연결           |
| 디바이스 경로 | `/dev/sdX`                 | `/dev/gdgXnY`            |
| 관리 도구     | storcli / megacli          | graidctl                 |


> 출처: https://www.graidtech.com/ | https://docs.graidtech.com/sr/

### 아키텍처 스택

```
┌────────────────────────────────────────────────────────┐
│              Linux / Windows OS                        │
├────────────────────────────────────────────────────────┤
│              graidctl / graid_server                   │
├────────────────────────────────────────────────────────┤
│              graid.ko (kernel module)                  │
├────────────────────────────────────────────────────────┤
│         SupremeRAID GPU Card (SR-1010 etc.)            │
├─────────┬─────────┬─────────┬─────────┬────────────────┤
│ NVMe 0  │ NVMe 1  │ NVMe 2  │ NVMe 3  │  ...           │
└─────────┴─────────┴─────────┴─────────┴────────────────┘
```

### 계층별 상세 설명

#### NVMe SSD (물리 디스크)

- 일반 서버에서는 NVMe SSD가 OS에 `/dev/nvme0n1`으로 직접 노출됩니다.
- `graidctl create physical_drive` 실행 시 해당 SSD는 OS 네임스페이스(`/dev/nvmeXn1`)에서 해제됩니다.
- 해제된 SSD는 `/dev/gpdX` 경로로만 노출되며, SMART 조회 등 관리 명령에 사용됩니다.

#### GPU Card (하드웨어 RAID 엔진)

- CUDA 코어가 RAID 5/6의 패리티 계산 또는 RAID 1/10의 미러 복제를 수행합니다.
- 패리티 연산이 GPU에서 처리되므로 호스트 CPU의 RAID 관련 부하가 발생하지 않습니다.
- RAID 메타데이터는 SSD에 저장됩니다. GPU 교체 시 새 라이선스 키와 함께 복구 절차를 진행할 수 있습니다.

#### graid.ko (커널 모듈)

- Linux 커널에 로드되는 드라이버입니다.
- OS의 블록 I/O 요청을 인터셉트하여 GPU로 전달하고, GPU 처리 결과를 SSD에 기록합니다.
- Virtual Drive(`/dev/gdgXnY`)를 커널에 블록 디바이스로 등록합니다.
- 커널 버전에 종속됩니다 — 미지원 커널에서는 모듈 로드가 실패합니다.

#### graidctl / graid_server (사용자 공간)

- `graid_server`: 백그라운드 데몬. GPU 펌웨어와 통신하여 RAID 상태 모니터링 및 이벤트 수집을 수행합니다.
- `graidctl`: CLI 도구. PD/DG/VD 생성, 삭제, 교체, CC 실행 등 모든 관리 작업을 수행합니다.
- `graid-mgr` (1.6+): 웹 기반 GUI/REST API 인터페이스입니다.

#### Linux / Windows OS (최상위)

- OS는 Virtual Drive(`/dev/gdgXnY`)를 일반 블록 디바이스로 인식합니다.
- `mkfs`, `mount`, `fio` 등 표준 블록 디바이스 명령어가 그대로 동작합니다.

### 데이터 흐름

```
Application writes to /dev/gdg0n1                                        
         │                                                               
         v                                                               
┌─────────────────────────┐                                              
│   OS (Block Layer)      │  normal block I/O request                    
└─────────┬───────────────┘                                              
          │                                                              
          v                                                              
┌─────────────────────────┐                                              
│   graid.ko              │  intercept I/O, forward to GPU               
└─────────┬───────────────┘                                              
          │                                                              
          v                                                              
┌─────────────────────────┐                                              
│   GPU (CUDA cores)      │  parity calc (RAID 5/6) or mirror (RAID 1/10)
└─────────┬───────────────┘                                              
          │                                                              
          v                                                              
┌─────────────────────────┐                                              
│  NVMe SSD 0, 1, 2 ...   │  data + parity distributed across SSDs        
└─────────────────────────┘                                              
```

### RAID 논리 구성 요소

| 구성 요소      | 약칭 | 디바이스 경로 | 설명                                 |
|----------------|------|---------------|--------------------------------------|
| Physical Drive | PD   | `/dev/gpdX`   | RAID 전용으로 할당된 NVMe SSD        |
| Drive Group    | DG   | -             | RAID 레벨이 적용된 PD 그룹           |
| Virtual Drive  | VD   | `/dev/gdgXnY` | OS에 노출되는 볼륨 (mkfs/mount 대상) |
| Controller     | CX   | -             | GPU RAID 컨트롤러 (온도, 팬, SN)     |

#### 구성 흐름

```
NVMe SSD                                         
    │  graidctl create physical_drive            
    v                                            
Physical Drive (PD, /dev/gpdX)                   
    │  graidctl create drive_group --raid-level 5
    v                                            
Drive Group (DG)                                 
    │  graidctl create virtual_drive             
    v                                            
Virtual Drive (VD, /dev/gdgXnY)                  
    │  mkfs.xfs / mount                          
    v                                            
Application usage                                
```

#### systemd 서비스 구조 및 부팅 순서

graid-sr-installer 실행 시 아래 service unit 파일이 자동 설치됩니다.

| 파일                                                     | 역할                                       |
|----------------------------------------------------------|--------------------------------------------|
| `/usr/lib/systemd/system/graid.service`                  | 메인 서비스 (graid_server 데몬)            |
| `/usr/lib/systemd/system/graidcore@.service`             | GPU 코어 인스턴스 (템플릿 unit)            |
| `/etc/systemd/system/sysinit.target.wants/graid.service` | `systemctl enable` 시 생성되는 심볼릭 링크 |

🟡 Debian 계열에서 `/lib/systemd/system/`은 `/usr/lib/systemd/system/`의 심볼릭 링크이므로 동일 파일이 두 경로에 보입니다.

| 경로                       | 용도                                            |
|----------------------------|-------------------------------------------------|
| `/usr/lib/systemd/system/` | 패키지/installer가 설치하는 unit 위치           |
| `/etc/systemd/system/`     | 관리자가 직접 생성하거나 override하는 unit 위치 |

**부팅 순서:**

```
1. local-fs.target        (OS 파티션 마운트)
2. graidcore@0, @1        (GPU 초기화)
3. graid.service          (graid_server 시작, VD 인식)
4. fstab mount            (x-systemd.requires=graid.service → VD 마운트)
5. sysinit.target 완료
6. 이후 서비스 시작
```

**graid.service unit 전체 (`/usr/lib/systemd/system/graid.service`):**

```ini
[Unit]
Description="Graid Server"
Wants=graidcore@0.service graidcore@1.service
After=local-fs.target graidcore@0.service graidcore@1.service
Before=sysinit.target shutdown.target
Conflicts=shutdown.target
DefaultDependencies=no

[Service]
Type=notify
ExecStartPre=/usr/bin/graid_server_pre.sh
ExecStart=/usr/bin/graid_server
KillMode=process
Restart=no
RestartSec=55s
TimeoutStopSec=60s
OOMScoreAdjust=-1000
LimitNOFILE=65536

[Install]
WantedBy=sysinit.target
```

**[Unit] 섹션:**

| 설정                                            | 의미                                                          |
|-------------------------------------------------|---------------------------------------------------------------|
| `Wants=graidcore@0.service graidcore@1.service` | GPU 코어 서비스를 함께 시작 요청 (실패해도 graid는 시작 시도) |
| `After=local-fs.target`                         | OS 파일시스템 마운트 완료 후 시작                             |
| `After=graidcore@0.service graidcore@1.service` | GPU 코어 초기화 완료 후 시작                                  |
| `Before=sysinit.target`                         | sysinit 완료 전에 graid 준비 보장                             |
| `Before=shutdown.target`                        | 셧다운 절차 시작 전에 graid가 먼저 정리됨                     |
| `Conflicts=shutdown.target`                     | shutdown 진입 시 graid.service 자동 중지                      |
| `DefaultDependencies=no`                        | systemd 기본 의존성 무시 (부팅 초기 실행을 위해 직접 제어)    |

**[Service] 섹션:**

| 설정                                        | 의미                                                     |
|---------------------------------------------|----------------------------------------------------------|
| `Type=notify`                               | graid_server가 준비 완료 시 systemd에 알림 (sd_notify)   |
| `ExecStartPre=/usr/bin/graid_server_pre.sh` | graid_server 시작 전 사전 스크립트 실행 (환경 초기화)    |
| `ExecStart=/usr/bin/graid_server`           | 메인 데몬 바이너리                                       |
| `KillMode=process`                          | 중지 시 메인 프로세스만 종료 (자식 프로세스는 별도 처리) |
| `Restart=no`                                | 비정상 종료 시 자동 재시작하지 않음 (수동 개입 필요)     |
| `RestartSec=55s`                            | 재시작 시 55초 대기 (Restart=no이므로 실질적으로 미사용) |
| `TimeoutStopSec=60s`                        | 종료 시 60초 대기 후 강제 종료                           |
| `OOMScoreAdjust=-1000`                      | OOM Killer 대상에서 제외 (최저 점수)                     |
| `LimitNOFILE=65536`                         | 프로세스 최대 열린 파일 수 65536                         |

**[Install] 섹션:**

| 설정                      | 의미                                                           |
|---------------------------|----------------------------------------------------------------|
| `WantedBy=sysinit.target` | `systemctl enable` 시 sysinit.target.wants/에 심볼릭 링크 생성 |

🟡 `Restart=no` 설정으로 인해 graid_server가 비정상 종료되면 자동 복구되지 않습니다. 장애 감지 시 수동으로 `systemctl start graid` 실행이 필요합니다.

**상태 확인:**

```bash
systemctl status graid.service
systemctl status graidcore@0.service
# 또는
systemctl is-active graid.service graidcore@0.service graidcore@1.service
```

> 출처: SupremeRAID Linux User Guide v1.7.2 (p.62) — `systemctl enable graid` / `systemctl start graid`

#### VD 자동 마운트 설정 (fstab)

VD 생성 후 `/etc/fstab`에 등록하여 부팅 시 자동 마운트를 설정합니다. graid.service가 시작된 후 마운트되도록 의존성을 명시해야 합니다.

> "It is critically important to follow these instructions to guarantee that the RAID group mounts automatically during system boot and to avoid any improper or unclear shutdown processes that could cause the RAID group to enter resync mode."
>
> — SupremeRAID Linux User Guide v1.7.2 (p.96)

**Debian 계열 (Ubuntu):**

```bash
# /etc/fstab
/dev/disk/by-id/<VD_ID>  /mnt/<name>  xfs  x-systemd.requires=graid.service,nofail  0  0
```

**RHEL 계열 (Rocky, CentOS):**

```bash
# /etc/fstab
/dev/disk/by-id/<VD_ID>  /mnt/<name>  xfs  x-systemd.wants=graid.service,x-systemd.automount,nofail  0  0
```

| 옵션                               | 의미                                  |
|------------------------------------|---------------------------------------|
| `x-systemd.requires=graid.service` | graid.service 시작 후 마운트 (Debian) |
| `x-systemd.wants=graid.service`    | graid.service 시작 후 마운트 (RHEL)   |
| `x-systemd.automount`              | 접근 시 자동 마운트 (RHEL)            |
| `nofail`                           | 마운트 실패 시 부팅 중단하지 않음     |

> 출처: SupremeRAID Linux User Guide v1.7.2 (p.152)

🟡 `nofail` 없이 VD 마운트가 실패하면 시스템이 emergency mode로 진입합니다. 반드시 포함합니다.

#### 추가 옵션: discard (v1.6.1+)

파일 삭제 시 SSD에 deallocate(TRIM) 명령을 전달하여 write amplification을 줄이고 SSD 수명을 연장합니다.

```bash
# discard 포함 예시 (Debian)
/dev/disk/by-id/<VD_ID>  /mnt/<name>  xfs  x-systemd.requires=graid.service,nofail,discard  0  0
```

> "To ensure the filesystem can take advantage of this capability and issue discard commands when files are deleted, it must be mounted with the discard option."
>
> — SupremeRAID Linux User Guide v1.7.2 (p.19)

| 조건                              | 동작                                           |
|-----------------------------------|------------------------------------------------|
| SSD가 deallocate + 제로 반환 지원 | deallocate 명령 전달 (자동 활성화)             |
| SSD가 제로 반환 미지원            | write zeros 명령으로 대체 (데이터 정합성 보장) |
| 최소 discard 범위                 | 4KB (LBA 정렬)                                 |
| 최대 discard 범위                 | ~400 GiB / 명령                                |

🟡 `discard` 옵션은 Linux driver v1.6.1 이상에서만 지원됩니다. 이전 버전에서는 무시됩니다.

### 지원 사양

| 항목                   | 값                        |
|------------------------|---------------------------|
| 지원 RAID 레벨         | 0, 1, 5, 6, 10            |
| 최대 Physical Drive 수 | 32                        |
| 최대 Drive Group 수    | 8                         |
| 최대 Virtual Drive 수  | 1,023 / Drive Group       |
| Dual Controller (HA)   | 지원 (Linux만)            |
| NVMe-oF                | 지원 (Remote RAID Volume) |
| SAS/SATA               | 지원 (scsi_drive)         |

### RAID 레벨별 최소 드라이브

| RAID | 최소 드라이브 | 패리티/미러       | 허용 장애 수 |
|------|---------------|-------------------|--------------|
| 0    | 1             | 없음              | 0            |
| 1    | 2             | 미러링            | 1            |
| 5    | 3             | 단일 패리티       | 1            |
| 6    | 4             | 이중 패리티       | 2            |
| 10   | 2             | 미러 + 스트라이프 | 1 per mirror |

### 핵심 포인트

- **GPU가 RAID 컨트롤러** — 별도 RAID 카드 불필요합니다.
- **NVMe 성능 보존** — CPU가 패리티 계산을 하지 않으므로 SSD 원래 속도를 유지합니다.
- **VD만 블록 디바이스로 노출** — OS는 PD를 직접 마운트할 수 없으며, VD(`/dev/gdgXnY`)만 파일시스템으로 사용합니다.
- **RAID 메타데이터가 SSD에 저장됨** — GPU 교체 절차가 공식 문서에 존재하며, SSD를 다른 서버로 이관할 수 있습니다.
- **커널 종속** — 미지원 커널 부팅 시 볼륨 접근 불가 (데이터 유실 아님)

### graidctl CLI 구조 (v1.5+)

| 명령어                               | 용도      |
|--------------------------------------|-----------|
| `graidctl list <component>`          | 목록 조회 |
| `graidctl describe <component> <id>` | 상세 조회 |
| `graidctl create <component>`        | 생성      |
| `graidctl delete <component> <id>`   | 삭제      |
| `graidctl start <task> <id>`         | 작업 시작 |
| `graidctl stop <task> <id>`          | 작업 중지 |
| `graidctl set <component>`           | 설정 변경 |
| `graidctl replace <component>`       | 교체      |
| `graidctl version`                   | 버전 확인 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 점검 주기

| 주기 | 점검 항목                                       | 소요 시간 (추정) |
|------|-------------------------------------------------|------------------|
| 일일 | 상태 확인, 이벤트 로그                          | ~2분             |
| 주간 | SMART 요약, GPU 온도, 디스크 사용량             | ~5분             |
| 월간 | Consistency Check, SMART 상세, 펌웨어 확인      | 20분+            |
| 분기 | 드라이버/커널 호환 확인, 수명 예측, 성능 기준선 | ~30분            |

🟡 소요 시간은 환경(DG 수, SSD 수)에 따라 상이합니다. 월간 CC 소요 시간은 공식 FAQ 기준(~10 GB/sec)입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 일일 점검

### 3.1 전체 상태 확인

```bash
graidctl list controller
# 기대: STATE = ONLINE

graidctl list drive_group
# 기대: 모든 DG STATE = OPTIMAL

graidctl list virtual_drive
# 기대: 모든 VD STATE = OPTIMAL

graidctl list physical_drive
# 기대: 모든 PD STATE = ONLINE
```

### 3.2 이벤트 확인

```bash
graidctl list event
```

### 3.3 정상 상태 기준

| 컴포넌트   | 정상 상태 | 비정상 시 조치                         |
|------------|-----------|----------------------------------------|
| Controller | ONLINE    | 즉시 벤더(GRAID) 지원 요청 + §9.2 절차 |
| DG         | OPTIMAL   | DEGRADED → 디스크 교체                 |
| VD         | OPTIMAL   | DEGRADED → DG 확인                     |
| PD         | ONLINE    | FAILED → 교체 절차                     |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 주간 점검

### 4.1 DG 상세 확인

```bash
graidctl describe drive_group <dg_id>
# 확인: State, Running Controller, Attributes
```

### 4.2 NVMe SMART 요약

```bash
# 전체 PD SMART 주요 항목
for dev in /dev/gpd*; do
    echo "=== ${dev} ==="
    nvme smart-log "${dev}" 2>/dev/null | grep -i "temperature\|percentage_used\|available_spare"
done
```

| SMART 항목      | 정상 범위 | 주의 기준                |
|-----------------|-----------|--------------------------|
| Temperature     | < 70°C    | > 75°C 경고, > 80°C 위험 |
| Percentage Used | < 80%     | > 90% 교체 계획          |
| Available Spare | > 10%     | < 10% 교체 계획          |

### 4.3 디스크 사용량

```bash
df -h /dev/gdg*
```

### 4.4 GPU 온도 확인

```bash
nvidia-smi --query-gpu=temperature.gpu,fan.speed --format=csv,noheader
```

#### 출력 예시 (`nvidia-smi` 전체)

```
|   0  NVIDIA RTX A2000               On  |   00000000:A0:00.0 Off |                 Off* |
| 30%   47C    P2             32W /   70W |    1330MiB /   6138MiB |    100%   E. Process |
|=========================================================================================|
|    0   N/A  N/A       606      C   /usr/bin/graid_core                          1316MiB |
```

#### 확인 항목

| 항목     | 위치         | 정상 범위     | 비고                             |
|----------|--------------|---------------|----------------------------------|
| Fan      | `30%`        | 제조사별 상이 | 팬 0%이면 팬 고장 의심           |
| Temp     | `47C`        | < 80°C        | 지속 80°C 이상 시 공기 흐름 확인 |
| Pwr      | `32W / 70W`  | Cap 미만      | Cap 도달 시 throttling 발생      |
| GPU-Util | `100%`       | 항상 100%     | SupremeRAID 정상 동작 (polling)  |
| Process  | `graid_core` | 존재          | 없으면 서비스 장애               |

🟡 `GPU-Util 100%`와 `graid_core` 프로세스 존재가 정상 상태의 핵심 지표입니다.

> "The SupremeRAID™ GPU utilization shows 100% at all times. This is to be expected due to a polling mechanism requirement."
>
> — graidtech.com/faq/

[⬆ 목차로 돌아가기](#목차)

---

## 5. 월간 점검

### 5.1 Consistency Check 실행

CC는 DG가 OPTIMAL 또는 PARTIALLY_DEGRADED 상태일 때 실행 가능하며, 운영 중(서비스 가동 상태)에서도 실행할 수 있습니다.

> "These checks can be performed on a regular schedule or manually initiated as needed."
>
> — SupremeRAID Linux User Guide v1.7.2 (p.13)

> "A consistency check can only run when the DG is in OPTIMAL or PARTIALLY_DEGRADED state."
>
> — SupremeRAID Linux User Guide v1.7.2 (p.122)

```bash
# 각 DG에 대해 실행
graidctl start consistency_check <dg_id>

# 진행 상태 확인
graidctl describe consistency_check
```

🟡 예상 속도: ~10 GB/sec (FAQ 기준). 10TB DG ≈ 17분. CC 중 드라이브 읽기 대역을 사용하므로 I/O 성능에 영향이 있을 수 있습니다.

### 5.2 SMART 상세

```bash
nvme smart-log /dev/gpd<id>
```

### 5.3 커널/드라이버 호환 확인

```bash
uname -r
graidctl version

# 커널 업데이트 보류 확인
apt list --upgradable 2>/dev/null | grep linux-image
```

🟡 커널 업데이트 전 반드시 https://docs.graidtech.com/ 지원 목록 확인 필수입니다.

### 5.4 라이선스 확인

```bash
graidctl describe license
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 분기 점검

### 6.1 SSD 수명 예측

```bash
for dev in /dev/gpd*; do
    echo -n "${dev}: "
    nvme smart-log "${dev}" 2>/dev/null | grep "percentage_used"
done
```

수명 예측 공식 (운영 경험 기반 추정, NVMe Health Information Log 필드 활용):

```
남은 수명(월) = (100 - percentage_used) ÷ (월간 증가율)
월간 증가율 = (현재값 - 3개월 전 값) ÷ 3
```

### 6.2 성능 기준선 측정

```bash
# 순차 읽기 (비파괴, read-only)
fio --name=seqread --filename=/dev/gdg<X>n1 --rw=read \
    --bs=128k --numjobs=4 --iodepth=32 --size=1G \
    --runtime=30 --time_based --group_reporting --readonly
```

🟡 운영 중 성능 테스트는 반드시 read-only로만 실행합니다.

### 6.3 드라이버/펌웨어 업데이트 검토

```bash
graidctl describe drive_group <dg_id> | grep Firmware
# 최신 버전: https://docs.graidtech.com/sr/release-notes/linux/
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Consistency Check 운영

### 개요

Consistency Check(CC)는 RAID 어레이의 패리티/미러 데이터 정합성을 검증하는 백그라운드 작업입니다. 드라이브 간 데이터 불일치를 사전에 탐지하여 silent data corruption을 방지합니다.

| 항목           | 내용                                    |
|----------------|-----------------------------------------|
| 목적           | 패리티/미러 정합성 검증, 비트 부패 탐지 |
| 권장 주기      | 월 1회 (공식 FAQ)                       |
| 예상 속도      | ~10 GB/sec (드라이브 성능 의존)         |
| 예상 소요 시간 | 10TB DG → 약 17분                       |
| 운영 중 I/O    | 가능 (백그라운드 실행, I/O 영향 최소)   |
| RAID 0 지원    | ❌ (패리티 없음, CC 불가)               |
| 지원 RAID 레벨 | RAID 1, 5, 6, 10                        |


### 동작 원리 (공식 문서)

CC 실행 시 시스템은 DG 내 각 디스크의 데이터를 비교하여 불일치나 오류를 탐지합니다. 관리자가 설정한 정책에 따라 오류를 자동 수정(`auto_fix`)하거나, 검사를 중지하고 오류를 보고(`stop_on_error`)합니다. 이를 통해 silent data corruption을 조기에 탐지하고 복구합니다.

> "The consistency check function allows administrators to ensure that the data stored on the SupremeRAID™ system is intact and uncorrupted. While running the consistency check, the system compares the data on each disk to identify any discrepancies or errors. Depending on the settings chosen by the administrator, the consistency check function can either automatically fix any errors that are found or stop the check and alert the administrator to any detected errors."
>
> — SupremeRAID Linux User Guide v1.7.2 (p.13)

> "This process aids in the early detection and rectification of silent data corruption."
>
> — graidtech.com/faq/ (Data Integrity)

### Policy 옵션

| Policy        | 동작                                       | 사용 시나리오           |
|---------------|--------------------------------------------|-------------------------|
| auto_fix      | 불일치 발견 시 자동으로 복구               | 일반 운영 환경 (권장)   |
| stop_on_error | 불일치 발견 시 CC 중지, 이벤트 로그에 기록 | 원인 분석이 필요한 경우 |

### 권장 설정

| 항목         | 권장 값                         |
|--------------|---------------------------------|
| Schedule     | 월 1회                          |
| Policy       | auto_fix                        |
| Excluded DGs | 없음 (모든 DG를 CC 대상에 포함) |

### CC 최초 설정 절차 (권장 순서)

기본 설정(`stop_on_error`, schedule off)에서 운영 권장 설정으로 전환하는 절차입니다.

```bash
# 1. 현재 설정 확인
graidctl describe consistency_check

# 2. 먼저 stop_on_error 상태에서 수동 1회 실행 (현황 파악)
graidctl start consistency_check <dg_id>
graidctl describe consistency_check
# 결과 확인: 에러 0건이면 auto_fix 전환 안전

# 3. auto_fix로 전환
graidctl set consistency_check --policy auto_fix

# 4. 스케줄 활성화 (월 1회)
graidctl set consistency_check --schedule-mode on
```

🟡 처음부터 `auto_fix`로 전환하지 않는 이유: 기존 불일치가 있을 경우 원인 파악 없이 자동 수정되므로, 최초 1회는 `stop_on_error`로 실행하여 불일치 건수를 먼저 확인합니다.

### CC 설정 변경

```bash
# 정책 변경
graidctl set consistency_check --policy auto_fix

# 스케줄 옵션 확인
graidctl set consistency_check --help
```

### CC 수동 실행

```bash
# 특정 DG에 대해 실행
graidctl start consistency_check <dg_id>

# 진행 상태 확인 (progress %)
graidctl describe consistency_check

# 중지 (필요 시 — 재시작하면 처음부터)
graidctl stop consistency_check <dg_id>
```

### CC 결과 해석

| 결과      | 의미                     | 조치                            |
|-----------|--------------------------|---------------------------------|
| COMPLETED | 정상 완료, 에러 없음     | 없음                            |
| FIXED     | 불일치 발견 후 자동 복구 | 이벤트 로그 확인, PD SMART 점검 |
| ERROR     | 복구 불가 불일치         | 드라이브 상태 확인, 교체 검토   |

### CC 주의사항

**공식 문서 근거:**

- RAID 0 DG에서는 CC를 시작할 수 없습니다.

> "The consistency check function is not supported on SupremeRAID™ systems configured in RAID0 mode because RAID0 does not provide data redundancy."
>
> — SupremeRAID Linux User Guide v1.7.2 (p.13)

**운영 권장 사항 (공식 문서 미기재):**

- CC 실행 중 드라이버 업데이트/리부팅을 피하고, CC 완료 후 진행합니다.
- CC 중 PD 장애 발생 시 리빌드를 우선 확인합니다.
- `FIXED` 결과가 동일 PD에서 반복 발생하면 해당 PD의 SMART를 확인하고 교체를 검토합니다.

### Live 운영 시 주의사항

#### 커널/OS 업데이트

| 항목                     | 규칙                                                   |
|--------------------------|--------------------------------------------------------|
| 커널 업데이트 전         | 공식 지원 목록 확인 필수 (https://docs.graidtech.com/) |
| 미지원 커널 부팅 시      | graid.ko 로드 실패 → 볼륨 접근 불가 (데이터 유실 아님) |
| 커널 + 드라이버 동시작업 | 금지 — 하나씩 순차 진행                                |
| 롤백 계획                | 이전 커널 GRUB 엔트리 유지 필수                        |
| unattended-upgrades      | linux-image 자동 업데이트 제외 설정 권장               |

#### 드라이버 업그레이드

| 현재 버전 | 대상 버전       | 경로                                    |
|-----------|-----------------|-----------------------------------------|
| 1.x       | 2.0.0 Update 93 | 1.x → 1.7.2 Update 67 → 2.0.0 Update 93 |
| 1.7.2+    | 2.0.0 Update 93 | 직접 업그레이드 가능                    |

- 1.x에서 2.0.0으로 **직접 업그레이드 불가** — 반드시 1.7.2 Update 67 경유합니다.
- 업그레이드 중 DG가 일시적으로 `TRANSFORMING` 상태 진입 가능 → `OPTIMAL` 복귀 확인 후 서비스 재개합니다.
- 2.0.0부터 V2 라이선스 필요 — 업그레이드 전 사전 확보합니다.

#### GPU 관련

- SupremeRAID GPU는 `nvidia-smi`에서 항상 100% utilization 표시 → 정상 (polling mechanism)
- GPU를 일반 CUDA/AI 워크로드와 공유할 수 없습니다.
- GPU 물리 교체 시 새 라이선스 키가 필요합니다 (시리얼 넘버 종속)
- GPU 온도는 `nvidia-smi` 또는 `graidctl show controller` (v1.5) / `graidctl describe controller` (v2.0+)로 확인합니다.

#### 리빌드 중 운영

| 항목               | 규칙                                       |
|--------------------|--------------------------------------------|
| 리빌드 중 I/O      | 가능하나 성능 저하 (백그라운드 대역 사용)  |
| 리빌드 중 리부팅   | 가능 — 재부팅 후 리빌드 자동 재개          |
| 리빌드 중 2차 장애 | RAID 5: 데이터 유실, RAID 6: 1대 추가 허용 |
| 리빌드 우선순위    | CC/초기화보다 우선 실행                    |

#### 서버 간 디스크 이관

- SSD를 물리적으로 다른 서버로 이동 가능합니다.
- 데이터 + SupremeRAID 메타데이터가 드라이브에 저장되어 있습니다.
- 대상 서버에 동일 버전 SupremeRAID 소프트웨어 + 유효 라이선스가 필요합니다.
- 드라이브 순서가 바뀌어도 정상 인식됩니다.

#### 알림 설정 (권장)

```bash
# SMTP 알림 설정 (이벤트 발생 시 이메일 발송)
graidctl set alert --smtp-server <smtp_host> --smtp-port 587 \
  --sender <sender@example.com> --recipient <admin@example.com>
```

- severity 필터로 Warning, Error, Info를 선택할 수 있습니다.
- PD/DG/VD 상태 변경 시 즉시 알림을 발송합니다.
- 일일 점검을 대체하지는 않지만 장애 초기 대응 시간을 단축합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. SSD 수명 관리

### 모니터링 항목

| SMART 필드           | 의미               | 교체 기준      |
|----------------------|--------------------|----------------|
| `percentage_used`    | 수명 소모율 (%)    | > 90%          |
| `available_spare`    | 예비 영역 잔여 (%) | < 10%          |
| `media_errors`       | 미디어 오류 횟수   | > 0 (모니터링) |
| `critical_warning`   | 치명적 경고 비트맵 | != 0           |
| `temperature`        | 현재 온도          | > 75°C         |
| `data_units_written` | 총 쓰기량          | TBW 80% 도달   |

### 쓰기량 계산 (TB)

```bash
nvme smart-log /dev/gpd<id> | grep "data_units_written"
# 값 × 512 × 1000 / 1024^4 = TB
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 장애 대응

### 9.1 PD 장애 (단일 디스크 실패)

```
증상: PD STATE = FAILED, DG STATE = DEGRADED
```

```bash
# 1. 상태 확인
graidctl list physical_drive
graidctl list drive_group

# 2. 장애 PD 식별
graidctl describe physical_drive <failed_pd_id>

# 3. 장애 PD 삭제
graidctl delete physical_drive <failed_pd_id>

# 4. 새 SSD 장착 후 인식 확인
graidctl list nvme_drive

# 5. 새 PD 생성
graidctl create physical_drive --nvme-drive <new_drive_path>

# 6. DG에 교체 (리빌드 자동 시작)
graidctl replace physical_drive <dg_id> <old_pd_id> <new_pd_id>

# 7. 리빌드 확인
graidctl list drive_group
graidctl list event
```

### 9.2 컨트롤러 장애 (GPU 실패)

#### 듀얼 컨트롤러 구성

- active/active 구성에서 Primary GPU 장애 시, 모든 SSD가 Secondary GPU로 자동 인수(failover)됩니다.
- 수동 설정 불필요 — SupremeRAID가 자동으로 최적 컨트롤러를 선택합니다.

> 출처 (FAQ): "If the primary SupremeRAID™ controller fails, all SSDs will seamlessly be managed by the remaining operational SupremeRAID™ controller."

#### 단일 컨트롤러 구성 — GPU 교체 절차

공식 문서 "Replacing a SupremeRAID™ Card" 섹션 기준입니다.

```bash
# 1. 서버 전원 OFF

# 2. 장애 GPU 물리 제거, 새 GPU 장착

# 3. 서버 부팅 후 새 라이선스 키 적용
graidctl apply license <NEW_LICENSE_KEY>

# 4. RAID 상태 확인
graidctl list controller
graidctl list drive_group
# 기대: DG STATE = OPTIMAL (메타데이터가 SSD에 있으므로 자동 인식)
```

🟡 GPU 교체 전 반드시 교체용 라이선스 키를 확보해야 합니다. 라이선스는 GPU 시리얼 넘버에 종속됩니다.

> 출처 (FAQ): "Before doing this, please ensure you have the replacement license key to hand as each SupremeRAID™ GPU requires a unique license key."

### 9.3 에스컬레이션 기준

| 상태               | 긴급도 | 조치 시한      |
|--------------------|--------|----------------|
| PD FAILED          | 높음   | 24시간 내 교체 |
| DG DEGRADED        | 높음   | 24시간 내 교체 |
| CC ERROR           | 중간   | 72시간 내 조사 |
| Temperature > 80°C | 높음   | 즉시 확인      |
| Controller OFFLINE | 긴급   | 즉시 대응      |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 드라이버 업데이트 절차

```bash
# 1. CC 실행 중이면 완료 대기
graidctl describe consistency_check

# 2. 현재 구성 백업
graidctl list controller > /tmp/graid_backup.txt
graidctl list drive_group >> /tmp/graid_backup.txt
graidctl list physical_drive >> /tmp/graid_backup.txt
graidctl list virtual_drive >> /tmp/graid_backup.txt

# 3. 서비스 정지 (가능하면)

# 4. 드라이버 설치 (공식 문서 참조)

# 5. 서비스 재시작 / 리부팅

# 6. 상태 확인
graidctl version
graidctl list controller
graidctl list drive_group
```

🟡 커널 업데이트와 GRAID 드라이버 업데이트는 동시에 하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 11. 점검 체크리스트

### 일일 (2분)

- [ ] `graidctl list controller` → ONLINE
- [ ] `graidctl list drive_group` → 전체 OPTIMAL
- [ ] `graidctl list virtual_drive` → 전체 OPTIMAL
- [ ] `graidctl list physical_drive` → 전체 ONLINE
- [ ] `graidctl list event` → 새 에러/경고 없음

### 주간 (5분)

- [ ] NVMe SMART temperature < 70°C
- [ ] NVMe percentage_used 추이 기록
- [ ] GPU 온도 정상 범위
- [ ] 디스크 사용량 (df) 확인

### 월간 (20분+)

- [ ] Consistency Check 전체 DG 실행
- [ ] CC 결과 확인 (에러 없음)
- [ ] SMART 상세 로그 수집
- [ ] 커널 업데이트 보류 건 확인
- [ ] 라이선스 상태 확인

### 분기 (30분)

- [ ] SSD percentage_used 추이 → 수명 예측
- [ ] 성능 기준선 측정 (fio read-only)
- [ ] 드라이버 릴리즈 노트 확인
- [ ] OS/커널 지원 목록 변경 확인
- [ ] 장애 대응 절차 리뷰

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- GRAID SupremeRAID Documentation: [docs.graidtech.com/sr/](https://docs.graidtech.com/sr/) — ★★★☆☆
- GRAID SupremeRAID FAQ: [graidtech.com/faq/](https://www.graidtech.com/faq/) — ★★☆☆☆
- [_reference/graid_supremeraid_official_notes.md](../../_reference/graid_supremeraid_official_notes.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-10

**마지막 업데이트**: 2026-07-14

© 2026 siasia86. Licensed under CC BY 4.0.

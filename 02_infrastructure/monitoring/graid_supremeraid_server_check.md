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

- 일반 서버에서는 NVMe SSD가 OS에 직접 `/dev/nvme0n1`으로 노출됩니다.
- SupremeRAID 환경에서는 NVMe SSD가 PD로 전환되면 일반 네임스페이스(`/dev/nvmeXn1`)에서 해제되어 OS에 블록 디바이스로 노출되지 않습니다.
- SupremeRAID GPU가 SSD를 점유하고 I/O를 관리합니다.
- 물리적으로 분리된 SSD는 `/dev/gpdX` 경로로만 접근합니다.

#### GPU Card (하드웨어 RAID 엔진)

- GPU의 수천 개 CUDA 코어가 패리티 계산(RAID 5/6) 또는 미러링(RAID 1/10)을 수행합니다.
- CPU는 RAID 연산에서 완전히 해방됩니다 — 애플리케이션에 CPU 100% 사용 가능합니다.
- GPU가 죽어도 **데이터는 SSD에 보존**됩니다 (메타데이터가 SSD에 저장)

#### graid.ko (커널 모듈)

- Linux 커널에 로드되는 드라이버 모듈입니다.
- GPU와 NVMe SSD 사이의 I/O 경로를 관리합니다.
- OS가 Virtual Drive(`/dev/gdgXnY`)를 일반 블록 디바이스로 인식할 수 있게 합니다.
- 커널 버전에 종속 — 지원되지 않는 커널에서는 로드 실패합니다.

#### graidctl / graid_server (사용자 공간)

- `graid_server`: 백그라운드 데몬. GPU와 통신하며 RAID 상태를 관리합니다.
- `graidctl`: CLI 관리 도구. 사용자가 RAID를 생성/조회/삭제/교체하는 인터페이스입니다.
- `graid-mgr` (1.6+): GUI/API 관리 인터페이스입니다.

#### Linux / Windows OS (최상위)

- OS는 Virtual Drive(`/dev/gdgXnY`)만 인식합니다.
- OS에서 일반 블록 디바이스와 동일하게 `mkfs`, `mount`, `fio`를 사용할 수 있습니다.
- 물리 NVMe SSD(`/dev/nvmeXn1`)는 OS에서 보이지 않습니다.

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
│  NVMe SSD 0, 1, 2 ...  │  data + parity distributed across SSDs        
└─────────────────────────┘                                              
```

### RAID 논리 구성 요소

| 구성 요소      | 약칭 | 디바이스 경로 | 설명                                 |
|----------------|------|---------------|--------------------------------------|
| Physical Drive | PD   | `/dev/gpdX`   | OS에서 분리된 NVMe SSD               |
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
- **OS와 SSD가 분리** — OS는 물리 SSD를 볼 수 없고 VD만 인식합니다.
- **데이터는 SSD에 저장** — GPU 장애 시에도 데이터는 SSD에 보존됩니다 (GPU 교체 후 복구 가능)
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

| 주기 | 점검 항목                                       | 소요 시간 |
|------|-------------------------------------------------|-----------|
| 일일 | 상태 확인, 이벤트 로그                          | 2분       |
| 주간 | SMART 요약, GPU 온도, 디스크 사용량             | 5분       |
| 월간 | Consistency Check, SMART 상세, 펌웨어 확인      | 20분+     |
| 분기 | 드라이버/커널 호환 확인, 수명 예측, 성능 기준선 | 30분      |

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

| 컴포넌트   | 정상 상태 | 비정상 시 조치         |
|------------|-----------|------------------------|
| Controller | ONLINE    | 즉시 에스컬레이션      |
| DG         | OPTIMAL   | DEGRADED → 디스크 교체 |
| VD         | OPTIMAL   | DEGRADED → DG 확인     |
| PD         | ONLINE    | FAILED → 교체 절차     |

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

🟡 SupremeRAID GPU는 항상 100% utilization 표시 — 정상입니다 (polling mechanism).

[⬆ 목차로 돌아가기](#목차)

---

## 5. 월간 점검

### 5.1 Consistency Check 실행

```bash
# 각 DG에 대해 실행
graidctl start consistency_check <dg_id>

# 진행 상태 확인
graidctl describe consistency_check
```

🟡 예상 속도: ~10 GB/sec. 10TB DG ≈ 17분.

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

수명 예측 공식:

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

### 동작 원리

```
┌─────────────────────────────────────────────────────────┐ 
│               Consistency Check Process                  │
├─────────────────────────────────────────────────────────┤ 
│  1. Read data strips from all PDs in DG                 │ 
│  2. Recalculate parity from data strips                 │ 
│  3. Compare calculated parity vs stored parity          │ 
│  4. If mismatch:                                        │ 
│     - auto_fix: overwrite stored parity (recommended)   │ 
│     - stop_on_error: halt and report                    │ 
│  5. Continue until all strips checked                   │ 
└─────────────────────────────────────────────────────────┘ 
```

### Policy 옵션

| Policy        | 동작                         | 사용 시나리오           |
|---------------|------------------------------|-------------------------|
| auto_fix      | 불일치 발견 시 자동으로 복구 | 일반 운영 환경 (권장)   |
| stop_on_error | 불일치 발견 시 중지 후 보고  | 원인 분석이 필요한 경우 |

### 권장 설정

| 항목         | 권장 값        |
|--------------|----------------|
| Schedule     | 월 1회         |
| Policy       | auto_fix       |
| Excluded DGs | [] (전체 포함) |

### CC 설정 변경

```bash
# 현재 CC 설정 확인
graidctl describe consistency_check

# 정책 변경
graidctl set consistency_check --policy auto_fix

# 스케줄 활성화 (옵션은 --help로 확인)
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

- CC 실행 중 드라이버 업데이트/리부팅 금지 — 완료 대기 후 진행합니다.
- CC는 백그라운드로 실행되며 I/O 성능에 미미한 영향을 줍니다.
- RAID 0 DG에서는 CC를 시작할 수 없습니다 (패리티 없음)
- CC 중 PD 장애 발생 시 CC는 자동 중단되고 리빌드가 우선 실행됩니다.
- `FIXED` 결과가 반복 발생하면 해당 PD의 SMART를 확인하고 교체를 검토합니다.

🟡 CC에서 `FIXED`가 한 번 나오는 것은 정상적인 비트 부패 복구입니다. 동일 PD에서 반복 발생 시 드라이브 열화를 의심합니다.

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

1. 듀얼 컨트롤러 구성: auto_failover로 자동 인수
2. 단일 컨트롤러: 재부팅 → GPU 교체 (새 라이선스 키 필요)
3. 데이터는 SSD에 보존됨

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

**마지막 업데이트**: 2026-07-10

© 2026 siasia86. Licensed under CC BY 4.0.

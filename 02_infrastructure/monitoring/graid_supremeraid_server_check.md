# GRAID SupremeRAID 서버 점검 가이드

SupremeRAID (GPU 기반 NVMe RAID) 환경의 정기 점검 절차를 정리합니다. 서버/구성에 관계없이 적용 가능한 범용 가이드입니다.

## 목차

| 섹션                                                                                                                         |
|------------------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 점검 주기](#2-점검-주기) / [3. 일일 점검](#3-일일-점검)                                             |
| [4. 주간 점검](#4-주간-점검) / [5. 월간 점검](#5-월간-점검) / [6. 분기 점검](#6-분기-점검)                                   |
| [7. Consistency Check 운영](#7-consistency-check-운영) / [8. SSD 수명 관리](#8-ssd-수명-관리) / [9. 장애 대응](#9-장애-대응) |
| [10. 드라이버 업데이트 절차](#10-드라이버-업데이트-절차) / [11. 점검 체크리스트](#11-점검-체크리스트)                        |

---

## 1. 개요

### SupremeRAID 아키텍처

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

### RAID 논리 구성 요소

| 구성 요소      | 약칭 | 디바이스 경로 | 설명                       |
|----------------|------|---------------|----------------------------|
| Physical Drive | PD   | `/dev/gpdX`   | OS에서 분리된 NVMe SSD     |
| Drive Group    | DG   | -             | RAID 레벨이 적용된 PD 그룹 |
| Virtual Drive  | VD   | `/dev/gdgXnY` | OS에 노출되는 볼륨         |
| Controller     | CX   | -             | GPU RAID 컨트롤러          |

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

### 권장 설정

| 항목         | 권장 값        |
|--------------|----------------|
| Schedule     | 월 1회         |
| Policy       | auto_fix       |
| Excluded DGs | [] (전체 포함) |

### CC 설정 변경

```bash
# 정책 변경
graidctl set consistency_check --policy auto_fix

# 스케줄 활성화 (옵션은 --help로 확인)
graidctl set consistency_check --help
```

### CC 수동 실행

```bash
graidctl start consistency_check <dg_id>
graidctl describe consistency_check
graidctl stop consistency_check <dg_id>   # 필요 시
```

### CC 결과 해석

| 결과      | 의미                     | 조치               |
|-----------|--------------------------|--------------------|
| COMPLETED | 정상 완료, 에러 없음     | 없음               |
| FIXED     | 불일치 발견 후 자동 복구 | 이벤트 로그 확인   |
| ERROR     | 복구 불가 불일치         | 드라이브 상태 확인 |

🟡 RAID 0에서는 CC 미지원 (패리티 없음).

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

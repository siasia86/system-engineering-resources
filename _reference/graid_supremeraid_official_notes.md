---
name: graid-supremeraid-official-notes
description: GRAID Technology SupremeRAID 공식 문서 요약. GPU 기반 NVMe RAID 아키텍처, CLI 명령어, 점검 항목.
tags:
  - graid
  - supremeraid
  - nvme
  - raid
  - storage
last_checked: 2026-07-10
sources:
  - https://docs.graidtech.com/sr/
  - https://docs.graidtech.com/sr/user-guide/linux/2.0.0/
  - https://www.graidtech.com/faq/
---

# GRAID SupremeRAID 공식 문서 참조 노트

## 버전 정보

| 항목                | 값                                  |
|---------------------|-------------------------------------|
| 최신 Linux 드라이버 | 2.0.0 Update 93 (2026 기준)         |
| 최신 Windows        | 1.2.5 Update 85                     |
| User Guide          | Linux 2.0.0 Rev.001 (2026-04-27)    |
| 사용자 버전 (예시)  | 1.5.0-706 (graidctl + graid_server) |
| 문서 사이트         | https://docs.graidtech.com/sr/      |

## 제품 라인업

| 모델명      | 현재 명칭         | 비고                    |
|-------------|-------------------|-------------------------|
| SR-1010     | SupremeRAID Ultra | 최상위 모델             |
| SR-1000     | SupremeRAID Pro   | 범용 엔터프라이즈       |
| SR-1001     | SupremeRAID Core  | 엔트리                  |
| SR-CORE-AM  | SupremeRAID Core  | AM 폼팩터               |
| SR-PRO-AM   | SupremeRAID Pro   | AM 폼팩터               |
| SR-ULTRA-AD | SupremeRAID Ultra | AD 폼팩터               |
| -           | SupremeRAID SE    | 소프트웨어 에디션 (OEM) |
| -           | SupremeRAID AE    | AI Edition              |
| -           | SupremeRAID HE    | HPC Edition (HA 강화)   |

## 소프트웨어 구성 요소

| 컴포넌트       | 역할                           |
|----------------|--------------------------------|
| `graidctl`     | CLI 관리 도구                  |
| `graid_server` | 관리 데몬 (graidctl 요청 처리) |
| `graid.ko`     | 커널 드라이버 모듈             |
| `graid_core`   | GPU 관리 인스턴스              |
| `graid-mgr`    | GUI/API 관리 데몬 (1.6+)       |

## RAID 논리 구성 요소

| 구성 요소      | 약칭 | 설명                                            |
|----------------|------|-------------------------------------------------|
| Physical Drive | PD   | OS에서 분리된 NVMe SSD (/dev/gpdX)              |
| Drive Group    | DG   | RAID 레벨이 적용된 PD 그룹                      |
| Virtual Drive  | VD   | OS에 노출되는 볼륨 (/dev/gdgXnY)                |
| Controller     | CX   | GPU RAID 컨트롤러 (하드웨어 정보, 온도, 팬속도) |

### 구성 흐름

```
NVMe SSD → (graidctl create physical_drive)
         → Physical Drive (PD, /dev/gpdX)
         → (graidctl create drive_group, RAID 레벨 지정)
         → Drive Group (DG)
         → (graidctl create virtual_drive)
         → Virtual Drive (VD, /dev/gdgXnY) → mkfs/mount
```

## 지원 사양

| 항목                   | 값                                       |
|------------------------|------------------------------------------|
| 지원 RAID 레벨         | 0, 1, 5, 6, 10                           |
| 최대 Physical Drive 수 | 32                                       |
| 최대 Drive Group 수    | 8                                        |
| 최대 Virtual Drive 수  | 1,023 / Drive Group                      |
| Strip size (RAID 0/10) | 4K, 8K, 16K, 32K, 64K, 128K              |
| Dual Controller (HA)   | 지원 (Linux, dual-active/active-passive) |
| NVMe-oF                | 지원 (Local RAID + Remote RAID Volume)   |
| SAS/SATA               | 지원 (scsi_drive)                        |

### RAID 레벨별 최소 드라이브

| RAID | 최소 드라이브 | 패리티/미러     |
|------|---------------|-----------------|
| 0    | 1             | 없음            |
| 1    | 2             | 미러링          |
| 5    | 3             | 단일 패리티     |
| 6    | 4             | 이중 패리티     |
| 10   | 2             | 미러+스트라이프 |

## 디바이스 경로 변경 이력

| 버전   | VD 디바이스 경로 |
|--------|------------------|
| ~1.2.x | `/dev/gvdXn1`    |
| 1.5.x  | `/dev/gdgXnY`    |
| 1.6+   | `/dev/gdgXnY`    |

## graidctl CLI 구조 (v1.5 기준)

### list 서브커맨드

| 명령어                         | 설명                        |
|--------------------------------|-----------------------------|
| `graidctl list controller`     | 컨트롤러 목록               |
| `graidctl list physical_drive` | Physical Drive 목록         |
| `graidctl list drive_group`    | Drive Group 목록            |
| `graidctl list virtual_drive`  | Virtual Drive 목록          |
| `graidctl list nvme_drive`     | NVMe 드라이브 목록 (미할당) |
| `graidctl list scsi_drive`     | SAS/SATA 드라이브 목록      |
| `graidctl list event`          | 이벤트 로그                 |
| `graidctl list nvmeof_target`  | NVMe-oF 타겟 목록           |
| `graidctl list remote_target`  | 원격 NVMe-oF 타겟 목록      |

### 주요 관리 명령어

| 명령어                                | 설명                         |
|---------------------------------------|------------------------------|
| `graidctl version`                    | 버전 확인                    |
| `graidctl show controller <id>`       | 컨트롤러 상세 (온도, 팬, SN) |
| `graidctl show physical_drive <id>`   | PD 상세 (모델, SMART)        |
| `graidctl show drive_group <id>`      | DG 상세 (RAID 레벨, 상태)    |
| `graidctl show virtual_drive <id>`    | VD 상세 (크기, 상태)         |
| `graidctl create physical_drive`      | PD 생성                      |
| `graidctl create drive_group`         | DG 생성                      |
| `graidctl create virtual_drive`       | VD 생성                      |
| `graidctl delete physical_drive <id>` | PD 삭제 (SSD OS로 반환)      |
| `graidctl delete drive_group <id>`    | DG 삭제                      |
| `graidctl delete virtual_drive <id>`  | VD 삭제                      |
| `graidctl apply license <KEY>`        | 라이선스 적용                |

### describe 서브커맨드

| 명령어                                      | 설명                     |
|---------------------------------------------|--------------------------|
| `graidctl describe drive_group <id>`        | DG 상세 (RAID, 상태, PD) |
| `graidctl describe physical_drive <id>`     | PD 상세 (모델, SMART)    |
| `graidctl describe virtual_drive <dg> <vd>` | VD 상세 (크기, 상태)     |
| `graidctl describe consistency_check`       | CC 설정 및 상태          |
| `graidctl describe license`                 | 라이선스 정보            |
| `graidctl describe config led`              | LED 설정 정보            |
| `graidctl describe nvmeof_target <id>`      | NVMe-oF 타겟 상세        |

### 점검/유지보수 명령어

| 명령어                                         | 설명                   |
|------------------------------------------------|------------------------|
| `graidctl check consistency <dg_id>`           | Consistency Check 시작 |
| `graidctl show consistency_check_task <dg_id>` | CC 진행 상태 확인      |
| `nvme smart-log /dev/gpdX`                     | PD의 NVMe SMART 로그   |
| `graidctl list event`                          | 에러/경고 이벤트 확인  |

## Consistency Check (정합성 검사)

| 항목        | 내용                            |
|-------------|---------------------------------|
| 권장 주기   | 월 1회 (공식 FAQ)               |
| 예상 속도   | ~10 GB/sec (드라이브 성능 의존) |
| 예시        | 10TB DG → 약 17분               |
| 옵션        | auto fix (권장) / stop on error |
| RAID 0      | CC 미지원 (패리티 없음)         |
| 동작 중 I/O | 가능 (백그라운드)               |

## 초기화 (Initialization)

| 종류            | 조건                            | 동작              |
|-----------------|---------------------------------|-------------------|
| Fast Init       | SSD가 deallocate 지원 시 (기본) | 즉시 최적 상태    |
| Background Init | 그 외                           | 백그라운드 동기화 |

## GPU 관련 참고

- SupremeRAID GPU는 항상 100% utilization 표시 (polling mechanism, 정상)
- GPU 온도/팬속도는 `graidctl show controller` 로 확인
- `nvidia-smi`로도 확인 가능하나, 일반 GPU 워크로드와 공유 불가

## 고가용성 (HA)

- Dual Controller 지원 (Linux만)
- dual-active / active-passive 모드
- 자동 failover: Primary 장애 시 Secondary가 DG 인수
- Root Complex 무관 (같은/다른 RC에서도 동작)
- GPU 교체 시 새 라이선스 키 필요

## OS/커널 업데이트 주의사항

- 커널/OS 업데이트 전 반드시 공식 지원 목록 확인
- 미지원 커널 사용 시 데이터 접근 불가 위험
- 롤백 또는 베타 드라이버 필요할 수 있음
- 공식 지원 목록: https://docs.graidtech.com/

## 알림 설정

- SMTP 통합으로 이메일 알림 지원
- 필터 가능: severity (Warning, Error, Info)
- PD/DG/VD 상태 변경 알림 가능
- Linux/Windows 모두 지원

## 드라이버 업그레이드 경로

| 현재 버전 | 대상 버전       | 경로                                    |
|-----------|-----------------|-----------------------------------------|
| 1.x       | 2.0.0 Update 93 | 1.x → 1.7.2 Update 67 → 2.0.0 Update 93 |
| 1.7.2+    | 2.0.0 Update 93 | 1.7.2 Update 67+ → 2.0.0 Update 93      |

- 1.x에서 2.0.0으로 직접 업그레이드 불가
- 반드시 1.7.2 Update 67을 경유해야 함
- 업그레이드 중 DG/VD가 일시적으로 TRANSFORMING 상태 진입 가능 → OPTIMAL 복귀 확인 후 진행

## 라이선스

| 버전   | 라이선스 | 비고                         |
|--------|----------|------------------------------|
| 1.x    | V1       | 기존 라이선스                |
| 2.0.0+ | V2       | 업그레이드 전 사전 확보 필수 |

- 2.0.0부터 V2 라이선스 필요
- V1 → V2 전환은 영업 담당자 통해 발급
- 라이선스는 GPU 시리얼 넘버에 종속

## 디스크 이관 (서버 간 이동)

- SSD를 물리적으로 다른 서버로 이동 가능
- 데이터 + SupremeRAID 설정이 드라이브에 저장됨
- 대상 서버에 SupremeRAID 소프트웨어 + 라이선스 필요
- 부팅 후 즉시 사용 가능

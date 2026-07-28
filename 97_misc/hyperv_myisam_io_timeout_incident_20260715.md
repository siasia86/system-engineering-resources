# Hyper-V MyISAM I/O Timeout 장애 분석 (2026-07-15)

CentOS 5.11 게임 DB 서버에서 동시 발생한 SCSI timeout → EXT4 read-only → MyISAM 테이블 파손 장애를 분석합니다.

## 장애 상황 요약

| 항목                   | 내용                                                                                 |
|------------------------|--------------------------------------------------------------------------------------|
| 장애 일시              | 2026-07-15 (화) 16:38:24 KST                                                         |
| I/O 포화 시작          | 16:36:20경 (StorageVSP 최초 경고: 16:36:32)                                          |
| 장애 지속              | 약 2시간 (16:38 ~ 18:31 수동 reboot)                                                 |
| 호스트                 | Windows Server 2022 (Build 20348), Hyper-V, Vmbus 3.0                                |
| 스토리지               | 외장 스토리지 (CSV: ClusterStorage\Volume1, Volume2)                                 |
| 전체 VM 수             | 12대+ (CentOS 5.11 x 6, Windows x ?, Debian x ?, RedHat x ?)                         |
| 장애 VM                | CentOS 5.11 전체 6대 (DBA 증언 + 3대 로그 확인)                                      |
| 비 CentOS VM           | Windows/Debian/RedHat — 동일 지연 겪었으나 장애 없음                                 |
| MySQL 버전             | 4.0.27 / 4.1.24 (2008년 EOL)                                                         |
| 엔진                   | MyISAM (트랜잭션 미지원, crash recovery 없음)                                        |
| 피해                   | MyISAM 테이블 파손 — GalaxyDB 12개, AcheronDB 10개, HermesDB 2개, CassiopeaDB 미확인 |
| **트리거 (확정)**      | MV-Live VM의 `_backup.vhdx` 대량 READ 작업 (주기적 I/O 작업)                         |
| **근본 원인**          | CSV 전체 I/O 대역폭 포화 (최대 latency 116초)                                        |
| **CentOS만 장애 이유** | storvsc (LIS 4.1.3-2) 구버전: 60초 timeout 후 즉시 abort, retry 없음                 |

### DBA 증언 vs 로그 증거

| 구분        | DBA 증언  | 로그 증거                                     |
|-------------|-----------|-----------------------------------------------|
| CassiopeaDB | 장애 발생 | ✅ kernel: timing out command, waited 60s     |
| HermesDB    | 장애 발생 | ✅ kernel: timing out command, waited 60s     |
| GalaxyDB    | 장애 발생 | ✅ kernel: timing out command, waited 60s     |
| AcheronDB   | 장애 발생 | ✅ slow log: REPAIR TABLE t_inven00~09 (10건) |
| TestDB      | 장애 발생 | 🟡 messages.1 유실 (장애 시점 로그 없음)      |
| 6번째 VM    | 장애 발생 | ❌ 로그 미수집                                |

## 목차

| 섹션                                                                                                                                                         |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 장애 환경](#1-장애-환경) / [2. 트리거 확정](#2-트리거-확정) / [3. 장애 타임라인](#3-장애-타임라인)                                                       |
| [4. CentOS만 장애 발생한 이유](#4-centos만-장애-발생한-이유) / [5. MyISAM 파손 메커니즘](#5-myisam-파손-메커니즘) / [6. MySQL 로그 분석](#6-mysql-로그-분석) |
| [7. 피해 증폭 요인](#7-피해-증폭-요인) / [8. 재발 방지 조치](#8-재발-방지-조치) / [9. 호스트 확인 명령어](#9-호스트-확인-명령어)                             |
| [10. LIS 드라이버 검증](#10-lis-드라이버-검증-2026-07-28) / [11. 참고 자료](#11-참고-자료)                                                                   |

---

## 1. 장애 환경

### 호스트/스토리지

| 항목        | 값                                              |
|-------------|-------------------------------------------------|
| 호스트 OS   | Windows Server 2022 (Build 20348-10.0-2-0.2461) |
| Vmbus       | version 3.0                                     |
| 스토리지    | 외장 스토리지 (3.6.0.0, Build 2145637)          |
| CSV Volume  | LH (DB/Game), ND, MV  등                        |
| Storage QoS | 미설정 (VM 간 I/O 격리 없음)                    |

### 게스트 (CentOS 5.11 DB 서버)

| 항목            | 값                                              |
|-----------------|-------------------------------------------------|
| 게스트 OS       | CentOS 5.11 i386 PAE (kernel 2.6.18-419.el5PAE) |
| LIS             | 4.1.3-2 (hv_storvsc)                            |
| 디스크 드라이버 | storvsc (synthetic SCSI, 큐 깊이 64+)           |
| CPU             | Intel Xeon Gold 6444Y (8 vCPU)                  |
| RAM             | 16GB (15616MB HIGHMEM + 896MB LOWMEM)           |
| 파일시스템      | sda: EXT3 (LVM, OS) / sdb, sdc: EXT4 (데이터)   |
| SCSI timeout    | 60초 (기본 30초에서 변경된 상태)                |
| VHD 경로        | C:\ClusterStorage\Volume1\Masang\VHD\LH\Live\   |

### 영향 받은 VM

| VM          | 장애     | SCSI timeout 로그                   | MyISAM 파손 |
|-------------|----------|-------------------------------------|-------------|
| CassiopeaDB | ✅       | sd 1:0:0:0, sd 1:0:0:1 (waited 60s) | 미확인      |
| HermesDB    | ✅       | sd 1:0:0:0, sd 1:0:0:1 (waited 60s) | 2개         |
| GalaxyDB    | ✅       | sd 1:0:0:0, sd 1:0:0:1 (waited 60s) | 12개        |
| AcheronDB   | ✅ (DBA) | 로그 유실                           | 미확인      |
| TestDB      | ✅ (DBA) | 로그 유실                           | 미확인      |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 트리거 확정

### StorageVSP 이벤트 로그 분석

호스트 `Microsoft-Windows-Hyper-V-StorageVSP-Admin` 로그에서 352건의 I/O 경고를 확인했습니다.

### 트리거: MV-Live VM의 주기적 대량 READ 작업

| 항목           | 확인 내용                                                    |
|----------------|--------------------------------------------------------------|
| 최초 지연 발생 | 16:36:32 — `MV-Live] Main1 Frankfurt Srv_backup.vhdx` (12초) |
| 대상 파일      | `*_backup.vhdx` 다수 (Main1, Main2, Virginia, Auth 등)       |
| 연산 코드      | `READ SUB CHANNEL` — 읽기 작업                               |
| 결과 상태      | `SRB_STATUS_SUCCESS` — 결국 완료됨 (abort 아님)              |
| 영향 범위      | Volume1 + Volume2 전체 (모든 VM 영향)                        |
| 최대 latency   | **116초** (MV-Live Tool Srv_var_local.vhdx)                  |

### 주기적 패턴 (매주 발생)

| 날짜                | 시각               | 건수      | 최대 latency | CentOS 장애    |
|---------------------|--------------------|-----------|--------------|----------------|
| 2026-07-06 (일)     | 오전 12~1시        | 247건     | ~14초        | ❌ (60초 미만) |
| 2026-07-13 (일)     | 오전 12~1시        | 271건     | ~14초        | ❌ (60초 미만) |
| **2026-07-15 (화)** | **오후 4:36~4:38** | **352건** | **116초**    | ✅ (60초 초과) |

- 매주 일요일 새벽: 동일 작업이 실행되나 latency 14초 수준 → 장애 없음
- 7/15 오후: **동일 작업이 업무 시간에 실행** + I/O 부하 중첩 → latency 116초 → 장애

### 트리거 출처 (추정)

| 후보                          | 가능성 | 근거                                           |
|-------------------------------|--------|------------------------------------------------|
| Hyper-V Replica (전체 동기화) | ★★★★☆  | 주기적 + `_backup.vhdx` READ + 스케줄러에 없음 |
| 스토리지 스냅샷/복제          | ★★★☆☆  | 외장 스토리지에서 볼륨 레벨 복제               |
| 서비스 기반 VHD 백업          | ★★★☆☆  | Windows 서비스로 등록된 백업 에이전트          |
| 수동 복사                     | ★☆☆☆☆  | 매주 반복 + 새벽 실행 → 수동 가능성 낮음       |

🟡 호스트에서 `Get-VMReplication` 또는 `Get-Service | Where {$_.DisplayName -match 'backup|replica'}` 로 확인 필요.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 장애 타임라인

### StorageVSP + 게스트 로그 통합

```
16:36:20  ★ MV-Live _backup.vhdx 대량 READ 시작 (트리거)
16:36:32  StorageVSP 최초 경고 (12초 지연)
         │
16:36:43  23초 → 16:36:52 32초 → 16:37:00 40초 (점점 악화)
         │
16:37:03  Volume2 전체 43초 지연 (MV-Live/QA 모든 VHD)
16:37:24  ★ CentOS storvsc 60초 timeout 도달 (16:36:24에 시작된 I/O)
         │
16:37:45  Volume1 (LH-DB) 전파:
         │   LH-DB-Hermes-MDF: 72초
         │   LH-DB-Galaxy-MDF: 80초
         │   LH-DB-Cassiopea-MDF: 82초
         │   LH-DB-Acheron-MDF: 81초
         │
16:38:16  최대 latency 116초 (MV-Live Tool Srv_var_local)
16:38:24  ★ CentOS kernel "timing out command, waited 60s"
16:38:25  EXT4 journal abort → sdb, sdc read-only
         │   → MyISAM 테이블 쓰기 중단 → 데이터 파손
         │
         │  (약 2시간 read-only 상태로 방치)
         │
18:31:32  수동 reboot
18:32:18  부팅 — "mounting fs with errors, running e2fsck is recommended"
         │   → e2fsck 미실행, 그대로 마운트
         │
18:37~20:47  DBA CHECK TABLE / REPAIR TABLE 수행
```

### 게스트 로그 증적 (CassiopeaDB)

```
Jul 15 16:38:24 CassiopeaDB kernel: sd 1:0:0:1: timing out command, waited 60s
Jul 15 16:38:24 CassiopeaDB kernel: sd 1:0:0:0: timing out command, waited 60s
Jul 15 16:38:25 CassiopeaDB kernel: Aborting journal on device sdc-8.
Jul 15 16:38:25 CassiopeaDB kernel: Aborting journal on device sdb-8.
Jul 15 16:38:25 CassiopeaDB kernel: EXT4-fs error (device sdb): ext4_journal_start_sb: Detected aborted journal
Jul 15 16:38:25 CassiopeaDB kernel: EXT4-fs (sdb): Remounting filesystem read-only
Jul 15 16:38:25 CassiopeaDB kernel: EXT4-fs (sdb): ext4_da_writepages: jbd2_start: 1024 pages, ino 524313; err -30
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. CentOS만 장애 발생한 이유

모든 VM이 **동일한 I/O 지연** (60~116초)을 겪었으나, CentOS 5.11만 장애가 발생했습니다.

### storvsc 드라이버 버전 차이

| 항목              | CentOS 5.11 (장애)                            | Windows/최신 Linux (무사)                  |
|-------------------|-----------------------------------------------|--------------------------------------------|
| 드라이버          | LIS 4.1.3-2 storvsc (2017년, kernel 2.6.18용) | in-kernel storvsc (최신) 또는 Windows 내장 |
| I/O timeout 후    | 60초 → **즉시 command abort**                 | timeout → **retry/reconnect 시도**         |
| 에러 복구         | abort만 (단순)                                | retry → reset → abort (단계적)             |
| VMBus 채널 재연결 | 미지원                                        | 지원                                       |
| 결과              | EXT4 journal abort → read-only                | I/O 지연만 발생, 정상 완료                 |

### 호스트 StorageVSP 로그가 증명

```
모든 VHD: "상태 = SRB_STATUS_SUCCESS"
→ 호스트 측에서는 모든 I/O가 (느리지만) 성공적으로 완료됨
→ 최신 드라이버는 이 "느린 성공"을 기다렸고, CentOS는 60초에 포기함
```

### 분기 흐름

```
CSV 전체 I/O 포화 (latency 60~116초)
         │
         ├── CentOS 5.11 (LIS 4.1.3-2 storvsc)
         │     1. SCSI command 전송 → 60초 무응답
         │     2. timeout → 즉시 abort (retry 없음)
         │     3. 커널: "timing out command, waited 60s"
         │     4. EXT4 journal abort → read-only
         │     5. MyISAM 테이블 파손
         │
         └── Windows / 최신 Linux (최신 storvsc)
               1. SCSI command 전송 → 60초 무응답
               2. timeout → retry (VMBus 채널 통해 재전송)
               3. 호스트에서 (느리지만) 완료: SRB_STATUS_SUCCESS
               4. 일시적 지연만 발생, 파일시스템 정상
```

### I/O 요청 시퀀스 (실제 동작)

```
VM (CentOS)                         호스트 (Hyper-V)                 스토리지
     │                                    │                              │
     │  ① SCSI WRITE 요청 전송            │                              │
     │  (MySQL이 MyISAM에 write)          │                              │
     ├─────────────────────────────────>  │                              │
     │                                    │  ② 물리 I/O 요청 전달        │
     │                                    ├────────────────────────────> │
     │                                    │                              │
     │  storvsc: "응답 대기 중..."        │ 스토리지: "다른 I/O 처리 중" │
     │  10초... 20초... 30초...           │  (MV-Live backup READ 폭주)  │
     │  40초... 50초... 60초...           │                              │
     │                                    │                              │
     │  ★ 60초 도달 → TIMEOUT!            │                              │
     │  "이 요청은 실패한 것으로 간주"    │                              │
     │  → abort → journal fail            │                              │
     │                                    │                              │
     │                                    │  ③ (82초 후) 드디어 완료!    │
     │                                    │ <─────────────────────────── │
     │                                    │                              │
     │  ④ 호스트가 "성공" 응답 전달       │                              │
     │ <─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─     │                              │
     │  ★ 이미 abort 처리 완료            │                              │
     │    → 이 응답은 무시됨              │                              │
```

- 호스트 StorageVSP 로그: "82초 걸렸지만 SRB_STATUS_SUCCESS" (경고만 기록)
- CentOS 커널 로그: "timing out command, waited 60s" (abort 처리)
- 결과: 호스트는 성공으로 봤지만, CentOS는 60초에 이미 포기한 상태

### /sys/block/sdX/device/timeout 이란

Linux 커널이 SCSI 디스크에 보낸 I/O 요청의 **최대 대기 시간(초)**입니다.

```bash
# 확인
cat /sys/block/sda/device/timeout
60
```

| 항목       | 설명                                                        |
|------------|-------------------------------------------------------------|
| 파일 위치  | `/sys/block/sdX/device/timeout` (디스크별 개별 설정)        |
| 기본값     | 30초 (Linux 커널 기본)                                      |
| 이 환경 값 | 60초 (누군가 변경한 상태)                                   |
| 단위       | 초 (seconds)                                                |
| 동작       | I/O 요청 전송 후 이 시간 내에 완료 응답이 없으면 abort 처리 |
| 영향 범위  | 해당 블록 디바이스(sda, sdb, sdc 등)에 대한 모든 I/O        |
| 재부팅 시  | 기본값으로 초기화됨 (영구 적용은 rc.local 등에 설정 필요)   |

#### timeout 동작 흐름

```
애플리케이션 (MySQL)
     │ write() 호출
     v
파일시스템 (EXT4)
     │ bio 생성
     v
SCSI 스택 (storvsc)
     │ SCSI command 전송 + 타이머 시작 (60초)
     v
VMBus → 호스트 → 스토리지
     │
     ├── 60초 이내 완료 → 정상 처리 (타이머 취소)
     └── 60초 초과       → timeout 만료 → scsi_abort_command()
                                │
                                v
                         I/O 에러 반환 → EXT4 journal abort
```

#### 값에 따른 동작 차이

| timeout 값  | 이번 장애 시 결과 (max latency 116초)              |
|-------------|----------------------------------------------------|
| 30초        | 🔴 abort (기본값이었으면 더 빨리 장애 발생)        |
| 60초 (현재) | 🔴 abort — 82초 걸린 I/O도 실패 처리               |
| 120초       | 🟡 116초 이내 모두 완료 → **장애 미발생** (지연만) |
| 180초       | ✅ 여유 있게 통과                                  |
| 0 (무한)    | ❌ 설정 불가 — 진짜 디스크 고장 시 영원히 hang     |

🟡 timeout 증가는 "파손 vs 서비스 멈춤" 중 **멈춤을 선택**하는 것입니다. 게임 DB에서는 테이블 파손(복구 수십 분~수 시간)보다 일시적 멈춤이 낫습니다.

#### 60초 vs 120초 vs 180초 비교

| 항목                  | 60초 (현재)         | 120초 (권장)                 | 180초                |
|-----------------------|---------------------|------------------------------|----------------------|
| 이번 장애 방지        | ❌ 불가             | ✅ 가능 (max 116초 < 120초)  | ✅ 가능 (여유 있음)  |
| 서비스 최대 중단      | 60초                | 120초                        | 180초                |
| 게임 클라이언트       | 60초 무응답 → 끊김  | 120초 무응답 → 끊김          | 180초 무응답 → 끊김  |
| DB 커넥션 풀 점유     | 60초간 블로킹       | 120초간 블로킹               | 180초간 블로킹       |
| 진짜 디스크 고장 감지 | 60초 후 즉시        | 120초 후                     | 180초 후 (대응 지연) |
| 모니터링 알람 지연    | 낮음                | 중간                         | 높음                 |
| 일시적 I/O 포화 복구  | ❌ 대부분 abort     | ✅ 대부분 복구               | ✅ 거의 모두 복구    |
| MyISAM 파손 위험      | 🔴 높음             | 🟡 낮음                      | ✅ 매우 낮음         |
| 적합 환경             | 빠른 장애 감지 필요 | **게임 DB (일시 포화 대응)** | 배치/백업 서버       |

#### 권장: 120초

- 이번 장애 최대 latency (116초)를 커버하면서 과도하지 않은 값입니다
- 120초 이상 hang이면 일시적 I/O 포화가 아닌 실제 장애 가능성이 높아 abort가 적절합니다
- 게임 서비스 관점: 120초 무응답은 이미 유저 접속 끊김 발생 → 그 이상 기다리는 것은 의미 없음

[⬆ 목차로 돌아가기](#목차)

---

## 5. MyISAM 파손 메커니즘

### I/O timeout → 테이블 손상 경로

```
storvsc 60초 timeout → command abort
         │
         v
EXT4 journal abort (jbd2_start err -30 = EROFS)
         │
         v
Filesystem read-only 전환
         │
         v
MyISAM write 중단:
  - .MYD (data) 파일 write 중 중단 → 행 데이터 불완전
  - .MYI (index) 파일 업데이트 중 중단 → 인덱스 트리 손상
  - 저널/WAL 없음 → 자동 복구 불가
         │
         v
테이블 깨짐 (REPAIR TABLE 필요)
```

### MyISAM vs InnoDB

| 항목            | MyISAM         | InnoDB                 |
|-----------------|----------------|------------------------|
| 트랜잭션        | ❌ 미지원      | ✅ 지원                |
| 크래시 복구     | ❌ 수동 REPAIR | ✅ 자동 crash recovery |
| WAL             | ❌ 없음        | ✅ redo log            |
| Doublewrite     | ❌ 없음        | ✅ partial write 보호  |
| 이 장애 시 결과 | 🔴 테이블 파손 | 🟡 자동 복구 가능      |

[⬆ 목차로 돌아가기](#목차)

---

## 6. MySQL 로그 분석

### MySQL 환경

| VM          | MySQL 버전 | 바이너리 경로                    | DB 이름               |
|-------------|------------|----------------------------------|-----------------------|
| CassiopeaDB | 4.1.24-log | /masang_mdf/mysql/libexec/mysqld | lh_game_svr_cassiopea |
| HermesDB    | 4.0.27-log | /masang_mdf/mysql/libexec/mysqld | lh_game_svr_hermes    |
| GalaxyDB    | 4.0.27-log | /masang_mdf/mysql/libexec/mysqld | lh_game_svr_galaxy    |
| AcheronDB   | 4.0.27-log | /masang_mdf/mysql/libexec/mysqld | (파손 여부 미확인)    |
| TestDB      | 4.0.27-log | /masang_mdf/mysql/libexec/mysqld | (파손 여부 미확인)    |

🔴 MySQL 4.0/4.1은 2008년에 EOL된 버전입니다.

### 파손된 테이블 (slow log 기반)

| VM          | REPAIR TABLE 실행 내역               | 시각               | 수량   |
|-------------|--------------------------------------|--------------------|--------|
| GalaxyDB    | t_inven00~09, t_characters, t_pets   | 260715 20:21~20:47 | 12     |
| AcheronDB   | t_inven00~09                         | 260715 20:57~21:06 | 10     |
| HermesDB    | t_inven03, t_stash07                 | 260715 20:07~20:08 | 2      |
| TestDB      | CHECK TABLE만 실행 (REPAIR 없음)     | 260715 20:10       | 0      |
| CassiopeaDB | (slow log에 260715 기록 없음 — 유실) | —                  | 미확인 |

- **AcheronDB**: messages.1은 유실되었으나, **slow log에서 REPAIR TABLE 10건 확인** → 장애 및 파손 확정
- **TestDB**: CHECK TABLE만 수행, REPAIR 미실행 → 파손 없거나 경미
- **CassiopeaDB**: MySQL이 crash 상태에서 slow log 기록 불가 + rotation으로 유실

### mysql-error.log 유실 원인

- filesystem read-only 전환 시점에 MySQL이 에러 로그 기록 불가
- mysqld 프로세스가 hung 상태로 남아있다가 수동 reboot으로 종료
- 복구 과정에서 log rotation 발생하여 장애 시점 로그 유실

[⬆ 목차로 돌아가기](#목차)

---

## 7. 피해 증폭 요인

### maximal mount count 초과 (e2fsck 미실행)

5대 전체 VM에서 Jul 2부터 매 부팅마다 경고:

```
EXT4-fs (sdb): warning: maximal mount count reached, running e2fsck is recommended
EXT4-fs (sdc): warning: maximal mount count reached, running e2fsck is recommended
```

e2fsck를 실행하지 않고 계속 마운트하여 운영 → 잠재 메타데이터 손상 누적 가능.

### 증폭 요인 종합

| 요소                             | 역할                                      |
|----------------------------------|-------------------------------------------|
| MV-Live 대량 READ (트리거)       | CSV I/O 포화 유발                         |
| Storage QoS 미설정               | VM 간 I/O 격리 없음 — noisy neighbor 방치 |
| storvsc 구버전 (LIS 4.1.3-2)     | 60초 timeout 후 즉시 abort, retry 없음    |
| e2fsck 미실행 (mount count 초과) | 파일시스템 잠재 손상 누적                 |
| MyISAM 엔진                      | crash recovery 없음, write 중단 시 파손   |
| MySQL 4.0/4.1 (EOL)              | InnoDB 제한적, 보안 취약                  |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 재발 방지 조치

### 즉시 조치 (긴급)

| 순위 | 조치                                                        | 효과  |
|------|-------------------------------------------------------------|-------|
| 1    | **MV-Live 주기적 I/O 작업 식별 및 시간/대역폭 제한**        | ★★★★★ |
| 2    | `e2fsck -f /dev/sdb` + `e2fsck -f /dev/sdc` 실행 (6대 전체) | ★★★★★ |
| 3    | CentOS SCSI timeout 120초 이상으로 증가                     | ★★★☆☆ |

### 단기 조치

| 순위 | 조치                                           | 효과  |
|------|------------------------------------------------|-------|
| 4    | **Storage QoS 활성화** — DB VM에 min IOPS 보장 | ★★★★☆ |
| 5    | DB VHD를 별도 CSV 볼륨/LUN으로 분리            | ★★★★★ |
| 6    | MyISAM 테이블 REPAIR + 정합성 검증             | ★★★★☆ |

### 중장기 조치

| 순위 | 조치                                                 | 효과  |
|------|------------------------------------------------------|-------|
| 7    | MyISAM → InnoDB 전환 (crash-safe)                    | ★★★★☆ |
| 8    | CentOS 5.11 → 지원 OS 업그레이드 (in-kernel storvsc) | ★★★★★ |
| 9    | MySQL 4.0/4.1 → 5.7+ 업그레이드                      | ★★★★☆ |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 호스트 확인 명령어

### 트리거 특정 (미완료)

```powershell
# Hyper-V Replica 확인
Get-VMReplication | Select VMName, State, FrequencySec, PrimaryServer, ReplicaServer

# 백업 관련 서비스
Get-Service | Where-Object {$_.DisplayName -match 'backup|replica|sync|copy'}

# Windows Server Backup 스케줄
wbadmin get schedule

# _backup.vhdx 파일 수정 시각 (복사 완료 시각 확인)
Get-ChildItem "C:\ClusterStorage\Volume2\Masang\VHD\MV\Live\" -Recurse -Filter "*backup*" | Select Name, @{N='GB';E={[math]::Round($_.Length/1GB,1)}}, LastWriteTime
```

### DB VM VHD 배치 확인

```powershell
Get-VM | Where-Object {$_.Name -match 'LH.*DB|Cassiopea|Hermes|Galaxy|Acheron|Test'} |
Get-VMHardDiskDrive | Select VMName, ControllerNumber, ControllerLocation, Path
```

### Storage QoS 설정

```powershell
# DB VM 보호 정책
New-StorageQoSPolicy -Name "GameDB-Floor" -MinimumIops 500 -MaximumIops 5000 -PolicyType Dedicated
$gp = Get-StorageQoSPolicy -Name "GameDB-Floor"
Get-VM "*DB*" | Get-VMHardDiskDrive | Set-VMHardDiskDrive -QoSPolicyID $gp.PolicyId
```

### 게스트 SCSI timeout 증가

```bash
# 현재 값 확인
cat /sys/block/sdb/device/timeout
cat /sys/block/sdc/device/timeout

# 120초로 변경 (임시)
echo 120 > /sys/block/sdb/device/timeout
echo 120 > /sys/block/sdc/device/timeout

# 영구 적용
echo 'echo 120 > /sys/block/sdb/device/timeout' >> /etc/rc.local
echo 'echo 120 > /sys/block/sdc/device/timeout' >> /etc/rc.local
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. LIS 드라이버 검증 (2026-07-28)

장애 서버에서 직접 확인한 LIS 설치 상태 및 분석입니다.

### 설치된 패키지

```
[root@gamedb-srv01 ~]# rpm -qa | grep -i "microsoft\|hyper\|kmod"
kmod-microsoft-hyper-v-PAE-4.1.3.2-20170307
microsoft-hyper-v-4.1.3.2-20170307
microsoft-hyper-v-debuginfo-4.1.3.2-20170307
```

| 패키지                        | 역할                              | 빌드 날짜  |
|-------------------------------|-----------------------------------|------------|
| `kmod-microsoft-hyper-v-PAE`  | 커널 모듈 (PAE 커널용 storvsc 등) | 2017-03-07 |
| `microsoft-hyper-v`           | 유저스페이스 데몬 (KVP, VSS 등)   | 2017-03-07 |
| `microsoft-hyper-v-debuginfo` | 디버그 심볼                       | 2017-03-07 |

### 로드된 커널 모듈

```
[root@gamedb-srv01 ~]# lsmod | grep -i hv_
hv_netvsc              31232  0
hv_balloon             17952  0 [permanent]
hv_utils               20988  1
hv_storvsc             20884  6
hv_vmbus               39608  7 hv_netvsc,hv_balloon,hyperv_fb,hv_utils,hyperv_keyboard,hid_hyperv,hv_storvsc
```

| 모듈         | 사용 카운트 | 역할                         |
|--------------|-------------|------------------------------|
| `hv_vmbus`   | 7           | Hyper-V 통신 버스 (최상위)   |
| `hv_storvsc` | 6           | SCSI 디스크 드라이버 (6 LUN) |
| `hv_netvsc`  | 0           | 네트워크 드라이버            |
| `hv_balloon` | 0 (perm)    | Dynamic Memory               |
| `hv_utils`   | 1           | KVP, Shutdown, TimeSync IC   |

### 분석: storvsc 에러 처리 경로 비교

LIS 4.1.3-2의 `hv_storvsc`와 최신 커널(5.x+)의 `hv_storvsc`의 에러 처리 차이입니다.

#### LIS 4.1.3-2 (CentOS 5.11, 장애 서버)

```
SCSI command 전송
     │
     v  (응답 대기)
60초 경과 (timeout)
     │
     v
scsi_times_out()
     │
     v
storvsc_command_done() → status = DID_ABORT
     │
     v  (상위 계층 통보)
sd: command abort
     │
     v
EXT4: I/O error → journal abort → remount read-only
     │
     v
MyISAM: write 중단 → MYI/MYD 불일치 → 테이블 파손
```

- retry 로직 없음 (abort 즉시)
- VMBus 채널 재연결 미지원
- SCSI error handler (eh_host_reset_handler) 미구현

#### 최신 커널 in-kernel storvsc (5.x+)

```
SCSI command 전송
     │
     v  (응답 대기)
timeout 경과
     │
     v
scsi_times_out() → BLK_EH_RESET_TIMER (retry)
     │
     ├── 1차: command retry (재전송)
     │         │
     │         v  성공 → 정상 완료
     │
     ├── 2차: storvsc_host_reset_handler() (VMBus 채널 리셋)
     │         │
     │         v  성공 → 정상 완료
     │
     └── 3차: abort (최종 실패)
              │
              v
         I/O error (여기서야 상위 통보)
```

- 단계적 복구: retry → channel reset → abort
- VMBus 채널 재연결 지원 (storvsc_host_reset_handler)
- timeout 기본값 180초 (vs LIS 4.x의 60초)

### 분석: 동일 장애 상황 시뮬레이션

2026-07-15 장애 당시 CSV latency 최대 116초를 기준으로 비교합니다.

| 시나리오                  | LIS 4.1.3-2 (장애 서버)     | 최신 storvsc (5.x+)          |
|---------------------------|-----------------------------|------------------------------|
| latency 50초              | ✅ 정상 (timeout 60초 미만) | ✅ 정상                      |
| latency 65초              | ❌ abort → read-only        | ✅ 정상 (timeout 180초 미만) |
| latency 116초 (최대 관측) | ❌ abort → read-only        | ✅ 정상 (180초 미만)         |
| latency 185초 (가정)      | ❌ abort → read-only        | 🟡 1차 retry 후 성공 가능    |
| latency 300초+ (가정)     | ❌ abort → read-only        | ❌ 3차 abort → read-only     |

🟡 timeout을 120초로 변경하면 116초 latency에서 생존하지만, retry 로직이 없으므로 120초를 1초라도 초과하면 즉시 abort됩니다.

### 분석: LIS 버전 히스토리와 EOL

| LIS 버전 | 릴리스     | 지원 커널                   | CentOS 5 지원 |
|----------|------------|-----------------------------|---------------|
| 3.5      | 2014       | 2.6.18~2.6.32               | ✅            |
| 4.0      | 2015       | 2.6.32~3.x                  | ✅            |
| 4.1.3-2  | 2017-03-07 | 2.6.18 (PAE), 2.6.32        | ✅ (마지막)   |
| 4.2      | 2017       | 3.10+ (RHEL 7 전용)         | ❌            |
| 4.3      | 2019       | 3.10+ (RHEL 7 전용)         | ❌            |
| —        | 2019+      | in-kernel (별도 LIS 불필요) | ❌            |

- LIS 4.1.3-2가 **CentOS 5용 마지막 릴리스**입니다
- 이후 LIS는 RHEL 7+(커널 3.10+) 전용으로 전환되었습니다
- 2019년 이후 RHEL 7+/8+는 커널 내장 `hv_*` 드라이버를 사용하며 별도 LIS 설치가 불필요합니다
- Microsoft Download Center의 LIS 다운로드 페이지는 **폐쇄**되었습니다

### 분석: 패키지 구조 해부

```
microsoft-hyper-v-4.1.3.2-20170307 (메타 패키지)
├── /usr/sbin/hv_kvp_daemon          KVP (Key-Value Pair) 데몬
├── /usr/sbin/hv_vss_daemon          VSS (Volume Shadow Copy) 데몬
├── /usr/sbin/hv_fcopy_daemon        File Copy 데몬
└── /etc/init.d/hv_kvp_daemon        SysV init 스크립트

kmod-microsoft-hyper-v-PAE-4.1.3.2-20170307 (커널 모듈)
├── /lib/modules/2.6.18-419.el5PAE/extra/microsoft-hyper-v/
│   ├── hv_vmbus.ko                  VMBus 통신 (최상위)
│   ├── hv_storvsc.ko                SCSI 스토리지
│   ├── hv_netvsc.ko                 네트워크
│   ├── hv_utils.ko                  KVP/Shutdown/TimeSync IC
│   ├── hv_balloon.ko                Dynamic Memory
│   ├── hyperv_fb.ko                 프레임버퍼 (비디오)
│   └── hid_hyperv.ko                HID 입력 장치
└── /etc/depmod.d/hyperv.conf        모듈 의존성
```

🟡 모듈은 `/lib/modules/.../extra/` 에 위치합니다. 커널 내장 모듈(`/lib/modules/.../kernel/`)이 아닌 외부 설치 모듈입니다.

### 확인 명령어 모음

```bash
# ── LIS 패키지 확인 ──
rpm -qa | grep -i "microsoft\|hyper\|kmod"
rpm -ql microsoft-hyper-v | head -20
rpm -ql kmod-microsoft-hyper-v-PAE | head -20

# ── 커널 모듈 상태 ──
lsmod | grep -i "hv_\|vmbus\|hyperv"
modinfo hv_storvsc
modinfo hv_vmbus

# ── storvsc 디스크 매핑 ──
ls -la /sys/block/sd*/device/driver
cat /sys/block/sd*/device/model
cat /sys/block/sd*/device/vendor

# ── SCSI timeout 현재 값 ──
for d in /sys/block/sd?/device/timeout; do
    echo "$(basename $(dirname $(dirname $d))): $(cat $d)초"
done

# ── storvsc 큐 깊이 ──
cat /sys/block/sd*/device/queue_depth

# ── VMBus 채널 상태 ──
ls /sys/bus/vmbus/devices/ 2>/dev/null
cat /proc/interrupts | grep -i hyperv

# ── LIS 데몬 동작 확인 ──
ps aux | grep hv_
service hv_kvp_daemon status 2>/dev/null

# ── 커널 링 버퍼에서 Hyper-V 관련 메시지 ──
dmesg | grep -i "hyper\|vmbus\|storvsc\|netvsc"
```

### 확정 결론

| 항목               | 확인 결과                                                         |
|--------------------|-------------------------------------------------------------------|
| LIS 버전           | **4.1.3-2** (2017-03-07 빌드) — CentOS 5용 마지막 릴리스          |
| storvsc 동작       | `hv_storvsc` 로드 + 6개 디바이스 → SCSI 큐 사용 중                |
| timeout 기본값     | 60초 (장애 로그 "waited 60s"와 일치)                              |
| retry 로직         | **없음** — abort only (단계적 복구 미지원)                        |
| 최신 커널과 차이   | retry → channel reset → abort 3단계 vs abort only                 |
| 업데이트 가능성    | ❌ LIS EOL + Download Center 폐쇄 + 커널 2.6.18 제약              |
| timeout 120초 완화 | 116초 latency에서 생존 가능, 그러나 retry 없어 초과 시 즉시 abort |
| 근본 해결          | OS 마이그레이션 (x86_64 + 최신 커널) → in-kernel storvsc 확보     |

[⬆ 목차로 돌아가기](#목차)

---

## 11. 참고 자료

### 호스트/Hyper-V

- Storage QoS Overview: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/storage/storage-qos/storage-qos-overview) — ★★★☆☆
- Hyper-V StorageVSP Event ID 9: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/best-practices-analyzer/virtual-hard-disks-with-paging-files-should-be-excluded-from-replication) — ★★☆☆☆
- Hyper-V Supported Linux VMs: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/Supported-CentOS-and-Red-Hat-Enterprise-Linux-virtual-machines-on-Hyper-V) — ★★★☆☆
- Hyper-V Scalability Limits: [learn.microsoft.com](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/plan/plan-hyper-v-scalability-in-windows-server) — ★★★☆☆
- Windows Server Lifecycle: [learn.microsoft.com](https://learn.microsoft.com/en-us/lifecycle/products/windows-server-2022) — ★★★☆☆

### Linux/storvsc

- Linux SCSI timeout: [kernel.org](https://www.kernel.org/doc/html/latest/scsi/scsi_mid_low_api.html) — ★★☆☆☆
- storvsc 소스코드 (최신): [github.com/torvalds/linux](https://github.com/torvalds/linux/blob/master/drivers/scsi/storvsc_drv.c) — ★★★☆☆
- LIS 4.x Release Notes: [github.com/LIS](https://github.com/LIS/lis-next/releases) — ★★☆☆☆
- EXT4 error handling: [kernel.org](https://www.kernel.org/doc/html/latest/filesystems/ext4/) — ★★★☆☆

### MySQL/MyISAM

- MySQL 4.0 Reference Manual: [dev.mysql.com](https://dev.mysql.com/doc/refman/4.1/en/) — ★★☆☆☆
- MyISAM Repair: [dev.mysql.com](https://dev.mysql.com/doc/refman/5.7/en/myisam-repair.html) — ★★☆☆☆
- InnoDB Crash Recovery: [dev.mysql.com](https://dev.mysql.com/doc/refman/8.0/en/innodb-recovery.html) — ★★★☆☆

### 내부 문서

- [97_misc/hyperv_io_contention_legacy_vm.md](hyperv_io_contention_legacy_vm.md)
- [97_misc/centos5_gamedb_hyperv_host_compatibility.md](centos5_gamedb_hyperv_host_compatibility.md)
- [_reference/hyperv_version_comparison_notes.md](../_reference/hyperv_version_comparison_notes.md)

[⬆ 목차로 돌아가기](#목차)

---

**작성일**: 2026-07-20

**마지막 업데이트**: 2026-07-28

© 2026 siasia86. Licensed under CC BY 4.0.

# S3 Backup Script 엣지 케이스 정리

## 목차

| 섹션                                                               |
|--------------------------------------------------------------------|
| [1. 중복 실행 방지](#1-중복-실행-방지)                             |
| [2. 파일 필터링](#2-파일-필터링)                                   |
| [3. 날짜 추출](#3-날짜-추출)                                       |
| [4. 파일명 생성 (make_group_name)](#4-파일명-생성-make_group_name) |
| [5. 하위 디렉토리 동일 파일명](#5-하위-디렉토리-동일-파일명)       |
| [6. S3 업로드](#6-s3-업로드)                                       |
| [7. 압축 검증](#7-압축-검증)                                       |
| [8. 로컬 정리 (cleanup)](#8-로컬-정리-cleanup)                     |
| [9. CPU 과부하 보호](#9-cpu-과부하-보호)                           |
| [10. 디스크 여유 공간](#10-디스크-여유-공간)                       |
| [11. 프로세스 잠금 체크](#11-프로세스-잠금-체크)                   |
| [12. get_server_ip](#12-get_server_ip)                             |
| [13. 에러 코드 (backup.status)](#13-에러-코드-backupstatus)        |

---


`01_aojp_s3_file_upload.py` (VERSION: 26.04.03)

[⬆ 목차로 돌아가기](#목차)

---

## 1. 중복 실행 방지

| 상황                           | 동작                                    |
|--------------------------------|-----------------------------------------|
| lock 파일 없음                 | 정상 실행                               |
| lock 파일 있음 + PID 살아있음  | `already running (PID xxxx)` → 종료     |
| lock 파일 있음 + PID 죽음      | `stale lock removed` → lock 삭제 → 실행 |
| lock 파일 있음 + PID 읽기 실패 | lock 삭제 → 실행                        |
| 정상 종료 / 에러 종료          | `finally`에서 lock 삭제                 |
| CPU skip으로 return            | `finally`에서 lock 삭제                 |

🟡 PID 재사용으로 인한 오판 가능성 있으나 확률 매우 낮음

[⬆ 목차로 돌아가기](#목차)

---

## 2. 파일 필터링

### FILE_PATTERNS 매칭

```python
FILE_PATTERNS = ['*game_log_*.log', '*gamelog_*.log']
```

| 파일명                                           | 매칭 |
|--------------------------------------------------|------|
| `ao_game_log_2025-10-14_17-01-02_IMChatting.log` | ✅   |
| `LogGameLog_20230327_111323.log`                 | ✅   |
| `system.log`                                     | ❌   |
| `readme.txt`                                     | ❌   |

### FILE_EXTENSIONS 빈 값

```python
FILE_EXTENSIONS = []  # → 모든 파일 False → 압축 대상 0건 → 정상 종료
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 날짜 추출

### extract_date

| 파일명                                           | 추출 결과                 |
|--------------------------------------------------|---------------------------|
| `ao_game_log_2025-10-14_17-01-02_IMChatting.log` | `20251014`                |
| `LogGameLog_20230327_111323.log`                 | `20230327`                |
| `no_date_file.log`                               | `None` (skip)             |
| `log_2025-01-01_to_2025-12-31.log`               | `20250101` (첫 번째 매칭) |

🟡 YYYY-MM-DD 패턴을 우선 매칭. 없으면 YYYYMMDD 8자리 매칭

### extract_year_from_filename

| 파일명                                     | 년도                 |
|--------------------------------------------|----------------------|
| `ao_game_log_20250923_12files.tar.zst`     | `2025`               |
| `ao_game_log_2026-04-01.tar.zst`           | `2026`               |
| `ao_game_log_20260401_12files.tar.zst.~1~` | `2026`               |
| `unknown.tar.zst`                          | 현재 년도 (fallback) |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 파일명 생성 (make_group_name)

### prefix 추출

| 원본 파일명                                    | prefix           | 출력                                   |
|------------------------------------------------|------------------|----------------------------------------|
| `ao_game_log_2025-09-23_15-42-38_IMSystem.log` | `ao_game_log`    | `ao_game_log_20250923.tar.zst`         |
| `LogGameLog_20230327_111323.log`               | `LogGameLog`     | `LogGameLog_20230327.tar.zst`          |
| `20260401_backup.log`                          | `log` (fallback) | `log_20260401.tar.zst`                 |
| 같은 날짜 12개 파일                            | `ao_game_log`    | `ao_game_log_20260401_12files.tar.zst` |

🟡 prefix는 첫 번째 파일 기준. 같은 날짜에 다른 prefix 파일이 섞이면 첫 파일 기준 이름 생성

### Windows 경로 260자 제한

```
D:\Masang\Server\ao_log_compressed\ao_game_log_20260401_12files.tar.zst
→ 71자 ✅ (260자 미만)
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 하위 디렉토리 동일 파일명

```
LOG_DIR/
  ├── ChattingLog/ao_game_log_2025-01-01.log
  └── SystemLog/ao_game_log_2025-01-01.log
```

`arcname=os.path.relpath(fp, LOG_DIR)` 적용으로 tar 내 디렉토리 구조 보존:

```
tar 내부:
  ├── ChattingLog/ao_game_log_2025-01-01.log
  └── SystemLog/ao_game_log_2025-01-01.log
```

하위 경로가 여러 단계여도 정상 동작:

```
ChattingLog/Server01/2025/ao_game_log_2025-01-01.log
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. S3 업로드

### 멱등성

```
업로드 전: s3 ls로 파일명 + 사이즈 비교
동일하면 skip → 재실행해도 중복 업로드 없음
```

### 재시도

```
1회 시도 → 실패 → 5초 대기 → 2회 → 실패 → 5초 대기 → 3회 → 실패 → Exception
총 3회 (초기 1회 + 재시도 2회)
```

### 최초 실행 (S3 비어있음)

```
aws s3 ls → returncode != 0 + stdout/stderr 비어있음
→ INFO 로그 + 빈 dict {} 반환 (에러 아님)
```

### S3 키 구조

```
s3://BUCKET/PRODUCT_NAME/년도/IP-hostname/파일명
s3://02-masang-backup-ap-northeast-1/ao/2026/172.31.29.142-EC2AMAZ-REAGL1N/ao_game_log_20260401_12files.tar.zst
```

### hostname 공백 처리

```python
socket.gethostname().replace(" ", "_")
# "my server" → "my_server"
```

### s3 ls 파일명 공백 처리

```python
key = ' '.join(parts[3:])  # 공백 포함 파일명 복원
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 압축 검증

| 조건                                          | 동작               |
|-----------------------------------------------|--------------------|
| 압축 파일 존재 + 사이즈 > 0                   | 원본 삭제          |
| 압축 파일 존재 + 사이즈 == 0 + 원본도 0바이트 | 원본 삭제 (의도됨) |
| 압축 파일 미존재 또는 사이즈 0 (원본 > 0)     | 원본 유지 + 경고   |

### backup_path 중복 방지

```
같은 이름 존재 시: .~1~, .~2~, .~3~ ... 순번 증가
→ 기존 파일 덮어쓰기 없음
```

🟡 반복 실패 시 `.~N~` 파일이 누적되어 S3에 중복 업로드될 수 있음

[⬆ 목차로 돌아가기](#목차)

---

## 8. 로컬 정리 (cleanup)

| 조건                                | 동작             |
|-------------------------------------|------------------|
| S3에 동일 파일명 + 동일 사이즈 존재 | 로컬 삭제        |
| S3에 파일 없음                      | 로컬 유지 + 경고 |
| S3 사이즈 불일치                    | 로컬 유지 + 경고 |
| 로컬 파일 90일 미경과               | 삭제 대상 아님   |

90일 기준: 파일의 `mtime` (수정 시간 = 압축 생성 시점) 기준

[⬆ 목차로 돌아가기](#목차)

---

## 9. CPU 과부하 보호

```
CPU >= 80% → skip (카운트 증가)
3회 연속 skip → ERR_CPU_SKIP (7) 기록 → Zabbix 알림
CPU < 80% → 카운트 리셋 → 정상 실행
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. 디스크 여유 공간

```
WORK_DIR 디스크 여유 < 1GB → 압축 skip
업로드/정리는 실행 (디스크 확보 가능)
```

[⬆ 목차로 돌아가기](#목차)

---

## 11. 프로세스 잠금 체크

```
시작 시 1회 전체 프로세스 스캔 → locked 파일 set 생성
파일별 O(1) 조회 (파일마다 스캔하지 않음)
```

| 상황                     | 동작                                    |
|--------------------------|-----------------------------------------|
| 프로세스가 파일 사용 중  | `file locked by PID xxxx` → skip        |
| AccessDenied (권한 부족) | 해당 프로세스 skip → 다음 프로세스 계속 |
| 프로세스 종료됨          | NoSuchProcess → skip                    |

[⬆ 목차로 돌아가기](#목차)

---

## 12. get_server_ip

| 상황          | 반환값                      | 영향                           |
|---------------|-----------------------------|--------------------------------|
| 네트워크 정상 | 실제 IP (예: 172.31.29.142) | 정상                           |
| 네트워크 단절 | hostname                    | S3 키 변경 → cleanup 매칭 실패 |

`main()`에서 1회만 호출하여 `do_s3_upload`, `do_cleanup`에 전달 → 실행 중 불일치 방지

[⬆ 목차로 돌아가기](#목차)

---

## 13. 에러 코드 (backup.status)

```
+------+---------+----------------------------+
| 코드 | 상수    | 설명                       |
+------+---------+----------------------------+
| 0    | -       | 정상                       |
| 1    | COMPRESS| 압축 실패                  |
| 2    | VERIFY  | 압축 검증 실패             |
| 3    | S3_LS   | S3 목록 조회 실패          |
| 4    | S3_UPLOAD| S3 업로드 실패            |
| 5    | CLEANUP | 로컬 정리 실패             |
| 6    | UNEXPECTED| 예상치 못한 에러         |
| 7    | CPU_SKIP| CPU 과부하 3회 연속 skip   |
+------+---------+----------------------------+
```

여러 에러 발생 시 `min(error_codes)` → 가장 낮은 번호(가장 먼저 발생하는 단계)만 기록

---

## 참고 자료

- AWS S3 Documentation: [docs.aws.amazon.com](https://docs.aws.amazon.com/s3/) — ★★★☆☆
- AWS CLI S3 Reference: [AWS CLI S3](https://docs.aws.amazon.com/cli/latest/reference/s3/) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-04-03

**마지막 업데이트**: 2026-04-03

© 2026 siasia86. Licensed under CC BY 4.0.

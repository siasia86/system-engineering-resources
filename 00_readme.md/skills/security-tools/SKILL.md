# Security Masking Tools

## 1. 스크립트 목록

| 파일 | 용도 | 대상 |
|------|------|------|
| `/root/sj_del/ip_mask.py` | 공인 IP → RFC 5737 | 모든 텍스트 파일 |
| `/root/sj_del/json_mask.py` | AWS 리소스 18종 마스킹 | `.json` 파일 |
| `/root/sj_del/aws-security-check.sh` | AWS 민감 데이터 탐지 (9종) | 디렉토리 스캔 |
| `/root/sj_del/git-security-check.sh` | pre-commit 보안 검사 (5종) | Git staged 파일 |
| `/root/sj_del/md-style-check.sh` | 마크다운 스타일 검사 | `.md` 파일 |
| `/root/sj_del/security-check.conf` | bash 스크립트 공유 설정 | conf |

## 2. 공통 옵션 체계 (ip_mask.py / json_mask.py)

| 옵션 | 설명 |
|------|------|
| `-f` / `--file` | 단일 파일 지정 |
| `-D` / `--dir` | 디렉토리 재귀 처리 |
| `-r` / `--restore` | 원복 |
| `-d` / `--dry-run` | 파일 미변경, 미리보기 |
| `-v` / `--verbose` | 변경 라인 상세 출력 |
| `--all` | skip 파일 포함 전체 출력 (ip_mask.py) |
| `--force` | serial 불일치 무시 |
| `-V` / `--version` | 버전 출력 |
| `-i` / `--include` | 포함 확장자 필터 |
| `-e` / `--exclude` | 제외 확장자 필터 |
| `-q` / `--quiet` | 로그 최소화 |
| `-m` / `--map` | map 파일 경로 직접 지정 |
| `--debug` | 패턴 디버깅 (json_mask.py 전용) |

## 3. 설계 원칙

- map 파일 삭제 금지 (복원 시에도 유지)
- serial 검증: 파일 hash ↔ map `_meta.serial` 일치 확인
- atomic write: 임시 파일 → rename (중간 실패 시 원본 보존)
- 권한 보존: 원본 파일 퍼미션 유지
- 멱등성: 이미 마스킹된 파일 재실행 시 변경 없음
- `.bak.N` 백업: map 덮어쓰기 전 자동 백업
- SAFETY 라인: `ip_mask.py` 상단 `import sys; sys.exit(0)` 유지 (의도적 비활성)

## 4. 컬러 규칙

| 색상 | 용도 |
|------|------|
| 빨간색 | mask 파일명, masked 숫자 |
| 보라색 | restore 파일명, backup 경로 |
| 노란색 | skip/warning, 변경 전 IP |
| 초록색 | 변경 후 IP, restored 숫자 |
| 회색 | 라인 번호 (`L1`, `L2`) |

## 5. ip_mask.py 상세

- 공인 IP 자동 탐지 (사설/예제/특수 IP 제외)
- RFC 5737 순차 할당: `192.0.2.0/24` → `198.51.100.0/24` → `203.0.113.0/24` (최대 762개)
- 버전 번호 제외: IP 앞뒤에 `-` 또는 `_` 있으면 skip
- map 파일: `<원본파일>.map.ip.json`
- 제외: `SKIP_EXTS` (바이너리), `SKIP_FILES` (자기 자신 등), `SKIP_TARGETS` (특정 파일명)
- 제외 디렉토리: `.git`, `.ssh`, `.kiro`
- 파일명에 `.map.ip.json` 포함 시 무조건 제외

## 6. json_mask.py 상세

- 18종 패턴: ACCOUNT-ID, BUCKET, VPCE-ID, VPC-ID, SUBNET-ID, SG-ID, ENI-ID, INSTANCE-ID, ELB-NAME, RDS-EP, CF-DIST-ID, NAT-GW-ID, RTB-ID, IGW-ID, IP, DOMAIN
- 플레이스홀더 형식: `<TYPE-N>` (예: `<IP-1>`, `<ACCOUNT-ID-1>`)
- map 파일: `<원본파일>.map.json`
- `_meta` 블록: serial, source, version

## 7. 검증 절차

코드 변경 후 반드시:
1. `py_compile` 문법 검증
2. SAFETY 라인 임시 비활성 후 실행 테스트
3. mask → restore round-trip 확인
4. 기존 map 파일과의 호환성 확인

```bash
sudo python3 -c "import py_compile; py_compile.compile('/root/sj_del/ip_mask.py', doraise=True); print('OK')"
sudo python3 -c "import py_compile; py_compile.compile('/root/sj_del/json_mask.py', doraise=True); print('OK')"
```

## 8. aws-security-check.sh 상세

- 9종 검사: Access Keys, Secret Keys, Account IDs, ARNs, VPCE, Public IPs, Resource IDs, S3 Buckets, .map.json 추적
- `security-check.conf`에서 EXCLUDE_IPS, EXCLUDE_BUCKETS 동적 로드
- 버전 번호 패턴 제외 (IP 뒤 `-` 있으면 skip)
- `0x` hex 주소 제외
- `ami-` prefix 제외 (Resource IDs)
- conf 없으면 fallback 기본값 사용

## 9. git-security-check.sh 상세

- 5종 검사: Sensitive IPs, Passwords/Keys, AWS Account IDs, Large Files, Sensitive Filenames
- 모든 검사 통과 시 `✓` 출력
- `security-check.conf`에서 EXCLUDE_PASSWORDS, EXCLUDE_KEYWORDS 동적 필터링
- `0x` hex, `ULL` C 리터럴, 날짜 패턴 제외 (Account ID 오탐 방지)
- EXCLUDE_DIRS/EXCLUDE_FILES 기반 find 제외
- printf 방식 ANSI 컬러 (echo -e 호환 문제 회피)

## 10. bash 스크립트 공통 규칙

- 출력 형식: `[N/M] 검사명` + 결과 (`✓` / `✗` / `⚠`)
- `bash -n` 문법 검증 필수
- `security-check.conf` 공유 (source 방식 로드)
- `.kiro` 디렉토리 제외

## 11. 관련 설정 파일

- `/root/sj_del/security-check.conf` — EXCLUDE_IPS, EXCLUDE_PASSWORDS, EXCLUDE_KEYWORDS, EXCLUDE_BUCKETS, EXCLUDE_DIRS, EXCLUDE_FILES
- `/root/sj_del/ip_mask.toml` — 구버전 설정 (사용 안 함, 삭제 가능)

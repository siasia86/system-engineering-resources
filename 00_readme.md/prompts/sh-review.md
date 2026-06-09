---
description: Bash 스크립트 리뷰 — skill://bash-script-template 기준 검증
input:
  - name: target
    description: 리뷰 대상 .sh 파일 경로
    required: false
# ${1} 생략 시: 이 대화에서 가장 최근에 수정/생성/읽은 .sh 파일을 자동으로 대상으로 삼을 것.
# 최근 작업 파일이 불명확하면 "어떤 파일을 리뷰할까요?" 라고 물어볼 것.
---

# Bash Script Review

`skill://bash-script-template` 기준으로 아래 항목을 검증합니다.

## 검증 항목

### 구조
- [ ] shebang: `#!/bin/bash`
- [ ] 헤더 주석: `#### This script was created by sjyun on YYYY-MM-DD. version YY.MM.DD.`
- [ ] 복잡도 기준에 따른 구조 선택 (간단/보통/복잡)
- [ ] `main()` 함수 사용 (100줄 이상)
- [ ] `main "$@"` 호출 (마지막 줄)

### 로깅
- [ ] 간단: 인라인 `echo` + `|| exit`
- [ ] 보통 이상: `run_msg_info` / `log_msg_info` / `log_msg_error` 사용
- [ ] `LOG_FILE01` 정의 + `exec >>` 리다이렉션
- [ ] 에러 코드 순차 번호 (1, 2, 3...)

### 변수/함수
- [ ] 변수 섹션: `# ── 변수 ──...`
- [ ] `DATE=$(date +%Y%m%d_%H%M%S)` (백업 시)
- [ ] `backup_conf()` 사용 (설정 파일 수정 전)
- [ ] `service_start()` 사용 (서비스 재시작 시)
- [ ] `ensure_dir()` 사용 (디렉토리 생성 시)

### 에러 처리
- [ ] 주요 명령어에 `|| { log_msg_error N "msg" ; exit 1; }` 패턴
- [ ] `$?` 저장: `local` 선언 전에 캡처
- [ ] `eval` 사용 시 따옴표 감싸기 + 외부 입력값 전달 금지

### 보안
- [ ] 하드코딩된 패스워드 없음 (변수 또는 파일 참조)
- [ ] `rm -rf` 사용 시 변수 빈 값 가드: `${VAR:?}`
- [ ] `set -u` 또는 변수 미정의 가드: `${VAR:-default}`

### 엣지 케이스 / 테스트 관점

경계값 분석 (Boundary Value Analysis):
- [ ] 빈 입력 (인수 없음, 빈 파일, 빈 변수)
- [ ] 경로에 공백/특수문자 포함 (`"$var"` 따옴표 처리)
- [ ] 디스크 풀/권한 없음 상황에서의 동작

동등 분할 (Equivalence Partitioning):
- [ ] 파일: 존재 / 미존재 / 디렉토리 / 심볼릭 링크
- [ ] OS: Ubuntu / Rocky / Amazon Linux 분기 처리
- [ ] 서비스: 이미 실행 중 / 정지 / 미설치

상태 전이 (State Transition):
- [ ] 재실행 시 멱등성 (이미 설치된 패키지, 이미 존재하는 디렉토리)
- [ ] 스크립트 중간 실패 후 재실행 시 정상 복구

에러 경로:
- [ ] 모든 주요 명령에 `|| { error; exit; }` 존재
- [ ] 변수 미정의: `${VAR:?"error msg"}` 또는 `${VAR:-default}`
- [ ] 네트워크 실패 (apt/yum 다운로드) → 재시도 또는 명확한 에러
- [ ] 부분 실패 시 cleanup (trap EXIT)

파이프 / 글로빙 / 신호:
- [ ] `set -o pipefail` 설정 (파이프 중간 실패 감지)
- [ ] 파일 0개 매칭 시 `*.log` 리터럴 전달 방지 (`shopt -s nullglob` 또는 `find`)
- [ ] SIGTERM/SIGHUP 수신 시 cleanup (`trap cleanup SIGTERM SIGHUP`)
- [ ] 같은 스크립트 중복 실행 방지 (lock file: `flock` 또는 PID file)

## 출력 형식

```
✅ 통과 항목 (요약)
❌ 미충족 항목 + 수정 제안
🟡 권장 사항 (필수 아님)
```

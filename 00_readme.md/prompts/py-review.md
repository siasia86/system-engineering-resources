---
description: Python 스크립트 리뷰 — skill://python-script-template 기준 검증
input:
  - name: target
    description: 리뷰 대상 .py 파일 경로
    required: false
# ${1} 생략 시: 이 대화에서 가장 최근에 수정/생성/읽은 .py 파일을 자동으로 대상으로 삼을 것.
# 최근 작업 파일이 불명확하면 "어떤 파일을 리뷰할까요?" 라고 물어볼 것.
---

# Python Script Review

`skill://python-script-template` 기준으로 아래 항목을 검증합니다.

## 검증 항목

### 구조
- [ ] shebang: `#!/usr/bin/env python3`
- [ ] SAFETY comment: `#import sys; sys.exit(0)  # SAFETY: ...`
- [ ] module docstring (Usage 포함)
- [ ] VERSION = "YY.MM.DD"
- [ ] import: 한 줄씩, stdlib 알파벳순
- [ ] 섹션 구분 주석: `# ── section ──...`
- [ ] `if __name__ == '__main__': try/except KeyboardInterrupt`

### argparse
- [ ] `parse_args()` 별도 함수 분리
- [ ] `-V/--version` 존재
- [ ] `-d/--dry-run` 존재 (해당 시)
- [ ] `epilog` Examples 포함
- [ ] `formatter_class=RawDescriptionHelpFormatter`

### 로깅/출력
- [ ] 100줄 이상: `_setup_logger()` 사용
- [ ] 색상: `_c(text, color)` + tty 체크
- [ ] `log.error()` / `log.info()` 일관성

### 코드 품질
- [ ] 모든 함수 docstring (1줄 요약)
- [ ] `re.compile()` 모듈 레벨 (함수 내 금지)
- [ ] 함수 내 import 금지
- [ ] dry-run 경로에서 부작용 없음
- [ ] 파일 쓰기: `_atomic_write()` 사용 여부
- [ ] 멱등성: 재실행 시 동일 결과

### 보안
- [ ] 하드코딩된 패스워드/키 없음
- [ ] `subprocess.run(shell=True)` 사용 시 입력값 `shlex.quote()` 처리
- [ ] 임시 파일 생성 후 정리 (`finally` 블록)

### 엣지 케이스 / 테스트 관점

경계값 분석 (Boundary Value Analysis):
- [ ] 빈 입력 (파일 0바이트, 빈 리스트, 빈 문자열)
- [ ] 단일 요소 (파일 1줄, 리스트 1개)
- [ ] 최대 크기 입력 (매우 큰 파일, 긴 경로명)
- [ ] 경계값 ±1 (인덱스 0, -1, len-1, len)

동등 분할 (Equivalence Partitioning):
- [ ] 정상 입력 / 비정상 입력 / 경계 입력 분리 처리
- [ ] 파일: 존재 / 미존재 / 권한 없음 / 심볼릭 링크
- [ ] 경로: 절대 / 상대 / `~` / 공백 포함 / 한글 포함

상태 전이 (State Transition):
- [ ] dry-run → 실제 실행 전환 시 부작용 누수 없음
- [ ] 이미 처리된 파일 재처리 시 멱등성 유지

에러 경로:
- [ ] 파일 읽기 실패 → graceful error (traceback 노출 금지)
- [ ] 네트워크 타임아웃 → 적절한 에러 메시지 + 종료 코드
- [ ] 부분 실패 시 롤백 또는 상태 보고
- [ ] KeyboardInterrupt (Ctrl+C) 처리

동시성 / 플랫폼:
- [ ] 같은 파일을 두 프로세스가 동시 수정 시 안전 (lock 또는 atomic write)
- [ ] 인코딩: UTF-8 BOM, Latin-1, 바이너리 파일 입력 시 예외 처리
- [ ] 심볼릭 링크 순환 (디렉토리 재귀 탐색 시 `followlinks=False`)
- [ ] 경로 구분자 (`/` vs `\`), line ending (`\r\n` vs `\n`) 처리

## 출력 형식

```
✅ 통과 항목 (요약)
❌ 미충족 항목 + 수정 제안
🟡 권장 사항 (필수 아님)
```

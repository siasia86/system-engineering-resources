# 기본 Linux 명령어 및 스크립팅

Bash 스크립팅, 네트워크, 시스템 모니터링 등 기본적인 Linux 명령어와 도구 사용법을 정리한 문서입니다.

## 문서 목록

### Bash 스크립팅
- **[Bash 수학 연산](bash_math.md)** - Bash에서 산술 연산 수행 방법
- **[Bash trap 가이드](bash_trap_complete_guide.md)** - 시그널 처리 및 cleanup 패턴

### 시스템 모니터링
- **[리소스 모니터링](../04_system_engineer/resource_utilization_monitoring.md)** - CPU, 메모리, 디스크 사용량 확인

### 시스템 관리
- **[Root 패스워드 복구](root_password_recovery.md)** - root 비밀번호 분실 시 복구 방법

### 에디터
- **[Vim 사용법](vim.md)** - Vim 에디터 기본 및 고급 기능
- **[vim-airline](vim_airline.md)** - Vim 상태바 플러그인

---

## 추천 학습 순서

### 1단계: 기본 명령어
```bash
# 파일 및 디렉토리 조작
ls, cd, pwd, mkdir, rm, cp, mv

# 텍스트 처리
cat, grep, sed, awk, cut

# 시스템 정보
ps, top, df, du, free
```

### 2단계: Bash 스크립팅
1. [Bash 수학 연산](bash_math.md)
2. [Bash trap 가이드](bash_trap_complete_guide.md)

### 3단계: 네트워크 & 모니터링
3. [리소스 모니터링](../04_system_engineer/resource_utilization_monitoring.md)

### 4단계: 시스템 관리 & 에디터
1. [Root 패스워드 복구](root_password_recovery.md)
2. [Vim 사용법](vim.md)

---

## 빠른 참조

### 자주 사용하는 명령어

```bash
# 디스크 사용량 확인
df -h

# 메모리 사용량 확인
free -h

# 프로세스 확인
ps aux | grep process_name

# 네트워크 연결 확인
netstat -tuln
ss -tuln

# 로그 실시간 확인
tail -f /var/log/syslog
```

### Bash 스크립트 템플릿

```bash
#!/bin/bash
set -euo pipefail

# 변수 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 함수 정의
main() {
    echo "Hello World"
}

# 실행
main "$@"
```

---

[문서 전체 로드맵](../README.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-14

© 2026 siasia86. Licensed under CC BY 4.0.

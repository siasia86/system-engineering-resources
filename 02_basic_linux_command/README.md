# 기본 Linux 명령어 및 스크립팅

Bash 스크립팅, 네트워크, 시스템 모니터링 등 기본적인 Linux 명령어와 도구 사용법을 정리한 문서입니다.

## 문서 목록

### Bash 스크립팅
- **[Bash 수학 연산](bash_math.md)** - Bash에서 산술 연산 수행 방법
- **[Bash trap 가이드](bash_trap_complete_guide.md)** - 시그널 처리 및 cleanup 패턴

### 네트워크
- **[IP 주소 체계 가이드](ip_addressing_guide.md)** - IPv4/IPv6, 서브넷, CIDR 표기법
- **[tcpdump 예제](tcpdump_examples.md)** - 네트워크 패킷 캡처 실전 예제

### 시스템 모니터링
- **[리소스 모니터링](resource_utilization_monitoring.md)** - CPU, 메모리, 디스크 사용량 확인

### 에디터
- **[Vim 사용법](vim.md)** - Vim 에디터 기본 및 고급 기능

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
1. [IP 주소 체계](ip_addressing_guide.md)
2. [tcpdump 예제](tcpdump_examples.md)
3. [리소스 모니터링](resource_utilization_monitoring.md)

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

## 관련 문서

- [Linux 디버깅 도구](../01_debuggin_linux/) - 시스템 디버깅
- [고급 Linux](../03_advanced_linux/) - 고급 시스템 관리
- [네트워크 이론](../05_computer_science/) - 네트워크 프로토콜

---

© 2026. Licensed under CC BY 4.0.

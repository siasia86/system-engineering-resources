# Linux 디버깅/추적 도구 가이드 - 목차

> **내부 공유 자료**  
> 작성일: 2026-01-29  
> 버전: 1.0  
> 관리: SRE Team

## 문서 목록

### 기본 추적 도구
1. **[ltrace.md](ltrace.md)** - 라이브러리 함수 추적
   - 용도: 함수 호출 추적, 라이브러리 디버깅
   - 난이도: ⭐⭐
   - 오버헤드: 높음 (10-20배)

2. **[strace.md](strace.md)** - 시스템 콜 추적
   - 용도: 파일/네트워크 문제, 시스템 콜 디버깅
   - 난이도: ⭐⭐
   - 오버헤드: 중간 (5-10배)

### 성능 분석 도구
3. **[perf.md](perf.md)** - CPU 성능 프로파일링
   - 용도: CPU 병목, 성능 최적화
   - 난이도: ⭐⭐⭐
   - 오버헤드: 낮음 (1-5%)

4. **[bpftrace.md](bpftrace.md)** - eBPF 기반 동적 추적
   - 용도: 프로덕션 환경 추적, 커널 분석
   - 난이도: ⭐⭐⭐⭐
   - 오버헤드: 매우 낮음 (< 1%)

### 디버깅 도구
5. **[gdb.md](gdb.md)** - 소스 레벨 디버거
   - 용도: 크래시 분석, 로직 버그
   - 난이도: ⭐⭐⭐
   - 오버헤드: 높음 (중단점 사용)

6. **[valgrind.md](valgrind.md)** - 메모리 디버깅
   - 용도: 메모리 누수, 버퍼 오버플로우
   - 난이도: ⭐⭐
   - 오버헤드: 매우 높음 (20-50배)

### 시스템 모니터링 도구
7. **[lsof.md](lsof.md)** - 열린 파일 추적
   - 용도: 파일/포트 사용 확인
   - 난이도: ⭐
   - 오버헤드: 매우 낮음

8. **[iotop.md](iotop.md)** - I/O 모니터링
   - 용도: 디스크 I/O 병목
   - 난이도: ⭐
   - 오버헤드: 매우 낮음

9. **[tcpdump.md](tcpdump.md)** - 네트워크 패킷 캡처
   - 용도: 네트워크 문제, 프로토콜 분석
   - 난이도: ⭐⭐⭐
   - 오버헤드: 중간

## 상황별 도구 선택 가이드

### 문제 유형별

| 문제 | 1순위 | 2순위 | 3순위 |
|------|-------|-------|-------|
| **파일을 못 찾음** | strace | lsof | - |
| **메모리 누수** | valgrind | ltrace | bpftrace |
| **CPU 병목** | perf | bpftrace | - |
| **네트워크 문제** | tcpdump | strace | lsof |
| **디스크 느림** | iotop | strace | perf |
| **크래시 분석** | gdb | strace | - |
| **포트 충돌** | lsof | strace | - |

### 환경별

**개발 환경:**
- 모든 도구 사용 가능
- valgrind, gdb 적극 활용
- 오버헤드 무시 가능

**스테이징 환경:**
- 대부분 도구 사용 가능
- 성능 영향 고려
- 짧은 시간 사용

**프로덕션 환경:**
- ⚠️ 주의 필요
- 권장: perf, bpftrace, lsof, iotop
- 제한적 사용: strace, ltrace (짧은 시간만)
- 비권장: valgrind, gdb (서비스 중단)

## 체크리스트

### 프로덕션 환경 사용 전

- [ ] 테스트 환경에서 먼저 실행
- [ ] 예상 오버헤드 확인
- [ ] 시간 제한 설정 (timeout 사용)
- [ ] 로그 저장 경로 및 권한 확인
- [ ] 모니터링 준비 (CPU, 메모리, 디스크)
- [ ] 롤백 계획 수립
- [ ] 팀원에게 알림

### 실행 중

- [ ] 시스템 리소스 모니터링
- [ ] 서비스 응답 시간 확인
- [ ] 에러 로그 확인
- [ ] 필요 시 즉시 중단

### 실행 후

- [ ] 로그 파일 검토
- [ ] 민감 정보 확인 및 삭제
- [ ] 결과 문서화
- [ ] 팀 공유

## 일반적인 워크플로우

### 1. 문제 발견
```bash
# 빠른 확인
top, htop          # CPU/메모리
iotop              # 디스크 I/O
lsof -i            # 네트워크
```

### 2. 초기 진단
```bash
# 통계 수집
strace -c ./myapp
perf stat ./myapp
```

### 3. 상세 분석
```bash
# 문제 영역 집중
strace -e trace=file ./myapp
perf record -g ./myapp
```

### 4. 근본 원인 분석
```bash
# 깊이 있는 분석
gdb ./myapp core
valgrind --leak-check=full ./myapp
```

##  지원

### 문의
- **Slack:** -
- **Email:** siasia.linux@gmail.com
- **github:**  

### 교육
- 1:1 멘토링: 인프라팀에 요청

## 기여

문서 개선 제안:
1. GitHub Issue 생성
2. Pull Request 제출
3. 인프라팀에 직접 연락

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

**마지막 업데이트**: 2026-03-25

© 2026 siasia86. Licensed under CC BY 4.0.

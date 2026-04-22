# perf - Linux 성능 분석 도구

## perf란?

**Performance Analysis Tool** - Linux 커널에 내장된 성능 분석 도구로, CPU 프로파일링과 성능 카운터를 사용하여 시스템 성능을 분석합니다.

## 주요 특징

- 하드웨어 성능 카운터 사용
- 커널과 유저 공간 모두 분석
- 낮은 오버헤드 (1-5%)
- 샘플링 기반 프로파일링
- 콜 그래프 지원

## 설치

```bash
# Ubuntu/Debian
sudo apt-get install linux-tools-common linux-tools-generic

# CentOS/RHEL
sudo yum install perf

# 현재 커널 버전용
sudo apt-get install linux-tools-$(uname -r)
```

## 기본 명령어

### 1. perf stat (통계)

**기본 사용:**
```bash
# 프로그램 실행 통계
perf stat ls

# 출력 예시:
# Performance counter stats for 'ls':
#           0.52 msec task-clock
#              1      context-switches
#              0      cpu-migrations
#            156      page-faults
#      1,234,567      cycles
#        987,654      instructions
```

**상세 통계:**
```bash
# 모든 카운터
perf stat -d ls

# 특정 이벤트
perf stat -e cycles,instructions,cache-misses ls

# 반복 실행
perf stat -r 10 ls
```

### 2. perf record (기록)

**CPU 프로파일링:**
```bash
# 기본 기록
perf record ls

# 콜 그래프 포함
perf record -g ls

# 특정 프로세스
perf record -p <PID>

# 특정 시간
perf record -a sleep 10

# 샘플링 주파수 조정
perf record -F 99 ls
```

**출력 파일:**
- 기본: `perf.data`
- 지정: `perf record -o output.data ls`

### 3. perf report (보고서)

**결과 분석:**
```bash
# 기본 보고서
perf report

# 특정 파일
perf report -i perf.data

# 콜 그래프
perf report -g

# TUI 인터페이스
perf report --tui
```

**출력 예시:**
```
# Overhead  Command  Shared Object     Symbol
# ........  .......  ................  ......
    45.23%  ls       libc.so.6         [.] __strcmp_avx2
    12.45%  ls       libc.so.6         [.] strlen
     8.67%  ls       [kernel]          [k] syscall_return
```

### 4. perf top (실시간)

**실시간 모니터링:**
```bash
# 전체 시스템
perf top

# 특정 프로세스
perf top -p <PID>

# 커널만
perf top -K

# 유저 공간만
perf top -U
```

## 고급 사용법

### CPU 프로파일링

**전체 시스템:**
```bash
# 10초간 전체 시스템 프로파일링
perf record -a -g sleep 10
perf report
```

**특정 프로세스:**
```bash
# 프로세스 시작부터
perf record -g ./myapp

# 실행 중인 프로세스
perf record -g -p $(pgrep myapp) sleep 30
```

### 이벤트 추적

**사용 가능한 이벤트 확인:**
```bash
# 모든 이벤트
perf list

# 하드웨어 이벤트
perf list hardware

# 소프트웨어 이벤트
perf list software

# 캐시 이벤트
perf list cache
```

**특정 이벤트 추적:**
```bash
# 캐시 미스
perf stat -e cache-misses,cache-references ls

# 브랜치 예측 실패
perf stat -e branch-misses,branches ls

# 페이지 폴트
perf stat -e page-faults ls
```

### 콜 그래프 분석

**Flame Graph 생성:**
```bash
# 1. 데이터 수집
perf record -F 99 -a -g sleep 30

# 2. 스크립트 변환
perf script > out.perf

# 3. Flame Graph 생성 (FlameGraph 도구 필요)
./stackcollapse-perf.pl out.perf > out.folded
./flamegraph.pl out.folded > flamegraph.svg
```

### 특정 CPU 추적

```bash
# CPU 0만
perf record -C 0 sleep 10

# CPU 0,1,2
perf record -C 0-2 sleep 10
```

## 실전 예제

### 예제 1: 느린 프로그램 분석

```bash
# 1. 프로파일링
perf record -g ./slow_program

# 2. 보고서 확인
perf report

# 3. 핫스팟 확인
# Overhead가 높은 함수 찾기
```

### 예제 2: 캐시 성능 분석

```bash
# 캐시 통계
perf stat -e cache-misses,cache-references,L1-dcache-load-misses ./myapp

# 출력:
#   1,234,567  cache-references
#     123,456  cache-misses              # 10% miss rate
```

### 예제 3: 멀티스레드 분석

```bash
# 스레드별 분석
perf record -g --call-graph dwarf ./multithread_app
perf report --sort comm,dso,symbol
```

### 예제 4: 시스템 전체 분석

```bash
# 10초간 전체 시스템
perf record -a -g -F 99 sleep 10

# CPU별 분석
perf report --sort cpu,comm,dso,symbol
```

### 예제 5: 특정 함수 추적

```bash
# 함수 진입/종료 추적
perf probe -x /path/to/binary function_name
perf record -e probe:function_name ./myapp
perf script
```

## 성능 메트릭 해석

### CPU 사용률

```bash
perf stat ./myapp

# task-clock: 실제 CPU 사용 시간
# context-switches: 컨텍스트 스위치 횟수
# cpu-migrations: CPU 간 마이그레이션
```

### IPC (Instructions Per Cycle)

```bash
perf stat -e cycles,instructions ./myapp

# IPC = instructions / cycles
# 높을수록 효율적 (일반적으로 1-4)
```

### 캐시 성능

```bash
perf stat -e cache-misses,cache-references ./myapp

# Miss Rate = cache-misses / cache-references
# 낮을수록 좋음 (일반적으로 < 5%)
```

## 트러블슈팅

### 문제 1: "Permission denied"

```bash
# 해결 1: sudo 사용
sudo perf record ls

# 해결 2: perf_event_paranoid 설정
cat /proc/sys/kernel/perf_event_paranoid
# -1: 제한 없음
#  0: 일부 제한
#  1: 커널 프로파일링 제한
#  2: 커널 프로파일링 + CPU 이벤트 제한

# 임시 변경
echo -1 | sudo tee /proc/sys/kernel/perf_event_paranoid

# 영구 변경
echo "kernel.perf_event_paranoid = -1" | sudo tee -a /etc/sysctl.conf
```

### 문제 2: "No such file or directory"

```bash
# 심볼 정보 없음
# 해결: 디버그 심볼 설치
sudo apt-get install libc6-dbg
```

### 문제 3: "Failed to open"

```bash
# perf.data 권한 문제
sudo chown $USER perf.data
```

## 최적화 팁

### 1. 샘플링 주파수 조정

```bash
# 기본: 1000Hz
perf record -F 1000 ./myapp

# 낮은 오버헤드: 99Hz
perf record -F 99 ./myapp

# 높은 정확도: 4000Hz
perf record -F 4000 ./myapp
```

### 2. 콜 스택 깊이

```bash
# 기본: 127
perf record -g ./myapp

# 깊이 제한
perf record --call-graph dwarf,8192 ./myapp
```

### 3. 데이터 크기 제한

```bash
# 최대 크기 설정 (MB)
perf record -m 128 ./myapp
```

## 실무 워크플로우

### 성능 문제 진단

```bash
# 1. 빠른 확인
perf stat ./myapp

# 2. 프로파일링
perf record -g ./myapp

# 3. 분석
perf report

# 4. 핫스팟 확인
# Overhead > 5% 함수 최적화
```

### 비교 분석

```bash
# 최적화 전
perf stat -r 10 ./myapp_old > before.txt

# 최적화 후
perf stat -r 10 ./myapp_new > after.txt

# 비교
diff before.txt after.txt
```

## 관련 도구

| 도구           | 용도              |
|----------------|-------------------|
| **perf**       | CPU 프로파일링    |
| **flamegraph** | 시각화            |
| **hotspot**    | GUI 프로파일러    |
| **gprof**      | 함수 프로파일링   |
| **valgrind**   | 메모리 프로파일링 |

## 요약

**perf의 강점:**
- 낮은 오버헤드
- 커널 통합
- 하드웨어 카운터 사용
- 전체 시스템 분석

**주요 명령어:**
- `perf stat` - 통계
- `perf record` - 기록
- `perf report` - 분석
- `perf top` - 실시간

**언제 사용?**
- CPU 병목 찾기
- 성능 최적화
- 캐시 성능 분석
- 시스템 전체 프로파일링

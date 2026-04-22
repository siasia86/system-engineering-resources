# bpftrace - eBPF 기반 동적 추적 도구

## bpftrace란?

**eBPF-based Tracing Tool** - Linux eBPF를 사용하여 커널과 유저 공간을 동적으로 추적하는 고성능 도구입니다.

## 주요 특징

- 매우 낮은 오버헤드 (< 1%)
- 커널 수정 없이 추적
- 강력한 스크립팅 언어
- 실시간 분석
- 프로덕션 환경 사용 가능

## 설치

```bash
# Ubuntu 20.04+
sudo apt-get install bpftrace

# Fedora/CentOS 8+
sudo dnf install bpftrace

# 소스 컴파일
git clone https://github.com/iovisor/bpftrace
cd bpftrace
mkdir build && cd build
cmake ..
make && sudo make install

# 버전 확인
bpftrace --version
```

## 기본 사용법

### One-Liners

```bash
# 시스템 콜 추적
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf("%s %s\n", comm, str(args->filename)); }'

# 함수 호출 추적
sudo bpftrace -e 'kprobe:do_sys_open { printf("%s\n", str(arg1)); }'

# 프로세스 생성 추적
sudo bpftrace -e 'tracepoint:sched:sched_process_exec { printf("%s\n", comm); }'
```

### 스크립트 파일

```bash
# 스크립트 작성
cat > trace.bt << 'EOF'
#!/usr/bin/env bpftrace

BEGIN {
    printf("Tracing... Hit Ctrl-C to end.\n");
}

tracepoint:syscalls:sys_enter_openat {
    printf("%s opened %s\n", comm, str(args->filename));
}

END {
    printf("Done.\n");
}
EOF

# 실행
sudo bpftrace trace.bt
```

## 프로브 타입

### 1. Tracepoints

```bash
# 사용 가능한 tracepoint 목록
sudo bpftrace -l 'tracepoint:*'

# 시스템 콜 진입
tracepoint:syscalls:sys_enter_*

# 시스템 콜 종료
tracepoint:syscalls:sys_exit_*

# 스케줄러
tracepoint:sched:*
```

### 2. Kprobes (커널 함수)

```bash
# 커널 함수 목록
sudo bpftrace -l 'kprobe:*'

# 함수 진입
kprobe:do_sys_open

# 함수 종료
kretprobe:do_sys_open
```

### 3. Uprobes (유저 함수)

```bash
# 유저 함수 추적
uprobe:/bin/bash:readline

# 함수 종료
uretprobe:/bin/bash:readline

# 라이브러리 함수
uprobe:/lib/x86_64-linux-gnu/libc.so.6:malloc
```

### 4. USDT (User Statically-Defined Tracing)

```bash
# USDT 프로브 목록
sudo bpftrace -l 'usdt:/usr/bin/python3:*'

# Python 함수 호출
usdt:/usr/bin/python3:function__entry
```

## 내장 변수

```bash
# 프로세스 정보
comm    # 프로세스 이름
pid     # 프로세스 ID
tid     # 스레드 ID
uid     # 사용자 ID
gid     # 그룹 ID

# 시간
nsecs   # 나노초 타임스탬프
elapsed # 경과 시간

# 함수 정보
func    # 함수 이름
probe   # 프로브 이름
retval  # 반환값 (kretprobe)

# 인자
arg0-argN  # 함수 인자
args       # tracepoint 인자
```

## 실전 예제

### 예제 1: 파일 열기 추적

```bash
# 모든 파일 열기
sudo bpftrace -e '
tracepoint:syscalls:sys_enter_openat {
    printf("%s(%d) opened: %s\n", comm, pid, str(args->filename));
}'

# 특정 프로세스만
sudo bpftrace -e '
tracepoint:syscalls:sys_enter_openat /comm == "nginx"/ {
    printf("nginx opened: %s\n", str(args->filename));
}'
```

### 예제 2: 느린 시스템 콜 찾기

```bash
sudo bpftrace -e '
tracepoint:syscalls:sys_enter_* {
    @start[tid] = nsecs;
}

tracepoint:syscalls:sys_exit_* /@start[tid]/ {
    $duration = (nsecs - @start[tid]) / 1000000;  // ms
    if ($duration > 10) {
        printf("%s took %d ms\n", probe, $duration);
    }
    delete(@start[tid]);
}'
```

### 예제 3: 메모리 할당 추적

```bash
sudo bpftrace -e '
uprobe:/lib/x86_64-linux-gnu/libc.so.6:malloc {
    printf("%s malloc(%d)\n", comm, arg0);
    @bytes[comm] = sum(arg0);
}

END {
    printf("\nMemory allocated by process:\n");
    print(@bytes);
}'
```

### 예제 4: TCP 연결 추적

```bash
sudo bpftrace -e '
kprobe:tcp_connect {
    printf("%s connecting to ", comm);
}

kretprobe:tcp_connect {
    printf("result: %d\n", retval);
}'
```

### 예제 5: 프로세스 생성 모니터링

```bash
sudo bpftrace -e '
tracepoint:sched:sched_process_exec {
    printf("%s(%d) executed: %s\n", comm, pid, str(args->filename));
}'
```

## 고급 기능

### 맵 (Maps)

```bash
# 카운터
@count[comm] = count();

# 합계
@bytes[comm] = sum(arg0);

# 평균
@avg[comm] = avg(arg0);

# 최소/최대
@min[comm] = min(arg0);
@max[comm] = max(arg0);

# 히스토그램
@hist = hist(arg0);

# 선형 히스토그램
@lhist = lhist(arg0, 0, 1000, 100);
```

### 필터링

```bash
# 조건부 실행
tracepoint:syscalls:sys_enter_openat /pid == 1234/ {
    printf("PID 1234 opened: %s\n", str(args->filename));
}

# 복합 조건
tracepoint:syscalls:sys_enter_openat /comm == "nginx" && uid == 0/ {
    printf("root nginx opened: %s\n", str(args->filename));
}
```

### 시간 간격

```bash
# 1초마다 실행
interval:s:1 {
    printf("Tick\n");
    print(@count);
    clear(@count);
}

# 프로파일 (99Hz)
profile:hz:99 {
    @[kstack] = count();
}
```

## 유용한 스크립트

### 1. 파일 I/O 모니터링

```bash
#!/usr/bin/env bpftrace

BEGIN {
    printf("Tracing file I/O... Hit Ctrl-C to end.\n");
}

tracepoint:syscalls:sys_enter_read,
tracepoint:syscalls:sys_enter_write {
    @io[comm] = count();
    @bytes[comm] = sum(args->count);
}

END {
    printf("\nI/O operations by process:\n");
    print(@io);
    printf("\nBytes by process:\n");
    print(@bytes);
}
```

### 2. CPU 사용률 프로파일링

```bash
#!/usr/bin/env bpftrace

profile:hz:99 {
    @[comm, kstack] = count();
}

END {
    printf("Top CPU consumers:\n");
    print(@, 10);
}
```

### 3. 네트워크 지연 측정

```bash
#!/usr/bin/env bpftrace

kprobe:tcp_sendmsg {
    @start[tid] = nsecs;
}

kretprobe:tcp_sendmsg /@start[tid]/ {
    $duration = (nsecs - @start[tid]) / 1000;  // us
    @latency = hist($duration);
    delete(@start[tid]);
}

END {
    printf("TCP send latency (us):\n");
    print(@latency);
}
```

### 4. 디스크 I/O 지연

```bash
#!/usr/bin/env bpftrace

kprobe:blk_account_io_start {
    @start[arg0] = nsecs;
}

kprobe:blk_account_io_done /@start[arg0]/ {
    $duration = (nsecs - @start[arg0]) / 1000000;  // ms
    @io_latency = hist($duration);
    delete(@start[arg0]);
}

END {
    printf("Disk I/O latency (ms):\n");
    print(@io_latency);
}
```

### 5. 시스템 콜 통계

```bash
#!/usr/bin/env bpftrace

tracepoint:syscalls:sys_enter_* {
    @syscalls[probe] = count();
}

interval:s:1 {
    printf("\nTop syscalls:\n");
    print(@syscalls, 10);
    clear(@syscalls);
}
```

## 실무 활용

### 1. 성능 병목 찾기

```bash
# CPU 핫스팟
sudo bpftrace -e 'profile:hz:99 { @[kstack] = count(); }'

# 느린 함수
sudo bpftrace -e '
kprobe:vfs_read {
    @start[tid] = nsecs;
}
kretprobe:vfs_read /@start[tid]/ {
    @us[comm] = hist((nsecs - @start[tid]) / 1000);
    delete(@start[tid]);
}'
```

### 2. 메모리 누수 추적

```bash
# malloc/free 추적
sudo bpftrace -e '
uprobe:/lib/x86_64-linux-gnu/libc.so.6:malloc {
    @alloc[comm] = count();
}
uprobe:/lib/x86_64-linux-gnu/libc.so.6:free {
    @free[comm] = count();
}
interval:s:5 {
    print(@alloc);
    print(@free);
}'
```

### 3. 네트워크 디버깅

```bash
# 패킷 드롭 추적
sudo bpftrace -e '
tracepoint:skb:kfree_skb {
    @drop[kstack] = count();
}'
```

### 4. 보안 감사

```bash
# 권한 상승 추적
sudo bpftrace -e '
tracepoint:syscalls:sys_enter_setuid /args->uid == 0/ {
    printf("%s(%d) became root\n", comm, pid);
}'
```

## 트러블슈팅

### 문제 1: "Operation not permitted"

```bash
# 해결: sudo 사용
sudo bpftrace script.bt

# 또는 권한 부여
sudo setcap cap_sys_admin,cap_bpf=eip /usr/bin/bpftrace
```

### 문제 2: "Could not resolve symbol"

```bash
# 디버그 심볼 설치
sudo apt-get install linux-headers-$(uname -r)
```

### 문제 3: "BPF program too large"

```bash
# 프로그램 단순화
# 또는 커널 파라미터 조정
sudo sysctl -w net.core.bpf_jit_limit=1000000000
```

## 성능 고려사항

```bash
# 오버헤드 측정
sudo bpftrace -e 'BEGIN { printf("overhead test\n"); }'

# 샘플링 주파수 조정
profile:hz:49  # 낮은 주파수 (낮은 오버헤드)
profile:hz:999 # 높은 주파수 (높은 정확도)
```

## 관련 도구

| 도구          | 용도             |
|---------------|------------------|
| **bpftrace**  | eBPF 스크립팅    |
| **bcc**       | eBPF 도구 모음   |
| **perf**      | 성능 분석        |
| **ftrace**    | 커널 추적        |
| **systemtap** | 동적 추적 (구형) |

## 요약

**bpftrace의 강점:**
- 매우 낮은 오버헤드
- 프로덕션 사용 가능
- 강력한 스크립팅
- 커널/유저 공간 모두 추적

**주요 프로브:**
- tracepoint - 안정적인 추적점
- kprobe - 커널 함수
- uprobe - 유저 함수
- profile - 샘플링

**언제 사용?**
- 성능 병목 찾기
- 시스템 동작 이해
- 프로덕션 디버깅
- 보안 감사

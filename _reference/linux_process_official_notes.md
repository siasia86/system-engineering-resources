---
name: linux-process-official-notes
last_checked: 2026-08-01
sources:
  - https://man7.org/linux/man-pages/man2/fork.2.html
  - https://man7.org/linux/man-pages/man2/execve.2.html
  - https://man7.org/linux/man-pages/man2/wait.2.html
  - https://man7.org/linux/man-pages/man2/mmap.2.html
  - https://man7.org/linux/man-pages/man7/pipe.7.html
  - https://man7.org/linux/man-pages/man2/shmget.2.html
  - https://man7.org/linux/man-pages/man7/mq_overview.7.html
  - https://man7.org/linux/man-pages/man5/proc_sys_vm.5.html
---

# Linux Process / Memory / IPC 공식 참조 노트

## 1. Process Lifecycle (fork/exec/wait/exit)

### 공식 소스

| 소스     | URL                                                 | 용도                |
|----------|-----------------------------------------------------|---------------------|
| fork.2   | https://man7.org/linux/man-pages/man2/fork.2.html   | fork 동작, 에러코드 |
| execve.2 | https://man7.org/linux/man-pages/man2/execve.2.html | exec 계열 동작      |
| wait.2   | https://man7.org/linux/man-pages/man2/wait.2.html   | wait/zombie 상태    |

### 검증된 사실 (2026-08-01)

| 항목               | 값                                             | 출처     |
|--------------------|------------------------------------------------|----------|
| fork 반환값 (부모) | 자식 PID (양수)                                | fork.2   |
| fork 반환값 (자식) | 0                                              | fork.2   |
| fork 실패 시       | -1 반환, EAGAIN(RLIMIT_NPROC 초과) 또는 ENOMEM | fork.2   |
| execve 성공 시     | 반환하지 않음 (프로세스 이미지 교체)           | execve.2 |
| execve 실패 시     | -1 반환, ENOEXEC(바이너리 형식 오류) 등        | execve.2 |
| zombie 프로세스    | 종료 후 부모가 wait 호출 전까지 유지           | wait.2   |
| wait 해제 효과     | zombie 상태 자식의 커널 자원 해제              | wait.2   |
| SIGCHLD            | 자식 상태 변경 시 부모에게 전달                | wait.2   |
| SCHED_DEADLINE     | fork 시 EAGAIN 반환 가능 (man page 명시)       | fork.2   |

## 2. Virtual Memory

### 공식 소스

| 소스        | URL                                                  | 용도                  |
|-------------|------------------------------------------------------|-----------------------|
| mmap.2      | https://man7.org/linux/man-pages/man2/mmap.2.html    | mmap 파라미터, 플래그 |
| MM concepts | https://docs.kernel.org/admin-guide/mm/concepts.html | 가상 메모리 개념      |

### 검증된 사실 (2026-08-01)

| 항목                 | 값                                                | 출처        |
|----------------------|---------------------------------------------------|-------------|
| 가상 메모리 목적     | 물리 메모리 세부사항 추상화, demand paging 제공   | MM concepts |
| anonymous mapping    | 파일과 연결되지 않은 메모리 (heap, stack 등)      | MM concepts |
| file-backed mapping  | 파일 내용으로 초기화되는 메모리                   | MM concepts |
| MAP_PRIVATE          | CoW 사본 (다른 프로세스와 공유하지 않음)          | mmap.2      |
| MAP_SHARED           | 물리 페이지 공유 (변경사항 파일에 반영)           | mmap.2      |
| MAP_SHARED_VALIDATE  | MAP_SHARED + 알 수 없는 플래그 거부 (Linux 4.15+) | mmap.2      |
| MAP_ANONYMOUS        | fd=-1, 파일 연결 없는 익명 매핑                   | mmap.2      |
| addr=NULL 시         | 커널이 페이지 정렬된 주소 선택                    | mmap.2      |
| PROT_READ/WRITE/EXEC | 페이지 보호 비트 (OR 조합)                        | mmap.2      |
| dirty page 처리      | 익명 매핑 dirty page → 스왑 아웃                  | MM concepts |

## 3. OOM (Out-of-Memory) Killer

### 공식 소스

| 소스          | URL                                                      | 용도                     |
|---------------|----------------------------------------------------------|--------------------------|
| proc.5        | https://man7.org/linux/man-pages/man5/proc.5.html        | oom_score, oom_score_adj |
| proc_sys_vm.5 | https://man7.org/linux/man-pages/man5/proc_sys_vm.5.html | overcommit_memory 값     |

### 검증된 사실 (2026-08-01)

| 항목                    | 값                                          | 출처          |
|-------------------------|---------------------------------------------|---------------|
| /proc/PID/oom_score     | 커널이 계산한 OOM 점수 (높을수록 먼저 종료) | proc.5        |
| /proc/PID/oom_score_adj | 사용자 조정값 (-1000 ~ +1000)               | proc.5        |
| oom_score_adj = -1000   | OOM killer 대상에서 제외                    | proc.5        |
| overcommit_memory = 0   | 휴리스틱 기반 허용 (기본값)                 | proc_sys_vm.5 |
| overcommit_memory = 1   | 항상 허용 (sparse array 등 과학 계산 용도)  | proc_sys_vm.5 |
| overcommit_memory = 2   | 제한 초과 시 할당 거부 (swap + RAM% 초과)   | proc_sys_vm.5 |

## 4. IPC (Inter-Process Communication)

### 공식 소스

| 소스          | URL                                                      | 용도                 |
|---------------|----------------------------------------------------------|----------------------|
| pipe.7        | https://man7.org/linux/man-pages/man7/pipe.7.html        | pipe/FIFO 개요       |
| shmget.2      | https://man7.org/linux/man-pages/man2/shmget.2.html      | System V 공유 메모리 |
| mq_overview.7 | https://man7.org/linux/man-pages/man7/mq_overview.7.html | POSIX 메시지 큐      |

### 검증된 사실 (2026-08-01)

| IPC 메커니즘         | 특성                                              | 출처          |
|----------------------|---------------------------------------------------|---------------|
| pipe                 | 단방향, 관련 프로세스 간 (부모-자식)              | pipe.7        |
| FIFO (named pipe)    | 단방향, 비관련 프로세스 간 (파일시스템 경로 사용) | pipe.7        |
| System V shm         | shmget으로 세그먼트 생성, 프로세스 간 공유        | shmget.2      |
| POSIX mq             | mq_open으로 큐 생성, 메시지 단위 교환             | mq_overview.7 |
| POSIX mq vs Sys V mq | API 별도, POSIX mq는 우선순위 지원                | mq_overview.7 |
| shmget IPC_PRIVATE   | 새 공유 메모리 세그먼트 생성 (관련 프로세스용)    | shmget.2      |
| 공유 메모리 초기값   | 새 세그먼트 생성 시 0으로 초기화                  | shmget.2      |

## 5. Linux 시스템 프로세스

### 공식 소스

| 소스      | URL                                                  | 용도             |
|-----------|------------------------------------------------------|------------------|
| init.1    | https://man7.org/linux/man-pages/man1/init.1.html    | PID 1, init 계열 |
| systemd.1 | https://man7.org/linux/man-pages/man1/systemd.1.html | systemd 개요     |

### 검증된 사실 (2026-08-01)

| 항목             | 값                                              | 출처      |
|------------------|-------------------------------------------------|-----------|
| PID 0            | swapper/idle 프로세스 (스케줄러)                | 커널 소스 |
| PID 1            | init 또는 systemd (모든 사용자 프로세스의 조상) | systemd.1 |
| kthreadd (PID 2) | 모든 커널 스레드의 부모                         | 커널 관례 |
| orphan 프로세스  | 부모 종료 시 PID 1(init/systemd)에 입양         | wait.2    |
| zombie 정리      | 부모가 wait 호출하지 않으면 PID 1이 회수        | wait.2    |

## 6. deprecated / removed

| 항목                         | 상태                                 | 출처        |
|------------------------------|--------------------------------------|-------------|
| System V IPC (shmget/msgget) | POSIX IPC 사용 권장                  | mq_overview |
| vfork                        | fork+exec 패턴 또는 posix_spawn 권장 | fork.2      |

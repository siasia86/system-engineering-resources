# TODO2 — linux/ _reference 신규 작성 작업

`01_fundamentals/linux/` 문서 중 `<!-- reference:` 연결이 불가한 12개 파일을 위해
`_reference/` 파일을 신규 작성합니다.

작업 단위: **3개씩 배치** (context compact 대비)
완료 기준: `_reference` 작성 → `INDEX.md` 등록 → `<!-- reference:` 삽입 → md-style-check 0건

---

## 목차

| 배치 | 섹션                                                   |
|------|--------------------------------------------------------|
| 1    | [Batch 1: gdb / strace / ltrace](#batch-1)             |
| 2    | [Batch 2: valgrind / perf / lsof](#batch-2)            |
| 3    | [Batch 3: iotop / tcpdump / shell](#batch-3)           |
| 4    | [Batch 4: root_password / vim / vim_airline](#batch-4) |

---

## Batch 1

**대상 파일:** `gdb.md` / `strace.md` / `ltrace.md`

### 작업 항목

| # | 작업                                       | 상태 |
|---|--------------------------------------------|------|
| 1 | `_reference/gdb_official_notes.md` 작성    | ⬜   |
| 2 | `_reference/strace_official_notes.md` 작성 | ⬜   |
| 3 | `_reference/ltrace_official_notes.md` 작성 | ⬜   |
| 4 | `_reference/INDEX.md` 3건 등록             | ⬜   |
| 5 | `gdb.md` → `<!-- reference:` 삽입          | ⬜   |
| 6 | `strace.md` → `<!-- reference:` 삽입       | ⬜   |
| 7 | `ltrace.md` → `<!-- reference:` 삽입       | ⬜   |
| 8 | md-style-check 3파일 0건 확인              | ⬜   |

### 공식 소스 URL

| 파일                       | 공식 소스 URL                                       |
|----------------------------|-----------------------------------------------------|
| `gdb_official_notes.md`    | https://www.sourceware.org/gdb/documentation/       |
| `gdb_official_notes.md`    | https://man7.org/linux/man-pages/man1/gdb.1.html    |
| `strace_official_notes.md` | https://strace.io/                                  |
| `strace_official_notes.md` | https://man7.org/linux/man-pages/man1/strace.1.html |
| `ltrace_official_notes.md` | https://man7.org/linux/man-pages/man1/ltrace.1.html |
| `ltrace_official_notes.md` | https://gitlab.com/cespedes/ltrace                  |

---

## Batch 2

**대상 파일:** `valgrind.md` / `perf.md` / `lsof.md`

### 작업 항목

| # | 작업                                         | 상태 |
|---|----------------------------------------------|------|
| 1 | `_reference/valgrind_official_notes.md` 작성 | ⬜   |
| 2 | `_reference/perf_official_notes.md` 작성     | ⬜   |
| 3 | `_reference/lsof_official_notes.md` 작성     | ⬜   |
| 4 | `_reference/INDEX.md` 3건 등록               | ⬜   |
| 5 | `valgrind.md` → `<!-- reference:` 삽입       | ⬜   |
| 6 | `perf.md` → `<!-- reference:` 삽입           | ⬜   |
| 7 | `lsof.md` → `<!-- reference:` 삽입           | ⬜   |
| 8 | md-style-check 3파일 0건 확인                | ⬜   |

### 공식 소스 URL

| 파일                         | 공식 소스 URL                                     |
|------------------------------|---------------------------------------------------|
| `valgrind_official_notes.md` | https://valgrind.org/docs/manual/manual.html      |
| `valgrind_official_notes.md` | https://valgrind.org/docs/manual/mc-manual.html   |
| `perf_official_notes.md`     | https://perf.wiki.kernel.org/index.php/Main_Page  |
| `perf_official_notes.md`     | https://man7.org/linux/man-pages/man1/perf.1.html |
| `lsof_official_notes.md`     | https://man7.org/linux/man-pages/man8/lsof.8.html |
| `lsof_official_notes.md`     | https://github.com/nicowillis/lsof                |

---

## Batch 3

**대상 파일:** `iotop.md` / `tcpdump.md` / `shell_interactive_mode.md`

### 작업 항목

| #  | 작업                                                            | 상태 |
|----|-----------------------------------------------------------------|------|
| 1  | `_reference/iotop_official_notes.md` 작성                       | ⬜   |
| 2  | `_reference/tcpdump_official_notes.md` 작성                     | ⬜   |
| 3  | `_reference/bash_shell_official_notes.md` 작성                  | ⬜   |
| 4  | `_reference/INDEX.md` 3건 등록                                  | ⬜   |
| 5  | `iotop.md` → `<!-- reference:` 삽입                             | ⬜   |
| 6  | `tcpdump.md` → `<!-- reference:` 삽입                           | ⬜   |
| 7  | `shell_interactive_mode.md` → `<!-- reference:` 삽입            | ⬜   |
| 8  | `bash_file_redirection.md` 추가 연결 (bash_shell → kernel 병기) | ⬜   |
| 9  | `bash_math.md` 추가 연결                                        | ⬜   |
| 10 | `bash_trap_complete_guide.md` 추가 연결                         | ⬜   |
| 11 | md-style-check 대상 파일 0건 확인                               | ⬜   |

### 공식 소스 URL

| 파일                           | 공식 소스 URL                                      |
|--------------------------------|----------------------------------------------------|
| `iotop_official_notes.md`      | https://man7.org/linux/man-pages/man8/iotop.8.html |
| `iotop_official_notes.md`      | https://github.com/Tomas-M/iotop                   |
| `tcpdump_official_notes.md`    | https://www.tcpdump.org/manpages/tcpdump.1.html    |
| `tcpdump_official_notes.md`    | https://www.tcpdump.org/                           |
| `bash_shell_official_notes.md` | https://www.gnu.org/software/bash/manual/bash.html |
| `bash_shell_official_notes.md` | https://man7.org/linux/man-pages/man1/bash.1.html  |

🟡 `bash_shell_official_notes.md` 작성 시 `bash_file_redirection.md`, `bash_math.md`,
   `bash_trap_complete_guide.md`에도 동시 연결. 기존 `linux_kernel_official_notes.md`와
   병기 형태(`<!-- reference: _reference/linux_kernel_official_notes.md, _reference/bash_shell_official_notes.md -->`)로 적용.

---

## Batch 4

**대상 파일:** `root_password_recovery.md` / `vim.md` / `vim_airline.md`

### 작업 항목

| # | 작업                                                                 | 상태 |
|---|----------------------------------------------------------------------|------|
| 1 | `_reference/vim_official_notes.md` 작성                              | ⬜   |
| 2 | `_reference/INDEX.md` 1건 등록                                       | ⬜   |
| 3 | `vim.md` → `<!-- reference:` 삽입                                    | ⬜   |
| 4 | `vim_airline.md` H1 구조 수정 (H1 12개 → H2 변환)                    | ⬜   |
| 5 | `vim_airline.md` → `<!-- reference:` 삽입                            | ⬜   |
| 6 | `root_password_recovery.md` 재검토 (절차 문서, ref 불필요 최종 확인) | ⬜   |
| 7 | md-style-check 대상 파일 0건 확인                                    | ⬜   |

### 공식 소스 URL

| 파일                    | 공식 소스 URL                              |
|-------------------------|--------------------------------------------|
| `vim_official_notes.md` | https://www.vim.org/docs.php               |
| `vim_official_notes.md` | https://vimhelp.org/                       |
| `vim_airline.md` (참고) | https://github.com/vim-airline/vim-airline |

🟡 `root_password_recovery.md`: 배포판별 절차 문서로 단일 공식 소스 특정 불가.
   `_reference` 작성 불필요 — 이 배치에서 최종 확인 후 ✅ 처리.

🟡 `vim_airline.md` H1 구조 문제 (별도 수정 필요):
   현재 H1이 12개 (GitHub README 원문 그대로). `#` → `##` 변환 후 reference 삽입.

---

## 진행 규칙

- 각 배치 순서 엄수: `_reference` 작성 → `INDEX.md` 등록 → `<!-- reference:` 삽입 → md-style-check
- 공식 소스 확인 방법: `lynx -dump <URL>` 또는 `curl` + GitHub API
- `last_checked`: 작업 당일 날짜 기재
- 배치 완료 시 ⬜ → ✅ 업데이트 후 다음 배치 진행

---

## 완료 현황

| 배치    | 대상 파일                                    | 상태 | 완료일 |
|---------|----------------------------------------------|------|--------|
| Batch 1 | gdb.md / strace.md / ltrace.md               | ⬜   | -      |
| Batch 2 | valgrind.md / perf.md / lsof.md              | ⬜   | -      |
| Batch 3 | iotop.md / tcpdump.md / shell_interactive.md | ⬜   | -      |
| Batch 4 | root_password.md / vim.md / vim_airline.md   | ⬜   | -      |

---

## 사전 완료 작업 (2026-08-01)

### `<!-- reference:` 15개 즉시 적용

| 파일                          | 연결 _reference                                  | 상태 |
|-------------------------------|--------------------------------------------------|------|
| `linux_filesystem.md`         | `linux_filesystem_official_notes.md`             | ✅   |
| `linux_virtual_fs.md`         | `linux_filesystem_official_notes.md`             | ✅   |
| `scheduler.md`                | `linux_kernel_official_notes.md`                 | ✅   |
| `netfilter_tc.md`             | `linux_kernel_official_notes.md`                 | ✅   |
| `seccomp_capabilities.md`     | `linux_kernel_official_notes.md`                 | ✅   |
| `bash_file_redirection.md`    | `linux_kernel_official_notes.md`                 | ✅   |
| `bash_math.md`                | `linux_kernel_official_notes.md`                 | ✅   |
| `bash_trap_complete_guide.md` | `linux_kernel_official_notes.md`                 | ✅   |
| `ebpf.md`                     | `ebpf_bpftrace_official_notes.md`                | ✅   |
| `bpftrace.md`                 | `ebpf_bpftrace_official_notes.md`                | ✅   |
| `process_lifecycle.md`        | `linux_process_official_notes.md`                | ✅   |
| `linux_system_processes.md`   | `linux_process_official_notes.md`                | ✅   |
| `ipc.md`                      | kernel_notes + `linux_process_official_notes.md` | ✅   |
| `virtual_memory.md`           | `linux_process_official_notes.md`                | ✅   |
| `oom_hang.md`                 | kernel_notes + `linux_process_official_notes.md` | ✅   |

### 신규 `_reference` 2개 작성 및 fact-check 완료

| 파일                              | 공식 소스                                                                               | fact-check  |
|-----------------------------------|-----------------------------------------------------------------------------------------|-------------|
| `ebpf_bpftrace_official_notes.md` | bpf.2 / docs.kernel.org / ebpf.io / GitHub API                                          | ✅ 0건      |
| `linux_process_official_notes.md` | fork.2 / execve.2 / wait.2 / mmap.2 / pipe.7 / shmget.2 / mq_overview.7 / proc_sys_vm.5 | ✅ 1건 수정 |

🟡 수정 내용: `overcommit_memory` 출처 `MM concepts` → `proc_sys_vm.5` 변경 (직접 접근 가능한 man page 기반으로 교체)

---

**작성일**: 2026-08-01

**마지막 업데이트**: 2026-08-01

© 2026 siasia86. Licensed under CC BY 4.0.

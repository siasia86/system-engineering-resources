# Rust 시스템 프로그래밍

SE 실무에서 필요한 파일 I/O, 프로세스 관리, 시그널 처리, 환경 변수, FFI를 정리합니다.

## 목차

| 섹션                                                                                            |
|-------------------------------------------------------------------------------------------------|
| [1. 파일 I/O](#1-파일-io) / [2. 경로 처리](#2-경로-처리) / [3. 프로세스 관리](#3-프로세스-관리) |
| [4. 환경 변수](#4-환경-변수) / [5. 시그널 처리](#5-시그널-처리) / [6. /proc 파싱](#6-proc-파싱) |
| [7. FFI (C 호출)](#7-ffi-c-호출) / [8. SE 실전 예제](#8-se-실전-예제) / [9. 요약](#9-요약)      |

---

## 1. 파일 I/O

### 읽기

```rust
use std::fs;
use std::io::{self, BufRead, Read};

// 전체 읽기 (소규모 파일)
fn read_all(path: &str) -> io::Result<String> {
    fs::read_to_string(path)
}

// 줄 단위 읽기 (대용량 파일, 메모리 효율적)
fn read_lines(path: &str) -> io::Result<Vec<String>> {
    let file = fs::File::open(path)?;
    let reader = io::BufReader::new(file);
    reader.lines().collect()
}

// 바이너리 읽기
fn read_bytes(path: &str) -> io::Result<Vec<u8>> {
    fs::read(path)
}
```

### 쓰기

```rust
use std::fs::{self, File, OpenOptions};
use std::io::Write;

// 전체 덮어쓰기
fn write_all(path: &str, content: &str) -> io::Result<()> {
    fs::write(path, content)
}

// 추가 (append)
fn append_line(path: &str, line: &str) -> io::Result<()> {
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(path)?;
    writeln!(file, "{}", line)
}

// atomic write (안전한 파일 쓰기)
fn atomic_write(path: &str, content: &str) -> io::Result<()> {
    let tmp = format!("{}.tmp", path);
    fs::write(&tmp, content)?;
    fs::rename(&tmp, path) // rename은 atomic
}
```

### 디렉토리 순회

```rust
use std::fs;
use std::path::Path;

fn find_log_files(dir: &str) -> io::Result<Vec<String>> {
    let mut logs = Vec::new();
    for entry in fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.extension().map_or(false, |ext| ext == "log") {
            logs.push(path.display().to_string());
        }
    }
    Ok(logs)
}

// 재귀 순회 (walkdir 크레이트 권장)
fn find_recursive(dir: &Path, ext: &str) -> io::Result<Vec<String>> {
    let mut results = Vec::new();
    if dir.is_dir() {
        for entry in fs::read_dir(dir)? {
            let path = entry?.path();
            if path.is_dir() {
                results.extend(find_recursive(&path, ext)?);
            } else if path.extension().map_or(false, |e| e == ext) {
                results.push(path.display().to_string());
            }
        }
    }
    Ok(results)
}
```

### 파일 메타데이터

```rust
use std::fs;
use std::os::unix::fs::MetadataExt;

fn file_info(path: &str) -> io::Result<()> {
    let meta = fs::metadata(path)?;
    println!("size: {} bytes", meta.len());
    println!("modified: {:?}", meta.modified()?);
    println!("permissions: {:o}", meta.mode());
    println!("uid: {}, gid: {}", meta.uid(), meta.gid());
    Ok(())
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 경로 처리

### Path와 PathBuf

```rust
use std::path::{Path, PathBuf};

fn path_operations() {
    let path = Path::new("/var/log/nginx/access.log");

    println!("parent: {:?}", path.parent());           // /var/log/nginx
    println!("filename: {:?}", path.file_name());      // access.log
    println!("stem: {:?}", path.file_stem());          // access
    println!("extension: {:?}", path.extension());     // log
    println!("exists: {}", path.exists());
    println!("is_file: {}", path.is_file());
    println!("is_dir: {}", path.is_dir());

    // 경로 조합
    let mut log_dir = PathBuf::from("/var/log");
    log_dir.push("app");
    log_dir.push("error.log");
    println!("combined: {}", log_dir.display()); // /var/log/app/error.log
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 프로세스 관리

### 외부 명령 실행

```rust
use std::process::Command;

// 단순 실행
fn run_command(cmd: &str, args: &[&str]) -> io::Result<()> {
    let status = Command::new(cmd)
        .args(args)
        .status()?;

    if !status.success() {
        eprintln!("Command failed: exit {}", status.code().unwrap_or(-1));
    }
    Ok(())
}

// 출력 캡처
fn capture_output(cmd: &str, args: &[&str]) -> io::Result<String> {
    let output = Command::new(cmd)
        .args(args)
        .output()?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(io::Error::new(io::ErrorKind::Other, stderr.to_string()))
    }
}

// 사용 예시
fn get_hostname() -> io::Result<String> {
    let output = capture_output("hostname", &[])?;
    Ok(output.trim().to_string())
}

fn get_disk_usage() -> io::Result<String> {
    capture_output("df", &["-h", "/"])
}
```

### 파이프 연결

```rust
use std::process::{Command, Stdio};

fn grep_logs(pattern: &str, logfile: &str) -> io::Result<String> {
    let cat = Command::new("cat")
        .arg(logfile)
        .stdout(Stdio::piped())
        .spawn()?;

    let grep = Command::new("grep")
        .arg(pattern)
        .stdin(cat.stdout.unwrap())
        .output()?;

    Ok(String::from_utf8_lossy(&grep.stdout).to_string())
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 환경 변수

```rust
use std::env;

fn get_config_from_env() {
    // 단일 변수
    let port = env::var("PORT").unwrap_or_else(|_| "8080".to_string());

    // 필수 변수 (없으면 종료)
    let db_url = env::var("DATABASE_URL")
        .expect("DATABASE_URL must be set");

    // 전체 환경 변수 순회
    for (key, value) in env::vars() {
        if key.starts_with("APP_") {
            println!("{} = {}", key, value);
        }
    }

    // 커맨드라인 인수
    let args: Vec<String> = env::args().collect();
    println!("Program: {}", args[0]);
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 시그널 처리

### signal-hook 크레이트

```toml
[dependencies]
signal-hook = "0.4"
```

```rust
use signal_hook::{consts::SIGTERM, iterator::Signals};
use std::thread;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut signals = Signals::new(&[SIGTERM, signal_hook::consts::SIGINT])?;

    let handle = thread::spawn(move || {
        for sig in signals.forever() {
            match sig {
                SIGTERM | signal_hook::consts::SIGINT => {
                    println!("Received signal {}, shutting down...", sig);
                    // cleanup
                    break;
                }
                _ => unreachable!(),
            }
        }
    });

    // 메인 작업...
    println!("Running... (Ctrl+C to stop)");
    handle.join().unwrap();
    Ok(())
}
```

### ctrlc 크레이트 (간단)

```rust
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

fn main() {
    let running = Arc::new(AtomicBool::new(true));
    let r = running.clone();

    ctrlc::set_handler(move || {
        r.store(false, Ordering::SeqCst);
    }).expect("Error setting Ctrl-C handler");

    while running.load(Ordering::SeqCst) {
        // 메인 루프
        std::thread::sleep(std::time::Duration::from_secs(1));
        println!("working...");
    }
    println!("Graceful shutdown");
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. /proc 파싱

### CPU 사용량

```rust
use std::fs;
use std::thread;
use std::time::Duration;

#[derive(Debug)]
struct CpuTimes {
    user: u64,
    nice: u64,
    system: u64,
    idle: u64,
    iowait: u64,
}

fn read_cpu_times() -> io::Result<CpuTimes> {
    let content = fs::read_to_string("/proc/stat")?;
    let line = content.lines().next().unwrap(); // "cpu  user nice sys idle..."
    let parts: Vec<u64> = line.split_whitespace()
        .skip(1) // "cpu" 건너뜀
        .take(5)
        .map(|s| s.parse().unwrap_or(0))
        .collect();

    Ok(CpuTimes {
        user: parts[0], nice: parts[1], system: parts[2],
        idle: parts[3], iowait: parts[4],
    })
}

fn cpu_usage_percent() -> io::Result<f64> {
    let t1 = read_cpu_times()?;
    thread::sleep(Duration::from_secs(1));
    let t2 = read_cpu_times()?;

    let total1 = t1.user + t1.nice + t1.system + t1.idle + t1.iowait;
    let total2 = t2.user + t2.nice + t2.system + t2.idle + t2.iowait;
    let idle_diff = (t2.idle + t2.iowait) - (t1.idle + t1.iowait);
    let total_diff = total2 - total1;

    Ok(100.0 * (1.0 - idle_diff as f64 / total_diff as f64))
}
```

### 메모리 정보

```rust
fn memory_info() -> io::Result<(u64, u64)> {
    let content = fs::read_to_string("/proc/meminfo")?;
    let mut total = 0u64;
    let mut available = 0u64;

    for line in content.lines() {
        if line.starts_with("MemTotal:") {
            total = parse_meminfo_value(line);
        } else if line.starts_with("MemAvailable:") {
            available = parse_meminfo_value(line);
        }
    }
    Ok((total, available))
}

fn parse_meminfo_value(line: &str) -> u64 {
    line.split_whitespace()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(0)
}
```

### 디스크 I/O (diskstats)

```rust
fn disk_io_stats(device: &str) -> io::Result<(u64, u64)> {
    let content = fs::read_to_string("/proc/diskstats")?;
    for line in content.lines() {
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() >= 14 && parts[2] == device {
            let reads: u64 = parts[5].parse().unwrap_or(0);   // sectors read
            let writes: u64 = parts[9].parse().unwrap_or(0);  // sectors written
            return Ok((reads * 512, writes * 512)); // bytes
        }
    }
    Err(io::Error::new(io::ErrorKind::NotFound, "device not found"))
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. FFI (C 호출)

### libc 크레이트

```toml
[dependencies]
libc = "0.2"
```

```rust
use libc::{statvfs, c_char};
use std::ffi::CString;
use std::mem;

fn disk_free(path: &str) -> io::Result<(u64, u64)> {
    let c_path = CString::new(path).unwrap();
    let mut stat: statvfs = unsafe { mem::zeroed() };

    let ret = unsafe { libc::statvfs(c_path.as_ptr(), &mut stat) };
    if ret != 0 {
        return Err(io::Error::last_os_error());
    }

    let total = stat.f_blocks * stat.f_frsize;
    let free = stat.f_bavail * stat.f_frsize;
    Ok((total, free))
}
```

### nix 크레이트 (안전한 POSIX 래퍼)

```toml
[dependencies]
nix = { version = "0.31", features = ["fs", "process", "signal"] }
```

```rust
use nix::sys::signal::{self, Signal};
use nix::unistd::Pid;

// 프로세스에 시그널 전송
fn send_signal(pid: i32, sig: Signal) -> nix::Result<()> {
    signal::kill(Pid::from_raw(pid), sig)
}

// 사용
fn restart_service(pid: i32) -> nix::Result<()> {
    send_signal(pid, Signal::SIGHUP)
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. SE 실전 예제

### 로그 로테이션

```rust
use std::fs;
use std::path::Path;

fn rotate_log(log_path: &str, max_files: u32) -> io::Result<()> {
    // app.log.3 → app.log.4, app.log.2 → app.log.3, ...
    for i in (1..max_files).rev() {
        let from = format!("{}.{}", log_path, i);
        let to = format!("{}.{}", log_path, i + 1);
        if Path::new(&from).exists() {
            fs::rename(&from, &to)?;
        }
    }

    // app.log → app.log.1
    if Path::new(log_path).exists() {
        fs::rename(log_path, format!("{}.1", log_path))?;
    }

    // 새 빈 파일 생성
    fs::File::create(log_path)?;
    Ok(())
}
```

### 서비스 PID 관리

```rust
use std::fs;
use std::process;

fn write_pid(pid_file: &str) -> io::Result<()> {
    fs::write(pid_file, process::id().to_string())
}

fn read_pid(pid_file: &str) -> io::Result<u32> {
    let content = fs::read_to_string(pid_file)?;
    content.trim().parse()
        .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))
}

fn is_process_running(pid: u32) -> bool {
    Path::new(&format!("/proc/{}", pid)).exists()
}

fn ensure_single_instance(pid_file: &str) -> io::Result<()> {
    if Path::new(pid_file).exists() {
        let old_pid = read_pid(pid_file)?;
        if is_process_running(old_pid) {
            return Err(io::Error::new(
                io::ErrorKind::AlreadyExists,
                format!("Already running (PID {})", old_pid),
            ));
        }
    }
    write_pid(pid_file)
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 요약

| 기능            | 모듈/크레이트      | 핵심 함수/타입                 |
|-----------------|--------------------|--------------------------------|
| 파일 읽기       | `std::fs`          | `read_to_string`, `File::open` |
| 파일 쓰기       | `std::fs`          | `write`, `OpenOptions`         |
| 줄 단위 읽기    | `std::io::BufRead` | `BufReader::lines()`           |
| 경로 조작       | `std::path`        | `Path`, `PathBuf`              |
| 명령 실행       | `std::process`     | `Command::new().output()`      |
| 환경 변수       | `std::env`         | `var()`, `vars()`              |
| 시그널          | `signal-hook`      | `Signals::new()`               |
| /proc 파싱      | `std::fs`          | 텍스트 파싱                    |
| POSIX 시스템 콜 | `nix`              | `kill`, `statvfs`, `getuid`    |
| C FFI           | `libc`             | unsafe + C 함수 호출           |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Rust std::fs: [doc.rust-lang.org/std/fs](https://doc.rust-lang.org/std/fs/) — ★★★☆☆
- Rust std::process: [doc.rust-lang.org/std/process](https://doc.rust-lang.org/std/process/) — ★★★☆☆
- nix crate: [docs.rs/nix](https://docs.rs/nix) — ★★★☆☆
- Command-Line Rust (O'Reilly): [oreilly.com](https://www.oreilly.com/library/view/command-line-rust/9781098109424/) — ★★★★☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-28

**마지막 업데이트**: 2026-07-28

© 2026 siasia86. Licensed under CC BY 4.0.

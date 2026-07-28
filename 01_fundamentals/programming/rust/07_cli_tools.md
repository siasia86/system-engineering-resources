# Rust CLI 도구 개발

clap을 사용한 인수 파싱, 바이너리 배포, 크로스 컴파일 방법을 정리합니다.

## 목차

| 섹션                                                                                                                            |
|---------------------------------------------------------------------------------------------------------------------------------|
| [1. 프로젝트 구조](#1-프로젝트-구조) / [2. clap (인수 파싱)](#2-clap-인수-파싱) / [3. 출력 (색상, 테이블)](#3-출력-색상-테이블) |
| [4. 설정 파일 로드](#4-설정-파일-로드) / [5. 로깅](#5-로깅) / [6. 빌드와 배포](#6-빌드와-배포)                                  |
| [7. 크로스 컴파일](#7-크로스-컴파일) / [8. SE 실전 예제](#8-se-실전-예제) / [9. 요약](#9-요약)                                  |

---

## 1. 프로젝트 구조

### Cargo 프로젝트 생성

```bash
cargo new my-tool
cd my-tool
```

### 권장 구조

```
my-tool/
├── Cargo.toml
├── src/
│   ├── main.rs        # 진입점, CLI 파싱
│   ├── lib.rs         # 핵심 로직 (테스트 용이)
│   ├── config.rs      # 설정 로드
│   └── output.rs      # 출력 포맷
├── tests/
│   └── integration.rs # 통합 테스트
└── README.md
```

### Cargo.toml 기본

```toml
[package]
name = "my-tool"
version = "0.1.0"
edition = "2021"
description = "서버 헬스체크 도구"

[dependencies]
clap = { version = "4", features = ["derive"] }
anyhow = "1"
serde = { version = "1", features = ["derive"] }
toml = "0.8"

[profile.release]
opt-level = 3
lto = true        # Link-Time Optimization
strip = true      # 디버그 심볼 제거 (바이너리 크기 감소)
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. clap (인수 파싱)

### derive 방식 (권장)

```rust
use clap::Parser;

#[derive(Parser, Debug)]
#[command(name = "srvcheck", version, about = "서버 헬스체크 도구")]
struct Args {
    /// 대상 호스트 (필수)
    #[arg(short, long)]
    host: String,

    /// 포트 (기본: 80)
    #[arg(short, long, default_value_t = 80)]
    port: u16,

    /// 타임아웃 (초)
    #[arg(short, long, default_value_t = 5)]
    timeout: u64,

    /// 상세 출력
    #[arg(short, long)]
    verbose: bool,

    /// 설정 파일 경로
    #[arg(short, long, default_value = "/etc/srvcheck.toml")]
    config: String,
}

fn main() {
    let args = Args::parse();
    println!("Checking {}:{} (timeout={}s)", args.host, args.port, args.timeout);
}
```

### 서브커맨드

```rust
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "infra", about = "인프라 관리 도구")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// 서버 상태 확인
    Check {
        #[arg(short, long)]
        host: String,
    },
    /// 서비스 재시작
    Restart {
        #[arg(short, long)]
        service: String,
        /// dry-run (실행 안 함)
        #[arg(short, long)]
        dry_run: bool,
    },
    /// 서버 목록 출력
    List {
        /// 출력 형식 (json, table)
        #[arg(short, long, default_value = "table")]
        format: String,
    },
}

fn main() {
    let cli = Cli::parse();
    match cli.command {
        Commands::Check { host } => check_server(&host),
        Commands::Restart { service, dry_run } => restart_service(&service, dry_run),
        Commands::List { format } => list_servers(&format),
    }
}
```

### 도움말 출력 예시

```
$ srvcheck --help
서버 헬스체크 도구

Usage: srvcheck [OPTIONS] --host <HOST>

Options:
  -h, --host <HOST>        대상 호스트 (필수)
  -p, --port <PORT>        포트 [default: 80]
  -t, --timeout <TIMEOUT>  타임아웃 (초) [default: 5]
  -v, --verbose            상세 출력
  -c, --config <CONFIG>    설정 파일 경로 [default: /etc/srvcheck.toml]
      --help               Print help
  -V, --version            Print version
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 출력 (색상, 테이블)

### colored 크레이트

```rust
use colored::*;

fn print_status(name: &str, healthy: bool, latency_ms: u128) {
    let status = if healthy {
        "OK".green().bold()
    } else {
        "FAIL".red().bold()
    };
    let latency = if latency_ms > 1000 {
        format!("{}ms", latency_ms).yellow()
    } else {
        format!("{}ms", latency_ms).normal()
    };
    println!("[{}] {} ({})", status, name, latency);
}
```

### 진행률 표시 (indicatif)

```rust
use indicatif::{ProgressBar, ProgressStyle};

fn scan_with_progress(hosts: &[&str]) {
    let pb = ProgressBar::new(hosts.len() as u64);
    pb.set_style(ProgressStyle::default_bar()
        .template("{bar:40.cyan/blue} {pos}/{len} {msg}")
        .unwrap());

    for host in hosts {
        pb.set_message(format!("Scanning {}", host));
        // 스캔 로직...
        pb.inc(1);
    }
    pb.finish_with_message("Complete");
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 설정 파일 로드

### TOML 설정

```toml
# /etc/srvcheck.toml
[general]
timeout = 10
retries = 3
log_level = "info"

[[servers]]
name = "web01"
host = "192.0.2.1"
port = 80

[[servers]]
name = "db01"
host = "192.0.2.2"
port = 3306
```

### serde + toml 파싱

```rust
use serde::Deserialize;
use std::fs;

#[derive(Deserialize, Debug)]
struct Config {
    general: General,
    servers: Vec<ServerConfig>,
}

#[derive(Deserialize, Debug)]
struct General {
    timeout: u64,
    retries: u32,
    log_level: String,
}

#[derive(Deserialize, Debug)]
struct ServerConfig {
    name: String,
    host: String,
    port: u16,
}

fn load_config(path: &str) -> anyhow::Result<Config> {
    let content = fs::read_to_string(path)?;
    let config: Config = toml::from_str(&content)?;
    Ok(config)
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 로깅

### env_logger (간단)

```rust
use log::{info, warn, error, debug};

fn main() {
    env_logger::init(); // RUST_LOG=info 환경변수로 레벨 제어

    info!("Starting server check");
    debug!("Config loaded from /etc/app.toml");
    warn!("Server web02 slow response: 2500ms");
    error!("Server db01 connection refused");
}
```

### tracing (구조적 로깅, 비동기 대응)

```rust
use tracing::{info, warn, instrument};
use tracing_subscriber;

#[instrument]
async fn check_server(host: &str, port: u16) -> bool {
    info!(host, port, "Checking server");
    // ...
    true
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();
    check_server("web01", 80).await;
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 빌드와 배포

### 릴리스 빌드

```bash
# 최적화 빌드
cargo build --release

# 바이너리 위치
ls -la target/release/my-tool

# 바이너리 크기 확인
du -h target/release/my-tool
```

### static 링크 (musl)

```bash
# musl 타겟 추가
rustup target add x86_64-unknown-linux-musl

# static 빌드 (glibc 의존 없음, 어떤 Linux에서도 실행)
cargo build --release --target x86_64-unknown-linux-musl

# 확인
file target/x86_64-unknown-linux-musl/release/my-tool
# statically linked
```

### 바이너리 크기 최적화

| 방법          | Cargo.toml 설정     | 효과        |
|---------------|---------------------|-------------|
| LTO           | `lto = true`        | 10~20% 감소 |
| Strip         | `strip = true`      | 30~50% 감소 |
| opt-level s   | `opt-level = "s"`   | 크기 최적화 |
| codegen-units | `codegen-units = 1` | 5~10% 감소  |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 크로스 컴파일

### cross 도구

```bash
# cross 설치
cargo install cross

# ARM64 (Raspberry Pi, AWS Graviton)
cross build --release --target aarch64-unknown-linux-musl

# x86_64 static
cross build --release --target x86_64-unknown-linux-musl
```

### 주요 타겟

| 타겟                         | 용도                   |
|------------------------------|------------------------|
| `x86_64-unknown-linux-musl`  | Linux x86_64 (static)  |
| `aarch64-unknown-linux-musl` | Linux ARM64 (Graviton) |
| `x86_64-unknown-linux-gnu`   | Linux x86_64 (dynamic) |
| `x86_64-pc-windows-msvc`     | Windows                |
| `x86_64-apple-darwin`        | macOS Intel            |
| `aarch64-apple-darwin`       | macOS Apple Silicon    |

[⬆ 목차로 돌아가기](#목차)

---

## 8. SE 실전 예제

### CLI 도구 전체 구조

```rust
use clap::Parser;
use anyhow::Result;

#[derive(Parser)]
#[command(name = "srvcheck", version, about = "서버 헬스체크")]
struct Args {
    #[arg(short, long)]
    config: Option<String>,

    #[arg(short, long)]
    verbose: bool,

    /// 대상 서버 (미지정 시 설정 파일 전체)
    servers: Vec<String>,
}

fn main() {
    if let Err(e) = run() {
        eprintln!("ERROR: {:#}", e);
        std::process::exit(1);
    }
}

fn run() -> Result<()> {
    let args = Args::parse();

    // 설정 로드
    let config_path = args.config.as_deref().unwrap_or("/etc/srvcheck.toml");
    let config = load_config(config_path)?;

    // 로깅 초기화
    if args.verbose {
        env_logger::Builder::new()
            .filter_level(log::LevelFilter::Debug)
            .init();
    } else {
        env_logger::init();
    }

    // 실행
    let results = check_all(&config, &args.servers)?;

    // 결과 출력
    print_results(&results);

    // 실패한 서버가 있으면 exit 1
    if results.iter().any(|r| !r.healthy) {
        std::process::exit(1);
    }
    Ok(())
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 요약

| 크레이트       | 용도          | 비고                      |
|----------------|---------------|---------------------------|
| `clap`         | CLI 인수 파싱 | derive 방식 권장          |
| `serde`/`toml` | 설정 파일     | TOML/YAML/JSON 지원       |
| `colored`      | 터미널 색상   | stdout.isatty() 자동 감지 |
| `indicatif`    | 진행률 바     | 대량 작업 시              |
| `env_logger`   | 간단한 로깅   | RUST_LOG 환경변수         |
| `tracing`      | 구조적 로깅   | async 대응, span 추적     |
| `cross`        | 크로스 컴파일 | Docker 기반               |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- clap docs: [docs.rs/clap](https://docs.rs/clap) — ★★★★☆
- Command-Line Rust (O'Reilly): [oreilly.com](https://www.oreilly.com/library/view/command-line-rust/9781098109424/) — ★★★★☆
- cross: [github.com/cross-rs/cross](https://github.com/cross-rs/cross) — ★★★☆☆
- min-sized-rust: [github.com/nicholasf/min-sized-rust](https://github.com/nicholasf/min-sized-rust) — ★★☆☆☆

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

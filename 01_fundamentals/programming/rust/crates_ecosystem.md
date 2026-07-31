# Rust 크레이트 생태계

SE 실무에서 자주 사용하는 핵심 크레이트와 Cargo 활용법을 정리합니다.

## 목차

| 섹션                                                                                                                   |
|------------------------------------------------------------------------------------------------------------------------|
| [1. Cargo 기본](#1-cargo-기본) / [2. 핵심 크레이트 목록](#2-핵심-크레이트-목록) / [3. serde (직렬화)](#3-serde-직렬화) |
| [4. regex](#4-regex) / [5. chrono (시간)](#5-chrono-시간) / [6. tokio 생태계](#6-tokio-생태계)                         |
| [7. Cargo 고급](#7-cargo-고급) / [8. 요약](#8-요약)                                                                    |

---

## 1. Cargo 기본

### 주요 명령어

| 명령어             | 용도                      |
|--------------------|---------------------------|
| `cargo new <name>` | 프로젝트 생성             |
| `cargo build`      | 빌드 (debug)              |
| `cargo build -r`   | 릴리스 빌드               |
| `cargo run`        | 빌드 + 실행               |
| `cargo test`       | 테스트 실행               |
| `cargo clippy`     | 린트 (코드 품질 검사)     |
| `cargo fmt`        | 코드 포맷팅               |
| `cargo doc --open` | 문서 생성 + 브라우저 열기 |
| `cargo update`     | 의존성 업데이트           |
| `cargo audit`      | 보안 취약점 검사          |
| `cargo tree`       | 의존성 트리 출력          |

### Cargo.toml 구조

```toml
[package]
name = "my-tool"
version = "0.1.0"
edition = "2021"
rust-version = "1.70"

[dependencies]
tokio = { version = "1.40", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
anyhow = "1.0"

[dev-dependencies]
assert_cmd = "2.0"
tempfile = "3.0"

[profile.release]
opt-level = 3
lto = true
strip = true
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 핵심 크레이트 목록

### SE 필수 크레이트

| 크레이트    | 용도                   | 비고               |
|-------------|------------------------|--------------------|
| `tokio`     | 비동기 런타임          | 네트워크, 타이머   |
| `serde`     | 직렬화/역직렬화        | JSON, TOML, YAML   |
| `reqwest`   | HTTP 클라이언트        | async, TLS 내장    |
| `clap`      | CLI 인수 파싱          | derive 방식        |
| `anyhow`    | 에러 처리 (앱)         | 간편한 에러 전파   |
| `thiserror` | 에러 처리 (라이브러리) | 커스텀 에러 derive |
| `regex`     | 정규 표현식            | 로그 파싱          |
| `chrono`    | 날짜/시간              | 타임존, 포맷       |
| `tracing`   | 구조적 로깅            | async 대응         |
| `toml`      | TOML 파서              | 설정 파일          |

### 시스템/인프라 크레이트

| 크레이트            | 용도                  | 비고                  |
|---------------------|-----------------------|-----------------------|
| `nix`               | POSIX 시스템 콜       | 안전한 libc 래퍼      |
| `signal-hook`       | 시그널 처리           | SIGTERM, SIGINT       |
| `walkdir`           | 디렉토리 재귀 순회    | 빠르고 간결           |
| `notify`            | 파일시스템 변경 감시  | inotify 래퍼          |
| `sysinfo`           | 시스템 정보 수집      | CPU, 메모리, 프로세스 |
| `bollard`           | Docker API 클라이언트 | 컨테이너 관리         |
| `russh`             | SSH 클라이언트        | 원격 명령 실행        |
| `prometheus-client` | Prometheus 메트릭     | exporter 개발         |

[⬆ 목차로 돌아가기](#목차)

---

## 3. serde (직렬화)

### JSON 파싱

```rust
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
struct ServerInfo {
    hostname: String,
    ip: String,
    port: u16,
    #[serde(default)]
    tags: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    description: Option<String>,
}

// JSON → struct
let json = r#"{"hostname":"web01","ip":"10.0.0.1","port":80}"#;
let server: ServerInfo = serde_json::from_str(json)?;

// struct → JSON
let output = serde_json::to_string_pretty(&server)?;
```

### TOML 파싱

```rust
use serde::Deserialize;

#[derive(Deserialize)]
struct Config {
    server: ServerSection,
    database: DbSection,
}

#[derive(Deserialize)]
struct ServerSection {
    host: String,
    port: u16,
    workers: usize,
}

#[derive(Deserialize)]
struct DbSection {
    url: String,
    max_connections: u32,
}

let content = std::fs::read_to_string("config.toml")?;
let config: Config = toml::from_str(&content)?;
```

### 커스텀 직렬화

```rust
use serde::{Deserialize, Deserializer};

#[derive(Deserialize)]
struct Threshold {
    #[serde(deserialize_with = "parse_size")]
    max_size: u64, // "10GB" → 10737418240
}

fn parse_size<'de, D>(deserializer: D) -> Result<u64, D::Error>
where D: Deserializer<'de> {
    let s: String = Deserialize::deserialize(deserializer)?;
    // "10GB", "512MB" 등 파싱 로직
    Ok(0) // 간략화
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. regex

```rust
use regex::Regex;

// 로그 파싱 예시
fn parse_nginx_log(line: &str) -> Option<(String, u16, String)> {
    let re = Regex::new(
        r#"(\d+\.\d+\.\d+\.\d+) .+ \[.+\] "(\w+) (.+?) HTTP"#
    ).unwrap();

    re.captures(line).map(|caps| {
        (
            caps[1].to_string(), // IP
            caps[2].parse().unwrap_or(0), // method → 간략화
            caps[3].to_string(), // path
        )
    })
}

// 컴파일 한 번만 (모듈 레벨 또는 lazy_static)
use std::sync::LazyLock;

static LOG_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (.+)").unwrap()
});

fn parse_log_line(line: &str) -> Option<(&str, &str, &str)> {
    LOG_RE.captures(line).map(|caps| {
        (caps.get(1).unwrap().as_str(),
         caps.get(2).unwrap().as_str(),
         caps.get(3).unwrap().as_str())
    })
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. chrono (시간)

```rust
use chrono::{Local, Utc, Duration, NaiveDateTime};

// 현재 시각
let now = Local::now();
println!("{}", now.format("%Y-%m-%d %H:%M:%S"));

// UTC
let utc = Utc::now();
println!("{}", utc.to_rfc3339());

// 시간 계산
let yesterday = now - Duration::days(1);
let next_hour = now + Duration::hours(1);

// 문자열 파싱
let dt = NaiveDateTime::parse_from_str(
    "2026-07-28 14:30:00",
    "%Y-%m-%d %H:%M:%S"
)?;

// 로그 타임스탬프 포맷
fn log_timestamp() -> String {
    Local::now().format("%Y-%m-%d %H:%M:%S").to_string()
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. tokio 생태계

| 크레이트         | 용도                    |
|------------------|-------------------------|
| `tokio`          | 비동기 런타임 (코어)    |
| `tokio::fs`      | 비동기 파일 I/O         |
| `tokio::net`     | 비동기 TCP/UDP          |
| `tokio::sync`    | 비동기 채널, Mutex      |
| `tokio::time`    | 타이머, interval, sleep |
| `tokio::signal`  | 비동기 시그널 처리      |
| `tokio::process` | 비동기 프로세스 실행    |
| `tokio-util`     | 코덱, 프레임            |
| `hyper`          | HTTP (low-level)        |
| `axum`           | HTTP 서버 (high-level)  |
| `tonic`          | gRPC                    |

[⬆ 목차로 돌아가기](#목차)

---

## 7. Cargo 고급

### workspace (모노레포)

```toml
# 최상위 Cargo.toml
[workspace]
members = [
    "crates/core",
    "crates/cli",
    "crates/agent",
]

[workspace.dependencies]
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
```

### features (조건부 컴파일)

```toml
[features]
default = ["json"]
json = ["serde_json"]
yaml = ["serde_yaml"]
full = ["json", "yaml", "toml"]
```

```rust
#[cfg(feature = "json")]
pub fn to_json<T: Serialize>(data: &T) -> String {
    serde_json::to_string(data).unwrap()
}
```

### cargo-audit (보안 검사)

```bash
cargo install cargo-audit
cargo audit

# CI에서 사용
cargo audit --deny warnings
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 요약

| 분류      | 크레이트                              | 한 줄 설명              |
|-----------|---------------------------------------|-------------------------|
| 비동기    | `tokio`                               | 비동기 런타임 표준      |
| 직렬화    | `serde` + `serde_json`/`toml`         | 타입 안전 파싱          |
| HTTP      | `reqwest` (클라이언트), `axum` (서버) | 비동기 HTTP             |
| CLI       | `clap`                                | derive 기반 인수 파싱   |
| 에러      | `anyhow` + `thiserror`                | 앱/라이브러리 에러 처리 |
| 로깅      | `tracing` / `env_logger`              | 구조적/간단 로깅        |
| 정규식    | `regex`                               | 로그 파싱               |
| 시간      | `chrono`                              | 포맷, 파싱, 계산        |
| 시스템    | `nix`, `sysinfo`                      | POSIX, 시스템 정보      |
| 파일 감시 | `notify`                              | inotify 래퍼            |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- crates.io: [crates.io](https://crates.io/) — ★★★☆☆
- lib.rs (크레이트 검색): [lib.rs](https://lib.rs/) — ★★★☆☆
- Awesome Rust: [github.com/rust-unofficial/awesome-rust](https://github.com/rust-unofficial/awesome-rust) — ★★☆☆☆
- Cargo Book: [doc.rust-lang.org/cargo](https://doc.rust-lang.org/cargo/) — ★★★★☆

---

## 통계


## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-28

**마지막 업데이트**: 2026-07-31

© 2026 siasia86. Licensed under CC BY 4.0.

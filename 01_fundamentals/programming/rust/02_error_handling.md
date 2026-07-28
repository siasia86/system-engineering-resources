# Rust 에러 처리

Rust의 에러 처리 방식인 Result, Option, ? 연산자, 커스텀 에러 타입을 정리합니다.

## 목차

| 섹션                                                                                                          |
|---------------------------------------------------------------------------------------------------------------|
| [1. 에러 처리 철학](#1-에러-처리-철학) / [2. Option 타입](#2-option-타입) / [3. Result 타입](#3-result-타입)  |
| [4. ? 연산자](#4--연산자) / [5. 커스텀 에러](#5-커스텀-에러) / [6. anyhow와 thiserror](#6-anyhow와-thiserror) |
| [7. panic vs Result](#7-panic-vs-result) / [8. SE 실전 패턴](#8-se-실전-패턴) / [9. 요약](#9-요약)            |

---

## 1. 에러 처리 철학

### 다른 언어와 비교

| 언어   | 에러 처리 방식           | 문제점                            |
|--------|--------------------------|-----------------------------------|
| C      | 반환값 (-1, NULL)        | 무시 가능, 타입 안전 없음         |
| Java   | try/catch 예외           | 런타임 비용, 어디서 발생할지 불명 |
| Go     | (value, error) 튜플      | if err != nil 반복, 무시 가능     |
| Python | try/except 예외          | 런타임 비용, 타입 불명확          |
| Rust   | Result<T, E> / Option<T> | 컴파일 타임 강제, 무시 불가       |

Rust는 에러를 **타입 시스템**으로 표현합니다. 에러를 처리하지 않으면 컴파일이 되지 않습니다.

### 두 가지 에러 카테고리

| 카테고리           | 타입     | 용도                    | 예시                     |
|--------------------|----------|-------------------------|--------------------------|
| 복구 가능한 에러   | `Result` | 정상 흐름에서 실패 가능 | 파일 열기, 네트워크 연결 |
| 복구 불가능한 에러 | `panic!` | 프로그래밍 버그         | 인덱스 초과, 논리 에러   |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Option 타입

값이 있을 수도, 없을 수도 있는 경우입니다. 다른 언어의 `null`/`None`을 안전하게 대체합니다.

### 정의

```rust
enum Option<T> {
    Some(T), // 값이 있음
    None,    // 값이 없음
}
```

### 기본 사용법

```rust
fn find_server(servers: &[&str], name: &str) -> Option<&str> {
    servers.iter().find(|&&s| s == name).copied()
}

fn main() {
    let servers = vec!["web01", "db01", "cache01"];

    // match로 처리
    match find_server(&servers, "db01") {
        Some(s) => println!("Found: {}", s),
        None => println!("Not found"),
    }

    // if let으로 간결하게
    if let Some(s) = find_server(&servers, "web01") {
        println!("Server: {}", s);
    }
}
```

### 주요 메서드

| 메서드                    | 동작                              | 사용 시나리오          |
|---------------------------|-----------------------------------|------------------------|
| `unwrap()`                | Some → 값 반환, None → panic      | 테스트/프로토타입만    |
| `unwrap_or(default)`      | Some → 값, None → 기본값          | 기본값이 있을 때       |
| `unwrap_or_else(f)`       | Some → 값, None → 클로저 실행     | 기본값 계산 비용 클 때 |
| `expect("msg")`           | unwrap + 에러 메시지              | 디버깅용               |
| `map(f)`                  | Some(x) → Some(f(x)), None → None | 값 변환                |
| `and_then(f)`             | Some(x) → f(x), None → None       | 체이닝 (flatmap)       |
| `is_some()` / `is_none()` | bool 반환                         | 조건 분기              |
| `ok_or(err)`              | Option → Result 변환              | Result 체인에 합류     |

### 실전 예시

```rust
use std::env;

fn get_port() -> u16 {
    env::var("PORT")
        .ok()                          // Result → Option
        .and_then(|s| s.parse().ok())  // String → Option<u16>
        .unwrap_or(8080)               // 없으면 기본 8080
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. Result 타입

성공 또는 실패를 표현합니다. Rust에서 가장 많이 사용하는 에러 처리 방식입니다.

### 정의

```rust
enum Result<T, E> {
    Ok(T),  // 성공: 값 T
    Err(E), // 실패: 에러 E
}
```

### 기본 사용법

```rust
use std::fs;
use std::io;

fn read_config(path: &str) -> Result<String, io::Error> {
    fs::read_to_string(path)
}

fn main() {
    match read_config("/etc/app.conf") {
        Ok(content) => println!("Config: {}", content),
        Err(e) => eprintln!("Error: {}", e),
    }
}
```

### 주요 메서드

| 메서드                 | 동작                        | 사용 시나리오         |
|------------------------|-----------------------------|-----------------------|
| `unwrap()`             | Ok → 값, Err → panic        | 절대 실패하지 않을 때 |
| `expect("msg")`        | unwrap + 메시지             | 실패하면 안 되는 곳   |
| `unwrap_or(default)`   | Ok → 값, Err → 기본값       | 폴백 값이 있을 때     |
| `map(f)`               | Ok(x) → Ok(f(x))            | 성공 값 변환          |
| `map_err(f)`           | Err(e) → Err(f(e))          | 에러 타입 변환        |
| `and_then(f)`          | Ok(x) → f(x)                | 연속 연산 체이닝      |
| `or_else(f)`           | Err(e) → f(e)               | 실패 시 대안 시도     |
| `is_ok()` / `is_err()` | bool                        | 조건 분기             |
| `ok()`                 | Result → Option (에러 버림) | 에러 무시할 때        |

### 체이닝 패턴

```rust
fn parse_timeout(config: &str) -> Result<u64, String> {
    config
        .lines()
        .find(|l| l.starts_with("timeout="))
        .ok_or("timeout key not found".to_string())?
        .strip_prefix("timeout=")
        .ok_or("invalid format".to_string())?
        .trim()
        .parse::<u64>()
        .map_err(|e| format!("parse error: {}", e))
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. ? 연산자

에러를 호출자에게 전파하는 간결한 문법입니다. `match`를 대체합니다.

### 동작 원리

```rust
// ? 연산자 사용
fn read_file(path: &str) -> Result<String, io::Error> {
    let content = fs::read_to_string(path)?; // 실패 시 즉시 Err 반환
    Ok(content)
}

// ? 없이 동일한 코드
fn read_file_verbose(path: &str) -> Result<String, io::Error> {
    let content = match fs::read_to_string(path) {
        Ok(c) => c,
        Err(e) => return Err(e), // 명시적 반환
    };
    Ok(content)
}
```

### 여러 연산 체이닝

```rust
use std::fs;
use std::io;
use std::net::TcpStream;

fn connect_from_config(path: &str) -> Result<TcpStream, io::Error> {
    let config = fs::read_to_string(path)?;          // 파일 읽기 실패 시 반환
    let addr = config.trim();
    let stream = TcpStream::connect(addr)?;          // 연결 실패 시 반환
    Ok(stream)
}
```

### ? 사용 조건

| 조건                      | 설명                                    |
|---------------------------|-----------------------------------------|
| 함수 반환 타입이 `Result` | `?`가 `Err`를 반환할 수 있어야 함       |
| 에러 타입 호환            | `From` 트레이트로 자동 변환 가능해야 함 |
| `main()`에서도 사용 가능  | `fn main() -> Result<(), E>` 형태       |

### main()에서 ? 사용

```rust
use std::fs;
use std::io;

fn main() -> Result<(), io::Error> {
    let config = fs::read_to_string("/etc/app.conf")?;
    println!("Config loaded: {} bytes", config.len());
    Ok(())
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 커스텀 에러

### 수동 정의

```rust
use std::fmt;
use std::io;
use std::num::ParseIntError;

#[derive(Debug)]
enum AppError {
    Io(io::Error),
    Parse(ParseIntError),
    Config(String),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AppError::Io(e) => write!(f, "I/O error: {}", e),
            AppError::Parse(e) => write!(f, "Parse error: {}", e),
            AppError::Config(msg) => write!(f, "Config error: {}", msg),
        }
    }
}

impl std::error::Error for AppError {}

// From 구현으로 ? 연산자에서 자동 변환
impl From<io::Error> for AppError {
    fn from(e: io::Error) -> Self {
        AppError::Io(e)
    }
}

impl From<ParseIntError> for AppError {
    fn from(e: ParseIntError) -> Self {
        AppError::Parse(e)
    }
}
```

### 사용

```rust
fn load_config(path: &str) -> Result<u16, AppError> {
    let content = fs::read_to_string(path)?;  // io::Error → AppError::Io 자동 변환
    let port: u16 = content.trim().parse()?;  // ParseIntError → AppError::Parse
    if port == 0 {
        return Err(AppError::Config("port cannot be 0".to_string()));
    }
    Ok(port)
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. anyhow와 thiserror

수동으로 에러 타입을 정의하는 것은 번거롭습니다. 두 크레이트가 이를 해결합니다.

### thiserror — 라이브러리용 (구체적 에러 타입)

```rust
use thiserror::Error;

#[derive(Error, Debug)]
enum ConfigError {
    #[error("file not found: {path}")]
    NotFound { path: String },

    #[error("parse error at line {line}: {message}")]
    ParseError { line: usize, message: String },

    #[error("I/O error")]
    Io(#[from] std::io::Error),

    #[error("invalid port: {0}")]
    InvalidPort(#[from] std::num::ParseIntError),
}
```

### anyhow — 애플리케이션용 (간편한 에러 전파)

```rust
use anyhow::{Context, Result};
use std::fs;

fn load_server_list(path: &str) -> Result<Vec<String>> {
    let content = fs::read_to_string(path)
        .with_context(|| format!("Failed to read {}", path))?;

    let servers: Vec<String> = content
        .lines()
        .filter(|l| !l.is_empty() && !l.starts_with('#'))
        .map(String::from)
        .collect();

    if servers.is_empty() {
        anyhow::bail!("No servers found in {}", path);
    }

    Ok(servers)
}

fn main() -> Result<()> {
    let servers = load_server_list("/etc/servers.conf")?;
    println!("Loaded {} servers", servers.len());
    Ok(())
}
```

### 선택 기준

| 상황             | 선택        | 이유                                        |
|------------------|-------------|---------------------------------------------|
| 라이브러리 개발  | `thiserror` | 사용자가 에러 종류를 구분해야 함            |
| 애플리케이션/CLI | `anyhow`    | 간편하게 에러 전파 + 컨텍스트               |
| 두 개 조합       | 둘 다       | 라이브러리 내부 thiserror + main에서 anyhow |

[⬆ 목차로 돌아가기](#목차)

---

## 7. panic vs Result

### panic!

프로그램을 즉시 중단합니다. 복구 불가능한 버그에만 사용합니다.

```rust
// 명시적 panic
panic!("critical error: database corrupted");

// 암시적 panic (인덱스 초과)
let v = vec![1, 2, 3];
let x = v[10]; // panic: index out of bounds
```

### 사용 기준

| 상황                       | 선택     | 이유                          |
|----------------------------|----------|-------------------------------|
| 파일 열기 실패             | `Result` | 복구 가능 (다른 경로 시도 등) |
| 네트워크 연결 실패         | `Result` | 재시도 가능                   |
| 설정 파일 문법 오류        | `Result` | 사용자에게 알림 후 종료       |
| 배열 인덱스가 범위 밖      | `panic`  | 프로그래밍 버그               |
| 절대 발생하면 안 되는 상태 | `panic`  | 불변 조건 위반                |
| 프로토타입 / 빠른 테스트   | `unwrap` | 나중에 proper error handling  |

### unwrap/expect 허용 범위

```rust
// ✅ OK: 프로그램 시작 시 필수 설정 로드
let config = fs::read_to_string("/etc/critical.conf")
    .expect("FATAL: critical.conf must exist");

// ✅ OK: 정규식 컴파일 (컴파일 타임에 확인 가능)
let re = Regex::new(r"^\d{4}-\d{2}-\d{2}$").unwrap();

// ❌ BAD: 사용자 입력 파싱
let port: u16 = user_input.parse().unwrap(); // 사용자가 잘못 입력하면 panic
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. SE 실전 패턴

### 패턴 1: 설정 파일 로드 (여러 에러 타입)

```rust
use anyhow::{Context, Result};
use std::collections::HashMap;
use std::fs;

fn load_config(path: &str) -> Result<HashMap<String, String>> {
    let content = fs::read_to_string(path)
        .with_context(|| format!("Cannot read config: {}", path))?;

    let mut config = HashMap::new();
    for (i, line) in content.lines().enumerate() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let (key, value) = line.split_once('=')
            .with_context(|| format!("Invalid syntax at line {}: {}", i + 1, line))?;
        config.insert(key.trim().to_string(), value.trim().to_string());
    }
    Ok(config)
}
```

### 패턴 2: 서비스 헬스체크 (재시도 포함)

```rust
use anyhow::{bail, Result};
use std::net::TcpStream;
use std::thread;
use std::time::Duration;

fn health_check(addr: &str, retries: u32) -> Result<()> {
    for attempt in 1..=retries {
        match TcpStream::connect_timeout(
            &addr.parse()?,
            Duration::from_secs(5),
        ) {
            Ok(_) => return Ok(()),
            Err(e) if attempt < retries => {
                eprintln!("Attempt {}/{} failed: {}", attempt, retries, e);
                thread::sleep(Duration::from_secs(2));
            }
            Err(e) => bail!("Health check failed after {} attempts: {}", retries, e),
        }
    }
    unreachable!()
}
```

### 패턴 3: 다중 파일 처리 (에러 수집)

```rust
use std::fs;
use std::path::Path;

fn process_logs(dir: &str) -> Vec<(String, String)> {
    let mut errors = Vec::new();

    let entries = match fs::read_dir(dir) {
        Ok(e) => e,
        Err(e) => {
            errors.push((dir.to_string(), e.to_string()));
            return errors;
        }
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if path.extension().map_or(false, |ext| ext == "log") {
            if let Err(e) = process_single_log(&path) {
                errors.push((path.display().to_string(), e.to_string()));
            }
        }
    }
    errors
}

fn process_single_log(path: &Path) -> Result<(), std::io::Error> {
    let content = fs::read_to_string(path)?;
    // 처리 로직...
    println!("Processed: {} ({} lines)", path.display(), content.lines().count());
    Ok(())
}
```

### 패턴 4: graceful shutdown with Result

```rust
use anyhow::Result;
use std::process;

fn run() -> Result<()> {
    let config = load_config("/etc/app.conf")?;
    let server = start_server(&config)?;
    server.wait_for_shutdown()?;
    Ok(())
}

fn main() {
    if let Err(e) = run() {
        eprintln!("ERROR: {:#}", e); // {:#}는 에러 체인 전체 출력
        process::exit(1);
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 요약

| 항목        | 용도                   | 예시                                |
|-------------|------------------------|-------------------------------------|
| `Option`    | 값이 없을 수 있음      | `HashMap::get()`, `find()`          |
| `Result`    | 성공/실패 표현         | `fs::read_to_string()`, `parse()`   |
| `?`         | 에러 전파 (간결)       | `let x = fallible_fn()?;`           |
| `unwrap`    | 절대 실패 않을 때      | `Regex::new(r"...")` (정적 패턴)    |
| `expect`    | 실패하면 안 되는 곳    | 프로그램 시작 시 필수 리소스        |
| `anyhow`    | 애플리케이션 에러 전파 | CLI 도구, 에이전트                  |
| `thiserror` | 라이브러리 에러 정의   | 재사용 가능한 크레이트              |
| `panic!`    | 프로그래밍 버그        | 불변 조건 위반, 절대 도달 불가 코드 |

### 에러 처리 흐름도

```
함수에서 에러 발생 가능?
  │
  ├── 아니오 → 그냥 반환
  │
  └── 예 → Result<T, E> 반환
            │
            ├── 호출자가 처리? → match / if let
            │
            ├── 상위로 전파? → ? 연산자
            │
            └── 절대 실패 불가? → unwrap/expect
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- The Rust Programming Language Ch.9: [doc.rust-lang.org/book/ch09-00-error-handling.html](https://doc.rust-lang.org/book/ch09-00-error-handling.html) — ★★★★☆
- anyhow 크레이트: [docs.rs/anyhow](https://docs.rs/anyhow) — ★★★☆☆
- thiserror 크레이트: [docs.rs/thiserror](https://docs.rs/thiserror) — ★★★☆☆
- Error Handling in Rust (blog): [nick.groenen.me](https://nick.groenen.me/posts/rust-error-handling/) — ★★☆☆☆

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

# Rust 테스트

단위 테스트, 통합 테스트, 모킹, 벤치마크를 정리합니다.

## 목차

| 섹션                                                                                                   |
|--------------------------------------------------------------------------------------------------------|
| [1. 테스트 기본](#1-테스트-기본) / [2. 단위 테스트](#2-단위-테스트) / [3. 통합 테스트](#3-통합-테스트) |
| [4. 테스트 헬퍼](#4-테스트-헬퍼) / [5. 모킹](#5-모킹) / [6. CLI 테스트](#6-cli-테스트)                 |
| [7. 비동기 테스트](#7-비동기-테스트) / [8. 요약](#8-요약)                                              |

---

## 1. 테스트 기본

### 실행 명령어

| 명령어                           | 용도               |
|----------------------------------|--------------------|
| `cargo test`                     | 전체 테스트 실행   |
| `cargo test <name>`              | 이름 매칭 테스트만 |
| `cargo test -- --nocapture`      | stdout 출력 표시   |
| `cargo test -- --test-threads=1` | 직렬 실행          |
| `cargo test --lib`               | 단위 테스트만      |
| `cargo test --test <name>`       | 특정 통합 테스트만 |

### 기본 구조

```rust
// src/lib.rs 또는 모듈 파일 하단
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic() {
        assert_eq!(2 + 2, 4);
    }

    #[test]
    fn test_with_result() -> Result<(), String> {
        if 2 + 2 == 4 {
            Ok(())
        } else {
            Err("math is broken".to_string())
        }
    }

    #[test]
    #[should_panic(expected = "division by zero")]
    fn test_panic() {
        divide(10, 0);
    }

    #[test]
    #[ignore] // 느린 테스트, cargo test -- --ignored로 실행
    fn test_slow_integration() {
        // ...
    }
}
```

### 주요 assert 매크로

| 매크로                       | 용도                    |
|------------------------------|-------------------------|
| `assert!(expr)`              | expr이 true인지 확인    |
| `assert_eq!(a, b)`           | a == b 확인 (diff 출력) |
| `assert_ne!(a, b)`           | a != b 확인             |
| `assert!(expr, "msg {}", v)` | 실패 시 메시지          |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 단위 테스트

### 파일 구조

```rust
// src/config.rs
pub fn parse_port(s: &str) -> Result<u16, String> {
    let port: u16 = s.parse()
        .map_err(|_| format!("invalid port: {}", s))?;
    if port == 0 {
        return Err("port cannot be 0".to_string());
    }
    Ok(port)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn valid_port() {
        assert_eq!(parse_port("8080"), Ok(8080));
        assert_eq!(parse_port("443"), Ok(443));
    }

    #[test]
    fn invalid_port_string() {
        assert!(parse_port("abc").is_err());
    }

    #[test]
    fn port_zero_rejected() {
        let result = parse_port("0");
        assert_eq!(result, Err("port cannot be 0".to_string()));
    }

    #[test]
    fn port_overflow() {
        assert!(parse_port("99999").is_err());
    }
}
```

### 경계값 테스트 (BVA)

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn port_boundary_values() {
        // 유효 경계
        assert_eq!(parse_port("1"), Ok(1));       // 최소 유효값
        assert_eq!(parse_port("65535"), Ok(65535)); // 최대 유효값

        // 무효 경계
        assert!(parse_port("0").is_err());          // 최소 미만
        assert!(parse_port("65536").is_err());      // 최대 초과
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 통합 테스트

### 파일 구조

```
my-tool/
├── src/
│   ├── main.rs
│   └── lib.rs
└── tests/
    ├── health_check.rs    # 각 파일이 별도 바이너리
    └── config_test.rs
```

### 통합 테스트 예시

```rust
// tests/config_test.rs
use my_tool::config::load_config;
use tempfile::NamedTempFile;
use std::io::Write;

#[test]
fn load_valid_config() {
    let mut file = NamedTempFile::new().unwrap();
    writeln!(file, "port = 8080").unwrap();
    writeln!(file, "host = \"0.0.0.0\"").unwrap();

    let config = load_config(file.path().to_str().unwrap()).unwrap();
    assert_eq!(config.port, 8080);
    assert_eq!(config.host, "0.0.0.0");
}

#[test]
fn load_missing_file_returns_error() {
    let result = load_config("/nonexistent/path.toml");
    assert!(result.is_err());
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 테스트 헬퍼

### tempfile (임시 파일/디렉토리)

```rust
use tempfile::{tempdir, NamedTempFile};
use std::fs;

#[test]
fn test_log_rotation() {
    let dir = tempdir().unwrap();
    let log_path = dir.path().join("app.log");

    fs::write(&log_path, "line1\nline2\n").unwrap();
    rotate_log(log_path.to_str().unwrap(), 3).unwrap();

    assert!(!log_path.exists() || fs::read_to_string(&log_path).unwrap().is_empty());
    assert!(dir.path().join("app.log.1").exists());
}
```

### 테스트 픽스처 패턴

```rust
struct TestServer {
    addr: String,
    // handle for cleanup
}

impl TestServer {
    fn new() -> Self {
        // 테스트 서버 시작
        TestServer { addr: "127.0.0.1:0".to_string() }
    }
}

impl Drop for TestServer {
    fn drop(&mut self) {
        // 자동 정리
    }
}

#[test]
fn test_with_server() {
    let server = TestServer::new();
    // 테스트 로직...
} // server.drop() 자동 호출
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 모킹

### trait 기반 모킹 (수동)

```rust
trait HttpClient {
    fn get(&self, url: &str) -> Result<String, String>;
}

// 실제 구현
struct RealClient;
impl HttpClient for RealClient {
    fn get(&self, url: &str) -> Result<String, String> {
        // reqwest 호출...
        Ok("real response".to_string())
    }
}

// 테스트용 목
struct MockClient {
    response: Result<String, String>,
}
impl HttpClient for MockClient {
    fn get(&self, _url: &str) -> Result<String, String> {
        self.response.clone()
    }
}

// 비즈니스 로직 (제네릭으로 클라이언트 주입)
fn check_health(client: &dyn HttpClient, url: &str) -> bool {
    client.get(url).is_ok()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn healthy_when_200() {
        let mock = MockClient { response: Ok("OK".to_string()) };
        assert!(check_health(&mock, "http://example.com"));
    }

    #[test]
    fn unhealthy_when_error() {
        let mock = MockClient { response: Err("timeout".to_string()) };
        assert!(!check_health(&mock, "http://example.com"));
    }
}
```

### mockall 크레이트

```rust
use mockall::automock;

#[automock]
trait Database {
    fn get_server_count(&self) -> u32;
    fn is_connected(&self) -> bool;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_with_mock_db() {
        let mut mock = MockDatabase::new();
        mock.expect_get_server_count().returning(|| 5);
        mock.expect_is_connected().returning(|| true);

        assert_eq!(mock.get_server_count(), 5);
        assert!(mock.is_connected());
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. CLI 테스트

### assert_cmd 크레이트

```rust
// tests/cli_test.rs
use assert_cmd::Command;

#[test]
fn test_help_flag() {
    Command::cargo_bin("my-tool")
        .unwrap()
        .arg("--help")
        .assert()
        .success()
        .stdout(predicates::str::contains("Usage"));
}

#[test]
fn test_invalid_args() {
    Command::cargo_bin("my-tool")
        .unwrap()
        .arg("--invalid-flag")
        .assert()
        .failure();
}

#[test]
fn test_version() {
    Command::cargo_bin("my-tool")
        .unwrap()
        .arg("--version")
        .assert()
        .success()
        .stdout(predicates::str::contains(env!("CARGO_PKG_VERSION")));
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 비동기 테스트

### tokio::test

```rust
#[tokio::test]
async fn test_async_health_check() {
    let result = check_server("127.0.0.1:80").await;
    // 로컬에서 실행 시 포트에 따라 결과 다름
    assert!(result.is_ok() || result.is_err());
}

#[tokio::test]
async fn test_timeout() {
    use tokio::time::{timeout, Duration};

    let result = timeout(
        Duration::from_millis(100),
        tokio::time::sleep(Duration::from_secs(10)),
    ).await;

    assert!(result.is_err()); // timeout 발생
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 요약

| 테스트 유형 | 위치            | 실행 명령           | 용도           |
|-------------|-----------------|---------------------|----------------|
| 단위 테스트 | `src/*.rs` 내부 | `cargo test --lib`  | 함수/모듈 단위 |
| 통합 테스트 | `tests/*.rs`    | `cargo test --test` | 모듈 간 연동   |
| 문서 테스트 | `///` 주석 코드 | `cargo test --doc`  | 문서 예제 검증 |
| CLI 테스트  | `tests/`        | `cargo test`        | 바이너리 동작  |
| 벤치마크    | `benches/*.rs`  | `cargo bench`       | 성능 측정      |

### 테스트 작성 원칙

| 원칙                      | 설명                     |
|---------------------------|--------------------------|
| AAA 패턴                  | Arrange → Act → Assert   |
| 하나의 테스트 하나의 검증 | assert 하나에 집중       |
| 경계값 테스트             | 최소/최대/경계 근처      |
| 에러 경로 테스트          | 실패 시나리오 필수 커버  |
| 독립성                    | 테스트 간 상태 공유 금지 |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- The Rust Programming Language Ch.11: [doc.rust-lang.org/book/ch11-00-testing.html](https://doc.rust-lang.org/book/ch11-00-testing.html) — ★★★★☆
- assert_cmd: [docs.rs/assert_cmd](https://docs.rs/assert_cmd) — ★★★☆☆
- mockall: [docs.rs/mockall](https://docs.rs/mockall) — ★★★☆☆

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

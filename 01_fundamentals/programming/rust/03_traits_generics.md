# Rust 트레이트와 제네릭

Rust의 다형성을 구현하는 트레이트(Trait)와 제네릭(Generic)을 정리합니다.

## 목차

| 섹션                                                                                                                         |
|------------------------------------------------------------------------------------------------------------------------------|
| [1. 트레이트 기초](#1-트레이트-기초) / [2. 트레이트 구현](#2-트레이트-구현) / [3. 주요 표준 트레이트](#3-주요-표준-트레이트) |
| [4. 제네릭](#4-제네릭) / [5. 트레이트 바운드](#5-트레이트-바운드) / [6. impl Trait vs dyn Trait](#6-impl-trait-vs-dyn-trait) |
| [7. 연관 타입과 기본 구현](#7-연관-타입과-기본-구현) / [8. SE 실전 패턴](#8-se-실전-패턴) / [9. 요약](#9-요약)               |

---

## 1. 트레이트 기초

### 트레이트란

다른 언어의 인터페이스(Java)와 유사합니다. 타입이 구현해야 할 동작을 정의합니다.

```rust
// 트레이트 정의
trait HealthCheck {
    fn is_healthy(&self) -> bool;
    fn name(&self) -> &str;
}
```

### 다른 언어와 비교

| 언어   | 개념              | Rust 트레이트와 차이              |
|--------|-------------------|-----------------------------------|
| Java   | interface         | 상속 없음, 구현만 가능            |
| Go     | interface         | 암묵적 구현 vs Rust는 명시적 impl |
| Python | ABC (추상 클래스) | 런타임 체크 vs 컴파일 타임 체크   |
| C++    | 순수 가상 함수    | vtable 비용 선택적 (dyn만)        |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 트레이트 구현

### 기본 구현

```rust
struct WebServer {
    host: String,
    port: u16,
}

struct Database {
    connection_string: String,
    max_connections: u32,
}

impl HealthCheck for WebServer {
    fn is_healthy(&self) -> bool {
        // TCP 연결 시도
        std::net::TcpStream::connect(format!("{}:{}", self.host, self.port)).is_ok()
    }
    fn name(&self) -> &str {
        "WebServer"
    }
}

impl HealthCheck for Database {
    fn is_healthy(&self) -> bool {
        // DB 연결 확인 (간략화)
        !self.connection_string.is_empty()
    }
    fn name(&self) -> &str {
        "Database"
    }
}
```

### 기본 메서드 (default implementation)

```rust
trait Monitorable {
    fn metric_name(&self) -> String;
    fn collect_metrics(&self) -> Vec<(String, f64)>;

    // 기본 구현 (오버라이드 가능)
    fn report(&self) {
        for (name, value) in self.collect_metrics() {
            println!("{}.{} = {}", self.metric_name(), name, value);
        }
    }
}
```

### derive 매크로로 자동 구현

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct Server {
    hostname: String,
    ip: String,
    port: u16,
}

// Debug: {:?} 출력 가능
// Clone: .clone() 호출 가능
// PartialEq/Eq: == 비교 가능
// Hash: HashMap 키로 사용 가능
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 주요 표준 트레이트

### 자주 사용하는 트레이트

| 트레이트      | 용도                   | derive 가능 | 예시                          |
|---------------|------------------------|-------------|-------------------------------|
| `Debug`       | `{:?}` 디버그 출력     | ✅          | `println!("{:?}", server)`    |
| `Display`     | `{}` 사용자 출력       | ❌          | `impl fmt::Display for T`     |
| `Clone`       | 깊은 복사 `.clone()`   | ✅          | `let s2 = s1.clone()`         |
| `Copy`        | 암묵적 복사            | ✅          | 스택 타입만                   |
| `PartialEq`   | `==` / `!=` 비교       | ✅          | `if a == b`                   |
| `Eq`          | 전순서 동치 (NaN 제외) | ✅          | `HashMap` 키 조건             |
| `Hash`        | 해시 계산              | ✅          | `HashMap`/`HashSet` 키        |
| `Default`     | 기본값 생성            | ✅          | `Config::default()`           |
| `From`/`Into` | 타입 변환              | ❌          | `String::from("hello")`       |
| `Iterator`    | 반복자                 | ❌          | `for item in collection`      |
| `Drop`        | 소멸자 (리소스 정리)   | ❌          | 파일 핸들, 네트워크 연결 정리 |

### Display 구현 예시

```rust
use std::fmt;

struct ServerInfo {
    hostname: String,
    ip: String,
    port: u16,
}

impl fmt::Display for ServerInfo {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}({}:{})", self.hostname, self.ip, self.port)
    }
}

// 사용
let srv = ServerInfo { hostname: "web01".into(), ip: "10.0.0.1".into(), port: 80 };
println!("{}", srv); // "web01(10.0.0.1:80)"
```

### From/Into 변환

```rust
struct Port(u16);

impl From<u16> for Port {
    fn from(n: u16) -> Self {
        Port(n)
    }
}

// From을 구현하면 Into는 자동 제공
let p: Port = 8080u16.into();
let p2 = Port::from(443);
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 제네릭

### 함수 제네릭

```rust
// T는 어떤 타입이든 가능
fn first<T>(items: &[T]) -> Option<&T> {
    items.first()
}

// 사용
let numbers = vec![1, 2, 3];
let servers = vec!["web01", "db01"];

let n = first(&numbers); // Option<&i32>
let s = first(&servers); // Option<&&str>
```

### 구조체 제네릭

```rust
struct Metric<T> {
    name: String,
    value: T,
    timestamp: u64,
}

// 사용
let cpu = Metric { name: "cpu_usage".into(), value: 85.5f64, timestamp: 1234567890 };
let conns = Metric { name: "connections".into(), value: 42u32, timestamp: 1234567890 };
```

### 제네릭 구현 블록

```rust
impl<T> Metric<T> {
    fn new(name: &str, value: T) -> Self {
        Metric {
            name: name.to_string(),
            value,
            timestamp: 0, // 간략화
        }
    }
}

// 특정 타입에만 추가 메서드
impl Metric<f64> {
    fn is_critical(&self, threshold: f64) -> bool {
        self.value > threshold
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 트레이트 바운드

제네릭 타입에 제약 조건을 추가합니다.

### 기본 문법

```rust
// T는 Display를 구현해야 함
fn print_metric<T: std::fmt::Display>(name: &str, value: T) {
    println!("{} = {}", name, value);
}

// 여러 바운드: + 사용
fn serialize<T: Clone + std::fmt::Debug>(item: &T) -> String {
    format!("{:?}", item.clone())
}
```

### where 절 (복잡한 바운드)

```rust
fn process_items<T, U>(items: &[T], transformer: U) -> Vec<String>
where
    T: std::fmt::Display + Clone,
    U: Fn(&T) -> String,
{
    items.iter().map(|item| transformer(item)).collect()
}
```

### 반환 타입에 트레이트 바운드

```rust
fn create_checker(check_type: &str) -> Box<dyn HealthCheck> {
    match check_type {
        "web" => Box::new(WebServer { host: "localhost".into(), port: 80 }),
        "db" => Box::new(Database { connection_string: "...".into(), max_connections: 10 }),
        _ => panic!("Unknown check type"),
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. impl Trait vs dyn Trait

### 정적 디스패치: impl Trait

```rust
// 컴파일 타임에 구체 타입 결정 (모노모피제이션)
fn run_check(checker: &impl HealthCheck) -> bool {
    println!("Checking: {}", checker.name());
    checker.is_healthy()
}
// 실제로는 각 타입별 함수가 생성됨 (인라인 가능, 빠름)
```

### 동적 디스패치: dyn Trait

```rust
// 런타임에 타입 결정 (vtable 사용)
fn run_checks(checkers: &[Box<dyn HealthCheck>]) {
    for checker in checkers {
        let status = if checker.is_healthy() { "OK" } else { "FAIL" };
        println!("[{}] {}", status, checker.name());
    }
}
```

### 비교

| 항목          | `impl Trait` (정적) | `dyn Trait` (동적)       |
|---------------|---------------------|--------------------------|
| 디스패치      | 컴파일 타임         | 런타임 (vtable)          |
| 성능          | 빠름 (인라인 가능)  | vtable 간접 호출 비용    |
| 바이너리 크기 | 각 타입별 코드 복제 | 공유 코드                |
| 이종 컬렉션   | 불가                | 가능 (`Vec<Box<dyn T>>`) |
| 사용 시점     | 단일 타입 확정      | 여러 타입 혼합           |

### 선택 기준

```
하나의 구체 타입만 사용?
  │
  ├── 예 → impl Trait (성능 최적)
  │
  └── 아니오 → Vec 등에 여러 타입 저장?
                │
                ├── 예 → Box<dyn Trait>
                │
                └── enum으로 표현 가능? → enum (최적)
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 연관 타입과 기본 구현

### 연관 타입 (Associated Type)

```rust
trait Parser {
    type Output;                    // 연관 타입
    type Error;

    fn parse(&self, input: &str) -> Result<Self::Output, Self::Error>;
}

struct PortParser;

impl Parser for PortParser {
    type Output = u16;
    type Error = std::num::ParseIntError;

    fn parse(&self, input: &str) -> Result<u16, std::num::ParseIntError> {
        input.trim().parse()
    }
}
```

### 트레이트 상속 (Supertrait)

```rust
trait Alertable: HealthCheck + std::fmt::Display {
    fn alert_message(&self) -> String {
        format!("ALERT: {} is unhealthy!", self.name())
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. SE 실전 패턴

### 패턴 1: 플러그인 시스템

```rust
trait MetricCollector: Send + Sync {
    fn name(&self) -> &str;
    fn collect(&self) -> Vec<(String, f64)>;
    fn interval_secs(&self) -> u64 { 60 } // 기본 60초
}

struct CpuCollector;
struct DiskCollector { mount_point: String }
struct NetworkCollector { interface: String }

impl MetricCollector for CpuCollector {
    fn name(&self) -> &str { "cpu" }
    fn collect(&self) -> Vec<(String, f64)> {
        vec![("usage_percent".into(), 45.2)]
    }
}

impl MetricCollector for DiskCollector {
    fn name(&self) -> &str { "disk" }
    fn collect(&self) -> Vec<(String, f64)> {
        vec![("usage_percent".into(), 72.0), ("iops".into(), 1500.0)]
    }
    fn interval_secs(&self) -> u64 { 30 } // 디스크는 30초마다
}

// 사용: 런타임에 컬렉터 동적 추가
fn run_collectors(collectors: Vec<Box<dyn MetricCollector>>) {
    for c in &collectors {
        println!("[{}] (interval: {}s)", c.name(), c.interval_secs());
        for (metric, value) in c.collect() {
            println!("  {}.{} = {:.1}", c.name(), metric, value);
        }
    }
}
```

### 패턴 2: 설정 소스 추상화

```rust
trait ConfigSource {
    fn get(&self, key: &str) -> Option<String>;
    fn source_name(&self) -> &str;
}

struct EnvConfig;
struct FileConfig { path: String, data: std::collections::HashMap<String, String> }

impl ConfigSource for EnvConfig {
    fn get(&self, key: &str) -> Option<String> {
        std::env::var(key).ok()
    }
    fn source_name(&self) -> &str { "environment" }
}

// 우선순위 기반 설정 조회
fn get_config(sources: &[&dyn ConfigSource], key: &str) -> Option<String> {
    sources.iter()
        .find_map(|src| src.get(key))
}
```

### 패턴 3: 제네릭 재시도 함수

```rust
use std::thread;
use std::time::Duration;

fn retry<T, E, F>(max_attempts: u32, delay: Duration, mut f: F) -> Result<T, E>
where
    F: FnMut() -> Result<T, E>,
    E: std::fmt::Display,
{
    let mut last_err = None;
    for attempt in 1..=max_attempts {
        match f() {
            Ok(v) => return Ok(v),
            Err(e) => {
                eprintln!("Attempt {}/{} failed: {}", attempt, max_attempts, e);
                last_err = Some(e);
                if attempt < max_attempts {
                    thread::sleep(delay);
                }
            }
        }
    }
    Err(last_err.unwrap())
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 요약

| 개념            | 용도                    | 문법                                |
|-----------------|-------------------------|-------------------------------------|
| trait 정의      | 동작(메서드) 계약       | `trait T { fn m(&self); }`          |
| impl trait for  | 타입에 트레이트 구현    | `impl T for MyStruct { ... }`       |
| derive          | 표준 트레이트 자동 구현 | `#[derive(Debug, Clone)]`           |
| Generic<T>      | 타입 매개변수           | `fn f<T>(x: T)`, `struct S<T>`      |
| Trait Bound     | 제네릭 타입 제약        | `T: Display + Clone`                |
| where           | 복잡한 바운드 분리      | `where T: Display`                  |
| impl Trait      | 정적 디스패치 (빠름)    | `fn f(x: &impl Trait)`              |
| dyn Trait       | 동적 디스패치 (유연)    | `Box<dyn Trait>`, `&dyn Trait`      |
| Associated Type | 트레이트 내 타입 정의   | `type Output;`                      |
| Default impl    | 기본 구현 제공          | `fn method(&self) { ... }` in trait |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- The Rust Programming Language Ch.10: [doc.rust-lang.org/book/ch10-00-generics.html](https://doc.rust-lang.org/book/ch10-00-generics.html) — ★★★★☆
- Rust by Example - Traits: [doc.rust-lang.org/rust-by-example/trait.html](https://doc.rust-lang.org/rust-by-example/trait.html) — ★★★☆☆
- Rust Design Patterns: [rust-unofficial.github.io/patterns](https://rust-unofficial.github.io/patterns/) — ★★★☆☆

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

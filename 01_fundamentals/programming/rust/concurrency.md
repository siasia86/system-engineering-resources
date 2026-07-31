# Rust 동시성

Rust의 스레드, async/await, 채널, 동기화 프리미티브를 정리합니다.

## 목차

| 섹션                                                                                                                        |
|-----------------------------------------------------------------------------------------------------------------------------|
| [1. 동시성 모델 개요](#1-동시성-모델-개요) / [2. 스레드](#2-스레드) / [3. 공유 상태](#3-공유-상태)                          |
| [4. 채널 (Message Passing)](#4-채널-message-passing) / [5. async/await](#5-asyncawait) / [6. tokio 런타임](#6-tokio-런타임) |
| [7. SE 실전 패턴](#7-se-실전-패턴) / [8. 요약](#8-요약)                                                                     |

---

## 1. 동시성 모델 개요

| 모델        | Rust 구현            | 사용 시나리오                  |
|-------------|----------------------|--------------------------------|
| OS 스레드   | `std::thread`        | CPU-bound 작업, 병렬 계산      |
| 공유 메모리 | `Arc<Mutex<T>>`      | 여러 스레드가 같은 데이터      |
| 메시지 패싱 | `mpsc`, `crossbeam`  | 프로듀서-컨슈머                |
| async/await | `tokio`, `async-std` | I/O-bound, 네트워크, 대량 연결 |

### Rust 동시성 안전 보장

| 보장               | 방법                               |
|--------------------|------------------------------------|
| 데이터 레이스 방지 | 소유권 시스템 + Send/Sync 트레이트 |
| 교착 상태          | 컴파일러가 방지 불가 (개발자 책임) |
| use-after-free     | 소유권으로 원천 차단               |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 스레드

### 기본 스레드 생성

```rust
use std::thread;
use std::time::Duration;

fn main() {
    let handle = thread::spawn(|| {
        for i in 1..=5 {
            println!("worker: {}", i);
            thread::sleep(Duration::from_millis(100));
        }
    });

    for i in 1..=3 {
        println!("main: {}", i);
        thread::sleep(Duration::from_millis(150));
    }

    handle.join().unwrap(); // 스레드 완료 대기
}
```

### move 클로저로 소유권 이전

```rust
use std::thread;

fn main() {
    let servers = vec!["web01", "web02", "web03"];

    let handle = thread::spawn(move || {
        // move: servers의 소유권을 스레드로 이전
        for s in &servers {
            println!("Checking: {}", s);
        }
    });

    // println!("{:?}", servers); // 에러! 소유권 이동됨
    handle.join().unwrap();
}
```

### 여러 스레드 + 결과 수집

```rust
use std::thread;
use std::net::TcpStream;
use std::time::Duration;

fn check_port(host: &str, port: u16) -> bool {
    let addr = format!("{}:{}", host, port);
    TcpStream::connect_timeout(&addr.parse().unwrap(), Duration::from_secs(2)).is_ok()
}

fn main() {
    let targets: Vec<(&str, u16)> = vec![
        ("192.0.2.1", 22),
        ("192.0.2.1", 80),
        ("192.0.2.1", 443),
        ("192.0.2.1", 3306),
    ];

    let handles: Vec<_> = targets.into_iter().map(|(host, port)| {
        let host = host.to_string();
        thread::spawn(move || {
            let open = check_port(&host, port);
            (host, port, open)
        })
    }).collect();

    for h in handles {
        let (host, port, open) = h.join().unwrap();
        let status = if open { "OPEN" } else { "CLOSED" };
        println!("{}:{} = {}", host, port, status);
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 공유 상태

### Mutex (상호 배제)

```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0u64));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();
            *num += 1;
        });
        handles.push(handle);
    }

    for h in handles {
        h.join().unwrap();
    }

    println!("Result: {}", *counter.lock().unwrap()); // 10
}
```

### RwLock (읽기/쓰기 분리)

```rust
use std::sync::{Arc, RwLock};
use std::thread;

fn main() {
    let config = Arc::new(RwLock::new(vec!["web01".to_string(), "web02".to_string()]));

    // 읽기 스레드 (여러 개 동시 가능)
    let config_r = Arc::clone(&config);
    let reader = thread::spawn(move || {
        let servers = config_r.read().unwrap();
        println!("Servers: {:?}", *servers);
    });

    // 쓰기 스레드 (하나만)
    let config_w = Arc::clone(&config);
    let writer = thread::spawn(move || {
        let mut servers = config_w.write().unwrap();
        servers.push("web03".to_string());
    });

    reader.join().unwrap();
    writer.join().unwrap();
}
```

### Arc vs Rc

| 타입  | 스레드 안전 | 용도                    |
|-------|-------------|-------------------------|
| `Rc`  | ❌          | 단일 스레드 참조 카운팅 |
| `Arc` | ✅          | 멀티스레드 참조 카운팅  |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 채널 (Message Passing)

### mpsc (Multiple Producer, Single Consumer)

```rust
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

fn main() {
    let (tx, rx) = mpsc::channel();

    // 여러 프로듀서
    for i in 0..3 {
        let tx = tx.clone();
        thread::spawn(move || {
            let msg = format!("message from thread {}", i);
            tx.send(msg).unwrap();
            thread::sleep(Duration::from_millis(100));
        });
    }
    drop(tx); // 원본 sender 제거 (모든 sender 닫혀야 rx 종료)

    // 단일 컨슈머
    for received in rx {
        println!("Got: {}", received);
    }
}
```

### crossbeam 채널 (고성능)

```rust
use crossbeam::channel;
use std::thread;
use std::time::Duration;

fn main() {
    let (sender, receiver) = channel::bounded(100); // 버퍼 100개

    // 프로듀서
    let s = sender.clone();
    thread::spawn(move || {
        for i in 0..1000 {
            s.send(format!("log line {}", i)).unwrap();
        }
    });

    // 컨슈머
    thread::spawn(move || {
        while let Ok(msg) = receiver.recv_timeout(Duration::from_secs(5)) {
            // 로그 처리
            println!("{}", msg);
        }
    }).join().unwrap();
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. async/await

### 기본 개념

```rust
// async 함수: Future를 반환
async fn fetch_status(url: &str) -> Result<u16, reqwest::Error> {
    let resp = reqwest::get(url).await?;
    Ok(resp.status().as_u16())
}

// .await: Future 완료까지 대기 (스레드 차단 없이)
```

### 동기 vs 비동기 비교

| 항목            | 동기 (std::thread)               | 비동기 (async/await)            |
|-----------------|----------------------------------|---------------------------------|
| 1000 연결       | 1000 OS 스레드 (무거움)          | 1 스레드 + 1000 태스크 (가벼움) |
| 메모리/태스크   | ~2MiB (스택, platform-dependent) | ~64 bytes (Tokio 태스크)        |
| 적합 대상       | CPU-bound                        | I/O-bound (네트워크, 파일)      |
| 컨텍스트 스위칭 | OS 스케줄러 (비쌈)               | 유저스페이스 (저렴)             |

### 언제 async를 선택하는가

```
작업이 CPU-bound? (계산, 압축, 해시)
  │
  ├── 예 → std::thread 또는 rayon
  │
  └── 아니오 → I/O 대기 많음? (네트워크, 디스크)
                │
                ├── 예 + 동시 연결 많음 → async/await (tokio)
                │
                └── 예 + 동시 연결 적음 → std::thread도 충분
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. tokio 런타임

### Cargo.toml

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
```

### 기본 사용

```rust
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    println!("start");
    sleep(Duration::from_secs(1)).await;
    println!("1 second later");
}
```

### 동시 실행 (join!)

```rust
use tokio::time::{sleep, Duration};

async fn check_web() -> bool {
    sleep(Duration::from_millis(100)).await;
    true
}

async fn check_db() -> bool {
    sleep(Duration::from_millis(200)).await;
    true
}

#[tokio::main]
async fn main() {
    // 동시 실행 (총 200ms, 직렬이면 300ms)
    let (web, db) = tokio::join!(check_web(), check_db());
    println!("web={}, db={}", web, db);
}
```

### 태스크 스폰

```rust
use tokio::task;

#[tokio::main]
async fn main() {
    let mut handles = vec![];

    for i in 0..10 {
        let handle = task::spawn(async move {
            // 비동기 작업
            tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
            format!("task {} done", i)
        });
        handles.push(handle);
    }

    for h in handles {
        let result = h.await.unwrap();
        println!("{}", result);
    }
}
```

### tokio 채널

```rust
use tokio::sync::mpsc;

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel(100);

    tokio::spawn(async move {
        for i in 0..10 {
            tx.send(format!("msg {}", i)).await.unwrap();
        }
    });

    while let Some(msg) = rx.recv().await {
        println!("Received: {}", msg);
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. SE 실전 패턴

### 패턴 1: 병렬 서버 헬스체크

```rust
use tokio::net::TcpStream;
use tokio::time::{timeout, Duration};

async fn check_server(addr: &str) -> (String, bool) {
    let result = timeout(
        Duration::from_secs(5),
        TcpStream::connect(addr),
    ).await;

    let healthy = matches!(result, Ok(Ok(_)));
    (addr.to_string(), healthy)
}

#[tokio::main]
async fn main() {
    let servers = vec![
        "192.0.2.1:80",
        "192.0.2.1:443",
        "192.0.2.1:3306",
        "192.0.2.1:6379",
    ];

    let mut handles = vec![];
    for addr in servers {
        handles.push(tokio::spawn(async move {
            check_server(addr).await
        }));
    }

    for h in handles {
        let (addr, healthy) = h.await.unwrap();
        let status = if healthy { "OK" } else { "FAIL" };
        println!("[{}] {}", status, addr);
    }
}
```

### 패턴 2: 주기적 메트릭 수집

```rust
use tokio::time::{interval, Duration};

async fn collect_metrics() {
    let mut ticker = interval(Duration::from_secs(60));

    loop {
        ticker.tick().await;
        // CPU, 메모리, 디스크 수집
        let cpu = get_cpu_usage().await;
        let mem = get_memory_usage().await;
        println!("cpu={:.1}%, mem={:.1}%", cpu, mem);
    }
}
```

### 패턴 3: graceful shutdown

```rust
use tokio::signal;
use tokio::sync::broadcast;

#[tokio::main]
async fn main() {
    let (shutdown_tx, _) = broadcast::channel(1);

    // 워커 태스크
    let mut rx = shutdown_tx.subscribe();
    let worker = tokio::spawn(async move {
        loop {
            tokio::select! {
                _ = rx.recv() => {
                    println!("Worker: shutting down");
                    break;
                }
                _ = tokio::time::sleep(Duration::from_secs(1)) => {
                    println!("Worker: tick");
                }
            }
        }
    });

    // SIGTERM/SIGINT 대기
    signal::ctrl_c().await.unwrap();
    println!("Shutdown signal received");
    let _ = shutdown_tx.send(());

    worker.await.unwrap();
    println!("Clean shutdown complete");
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 요약

| 도구             | 용도                     | 예시                        |
|------------------|--------------------------|-----------------------------|
| `thread::spawn`  | OS 스레드 생성           | CPU-bound 병렬 처리         |
| `Arc<Mutex<T>>`  | 공유 상태 보호           | 카운터, 설정 공유           |
| `Arc<RwLock<T>>` | 읽기 많은 공유 상태      | 설정 파일, 캐시             |
| `mpsc::channel`  | 스레드 간 메시지 전달    | 로그 수집, 이벤트 처리      |
| `async fn`       | 비동기 함수              | 네트워크 I/O                |
| `tokio::spawn`   | 비동기 태스크 생성       | 동시 HTTP 요청              |
| `tokio::join!`   | 여러 Future 동시 대기    | 병렬 헬스체크               |
| `tokio::select!` | 첫 번째 완료 Future 선택 | timeout + graceful shutdown |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- The Rust Programming Language Ch.16: [doc.rust-lang.org/book/ch16-00-concurrency.html](https://doc.rust-lang.org/book/ch16-00-concurrency.html) — ★★★★☆
- Tokio Tutorial: [tokio.rs/tokio/tutorial](https://tokio.rs/tokio/tutorial) — ★★★★☆
- Async Book: [rust-lang.github.io/async-book](https://rust-lang.github.io/async-book/) — ★★★☆☆

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

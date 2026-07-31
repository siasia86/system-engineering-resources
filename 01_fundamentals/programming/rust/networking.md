# Rust 네트워크 프로그래밍

TCP/UDP 소켓, HTTP 클라이언트/서버, DNS 조회 등 SE 실무 네트워크 프로그래밍을 정리합니다.

## 목차

| 섹션                                                                                                                 |
|----------------------------------------------------------------------------------------------------------------------|
| [1. TCP 소켓](#1-tcp-소켓) / [2. UDP 소켓](#2-udp-소켓) / [3. HTTP 클라이언트 (reqwest)](#3-http-클라이언트-reqwest) |
| [4. HTTP 서버 (axum)](#4-http-서버-axum) / [5. DNS 조회](#5-dns-조회) / [6. SE 실전 예제](#6-se-실전-예제)           |
| [7. 요약](#7-요약)                                                                                                   |

---

## 1. TCP 소켓

### 동기 TCP 클라이언트

```rust
use std::io::{Read, Write};
use std::net::TcpStream;
use std::time::Duration;

fn tcp_connect(addr: &str) -> std::io::Result<String> {
    let mut stream = TcpStream::connect_timeout(
        &addr.parse().unwrap(),
        Duration::from_secs(5),
    )?;
    stream.set_read_timeout(Some(Duration::from_secs(10)))?;

    stream.write_all(b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n")?;

    let mut response = String::new();
    stream.read_to_string(&mut response)?;
    Ok(response)
}
```

### 비동기 TCP (tokio)

```rust
use tokio::net::TcpStream;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::time::{timeout, Duration};

async fn async_tcp_connect(addr: &str) -> anyhow::Result<String> {
    let mut stream = timeout(
        Duration::from_secs(5),
        TcpStream::connect(addr),
    ).await??;

    stream.write_all(b"PING\r\n").await?;

    let mut buf = vec![0u8; 4096];
    let n = stream.read(&mut buf).await?;
    Ok(String::from_utf8_lossy(&buf[..n]).to_string())
}
```

### TCP 서버 (간단한 에코)

```rust
use tokio::net::TcpListener;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let listener = TcpListener::bind("0.0.0.0:9000").await?;
    println!("Listening on :9000");

    loop {
        let (mut socket, addr) = listener.accept().await?;
        println!("Connection from: {}", addr);

        tokio::spawn(async move {
            let mut buf = [0u8; 1024];
            loop {
                let n = match socket.read(&mut buf).await {
                    Ok(0) => return, // 연결 종료
                    Ok(n) => n,
                    Err(_) => return,
                };
                if socket.write_all(&buf[..n]).await.is_err() {
                    return;
                }
            }
        });
    }
}
```

### 포트 스캐너

```rust
use tokio::net::TcpStream;
use tokio::time::{timeout, Duration};

async fn scan_port(host: &str, port: u16) -> (u16, bool) {
    let addr = format!("{}:{}", host, port);
    let result = timeout(Duration::from_secs(2), TcpStream::connect(&addr)).await;
    (port, matches!(result, Ok(Ok(_))))
}

#[tokio::main]
async fn main() {
    let host = "192.0.2.1";
    let ports = vec![22, 80, 443, 3306, 5432, 6379, 8080, 9090];

    let mut handles = vec![];
    for port in ports {
        let h = host.to_string();
        handles.push(tokio::spawn(async move { scan_port(&h, port).await }));
    }

    for h in handles {
        let (port, open) = h.await.unwrap();
        if open {
            println!("  {:5} OPEN", port);
        }
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. UDP 소켓

```rust
use tokio::net::UdpSocket;

async fn udp_echo_server() -> anyhow::Result<()> {
    let socket = UdpSocket::bind("0.0.0.0:9001").await?;
    let mut buf = [0u8; 1024];

    loop {
        let (len, addr) = socket.recv_from(&mut buf).await?;
        println!("Received {} bytes from {}", len, addr);
        socket.send_to(&buf[..len], addr).await?;
    }
}

async fn udp_client(addr: &str, msg: &[u8]) -> anyhow::Result<String> {
    let socket = UdpSocket::bind("0.0.0.0:0").await?;
    socket.send_to(msg, addr).await?;

    let mut buf = [0u8; 1024];
    let (len, _) = socket.recv_from(&mut buf).await?;
    Ok(String::from_utf8_lossy(&buf[..len]).to_string())
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. HTTP 클라이언트 (reqwest)

### Cargo.toml

```toml
[dependencies]
reqwest = { version = "0.13", features = ["json"] }
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

### 기본 GET/POST

```rust
use reqwest;

// GET
async fn get_status(url: &str) -> anyhow::Result<u16> {
    let resp = reqwest::get(url).await?;
    Ok(resp.status().as_u16())
}

// POST JSON
async fn post_alert(webhook_url: &str, message: &str) -> anyhow::Result<()> {
    let client = reqwest::Client::new();
    let body = serde_json::json!({
        "text": message,
        "level": "critical"
    });

    let resp = client.post(webhook_url)
        .json(&body)
        .timeout(std::time::Duration::from_secs(10))
        .send()
        .await?;

    if !resp.status().is_success() {
        anyhow::bail!("Webhook failed: {}", resp.status());
    }
    Ok(())
}
```

### JSON 응답 파싱

```rust
use serde::Deserialize;

#[derive(Deserialize, Debug)]
struct ApiResponse {
    status: String,
    data: Vec<MetricData>,
}

#[derive(Deserialize, Debug)]
struct MetricData {
    name: String,
    value: f64,
}

async fn fetch_metrics(api_url: &str) -> anyhow::Result<Vec<MetricData>> {
    let resp: ApiResponse = reqwest::get(api_url)
        .await?
        .json()
        .await?;
    Ok(resp.data)
}
```

### 타임아웃 + 재시도

```rust
use reqwest::Client;
use std::time::Duration;

fn build_client() -> Client {
    Client::builder()
        .timeout(Duration::from_secs(30))
        .connect_timeout(Duration::from_secs(5))
        .pool_max_idle_per_host(10)
        .build()
        .unwrap()
}

async fn get_with_retry(client: &Client, url: &str, retries: u32) -> anyhow::Result<String> {
    let mut last_err = None;
    for attempt in 1..=retries {
        match client.get(url).send().await {
            Ok(resp) if resp.status().is_success() => {
                return resp.text().await.map_err(Into::into);
            }
            Ok(resp) => {
                last_err = Some(anyhow::anyhow!("HTTP {}", resp.status()));
            }
            Err(e) => {
                last_err = Some(e.into());
            }
        }
        if attempt < retries {
            tokio::time::sleep(Duration::from_secs(2u64.pow(attempt))).await;
        }
    }
    Err(last_err.unwrap())
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. HTTP 서버 (axum)

### Cargo.toml

```toml
[dependencies]
axum = "0.8"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

### 기본 서버

```rust
use axum::{routing::get, Router, Json};
use serde::Serialize;

#[derive(Serialize)]
struct HealthResponse {
    status: String,
    uptime_secs: u64,
}

async fn health_check() -> Json<HealthResponse> {
    Json(HealthResponse {
        status: "ok".to_string(),
        uptime_secs: 3600,
    })
}

async fn metrics() -> String {
    // Prometheus 형식
    format!(
        "# HELP cpu_usage CPU usage percent\n\
         # TYPE cpu_usage gauge\n\
         cpu_usage 45.2\n\
         # HELP memory_used Memory used bytes\n\
         # TYPE memory_used gauge\n\
         memory_used 8589934592\n"
    )
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/health", get(health_check))
        .route("/metrics", get(metrics));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:9090").await.unwrap();
    println!("Server listening on :9090");
    axum::serve(listener, app).await.unwrap();
}
```

### Prometheus exporter 패턴

```rust
use axum::{routing::get, Router};
use std::sync::{Arc, Mutex};
use tokio::time::{interval, Duration};

struct Metrics {
    cpu_usage: f64,
    memory_used: u64,
    disk_usage: f64,
}

async fn collect_loop(metrics: Arc<Mutex<Metrics>>) {
    let mut ticker = interval(Duration::from_secs(15));
    loop {
        ticker.tick().await;
        let mut m = metrics.lock().unwrap();
        m.cpu_usage = 42.5;  // 실제 수집 로직
        m.memory_used = 8 * 1024 * 1024 * 1024;
        m.disk_usage = 72.0;
    }
}

async fn metrics_handler(metrics: Arc<Mutex<Metrics>>) -> String {
    let m = metrics.lock().unwrap();
    format!(
        "cpu_usage {:.1}\nmemory_used_bytes {}\ndisk_usage_percent {:.1}\n",
        m.cpu_usage, m.memory_used, m.disk_usage
    )
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. DNS 조회

### std::net (기본)

```rust
use std::net::ToSocketAddrs;

fn resolve(hostname: &str) -> Vec<String> {
    let addr = format!("{}:0", hostname);
    match addr.to_socket_addrs() {
        Ok(addrs) => addrs.map(|a| a.ip().to_string()).collect(),
        Err(e) => {
            eprintln!("DNS resolve failed: {}", e);
            vec![]
        }
    }
}
```

### trust-dns (비동기, 상세 제어)

```rust
use trust_dns_resolver::TokioAsyncResolver;
use trust_dns_resolver::config::*;

async fn dns_lookup(domain: &str) -> anyhow::Result<Vec<String>> {
    let resolver = TokioAsyncResolver::tokio(
        ResolverConfig::default(),
        ResolverOpts::default(),
    );

    let response = resolver.lookup_ip(domain).await?;
    Ok(response.iter().map(|ip| ip.to_string()).collect())
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. SE 실전 예제

### 병렬 헬스체크 도구

```rust
use reqwest::Client;
use std::time::{Duration, Instant};
use tokio;

#[derive(Debug)]
struct CheckResult {
    url: String,
    status: u16,
    latency_ms: u128,
    healthy: bool,
}

async fn check_endpoint(client: &Client, url: &str) -> CheckResult {
    let start = Instant::now();
    let result = client.get(url)
        .timeout(Duration::from_secs(10))
        .send()
        .await;

    match result {
        Ok(resp) => CheckResult {
            url: url.to_string(),
            status: resp.status().as_u16(),
            latency_ms: start.elapsed().as_millis(),
            healthy: resp.status().is_success(),
        },
        Err(_) => CheckResult {
            url: url.to_string(),
            status: 0,
            latency_ms: start.elapsed().as_millis(),
            healthy: false,
        },
    }
}

#[tokio::main]
async fn main() {
    let client = Client::builder()
        .timeout(Duration::from_secs(10))
        .build()
        .unwrap();

    let endpoints = vec![
        "https://example.com/health",
        "https://example.com/api/status",
        "https://example.com/metrics",
    ];

    let mut handles = vec![];
    for url in endpoints {
        let c = client.clone();
        handles.push(tokio::spawn(async move {
            check_endpoint(&c, url).await
        }));
    }

    println!("{:<40} {:>6} {:>8} {}", "URL", "STATUS", "LATENCY", "HEALTH");
    println!("{}", "-".repeat(70));
    for h in handles {
        let r = h.await.unwrap();
        let health = if r.healthy { "OK" } else { "FAIL" };
        println!("{:<40} {:>6} {:>5}ms {}", r.url, r.status, r.latency_ms, health);
    }
}
```

### 간단한 TCP 프록시

```rust
use tokio::io::{copy, split};
use tokio::net::{TcpListener, TcpStream};

async fn proxy(listen: &str, target: &str) -> anyhow::Result<()> {
    let listener = TcpListener::bind(listen).await?;
    println!("Proxy {} -> {}", listen, target);

    loop {
        let (client, addr) = listener.accept().await?;
        let target = target.to_string();

        tokio::spawn(async move {
            let server = match TcpStream::connect(&target).await {
                Ok(s) => s,
                Err(e) => { eprintln!("{}: connect error: {}", addr, e); return; }
            };

            let (mut cr, mut cw) = split(client);
            let (mut sr, mut sw) = split(server);

            let c2s = copy(&mut cr, &mut sw);
            let s2c = copy(&mut sr, &mut cw);

            tokio::select! {
                _ = c2s => {},
                _ = s2c => {},
            }
        });
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 요약

| 기능            | 크레이트              | SE 활용                     |
|-----------------|-----------------------|-----------------------------|
| TCP 클라이언트  | `tokio::net`          | 포트 체크, 헬스체크         |
| TCP 서버        | `tokio::net`          | 에코 서버, 프록시           |
| HTTP 클라이언트 | `reqwest`             | API 호출, 웹훅, 모니터링    |
| HTTP 서버       | `axum`                | 메트릭 엔드포인트, 내부 API |
| DNS             | `trust-dns`           | 도메인 조회, 검증           |
| UDP             | `tokio::net`          | 로그 전송 (syslog), SNMP    |
| TLS             | `rustls`/`native-tls` | HTTPS, 인증서 검증          |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Tokio Tutorial: [tokio.rs/tokio/tutorial](https://tokio.rs/tokio/tutorial) — ★★★★☆
- reqwest docs: [docs.rs/reqwest](https://docs.rs/reqwest) — ★★★☆☆
- axum docs: [docs.rs/axum](https://docs.rs/axum) — ★★★☆☆
- Rust Networking (book): [oreilly.com](https://www.oreilly.com/library/view/network-programming-with/9781788624893/) — ★★☆☆☆

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

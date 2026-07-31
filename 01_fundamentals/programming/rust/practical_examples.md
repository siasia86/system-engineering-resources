# Rust SE 실전 예제

SE 업무에서 바로 사용할 수 있는 Rust 코드 예제를 모아 정리합니다.

## 목차

| 섹션                                                                                                                                             |
|--------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 디스크 사용량 모니터](#1-디스크-사용량-모니터) / [2. 로그 파서](#2-로그-파서) / [3. 서버 인벤토리 수집](#3-서버-인벤토리-수집)               |
| [4. Prometheus Exporter](#4-prometheus-exporter) / [5. 설정 파일 diff 도구](#5-설정-파일-diff-도구) / [6. 파일 무결성 검사](#6-파일-무결성-검사) |
| [7. 배치 SSH 실행기](#7-배치-ssh-실행기) / [8. 요약](#8-요약)                                                                                    |

---

## 1. 디스크 사용량 모니터

```rust
use std::fs;
use std::process::Command;

#[derive(Debug)]
struct DiskUsage {
    mount_point: String,
    total_gb: f64,
    used_gb: f64,
    usage_percent: f64,
}

fn get_disk_usage() -> Vec<DiskUsage> {
    let output = Command::new("df")
        .args(["-B1", "--output=target,size,used,pcent"])
        .output()
        .expect("df command failed");

    let stdout = String::from_utf8_lossy(&output.stdout);
    stdout.lines()
        .skip(1) // 헤더
        .filter_map(|line| {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 4 {
                let mount = parts[0].to_string();
                let total: f64 = parts[1].parse().unwrap_or(0.0) / 1_073_741_824.0;
                let used: f64 = parts[2].parse().unwrap_or(0.0) / 1_073_741_824.0;
                let percent: f64 = parts[3].trim_end_matches('%').parse().unwrap_or(0.0);
                Some(DiskUsage { mount_point: mount, total_gb: total, used_gb: used, usage_percent: percent })
            } else { None }
        })
        .filter(|d| d.total_gb > 0.1) // tmpfs 등 제외
        .collect()
}

fn main() {
    let disks = get_disk_usage();
    println!("{:<20} {:>8} {:>8} {:>6}", "MOUNT", "TOTAL", "USED", "USE%");
    println!("{}", "-".repeat(50));
    for d in &disks {
        let indicator = if d.usage_percent > 90.0 { "!!" }
                       else if d.usage_percent > 80.0 { "!" }
                       else { "" };
        println!("{:<20} {:>6.1}GB {:>6.1}GB {:>5.1}% {}",
            d.mount_point, d.total_gb, d.used_gb, d.usage_percent, indicator);
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 로그 파서

### nginx access.log 분석기

```rust
use regex::Regex;
use std::collections::HashMap;
use std::fs;

#[derive(Debug)]
struct LogEntry {
    ip: String,
    method: String,
    path: String,
    status: u16,
    size: u64,
}

fn parse_nginx_log(path: &str) -> anyhow::Result<Vec<LogEntry>> {
    let re = Regex::new(
        r#"^(\S+) .+ \[.+\] "(\S+) (\S+) .+" (\d+) (\d+)"#
    )?;

    let content = fs::read_to_string(path)?;
    let entries: Vec<LogEntry> = content.lines()
        .filter_map(|line| {
            re.captures(line).map(|caps| LogEntry {
                ip: caps[1].to_string(),
                method: caps[2].to_string(),
                path: caps[3].to_string(),
                status: caps[4].parse().unwrap_or(0),
                size: caps[5].parse().unwrap_or(0),
            })
        })
        .collect();
    Ok(entries)
}

fn print_summary(entries: &[LogEntry]) {
    // 상태 코드별 카운트
    let mut status_count: HashMap<u16, usize> = HashMap::new();
    for e in entries {
        *status_count.entry(e.status).or_insert(0) += 1;
    }

    println!("\n=== Status Code Distribution ===");
    let mut codes: Vec<_> = status_count.iter().collect();
    codes.sort_by_key(|(code, _)| *code);
    for (code, count) in codes {
        println!("  {} : {} requests", code, count);
    }

    // 상위 IP
    let mut ip_count: HashMap<&str, usize> = HashMap::new();
    for e in entries {
        *ip_count.entry(&e.ip).or_insert(0) += 1;
    }
    println!("\n=== Top 5 IPs ===");
    let mut ips: Vec<_> = ip_count.iter().collect();
    ips.sort_by(|a, b| b.1.cmp(a.1));
    for (ip, count) in ips.iter().take(5) {
        println!("  {} : {} requests", ip, count);
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 서버 인벤토리 수집

```rust
use serde::Serialize;
use std::fs;

#[derive(Serialize, Debug)]
struct ServerInventory {
    hostname: String,
    os: String,
    kernel: String,
    cpu_cores: usize,
    memory_total_mb: u64,
    disk_total_gb: f64,
    uptime_hours: f64,
}

fn collect_inventory() -> anyhow::Result<ServerInventory> {
    let hostname = fs::read_to_string("/etc/hostname")?.trim().to_string();

    let os_release = fs::read_to_string("/etc/os-release")?;
    let os = os_release.lines()
        .find(|l| l.starts_with("PRETTY_NAME="))
        .map(|l| l.trim_start_matches("PRETTY_NAME=").trim_matches('"').to_string())
        .unwrap_or_else(|| "Unknown".to_string());

    let kernel = fs::read_to_string("/proc/version")?
        .split_whitespace().nth(2).unwrap_or("unknown").to_string();

    let cpu_cores = fs::read_to_string("/proc/cpuinfo")?
        .lines().filter(|l| l.starts_with("processor")).count();

    let meminfo = fs::read_to_string("/proc/meminfo")?;
    let mem_kb: u64 = meminfo.lines()
        .find(|l| l.starts_with("MemTotal:"))
        .and_then(|l| l.split_whitespace().nth(1))
        .and_then(|s| s.parse().ok())
        .unwrap_or(0);

    let uptime: f64 = fs::read_to_string("/proc/uptime")?
        .split_whitespace().next()
        .and_then(|s| s.parse().ok())
        .unwrap_or(0.0);

    Ok(ServerInventory {
        hostname,
        os,
        kernel,
        cpu_cores,
        memory_total_mb: mem_kb / 1024,
        disk_total_gb: 0.0, // df 파싱 추가 가능
        uptime_hours: uptime / 3600.0,
    })
}

fn main() -> anyhow::Result<()> {
    let inv = collect_inventory()?;
    println!("{}", serde_json::to_string_pretty(&inv)?);
    Ok(())
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. Prometheus Exporter

```rust
use axum::{routing::get, Router};
use std::sync::{Arc, Mutex};
use tokio::time::{interval, Duration};

struct Metrics {
    cpu_usage: f64,
    memory_used_bytes: u64,
    memory_total_bytes: u64,
    disk_usage_percent: f64,
    load_average_1m: f64,
}

async fn collect_metrics(metrics: Arc<Mutex<Metrics>>) {
    let mut ticker = interval(Duration::from_secs(15));
    loop {
        ticker.tick().await;
        let mut m = metrics.lock().unwrap();
        // /proc 파싱으로 실제 값 수집
        m.cpu_usage = 42.5;
        m.memory_used_bytes = 8 * 1024 * 1024 * 1024;
        m.memory_total_bytes = 16 * 1024 * 1024 * 1024;
        m.disk_usage_percent = 72.3;
        m.load_average_1m = 2.1;
    }
}

async fn metrics_handler(
    axum::extract::State(metrics): axum::extract::State<Arc<Mutex<Metrics>>>
) -> String {
    let m = metrics.lock().unwrap();
    format!(
        "# HELP node_cpu_usage CPU usage percent\n\
         # TYPE node_cpu_usage gauge\n\
         node_cpu_usage {:.2}\n\
         # HELP node_memory_used_bytes Memory used in bytes\n\
         # TYPE node_memory_used_bytes gauge\n\
         node_memory_used_bytes {}\n\
         # HELP node_memory_total_bytes Memory total in bytes\n\
         # TYPE node_memory_total_bytes gauge\n\
         node_memory_total_bytes {}\n\
         # HELP node_disk_usage_percent Disk usage percent\n\
         # TYPE node_disk_usage_percent gauge\n\
         node_disk_usage_percent {:.2}\n\
         # HELP node_load_average_1m Load average 1 minute\n\
         # TYPE node_load_average_1m gauge\n\
         node_load_average_1m {:.2}\n",
        m.cpu_usage, m.memory_used_bytes, m.memory_total_bytes,
        m.disk_usage_percent, m.load_average_1m
    )
}

#[tokio::main]
async fn main() {
    let metrics = Arc::new(Mutex::new(Metrics {
        cpu_usage: 0.0, memory_used_bytes: 0, memory_total_bytes: 0,
        disk_usage_percent: 0.0, load_average_1m: 0.0,
    }));

    // 백그라운드 수집
    let m = Arc::clone(&metrics);
    tokio::spawn(collect_metrics(m));

    // HTTP 서버
    let app = Router::new()
        .route("/metrics", get(metrics_handler))
        .with_state(metrics);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:9100").await.unwrap();
    println!("Exporter listening on :9100/metrics");
    axum::serve(listener, app).await.unwrap();
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 설정 파일 diff 도구

```rust
use std::collections::BTreeMap;
use std::fs;

fn parse_ini(content: &str) -> BTreeMap<String, String> {
    content.lines()
        .filter(|l| !l.trim().is_empty() && !l.starts_with('#') && !l.starts_with(';'))
        .filter_map(|l| {
            l.split_once('=').map(|(k, v)| (k.trim().to_string(), v.trim().to_string()))
        })
        .collect()
}

fn diff_configs(file_a: &str, file_b: &str) -> anyhow::Result<()> {
    let a = parse_ini(&fs::read_to_string(file_a)?);
    let b = parse_ini(&fs::read_to_string(file_b)?);

    println!("=== Added (in B, not in A) ===");
    for (k, v) in &b {
        if !a.contains_key(k) {
            println!("  + {} = {}", k, v);
        }
    }

    println!("\n=== Removed (in A, not in B) ===");
    for (k, v) in &a {
        if !b.contains_key(k) {
            println!("  - {} = {}", k, v);
        }
    }

    println!("\n=== Changed ===");
    for (k, v_a) in &a {
        if let Some(v_b) = b.get(k) {
            if v_a != v_b {
                println!("  ~ {} : {} → {}", k, v_a, v_b);
            }
        }
    }
    Ok(())
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 파일 무결성 검사

```rust
use sha2::{Sha256, Digest};
use std::fs;
use std::io::{BufReader, Read};
use std::path::Path;

fn file_sha256(path: &Path) -> anyhow::Result<String> {
    let file = fs::File::open(path)?;
    let mut reader = BufReader::new(file);
    let mut hasher = Sha256::new();
    let mut buffer = [0u8; 8192];

    loop {
        let n = reader.read(&mut buffer)?;
        if n == 0 { break; }
        hasher.update(&buffer[..n]);
    }

    Ok(format!("{:x}", hasher.finalize()))
}

fn check_integrity(manifest_path: &str) -> anyhow::Result<Vec<(String, bool)>> {
    let content = fs::read_to_string(manifest_path)?;
    let mut results = Vec::new();

    for line in content.lines() {
        if let Some((hash, path)) = line.split_once("  ") {
            let current = file_sha256(Path::new(path)).unwrap_or_default();
            let ok = current == hash;
            results.push((path.to_string(), ok));
        }
    }
    Ok(results)
}

fn generate_manifest(dir: &str) -> anyhow::Result<String> {
    let mut manifest = String::new();
    for entry in walkdir::WalkDir::new(dir).into_iter().flatten() {
        if entry.file_type().is_file() {
            let hash = file_sha256(entry.path())?;
            manifest.push_str(&format!("{}  {}\n", hash, entry.path().display()));
        }
    }
    Ok(manifest)
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 배치 SSH 실행기

```rust
use std::process::Command;
use std::thread;
use std::sync::mpsc;

#[derive(Debug)]
struct SshResult {
    host: String,
    exit_code: i32,
    stdout: String,
    stderr: String,
}

fn ssh_exec(host: &str, command: &str, timeout_secs: u64) -> SshResult {
    let output = Command::new("ssh")
        .args([
            "-o", "StrictHostKeyChecking=no",
            "-o", &format!("ConnectTimeout={}", timeout_secs),
            "-o", "BatchMode=yes",
            host,
            command,
        ])
        .output();

    match output {
        Ok(out) => SshResult {
            host: host.to_string(),
            exit_code: out.status.code().unwrap_or(-1),
            stdout: String::from_utf8_lossy(&out.stdout).trim().to_string(),
            stderr: String::from_utf8_lossy(&out.stderr).trim().to_string(),
        },
        Err(e) => SshResult {
            host: host.to_string(),
            exit_code: -1,
            stdout: String::new(),
            stderr: e.to_string(),
        },
    }
}

fn batch_exec(hosts: &[&str], command: &str) -> Vec<SshResult> {
    let (tx, rx) = mpsc::channel();

    for host in hosts {
        let tx = tx.clone();
        let host = host.to_string();
        let cmd = command.to_string();
        thread::spawn(move || {
            let result = ssh_exec(&host, &cmd, 10);
            tx.send(result).unwrap();
        });
    }
    drop(tx);

    rx.iter().collect()
}

fn main() {
    let hosts = vec!["web01", "web02", "web03", "db01"];
    let command = "uptime";

    println!("Executing '{}' on {} hosts...\n", command, hosts.len());
    let results = batch_exec(&hosts, command);

    for r in &results {
        let status = if r.exit_code == 0 { "OK" } else { "FAIL" };
        println!("[{}] {} (exit={})", status, r.host, r.exit_code);
        if !r.stdout.is_empty() {
            println!("     {}", r.stdout);
        }
        if !r.stderr.is_empty() {
            eprintln!("     ERR: {}", r.stderr);
        }
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 요약

| 예제                | 핵심 크레이트           | SE 활용                 |
|---------------------|-------------------------|-------------------------|
| 디스크 모니터       | std::process            | 용량 경보               |
| 로그 파서           | regex, std::collections | 장애 분석, 통계         |
| 인벤토리 수집       | serde_json, /proc       | 자산 관리, Ansible 대체 |
| Prometheus Exporter | axum, tokio             | 커스텀 모니터링         |
| 설정 diff           | std::collections        | 변경 관리               |
| 파일 무결성         | sha2, walkdir           | 보안 감사, AIDE 대체    |
| 배치 SSH            | std::process, thread    | 일괄 명령 실행          |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Rust Cookbook: [rust-lang-nursery.github.io/rust-cookbook](https://rust-lang-nursery.github.io/rust-cookbook/) — ★★★☆☆
- Command-Line Rust: [oreilly.com](https://www.oreilly.com/library/view/command-line-rust/9781098109424/) — ★★★★☆
- Zero To Production In Rust: [zero2prod.com](https://www.zero2prod.com/) — ★★★☆☆

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

---
name: rust-official-notes
description: Rust 공식 문서 기반 핵심 사실, deprecated, breaking changes, 크레이트 버전 현황 정리. Rust 문서 작성/검토 시 참조.
tags:
  - rust
  - programming
  - systems-programming
  - cargo
  - crates
last_checked: 2026-07-29
sources:
  - https://doc.rust-lang.org/book/
  - https://doc.rust-lang.org/std/
  - https://doc.rust-lang.org/reference/
  - https://tokio.rs/tokio/tutorial
  - https://crates.io/
---

# Rust 공식 문서 참조 노트

## 1. 버전 현황 (확인일: 2026-07-29)

### Rust 릴리스

> 확인일: 2026-07-29 기준. Rust는 6주 릴리스 사이클로 업데이트됩니다.

| 항목        | 버전   | 비고                                   |
|-------------|--------|----------------------------------------|
| Stable      | 1.97.1 | MSRV 기준 확인 필요                    |
| Edition     | 2024   | 현행 권장 (Rust 1.85+, cargo new 기본) |
| MSRV (최소) | 1.70   | LazyLock=1.80+, Edition 2024=1.85+     |

### 주요 크레이트 최신 안정 버전 (2026-07-29)

| 크레이트    | 최신 버전 | 주요 변경             |
|-------------|-----------|-----------------------|
| tokio       | 1.53.1    | 안정적, API 변경 없음 |
| serde       | 1.0.229   | 안정적                |
| reqwest     | 0.13.4    | 0.12→0.13 breaking    |
| axum        | 0.8.9     | 0.7→0.8 breaking      |
| clap        | 4.6.4     | derive 방식 표준화    |
| anyhow      | 1.0.104   | 안정적                |
| thiserror   | 2.0.19    | 2.x로 major bump      |
| signal-hook | 0.4.4     | 0.3→0.4 minor 변경    |
| nix         | 0.31.3    | 0.29→0.31             |
| crossbeam   | 0.8.4     | MPMC (mpsc와 다름)    |
| regex       | 1.13.1    | 안정적                |
| chrono      | 0.4.45    | 안정적                |

## 2. 소유권 시스템 핵심 사실

### 스택/힙 타입

| 타입               | Copy | 위치 | 크기        |
|--------------------|------|------|-------------|
| i8~i128, u8~u128   | ✅   | 스택 | 고정        |
| f32, f64           | ✅   | 스택 | 4/8 bytes   |
| bool               | ✅   | 스택 | 1 byte      |
| char               | ✅   | 스택 | **4 bytes** |
| &T (불변 참조)     | ✅   | 스택 | 포인터 크기 |
| &mut T (가변 참조) | ❌   | 스택 | 포인터 크기 |
| String             | ❌   | 힙   | 가변        |
| Vec<T>             | ❌   | 힙   | 가변        |

> 출처: doc.rust-lang.org/std/primitive.char.html
> "char is always four bytes in size."

### char 4바이트 근거

```
char = Unicode scalar value (U+0000 ~ U+D7FF, U+E000 ~ U+10FFFF)
     = UTF-32 단일 코드 포인트
     = 항상 4바이트 고정 (ASCII도 4바이트로 저장)
```

### NLL (Non-Lexical Lifetime)

- Rust 2018 Edition 도입 (1.31), 모든 Edition에 완전 활성화는 **Rust 1.63**.
- 참조의 생존 범위를 블록이 아닌 **마지막 사용 시점**으로 계산.
- 결과: 같은 스코프 내에서 불변 참조 종료 후 가변 참조 허용.

```rust
let mut s = String::from("hello");
let r1 = &s;
println!("{}", r1); // r1 마지막 사용 (NLL: 여기서 생존 종료)
let r2 = &mut s;   // OK: r1이 더 이상 사용되지 않으므로
```

### 라이프타임 Elision Rules (3개)

| 규칙 | 조건                          | 동작                                |
|------|-------------------------------|-------------------------------------|
| 1    | 입력 참조마다 별도 라이프타임 | `fn f(x: &str, y: &str)` → `'a, 'b` |
| 2    | 입력 참조 1개                 | 출력 라이프타임 = 입력 라이프타임   |
| 3    | &self/&mut self 존재          | 출력 라이프타임 = self 라이프타임   |

> 출처: doc.rust-lang.org/reference/lifetime-elision.html

## 3. 동시성 핵심 사실

### 스레드 스택 크기

```
기본 스택: 2 MiB (Tier-1 플랫폼 기준, platform-dependent)
```

> 출처: doc.rust-lang.org/std/thread/index.html
> "Currently, it is 2 MiB on all Tier-1 platforms."

- 8MB라고 알려진 것은 **Linux pthread 기본값** (Rust 스레드가 아님).
- Rust의 `std::thread::spawn`은 2 MiB.
- `Builder::stack_size()`로 변경 가능.

### Tokio 태스크 메모리

```
태스크당: 단일 할당 + 64 bytes
```

> 출처: tokio.rs/tokio/tutorial/spawning
> "They require only a single allocation and 64 bytes of memory."

### tokio::join! vs tokio::spawn 차이

| 항목      | `tokio::join!`               | `tokio::spawn`              |
|-----------|------------------------------|-----------------------------|
| 실행 방식 | 동시성 (같은 태스크)         | 별도 태스크 (병렬 가능)     |
| 병렬 여부 | ❌ (단일 스레드 내 인터리빙) | ✅ (work-stealing 스케줄러) |
| 취소      | Err 발생해도 모두 완료 대기  | 독립적                      |
| 반환값    | 모두 완료 후 튜플 반환       | JoinHandle                  |

> 출처: docs.rs/tokio/latest/tokio/macro.join.html
> "concurrently on the same task... not in parallel"

### mpsc vs crossbeam 채널

| 항목 | `std::sync::mpsc`   | `crossbeam::channel`   |
|------|---------------------|------------------------|
| 패턴 | MPSC (단일 수신자)  | MPMC (다중 수신자)     |
| 버퍼 | unbounded           | bounded/unbounded 선택 |
| 클론 | sender만 clone 가능 | sender/receiver 모두   |
| 성능 | 표준                | 고성능 (lock-free)     |

## 4. 에러 처리 핵심 사실

### thiserror 2.x

- 1.x → 2.x: major version bump (2024).
- `#[from]` 속성으로 `From` 트레이트 자동 구현.
- `#[error("message {field}")]`로 Display 자동 구현.
- Cargo.toml: `thiserror = "2"` (대부분 호환, #[error] / #[from] 문법 동일)

> 출처: docs.rs/thiserror

### anyhow Context

```rust
use anyhow::{Context, Result};

// with_context: lazy 평가 (실패 시에만 메시지 생성)
let content = fs::read_to_string(path)
    .with_context(|| format!("Cannot read: {}", path))?;

// bail!: 즉시 Err 반환
anyhow::bail!("No servers found in {}", path);

// {:#}: 에러 체인 전체 출력
eprintln!("ERROR: {:#}", e);
```

## 5. 크레이트 Breaking Changes

### reqwest 0.12 → 0.13

- `ClientBuilder` API 일부 변경.
- TLS 백엔드 기본값 변경 (rustls 기본화 진행).
- `json()` feature는 동일하게 사용 가능.

```toml
reqwest = { version = "0.13", features = ["json"] }
```

### axum 0.7 → 0.8

- `axum::serve()` API는 0.7/0.8 모두 동일하게 사용 가능.
- `Router::with_state()` → `Router::route()` + `State` extractor 패턴 동일.
- Handler signature 일부 변경.

```toml
axum = "0.8"
```

### signal-hook 0.3 → 0.4

- `Signals::new(&[SIGTERM])` → API 동일, 내부 구조 개선.
- `iterator::Signals` 경로 유지.

```toml
signal-hook = "0.4"
```

### nix 0.29 → 0.31

- feature 플래그 분리 강화.
- `nix = { version = "0.31", features = ["fs", "process", "signal"] }` 권장.

## 6. Cargo 주요 옵션

### profile.release 옵션

| 옵션            | 기본값   | 권장 (배포) | 효과             |
|-----------------|----------|-------------|------------------|
| `opt-level`     | 3        | 3           | 최대 최적화      |
| `lto`           | false    | true        | 10~20% 크기 감소 |
| `strip`         | none     | "symbols"   | 30~50% 크기 감소 |
| `codegen-units` | 16       | 1           | 최적화 개선      |
| `panic`         | "unwind" | "abort"     | 크기 감소        |

> 출처: doc.rust-lang.org/cargo/reference/profiles.html

### static 링크 (musl)

```bash
rustup target add x86_64-unknown-linux-musl
cargo build --release --target x86_64-unknown-linux-musl
# 결과: glibc 의존 없는 정적 바이너리
```

## 7. 표준 라이브러리 주요 사실

### fs::rename atomic 보장 조건

- **같은 파일시스템** 내에서만 atomic 보장 (POSIX rename(2) 기반).
- 다른 마운트 포인트 간 rename → `io::ErrorKind::Other` 에러.
- Windows: Windows 10 1607+ + FileRenameInfoEx 지원 시 atomic.

> 출처: doc.rust-lang.org/std/fs/fn.rename.html

### LazyLock (Rust 1.80+)

- `std::sync::LazyCell`의 thread-safe 버전 (OnceLock과 무관).
- `lazy_static` 크레이트 대체 가능.
- `static` 변수에 사용하는 표준 방식.

```rust
use std::sync::LazyLock;
use regex::Regex;

static RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\d+").unwrap()
});
```

## 8. 트레이트 핵심 사실

### impl Trait vs dyn Trait

| 항목          | `impl Trait` (정적) | `dyn Trait` (동적)    |
|---------------|---------------------|-----------------------|
| 디스패치      | 컴파일 타임         | 런타임 (vtable)       |
| 바이너리 크기 | 타입별 코드 복제    | 공유 코드             |
| 이종 컬렉션   | 불가                | `Vec<Box<dyn Trait>>` |
| object safety | 불필요              | Object-safe trait만   |

### Object Safety 조건

- 메서드가 `Sized` 바운드를 요구하지 않아야 함.
- 메서드가 제네릭 타입 매개변수를 사용하지 않아야 함.
- `Self` 반환 타입 없어야 함 (단, `Box<Self>` 가능).

## 9. 버전별 주요 기능 추가

| Rust 버전 | 기능                               |
|-----------|------------------------------------|
| 1.65      | let-else, GAT (Generic Assoc Type) |
| 1.70      | OnceCell/OnceLock 안정화           |
| 1.75      | async fn in trait 안정화           |
| 1.80      | LazyLock, LazyCell 안정화          |
| 1.82      | `&raw const/mut` 안정화            |
| 1.85      | edition 2024 출시                  |


# Rust 소유권과 빌림

Rust의 핵심 개념인 소유권(Ownership), 빌림(Borrowing), 라이프타임(Lifetime)을 정리합니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. 소유권 개요](#1-소유권-개요) / [2. 소유권 규칙](#2-소유권-규칙) / [3. Move와 Copy](#3-move와-copy)   |
| [4. 빌림 (Borrowing)](#4-빌림-borrowing) / [5. 라이프타임](#5-라이프타임) / [6. 실전 패턴](#6-실전-패턴) |
| [7. 자주하는 실수](#7-자주하는-실수) / [8. SE 관점 활용](#8-se-관점-활용) / [9. 요약](#9-요약)           |

---

## 1. 소유권 개요

### 왜 소유권이 필요한가

| 언어   | 메모리 관리        | 문제점                         |
|--------|--------------------|--------------------------------|
| C/C++  | 수동 malloc/free   | use-after-free, double free    |
| Java   | GC (가비지 컬렉터) | GC pause, 메모리 오버헤드      |
| Python | GC (참조 카운팅)   | 성능 오버헤드, 순환 참조       |
| Rust   | 소유권 시스템      | 컴파일 타임에 메모리 안전 보장 |

Rust는 GC 없이 컴파일러가 메모리 해제 시점을 결정합니다. 런타임 비용 없이 메모리 안전을 보장합니다.

### 핵심 개념

```
┌──────────────────────────────────────────────────────────────────┐
│                    Stack                                         │
│  ┌─────────┐                                                     │
│  │ owner   │──────> Heap data                                    │
│  └─────────┘        (auto-drop when owner goes out of scope)     │
└──────────────────────────────────────────────────────────────────┘






```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 소유권 규칙

Rust의 소유권 규칙 3가지:

1. 모든 값은 **소유자(owner)**가 정확히 하나 존재합니다.
2. 소유자가 **스코프를 벗어나면** 값이 드롭(drop)됩니다.
3. 한 시점에 소유자는 **하나만** 존재합니다.

### 스코프와 드롭

```rust
fn main() {
    {
        let s = String::from("hello"); // s가 소유자
        println!("{}", s);
    } // s가 스코프를 벗어남 → drop() 호출 → 힙 메모리 해제

    // println!("{}", s); // 컴파일 에러: s는 이미 해제됨
}
```

### Drop 타이밍

| 상황                 | Drop 시점                     |
|----------------------|-------------------------------|
| 변수가 스코프 벗어남 | 블록(`{}`) 끝                 |
| 명시적 drop          | `drop(value)` 호출 시         |
| Move 발생            | 이전 소유자는 무효화 (drop X) |
| 함수에 전달          | 함수 종료 시 drop             |

[⬆ 목차로 돌아가기](#목차)

---

## 3. Move와 Copy

### Move (이동)

```rust
let s1 = String::from("hello");
let s2 = s1; // s1의 소유권이 s2로 이동 (move)

// println!("{}", s1); // 컴파일 에러! s1은 더 이상 유효하지 않음
println!("{}", s2);    // OK
```

### Copy (복사)

스택에만 저장되는 타입은 Copy 트레이트가 구현되어 있어 자동 복사됩니다.

```rust
let x = 5;
let y = x; // Copy! x도 y도 유효

println!("x={}, y={}", x, y); // 둘 다 사용 가능
```

### Copy가 되는 타입

| 타입                | Copy | 이유                |
|---------------------|------|---------------------|
| i32, u64, f64, bool | ✅   | 스택 고정 크기      |
| char                | ✅   | 4바이트 고정        |
| (i32, i32) 튜플     | ✅   | 내부 요소 모두 Copy |
| &T (불변 참조)      | ✅   | 포인터 복사만       |
| String              | ❌   | 힙 데이터 소유      |
| Vec<T>              | ❌   | 힙 데이터 소유      |
| &mut T              | ❌   | 가변 참조는 하나만  |

### Clone (명시적 깊은 복사)

```rust
let s1 = String::from("hello");
let s2 = s1.clone(); // 힙 데이터까지 복제

println!("s1={}, s2={}", s1, s2); // 둘 다 유효
```

🟡 `clone()`은 비용이 있습니다. 힙 데이터 전체를 복사하므로 대용량 데이터에서는 주의합니다.

### 함수와 소유권

```rust
fn take_ownership(s: String) {
    println!("{}", s);
} // s가 drop됨

fn make_copy(n: i32) {
    println!("{}", n);
} // n은 Copy이므로 원본에 영향 없음

fn main() {
    let s = String::from("hello");
    take_ownership(s);
    // println!("{}", s); // 에러! s는 이동됨

    let n = 42;
    make_copy(n);
    println!("{}", n); // OK! i32는 Copy
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 빌림 (Borrowing)

소유권을 넘기지 않고 **참조**로 빌려주는 것입니다.

### 불변 참조 (&T)

```rust
fn calculate_length(s: &String) -> usize {
    s.len()
} // s는 참조만 빌린 것, drop되지 않음

fn main() {
    let s = String::from("hello");
    let len = calculate_length(&s); // &s: 불변 참조 전달
    println!("'{}' length = {}", s, len); // s 여전히 유효
}
```

### 가변 참조 (&mut T)

```rust
fn append_world(s: &mut String) {
    s.push_str(", world");
}

fn main() {
    let mut s = String::from("hello");
    append_world(&mut s);
    println!("{}", s); // "hello, world"
}
```

### 빌림 규칙

| 규칙                                    | 이유               |
|-----------------------------------------|--------------------|
| 불변 참조는 여러 개 동시 가능 (&T 다수) | 읽기만 하므로 안전 |
| 가변 참조는 하나만 가능 (&mut T 1개)    | 데이터 레이스 방지 |
| 불변 참조와 가변 참조 동시 불가         | 읽는 중 수정 방지  |

```rust
let mut s = String::from("hello");

let r1 = &s;     // OK: 불변 참조 1
let r2 = &s;     // OK: 불변 참조 2
// let r3 = &mut s; // 에러! 불변 참조가 있는 동안 가변 참조 불가

println!("{}, {}", r1, r2);
// r1, r2 여기서 마지막 사용 (NLL: Non-Lexical Lifetime)

let r3 = &mut s; // OK: r1, r2가 더 이상 사용되지 않으므로
r3.push_str(" world");
```

### 댕글링 참조 방지

```rust
// fn dangle() -> &String {        // 컴파일 에러!
//     let s = String::from("hello");
//     &s                            // s가 drop되면 참조가 무효화됨
// }

fn no_dangle() -> String {
    let s = String::from("hello");
    s // 소유권을 이동 (move)하여 반환
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 라이프타임

### 라이프타임이란

참조가 유효한 범위를 컴파일러에게 알려주는 표기입니다. 대부분 컴파일러가 자동 추론하지만, 모호한 경우 명시합니다.

### 기본 문법

```rust
// 'a: 라이프타임 매개변수
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}
```

의미: 반환된 참조의 수명은 `x`와 `y` 중 **짧은 쪽**과 동일합니다.

### 라이프타임 생략 규칙 (Elision Rules)

컴파일러가 자동으로 추론하는 3가지 규칙:

| 규칙 | 조건                              | 적용                                |
|------|-----------------------------------|-------------------------------------|
| 1    | 각 입력 참조에 별도 라이프타임    | `fn f(x: &str, y: &str)` → `'a, 'b` |
| 2    | 입력 참조가 1개면 출력에 적용     | `fn f(x: &str) -> &str` → 동일 'a   |
| 3    | `&self`/`&mut self`면 출력에 적용 | 메서드의 self 라이프타임 적용       |

```rust
// 이 두 시그니처는 동일합니다:
fn first_word(s: &str) -> &str { ... }
fn first_word<'a>(s: &'a str) -> &'a str { ... }
```

### 구조체에서의 라이프타임

```rust
struct Config<'a> {
    filename: &'a str,
    verbose: bool,
}

fn main() {
    let name = String::from("/etc/hosts");
    let config = Config {
        filename: &name,
        verbose: true,
    };
    println!("file: {}", config.filename);
}
```

🟡 구조체가 참조를 포함하면 라이프타임을 명시해야 합니다. 처음에는 `String`을 소유하는 것이 더 간단합니다.

### 'static 라이프타임

프로그램 전체 수명과 동일한 참조입니다.

```rust
let s: &'static str = "hello"; // 문자열 리터럴은 항상 'static

// 바이너리에 포함된 데이터이므로 프로그램 종료까지 유효
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 실전 패턴

### 패턴 1: 읽기만 할 때 — 불변 참조

```rust
fn print_config(config: &HashMap<String, String>) {
    for (key, value) in config {
        println!("{} = {}", key, value);
    }
}
```

### 패턴 2: 수정할 때 — 가변 참조

```rust
fn add_default_config(config: &mut HashMap<String, String>) {
    config.entry("timeout".to_string())
          .or_insert("30".to_string());
}
```

### 패턴 3: 소유권 이전이 필요할 때 — 값으로 전달

```rust
fn spawn_worker(config: Config) -> JoinHandle<()> {
    // 스레드에 소유권 이전 (스레드가 독립적으로 사용)
    thread::spawn(move || {
        process(config);
    })
}
```

### 패턴 4: 선택적 소유 — Cow (Clone on Write)

```rust
use std::borrow::Cow;

fn normalize_path(path: &str) -> Cow<str> {
    if path.contains("//") {
        Cow::Owned(path.replace("//", "/")) // 수정 필요: 새 String 생성
    } else {
        Cow::Borrowed(path) // 수정 불필요: 참조만 반환
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 자주하는 실수

### 실수 1: Move 후 사용

```rust
// ❌ 잘못된 코드
let path = String::from("/etc/nginx/nginx.conf");
let backup = path; // move!
// println!("original: {}", path); // 컴파일 에러

// ✅ 올바른 코드
let path = String::from("/etc/nginx/nginx.conf");
let backup = path.clone(); // 명시적 복사
println!("original: {}", path); // OK
```

### 실수 2: 루프에서 소유권 이동

```rust
// ❌ 잘못된 코드
let files = vec!["a.log", "b.log", "c.log"];
let names = files.into_iter().map(String::from).collect::<Vec<_>>();
// for f in files { ... } // 에러! files는 into_iter()로 소비됨

// ✅ 올바른 코드 (참조로 순회)
let files = vec!["a.log", "b.log", "c.log"];
for f in &files {
    println!("{}", f);
}
// files 여전히 사용 가능
```

### 실수 3: 함수에서 참조 반환 시 라이프타임 누락

```rust
// ❌ 컴파일 에러
// fn get_name() -> &str {
//     let name = String::from("server01");
//     &name // name이 함수 끝에서 drop → 댕글링 참조
// }

// ✅ 소유권을 반환
fn get_name() -> String {
    String::from("server01")
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. SE 관점 활용

### 설정 파일 파싱

```rust
use std::collections::HashMap;
use std::fs;

fn parse_config(path: &str) -> HashMap<String, String> {
    let content = fs::read_to_string(path)
        .expect("Failed to read config");

    content.lines()
        .filter(|line| !line.starts_with('#') && line.contains('='))
        .map(|line| {
            let mut parts = line.splitn(2, '=');
            let key = parts.next().unwrap().trim().to_string();
            let value = parts.next().unwrap().trim().to_string();
            (key, value)
        })
        .collect()
}
```

### 로그 파일 처리 (참조로 효율적 파싱)

```rust
fn extract_errors(log_content: &str) -> Vec<&str> {
    log_content.lines()
        .filter(|line| line.contains("ERROR") || line.contains("FATAL"))
        .collect()
}

fn main() {
    let log = fs::read_to_string("/var/log/app.log").unwrap();
    let errors = extract_errors(&log); // log의 참조를 빌림
    println!("Found {} errors", errors.len());
}
```

### 서버 리스트 관리

```rust
struct Server {
    hostname: String,
    ip: String,
    port: u16,
}

fn find_by_hostname<'a>(servers: &'a [Server], name: &str) -> Option<&'a Server> {
    servers.iter().find(|s| s.hostname == name)
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 요약

| 개념          | 핵심                                   | 언제 사용                    |
|---------------|----------------------------------------|------------------------------|
| Ownership     | 값의 소유자는 하나, 스코프 끝에서 drop | 항상 (Rust 기본 동작)        |
| Move          | 소유권 이전, 이전 변수 무효화          | String, Vec 등 힙 타입       |
| Copy          | 스택 값 복사, 원본 유지                | i32, bool, &T 등             |
| Clone         | 명시적 깊은 복사                       | 원본 유지하면서 복제 필요 시 |
| & (불변 참조) | 읽기만 가능, 여러 개 동시 가능         | 함수에 데이터 전달 (읽기)    |
| &mut (가변)   | 수정 가능, 동시에 하나만               | 함수에서 데이터 수정         |
| Lifetime 'a   | 참조의 유효 범위 표시                  | 컴파일러가 추론 못 할 때     |

### 선택 가이드

```
데이터를 함수에 전달할 때:
  │
  ├── 읽기만? → &T (불변 참조)
  │
  ├── 수정 필요? → &mut T (가변 참조)
  │
  ├── 소유권 이전 필요? → T (값으로 전달)
  │   (스레드 전달, 컬렉션 저장 등)
  │
  └── 조건부 복사? → Cow<T>
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- The Rust Programming Language Ch.4: [doc.rust-lang.org/book/ch04-00-understanding-ownership.html](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html) — ★★★★☆
- Rust by Example - Ownership: [doc.rust-lang.org/rust-by-example/scope.html](https://doc.rust-lang.org/rust-by-example/scope.html) — ★★★☆☆
- Visualizing Rust Ownership: [rufflewind.com/2017-02-15/rust-move-copy-borrow](https://rufflewind.com/2017-02-15/rust-move-copy-borrow) — ★★☆☆☆

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

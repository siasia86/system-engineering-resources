# Rust 핵심 개념
<!-- reference: _reference/rust_official_notes.md -->

Rust의 개념적 뼈대를 정리합니다. 소유권 모델, 타입 시스템, 메모리 모델, 컴파일러 보증 등
"왜 이렇게 동작하는가"에 초점을 맞춥니다. 구체적인 사용법은 각 주제별 파일을 참조합니다.

## 목차

| 섹션                                                                                                                                                 |
|------------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 소유권 모델](#1-소유권-모델) / [2. 타입 시스템](#2-타입-시스템) / [3. 메모리 모델](#3-메모리-모델)                                               |
| [4. 컴파일러 보증](#4-컴파일러-보증) / [5. 제로 코스트 추상화](#5-제로-코스트-추상화) / [6. 에디션 시스템](#6-에디션-시스템)                         |
| [7. 빌드 시스템과 생태계](#7-빌드-시스템과-생태계) / [8. unsafe와 안전성 경계](#8-unsafe와-안전성-경계) / [9. 다른 언어와 비교](#9-다른-언어와-비교) |

---

## 1. 소유권 모델

### 핵심 규칙

Rust의 소유권은 컴파일러가 GC 없이 메모리 안전성을 보장하는 핵심 메커니즘입니다.

```
소유권 3원칙
  1. 모든 값에는 소유자(owner)가 정확히 하나 있습니다.
  2. 소유자가 스코프를 벗어나면 값이 drop됩니다.
  3. 소유권은 이동(move)되거나 빌림(borrow)될 수 있습니다.
```

### Move vs Copy vs Clone

| 방식    | 동작                        | 적용 타입                       | 비고                        |
|---------|-----------------------------|---------------------------------|-----------------------------|
| `Copy`  | 스택 복사, 원본 유지        | i32, f64, bool, char, &T        | 4바이트 이하 또는 참조      |
| `Move`  | 소유권 이전, 원본 무효화    | String, Vec, Box, 커스텀 구조체 | 힙 데이터는 기본 move       |
| `Clone` | 명시적 깊은 복사 `.clone()` | Clone 트레이트 구현 타입        | 비용 발생, 명시적 호출 필요 |

> `char`는 Unicode scalar value를 UTF-32로 저장. 항상 4바이트 고정.
> 출처: doc.rust-lang.org/std/primitive.char.html

### 빌림(Borrowing) 규칙

```
불변 참조 (&T)     →  동시에 여러 개 허용
가변 참조 (&mut T) →  동시에 하나만 허용, 불변 참조와 공존 불가
```

| 상황                   | 허용 여부 |
|------------------------|-----------|
| 불변 참조 여러 개      | ✅        |
| 가변 참조 하나         | ✅        |
| 불변 + 가변 참조 동시  | ❌        |
| 가변 참조 둘 이상 동시 | ❌        |

### NLL (Non-Lexical Lifetime)

Rust 1.63+에서 전체 활성화. 참조 생존 범위를 블록이 아닌 **마지막 사용 시점**으로 계산합니다.

```rust
let mut s = String::from("hello");
let r1 = &s;
println!("{}", r1);  // r1 마지막 사용 → 여기서 생존 종료
let r2 = &mut s;     // OK: r1이 더 이상 사용되지 않음 (NLL)
```

NLL 이전(lexical lifetime)에는 `r1`의 스코프가 블록 끝까지 유지되어 `r2`와 충돌했습니다.

### 라이프타임 Elision Rules

컴파일러가 라이프타임을 자동 추론하는 3가지 규칙입니다.

| 규칙 | 조건                       | 동작                              |
|------|----------------------------|-----------------------------------|
| 1    | 입력 참조마다              | 별도 라이프타임 부여 (`'a`, `'b`) |
| 2    | 입력 참조가 정확히 1개     | 출력 라이프타임 = 입력            |
| 3    | `&self` / `&mut self` 존재 | 출력 라이프타임 = self            |

3가지 규칙으로 해소되지 않으면 명시적 라이프타임 표기가 필요합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 타입 시스템

### 타입 분류

```
Rust 타입 분류
  ├── 스칼라(Scalar)
  │   ├── 정수: i8/u8 ~ i128/u128, isize/usize
  │   ├── 부동소수: f32, f64
  │   ├── 불리언: bool (1 byte)
  │   └── 문자: char (4 bytes, UTF-32)
  ├── 복합(Compound)
  │   ├── 튜플: (T1, T2, ...)  — 고정 크기, 이종 타입
  │   └── 배열: [T; N]         — 고정 크기, 동종 타입 (스택)
  ├── 소유 타입(Owned)
  │   ├── String    — 힙, 가변 UTF-8
  │   ├── Vec<T>    — 힙, 가변 배열
  │   └── Box<T>    — 힙 할당 포인터
  └── 참조/슬라이스
      ├── &str      — 문자열 슬라이스 (참조)
      └── &[T]      — 슬라이스 (참조)
```

### 스택 vs 힙

| 항목      | 스택                        | 힙                          |
|-----------|-----------------------------|-----------------------------|
| 할당 방식 | 컴파일 타임 고정 크기       | 런타임 동적 크기            |
| 속도      | 빠름 (포인터 이동만)        | 상대적으로 느림 (allocator) |
| Copy 타입 | 기본 수치, 참조, bool, char | 해당 없음                   |
| Drop 시점 | 스코프 종료 즉시            | 소유자 drop 시              |

### 트레이트 디스패치

| 방식          | 문법         | 디스패치 시점 | 이종 컬렉션 |
|---------------|--------------|---------------|-------------|
| 정적 디스패치 | `impl Trait` | 컴파일 타임   | ❌          |
| 동적 디스패치 | `dyn Trait`  | 런타임 vtable | ✅          |

동적 디스패치 사용 시 `Box<dyn Trait>` 또는 `&dyn Trait` 형태로 사용합니다.
Object-safe trait만 `dyn`으로 사용 가능합니다.

#### Object Safety 조건

- 메서드가 `Sized` 바운드를 요구하지 않습니다.
- 메서드가 제네릭 타입 매개변수를 사용하지 않습니다.
- `Self`를 직접 반환하지 않습니다 (`Box<Self>` 허용).

### 제네릭 단형화(Monomorphization)

```
제네릭 함수 → 컴파일 타임에 사용된 타입별로 별도 코드 생성
→ 런타임 오버헤드 없음 (zero-cost)
→ 바이너리 크기 증가 가능
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 메모리 모델

### 메모리 영역

```
프로세스 메모리
  ├── 스택 (Stack)    — 함수 프레임, 지역 변수, Copy 타입
  ├── 힙   (Heap)     — Box, String, Vec, Arc 등 동적 할당
  ├── 정적 (Static)   — 'static 라이프타임 데이터, 리터럴
  └── 코드 (Text)     — 컴파일된 바이너리
```

### 스마트 포인터 비교

| 타입         | 소유권 | 스레드 안전 | 용도                             |
|--------------|--------|-------------|----------------------------------|
| `Box<T>`     | 단독   | ✅          | 힙 할당, 재귀 타입, trait object |
| `Rc<T>`      | 공유   | ❌          | 단일 스레드 참조 카운팅          |
| `Arc<T>`     | 공유   | ✅          | 멀티 스레드 참조 카운팅          |
| `Cell<T>`    | 단독   | ❌          | Copy 타입 내부 가변성            |
| `RefCell<T>` | 단독   | ❌          | 런타임 빌림 검사, 내부 가변성    |
| `Mutex<T>`   | 공유   | ✅          | 멀티 스레드 내부 가변성          |
| `RwLock<T>`  | 공유   | ✅          | 읽기 다수 / 쓰기 단독            |

### 내부 가변성 (Interior Mutability)

컴파일러 빌림 규칙을 우회하여 불변 참조로 내부 값을 변경하는 패턴입니다.

```
외부 불변성 (컴파일 타임) + 내부 가변성 (런타임 검사)
  ├── RefCell<T>  — 단일 스레드, 런타임 패닉 가능
  ├── Cell<T>     — Copy 타입 전용, get/set
  └── Mutex<T>    — 멀티 스레드, lock 실패 시 Err
```

🟡 `RefCell<T>`은 빌림 규칙을 런타임으로 미룹니다. 위반 시 `panic!` 발생합니다.

### Drop과 메모리 해제

```
값의 drop 순서
  1. 변수: 선언의 역순 (LIFO)
  2. 구조체 필드: 선언 순서
  3. 튜플/배열: 앞에서 뒤로
```

`Drop::drop()`을 직접 호출하는 것은 금지됩니다. 조기 해제는 `drop(value)` 함수를 사용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 컴파일러 보증

### 컴파일 타임에 차단하는 버그 유형

| 버그 유형        | C/C++         | Rust                         |
|------------------|---------------|------------------------------|
| Use after free   | 런타임        | ✅ 컴파일 에러               |
| Double free      | 런타임        | ✅ 컴파일 에러               |
| Null dereference | 런타임        | ✅ Option<T>으로 표현        |
| Buffer overflow  | 런타임        | ✅ 슬라이스 범위 검사        |
| Data race        | 런타임        | ✅ 컴파일 에러 (Send + Sync) |
| Use after move   | 정의되지 않음 | ✅ 컴파일 에러               |

### Send + Sync 트레이트

| 트레이트 | 의미                                  | 자동 구현 조건     |
|----------|---------------------------------------|--------------------|
| `Send`   | 소유권을 다른 스레드로 이전 가능      | 모든 필드가 `Send` |
| `Sync`   | 참조를 여러 스레드에서 동시 접근 가능 | 모든 필드가 `Sync` |

```
Send 아닌 타입: Rc<T>, RefCell<T>, raw pointer
Sync 아닌 타입: Cell<T>, RefCell<T>, UnsafeCell<T>
```

### Rust 보증의 한계

컴파일러가 보증하지 않는 항목입니다.

| 항목          | 설명                                     |
|---------------|------------------------------------------|
| 논리적 정확성 | 비즈니스 로직 버그는 프로그래머 책임     |
| 데드락        | Mutex 잘못된 순서 획득 시 데드락 가능    |
| 정수 오버플로 | debug: panic, release: wrapping (기본값) |
| 무한 루프     | 컴파일러가 차단하지 않음                 |
| I/O 에러      | 런타임 에러, Result로 처리               |

🟡 release 빌드에서 정수 오버플로는 wrapping 동작입니다. 명시적 처리가 필요하면 `checked_add()` 등을 사용합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 제로 코스트 추상화

### 개념

> "What you don't use, you don't pay for.
> What you do use, you couldn't hand-code any better."
> — Bjarne Stroustrup (C++ 원칙, Rust도 동일 채택)

고수준 추상화가 저수준 코드와 동일한 성능을 냅니다.

| 추상화        | 런타임 비용 | 구현 방식                   |
|---------------|-------------|-----------------------------|
| 제네릭        | 없음        | 단형화(monomorphization)    |
| 이터레이터    | 없음        | 컴파일 타임 인라인 + 최적화 |
| 클로저        | 없음        | 구조체 + 트레이트로 변환    |
| `impl Trait`  | 없음        | 정적 디스패치               |
| `dyn Trait`   | vtable 조회 | 런타임 포인터 역참조        |
| `async/await` | 없음        | 상태 머신으로 변환          |

### 이터레이터 최적화 예시

```rust
// 고수준 표현
let sum: i32 = (0..1000).filter(|x| x % 2 == 0).map(|x| x * 2).sum();

// 컴파일러가 생성하는 코드와 동일한 수준
let mut sum = 0;
for x in 0..1000 {
    if x % 2 == 0 { sum += x * 2; }
}
```

LLVM 최적화 후 두 코드는 동일한 어셈블리를 생성합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 에디션 시스템

### 에디션 개요

에디션은 언어 수준 호환성 단위입니다. 크레이트 단위로 적용되며, 서로 다른 에디션의 크레이트는 동일 바이너리에 혼재 가능합니다.

| 에디션 | 출시 Rust 버전 | 주요 변경                                                           |
|--------|----------------|---------------------------------------------------------------------|
| 2015   | 1.0            | 초기 에디션                                                         |
| 2018   | 1.31           | NLL 기본 활성화, `mod.rs` 불필요, use path 개선                     |
| 2021   | 1.56           | Closure capture 개선, array `IntoIterator`                          |
| 2024   | 1.85           | `gen` 키워드 예약, `async` 클로저 안정화, RPIT 라이프타임 캡처 규칙 |

```toml
# Cargo.toml
[package]
edition = "2024"   # cargo new 기본값 (Rust 1.85+)
```

🟡 에디션 변경은 코드 파괴를 유발할 수 있습니다. `cargo fix --edition`으로 자동 마이그레이션이 가능합니다.

### MSRV (Minimum Supported Rust Version)

라이브러리는 지원하는 최소 Rust 버전을 명시합니다.

```toml
[package]
rust-version = "1.70"   # MSRV 명시
```

| 기능                                     | 필요 Rust 버전 |
|------------------------------------------|----------------|
| NLL migrate mode 제거 (모든 에디션 적용) | 1.63           |
| OnceLock                                 | 1.70           |
| async fn in trait                        | 1.75           |
| LazyLock                                 | 1.80           |
| Edition 2024                             | 1.85           |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 빌드 시스템과 생태계

### Cargo 핵심 개념

```
Cargo 역할
  ├── 빌드: cargo build / cargo build --release
  ├── 의존성: Cargo.toml + Cargo.lock
  ├── 테스트: cargo test
  ├── 문서: cargo doc
  ├── 배포: cargo publish (crates.io)
  └── 스크립트: build.rs (빌드 전 실행)
```

### Cargo.lock 관리 원칙

| 프로젝트 유형 | Cargo.lock 커밋 여부 | 이유                          |
|---------------|----------------------|-------------------------------|
| 바이너리      | ✅ 커밋              | 재현 가능한 빌드 보장         |
| 라이브러리    | ❌ .gitignore        | 사용자가 버전 결정하도록 위임 |

### 빌드 프로파일

| 프로파일     | 명령어                  | opt-level | 용도              |
|--------------|-------------------------|-----------|-------------------|
| `dev` (기본) | `cargo build`           | 0         | 개발, 빠른 컴파일 |
| `release`    | `cargo build --release` | 3         | 배포, 최대 성능   |
| `test`       | `cargo test`            | 0         | 테스트            |
| `bench`      | `cargo bench`           | 3         | 벤치마크          |

#### 배포 최적화 권장 설정

```toml
[profile.release]
opt-level = 3
lto = true            # 10~20% 크기 감소
strip = "symbols"     # 30~50% 크기 감소
codegen-units = 1     # 최적화 개선 (빌드 느려짐)
panic = "abort"       # unwind 코드 제거
```

### 정적 바이너리 (musl)

```bash
rustup target add x86_64-unknown-linux-musl
cargo build --release --target x86_64-unknown-linux-musl
# glibc 의존 없는 정적 바이너리 → Alpine, Docker scratch 이미지에 적합
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. unsafe와 안전성 경계

### unsafe가 허용하는 것

```
unsafe 블록에서만 가능한 5가지
  1. raw pointer 역참조 (*const T, *mut T)
  2. unsafe 함수/메서드 호출
  3. 가변 정적 변수 접근
  4. unsafe trait 구현
  5. union 필드 접근
```

unsafe는 컴파일러 보증을 프로그래머가 직접 책임지는 계약입니다. 가능한 작은 범위로 제한합니다.

### 안전한 추상화 패턴

```rust
// unsafe를 캡슐화하여 안전한 공개 API 제공
pub fn split_at<T>(slice: &[T], mid: usize) -> (&[T], &[T]) {
    assert!(mid <= slice.len());
    unsafe {
        (
            std::slice::from_raw_parts(slice.as_ptr(), mid),
            std::slice::from_raw_parts(slice.as_ptr().add(mid), slice.len() - mid),
        )
    }
}
```

### FFI (Foreign Function Interface)

```rust
extern "C" {
    fn abs(input: i32) -> i32;
}

fn main() {
    unsafe {
        println!("{}", abs(-3));  // C 함수 호출은 unsafe
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 다른 언어와 비교

### 메모리 관리 방식 비교

| 언어    | 메모리 관리                   | 런타임 비용    | 안전성           |
|---------|-------------------------------|----------------|------------------|
| C/C++   | 수동 (malloc/free)            | 없음           | 프로그래머 책임  |
| Java/Go | GC                            | STW pause 있음 | 보장             |
| Python  | GC (레퍼런스 카운팅 + 사이클) | 높음           | 보장             |
| Rust    | 소유권 (컴파일 타임)          | 없음           | 컴파일 타임 보장 |

### 에러 처리 방식 비교

| 언어     | 방식                | 강제 처리 여부 |
|----------|---------------------|----------------|
| C        | 반환값 (int, errno) | ❌             |
| C++/Java | 예외 (exception)    | ❌             |
| Go       | (value, error) 튜플 | ❌             |
| Rust     | `Result<T, E>`, `?` | ✅ 컴파일 강제 |

### Go vs Rust 선택 기준

| 기준        | Rust 선택                     | Go 선택                   |
|-------------|-------------------------------|---------------------------|
| 메모리 제어 | 커널 수준, 임베디드, 드라이버 | 일반 서버, 마이크로서비스 |
| 성능 요구   | 나노초 레이턴시, C 수준 필요  | 밀리초 레이턴시로 충분    |
| 학습 곡선   | 감수 가능                     | 빠른 팀 온보딩 필요       |
| 동시성 모델 | 세밀한 제어 필요              | goroutine으로 충분        |
| 생태계      | 시스템/인프라 도구            | 웹 서버, DevOps 도구      |

> SE 실무 선택 기준 상세는 [rust_roadmap_for_se.md](../rust_roadmap_for_se.md) 참조.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Rust Book: [doc.rust-lang.org/book](https://doc.rust-lang.org/book/) — ★★★★☆
- Rust Reference: [doc.rust-lang.org/reference](https://doc.rust-lang.org/reference/) — ★★★★☆
- Rustonomicon (unsafe): [doc.rust-lang.org/nomicon](https://doc.rust-lang.org/nomicon/) — ★★★☆☆
- [ownership_borrowing.md](./ownership_borrowing.md)
- [traits_generics.md](./traits_generics.md)
- [concurrency.md](./concurrency.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-31

**마지막 업데이트**: 2026-07-31

© 2026 siasia86. Licensed under CC BY 4.0.

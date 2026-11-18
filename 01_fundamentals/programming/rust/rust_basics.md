# Rust 기초 문법
<!-- reference: _reference/rust_official_notes.md -->

변수, 타입, 문자열, 제어문, 함수, 구조체, 열거형, 컬렉션, 모듈까지 Rust 문법의 기초를 bash·python과 비교하며 정리합니다. 소유권·빌림은 이 문서에서 필요한 만큼만 다루고 [소유권과 빌림](./ownership_borrowing.md)에서 자세히 설명합니다. 개발 환경 설치는 [전환 가이드 3절](./rust_for_bash_python_se.md#3-개발-환경)을 참고합니다.

## 목차

| 섹션                                                                                                                                |
|-------------------------------------------------------------------------------------------------------------------------------------|
| [1. 프로그램 구조](#1-프로그램-구조) / [2. 변수와 가변성](#2-변수와-가변성) / [3. 기본 타입](#3-기본-타입) / [4. 문자열](#4-문자열) |
| [5. 제어문](#5-제어문) / [6. 함수](#6-함수) / [7. 구조체](#7-구조체) / [8. 열거형과 match](#8-열거형과-match)                       |
| [9. 컬렉션](#9-컬렉션) / [10. 모듈](#10-모듈) / [11. 출력과 포맷](#11-출력과-포맷) / [12. 종합 예제](#12-종합-예제)                 |

---

## 1. 프로그램 구조

```rust
// src/main.rs
fn main() {
    println!("hello, rust");
}
```

| 항목    | bash                     | python                                              | Rust                               |
|---------|--------------------------|-----------------------------------------------------|------------------------------------|
| 시작점  | 파일 첫 줄부터 실행      | 파일 첫 줄부터 (관례상 `if __name__ == "__main__"`) | `fn main()`                        |
| 문장 끝 | 줄바꿈                   | 줄바꿈                                              | `;` (마지막 식은 `;` 없이 값이 됨) |
| 블록    | `then`…`fi`, `do`…`done` | 들여쓰기                                            | `{ }`                              |
| 주석    | `#`                      | `#`                                                 | `//`, `/* */`, 문서 주석 `///`     |
| 실행    | `bash x.sh`              | `python3 x.py`                                      | `cargo run` (컴파일 후 실행)       |

`println!`처럼 이름 끝에 `!`가 붙은 것은 함수가 아니라 매크로입니다. 처음에는 "인수 개수가 자유로운 특수 함수" 정도로 이해해도 됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 변수와 가변성

```rust
fn main() {
    let host = "web01";          // 기본은 불변
    let mut retries = 0;         // 바꿀 변수는 mut
    retries += 1;

    let port: u16 = 8080;        // 타입을 직접 적을 수도 있음
    const MAX_RETRIES: u32 = 3;  // 상수: 타입 필수, 대문자 관례

    let input = "42";            // 같은 이름으로 다시 선언(섀도잉)
    let input: i32 = input.parse().unwrap();

    println!("{host}:{port} retries={retries}/{MAX_RETRIES} input={input}");
}
```

출력: `web01:8080 retries=1/3 input=42`

| 개념             | bash·python                          | Rust                                             |
|------------------|--------------------------------------|--------------------------------------------------|
| 변경 가능 여부   | 모든 변수 변경 가능                  | 기본 불변, `mut`을 붙여야 변경 가능              |
| 타입             | bash는 문자열, python은 실행 중 결정 | 컴파일 때 결정. 대부분 추론되고 필요할 때만 적음 |
| 같은 이름 재선언 | 덮어쓰기                             | 섀도잉: 새 변수를 만들며 타입도 바꿀 수 있음     |
| 상수             | `readonly`, 관례상 대문자            | `const`                                          |

기본이 불변인 이유는 "어디서 값이 바뀌는지"를 `mut`만 찾으면 알 수 있게 하기 위해서입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 기본 타입

| 분류           | 타입                                  | 예              | 비고                         |
|----------------|---------------------------------------|-----------------|------------------------------|
| 부호 있는 정수 | `i8` `i16` `i32` `i64` `i128` `isize` | `-5`            | 정수 기본은 `i32`            |
| 부호 없는 정수 | `u8` `u16` `u32` `u64` `u128` `usize` | `8080u16`       | 인덱스·길이는 `usize`        |
| 실수           | `f32` `f64`                           | `0.75`          | 기본 `f64`                   |
| 불리언         | `bool`                                | `true`          |                              |
| 문자           | `char`                                | `'가'`          | 유니코드 문자 1개 (4바이트)  |
| 튜플           | `(T, U, ...)`                         | `("web01", 22)` | 여러 타입 묶음               |
| 배열           | `[T; N]`                              | `[0u8; 4]`      | 길이 고정. 가변 길이는 `Vec` |

```rust
fn main() {
    let used: u64 = 750;
    let total: u64 = 1000;
    let ratio = used as f64 / total as f64;      // 정수 → 실수는 as로 명시
    let pct = (ratio * 100.0).round() as u8;

    let big: i64 = 300;
    let small = u8::try_from(big);               // 범위를 넘으면 Err
    println!("{pct}% {small:?}");

    let (name, port) = ("web01", 22);            // 튜플 분해
    let octets = [10, 0, 0, 1];
    println!("{name}:{port} first={}", octets[0]);
}
```

출력:

```
75% Err(TryFromIntError(PosOverflow))
web01:22 first=10
```

정수 타입끼리는 자동 변환이 없습니다. `u64 + u32`는 컴파일 오류이며 `as`나 `try_from`으로 맞춥니다. 디버그 빌드에서 정수가 넘치면(오버플로) 프로그램이 멈추므로(panic), 의도한 감싸기 연산은 `wrapping_add`, 넘침을 확인하려면 `checked_add`를 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 문자열

Rust에는 문자열 타입이 두 가지 있습니다.

| 타입     | 의미                                            | 비유                                 |
|----------|-------------------------------------------------|--------------------------------------|
| `String` | 내용을 소유하고 늘리거나 바꿀 수 있는 문자열    | python의 `str` 객체 하나를 가진 상태 |
| `&str`   | 어딘가에 있는 문자열을 빌려 보는 읽기 전용 참조 | 문자열의 한 구간을 가리키는 보기     |

```rust
fn main() {
    let literal: &str = "ERROR disk full";        // 문자열 리터럴은 &str
    let mut line = String::from("host=");         // 소유 문자열
    line.push_str("web01");
    line += ",port=22";

    let owned: String = literal.to_string();      // &str → String
    let view: &str = &owned;                      // String → &str (빌림)

    println!("{line}");
    println!("{}", view.to_lowercase());
    println!("starts={} len={}", literal.starts_with("ERROR"), literal.len());

    for part in line.split(',') {
        if let Some((k, v)) = part.split_once('=') {
            println!("{k} -> {v}");
        }
    }

    let name = "서버01";
    println!("bytes={} chars={}", name.len(), name.chars().count());
}
```

출력:

```
host=web01,port=22
error disk full
starts=true len=15
host -> web01
port -> 22
bytes=8 chars=4
```

| 작업           | python            | Rust                                      |
|----------------|-------------------|-------------------------------------------|
| 붙이기         | `a + b`, f-string | `push_str`, `+=`, `format!`               |
| 나누기         | `s.split(",")`    | `s.split(',')` (반복자)                   |
| 앞뒤 공백 제거 | `s.strip()`       | `s.trim()`                                |
| 포함 여부      | `"x" in s`        | `s.contains("x")`                         |
| 바꾸기         | `s.replace(a, b)` | `s.replace(a, b)`                         |
| 숫자로         | `int(s)`          | `s.parse::<i32>()` (실패하면 `Err`)       |
| 글자 수        | `len(s)`          | `s.chars().count()` (`len()`은 바이트 수) |

- 함수 인수로 문자열을 받을 때는 보통 `&str`로 받습니다. `String`과 `&str`을 모두 넘길 수 있습니다.
- `s[0]`처럼 숫자로 한 글자를 꺼낼 수 없습니다. UTF-8에서 한 글자가 여러 바이트일 수 있기 때문이며, `s.chars().nth(0)`이나 `s.get(0..3)`을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 제어문

### if는 값을 만든다

```rust
fn main() {
    let usage = 92;
    let level = if usage >= 90 { "critical" } else if usage >= 70 { "warning" } else { "ok" };
    println!("{level}");
}
```

출력: `critical`

조건에 괄호가 필요 없고, 조건은 반드시 `bool`이어야 합니다. bash처럼 빈 문자열이나 0을 거짓으로 보지 않습니다.

### 반복

```rust
fn main() {
    let hosts = ["web01", "web02", "db01"];

    for h in hosts {                           // 컬렉션 순회
        print!(" {h}");
    }
    println!();

    for (i, h) in hosts.iter().enumerate() {   // 인덱스와 함께
        if h.starts_with("db") { continue; }
        print!(" {i}:{h}");
    }
    println!();

    for n in 1..=3 {                           // 범위 1, 2, 3
        print!(" {n}");
    }
    println!();

    let mut tries = 0;
    let result = loop {                        // 무한 반복, break로 값 반환
        tries += 1;
        if tries == 3 { break tries * 10; }
    };

    let mut left = 2;
    while left > 0 { left -= 1; }
    println!("result={result} left={left}");
}
```

출력:

```
 web01 web02 db01
 0:web01 1:web02
 1 2 3
result=30 left=0
```

| bash                | python                  | Rust                                         |
|---------------------|-------------------------|----------------------------------------------|
| `for h in a b c`    | `for h in hosts:`       | `for h in hosts`                             |
| `for i in {1..3}`   | `for i in range(1, 4):` | `for i in 1..=3` (끝 포함), `1..4` (끝 제외) |
| `while true`        | `while True:`           | `loop`                                       |
| `break`, `continue` | `break`, `continue`     | `break`, `continue`, `break 값`              |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 함수

```rust
fn disk_level(used: u64, total: u64) -> &'static str {
    let pct = used * 100 / total;
    if pct >= 90 {
        return "critical";                // 중간에 빠져나갈 때 return
    }
    if pct >= 70 { "warning" } else { "ok" }   // 마지막 식이 반환값 (; 없음)
}

fn add_suffix(name: &str, suffix: &str) -> String {
    format!("{name}.{suffix}")
}

fn bump(counter: &mut u32) {              // 호출한 쪽 변수를 바꾸려면 &mut
    *counter += 1;
}

fn main() {
    println!("{}", disk_level(95, 100));
    println!("{}", disk_level(50, 100));
    println!("{}", add_suffix("web01", "internal"));

    let mut c = 0;
    bump(&mut c);
    bump(&mut c);
    println!("c={c}");
}
```

출력:

```
critical
ok
web01.internal
c=2
```

| 항목               | python         | Rust                                      |
|--------------------|----------------|-------------------------------------------|
| 정의               | `def f(a, b):` | `fn f(a: T, b: U) -> R`                   |
| 인수·반환 타입     | 선택 (힌트)    | 인수 타입 필수, 반환이 있으면 `-> R` 필수 |
| 반환               | `return x`     | 마지막 식(`;` 없음) 또는 `return x;`      |
| 기본값·키워드 인수 | 지원           | 없음. 구조체나 빌더 패턴으로 대신         |
| 여러 값 반환       | 튜플           | 튜플 `(a, b)`                             |

`&'static str`은 "프로그램이 끝날 때까지 살아 있는 문자열 참조"로, 문자열 리터럴을 반환할 때 쓰는 타입입니다. 수명(`'static` 같은 표기)은 [소유권과 빌림](./ownership_borrowing.md)에서 다룹니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 구조체

python의 클래스·`dataclass`에 해당합니다. 데이터는 `struct`, 메서드는 `impl` 블록에 따로 적습니다.

```rust
#[derive(Debug, Clone, PartialEq)]
struct Server {
    name: String,
    port: u16,
    healthy: bool,
}

impl Server {
    fn new(name: &str, port: u16) -> Self {      // 생성 함수 (관례상 new)
        Server { name: name.to_string(), port, healthy: true }
    }

    fn address(&self) -> String {                 // 읽기 메서드: &self
        format!("{}:{}", self.name, self.port)
    }

    fn mark_down(&mut self) {                     // 수정 메서드: &mut self
        self.healthy = false;
    }
}

fn main() {
    let mut s = Server::new("web01", 443);
    println!("{}", s.address());
    s.mark_down();
    println!("{s:?}");

    let backup = Server { name: "web02".into(), ..s.clone() };   // 나머지 필드 복사
    println!("same={}", backup == s);
}
```

출력:

```
web01:443
Server { name: "web01", port: 443, healthy: false }
same=false
```

| 항목        | python                | Rust                                                                  |
|-------------|-----------------------|-----------------------------------------------------------------------|
| 정의        | `class`, `@dataclass` | `struct` + `impl`                                                     |
| 생성자      | `__init__`            | 관례상 `fn new(...) -> Self`                                          |
| 자기 자신   | `self`                | `&self` (읽기), `&mut self` (수정), `self` (소비)                     |
| 출력용 표현 | `__repr__`            | `#[derive(Debug)]` 후 `{:?}`                                          |
| 비교        | `__eq__`              | `#[derive(PartialEq)]`                                                |
| 상속        | 클래스 상속           | 없음. 공통 동작은 트레이트([트레이트와 제네릭](./traits_generics.md)) |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 열거형과 match

Rust의 `enum`은 값마다 다른 데이터를 담을 수 있습니다. `match`는 모든 경우를 처리해야 컴파일되므로, 새 상태를 추가하면 처리하지 않은 곳을 컴파일러가 알려 줍니다.

```rust
#[derive(Debug)]
enum Check {
    Ok,
    Warn(u8),                         // 값 하나
    Fail { code: i32, msg: String },  // 이름 붙은 필드
}

fn describe(c: &Check) -> String {
    match c {
        Check::Ok => "ok".to_string(),
        Check::Warn(p) if *p >= 90 => format!("warn (high {p}%)"),   // 조건 붙은 갈래
        Check::Warn(p) => format!("warn {p}%"),
        Check::Fail { code, msg } => format!("fail {code}: {msg}"),
    }
}

fn main() {
    let results = vec![
        Check::Ok,
        Check::Warn(75),
        Check::Warn(95),
        Check::Fail { code: 2, msg: "timeout".into() },
    ];
    for r in &results {
        println!("{}", describe(r));
    }

    let code = 404;
    let kind = match code {
        200..=299 => "success",
        301 | 302 => "redirect",
        400..=499 => "client error",
        _ => "other",                 // 나머지 모두
    };
    println!("{kind}");
}
```

출력:

```
ok
warn 75%
warn (high 95%)
fail 2: timeout
client error
```

### Option: 값이 없을 수 있음

python의 `None`에 해당합니다. `Option<T>`는 `Some(값)` 또는 `None`이며, 꺼내기 전에 반드시 처리해야 합니다.

```rust
fn find_port(name: &str) -> Option<u16> {
    match name {
        "ssh" => Some(22),
        "https" => Some(443),
        _ => None,
    }
}

fn main() {
    if let Some(p) = find_port("ssh") {          // 있을 때만 처리
        println!("ssh={p}");
    }
    let p = find_port("ftp").unwrap_or(0);       // 없으면 기본값
    println!("ftp={p}");
}
```

출력:

```
ssh=22
ftp=0
```

실패 이유까지 전달하는 `Result<T, E>`와 `?` 연산자는 [에러 처리](./error_handling.md)에서 다룹니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 컬렉션

| 용도           | python              | Rust                                                    |
|----------------|---------------------|---------------------------------------------------------|
| 가변 길이 목록 | `list`              | `Vec<T>`                                                |
| 키-값          | `dict`              | `HashMap<K, V>` (순서 없음), `BTreeMap<K, V>` (키 순서) |
| 집합           | `set`               | `HashSet<T>`, `BTreeSet<T>`                             |
| 양끝 큐        | `collections.deque` | `VecDeque<T>`                                           |

```rust
use std::collections::HashMap;

fn main() {
    let mut ports: Vec<u16> = vec![443, 22, 80];
    ports.push(8080);
    ports.sort();
    println!("{ports:?} len={} first={:?}", ports.len(), ports.first());

    let web: Vec<u16> = ports.iter().filter(|p| **p != 22).copied().collect();
    println!("{web:?}");

    let lines = ["ERROR a", "INFO b", "ERROR c", "WARN d"];
    let mut count: HashMap<&str, u32> = HashMap::new();
    for l in lines {
        let level = l.split_whitespace().next().unwrap_or("-");
        *count.entry(level).or_insert(0) += 1;     // 없으면 0으로 만들고 더하기
    }

    let mut keys: Vec<_> = count.keys().collect();
    keys.sort();
    for k in keys {
        println!("{k}={}", count[k]);
    }
    println!("has DEBUG={}", count.contains_key("DEBUG"));
}
```

출력:

```
[22, 80, 443, 8080] len=4 first=Some(22)
[80, 443, 8080]
ERROR=2
INFO=1
WARN=1
has DEBUG=false
```

- `ports.first()`처럼 없을 수도 있는 값은 `Option`으로 돌아옵니다. `ports[10]`처럼 범위를 넘는 인덱스는 panic이므로, 확실하지 않으면 `ports.get(10)`을 씁니다.
- `iter().filter(...).collect()`는 python의 리스트 컴프리헨션에 해당하는 반복자 체인입니다.
- `HashMap` 순회 순서는 정해져 있지 않습니다. 출력 순서가 필요하면 키를 정렬하거나 `BTreeMap`을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 모듈

코드를 나누는 단위입니다. 기본은 비공개이며 밖에서 쓸 것에만 `pub`을 붙입니다.

```rust
mod check {
    pub fn disk(pct: u8) -> &'static str {
        if pct >= 90 { "critical" } else { level_ok() }
    }

    fn level_ok() -> &'static str {     // pub 없음: 모듈 안에서만 사용
        "ok"
    }

    pub mod net {
        pub fn port_open(port: u16) -> bool {
            port == 22 || port == 443
        }
    }
}

use check::net::port_open;

fn main() {
    println!("{}", check::disk(95));
    println!("{}", port_open(22));
}
```

출력:

```
critical
true
```

실제 프로젝트에서는 파일로 나눕니다.

```
myapp/
├── Cargo.toml
└── src/
    ├── main.rs        mod check; 로 아래 파일을 불러옴
    ├── check.rs       check 모듈 (pub fn disk ...)
    └── check/
        └── net.rs     check::net 모듈 (check.rs에 pub mod net;)
```

| 개념            | python        | Rust                                   |
|-----------------|---------------|----------------------------------------|
| 파일 하나       | 모듈          | 모듈 (`mod 이름;`으로 선언해야 포함됨) |
| 가져오기        | `import a.b`  | `use a::b;`                            |
| 공개 범위       | `_이름` 관례  | `pub` 키워드 (컴파일러가 강제)         |
| 패키지          | 패키지·배포판 | 크레이트 (`Cargo.toml` 하나)           |
| 외부 라이브러리 | `pip install` | `cargo add 크레이트`                   |

[⬆ 목차로 돌아가기](#목차)

---

## 11. 출력과 포맷

```rust
fn main() {
    let host = "web01";
    let cpu = 12.3456;
    let mem = 734u32;

    println!("{host} cpu={cpu:.1}% mem={mem}MB");     // 소수점 1자리
    println!("[{host:<8}] [{mem:>6}] [{mem:06}]");    // 왼쪽·오른쪽 정렬, 0 채움
    println!("{:?} {:#x}", ("a", 1), 255);            // 디버그 출력, 16진수
    eprintln!("to stderr");                           // 표준 오류

    let msg = format!("{host}:{}", 22);               // 출력하지 않고 String 만들기
    println!("{msg}");
}
```

표준 출력:

```
web01 cpu=12.3% mem=734MB
[web01   ] [   734] [000734]
("a", 1) 0xff
web01:22
```

| python                        | Rust                            |
|-------------------------------|---------------------------------|
| `print(f"{x}")`               | `println!("{x}")`               |
| `print(x, end="")`            | `print!("{x}")`                 |
| `print(..., file=sys.stderr)` | `eprintln!(...)`                |
| `f"{x:.2f}"`, `f"{x:>8}"`     | `"{x:.2}"`, `"{x:>8}"`          |
| `repr(x)`                     | `"{x:?}"` (타입에 `Debug` 필요) |
| `str.format` 결과 저장        | `format!(...)`                  |

[⬆ 목차로 돌아가기](#목차)

---

## 12. 종합 예제

`df -P` 형식 텍스트에서 사용률이 기준 이상인 마운트를 찾는 예입니다. 지금까지의 문법(구조체, `Option`, 문자열 처리, `Vec`, 반복자, 포맷)을 함께 씁니다.

```rust
#[derive(Debug)]
struct Mount {
    target: String,
    used_pct: u8,
}

fn parse_line(line: &str) -> Option<Mount> {
    let cols: Vec<&str> = line.split_whitespace().collect();
    if cols.len() < 6 {
        return None;
    }
    let used_pct = cols[4].trim_end_matches('%').parse::<u8>().ok()?;   // 실패하면 None
    Some(Mount { target: cols[5].to_string(), used_pct })
}

fn main() {
    let df = "\
Filesystem 1024-blocks Used Available Capacity Mounted on
/dev/sda1 1000 950 50 95% /
/dev/sdb1 1000 400 600 40% /data
tmpfs 100 85 15 85% /run";

    let threshold = 80;
    let mut alerts: Vec<Mount> = df
        .lines()
        .skip(1)                                  // 머리글 건너뛰기
        .filter_map(parse_line)                   // None은 버리고 Some만
        .filter(|m| m.used_pct >= threshold)
        .collect();
    alerts.sort_by_key(|m| std::cmp::Reverse(m.used_pct));   // 사용률 내림차순

    for m in &alerts {
        println!("{:<6} {:>3}%", m.target, m.used_pct);
    }
    println!("alerts={}", alerts.len());
}
```

출력:

```
/       95%
/run    85%
alerts=2
```

같은 일을 bash로 하면 `df -P | awk 'NR>1 && $5+0 >= 80 {print $6, $5}'` 한 줄입니다. 이 정도 작업은 bash가 낫고, Rust는 이 처리가 큰 도구의 일부이거나 결과를 구조체로 다뤄야 할 때 의미가 있습니다([전환 가이드 1절](./rust_for_bash_python_se.md#1-언제-rust를-쓰는가)).

### 다음 단계

| 순서 | 문서                                      | 이 문서와의 관계                                 |
|------|-------------------------------------------|--------------------------------------------------|
| 1    | [소유권과 빌림](./ownership_borrowing.md) | `&`, `&mut`, `.clone()`, `'static`이 왜 필요한지 |
| 2    | [에러 처리](./error_handling.md)          | `unwrap` 대신 `Result`와 `?`                     |
| 3    | [트레이트와 제네릭](./traits_generics.md) | `derive`, 공통 동작, 제네릭 함수                 |
| 4    | [Rust 핵심 개념](./rust_key_concepts.md)  | 타입·메모리 모델 전체 정리                       |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- The Rust Programming Language 3~8장(문법 기초, 구조체, 열거형, 모듈, 컬렉션): [doc.rust-lang.org/book](https://doc.rust-lang.org/book/) — ★★★☆☆
- Rust by Example: [doc.rust-lang.org/rust-by-example](https://doc.rust-lang.org/rust-by-example/) — ★★★☆☆
- `std::fmt` 포맷 문법: [doc.rust-lang.org/std/fmt](https://doc.rust-lang.org/std/fmt/) — ★★★☆☆
- `std::collections`: [doc.rust-lang.org/std/collections](https://doc.rust-lang.org/std/collections/) — ★★★☆☆
- 공식 사실 정리: [Rust 공식 문서 참조 노트](../../../_reference/rust_official_notes.md)

확인일: 2026-11-18. 이 문서의 Rust 예제는 모두 Rust 1.100.0(공식 `rust:1.100-slim` 이미지)에서 컴파일·실행했고, 적어 둔 출력은 실제 실행 결과입니다.

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-18

**마지막 업데이트**: 2026-11-18

© 2026 siasia86. Licensed under CC BY 4.0.

# bash·python 사용자를 위한 Rust 전환 가이드
<!-- reference: _reference/rust_official_notes.md -->

bash·python으로 인프라 작업을 해 온 SE가 Rust를 시작할 때 필요한 대응표와 비교 예제입니다. 학습 기간 전체 계획은 [SE를 위한 Rust 학습 로드맵](../rust_roadmap_for_se.md), 개념 설명은 [Rust 핵심 개념](./rust_key_concepts.md)에 있습니다.

## 목차

| 섹션                                                                                                                             |
|----------------------------------------------------------------------------------------------------------------------------------|
| [1. 언제 Rust를 쓰는가](#1-언제-rust를-쓰는가) / [2. 사고방식 차이](#2-사고방식-차이) / [3. 개발 환경](#3-개발-환경)             |
| [4. 도구 대응표](#4-도구-대응표) / [5. 작업별 대응표](#5-작업별-대응표) / [6. 같은 작업 세 언어 비교](#6-같은-작업-세-언어-비교) |
| [7. 처음 막히는 지점](#7-처음-막히는-지점) / [8. 첫 4주 계획](#8-첫-4주-계획)                                                    |

---

## 1. 언제 Rust를 쓰는가

세 언어는 대체 관계가 아니라 역할이 다릅니다. bash·python을 버리는 것이 아니라 Rust가 나은 자리에만 씁니다.

| 상황                                                  | 권장   | 이유                                             |
|-------------------------------------------------------|--------|--------------------------------------------------|
| 명령 몇 개를 잇는 일회성 작업, 배포 훅                | bash   | 가장 짧고 어디에나 있음                          |
| API 호출, 데이터 가공, 빠른 자동화                    | python | 라이브러리가 많고 수정이 빠름                    |
| 여러 서버에 배포할 상시 실행 에이전트·exporter        | Rust   | 런타임 없는 단일 바이너리, 메모리 사용 예측 가능 |
| GB 단위 로그 처리, 높은 처리량 프록시                 | Rust   | GC 없는 성능, 안전한 병렬 처리                   |
| Python 버전·venv가 서버마다 달라 배포가 번거로운 도구 | Rust   | 정적 링크 바이너리 하나만 복사                   |
| 잘못 동작하면 피해가 큰 도구(삭제, 권한 변경)         | Rust   | 타입·빌림 검사가 실수를 컴파일 단계에서 차단     |

옮기지 않는 편이 나은 경우도 있습니다.

- 200줄 미만이고 잘 동작하는 bash·python 스크립트
- 요구가 자주 바뀌는 실험 단계 도구
- 팀에 Rust를 읽을 사람이 없어 유지보수를 넘길 수 없는 도구

[⬆ 목차로 돌아가기](#목차)

## 2. 사고방식 차이

| 항목           | bash                      | python                  | Rust                                      |
|----------------|---------------------------|-------------------------|-------------------------------------------|
| 실행           | 해석 실행                 | 해석 실행 (바이트코드)  | 컴파일 후 실행                            |
| 타입           | 모두 문자열               | 동적 타입 (힌트는 선택) | 정적 타입, 대부분 추론                    |
| 오류 처리      | 종료 코드, `set -e`       | 예외 (`try`/`except`)   | 반환 값 `Result<T, E>`, `?` 연산자        |
| 값 없음        | 빈 문자열                 | `None`                  | `Option<T>` (처리하지 않으면 컴파일 오류) |
| 메모리         | 신경 쓰지 않음            | GC                      | 소유권 규칙으로 컴파일 시 결정            |
| 오류 발견 시점 | 실행 중                   | 실행 중                 | 대부분 컴파일 중                          |
| 의존성         | 시스템 명령               | pip + venv              | Cargo (`Cargo.toml`, `Cargo.lock`)        |
| 배포           | 스크립트 복사 + 명령 설치 | 인터프리터 + 패키지     | 바이너리 하나                             |

가장 큰 변화는 "실행해 보고 고친다"에서 "컴파일러가 통과시킬 때까지 고친다"로 바뀌는 것입니다. 처음에는 느리게 느껴지지만, 컴파일된 뒤에는 bash의 따옴표 실수나 python의 `KeyError` 같은 실행 중 오류가 크게 줄어듭니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 개발 환경

### 설치 (Ubuntu·Rocky Linux 공통)

Rust 컴파일러는 링크 단계에서 C 링커(`cc`)를 씁니다. 먼저 설치합니다.

```bash
# Ubuntu
sudo apt install -y build-essential

# Rocky Linux
sudo dnf install -y gcc
```

```bash
# 공식 설치 스크립트 (rustup). 사용자 홈의 ~/.cargo, ~/.rustup에 설치
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"

rustc --version
cargo --version
rustup component add clippy rustfmt rust-analyzer
```

### 첫 프로젝트

```bash
cargo new logcount          # 바이너리 프로젝트 (src/main.rs)
cd logcount
cargo run -- /var/log/syslog   # -- 뒤는 프로그램 인수
cargo build --release          # 결과: target/release/logcount
```

| 명령                               | 하는 일                                          |
|------------------------------------|--------------------------------------------------|
| `cargo check`                      | 바이너리를 만들지 않고 컴파일 검사만 (가장 빠름) |
| `cargo clippy`                     | 흔한 실수·비권장 패턴 경고                       |
| `cargo fmt`                        | 코드 정렬                                        |
| `cargo test`                       | 단위·통합 테스트 실행                            |
| `cargo add clap --features derive` | 의존성 추가                                      |

배포용 정적 바이너리(musl)는 [Rust 핵심 개념의 정적 바이너리 절](./rust_key_concepts.md#정적-바이너리-musl)을 참고합니다.

[⬆ 목차로 돌아가기](#목차)

## 4. 도구 대응표

| 용도        | bash             | python                               | Rust                                    |
|-------------|------------------|--------------------------------------|-----------------------------------------|
| 의존성 선언 | 없음 (설치 문서) | `requirements.txt`, `pyproject.toml` | `Cargo.toml`                            |
| 의존성 고정 | 없음             | `pip freeze`, lock 파일              | `Cargo.lock`                            |
| 격리 환경   | 없음             | `venv`                               | 프로젝트별 `target/` (별도 환경 불필요) |
| 정적 검사   | `shellcheck`     | `ruff`, `pylint`, `mypy`             | 컴파일러 + `cargo clippy`               |
| 포맷        | `shfmt`          | `black`, `ruff format`               | `cargo fmt`                             |
| 테스트      | `bats`           | `pytest`                             | `cargo test`                            |
| 배포 묶음   | 없음             | `pyinstaller`, wheel                 | `cargo build --release`                 |
| 문서        | 주석             | docstring, Sphinx                    | `///` 주석, `cargo doc`                 |

[⬆ 목차로 돌아가기](#목차)

## 5. 작업별 대응표

Rust 열의 크레이트는 `cargo add`로 추가하는 외부 라이브러리이고, `std::`는 표준 라이브러리입니다.

| 작업             | bash                     | python               | Rust                             |
|------------------|--------------------------|----------------------|----------------------------------|
| 인수 파싱        | `getopts`, `$1`          | `argparse`           | `clap` (derive)                  |
| 환경 변수        | `$VAR`                   | `os.environ`         | `std::env::var`                  |
| 외부 명령 실행   | 직접 실행, `$(...)`      | `subprocess.run`     | `std::process::Command`          |
| 파일 읽기        | `while read`             | `open()`             | `std::fs`, `BufReader`           |
| 디렉토리 순회    | `find`                   | `os.walk`, `pathlib` | `walkdir`                        |
| 경로 조작        | `dirname`, `basename`    | `pathlib.Path`       | `std::path::Path`, `PathBuf`     |
| 정규식           | `grep -E`, `sed`         | `re`                 | `regex`                          |
| JSON             | `jq`                     | `json`               | `serde` + `serde_json`           |
| YAML·TOML        | `yq`                     | `PyYAML`, `tomllib`  | `serde_yaml` 계열, `toml`        |
| HTTP 요청        | `curl`                   | `requests`           | `reqwest`                        |
| 로그 출력        | `logger`, `echo >&2`     | `logging`            | `tracing` + `tracing-subscriber` |
| 시그널 처리      | `trap`                   | `signal`             | `signal-hook`, `tokio::signal`   |
| 병렬 실행        | `xargs -P`, `&` + `wait` | `concurrent.futures` | `std::thread`, `rayon`           |
| 비동기 I/O       | 없음                     | `asyncio`            | `tokio`                          |
| 날짜·시간        | `date`                   | `datetime`           | `chrono`, `std::time`            |
| 종료 코드        | `exit 1`                 | `sys.exit(1)`        | `std::process::ExitCode`         |
| 오류 메시지 묶기 | 실패 시 메시지 함수 호출 | `raise ... from e`   | `anyhow::Context`                |

🟡 `serde_yaml`은 원 저작자가 유지보수를 끝냈습니다. YAML 크레이트는 도입 시점에 유지 상태를 확인하고 고릅니다([크레이트 생태계](./crates_ecosystem.md)).

[⬆ 목차로 돌아가기](#목차)

## 6. 같은 작업 세 언어 비교

### 로그에서 ERROR 줄 세기

```bash
grep -c 'ERROR' /var/log/app.log
```

```python
import sys

count = 0
with open(sys.argv[1], encoding="utf-8", errors="replace") as f:
    for line in f:
        if "ERROR" in line:
            count += 1
print(count)
```

```rust
use std::env;
use std::fs::File;
use std::io::{self, BufRead, BufReader};

fn main() -> io::Result<()> {
    let path = env::args().nth(1).expect("사용법: logcount <파일>");
    let reader = BufReader::new(File::open(&path)?);

    let mut count: u64 = 0;
    for line in reader.lines() {
        if line?.contains("ERROR") {
            count += 1;
        }
    }
    println!("{count}");
    Ok(())
}
```

| 비교점      | 설명                                                                                                                                                                          |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `?`         | 파일 열기·읽기 오류를 호출자(`main`)로 넘김. `main`이 `Err`를 반환하면 오류를 출력하고 종료 코드 1로 끝남                                                                     |
| `BufReader` | python의 `for line in f`처럼 한 줄씩 읽어 큰 파일도 메모리를 적게 씀                                                                                                          |
| UTF-8       | `lines()`는 UTF-8이 아닌 줄에서 오류를 냄. 깨진 바이트가 섞인 로그는 `split(b'\n')`으로 바이트를 읽고 `String::from_utf8_lossy`로 바꿈(python `errors="replace"`와 같은 효과) |

### 외부 명령과 종료 코드

```bash
if ! state=$(systemctl is-active nginx); then
    echo "inactive: ${state}" >&2
    exit 1
fi
echo active
```

```python
import subprocess
import sys

r = subprocess.run(["systemctl", "is-active", "nginx"],
                   capture_output=True, text=True)
if r.returncode != 0:
    print(f"inactive: {r.stdout.strip()}", file=sys.stderr)
    sys.exit(1)
print("active")
```

```rust
use std::process::{Command, ExitCode};

fn main() -> ExitCode {
    let output = match Command::new("systemctl").args(["is-active", "nginx"]).output() {
        Ok(o) => o,
        Err(e) => {
            eprintln!("실행 실패: {e}");
            return ExitCode::from(2);
        }
    };

    if output.status.success() {
        println!("active");
        ExitCode::SUCCESS
    } else {
        let state = String::from_utf8_lossy(&output.stdout);
        eprintln!("inactive: {}", state.trim());
        ExitCode::from(1)
    }
}
```

`Command`는 셸을 거치지 않고 인수를 배열로 넘기므로, bash에서 흔한 따옴표·공백 문제와 셸 주입이 생기지 않습니다. 파이프·리다이렉션이 꼭 필요하면 `Command::new("sh").args(["-c", "..."])`를 쓰되, 외부 입력을 문자열에 붙이지 않습니다.

### JSON 설정 읽기

```bash
jq -r '.hosts[]' config.json
```

```python
import json

with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)
for host in cfg["hosts"]:
    print(f"{host} (timeout {cfg['timeout_secs']}s)")
```

```toml
# Cargo.toml
[dependencies]
anyhow = "1"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

```rust
use anyhow::Context;
use serde::Deserialize;
use std::fs;

#[derive(Debug, Deserialize)]
struct Config {
    hosts: Vec<String>,
    timeout_secs: u64,
    #[serde(default)]
    verbose: bool,
}

fn main() -> anyhow::Result<()> {
    let text = fs::read_to_string("config.json").context("config.json 읽기 실패")?;
    let cfg: Config = serde_json::from_str(&text).context("config.json 형식 오류")?;

    for host in &cfg.hosts {
        println!("{host} (timeout {}s)", cfg.timeout_secs);
    }
    if cfg.verbose {
        eprintln!("{cfg:?}");
    }
    Ok(())
}
```

python은 `timeout_secs`가 빠져 있으면 해당 줄을 실행할 때 `KeyError`가 납니다. Rust는 읽는 순간 구조체로 검사하므로, 필드가 없거나 타입이 다르면 처리 전에 오류를 냅니다. 선택 항목은 `#[serde(default)]`나 `Option<T>`로 표시합니다.

[⬆ 목차로 돌아가기](#목차)

## 7. 처음 막히는 지점

| 컴파일 오류·증상                      | 원인                                    | 처음에 쓰는 해결                                   |
|---------------------------------------|-----------------------------------------|----------------------------------------------------|
| `borrow of moved value`               | 값을 다른 변수·함수로 넘긴 뒤 다시 사용 | 참조(`&value`)로 넘기거나, 일단 `.clone()`         |
| `expected &str, found String`         | 소유 문자열과 빌린 문자열의 구분        | 인수는 `&str`로 받고, 넘길 때 `&s`                 |
| `cannot borrow as mutable`            | 변수에 `mut`이 없거나 빌림이 겹침       | `let mut`, 빌림 범위를 짧게                        |
| `the ? operator can only be used ...` | 함수 반환 타입이 `Result`가 아님        | `fn main() -> anyhow::Result<()>`                  |
| `missing lifetime specifier`          | 참조를 반환하거나 구조체에 보관         | 처음에는 `String`처럼 소유 타입으로 보관           |
| 문자열 인덱싱 `s[0]` 불가             | UTF-8 바이트 경계 보호                  | `s.chars().next()`, `s.get(0..3)`                  |
| 정수 타입 불일치                      | `usize`, `u64`, `i32` 자동 변환 없음    | `u64::try_from(x)?` 또는 확실할 때 `as`            |
| `.unwrap()`에서 panic                 | 오류를 처리하지 않고 꺼냄               | 도구 코드에서는 `?`와 `context`로 바꿈             |
| 컴파일이 느림                         | 의존성 첫 빌드                          | 개발 중에는 `cargo check`, 의존성은 한 번만 빌드됨 |

처음부터 `clone()`과 소유 타입을 피하려고 애쓸 필요는 없습니다. 동작하는 코드를 먼저 만들고, 프로파일링으로 병목이 보일 때 참조로 바꿉니다. 소유권 규칙 자체는 [소유권과 빌림](./ownership_borrowing.md), 오류 처리는 [에러 처리](./error_handling.md)에서 다룹니다.

[⬆ 목차로 돌아가기](#목차)

## 8. 첫 4주 계획

로드맵 Phase 1의 앞부분을 실무 스크립트 하나로 연결한 계획입니다. 주 5~10시간을 기준으로 합니다.

| 주차 | 읽을 것                                                                        | 만들 것                                          |
|------|--------------------------------------------------------------------------------|--------------------------------------------------|
| 1주  | The Rust Programming Language 1~6장, [소유권과 빌림](./ownership_borrowing.md) | 6절 ERROR 세기 도구                              |
| 2주  | Book 8~9장, [에러 처리](./error_handling.md)                                   | 6절 JSON 설정 읽기 + 필드 검사                   |
| 3주  | [CLI 도구 개발](./cli_tools.md)                                                | 평소 쓰는 bash 스크립트 하나를 `clap`으로 옮기기 |
| 4주  | Book 11장, [테스트](./testing.md)                                              | 3주 도구에 테스트와 `cargo clippy` 경고 0건      |

옮길 스크립트는 입력·출력이 분명하고 외부 명령 호출이 적은 것(로그 집계, 설정 검사, 디스크 사용량 보고)이 좋습니다. 4주 뒤에는 [로드맵](../rust_roadmap_for_se.md) Phase 1의 트레이트·제네릭으로 이어 갑니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- Rust 설치(rustup): [rust-lang.org/tools/install](https://www.rust-lang.org/tools/install) — ★★★☆☆
- The Rust Programming Language: [doc.rust-lang.org/book](https://doc.rust-lang.org/book/) — ★★★☆☆
- `std::process::Command`: [doc.rust-lang.org/std/process/struct.Command.html](https://doc.rust-lang.org/std/process/struct.Command.html) — ★★★☆☆
- `std::process::ExitCode`: [doc.rust-lang.org/std/process/struct.ExitCode.html](https://doc.rust-lang.org/std/process/struct.ExitCode.html) — ★★★☆☆
- `BufRead::lines`: [doc.rust-lang.org/std/io/trait.BufRead.html](https://doc.rust-lang.org/std/io/trait.BufRead.html#method.lines) — ★★★☆☆
- Cargo Book: [doc.rust-lang.org/cargo](https://doc.rust-lang.org/cargo/) — ★★★☆☆
- serde: [serde.rs](https://serde.rs/) — ★★★☆☆
- 공식 사실 정리: [Rust 공식 문서 참조 노트](../../../_reference/rust_official_notes.md)

확인일: 2026-11-18. 6절의 Rust 예제 3개는 Rust 1.100.0(공식 `rust:1.100-slim` 이미지)에서 컴파일·실행했고 `cargo clippy -- -D warnings` 경고 0건을 확인했습니다. 3절의 설치 명령은 실행하지 않았습니다.

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

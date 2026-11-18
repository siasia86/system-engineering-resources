# Rust 프로그래밍

SE 실무(CLI 도구, 시스템 에이전트, 네트워크 도구) 관점의 Rust 학습 자료입니다.
기준 버전: **Rust 1.100 / Edition 2024** (2026-11-18 확인, [공식 참조 노트](../../../_reference/rust_official_notes.md))

## 목차

| 섹션                                                                        |
|-----------------------------------------------------------------------------|
| [문서 목록](#문서-목록) / [학습 순서](#학습-순서) / [빠른 참조](#빠른-참조) |

---

## 문서 목록

### 시작
- **[bash·python 사용자를 위한 Rust 전환 가이드](rust_for_bash_python_se.md)** — 언제 Rust를 쓰는지, 도구·작업 대응표, 세 언어 비교 예제, 첫 4주 계획
- **[SE를 위한 Rust 학습 로드맵](../rust_roadmap_for_se.md)** — Phase 1~4 전체 학습 경로
- **[Rust 기초 문법](rust_basics.md)** — 변수·타입·문자열·제어문·함수·구조체·열거형·컬렉션·모듈, bash·python 비교

### 핵심 개념
- **[Rust 핵심 개념](rust_key_concepts.md)** — 소유권 모델, 타입·메모리 모델, 컴파일러 보증, 에디션, Cargo, unsafe
- **[소유권과 빌림](ownership_borrowing.md)** — Ownership, Borrowing, Lifetime
- **[에러 처리](error_handling.md)** — Result, Option, `?` 연산자, thiserror·anyhow
- **[트레이트와 제네릭](traits_generics.md)** — Trait, Generic, impl Trait, dyn Trait

### 시스템·동시성
- **[시스템 프로그래밍](system_programming.md)** — 파일 I/O, 프로세스, 시그널, 환경 변수, FFI
- **[동시성](concurrency.md)** — 스레드, 채널, 동기화, async/await

### 네트워크·생태계
- **[네트워크 프로그래밍](networking.md)** — TCP/UDP, HTTP 클라이언트·서버, DNS
- **[크레이트 생태계](crates_ecosystem.md)** — 실무 핵심 크레이트, Cargo 활용

### 실전
- **[CLI 도구 개발](cli_tools.md)** — clap, 바이너리 배포, 크로스 컴파일
- **[테스트](testing.md)** — 단위·통합 테스트, 모킹, CLI·비동기 테스트
- **[SE 실전 예제](practical_examples.md)** — 업무에 바로 쓰는 예제 모음

[⬆ 목차로 돌아가기](#목차)

## 학습 순서

| 단계 | 문서                                                | 로드맵 단계 |
|------|-----------------------------------------------------|-------------|
| 1    | 전환 가이드 → 기초 문법 → 소유권과 빌림 → 핵심 개념 | Phase 1     |
| 2    | 에러 처리 → 트레이트와 제네릭                       | Phase 1     |
| 3    | 시스템 프로그래밍 → 동시성 → 테스트                 | Phase 2     |
| 4    | 네트워크 프로그래밍 → 크레이트 생태계               | Phase 3     |
| 5    | CLI 도구 개발 → SE 실전 예제                        | Phase 4     |

[⬆ 목차로 돌아가기](#목차)

## 빠른 참조

| 하고 싶은 일     | 명령                                                               |
|------------------|--------------------------------------------------------------------|
| 설치             | [전환 가이드 3절](rust_for_bash_python_se.md#3-개발-환경) (rustup) |
| 새 프로젝트      | `cargo new <이름>`                                                 |
| 컴파일 검사만    | `cargo check`                                                      |
| 실행 (인수 전달) | `cargo run -- <인수>`                                              |
| 배포 빌드        | `cargo build --release`                                            |
| 린트·포맷        | `cargo clippy`, `cargo fmt`                                        |
| 테스트           | `cargo test`                                                       |
| 의존성 추가      | `cargo add <크레이트>`                                             |
| 툴체인 갱신      | `rustup update`                                                    |

[⬆ 목차로 돌아가기](#목차)

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

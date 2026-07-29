# Rust 문서 Fact-check 수정 내역 (2026-07-29)

fact-check 결과 발견된 오류 및 수정 내역을 기록합니다.
최종 수정 완료 후 이 파일을 삭제합니다.

## 수정 완료 항목

| # | 파일                       | 수정 전               | 수정 후                            | 근거                                       |
|---|----------------------------|-----------------------|------------------------------------|--------------------------------------------|
| 1 | `04_concurrency.md`        | `~8MB (스택)`         | `~2MiB (스택, platform-dependent)` | Rust 공식: "2 MiB on all Tier-1 platforms" |
| 2 | `04_concurrency.md`        | `~수 KB`              | `~64 bytes (Tokio 태스크)`         | Tokio 공식: "64 bytes of memory"           |
| 3 | `06_networking.md`         | `reqwest = "0.12"`    | `reqwest = "0.13"`                 | crates.io: 0.13.4 (2026-07-29 확인)        |
| 4 | `06_networking.md`         | `axum = "0.7"`        | `axum = "0.8"`                     | crates.io: 0.8.9 (2026-07-29 확인)         |
| 5 | `05_system_programming.md` | `signal-hook = "0.3"` | `signal-hook = "0.4"`              | crates.io: 0.4.4 (2026-07-29 확인)         |
| 6 | `05_system_programming.md` | `nix = "0.29"`        | `nix = "0.31"`                     | crates.io: 0.31.3 (2026-07-29 확인)        |

## 검증 통과 (주요 기술 주장)

| 항목                          | 출처                                           | 판정 |
|-------------------------------|------------------------------------------------|------|
| char = 4바이트 고정           | doc.rust-lang.org/std/primitive.char.html      | ✅   |
| &T Copy / &mut T non-Copy     | doc.rust-lang.org/std/primitive.reference.html | ✅   |
| NLL Rust 2018+ 기본 활성화    | doc.rust-lang.org/edition-guide                | ✅   |
| Elision Rules 3개             | doc.rust-lang.org/reference/lifetime-elision   | ✅   |
| tokio::join! 동시성 (비병렬)  | docs.rs/tokio/macro.join.html                  | ✅   |
| tokio::spawn 병렬 실행 가능   | docs.rs/tokio/fn.spawn.html                    | ✅   |
| RwLock 다중 읽기 허용         | doc.rust-lang.org/std/sync/struct.RwLock.html  | ✅   |
| rename atomic (같은 fs 한정)  | doc.rust-lang.org/std/fs/fn.rename.html        | ✅   |
| LazyLock stable 1.80+         | doc.rust-lang.org/std/sync/struct.LazyLock     | ✅   |
| thiserror #[from] → From 자동 | docs.rs/thiserror                              | ✅   |
| anyhow Context/bail           | docs.rs/anyhow                                 | ✅   |
| axum 0.7→0.8 serve API 호환   | docs.rs/axum/0.8.9                             | ✅   |

## 크레이트 버전 현황 (2026-07-29 기준)

| 크레이트    | 문서 사용 버전 | 최신 안정 버전 | 상태    |
|-------------|----------------|----------------|---------|
| tokio       | 1.x            | 1.53.1         | ✅      |
| serde       | 1.x            | 1.0.229        | ✅      |
| reqwest     | 0.13           | 0.13.4         | ✅ 수정 |
| axum        | 0.8            | 0.8.9          | ✅ 수정 |
| clap        | 4.x            | 4.6.4          | ✅      |
| anyhow      | 1.x            | 1.0.104        | ✅      |
| signal-hook | 0.4            | 0.4.4          | ✅ 수정 |
| nix         | 0.31           | 0.31.3         | ✅ 수정 |
| crossbeam   | 0.8.x          | 0.8.4          | ✅      |

---

**작성일**: 2026-07-29

**마지막 업데이트**: 2026-07-29

© 2026 siasia86. Licensed under CC BY 4.0.

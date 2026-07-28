# SE를 위한 Rust 학습 로드맵

시스템 엔지니어 관점에서 Rust를 학습하는 로드맵입니다. 인프라 도구 개발, CLI 유틸리티, 시스템 프로그래밍에 초점을 맞춥니다.

## 목차

| 섹션                                                                                                                                                         |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 왜 SE가 Rust를 배워야 하는가](#1-왜-se가-rust를-배워야-하는가) / [2. 학습 전제 조건](#2-학습-전제-조건) / [3. 단계별 로드맵](#3-단계별-로드맵)           |
| [4. Phase 1: 기초 (1~2개월)](#4-phase-1-기초-12개월) / [5. Phase 2: 시스템 프로그래밍 (2~3개월)](#5-phase-2-시스템-프로그래밍-23개월)                        |
| [6. Phase 3: 네트워크/인프라 (2~3개월)](#6-phase-3-네트워크인프라-23개월) / [7. Phase 4: 실전 프로젝트 (2~3개월)](#7-phase-4-실전-프로젝트-23개월)           |
| [8. SE 실무에서 Rust가 쓰이는 도구](#8-se-실무에서-rust가-쓰이는-도구) / [9. Rust vs Go 선택 기준](#9-rust-vs-go-선택-기준) / [10. 참고 자료](#10-참고-자료) |

---

## 1. 왜 SE가 Rust를 배워야 하는가

| 이유                 | 설명                                                   |
|----------------------|--------------------------------------------------------|
| 인프라 도구 트렌드   | ripgrep, fd, bat, dust, bottom — 기존 도구 대체 가속   |
| 메모리 안전 + 고성능 | C/C++ 수준 성능, 메모리 버그 없음                      |
| 시스템 프로그래밍    | 커널 모듈, eBPF, 네트워크 도구 개발                    |
| 클라우드 네이티브    | Firecracker(AWS Lambda), Bottlerocket, tikv            |
| CVE 감소             | 메모리 안전 언어로 전환하는 업계 흐름 (Linux, Android) |
| 커리어 차별화        | SE + Rust = 시스템 프로그래머 영역 진입 가능           |

### SE에게 Rust가 적합한 영역

| 적합                           | 부적합            |
|--------------------------------|-------------------|
| CLI 도구 (로그 파서, 모니터링) | 웹 프론트엔드     |
| 네트워크 프록시/필터           | CRUD 웹 앱        |
| 시스템 에이전트 (exporter)     | 빠른 프로토타이핑 |
| eBPF 유저스페이스              | 간단한 스크립트   |
| 파일시스템 도구                | 데이터 분석/ML    |
| 고성능 로그 수집기             | 인프라 글루 코드  |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 학습 전제 조건

| 항목           | 필요 수준                              | 확인 방법            |
|----------------|----------------------------------------|----------------------|
| Linux 기초     | 파일시스템, 프로세스, 시그널 이해      | SE라면 이미 충족     |
| C 언어 경험    | 포인터, 메모리 할당 개념 (코딩 불필요) | 개념만 이해하면 충분 |
| Python/Go 경험 | 변수, 함수, 에러 처리 패턴             | 하나라도 사용 경험   |
| Git            | 기본 워크플로우                        | commit/push/branch   |
| 영어 문서 독해 | Rust 생태계는 영문 자료가 압도적       | 공식 Book 읽기 가능  |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 단계별 로드맵

```
Phase 1: 기초 (1~2개월)
  │  Ownership, Borrowing, Lifetime
  │  기본 문법, 에러 처리, 패턴 매칭
  v
Phase 2: 시스템 프로그래밍 (2~3개월)
  │  파일 I/O, 프로세스, 시그널
  │  멀티스레딩, 채널, async
  v
Phase 3: 네트워크/인프라 (2~3개월)
  │  TCP/UDP, HTTP, gRPC
  │  시스템 에이전트, Prometheus exporter
  v
Phase 4: 실전 프로젝트 (2~3개월)
  │  CLI 도구, 모니터링 에이전트
  │  오픈소스 기여
  v
실무 적용
```

**총 소요: 8~11개월** (주 5~10시간 기준)

[⬆ 목차로 돌아가기](#목차)

---

## 4. Phase 1: 기초 (1~2개월)

### 핵심 개념

| 주차  | 주제                    | 핵심 포인트                              |
|-------|-------------------------|------------------------------------------|
| 1~2주 | 소유권 (Ownership)      | move, copy, drop — Rust의 핵심 차별점    |
| 3주   | 참조와 빌림 (Borrowing) | &T, &mut T, 빌림 규칙                    |
| 4주   | 라이프타임 (Lifetime)   | 'a 표기, 함수 시그니처                   |
| 5주   | 에러 처리               | Result<T, E>, ? 연산자, thiserror/anyhow |
| 6주   | 패턴 매칭 + enum        | match, Option, if let                    |
| 7~8주 | 트레이트 + 제네릭       | impl Trait, dyn Trait, where 절          |

### 학습 자료

| 자료                          | 용도             | 비고                  |
|-------------------------------|------------------|-----------------------|
| The Rust Programming Language | 공식 Book (필독) | 챕터 1~12 집중        |
| Rustlings                     | 실습 문제        | 각 개념별 소규모 연습 |
| Rust by Example               | 예제 참조        | 문법 빠르게 확인      |

### SE 관점 연습 과제

```
1. cat 클론 — 파일 읽기 + stdin 처리 + 에러 핸들링
2. wc 클론 — 줄/단어/바이트 카운트
3. 간단한 로그 파서 — regex, 파일 I/O
4. 설정 파일 파서 — serde + TOML/YAML
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. Phase 2: 시스템 프로그래밍 (2~3개월)

### 핵심 주제

| 주제          | 크레이트               | SE 활용 사례                  |
|---------------|------------------------|-------------------------------|
| 파일 I/O      | std::fs, tokio::fs     | 로그 로테이션, 설정 관리      |
| 프로세스 관리 | std::process, nix      | 서비스 래퍼, 프로세스 모니터  |
| 시그널 처리   | signal-hook, ctrlc     | graceful shutdown             |
| 멀티스레딩    | std::thread, rayon     | 병렬 로그 처리                |
| 채널          | crossbeam, tokio::sync | 프로듀서-컨슈머 패턴          |
| async/await   | tokio, async-std       | 비동기 I/O, 네트워크 서버     |
| FFI           | libc, bindgen          | C 라이브러리 호출 (시스템 콜) |

### 학습 순서

```
std::fs (동기 파일 I/O)
  │
  v
std::process (프로세스 생성/관리)
  │
  v
std::thread + crossbeam (멀티스레딩)
  │
  v
tokio (비동기 런타임)
  │
  v
nix crate (POSIX 시스템 콜 래퍼)
```

### SE 관점 연습 과제

```
1. tail -f 클론 — 파일 감시 + 비동기 읽기
2. 프로세스 모니터 — /proc 파싱, CPU/메모리 수집
3. 간단한 cron — 시그널 처리, 프로세스 생성
4. 디스크 사용량 수집기 — statvfs, 임계값 알림
5. 파일 동기화 도구 — inotify + rsync 대체 (간단 버전)
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Phase 3: 네트워크/인프라 (2~3개월)

### 핵심 주제

| 주제               | 크레이트             | SE 활용 사례                |
|--------------------|----------------------|-----------------------------|
| TCP/UDP 소켓       | tokio::net, std::net | 포트 스캐너, 헬스체크       |
| HTTP 클라이언트    | reqwest, hyper       | API 호출, 웹훅              |
| HTTP 서버          | axum, actix-web      | 내부 API, 메트릭 엔드포인트 |
| gRPC               | tonic                | 마이크로서비스 통신         |
| DNS                | trust-dns            | DNS 조회 도구               |
| Prometheus metrics | prometheus-client    | 커스텀 exporter 개발        |
| SSH                | thrussh, russh       | 원격 명령 실행              |

### SE 관점 연습 과제

```
1. TCP 포트 스캐너 — async 병렬 스캔 (nmap 미니 버전)
2. HTTP 헬스체커 — 여러 URL 병렬 체크, 응답 시간 측정
3. Prometheus exporter — 커스텀 메트릭 수집/노출
4. 간단한 리버스 프록시 — L7 로드밸런서 기초
5. SSH 배치 실행기 — 여러 서버에 동시 명령 실행
```

### Prometheus Exporter 예시 구조

```rust
use prometheus_client::metrics::gauge::Gauge;
use prometheus_client::registry::Registry;

// SE가 만들 수 있는 exporter 예시:
// - 디스크 사용량 exporter
// - MySQL 커넥션 수 exporter
// - 프로세스 상태 exporter
// - 네트워크 인터페이스 통계 exporter
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Phase 4: 실전 프로젝트 (2~3개월)

### 프로젝트 아이디어 (SE 실무 기반)

| 프로젝트              | 난이도 | 대체 대상          | 핵심 학습                       |
|-----------------------|--------|--------------------|---------------------------------|
| 로그 수집 에이전트    | ★★★☆☆  | Filebeat 미니 버전 | async I/O, 파일 감시, 버퍼링    |
| 서버 인벤토리 수집기  | ★★☆☆☆  | Ansible facts 대체 | /proc 파싱, JSON 출력, SSH      |
| 설정 파일 diff 도구   | ★★☆☆☆  | diff + 구조 인식   | 파서, TOML/YAML, 트리 비교      |
| 네트워크 진단 도구    | ★★★☆☆  | mtr + ping 통합    | raw socket, ICMP, async         |
| 간단한 로드밸런서     | ★★★★☆  | HAProxy 미니 버전  | TCP proxy, 헬스체크, 라운드로빈 |
| 인프라 변경 감지기    | ★★★☆☆  | AIDE 대체          | 파일 해시, inotify, 알림        |
| MySQL slow query 파서 | ★★☆☆☆  | pt-query-digest    | 파일 파싱, 통계, 정렬           |

### 오픈소스 기여 추천

| 프로젝트 | 영역            | 기여 포인트              |
|----------|-----------------|--------------------------|
| ripgrep  | 검색 도구       | 버그 리포트, 문서 개선   |
| fd       | 파일 찾기       | 기능 추가, 플랫폼 테스트 |
| vector   | 로그 파이프라인 | source/sink 플러그인     |
| bottom   | 시스템 모니터   | 위젯 추가, 버그 수정     |
| nushell  | 셸              | 명령어 추가              |

[⬆ 목차로 돌아가기](#목차)

---

## 8. SE 실무에서 Rust가 쓰이는 도구

### 이미 사용 중인 Rust 도구

| 도구         | 대체 대상 | 용도                 | 성능 차이  |
|--------------|-----------|----------------------|------------|
| ripgrep (rg) | grep      | 코드/로그 검색       | 2~5배 빠름 |
| fd           | find      | 파일 검색            | 5배+ 빠름  |
| bat          | cat       | 구문 강조 출력       | —          |
| dust         | du        | 디스크 사용량 시각화 | —          |
| bottom (btm) | top/htop  | 시스템 모니터        | —          |
| zoxide       | cd        | 스마트 디렉토리 이동 | —          |
| procs        | ps        | 프로세스 목록        | —          |
| delta        | diff      | Git diff 출력 개선   | —          |
| bandwhich    | iftop     | 프로세스별 대역폭    | —          |
| tokei        | cloc      | 코드 라인 카운트     | 10배+ 빠름 |

### 인프라 프로젝트에서의 Rust

| 프로젝트       | 조직    | 용도                           |
|----------------|---------|--------------------------------|
| Firecracker    | AWS     | Lambda/Fargate 마이크로 VM     |
| Bottlerocket   | AWS     | 컨테이너 전용 OS               |
| tikv           | PingCAP | 분산 KV 스토리지 (TiDB 백엔드) |
| Vector         | Datadog | 로그/메트릭 파이프라인         |
| Linkerd2-proxy | Buoyant | 서비스 메시 프록시             |
| Quilkin        | Google  | 게임 서버 프록시               |
| Stratisd       | Red Hat | 스토리지 관리 데몬             |
| sudo-rs        | ISRG    | sudo 재구현 (메모리 안전)      |

[⬆ 목차로 돌아가기](#목차)

---

## 9. Rust vs Go 선택 기준

| 기준              | Rust                      | Go                        |
|-------------------|---------------------------|---------------------------|
| 학습 곡선         | 가파름 (3~6개월)          | 완만 (2~4주)              |
| 빌드 속도         | 느림                      | 빠름                      |
| 런타임 성능       | C/C++ 수준                | 충분히 빠름 (GC 있음)     |
| 메모리 사용       | 최소                      | GC로 인한 오버헤드        |
| 바이너리 크기     | 작음 (static link 시)     | 중간                      |
| 동시성 모델       | async/await + 스레드      | goroutine (CSP)           |
| 에러 처리         | Result<T,E> (강제)        | error interface (관습)    |
| 생태계 (인프라)   | 성장 중                   | 성숙 (Docker, K8s, TF)    |
| 적합 영역         | 고성능, 안전 필수, 시스템 | 빠른 개발, 마이크로서비스 |
| SE 실무 도구 비율 | CLI 도구, 에이전트        | 오케스트레이션, API 서버  |

### SE 관점 선택 가이드

| 상황                              | 선택     | 이유                       |
|-----------------------------------|----------|----------------------------|
| 빠르게 인프라 도구 개발           | **Go**   | 학습 비용 대비 생산성 높음 |
| 고성능 에이전트/프록시 개발       | **Rust** | 메모리 안전 + C 수준 성능  |
| 기존 C 코드 교체/확장             | **Rust** | FFI, 메모리 안전           |
| Kubernetes operator 개발          | **Go**   | 생태계 표준                |
| 보안 민감 시스템 도구 (sudo, ssh) | **Rust** | 메모리 버그 원천 차단      |
| Terraform provider 개발           | **Go**   | SDK가 Go만 지원            |
| 로그 파서/분석기 (대용량)         | **Rust** | 성능 + 메모리 효율         |
| 내부 모니터링 에이전트            | 둘 다    | 요구 성능에 따라           |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 참고 자료

- The Rust Programming Language (Book): [doc.rust-lang.org/book](https://doc.rust-lang.org/book/) — ★★★★☆
- Rust by Example: [doc.rust-lang.org/rust-by-example](https://doc.rust-lang.org/rust-by-example/) — ★★★☆☆
- Rustlings: [github.com/rust-lang/rustlings](https://github.com/rust-lang/rustlings) — ★★★☆☆
- Command-Line Rust (O'Reilly): [oreilly.com](https://www.oreilly.com/library/view/command-line-rust/9781098109424/) — ★★★★☆
- Zero To Production In Rust: [zero2prod.com](https://www.zero2prod.com/) — ★★★☆☆
- Rust for Rustaceans: [nostarch.com](https://nostarch.com/rust-rustaceans) — ★★★☆☆
- Awesome Rust: [github.com/rust-unofficial/awesome-rust](https://github.com/rust-unofficial/awesome-rust) — ★★☆☆☆

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

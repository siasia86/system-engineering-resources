# SE를 위한 Lean 언어 학습 로드맵
<!-- reference: _reference/lean_official_notes.md -->

시스템 엔지니어 관점에서 Lean을 학습하는 로드맵입니다. 함수형 프로그래밍, 정형 검증(Formal Verification), 증명 자동화와 인프라 운영 도구의 검증 가능성에 초점을 맞춥니다.

## 목차

| 섹션                                                                                                                                         |
|----------------------------------------------------------------------------------------------------------------------------------------------|
| [1. Lean 개요](#1-lean-개요) / [2. SE 활용 판단](#2-se-활용-판단) / [3. 학습 전제 조건](#3-학습-전제-조건)                                   |
| [4. 핵심 언어 개념](#4-핵심-언어-개념) / [5. 개발 도구와 프로젝트](#5-개발-도구와-프로젝트) / [6. 증명 개발 워크플로](#6-증명-개발-워크플로) |
| [7. 단계별 로드맵](#7-단계별-로드맵) / [8. SE 실무 프로젝트](#8-se-실무-프로젝트) / [9. 운영 및 CI 검증](#9-운영-및-ci-검증)                 |

---

## 1. Lean 개요

Lean은 함수형 프로그래밍 언어이자 interactive theorem prover입니다. 프로그램의 타입과 수학적 명제를 같은 타입 검사 체계로 표현하고, 커널(kernel)이 최종 proof term을 검사합니다.

> 정형 검증(Formal Verification): 시스템의 요구사항과 불변식을 형식 언어로 표현한 뒤, 도구가 모든 허용된 실행 경로에 대해 조건을 만족하는지 검사하는 방법입니다. 테스트가 선택한 입력을 검증하는 방식이라면, 정형 검증은 모델과 증명 범위 안의 입력 공간을 대상으로 합니다.

### 핵심 특징

| 특징               | 설명                                                    |
|--------------------|---------------------------------------------------------|
| 종속 타입          | 값에 따라 달라지는 타입으로 데이터와 조건을 함께 표현   |
| 커널 검증          | 전술이 생성한 proof term을 최소 trusted kernel이 재검사 |
| 함수형 프로그래밍  | 불변 데이터, 고차 함수, 대수적 데이터 타입 중심         |
| 증분 컴파일        | `lake`가 소스와 의존성을 추적하여 필요한 부분만 빌드    |
| 확장 가능한 자동화 | Lean으로 전술과 도메인별 표기·자동화 기능 확장 가능     |

Lean은 일반 애플리케이션 개발 언어라기보다, 오류 비용이 높은 알고리즘·프로토콜·보안 속성을 실행 가능한 코드와 함께 명세하는 도구로 보는 편이 적절합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. SE 활용 판단

### 적합한 영역

| 영역                   | Lean 활용 예시                    | 기대 효과                      |
|------------------------|-----------------------------------|--------------------------------|
| 프로토콜 명세          | 상태 전이, 패킷 형식, 허용된 순서 | 모호한 요구사항의 형식화       |
| 보안 알고리즘          | 암호 구성요소의 수학적 성질       | 핵심 불변식의 기계 검증        |
| 스케줄러·분산 알고리즘 | 공정성, 종료성, 상태 일관성       | 설계 오류의 조기 발견          |
| 컴파일러·변환기        | 변환 전후 의미 보존               | 최적화 정당성 검증             |
| 운영 도구의 핵심 로직  | 파서, 정책 평가기, 상태 머신      | 입력 경계와 정책 조건의 명시화 |

### 다른 언어와의 역할 분담

| 요구사항                      | 우선 선택      | Lean의 역할                  |
|-------------------------------|----------------|------------------------------|
| 빠른 운영 자동화              | Python, Bash   | 핵심 정책·파서의 검증        |
| 고성능 장기 실행 서비스       | Rust, Go       | 알고리즘 명세와 정합성 검증  |
| 안전성이 중요한 핵심 알고리즘 | Lean           | 명세, 증명, 실행 코드의 기준 |
| 대규모 수학 라이브러리 활용   | Lean + Mathlib | 기존 정리와 자동화 재사용    |

Lean으로 전체 인프라를 대체하기보다, 장애·보안·데이터 손실로 이어질 수 있는 작은 핵심 로직부터 검증하는 방식이 현실적입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 학습 전제 조건

| 항목            | 필요 수준                             | 학습 확인 방법               |
|-----------------|---------------------------------------|------------------------------|
| 함수와 자료구조 | 함수, 재귀, 리스트, 트리 이해         | 작은 재귀 함수 직접 작성     |
| 논리 기초       | 명제, 전칭·존재 한정, 귀납법          | 간단한 명제의 증명 구조 설명 |
| 타입 시스템     | 정적 타입, 제네릭, 대수적 데이터 타입 | `Option`·`Result` 모델링     |
| Linux·Git       | 파일, 프로세스, CI, diff 기본 사용    | 프로젝트 빌드와 검증 자동화  |
| 수학 기초       | 집합, 함수, 관계, 귀납법              | Mathlib 학습 시 유리         |

Lean을 시작하기 위해 고급 수학이 필수는 아닙니다. 시스템 엔지니어라면 먼저 함수·타입·재귀·불변식의 연결을 익히고, 이후 증명 전술과 라이브러리 사용으로 확장합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 핵심 언어 개념

### 함수와 타입

Lean에서는 함수와 타입이 모두 term으로 다뤄집니다. 함수의 입력 타입과 출력 타입을 명시하면 인터페이스의 전제 조건과 결과 형태를 코드에 남길 수 있습니다.

```lean
def double (n : Nat) : Nat := n + n

#check double
#eval double 21
```

### 대수적 데이터 타입

`inductive`로 상태와 이벤트를 제한된 생성자 집합으로 표현합니다. 운영 도구의 상태 머신이나 프로토콜 단계처럼 허용된 상태를 열거해야 하는 경우에 유용합니다.

```lean
inductive ServiceState where
  | stopped
  | starting
  | running
  | failed (reason : String)
  deriving Repr

#check ServiceState.running
```

### 명제와 증명

명제는 타입이고 증명은 그 타입의 값입니다. 아래 정리는 자연수에 0을 더한 결과가 원래 수와 같다는 명제를 `simp` 전술로 증명합니다.

```lean
theorem add_zero (n : Nat) : n + 0 = n := by
  simp
```

### 전술과 proof state

전술(tactic)은 현재 목표와 가정을 가진 proof state를 변환합니다. `intro`, `exact`, `rw`, `simp`, `cases`, `induction`을 기본 도구로 익힌 뒤 자동화 전술을 추가합니다.

> 전술(Tactic): 증명 목표를 더 작은 목표로 변환하거나 이미 알고 있는 정리와 일치시키는 증명 작성 명령입니다. 전술 실행 결과는 최종적으로 커널이 검사할 수 있는 proof term으로 변환됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 개발 도구와 프로젝트

Lean 공식 도구 체계는 `lean`, `lake`, `elan`을 중심으로 구성됩니다. 공식 설치 안내는 VS Code와 Lean 4 VS Code extension 조합을 권장합니다.

### 도구 역할

| 도구          | 역할                                | 운영 관점의 확인 사항                 |
|---------------|-------------------------------------|---------------------------------------|
| `lean`        | 소스 elaboration, 증명 검사, 컴파일 | 오류와 경고를 CI에서 수집             |
| `lake`        | 증분 빌드와 의존성 관리             | 재현 가능한 빌드 명령으로 고정        |
| `elan`        | toolchain 설치와 선택               | 프로젝트별 버전 고정                  |
| `leanchecker` | `.olean` 결과의 추가 커널 재검사    | 높은 보증 수준이 필요한 릴리스에 적용 |

> Elaboration: 사용자가 작성한 간결한 Lean 문법에 타입·암시적 인자·인스턴스 정보를 보완하여, 커널이 검사할 수 있는 내부 term으로 변환하는 과정입니다.

### 최소 프로젝트 흐름

```bash
lake new se_lean
cd se_lean
lake build
```

프로젝트가 생성되면 `lakefile.lean`, `Main.lean`, toolchain 설정을 확인합니다. CI에서는 개발자 로컬의 암묵적인 전역 설정에 의존하지 않고 저장소의 버전 설정과 lock 상태를 함께 관리합니다.

### 소스 파일 확인 명령

```lean
#check List Nat
#check List.map
#print List.map
#synth Repr Nat
#version
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 증명 개발 워크플로

증명은 한 번에 복잡한 자동화를 적용하기보다 명세, 작은 보조 정리, 기본 전술, 커널 검증 순서로 진행합니다.

```
Requirement
    │
    v
Formal specification
    │
    v
Lemma and theorem
    │
    v
Tactic proof
    │
    v
Kernel check + lake build
    │
    v
CI artifact and review
```

### 권장 순서

1. 입력·출력·오류 상태와 불변식을 먼저 타입과 명제로 정의합니다.
2. 작은 예제로 정의가 의도대로 계산되는지 `#eval`과 `#check`로 확인합니다.
3. 일반 정리를 보조 정리로 나누고, 각 목표의 전제 조건을 명시합니다.
4. `simp`, `rw`, `cases`, `induction` 등 읽기 쉬운 전술부터 적용합니다.
5. `lake build`와 필요한 경우 `#print axioms`로 결과를 검증합니다.
6. 증명 변경과 명세 변경을 분리하여 코드 리뷰에서 의도를 확인합니다.

### 검증 가능성 점검

| 점검 대상        | 확인 방법                   | 실패 시 조치                   |
|------------------|-----------------------------|--------------------------------|
| 정의의 계산 결과 | `#eval`, 예제 정리          | 정의와 테스트 입력 재검토      |
| 타입과 인스턴스  | `#check`, `#synth`          | 타입 주석·import·instance 확인 |
| 증명 완결성      | `lake build`                | 남은 goal과 오류 메시지 분석   |
| 공리 의존성      | `#print axioms theoremName` | 허용 공리 정책과 비교          |
| 재현성           | 고정 toolchain + CI 빌드    | 로컬 전역 설정 제거            |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 단계별 로드맵

| 단계    | 기간     | 학습 주제                                       | 산출물                       |
|---------|----------|-------------------------------------------------|------------------------------|
| Phase 1 | 1~2주    | 함수, 재귀, 타입, `inductive`, pattern matching | 간단한 상태 모델             |
| Phase 2 | 2~4주    | 명제, 등식, `intro`, `exact`, `rw`, `simp`      | 기본 정리 모음               |
| Phase 3 | 3~5주    | 리스트·트리 불변식, `cases`, `induction`        | 파서·상태 머신의 안전성 정리 |
| Phase 4 | 4~6주    | `lake`, 모듈, type class, 오류 모델             | 빌드 가능한 Lean 프로젝트    |
| Phase 5 | 6주 이후 | Mathlib, 전술 자동화, 실행 코드, CI             | SE 실무 검증 프로젝트        |

### 주차별 연습

```text
1주차  함수·재귀·List·Option·Result
2주차  inductive 상태 모델·pattern matching
3주차  등식·명제·implication·conjunction
4주차  simp·rw·cases·induction
5주차  Lake 프로젝트·모듈·type class
6주차  운영 도구의 파서 또는 정책 엔진 명세
```

학습 중에는 증명보다 명세의 정확성을 우선합니다. 구현을 먼저 작성한 뒤 증명을 맞추면 잘못된 요구사항을 정당화할 수 있으므로, 입력·출력·실패 조건을 먼저 문서화합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. SE 실무 프로젝트

### 추천 프로젝트

| 프로젝트                    | 난이도 | 검증 대상                         | 연계 기술        |
|-----------------------------|--------|-----------------------------------|------------------|
| 설정 파일 파서              | ★★☆☆☆  | 허용 키, 기본값, 오류 입력        | Python 또는 Rust |
| 서비스 상태 머신            | ★★☆☆☆  | 허용 전이, 종료 상태              | systemd 개념     |
| 재시도 정책 평가기          | ★★★☆☆  | backoff, 최대 시도, 종료 조건     | HTTP client      |
| 방화벽 정책 모델            | ★★★★☆  | 규칙 우선순위, 충돌, 기본 거부    | nftables 개념    |
| 배포 롤백 결정 로직         | ★★★★☆  | 상태 전이, 승인 조건, 롤백 가능성 | CI/CD            |
| 체크섬·해시 검증 파이프라인 | ★★★☆☆  | 파일 목록과 검증 결과의 일관성    | SHA-256 도구     |

### 첫 프로젝트 권장 범위

설정 파일 파서 또는 서비스 상태 머신으로 시작합니다. 외부 시스템을 직접 변경하지 않고 문자열·상태·정책을 입력으로 받아 결정 결과를 출력하게 만들면, 테스트와 증명을 분리하기 쉽습니다.

```lean
inductive Decision where
  | allow
  | deny
  deriving Repr

def defaultDecision : Decision := .deny

theorem default_is_deny : defaultDecision = .deny := by
  rfl
```

운영 반영 단계에서는 Lean으로 검증한 순수 결정 로직을 Rust·Go·Python 서비스에서 호출하거나, 동일한 명세를 다른 언어 구현의 테스트 기준으로 사용합니다. 직접 배포하기 전에 기존 시스템의 dry-run 결과와 비교합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 운영 및 CI 검증

Lean 프로젝트를 운영 코드에 연결할 때는 증명 성공만 확인하지 않고 버전, 의존성, 산출물, 검증 범위를 함께 관리합니다.

### CI 기본 단계

```bash
lake build
```

### 운영 체크리스트

| 항목           | 확인 내용                                    |
|----------------|----------------------------------------------|
| Toolchain 고정 | 로컬·CI·릴리스 환경의 Lean 버전 일치         |
| 의존성 관리    | `lakefile`과 lock 상태 변경을 코드 리뷰      |
| 빌드 재현성    | 깨끗한 환경에서 `lake build` 성공            |
| 공리 정책      | 핵심 theorem의 `#print axioms` 결과 검토     |
| 외부 효과 분리 | 파일·네트워크 변경은 검증된 결정 로직과 분리 |
| 롤백           | 기존 구현과 비교 실행 후 단계적 전환         |

🟡 Lean 증명이 통과해도 명세가 현실 요구사항을 잘못 표현하면 운영 안전성이 보장되지 않습니다. 요구사항 리뷰, 경계값 테스트, 기존 구현과의 differential test를 증명과 함께 유지합니다.

### SE 적용 원칙

- 검증 대상은 장애 비용과 보안 영향이 큰 작은 핵심 로직부터 선정합니다.
- 순수 함수와 외부 I/O를 분리하여 증명 범위를 작게 유지합니다.
- 명세·구현·증명·CI 로그를 같은 변경 단위로 추적합니다.
- 버전 업그레이드 시 안정 릴리스와 `latest` 문서의 대상 버전을 구분합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Lean 공식 홈페이지: [lean-lang.org](https://lean-lang.org/) — ★★★☆☆
- Lean 설치 안내: [lean-lang.org/install](https://lean-lang.org/install/) — ★★★☆☆
- Lean 학습 자료: [lean-lang.org/learn](https://lean-lang.org/learn/) — ★★★☆☆
- Lean Language Reference: [lean-lang.org/doc/reference/latest](https://lean-lang.org/doc/reference/latest/) — ★★★☆☆
- Lean 4 releases: [github.com/leanprover/lean4/releases](https://github.com/leanprover/lean4/releases) — ★★★☆☆
- [Lean 공식 문서 참조 노트](../../_reference/lean_official_notes.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-11

**마지막 업데이트**: 2026-09-11

© 2026 siasia86. Licensed under CC BY 4.0.

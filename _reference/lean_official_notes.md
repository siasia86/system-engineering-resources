---
name: lean-official-notes
description: Lean 4 공식 문서 기반 언어·증명·빌드 도구·버전 현황 정리.
tags:
  - lean
  - functional-programming
  - theorem-proving
  - formal-verification
  - lake
last_checked: 2026-09-11
sources:
  - https://lean-lang.org/
  - https://lean-lang.org/install/
  - https://lean-lang.org/learn/
  - https://lean-lang.org/doc/reference/latest/
  - https://github.com/leanprover/lean4/releases/latest
---

# Lean 공식 문서 참조 노트

## 1. 버전 현황

### Lean 릴리스

| 항목               | 버전 또는 상태  | 확인 내용                             |
|--------------------|-----------------|---------------------------------------|
| 안정 릴리스        | v4.33.1         | 2026-08-21 릴리스                     |
| 최신 릴리스        | v4.33.1         | GitHub `leanprover/lean4` 최신 릴리스 |
| Language Reference | 4.34.0-rc2 대상 | 최신 문서 페이지가 릴리스 후보를 설명 |

🟡 Language Reference의 `latest`는 안정 릴리스와 일치하지 않을 수 있습니다. 배포 프로젝트에서는
프로젝트가 고정한 `elan` toolchain과 `lake` 의존성 버전을 기준으로 검증합니다.

## 2. 언어와 증명 모델

- Lean은 함수형 프로그래밍 언어이면서 interactive theorem prover입니다.
- Lean의 핵심 타입 이론은 dependent type theory 기반입니다.
- 명제(Proposition)는 타입으로 표현하고, 증명은 해당 타입을 inhabit하는 term으로 표현합니다.
- 최소 trusted kernel이 proof term을 검사합니다. 전술(tactic)은 proof term을 생성하며, 전술 자체의 오류가 커널 검사를 우회하지 않습니다.
- 타입 시스템은 함수, 명제, universe, inductive type, quotient 등을 다룹니다.
- Lean은 일반 프로그램 실행을 위해 런타임, 병렬 처리, monadic I/O 등의 기능도 제공합니다.

> 종속 타입(Dependent Type): 값에 따라 타입이 달라질 수 있는 타입입니다. 데이터와 그 데이터에
> 대한 조건을 타입 수준에서 함께 표현할 수 있어, 프로그램의 불변식과 수학적 명제를 동일한
> 타입 검사 체계에서 검증하는 데 사용됩니다.

## 3. 공식 도구 체계

| 도구          | 역할                                              |
|---------------|---------------------------------------------------|
| `lean`        | Lean 소스 파일의 elaboration, 증명 검사, 컴파일   |
| `lake`        | 의존성을 추적하면서 Lean 및 관련 도구를 증분 빌드 |
| `elan`        | Lean toolchain 설치·선택·관리                     |
| `leanchecker` | `.olean` 결과를 커널로 재검사하여 추가 검증       |
| `leanc`       | Lean 배포판에 포함된 C 컴파일러                   |

## 4. 설치와 프로젝트 관리

- 공식 설치 안내는 VS Code와 공식 Lean 4 VS Code extension 조합을 권장합니다.
- 프로젝트 단위 toolchain을 고정하고, CI에서는 동일한 toolchain으로 `lake build`를 실행하는 방식이 적합합니다.
- `lake`는 Lean 파일과 라이브러리 의존성을 관리하는 표준 빌드 도구입니다.
- 외부 패키지를 사용할 때는 프로젝트의 `lakefile.lean` 또는 `lakefile.toml`과 toolchain 설정을 함께 검토합니다.

## 5. 상호작용 명령

| 명령                  | 용도                           |
|-----------------------|--------------------------------|
| `#check term`         | term의 타입 확인               |
| `#eval term`          | 실행 가능한 term 평가          |
| `#reduce term`        | term을 축약하여 계산 결과 확인 |
| `#print name`         | 선언의 내부 표현 확인          |
| `#print axioms name`  | 선언이 사용하는 공리 확인      |
| `#synth instanceType` | type class 인스턴스 합성 확인  |
| `#version`            | 현재 Lean 버전 확인            |

## 6. 공식 학습 경로

| 자료                           | 대상                                   |
|--------------------------------|----------------------------------------|
| Functional Programming in Lean | 함수형 프로그래밍을 처음 배우는 개발자 |
| Theorem Proving in Lean        | Lean 증명 개발과 dependent type theory |
| Mathematics in Lean            | Mathlib 기반 수학 형식화               |
| Lean Language Reference        | 문법·타입·전술·빌드 도구의 정밀 참조   |

## 7. 운영 시 확인 항목

- 개발자 로컬과 CI의 Lean toolchain이 동일한지 확인합니다.
- `lake build`를 변경 검증의 기본 단계로 사용합니다.
- 증명 변경 후 필요한 경우 `#print axioms`로 의존 공리를 확인합니다.
- `latest` 문서가 release candidate를 가리킬 수 있으므로, 안정 릴리스와 문서 대상 버전을 구분합니다.
- 자동화 전술을 사용하더라도 최종 proof term은 커널 검사를 통과해야 합니다.

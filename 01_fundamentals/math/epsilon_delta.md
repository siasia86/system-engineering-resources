# 엡실론-델타 논법 (ε-δ Definition of Limits)
<!-- reference: _reference/epsilon_delta_math_notes.md -->

함수의 극한을 엄밀하게 정의하는 엡실론-델타 논법을 정리합니다. 직관적 이해부터 형식적 증명 구조까지 다룹니다.

## 목차

| 섹션                                                                                       |
|--------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 직관적 이해](#2-직관적-이해) / [3. 형식적 정의](#3-형식적-정의)   |
| [4. 증명 구조](#4-증명-구조) / [5. 예제](#5-예제) / [6. 자주 하는 실수](#6-자주-하는-실수) |
| [7. 변형](#7-변형) / [8. SE에서의 의미](#8-se에서의-의미)                                  |

## 1. 개요

| 항목   | 내용                                             |
|--------|--------------------------------------------------|
| 분야   | 해석학 (Real Analysis)                           |
| 제안자 | Augustin-Louis Cauchy / Karl Weierstrass         |
| 목적   | 극한의 엄밀한 정의 (직관적 "가까이 간다" → 정량) |
| 표기   | lim(x→a) f(x) = L                                |
| 핵심   | "임의의 ε > 0에 대해 δ > 0이 존재한다"           |

### 왜 필요한가

- "x가 a에 가까워지면 f(x)가 L에 가까워진다" → "가까이"의 정확한 의미가 없습니다
- ε-δ 논법은 "얼마나 가까이"를 수량화합니다
- 모든 현대 미적분/해석학의 기초입니다

## 2. 직관적 이해

```
f(x)                                    
  ^                                     
  │          ╭───╮                      
L+ε ─ ─ ─ ─╱─ ─ ─╲─ ─ ─ ─ ─ ─ ─ ─ ε band
  │        ╱       ╲                    
L ─ ─ ─ ─╱─ ─ ─ ─ ─╲─ ─ ─ ─ ─ ─ ─       
  │      ╱             ╲                
L-ε ─ ─╱─ ─ ─ ─ ─ ─ ─ ─╲─ ─ ─ ─ ─ ε band
  │   ╱                    ╲            
  │──┼──────────┼──────────┼──────── > x
     a-δ        a         a+δ           
              δ band                    
```

- **ε (epsilon)**: f(x)가 L에서 벗어나도 되는 허용 범위 (output tolerance)
- **δ (delta)**: x가 a에서 벗어나도 되는 범위 (input tolerance)
- 핵심: **어떤 ε을 잡아도** 그에 맞는 δ를 찾을 수 있어야 합니다

## 3. 형식적 정의

### 함수의 극한

```
lim f(x) = L
x→a
```

**정의**: 임의의 ε > 0에 대해, 어떤 δ > 0이 존재하여

```
0 < |x - a| < δ  →  |f(x) - L| < ε
```

를 만족합니다.

### 논리 기호 표현

```
∀ε > 0, ∃δ > 0 such that:
  0 < |x - a| < δ  ⟹  |f(x) - L| < ε
```

### 각 기호의 의미

| 기호            | 의미                                 |
|-----------------|--------------------------------------|
| ∀ε > 0          | 임의의 양수 ε에 대해 (아무리 작아도) |
| ∃δ > 0          | 적절한 양수 δ가 존재하여             |
| `0 < \|x - a\|` | x ≠ a이면서 x가 a에 충분히 가까울 때 |
| < δ             | x와 a의 거리가 δ 미만이면            |
| `\|f(x) - L\|`  | f(x)와 L의 거리가                    |
| < ε             | ε 미만입니다                         |

🟡 `0 < |x - a|` 조건은 x = a에서의 함수값을 사용하지 않는다는 의미입니다. 극한은 "a에서의 값"이 아니라 "a로 다가갈 때의 경향"입니다.

## 4. 증명 구조

### 단계별 절차

```
┌─────────────────────────────────────────────────────┐ 
│              epsilon-delta Proof Structure           │
├─────────────────────────────────────────────────────┤ 
│  1. State: "Let ε > 0 be given"                     │ 
│  2. Find: construct δ in terms of ε                 │ 
│  3. Assume: 0 < |x - a| < δ                        │  
│  4. Show: |f(x) - L| < ε                           │  
│  5. Conclude: therefore lim f(x) = L as x → a      │  
└─────────────────────────────────────────────────────┘ 
```

### δ 찾기 전략

| 전략            | 적용 대상                 | 방법                            |
|-----------------|---------------------------|---------------------------------|
| 직접 계산       | 선형 함수, 다항식         | `\|f(x)-L\|`을 `\|x-a\|`로 변환 |
| 상한 설정       | 분모에 x가 있는 함수      | δ ≤ 1 등으로 제한 후 바운드     |
| min(δ₁, δ₂)     | 여러 조건을 동시에 만족   | δ = min(1, ε/M)                 |
| 샌드위치/스퀴즈 | 직접 인수분해 어려운 경우 | 부등식 체인                     |

## 5. 예제

### 예제 1: lim(x→3) 2x + 1 = 7

**증명**:

Let ε > 0 be given. Choose δ = ε/2.

```
|f(x) - L| = |(2x + 1) - 7|
            = |2x - 6|
            = 2|x - 3|
            < 2δ
            = 2 · (ε/2)
            = ε  ✓
```

### 예제 2: lim(x→2) x² = 4

**증명**:

Let ε > 0 be given. Choose δ = min(1, ε/5).

```
|x - 2| < δ ≤ 1  →  1 < x < 3  →  |x + 2| < 5

|f(x) - L| = |x² - 4|
            = |x - 2| · |x + 2|
            < δ · 5
            ≤ (ε/5) · 5
            = ε  ✓
```

🟡 δ = min(1, ε/5)에서 1을 잡는 이유: |x+2|의 상한을 확보하기 위함입니다. δ ≤ 1이면 x ∈ (1,3)이므로 |x+2| < 5가 보장됩니다.

### 예제 3: lim(x→0) x·sin(1/x) = 0

**증명**:

Let ε > 0 be given. Choose δ = ε.

```
|f(x) - L| = |x · sin(1/x) - 0|
            = |x| · |sin(1/x)|
            ≤ |x| · 1          (∵ |sin(θ)| ≤ 1)
            < δ
            = ε  ✓
```

## 6. 자주 하는 실수

| 실수                    | 올바른 이해                                     |
|-------------------------|-------------------------------------------------|
| ε을 먼저 고정하지 않음  | 증명은 반드시 "Let ε > 0"으로 시작합니다        |
| δ가 ε에 의존하지 않음   | δ는 ε의 함수입니다 (δ = f(ε))                   |
| x = a를 대입            | `0 < \|x-a\|` 조건으로 x ≠ a입니다              |
| δ를 구한 후 역방향 증명 | 순방향: `\|x-a\| < δ` → `\|f(x)-L\| < ε`로 진행 |
| "충분히 작은 δ" 서술    | 구체적 δ 값 (ε의 식)을 명시해야 합니다          |

## 7. 변형

### 단측 극한

```
lim f(x) = L  :  0 < x - a < δ  →  |f(x) - L| < ε  (right limit)
x→a+

lim f(x) = L  :  0 < a - x < δ  →  |f(x) - L| < ε  (left limit)
x→a-
```

### 무한대에서의 극한

```
lim f(x) = L  :  ∀ε > 0, ∃M > 0 s.t. x > M → |f(x) - L| < ε
x→∞
```

### 극한값이 무한대

```
lim f(x) = ∞  :  ∀M > 0, ∃δ > 0 s.t. 0 < |x - a| < δ → f(x) > M
x→a
```

### 함수의 연속성

```
f is continuous at a  ⟺  lim f(x) = f(a)
                          x→a

⟺  ∀ε > 0, ∃δ > 0 s.t. |x - a| < δ → |f(x) - f(a)| < ε
```

🟡 연속성에서는 `0 < |x-a|`가 아닌 `|x-a|` (x = a 포함)입니다.

## 8. SE에서의 의미

| 개념          | SE 대응                                     |
|---------------|---------------------------------------------|
| ε (허용 오차) | SLA tolerance, 응답시간 편차 허용값         |
| δ (입력 범위) | 부하 범위, 입력 파라미터 변동 허용값        |
| 극한 존재     | 시스템이 특정 조건에서 안정 상태로 수렴     |
| 극한 미존재   | 발산/진동 — 시스템 불안정                   |
| 연속성        | 입력 변화에 출력이 급변하지 않음 (graceful) |
| min(δ₁, δ₂)   | 여러 제약 중 가장 엄격한 조건 적용          |

실용 예시:
- "CPU 사용률이 90%에 근접할 때 응답시간이 어떤 값으로 수렴하는가" → 극한
- "부하가 ±δ 변동해도 응답시간 편차가 ε 이내인가" → ε-δ 조건
- "특정 임계점에서 시스템이 급격히 열화하는가" → 불연속점

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Rudin, Walter. "Principles of Mathematical Analysis" (Baby Rudin) — ★★★★☆
- Abbott, Stephen. "Understanding Analysis" — ★★★☆☆
- 3Blue1Brown Limits (visual): [youtube.com](https://www.youtube.com/watch?v=kfF40MiS7zA) — ★★☆☆☆
- [_reference/epsilon_delta_math_notes.md](../../_reference/epsilon_delta_math_notes.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-14

**마지막 업데이트**: 2026-07-14

© 2026 siasia86. Licensed under CC BY 4.0.

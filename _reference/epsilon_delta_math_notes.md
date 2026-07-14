---
name: epsilon-delta-math-notes
description: ε-δ 논법 (엡실론-델타) 관련 수학 공식 정의, 정리, 출처 정리.
tags:
  - math
  - analysis
  - limits
  - epsilon-delta
  - calculus
last_checked: 2026-07-14
sources:
  - https://en.wikipedia.org/wiki/(%CE%B5,_%CE%B4)-definition_of_limit
  - Rudin, Walter. "Principles of Mathematical Analysis" 3rd ed. McGraw-Hill, 1976.
  - Abbott, Stephen. "Understanding Analysis" 2nd ed. Springer, 2015.
---

# ε-δ 논법 수학 참조 노트

## 정의 (Definition 4.1, Rudin Ch.4)

Let f be defined on E ⊂ ℝ, and let p be a limit point of E.

```
lim f(x) = q
x→p
```

means: for every ε > 0 there exists δ > 0 such that
for all x ∈ E with 0 < |x - p| < δ, we have |f(x) - q| < ε.

## 연속성 정의 (Definition 4.5, Rudin Ch.4)

f is continuous at p if:

```
∀ε > 0, ∃δ > 0 such that:
  |x - p| < δ  ⟹  |f(x) - f(p)| < ε
```

차이: 극한 정의에서는 `0 < |x - p|` (x ≠ p), 연속에서는 `|x - p|` (x = p 포함).

## 단측 극한 (One-sided Limits)

### Right limit (x → a⁺)

```
∀ε > 0, ∃δ > 0 such that:
  0 < x - a < δ  ⟹  |f(x) - L| < ε
```

### Left limit (x → a⁻)

```
∀ε > 0, ∃δ > 0 such that:
  0 < a - x < δ  ⟹  |f(x) - L| < ε
```

## 무한대 극한 (Limits at Infinity)

### x → ∞

```
∀ε > 0, ∃M > 0 such that:
  x > M  ⟹  |f(x) - L| < ε
```

### f(x) → ∞ as x → a

```
∀M > 0, ∃δ > 0 such that:
  0 < |x - a| < δ  ⟹  f(x) > M
```

## 극한의 유일성 (Theorem 4.2, Rudin)

If lim(x→p) f(x) = q₁ and lim(x→p) f(x) = q₂, then q₁ = q₂.

증명 핵심: 삼각 부등식으로 |q₁ - q₂| < 2ε → ε arbitrary → q₁ = q₂.

## 극한의 산술 (Theorem 4.4, Rudin)

If lim(x→p) f(x) = A and lim(x→p) g(x) = B, then:

| 연산  | 결과  | 조건       |
|-------|-------|------------|
| f + g | A + B | -          |
| f · g | A · B | -          |
| f / g | A / B | B ≠ 0      |
| c · f | c · A | c constant |

## 증명 전략 요약

| 전략        | 적용 조건            | δ 선택               |                   |                   |  |                 |
|-------------|----------------------|----------------------|-------------------|-------------------|--|-----------------|
| Direct      | f(x) - L이           | x - a                | 의 상수배         | δ = ε / c         |  |                 |
| Bound + min |                      | x - a                | 외 다른 인수 존재 | δ = min(1, ε / M) |  |                 |
| Squeeze     |                      | f(x) - L             | ≤ g(x) ·          | x - a             |  | δ = ε / (sup g) |
| Composition | f = h ∘ g, 각각 연속 | δ₁ from g, δ₂ from h |                   |                   |  |                 |

## 관련 정리

### Bolzano-Weierstrass Theorem

Every bounded sequence in ℝ has a convergent subsequence.

### Intermediate Value Theorem (IVT)

If f is continuous on [a,b] and f(a) < c < f(b), then ∃x₀ ∈ (a,b) such that f(x₀) = c.

- IVT의 증명에 ε-δ 연속성 정의가 핵심적으로 사용됨

### Extreme Value Theorem (EVT)

If f is continuous on [a,b] (compact), then f attains its maximum and minimum.

## 역사적 맥락

| 연도 | 인물        | 기여                                        |
|------|-------------|---------------------------------------------|
| 1821 | Cauchy      | "Cours d'analyse"에서 극한 개념 정식화 시도 |
| 1854 | Weierstrass | 현대적 ε-δ 정의 확립 (강의)                 |
| 1861 | Weierstrass | 출판된 형태로 정리                          |

- Cauchy는 "한없이 가까이"라는 표현을 사용했으나 정량적 정의는 Weierstrass가 완성
- ε-δ 형식화로 미적분학이 직관에서 엄밀한 논리 체계로 전환

## 주의사항

- δ는 ε에 의존할 수 있음 (δ = f(ε))
- δ는 점 a에도 의존할 수 있음 (pointwise continuity vs uniform continuity)
- Uniform continuity: δ가 a에 무관하게 ε만으로 결정됨
  - `∀ε > 0, ∃δ > 0 such that ∀x,y: |x - y| < δ ⟹ |f(x) - f(y)| < ε`
- 극한 정의에서 x = a에서의 함수값은 무관 (정의되지 않아도 극한 존재 가능)

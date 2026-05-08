# 페어와이즈 테스트 (Pairwise Testing)

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 원리](#2-원리) / [3. 생성 방법](#3-생성-방법) |
| [4. 예시](#4-예시) / [5. 도구](#5-도구) |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

페어와이즈 테스트(All-Pairs Testing)는 모든 입력 파라미터의 2개씩 조합(pair)을 최소 1회 포함하도록 테스트 케이스를 생성하는 기법입니다.

| 항목          | 내용                                              |
|---------------|---------------------------------------------------|
| 분류          | 블랙박스 테스트 기법 (조합 테스트)                |
| 핵심 아이디어 | 결함의 대부분은 2개 파라미터 상호작용에서 발생    |
| 목적          | 전수 조합 대비 테스트 수를 대폭 감소              |
| 근거          | 결함의 70~90%가 1~2개 파라미터 상호작용에서 발생  |

[⬆ 목차로 돌아가기](#목차)

## 2. 원리

### 전수 조합 vs 페어와이즈

```
파라미터: OS(3) × 브라우저(3) × 해상도(3)

전수 조합: 3 × 3 × 3 = 27개
페어와이즈: 9개 (모든 2개 조합 커버)
```

### 커버리지 보장

모든 파라미터 쌍의 모든 값 조합이 최소 1회 등장합니다.

```
파라미터 A: {a1, a2}
파라미터 B: {b1, b2}
파라미터 C: {c1, c2}

필요한 쌍:
  A×B: (a1,b1), (a1,b2), (a2,b1), (a2,b2)
  A×C: (a1,c1), (a1,c2), (a2,c1), (a2,c2)
  B×C: (b1,c1), (b1,c2), (b2,c1), (b2,c2)

전수: 8개 / 페어와이즈: 4개로 모든 쌍 커버 가능
```

[⬆ 목차로 돌아가기](#목차)

## 3. 생성 방법

### 직교 배열 (Orthogonal Array)

수학적으로 균형 잡힌 조합을 생성합니다.

### 알고리즘 기반

IPOG, AETG 등의 알고리즘으로 최소 테스트 세트를 생성합니다.

### 수동 생성 (소규모)

1. 첫 번째 파라미터 쌍의 모든 조합 나열
2. 나머지 파라미터를 기존 행에 배치 (새 쌍 커버 최대화)
3. 커버되지 않은 쌍이 있으면 행 추가

[⬆ 목차로 돌아가기](#목차)

## 4. 예시

### 예시 1: 웹 호환성 테스트

파라미터:
- OS: Windows, macOS, Linux
- 브라우저: Chrome, Firefox, Safari
- 해상도: 1080p, 1440p, 4K

전수 조합: 27개 → 페어와이즈: 9개

| TC | OS      | 브라우저 | 해상도 |
|----|---------|----------|--------|
| 1  | Windows | Chrome   | 1080p  |
| 2  | Windows | Firefox  | 1440p  |
| 3  | Windows | Safari   | 4K     |
| 4  | macOS   | Chrome   | 1440p  |
| 5  | macOS   | Firefox  | 4K     |
| 6  | macOS   | Safari   | 1080p  |
| 7  | Linux   | Chrome   | 4K     |
| 8  | Linux   | Firefox  | 1080p  |
| 9  | Linux   | Safari   | 1440p  |

### 예시 2: API 테스트

파라미터:
- HTTP Method: GET, POST, PUT, DELETE
- Auth: token, api_key, none
- Content-Type: json, xml

전수: 24개 → 페어와이즈: 12개

### 테스트 수 감소 효과

| 파라미터 수 | 값 수  | 전수 조합 | 페어와이즈 | 감소율 |
|-------------|--------|-----------|------------|--------|
| 3           | 3      | 27        | 9          | 67%    |
| 4           | 3      | 81        | 9          | 89%    |
| 5           | 4      | 1,024     | 16         | 98%    |
| 10          | 3      | 59,049    | 15         | 99.9%  |

[⬆ 목차로 돌아가기](#목차)

## 5. 도구

| 도구       | 특징                          | URL                              |
|------------|-------------------------------|----------------------------------|
| PICT       | Microsoft, CLI 도구           | github.com/microsoft/pict        |
| AllPairs   | Python 라이브러리             | `pip install allpairspy`         |
| Jenny      | C 기반, 빠름                  | burtleburtle.net/bob/math/jenny  |

### PICT 사용 예시

```
# input.txt
OS: Windows, macOS, Linux
Browser: Chrome, Firefox, Safari
Resolution: 1080p, 1440p, 4K
```

```bash
pict input.txt
```

### allpairspy (Python)

```python
from allpairspy import AllPairs

parameters = [
    ["Windows", "macOS", "Linux"],
    ["Chrome", "Firefox", "Safari"],
    ["1080p", "1440p", "4K"],
]

for i, pair in enumerate(AllPairs(parameters)):
    print(f"TC{i+1}: {pair}")
```

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- PICT: [github.com/microsoft/pict](https://github.com/microsoft/pict) — ★★★☆☆
- ISTQB Foundation Level Syllabus — ★★★☆☆
- [결정 테이블 테스트](decision_table_testing.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-08

**마지막 업데이트**: 2026-05-08

© 2026 siasia86. Licensed under CC BY 4.0.

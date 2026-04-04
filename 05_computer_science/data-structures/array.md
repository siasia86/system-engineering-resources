# 배열 (Array)

## 개요

연속된 메모리 공간에 같은 타입의 데이터를 순서대로 저장하는 자료구조.

## 종류

| 종류              | 설명                                                        |
|-------------------|-----------------------------------------------------------|
| 정적 배열 (Static) | 크기 고정, 컴파일 타임에 결정                                 |
| 동적 배열 (Dynamic)| 크기 가변, 용량 초과 시 자동 확장 (Python list, Java ArrayList)|
| 다차원 배열        | 2D, 3D 등 행렬 표현에 사용                                   |

## 메모리 구조

```
+-----+-----+-----+-----+-----+
| [0] | [1] | [2] | [3] | [4] |
|  10 |  20 |  30 |  40 |  50 |
+-----+-----+-----+-----+-----+
  0x00  0x04  0x08  0x0C  0x10   (int 4byte 기준)
```

인덱스 접근 공식: `주소 = 시작주소 + (인덱스 × 요소크기)`

## 시간 복잡도

| 연산          | 시간 복잡도  | 비고                    |
|--------------|-------------|------------------------|
| 인덱스 접근    | O(1)        | 랜덤 액세스 가능          |
| 탐색 (선형)   | O(n)        | 정렬 안 된 경우           |
| 탐색 (이진)   | O(log n)    | 정렬된 경우              |
| 맨 뒤 삽입    | O(1)        | 동적 배열 amortized      |
| 중간 삽입/삭제 | O(n)        | 요소 이동 필요            |

## 동적 배열 확장 원리

```
용량 4 → 가득 참 → 새 배열(용량 8) 할당 → 복사 → 기존 해제

+---+---+---+---+
| 1 | 2 | 3 | 4 |  ← 가득 참
+---+---+---+---+

+---+---+---+---+---+---+---+---+
| 1 | 2 | 3 | 4 | 5 |   |   |   |  ← 2배 확장
+---+---+---+---+---+---+---+---+
```

## 구현 (Python)

```python
arr = []
arr.append(10)      # O(1) amortized
arr.insert(0, 5)    # O(n) - 맨 앞 삽입
arr.pop()           # O(1) - 맨 뒤 삭제
arr.pop(0)          # O(n) - 맨 앞 삭제
```

## 장단점

| 장점                    | 단점                        |
|------------------------|----------------------------|
| O(1) 랜덤 액세스        | 중간 삽입/삭제 O(n)          |
| 캐시 친화적 (연속 메모리) | 정적 배열은 크기 변경 불가     |
| 구현 단순               | 동적 배열 확장 시 복사 비용    |

## 활용

- 정렬 알고리즘의 기본 자료구조
- 행렬 연산
- 동적 프로그래밍 테이블
- 스택, 큐의 내부 구현

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-04

© 2026 siasia86. Licensed under CC BY 4.0.

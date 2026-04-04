# 힙 (Heap)

## 개요

완전 이진 트리 기반으로, 부모-자식 간 대소 관계를 유지하는 자료구조. 우선순위 큐 구현에 사용.

## 종류

| 종류     | 조건                       |
|---------|---------------------------|
| 최소 힙  | 부모 ≤ 자식 (루트가 최솟값)  |
| 최대 힙  | 부모 ≥ 자식 (루트가 최댓값)  |

## 구조

```
최소 힙:              최대 힙:
      1                    9
     / \                  / \
    3   5                7   8
   / \                  / \
  7   9                3   5
```

## 배열 표현

```
인덱스:  [0] [1] [2] [3] [4]
최소힙:   1   3   5   7   9

부모: (i - 1) // 2
왼쪽 자식: 2 * i + 1
오른쪽 자식: 2 * i + 2
```

## 핵심 연산

| 연산        | 시간 복잡도 | 설명                             |
|------------|------------|----------------------------------|
| insert     | O(log n)   | 맨 끝 삽입 후 위로 이동 (sift up)   |
| extract    | O(log n)   | 루트 제거 후 아래로 이동 (sift down) |
| peek       | O(1)       | 루트 값 조회                       |
| heapify    | O(n)       | 배열을 힙으로 변환                  |

## 구현 (Python)

```python
import heapq

# 최소 힙 (Python 기본)
h = []
heapq.heappush(h, 5)
heapq.heappush(h, 1)
heapq.heappush(h, 3)
print(heapq.heappop(h))  # 1

# 최대 힙 (부호 반전)
h = []
heapq.heappush(h, -5)
heapq.heappush(h, -1)
print(-heapq.heappop(h))  # 5

# 배열 → 힙 변환
arr = [5, 3, 8, 1, 2]
heapq.heapify(arr)  # O(n)
```

## 힙 정렬

```python
def heap_sort(arr):
    heapq.heapify(arr)
    return [heapq.heappop(arr) for _ in range(len(arr))]
```

시간 복잡도: O(n log n)

## 활용

- 우선순위 큐
- 다익스트라 최단 경로 알고리즘
- 힙 정렬
- 중앙값 구하기 (최대힙 + 최소힙)
- Top-K 문제

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

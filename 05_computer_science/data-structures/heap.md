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

### Sift Up / Sift Down 과정

```
Insert(2) - Sift Up:
      1                1                1
     / \              / \              / \
    3   5    →       3   2    →       3   2
   / \ /            / \ /            / \
  7  9 2           7  9 5           7  9 5
                  (6번 위치에 삽입) (2<5이므로 교환, 2>1이므로 멈춤)

Extract Min - Sift Down:
      1                9                3
     / \              / \              / \
    3   5    →       3   5    →       3   5
   / \              /                /
  7   9            7                7
(루트 1 제거,     (마지막 9→루트)   (9>3, 9>5 → 작은 자식 3과 교환)
 마지막 이동)
                       3
                      / \
                →    7   5
                    /
                   9
                  (9>7 → 교환, 리프 도달 → 멈춤. 최종: [3,7,5,9])
```

## 공간 복잡도

| 항목       | 복잡도  | 비고                    |
|-----------|--------|------------------------|
| 힙 저장    | O(n)   | 배열 기반, 추가 포인터 없음 |
| heapify   | O(1)   | in-place 변환 가능       |

## 구현 (Python)

### heapq 모듈 사용

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

# Top-K 최솟값
heapq.nsmallest(3, arr)  # 가장 작은 3개

# Top-K 최댓값
heapq.nlargest(3, arr)   # 가장 큰 3개
```

### 직접 구현 (최소 힙)

```python
class MinHeap:
    def __init__(self):
        self.heap = []

    def push(self, val):
        self.heap.append(val)
        self._sift_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            raise IndexError("heap is empty")
        self._swap(0, len(self.heap) - 1)
        val = self.heap.pop()
        if self.heap:
            self._sift_down(0)
        return val

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self.heap[i] < self.heap[parent]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i):
        n = len(self.heap)
        while 2 * i + 1 < n:
            child = 2 * i + 1
            if child + 1 < n and self.heap[child + 1] < self.heap[child]:
                child += 1
            if self.heap[i] > self.heap[child]:
                self._swap(i, child)
                i = child
            else:
                break

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
```

## heapify가 O(n)인 이유

- 리프 노드(절반)는 sift down 불필요
- 높이 h인 노드 수: `n / 2^(h+1)`, sift down 비용: O(h)
- 총합: `Σ (n / 2^(h+1)) × h` = O(n)
- 반면 n번 insert는 O(n log n)

## 힙 정렬

```python
def heap_sort(arr):
    heapq.heapify(arr)
    return [heapq.heappop(arr) for _ in range(len(arr))]
```

| 항목        | 값          |
|------------|-------------|
| 시간 복잡도  | O(n log n)  |
| 공간 복잡도  | O(1) (in-place 가능) |
| 안정 정렬    | ❌ 아님      |

## 자주 나오는 문제 패턴

| 문제                  | 핵심 접근법                          |
|----------------------|-------------------------------------|
| Top-K 빈출 요소       | 해시맵 카운팅 + 최소힙 크기 K 유지     |
| K번째 큰 수           | 최소힙 크기 K 유지                    |
| 스트림 중앙값          | 최대힙(왼쪽) + 최소힙(오른쪽) 균형 유지 |
| 정렬된 리스트 병합      | 각 리스트 head를 힙에 넣고 순차 추출   |
| 작업 스케줄링          | 우선순위 큐로 다음 작업 선택           |

## 활용

- 우선순위 큐
- 다익스트라 최단 경로 알고리즘
- 힙 정렬
- 중앙값 구하기 (최대힙 + 최소힙)
- Top-K 문제
- 허프만 코딩
- 운영체제 프로세스 스케줄링

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-05

© 2026 siasia86. Licensed under CC BY 4.0.

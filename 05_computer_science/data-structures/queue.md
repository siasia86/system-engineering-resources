# 큐 (Queue)

## 목차

| 단계 | 섹션                                                                                                                                           |
|----|------------------------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. 개요](#1-개요) / [2. 구조](#2-구조) / [3. 종류](#3-종류) / [4. 핵심 연산](#4-핵심-연산)                                                                      |
| 구현 | [5. 공간 복잡도](#5-공간-복잡도) / [6. 구현 (Python)](#6-구현-python) / [7. 원형 큐 구현](#7-원형-큐-구현) / [8. 덱 (Deque) 구현](#8-덱-deque-구현) / [9. 우선순위 큐](#9-우선순위-큐) |
| 실전 | [10. 자주 나오는 문제 패턴](#10-자주-나오는-문제-패턴) / [11. 활용](#11-활용)                                                                                      |

---

## 1. 개요

FIFO(First In, First Out) 원칙으로 동작하는 선형 자료구조. 먼저 삽입된 요소가 먼저 제거.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 구조

```
enqueue ──>  ┌────┬────┬────┬────┐  ──> dequeue
             │ 40 │ 30 │ 20 │ 10 │
             └────┴────┴────┴────┘
             rear              front
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 종류

| 종류                   | 설명                                     |
|------------------------|------------------------------------------|
| 선형 큐 (Linear)       | 기본 FIFO 큐                             |
| 원형 큐 (Circular)     | 배열 끝과 처음이 연결, 공간 재활용       |
| 덱 (Deque)             | 양쪽 끝에서 삽입/삭제 가능               |
| 우선순위 큐 (Priority) | 우선순위가 높은 요소 먼저 제거 (힙 기반) |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 핵심 연산

| 연산       | 설명                    | 시간 복잡도 |
|------------|-------------------------|-------------|
| enqueue(x) | rear에 요소 추가        | O(1)        |
| dequeue()  | front 요소 제거 및 반환 | O(1)        |
| peek()     | front 요소 조회         | O(1)        |
| isEmpty()  | 비어있는지 확인         | O(1)        |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 공간 복잡도

| 구현 방식   | 공간 복잡도 | 비고                      |
|-------------|-------------|---------------------------|
| 배열 (선형) | O(n)        | dequeue 시 앞쪽 공간 낭비 |
| 배열 (원형) | O(n)        | 공간 재활용, 낭비 없음    |
| 연결 리스트 | O(n)        | 노드당 포인터 오버헤드    |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 구현 (Python)

```python
from collections import deque

class Queue:
    def __init__(self):
        self.items = deque()

    def enqueue(self, val):
        self.items.append(val)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("queue is empty")
        return self.items.popleft()

    def peek(self):
        if self.is_empty():
            raise IndexError("queue is empty")
        return self.items[0]

    def is_empty(self):
        return len(self.items) == 0
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 원형 큐 구현

```
front=0, rear=4, capacity=5:

┌───┬───┬───┬───┬───┐
│ _ │ 2 │ 3 │ 4 │ _ │
└───┴───┴───┴───┴───┘
  0   1   2   3   4
      f           r

dequeue → front = (0+1) % 5 = 1
enqueue → rear  = (4+1) % 5 = 0  ← 앞쪽 재활용
```

```python
class CircularQueue:
    def __init__(self, capacity):
        self.arr = [None] * capacity
        self.cap = capacity
        self.front = self.rear = -1

    def enqueue(self, val):
        if (self.rear + 1) % self.cap == self.front:
            raise OverflowError("queue is full")
        if self.front == -1:
            self.front = 0
        self.rear = (self.rear + 1) % self.cap
        self.arr[self.rear] = val

    def dequeue(self):
        if self.front == -1:
            raise IndexError("queue is empty")
        val = self.arr[self.front]
        if self.front == self.rear:
            self.front = self.rear = -1
        else:
            self.front = (self.front + 1) % self.cap
        return val
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 덱 (Deque) 구현

```python
from collections import deque

dq = deque()
dq.append(1)       # 오른쪽 삽입
dq.appendleft(2)   # 왼쪽 삽입
dq.pop()           # 오른쪽 제거
dq.popleft()       # 왼쪽 제거

# 최대 크기 제한 (슬라이딩 윈도우에 유용)
dq = deque(maxlen=3)
dq.append(1)  # [1]
dq.append(2)  # [1, 2]
dq.append(3)  # [1, 2, 3]
dq.append(4)  # [2, 3, 4] ← 1 자동 제거
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 우선순위 큐

```python
import heapq

pq = []
heapq.heappush(pq, (2, "low"))     # (우선순위, 데이터)
heapq.heappush(pq, (1, "high"))
heapq.heappush(pq, (3, "lowest"))

print(heapq.heappop(pq))  # (1, 'high') ← 우선순위 높은 것 먼저
```

| 연산        | 시간 복잡도 |
|-------------|-------------|
| 삽입        | O(log n)    |
| 최솟값 제거 | O(log n)    |
| 최솟값 조회 | O(1)        |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 자주 나오는 문제 패턴

| 문제                   | 핵심 접근법                       |
|------------------------|-----------------------------------|
| BFS 탐색               | 큐에 시작점 넣고 레벨별 순회      |
| 슬라이딩 윈도우 최댓값 | 덱으로 단조 감소 유지             |
| 작업 스케줄링          | 우선순위 큐로 다음 작업 선택      |
| 스트림 중앙값          | 최대힙 + 최소힙 (우선순위 큐 2개) |

[⬆ 목차로 돌아가기](#목차)

---

## 11. 활용

- BFS (너비 우선 탐색)
- 프로세스 스케줄링 (라운드 로빈)
- 프린터 작업 대기열
- 메시지 큐 (Kafka, RabbitMQ)
- 캐시 구현
- 네트워크 패킷 버퍼
---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---
**작성일**: 2026-04-05
**마지막 업데이트**: 2026-04-22

© 2026 siasia86. Licensed under CC BY 4.0.

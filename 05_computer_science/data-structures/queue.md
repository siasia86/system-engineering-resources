# 큐 (Queue)

## 개요

FIFO(First In, First Out) 원칙으로 동작하는 선형 자료구조. 먼저 삽입된 요소가 먼저 제거.

## 구조

```
enqueue -->  +----+----+----+----+  --> dequeue
             | 40 | 30 | 20 | 10 |
             +----+----+----+----+
             rear              front
```

## 종류

| 종류                   | 설명                                   |
|-----------------------|----------------------------------------|
| 선형 큐 (Linear)       | 기본 FIFO 큐                            |
| 원형 큐 (Circular)     | 배열 끝과 처음이 연결, 공간 재활용         |
| 덱 (Deque)            | 양쪽 끝에서 삽입/삭제 가능                |
| 우선순위 큐 (Priority)  | 우선순위가 높은 요소 먼저 제거 (힙 기반)   |

## 핵심 연산

| 연산        | 설명                    | 시간 복잡도 |
|------------|------------------------|------------|
| enqueue(x) | rear에 요소 추가         | O(1)       |
| dequeue()  | front 요소 제거 및 반환   | O(1)       |
| peek()     | front 요소 조회          | O(1)       |
| isEmpty()  | 비어있는지 확인           | O(1)       |

## 구현 (Python)

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

## 원형 큐 구현

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

## 활용

- BFS (너비 우선 탐색)
- 프로세스 스케줄링 (라운드 로빈)
- 프린터 작업 대기열
- 메시지 큐 (Kafka, RabbitMQ)
- 캐시 구현

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

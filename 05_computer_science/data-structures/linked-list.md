# 연결 리스트 (Linked List)

## 개요

각 노드가 데이터와 다음 노드의 참조(포인터)를 가지는 선형 자료구조. 메모리상 비연속적으로 저장.

## 종류

| 종류                        | 설명                            |
|----------------------------|---------------------------------|
| 단일 연결 리스트 (Singly)     | 각 노드가 다음 노드만 참조        |
| 이중 연결 리스트 (Doubly)     | 각 노드가 이전/다음 노드 모두 참조 |
| 원형 연결 리스트 (Circular)   | 마지막 노드가 첫 노드를 참조       |

## 구조

```
단일 연결 리스트:
+------+    +------+    +------+
|  10  |--->|  20  |--->|  30  |---> None
+------+    +------+    +------+

이중 연결 리스트:
None <---+------+<--->+------+<--->+------+---> None
         |  10  |     |  20  |     |  30  |
         +------+     +------+     +------+

원형 연결 리스트:
+------+    +------+    +------+
|  10  |--->|  20  |--->|  30  |---+
+------+    +------+    +------+   |
   ^                               |
   +-------------------------------+
```

## 시간 복잡도

| 연산           | 시간 복잡도 | 비고                |
|---------------|------------|---------------------|
| 맨 앞 삽입/삭제 | O(1)       | head 포인터만 변경   |
| 맨 뒤 삽입     | O(1)       | tail 포인터 유지 시  |
| 중간 삽입/삭제  | O(1)       | 위치를 알고 있을 때   |
| 탐색           | O(n)       | 순차 접근만 가능     |

## 구현 (Python)

```python
class Node:
    def __init__(self, val):
        self.val = val
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def prepend(self, val):
        node = Node(val)
        node.next = self.head
        self.head = node
        if self.tail is None:
            self.tail = node

    def append(self, val):
        node = Node(val)
        if not self.head:
            self.head = self.tail = node
            return
        self.tail.next = node
        self.tail = node

    def delete(self, val):
        if not self.head:
            return
        if self.head.val == val:
            if self.head == self.tail:
                self.tail = None
            self.head = self.head.next
            return
        cur = self.head
        while cur.next and cur.next.val != val:
            cur = cur.next
        if cur.next:
            if cur.next == self.tail:
                self.tail = cur
            cur.next = cur.next.next
```

## 배열 vs 연결 리스트

| 항목          | 배열          | 연결 리스트       |
|--------------|--------------|------------------|
| 메모리 할당   | 연속          | 비연속            |
| 랜덤 액세스   | O(1)         | O(n)             |
| 삽입/삭제     | O(n)         | O(1) (위치 알 때)  |
| 캐시 효율     | 높음          | 낮음              |
| 메모리 오버헤드| 없음          | 포인터 추가 저장    |

## 활용

- 스택, 큐 구현
- LRU 캐시 (이중 연결 리스트 + 해시맵)
- 다항식 표현
- 운영체제 프로세스 관리

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

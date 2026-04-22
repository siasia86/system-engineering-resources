# 스택 (Stack)

## 개요

LIFO(Last In, First Out) 원칙으로 동작하는 선형 자료구조. 마지막에 삽입된 요소가 가장 먼저 제거.

## 구조

```
        ┌─────┐
push -->│ top │<-- pop
        ├─────┤
        │  30 │  ← top
        ├─────┤
        │  20 │
        ├─────┤
        │  10 │
        └─────┘
```

## 핵심 연산

| 연산      | 설명                       | 시간 복잡도 |
|-----------|----------------------------|-------------|
| push(x)   | top에 요소 추가            | O(1)        |
| pop()     | top 요소 제거 및 반환      | O(1)        |
| peek()    | top 요소 조회 (제거 안 함) | O(1)        |
| isEmpty() | 비어있는지 확인            | O(1)        |
| size()    | 요소 개수 반환             | O(1)        |

## 공간 복잡도

| 구현 방식   | 공간 복잡도 | 비고                         |
|-------------|-------------|------------------------------|
| 배열 기반   | O(n)        | 동적 배열 시 최대 2배 메모리 |
| 연결 리스트 | O(n)        | 노드당 포인터 오버헤드       |

## 구현 (Python)

```python
class Stack:
    def __init__(self):
        self.items = []

    def push(self, val):
        self.items.append(val)

    def pop(self):
        if self.is_empty():
            raise IndexError("stack is empty")
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("stack is empty")
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0
```

## 응용 구현

### 최소값 스택 (Min Stack)

push/pop/getMin 모두 O(1).

```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []

    def push(self, val):
        self.stack.append(val)
        if not self.min_stack or val <= self.min_stack[-1]:
            self.min_stack.append(val)

    def pop(self):
        val = self.stack.pop()
        if val == self.min_stack[-1]:
            self.min_stack.pop()
        return val

    def get_min(self):
        return self.min_stack[-1]
```

### 두 개 스택으로 큐 구현

```python
class QueueWithStacks:
    def __init__(self):
        self.in_stack = []
        self.out_stack = []

    def enqueue(self, val):
        self.in_stack.append(val)

    def dequeue(self):
        if not self.out_stack:
            while self.in_stack:
                self.out_stack.append(self.in_stack.pop())
        return self.out_stack.pop()
```

amortized O(1): 각 요소는 최대 2번 이동 (in → out)

## 활용 예시: 괄호 검사

```python
def is_valid(s):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for c in s:
        if c in '([{':
            stack.append(c)
        elif c in pairs:
            if not stack or stack[-1] != pairs[c]:
                return False
            stack.pop()
    return len(stack) == 0
```

## 활용 예시: 후위 표기법 계산

```
중위: 3 + 4 * 2  →  후위: 3 4 2 * +

계산 과정:
3 → push(3)           stack: [3]
4 → push(4)           stack: [3, 4]
2 → push(2)           stack: [3, 4, 2]
* → pop 4,2 → 4*2=8   stack: [3, 8]
+ → pop 3,8 → 3+8=11  stack: [11]
```

```python
def eval_postfix(tokens):
    stack = []
    ops = {'+': lambda a, b: a + b, '-': lambda a, b: a - b,
           '*': lambda a, b: a * b, '/': lambda a, b: int(a / b)}
    for t in tokens:
        if t in ops:
            b, a = stack.pop(), stack.pop()
            stack.append(ops[t](a, b))
        else:
            stack.append(int(t))
    return stack[0]
```

## 자주 나오는 문제 패턴

| 문제                      | 핵심 접근법                          |
|---------------------------|--------------------------------------|
| 괄호 유효성 검사          | 여는 괄호 push, 닫는 괄호 매칭 pop   |
| 후위 표기법 계산          | 피연산자 push, 연산자 만나면 pop 2개 |
| 다음 큰 수 (Next Greater) | 단조 감소 스택                       |
| 히스토그램 최대 넓이      | 단조 증가 스택                       |
| 문자열 디코딩             | 숫자/문자열 각각 스택에 저장         |

## 활용

- 함수 호출 스택 (Call Stack)
- 괄호 유효성 검사
- 후위 표기법 계산
- DFS (깊이 우선 탐색)
- Undo/Redo 기능
- 브라우저 뒤로가기/앞으로가기
- 컴파일러 구문 분석

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

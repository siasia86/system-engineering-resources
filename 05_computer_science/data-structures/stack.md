# 스택 (Stack)

## 개요

LIFO(Last In, First Out) 원칙으로 동작하는 선형 자료구조. 마지막에 삽입된 요소가 가장 먼저 제거.

## 구조

```
        +-----+
push -->| top |<-- pop
        +-----+
        |  30 |  ← top
        +-----+
        |  20 |
        +-----+
        |  10 |
        +-----+
```

## 핵심 연산

| 연산       | 설명                      | 시간 복잡도 |
|-----------|--------------------------|------------|
| push(x)   | top에 요소 추가            | O(1)       |
| pop()     | top 요소 제거 및 반환       | O(1)       |
| peek()    | top 요소 조회 (제거 안 함)  | O(1)       |
| isEmpty() | 비어있는지 확인             | O(1)       |

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

## 활용

- 함수 호출 스택 (Call Stack)
- 괄호 유효성 검사
- 후위 표기법 계산
- DFS (깊이 우선 탐색)
- Undo/Redo 기능
- 브라우저 뒤로가기/앞으로가기

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

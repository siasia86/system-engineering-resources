# 이진 트리 (Binary Tree)

## 개요

각 노드가 최대 2개의 자식 노드(왼쪽, 오른쪽)를 가지는 트리 자료구조.

## 종류

| 종류                          | 설명                                              |
|-------------------------------|---------------------------------------------------|
| 정 이진 트리 (Full)            | 모든 노드가 0개 또는 2개의 자식을 가짐              |
| 완전 이진 트리 (Complete)      | 마지막 레벨 제외 모두 채워지고, 왼쪽부터 채움        |
| 포화 이진 트리 (Perfect)       | 모든 내부 노드가 2개 자식, 리프 노드 같은 레벨       |
| 편향 이진 트리 (Skewed)        | 한쪽 방향으로만 자식이 존재                         |
| 이진 탐색 트리 (BST)           | 왼쪽 < 부모 < 오른쪽 정렬 규칙 유지                 |

## 구조

```
        1
       / \
      2   3
     / \   \
    4   5   6
```

## 속성

- 높이 h인 트리의 최대 노드 수: `2^(h+1) - 1`
- 노드 n개인 완전 이진 트리 높이: `⌊log₂(n)⌋`
- 리프 노드 수 = 차수 2인 노드 수 + 1

## 순회 (Traversal)

### 깊이 우선 탐색 (DFS)

| 순회 방식   | 순서              | 위 트리 결과     |
|------------|-------------------|-----------------|
| 전위 (Pre)  | 루트 → 왼 → 오    | 1 2 4 5 3 6    |
| 중위 (In)   | 왼 → 루트 → 오    | 4 2 5 1 3 6    |
| 후위 (Post) | 왼 → 오 → 루트    | 4 5 2 6 3 1    |

### 너비 우선 탐색 (BFS)

레벨 순서대로 방문: `1 2 3 4 5 6`

## 구현 (Python)

```python
class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

# 순회
def preorder(node):
    if not node:
        return []
    return [node.val] + preorder(node.left) + preorder(node.right)

def inorder(node):
    if not node:
        return []
    return inorder(node.left) + [node.val] + inorder(node.right)

def postorder(node):
    if not node:
        return []
    return postorder(node.left) + postorder(node.right) + [node.val]

def levelorder(root):
    if not root:
        return []
    queue, result = [root], []
    while queue:
        node = queue.pop(0)
        result.append(node.val)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return result
```

## 시간 복잡도

일반 이진 트리는 정렬 규칙이 없으므로 탐색/삽입/삭제 모두 O(n). 아래는 이진 탐색 트리(BST) 기준.

| 연산   | BST 평균    | BST 최악 (편향) | 일반 이진 트리 |
|--------|------------|----------------|--------------|
| 탐색   | O(log n)   | O(n)           | O(n)         |
| 삽입   | O(log n)   | O(n)           | O(n)         |
| 삭제   | O(log n)   | O(n)           | O(n)         |
| 순회   | O(n)       | O(n)           | O(n)         |

## 활용

- 이진 탐색 트리 (BST), AVL, Red-Black Tree의 기반
- 힙 (우선순위 큐)
- 허프만 코딩 (압축)
- 수식 트리 (Expression Tree)

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

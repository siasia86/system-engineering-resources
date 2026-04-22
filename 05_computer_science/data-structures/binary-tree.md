# 이진 트리 (Binary Tree)

## 목차

| 단계 | 섹션                                                                         |
|----|------------------------------------------------------------------------------|
| 기초 | [1. 개요](#1-개요) / [2. 용어 정리](#2-용어-정리) / [3. 종류](#3-종류) / [4. 속성](#4-속성)    |
| 탐색 | [5. 순회 (Traversal)](#5-순회-traversal) / [6. 구현 (Python)](#6-구현-python)      |
| 분석 | [7. 시간 복잡도](#7-시간-복잡도) / [8. 공간 복잡도](#8-공간-복잡도) / [9. 균형 이진 트리](#9-균형-이진-트리) |
| 실전 | [10. 자주 나오는 문제 패턴](#10-자주-나오는-문제-패턴) / [11. 활용](#11-활용)                    |

---

## 1. 개요

각 노드가 최대 2개의 자식 노드(왼쪽, 오른쪽)를 가지는 트리 자료구조.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 용어 정리

```
        1          ← 루트 (root), 깊이 0, 레벨 1
       / \
      2   3        ← 깊이 1, 레벨 2
     / \   \
    4   5   6      ← 깊이 2, 레벨 3 (리프 노드)
```

| 용어          | 설명                                                            |
|---------------|-----------------------------------------------------------------|
| 루트 (Root)   | 최상위 노드 (부모 없음)                                         |
| 리프 (Leaf)   | 자식이 없는 노드                                                |
| 내부 노드     | 자식이 1개 이상인 노드                                          |
| 깊이 (Depth)  | 루트에서 해당 노드까지의 간선 수                                |
| 높이 (Height) | 해당 노드에서 가장 먼 리프까지의 간선 수                        |
| 레벨 (Level)  | 깊이 + 1 (루트가 레벨 1). 교재에 따라 깊이=레벨로 정의하기도 함 |
| 차수 (Degree) | 노드의 자식 수                                                  |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 종류

| 종류                      | 설명                                             |
|---------------------------|--------------------------------------------------|
| 정 이진 트리 (Full)       | 모든 노드가 0개 또는 2개의 자식을 가짐           |
| 완전 이진 트리 (Complete) | 마지막 레벨 제외 모두 채워지고, 왼쪽부터 채움    |
| 포화 이진 트리 (Perfect)  | 모든 내부 노드가 2개 자식, 리프 노드 같은 레벨   |
| 편향 이진 트리 (Skewed)   | 한쪽 방향으로만 자식이 존재                      |
| 이진 탐색 트리 (BST)      | 왼쪽 서브트리 전체 < 부모 < 오른쪽 서브트리 전체 |

### 종류별 구조 비교

```
정 이진 트리 (Full):     완전 이진 트리 (Complete):   포화 이진 트리 (Perfect):
      1                       1                          1
     / \                     / \                        / \
    2   3                   2   3                      2   3
   / \                     / \ /                      / \ / \
  4   5                   4  5 6                     4  5 6  7

편향 이진 트리 (Skewed):
  1
   \
    2
     \
      3
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 속성

- 높이 h인 트리의 최대 노드 수: `2^(h+1) - 1`
- 높이 h인 트리의 최소 노드 수: `h + 1`
- 노드 n개인 완전 이진 트리 높이: `⌊log₂(n)⌋`
- 리프 노드 수(L) = 차수 2인 노드 수(T) + 1 → `L = T + 1`
- 포화 이진 트리의 리프 노드 수: `2^h`
- 간선 수 = 노드 수 - 1

[⬆ 목차로 돌아가기](#목차)

---

## 5. 순회 (Traversal)

```
        1
       / \
      2   3
     / \   \
    4   5   6
```

### 깊이 우선 탐색 (DFS)

| 순회 방식   | 순서           | 위 트리 결과 | 주요 용도              |
|-------------|----------------|--------------|------------------------|
| 전위 (Pre)  | 루트 → 왼 → 오 | 1 2 4 5 3 6  | 트리 복사, 직렬화      |
| 중위 (In)   | 왼 → 루트 → 오 | 4 2 5 1 3 6  | BST 정렬 순서 출력     |
| 후위 (Post) | 왼 → 오 → 루트 | 4 5 2 6 3 1  | 트리 삭제, 후위 표기법 |

### 너비 우선 탐색 (BFS)

레벨 순서대로 방문: `1 2 3 4 5 6`

용도: 최단 경로, 레벨별 처리

[⬆ 목차로 돌아가기](#목차)

---

## 6. 구현 (Python)

### 기본 노드 및 순회

```python
class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

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

### 반복문 기반 중위 순회 (스택 활용)

재귀 깊이 제한을 피할 때 사용.

```python
def inorder_iterative(root):
    stack, result = [], []
    cur = root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        result.append(cur.val)
        cur = cur.right
    return result
```

### BST 삽입 / 탐색 / 삭제

```python
def bst_insert(root, val):
    if not root:
        return Node(val)
    if val < root.val:
        root.left = bst_insert(root.left, val)
    elif val > root.val:
        root.right = bst_insert(root.right, val)
    return root

def bst_search(root, val):
    if not root or root.val == val:
        return root
    if val < root.val:
        return bst_search(root.left, val)
    return bst_search(root.right, val)

def bst_delete(root, val):
    if not root:
        return None
    if val < root.val:
        root.left = bst_delete(root.left, val)
    elif val > root.val:
        root.right = bst_delete(root.right, val)
    else:
        # 자식이 0~1개
        if not root.left:
            return root.right
        if not root.right:
            return root.left
        # 자식이 2개: 오른쪽 서브트리의 최솟값으로 대체
        successor = root.right
        while successor.left:
            successor = successor.left
        root.val = successor.val
        root.right = bst_delete(root.right, successor.val)
    return root
```

### 트리 높이 / 노드 수

```python
def height(node):
    if not node:
        return -1
    return 1 + max(height(node.left), height(node.right))

def count_nodes(node):
    if not node:
        return 0
    return 1 + count_nodes(node.left) + count_nodes(node.right)
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 시간 복잡도

일반 이진 트리는 정렬 규칙이 없으므로 탐색/삽입/삭제 모두 O(n). 아래는 이진 탐색 트리(BST) 기준.

| 연산 | BST 평균 | BST 최악 (편향) | 일반 이진 트리 |
|------|----------|-----------------|----------------|
| 탐색 | O(log n) | O(n)            | O(n)           |
| 삽입 | O(log n) | O(n)            | O(n)           |
| 삭제 | O(log n) | O(n)            | O(n)           |
| 순회 | O(n)     | O(n)            | O(n)           |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 공간 복잡도

| 항목             | 복잡도   | 비고                 |
|------------------|----------|----------------------|
| 트리 저장        | O(n)     | 노드 수만큼          |
| 재귀 순회 (균형) | O(log n) | 콜 스택 깊이         |
| 재귀 순회 (편향) | O(n)     | 최악의 콜 스택       |
| BFS (레벨 순회)  | O(w)     | w = 트리의 최대 너비 |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 균형 이진 트리

BST가 편향되면 O(n)으로 성능 저하 → 자동 균형 유지하는 트리가 필요.

| 종류           | 균형 조건                               | 회전 연산      |
|----------------|-----------------------------------------|----------------|
| AVL 트리       | 모든 노드의 좌우 높이 차이 ≤ 1          | 단일/이중 회전 |
| Red-Black 트리 | 색상 규칙으로 최장 경로 ≤ 최단 경로 × 2 | 색상 변경+회전 |

```
AVL 불균형 → 우회전 (Right Rotation):

    3              2
   /              / \
  2       →      1   3
 /
1

AVL 불균형 → 좌-우 이중 회전 (LR Rotation):

    3              3              2
   /              /              / \
  1       →      2       →     1   3
   \            /
    2          1
```

| 비교 항목 | AVL 트리            | Red-Black 트리        |
|-----------|---------------------|-----------------------|
| 탐색 속도 | 더 빠름 (엄격 균형) | 약간 느림             |
| 삽입/삭제 | 회전 빈번           | 회전 적음             |
| 사용 사례 | 읽기 위주           | 삽입/삭제 빈번        |
| 실제 구현 | DB 인덱스           | Java TreeMap, C++ map |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 자주 나오는 문제 패턴

| 문제                 | 핵심 접근법                     |
|----------------------|---------------------------------|
| 트리 높이 구하기     | 재귀: `1 + max(left, right)`    |
| 좌우 반전 (Mirror)   | 재귀로 left/right swap          |
| 두 트리 동일 여부    | 재귀로 val, left, right 비교    |
| 최소 공통 조상 (LCA) | 재귀로 좌우 탐색 후 분기점 반환 |
| BST 유효성 검사      | 중위 순회 시 오름차순인지 확인  |
| 직렬화/역직렬화      | 전위 순회 + null 마커           |

### 좌우 반전 예시

```python
def invert_tree(node):
    if not node:
        return None
    node.left, node.right = node.right, node.left
    invert_tree(node.left)
    invert_tree(node.right)
    return node
```

### 최소 공통 조상 (LCA) 예시

```python
def lca(root, p, q):
    if not root or root == p or root == q:
        return root
    left = lca(root.left, p, q)
    right = lca(root.right, p, q)
    if left and right:
        return root
    return left or right
```

[⬆ 목차로 돌아가기](#목차)

---

## 11. 활용

- 이진 탐색 트리 (BST), AVL, Red-Black Tree의 기반
- 힙 (우선순위 큐)
- 허프만 코딩 (압축)
- 수식 트리 (Expression Tree)
- 데이터베이스 B-Tree / B+Tree 인덱스의 기초 개념
- 파일 시스템 디렉토리 구조
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

# 그래프 (Graph)

## 개요

정점(Vertex)과 간선(Edge)으로 구성된 비선형 자료구조. 객체 간의 관계를 표현.

## 종류

| 종류              | 설명                          |
|------------------|-------------------------------|
| 무방향 그래프      | 간선에 방향 없음 (A — B)       |
| 방향 그래프        | 간선에 방향 있음 (A → B)       |
| 가중치 그래프      | 간선에 비용/거리 값 존재        |
| 완전 그래프        | 모든 정점이 서로 연결           |
| 이분 그래프        | 두 그룹으로 나눠 그룹 간만 연결  |
| DAG              | 방향 비순환 그래프              |

## 구조

```
무방향 그래프:          방향 그래프:
  A --- B               A --> B
  |   / |               |     |
  |  /  |               v     v
  C --- D               C --> D
```

## 표현 방법

### 인접 행렬 (Adjacency Matrix)

```
    A  B  C  D
A [ 0, 1, 1, 0 ]
B [ 1, 0, 1, 1 ]
C [ 1, 1, 0, 1 ]
D [ 0, 1, 1, 0 ]
```

### 인접 리스트 (Adjacency List)

```
A → [B, C]
B → [A, C, D]
C → [A, B, D]
D → [B, C]
```

## 인접 행렬 vs 인접 리스트

| 항목          | 인접 행렬     | 인접 리스트    |
|--------------|-------------|---------------|
| 공간 복잡도   | O(V²)       | O(V + E)      |
| 간선 존재 확인 | O(1)        | O(degree)     |
| 모든 인접 정점 | O(V)        | O(degree)     |
| 적합한 경우   | 밀집 그래프   | 희소 그래프    |

## 탐색 알고리즘

### DFS (깊이 우선 탐색)

```python
def dfs(graph, start):
    visited = set()
    stack = [start]
    result = []
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            result.append(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    stack.append(neighbor)
    return result
```

### BFS (너비 우선 탐색)

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    result = []
    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return result
```

## 시간 복잡도

| 알고리즘  | 인접 리스트  | 인접 행렬  |
|----------|------------|-----------|
| DFS      | O(V + E)   | O(V²)    |
| BFS      | O(V + E)   | O(V²)    |

## 활용

- 소셜 네트워크 (친구 관계)
- 지도/네비게이션 (최단 경로)
- 웹 크롤링 (링크 구조)
- 작업 스케줄링 (위상 정렬)
- 네트워크 라우팅

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

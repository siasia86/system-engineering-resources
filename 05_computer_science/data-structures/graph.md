# 그래프 (Graph)

## 목차

| 단계 | 섹션                                                                                                                                            |
|------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. 개요](#1-개요) / [2. 용어 정리](#2-용어-정리) / [3. 종류](#3-종류) / [4. 구조](#4-구조)                                                                       |
| 표현 | [5. 표현 방법](#5-표현-방법) / [6. 인접 행렬 vs 인접 리스트](#6-인접-행렬-vs-인접-리스트)                                                                               |
| 알고리즘 | [7. 탐색 알고리즘](#7-탐색-알고리즘) / [8. 위상 정렬 (Topological Sort)](#8-위상-정렬-topological-sort) / [9. 사이클 탐지](#9-사이클-탐지) / [10. 최단 경로 알고리즘](#10-최단-경로-알고리즘) |
| 분석 | [11. 시간 복잡도](#11-시간-복잡도) / [12. 공간 복잡도](#12-공간-복잡도)                                                                                           |
| 실전 | [13. 자주 나오는 문제 패턴](#13-자주-나오는-문제-패턴) / [14. 활용](#14-활용)                                                                                       |

---

## 1. 개요

정점(Vertex)과 간선(Edge)으로 구성된 비선형 자료구조. 객체 간의 관계를 표현.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 용어 정리

| 용어            | 설명                             |
|-----------------|----------------------------------|
| 정점 (Vertex)   | 그래프의 노드                    |
| 간선 (Edge)     | 정점 간의 연결                   |
| 차수 (Degree)   | 정점에 연결된 간선 수            |
| 진입 차수 (In)  | 방향 그래프에서 들어오는 간선 수 |
| 진출 차수 (Out) | 방향 그래프에서 나가는 간선 수   |
| 경로 (Path)     | 정점 간 간선의 연속              |
| 사이클 (Cycle)  | 시작 정점으로 돌아오는 경로      |
| 연결 요소       | 서로 도달 가능한 정점들의 집합   |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 종류

| 종류          | 설명                            |
|---------------|---------------------------------|
| 무방향 그래프 | 간선에 방향 없음 (A — B)        |
| 방향 그래프   | 간선에 방향 있음 (A → B)        |
| 가중치 그래프 | 간선에 비용/거리 값 존재        |
| 완전 그래프   | 모든 정점이 서로 연결           |
| 이분 그래프   | 두 그룹으로 나눠 그룹 간만 연결 |
| DAG           | 방향 비순환 그래프              |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 구조

```
무방향 그래프:          방향 그래프:          가중치 그래프:
  A --- B               A --> B              A --3-- B
  |   / |               |     |              |      /|
  |  /  |               v     v              5    2  4
  C --- D               C --> D              |  /    |
                                             C --1-- D
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 표현 방법

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

### 간선 리스트 (Edge List)

```
[(A,B), (A,C), (B,C), (B,D), (C,D)]
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 인접 행렬 vs 인접 리스트

| 항목           | 인접 행렬   | 인접 리스트 |
|----------------|-------------|-------------|
| 공간 복잡도    | O(V²)       | O(V + E)    |
| 간선 존재 확인 | O(1)        | O(degree)   |
| 모든 인접 정점 | O(V)        | O(degree)   |
| 간선 추가      | O(1)        | O(1)        |
| 적합한 경우    | 밀집 그래프 | 희소 그래프 |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 탐색 알고리즘

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

# 재귀 버전
def dfs_recursive(graph, node, visited=None):
    if visited is None:
        visited = set()
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)
    return visited
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

[⬆ 목차로 돌아가기](#목차)

---

## 8. 시간 복잡도

| 알고리즘 | 인접 리스트 | 인접 행렬 |
|----------|-------------|-----------|
| DFS      | O(V + E)    | O(V²)     |
| BFS      | O(V + E)    | O(V²)     |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 공간 복잡도

| 항목          | 인접 행렬 | 인접 리스트 |
|---------------|-----------|-------------|
| 그래프 저장   | O(V²)     | O(V + E)    |
| DFS 방문 배열 | O(V)      | O(V)        |
| BFS 큐        | O(V)      | O(V)        |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 위상 정렬 (Topological Sort)

DAG에서 선후 관계를 유지하며 정렬. 작업 스케줄링에 사용.

```
A → B → D
|       ^
+→ C ---+

위상 정렬 결과: A → B → C → D  또는  A → C → B → D
```

```python
from collections import deque

def topological_sort(graph, in_degree):
    queue = deque([v for v in in_degree if in_degree[v] == 0])
    result = []
    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    if len(result) != len(in_degree):
        return []  # 사이클 존재
    return result
```

[⬆ 목차로 돌아가기](#목차)

---

## 11. 사이클 탐지

### 무방향 그래프: Union-Find

```python
def find(parent, x):
    if parent[x] != x:
        parent[x] = find(parent, parent[x])
    return parent[x]

def union(parent, rank, a, b):
    a, b = find(parent, a), find(parent, b)
    if a == b:
        return False  # 사이클 발견
    if rank[a] < rank[b]:
        a, b = b, a
    parent[b] = a
    if rank[a] == rank[b]:
        rank[a] += 1
    return True
```

### 방향 그래프: DFS 색상법

```python
def has_cycle_directed(graph):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {v: WHITE for v in graph}

    def dfs(node):
        color[node] = GRAY
        for neighbor in graph[node]:
            if color[neighbor] == GRAY:
                return True  # 사이클
            if color[neighbor] == WHITE and dfs(neighbor):
                return True
        color[node] = BLACK
        return False

    return any(color[v] == WHITE and dfs(v) for v in graph)
```

[⬆ 목차로 돌아가기](#목차)

---

## 12. 최단 경로 알고리즘

| 알고리즘      | 용도               | 시간 복잡도      |
|---------------|--------------------|------------------|
| BFS           | 가중치 없는 그래프 | O(V + E)         |
| 다익스트라    | 양의 가중치        | O((V + E) log V) |
| 벨만-포드     | 음의 가중치 허용   | O(V × E)         |
| 플로이드-워셜 | 모든 쌍 최단 경로  | O(V³)            |

### 다익스트라 구현

```python
import heapq

def dijkstra(graph, start):
    dist = {v: float('inf') for v in graph}
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    return dist
```

[⬆ 목차로 돌아가기](#목차)

---

## 13. 자주 나오는 문제 패턴

| 문제                  | 핵심 접근법                          |
|-----------------------|--------------------------------------|
| 섬의 개수             | DFS/BFS로 연결 요소 카운팅           |
| 최단 경로             | BFS (무가중치) / 다익스트라 (가중치) |
| 작업 순서 (선수 과목) | 위상 정렬                            |
| 사이클 탐지           | DFS 색상법 / Union-Find              |
| 이분 그래프 판별      | BFS로 2색 칠하기                     |

[⬆ 목차로 돌아가기](#목차)

---

## 14. 활용

- 소셜 네트워크 (친구 관계)
- 지도/네비게이션 (최단 경로)
- 웹 크롤링 (링크 구조)
- 작업 스케줄링 (위상 정렬)
- 네트워크 라우팅
- 추천 시스템
- 컴파일러 의존성 분석
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

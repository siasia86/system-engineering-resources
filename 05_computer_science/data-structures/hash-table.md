# 해시 테이블 (Hash Table)

## 목차

| 단계 | 섹션                                                                                                                            |
|----|---------------------------------------------------------------------------------------------------------------------------------|
| 기초 | [1. 개요](#1-개요) / [2. 구조](#2-구조) / [3. 좋은 해시 함수의 조건](#3-좋은-해시-함수의-조건)                                                          |
| 충돌 | [4. 해시 충돌 해결](#4-해시-충돌-해결) / [5. 적재율 (Load Factor)](#5-적재율-load-factor)                                                       |
| 분석 | [6. 시간 복잡도](#6-시간-복잡도) / [7. 공간 복잡도](#7-공간-복잡도)                                                                               |
| 실전 | [8. 구현 (Python)](#8-구현-python) / [9. 언어별 해시 테이블 구현](#9-언어별-해시-테이블-구현) / [10. 자주 나오는 문제 패턴](#10-자주-나오는-문제-패턴) / [11. 활용](#11-활용) |

---

## 1. 개요

키(Key)를 해시 함수로 변환하여 값(Value)을 저장/조회하는 자료구조. 평균 O(1) 접근 가능.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 구조

```
Key        Hash Function     Bucket
┌───────┐                  ┌────────┐
│ "cat" │ ──> hash() ──>   │ [0]    │
├───────┤                  ├────────┤
│ "dog" │ ──> hash() ──>   │ [1] ───┬──> ("dog", 5)
├───────┤                  ├────────┤
│ "ant" │ ──> hash() ──>   │ [2] ───┬──> ("ant", 3) ──> ("cat", 7)
└───────┘                  ├────────┤    (Collision → Chaining)
                           │ [3]    │
                           └────────┘
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 좋은 해시 함수의 조건

| 조건        | 설명                                |
|-------------|-------------------------------------|
| 균등 분포   | 키가 버킷에 고르게 분산             |
| 결정적      | 같은 입력 → 항상 같은 출력          |
| 빠른 계산   | O(1) 시간에 해시값 계산             |
| 눈사태 효과 | 입력이 조금 바뀌면 출력이 크게 변함 |

대표적 해시 함수: 나눗셈법, 곱셈법, MurmurHash, SHA 계열

[⬆ 목차로 돌아가기](#목차)

---

## 4. 해시 충돌 해결

| 방법                          | 설명                           |
|-------------------------------|--------------------------------|
| 체이닝 (Chaining)             | 같은 버킷에 연결 리스트로 저장 |
| 개방 주소법 (Open Addressing) | 다른 빈 버킷을 탐색하여 저장   |
| ├ 선형 탐사 (Linear)          | 다음 칸으로 순차 이동          |
| ├ 이차 탐사 (Quadratic)       | 1², 2², 3² 간격으로 이동       |
| └ 이중 해싱 (Double)          | 두 번째 해시 함수로 간격 결정  |

### 체이닝 vs 개방 주소법

| 비교 항목   | 체이닝             | 개방 주소법           |
|-------------|--------------------|-----------------------|
| 구현 난이도 | 쉬움               | 보통                  |
| 적재율 제한 | 1.0 초과 가능      | 1.0 미만이어야 함     |
| 캐시 효율   | 낮음 (포인터 추적) | 높음 (연속 메모리)    |
| 삭제 처리   | 간단               | 복잡 (tombstone 필요) |
| 클러스터링  | 없음               | 선형 탐사 시 발생     |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 시간 복잡도

| 연산 | 평균 | 최악 (모두 충돌) |
|------|------|------------------|
| 삽입 | O(1) | O(n)             |
| 탐색 | O(1) | O(n)             |
| 삭제 | O(1) | O(n)             |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 공간 복잡도

| 항목            | 복잡도 | 비고                        |
|-----------------|--------|-----------------------------|
| 전체 저장       | O(n)   | n = 저장된 키-값 쌍 수      |
| 체이닝 오버헤드 | O(n)   | 연결 리스트 포인터          |
| 빈 버킷         | O(m)   | m = 버킷 수 (보통 n보다 큼) |

[⬆ 목차로 돌아가기](#목차)

---

## 7. 구현 (Python)

### 체이닝 방식

```python
class HashTable:
    def __init__(self, size=16):
        self.size = size
        self.count = 0
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        return hash(key) % self.size

    def put(self, key, val):
        idx = self._hash(key)
        for i, (k, v) in enumerate(self.table[idx]):
            if k == key:
                self.table[idx][i] = (key, val)
                return
        self.table[idx].append((key, val))
        self.count += 1
        if self.count / self.size > 0.75:
            self._resize()

    def get(self, key):
        idx = self._hash(key)
        for k, v in self.table[idx]:
            if k == key:
                return v
        raise KeyError(key)

    def delete(self, key):
        idx = self._hash(key)
        for i, (k, v) in enumerate(self.table[idx]):
            if k == key:
                del self.table[idx][i]
                self.count -= 1
                return
        raise KeyError(key)

    def _resize(self):
        old = self.table
        self.size *= 2
        self.count = 0
        self.table = [[] for _ in range(self.size)]
        for bucket in old:
            for k, v in bucket:
                self.put(k, v)
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 적재율 (Load Factor)

```
적재율 α = 저장된 요소 수(n) / 버킷 수(m)
```

| 적재율 범위 | 상태                              |
|-------------|-----------------------------------|
| α < 0.5     | 여유 있음, 충돌 적음              |
| 0.5~0.75    | 적정 범위                         |
| α > 0.75    | 리사이징 권장 (2배 확장 + 재해싱) |
| α > 1.0     | 체이닝만 가능, 성능 저하          |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 언어별 해시 테이블 구현

| 언어   | 자료구조      | 충돌 해결                           |
|--------|---------------|-------------------------------------|
| Python | dict          | 개방 주소법 (탐사)                  |
| Java   | HashMap       | 체이닝 (8개 초과 시 Red-Black Tree) |
| C++    | unordered_map | 체이닝                              |
| Go     | map           | 체이닝 (버킷 배열)                  |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 자주 나오는 문제 패턴

| 문제                       | 핵심 접근법               |
|----------------------------|---------------------------|
| 두 수의 합 (Two Sum)       | 해시맵에 보수 저장, O(n)  |
| 애너그램 그룹              | 정렬된 문자열을 키로 사용 |
| 중복 문자 없는 부분 문자열 | 해시셋 + 슬라이딩 윈도우  |
| 빈도수 카운팅              | Counter / defaultdict     |
| LRU 캐시                   | 해시맵 + 이중 연결 리스트 |

[⬆ 목차로 돌아가기](#목차)

---

## 11. 활용

- Python `dict`, Java `HashMap`
- 데이터베이스 인덱싱
- 캐시 (Redis, Memcached)
- 중복 검사
- 문자열 빈도 카운팅
- 라우팅 테이블
- 심볼 테이블 (컴파일러)
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

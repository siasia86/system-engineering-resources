# 해시 테이블 (Hash Table)

## 개요

키(Key)를 해시 함수로 변환하여 값(Value)을 저장/조회하는 자료구조. 평균 O(1) 접근 가능.

## 구조

```
Key        Hash Function     Bucket
+-------+                  +--------+
| "cat" | ---> hash() ---> | [0]    |
+-------+                  +--------+
| "dog" | ---> hash() ---> | [1] ---+--> ("dog", 5)
+-------+                  +--------+
| "ant" | ---> hash() ---> | [2] ---+--> ("ant", 3) --> ("cat", 7)
+-------+                  +--------+    (충돌 → 체이닝)
                           | [3]    |
                           +--------+
```

## 해시 충돌 해결

| 방법                         | 설명                            |
|-----------------------------|--------------------------------|
| 체이닝 (Chaining)            | 같은 버킷에 연결 리스트로 저장    |
| 개방 주소법 (Open Addressing) | 다른 빈 버킷을 탐색하여 저장      |
| ├ 선형 탐사 (Linear)         | 다음 칸으로 순차 이동             |
| ├ 이차 탐사 (Quadratic)      | 1², 2², 3² 간격으로 이동         |
| └ 이중 해싱 (Double)         | 두 번째 해시 함수로 간격 결정     |

## 시간 복잡도

| 연산 | 평균   | 최악 (모두 충돌) |
|------|--------|-----------------|
| 삽입 | O(1)   | O(n)            |
| 탐색 | O(1)   | O(n)            |
| 삭제 | O(1)   | O(n)            |

## 구현 (Python)

```python
class HashTable:
    def __init__(self, size=16):
        self.size = size
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
                return
        raise KeyError(key)
```

## 적재율 (Load Factor)

```
적재율 = 저장된 요소 수 / 버킷 수
```

- 적재율이 높아지면 충돌 증가 → 성능 저하
- 일반적으로 0.75 초과 시 리사이징 (2배 확장 + 재해싱)

## 활용

- Python `dict`, Java `HashMap`
- 데이터베이스 인덱싱
- 캐시 (Redis, Memcached)
- 중복 검사
- 문자열 빈도 카운팅

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

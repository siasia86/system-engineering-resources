# 확률적 자료구조: 블룸 필터·HyperLogLog·Count-Min Sketch

정확한 답 대신 작은 오차를 허용하고 메모리를 크게 줄이는 확률적 자료구조(probabilistic data structure)를 정리합니다. 존재 여부(블룸 필터·쿠쿠 필터), 고유 개수(HyperLogLog), 빈도(Count-Min Sketch)를 다루며, Redis·Cassandra·PostgreSQL에서 실제로 설정하는 값과 크기 계산법을 함께 봅니다.

## 목차

| 섹션                                                                                                                                                 |
|------------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 왜 확률적 자료구조인가](#1-왜-확률적-자료구조인가) / [2. 블룸 필터 원리](#2-블룸-필터-원리) / [3. 블룸 필터 크기 계산](#3-블룸-필터-크기-계산)   |
| [4. 블룸 필터 구현 (Python)](#4-블룸-필터-구현-python) / [5. 블룸 필터의 한계와 변형](#5-블룸-필터의-한계와-변형) / [6. HyperLogLog](#6-hyperloglog) |
| [7. Count-Min Sketch](#7-count-min-sketch) / [8. 실제 시스템의 사용 예](#8-실제-시스템의-사용-예) / [9. 선택 기준과 점검표](#9-선택-기준과-점검표)   |

---

## 1. 왜 확률적 자료구조인가

수억 개의 항목을 다룰 때 정확한 집합(해시 테이블)은 항목 수에 비례하는 메모리가 필요합니다. 확률적 자료구조는 항목 자체를 저장하지 않고 해시 결과만 요약해 고정된 작은 메모리로 근사 답을 냅니다.

| 질문                       | 정확한 방법      | 확률적 방법      | 오차의 형태              |
|----------------------------|------------------|------------------|--------------------------|
| 이 항목이 집합에 있는가    | 해시 집합        | 블룸·쿠쿠 필터   | "있다"가 틀릴 수 있음    |
| 서로 다른 항목이 몇 개인가 | 해시 집합의 크기 | HyperLogLog      | 개수 추정치에 표준 오차  |
| 이 항목이 몇 번 나왔는가   | 해시 맵 카운터   | Count-Min Sketch | 실제보다 크게 셀 수 있음 |

공통 조건은 "약간 틀려도 되는 질문"이어야 한다는 점입니다. 과금·권한 판정처럼 정확해야 하는 판단에는 단독으로 쓰지 않고, 비싼 정확한 조회 앞의 거름망으로 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 블룸 필터 원리

블룸 필터(Bloom filter)는 Burton H. Bloom이 1970년 발표한 구조로, m비트 배열과 k개의 해시 함수로 이루어집니다.

- 추가: 항목을 k개의 해시 함수에 넣어 나온 k개 위치의 비트를 1로 바꿉니다.
- 조회: k개 위치가 모두 1이면 "아마 있음", 하나라도 0이면 "확실히 없음"입니다.

```text
m = 16 bits, k = 3

add("apple")  -> h1=2, h2=7, h3=11
add("banana") -> h1=4, h2=7, h3=14

index  0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
bits   0 0 1 0 1 0 0 1 0 0  0  1  0  0  1  0

query("cherry") -> 2, 4, 14  -> all 1 -> "maybe" (false positive)
query("grape")  -> 3, 7, 11  -> bit 3 is 0 -> "definitely not"
```

| 응답 | 의미                                  | 틀릴 수 있는가         |
|------|---------------------------------------|------------------------|
| 없음 | 한 번도 추가되지 않음                 | 아니요(거짓 음성 없음) |
| 있음 | 추가되었거나, 다른 항목과 비트가 겹침 | 예(거짓 양성)          |

Redis 문서도 블룸 필터는 "없음"은 보장하고 "있음"은 추정만 한다고 설명합니다. 그래서 "없으면 비싼 조회를 건너뛴다"는 용도에 맞습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 블룸 필터 크기 계산

항목 수 n, 목표 거짓 양성률 p가 주어지면 필요한 비트 수와 해시 함수 수는 다음과 같습니다(Redis 블룸 필터 문서의 식).

```text
bits per item   = -ln(p) / (ln 2)^2
total bits  m   = n * -ln(p) / (ln 2)^2
hash count  k   = ceil(-ln(p) / ln 2)
```

| 목표 거짓 양성률 | 해시 함수 수 k | 항목당 비트 | 100만 항목 메모리(약) |
|------------------|----------------|-------------|-----------------------|
| 1%               | 7              | 9.585       | 1.14 MiB              |
| 0.1%             | 10             | 14.378      | 1.71 MiB              |
| 0.01%            | 14             | 19.170      | 2.29 MiB              |

거짓 양성률을 10배 줄일 때마다 항목당 약 4.8비트가 더 필요합니다. 비교하면 IPv4 주소 100만 개를 Redis 집합(Set)에 넣으면 Redis 문서 기준 항목당 약 40바이트(320비트)가 필요합니다.

설계 크기 n보다 많이 넣으면 거짓 양성률이 빠르게 오릅니다. 실제 m, k에서 n개를 넣었을 때의 근사 거짓 양성률은 `(1 - e^(-k*n/m))^k`입니다.

```python
import math

def bloom_fp_rate(m_bits: int, k: int, n: int) -> float:
    return (1 - math.exp(-k * n / m_bits)) ** k

m = 9_585_059          # sized for 1,000,000 items at 1%
for n in (1_000_000, 2_000_000, 4_000_000):
    print(n, f"{bloom_fp_rate(m, 7, n):.2%}")
# 1000000 1.00%
# 2000000 15.75%
# 4000000 67.87%
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 블룸 필터 구현 (Python)

k개의 독립 해시 함수 대신 해시값 두 개를 조합해 k개 위치를 만드는 방식(double hashing)을 씁니다.

```python
import hashlib
import math


class BloomFilter:
    def __init__(self, capacity: int, error_rate: float):
        self.m = math.ceil(-capacity * math.log(error_rate) / math.log(2) ** 2)
        self.k = math.ceil(-math.log(error_rate) / math.log(2))
        self.bits = bytearray((self.m + 7) // 8)

    def _positions(self, item: str):
        digest = hashlib.sha256(item.encode()).digest()
        h1 = int.from_bytes(digest[:8], "big")
        h2 = int.from_bytes(digest[8:16], "big") | 1
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def add(self, item: str) -> None:
        for pos in self._positions(item):
            self.bits[pos // 8] |= 1 << (pos % 8)

    def __contains__(self, item: str) -> bool:
        return all(self.bits[pos // 8] & (1 << (pos % 8))
                   for pos in self._positions(item))


bf = BloomFilter(capacity=100_000, error_rate=0.01)
for i in range(100_000):
    bf.add(f"blocked:{i}")

print("m bits:", bf.m, "k:", bf.k, "bytes:", len(bf.bits))
print("no false negative:", all(f"blocked:{i}" in bf for i in range(100_000)))
fp = sum(f"other:{i}" in bf for i in range(100_000))
print(f"false positive rate: {fp / 100_000:.3%}")
```

실행 결과(2026-11-16, Python 3)는 다음과 같습니다. 거짓 음성은 없고 거짓 양성률은 목표값 1% 근처입니다.

```text
m bits: 958506 k: 7 bytes: 119814
no false negative: True
false positive rate: 1.016%
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 블룸 필터의 한계와 변형

| 한계                | 설명                         | 대안                                               |
|---------------------|------------------------------|----------------------------------------------------|
| 삭제 불가           | 비트 하나를 여러 항목이 공유 | 카운팅 블룸 필터(비트 대신 작은 카운터), 쿠쿠 필터 |
| 크기 고정           | n을 넘기면 오차 급증         | 확장형(scalable) 블룸 필터: 하위 필터를 쌓음       |
| 항목 목록 복원 불가 | 해시 결과만 남음             | 원본 저장소를 별도로 유지                          |
| 해시 품질 의존      | 해시가 치우치면 오차 증가    | 분포가 고른 비암호 해시(MurmurHash 등) 사용        |

Redis의 `BF.RESERVE`는 용량을 넘으면 기존 크기에 `EXPANSION`(기본 2)을 곱한 하위 필터를 새로 쌓습니다. 이때 추가 지연은 그대로지만 조회는 하위 필터를 차례로 확인하므로 느려집니다. 크기를 알면 `NONSCALING`으로 고정합니다.

쿠쿠 필터(cuckoo filter)는 항목의 짧은 지문(fingerprint)을 버킷에 저장하는 구조로, Redis 문서는 블룸 필터가 추가에, 쿠쿠 필터가 조회와 삭제에 유리하다고 정리합니다.

🟡 블룸 필터는 항목을 직접 저장하지 않지만, 후보 값을 하나씩 넣어 보면 포함 여부를 추측할 수 있습니다. 개인정보 목록을 필터로 공유할 때 이를 익명화로 간주하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. HyperLogLog

HyperLogLog(HLL)는 Flajolet 등이 2007년 발표한 고유 개수(cardinality) 추정 알고리즘입니다. 각 항목의 해시값 앞부분으로 레지스터(register)를 고르고, 나머지 비트에서 연속된 0의 개수 최댓값을 기록합니다. 해시가 고르게 퍼져 있으면 0이 길게 이어진 값을 볼 확률로 전체 개수를 추정할 수 있습니다.

```text
hash(item) = 0b 00000110 1100 0001 0000...
               |-- p bits --|-- rest --|
               register idx   count leading zeros (+1)

register[idx] = max(register[idx], leading_zeros + 1)
estimate      = harmonic mean of 2^register[i], corrected
```

레지스터 수가 m일 때 표준 오차는 약 `1.04 / sqrt(m)`입니다. Redis 구현은 최대 12KB를 쓰며 표준 오차 0.81%를 제공한다고 문서화되어 있습니다(16,384개 레지스터 × 6비트 = 12,288바이트, 1.04 / sqrt(16384) ≈ 0.81%).

```bash
# Redis HyperLogLog: 일별 고유 방문자 추정
redis-cli PFADD visitors:2026-11-16 user:1 user:2 user:3
redis-cli PFADD visitors:2026-11-17 user:3 user:4
redis-cli PFCOUNT visitors:2026-11-16                       # 3
redis-cli PFMERGE visitors:week visitors:2026-11-16 visitors:2026-11-17
redis-cli PFCOUNT visitors:week                             # 4 (approx.)
```

| 특징      | 내용                                                 |
|-----------|------------------------------------------------------|
| 병합 가능 | 기간·서버별 HLL을 합쳐 전체 고유 수 추정 (`PFMERGE`) |
| 교집합    | 직접 지원하지 않음, 합집합 공식으로 근사하면 오차 큼 |
| 작은 개수 | Redis는 희소(sparse) 표현으로 메모리를 더 적게 씀    |
| 항목 조회 | 불가, 개수만 추정                                    |

[⬆ 목차로 돌아가기](#목차)

---

## 7. Count-Min Sketch

Count-Min Sketch(CMS)는 Cormode와 Muthukrishnan이 2005년 Journal of Algorithms에 발표한 빈도 추정 구조입니다. 폭 w, 깊이 d인 카운터 행렬과 d개의 해시 함수를 씁니다.

```text
d = 3 rows, w = 8 columns

add(x):   row0[h0(x)] += 1 ; row1[h1(x)] += 1 ; row2[h2(x)] += 1
query(x): min(row0[h0(x)], row1[h1(x)], row2[h2(x)])

row0  0 3 0 1 0 0 5 0
row1  1 0 0 0 4 0 0 3
row2  0 0 3 0 0 2 0 1
```

충돌한 다른 항목의 카운트가 더해질 수는 있어도 빠지지는 않으므로, 추정값은 실제 값 이상입니다. 여러 행의 최솟값을 취해 과대 추정을 줄입니다.

Redis 문서는 `CMS.INITBYPROB key error probability`의 의미를 다음처럼 설명합니다.

| 매개변수      | 결정하는 것          | 해석                                               |
|---------------|----------------------|----------------------------------------------------|
| `error`       | 폭 w                 | 신뢰 가능한 임계값 = `error × 전체 카운트 합`      |
| `probability` | 깊이 d(해시 함수 수) | 임계값 아래 항목이 큰 항목과 모든 행에서 겹칠 확률 |

```bash
redis-cli CMS.INITBYPROB req:by_ip 0.001 0.002
redis-cli CMS.INCRBY req:by_ip 192.0.2.10 120 192.0.2.20 3
redis-cli CMS.QUERY req:by_ip 192.0.2.10 192.0.2.20
redis-cli CMS.INFO req:by_ip        # width 2000, depth 9, count 123
```

임계값보다 작은 추정값은 잡음으로 보고 버립니다. 그래서 CMS는 "가장 많이 요청한 IP", "많이 팔린 상품" 같은 상위 항목(heavy hitter) 탐지에 맞고, 드문 항목의 정확한 횟수에는 맞지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 실제 시스템의 사용 예

| 시스템                   | 구조                         | 용도                                   | 설정·명령                                      |
|--------------------------|------------------------------|----------------------------------------|------------------------------------------------|
| Redis Open Source 8 이상 | 블룸·쿠쿠·CMS·Top-K·t-digest | 내장 자료형(이전에는 RedisBloom 모듈)  | `BF.*`, `CF.*`, `CMS.*`, `TOPK.*`, `TDIGEST.*` |
| Redis                    | HyperLogLog                  | 고유 방문자 수                         | `PFADD`, `PFCOUNT`, `PFMERGE`                  |
| Cassandra                | 블룸 필터                    | 키가 없는 SSTable 디스크 읽기 생략     | 테이블 옵션 `bloom_filter_fp_chance`           |
| PostgreSQL               | 블룸 필터                    | 여러 칼럼 임의 조합의 등호 검색 인덱스 | `contrib` 확장 `bloom`                         |

Cassandra 문서에 따르면 `bloom_filter_fp_chance` 기본값은 LeveledCompactionStrategy 테이블에서 0.1, 그 밖에서 0.01입니다. 값을 낮추면 메모리를 더 쓰고 불필요한 디스크 읽기가 줄어듭니다. 변경은 새로 쓰는 SSTable부터 적용됩니다.

```sql
-- Cassandra: 거짓 양성률 조정 (기존 SSTable은 compaction 또는
-- nodetool upgradesstables -a 로 다시 쓸 때 반영)
ALTER TABLE shop.orders WITH bloom_filter_fp_chance = 0.01;
```

```sql
-- PostgreSQL: bloom 확장 (int4, text 타입의 = 검색만 지원)
CREATE EXTENSION bloom;
CREATE INDEX bloomidx ON tbloom USING bloom (i1, i2, i3)
    WITH (length = 80, col1 = 2, col2 = 2, col3 = 4);
```

PostgreSQL 18 문서 기준 `length`는 기본 80비트(최대 4096), `colN`은 칼럼당 비트 수(기본 2)이며, 결과에 거짓 양성이 있을 수 있어 테이블에서 다시 확인합니다.

🟡 `nodetool upgradesstables -a`는 모든 SSTable을 다시 써서 디스크 I/O와 임시 공간을 많이 씁니다. 부하가 낮은 시간에 노드별로 실행합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 선택 기준과 점검표

| 상황                                         | 선택                        |
|----------------------------------------------|-----------------------------|
| "없음"을 빠르게 걸러 비싼 조회를 줄이고 싶음 | 블룸 필터                   |
| 거르기 + 삭제가 필요함                       | 쿠쿠 필터, 카운팅 블룸 필터 |
| 고유 사용자·IP 수를 기간·서버별로 합산       | HyperLogLog                 |
| 스트림에서 많이 나온 항목과 대략의 횟수      | Count-Min Sketch, Top-K     |
| 결과가 정확해야 함(과금, 권한, 감사)         | 정확한 자료구조             |

| 점검 항목                                                     | 확인 |
|---------------------------------------------------------------|------|
| 허용 오차의 방향(거짓 양성·과대 추정)이 업무에 문제가 없는가  | ☐    |
| 예상 항목 수 n과 목표 오차로 크기를 계산했는가                | ☐    |
| 설계 크기를 넘는 증가를 감시하거나 확장 방식을 정했는가       | ☐    |
| "있음" 응답 뒤에 원본 저장소로 다시 확인하는 경로가 있는가    | ☐    |
| 필터·스케치를 재생성할 원본 데이터와 절차가 있는가            | ☐    |
| 개인 식별 정보를 넣는 경우 추측 공격과 법적 요건을 검토했는가 | ☐    |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [해시 테이블](hash_table.md)
- [머클 트리](merkle_tree.md)
- [Redis 개념](../../../05_database/nosql/nosql_redis.md)
- [일관된 해싱](../algorithms/consistent_hashing.md)
- Burton H. Bloom: [Space/Time Trade-offs in Hash Coding with Allowable Errors (CACM, 1970)](https://doi.org/10.1145/362686.362692) — ★★★★☆ (확인일 2026-11-16)
- Flajolet 외: [HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm (AofA 2007)](https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf) — ★★★★☆ (확인일 2026-11-16)
- Graham Cormode, S. Muthukrishnan: [An Improved Data Stream Summary: The Count-Min Sketch and its Applications (Journal of Algorithms, 2005)](https://doi.org/10.1016/j.jalgor.2003.12.001) — ★★★★☆ (확인일 2026-11-16)
- Redis Documentation: [Bloom filter](https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/) — ★★★☆☆ (확인일 2026-11-16)
- Redis Documentation: [HyperLogLog](https://redis.io/docs/latest/develop/data-types/probabilistic/hyperloglogs/) — ★★★☆☆ (확인일 2026-11-16)
- Redis Documentation: [Count-min sketch](https://redis.io/docs/latest/develop/data-types/probabilistic/count-min-sketch/) — ★★★☆☆ (확인일 2026-11-16)
- RedisBloom: [GitHub 저장소 (Redis 8부터 Redis에 통합)](https://github.com/RedisBloom/RedisBloom) — ★★★☆☆ (확인일 2026-11-16)
- Apache Cassandra Documentation: [Bloom Filters](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/bloom_filters.html) — ★★★☆☆ (확인일 2026-11-16)
- PostgreSQL 18 Documentation: [bloom — bloom filter index access method](https://www.postgresql.org/docs/current/bloom.html) — ★★★☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.

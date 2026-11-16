# 일관된 해싱
<!-- reference: _reference/web_server_official_notes.md -->

서버 수가 바뀌어도 대부분의 키가 원래 서버에 그대로 남도록 키를 서버에 배정하는 일관된 해싱(consistent hashing)을 정리합니다. 모듈러 해싱의 문제, 해시 링과 가상 노드, 랑데부 해싱·점프 해싱·Maglev 같은 변형, 부하 상한을 둔 방식, 그리고 HAProxy·NGINX에서 설정하는 방법을 다룹니다.

## 목차

| 섹션                                                                                                                                                             |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [1. 문제: 모듈러 해싱의 재배치](#1-문제-모듈러-해싱의-재배치) / [2. 해시 링](#2-해시-링) / [3. 가상 노드와 가중치](#3-가상-노드와-가중치)                        |
| [4. 구현과 재배치 측정 (Python)](#4-구현과-재배치-측정-python) / [5. 랑데부 해싱](#5-랑데부-해싱) / [6. 점프 해싱과 Maglev](#6-점프-해싱과-maglev)               |
| [7. 부하 상한이 있는 일관된 해싱](#7-부하-상한이-있는-일관된-해싱) / [8. 로드 밸런서 설정](#8-로드-밸런서-설정) / [9. 선택 기준과 점검표](#9-선택-기준과-점검표) |

---

## 1. 문제: 모듈러 해싱의 재배치

가장 단순한 배정은 `server = hash(key) % N`입니다. 서버 수 N이 고정이면 고르게 나뉘지만, N이 바뀌면 거의 모든 키의 배정이 바뀝니다.

```text
hash(key) % 4  ->  hash(key) % 5

key hash   %4   %5   moved?
   10       2    0    yes
   11       3    1    yes
   12       0    2    yes
   13       1    3    yes
   20       0    0    no
```

N에서 N+1로 바뀔 때 제자리에 남는 키는 대략 1/(N+1)뿐입니다. 캐시 서버라면 서버 하나를 추가한 순간 캐시 대부분이 무효가 되어 원본 서버(DB·오리진)로 요청이 몰립니다. 이를 캐시 미스 폭주라 부르며, 증설이 오히려 장애를 부르는 원인이 됩니다.

NGINX 문서도 `hash` 지시어에 `consistent`를 붙이지 않으면 서버를 추가·제거할 때 "대부분의 키가 다른 서버로 다시 매핑될 수 있다"고 설명합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 해시 링

일관된 해싱은 Karger 등이 1997년 STOC 논문에서 웹 캐시의 핫스팟 문제를 풀기 위해 제안했습니다. 기본 아이디어는 서버와 키를 같은 해시 공간(예: 0 ~ 2^32 − 1)에 올리고 그 공간을 원(링)으로 보는 것입니다.

1. 각 서버를 해시해 링 위의 한 점에 놓습니다.
2. 키를 해시해 링 위의 위치를 구합니다.
3. 키 위치에서 시계 방향으로 처음 만나는 서버가 담당 서버입니다.

```text
                 0 / 2^32
                    |
          S-A  *         * key1 -> S-B
                \       /
     key3 ->     \     /
     S-A          ring
                 /     \
          S-C  *        * S-B
                 \     /
                  key2 -> S-C
```

| 변화      | 영향받는 키                                        |
|-----------|----------------------------------------------------|
| 서버 추가 | 새 서버와 그 앞(반시계 방향) 서버 사이의 키만 이동 |
| 서버 제거 | 제거된 서버가 맡던 키만 다음 서버로 이동           |

서버 N개에서 하나를 더하면 평균적으로 약 1/(N+1)의 키만 움직입니다. 모듈러 방식과 비율이 정반대입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 가상 노드와 가중치

서버마다 링 위에 점 하나만 두면 점 사이 간격이 우연에 따라 크게 달라져 부하가 치우칩니다. 또 서버 하나가 빠지면 그 몫이 바로 다음 서버 하나에 몰립니다.

가상 노드(virtual node)는 서버 하나를 링 위의 여러 점(예: `cache-a#0` ~ `cache-a#99`)으로 올리는 방법입니다.

| 효과        | 설명                                                     |
|-------------|----------------------------------------------------------|
| 분포 균등화 | 점이 많을수록 서버별 담당 구간 합이 평균에 가까워짐      |
| 장애 분산   | 빠진 서버의 몫이 여러 서버로 나뉘어 이동                 |
| 가중치      | 성능이 두 배인 서버에 가상 노드를 두 배 배정             |
| 비용        | 링 크기(메모리)와 탐색 시간이 늘어남(이진 탐색 O(log V)) |

NGINX의 `hash ... consistent`는 ketama 방식을 쓰며, 문서는 이를 `ketama_points`를 160으로 둔 Cache::Memcached::Fast Perl 라이브러리와 호환된다고 밝힙니다. HAProxy의 `hash-type consistent`도 "각 서버의 여러 점이 들어간 트리"에서 가장 가까운 서버를 고릅니다.

🟡 여러 로드 밸런서가 같은 배정을 내려면 서버 이름·ID·가중치·해시 함수가 모두 같아야 합니다. HAProxy 문서도 여러 로드 밸런서에서 같은 분포를 얻으려면 모든 서버의 ID가 정확히 같아야 한다고 설명합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 구현과 재배치 측정 (Python)

```python
import bisect
import hashlib


def h(value: str) -> int:
    return int.from_bytes(hashlib.md5(value.encode()).digest()[:8], "big")


class HashRing:
    def __init__(self, nodes, vnodes=100):
        self.vnodes = vnodes
        self.ring = []  # sorted list of (hash, node)
        for node in nodes:
            self.add(node)

    def add(self, node):
        for i in range(self.vnodes):
            bisect.insort(self.ring, (h(f"{node}#{i}"), node))

    def remove(self, node):
        self.ring = [(p, n) for p, n in self.ring if n != node]

    def get(self, key):
        idx = bisect.bisect(self.ring, (h(key), ""))
        return self.ring[idx % len(self.ring)][1]


keys = [f"user:{i}" for i in range(100_000)]
nodes = ["cache-a", "cache-b", "cache-c", "cache-d"]

before_mod = {k: nodes[h(k) % 4] for k in keys}
after_mod = {k: (nodes + ["cache-e"])[h(k) % 5] for k in keys}
moved = sum(before_mod[k] != after_mod[k] for k in keys)
print(f"modulo 4->5 moved: {moved / len(keys):.1%}")

ring = HashRing(nodes)
before = {k: ring.get(k) for k in keys}
ring.add("cache-e")
after = {k: ring.get(k) for k in keys}
moved = sum(before[k] != after[k] for k in keys)
print(f"ring   4->5 moved: {moved / len(keys):.1%}")
```

실행 결과(2026-11-16, Python 3)입니다. MD5는 여기서 보안 용도가 아니라 고른 분포를 얻기 위한 해시로만 씁니다.

```text
modulo 4->5 moved: 79.9%
ring   4->5 moved: 19.1%
```

이론값(모듈러 약 80%, 링 약 20% = 1/5)과 가깝습니다. 가상 노드 수를 줄이면 서버별 담당 비율의 편차가 커지므로, 실제 분포를 측정해 가상 노드 수를 정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 랑데부 해싱

랑데부 해싱(rendezvous hashing)은 HRW(Highest Random Weight)라고도 하며, Thaler와 Ravishankar가 1998년 IEEE/ACM Transactions on Networking 논문에서 정리했습니다. 링 없이 키마다 모든 서버의 점수를 계산해 가장 높은 서버를 고릅니다.

```python
import hashlib


def score(node: str, key: str) -> int:
    return int.from_bytes(hashlib.sha256(f"{node}:{key}".encode()).digest()[:8], "big")


def pick(nodes, key):
    return max(nodes, key=lambda n: score(n, key))


nodes = ["cache-a", "cache-b", "cache-c", "cache-d"]
keys = [f"user:{i}" for i in range(50_000)]
before = {k: pick(nodes, k) for k in keys}
after = {k: pick([n for n in nodes if n != "cache-b"], k) for k in keys}
moved = [k for k in keys if before[k] != after[k]]
print(f"HRW remove cache-b moved: {len(moved) / len(keys):.1%}")
print("all moved keys were on cache-b:", all(before[k] == "cache-b" for k in moved))
# HRW remove cache-b moved: 24.9%
# all moved keys were on cache-b: True
```

| 항목          | 해시 링                     | 랑데부 해싱                          |
|---------------|-----------------------------|--------------------------------------|
| 조회 비용     | O(log V) (V = 가상 노드 수) | O(N) (N = 서버 수)                   |
| 추가 메모리   | 링 배열                     | 없음                                 |
| 분포          | 가상 노드 수에 의존         | 가상 노드 없이도 고름                |
| 상위 k개 선택 | 링을 따라 다음 서버         | 점수 순 상위 k개(복제본 배치에 편리) |

서버 수가 수십 대 이하이면 계산 비용이 작아 랑데부 해싱이 단순하고, 수천 대 이상이면 링이나 테이블 방식이 유리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 점프 해싱과 Maglev

### 6.1 점프 해싱

점프 일관된 해싱(jump consistent hash)은 Lamping과 Veach가 2014년 발표한 알고리즘으로, 저장 공간 없이 몇 줄의 코드로 키를 0 ~ N−1 버킷에 배정합니다.

```python
def jump_hash(key: int, num_buckets: int) -> int:
    b, j = -1, 0
    while j < num_buckets:
        b = j
        key = (key * 2862933555777941757 + 1) & 0xFFFFFFFFFFFFFFFF
        j = int((b + 1) * ((1 << 31) / ((key >> 33) + 1)))
    return b


keys = range(100_000)
moved = sum(jump_hash(k, 10) != jump_hash(k, 11) for k in keys)
print(f"jump 10->11 moved: {moved / len(keys):.1%}")   # 9.0% (theory 1/11)
```

논문이 밝힌 제약은 버킷 번호가 연속이어야 한다는 점입니다. 마지막 버킷만 늘리거나 줄일 수 있고 가운데 서버를 임의로 빼기 어렵기 때문에, 샤드 번호가 고정된 데이터 저장소에 맞고 서버가 수시로 죽고 살아나는 웹 캐시에는 덜 맞습니다.

### 6.2 Maglev 해싱

Maglev는 Google이 NSDI 2016에서 발표한 소프트웨어 네트워크 로드 밸런서이며, 일관된 해싱과 연결 추적(connection tracking)으로 장애 때 연결 단위 프로토콜의 영향을 줄입니다. 서버별 선호 순열로 고정 크기 조회 테이블을 채워, 조회는 배열 접근 한 번이고 서버 변화 시 테이블의 일부만 바뀝니다. 같은 패킷 흐름이 여러 로드 밸런서 중 어디로 가더라도 같은 백엔드로 가야 하는 L4 로드 밸런서에 쓰입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 부하 상한이 있는 일관된 해싱

일관된 해싱은 키 수를 고르게 나누지만, 요청이 특정 키에 몰리면(인기 상품, 대형 고객) 그 키의 서버만 과부하가 됩니다. Mirrokni, Thorup, Zadimoghaddam의 "Consistent Hashing with Bounded Loads"(arXiv 1608.01350)는 서버 부하가 평균의 c배(c = 1 + ε)를 넘지 않도록 상한을 두고, 넘으면 링의 다음 서버로 넘기는 방식을 분석했습니다.

HAProxy는 이를 `hash-balance-factor`로 제공합니다.

| 설정값    | 의미                                              |
|-----------|---------------------------------------------------|
| 0         | 기본값, 기능 꺼짐                                 |
| 150       | 어떤 서버도 평균 동시 요청의 1.5배를 넘지 않게 함 |
| 125 ~ 200 | 문서가 제시하는 적정 범위                         |

값이 낮을수록 고르지만 더 많은 서버를 확인하므로 성능 비용이 있고, 높을수록 캐시 적중률(같은 키는 같은 서버)이 유지됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 로드 밸런서 설정

### 8.1 HAProxy

HAProxy 3.2 문서 기준 `hash-type`의 기본값은 `map-based`입니다. map-based는 서버 수가 바뀌면 대부분의 연결이 다른 서버로 재분배되므로 캐시 앞에서는 `consistent`를 씁니다. `consistent`는 해시 함수를 지정하지 않으면 `sdbm`과 `avalanche`를 씁니다.

```haproxy
backend cache_servers
    balance uri
    hash-type consistent sdbm avalanche
    hash-balance-factor 150
    server cache-a 192.0.2.11:80 id 1 check
    server cache-b 192.0.2.12:80 id 2 check
    server cache-c 192.0.2.13:80 id 3 check
```

| 방법         | 서버 증감 시        | 가중치 변경(서버 동작 중) | 분포의 고름 |
|--------------|---------------------|---------------------------|-------------|
| `map-based`  | 대부분 재배치       | 무시됨(slow start 없음)   | 고름        |
| `consistent` | 해당 서버 몫만 이동 | 반영됨                    | 덜 고름     |

### 8.2 NGINX

```nginx
upstream cache_servers {
    hash $request_uri consistent;
    server 192.0.2.11:80;
    server 192.0.2.12:80;
    server 192.0.2.13:80;
}
```

`hash` 지시어는 NGINX 1.7.2부터 있으며, `consistent`가 없으면 서버 증감 때 대부분의 키가 다시 매핑될 수 있습니다. `ip_hash`는 IPv4 주소의 앞 세 옥텟(IPv6는 전체 주소)을 키로 쓰는 별도 방식이고, 서버를 잠시 빼면서 기존 배정을 유지하려면 `down`으로 표시합니다.

🟡 설정 변경 전 `haproxy -c -f <설정 파일>` 또는 `nginx -t`로 문법을 검사하고, 운영 반영은 reload로 합니다. 해시 방식을 바꾸는 순간 배정이 한 번 크게 바뀌어 캐시 적중률이 떨어지므로 트래픽이 적은 시간에 바꿉니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 선택 기준과 점검표

| 상황                                                         | 선택                                      |
|--------------------------------------------------------------|-------------------------------------------|
| 서버 수가 고정이고 바뀔 때 재배치를 감수함                   | 모듈러 해싱(`map-based`)                  |
| 캐시 서버가 수시로 추가·제거됨                               | 해시 링 + 가상 노드(`consistent`)         |
| 서버 수십 대 이하, 복제본 k개 배치가 필요함                  | 랑데부 해싱                               |
| 샤드 번호가 연속이고 끝에서만 늘어남                         | 점프 해싱                                 |
| L4 로드 밸런서 여러 대가 같은 흐름을 같은 백엔드로 보내야 함 | Maglev 계열 테이블                        |
| 인기 키 때문에 특정 서버가 과부하                            | 부하 상한(`hash-balance-factor`), 키 복제 |

| 점검 항목                                                         | 확인 |
|-------------------------------------------------------------------|------|
| 서버 1대 추가·제거 시 이동하는 키 비율을 측정했는가               | ☐    |
| 서버별 담당 비율의 편차를 측정하고 가상 노드 수·가중치를 정했는가 | ☐    |
| 여러 로드 밸런서·클라이언트가 같은 서버 ID·해시 함수를 쓰는가     | ☐    |
| 해시 키(URI, 사용자 ID, IP)가 충분히 다양한가(NAT 뒤 IP 쏠림 등)  | ☐    |
| 인기 키 쏠림을 감시하고 부하 상한 또는 키 분산 대책이 있는가      | ☐    |
| 해시 방식 변경 시 캐시 적중률 하락과 원본 부하를 예상했는가       | ☐    |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [HAProxy 개념](../../../02_infrastructure/web_server/haproxy_concepts.md)
- [로드 밸런서 테스트](../web_testing/load_balancer_testing.md)
- [해시 테이블](../data_structures/hash_table.md)
- [분산 시스템 기초 개념](../distributed_systems_concepts.md)
- [웹 서버 공식 참조 노트](../../../_reference/web_server_official_notes.md)
- Karger 외: [Consistent Hashing and Random Trees (STOC 1997)](https://doi.org/10.1145/258533.258660) — ★★★★☆ (확인일 2026-11-16)
- David G. Thaler, Chinya V. Ravishankar: [Using Name-Based Mappings to Increase Hit Rates (IEEE/ACM ToN, 1998)](https://www.cs.ucr.edu/~ravi/Papers/Jrnl/HRW98.pdf) — ★★★★☆ (확인일 2026-11-16)
- John Lamping, Eric Veach: [A Fast, Minimal Memory, Consistent Hash Algorithm (arXiv 1406.2294)](https://arxiv.org/abs/1406.2294) — ★★★★☆ (확인일 2026-11-16)
- Eisenbud 외: [Maglev: A Fast and Reliable Software Network Load Balancer (NSDI 2016)](https://www.usenix.org/conference/nsdi16/technical-sessions/presentation/eisenbud) — ★★★★☆ (확인일 2026-11-16)
- Mirrokni, Thorup, Zadimoghaddam: [Consistent Hashing with Bounded Loads (arXiv 1608.01350)](https://arxiv.org/abs/1608.01350) — ★★★★☆ (확인일 2026-11-16)
- HAProxy 3.2 Documentation: [Configuration Manual (hash-type, hash-balance-factor)](https://docs.haproxy.org/3.2/configuration.html) — ★★★☆☆ (확인일 2026-11-16)
- NGINX Documentation: [ngx_http_upstream_module (hash, ip_hash)](https://nginx.org/en/docs/http/ngx_http_upstream_module.html) — ★★★☆☆ (확인일 2026-11-16)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.

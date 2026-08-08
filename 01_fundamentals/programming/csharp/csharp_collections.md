# C# 컬렉션
<!-- reference: _reference/csharp_official_notes.md -->

C#의 주요 컬렉션 타입 — 선택 기준, 특성, 스레드 안전 컬렉션, 불변 컬렉션을 정리합니다.

## 목차

| 섹션                                                                                                                           |
|--------------------------------------------------------------------------------------------------------------------------------|
| [1. 컬렉션 선택 기준](#1-컬렉션-선택-기준) / [2. 주요 컬렉션 타입](#2-주요-컬렉션-타입) / [3. 딕셔너리 계열](#3-딕셔너리-계열) |
| [4. 스레드 안전 컬렉션](#4-스레드-안전-컬렉션) / [5. 불변 컬렉션](#5-불변-컬렉션) / [6. 성능 비교](#6-성능-비교)               |

---

## 1. 컬렉션 선택 기준

```
순서 있는 컬렉션?
├── 빠른 인덱스 접근 필요     → List<T>  (동적 배열, 가장 범용)
├── 고정 크기, 성능 민감      → T[]      (배열, 가장 빠름)
├── 양쪽 끝 삽입/삭제 빈번    → LinkedList<T>
└── LIFO / FIFO 구조 필요     → Stack<T> / Queue<T>

키-값 매핑?
├── 일반 용도                 → Dictionary<K,V>  (해시 기반, O(1))
├── 키 정렬 필요              → SortedDictionary<K,V>  (레드-블랙 트리)
├── 메모리 효율 + 정렬        → SortedList<K,V>
└── 중복 키 허용              → ILookup<K,V>  (ToLookup()으로 생성)

집합 연산?
└── 중복 없는 집합            → HashSet<T>  / SortedSet<T>

멀티스레드?
├── 읽기 많고 쓰기 드뭄       → ImmutableArray<T> / ImmutableDictionary<K,V>
├── 동시 쓰기                 → ConcurrentDictionary<K,V>
└── 생산자-소비자             → ConcurrentQueue<T> / BlockingCollection<T>
```

---

## 2. 주요 컬렉션 타입

### List\<T\> — 동적 배열 (가장 범용)

```csharp
var list = new List<int> { 1, 2, 3 };

// 추가 / 삽입
list.Add(4);                    // 끝에 추가 — O(1) 분할 상환
list.Insert(0, 0);              // 인덱스 삽입 — O(n) (이동 비용)
list.AddRange([5, 6, 7]);       // 범위 추가

// 제거
list.Remove(3);                 // 값으로 제거 — O(n)
list.RemoveAt(0);               // 인덱스로 제거 — O(n) (이동 비용)
list.RemoveAll(n => n % 2 == 0); // 조건 제거

// 조회
var item = list[2];             // 인덱스 접근 — O(1)
int idx = list.IndexOf(5);     // 위치 조회 — O(n)
bool has = list.Contains(4);   // 존재 확인 — O(n)

// 정렬
list.Sort();                                   // 기본 정렬
list.Sort((a, b) => b.CompareTo(a));           // 내림차순

// 용량 관리
var sized = new List<int>(capacity: 1000);    // 사전 용량 지정 (재할당 감소)
list.TrimExcess();                             // 잉여 용량 반환
```

🟡 `List<T>`는 내부적으로 배열을 2배씩 확장합니다. 크기를 미리 알면 `new List<T>(capacity)` 로 재할당 비용을 줄입니다.

### Stack\<T\> / Queue\<T\>

```csharp
// Stack<T> — LIFO
var stack = new Stack<int>();
stack.Push(1);
stack.Push(2);
stack.Push(3);

int top = stack.Peek();         // 3 — 꺼내지 않고 확인
int popped = stack.Pop();       // 3 — 꺼내기
bool has = stack.TryPeek(out var val); // 안전 버전

// Queue<T> — FIFO
var queue = new Queue<int>();
queue.Enqueue(1);
queue.Enqueue(2);

int front = queue.Peek();       // 1 — 꺼내지 않고 확인
int dequeued = queue.Dequeue(); // 1 — 꺼내기
bool ok = queue.TryDequeue(out var item); // 안전 버전
```

### LinkedList\<T\>

```csharp
var linked = new LinkedList<int>();
var node = linked.AddLast(1);
linked.AddLast(2);
linked.AddFirst(0);             // 앞에 추가 — O(1)
linked.AddAfter(node, 10);      // 특정 노드 뒤에 추가 — O(1)
linked.Remove(node);            // 노드 제거 — O(1)
```

🟡 `LinkedList<T>`는 노드 삽입/삭제가 O(1)이지만 인덱스 접근이 O(n)이고 캐시 효율이 낮습니다. 삽입/삭제가 매우 빈번한 경우에만 `List<T>` 대신 사용합니다.

### HashSet\<T\> / SortedSet\<T\>

```csharp
var set = new HashSet<int> { 1, 2, 3, 4, 5 };
set.Add(3);                     // 이미 있으면 false 반환, 중복 없음
set.Remove(3);
bool has = set.Contains(2);     // O(1)

// 집합 연산
var other = new HashSet<int> { 3, 4, 5, 6 };
set.IntersectWith(other);       // 교집합 (in-place)
set.UnionWith(other);           // 합집합 (in-place)
set.ExceptWith(other);          // 차집합 (in-place)
bool isSubset = set.IsSubsetOf(other);

// SortedSet<T> — 정렬 유지
var sorted = new SortedSet<int> { 5, 3, 1, 4, 2 }; // 내부 정렬 유지
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 딕셔너리 계열

### Dictionary\<K, V\> — 해시 기반, 가장 범용

```csharp
var dict = new Dictionary<string, int>
{
    ["apple"]  = 1,
    ["banana"] = 2,
};

// 추가 / 업데이트
dict["cherry"] = 3;             // 없으면 추가, 있으면 업데이트
dict.Add("date", 4);            // 이미 존재하면 예외
bool added = dict.TryAdd("apple", 99); // false (이미 존재)

// 조회
int val = dict["apple"];        // 없으면 KeyNotFoundException
bool ok = dict.TryGetValue("mango", out var v); // 안전 조회

// 삭제
dict.Remove("banana");

// 순회
foreach (var (key, value) in dict)
    Console.WriteLine($"{key}: {value}");

// 키/값 컬렉션
IEnumerable<string> keys = dict.Keys;
IEnumerable<int> values = dict.Values;
```

### GetValueOrDefault / CollectionsMarshal (고성능)

```csharp
// GetValueOrDefault — 없으면 default 반환 (C# 7.2+)
int count = dict.GetValueOrDefault("apple", 0);

// 값 업데이트 in-place (ref 반환, .NET 6+)
// dict에 키가 없으면 추가 후 ref 반환
ref int refVal = ref System.Runtime.InteropServices.CollectionsMarshal
    .GetValueRefOrAddDefault(dict, "apple", out bool exists);
refVal++;  // dict["apple"]를 직접 수정 (조회 없이)
```

### SortedDictionary\<K, V\> / SortedList\<K, V\>

| 항목        | `SortedDictionary<K,V>` | `SortedList<K,V>`      |
|-------------|-------------------------|------------------------|
| 내부 구조   | 레드-블랙 트리          | 정렬된 배열 2개        |
| 삽입/삭제   | O(log n)                | O(n) (이동 비용)       |
| 조회        | O(log n)                | O(log n)               |
| 메모리      | 더 사용                 | 더 효율적              |
| 인덱스 접근 | 불가                    | 가능 (`Keys[i]`)       |
| 권장 상황   | 삽입/삭제 빈번          | 읽기 위주, 메모리 중요 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 스레드 안전 컬렉션

### ConcurrentDictionary\<K, V\>

```csharp
var concurrent = new ConcurrentDictionary<string, int>();

// 스레드 안전 추가
concurrent.TryAdd("key1", 1);

// GetOrAdd — 없으면 추가 (팩토리 함수는 여러 번 호출될 수 있음)
int val = concurrent.GetOrAdd("key2", key => ExpensiveCompute(key));

// AddOrUpdate — 추가 또는 업데이트 (원자적)
concurrent.AddOrUpdate(
    "counter",
    addValue: 1,
    updateValueFactory: (key, old) => old + 1
);

// TryUpdate — 기존 값과 일치할 때만 업데이트 (CAS 패턴)
bool updated = concurrent.TryUpdate("key1", newValue: 2, comparisonValue: 1);
```

🟡 `ConcurrentDictionary`의 `GetOrAdd`는 팩토리 함수 호출과 딕셔너리 삽입이 원자적이지 않습니다. 팩토리가 여러 번 호출될 수 있으므로 side-effect가 없어야 합니다.

### ConcurrentQueue\<T\> / ConcurrentBag\<T\>

```csharp
// ConcurrentQueue<T> — 스레드 안전 FIFO
var cq = new ConcurrentQueue<int>();
cq.Enqueue(1);
bool ok = cq.TryDequeue(out var item);
bool peek = cq.TryPeek(out var first);

// ConcurrentBag<T> — 순서 없는 스레드 안전 컬렉션
// 각 스레드가 자신의 로컬 저장소를 사용 → 같은 스레드 반환 최적화
var bag = new ConcurrentBag<int>();
bag.Add(42);
bag.TryTake(out var taken); // 비결정적 순서

// BlockingCollection<T> — 생산자-소비자 패턴
var bc = new BlockingCollection<int>(boundedCapacity: 100);

// 생산자
Task.Run(() =>
{
    for (int i = 0; i < 10; i++)
        bc.Add(i); // 가득 차면 블로킹
    bc.CompleteAdding();
});

// 소비자
foreach (var item in bc.GetConsumingEnumerable()) // CompleteAdding 시 종료
    Console.WriteLine(item);
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 불변 컬렉션

`System.Collections.Immutable` 네임스페이스. 변경 시 새 인스턴스를 반환합니다.

```xml
<PackageReference Include="System.Collections.Immutable" Version="9.0.0" />
```

```csharp
using System.Collections.Immutable;

// ImmutableArray<T> — 불변 배열 (구조적 동등성, 가장 빠름)
var arr = ImmutableArray.Create(1, 2, 3);
var arr2 = arr.Add(4);   // 새 인스턴스 반환 (원본 불변)

// ImmutableList<T> — 불변 리스트 (AVL 트리 기반, O(log n))
var list = ImmutableList.Create(1, 2, 3);
var list2 = list.Add(4);
var list3 = list2.Remove(2);

// ImmutableDictionary<K,V>
var dict = ImmutableDictionary<string, int>.Empty
    .Add("a", 1)
    .Add("b", 2);
var dict2 = dict.SetItem("a", 99); // 키 업데이트

// ImmutableHashSet<T>
var set = ImmutableHashSet.Create(1, 2, 3);
var set2 = set.Add(4).Remove(1);

// Builder 패턴 — 여러 변경 후 한 번에 불변 인스턴스 생성 (성능 최적화)
var builder = ImmutableList.CreateBuilder<int>();
for (int i = 0; i < 1000; i++)
    builder.Add(i);
ImmutableList<int> immutable = builder.ToImmutable();
```

### 불변 컬렉션 사용 시점

| 사용 시점                              | 이유                                      |
|----------------------------------------|-------------------------------------------|
| 멀티스레드 읽기 전용 공유              | 락 불필요, 안전하게 공유                  |
| 함수형 패턴 / 상태 변경 이력 추적      | 이전 상태 보존                            |
| 설정, 화이트리스트 등 변경 없는 데이터 | 의도를 코드로 표현                        |
| Snapshot 공유                          | 변경 중 다른 스레드가 일관된 뷰 접근 가능 |

[⬆ 목차로 돌아가기](#목차)

---

## 6. 성능 비교

### 주요 연산 시간 복잡도

| 연산        | `T[]` | `List<T>` | `LinkedList<T>` | `Dictionary<K,V>` | `SortedDictionary` | `HashSet<T>` |
|-------------|-------|-----------|-----------------|-------------------|--------------------|--------------|
| 인덱스 접근 | O(1)  | O(1)      | O(n)            | O(1)              | O(log n)           | —            |
| 끝에 추가   | —     | O(1)*     | O(1)            | —                 | —                  | O(1)*        |
| 중간 삽입   | —     | O(n)      | O(1)**          | —                 | —                  | —            |
| 삭제        | —     | O(n)      | O(1)**          | O(1)*             | O(log n)           | O(1)*        |
| 키/값 조회  | —     | O(n)      | O(n)            | O(1)*             | O(log n)           | O(1)*        |
| 정렬 유지   | ❌    | ❌        | ❌              | ❌                | ✅                 | ❌           |

\* 해시 충돌 없는 평균. 최악 O(n).
\*\* 노드 참조가 있을 때.

### 실무 권장 패턴

```csharp
// 1. 크기 알 때 용량 지정
var list = new List<Order>(expectedCount);
var dict = new Dictionary<string, int>(expectedCount);

// 2. 읽기 전용 노출 — 내부는 List, 외부에는 IReadOnlyList
public IReadOnlyList<Order> Orders => _orders;
private readonly List<Order> _orders = new();

// 3. 인터페이스로 선언
IList<int> list = new List<int>();   // 구현 교체 용이
IDictionary<string, int> dict = new Dictionary<string, int>();

// 4. foreach 대신 span/array — 성능 민감한 내부 루프
Span<int> span = list.CollectionsMarshal_AsSpan(); // .NET 5+
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- .NET 컬렉션 개요: [learn.microsoft.com/dotnet/standard/collections](https://learn.microsoft.com/en-us/dotnet/standard/collections/) — ★★★☆☆
- System.Collections.Immutable: [learn.microsoft.com/dotnet/standard/collections/immutable-collections](https://learn.microsoft.com/en-us/dotnet/standard/collections/immutable-collections-guidelines) — ★★★☆☆
- ConcurrentDictionary: [learn.microsoft.com/dotnet/api/system.collections.concurrent.concurrentdictionary-2](https://learn.microsoft.com/en-us/dotnet/api/system.collections.concurrent.concurrentdictionary-2) — ★★★☆☆

---

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)

---

**작성일**: 2026-08-08

**마지막 업데이트**: 2026-08-08

© 2026 siasia86. Licensed under CC BY 4.0.

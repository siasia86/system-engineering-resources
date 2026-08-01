# C# LINQ
<!-- reference: _reference/csharp_official_notes.md -->

C# 3에서 도입된 LINQ(Language Integrated Query)와 람다, 함수형 패턴을 정리합니다.

## 목차

| 섹션                                                                                       |
|--------------------------------------------------------------------------------------------|
| [1. 람다 식](#1-람다-식) / [2. LINQ 기초](#2-linq-기초) / [3. LINQ 연산자](#3-linq-연산자) |
| [4. 지연 실행과 즉시 실행](#4-지연-실행과-즉시-실행) / [5. 함수형 패턴](#5-함수형-패턴)    |

---

## 1. 람다 식

C# 3에서 도입. 익명 함수를 간결하게 표현합니다.

```csharp
// 기본 형식
Func<int, int> square = x => x * x;
Func<int, int, int> add = (x, y) => x + y;
Action<string> print = msg => Console.WriteLine(msg);

// 블록 람다
Func<int, string> describe = n =>
{
    if (n > 0) return "양수";
    if (n < 0) return "음수";
    return "0";
};

// 파라미터 없음
Func<DateTime> now = () => DateTime.Now;
```

### delegate / Func / Action / Predicate

| 타입               | 시그니처              | 용도             |
|--------------------|-----------------------|------------------|
| `Func<T, TResult>` | 입력 T → 출력 TResult | 반환값 있는 함수 |
| `Action<T>`        | 입력 T → void         | 반환값 없는 함수 |
| `Predicate<T>`     | 입력 T → bool         | 조건 판별        |
| `Comparison<T>`    | (T, T) → int          | 정렬 비교        |

```csharp
var numbers = new List<int> { 3, 1, 4, 1, 5, 9, 2, 6 };

// Predicate<int>
numbers.RemoveAll(n => n < 3); // 3 미만 제거

// Comparison<int>
numbers.Sort((a, b) => b.CompareTo(a)); // 내림차순
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. LINQ 기초

LINQ는 두 가지 문법으로 동일하게 동작합니다.

```csharp
var numbers = new[] { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };

// 쿼리 문법 (SQL 유사)
var evens1 =
    from n in numbers
    where n % 2 == 0
    orderby n descending
    select n * n;

// 메서드 문법 (체이닝)
var evens2 = numbers
    .Where(n => n % 2 == 0)
    .OrderByDescending(n => n)
    .Select(n => n * n);

// 결과 동일: [100, 64, 36, 16, 4]
```

### LINQ 대상

| 대상           | 인터페이스         | 비고                    |
|----------------|--------------------|-------------------------|
| 컬렉션 / 배열  | `IEnumerable<T>`   | 가장 일반적             |
| 병렬 컬렉션    | `ParallelQuery<T>` | `AsParallel()` 사용     |
| 쿼리 가능 소스 | `IQueryable<T>`    | EF Core 등 DB 쿼리 변환 |

[⬆ 목차로 돌아가기](#목차)

---

## 3. LINQ 연산자

### 필터링 / 변환

```csharp
var data = new[] { 1, 2, 3, 4, 5 };

data.Where(x => x > 2);            // [3, 4, 5]
data.Select(x => x * 2);           // [2, 4, 6, 8, 10]
data.SelectMany(x => new[] {x, -x}); // [1,-1, 2,-2, ...]
data.Take(3);                       // [1, 2, 3]
data.Skip(2);                       // [3, 4, 5]
data.TakeWhile(x => x < 4);        // [1, 2, 3]
data.SkipWhile(x => x < 3);        // [3, 4, 5]
data.Distinct();                    // 중복 제거
```

### 집계

```csharp
data.Count();                       // 5
data.Sum();                         // 15
data.Average();                     // 3.0
data.Min();                         // 1
data.Max();                         // 5
data.Aggregate((acc, x) => acc + x); // 15 (Sum과 동일)
```

### 정렬

```csharp
var people = new[] {
    new { Name = "Charlie", Age = 30 },
    new { Name = "Alice",   Age = 25 },
    new { Name = "Bob",     Age = 25 },
};

people.OrderBy(p => p.Age)
      .ThenBy(p => p.Name);   // Age 오름차순, 동일 시 Name 오름차순
```

### 그룹화 / 조인

```csharp
// GroupBy
var byAge = people.GroupBy(p => p.Age);
foreach (var group in byAge)
{
    Console.WriteLine($"나이 {group.Key}: {string.Join(", ", group.Select(p => p.Name))}");
}

// Join
var orders = new[] { new { UserId = 1, Item = "책" } };
var users  = new[] { new { Id = 1, Name = "Alice" } };

var joined = users.Join(
    orders,
    u => u.Id,
    o => o.UserId,
    (u, o) => new { u.Name, o.Item }
);
```

### 단일 요소 조회

| 메서드              | 결과 없음 시 | 여러 개 시   |
|---------------------|--------------|--------------|
| `First()`           | 예외         | 첫 번째 반환 |
| `FirstOrDefault()`  | default 반환 | 첫 번째 반환 |
| `Single()`          | 예외         | 예외         |
| `SingleOrDefault()` | default 반환 | 예외         |
| `Last()`            | 예외         | 마지막 반환  |
| `ElementAt(i)`      | 예외         | i번째 반환   |

```csharp
var found = numbers.FirstOrDefault(n => n > 100); // 0 (default)
var single = numbers.Single(n => n == 5);          // 5
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 지연 실행과 즉시 실행

### 지연 실행 (Deferred Execution)

대부분의 LINQ 연산자는 열거 시점까지 실행을 미룹니다.

```csharp
var query = numbers.Where(n => n > 3); // 아직 실행 안 됨

numbers.Add(10); // 이후 변경 반영됨

foreach (var n in query) // 여기서 실행
    Console.WriteLine(n); // 4, 5, 10
```

### 즉시 실행

`ToList()`, `ToArray()`, `ToDictionary()`, 집계 메서드 등이 즉시 실행을 유발합니다.

```csharp
// 즉시 실행 — 스냅샷 생성
var snapshot = numbers.Where(n => n > 3).ToList();

numbers.Add(10); // snapshot에 반영되지 않음
```

🟡 EF Core `IQueryable`에서는 지연 실행이 DB 쿼리 최적화에 활용됩니다. `ToList()` 호출 전까지 SQL이 생성되지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 함수형 패턴

### 불변 변환 체이닝

```csharp
var result = Enumerable.Range(1, 100)
    .Where(n => n % 3 == 0 || n % 5 == 0)
    .Sum(); // FizzBuzz 합계
```

### Dictionary / Lookup 변환

```csharp
var dict = people.ToDictionary(p => p.Name, p => p.Age);
// { "Alice": 25, "Bob": 25, "Charlie": 30 }

// 중복 키 허용 (ToLookup)
var lookup = people.ToLookup(p => p.Age);
foreach (var person in lookup[25])
    Console.WriteLine(person.Name); // Alice, Bob
```

### Zip

```csharp
var names = new[] { "Alice", "Bob" };
var ages  = new[] { 25, 30 };

var combined = names.Zip(ages, (name, age) => $"{name}({age})");
// ["Alice(25)", "Bob(30)"]
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Microsoft Learn LINQ: [learn.microsoft.com/dotnet/csharp/linq](https://learn.microsoft.com/en-us/dotnet/csharp/linq/) — ★★★☆☆
- Standard Query Operators: [learn.microsoft.com/dotnet/csharp/linq/standard-query-operators](https://learn.microsoft.com/en-us/dotnet/csharp/linq/standard-query-operators/) — ★★★☆☆

---

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)

---

**작성일**: 2026-08-02

**마지막 업데이트**: 2026-08-02

© 2026 siasia86. Licensed under CC BY 4.0.

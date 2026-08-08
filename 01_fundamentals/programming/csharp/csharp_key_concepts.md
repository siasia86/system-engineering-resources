# C# 핵심 개념
<!-- reference: _reference/csharp_official_notes.md -->

C#의 타입 시스템, 값/참조 형식, record, nullable, 주요 언어 기능을 정리합니다.
"왜 이렇게 동작하는가"에 초점을 맞춥니다.

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 타입 시스템](#1-타입-시스템) / [2. 값 형식과 참조 형식](#2-값-형식과-참조-형식) / [3. record](#3-record) |
| [4. nullable](#4-nullable) / [5. 주요 언어 기능](#5-주요-언어-기능) / [6. .NET 버전 대응](#6-net-버전-대응)  |

---

## 1. 타입 시스템

C#은 정적 타입 언어입니다. 모든 변수는 컴파일 타임에 타입이 결정됩니다.

### 기본 특성

```csharp
// var: 컴파일 타임 타입 추론 (dynamic 아님)
var count = 10;       // int로 추론
var name = "Alice";   // string으로 추론

// bool은 int로 변환 불가 (C/C++과 다름)
bool flag = true;
// int x = flag;  // 컴파일 에러
```

### 타입 분류

| 분류                | 종류                                     | 할당 위치 | 복사 동작   |
|---------------------|------------------------------------------|-----------|-------------|
| 값 형식(value type) | `int`, `float`, `bool`, `struct`, `enum` | 스택      | 독립적 복사 |
| 참조 형식(ref type) | `class`, `interface`, `delegate`, 배열   | 힙        | 참조 복사   |
| `string`            | 참조 형식이지만 불변(immutable)          | 힙        | 값처럼 동작 |

```csharp
// 값 형식: 복사 시 독립
int a = 10;
int b = a;
b = 20;
Console.WriteLine(a); // 10 (영향 없음)

// 참조 형식: 참조 공유
var list1 = new List<int> { 1, 2, 3 };
var list2 = list1;
list2.Add(4);
Console.WriteLine(list1.Count); // 4 (공유됨)
```

### string 동등성

```csharp
// string은 참조 형식이지만 == 는 값 기반 비교
string s1 = "hello";
string s2 = "hello";
Console.WriteLine(s1 == s2);           // true (값 비교)
Console.WriteLine(object.ReferenceEquals(s1, s2)); // 인턴 풀 여부에 따라 다름
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 값 형식과 참조 형식

### struct vs class

| 항목           | `struct` (값 형식)            | `class` (참조 형식)          |
|----------------|-------------------------------|------------------------------|
| 메모리 위치    | 스택 (또는 인라인)            | 힙                           |
| 복사 동작      | 전체 복사                     | 참조 복사                    |
| 기본값         | 모든 필드 0/false/null        | null                         |
| 상속           | 불가 (인터페이스 구현은 가능) | 가능                         |
| null 가능 여부 | 불가 (`T?`로 nullable 가능)   | 가능                         |
| 사용 권장 상황 | 작고 불변인 데이터 (Point 등) | 동작과 상태를 함께 가진 객체 |

```csharp
struct Point
{
    public int X;
    public int Y;
}

Point p1 = new Point { X = 1, Y = 2 };
Point p2 = p1;   // 전체 복사
p2.X = 99;
Console.WriteLine(p1.X); // 1 (영향 없음)
```

### boxing / unboxing

값 형식을 `object`로 다룰 때 발생합니다.

```csharp
int n = 42;
object boxed = n;       // boxing (힙 할당)
int unboxed = (int)boxed; // unboxing (타입 캐스트 필요)
```

🟡 boxing은 힙 할당을 유발합니다. 성능에 민감한 코드에서는 제네릭 사용을 권장합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. record

C# 9에서 도입된 불변 데이터 모델링용 타입입니다.

### record class vs record struct

| 항목      | `record class`       | `record struct` |
|-----------|----------------------|-----------------|
| 도입 버전 | C# 9                 | C# 10           |
| 기반 형식 | 참조 형식            | 값 형식         |
| `==` 동작 | 값 기반 동등성       | 값 기반 동등성  |
| 불변성    | `init` setter로 보장 | 기본 mutable    |
| `with` 식 | 지원                 | 지원            |

```csharp
// record class (C# 9+)
record Person(string Name, int Age);

var p1 = new Person("Alice", 30);
var p2 = new Person("Alice", 30);
Console.WriteLine(p1 == p2); // true (값 기반 비교)

// with 식: 일부만 변경한 새 인스턴스 생성
var p3 = p1 with { Age = 31 };
Console.WriteLine(p3); // Person { Name = Alice, Age = 31 }
```

```csharp
// record struct (C# 10+)
record struct Point(double X, double Y);
```

### init-only setter (C# 9)

```csharp
class Config
{
    public string Host { get; init; } = "localhost";
    public int Port { get; init; } = 8080;
}

var cfg = new Config { Host = "server1" }; // 초기화 시만 설정 가능
// cfg.Port = 9090; // 컴파일 에러
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. nullable

### nullable 값 형식 (C# 2+)

`Nullable<T>` 또는 `T?` 문법으로 값 형식에 null을 허용합니다.

```csharp
int? age = null;
Console.WriteLine(age.HasValue);   // false
Console.WriteLine(age ?? -1);      // -1 (null이면 -1)

age = 25;
Console.WriteLine(age.Value);      // 25
```

### nullable 참조 형식, NRT (C# 8+)

컴파일러가 null 역참조를 정적 분석으로 경고합니다. `.csproj`에서 활성화합니다.

```xml
<Nullable>enable</Nullable>
```

```csharp
string name = "Alice";    // non-nullable: null 할당 시 경고
string? title = null;     // nullable: null 허용

// null-forgiving operator: 개발자가 null 아님을 보증
string forced = title!;   // 경고 억제 (신중히 사용)
```

### null 연산자 모음

| 연산자 | 의미                                          | 도입 버전 |
|--------|-----------------------------------------------|-----------|
| `?.`   | null이면 null 반환, 아니면 멤버 접근          | C# 6      |
| `??`   | null이면 우변 값 반환                         | C# 2      |
| `??=`  | null이면 우변 값 할당                         | C# 8      |
| `!`    | null-forgiving — 경고 억제 (런타임 보장 아님) | C# 8      |

```csharp
string? s = null;
Console.WriteLine(s?.Length);       // null
Console.WriteLine(s?.Length ?? 0);  // 0
s ??= "default";
Console.WriteLine(s);               // "default"
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 주요 언어 기능

### pattern matching (C# 7~14)

```csharp
// is 패턴 (C# 7+)
object obj = "hello";
if (obj is string s)
    Console.WriteLine(s.ToUpper()); // HELLO

// switch 식 패턴 (C# 8+)
string Describe(object o) => o switch
{
    int n when n > 0  => "양수",
    int n when n < 0  => "음수",
    int                => "0",
    string str         => $"문자열: {str}",
    null               => "null",
    _                  => "기타"
};
```

### 컬렉션 식 (C# 12)

```csharp
int[] arr = [1, 2, 3];
List<int> list = [4, 5, 6];

// spread 연산자
int[] combined = [..arr, ..list]; // [1, 2, 3, 4, 5, 6]
```

### primary constructor (C# 12)

```csharp
// 기존
class Service
{
    private readonly ILogger _logger;
    public Service(ILogger logger) => _logger = logger;
}

// primary constructor
class Service(ILogger logger)
{
    public void Log(string msg) => logger.LogInformation(msg);
}
```

### required 멤버 (C# 11)

```csharp
class User
{
    public required string Name { get; init; }
    public required string Email { get; init; }
}

// var u = new User(); // 컴파일 에러 — Name, Email 미설정
var u = new User { Name = "Alice", Email = "a@example.com" };
```

### global using (C# 10)

```csharp
// GlobalUsings.cs (프로젝트 전역 적용)
global using System;
global using System.Collections.Generic;
global using System.Linq;
```

### field 키워드 (C# 14)

auto-property의 backing field에 접근하는 컨텍스트 키워드입니다.
getter/setter 한쪽에만 로직을 추가할 때 별도 필드 선언이 불필요합니다.

```csharp
public class Config
{
    // C# 14 이전 — backing field 직접 선언
    private string _host = "localhost";
    public string Host
    {
        get => _host;
        set => _host = value?.Trim() ?? throw new ArgumentNullException(nameof(value));
    }

    // C# 14 — field 키워드로 backing field 접근 (backing field 선언 불필요)
    public string Host2
    {
        get;
        set => field = value?.Trim() ?? throw new ArgumentNullException(nameof(value));
    }

    // 유효성 검사 + 알림 패턴
    public int Port
    {
        get => field;
        set
        {
            if (value is < 1 or > 65535)
                throw new ArgumentOutOfRangeException(nameof(value));
            field = value;
        }
    } = 8080; // 초기값 설정
}
```

🟡 `field`는 C# 13에서 preview였다가 C# 14에서 정식 도입되었습니다. `.NET 10 / C# 14` 프로젝트에서 사용 가능합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. .NET 버전 대응

| .NET 버전 | 릴리스 유형 | EOL        | 기본 C# 버전 |
|-----------|-------------|------------|--------------|
| .NET 10   | LTS         | 2028-11-14 | C# 14        |
| .NET 9    | STS         | 2026-11-10 | C# 13        |
| .NET 8    | LTS         | 2026-11-10 | C# 12        |
| .NET 7    | STS         | 2024-05-14 | C# 11        |
| .NET 6    | LTS         | 2024-11-12 | C# 10        |

🟡 .NET 8/9는 2026-11-10 EOL 예정.

---

## 참고 자료

- Microsoft Learn: [learn.microsoft.com/dotnet/csharp](https://learn.microsoft.com/en-us/dotnet/csharp/) — ★★★☆☆
- C# Language Reference: [learn.microsoft.com/dotnet/csharp/language-reference](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/) — ★★★☆☆
- dotnet/csharplang Language-Version-History: [github.com/dotnet/csharplang](https://github.com/dotnet/csharplang/blob/main/Language-Version-History.md) — ★★★☆☆

---

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)

---

**작성일**: 2026-08-02

**마지막 업데이트**: 2026-08-02

© 2026 siasia86. Licensed under CC BY 4.0.

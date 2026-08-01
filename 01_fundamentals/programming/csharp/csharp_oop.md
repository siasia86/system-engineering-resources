# C# OOP — 객체지향 프로그래밍
<!-- reference: _reference/csharp_official_notes.md -->

C#의 클래스, 상속, 인터페이스, 추상 클래스, 다형성을 정리합니다.

## 목차

| 섹션                                                                                   |
|----------------------------------------------------------------------------------------|
| [1. 클래스 기초](#1-클래스-기초) / [2. 상속](#2-상속) / [3. 인터페이스](#3-인터페이스) |
| [4. 추상 클래스](#4-추상-클래스) / [5. 다형성](#5-다형성) / [6. 제네릭](#6-제네릭)     |

---

## 1. 클래스 기초

### 클래스 구성 요소

```csharp
public class Person
{
    // 필드
    private string _name;

    // 프로퍼티 (C# 권장 방식)
    public string Name
    {
        get => _name;
        set => _name = value ?? throw new ArgumentNullException(nameof(value));
    }

    // auto-implemented property
    public int Age { get; set; }

    // init-only property (C# 9+)
    public string Id { get; init; } = Guid.NewGuid().ToString();

    // 생성자
    public Person(string name, int age)
    {
        Name = name;
        Age = age;
    }

    // 메서드
    public string Greet() => $"안녕하세요, {Name}입니다.";

    // 정적 멤버
    public static int Count { get; private set; }
}
```

### 접근 제한자

| 접근 제한자          | 접근 범위                        |
|----------------------|----------------------------------|
| `public`             | 어디서나                         |
| `private`            | 클래스 내부만                    |
| `protected`          | 클래스 + 파생 클래스             |
| `internal`           | 같은 어셈블리 내                 |
| `protected internal` | 같은 어셈블리 또는 파생 클래스   |
| `private protected`  | 같은 어셈블리 내의 파생 클래스만 |

### primary constructor (C# 12)

```csharp
// 생성자 파라미터가 클래스 스코프 전체에서 사용 가능
class OrderService(IRepository repo, ILogger<OrderService> logger)
{
    public async Task PlaceOrder(Order order)
    {
        logger.LogInformation("주문 처리: {Id}", order.Id);
        await repo.SaveAsync(order);
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 상속

C#은 단일 클래스 상속만 지원합니다. 인터페이스는 다중 구현 가능합니다.

```csharp
public class Animal
{
    public string Name { get; }

    public Animal(string name) => Name = name;

    // virtual: 파생 클래스에서 재정의 가능
    public virtual string Speak() => "...";

    // sealed: 더 이상 재정의 불가
    public sealed string Describe() => $"{GetType().Name}: {Name}";
}

public class Dog : Animal
{
    public Dog(string name) : base(name) { }

    // override: 부모 메서드 재정의
    public override string Speak() => "멍멍";
}

public class GuideDog : Dog
{
    public GuideDog(string name) : base(name) { }

    public override string Speak() => base.Speak() + " (안내견)";
}
```

### 상속 관련 키워드

| 키워드     | 역할                                         |
|------------|----------------------------------------------|
| `virtual`  | 파생 클래스에서 재정의 허용                  |
| `override` | 부모의 virtual/abstract 메서드 재정의        |
| `sealed`   | 클래스/메서드의 추가 상속/재정의 금지        |
| `base`     | 부모 클래스 멤버 또는 생성자 호출            |
| `new`      | 부모 멤버를 숨기고 새로 정의 (권장하지 않음) |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 인터페이스

C# 8부터 기본 구현(default interface members)을 가질 수 있습니다.

```csharp
public interface IShape
{
    // 구현 강제
    double Area();
    double Perimeter();

    // default 구현 (C# 8+) — 구현 클래스에서 재정의 가능
    string Describe() => $"넓이: {Area():F2}, 둘레: {Perimeter():F2}";
}

public interface ISerializable
{
    string Serialize();
}

// 다중 인터페이스 구현
public class Circle : IShape, ISerializable
{
    public double Radius { get; }
    public Circle(double radius) => Radius = radius;

    public double Area() => Math.PI * Radius * Radius;
    public double Perimeter() => 2 * Math.PI * Radius;
    public string Serialize() => $"{{\"radius\":{Radius}}}";
}
```

### 인터페이스 vs 추상 클래스 선택 기준

| 기준            | 인터페이스             | 추상 클래스      |
|-----------------|------------------------|------------------|
| 다중 구현       | 가능                   | 불가 (단일 상속) |
| 상태(필드) 보유 | 불가                   | 가능             |
| 생성자          | 없음                   | 있음             |
| 관계 표현       | "~할 수 있다 (can-do)" | "~이다 (is-a)"   |
| 기본 구현       | C# 8+부터 가능         | 항상 가능        |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 추상 클래스

```csharp
public abstract class Repository<T>
{
    // 구현 강제 — 파생 클래스 필수 구현
    public abstract Task<T?> FindByIdAsync(int id);
    public abstract Task SaveAsync(T entity);

    // 공통 구현 제공
    public async Task<List<T>> FindAllAsync()
    {
        // 공통 로직
        return new List<T>();
    }
}

public class UserRepository : Repository<User>
{
    public override async Task<User?> FindByIdAsync(int id)
    {
        // DB 조회 구현
        return await Task.FromResult<User?>(null);
    }

    public override async Task SaveAsync(User entity)
    {
        await Task.CompletedTask;
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 다형성

```csharp
List<IShape> shapes = new()
{
    new Circle(5),
    new Rectangle(4, 6),
};

foreach (var shape in shapes)
{
    // 런타임에 실제 타입에 따라 Area() 호출
    Console.WriteLine($"{shape.GetType().Name}: {shape.Area():F2}");
}

// 타입 패턴 매칭 (C# 7+)
foreach (var shape in shapes)
{
    string info = shape switch
    {
        Circle c   => $"원, 반지름={c.Radius}",
        Rectangle r => $"사각형, {r.Width}x{r.Height}",
        _          => "알 수 없는 도형"
    };
    Console.WriteLine(info);
}
```

### as / is 연산자

```csharp
object obj = new Circle(3);

// is: 타입 확인 + 변수 선언 (C# 7+)
if (obj is Circle circle)
    Console.WriteLine($"원: {circle.Radius}");

// as: 실패 시 null 반환 (참조 형식/nullable 전용)
var rect = obj as Rectangle; // null
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 제네릭

```csharp
// 제네릭 클래스
public class Stack<T>
{
    private readonly List<T> _items = new();

    public void Push(T item) => _items.Add(item);
    public T Pop()
    {
        var item = _items[^1]; // C# 8+ index from end
        _items.RemoveAt(_items.Count - 1);
        return item;
    }
    public int Count => _items.Count;
}

// 제네릭 제약
public T Max<T>(T a, T b) where T : IComparable<T>
    => a.CompareTo(b) >= 0 ? a : b;
```

### 주요 제약 조건

| 제약                | 의미                         |
|---------------------|------------------------------|
| `where T : class`   | 참조 형식만                  |
| `where T : struct`  | 값 형식만 (nullable 아님)    |
| `where T : new()`   | 기본 생성자 필요             |
| `where T : Base`    | Base 또는 파생 클래스만      |
| `where T : IFoo`    | IFoo 인터페이스 구현 필요    |
| `where T : notnull` | nullable이 아닌 타입 (C# 8+) |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Microsoft Learn OOP: [learn.microsoft.com/dotnet/csharp/fundamentals/object-oriented](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/object-oriented/) — ★★★☆☆
- C# Language Reference: [learn.microsoft.com/dotnet/csharp/language-reference](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/) — ★★★☆☆

---

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)

---

**작성일**: 2026-08-02

**마지막 업데이트**: 2026-08-02

© 2026 siasia86. Licensed under CC BY 4.0.

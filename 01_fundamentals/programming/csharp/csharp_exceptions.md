# C# 예외 처리
<!-- reference: _reference/csharp_official_notes.md -->

C#의 예외 처리 — try/catch/finally, 예외 계층, 커스텀 예외, 전파 패턴을 정리합니다.

## 목차

| 섹션                                                                                                       |
|------------------------------------------------------------------------------------------------------------|
| [1. 기본 구조](#1-기본-구조) / [2. 예외 계층](#2-예외-계층) / [3. 커스텀 예외](#3-커스텀-예외)             |
| [4. 예외 전파와 래핑](#4-예외-전파와-래핑) / [5. 비동기 예외](#5-비동기-예외) / [6. 안티패턴](#6-안티패턴) |

---

## 1. 기본 구조

### try / catch / finally / when

```csharp
try
{
    var result = int.Parse(input);  // FormatException 가능
    var data = await FetchAsync();  // HttpRequestException 가능
}
catch (FormatException ex)
{
    // 구체적인 예외 먼저 — 순서 중요
    Console.WriteLine($"형식 오류: {ex.Message}");
}
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.NotFound)
{
    // when 필터: 조건이 true일 때만 catch (C# 6+)
    Console.WriteLine("리소스 없음");
}
catch (Exception ex)
{
    // 최후 포괄 catch — 구체적 catch 뒤에 배치
    Console.WriteLine($"예외: {ex}");
    throw; // 원본 스택 트레이스 유지하며 재던지기
}
finally
{
    // 예외 여부와 관계없이 항상 실행
    // 리소스 정리, 로그 등
}
```

### throw vs throw ex

```csharp
catch (Exception ex)
{
    // ❌ throw ex — 스택 트레이스 초기화됨 (발생 위치 정보 손실)
    throw ex;

    // ✅ throw — 원본 스택 트레이스 유지
    throw;

    // ✅ throw new WrapException("메시지", ex) — 내부 예외 유지
    throw new InvalidOperationException("처리 실패", ex);
}
```

### when 필터 활용

```csharp
// when은 catch 블록 진입 전 조건 확인 — 스택 언와인딩 전에 평가됨
catch (SqlException ex) when (ex.Number == 1205) // 교착 상태
{
    await Task.Delay(100);
    // 재시도 로직
}
catch (SqlException ex) when (ex.Number == 547)  // FK 위반
{
    throw new ValidationException("참조 무결성 위반", ex);
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 예외 계층

### .NET 주요 예외 계층

```
Exception
├── SystemException
│   ├── ArgumentException
│   │   ├── ArgumentNullException        — null 인수
│   │   └── ArgumentOutOfRangeException  — 범위 벗어난 인수
│   ├── InvalidOperationException        — 현재 상태에서 불가한 연산
│   ├── NotSupportedException            — 구현하지 않은 기능
│   ├── NotImplementedException          — 미구현 (개발 중 임시)
│   ├── NullReferenceException           — null 역참조 (런타임)
│   ├── IndexOutOfRangeException         — 배열 범위 초과
│   ├── OverflowException                — 산술 오버플로우
│   ├── FormatException                  — 형식 변환 오류
│   ├── IOException
│   │   ├── FileNotFoundException
│   │   └── DirectoryNotFoundException
│   ├── TimeoutException
│   └── OperationCanceledException       — 취소 요청 처리됨
│       └── TaskCanceledException        — Task 취소
├── ApplicationException                 — (사용 비권장, Exception 직접 상속 권장)
└── AggregateException                   — 여러 예외 묶음 (Task.WhenAll 등)
```

### 자주 쓰는 예외 생성 패턴

```csharp
// 인수 검증 (C# 11+: ArgumentException.ThrowIfNull)
ArgumentNullException.ThrowIfNull(name);
ArgumentException.ThrowIfNullOrEmpty(name);
ArgumentOutOfRangeException.ThrowIfNegative(count);

// C# 10 이하 방식
if (name is null)
    throw new ArgumentNullException(nameof(name));

if (count < 0)
    throw new ArgumentOutOfRangeException(nameof(count), "0 이상이어야 합니다.");

// 상태 검증
if (!_initialized)
    throw new InvalidOperationException("초기화가 필요합니다.");
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 커스텀 예외

### 기본 패턴

```csharp
// Exception 직접 상속 (ApplicationException 상속 비권장)
public class OrderNotFoundException : Exception
{
    public int OrderId { get; }

    public OrderNotFoundException(int orderId)
        : base($"주문 {orderId}을 찾을 수 없습니다.")
    {
        OrderId = orderId;
    }

    public OrderNotFoundException(int orderId, Exception inner)
        : base($"주문 {orderId}을 찾을 수 없습니다.", inner)
    {
        OrderId = orderId;
    }
}
```

```csharp
// 사용
try
{
    var order = await _repo.FindAsync(orderId)
        ?? throw new OrderNotFoundException(orderId);
}
catch (OrderNotFoundException ex)
{
    _logger.LogWarning("주문 없음: {OrderId}", ex.OrderId);
}
```

### 도메인별 예외 계층

```csharp
// 도메인 기반 예외 기반 클래스
public abstract class DomainException : Exception
{
    protected DomainException(string message) : base(message) { }
    protected DomainException(string message, Exception inner) : base(message, inner) { }
}

public class InsufficientStockException : DomainException
{
    public string ProductId { get; }
    public int Requested { get; }
    public int Available { get; }

    public InsufficientStockException(string productId, int requested, int available)
        : base($"재고 부족 — 상품: {productId}, 요청: {requested}, 가용: {available}")
    {
        ProductId = productId;
        Requested = requested;
        Available = available;
    }
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 예외 전파와 래핑

### ExceptionDispatchInfo — 스택 트레이스 보존 재던지기

```csharp
using System.Runtime.ExceptionServices;

ExceptionDispatchInfo? captured = null;

try
{
    await RiskyOperationAsync();
}
catch (Exception ex)
{
    captured = ExceptionDispatchInfo.Capture(ex);
}

// 나중에 다른 컨텍스트에서 원본 스택 트레이스 보존하며 재던지기
captured?.Throw(); // throw; 와 동일한 효과, 다른 위치에서 호출 가능
```

### 예외 래핑 패턴

```csharp
// 하위 계층 예외를 상위 계층 예외로 변환
public async Task<Order> GetOrderAsync(int id)
{
    try
    {
        return await _db.Orders.FindAsync(id)
            ?? throw new OrderNotFoundException(id);
    }
    catch (SqlException ex)
    {
        // 인프라 예외 → 도메인 예외 변환 (InnerException 유지)
        throw new RepositoryException($"주문 조회 실패: {id}", ex);
    }
}
```

### AggregateException (Task.WhenAll)

```csharp
try
{
    await Task.WhenAll(task1, task2, task3);
}
catch (AggregateException aggEx)
{
    // 여러 Task 동시 실패 시 AggregateException
    foreach (var inner in aggEx.InnerExceptions)
        Console.WriteLine(inner.Message);
}
```

🟡 `await Task.WhenAll()` 은 첫 번째 예외만 unwrap하여 던집니다. 모든 예외를 얻으려면 각 Task의 `.Exception` 프로퍼티를 확인하거나 `AggregateException`을 직접 처리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 비동기 예외

### async Task 예외 전파

```csharp
// async Task — await 하는 쪽으로 예외 전파
public async Task<string> FetchAsync()
{
    await Task.Delay(100);
    throw new HttpRequestException("연결 실패"); // await 하는 쪽에서 catch 가능
}

try
{
    var result = await FetchAsync();
}
catch (HttpRequestException ex)
{
    Console.WriteLine(ex.Message); // "연결 실패"
}
```

### Fire-and-forget 예외 처리

```csharp
// ❌ async void: 예외를 잡을 방법 없음
async void FireAndForget()
{
    await Task.Delay(100);
    throw new Exception("사라짐");
}

// ✅ Task.Run + 내부 try/catch
_ = Task.Run(async () =>
{
    try
    {
        await DoWorkAsync();
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "백그라운드 작업 실패");
    }
});
```

### OperationCanceledException

```csharp
// 취소는 예외지만 오류가 아님 — 별도 처리
try
{
    await LongOperationAsync(cancellationToken);
}
catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
{
    // 정상적인 취소 — 오류 로그 불필요
    _logger.LogInformation("작업 취소됨");
}
catch (Exception ex)
{
    // 실제 오류
    _logger.LogError(ex, "작업 실패");
    throw;
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 안티패턴

### catch-and-swallow

```csharp
// ❌ 예외 무시 — 문제 파악 불가
try
{
    await ProcessAsync();
}
catch (Exception)
{
    // 아무것도 하지 않음
}

// ✅ 최소한 로그
catch (Exception ex)
{
    _logger.LogError(ex, "ProcessAsync 실패");
    // 상황에 따라 re-throw 또는 fallback
}
```

### 포괄 catch 남용

```csharp
// ❌ 모든 예외를 동일하게 처리
catch (Exception ex)
{
    return Result.Failure(ex.Message);
}

// ✅ 예외 유형에 따른 분기
catch (ValidationException ex)
{
    return Result.Failure(ex.Message);   // 사용자 입력 오류
}
catch (NotFoundException ex)
{
    return Result.NotFound(ex.Message);  // 리소스 없음
}
catch (Exception ex)
{
    _logger.LogError(ex, "예상치 못한 오류");
    throw; // 복구 불가 — 상위로 전파
}
```

### 안티패턴 요약

| 안티패턴                       | 문제                           | 대안                              |
|--------------------------------|--------------------------------|-----------------------------------|
| `catch (Exception) { }`        | 예외 무시, 문제 추적 불가      | 로그 후 re-throw 또는 fallback    |
| `throw ex`                     | 스택 트레이스 초기화           | `throw` 또는 `throw new Wrap(ex)` |
| `ex.Message`만 로그            | 스택 트레이스, 내부 예외 손실  | `_logger.LogError(ex, "...")`     |
| `NullReferenceException` catch | null 역참조는 버그, catch 금지 | NRT + null 검사로 예방            |
| InnerException 없이 재던지기   | 원인 컨텍스트 손실             | `throw new Wrap("msg", ex)`       |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Microsoft Learn 예외 처리: [learn.microsoft.com/dotnet/csharp/fundamentals/exceptions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/exceptions/) — ★★★☆☆
- Exception handling best practices: [learn.microsoft.com/dotnet/standard/exceptions/best-practices-for-exceptions](https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions) — ★★★☆☆

---

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)

---

**작성일**: 2026-08-08

**마지막 업데이트**: 2026-08-08

© 2026 siasia86. Licensed under CC BY 4.0.

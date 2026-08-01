# C# async / await
<!-- reference: _reference/csharp_official_notes.md -->

C#의 비동기 프로그래밍 모델 — Task, ValueTask, async/await 패턴, 취소 토큰을 정리합니다.

## 목차

| 섹션                                                                                                                      |
|---------------------------------------------------------------------------------------------------------------------------|
| [1. async/await 기초](#1-asyncawait-기초) / [2. Task와 ValueTask](#2-task와-valuetask) / [3. 비동기 패턴](#3-비동기-패턴) |
| [4. 취소 토큰](#4-취소-토큰) / [5. 주의사항](#5-주의사항)                                                                 |

---

## 1. async/await 기초

C# 5에서 도입된 비동기 모델입니다. 스레드를 블로킹하지 않고 I/O 대기를 처리합니다.

```csharp
// async 메서드 기본 구조
public async Task<string> FetchDataAsync(string url)
{
    using var client = new HttpClient();
    string result = await client.GetStringAsync(url); // 대기 중 스레드 반환
    return result;
}
```

### async 반환 타입

| 반환 타입      | 용도                                 |
|----------------|--------------------------------------|
| `Task`         | 반환값 없는 비동기 메서드            |
| `Task<T>`      | 반환값 있는 비동기 메서드            |
| `void`         | 이벤트 핸들러 전용 (await 불가)      |
| `ValueTask<T>` | 동기 완료가 잦은 경우 힙 할당 절감용 |

```csharp
// Task (반환값 없음)
public async Task LogAsync(string message)
{
    await File.AppendAllTextAsync("log.txt", message);
}

// Task<T> (반환값 있음)
public async Task<int> GetCountAsync()
{
    await Task.Delay(100);
    return 42;
}

// async void — 이벤트 핸들러만 사용 (예외 catch 불가)
private async void Button_Click(object sender, EventArgs e)
{
    await LoadDataAsync();
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. Task와 ValueTask

### Task 생성 방법

```csharp
// await 권장
var result = await SomeAsync();

// Task.FromResult: 이미 완료된 결과를 Task로 래핑
Task<int> t = Task.FromResult(42);

// Task.CompletedTask: 반환값 없는 완료 Task
await Task.CompletedTask;

// Task.WhenAll: 여러 Task 병렬 대기
var (r1, r2) = await (Task1Async(), Task2Async()); // C# 10 분해 (tuple)
await Task.WhenAll(task1, task2, task3);

// Task.WhenAny: 가장 먼저 완료되는 Task 대기
var first = await Task.WhenAny(task1, task2);
```

### ValueTask 사용 시점

```csharp
// 캐시에서 반환될 때 동기 완료가 잦은 경우
public ValueTask<string> GetFromCacheAsync(string key)
{
    if (_cache.TryGetValue(key, out var cached))
        return new ValueTask<string>(cached); // 힙 할당 없음

    return new ValueTask<string>(FetchFromDbAsync(key));
}
```

🟡 `ValueTask`는 단순 await 외 반복 await, 여러 번 await 금지입니다. 일반적으로 `Task`를 기본으로 사용하고 성능 측정 후 교체합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 비동기 패턴

### 병렬 실행

```csharp
// 순차 실행 (느림)
var user = await GetUserAsync(id);
var orders = await GetOrdersAsync(id);

// 병렬 실행 (빠름)
var userTask = GetUserAsync(id);
var ordersTask = GetOrdersAsync(id);
await Task.WhenAll(userTask, ordersTask);
var user = userTask.Result;
var orders = ordersTask.Result;
```

### ConfigureAwait

```csharp
// 라이브러리 코드: UI/ASP.NET 컨텍스트 캡처 불필요 시 사용
public async Task<string> LibraryMethodAsync()
{
    var data = await FetchAsync().ConfigureAwait(false);
    return Process(data);
}
```

🟡 ASP.NET Core와 .NET 5+ 콘솔/서버 앱은 동기화 컨텍스트가 없어 `ConfigureAwait(false)` 효과가 없습니다. 라이브러리 코드에서의 사용이 주된 목적입니다.

### async 스트림 (C# 8+)

```csharp
// IAsyncEnumerable<T> 생성
public async IAsyncEnumerable<int> GenerateAsync()
{
    for (int i = 0; i < 10; i++)
    {
        await Task.Delay(100);
        yield return i;
    }
}

// await foreach로 소비
await foreach (var item in GenerateAsync())
{
    Console.WriteLine(item);
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 취소 토큰

```csharp
// CancellationToken 전달 패턴
public async Task ProcessAsync(CancellationToken cancellationToken = default)
{
    while (true)
    {
        cancellationToken.ThrowIfCancellationRequested();
        await DoWorkAsync(cancellationToken);
    }
}

// 사용 측
using var cts = new CancellationTokenSource();
cts.CancelAfter(TimeSpan.FromSeconds(30)); // 30초 타임아웃

try
{
    await ProcessAsync(cts.Token);
}
catch (OperationCanceledException)
{
    Console.WriteLine("취소됨");
}
```

### Timeout 패턴

```csharp
using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));

try
{
    var result = await FetchAsync(cts.Token);
}
catch (OperationCanceledException) when (cts.IsCancellationRequested)
{
    // 타임아웃
}
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 주의사항

### 동기 블로킹 금지

```csharp
// ❌ 데드락 위험 (ASP.NET 등 동기화 컨텍스트 있는 환경)
var result = SomeAsync().Result;
var result2 = SomeAsync().GetAwaiter().GetResult();
Task.Run(() => SomeAsync()).Wait();

// ✅ await 사용
var result = await SomeAsync();
```

### async void 예외 처리 불가

```csharp
// ❌ 예외가 호출자에게 전파되지 않음
async void BadMethod()
{
    await Task.Delay(100);
    throw new Exception("이 예외는 잡히지 않음");
}

// ✅ async Task 반환 후 await
async Task GoodMethod()
{
    await Task.Delay(100);
    throw new Exception("await 하는 쪽에서 잡힘");
}
```

### 안티패턴 요약

| 안티패턴                    | 문제                       | 대안                    |
|-----------------------------|----------------------------|-------------------------|
| `.Result` / `.Wait()`       | 데드락, 스레드 블로킹      | `await` 사용            |
| `async void`                | 예외 전파 불가             | `async Task` 반환       |
| `Task.Run` 남용             | 불필요한 스레드 풀 사용    | 순수 I/O는 async 메서드 |
| `await` 없는 `async` 메서드 | 컴파일러 경고, 동기 실행됨 | `await` 추가 또는 제거  |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Microsoft Learn async/await: [learn.microsoft.com/dotnet/csharp/asynchronous-programming](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/) — ★★★☆☆
- async return types: [learn.microsoft.com/dotnet/csharp/asynchronous-programming/async-return-types](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-return-types) — ★★★☆☆

---

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)

---

**작성일**: 2026-08-02

**마지막 업데이트**: 2026-08-02

© 2026 siasia86. Licensed under CC BY 4.0.

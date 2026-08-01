# C# 프로그래밍

C# 핵심 개념부터 .NET 생태계까지 다루는 학습 자료입니다.
기준 버전: **.NET 10 LTS / C# 14**

## 목차

| 섹션                                                                                                  |
|-------------------------------------------------------------------------------------------------------|
| [문서 목록](#문서-목록) / [학습 순서](#학습-순서) / [빠른 참조](#빠른-참조) / [주요 개념](#주요-개념) |

---

## 문서 목록

### 핵심 개념
- **[C# 핵심 개념](csharp_key_concepts.md)** — 타입 시스템, 값/참조 형식, record, nullable, 언어 버전

### 객체지향 프로그래밍
- **[OOP](csharp_oop.md)** — 클래스, 상속, 인터페이스, 추상 클래스, 다형성

### 비동기 프로그래밍
- **[async / await](csharp_async.md)** — Task, ValueTask, async 패턴, 취소 토큰

### 함수형 / 쿼리
- **[LINQ](csharp_linq.md)** — LINQ, 람다, 함수형 패턴, 컬렉션 연산

### 빌드 / 생태계
- **[dotnet CLI](csharp_dotnet_cli.md)** — dotnet 명령어, .csproj, NuGet, 빌드/테스트

---

## 학습 순서

```
1. csharp_key_concepts.md   — 타입 시스템, 값/참조 형식, record, nullable 이해
2. csharp_oop.md            — 클래스, 상속, 인터페이스 패턴 이해
3. csharp_linq.md           — 람다, LINQ 쿼리 패턴 이해
4. csharp_async.md          — 비동기 모델, Task, 취소 패턴
5. csharp_dotnet_cli.md     — 프로젝트 생성, 빌드, 배포, 패키지 관리
```

---

## 빠른 참조

| 목적           | 명령어 / 기법                             |
|----------------|-------------------------------------------|
| 프로젝트 생성  | `dotnet new console -n MyApp`             |
| 빌드           | `dotnet build`                            |
| 실행           | `dotnet run`                              |
| 테스트         | `dotnet test`                             |
| 패키지 추가    | `dotnet add package <패키지명>`           |
| null 안전 체크 | `obj?.Property ?? "default"`              |
| 비동기 메서드  | `async Task<T> MethodAsync()`             |
| LINQ 기본 쿼리 | `list.Where(x => x > 0).Select(x => x*2)` |
| 패턴 매칭      | `x switch { int n => n, _ => 0 }`         |

---

## 주요 개념

| 개념             | 한 줄 설명                                            |
|------------------|-------------------------------------------------------|
| 값 형식          | struct/enum — 스택 할당, 복사 시 독립적               |
| 참조 형식        | class/interface/배열 — 힙 할당, 참조 복사             |
| record           | C# 9+, 불변 데이터 모델링, 값 기반 동등성             |
| nullable         | `T?` — 값 형식은 C# 2+, 참조 형식은 C# 8+ (NRT)       |
| async/await      | C# 5+, Task 기반 비동기 모델, 스레드 블로킹 없이 대기 |
| LINQ             | C# 3+, 컬렉션/DB/XML을 동일 문법으로 쿼리             |
| pattern matching | C# 7+~14 지속 확장, is/switch 식 패턴                 |

---

**작성일**: 2026-08-02

**마지막 업데이트**: 2026-08-02

© 2026 siasia86. Licensed under CC BY 4.0.

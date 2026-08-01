---
name: csharp-official-notes
description: C# 공식 문서 기반 핵심 사실, 버전 대응표, deprecated, 주요 언어 기능 정리. C# 문서 작성/검토 시 참조.
tags:
  - csharp
  - dotnet
  - programming
  - microsoft
last_checked: 2026-08-02
sources:
  - https://learn.microsoft.com/en-us/dotnet/csharp/
  - https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/
  - https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/
  - https://dotnetcli.blob.core.windows.net/dotnet/release-metadata/releases-index.json
---

# C# / .NET 공식 참조 노트

## 1. 버전 현황 (확인일: 2026-08-02)

### 공식 소스

| 소스                       | URL                                                                                           | 용도                |
|----------------------------|-----------------------------------------------------------------------------------------------|---------------------|
| .NET releases-index        | https://dotnetcli.blob.core.windows.net/dotnet/release-metadata/releases-index.json           | 버전/LTS/EOL 현황   |
| C# what's new              | https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/                                    | 언어 버전 변경 이력 |
| configure-language-version | https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/configure-language-version | 버전 대응표         |

### 검증된 사실 (2026-08-02)

| .NET 버전 | 릴리스 유형 | 지원 상태   | EOL 날짜   | 기본 C# 버전 | 출처           |
|-----------|-------------|-------------|------------|--------------|----------------|
| .NET 11   | preview     | preview     | -          | C# 15(예정)  | releases-index |
| .NET 10   | LTS         | active      | 2028-11-14 | C# 14        | releases-index |
| .NET 9    | STS         | maintenance | 2026-11-10 | C# 13        | releases-index |
| .NET 8    | LTS         | maintenance | 2026-11-10 | C# 12        | releases-index |
| .NET 7    | STS         | EOL         | 2024-05-14 | C# 11        | releases-index |
| .NET 6    | LTS         | EOL         | 2024-11-12 | C# 10        | releases-index |

🟡 .NET 8/9는 2026-11-10 EOL 예정.

### C# 언어 버전 ↔ .NET SDK 기본 매핑

| C# 버전 | 기본 .NET SDK | 출처                |
|---------|---------------|---------------------|
| C# 14   | .NET 10       | whats-new/csharp-14 |
| C# 13   | .NET 9        | whats-new/csharp-13 |
| C# 12   | .NET 8        | language-reference  |
| C# 11   | .NET 7        | language-reference  |
| C# 10   | .NET 6        | language-reference  |
| C# 9    | .NET 5        | language-reference  |
| C# 8    | .NET Core 3.x | language-reference  |

## 2. 타입 시스템 (공식 문서 기반)

### 공식 소스

| 소스            | URL                                                                 | 용도      |
|-----------------|---------------------------------------------------------------------|-----------|
| C# types 개요   | https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/ | 타입 분류 |
| C# language ref | https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/ | 타입 상세 |

### 검증된 사실 (2026-08-02)

| 항목                | 값                                                                 | 출처         |
|---------------------|--------------------------------------------------------------------|--------------|
| bool → int 변환     | C#에서 bool은 int로 변환 불가 (C/C++과 다름)                       | csharp/types |
| 값 형식(value type) | struct, enum, 기본 타입(int/float/bool 등)                         | language-ref |
| 참조 형식(ref type) | class, interface, delegate, record class, 배열                     | language-ref |
| record              | C# 9+: 불변 데이터 모델링용, `==`는 값 기반 비교                   | language-ref |
| nullable 값 형식    | `int?` = `Nullable<int>` (C# 2+)                                   | language-ref |
| nullable ref 형식   | `string?` — C# 8+, NRT 활성화 필요 (`<Nullable>enable</Nullable>`) | language-ref |
| string              | 참조 형식이지만 불변(immutable), `==`는 값 기반 비교               | language-ref |
| var                 | 컴파일 타임 타입 추론 (runtime dynamic 아님)                       | language-ref |

## 3. 비동기 프로그래밍 (async/await)

### 공식 소스

| 소스             | URL                                                                       | 용도             |
|------------------|---------------------------------------------------------------------------|------------------|
| async/await 개요 | https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/ | Task, async 패턴 |

### 검증된 사실 (2026-08-02)

| 항목                     | 값                                                         | 출처             |
|--------------------------|------------------------------------------------------------|------------------|
| async 반환 타입          | `Task`, `Task<T>`, `void`(이벤트 핸들러만), `ValueTask<T>` | async/await docs |
| `await` 대상             | `Task`, `Task<T>`, `ValueTask<T>`, 커스텀 awaitable        | async/await docs |
| Task.Delay().Wait() 금지 | 동기 블로킹 — "Don't block, await instead" (공식 명시)     | async/await docs |
| ConfigureAwait(false)    | 라이브러리 코드에서 컨텍스트 전환 불필요 시 사용           | async/await docs |
| async void               | 예외 처리 어려움, 이벤트 핸들러 외 사용 비권장             | async/await docs |

## 4. 주요 언어 기능 (버전별)

### 공식 소스

| 소스             | URL                                                        | 용도            |
|------------------|------------------------------------------------------------|-----------------|
| C# 버전별 신기능 | https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/ | 버전별 변경사항 |

### 검증된 사실 (2026-08-02)

| 기능                  | 도입 버전 | 설명                                                 | 출처         |
|-----------------------|-----------|------------------------------------------------------|--------------|
| LINQ                  | C# 3      | 컬렉션/DB 쿼리 통합 문법                             | language-ref |
| lambda 식             | C# 3      | `(x) => x * 2`                                       | language-ref |
| dynamic               | C# 4      | 런타임 타입 결정 (DLR 기반)                          | language-ref |
| async/await           | C# 5      | 비동기 프로그래밍 모델                               | language-ref |
| null 조건 연산자 `?.` | C# 6      | `obj?.Property` — null이면 null 반환                 | language-ref |
| string 보간 `$""`     | C# 6      | `$"Hello {name}"` 형식                               | language-ref |
| tuple                 | C# 7      | `(int x, int y)` 값 튜플                             | language-ref |
| pattern matching      | C# 7+     | `is`, `switch` 식 패턴 (C# 8~14 지속 확장)           | language-ref |
| record                | C# 9      | `record` 키워드, 값 기반 동등성                      | language-ref |
| nullable ref 형식     | C# 8      | `string?`, NRT 옵트인                                | language-ref |
| init-only setter      | C# 9      | `init` — 객체 초기화 블록 후 불변                    | language-ref |
| global using          | C# 10     | `global using` 전역 네임스페이스 선언                | language-ref |
| record struct         | C# 10     | `record struct` — 값 형식 record                     | language-ref |
| required 멤버         | C# 11     | `required` 키워드 — 초기화 강제                      | language-ref |
| primary constructor   | C# 12     | class/struct에서 기본 생성자 선언 가능               | language-ref |
| 컬렉션 식             | C# 12     | `[1, 2, 3]` 형태 컬렉션 초기화                       | language-ref |
| field 키워드          | C# 14     | auto-property backing field 접근 (C# 13에서 preview) | language-ref |
| null 조건 할당 `??=`  | C# 8      | `x ??= defaultValue`                                 | language-ref |

## 5. 프로젝트 구조 / 빌드 시스템

### 공식 소스

| 소스       | URL                                                                     | 용도          |
|------------|-------------------------------------------------------------------------|---------------|
| .csproj    | https://learn.microsoft.com/en-us/dotnet/core/project-sdk/msbuild-props | 프로젝트 파일 |
| dotnet CLI | https://learn.microsoft.com/en-us/dotnet/core/tools/                    | CLI 명령어    |

### 검증된 사실 (2026-08-02)

| 항목             | 값                                                                 | 출처          |
|------------------|--------------------------------------------------------------------|---------------|
| 프로젝트 파일    | `.csproj` (MSBuild XML 기반)                                       | msbuild-props |
| 패키지 관리자    | NuGet (`dotnet add package`)                                       | dotnet CLI    |
| `dotnet new`     | 프로젝트 템플릿 생성 (console/web/classlib 등)                     | dotnet CLI    |
| `dotnet build`   | 컴파일 + 출력 디렉토리 생성 (`bin/`)                               | dotnet CLI    |
| `dotnet run`     | 빌드 + 실행                                                        | dotnet CLI    |
| `dotnet test`    | 테스트 실행 (xUnit/NUnit/MSTest 지원)                              | dotnet CLI    |
| `dotnet publish` | 배포용 출력 생성 (self-contained 가능)                             | dotnet CLI    |
| TargetFramework  | `net10.0`, `net9.0`, `net8.0` 등                                   | msbuild-props |
| Nullable         | `<Nullable>enable</Nullable>` — NRT 활성화                         | msbuild-props |
| ImplicitUsings   | `<ImplicitUsings>enable</ImplicitUsings>` — 공통 네임스페이스 자동 | msbuild-props |

## 6. deprecated / breaking changes

### 검증된 사실 (2026-08-02)

| 항목                        | 상태                                                       | 출처             |
|-----------------------------|------------------------------------------------------------|------------------|
| .NET Framework              | .NET 5+ 이후 별도 유지, 크로스 플랫폼 지원 없음            | MS 공식          |
| .NET Core 3.x               | EOL (2022-12-13), .NET 5+ 사용 권장                        | releases-index   |
| `Thread.Abort()`            | .NET 5+에서 `PlatformNotSupportedException` 발생           | language-ref     |
| `AppDomain.CreateDomain()`  | .NET Core/.NET 5+에서 지원 안 됨                           | language-ref     |
| 동기 블로킹 (`Task.Wait()`) | `await` 사용 권장 (공식 "Don't block, await instead")      | async/await docs |
| `var` 남용                  | 명시적 타입 가독성이 더 높은 경우 비권장 (공식 가이드라인) | language-ref     |

---

**작성일**: 2026-08-02

**마지막 업데이트**: 2026-08-02

© 2026 siasia86. Licensed under CC BY 4.0.

# C# dotnet CLI / 프로젝트 구조
<!-- reference: _reference/csharp_official_notes.md -->

dotnet CLI, .csproj 구조, NuGet 패키지 관리, 빌드/테스트/배포를 정리합니다.

## 목차

| 섹션                                                                                                     |
|----------------------------------------------------------------------------------------------------------|
| [1. dotnet CLI 기본](#1-dotnet-cli-기본) / [2. 프로젝트 파일 .csproj](#2-프로젝트-파일-csproj)           |
| [3. NuGet 패키지 관리](#3-nuget-패키지-관리) / [4. 빌드와 배포](#4-빌드와-배포) / [5. 테스트](#5-테스트) |

---

## 1. dotnet CLI 기본

### 프로젝트 생성 / 관리

```bash
# 프로젝트 생성 (템플릿)
dotnet new console -n MyApp          # 콘솔 앱
dotnet new webapi -n MyApi           # Web API
dotnet new classlib -n MyLib         # 클래스 라이브러리
dotnet new xunit -n MyTests          # xUnit 테스트
dotnet new sln -n MySolution         # 솔루션 파일

# 솔루션에 프로젝트 추가
dotnet sln MySolution.sln add MyApp/MyApp.csproj

# 템플릿 목록 확인
dotnet new list
```

### 실행 / 빌드 / 테스트

```bash
dotnet run                           # 빌드 + 실행
dotnet run --project MyApp           # 특정 프로젝트 실행
dotnet build                         # 빌드 (bin/ 출력)
dotnet build -c Release              # Release 구성으로 빌드
dotnet test                          # 테스트 실행
dotnet test --filter "Category=Unit" # 특정 테스트만 실행
dotnet clean                         # 빌드 결과물 제거
```

### 정보 확인

```bash
dotnet --version                     # SDK 버전
dotnet --list-sdks                   # 설치된 SDK 목록
dotnet --list-runtimes               # 설치된 런타임 목록
dotnet -vv                           # 자세한 버전 정보
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 프로젝트 파일 .csproj

MSBuild XML 기반입니다. 수동 편집 가능합니다.

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <!-- 대상 프레임워크 -->
    <TargetFramework>net10.0</TargetFramework>

    <!-- nullable 참조 형식 활성화 (C# 8+) -->
    <Nullable>enable</Nullable>

    <!-- 공통 네임스페이스 자동 추가 (C# 10+) -->
    <ImplicitUsings>enable</ImplicitUsings>

    <!-- C# 언어 버전 명시 (보통 자동 결정) -->
    <!-- <LangVersion>14</LangVersion> -->

    <!-- 루트 네임스페이스 -->
    <RootNamespace>MyApp</RootNamespace>

    <!-- 출력 타입: Exe (실행파일) / Library -->
    <OutputType>Exe</OutputType>
  </PropertyGroup>

  <!-- NuGet 패키지 참조 -->
  <ItemGroup>
    <PackageReference Include="Serilog" Version="4.3.0" />
    <PackageReference Include="Serilog.Sinks.Console" Version="6.0.0" />
  </ItemGroup>

  <!-- 프로젝트 참조 -->
  <ItemGroup>
    <ProjectReference Include="../MyLib/MyLib.csproj" />
  </ItemGroup>

</Project>
```

### 주요 PropertyGroup 설정

| 속성                    | 값 예시                   | 설명                             |
|-------------------------|---------------------------|----------------------------------|
| `TargetFramework`       | `net10.0`, `net8.0`       | 대상 .NET 버전                   |
| `Nullable`              | `enable` / `disable`      | NRT 활성화                       |
| `ImplicitUsings`        | `enable` / `disable`      | 자주 쓰는 네임스페이스 자동 추가 |
| `LangVersion`           | `14`, `latest`, `preview` | C# 언어 버전 지정                |
| `OutputType`            | `Exe` / `Library`         | 출력 타입                        |
| `Nullable`              | `enable`                  | C# 8+, `string?` 등 NRT 사용     |
| `TreatWarningsAsErrors` | `true`                    | 경고를 오류로 처리               |

### 멀티 타겟 프레임워크

```xml
<!-- 여러 프레임워크 동시 타겟 -->
<TargetFrameworks>net10.0;net8.0</TargetFrameworks>
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. NuGet 패키지 관리

```bash
# 패키지 추가
dotnet add package Serilog
dotnet add package Serilog --version 4.3.0  # 버전 고정

# 패키지 제거
dotnet remove package Serilog

# 패키지 업데이트 (최신 안정 버전)
dotnet add package Serilog

# 설치된 패키지 목록
dotnet list package

# 업데이트 가능한 패키지 확인
dotnet list package --outdated

# 패키지 복원 (nuget.config 또는 .csproj 기반)
dotnet restore
```

### packages.lock.json

```bash
# 재현 가능한 빌드를 위한 잠금 파일 생성
dotnet restore --use-lock-file
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 빌드와 배포

### 빌드 구성

```bash
# Debug 빌드 (기본)
dotnet build

# Release 빌드 (최적화)
dotnet build -c Release

# 출력 디렉토리 지정
dotnet build -o ./output
```

### 게시(Publish)

```bash
# 프레임워크 의존 게시 (런타임 별도 설치 필요)
dotnet publish -c Release

# self-contained 게시 (런타임 포함)
dotnet publish -c Release -r linux-x64 --self-contained

# 단일 파일 게시
dotnet publish -c Release -r linux-x64 \
  --self-contained \
  -p:PublishSingleFile=true \
  -p:EnableCompressionInSingleFile=true

# AOT (Ahead-of-Time) 컴파일 (.NET 8+)
dotnet publish -c Release -r linux-x64 \
  -p:PublishAot=true
```

### 런타임 식별자 (RID)

| 플랫폼      | RID           |
|-------------|---------------|
| Linux x64   | `linux-x64`   |
| Linux ARM64 | `linux-arm64` |
| macOS x64   | `osx-x64`     |
| macOS ARM64 | `osx-arm64`   |
| Windows x64 | `win-x64`     |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 테스트

### 테스트 프레임워크

| 프레임워크 | 패키지               | 특징                          |
|------------|----------------------|-------------------------------|
| xUnit      | `xunit`              | .NET 공식 권장, 병렬 실행     |
| NUnit      | `NUnit`              | 풍부한 어설션, 오래된 생태계  |
| MSTest     | `MSTest.TestAdapter` | Microsoft 공식, Visual Studio |

### xUnit 기본 구조

```csharp
using Xunit;

public class CalculatorTests
{
    [Fact]
    public void Add_TwoNumbers_ReturnsSum()
    {
        // Arrange
        var calc = new Calculator();

        // Act
        var result = calc.Add(2, 3);

        // Assert
        Assert.Equal(5, result);
    }

    [Theory]
    [InlineData(2, 3, 5)]
    [InlineData(-1, 1, 0)]
    [InlineData(0, 0, 0)]
    public void Add_WithVariousInputs(int a, int b, int expected)
    {
        var calc = new Calculator();
        Assert.Equal(expected, calc.Add(a, b));
    }
}
```

### 테스트 실행 옵션

```bash
dotnet test                              # 전체 실행
dotnet test --filter "FullyQualifiedName~Add"  # 이름 필터
dotnet test --filter "Category=Unit"           # 카테고리 필터
dotnet test -v normal                          # 상세 출력
dotnet test --collect:"XPlat Code Coverage"   # 코드 커버리지
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- dotnet CLI: [learn.microsoft.com/dotnet/core/tools](https://learn.microsoft.com/en-us/dotnet/core/tools/) — ★★★☆☆
- MSBuild props: [learn.microsoft.com/dotnet/core/project-sdk/msbuild-props](https://learn.microsoft.com/en-us/dotnet/core/project-sdk/msbuild-props) — ★★★☆☆
- NuGet CLI: [learn.microsoft.com/nuget/reference/dotnet-commands](https://learn.microsoft.com/en-us/nuget/reference/dotnet-commands) — ★★★☆☆

---

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)

---

**작성일**: 2026-08-02

**마지막 업데이트**: 2026-08-02

© 2026 siasia86. Licensed under CC BY 4.0.

# 통합 테스트 (Integration Testing)

## 목차

| 섹션                                                                                  |
|---------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 접근 방식](#2-접근-방식) / [3. 전략](#3-전략)                |
| [4. 유닛 테스트와의 차이](#4-유닛-테스트와의-차이) / [5. 실전 가이드](#5-실전-가이드) |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

통합 테스트는 개별 모듈/컴포넌트를 결합했을 때 인터페이스와 상호작용이 올바르게 동작하는지 검증하는 테스트입니다.

| 항목        | 내용                               |
|-------------|------------------------------------|
| 테스트 대상 | 모듈 간 인터페이스, 데이터 흐름    |
| 실행 속도   | 초~분 단위 (외부 의존성 포함 가능) |
| 실행 주체   | 개발자 또는 QA                     |
| 목적        | 모듈 간 연동 결함 발견             |

### 결함 발생 지점

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Module A │ ──> │ Module B │ ──> │ Module C │
└──────────┘     └──────────┘     └──────────┘
           ↑ 결함 발생 지점 ↑
       (인터페이스 불일치, 데이터 변환 오류)
```

[⬆ 목차로 돌아가기](#목차)

## 2. 접근 방식

### Big Bang

모든 모듈을 한 번에 결합하여 테스트합니다.

| 장점                 | 단점                  |
|----------------------|-----------------------|
| 준비 시간 짧음       | 결함 위치 파악 어려움 |
| 소규모 시스템에 적합 | 디버깅 비용 높음      |

### Top-Down

상위 모듈부터 하위 모듈 순으로 통합합니다.

```
     ┌───┐
     │ A │  ← test first
     └─┬─┘
   ┌───┴───┐
   │       │
 ┌─┴─┐  ┌─┴─┐
 │ B │  │ C │  ← replace with Stub
 └───┘  └───┘
```

- 하위 모듈은 **Stub**(더미 응답 반환)으로 대체
- 주요 제어 흐름을 먼저 검증 가능

### Bottom-Up

하위 모듈부터 상위 모듈 순으로 통합합니다.

```
 ┌───┐  ┌───┐
 │ B │  │ C │  ← test first
 └─┬─┘  └─┬─┘
   └───┬───┘
     ┌─┴─┐
     │ A │  ← call via Driver
     └───┘
```

- 상위 모듈은 **Driver**(호출자 역할)로 대체
- 하위 모듈의 기능을 먼저 검증 가능

### Sandwich (혼합)

Top-Down + Bottom-Up을 동시에 진행합니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 전략

### 테스트 대상 인터페이스

| 인터페이스 유형 | 검증 항목                           |
|-----------------|-------------------------------------|
| API 호출        | 요청/응답 형식, 상태 코드, 타임아웃 |
| DB 연동         | CRUD 정합성, 트랜잭션, 커넥션 풀    |
| 메시지 큐       | 발행/구독, 순서 보장, 재시도        |
| 파일 시스템     | 읽기/쓰기, 권한, 경로 처리          |
| 외부 서비스     | 인증, 에러 응답, 네트워크 장애      |

### 테스트 환경

```
┌───────────────────────────────────────┐
│         Test Environment              │
│  ┌──────┐  ┌──────┐  ┌─────────────┐  │
│  │ App  │──│  DB  │  │ Mock Server │  │
│  │      │──│(real)│  │ External API│  │
│  └──────┘  └──────┘  └─────────────┘  │
└───────────────────────────────────────┘
```

- DB: 실제 인스턴스 사용 (테스트 전용)
- 외부 API: Mock/Stub 서버로 대체
- 메시지 큐: 테스트용 인스턴스 또는 인메모리

[⬆ 목차로 돌아가기](#목차)

## 4. 유닛 테스트와의 차이

| 항목        | 유닛 테스트      | 통합 테스트            |
|-------------|------------------|------------------------|
| 범위        | 함수/클래스 1개  | 모듈 2개 이상 결합     |
| 외부 의존성 | Mock 처리        | 실제 사용 (DB, API 등) |
| 실행 속도   | ms 단위          | 초~분 단위             |
| 결함 유형   | 로직 오류        | 인터페이스 불일치      |
| 실행 빈도   | 코드 변경 시마다 | 빌드/배포 시           |
| 테스트 수   | 많음 (수백~수천) | 적음 (수십~수백)       |

[⬆ 목차로 돌아가기](#목차)

## 5. 실전 가이드

### 인프라 통합 테스트 예시

```python
import pytest
import subprocess

class TestNginxBackend:
    """Nginx → Backend 연동 테스트"""

    def test_proxy_pass(self):
        """Nginx가 백엔드로 요청을 전달하는지 확인"""
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost/api/health"],
            capture_output=True, text=True
        )
        assert result.stdout == "200"

    def test_upstream_failover(self):
        """백엔드 1대 다운 시 다른 서버로 전환되는지 확인"""
        # backend-1 중지 후 요청
        subprocess.run(["docker", "stop", "backend-1"])
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost/api/health"],
            capture_output=True, text=True
        )
        assert result.stdout == "200"
        subprocess.run(["docker", "start", "backend-1"])
```

### 테스트 격리

```python
@pytest.fixture(autouse=True)
def clean_db(db_connection):
    """각 테스트 전후 DB 초기화"""
    yield
    db_connection.execute("TRUNCATE TABLE users")
    db_connection.commit()
```

### 실행 분리

```bash
# 유닛 테스트만 (빠름)
pytest tests/unit/ -m "not integration"

# 통합 테스트만 (느림, CI에서)
pytest tests/integration/ -m integration
```

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- Martin Fowler. "Integration Test" — ★★★★☆
- ISTQB Foundation Level Syllabus — ★★★☆☆
- [유닛 테스트](unit_testing.md)
- [Python 테스트 실습](../../../11_python/python_testing.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-08

**마지막 업데이트**: 2026-05-08

© 2026 siasia86. Licensed under CC BY 4.0.

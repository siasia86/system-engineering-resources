# 회귀 테스트 (Regression Testing)

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. 전략](#2-전략) / [3. 자동화](#3-자동화) |
| [4. 실전 가이드](#4-실전-가이드) |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

회귀 테스트는 코드 변경(버그 수정, 기능 추가, 리팩토링) 후 기존 기능이 정상 동작하는지 재검증하는 테스트입니다.

| 항목          | 내용                                          |
|---------------|-----------------------------------------------|
| 목적          | 변경으로 인한 의도치 않은 부작용 탐지         |
| 실행 시점     | 코드 변경 후, 배포 전                         |
| 핵심 원칙     | 이전에 통과한 테스트가 여전히 통과해야 함     |
| 비용          | 테스트 스위트가 커질수록 실행 시간 증가       |

[⬆ 목차로 돌아가기](#목차)

## 2. 전략

### 전체 회귀 (Full Regression)

모든 테스트를 재실행합니다.

- 장점: 누락 없음
- 단점: 시간/비용 높음
- 적용: 릴리스 전, 주요 변경 시

### 선택적 회귀 (Selective Regression)

변경 영향 범위에 해당하는 테스트만 실행합니다.

- 장점: 빠름
- 단점: 영향 분석 정확도에 의존
- 적용: 일상적 코드 변경

### 우선순위 기반 (Priority-based)

| 우선순위 | 기준                          | 예시                    |
|----------|-------------------------------|-------------------------|
| P1       | 핵심 비즈니스 기능            | 결제, 로그인            |
| P2       | 자주 사용되는 기능            | 검색, 목록 조회         |
| P3       | 최근 변경된 영역              | 이번 스프린트 수정 부분 |
| P4       | 과거 결함 발생 영역           | 버그 이력 기반          |

[⬆ 목차로 돌아가기](#목차)

## 3. 자동화

### CI/CD 파이프라인 연동

```
코드 변경 → Push → CI 트리거 → 회귀 테스트 실행 → 결과 리포트
                                      │
                                      ├── Pass → Deploy
                                      └── Fail → Block, Alert
```

### 테스트 분류 실행

```bash
# 빠른 회귀 (PR 시)
pytest -m "not slow" --timeout=60

# 전체 회귀 (배포 전)
pytest --timeout=300

# 변경 파일 기반 선택적 실행
pytest --co -q | grep "$(git diff --name-only HEAD~1 | sed 's/.py//')"
```

[⬆ 목차로 돌아가기](#목차)

## 4. 실전 가이드

### 회귀 테스트 유지보수

| 문제                  | 해결                                    |
|-----------------------|-----------------------------------------|
| 테스트 실행 시간 증가 | 병렬 실행, 선택적 회귀                  |
| 불안정한 테스트       | flaky 테스트 격리, 재시도 로직          |
| 테스트 코드 부채      | 정기적 리뷰, 불필요 테스트 제거         |
| 환경 의존성           | Docker 기반 테스트 환경 표준화          |

### 회귀 테스트 추가 기준

새 버그를 수정할 때마다 해당 버그를 재현하는 테스트를 추가합니다.

```python
def test_issue_1234_negative_balance():
    """Issue #1234: 동시 출금 시 잔액이 음수가 되는 버그"""
    account = Account(balance=100)
    account.withdraw(100)
    with pytest.raises(InsufficientFundsError):
        account.withdraw(1)
```

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- ISTQB Foundation Level Syllabus — ★★★☆☆
- [유닛 테스트](unit_testing.md)
- [통합 테스트](integration_testing.md)

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

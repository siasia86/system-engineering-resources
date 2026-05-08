# 테스트 기법 (Testing Techniques)

소프트웨어 테스트 이론 및 기법 정리입니다. 언어에 종속되지 않는 범용 개념을 다룹니다.

## 구조

```
02_testing/
├── 01_black_box/                  # Black-box (input/output)
│   ├── boundary_value_analysis.md
│   ├── equivalence_partitioning.md
│   ├── decision_table_testing.md
│   ├── state_transition_testing.md
│   └── pairwise_testing.md
├── 02_white_box/                  # White-box (code-based)
│   └── code_coverage.md
├── 03_test_levels/                # Test levels
│   ├── unit_testing.md
│   ├── integration_testing.md
│   ├── regression_testing.md
│   ├── performance_testing.md
│   └── e2e_testing.md
└── README.md
```

## 블랙박스 테스트 (01_black_box)

내부 구현을 모르는 상태에서 입력/출력만으로 검증합니다.

| 문서                                                          | 설명                              |
|---------------------------------------------------------------|-----------------------------------|
| [경계값 분석](01_black_box/boundary_value_analysis.md)        | 경계 ±1 지점 테스트               |
| [동등 분할](01_black_box/equivalence_partitioning.md)         | 입력 도메인 파티셔닝              |
| [결정 테이블](01_black_box/decision_table_testing.md)         | 조건 조합별 동작 검증             |
| [상태 전이](01_black_box/state_transition_testing.md)         | 상태 머신 기반 검증               |
| [페어와이즈](01_black_box/pairwise_testing.md)                | 다중 입력 조합 최소화             |

## 화이트박스 테스트 (02_white_box)

소스 코드 구조를 기반으로 검증합니다.

| 문서                                          | 설명                                    |
|-----------------------------------------------|-----------------------------------------|
| [코드 커버리지](02_white_box/code_coverage.md) | 구문/분기/조건/MC/DC 커버리지          |

## 테스트 수준 (03_test_levels)

테스트 범위와 목적에 따른 분류입니다.

| 문서                                                    | 설명                          |
|---------------------------------------------------------|-------------------------------|
| [유닛 테스트](03_test_levels/unit_testing.md)           | 함수/클래스 단위 독립 검증    |
| [통합 테스트](03_test_levels/integration_testing.md)    | 모듈 간 인터페이스 검증       |
| [회귀 테스트](03_test_levels/regression_testing.md)     | 변경 후 기존 기능 재검증      |
| [성능 테스트](03_test_levels/performance_testing.md)    | 응답 시간, 처리량, 한계점     |
| [E2E 테스트](03_test_levels/e2e_testing.md)             | 전체 시스템 시나리오 검증     |

## 테스트 피라미드

```
        /\        E2E (소수, 느림)
       /  \
      /----\
     /      \     Integration (중간)
    /--------\
   /          \   Unit (다수, 빠름)
  /____________\
```

## 관련 문서

- [Python 테스트 실습](../../11_python/python_testing.md) — pytest, unittest, Mock, 커버리지

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

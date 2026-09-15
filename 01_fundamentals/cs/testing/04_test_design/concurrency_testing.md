# 동시성 테스트 (Concurrency Testing)
<!-- reference: _reference/software_testing_official_notes.md -->

동시성 테스트(Concurrency Testing)는 여러 작업이 동시에 실행되거나 실행 순서가 달라질 때 시스템의 정확성·안정성·데이터 정합성을 검증하는 테스트입니다.

## 목차

| 섹션                                                                                     |
|------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 동시성 위험](#2-동시성-위험) / [3. 테스트 설계](#3-테스트-설계) |
| [4. 실행·관찰](#4-실행관찰) / [5. 체크리스트](#5-체크리스트)                             |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

동시성 문제는 단일 실행에서는 나타나지 않고 타이밍·순서·리소스 경합에 따라 발생할 수 있습니다.

| 대상        | 검증 예시                         |
|-------------|-----------------------------------|
| 공유 데이터 | 동시 갱신·lost update·중복 생성   |
| 상태 전이   | 같은 이벤트의 중복 처리·순서 역전 |
| 리소스      | Lock·connection pool·파일·큐 경합 |
| 외부 호출   | 동시 retry·timeout·중복 요청      |
| 작업 실행   | 병렬 작업의 완료 순서·취소·재시작 |

동시성 테스트는 단순히 사용자 수를 늘리는 테스트가 아니라, **동시 실행으로 결과가 달라질 수 있는 조건**을 의도적으로 만드는 테스트입니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 동시성 위험

| 위험 유형           | 설명                                        |
|---------------------|---------------------------------------------|
| Race Condition      | 실행 순서에 따라 결과가 달라짐              |
| Lost Update         | 한 갱신이 다른 갱신을 덮어씀                |
| Duplicate Action    | 같은 작업이 두 번 이상 수행됨               |
| Deadlock            | 작업들이 서로 Lock을 기다리며 진행하지 못함 |
| Starvation          | 특정 작업이 계속 실행 기회를 얻지 못함      |
| Dirty Read          | 확정되지 않은 변경을 다른 작업이 읽음       |
| Resource Exhaustion | 동시 작업이 Pool·FD·메모리 등을 고갈시킴    |

### 상태와 이벤트 순서

동일한 이벤트라도 순서가 바뀌면 결과가 달라지는지 확인합니다.

```text
초기 상태
   ├── 요청 A → 상태 X
   └── 요청 B → 상태 Y

검증:
  A → B, B → A, A와 B 동시 실행의 최종 상태가 정책과 일치하는가?
```

[⬆ 목차로 돌아가기](#목차)

## 3. 테스트 설계

1. 공유되는 상태·데이터·리소스를 식별합니다.
2. 동시에 실행할 작업과 허용된 순서를 정의합니다.
3. 각 작업의 기대 결과와 최종 정합성 조건을 정의합니다.
4. 동시 실행·순서 교차·지연 삽입 조건을 구성합니다.
5. 중복·재시도·취소·timeout 이후의 결과를 확인합니다.
6. 실패 시 재현에 필요한 타이밍·입력·로그를 저장합니다.

### 케이스 예시

| 케이스  | 동시 작업                 | 기대 결과                            |
|---------|---------------------------|--------------------------------------|
| CON-001 | 동일 데이터에 두 갱신     | 정책에 맞는 최종값·충돌 처리         |
| CON-002 | 동일 요청 두 번 전송      | 멱등 처리·중복 부수 효과 없음        |
| CON-003 | Lock을 획득한 작업을 중단 | Lock 해제·다음 작업 진행             |
| CON-004 | 의존성 응답 지연 중 retry | 중복 호출 제한·일관된 최종 상태      |
| CON-005 | 작업 A·B의 완료 순서 역전 | 허용된 순서 규칙 또는 최종 상태 유지 |

테스트 결과는 단순 성공 여부뿐 아니라 최종 상태·중복·누락·Lock 잔존 여부를 포함해야 합니다.

[⬆ 목차로 돌아가기](#목차)

## 4. 실행·관찰

| 관찰 항목 | 확인 내용                                               |
|-----------|---------------------------------------------------------|
| 최종 상태 | 모든 동시 작업 이후 기대 상태인가?                      |
| 중복·누락 | 이벤트·데이터·부수 효과가 중복되거나 누락되지 않았는가? |
| Lock      | 교착·장기 점유·해제 누락이 없는가?                      |
| Pool      | 연결·스레드·파일·메시지 Pool이 회수되는가?              |
| 재시도    | timeout과 재시도가 폭주하지 않는가?                     |
| 재현성    | 실행 순서·지연·seed를 기록해 다시 재현할 수 있는가?     |

동시성 실패는 로그에 요청 ID·작업 ID·데이터 키·시각·상태 전이를 남겨야 분석할 수 있습니다. 테스트 환경의 부하 생성기 병목과 대상 시스템의 동시성 문제를 구분합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 체크리스트

- [ ] 공유 상태와 동시 작업이 명확합니다.
- [ ] 정상 순서와 역순·동시 실행을 비교합니다.
- [ ] 중복 요청·retry·timeout·취소를 포함합니다.
- [ ] 최종 데이터 정합성과 부수 효과를 검증합니다.
- [ ] Lock·Pool·FD·메모리 회수 상태를 확인합니다.
- [ ] deadlock·starvation·resource exhaustion 조건을 고려합니다.
- [ ] 요청·작업·데이터 키로 실행을 재현할 수 있습니다.
- [ ] 테스트 데이터와 실행 환경을 격리·정리합니다.

## 참고 자료

- ISTQB Certified Tester Foundation Level: [istqb.org](https://www.istqb.org/certifications/certified-tester-foundation-level) — ★★★☆☆
- [테스트 케이스 설계](test_case_design.md)
- [테스트 오라클](test_oracle.md)
- [Edge Case Testing](edge_case_testing.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-15

**마지막 업데이트**: 2026-09-15

© 2026 siasia86. Licensed under CC BY 4.0.

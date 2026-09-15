# 장애 주입 테스트 (Fault Injection Testing)
<!-- reference: _reference/software_testing_official_notes.md, _reference/chaos_finops_official_notes.md -->

장애 주입 테스트(Fault Injection Testing)는 시스템에 실패·지연·손실·고갈 조건을 의도적으로 넣고 오류 처리와 복구 동작을 검증하는 테스트입니다. 정상 흐름만으로 확인하기 어려운 복원력과 graceful degradation을 검증합니다.

## 목차

| 섹션                                                                                             |
|--------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 장애 유형](#2-장애-유형) / [3. 실험 설계](#3-실험-설계)                 |
| [4. 안전한 실행](#4-안전한-실행) / [5. 결과 판정](#5-결과-판정) / [6. 체크리스트](#6-체크리스트) |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

장애 주입은 무작위로 시스템을 망가뜨리는 작업이 아닙니다. 정상 상태와 가설을 먼저 정의하고 통제된 범위에서 장애를 주입한 뒤, 관찰 결과와 복구 기준을 비교합니다.

```text
정상 상태 정의
      │
      v
장애·영향·복구 가설 수립
      │
      v
안전 조건 확인 후 장애 주입
      │
      v
지표·로그·알림·복구 관찰
      │
      v
가설 판정·중단·정리·후속 조치
```

[⬆ 목차로 돌아가기](#목차)

## 2. 장애 유형

| 유형        | 주입 예시                          | 검증 대상                        |
|-------------|------------------------------------|----------------------------------|
| 프로세스    | 프로세스 종료·재시작               | 재시작·헬스체크·세션 복구        |
| 네트워크    | 지연·패킷 손실·연결 차단           | timeout·retry·fallback           |
| 의존 서비스 | DB·Cache·API 응답 오류 또는 지연   | circuit breaker·graceful degrade |
| 저장소      | 읽기 전용·공간 부족·I/O 오류       | 오류 처리·정리·알림              |
| 리소스      | CPU·메모리·FD·Connection Pool 고갈 | 제한·격리·확장·복구              |
| 데이터      | 잘못된 형식·부분 응답·중복 이벤트  | 검증·멱등성·정합성               |
| 시간        | 만료·시계 차이·응답 순서 역전      | 상태 전이·재시도·만료 처리       |

장애 유형은 시스템의 실제 의존성과 위협 모델에 맞춰 선택합니다. 테스트하지 않은 장애는 복원력이 확인된 것으로 간주하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 실험 설계

### 필수 설계 항목

| 항목      | 작성 내용                               |
|-----------|-----------------------------------------|
| 가설      | 장애 중에도 유지되어야 하는 정상 상태   |
| 대상      | 장애를 주입할 서비스·인스턴스·요청 범위 |
| 주입 방법 | 재현 가능한 명령·도구·설정              |
| 관찰 지표 | 오류율·지연·가용성·복구·데이터 상태     |
| 중단 조건 | 고객 영향·지표 악화·예상 밖 상태        |
| 복구 방법 | 자동 복구·수동 조치·rollback            |
| 종료 조건 | 실험 시간·복구 확인·증적 수집 완료      |
| 후속 조치 | 결함·알림 개선·설정 변경·재실험         |

### 테스트 케이스 예시

```text
FI-001: 외부 API timeout
  Given 정상 응답과 정상 지표가 확인됨
  When 외부 API 응답을 지연시킴
  Then timeout 후 재시도 횟수가 정책 이내이고 fallback 결과를 반환함
  And 복구 후 정상 요청이 재개됨

FI-002: DB 연결 실패
  Given 읽기·쓰기 요청이 정상 처리됨
  When DB 연결을 차단함
  Then 오류가 사용자 응답으로 안전하게 변환되고 민감 정보가 노출되지 않음
  And 연결 복구 후 중복·유실 데이터가 없음
```

[⬆ 목차로 돌아가기](#목차)

## 4. 안전한 실행

### 폭발 반경 제어

- 테스트 전용 환경 또는 승인된 제한 범위에서 시작합니다.
- 대상·시간·트래픽·계정 범위를 명시합니다.
- 자동 중단 조건과 수동 Kill Switch를 준비합니다.
- 고객 데이터·결제·외부 알림으로 장애가 전파되지 않도록 격리합니다.
- 실험 전후의 정상 상태와 rollback 방법을 확인합니다.
- 진행 중인 배포·백업·장애 대응과 충돌하지 않도록 조정합니다.

### 실행 전 확인

- [ ] 가설과 기대 복구 시간이 기록되었습니다.
- [ ] 영향 범위와 중단 조건이 승인되었습니다.
- [ ] 모니터링·알림·로그가 정상입니다.
- [ ] 테스트 데이터와 자격증명이 격리되었습니다.
- [ ] 복구 담당자와 연락 경로가 정해졌습니다.
- [ ] 실험 종료 후 정리 절차가 준비되었습니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 결과 판정

| 결과      | 의미                                       | 후속 조치                    |
|-----------|--------------------------------------------|------------------------------|
| 가설 확인 | 정상 상태·복구 기준을 만족                 | 증적 보관·범위 확대 검토     |
| 가설 반증 | 복구·오류 처리·데이터 조건이 기준을 벗어남 | 결함 등록·수정·재실험        |
| 부분 확인 | 일부 지표는 유지되나 특정 조건이 실패      | 실패 조건 분리·보완          |
| 판정 불가 | 관찰 지표·중단 조건·증적이 부족            | 관찰 설계 보완 후 재실험     |
| 실험 중단 | 안전 조건을 벗어나 중단                    | 영향 분석·rollback·사후 검토 |

장애 주입 테스트의 성공은 장애가 발생하지 않는 것이 아니라, 예상한 장애에서 시스템이 정의된 방식으로 실패하고 복구하는 것입니다.

실험 결과에는 주입 시각·대상·조건·지표·알림·복구 시각·데이터 검증·후속 조치를 기록합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 체크리스트

- [ ] 정상 상태와 장애 가설이 정의되었습니다.
- [ ] 장애 대상·범위·시간·주입 방법이 명확합니다.
- [ ] 오류율·지연·알림·복구·데이터 지표를 관찰합니다.
- [ ] 자동 중단과 수동 Kill Switch가 준비되었습니다.
- [ ] 고객·결제·외부 시스템으로의 영향이 차단되었습니다.
- [ ] 장애 중 중복·유실·민감 정보 노출을 확인합니다.
- [ ] 복구 후 정상 흐름과 잔존 리소스를 확인합니다.
- [ ] 실험 증적과 후속 조치를 기록합니다.
- [ ] 결함 수정 후 동일 조건으로 재검증합니다.

## 참고 자료

- Principles of Chaos Engineering: [principlesofchaos.org](https://principlesofchaos.org/) — ★★★★☆
- AWS Fault Injection Service: [docs.aws.amazon.com/fis](https://docs.aws.amazon.com/fis/latest/userguide/) — ★★★☆☆
- [Edge Case Testing](edge_case_testing.md)
- [테스트 오라클](test_oracle.md)

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

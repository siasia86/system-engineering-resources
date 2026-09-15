# 게임 성능 테스트 (Game Performance Testing)
<!-- reference: _reference/game_testing_official_notes.md, _reference/load_testing_official_notes.md -->

게임 성능 테스트는 게임 기능이 요구된 품질 수준에서 동작하는지 CPU·메모리·렌더링·게임 상태·네트워크·서버 처리 관점으로 측정하고 병목을 찾는 테스트입니다.

## 목차

| 섹션                                                                                             |
|--------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 성능 모델](#2-성능-모델) / [3. 측정 지표](#3-측정-지표)                 |
| [4. 테스트 유형](#4-테스트-유형) / [5. 결과 분석](#5-결과-분석) / [6. 체크리스트](#6-체크리스트) |

[⬆ 목차로 돌아가기](#목차)

## 1. 개요

게임 성능은 단일 지표가 아니라 사용자 입력부터 결과 표시·서버 상태·저장까지의 흐름으로 관찰합니다.

| 구간        | 성능 관점                     |
|-------------|-------------------------------|
| 초기 실행   | 로딩·설정·콘텐츠 준비·첫 화면 |
| 플레이 실행 | 입력·규칙·상태 갱신·렌더링    |
| 네트워크    | 요청·응답·장기 연결·재접속    |
| 서버 처리   | 게임 로직·방·매칭·이벤트·저장 |
| 데이터      | DB·Cache·Queue·파일 처리      |
| 장시간 운영 | 메모리·GC·FD·연결·성능 열화   |

게임 성능 테스트와 게임 서비스 부하 테스트는 연결되지만 같은 테스트는 아닙니다. 클라이언트·게임 루프·서버·인프라의 측정 범위를 구분합니다.

[⬆ 목차로 돌아가기](#목차)

## 2. 성능 모델

```text
입력·이벤트
    │
    v
게임 로직·상태 갱신 ──> 렌더링·출력
    │
    ├──> 네트워크 송수신
    ├──> 저장·이벤트 처리
    └──> 관찰 지표·로그
```

### 기준선 작성

1. 대표적인 정상 흐름과 데이터를 정합니다.
2. 테스트 환경·기기·빌드·서버 설정을 기록합니다.
3. 사용자 체감 구간과 내부 처리 구간을 분리합니다.
4. 정상 부하·증가 부하·장시간 부하를 비교합니다.
5. 병목·tail latency·리소스 열화를 함께 분석합니다.

합격 기준은 프로젝트 SLO·기기 등급·리전·게임 장르에 따라 정의하며, 일반적인 단일 수치를 모든 게임에 적용하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

## 3. 측정 지표

| 영역        | 지표 예시                                    |
|-------------|----------------------------------------------|
| 사용자 체감 | 입력 지연·화면 갱신·로딩·끊김                |
| 게임 루프   | frame/tick 시간·처리 누락·상태 갱신 지연     |
| CPU·메모리  | 사용률·할당·GC·메모리 증가 추세              |
| 네트워크    | RTT·지터·손실·메시지 지연·재연결             |
| 서버        | 요청 latency·처리량·오류율·방·CCU            |
| 데이터 계층 | DB query·lock·connection pool·cache hit/miss |
| 안정성      | crash·timeout·restart·복구 시간              |

평균값만 사용하지 않고 분포·tail latency·시간에 따른 변화와 오류율을 함께 기록합니다.

[⬆ 목차로 돌아가기](#목차)

## 4. 테스트 유형

| 유형             | 목적                                        |
|------------------|---------------------------------------------|
| 기준선 테스트    | 대표 흐름의 기준 성능 확보                  |
| 평균 부하 테스트 | 예상 정상 사용 조건의 성능 확인             |
| 스트레스 테스트  | 예상 범위를 초과할 때 한계와 장애 모드 확인 |
| 스파이크 테스트  | 갑작스러운 활동 증가에 대한 동작 확인       |
| 내구성 테스트    | 장시간 실행에 따른 누수·열화 확인           |
| 확장성 테스트    | 리소스·인스턴스 증가에 따른 처리 변화 확인  |
| 복구 성능 테스트 | 장애·재시작·재접속 후 정상화 과정 확인      |

k6의 부하 유형 기준은 `_reference/load_testing_official_notes.md`를 참조하고, 게임 클라이언트·게임 루프 측정은 `_reference/game_testing_official_notes.md`의 적용 범위로 구분합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 결과 분석

### 병목 분류

| 증상                  | 우선 확인 대상                           |
|-----------------------|------------------------------------------|
| 입력·상태 갱신 지연   | 게임 루프·CPU·동기 작업·GC               |
| 네트워크 tail latency | RTT·지터·재시도·연결 수·서버 처리        |
| 장시간 메모리 증가    | 객체 수명·캐시·이벤트·연결·로그          |
| 서버 처리량 저하      | CPU·Pool·DB query·lock·queue             |
| 오류율 증가           | 의존성 timeout·재시도·과부하·데이터 오류 |
| 복구 후 중복·유실     | 상태 저장·이벤트 순서·멱등성·재처리      |

### 분석 원칙

- 부하 생성기 병목과 대상 시스템 병목을 분리합니다.
- 클라이언트·네트워크·서버·DB의 측정 시각을 맞춥니다.
- 평균값만으로 정상 여부를 결론 내리지 않습니다.
- 테스트 환경·데이터·빌드·설정 차이를 결과와 함께 기록합니다.
- 성능 저하와 기능 오류·데이터 정합성 실패를 함께 판정합니다.

[⬆ 목차로 돌아가기](#목차)

## 6. 체크리스트

- [ ] 성능 범위와 사용자 흐름이 정의되었습니다.
- [ ] 기준선·평균·스트레스·스파이크·내구성 유형을 구분합니다.
- [ ] 클라이언트·게임 루프·네트워크·서버·데이터 지표를 분리합니다.
- [ ] 환경·기기·빌드·데이터·설정을 기록합니다.
- [ ] 평균·분포·tail latency·오류율을 함께 봅니다.
- [ ] CPU·메모리·GC·Pool·DB·Cache·Queue를 관찰합니다.
- [ ] 장애·재시작·재접속 후 성능과 정합성을 확인합니다.
- [ ] 병목과 부하 생성기 한계를 구분합니다.
- [ ] 특정 엔진·기기 수치를 모든 게임에 일반화하지 않습니다.

## 참고 자료

- k6 Load Test Types: [grafana.com/docs/k6](https://grafana.com/docs/k6/latest/testing-guides/test-types/) — ★★★☆☆
- Google SRE Managing Load: [sre.google/workbook/managing-load](https://sre.google/workbook/managing-load/) — ★★★★☆
- Unity Test Framework: [docs.unity3d.com](https://docs.unity3d.com/Packages/com.unity.test-framework@1.3/manual/index.html) — ★★★☆☆
- [게임 테스트 케이스 설계](game_test_case_design.md)
- [게임 상태 테스트](game_state_testing.md)

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

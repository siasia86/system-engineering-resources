---
name: game-testing-official-notes
description: 게임 도메인 테스트 개념을 위한 Unity Test Framework와 Firebase Test Lab 공식 참조 노트.
tags:
  - game-testing
  - unity
  - test-framework
  - firebase-test-lab
last_checked: 2026-09-15
sources:
  - https://docs.unity3d.com/Packages/com.unity.test-framework@1.3/manual/index.html
  - https://firebase.google.com/docs/test-lab/game-loop
---

# Game Testing 공식 참조 노트

## 1. 확인 범위

게임 도메인 테스트 문서에서 사용할 수 있는 공식 테스트 프레임워크와 게임 테스트 실행 모델을 2026-09-15에 Unity 공식 패키지 문서와 Firebase 공식 문서 기준으로 확인했습니다.

## 2. 공식 기준

Unity Test Framework 공식 문서는 Unity 프로젝트에서 테스트 프레임워크를 사용하는 방법과 테스트 실행 구조를 설명합니다. 확인한 문서는 `com.unity.test-framework` 1.3.9 패키지 문서입니다.

Firebase Test Lab Game Loop 공식 문서는 게임에 맞춘 테스트를 작성하고 선택한 실제·가상 기기에서 실행하는 흐름을 설명합니다.

## 3. 적용 범위

다음 게임 도메인 개념의 공통 참조로 사용합니다.

- 게임 테스트 케이스의 구성
- 게임 상태와 상태 전이
- 게임 플레이 시나리오
- 저장·복구와 중단 후 재실행
- 게임 기능 테스트의 실행 구조
- 게임 클라이언트 테스트의 기기 실행 관점

매칭 규칙·게임 경제·서버 부하·네트워크 프로토콜은 하나의 엔진 문서만으로 일반화하지 않습니다. 해당 주제는 본문 범위에 맞는 공식 API·부하·디바이스 참조 노트를 함께 연결합니다.

## 4. 검증 원칙

- Unity Test Framework의 동작을 모든 게임 엔진의 공통 규칙으로 확대하지 않습니다.
- Firebase Game Loop의 기기 실행 모델과 게임 서버 부하 테스트를 혼동하지 않습니다.
- 게임 장르별 규칙은 프로젝트 요구사항과 별도 테스트 오라클로 정의합니다.
- 실제 기기·에뮬레이터·게임 서버 검증은 서로 다른 테스트 대상으로 구분합니다.

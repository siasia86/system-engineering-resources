# Codex IDE 사용 가이드

VS Code 계열, JetBrains IDE, Xcode 등 IDE 안에서 열린 파일과 선택 코드를 활용해 Codex로 수정·리뷰·작업 위임을 수행하는 방법을 정리합니다.

## 목차

- [1. IDE 사용 범위](#1-ide-사용-범위)
- [2. 설치와 로그인](#2-설치와-로그인)
- [3. 편집기 context로 요청하기](#3-편집기-context로-요청하기)
- [4. 변경 검토](#4-변경-검토)
- [5. 작업 위임](#5-작업-위임)

---

## 1. IDE 사용 범위

IDE 통합은 현재 열어 둔 파일, 선택한 코드, 편집 중인 변경을 중심으로 빠르게 반복할 때 적합합니다. 전체 저장소 탐색·shell test·CI 자동화는 [CLI Linux 가이드](codex_cli_linux_guide.md), 제품 또는 pipeline 통합은 [API·자동화 가이드](codex_api_guide.md)를 사용합니다. 공통 원칙은 [Codex 공통 개념](codex_concepts.md)에 있습니다.

- 함수·모듈 한정 수정: 선택 코드와 예상 동작을 함께 첨부합니다.
- 익숙하지 않은 코드 이해: 열린 파일, 호출 위치, 질문 범위를 함께 제공합니다.
- 변경 사항 리뷰: diff를 나란히 보고 test와 위험을 요청합니다.
- 여러 영역의 장시간 작업: cloud 또는 subagent에 위임한 뒤 결과를 IDE에서 검토합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 설치와 로그인

지원 IDE에서 Codex 통합을 설치 또는 활성화한 후 ChatGPT 계정이나 조직이 허용한 인증 방식으로 로그인합니다. VS Code 및 호환 편집기는 Codex extension을 사용하며, JetBrains IDE와 Xcode는 각 IDE의 AI chat에서 Codex를 선택하는 방식이 제공될 수 있습니다.

IDE와 extension 버전, 조직 정책에 따라 메뉴 이름과 지원 범위가 달라질 수 있습니다. 설치 전에는 extension publisher와 요구 권한을 확인하고, 최신 지원 편집기 목록은 [공식 IDE 문서](https://learn.chatgpt.com/docs/codex/ide)를 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 편집기 context로 요청하기

열린 파일이나 선택 영역은 유용한 context이지만 전체 설계 의도를 자동으로 전달하지는 않습니다. 요청에는 다음을 포함합니다.

- 변경 목표와 사용자가 관찰한 증상
- 수정 가능 파일과 수정하지 않을 public API 또는 설정
- 관련 test와 성공 기준
- 생성 코드에 적용할 코드 스타일·보안·성능 제약

예시 요청:

```text
현재 선택한 retry 로직만 수정해.
재시도 횟수와 public 함수 signature는 유지하고, timeout 발생 시 중복 요청이 생기지 않게 해.
관련 unit test를 찾아 실행하고, 변경 diff와 남은 경쟁 조건을 보고해.
```

context에 보이지 않는 설정 파일, generated code, 배포 정책이 영향을 준다면 경로를 명시하거나 먼저 탐색·분석만 요청합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 변경 검토

IDE에서 제안된 변경은 적용 전과 후에 diff로 검토합니다. 특히 다음을 확인합니다.

1. 선택한 코드 밖의 파일이 변경되었는지 확인합니다.
2. 예외 처리, 입력 검증, logging에 비밀정보 노출이 없는지 확인합니다.
3. formatter·lint·unit test와 프로젝트의 필수 검증을 실행합니다.
4. test가 실행되지 않았거나 실패했다면 완료로 표시하지 않습니다.
5. 변경 단위를 작게 commit하고 reviewer가 재현할 수 있는 test 결과를 남깁니다.

IDE 채팅의 diff 검토는 코드 리뷰를 돕지만, branch protection, PR review, CI 같은 팀 통제를 대신하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 작업 위임

빠른 수정은 local IDE에서 처리하고, 넓은 조사나 장시간 작업은 cloud 또는 subagent에 위임한 뒤 결과를 편집기에서 검토합니다. 위임 요청에는 완료 기준과 파일 소유권을 명시합니다. 같은 파일을 여러 작업에 동시에 쓰기 권한으로 맡기지 않습니다.

IDE와 CLI를 병행할 때는 둘 다 같은 working tree에서 수정 중인지 먼저 확인합니다. 병렬 쓰기가 필요하면 Git worktree로 작업공간을 분리하고, 하나의 branch에 통합하기 전에 diff와 test를 다시 실행합니다.

## 참고 자료

- OpenAI Codex IDE extension: [learn.chatgpt.com/docs/codex/ide](https://learn.chatgpt.com/docs/codex/ide)
- OpenAI Codex 권한: [learn.chatgpt.com/docs/permissions](https://learn.chatgpt.com/docs/permissions)

---

**작성일**: 2026-09-22

**마지막 업데이트**: 2026-09-22

© 2026 siasia86. Licensed under CC BY 4.0.

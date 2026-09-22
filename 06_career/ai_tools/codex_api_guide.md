# Codex API와 자동화 가이드

Codex를 CI, 반복 작업, 내부 도구에 연결할 때 `codex exec`, Codex SDK, app-server의 역할을 구분하고 안전한 자동화 경계를 설계하는 가이드입니다.

## 목차

| 섹션                                                                                                                                |
|-------------------------------------------------------------------------------------------------------------------------------------|
| [1. 통합 방식 선택](#1-통합-방식-선택) / [2. 비대화형 CLI 자동화](#2-비대화형-cli-자동화)                                           |
| [3. Codex SDK](#3-codex-sdk) / [4. app-server](#4-app-server) / [5. 인증·비용·보안](#5-인증비용보안) / [6. 운영 검증](#6-운영-검증) |

---

## 1. 통합 방식 선택

API라는 말은 일반 OpenAI API 호출과 Codex 실행 통합을 모두 가리킬 수 있습니다. 작업에 맞는 경계를 먼저 고릅니다.

- `codex exec`: shell, CI job, scheduler에서 한 번의 Codex 작업을 실행할 때 사용합니다. 대화 상태·승인 UI를 세밀하게 제어해야 하는 제품에는 적합하지 않습니다.
- Codex SDK: 애플리케이션에서 Codex 작업을 만들고 event를 수집할 때 사용합니다. 단순 텍스트 생성만 필요한 경량 API 호출에는 적합하지 않을 수 있습니다.
- app-server: Codex와 깊게 통합한 client의 인증·대화·승인을 처리할 때 사용합니다. 일반 CI 자동화에는 적합하지 않습니다.
- Responses API: 모델을 직접 호출하는 제품 기능과 구조화된 출력에 사용합니다. Codex의 로컬 도구 실행 흐름이 필요한 자동화에는 적합하지 않습니다.

CI에서 repository를 분석·수정·검증하는 반복 작업은 보통 `codex exec` 또는 Codex SDK로 시작합니다. app-server는 client 제품이 Codex의 session, approval, event stream을 직접 다뤄야 할 때 선택합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 비대화형 CLI 자동화

`codex exec`는 interactive TUI 없이 한 작업을 실행하는 CLI 경로입니다. 자동화 요청은 목표·입력·출력·권한·성공 조건을 고정합니다.

```bash
codex exec --sandbox read-only --ask-for-approval on-request \
  "변경하지 말고 현재 branch의 Markdown 링크 오류를 찾아 파일별로 보고해"
```

CI에는 다음 통제를 함께 둡니다.

- 작업마다 최소 sandbox와 승인 정책을 명시합니다.
- 실행 가능한 repository code와 credential을 같은 신뢰 경계로 보지 않습니다.
- 진행 이벤트와 최종 출력의 보관 기간·마스킹 정책을 정합니다.
- 수정 작업은 diff, test, reviewer 또는 PR 단계를 거친 뒤에만 병합·배포합니다.
- 재시도 가능한 분석과 비가역 변경 작업을 분리합니다.

`--json` 출력은 event를 수집하는 자동화에 적합하지만, 로그에 비밀정보나 원문 source가 남지 않도록 downstream 저장소도 검토합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. Codex SDK

Codex SDK는 프로그램에서 Codex 작업을 시작하고 결과·이벤트를 통합할 때 사용합니다. SDK를 도입하기 전에는 다음 계약을 정합니다.

1. 입력: repository, prompt, 허용 도구, 파일과 네트워크 범위를 정의합니다.
2. 실행: timeout, 취소, 재시도, 동시 실행 수를 제한합니다.
3. 출력: event와 최종 결과를 구분하고, 사용자에게 보여 줄 정보만 선택합니다.
4. 검증: Codex 결과를 deployment 권한으로 바로 연결하지 않고 test·review gate를 둡니다.
5. 관측: 실행 ID, 모델·설정, 비용·실패 원인을 민감정보 없이 기록합니다.

최신 SDK 설치 방법, 언어별 API와 event 모델은 [공식 Codex SDK 문서](https://learn.chatgpt.com/docs/codex-sdk)를 기준으로 구현합니다. SDK 예제의 권한과 timeout을 운영 환경에 그대로 복사하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. app-server

app-server는 Codex 기반 client가 인증, conversation history, approval, agent event streaming 같은 고급 기능을 통합할 때 사용하는 프로토콜입니다. CI에서 명령 한 번을 실행하는 목적이라면 app-server보다 Codex SDK 또는 `codex exec`가 단순합니다.

app-server를 선택했다면 client가 다음 책임을 진다는 점을 명확히 합니다.

- 사용자와 service account 인증 수명주기
- tool approval UI와 감사 기록
- 대화·이벤트의 저장, 삭제, 재개 정책
- 로컬·원격 환경 연결과 네트워크 경계
- protocol 및 Codex version 호환성 검증

정식 protocol, 지원 capability, remote TUI 연결 방식은 [공식 app-server 문서](https://learn.chatgpt.com/docs/app-server)를 기준으로 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 인증·비용·보안

ChatGPT 로그인 사용량과 OpenAI Platform API 과금은 다른 체계입니다. CI·서비스 자동화에는 개인 브라우저 로그인이나 로컬 `auth.json`을 복사하지 않고, 조직의 Platform project와 최소 권한 service credential을 사용합니다.

API key와 access token은 secret manager 또는 workload identity로 job 실행 시점에만 주입합니다. repository, artifact, shell history, error log에 credential이 남지 않는지 검사하고, 정기적으로 폐기·교체 절차를 검증합니다.

사용량은 Platform의 project별 비용·rate limit·budget 정책으로 관리합니다. 모델, 입력 크기, reasoning 설정, 병렬 작업 수, 재시도 횟수가 비용과 처리량에 영향을 주므로 상한과 alert를 설정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 운영 검증

자동화는 다음 순서로 작은 범위에서 검증한 뒤 확장합니다.

1. 읽기 전용 sandbox에서 fixture repository를 분석합니다.
2. 예상 event와 오류 출력을 contract test로 확인합니다.
3. 임시 branch 또는 worktree에서 수정과 test 실행을 검증합니다.
4. PR 생성, artifact 업로드, 배포처럼 외부 상태를 바꾸는 단계를 분리합니다.
5. timeout, rate limit, credential 만료, tool failure를 강제로 재현해 실패 처리를 확인합니다.
6. audit log, 비용, 성공률, rollback 경로를 운영 runbook에 기록합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- OpenAI Codex SDK: [learn.chatgpt.com/docs/codex-sdk](https://learn.chatgpt.com/docs/codex-sdk) — ★★★☆☆
- OpenAI Codex app-server: [learn.chatgpt.com/docs/app-server](https://learn.chatgpt.com/docs/app-server) — ★★★☆☆
- OpenAI Codex CLI: [learn.chatgpt.com/docs/codex/cli](https://learn.chatgpt.com/docs/codex/cli) — ★★★☆☆
- OpenAI API Quickstart: [developers.openai.com/api/docs/quickstart](https://developers.openai.com/api/docs/quickstart) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-09-22

**마지막 업데이트**: 2026-09-22

© 2026 siasia86. Licensed under CC BY 4.0.

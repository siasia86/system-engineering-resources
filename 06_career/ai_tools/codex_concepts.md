# Codex 공통 개념과 작업 설계

Codex를 CLI(TUI), ChatGPT GUI, IDE, API 중 어떤 경로로 사용할지 판단하고, 모든 경로에 공통으로 적용하는 권한·컨텍스트·검증 원칙을 정리합니다.

## 목차

- [1. 문서와 진입점 선택](#1-문서와-진입점-선택)
- [2. 작업 단위와 컨텍스트](#2-작업-단위와-컨텍스트)
- [3. 권한·인증·비용 경계](#3-권한인증비용-경계)
- [4. 안전한 작업 흐름](#4-안전한-작업-흐름)
- [5. 확장 기능](#5-확장-기능)

---

## 1. 문서와 진입점 선택

Codex는 같은 목표를 여러 인터페이스에서 수행할 수 있습니다. 작업 위치와 자동화 필요 여부에 따라 진입점을 고릅니다.

- CLI/TUI: 로컬 저장소 탐색·수정·테스트와 shell 중심 작업에는 [CLI Linux 가이드](codex_cli_linux_guide.md)를 사용합니다.
- GUI: 브라우저·데스크톱에서 계획·조사·장시간 작업을 관리할 때는 [GUI 가이드](codex_gui_guide.md)를 사용합니다.
- IDE: 열린 파일·선택 코드 중심의 짧은 수정과 리뷰에는 [IDE 가이드](codex_ide_guide.md)를 사용합니다.
- API: CI, 반복 자동화, 제품 또는 내부 도구 통합에는 [API·자동화 가이드](codex_api_guide.md)를 사용합니다.

한 작업의 시작점이 결과 검토 위치를 제한하지는 않습니다. 예를 들어 IDE에서 작은 수정안을 검토하고, CLI에서 전체 테스트를 실행하며, 장시간 작업은 GUI 또는 cloud 환경으로 넘길 수 있습니다. 다만 같은 파일을 여러 세션에서 동시에 수정하지 않도록 작업 소유자를 하나로 정합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 작업 단위와 컨텍스트

Codex는 현재 대화, 첨부한 파일, 열어 둔 코드, 허용된 작업공간을 바탕으로 작업합니다. 필요한 정보만 제공하고, 오래 걸리는 작업은 재개 가능한 단위로 나눕니다.

- 목표: 완료 상태를 한 문장으로 정의합니다.
- 범위: 수정 가능한 디렉토리·파일과 수정하지 않을 영역을 지정합니다.
- 제약: 호환성, 보안, 배포 정책, 비밀정보 금지를 명시합니다.
- 검증: 실행할 test·lint·review와 성공 기준을 지정합니다.
- 인수: 변경 파일, 검증 결과, 남은 위험과 rollback 방법을 요청합니다.

`AGENTS.md`는 반복되는 저장소 규칙을 전달하는 수단이고, skills와 MCP는 재사용 가능한 절차·외부 도구 연결 수단입니다. 지침과 도구는 필요한 범위에서만 활성화하며, 외부 MCP에는 전달 데이터와 실행 권한을 먼저 확인합니다.

대화가 길어지면 완료한 결정, 변경 파일, 실행한 검증, 남은 작업을 요약한 뒤 context를 정리합니다. 요약은 기록을 대체하지 않으므로 중요한 운영 결정은 issue, PR 또는 저장소 문서에 남깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 권한·인증·비용 경계

권한, 인증, 과금은 별개입니다. 파일을 수정할 수 있다고 API 비용이 승인되는 것은 아니며, ChatGPT 로그인으로 작업한다고 CI에서 같은 자격증명을 사용해도 되는 것도 아닙니다.

- 권한: 필요한 파일·명령·네트워크 접근을 확인하고, 읽기 전용 분석 후 필요한 범위만 쓰기 권한을 부여합니다.
- ChatGPT 로그인: 대화형 Codex 사용량과 계정 정책을 확인하고, 개인·조직 정책과 Usage Dashboard를 기준으로 판단합니다.
- API 인증: 자동화가 Platform project·service account를 사용해야 하는지 확인하고, 비밀은 CI secret 또는 workload identity로 실행 때만 주입합니다.
- 비용: ChatGPT 플랜 사용량과 OpenAI Platform API 과금을 서로 대신한다고 가정하지 않습니다.

API key, access token, `auth.json`, SSH key, cloud credential을 프롬프트·문서·로그·commit에 넣지 않습니다. 자동화에는 최소 권한 credential과 격리된 runner를 사용하고, 배포 권한은 Codex 실행 권한과 분리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 안전한 작업 흐름

1. `git status`와 기존 문서를 확인해 현재 변경과 규칙을 파악합니다.
2. 분석 단계에서는 읽기 전용으로 영향 범위와 검증 계획을 확인합니다.
3. 수정 단계에서는 writable root와 명령 권한을 작업 범위로 한정합니다.
4. 결과는 `git diff`로 검토하고, 프로젝트의 test·lint·보안 검사를 직접 실행합니다.
5. commit 또는 PR 전에 변경 목적, 검증 결과, 알려진 제한을 기록합니다.
6. 실패하면 전체 변경을 자동으로 되돌리지 말고 diff와 로그를 확인해 필요한 범위만 rollback합니다.

subagent 병렬 작업은 독립적인 조사·리뷰·테스트 분석에 적합합니다. 각 subagent는 별도의 context와 모델·도구 호출을 사용하므로 총 사용량은 늘 수 있습니다. 동일 파일 수정은 한 agent에 맡기고, 나머지는 읽기 중심으로 분리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 확장 기능

- `AGENTS.md`: 사용자·저장소·하위 디렉토리의 지속 지침을 계층적으로 적용합니다.
- Skills: 특정 작업의 절차와 참고 자료를 묶어 재사용합니다.
- MCP: Codex에 외부 도구·데이터를 연결합니다. 서버별 권한과 데이터 흐름을 검토합니다.
- Subagents: 큰 작업을 독립된 분석 단위로 나누고 결과를 주 agent가 통합합니다.
- Git worktree: 여러 쓰기 작업을 병렬로 수행해야 할 때 파일 충돌을 줄이는 격리 수단입니다.

기능의 표시 여부와 세부 동작은 Codex 버전, 계정, 조직 관리 정책에 따라 달라질 수 있습니다. 실제 세션에서는 `/status`, `/permissions`, `/model`, `/agent`와 해당 UI의 설정 화면으로 적용 상태를 확인합니다.

## 참고 자료

- OpenAI Codex CLI: [learn.chatgpt.com/docs/codex/cli](https://learn.chatgpt.com/docs/codex/cli)
- OpenAI Codex 설정: [learn.chatgpt.com/docs/configuration](https://learn.chatgpt.com/docs/configuration)
- OpenAI Codex 권한: [learn.chatgpt.com/docs/permissions](https://learn.chatgpt.com/docs/permissions)
- OpenAI Codex subagents: [learn.chatgpt.com/docs/agent-configuration/subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

---

**작성일**: 2026-09-22

**마지막 업데이트**: 2026-09-22

© 2026 siasia86. Licensed under CC BY 4.0.

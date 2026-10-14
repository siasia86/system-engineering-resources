# Claude Code 공통 개념과 사용 흐름
<!-- reference: _reference/claude_code_official_notes.md -->

Claude Code는 코드베이스를 읽고 파일을 수정하며, 명령과 테스트를 실행하고 개발 도구와 연동하는 Anthropic의 코딩 에이전트입니다. 사용자는 원하는 결과를 설명하고, Claude Code는 필요한 파일을 찾고 변경하고 검증합니다.

이 문서는 Claude Code를 처음 접하는 사람이 **무엇을 맡길 수 있는지, 어디서 실행되는지, 권한과 비용을 어떻게 다루는지** 이해하기 위한 입문 문서입니다. 설치와 명령은 [Linux CLI 가이드](claude_code_cli_linux_guide.md), 지침 파일·Skills·Hooks·MCP는 [확장 기능 가이드](claude_code_extensions_guide.md), 모델 선택은 [모델 가이드](claude_models_guide.md)에서 다룹니다.

## 목차

| 섹션                                                                                          |
|-----------------------------------------------------------------------------------------------|
| [1. 모델·에이전트·도구](#1-모델에이전트도구) / [2. 사용 환경](#2-사용-환경)                   |
| [3. 작업이 진행되는 과정](#3-작업이-진행되는-과정) / [4. 컨텍스트와 지침](#4-컨텍스트와-지침) |
| [5. 권한 모드](#5-권한-모드) / [6. 계정과 비용](#6-계정과-비용)                               |
| [7. Codex와 비교](#7-codex와-비교) / [8. 추천 학습 순서](#8-추천-학습-순서)                   |

---

## 1. 모델·에이전트·도구

Claude Code는 판단하는 **모델**, 작업을 이어가는 **에이전트**, 실제 행동을 하는 **도구**로 나눠 보면 이해하기 쉽습니다.

| 구성 요소 | 역할                                           | 예시                                          |
|-----------|------------------------------------------------|-----------------------------------------------|
| 모델      | 요청을 이해하고 다음 행동을 결정               | Claude Opus 5.5, Sonnet 5.5, Haiku 5.5        |
| 에이전트  | 도구 실행 결과를 보고 다음 단계를 반복         | 수정 → 테스트 → 실패 원인 확인 → 재수정       |
| 도구      | 파일 읽기·편집, 셸 명령, 검색, 웹 조회 등 실행 | `Read`, `Edit`, `Bash`, `Grep`, MCP 서버 도구 |

모델이 바로 파일을 바꾸는 것이 아니라, 에이전트가 도구 호출을 요청하고 Claude Code가 권한 규칙에 따라 실행 여부를 결정합니다. 그래서 같은 모델이라도 권한 모드와 설정에 따라 할 수 있는 일이 달라집니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 사용 환경

| 환경      | 실행 위치          | 적합한 작업                                     |
|-----------|--------------------|-------------------------------------------------|
| CLI       | 내 컴퓨터·서버     | 터미널 작업, 원격 서버, 스크립트, 전체 기능     |
| Desktop   | 내 컴퓨터          | diff 시각 검토, 여러 세션 병렬 실행, 예약 작업  |
| VS Code   | 내 컴퓨터          | 편집기 안에서 inline diff로 검토                |
| JetBrains | 내 컴퓨터          | IntelliJ·PyCharm 등에서 diff 검토               |
| Web       | Anthropic 클라우드 | 오래 걸리고 개입이 적은 작업, 접속 종료 후 계속 |
| Mobile    | 클라우드·원격 연결 | 이동 중 작업 시작·상태 확인                     |

- 로컬 환경(CLI·Desktop·IDE)은 내 파일과 자격 증명에 직접 접근합니다. 권한 모드 선택이 중요합니다.
- Web은 클라우드 VM에서 저장소를 받아 작업하므로 내 컴퓨터를 꺼도 진행됩니다.
- Desktop 앱에는 Claude Code가 포함되어 있어 CLI를 따로 설치하지 않아도 됩니다.
- GitHub Actions·GitLab CI/CD·Slack·Chrome 연동으로 PR 리뷰, 이슈 처리, 브라우저 테스트도 맡길 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 작업이 진행되는 과정

예를 들어 "로그 정리 스크립트가 공백이 있는 경로에서 실패한다, 고쳐 달라"고 요청하면 다음 순서로 진행됩니다.

```text
요청
  ↓
탐색: 관련 파일 검색·읽기 (Grep, Read)
  ↓
계획: 원인 추정, 수정 범위 결정 (plan 모드면 여기서 승인 대기)
  ↓
수정: 파일 편집 (Edit) ── 권한 모드에 따라 승인 요청
  ↓
검증: 테스트·재현 명령 실행 (Bash)
  ↓
실패하면 원인 확인 후 수정 단계로 반복
  ↓
결과 요약: 변경 파일, 검증 결과, 남은 문제
```

- 결과를 받으면 변경된 diff와 실행한 검증 명령을 직접 확인합니다.
- 작업이 길어지면 대화 기록이 요약(compaction)되어 앞부분 세부 내용이 줄어들 수 있습니다. 중요한 결정은 지침 파일이나 작업 문서에 남깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 컨텍스트와 지침

Claude Code는 세션을 시작할 때 다음 내용을 자동으로 읽어 작업 기준으로 삼습니다.

| 종류            | 위치                                     | 내용                                    |
|-----------------|------------------------------------------|-----------------------------------------|
| 프로젝트 지침   | `./CLAUDE.md` 또는 `./.claude/CLAUDE.md` | 구조, 코딩 규칙, 검증 명령 (팀 공유)    |
| 개인 지침       | `~/.claude/CLAUDE.md`                    | 모든 프로젝트에 적용할 개인 선호        |
| 개인 프로젝트용 | `./CLAUDE.local.md`                      | 이 프로젝트에서만 쓰는 개인 설정        |
| `AGENTS.md`     | 프로젝트 루트                            | `CLAUDE.md`가 없을 때 프로젝트 지침으로 |
| Auto memory     | 저장소별 메모리                          | Claude가 기록한 선호·교정 내용          |

- 이 저장소처럼 `AGENTS.md`만 있는 경우 Claude Code는 `AGENTS.md`를 프로젝트 지침으로 읽습니다. `CLAUDE.md`를 새로 만들면 `AGENTS.md`는 읽지 않으므로, 둘 다 쓰려면 `CLAUDE.md`에서 `AGENTS.md`를 import합니다.
- 요청에는 목표, 수정 범위, 완료 확인 방법을 함께 적습니다. 예: "`scripts/cleanup.sh`만 수정하고, 공백 포함 경로로 재현 명령을 실행해 확인".

[⬆ 목차로 돌아가기](#목차)

---

## 5. 권한 모드

권한 모드는 Claude가 묻지 않고 실행할 수 있는 범위를 정합니다.

| 모드                | 묻지 않고 실행                            | 언제 쓰나                   |
|---------------------|-------------------------------------------|-----------------------------|
| `default` (Manual)  | 읽기만                                    | 민감한 작업, 처음 보는 코드 |
| `acceptEdits`       | 읽기, 파일 편집, 기본 파일 명령           | 검토하면서 반복 수정        |
| `plan`              | 읽기 (편집은 계획 승인 후)                | 변경 전 분석·설계           |
| `auto`              | 전부, 별도 분류기 모델이 위험 작업을 점검 | 긴 작업, 승인 피로 줄이기   |
| `dontAsk`           | 사전 허용한 도구만, 나머지는 거부         | 허용 목록이 고정된 CI       |
| `bypassPermissions` | 전부                                      | 격리된 컨테이너·VM에서만    |

- v2.1.283 이상에서는 대화형 터미널·VS Code 세션이 기본으로 `auto` 모드로 시작합니다. 운영 서버처럼 민감한 환경에서는 `--permission-mode default`로 시작하거나 설정 파일에 기본 모드를 지정합니다.
- 세션 중에는 `Shift+Tab`으로 모드를 바꿉니다.
- `bypassPermissions`는 모든 확인을 끄므로 격리 환경이 아니면 사용하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 계정과 비용

| 사용 방식                    | 과금                              | 비고                                |
|------------------------------|-----------------------------------|-------------------------------------|
| Pro·Max 구독                 | 월 구독료, 사용량 한도 공유       | 채팅과 Claude Code가 같은 한도 사용 |
| Team·Enterprise              | 좌석 요금 (+ Enterprise는 사용량) | 조직 관리, managed settings         |
| Claude Console API 키        | 토큰 종량제                       | CI·스크립트, 사용량 기반 정산       |
| Bedrock·Google Cloud·Foundry | 각 클라우드 요금                  | 조직 클라우드 계정 사용             |

- 무료 플랜에는 Claude Code가 포함되지 않습니다.
- 구독 사용량 한도는 5시간 단위로 초기화되고, 유료 플랜은 주간 한도도 있습니다.
- 구독으로 로그인했는데 `ANTHROPIC_API_KEY` 환경 변수도 있으면, 승인 후 API 키가 우선 사용되어 종량제로 과금될 수 있습니다. `/status`로 현재 인증 방식을 확인합니다.
- 공식 문서 기준 기업 배포 평균은 활성일 개발자당 약 $13, 월 $150~250입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. Codex와 비교

| 항목           | Claude Code                                   | Codex                |
|----------------|-----------------------------------------------|----------------------|
| 제공사         | Anthropic                                     | OpenAI               |
| 프로젝트 지침  | `CLAUDE.md` (없으면 `AGENTS.md`)              | `AGENTS.md`          |
| 반복 작업 정의 | Skills (`.claude/skills/`, Agent Skills 표준) | Skills               |
| 이벤트 자동화  | Hooks (30여 종 이벤트)                        | Hooks                |
| 하위 에이전트  | Subagents (`.claude/agents/`)                 | Subagents            |
| 권한 제어      | 권한 모드 6종 + 허용·거부 규칙 + 샌드박스     | 승인 정책 + 샌드박스 |
| 구독           | Claude Pro·Max·Team·Enterprise                | ChatGPT 플랜         |

같은 저장소에서 두 도구를 함께 쓰려면 공통 규칙은 `AGENTS.md`에 두고, Claude 전용 내용만 `CLAUDE.md`에 적은 뒤 `AGENTS.md`를 import하는 방식이 관리하기 쉽습니다. Codex 쪽 개념은 [Codex 공통 개념](../codex/codex_concepts.md)을 참고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 추천 학습 순서

1. 이 문서로 구성 요소와 권한 모드를 이해합니다.
2. [Linux CLI 가이드](claude_code_cli_linux_guide.md)로 설치·로그인하고 `plan` 모드로 작은 저장소를 분석해 봅니다.
3. [확장 기능 가이드](claude_code_extensions_guide.md)로 `CLAUDE.md`와 프로젝트 설정을 만듭니다.
4. 반복 작업을 Skills·Hooks로 고정합니다.
5. [모델 가이드](claude_models_guide.md)로 작업별 모델과 effort를 조정합니다.
6. CI에서는 `claude -p`와 `dontAsk` 모드로 허용 범위를 좁혀 자동화합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [_reference/claude_code_official_notes.md](../../../_reference/claude_code_official_notes.md) — 버전·모델·권한·설정 검증 근거 노트
- Claude Code Overview: [code.claude.com/docs/en/overview](https://code.claude.com/docs/en/overview) — ★★★☆☆
- How Claude Code works: [code.claude.com/docs/en/how-claude-code-works](https://code.claude.com/docs/en/how-claude-code-works) — ★★★☆☆
- Platforms: [code.claude.com/docs/en/platforms](https://code.claude.com/docs/en/platforms) — ★★★☆☆
- Permission modes: [code.claude.com/docs/en/permission-modes](https://code.claude.com/docs/en/permission-modes) — ★★★☆☆
- Memory: [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory) — ★★★☆☆
- Pricing: [claude.com/pricing](https://claude.com/pricing) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-10-14

**마지막 업데이트**: 2026-10-14

© 2026 siasia86. Licensed under CC BY 4.0.

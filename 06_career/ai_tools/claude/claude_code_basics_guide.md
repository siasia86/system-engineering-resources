# Claude Code 기본 사용법
<!-- reference: _reference/claude_code_official_notes.md -->

Claude Code를 설치한 뒤 매일 쓰는 흐름을 정리합니다. 첫 세션 시작, 요청 작성, plan 모드, 파일 지정, 컨텍스트 관리, 세션 재개와 되돌리기, 변경 검토를 다룹니다. 설치와 인증은 [Linux CLI 가이드](claude_code_cli_linux_guide.md), 구성 요소와 권한 모드의 개념은 [Claude Code 공통 개념](claude_code_concepts.md)을 참고합니다.

🟡 명령과 단축키는 2026-10-15 공식 문서 기준입니다. 이 서버에서는 Claude Code 2.1.295로 `--version`만 실행해 확인했고, 단축키 동작은 다시 시험하지 않았습니다.

## 목차

| 단계 | 섹션                                                                                                     |
|------|----------------------------------------------------------------------------------------------------------|
| 시작 | [1. 첫 세션 시작](#1-첫-세션-시작) / [2. 요청 작성법](#2-요청-작성법) / [3. plan 모드](#3-plan-모드)     |
| 입력 | [4. 파일 지정과 셸 명령](#4-파일-지정과-셸-명령) / [5. 작업 중 개입](#5-작업-중-개입)                    |
| 관리 | [6. 컨텍스트 관리](#6-컨텍스트-관리) / [7. 세션 재개](#7-세션-재개) / [8. 되돌리기](#8-되돌리기)         |
| 확인 | [9. 변경 검토](#9-변경-검토) / [10. 자주 하는 실수](#10-자주-하는-실수) / [11. 빠른 참조](#11-빠른-참조) |

---

## 1. 첫 세션 시작

작업할 저장소로 이동한 뒤 `claude`를 실행합니다. 세션은 시작한 디렉터리를 작업 범위로 삼고, 그 위치의 `CLAUDE.md`(없으면 `AGENTS.md`)를 읽습니다.

```bash
cd ~/project
git status                       # 기존 변경을 먼저 확인
claude --permission-mode plan    # 처음 보는 저장소는 분석 전용으로 시작
```

처음에는 수정 없이 질문부터 합니다.

```text
이 저장소의 구조와 주요 진입점을 설명해 줘
테스트는 어떤 명령으로 실행해?
```

- 프로젝트 지침이 없으면 `/init`으로 `CLAUDE.md` 초안을 만들고 직접 검토합니다.
- 상태 확인은 `/status`(버전·모델·계정), 도움말은 `/help`, 단축키 목록은 빈 입력에서 `?`입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 요청 작성법

좋은 요청에는 **대상·범위·완료 확인 방법**이 들어 있습니다. Claude는 일이 끝나 보이면 멈추므로, 스스로 실행할 수 있는 검사를 주면 결과가 안정됩니다.

| 나쁜 예            | 좋은 예                                                                                               |
|--------------------|-------------------------------------------------------------------------------------------------------|
| 로그인 버그 고쳐   | 세션 만료 후 로그인이 실패한다. `src/auth/`의 token 갱신을 확인하고, 재현 테스트를 먼저 쓴 뒤 고쳐 줘 |
| foo.py 테스트 추가 | 로그아웃 상태 경우를 다루는 `foo.py` 테스트를 써 줘. mock은 쓰지 말고 작성 후 테스트를 실행해         |
| 빌드가 실패해      | 이 오류로 빌드가 실패한다: (오류 붙여넣기). 오류를 숨기지 말고 원인을 고친 뒤 빌드 성공을 확인해      |

- 기존 코드의 예시 파일을 지목하면 같은 패턴을 따릅니다. 예: "`HotDogWidget.php`를 참고해 같은 방식으로".
- 성공 주장 대신 **증거**를 요청합니다. 실행한 명령, 종료 코드, 테스트 출력을 보고하게 합니다.
- 범위가 넓은 조사는 "subagent로 조사해 줘"처럼 맡기면 하위 에이전트가 별도 컨텍스트에서 읽고 요약만 돌려줍니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. plan 모드

plan 모드에서 Claude는 파일을 읽고 탐색 명령을 실행해 계획을 쓰지만, 계획을 승인하기 전에는 소스를 수정하지 않습니다. 변경 범위가 크거나 처음 보는 코드일 때 씁니다.

| 들어가는 방법                   | 설명                                               |
|---------------------------------|----------------------------------------------------|
| `claude --permission-mode plan` | plan 모드로 세션 시작                              |
| `Shift+Tab` 반복                | 상태 줄에 `⏸ plan mode on`이 보일 때까지 모드 순환 |
| `/plan 작업 설명`               | 한 요청만 plan 모드로 바로 시작                    |

계획이 준비되면 진행 방법을 고릅니다.

- **Yes, and use auto mode**: 승인 후 auto 모드로 진행 (auto 모드를 쓸 수 없으면 **Yes, auto-accept edits**)
- **Yes, manually approve edits**: 승인 후 편집마다 확인
- **No, keep planning**: plan 모드에 남아 수정할 점을 알려 줌

권장 순서는 **탐색 → 계획 → 구현 → 검증**입니다. 계획 단계에서 범위와 검증 명령을 합의하면 엉뚱한 문제를 푸는 일을 줄일 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 파일 지정과 셸 명령

| 입력        | 동작                                                                    | 예시                                  |
|-------------|-------------------------------------------------------------------------|---------------------------------------|
| `@파일`     | 파일 내용을 대화에 바로 포함 (경로 자동 완성)                           | `@src/utils/auth.js 로직을 설명해 줘` |
| `@디렉터리` | 내용이 아닌 파일 목록을 포함                                            | `@src/components 구조를 알려 줘`      |
| `!명령`     | Claude를 거치지 않고 셸 명령 실행, 출력이 대화에 추가되고 Claude가 응답 | `! git status`                        |
| `/명령`     | 내장 명령 또는 skill 실행                                               | `/compact`, `/skills`                 |
| 이미지      | `Ctrl+V`(WSL은 `Alt+V`)로 붙여넣기                                      | 화면 캡처, 오류 화면                  |

- `@` 참조는 해당 파일 디렉터리와 상위 디렉터리의 `CLAUDE.md`도 함께 읽습니다.
- 256KB가 넘는 텍스트 파일은 `@`로 포함되지 않습니다. 큰 로그는 필요한 부분만 붙여넣거나 `-p`로 파이프합니다.
- `!` 셸 모드 명령은 샌드박스를 켜도 샌드박스 밖에서 실행됩니다. Claude가 실행하는 명령에만 샌드박스가 적용되기 때문입니다.
- 여러 줄 입력은 `\` + `Enter` 또는 `Ctrl+J`가 모든 터미널에서 동작합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 작업 중 개입

| 조작            | 동작                                                                           |
|-----------------|--------------------------------------------------------------------------------|
| `Esc`           | 진행 중인 응답·도구 실행 중단. 지금까지 한 작업은 유지되어 방향을 바꿀 수 있음 |
| 작업 중 `Enter` | 메시지를 대기열에 넣음. 도구 실행이 끝나면 같은 턴 안에서 전달                 |
| `Ctrl+B`        | 오래 걸리는 Bash 명령을 백그라운드로 보냄 (tmux는 두 번)                       |
| `/btw 질문`     | 대화 기록에 남기지 않고 지금까지의 내용으로 짧게 질문 (도구 사용 없음)         |
| `Ctrl+O`        | 도구 실행 상세 기록 보기                                                       |
| `Ctrl+C`        | 실행 중이면 중단, 입력만 있으면 지우기, 두 번 누르면 종료                      |

같은 문제를 두 번 넘게 바로잡아도 계속 틀리면, 실패한 시도가 컨텍스트를 어지럽힌 상태입니다. `/clear`로 새로 시작하고 알게 된 내용을 반영해 요청을 다시 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 컨텍스트 관리

컨텍스트는 Claude가 한 번에 볼 수 있는 대화·파일·명령 출력의 총량입니다. 가득 차면 성능이 떨어지고, 한도에 가까워지면 자동 요약(compaction)이 일어나 앞부분 세부 내용이 줄어듭니다.

| 명령                  | 용도                                                               |
|-----------------------|--------------------------------------------------------------------|
| `/context`            | 현재 컨텍스트 사용량을 격자로 보고 줄일 방법을 제안                |
| `/compact [지시]`     | 지금까지의 대화를 요약해 공간 확보. 예: `/compact API 변경 위주로` |
| `/clear [이름]`       | 빈 컨텍스트로 새 대화 시작. 이전 대화는 `/resume`으로 복귀 가능    |
| `/rewind` → Summarize | 선택한 지점 앞 또는 뒤만 부분 요약                                 |
| `/btw`                | 기록에 남지 않는 곁가지 질문                                       |

- 관련 없는 작업 사이에는 `/clear`를 씁니다. 한 세션에 여러 주제를 섞으면 컨텍스트가 빨리 찹니다.
- 요약 후에도 남겨야 할 내용은 `CLAUDE.md`에 적습니다. 예: "요약할 때 수정한 파일 목록과 테스트 명령은 항상 유지".
- 중요한 결정·검증 결과는 대화에만 두지 말고 작업 문서나 commit에 남깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 세션 재개

대화는 로컬에 저장되므로 다음 날에도 같은 맥락에서 이어갈 수 있습니다.

```bash
claude -c              # 현재 디렉터리의 가장 최근 세션 이어가기 (--continue)
claude -r              # 목록에서 골라 재개 (--resume)
claude -r oauth-migration   # 이름이나 ID로 재개
```

| 세션 안 명령     | 용도                                                      |
|------------------|-----------------------------------------------------------|
| `/rename 이름`   | 세션 이름 지정. 작업 흐름마다 이름을 붙이면 찾기 쉬움     |
| `/resume`        | 다른 세션으로 전환                                        |
| `/branch [이름]` | 현재 지점에서 대화를 분기해 다른 방향을 시도. 원본은 보존 |
| `/recap`         | 지금까지의 세션을 한 줄로 요약                            |

같은 저장소에서 두 작업을 동시에 하려면 `claude --worktree 이름`으로 git worktree를 따로 만들어 편집 충돌을 피합니다. 저장소에 commit이 하나 이상 있어야 합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 되돌리기

요청을 보낼 때마다 checkpoint가 만들어집니다. `/rewind` 또는 빈 입력에서 `Esc`를 두 번 누르면 되돌리기 메뉴가 열립니다.

| 선택                          | 결과                                       |
|-------------------------------|--------------------------------------------|
| Restore code and conversation | 코드와 대화를 모두 그 시점으로             |
| Restore conversation          | 대화만 되돌리고 현재 코드는 유지           |
| Restore code                  | 파일 변경만 되돌리고 대화는 유지           |
| Summarize from here           | 그 지점 이후를 요약해 공간 확보            |
| Summarize up to here          | 그 지점 이전을 요약하고 이후는 그대로 유지 |

🟡 checkpoint는 Claude의 파일 편집 도구로 바꾼 내용만 추적합니다. 다음은 되돌릴 수 없으므로 Git으로 관리합니다.

- `rm`, `mv`, `cp`처럼 Bash 명령으로 바꾼 파일
- 대부분의 subagent 편집 (foreground로 실행한 fork skill 제외)
- 내가 직접 고친 파일, 다른 세션이 고친 파일
- symlink·hard link 경로

checkpoint 파일 사본은 기본으로 약 30일 뒤 정리됩니다. 장기 이력과 협업은 commit·branch로 남깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 변경 검토

`/diff`로 Claude가 지금까지 바꾼 내용과 아직 commit하지 않은 변경을 함께 봅니다. 파일 편집 후에는 턴(`T1`, `T2` …)별 변경도 고를 수 있습니다. 셸 명령으로 바꾼 파일은 턴별 보기에 나오지 않고 `Current`(작업 트리) 보기에만 나옵니다.

검토 순서는 다음을 권장합니다.

1. `/diff` 또는 `git diff`로 변경 파일과 범위를 확인합니다.
2. Claude가 보고한 검증 명령을 다시 보고, 필요하면 `! 명령`으로 직접 실행합니다.
3. 요청하지 않은 파일이 바뀌었으면 이유를 묻거나 되돌립니다.
4. commit·push는 범위를 확인한 뒤 직접 지시합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. 자주 하는 실수

| 실수                    | 증상                               | 해결                                      |
|-------------------------|------------------------------------|-------------------------------------------|
| 한 세션에 여러 주제     | 앞 작업의 내용이 섞여 답이 흐려짐  | 주제가 바뀌면 `/clear`                    |
| 같은 교정을 반복        | 실패한 시도가 쌓여 계속 틀림       | 두 번 실패하면 `/clear` 후 요청 재작성    |
| 지나치게 긴 `CLAUDE.md` | 중요한 규칙이 묻혀 지켜지지 않음   | 꼭 필요한 규칙만 남기고 나머지는 hook으로 |
| 검증 없이 받아들임      | 그럴듯하지만 경계 조건을 놓친 구현 | 테스트·스크립트·화면 비교로 확인          |
| 범위 없는 조사 요청     | 수백 개 파일을 읽어 컨텍스트 소진  | 범위를 좁히거나 subagent에 맡김           |

[⬆ 목차로 돌아가기](#목차)

---

## 11. 빠른 참조

| 키·명령            | 동작                    |
|--------------------|-------------------------|
| `Shift+Tab`        | 권한 모드 순환          |
| `Esc` / `Esc Esc`  | 중단 / 되돌리기 메뉴    |
| `Ctrl+R`           | 이전 입력 검색          |
| `Ctrl+G`           | 외부 편집기로 입력 작성 |
| `Ctrl+S`           | 입력 임시 보관·복원     |
| `Alt+P`            | 모델 전환               |
| `/model`·`/effort` | 모델·effort 변경        |
| `/usage`           | 세션 비용과 플랜 사용량 |
| `/exit`            | 종료                    |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [_reference/claude_code_official_notes.md](../../../_reference/claude_code_official_notes.md) — 버전·명령 검증 근거 노트
- Quickstart: [code.claude.com/docs/en/quickstart](https://code.claude.com/docs/en/quickstart) — ★★★☆☆
- Interactive mode: [code.claude.com/docs/en/interactive-mode](https://code.claude.com/docs/en/interactive-mode) — ★★★☆☆
- Common workflows: [code.claude.com/docs/en/common-workflows](https://code.claude.com/docs/en/common-workflows) — ★★★☆☆
- Best practices: [code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices) — ★★★☆☆
- Checkpointing: [code.claude.com/docs/en/checkpointing](https://code.claude.com/docs/en/checkpointing) — ★★★☆☆
- Commands: [code.claude.com/docs/en/commands](https://code.claude.com/docs/en/commands) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-10-15

**마지막 업데이트**: 2026-10-15

© 2026 siasia86. Licensed under CC BY 4.0.

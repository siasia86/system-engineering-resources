# Claude Code의 Code Mode
<!-- reference: _reference/claude_code_official_notes.md -->

Code Mode는 Claude가 도구를 하나씩 부르는 대신, 여러 도구 호출을 담은 JavaScript를 한 번에 써서 실행하게 하는 Claude Code의 실험 기능입니다. 이름이 비슷한 데스크톱 앱의 Code 탭, 권한 모드와는 다른 기능입니다. 이 문서는 이름 구분 → 동작 방식 → 쓰기 좋은 작업 → 요구 조건 → 켜고 끄기 → 권한과 보안 → 제한 → 문제 해결 순서로 정리합니다.

- 기준: 2026-11-26 공식 문서 [Code Mode](https://code.claude.com/docs/en/code-mode.md) 확인. Claude Code 최신판 v2.1.332(npm, 2026-11-26)
- 예제 시험: 미실행. Code Mode는 실험 기능이고 켜려면 사용자 설정을 바꿔야 해서 실행하지 않았습니다. 명령과 설정은 공식 문서와 대조했습니다

## 목차

| 섹션                                                                                                 |
|------------------------------------------------------------------------------------------------------|
| [1. 이름 구분](#1-이름-구분) / [2. 동작 방식](#2-동작-방식) / [3. 쓰기 좋은 작업](#3-쓰기-좋은-작업) |
| [4. 요구 조건](#4-요구-조건) / [5. 켜고 끄기](#5-켜고-끄기) / [6. 권한과 보안](#6-권한과-보안)       |
| [7. 제한](#7-제한) / [8. 트러블슈팅](#8-트러블슈팅)                                                  |

---

## 1. 이름 구분

"모드"나 "Code"가 들어간 이름이 여러 개라 헷갈리기 쉽습니다.

| 이름                | 무엇인가                                                      | 어디서                                 | 문서                                          |
|---------------------|---------------------------------------------------------------|----------------------------------------|-----------------------------------------------|
| Code Mode (이 문서) | 도구 호출을 JavaScript로 묶어 한 단계에 실행하는 실험 기능    | 터미널 `claude` 대화형 세션            | 이 문서                                       |
| Code 탭             | Claude 데스크톱 앱·claude.ai/code에서 Claude Code를 쓰는 화면 | 데스크톱 앱, 브라우저                  | [데스크톱 앱](./claude_code_desktop_guide.md) |
| 권한 모드           | 묻고 실행할지 정하는 방식(Manual·acceptEdits·plan·auto 등)    | 모든 Claude Code 화면                  | [공통 개념](./claude_code_concepts.md)        |
| plan 모드           | 권한 모드의 하나. 바꾸지 않고 계획만 세움                     | 모든 Claude Code 화면                  | [기본 사용법](./claude_code_basics_guide.md)  |
| fast mode           | `/fast`로 켜는 빠른 응답                                      | Claude Code                            | 공식 문서 Fast mode                           |
| Projects            | 관련 작업을 여러 클라우드 세션(스레드)으로 나눠 맡기는 기능   | claude.ai/code, 데스크톱 앱, 모바일 앱 | [Projects](./claude_code_projects.md)         |

- "Claude Code 모드"라는 말이 이 중 어느 것을 가리키는지는 문맥으로 정합니다. 공식 문서에서 "Code Mode"라는 이름을 쓰는 기능은 이 문서의 실험 기능 하나입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 동작 방식

| 구분          | Code Mode 끔                                                   | Code Mode 켬                                 |
|---------------|----------------------------------------------------------------|----------------------------------------------|
| 도구 호출     | Bash·Read·Edit 등을 하나씩 요청하고 결과를 읽은 뒤 다음을 정함 | JavaScript 한 덩어리 안에서 여러 호출을 실행 |
| 병렬          | 도구 호출 단위                                                 | 코드 안에서 명령을 동시에 실행               |
| 결과 전달     | 각 도구 결과 전체                                              | 코드가 고른 부분만 Claude에게 돌려줌         |
| 실행하는 도구 | 각 도구                                                        | `REPL` 도구가 코드를 실행                    |

공식 문서의 예(재시도 횟수를 3에서 5로 올리고 테스트):

```javascript
const files = await $`rg -l "function retryPolicy" src`.text();
const target = files.trim().split("\n")[0];
await edit(target, "maxAttempts: 3", "maxAttempts: 5");
({ edited: target, tests: $`npm test -- retryPolicy`.nothrow() });
```

- 대화 화면에는 코드가 아니라 실제 도구 호출(편집 diff 등)이 보입니다.
- 코드를 보려면 `Ctrl+O`로 대화 기록 보기(transcript viewer)를 열고 접혀 있는 **Code** 행을 펼칩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 쓰기 좋은 작업

| 맞는 작업                           | 이유                          |
|-------------------------------------|-------------------------------|
| 여러 파일에 같은 변경 반복          | 반복을 코드 한 번으로 처리    |
| 검색 결과를 걸러서 읽어야 하는 작업 | 걸러낸 결과만 Claude에게 전달 |
| 서로 독립인 명령 여러 개            | 코드 안에서 동시에 실행       |

공식 문서가 제안하는 첫 시험 요청: "Read every Markdown file in this project and list the links that point to local files that don't exist."

[⬆ 목차로 돌아가기](#목차)

---

## 4. 요구 조건

| 항목       | 조건                                                                                                                 |
|------------|----------------------------------------------------------------------------------------------------------------------|
| 판         | v2.1.323 이상(클라우드 제공자는 v2.1.331 이상). 두 배포 채널 모두                                                    |
| 계정       | Claude 구독, Console 계정, 또는 Amazon Bedrock·Google Cloud Agent Platform·Microsoft Foundry                         |
| 안 되는 곳 | gateway 경유, Claude for Government, HIPAA 구성·zero data retention 조직                                             |
| 모델       | Claude Opus 5.5, Sonnet 5.5, Haiku 5.5, Fable 5.2                                                                    |
| 화면       | 터미널의 대화형 `claude` 세션만. VS Code 패널, 데스크톱 앱, 클라우드 세션은 안 됨                                    |
| 설치       | 네이티브 빌드. Windows는 Git for Windows 필요                                                                        |
| 함께 쓸 때 | agent teams v2.1.326 이상, 도구 호출을 거는 mod v2.1.327 이상, OpenTelemetry 이벤트·지표 v2.1.329 이상, tracing은 끔 |

- `apiKeyHelper` 같은 일부 설정이 있으면 시작하지 않습니다(8절).
- 실험 기능이라 어느 판에서든 바뀌거나 없어질 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 켜고 끄기

```bash
claude --version                                  # v2.1.323 이상인지 확인
CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1 claude       # 이번 실행에서 켬
```

새 세션마다 켜려면 `~/.claude/settings.json`에 둡니다.

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_CODE_MODE": "1"
  }
}
```

- 처음 켜면 확인 질문에서 **Yes, turn on Code Mode**를 고릅니다. 다시 시작한 세션 위쪽에 `Code Mode (experimental) is on · this session can be resumed only with Code Mode on`이 보이면 켜진 것입니다.
- 이 변수는 프로젝트 설정 파일(`.claude/settings.json`)에서는 무시됩니다. clone한 저장소가 마음대로 켤 수 없게 하려는 것입니다.
- 끄기: 셸·`~/.claude/settings.json`·`--settings` 파일에서 변수를 지우거나 값을 `0`으로 둡니다. 한 곳이라도 `0`이면 다른 곳의 `1`보다 우선합니다.
- 조직에서 막기: managed settings의 `env`에 `"CLAUDE_CODE_EXPERIMENTAL_CODE_MODE": "0"`. managed settings로 켜는 것은 안 됩니다.
- subagent가 `tools` 목록을 가지면 `REPL`을 넣어야 그 subagent도 Code Mode를 씁니다(`tools: Read, Bash, REPL`).

[⬆ 목차로 돌아가기](#목차)

---

## 6. 권한과 보안

| 권한 모드               | 검사 방식                                                                         |
|-------------------------|-----------------------------------------------------------------------------------|
| auto                    | 분류기가 도구 호출 하나하나가 아니라 코드 한 덩어리를 실행 전에 검토              |
| bypassPermissions       | 코드가 처음부터 끝까지 묻지 않고 실행(어느 모드도 자동 승인하지 않는 동작은 제외) |
| 그 밖의 모드(Manual 등) | 그 모드에서 묻는 도구 호출마다 질문                                               |

- auto 분류기는 실행 중에 계산되는 값(검색 결과에서 나온 경로 등)을 보지 못합니다. 반드시 막아야 하는 호출은 `deny`·`ask` 권한 규칙이나 `PreToolUse` hook으로 둡니다. 규칙은 평소 도구 이름(`Bash` 등)으로 씁니다.
- 코드를 실행 전에 직접 보고 승인하려면 `"ask": ["REPL"]` 규칙을 둡니다.
- 셸 명령을 검사하는 hook은 명령의 각 부분을 확인해야 합니다. Code Mode에서는 `git push`가 `cd 'app' && git push` 형태로 hook에 들어올 수 있습니다.
- sandbox는 코드가 실행하는 셸 명령에만 적용됩니다. JavaScript 자체와 파일·웹·MCP 호출은 sandbox 밖에서 돕니다. 이것까지 격리하려면 Claude Code를 컨테이너·VM에서 실행합니다.
- 코드는 파일의 토큰 같은 값을 읽어 다른 호출에 넘길 수 있습니다. 결과를 가리려면 `REPL`에 거는 `PostToolUse` hook에서 `updatedToolOutput`으로 바꾼 사본을 돌려줍니다. OpenTelemetry로 보낼 때는 `OTEL_LOG_TOOL_DETAILS`를 켜지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 제한

| 항목              | 내용                                                                                                        |
|-------------------|-------------------------------------------------------------------------------------------------------------|
| 재개              | Code Mode 세션은 Code Mode를 켠 상태에서만 재개. 구독·Console로 실행한 세션은 클라우드 제공자에서 재개 불가 |
| 실행 시간         | 기다리는 코드는 10분에 멈춤. 백그라운드 코드는 최대 2시간(auto·bypassPermissions로 시작해야 함)             |
| 함께 못 쓰는 기능 | Remote Control, Claude in Chrome, computer use                                                              |
| 세션 옮기기       | 데스크톱 앱으로 옮기기, 백그라운드 세션으로 바꾸기, `/fork`로 백그라운드 사본 만들기 불가                   |
| hook              | `PreToolUse` hook이 끝나지 않으면 호출 거절, 다른 방식으로 실패하면 호출이 계속될 수 있음                   |

- 진행 중인 코드는 `Esc`로 멈춥니다. 응답이 끝난 뒤의 백그라운드 코드는 `/tasks`에서 골라 `x`로 멈춥니다. 멈춘 뒤에도 코드가 시작한 subagent·셸 명령·MCP 호출이 `/tasks`에 남아 있을 수 있습니다.
- `PreToolUse` hook이 실패했을 때 호출을 막으려면 `command`·`http` hook에 `"onFailure": "block"`을 둡니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 트러블슈팅

세션 위쪽에 `Code Mode (experimental) isn't available`이 나오면 같은 줄에 이유가 붙습니다. `/status`에도 보입니다.

| 이유에 들어 있는 문구                                      | 조치                                                                                            |
|------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| `it isn't open to your account yet`                        | v2.1.323 미만이면 업데이트. 그 이상이면 네트워크 확인 뒤 나중에 다시                            |
| `Anthropic has turned it off for now`                      | 업데이트하거나 나중에 다시                                                                      |
| `it isn't offered yet through a gateway or proxy`          | gateway 설정을 빼고 직접 연결(`HTTPS_PROXY`는 유지 가능)                                        |
| `it doesn't work with an API key helper`                   | `apiKeyHelper`, `ANTHROPIC_AUTH_TOKEN`, 사용자 인증 헤더를 빼고 로그인 또는 `ANTHROPIC_API_KEY` |
| `it only works with Opus 5.5, Sonnet 5.5 and later models` | 지원 모델의 전체 이름 지정(예 `--model claude-opus-5-5`)                                        |
| `it doesn't work in background jobs`                       | 전경에서 `--remote-control` 없이 시작                                                           |
| `your organization's settings don't allow it`              | 관리자에게 managed settings 확인                                                                |

- 아무 줄도 없으면 판(v2.1.323 이상)과 변수 값 `1`을 확인하고, 어딘가에 남은 `0`을 지웁니다.
- auto 모드에서 카운트다운 질문(`Claude Code will automatically block this request in 1:59 ...`)이 나오면 시간 안에 답합니다. 시간이 지나면 그 호출은 거절됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Claude Code 공통 개념](./claude_code_concepts.md) — 권한 모드
- [Claude Code 설정 파일](./claude_code_settings_guide.md) — `env`, managed settings, hook
- [Claude Code의 Projects](./claude_code_projects.md) — 여러 세션을 맡기는 기능

---

## 참고 자료

- Claude Code Docs: [Run tool calls from code with Code Mode](https://code.claude.com/docs/en/code-mode.md) — 2026-11-26 확인 — ★★★☆☆
- Claude Code Docs: [Choose a permission mode](https://code.claude.com/docs/en/permission-modes.md) · [Hooks reference](https://code.claude.com/docs/en/hooks.md) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-11-26

**마지막 업데이트**: 2026-11-26

© 2026 siasia86. Licensed under CC BY 4.0.

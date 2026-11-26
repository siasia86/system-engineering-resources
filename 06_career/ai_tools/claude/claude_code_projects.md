# Claude Code의 Projects
<!-- reference: _reference/claude_code_official_notes.md -->

Projects는 관련된 작업 흐름을 대화 하나에 맡기면, Claude가 작업마다 스레드(대부분 클라우드 세션)를 시작해 병렬로 진행하고 결과를 모아 주는 기능입니다. 저장소·지침·메모리를 모든 스레드가 함께 씁니다. 이 문서는 개념 → 언제 쓰나 → 구성 → 만들기 → 일 맡기기 → 공통 문맥 → 내 컴퓨터에서 실행 → 비용 → 다른 기능과 관계 → 제한 순서로 정리합니다.

- 기준: 2026-11-26 공식 문서 [Projects](https://code.claude.com/docs/en/claude-projects.md) 확인. Pro·Max·Ultra 공개 beta, 단계적 제공(Team·Enterprise 미제공)
- 예제 시험: 미실행. 화면 조작과 클라우드 스레드 실행은 하지 않았고 공식 문서와 대조했습니다. 데스크톱 앱 화면에서 쓰는 방법 요약은 [데스크톱 앱](./claude_code_desktop_guide.md) 8절에 있습니다

## 목차

| 섹션                                                                                                         |
|--------------------------------------------------------------------------------------------------------------|
| [1. 개념](#1-개념) / [2. 언제 쓰나](#2-언제-쓰나) / [3. 구성](#3-구성) / [4. 만들기](#4-만들기)              |
| [5. 일 맡기기](#5-일-맡기기) / [6. 공통 문맥](#6-공통-문맥) / [7. 내 컴퓨터에서 실행](#7-내-컴퓨터에서-실행) |
| [8. 사용량](#8-사용량) / [9. 다른 기능과 관계](#9-다른-기능과-관계) / [10. 제한](#10-제한)                   |

---

## 1. 개념

| 항목      | 내용                                                                          |
|-----------|-------------------------------------------------------------------------------|
| 하는 일   | 한 목표에 딸린 작업들을 Claude가 스레드로 나눠 시작·추적                      |
| 조정자    | 프로젝트 대화의 Claude. 받은 메시지를 답하거나 스레드로 보냄                  |
| 일꾼      | 스레드. 각자 컨텍스트를 가진 별도 세션, 끝나면 대화에 보고                    |
| 실행 위치 | 스레드는 기본으로 클라우드 세션. 요청하면 내 컴퓨터에서 Remote Control로 실행 |
| 사용 위치 | claude.ai/code, 데스크톱 앱 Code 탭, Claude 모바일 앱(iOS·Android)            |
| 제공 범위 | Pro·Max·Ultra 공개 beta, 단계적 제공. Team·Enterprise 미제공                  |
| 이름 주의 | claude.ai 채팅·Cowork의 예전 Projects(대화와 참고 파일 묶음)와 다른 기능      |

- 사이드바에 **Projects**가 없으면 **More** 아래를 봅니다. 그래도 없으면 아직 계정에 제공되지 않은 것입니다(대기 목록 신청 가능).
- 제공은 클라우드 세션을 써 본 계정, claude.ai 채팅·Cowork에 기존 프로젝트가 없는 계정부터 시작했습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 언제 쓰나

| 맞는 경우                  | 예                                                       |
|----------------------------|----------------------------------------------------------|
| 여러 저장소에 걸친 한 목표 | 모든 서비스에 새 lint 설정 적용(저장소마다 스레드·PR)    |
| 계속 들어오는 한 영역의 일 | 한 서비스의 버그·스택 트레이스·리뷰 요청을 그때그때 전달 |
| 세션 하나보다 큰 구축·이전 | 명세대로 구축, 오래된 ORM 걷어내기                       |
| 코드가 아닌 일             | 계약서 폴더·지원 티켓 내보내기 분석(파일 업로드)         |

| 다른 것이 나은 경우                  | 대신 쓸 것                      |
|--------------------------------------|---------------------------------|
| 세션 하나로 끝나는 작업              | 클라우드 세션 직접 시작         |
| 모든 작업에 내 컴퓨터가 필요         | 로컬 세션, 여러 개면 agent view |
| 대화 없이 주기적으로 도는 작업 하나  | 클라우드 예약 작업(routines)    |
| 여러 사람이 Slack 채널에서 함께 지시 | Claude Tag (Team·Enterprise)    |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 구성

```text
[You] --message--> [Project conversation: coordinator] --> answer
                          | start or route threads
          +---------------+---------------+
     [Thread A]      [Thread B]      [Thread C]   own branch and PR each
          +----- report --+---------------+
                          v
                 [Overview pane: threads by state]
```

모든 클라우드 스레드가 시작할 때 받는 것:

| 받음                                                         | 받지 않음                                             |
|--------------------------------------------------------------|-------------------------------------------------------|
| 프로젝트 저장소·파일, 프로젝트 지침·메모리                   | 내 컴퓨터의 Claude Code 설정·skill·MCP                |
| 각 저장소의 `CLAUDE.md`·`.claude/CLAUDE.md`·`.claude/rules/` | 저장소 `.mcp.json` 서버                               |
| 저장소 `.claude/` 아래 skill·agent·command                   | 저장소 `.claude/settings.json`의 hook·권한 규칙·`env` |
| claude.ai 계정의 connector                                   | -                                                     |
| 클라우드 환경(네트워크 허용, 환경 변수, 비밀값, 설치 도구)   | -                                                     |

Overview 창 **Threads** 탭의 상태:

| 상태             | 뜻                                            |
|------------------|-----------------------------------------------|
| Ready for review | PR이 열려 검토를 기다림                       |
| Waiting on you   | 답·승인이 필요하거나 실패함                   |
| Working          | 진행 중                                       |
| Landing          | PR 승인 또는 병합 대기열                      |
| Idle             | 끝났고 기다리는 것 없음                       |
| Resolved         | 완료 처리(직접, Claude, 또는 1주일 활동 없음) |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 만들기

준비:

| 항목   | 조건                                                                                                 |
|--------|------------------------------------------------------------------------------------------------------|
| 플랜   | Pro·Max·Ultra, 사이드바 **Projects**에 **New project**가 보임                                        |
| GitHub | github.com 저장소(GitHub Enterprise Server·GitLab·Bitbucket 불가), push 권한, Claude GitHub App 설치 |
| 환경   | 기본 환경은 흔한 패키지 저장소에 접근 가능. 다른 도메인·비밀값·도구는 클라우드 환경에서 설정         |

- `/web-setup`으로 연결한 GitHub 토큰은 다른 클라우드 세션에는 되지만 프로젝트 스레드에는 부족합니다. Claude GitHub App이 필요합니다.
- SAML SSO를 강제하는 GitHub 조직은 Claude 앱을 그 조직에 승인해야 비공개 저장소가 보입니다.

만드는 방법:

1. **처음부터**: **Projects > New project**에서 이름, 목표 한 줄(선택), Context(저장소·파일·폴더·Google Drive 폴더, 선택)를 넣고 **Create project**.
2. **진행 중인 클라우드 세션에서**: 세션 사이드바 메뉴 **Continue in project > Continue as new project**. Claude가 세션을 읽고 설정을 제안합니다.

- 첫 프로젝트를 만들면 Claude가 먼저 한 턴을 실행할 수 있고(사용량을 씀), 저장소를 읽기만 하는 탐색 스레드나 **Setup recommendations**를 내놓습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 일 맡기기

- 질문은 대화에서 바로 답하고, 새 일은 새 스레드나 그 영역을 맡은 기존 스레드로 보냅니다. 한 메시지의 서로 관계없는 작업들은 각각 스레드가 됩니다.
- 첫 묶음 전에: 프로젝트 지침 작성 → 작은 일 하나로 결과 형식 확인 → **Project settings > General**의 Threads 모델·effort 확인(새 프로젝트 기본 Opus·medium) → 처음에는 "스레드를 시작 전에 제안하고 한 번에 몇 개만" 요청.
- 대화에서 진행 방식을 말로 정할 수 있습니다: "시작 전에 제안하고 승인을 기다려", "한 번에 두 개까지", "계획을 보기 전에는 PR을 열지 마". 이런 선호는 프로젝트 메모리에 저장되지만 강제 설정이 아니라 지키려는 지시입니다.
- 코드를 바꾸는 클라우드 스레드는 기본 브랜치에서 새 브랜치를 만들고, 요청하면(버그 수정 등은 스스로) PR을 엽니다. PR을 연 뒤에는 auto-fix를 켜고 CI 실패·리뷰 댓글을 처리합니다.
- 스레드는 모델이 지원하면 auto 모드로 돌아 대부분 묻지 않고 실행합니다. 승인 질문은 그 스레드 안에 있어, 프로젝트 대화에서 "진행해"라고 해도 닿지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 공통 문맥

| 문맥             | 담는 것                                                               | 설정 위치                                             |
|------------------|-----------------------------------------------------------------------|-------------------------------------------------------|
| 프로젝트 메모리  | 요구사항·결정·주의점. `MEMORY.md` 색인을 스레드가 시작할 때 읽음      | 대화에서 "기억해" 요청, **Project settings > Memory** |
| 프로젝트 지침    | 새 스레드와 조정자에게 보내는 글, 최대 16,000자                       | **Project settings > Memory > Project instructions**  |
| 저장소·파일·환경 | 스레드가 clone하는 저장소, `/mnt/project-files`의 파일, 클라우드 환경 | **Project settings > Environment**, Context 탭        |

- 프로젝트 메모리는 내 컴퓨터의 Claude Code auto memory와도, 저장소의 `CLAUDE.md`와도 별개입니다. 저장소 규칙은 그 저장소의 `CLAUDE.md`에, 프로젝트 전체 메모는 프로젝트 메모리에 둡니다.
- claude.ai 설정에서 메모리를 끄면 프로젝트 메모리도 읽고 쓸 수 없습니다.
- 지침에 넣을 것: 프로젝트 목적, 저장소·시작 브랜치·PR 이름 규칙, 끝내기 전 검사 방법, 필요한 것이 없을 때 할 일(추측하지 말고 멈춤), 미리 승인받을 일(병합·force push·CI 변경 등).
- 업로드 한도: 한 번에 1,000개·2GB, 파일 하나 480MB. 폴더와 Google Drive 폴더 합쳐 10개. 업로드는 사본이라 내 컴퓨터에서 고친 내용은 다시 올려야 반영됩니다.
- 설정 변경(지침·저장소·환경)은 새 스레드부터 적용되고 이미 도는 스레드에는 닿지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 내 컴퓨터에서 실행

로컬 DB, 기기 에뮬레이터, VPN 뒤 API처럼 내 컴퓨터에만 있는 것이 필요한 작업은 그 스레드만 내 컴퓨터에서 돌릴 수 있습니다.

| 항목        | 클라우드 스레드        | 내 컴퓨터 스레드                                                |
|-------------|------------------------|-----------------------------------------------------------------|
| 파일·도구   | 프로젝트 클라우드 환경 | 그 컴퓨터의 파일·도구·MCP·Claude Code 설정(hook·권한 규칙 포함) |
| 지침·메모리 | 지침과 메모리          | 지침만, 메모리 파일은 읽지 않음                                 |
| 실행 조건   | 노트북을 닫아도 계속   | 그 컴퓨터가 켜져 있고 Remote Control이 연결된 동안              |

1. 폴더 연결(그 컴퓨터에 Claude Code v2.1.280 이상): 데스크톱 앱 **Settings > Claude Code**의 **Use this computer from your phone and claude.ai**를 켜고 폴더를 추가하거나, 터미널에서 그 폴더에 `claude remote-control`을 실행해 둡니다(git 저장소는 `--spawn worktree`로 스레드마다 worktree).
2. 프로젝트 대화의 **+** 메뉴에서 **Work locally**(데스크톱 앱은 **Work in a local folder**)를 고르고 작업을 적습니다.
3. **Allow Claude to work in a folder on your computer** 카드에서 폴더를 고르고 **Allow once**. 한 폴더에서 두 스레드가 동시에 일하면 서로 변경을 덮어쓸 수 있으니 git 저장소는 **Worktree**를 켭니다.

- 이 스레드는 auto 모드로 돌아 그 폴더에서 묻지 않고 명령·편집을 합니다. 다른 모드로 돌리려면 `claude remote-control --settings <파일>`에 `disableAutoMode: "disable"`과 `permissions.defaultMode`를 둡니다.
- 계정에 **Require trusted devices**가 켜져 있으면 **Work locally**를 쓸 수 없습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 사용량

- 프로젝트는 세션 하나보다 플랜 한도를 빨리 씁니다. 사용량이 드는 곳: 실행 중인 스레드(각각 세션 하나), 조정자 대화, PR을 지켜보는 스레드(CI 실패·리뷰 댓글에 다시 깨어남).
- 하루에 새 스레드는 모든 프로젝트를 합쳐 500개까지입니다. 대화로 정한 동시 실행 수는 상한이 아니라 선호입니다.
- 한도에 걸린 스레드는 기다렸다가 한도가 풀리면 기본으로 스스로 이어갑니다(**Continue threads automatically when usage limits reset**, 기본 켬).
- 줄이는 방법: 1시간 넘게 쉰 큰 스레드를 되살리기보다 새 스레드 시작(캐시 수명 1시간), 작은 모델·낮은 effort, 동시 스레드 수 줄이기, 작은 질문은 대화에서 답하게 하기.
- 쉬고 있는 프로젝트(실행 스레드·지켜보는 PR·새 메시지 없음)와 보관한 프로젝트는 사용량을 쓰지 않습니다.
- **Pause**는 모든 스레드와 대화를 멈추고, **Archive**는 숨기고 스레드를 보관하며, **Delete**는 스레드·메모리·파일을 되돌릴 수 없게 지웁니다(GitHub에 올린 브랜치·PR은 그대로).

[⬆ 목차로 돌아가기](#목차)

---

## 9. 다른 기능과 관계

| 기능                      | 관계                                                                                   |
|---------------------------|----------------------------------------------------------------------------------------|
| 클라우드 세션             | 스레드는 기본으로 클라우드 세션. 직접 시작한 클라우드 세션을 프로젝트로 가져올 수 있음 |
| Remote Control            | 내 컴퓨터에서 스레드를 돌릴 때 씀                                                      |
| 예약 작업(routines)       | 프로젝트에서 요청하면 그 프로젝트의 스레드로 도는 클라우드 예약 작업이 만들어짐        |
| 로컬 세션·agent view      | 프로젝트 밖. agent view는 내가 시작한 여러 로컬 세션을 나란히 보는 화면                |
| agent teams               | 한 세션이 한 작업을 위해 팀원 세션을 시작하고 작업과 함께 끝남                         |
| subagent                  | 한 세션 안의 곁가지 작업. 스레드도 subagent를 쓸 수 있음                               |
| worktree                  | 로컬 세션용. 클라우드 스레드는 각자 sandbox에 clone하므로 필요 없음                    |
| Claude Tag                | Team·Enterprise의 Slack 채널용, 여러 사람이 함께 지시. 프로젝트는 한 사람 전용         |
| claude.ai 채팅의 Projects | 대화·참고 파일 묶음(조정자·스레드 없음). 새 방식이 닿을 때까지 그대로 동작             |

[⬆ 목차로 돌아가기](#목차)

---

## 10. 제한

- 터미널 CLI, VS Code 확장, JetBrains 플러그인에서는 쓸 수 없고, Amazon Bedrock·Google Cloud Agent Platform·Microsoft Foundry를 통해서도 쓸 수 없습니다.
- 내가 시작한 로컬 세션을 프로젝트에 넣을 수는 없습니다(작업 내용을 가져오는 것만 가능).
- 클라우드 스레드의 sandbox는 턴 사이에 멈췄다가 다시 열립니다. 다시 열지 못하면 새 clone에서 이어가 commit하지 않은 변경이 사라질 수 있으니, 긴 작업은 중간에 commit·push를 요청합니다.
- 프로젝트는 한 사용자 것이며 공유할 수 없습니다. beta 동안 조직 단위 관리 기능은 없습니다.
- 스레드는 시작한 프로젝트에만 속합니다. 다른 프로젝트로 옮기거나 독립 세션으로 빼낼 수 없고, 두 프로젝트를 합칠 수 없습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 함께 보기

- [Claude Code 데스크톱 앱](./claude_code_desktop_guide.md) — Code 탭, 8절 Projects와 Code 세션 비교
- [Claude Code의 Code Mode](./claude_code_mode.md) — 이름이 비슷한 다른 기능 구분
- [Claude Code 공통 개념](./claude_code_concepts.md) — 사용 환경, 권한 모드

---

## 참고 자료

- Claude Code Docs: [Let Claude coordinate ongoing work with Projects](https://code.claude.com/docs/en/claude-projects.md) — 2026-11-26 확인 — ★★★☆☆
- Claude Code Docs: [Run agents in parallel](https://code.claude.com/docs/en/agents.md) · [Remote Control](https://code.claude.com/docs/en/remote-control.md) — ★★★☆☆
- Claude Help Center: [What are projects?](https://support.claude.com/en/articles/9517075-what-are-projects) — claude.ai 채팅의 예전 Projects — ★★★☆☆

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

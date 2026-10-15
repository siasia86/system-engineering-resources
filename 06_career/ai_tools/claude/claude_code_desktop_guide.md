# Claude Code 데스크톱 앱 가이드
<!-- reference: _reference/claude_code_official_notes.md -->

Claude 데스크톱 앱의 **Code 탭**에서 세션을 만들고, SSH로 Linux 서버에 연결해 작업하고, 여러 세션을 정리하는 방법을 다룹니다. 터미널 명령과 권한 규칙은 [Linux CLI 가이드](claude_code_cli_linux_guide.md), 매일 쓰는 요청·컨텍스트 관리는 [기본 사용법](claude_code_basics_guide.md)을 참고합니다.

🟡 내용은 2026-10-15 공식 문서(desktop, claude-projects) 기준입니다. 사이드바 구성은 같은 날 데스크톱 앱의 SSH 세션에서 확인했고, 단축키는 다시 시험하지 않았습니다. 화면 이름과 메뉴 위치는 앱 버전에 따라 바뀔 수 있습니다.

## 목차

| 단계 | 섹션                                                                                                                 |
|------|----------------------------------------------------------------------------------------------------------------------|
| 시작 | [1. Code 탭 구성](#1-code-탭-구성) / [2. 세션 시작](#2-세션-시작) / [3. SSH 원격 세션](#3-ssh-원격-세션)             |
| 작업 | [4. 권한 모드](#4-권한-모드) / [5. 화면 배치](#5-화면-배치) / [6. 변경 검토와 PR](#6-변경-검토와-pr)                 |
| 정리 | [7. 세션 관리](#7-세션-관리) / [8. 사이드바 정리](#8-사이드바-정리) / [9. 다른 기기에서 보기](#9-다른-기기에서-보기) |
| 참고 | [10. CLI와 차이](#10-cli와-차이) / [11. 단축키](#11-단축키)                                                          |

---

## 1. Code 탭 구성

데스크톱 앱에는 대화용 **Chat**, 긴 에이전트 작업용 **Cowork**, 개발용 **Code** 탭이 있습니다. Code 탭의 대화 하나가 **세션**이며, 세션마다 대화 기록·프로젝트 폴더·컨텍스트가 따로 있습니다.

| 영역      | 역할                                                    |
|-----------|---------------------------------------------------------|
| 사이드바  | 세션 목록, 새 세션, 필터·그룹 정리                      |
| 대화 창   | 요청 입력, 응답과 도구 실행 기록                        |
| 입력 영역 | 실행 환경·폴더·모델·권한 모드 선택, 파일 첨부(`+` 버튼) |
| 보조 창   | diff, 터미널, 파일 편집기, 브라우저, 계획, 작업 목록    |

앱에 Claude Code가 들어 있으므로 내 컴퓨터에서 쓸 때는 CLI를 따로 설치하지 않아도 됩니다. Linux용 데스크톱 앱은 beta이며 apt·.deb로 설치합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 세션 시작

첫 메시지를 보내기 전에 입력 영역에서 네 가지를 고릅니다.

| 항목          | 선택지                                                             |
|---------------|--------------------------------------------------------------------|
| 실행 환경     | Local(내 컴퓨터), Cloud(앱을 닫아도 계속), SSH 연결, Windows는 WSL |
| 프로젝트 폴더 | 작업할 폴더나 저장소 (Cloud는 저장소 여러 개 가능)                 |
| 모델          | 전송 버튼 옆 목록, 세션 중에도 변경 가능                           |
| 권한 모드     | 전송 버튼 옆 모드 선택기, 세션 중에도 변경 가능                    |

- Git 저장소에서는 branch 이름 옆 **worktree** 옵션으로 세션마다 격리된 작업 사본을 만들 수 있습니다. 기본 위치는 `<프로젝트>/.claude/worktrees/`입니다.
- 작업 중에 수정 요청을 입력하고 `Enter`를 누르면 현재 동작이 끝난 뒤 반영됩니다. 즉시 멈추려면 중지 버튼이나 `Esc`를 씁니다.
- 응답 뒤 빈 입력란에 회색으로 다음 요청 제안이 보이면 `Tab`으로 받아 고쳐 보낼 수 있습니다. 제안 생성도 사용량에 포함됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. SSH 원격 세션

SSH 세션은 Claude Code를 원격 서버에서 실행하고 데스크톱 앱을 화면으로 씁니다. 코드가 서버에만 있거나 서버의 도구·하드웨어가 필요할 때 적합합니다.

### 연결 추가

입력 영역의 실행 환경 목록에서 **SSH > Add SSH connection…**을 고르고 다음을 채웁니다.

| 항목            | 내용                                               |
|-----------------|----------------------------------------------------|
| Name            | 구분용 이름                                        |
| SSH host        | `user@hostname` 또는 `~/.ssh/config`의 Host 이름   |
| SSH port        | 비우면 22 또는 SSH 설정의 포트                     |
| SSH key         | 개인 키 경로 (비우면 SSH 설정·agent 사용)          |
| Worktree folder | 원격 서버에서 worktree를 만들 폴더 (비우면 기본값) |

첫 연결 때 앱이 원격 서버의 `~/.claude/remote/`에 Claude Code를 자동으로 설치합니다. 이 서버에서는 `~/.claude/remote/ccd-cli/` 아래 2.1.295가 설치된 것을 확인했습니다.

### 원격 서버 요구 사항

- x86_64 또는 arm64, glibc 2.17 이상 또는 musl (`ldd --version`으로 확인)
- SSH 서버의 SFTP 하위 시스템 (`sftp`로 접속해 `sftp>`가 보이면 정상)
- `MaxSessions`가 1이면 늘림 (앱이 한 연결에 세션을 여러 개 엶)
- 홈 디렉터리가 `noexec`가 아니고 사용자당 약 1GB 여유 공간
- 서버에서 Claude Code가 필요한 외부 주소로 나갈 수 있는 네트워크 (필요하면 proxy 설정)

### 연결이 끊겼을 때

Claude Code는 원격 서버의 프로세스로 돌기 때문에 내 컴퓨터가 잠들거나 네트워크가 끊겨도 작업이 계속됩니다. 다만 Claude 계정으로 로그인했다면 연결이 끊긴 동안 로그인 갱신이 멈춰 몇 분 만에 작업이 멈출 수도 있습니다.

- 밤새 돌려야 하면 컴퓨터를 깨워 두고 앱을 켜 두거나, Cloud 세션을 씁니다.
- 프롬프트 없이 로그인되는 SSH agent 키를 쓰면 끊긴 뒤 앱이 스스로 다시 연결합니다.
- 돌아와서 작업이 멈춰 있으면 재연결 실패·인증 오류·응답 대기 요청 중 무엇인지 확인하고, 없으면 메시지를 보내 이어갑니다.

### PR을 만들 때

SSH 세션에서 **Create PR**을 누르면 branch push와 `gh pr create`가 원격 서버에서 실행됩니다. 원격 서버에 `gh`를 직접 설치하고 `git push`와 `gh auth status`가 되는지 먼저 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 권한 모드

| 화면 이름          | 설정 값             | 동작                                                   |
|--------------------|---------------------|--------------------------------------------------------|
| Manual             | `default`           | 파일 편집·명령 실행 전마다 확인                        |
| Accept edits       | `acceptEdits`       | 파일 편집과 기본 파일 명령은 자동, 그 밖의 명령은 확인 |
| Plan               | `plan`              | 읽기·탐색 후 계획만 제안, 승인 전 수정 안 함           |
| Auto               | `auto`              | 일상 확인 없이 진행, 별도 분류기가 위험 작업을 점검    |
| Bypass permissions | `bypassPermissions` | 확인 없이 진행. 격리된 컨테이너·VM에서만 사용          |

- 터미널과 달리 데스크톱 앱에서는 `Shift+Tab`이 모드를 바꾸지 않습니다. 모드 선택기나 `Ctrl+Shift+M`(macOS `Cmd+Shift+M`)을 씁니다.
- 선택기에서 고른 모드는 폴더별로 기억되며 `permissions.defaultMode`보다 우선합니다. Plan은 현재 세션에만 적용됩니다.
- `dontAsk` 모드는 CLI에서만 쓸 수 있습니다.
- Auto나 Bypass 모드에서는 Claude가 확인 카드 없이 다른 세션을 보관(archive)할 수 있습니다. 확인을 받으려면 Manual로 바꿉니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 화면 배치

Code 탭은 대화·diff·브라우저·터미널·파일·계획·작업 창을 끌어서 배치합니다. 창 머리글을 끌어 위치를 바꾸고, 가장자리를 끌어 크기를 조절합니다.

| 창          | 여는 방법                                  | 용도                                     |
|-------------|--------------------------------------------|------------------------------------------|
| 터미널      | 제목 표시줄 **Terminal**, `Ctrl+백틱`      | 세션과 같은 폴더·환경에서 직접 명령 실행 |
| diff        | 변경량 표시(`+12 -1`) 클릭, `Ctrl+Shift+D` | 파일별 변경 검토와 줄 단위 의견          |
| 파일        | 대화의 파일 경로 클릭                      | 간단한 수정 후 **Save**                  |
| 작업        | **⋮** 메뉴 → Background tasks              | subagent·백그라운드 명령 상태 확인·중지  |
| 곁가지 대화 | `Ctrl+;`(macOS `Cmd+;`) 또는 `/btw`        | 본 대화에 남기지 않고 질문               |

- 보기 모드(Normal·Thinking·Verbose)는 `Ctrl+O`로 바꿉니다. Claude가 왜 그 행동을 했는지 볼 때 Verbose를 씁니다.
- 모델 선택기 옆 사용량 고리를 누르면 세션의 컨텍스트 사용량과 플랜 사용량을 봅니다. 컨텍스트는 세션별이고 플랜 사용량은 모든 Claude Code 환경이 공유합니다.
- 터미널과 파일 창은 Local·SSH 세션에서만 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 변경 검토와 PR

1. 변경량 표시를 눌러 diff를 엽니다. 왼쪽은 파일 목록, 오른쪽은 변경 내용입니다.
2. 고칠 줄을 눌러 의견을 적고, 여러 줄에 의견을 단 뒤 `Ctrl+Enter`(macOS `Cmd+Enter`)로 한 번에 보냅니다. Claude가 반영한 새 diff가 다시 나옵니다.
3. commit 전에 `/code-review`로 검토를 요청할 수 있습니다. 결과 카드에서 diff로 하나씩 보거나 수정을 요청합니다.
4. PR을 열면 CI 상태 표시줄이 나타납니다. **CI**를 눌러 실패한 검사 자동 수정, 검사 통과 후 자동 병합을 켤 수 있습니다. 자동 병합은 squash 방식이며 저장소 설정에서 auto-merge를 먼저 허용해야 합니다.

PR 상태 확인은 GitHub CLI(`gh`) 설치와 인증이 필요합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 세션 관리

| 작업                 | 방법                                                                         |
|----------------------|------------------------------------------------------------------------------|
| 새 세션              | 사이드바 **+ New session**, `Ctrl+N`(macOS `Cmd+N`)                          |
| 세션 이동            | `Ctrl+Tab` / `Ctrl+Shift+Tab`                                                |
| 분할 보기            | `Ctrl`(macOS `Cmd`)을 누른 채 사이드바의 세션 클릭, `Ctrl+\`로 닫기          |
| 이름 바꾸기          | 세션 위쪽 도구 모음의 제목 클릭                                              |
| 보관                 | 사이드바 세션에 마우스를 올리고 보관 아이콘 (worktree도 함께 정리)           |
| 다른 곳에서 이어가기 | 세션 메뉴 → **Open in** → Cloud 또는 편집기 (SSH·WSL 세션은 Cloud 이동 불가) |
| CLI 세션 가져오기    | 터미널 세션을 닫고 앱 입력란에 `/resume` (Local 세션에서만)                  |

- 세션 하나에는 주제 하나만 둡니다. 관련 없는 작업은 새 세션으로 시작하면 컨텍스트가 섞이지 않습니다.
- **Settings > Claude Code**에서 PR 병합·종료 후 자동 보관, worktree branch 접두어를 설정할 수 있습니다.
- Claude에게 "auth 작업한 세션이 어디야?", "API 세션에 스키마가 바뀌었다고 전해 줘"처럼 요청하면 다른 세션을 찾고 메시지를 보냅니다. 볼 수 있는 범위는 앱이 직접 실행한 Local·SSH·WSL 세션이며, Cloud·터미널 CLI 세션은 보이지 않습니다.
- 현재 작업 범위 밖의 일을 발견하면 Claude가 작업 카드로 새 세션을 제안할 수 있습니다. 카드를 눌러야 시작됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 8. 사이드바 정리

세션이 많아지면 사이드바를 **섹션** 단위로 정리합니다. 2026-10-15 이 앱에서 확인한 기본 섹션은 다음과 같습니다.

| 섹션          | 내용                                             |
|---------------|--------------------------------------------------|
| Pinned (고정) | 고정한 세션. 고정해도 원래 속한 그룹 정보는 유지 |
| Routines      | 예약 실행 작업. 사용하지 않으면 숨길 수 있음     |
| Sessions      | 나머지 세션. 프로젝트별 묶기, 최근 활동 순 정렬  |
| 사용자 그룹   | 직접 만든 그룹마다 섹션 하나. 세션을 끌어서 넣음 |

- **세션**은 대화 하나, **그룹**은 세션을 담는 사용자 폴더, **섹션**은 사이드바에 보이는 묶음 단위입니다. 사용자 그룹 하나가 섹션 하나로 보입니다.
- 사이드바 위쪽 필터로 상태·프로젝트·실행 환경별로 걸러 볼 수 있습니다.
- 자주 여는 세션은 고정하고, 허브·작업 대상처럼 성격이 같은 세션은 그룹으로 묶으면 찾기 쉽습니다.

### Projects (beta)와 Code 세션

사이드바에 **Projects**가 보이면 Claude가 관련 작업을 여러 스레드로 나눠 실행·추적하는 프로젝트를 만들 수 있습니다. 2026-10-15 기준 Pro·Max 플랜의 공개 beta이며 계정별로 단계적으로 제공됩니다. 프로젝트도 고정할 수 있어 Pinned에 세션과 함께 보일 수 있습니다.

| 항목      | Code 세션                    | Project                                             |
|-----------|------------------------------|-----------------------------------------------------|
| 작업 단위 | 세션 하나 = 대화 하나        | 대화 하나가 여러 스레드(세션)를 시작·추적           |
| 실행 위치 | Local·SSH·WSL·Cloud 중 선택  | 스레드마다 기본은 클라우드 세션                     |
| 기준 지침 | 저장소 `CLAUDE.md`·개인 설정 | 프로젝트 지침·메모리를 모든 스레드에 적용           |
| 코드 위치 | 선택한 폴더 그대로           | github.com 저장소 (Claude GitHub App·push 권한)     |
| 사용 위치 | CLI·IDE·데스크톱 앱          | claude.ai/code·데스크톱 앱·모바일 앱 (CLI·IDE 불가) |
| 공유      | 세션 단위                    | 한 사용자 전용, 공유 불가                           |

- 직접 시작한 Local·SSH 세션은 프로젝트에 넣을 수 없습니다. 프로젝트가 내 컴퓨터나 서버에 닿는 방법은 그 컴퓨터에서 스레드를 실행하는 것 하나입니다.
- 그 컴퓨터의 폴더가 필요한 작업은 먼저 폴더를 Remote Control로 연결하고(데스크톱 앱 **Settings > Claude Code > Use this computer from your phone and claude.ai**에서 폴더 추가, 또는 그 폴더에서 `claude remote-control` 실행, v2.1.280 이상), 프로젝트 대화의 **+** 메뉴에서 **Work locally**로 요청합니다. 이 스레드는 auto 모드로 실행되고, 프로젝트 지침은 받지만 메모리 파일은 받지 않으며, 그 컴퓨터가 켜져 연결된 동안만 진행됩니다.
- 클라우드 스레드의 sandbox는 턴 사이에 멈췄다가 다시 열립니다. 다시 열지 못하면 새 clone에서 이어가므로 commit하지 않은 변경이 사라질 수 있습니다. 긴 작업은 중간 commit·push를 요청합니다.
- claude.ai 채팅의 이전 Projects(대화와 참고 파일 묶음)와는 다른 기능입니다.
- 한 세션 안에서 끝나는 작업이나 로컬 서버 작업이 중심이면 Code 세션이 단순합니다. 여러 저장소에 걸치거나 계속 작업이 들어오는 목표라면 프로젝트가 맞습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 9. 다른 기기에서 보기

**Remote Control**을 켠 Local 세션은 claude.ai/code와 같은 계정의 Claude 앱 세션 목록에 나타납니다.

| 범위                | 켜기·끄기                                                           |
|---------------------|---------------------------------------------------------------------|
| 세션 하나           | 세션의 **Remote Control** 스위치, 또는 입력란에 `/remote-control`   |
| 이 컴퓨터의 새 세션 | **Settings > Claude Code > Connect new sessions to Remote Control** |
| CLI 포함 모든 세션  | `~/.claude/settings.json`에 `"disableRemoteControl": true`          |

연결 상태는 세션 제목 앞 노트북 아이콘으로 확인합니다. 이미 다른 기기에 보이는 세션을 숨기려면 앱에서 보관합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 10. CLI와 차이

앱과 CLI는 같은 엔진과 설정 파일(`CLAUDE.md`, `~/.claude/settings.json`, MCP·hook·skill 설정)을 함께 씁니다.

| 항목            | CLI                       | 데스크톱 앱                             |
|-----------------|---------------------------|-----------------------------------------|
| 권한 모드       | `dontAsk` 포함 전체       | Manual·Accept edits·Plan·Auto (+Bypass) |
| 여러 세션       | 터미널 여러 개            | 사이드바                                |
| 세션 격리       | `--worktree`              | 세션 시작 시 worktree 옵션              |
| 파일 첨부       | 불가 (이미지 붙여넣기만)  | 이미지·PDF                              |
| 반복 작업       | cron, CI                  | 예약 작업 (Scheduled tasks)             |
| 스크립트·자동화 | `-p`, `--output-format`   | 불가 (대화형 전용)                      |
| 설정 대화 상자  | `/permissions`, `/config` | 설정 파일 직접 수정 또는 Settings 화면  |

- 앱에서 `/permissions`처럼 터미널 대화 상자를 여는 명령은 `isn't available in this environment`로 응답합니다. 권한 규칙은 설정 파일을 직접 고칩니다.
- 스크립트·CI 자동화는 CLI, 여러 세션 병렬 관리와 시각적 diff 검토는 앱이 적합합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 11. 단축키

Windows·Linux 기준이며 macOS는 `Ctrl` 대신 `Cmd`를 씁니다. 세션 순환, 터미널, 보기 모드는 모든 OS에서 `Ctrl`입니다. 전체 목록은 `Ctrl+/`로 봅니다.

| 단축키              | 동작                |
|---------------------|---------------------|
| `Ctrl+N` / `Ctrl+W` | 새 세션 / 세션 닫기 |
| `Ctrl+Tab`          | 다음 세션           |
| `Esc`               | 응답 중지           |
| `Ctrl+Shift+D`      | diff 창 열기·닫기   |
| `Ctrl+백틱`         | 터미널 창 열기·닫기 |
| `Ctrl+\`            | 선택한 창 닫기      |
| `Ctrl+;`            | 곁가지 대화         |
| `Ctrl+O`            | 보기 모드 전환      |
| `Ctrl+Shift+M`      | 권한 모드 메뉴      |
| `Ctrl+Shift+I`      | 모델 메뉴           |
| `Ctrl+Shift+E`      | effort 메뉴         |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [_reference/claude_code_official_notes.md](../../../_reference/claude_code_official_notes.md) — 버전·사용 환경 검증 근거 노트
- Desktop application: [code.claude.com/docs/en/desktop](https://code.claude.com/docs/en/desktop) — ★★★☆☆
- Claude Desktop on Linux: [code.claude.com/docs/en/desktop-linux](https://code.claude.com/docs/en/desktop-linux) — ★★★☆☆
- Remote Control: [code.claude.com/docs/en/remote-control](https://code.claude.com/docs/en/remote-control) — ★★★☆☆
- Worktrees: [code.claude.com/docs/en/worktrees](https://code.claude.com/docs/en/worktrees) — ★★★☆☆
- Projects: [code.claude.com/docs/en/claude-projects](https://code.claude.com/docs/en/claude-projects) — ★★★☆☆

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

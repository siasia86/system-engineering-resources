# gstack

Claude Code 등 코딩 에이전트에 설치하는 slash command skill 묶음입니다. 제품 검토·설계 검토·코드 리뷰·브라우저 QA·보안 감사·배포를 역할별 skill로 나누어 한 흐름으로 실행합니다. Garry Tan(Y Combinator)이 공개한 MIT 라이선스 오픈소스입니다.

> 확인 기준: 공식 저장소 [garrytan/gstack](https://github.com/garrytan/gstack) README, `VERSION` `1.99.5.0`, commit `5b4fa9e`, 2026-11-17 확인. 설치·실행은 하지 않았으며 아래 내용은 README가 안내하는 범위입니다. 판이 자주 바뀌므로 적용 전에 README를 다시 확인합니다.

## 목차

| 섹션                                                                                                |
|-----------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 설치와 갱신](#2-설치와-갱신) / [3. 지원 에이전트](#3-지원-에이전트)        |
| [4. 작업 흐름과 주요 skill](#4-작업-흐름과-주요-skill) / [5. 안전 장치](#5-안전-장치)               |
| [6. 외부 전송과 개인정보](#6-외부-전송과-개인정보) / [7. 플랫폼과 문제 해결](#7-플랫폼과-문제-해결) |
| [8. 운영 저장소에 도입할 때](#8-운영-저장소에-도입할-때)                                            |

## 1. 개요

| 항목         | 내용                                                                 |
|--------------|----------------------------------------------------------------------|
| 유형         | 코딩 에이전트용 skill 묶음(slash command, Markdown)                  |
| 기본 대상    | Claude Code(다른 에이전트는 `--host`로 설치)                         |
| 설치 위치    | `~/.claude/skills/gstack` (Claude Code 기본)                         |
| 필수 도구    | Claude Code, Git, Bun v1.4.2 이상(시험 판), Windows는 Node.js도 필요 |
| 라이선스     | MIT                                                                  |
| 세션 간 학습 | `/learn`(프로젝트별 패턴·주의점 관리), 별도 지식 저장소 GBrain 연동  |

gstack은 독립 실행 에이전트가 아니라, 이미 쓰는 코딩 에이전트에 역할별 skill을 더하는 방식입니다. README는 "도구 모음이 아니라 절차"라고 설명하며, 앞 단계 skill이 만든 설계 문서·시험 계획을 다음 skill이 읽습니다.

## 2. 설치와 갱신

### 개인 설치

README는 Claude Code에 아래 명령을 실행하도록 요청하는 방식을 안내합니다.

```bash
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup
```

README의 설치 문구는 이어서 `CLAUDE.md`에 gstack 절을 추가하도록 요청합니다. 이 절은 웹 탐색에 gstack의 `/browse`를 쓰고 다른 브라우저 도구를 쓰지 않도록 지시하므로, 기존 `CLAUDE.md` 규칙과 충돌하지 않는지 먼저 확인합니다.

Bun은 1.3.3보다 낮으면 setup이 거부합니다. README는 낮은 판에서 컴파일된 도구가 프로젝트의 `.env`를 읽을 수 있다는 이유를 듭니다.

### 팀 모드

공유 저장소 안에서 실행하면 팀원 세션이 gstack을 자동으로 받도록 저장소를 설정하고 commit까지 합니다.

```bash
(cd ~/.claude/skills/gstack && ./setup --team) \
  && ~/.claude/skills/gstack/bin/gstack-team-init required \
  && git add .claude/ CLAUDE.md \
  && git commit -m "require gstack for AI-assisted work"
```

| 항목       | 내용                                                            |
|------------|-----------------------------------------------------------------|
| `required` | 팀원에게 gstack을 요구(hook이 막음). Node.js가 PATH에 있어야 함 |
| `optional` | 막지 않고 안내만 함                                             |
| 자동 갱신  | 세션 시작 시 갱신 확인(1시간에 한 번)                           |
| 제거       | 공식 `docs/uninstall.md` 절차                                   |

### 갱신 채널

| 채널     | 내용                                                          | 전환 명령                                     |
|----------|---------------------------------------------------------------|-----------------------------------------------|
| `stable` | 새 설치 기본값. tag가 붙은 release만 받음                     | `bin/gstack-config set update_channel stable` |
| `main`   | main에 병합될 때마다 받음. 기여자 checkout은 자동으로 이 채널 | `bin/gstack-config set update_channel main`   |

## 3. 지원 에이전트

`./setup`만 실행하면 Claude Code에만 설치합니다. 다른 에이전트는 `--host <이름>`으로, 감지된 에이전트 전부는 `--host auto`로 설치합니다. `./setup --status`는 설치마다 host·등급·판·경로를 한 줄씩 보여 줍니다.

| 에이전트           | 등급(README 기준) | 설치 옵션             | 안전 skill        |
|--------------------|-------------------|-----------------------|-------------------|
| Claude Code        | full              | `--host claude`(기본) | hook으로 차단     |
| OpenAI Codex CLI   | experimental      | `--host codex`        | 안내만, 차단 없음 |
| Kiro               | experimental      | `--host kiro`         | 안내만, 차단 없음 |
| Cursor             | experimental      | `--host cursor`       | 안내만, 차단 없음 |
| Gemini CLI         | experimental      | `--host gemini`       | 안내만, 차단 없음 |
| GitHub Copilot CLI | experimental      | `--host copilot`      | 안내만, 차단 없음 |

full은 실제 작업 실행으로 인증된 등급, experimental은 설치·적합성 시험만 통과한 등급입니다. 이 밖에 OpenCode·Factory Droid·Antigravity CLI·OpenClaw·Hermes 등이 있으며 전체 표는 README의 "Other AI Agents" 절에 있습니다. Claude Code 밖에서는 `/careful` 같은 안전 skill이 명령을 막지 않고 경고만 한다는 점에 주의합니다.

## 4. 작업 흐름과 주요 skill

README가 제시하는 순서는 Think → Plan → Build → Review → Test → Ship → Reflect입니다.

```
/office-hours ─> /plan-ceo-review ─> /plan-eng-review ─> (build)
      │                                    │
   design doc                          test plan
                                           │
/review ─> /qa ─> /ship ─> /land-and-deploy ─> /canary ─> /retro
```

| skill              | 역할                                                      |
|--------------------|-----------------------------------------------------------|
| `/office-hours`    | 시작 단계. 제품 전제를 질문으로 다시 잡고 설계 문서 작성  |
| `/plan-ceo-review` | 문제와 범위 재검토                                        |
| `/plan-eng-review` | 구조·데이터 흐름·경계 조건·시험 계획 확정                 |
| `/autoplan`        | CEO → 설계 → DX → 엔지니어링 검토를 한 번에 실행          |
| `/review`          | CI는 통과하지만 운영에서 깨질 버그 탐지, 명확한 것은 수정 |
| `/qa`              | 실제 브라우저나 API·CLI·job·webhook으로 재현·수정·재검증  |
| `/cso`             | OWASP·STRIDE 기반 보안 감사(Docker 없으면 정적 검사만)    |
| `/ship`            | main 동기화, 시험, 검토 후 push와 PR 생성                 |
| `/land-and-deploy` | PR 병합, CI·배포 대기, 운영 상태 확인                     |
| `/canary`          | 배포 후 콘솔 오류·성능 저하·페이지 실패 감시              |
| `/retro`           | 주간 회고(사람별 작업·시험 상태 추세)                     |
| `/learn`           | 세션 간 학습한 프로젝트 패턴 검토·검색·정리               |

README는 처음에는 `/office-hours`, `/review`, `/qa` 세 개만 써 보고 맞는지 판단하라고 권합니다. 모든 skill의 설명은 공식 `docs/skills.md`에 있습니다.

## 5. 안전 장치

| skill       | 동작                                                          |
|-------------|---------------------------------------------------------------|
| `/careful`  | `rm -rf`, `DROP TABLE`, force push 같은 파괴적 명령 전에 경고 |
| `/freeze`   | 파일 수정을 한 디렉토리로 제한                                |
| `/guard`    | `/careful`과 `/freeze`를 함께 적용                            |
| `/unfreeze` | `/freeze` 경계 해제                                           |

README는 root·home 재귀 삭제와 기본 branch force push를 항상 거부한다고 설명합니다. 이 차단은 hook이 동작하는 Claude Code(full 등급) 기준입니다.

## 6. 외부 전송과 개인정보

| 항목      | 기본값                                | 끄는 방법                                  |
|-----------|---------------------------------------|--------------------------------------------|
| 원격 측정 | 꺼짐(처음 한 번 질문)                 | 처음 질문에서 거절                         |
| 갱신 확인 | 켜짐(GitHub 요청 2~3회)               | `gstack-config set update_check false`     |
| 외부 검토 | 켜짐(코드를 Codex·Claude Code로 전송) | `gstack-config set codex_reviews disabled` |

외부 검토는 사용자 자신의 로그인으로 코드를 다른 에이전트에 보냅니다. 기기 밖으로 나가는 전송은 영수증으로 남고 `gstack-egress list`로 확인할 수 있습니다. 상세 항목은 공식 `docs/privacy.md`에 있습니다.

## 7. 플랫폼과 문제 해결

| 플랫폼  | README 기준 지원                                                             |
|---------|------------------------------------------------------------------------------|
| macOS   | 전체 지원. Aside 브라우저(macOS 15 이상)가 있으면 브라우저 skill이 먼저 사용 |
| Linux   | 전체 지원. 내장 Chromium 사용                                                |
| Windows | 최소 지원. Windows 11의 Git Bash 또는 WSL, Bun과 Node.js 모두 필요           |

- Ubuntu 24.04 이상에서 AppArmor가 비특권 user namespace를 막아 Chromium이 실행되지 않으면 `GSTACK_CHROMIUM_NO_SANDBOX=1`을 설정합니다.
- Windows에서 Developer Mode 없이 Git Bash를 쓰면 symlink 대신 파일 복사로 설치되므로 `git pull` 뒤마다 `./setup`을 다시 실행합니다.
- 설치 상태 점검은 `~/.claude/skills/gstack/bin/gstack-doctor`로 합니다. 설치·Bun·hook·브라우저·컴파일된 도구를 항목별로 `ok`, `warn`, `not configured`, `fail`로 보여 주며 `fail`일 때만 0이 아닌 종료 코드를 냅니다.

## 8. 운영 저장소에 도입할 때

- 팀 모드는 `.claude/`와 `CLAUDE.md`를 저장소에 commit하고 팀원 세션에 hook을 겁니다. 공유 저장소에서는 변경 승인 절차를 거친 뒤 적용합니다.
- 외부 검토가 기본으로 켜져 있어 코드가 다른 AI 서비스로 전송됩니다. 조직의 코드 반출 규칙을 먼저 확인하고, 필요하면 `codex_reviews`를 끕니다.
- Claude Code 밖의 에이전트에서는 안전 skill이 차단하지 않으므로, 파괴적 명령 차단을 gstack에 맡기지 않고 에이전트 자체 권한 설정으로 막습니다.
- `/ship`, `/land-and-deploy`는 push·병합·배포까지 진행합니다. 운영 배포 권한이 있는 저장소에서는 실행 범위를 따로 정합니다.
- 다른 skill 묶음과의 비교는 [GitHub 참고 저장소](../../_reference/github_references.md#11-개발-행동과-엔지니어링-절차)를 봅니다.

## 참고 자료

- gstack 공식 저장소 README: [github.com/garrytan/gstack](https://github.com/garrytan/gstack) — ★★★☆☆
- gstack 설치 상세: [docs/install.md](https://github.com/garrytan/gstack/blob/main/docs/install.md) — ★★★☆☆
- gstack 개인정보·원격 측정: [docs/privacy.md](https://github.com/garrytan/gstack/blob/main/docs/privacy.md) — ★★★☆☆

---

**작성일**: 2026-06-18

**마지막 업데이트**: 2026-11-17

© 2026 siasia86. Licensed under CC BY 4.0.

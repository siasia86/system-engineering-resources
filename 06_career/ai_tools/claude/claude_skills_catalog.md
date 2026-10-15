# Claude Code 스킬 목록과 한 줄 설명
<!-- reference: _reference/claude_code_official_notes.md -->

2026-10-15 Linux 서버의 Claude Code 세션에서 제공된 스킬의 용도를 정리합니다. 직접 설치한 개인 스킬 14개를 중심으로, Claude Code 기본 제공 스킬과 claude.ai 계정 스킬 중 자주 쓰는 것을 함께 적습니다. 스킬 작성법과 frontmatter는 [확장 기능 가이드](claude_code_extensions_guide.md#4-skills)를 참고합니다.

## 목차

| 섹션                                                                                              |
|---------------------------------------------------------------------------------------------------|
| [1. 목록의 확인 범위](#1-목록의-확인-범위) / [2. 개인 스킬](#2-개인-스킬)                         |
| [3. 기본 제공 스킬](#3-기본-제공-스킬) / [4. claude.ai 계정 스킬](#4-claudeai-계정-스킬)          |
| [5. 호출 방법](#5-호출-방법) / [6. 같은 이름의 우선순위](#6-같은-이름의-우선순위)                 |
| [7. 업무별 선택 예시](#7-업무별-선택-예시) / [8. 목록 유지와 스킬 수정](#8-목록-유지와-스킬-수정) |

---

## 1. 목록의 확인 범위

출처는 해당 세션에 제공된 스킬 목록과 `~/.claude/skills/*/SKILL.md`의 `name`·`description`입니다. 다른 서버나 다른 세션에 같은 스킬이 있다는 뜻은 아닙니다.

| 구분           | 위치                               | 개수·비고                             |
|----------------|------------------------------------|---------------------------------------|
| 개인 스킬      | `~/.claude/skills/<이름>/SKILL.md` | 14개, 이 서버의 모든 프로젝트에 적용  |
| 기본 제공 스킬 | Claude Code에 포함                 | 버전·기능 설정에 따라 다름            |
| 계정 스킬      | claude.ai 계정에서 동기화          | `anthropic-skills:이름` 형식으로 표시 |
| 프로젝트 스킬  | 저장소의 `.claude/skills/`         | 이 세션에서는 없음                    |

목록에 보이는 것과 실제로 동작하는 것은 별개입니다. 이 문서 작성 과정에서는 목록과 파일을 대조했으며, 각 스킬이 새 세션에서 자동 선택되는지는 새로 시험하지 않았습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 개인 스킬

개인 스킬 14개는 SKILL-35(`35_agent-skill`)의 `claude_linux/` 관리 원본에서 설치했습니다. 대부분 Codex용 원본을 옮기면서 `CODEX-COMPAT` 절만 `CLAUDE-COMPAT`로 바꿨습니다.

### 작업 규칙

| 스킬              | 한 줄 설명                                                                              |
|-------------------|-----------------------------------------------------------------------------------------|
| `git-commit-rule` | 한국어 type 접두사 commit 메시지, 검토한 파일만 staging, branch·push 규칙을 적용합니다. |
| `repo-governance` | 저장소의 `.governance/` 규칙을 찾고 전역 규칙과의 우선순위를 적용합니다.                |
| `readme-template` | Markdown 문서의 필수 footer(배지·날짜·라이선스) 양식을 적용합니다.                      |
| `md-link-check`   | Markdown 파일 링크·앵커·목차·헤딩 구조를 검사합니다.                                    |

### 인프라 작업 흐름

| 스킬                     | 한 줄 설명                                                          |
|--------------------------|---------------------------------------------------------------------|
| `spec-driven-infra`      | 큰 인프라 변경 전에 요구 사항과 명세를 먼저 작성합니다.             |
| `planning-and-breakdown` | 큰 작업을 실행 순서·영향 범위·완료 기준이 있는 단계로 나눕니다.     |
| `incremental-change`     | 여러 자원에 걸친 IaC 변경을 작은 단위로 나눠 적용합니다.            |
| `doubt-driven-infra`     | 운영·보안·되돌릴 수 없는 변경을 확정 전에 반대 입장에서 검토합니다. |
| `shipping-checklist`     | 운영 배포·단계적 출시 전 점검 목록을 적용합니다.                    |
| `debugging-and-recovery` | 서비스·빌드·배포 장애의 근본 원인을 추측 없이 단계별로 찾습니다.    |

### 코드와 검사

| 스킬                     | 한 줄 설명                                                        |
|--------------------------|-------------------------------------------------------------------|
| `bash-script-template`   | Bash 스크립트에 헤더·로깅·에러 처리·`main()` 구조를 적용합니다.   |
| `python-script-template` | Python 스크립트에 표준 구조·로깅·argparse·에러 처리를 적용합니다. |
| `testing-guide`          | AAA 패턴, 경계값·동등 분할, 경계 조건으로 테스트를 작성합니다.    |
| `security-tools`         | IP·JSON 마스킹, AWS·Git 보안 점검 스크립트의 사용법을 안내합니다. |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 기본 제공 스킬

Claude Code에 포함된 스킬입니다. 고정 동작을 실행하는 내장 명령과 달리, Claude에게 절차를 알려 주고 도구로 작업하게 합니다. 공식 명령 참조 문서(Commands)에서 Purpose가 **Skill**로 표시됩니다.

| 스킬                        | 한 줄 설명                                                    |
|-----------------------------|---------------------------------------------------------------|
| `/init`                     | 저장소를 분석해 `CLAUDE.md` 초안을 만듭니다.                  |
| `/code-review`              | 현재 diff나 PR의 정확성 문제를 검토합니다.                    |
| `/security-review`          | 현재 branch의 변경을 보안 관점에서 검토합니다.                |
| `/simplify`                 | 바뀐 코드의 재사용·단순화·효율 개선점을 찾아 고칩니다.        |
| `/run`                      | 프로젝트 앱을 실행해 변경이 실제로 동작하는지 확인합니다.     |
| `/loop`                     | 명령이나 요청을 정해진 간격으로 반복 실행합니다.              |
| `/schedule`                 | 정해진 시각에 실행되는 클라우드 에이전트(routine)를 만듭니다. |
| `/claude-api`               | Claude API·SDK 사용법, 모델 ID, 가격을 참고합니다.            |
| `/update-config`            | `settings.json`의 권한·hook·환경 변수를 설정합니다.           |
| `/fewer-permission-prompts` | 자주 쓰는 읽기 명령을 허용 목록에 넣어 확인 요청을 줄입니다.  |

- `/doctor`(설치 점검), `/batch`, `/debug`, `/verify`도 기본 제공 스킬입니다. 일부는 사용자가 직접 호출할 때만 실행됩니다.
- 모든 기본 제공 스킬을 끄려면 `disableBundledSkills` 설정을 씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. claude.ai 계정 스킬

claude.ai 계정으로 로그인한 세션은 계정에서 켠 스킬을 받아 옵니다. 목록에는 `anthropic-skills:이름`으로 보이며, 내가 만든 파일이 아니라 계정에서 내려받은 것입니다.

| 스킬                             | 한 줄 설명                                       |
|----------------------------------|--------------------------------------------------|
| `anthropic-skills:pdf`           | PDF 읽기·병합·분할·양식 작성·OCR을 처리합니다.   |
| `anthropic-skills:docx`          | Word 문서를 만들거나 읽고 고칩니다.              |
| `anthropic-skills:xlsx`          | 스프레드시트를 열고 정리하거나 새로 만듭니다.    |
| `anthropic-skills:pptx`          | PowerPoint 발표 자료를 만들거나 읽고 고칩니다.   |
| `anthropic-skills:skill-creator` | 새 스킬을 만들고 평가(eval)로 동작을 측정합니다. |
| `anthropic-skills:deep-research` | 여러 출처를 조사해 종합 보고서를 씁니다.         |

Cowork·클라우드 세션은 내 컴퓨터의 `~/.claude/skills/`를 읽지 않습니다. 개인 스킬을 그곳에서 쓰려면 claude.ai 계정에서 켜거나 저장소의 `.claude/skills/`에 commit합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 호출 방법

스킬은 사용자와 Claude 모두 호출할 수 있습니다.

| 방법      | 예시                    | 설명                                             |
|-----------|-------------------------|--------------------------------------------------|
| 직접 호출 | `/git-commit-rule`      | 메시지 맨 앞에 이름을 쓰면 바로 실행             |
| 인수 전달 | `/code-review high`     | 이름 뒤 문자열이 `$ARGUMENTS`로 전달             |
| 자동 선택 | "이 변경을 commit해 줘" | Claude가 `description`을 보고 맞는 스킬을 불러옴 |
| 목록 확인 | `/skills`               | 사용 가능한 스킬 검색, 보이기·숨기기 설정        |

- 문장 중간에 쓴 스킬 이름은 실행 허락일 뿐 바로 실행하지 않습니다. 확실히 실행하려면 메시지 맨 앞에 씁니다.
- `disable-model-invocation: true`인 스킬은 Claude가 스스로 부르지 않습니다. 배포처럼 부작용이 있는 스킬에 씁니다.
- 대화가 요약(compaction)되면 불러온 스킬의 앞부분만 남을 수 있습니다. 규칙을 놓치기 시작하면 스킬을 다시 호출합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 같은 이름의 우선순위

같은 이름의 스킬이 여러 곳에 있으면 어디에 있는지로 실행 대상이 정해집니다.

| 같은 이름이 있는 곳             | 실행되는 것                                           |
|---------------------------------|-------------------------------------------------------|
| 개인 스킬과 프로젝트 스킬       | **개인 스킬** (enterprise > 개인 > 프로젝트)          |
| 내 스킬과 기본 제공 스킬        | 내 스킬. 단, 기본 제공 스킬의 별칭은 원래 스킬 실행   |
| 스킬과 `.claude/commands/` 파일 | 스킬                                                  |
| 플러그인 스킬과 다른 스킬       | 둘 다 사용. 플러그인은 `/플러그인:스킬` 이름으로 구분 |
| 계정 동기화 스킬과 다른 스킬    | 다른 스킬. 동기화 스킬은 전체 이름으로만 실행         |

🟡 저장소에 넣은 프로젝트 스킬이 반영되지 않는 것처럼 보이면, 같은 이름의 개인 스킬이 `~/.claude/skills/`에 있는지 먼저 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 7. 업무별 선택 예시

| 업무                    | 선택할 스킬                                                           |
|-------------------------|-----------------------------------------------------------------------|
| 새 저장소에서 작업 시작 | `repo-governance` → 저장소 지침 확인                                  |
| 서버 구성 변경 계획     | `spec-driven-infra` → `planning-and-breakdown` → `doubt-driven-infra` |
| Ansible·Terraform 적용  | `incremental-change` → `shipping-checklist`                           |
| 장애 원인 분석          | `debugging-and-recovery`                                              |
| 점검 스크립트 작성      | `bash-script-template` 또는 `python-script-template`, `testing-guide` |
| 문서 작성 후 검사       | `md-link-check`, `readme-template`                                    |
| 변경 검토와 게시        | `/code-review` → `git-commit-rule`                                    |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 목록 유지와 스킬 수정

- 개인 스킬은 SKILL-35의 관리 원본에서 고치고 검증한 뒤 `~/.claude/skills/`에 반영합니다. 설치본만 따로 고치지 않습니다.
- Codex 스킬(`codex_*` 원본)은 Claude가 직접 고치지 않고 상호 검토로 제안합니다.
- 설치본과 원본이 같은지는 파일 해시로 확인합니다. 2026-10-15 기준 14개 스킬·79개 파일이 원본과 같습니다.
- 스킬이 사라졌으면 `~/.claude/skills/.trash/`를 확인합니다. 휴지통 항목은 기본 30일 뒤 정리됩니다.
- `claude plugin validate ~/.claude/skills`로 frontmatter 해석 오류를 찾을 수 있습니다(v2.1.233 이상).
- 스킬을 추가·삭제하면 이 문서의 개수와 표를 함께 고칩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [_reference/claude_code_official_notes.md](../../../_reference/claude_code_official_notes.md) — 버전·스킬 검증 근거 노트
- [Codex 스킬 목록](../codex/codex_skills_catalog.md) — 같은 형식의 Codex 쪽 목록
- Skills: [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) — ★★★☆☆
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

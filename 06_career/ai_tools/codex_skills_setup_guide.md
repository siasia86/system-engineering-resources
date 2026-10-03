# Codex Skills 설정 가이드
<!-- reference: _reference/codex_cli_official_notes.md -->

Codex CLI와 IDE에서 재사용할 skill을 작성·설치하고, 호출과 비활성화 상태를 확인하는 가이드입니다. 처음에는 프로젝트의 `.agents/skills/`에 하나의 작업 절차를 배치하고 명시적으로 호출해 확인하는 방식을 권장합니다. 여러 사람에게 배포하거나 MCP 연결을 함께 제공할 때는 plugin 구성을 참고합니다.

Codex 설치·인증은 [CLI Linux 가이드](codex_cli_linux_guide.md), 기능의 역할 구분은 [Codex 공통 개념](codex_concepts.md#52-agentsmdskillsmcp의-차이)을 먼저 확인합니다. 공식 문서와 GitHub 참고 자료의 확인일은 2026-10-03이며, 명령 예제의 설치·실행 결과는 사용하는 Codex 버전과 환경에서 별도로 확인합니다.

## 목차

| 섹션                                                                                    |
|-----------------------------------------------------------------------------------------|
| [1. 설정 방식 선택](#1-설정-방식-선택) / [2. 저장 위치](#2-저장-위치)                   |
| [3. 사용자 skill 작성](#3-사용자-skill-작성) / [4. 외부 skill 설치](#4-외부-skill-설치) |
| [5. 메타데이터와 MCP](#5-메타데이터와-mcp) / [6. 호출과 검증](#6-호출과-검증)           |
| [7. 비활성화와 복구](#7-비활성화와-복구) / [8. 설정 참고 URL](#8-설정-참고-url)         |

---

## 1. 설정 방식 선택

반복해서 수행할 작업의 입력·절차·출력이 정해져 있으면 skill로 묶습니다. 매 작업에 적용할 저장소 규칙은 `AGENTS.md`에 둡니다.

| 구성        | 사용하는 경우                    | 예시                             |
|-------------|----------------------------------|----------------------------------|
| `AGENTS.md` | 저장소 전반의 작업 규칙          | 사용자 변경 보존, 필수 검사 명령 |
| Skill       | 특정 요청에 적용할 재사용 절차   | 문서 검토, CI 실패 분석          |
| MCP         | 외부 시스템의 도구나 데이터 필요 | 공식 문서 검색, 이슈 조회        |
| Plugin      | skill과 연결 구성을 함께 배포    | 팀용 skill 묶음과 MCP 연결       |

이 구분은 [공식 Customization 안내](https://learn.chatgpt.com/docs/customization/overview)를 기준으로 합니다. skill의 설명은 작업 선택에 쓰이며, 실제 파일·네트워크 접근은 실행 환경의 권한 설정을 따릅니다.

## 2. 저장 위치

아래는 [공식 Build skills 안내](https://learn.chatgpt.com/docs/build-skills#where-to-save-skills)의 로컬 탐색 위치입니다.

| 범위     | 위치                                         | 용도                              |
|----------|----------------------------------------------|-----------------------------------|
| 프로젝트 | `.agents/skills/<skill-name>/SKILL.md`       | 저장소와 함께 관리할 팀 작업 절차 |
| 사용자   | `$HOME/.agents/skills/<skill-name>/SKILL.md` | 여러 저장소에서 사용할 개인 skill |
| 관리자   | `/etc/codex/skills/`                         | 관리자가 제공하는 공통 skill      |
| 시스템   | Codex에 포함                                 | 기본 제공 skill                   |

프로젝트에서는 현재 작업 디렉토리부터 Git 저장소 루트까지의 `.agents/skills/`를 탐색합니다. 같은 `name`이 여러 위치에 있으면 자동 병합하지 않으므로, 목록에서 출처를 확인합니다. symlink로 배치한 경우에는 링크 대상과 접근 가능 여부도 확인합니다.

일부 설치 도구는 사용자 skill을 `~/.codex/skills/`에 배치합니다. 예를 들어 [Vercel skills CLI의 Codex 경로 표](https://github.com/vercel-labs/skills#supported-agents)는 전역 경로를 이렇게 안내합니다. 공식 사용자 경로와 설치 도구의 목적지가 다를 수 있으므로, 프로젝트 범위로 시작하거나 설치 결과의 경로를 확인한 뒤 Codex의 `/skills`에서 발견 여부를 검증합니다.

## 3. 사용자 skill 작성

### 생성 도구 사용

Codex 대화 입력창에서 기본 제공 `skill-creator`를 호출하고 작업 범위와 저장 위치를 함께 전달합니다.

```text
$skill-creator
SE Markdown 문서의 내부 링크와 검증 누락을 검토하는 se-doc-review skill을
이 프로젝트의 .agents/skills/에 만들어 주세요.
문서 경로를 입력받고, 검사 결과와 미검증 항목을 한국어로 보고해 주세요.
본문 수정은 사용자가 요청한 범위에서 수행해 주세요.
```

`$skill-creator`는 Codex 입력창의 호출 문법입니다. Bash에서 실행하는 명령이 아닙니다. 생성한 파일은 저장 위치와 내용을 검토한 뒤 사용합니다.

### 수동 작성 예제

대상 프로젝트 루트에서 디렉토리를 준비합니다. 기존 파일이 있으면 내용을 읽고 필요한 부분을 병합합니다.

```bash
mkdir -p .agents/skills/se-doc-review
```

`.agents/skills/se-doc-review/SKILL.md`에 다음 내용을 작성합니다.

```markdown
---
name: se-doc-review
description: SE Markdown 문서의 내부 링크, 목차, 검사 누락을 검토한다. 문서 검토나 문서 변경 검증을 요청할 때 사용하며, 서버 설정 변경이나 배포에는 사용하지 않는다.
---

# SE 문서 검토

입력은 검토할 Markdown 문서 경로와 사용자가 요청한 검토 범위입니다.

1. 저장소 지침, Git 상태, 대상 문서를 읽고 기존 사용자 변경을 확인합니다.
2. 대상 문서와 직접 연결된 목차·참고 문서를 확인합니다.
3. 저장소가 지정한 링크·헤딩·스타일 검사 도구의 존재 여부를 확인합니다.
4. 사용 가능한 검사를 대상 범위에 실행하고 종료 상태와 warning을 확인합니다.
5. 발견한 문제, 실행한 검사, 미실행 검사와 이유를 한국어로 보고합니다.

사용자의 명시적 지시를 skill 지침보다 우선합니다.
필수 입력이 부족하면 필요한 경로를 질문합니다.
검사 도구가 없거나 필수 자료를 읽지 못하면 미검증으로 표시합니다.
본문 수정은 사용자가 요청한 범위에서 수행합니다.
```

`name`과 `description`은 필수입니다. `description`에는 적용할 요청과 제외할 요청을 쓰고, 본문에는 입력·수행 절차·완료 기준을 적습니다. 자세한 배경 자료는 `references/`, 복사할 템플릿은 `assets/`, 반복 계산이나 파일 처리는 필요할 때 `scripts/`에 둡니다. [공식 skill 작성 안내](https://developers.openai.com/plugins/build/skills)

## 4. 외부 skill 설치

### Codex 기본 설치 도구

Codex 입력창에서 `skill-installer`에 GitHub의 skill 디렉토리를 지정할 수 있습니다. 다음은 외부 skill 설치 요청 예제입니다.

```text
$skill-installer install https://github.com/addyosmani/agent-skills/tree/main/skills/code-review-and-quality
```

설치 도구가 보고한 목적지를 기록하고, `SKILL.md`가 참조하는 파일도 함께 설치됐는지 확인합니다. 기본 생성·설치 도구의 사용법은 [Build skills](https://learn.chatgpt.com/docs/build-skills)를 참고합니다.

### Vercel skills CLI

Node.js와 npm이 준비된 환경에서는 shell에서 실행합니다. 먼저 목록을 확인한 뒤 필요한 skill을 Codex의 프로젝트 범위에 설치합니다.

```bash
npx skills add addyosmani/agent-skills --list
npx skills add addyosmani/agent-skills --skill code-review-and-quality --agent codex
npx skills list --agent codex
```

`--skill`은 설치 대상을 선택하고 `--agent codex`는 적용할 도구를 지정합니다. `--global`을 추가하면 사용자 범위에 설치하므로 2절의 경로 차이를 함께 확인합니다. 명령과 옵션은 [Vercel skills CLI README](https://github.com/vercel-labs/skills)를 기준으로 합니다.

2026-10-03 확인 당시 [Addy Osmani README](https://github.com/addyosmani/agent-skills)는 개별 skill 설치 시 저장소 루트의 공유 `references/`가 함께 복사되지 않는 문제를 안내합니다. 단일 폴더만 설치했다면 필요한 참조 파일을 별도로 확인하거나 저장소 전체를 제공하는 plugin 구성을 검토합니다.

### Plugin으로 설치

여러 skill과 참조 파일을 함께 사용할 때는 저장소의 Codex 설치 안내를 따릅니다. 다음은 Addy Osmani 저장소가 안내하는 예제입니다.

```bash
codex plugin marketplace add addyosmani/agent-skills
codex plugin add agent-skills@agent-skills
codex plugin list --json
```

이 명령은 marketplace 등록과 plugin 설치 상태를 변경합니다. 로컬 `codex-cli 0.160.0`의 `--help`에서 명령과 인수 형식만 확인했으며 실제 설치는 실행하지 않았습니다. 설치 전에는 [Codex 전용 설정 안내](https://github.com/addyosmani/agent-skills/blob/main/docs/codex-setup.md)와 사용하는 버전의 `codex plugin --help`를 확인합니다.

직접 배포할 plugin의 구조와 marketplace 설정은 [공식 Package your plugin 안내](https://developers.openai.com/plugins/build/plugins)를 참고합니다.

## 5. 메타데이터와 MCP

skill의 `agents/openai.yaml`은 선택 사항입니다. 표시 이름과 기본 요청, 암묵적 호출 정책 등을 설정할 수 있습니다.

```yaml
interface:
  display_name: "SE 문서 검토"
  short_description: "SE 문서의 링크와 검증 누락을 확인합니다"
  default_prompt: "지정한 문서를 $se-doc-review skill로 검토해 주세요."

policy:
  allow_implicit_invocation: false
```

`allow_implicit_invocation: false`이면 요청 내용에 따른 자동 선택을 막고 `$se-doc-review`와 같은 명시적 호출을 사용합니다. 기본값은 `true`입니다. [공식 선택 메타데이터 안내](https://learn.chatgpt.com/docs/build-skills#optional-metadata)

MCP가 필요한 skill은 같은 파일에 의존성을 선언할 수 있습니다. 실제 연결 방법은 [CLI 가이드의 MCP 설정](codex_cli_linux_guide.md#7-설정과-agentsmd)을 참고하며, `SKILL.md`에는 사용할 도구와 연결 실패 시 처리 방법을 적습니다. API key와 token은 skill 파일에 기록하지 않습니다.

## 6. 호출과 검증

Codex CLI 또는 IDE 입력창에서 skill 목록을 확인하고 명시적으로 호출합니다.

```text
/skills
$se-doc-review README.md를 검토해 주세요.
```

다음 순서로 확인합니다. 아래 표는 작성한 skill을 검증하기 위한 권장 예제이며, 실제 결과를 기록합니다.

| 확인 대상          | 요청 예제                                            | 기대 결과                                  |
|--------------------|------------------------------------------------------|--------------------------------------------|
| 발견과 명시적 호출 | `$se-doc-review README.md를 검토해 주세요.`          | 지정한 skill과 문서를 선택                 |
| 암묵적 호출        | `README.md의 내부 링크와 검증 누락을 검토해 주세요.` | 암묵적 호출 허용 시 적용 범위에 맞게 선택  |
| 입력 부족          | `$se-doc-review 문서를 검토해 주세요.`               | 검토할 경로가 불명확하면 질문              |
| 범위 밖 요청       | `Nginx 설정을 변경하고 배포해 주세요.`               | 문서 검토 skill을 암묵적으로 선택하지 않음 |
| 도구 부족          | 문서 검토 중 필수 검사 도구가 없음                   | 미실행 검사와 이유를 보고                  |

암묵적 호출을 비활성화했다면 해당 행의 기대 결과는 자동 선택하지 않는 것으로 바꿉니다. 목록에 보이는 것과 작업을 올바르게 수행하는 것은 각각 확인합니다. 변경이 반영되지 않으면 새 세션을 열거나 Codex를 재시작합니다. 검증 요청의 구성은 [공식 Test the skill 안내](https://developers.openai.com/plugins/build/skills#test-the-skill)를 참고합니다.

## 7. 비활성화와 복구

로컬 skill은 `~/.codex/config.toml`의 `[[skills.config]]`로 비활성화할 수 있습니다. 기존 설정에 아래 항목을 병합하고, `path`는 해당 환경의 실제 절대 경로로 바꿉니다.

```toml
[[skills.config]]
path = "/absolute/path/to/project/.agents/skills/se-doc-review/SKILL.md"
enabled = false
```

설정 변경 후 Codex를 재시작합니다. 다시 사용하려면 `enabled = true`로 바꾸거나 해당 비활성화 항목을 제거합니다. 경로 형식은 [공식 비활성화 예제](https://learn.chatgpt.com/docs/build-skills#enable-or-disable-local-codex-skills)를 기준으로 합니다.

skill 본문 변경은 기존 파일을 보관하거나 Git으로 관리하고, 문제가 생기면 자신이 수정한 부분만 복원합니다. 설치 도구로 관리하는 skill은 해당 도구의 제거 절차를 확인합니다. plugin은 skill의 `[[skills.config]]`와 별도로 plugin 관리 기능을 사용합니다.

## 8. 설정 참고 URL

| 자료                                                                                | 참고할 내용                               |
|-------------------------------------------------------------------------------------|-------------------------------------------|
| [openai/plugins](https://github.com/openai/plugins)                                 | 공식 skill·MCP·plugin 패키지 예제         |
| [vercel-labs/skills](https://github.com/vercel-labs/skills)                         | 설치 범위, Codex 선택, 목록·업데이트·제거 |
| [affaan-m/ECC](https://github.com/affaan-m/ECC)                                     | Codex 설정·skill·MCP·agent 역할 예제      |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)               | SE 작업 절차와 Codex 전용 설정 안내       |
| [obra/superpowers](https://github.com/obra/superpowers)                             | 설계·TDD·디버깅·리뷰 workflow             |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 분야별 skill 탐색                         |
| [anthropics/skills](https://github.com/anthropics/skills)                           | skill 작성 템플릿과 Claude용 예제         |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)             | React·UI·문서 검토 skill 예제             |

GitHub star 수와 자료별 용도는 [GitHub 참고 목록](../../_reference/github_references.md#1-aiagent)에 정리합니다. Anthropic 예제의 Claude 전용 도구·호출 지침은 Codex 환경에 맞게 검토합니다.

2026-10-03 확인 당시 [openai/skills README](https://github.com/openai/skills)는 deprecated를 표시하고 후속 자료로 `openai/plugins`를 안내합니다. 공식 Build skills 문서에 남아 있는 과거 카탈로그 링크와 구분하여, 새 배포 예제는 `openai/plugins`에서 확인합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- OpenAI Build skills: [learn.chatgpt.com/docs/build-skills](https://learn.chatgpt.com/docs/build-skills) — ★★★☆☆
- OpenAI Skill 작성: [developers.openai.com/plugins/build/skills](https://developers.openai.com/plugins/build/skills) — ★★★☆☆
- OpenAI Package your plugin: [developers.openai.com/plugins/build/plugins](https://developers.openai.com/plugins/build/plugins) — ★★★☆☆
- OpenAI Customization: [learn.chatgpt.com/docs/customization/overview](https://learn.chatgpt.com/docs/customization/overview) — ★★★☆☆
- GitHub 설정 자료: [GitHub 참고 목록](../../_reference/github_references.md) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-10-03

**마지막 업데이트**: 2026-10-03

© 2026 siasia86. Licensed under CC BY 4.0.

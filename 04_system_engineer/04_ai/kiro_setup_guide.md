# Kiro CLI 설정 가이드

## 목차

| 섹션                                                                             |
|----------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 디렉토리 구조](#2-디렉토리-구조) / [3. Skill 작성](#3-skill-작성) |
| [4. Agent 작성](#4-agent-작성) / [5. Prompt 작성](#5-prompt-작성) / [6. Hook 설정](#6-hook-설정) |
| [7. 설정 검증](#7-설정-검증) / [8. 실전 조합 패턴](#8-실전-조합-패턴) / [9. 참고 자료](#9-참고-자료) |

---

## 1. 개요

Kiro CLI의 커스터마이징은 `~/.kiro/` (글로벌) 또는 `.kiro/` (프로젝트 로컬) 디렉토리 아래
4가지 구성 요소로 이루어집니다.

| 구성 요소 | 위치                | 역할                           |
|-----------|---------------------|--------------------------------|
| Skill     | `skills/*/SKILL.md` | AI 행동 규칙·워크플로 정의     |
| Agent     | `agents/*.json`     | 페르소나·도구 권한·리소스 묶음 |
| Prompt    | `prompts/*.md`      | 반복 사용 프롬프트 템플릿      |
| Hook      | hooks (JSON/sh)     | 특정 시점 자동 실행 동작       |

### 설계 원칙

```
Skill  = 사내 업무 규정 (SOP)     — "위험 작업 전 확인받아라"
Agent  = 직무기술서 (JD)          — "너는 인프라 엔지니어다"
Prompt = 체크리스트 템플릿        — "배포 전 이 항목을 확인해라"
Hook   = 자동화 트리거            — "파일 저장 시 git diff 출력"
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 디렉토리 구조

```
~/.kiro/                           ← 글로벌 (모든 프로젝트 공통)       
├── agents/                                                            
│   ├── infra.json                 ← 인프라 운영 에이전트              
│   └── readonly.json              ← 읽기 전용 안전 에이전트           
├── markdown/                                                          
│   └── STYLE.md                   ← 문서 작성 스타일 가이드           
├── prompts/                                                           
│   └── ansible-create.md          ← Ansible playbook 작성 템플릿      
├── settings/                                                          
│   └── cli.json                   ← CLI 전역 설정                     
└── skills/                                                            
    ├── work-rules/                                                    
    │   └── SKILL.md               ← 공통 작업 규칙                    
    └── infra-rules/                                                   
        └── SKILL.md               ← 인프라 전용 규칙                  
                                                                       
.kiro/                             ← 로컬 (프로젝트별, 글로벌보다 우선)
├── agents/                                                            
├── prompts/                                                           
└── skills/                                                            
```

### 글로벌 vs 로컬 우선순위

| 구분   | 경로           | 적용 범위       | 우선순위 |
|--------|----------------|-----------------|----------|
| 글로벌 | `~/.kiro/`     | 모든 프로젝트   | 낮음     |
| 로컬   | `.kiro/` (CWD) | 해당 프로젝트만 | 높음     |

동일한 이름의 설정이 있으면 로컬(`.kiro/`)이 글로벌(`~/.kiro/`)을 덮어씁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. Skill 작성

Skill은 AI에게 특정 상황에서 어떻게 행동할지 알려주는 Markdown 파일입니다.
레퍼런스 문서(참고 자료)가 아닌, AI가 따라야 할 **워크플로·프로세스**를 기술합니다.

### 3.1 파일 위치

```
~/.kiro/skills/                                                    
└── skill-name/          ← 디렉토리명 = skill 이름 (소문자, 하이픈)
    └── SKILL.md         ← 항상 대문자 SKILL.md                    
```

### 3.2 SKILL.md 구조

모든 SKILL.md는 YAML frontmatter로 시작해야 합니다.

```yaml
---
name: skill-name-with-hyphens
description: >
  Does [what]. Use when [trigger condition].
  Include both what the skill does and when to activate it.
---
```

`description` 작성 규칙:
- 최대 1024자
- AI가 skill을 언제 로드할지 판단하는 핵심 근거
- `Use when` 조건을 명확하게 포함
- 워크플로 단계를 설명하지 않음 (본문에 기술)

### 3.3 권장 섹션 구성

```markdown
---
name: infra-operation-rules
description: >
  Defines safe operation rules for infrastructure tasks.
  Use when executing server changes, deployments, or destructive operations.
---

# Infra Operation Rules

## Overview
인프라 작업 시 적용하는 안전 운영 규칙입니다.

## When to Use
- 서버 설정 변경, 서비스 재시작, 배포 작업 시
- terraform apply, ansible-playbook 실행 시
- NOT: 단순 조회 명령어 (ls, cat, ps 등)

## Core Process
1. 작업 대상 환경 확인 (dev / qa / stg / prd)
2. prd 환경이면 변경 내용을 출력하고 확인 요청
3. 롤백 방법 확인 후 작업 진행
4. 작업 완료 후 상태 검증

## Common Rationalizations

| 변명                             | 현실                                      |
|----------------------------------|-------------------------------------------|
| "간단한 작업이라 확인 불필요"    | 간단한 작업도 prd에서는 장애 유발         |
| "롤백 방법은 나중에 생각하면 됨" | 장애 중에는 롤백 방법을 생각할 여유가 없음 |

## Red Flags
- prd 환경에서 확인 없이 apply 실행
- 롤백 계획 없는 배포

## Verification
- [ ] 작업 대상 환경 확인 완료
- [ ] prd인 경우 확인 완료
- [ ] 롤백 방법 문서화
- [ ] 작업 후 상태 검증 완료
```

### 3.4 skill:// vs file:// 로드 방식

| 방식       | 로드 시점               | 토큰 소비   | 사용 시기                  |
|------------|-------------------------|-------------|----------------------------|
| `skill://` | AI가 필요하다고 판단 시 | 필요할 때만 | 상황별 규칙 (운영 규칙 등) |
| `file://`  | 에이전트 시작 시 항상   | 항상 소비   | 항상 참고해야 하는 파일    |

```json
"resources": [
  "skill://work-rules",
  "skill://infra-operation-rules",
  "file://~/.kiro/markdown/STYLE.md"
]
```

### 3.5 Skill 작성 원칙

1. **프로세스 우선**: 참고 자료가 아닌 AI가 따를 단계별 워크플로를 작성합니다.
2. **구체적으로**: "테스트를 확인해라"가 아닌 "pytest -v 를 실행하고 통과 여부를 확인해라".
3. **증거 기반 검증**: 체크리스트의 각 항목은 출력 결과 등 증거로 확인 가능해야 합니다.
4. **변명 차단**: AI가 단계를 건너뛸 수 있는 변명을 미리 차단합니다.
5. **토큰 절감**: 불필요한 섹션을 제거합니다. Skill은 영어로 작성하면 토큰이 절약됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. Agent 작성

Agent는 Skill, 도구 권한, 페르소나를 묶은 JSON 설정 파일입니다.
용도별로 분리하면 불필요한 도구 권한을 제거하여 안전성을 높일 수 있습니다.

### 4.1 파일 위치

```
~/.kiro/agents/infra.json
```

### 4.2 전체 필드 설명

```json
{
  "name": "infra",
  "description": "인프라 운영 전용 에이전트",
  "prompt": "시스템 엔지니어로서 답변해라. 서버 운영, 모니터링, IaC 중심.",
  "tools": ["shell", "read", "write", "aws"],
  "allowedTools": ["fs_read", "grep", "glob"],
  "toolsSettings": {
    "execute_bash": { "autoAllowReadonly": true },
    "fs_write": { "allowedPaths": ["~/ansible/**", "~/terraform/**"] }
  },
  "resources": [
    "skill://work-rules",
    "skill://infra-operation-rules",
    "file://~/.kiro/markdown/STYLE.md"
  ],
  "hooks": {
    "agentSpawn": [
      { "command": "hostname && uptime", "description": "서버 상태" }
    ]
  },
  "keyboardShortcut": "ctrl+shift+i",
  "welcomeMessage": "인프라 운영 에이전트입니다. 무엇을 도와드릴까요?"
}
```

### 4.3 주요 필드 비교

| 필드           | 역할                             | 없으면?                    |
|----------------|----------------------------------|----------------------------|
| `tools`        | 사용 가능한 도구 카테고리 활성화 | 해당 도구 자체를 사용 불가 |
| `allowedTools` | 확인 없이 자동 승인할 도구       | 매번 y/n 확인 프롬프트     |
| `prompt`       | 에이전트 페르소나 정의           | 기본 에이전트 동작         |
| `resources`    | skill/파일 자동 로드             | 추가 규칙 없음             |

### 4.4 tools 카테고리 → 실제 도구 매핑

| `tools` 카테고리 | 포함 도구                         |
|------------------|-----------------------------------|
| `read`           | `fs_read`, `glob`, `grep`, `code` |
| `write`          | `fs_write`                        |
| `shell`          | `execute_bash`                    |
| `aws`            | `use_aws`                         |
| `delegate`       | `use_subagent`                    |
| `knowledge`      | `web_search`, `web_fetch`         |

### 4.5 실행 흐름

```
tools 확인 → allowedTools 확인 → 실행

1단계: tools에 해당 카테고리가 있나?
   shell ✅ → execute_bash 사용 가능
   없으면 → 호출 불가

2단계: allowedTools에 해당 도구가 있나?
   execute_bash ✅ → 자동 실행 (확인 없음)
   없으면 → 매번 y/n 확인
```

### 4.6 에이전트 예시 모음

#### 인프라 운영 에이전트

```json
{
  "name": "infra",
  "description": "서버 운영, 모니터링, IaC 작업 전용",
  "prompt": "Senior infrastructure engineer. Focus on server operations, monitoring, IaC.",
  "tools": ["shell", "read", "write", "aws"],
  "allowedTools": ["fs_read", "grep", "glob"],
  "resources": [
    "skill://work-rules",
    "skill://infra-operation-rules",
    "file://~/.kiro/markdown/STYLE.md"
  ],
  "keyboardShortcut": "ctrl+shift+i"
}
```

#### 읽기 전용 안전 에이전트

```json
{
  "name": "readonly",
  "description": "파일 수정·명령 실행 불가 — 조회 전용",
  "tools": ["read"],
  "allowedTools": ["fs_read", "grep", "glob"],
  "keyboardShortcut": "ctrl+shift+r"
}
```

#### 문서 작성 에이전트

```json
{
  "name": "markdown-writer",
  "description": "Markdown 문서 작성 및 수정 전용",
  "prompt": "Technical writer. Follow STYLE.md rules exactly.",
  "tools": ["read", "write", "shell"],
  "allowedTools": ["fs_read", "grep", "glob", "fs_write"],
  "resources": [
    "skill://work-rules",
    "skill://readme-template",
    "file://~/.kiro/markdown/STYLE.md"
  ]
}
```

### 4.7 에이전트 사용법

```bash
# 시작 시 지정
kiro-cli chat --agent infra

# 채팅 중 전환
/agent swap infra

# 에이전트 목록 확인
/agent list
```

### 4.8 오케스트레이션 패턴

여러 에이전트를 조합할 때는 단일 오케스트레이터 패턴을 사용합니다.

```
system-engineer (orchestrator)                  
    ├── delegate → code-reviewer     ← 코드 리뷰
    ├── delegate → security-auditor  ← 보안 감사
    └── delegate → doc-reviewer      ← 문서 검증
```

금지 패턴:
- `code-reviewer` → `security-auditor` 호출 (중첩 금지)
- 라우터 역할만 하는 에이전트 생성 (오케스트레이션은 메인 에이전트 역할)

[⬆ 목차로 돌아가기](#목차)

---

## 5. Prompt 작성

Prompt는 `/prompts <name>` 명령으로 호출하는 재사용 가능한 프롬프트 템플릿입니다.
반복적으로 사용하는 요청(코드 리뷰, 배포 확인, 장애 분석 등)을 파일로 관리합니다.

### 5.1 파일 위치 및 우선순위

| 위치               | 우선순위 |
|--------------------|----------|
| `.kiro/prompts/`   | 1 (최고) |
| `~/.kiro/prompts/` | 2        |

### 5.2 기본 형식

```markdown
<!-- ~/.kiro/prompts/ansible-review.md -->
---
description: Ansible playbook 코드 리뷰
---

아래 Ansible playbook을 리뷰해줘:

## 체크 항목
- [ ] idempotency 보장 여부
- [ ] 하드코딩된 시크릿 없음
- [ ] handler 사용 적절성
- [ ] become 권한 최소화

## 리뷰 대상
$ARGUMENTS
```

### 5.3 인자 사용법

`$ARGUMENTS`는 `/prompts ansible-review <추가 텍스트>` 형태로 전달한 내용으로 치환됩니다.

```
> /prompts ansible-review roles/nginx/tasks/main.yml 을 리뷰해줘
```

### 5.4 프롬프트 예시 모음

#### 배포 전 확인

```markdown
<!-- ~/.kiro/prompts/deploy-check.md -->
---
description: 배포 전 체크리스트 확인
---

배포 전 아래 항목을 순서대로 확인해줘:

1. 현재 브랜치와 커밋 확인: `git log --oneline -5`
2. 미반영 변경사항 확인: `git status`
3. 테스트 통과 여부
4. 롤백 방법

대상: $ARGUMENTS
```

#### 장애 분석

```markdown
<!-- ~/.kiro/prompts/incident-analysis.md -->
---
description: 장애 원인 분석
---

아래 로그를 분석하고 원인과 조치 방법을 정리해줘:

## 분석 항목
- 최초 에러 발생 시각
- 에러 패턴 및 빈도
- 영향 범위
- 예상 원인 (우선순위 순)
- 즉각 조치 방법
- 재발 방지 방법

## 로그
$ARGUMENTS
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. Hook 설정

Hook은 특정 이벤트 시점에 자동으로 실행되는 커스텀 동작입니다.
Agent JSON의 `hooks` 필드 또는 별도 hooks 설정 파일로 관리합니다.

### 6.1 트리거 종류

| 트리거             | 실행 시점        | matcher | 주요 용도                |
|--------------------|------------------|---------|--------------------------|
| `agentSpawn`       | 에이전트 시작 시 | ❌      | 환경 정보 수집           |
| `userPromptSubmit` | 사용자 입력마다  | ❌      | 타임스탬프·컨텍스트 주입 |
| `preToolUse`       | 도구 실행 전     | ✅      | 위험 작업 차단           |
| `postToolUse`      | 도구 실행 후     | ✅      | 로깅·감사 기록           |
| `stop`             | AI 응답 완료 후  | ❌      | lint 자동 실행·포맷팅    |

### 6.2 Exit Code 동작

| Exit Code | 의미                                              |
|-----------|---------------------------------------------------|
| 0         | 성공. STDOUT이 컨텍스트에 추가됨                  |
| 2         | (preToolUse만) 도구 실행 차단. STDERR이 AI에 전달 |
| 기타      | 실패. STDERR이 경고로 표시됨                      |

### 6.3 Hook STDIN (이벤트 데이터)

Hook 스크립트는 JSON 형식의 이벤트 데이터를 STDIN으로 받습니다.

```json
{
  "hook_event_name": "preToolUse",
  "cwd": "/home/user/project",
  "tool_name": "fs_write",
  "tool_input": {
    "path": "/etc/nginx/nginx.conf",
    "command": "create"
  }
}
```

### 6.4 Matcher 패턴

| 패턴       | 매칭 대상                 |
|------------|---------------------------|
| `fs_write` | fs_write 도구만 정확 매칭 |
| `fs_*`     | fs_read, fs_write 등 전체 |
| `@git`     | git MCP 서버의 모든 도구  |
| `@builtin` | 모든 내장 도구            |
| `*`        | 모든 도구 (내장 + MCP)    |

### 6.5 Hook 예시 모음

#### 에이전트 시작 시 서버 상태 자동 수집

```json
{
  "hooks": {
    "agentSpawn": [
      {
        "command": "hostname && uptime && free -h | head -2",
        "description": "서버 기본 상태"
      }
    ]
  }
}
```

#### prd 경로 파일 쓰기 차단

```bash
#!/bin/bash
# ~/.kiro/hooks/block-prd-write.sh
EVENT=$(cat)
PATH_VALUE=$(echo "$EVENT" | jq -r '.tool_input.path // empty')

if echo "$PATH_VALUE" | grep -q '/prd/\|/prd-'; then
  echo "prd 환경 파일 쓰기 차단: $PATH_VALUE" >&2
  echo "prd 환경 파일 수정은 수동으로 진행하세요." >&2
  exit 2
fi
exit 0
```

```json
{
  "hooks": {
    "preToolUse": [
      {
        "matcher": "fs_write",
        "command": "~/.kiro/hooks/block-prd-write.sh",
        "description": "prd 경로 쓰기 차단"
      }
    ]
  }
}
```

#### 위험 명령어 차단

```bash
#!/bin/bash
# ~/.kiro/hooks/block-dangerous-cmd.sh
EVENT=$(cat)
CMD=$(echo "$EVENT" | jq -r '.tool_input.command // empty')

BLOCKED="rm -rf|mkfs|dd if=|shutdown|reboot|systemctl stop"
if echo "$CMD" | grep -qE "$BLOCKED"; then
  echo "위험 명령어 차단: $CMD" >&2
  echo "해당 명령어는 직접 터미널에서 실행하세요." >&2
  exit 2
fi
exit 0
```

#### 도구 실행 감사 로그

```bash
#!/bin/bash
# ~/.kiro/hooks/audit-log.sh
EVENT=$(cat)
TOOL=$(echo "$EVENT" | jq -r '.tool_name')
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "$TIMESTAMP | $TOOL | $(echo "$EVENT" | jq -c '.tool_input')" \
  >> ~/.kiro/audit.log
exit 0
```

```json
{
  "hooks": {
    "postToolUse": [
      {
        "matcher": "*",
        "command": "~/.kiro/hooks/audit-log.sh",
        "description": "모든 도구 실행 감사 로그"
      }
    ]
  }
}
```

#### 파일 변경 후 git diff 자동 표시

```json
{
  "hooks": {
    "postToolUse": [
      {
        "matcher": "fs_write",
        "command": "git diff --stat 2>/dev/null || true",
        "description": "파일 변경 후 diff 표시"
      }
    ]
  }
}
```

### 6.6 Hook 확인

```bash
# 현재 설정된 hook 목록
/hooks

# 감사 로그 실시간 확인
tail -f ~/.kiro/audit.log
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 설정 검증

### 7.1 CLI 설정 (settings/cli.json)

```json
{
  "chat.enableCheckpoint": true,
  "chat.enableContextUsageIndicator": true,
  "chat.disableAutoCompaction": false,
  "chat.enableTodoList": true
}
```

```bash
# 설정 확인
kiro-cli settings chat.enableCheckpoint

# 설정 변경
kiro-cli settings chat.enableCheckpoint true
```

### 7.2 설정 적용 확인 명령어

```bash
# 에이전트 목록 확인
/agent list

# 현재 로드된 컨텍스트 확인
/context show

# 설정된 hook 확인
/hooks

# 사용 가능한 프롬프트 확인
/prompts
```

### 7.3 자주 발생하는 문제

| 증상                              | 원인                             | 해결                              |
|-----------------------------------|----------------------------------|-----------------------------------|
| Skill이 적용되지 않음             | `description`에 트리거 조건 누락 | `Use when ...` 조건 명시          |
| Agent 전환이 안 됨                | JSON 문법 오류                   | `jq . agent.json` 으로 검증       |
| Hook이 실행되지 않음              | 스크립트 실행 권한 없음          | `chmod +x ~/.kiro/hooks/*.sh`     |
| allowedTools 없이 도구 실행 안 됨 | `tools`에 카테고리 미등록        | `tools` 배열에 해당 카테고리 추가 |
| prd 차단 hook이 동작 안 함        | exit 2 미반환 or jq 미설치       | `jq` 설치 후 스크립트 로직 확인   |

[⬆ 목차로 돌아가기](#목차)

---

## 8. 실전 조합 패턴

### 8.1 인프라 운영 세트

신규 서버 운영 또는 IaC 작업 시 권장하는 기본 구성입니다.

```
~/.kiro/                                                               
├── agents/                                                            
│   ├── infra.json          ← 운영 에이전트                            
│   └── readonly.json       ← 조회 전용 에이전트                       
├── hooks/                                                             
│   ├── block-prd-write.sh                                             
│   ├── block-dangerous-cmd.sh                                         
│   └── audit-log.sh                                                   
└── skills/                                                            
    ├── work-rules/                                                    
    │   └── SKILL.md        ← 공통 작업 규칙 (복명복창, 위험 작업 확인)
    └── infra-rules/                                                   
        └── SKILL.md        ← 인프라 운영 규칙 (환경별 처리, 롤백)     
```

### 8.2 Skill 로드 흐름

작업 유형에 따라 적합한 skill을 선택합니다.

```
작업 도착                                                                
    │                                                                    
    ├── 무엇을 만들지 모름?           → interview-me / idea-refine skill 
    ├── 신규 기능/변경 설계?          → spec-driven-development skill    
    ├── 스펙 있음, 작업 분해 필요?    → planning-and-task-breakdown skill
    ├── 코드 구현 중?                 → incremental-implementation skill 
    │   ├── IaC 작업?                 → incremental-change skill         
    │   └── 위험한 비가역 변경?       → doubt-driven-infra skill         
    ├── 오류 발생?                    → debugging-and-recovery skill     
    ├── 코드 리뷰?                    → code-review skill                
    ├── 배포/런칭?                    → shipping-checklist skill         
    └── 문서 작성?                    → readme-template / STYLE.md       
```

### 8.3 단계별 작업 Skill 시퀀스

| 단계 | Skill                    | 목적                    |
|------|--------------------------|-------------------------|
| 설계 | `spec-driven-infra`      | 스펙 먼저, 코드 나중    |
| 분해 | `planning-and-breakdown` | 단계별 작업 목록 생성   |
| 구현 | `incremental-change`     | 작은 단위로 점진적 변경 |
| 검증 | `doubt-driven-infra`     | 비가역 변경 안전 확인   |
| 배포 | `shipping-checklist`     | 배포 전 체크리스트      |

[⬆ 목차로 돌아가기](#목차)

---

## 9. 참고 자료

- addyosmani/agent-skills: [github.com](https://github.com/addyosmani/agent-skills) — ★★★☆☆
- Kiro CLI 공식 문서: [kiro.dev/docs/cli](https://kiro.dev/docs/cli/) — ★★★☆☆
- [kiro_cli_command_reference.md](./kiro_cli_command_reference.md)
- [skills/README.md](../../00_readme.md/skills/README.md)

---

**작성일**: 2026-06-09

**마지막 업데이트**: 2026-06-09

© 2026 siasia86. Licensed under CC BY 4.0.

---
name: github-references
description: 참고할 만한 GitHub 저장소 목록 (Codex Skills·AI/Agent, Harness/Loop, Packer/IaC, 도구).
tags:
  - github
  - git
  - repository
last_checked: 2026-10-03
sources:
  - https://github.com/gitleaks/gitleaks
  - https://github.com/addyosmani/agent-skills
  - https://github.com/marcinbojko/hv-packer
  - https://github.com/Baune8D/packer-windows-desktop
  - https://github.com/obra/superpowers
  - https://github.com/affaan-m/ECC
  - https://github.com/anthropics/skills
  - https://github.com/VoltAgent/awesome-agent-skills
  - https://github.com/vercel-labs/skills
  - https://github.com/vercel-labs/agent-skills
  - https://github.com/openai/plugins
  - https://github.com/openai/skills
  - https://github.com/mattpocock/skills
  - https://github.com/multica-ai/andrej-karpathy-skills
  - https://github.com/garrytan/gstack
  - https://github.com/OthmanAdi/planning-with-files
  - https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering
  - https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
  - https://github.com/pbakaus/impeccable
  - https://github.com/K-Dense-AI/scientific-agent-skills
  - https://github.com/github/awesome-copilot
  - https://github.com/agentskills/agentskills
  - https://github.com/composio-community/awesome-codex-skills
  - https://github.com/microsoft/skills
  - https://github.com/openai/codex
  - https://github.com/openai/symphony
  - https://github.com/anthropics/claude-quickstarts
  - https://github.com/snarktank/ralph
  - https://github.com/langchain-ai/deepagents
  - https://github.com/SWE-agent/mini-swe-agent
  - https://github.com/ai-boost/awesome-harness-engineering
  - https://github.com/walkinglabs/awesome-harness-engineering
---

# GitHub References

참고할 만한 GitHub 저장소 목록입니다.

## 목차

| 섹션                                                                                                               |
|--------------------------------------------------------------------------------------------------------------------|
| [1. AI/Agent](#1-aiagent) / [2. Packer/IaC](#2-packeriac) / [3. 도구](#3-도구) / [4. Harness/Loop](#4-harnessloop) |

## 1. AI/Agent

Codex skill 설정 절차는 [Codex Skills 설정 가이드](../06_career/ai_tools/codex_skills_setup_guide.md)에서 확인합니다. 아래 20개는 개발 절차, 분야별 예제, 공식 명세와 탐색 도구를 함께 살펴볼 참고 목록입니다.

GitHub stars는 2026-10-03 GitHub REST API의 `stargazers_count` 조회값입니다. 용도와 Codex 지원 근거는 각 저장소의 README에서 확인했습니다. 실제 clone·정적 검토 상태는 [41 참고 기록](https://github.com/siasia86/41_clone-repo/blob/yunli/docs/reference_repositories.md)에서 관리하며, 설치·실행과 Windows 동작 검증은 이 목록 작성의 결과가 아닙니다.

### 1.1. 개발 행동과 엔지니어링 절차

| 저장소                                                                                                                        | GitHub stars | 참고할 내용                                             | Codex 사용 근거                               |
|-------------------------------------------------------------------------------------------------------------------------------|--------------|---------------------------------------------------------|-----------------------------------------------|
| [obra/superpowers](https://github.com/obra/superpowers)                                                                       | 294,547      | 설계·TDD·디버깅·리뷰 절차                               | README에 Codex App·CLI 안내                   |
| [mattpocock/skills](https://github.com/mattpocock/skills)                                                                     | 274,833      | 요구사항 정리, 설계, TDD, 에이전트용 문서 작성          | Codex 설치 절 제공; native plugin은 계획 단계 |
| [affaan-m/ECC](https://github.com/affaan-m/ECC)                                                                               | 271,496      | 설정·skill·MCP·hook·agent 구성                          | Codex sync 지원과 플랫폼별 지원 범위 안내     |
| [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)                                     | 216,611      | 가정 명시, 단순성, 필요한 부분만 수정, 검증 가능한 목표 | CLAUDE.md 중심; Codex용 지침으로 옮길 때 검토 |
| [garrytan/gstack](https://github.com/garrytan/gstack)                                                                         | 134,824      | 제품·설계 검토, 코드 리뷰, 브라우저 QA, 배포 절차       | Other AI Agents 절에 --host codex 제공        |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)                                                         | 100,593      | API 설계, 코드 품질, TDD, 요구사항 정리                 | Codex 전용 설정 안내와 skills CLI 설치 안내   |
| [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files)                                             | 27,263       | 계획·발견·진행 상태를 파일로 유지하고 세션 복구         | docs/codex.md 제공; hook 동작은 별도 확인     |
| [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) | 18,062       | 컨텍스트 관리, agent 구조, 평가 절차                    | README에 Codex·공통 Agent Skills 배치 안내    |

Karpathy skills는 Karpathy의 관찰을 바탕으로 multica-ai가 관리하는 커뮤니티 가이드입니다. 원문의 `CLAUDE.md` 배치 예제를 Codex의 자동 탐색·설치 완료로 해석하지 않습니다.

gstack은 README에 Codex host 설치를 안내합니다. `/codex`를 통한 외부 검토 기능과 Codex 자체를 host로 선택하는 설치는 각각의 사용 방식이며, 선택한 CLI의 설치·인증과 부가 도구 의존성을 확인합니다.

### 1.2. 분야별 skill과 작성 예제

| 저장소                                                                                          | GitHub stars | 참고할 내용                                   | Codex 사용 근거                            |
|-------------------------------------------------------------------------------------------------|--------------|-----------------------------------------------|--------------------------------------------|
| [anthropics/skills](https://github.com/anthropics/skills)                                       | 179,437      | skill 작성 템플릿, 문서·디자인 등 분야별 예제 | Claude용 예제의 도구·호출 지침 검토        |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 132,609      | UI/UX 설계 자료와 구현 지침                   | CLI에 --ai codex, README에 PowerShell 안내 |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable)                                     | 74,464       | 프런트엔드 디자인 검토와 개선                 | Codex payload와 Windows launcher·hook 안내 |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)     | 47,402       | 과학·연구 작업의 skill과 참조 자료 구조       | Codex 지원 표기; Windows는 WSL2 전제       |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)                         | 31,857       | React·UI 구현과 검토 예제                     | 표준 SKILL.md 구조와 skills CLI 설치 안내  |

### 1.3. 공식 명세, 설치 도구와 탐색 목록

| 저장소                                                                                                | GitHub stars | 참고할 내용                              | Codex 사용 근거                                    |
|-------------------------------------------------------------------------------------------------------|--------------|------------------------------------------|----------------------------------------------------|
| [github/awesome-copilot](https://github.com/github/awesome-copilot)                                   | 39,643       | custom agent·지침·skill·hook 예제 탐색   | Copilot용 구성을 Codex에 맞게 검토                 |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)                   | 35,132       | 공식·커뮤니티 skill의 분야별 탐색        | Codex 호환과 경로 안내; 개별 항목은 원문 확인      |
| [vercel-labs/skills](https://github.com/vercel-labs/skills)                                           | 33,007       | 설치·목록·업데이트·제거 CLI              | Codex 대상과 설치 범위 선택 지원                   |
| [agentskills/agentskills](https://github.com/agentskills/agentskills)                                 | 25,867       | Agent Skills 형식·명세·문서              | 공통 형식과 검증 기준을 참고하는 명세 저장소       |
| [composio-community/awesome-codex-skills](https://github.com/composio-community/awesome-codex-skills) | 16,743       | Codex 작업 예제와 외부 앱 자동화 skill   | Codex용 설치 안내; 앱 연결·인증은 별도 필요        |
| [openai/plugins](https://github.com/openai/plugins)                                                   | 7,270        | OpenAI 공식 skill·MCP·plugin 패키지 예제 | Codex plugin 예제 저장소                           |
| [microsoft/skills](https://github.com/microsoft/skills)                                               | 3,073        | Microsoft SDK·Azure·MCP·agent 예제       | 표준 skill 구조와 skills CLI 안내; SDK 의존성 검토 |

[openai/skills](https://github.com/openai/skills)는 27,853 stars이며, 2026-10-03 README에 deprecated 안내와 `openai/plugins` 후속 링크가 있습니다. 과거 자료의 출처를 확인할 때 참고하고, 새 OpenAI plugin 예제는 후속 저장소에서 확인합니다.

### 1.4. Windows에서 확인할 범위

gstack README는 Windows 11의 Git Bash 또는 WSL 사용과 Bun·Node.js를 안내합니다. Windows의 일부 기능에는 PowerShell·C++ build 도구 등 추가 조건이 있으며, macOS용 브라우저 연동과 Windows의 브라우저 실행 방식도 다릅니다.

UI UX Pro Max와 Impeccable에는 Windows 관련 안내가 있고, scientific-agent-skills는 Windows에서 WSL2를 전제로 합니다. 이것은 각 저장소가 문서에 명시한 범위이며 이 환경에서 실행을 검증한 결과는 아닙니다.

자료를 검토할 때는 작업 목적에 필요한 skill을 선택하고, 참조 파일·scripts·hook·MCP 의존성을 함께 확인합니다. `.agents/skills/`와 도구별 `.codex/skills/` 설치 위치는 [설정 가이드의 저장 위치](../06_career/ai_tools/codex_skills_setup_guide.md#2-저장-위치)와 해당 도구의 실제 발견 결과를 대조합니다.

## 2. Packer/IaC

- hv-packer: [github.com/marcinbojko/hv-packer](https://github.com/marcinbojko/hv-packer) — ★★☆☆☆
- packer-windows-desktop: [github.com/Baune8D/packer-windows-desktop](https://github.com/Baune8D/packer-windows-desktop) — ★★☆☆☆

## 3. 도구

- gitleaks: [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) — ★★★☆☆

## 4. Harness/Loop

2026-10-03 각 저장소의 README와 Symphony SPEC을 확인한 참고 목록입니다. 아래는 별도 하네스·루프 구현과 자료 모음이며, 위 20개 skill 참고 목록과 구분합니다. clone·설치·실행·Windows 동작 검증은 이 목록 작성의 결과가 아닙니다.

| 저장소                                                                                                | 유형                     | 참고할 내용                                                      | 실행·지원 범위                                               |
|-------------------------------------------------------------------------------------------------------|--------------------------|------------------------------------------------------------------|--------------------------------------------------------------|
| [openai/codex](https://github.com/openai/codex)                                                       | 에이전트 런타임          | 대화·도구·승인·sandbox를 연결하는 구현 구조                      | Codex 구현 원문; 모든 코드를 skill로 설치하는 저장소가 아님  |
| [openai/symphony](https://github.com/openai/symphony)                                                 | 작업 오케스트레이터      | WORKFLOW.md·작업별 workspace·동시 실행·재시도 관리               | engineering preview; SPEC과 Elixir 참조 구현의 요구사항 확인 |
| [anthropics/claude-quickstarts](https://github.com/anthropics/claude-quickstarts)                     | 장기 실행 예제           | autonomous-coding의 initializer/coding agent·기능 목록·진행 기록 | Claude Agent SDK·인증 필요; Codex native 구현이 아님         |
| [snarktank/ralph](https://github.com/snarktank/ralph)                                                 | 외부 반복 실행기         | 작은 PRD 항목·새 context·progress.txt·Git·반복 상한              | README는 Amp/Claude Code 지원; Bash·jq와 선택 도구 확인      |
| [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents)                                 | agent harness 프레임워크 | 계획·파일·sub-agent·context 관리·상태 backend                    | 모델 API 기반 프레임워크; Codex skill 설치와 구분            |
| [SWE-agent/mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)                               | 최소 실행 구현           | 단순한 Bash 행동·선형 이력·subprocess 기반 피드백                | Python·Bash·모델 연결과 sandbox 실행 환경 확인               |
| [ai-boost/awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering)       | 자료 모음·template       | AGENTS·PLAN·검증·메모리·권한·관찰 항목 탐색                      | 참고 목록; 연결된 구현의 지원과 신뢰 범위는 각각 검토        |
| [walkinglabs/awesome-harness-engineering](https://github.com/walkinglabs/awesome-harness-engineering) | 자료 모음·학습 안내      | 하네스 도구·설계 사례·학습 자료 탐색                             | 참고 목록; 설치·실행 가능한 단일 bundle이 아님               |

Symphony는 신뢰하는 환경에서 시험하는 engineering preview로 명시되어 있습니다. Ralph README의 기본 반복 상한은 10회이며, 선택한 도구의 인증과 검사 명령을 별도로 설정합니다. 지원이 제안된 PR만으로 현재 Codex 지원을 확정하지 않습니다.

Windows에서는 PowerShell·Git Bash·WSL의 경로·인자·종료 코드와 각 실행기의 shell·SDK·sandbox 요구사항을 확인합니다. gstack·planning-with-files의 절차와 상태 파일 패턴은 [개발 행동 목록](#11-개발-행동과-엔지니어링-절차)에서 함께 참고할 수 있습니다.

개념과 적용 예시는 [Harness Engineering](../06_career/ai_tools/harness_engineering.md#6-실전-적용)과 [Loop Engineering](../06_career/ai_tools/loop_engineering.md#5-루프-설계-예시), 실제 개선 단계의 중앙 기준은 [31 workflow](https://github.com/siasia86/31_governances/blob/yunli/.governance/repository/agent_skill_improvement_workflow.md)에서 관리합니다.

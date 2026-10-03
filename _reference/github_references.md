---
name: github-references
description: 참고할 만한 GitHub 저장소 목록 (Codex Skills·AI/Agent, Packer/IaC, 도구).
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
---

# GitHub References

참고할 만한 GitHub 저장소 목록입니다.

## 목차

| 섹션                                                                           |
|--------------------------------------------------------------------------------|
| [1. AI/Agent](#1-aiagent) / [2. Packer/IaC](#2-packeriac) / [3. 도구](#3-도구) |

## 1. AI/Agent

Codex skill 설정 절차는 [Codex Skills 설정 가이드](../06_career/ai_tools/codex_skills_setup_guide.md)에서 확인합니다. 아래 star 수는 2026-10-03 조회 당시 GitHub의 반올림 표시값이며, 실제 설치·실행 검증 결과와 구분합니다.

| 저장소                                                                              | GitHub stars | Codex 설정에 참고할 내용                                  |
|-------------------------------------------------------------------------------------|--------------|-----------------------------------------------------------|
| [obra/superpowers](https://github.com/obra/superpowers)                             | 약 294.5k    | Codex 설치 안내, 설계·TDD·디버깅·리뷰 절차                |
| [affaan-m/ECC](https://github.com/affaan-m/ECC)                                     | 약 271.3k    | Codex 설정·skill·MCP·agent 역할 예제                      |
| [anthropics/skills](https://github.com/anthropics/skills)                           | 약 179.4k    | 작성 템플릿과 Claude용 예제, Codex 적용 시 도구 지침 검토 |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)               | 약 100.5k    | SE 작업 절차, Codex 전용 설치·문제 해결 안내              |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 약 35.1k     | 공식·커뮤니티 skill을 분야별로 탐색                       |
| [vercel-labs/skills](https://github.com/vercel-labs/skills)                         | 약 33.0k     | Codex 대상 설치·목록·업데이트·제거 CLI                    |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)             | 약 31.8k     | React·UI·문서 검토 skill 예제                             |
| [openai/plugins](https://github.com/openai/plugins)                                 | 약 7.3k      | 현재 OpenAI 공식 skill·MCP·plugin 패키지 예제             |

설치·관리 도구는 Vercel skills CLI, SE 절차는 Addy Osmani, 설정 예제는 ECC를 먼저 참고하는 순서를 권장합니다. 개별 skill의 참조 파일 포함 여부와 사용하는 Codex 버전의 지원 범위를 함께 확인합니다.

[openai/skills](https://github.com/openai/skills)는 약 27.8k stars이며, 2026-10-03 README에 deprecated 안내와 `openai/plugins` 후속 링크가 있습니다. 새 plugin 배포 예제는 후속 저장소를 우선 확인합니다.

## 2. Packer/IaC

- hv-packer: [github.com/marcinbojko/hv-packer](https://github.com/marcinbojko/hv-packer) — ★★☆☆☆
- packer-windows-desktop: [github.com/Baune8D/packer-windows-desktop](https://github.com/Baune8D/packer-windows-desktop) — ★★☆☆☆

## 3. 도구

- gitleaks: [github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) — ★★★☆☆

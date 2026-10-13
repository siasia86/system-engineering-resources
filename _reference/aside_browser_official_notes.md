---
name: aside-browser-official-notes
description: Aside AI 브라우저의 플랫폼·기능·요금·권한·데이터 처리에 관한 공식 참조 노트
tags:
  - aside
  - ai-browser
  - browser-agent
  - automation
last_checked: 2026-10-13
sources:
  - https://aside.com/
  - https://aside.com/download
  - https://aside.com/pricing
  - https://aside.com/features/browser-agent
  - https://aside.com/features/password-manager
  - https://aside.com/features/memory
  - https://docs.aside.com/help/get-started
  - https://docs.aside.com/help/tasks
  - https://docs.aside.com/help/ai
  - https://docs.aside.com/help/security
  - https://docs.aside.com/help/automation
  - https://docs.aside.com/help/memory
  - https://docs.aside.com/help/privacy
  - https://docs.aside.com/help/subscription
  - https://docs.aside.com/help/developers
  - https://docs.aside.com/changelog/native
  - https://aside.com/policy/privacy
  - https://aside.com/policy/terms
  - https://www.ycombinator.com/companies/aside
  - https://github.com/at-inc/aside-benchmarks
---

# Aside AI 브라우저 공식 참조 노트

## 1. 확인 범위

2026-10-13 기준 `aside.com`의 Aside AI 브라우저를 조사했습니다. 공식 제품·도움말·요금·정책과 제작사가 공개한 벤치마크 자료를 사용했습니다. 설치·로그인·결제·브라우저 자동화는 실행하지 않았습니다.

본문: [Aside AI 브라우저 가이드](../06_career/ai_tools/aside_browser_guide.md).

YC 회사 페이지는 Aside를 Fall 2025 기업으로 소개하고 공식 사이트를 `aside.com`으로 연결합니다. 회사명은 정책 문서의 Aside Computer Inc.를 기준으로 기록합니다. [YC](https://www.ycombinator.com/companies/aside), [이용약관](https://aside.com/policy/terms).

## 2. 플랫폼과 버전

| 항목            | 확인 결과                                      | 출처                                                   |
|-----------------|------------------------------------------------|--------------------------------------------------------|
| 데스크톱        | macOS·Windows 다운로드 안내                    | [Download](https://aside.com/download)                 |
| macOS 최소 버전 | 도움말에 15.0 이상 명시                        | [Get started](https://docs.aside.com/help/get-started) |
| Windows 지원    | v1.0.914.1에서 공식 제공 공지                  | [Changelog](https://docs.aside.com/changelog/native)   |
| 브라우저 버전   | 확인한 변경 이력의 상단 항목 v1.0.928.1        | [Changelog](https://docs.aside.com/changelog/native)   |
| Linux·모바일    | 조사한 다운로드·도움말에서 설치 지원 확인 못함 | [Download](https://aside.com/download)                 |

브라우저 버전과 AI 구성요소 버전은 동일한 값이라고 가정하지 않습니다. Windows의 최소 OS 버전·CPU 아키텍처는 미확인입니다.

## 3. 기능과 연결

- 웹사이트·계정·로컬 파일을 이용하는 다단계 작업. [Tasks](https://docs.aside.com/help/tasks).
- `Guard` 기본값, `Read only`·`Full access`와 `Allow`·`Ask`·`Deny` 규칙. [Permissions](https://docs.aside.com/help/security).
- `Aside`·`Subscription`·`API` 모델 공급자 유형. ChatGPT Plus/Pro·Claude Pro/Max·GitHub Copilot 구독 연결 안내. [AI providers](https://docs.aside.com/help/ai).
- Cron은 새 작업, Heartbeat는 기존 대화 재개. [Routines](https://docs.aside.com/help/automation).
- Markdown 메모리의 로컬 보관·편집과 보존 기간 설정. [Memory 기능](https://aside.com/features/memory), [Memory 설정](https://docs.aside.com/help/memory).
- 비밀번호 자동 입력과 사용 기록은 공식 기능 설명이며 독립 보안 검증은 미실행. [Vault](https://aside.com/features/password-manager).
- CLI·MCP·REPL 제공, `aside mcp` 연결 방식. [Developer tools](https://docs.aside.com/help/developers).

구독 연결 지원은 Aside의 안내이며 각 공급자의 계정·사용 한도·승인 조건을 대신 보장하지 않습니다.

## 4. 가격과 확인된 차이

월간 선택 상태의 공식 요금 페이지 기준입니다. [Pricing](https://aside.com/pricing).

| 플랜       | 표시 가격  | 대표 조건                                    |
|------------|------------|----------------------------------------------|
| Free       | USD 0      | 월 500 credits, 활성 routine 최대 3개        |
| Pro        | USD 20/월  | Free 사용량 3배, Ultrabrowse, routine 무제한 |
| Max        | USD 200/월 | Pro 포함, Free 사용량 40배로 표기            |
| Enterprise | 문의       | 팀·계정·권한 관리 안내                       |

Max 사용량은 요금 페이지의 **40배**와 구독 도움말의 **30배**가 다릅니다. 실제 부여량은 앱의 `Settings > Plan & Usage`에서 확인합니다. 외부 구독·API 비용과 Aside credits도 별개로 설명됩니다. [Subscription](https://docs.aside.com/help/subscription).

## 5. 데이터 처리와 근거의 한계

홈페이지는 로컬 보관과 LLM 공급자에 데이터가 공유되지 않는다는 문구를 사용합니다. 개인정보 정책 §4는 호스팅 모델에 프롬프트·선택된 화면·파일 등 작업 문맥이 전달될 수 있다고 명시합니다. “로컬 우선”을 외부 전송이 전혀 없다는 뜻으로 해석하지 않습니다. [홈페이지](https://aside.com/), [개인정보 정책](https://aside.com/policy/privacy).

정책에는 계정·결제·분석·동기화 등 서버 처리도 나옵니다. 분석 공유는 도움말에서 기본 켜짐으로 안내합니다. [Privacy 설정](https://docs.aside.com/help/privacy). 이용약관은 프롬프트 인젝션을 모두 차단한다고 보장하지 않습니다. [Terms §5](https://aside.com/policy/terms).

공개 벤치마크의 Online-Mind2Web 297/300·99.0%, Odysseys 모든 rubric 충족 151/200·75.5%, BU Bench V1 93/100·93.0%는 제작사 보고입니다. 실시간 사이트·사용 모델·평가 방식에 따른 조건을 보존하며 독립 재현은 하지 않았습니다. [공개 결과](https://github.com/at-inc/aside-benchmarks).

## 6. 검증 기록

- 1차 대조: 공식 제품·기능·도움말에서 작업 방식, 모델 연결, 권한, 메모리·routine·개발 도구 확인.
- 2차 대조: 다운로드와 변경 이력, 요금과 구독 도움말, 홈페이지와 개인정보 정책을 교차 확인. Max 사용량과 데이터 전송 설명의 차이를 기록.
- 벤치마크: 홈페이지의 순위 주장과 공개 결과의 평가 조건을 구분.
- 접근 한계: 일부 `.md` 도움말 URL은 웹 도구에서 지원하지 않아 같은 경로의 HTML 문서를 확인.
- 미실행: 설치·공급자 인증·MFA·결제·MCP 연결·routine 실행·보안 구조 검증·벤치마크 재현.

---

**작성일**: 2026-10-13

**마지막 업데이트**: 2026-10-13

© 2026 siasia86. Licensed under CC BY 4.0.

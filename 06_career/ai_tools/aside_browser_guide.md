# Aside AI 브라우저 가이드
<!-- reference: _reference/aside_browser_official_notes.md -->

Aside AI 브라우저의 기능, 지원 플랫폼, 요금, 사용 흐름과 데이터 처리 범위를 정리합니다. 2026-10-13에 공식 사이트와 도움말을 확인한 조사 문서이며 실제 설치·실행 리뷰는 아닙니다.

## 목차

| 섹션                                                                                          |
|-----------------------------------------------------------------------------------------------|
| [1. 제품 개요](#1-제품-개요) / [2. 플랫폼과 시작 방법](#2-플랫폼과-시작-방법)                 |
| [3. 주요 기능](#3-주요-기능) / [4. 모델 연결과 요금](#4-모델-연결과-요금)                     |
| [5. 권한과 데이터 처리](#5-권한과-데이터-처리) / [6. CLI와 MCP](#6-cli와-mcp)                 |
| [7. 성능 주장과 확인 한계](#7-성능-주장과-확인-한계) / [8. 업무 적용 예시](#8-업무-적용-예시) |

---

## 1. 제품 개요

Aside는 웹사이트에 로그인한 상태와 브라우저 문맥을 이용해 여러 단계의 업무를 수행하는 AI 브라우저입니다. 웹 조사, 문서·스프레드시트 작업, 메시지와 내부 도구 처리를 공식 사용 사례로 소개합니다. [공식 Browser agent](https://aside.com/features/browser-agent).

운영사는 정책 문서 기준 Aside Computer Inc.이며, YC는 Fall 2025 기업으로 소개합니다. [이용약관](https://aside.com/policy/terms), [YC 회사 소개](https://www.ycombinator.com/companies/aside).

이 문서의 대상은 **`aside.com`의 AI 브라우저**입니다. 비슷한 이름으로 검색되는 개발 도구·콘텐츠 보관 앱의 설명을 혼합하지 않습니다. 브라우저는 Chromium 기반으로, 공식 변경 이력에도 Chromium 업데이트가 기록됩니다. [변경 이력](https://docs.aside.com/changelog/native).

[⬆ 목차로 돌아가기](#목차)

## 2. 플랫폼과 시작 방법

| 항목         | 확인 내용                                                      |
|--------------|----------------------------------------------------------------|
| macOS        | 다운로드 제공; 시작 도움말은 macOS 15.0 이상 명시              |
| Windows      | 다운로드 제공; v1.0.914.1에서 공식 제공 공지                   |
| Linux·모바일 | 조사한 공식 자료에서 설치 지원 확인 못함                       |
| 버전         | 변경 이력 상단 v1.0.928.1; 설치 파일 버전은 직접 확인하지 않음 |

출처: [다운로드](https://aside.com/download), [시작 도움말](https://docs.aside.com/help/get-started), [변경 이력](https://docs.aside.com/changelog/native). 시작 도움말은 macOS를 중심으로 설명하지만 다운로드·변경 이력은 Windows 지원도 확인해 줍니다. Windows 최소 버전과 CPU 아키텍처는 미확인입니다.

공식 안내의 기본 시작 흐름은 다음과 같습니다. [Get started](https://docs.aside.com/help/get-started).

1. 공식 다운로드에서 OS에 맞는 설치 파일을 받습니다.
2. Aside를 실행하고 계정을 생성하거나 로그인합니다.
3. 필요한 브라우저 프로필의 기록·쿠키·북마크를 가져옵니다.
4. 비밀번호 관리자와 모델 공급자를 설정합니다.
5. 사용할 웹사이트·파일·결과를 지정해 첫 작업을 시작합니다.

여러 사이트에 걸친 작업은 작업 화면, 현재 페이지를 중심으로 한 작업은 사이드 패널에서 시작하도록 안내합니다. [Tasks](https://docs.aside.com/help/tasks).

[⬆ 목차로 돌아가기](#목차)

## 3. 주요 기능

| 기능          | 공식 설명                                                    | 출처                                                            |
|---------------|--------------------------------------------------------------|-----------------------------------------------------------------|
| Browser agent | 로그인한 웹사이트와 파일을 이용한 다단계 작업                | [Browser agent](https://aside.com/features/browser-agent)       |
| Ultrabrowse   | 자료가 많은 조사·복잡한 탐색용 모드                          | [Browser agent](https://aside.com/features/browser-agent)       |
| Memory        | 방문 기록·작업 문맥을 재사용하고 로컬 Markdown으로 보관·편집 | [Memory](https://aside.com/features/memory)                     |
| Aside Vault   | 비밀번호를 에이전트에 보여주지 않는 자동 입력·접근 기록      | [Password Manager](https://aside.com/features/password-manager) |
| Routines      | 일정에 따른 새 작업 또는 기존 대화 재개                      | [Routines](https://docs.aside.com/help/automation)              |
| 후속 지시     | `Queue`는 현재 실행 뒤 적용, `Steer`는 진행 중 방향 수정     | [Tasks](https://docs.aside.com/help/tasks)                      |

Routine은 Cron과 Heartbeat로 구분됩니다. Cron은 별도의 반복 작업을 시작하고 Heartbeat는 기존 대화를 이어갑니다. 제안된 routine은 초안 상태이며 검토 후 활성화하도록 안내합니다. [Routines](https://docs.aside.com/help/automation).

메모리는 `Settings > Memory`에서 확인·편집할 수 있습니다. 보존 기간은 `Never forget`, 30일, 90일이며, 메모리 생성도 끌 수 있습니다. [메모리 설정](https://docs.aside.com/help/memory).

[⬆ 목차로 돌아가기](#목차)

## 4. 모델 연결과 요금

### 4.1 모델 공급자

`Settings > Models > Providers`에서 세 유형을 구성합니다. 다음 지원 목록은 Aside의 안내입니다. [AI providers](https://docs.aside.com/help/ai).

| 유형         | 연결 대상                                                                      |
|--------------|--------------------------------------------------------------------------------|
| Aside        | Aside 플랜에 포함된 모델                                                       |
| Subscription | ChatGPT Plus/Pro, Claude Pro/Max, GitHub Copilot 구독                          |
| API          | OpenAI·Anthropic·OpenRouter·Google·xAI·Vercel AI Gateway·Cloudflare AI Gateway |

구독형 공급자는 OAuth 로그인 흐름으로 연결하도록 설명합니다. 연결 가능 여부와 실제 모델·사용 한도는 계정 및 현재 제공 조건에서 확인해야 합니다. 이 조사에서는 로그인하거나 계정을 연결하지 않았습니다.

### 4.2 요금제

월간 선택 상태의 공식 요금 페이지에서 확인한 금액입니다. [Pricing](https://aside.com/pricing).

| 플랜       | 표시 가격  | 주요 내용                                                                 |
|------------|------------|---------------------------------------------------------------------------|
| Free       | USD 0      | 월 500 credits, routine 최대 3개, 비밀번호 관리자·메모리                  |
| Pro        | USD 20/월  | Free 사용량 3배, Ultrabrowse, routine 무제한, Channels·Cloud handoff 표기 |
| Max        | USD 200/월 | Pro 포함, 사용량 확대, early access                                       |
| Enterprise | 별도 문의  | 팀 설정·공유 계정·권한 관리                                               |

**Max 사용량은 공식 자료끼리 다릅니다.** 요금 페이지는 Free의 40배, 구독 도움말은 30배로 표기합니다. 이 문서는 어느 한 값을 확정하지 않으며, 실제 부여량은 `Settings > Plan & Usage`에서 확인합니다. [Pricing](https://aside.com/pricing), [Subscription](https://docs.aside.com/help/subscription).

Aside credits는 외부 AI 구독·API 비용과 별개입니다. API 키를 연결하면 해당 공급자 계정에 비용이 청구될 수 있습니다. [구독·credits 설명](https://docs.aside.com/help/subscription). 표시 가격을 모든 모델 사용 비용이 포함된 총비용으로 해석하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 권한과 데이터 처리

### 5.1 작업 권한

공식 도움말은 새 작업의 기본 권한을 `Guard`로 설명합니다. [Permissions](https://docs.aside.com/help/security).

| 모드        | 설명                                            |
|-------------|-------------------------------------------------|
| Read only   | 브라우저·파일 문맥을 조사하며 파일 변경 제한    |
| Guard       | 허용된 폴더에서 작업하고 다른 폴더 접근 시 확인 |
| Full access | 컴퓨터 전체의 파일 읽기·쓰기 범위 확대          |

도구 규칙은 `Allow`, `Ask`, `Deny`로 구분되며 Deny가 우선합니다. 파일 권한, 도구 권한과 OS 샌드박스는 별도로 설정합니다. `Read only`의 파일 제한만으로 모든 웹사이트의 쓰기 동작까지 금지된다고 가정하지 않습니다. 실제 요청의 도구 규칙도 확인합니다. [Permissions](https://docs.aside.com/help/security).

결제·게시·메시지 같은 민감한 동작은 사용자 확인을 기다린다고 제품 페이지와 YC 소개가 설명합니다. 실제 확인 화면과 적용 범위는 실행 검증하지 않았습니다. [홈페이지](https://aside.com/), [YC](https://www.ycombinator.com/companies/aside).

### 5.2 로컬 보관과 외부 처리

홈페이지의 로컬 보관 설명만으로 **AI 작업 데이터가 외부로 전혀 전송되지 않는다고 판단하면 안 됩니다.** 개인정보 정책 §4는 호스팅 모델에 프롬프트, 도구 결과, 선택된 화면·스크린샷·파일 등 필요한 문맥이 전달될 수 있다고 명시합니다. [개인정보 정책](https://aside.com/policy/privacy).

| 데이터                   | 공식 정책의 처리 설명                        |
|--------------------------|----------------------------------------------|
| 작업 대화·산출물         | 로컬 보관                                    |
| 호스팅 모델용 작업 문맥  | 해당 AI 공급자로 전송될 수 있음              |
| 계정·결제·지원·분석      | 서버 서비스 이용                             |
| 브라우저·비밀번호 동기화 | 켜져 있으면 암호화된 동기화 데이터 서버 처리 |

제품 소개의 “LLM 공급자와 공유하지 않는다”는 문구와 정책의 호스팅 모델 설명은 차이가 있으므로 함께 확인해야 합니다. [홈페이지](https://aside.com/), [개인정보 정책](https://aside.com/policy/privacy).

분석 공유는 도움말에서 기본 켜짐으로 안내합니다. `Settings > Security & Privacy`에서 조정할 수 있습니다. [Privacy 설정](https://docs.aside.com/help/privacy). 이용약관도 웹페이지·문서의 프롬프트 인젝션을 모두 차단한다고 보장하지 않습니다. [이용약관 §5](https://aside.com/policy/terms).

[⬆ 목차로 돌아가기](#목차)

## 6. CLI와 MCP

공식 개발자 문서는 CLI, MCP 서버와 브라우저 자동화 REPL을 제공합니다. CLI 설치 안내는 macOS와 Windows로 구분되어 있습니다. [Developer tools](https://docs.aside.com/help/developers).

아래는 **이미 CLI가 설치된 환경에서 사용할 명령 예시**입니다. 이 조사에서는 설치하거나 실행하지 않았습니다.

```bash
aside account list
aside account status
aside "Open localhost:3000 and run a smoke test"
aside mcp
```

`aside mcp`는 다른 에이전트·코딩 도구에 연결할 MCP 서버를 시작합니다. `mcp.json`을 지원하는 클라이언트에는 다음 구조를 안내합니다. 실제 CLI 경로와 클라이언트의 설정 형식을 확인합니다. [공식 MCP 안내](https://docs.aside.com/help/developers).

```json
{
  "mcpServers": {
    "aside": {
      "command": "aside",
      "args": ["mcp"]
    }
  }
}
```

이는 `mcp.json`용 예시이며 모든 클라이언트에 같은 파일을 복사하는 절차는 아닙니다. REPL은 페이지 조사·스크린샷·다운로드·정해진 탐색 순서 구현 용도로 안내합니다. [개발자 도움말](https://docs.aside.com/help/developers).

[⬆ 목차로 돌아가기](#목차)

## 7. 성능 주장과 확인 한계

제작사는 세 브라우저 에이전트 벤치마크에서 1위라고 소개하며 결과 저장소를 공개합니다. 아래 값은 독립 재현 결과가 아닌 제작사 보고입니다. [기능 소개](https://aside.com/features/browser-agent), [공개 벤치마크](https://github.com/at-inc/aside-benchmarks).

| 벤치마크        | 공개 결과                       | 해석 기준                            |
|-----------------|---------------------------------|--------------------------------------|
| Online-Mind2Web | 297/300 성공, 99.0%             | 불가능 판정 1개를 제외하면 99.3%     |
| Odysseys        | 151/200 모든 rubric 충족, 75.5% | rubric 통과율 88.8%와 서로 다른 지표 |
| BU Bench V1     | GPT-5.5 실행 93/100 성공, 93.0% | 불가능 판정 1개를 제외하면 93.9%     |

공개 실행에는 모델·추론 설정·시간 및 단계 제한·LLM 평가기가 포함됩니다. 실시간 웹사이트 상태에 따라 결과도 달라질 수 있습니다. 표의 수치는 모든 계정·모델·업무에 적용되는 성공률 보장이 아닙니다.

이번 조사에서 설치, 로그인·MFA, 모델 연결, 메모리 생성, routine 실행, MCP 연결, 권한 차단과 암호화 구조는 직접 시험하지 않았습니다. Linux 지원과 Windows 최소 사양도 추가 확인 항목입니다. 출처별 확인과 두 차례 사실 대조는 [공식 참조 노트](../../_reference/aside_browser_official_notes.md)에 기록했습니다.

[⬆ 목차로 돌아가기](#목차)

## 8. 업무 적용 예시

다음은 이 문서에서 작성한 요청 예시입니다. 기능이 실제 업무에서 성공한다는 검증 결과는 아닙니다.

| 업무               | 요청 예시                                                           | 확인할 결과                        |
|--------------------|---------------------------------------------------------------------|------------------------------------|
| 기술 조사          | 지정한 공식 사이트에서 OS 지원·제한을 조사하고 출처 URL을 표에 기록 | 링크가 주장과 일치하는지 확인      |
| 릴리스 조사        | 지정 프로젝트의 변경 이력과 현재 배포 버전을 비교                   | 브라우저 버전과 구성요소 버전 구분 |
| 내부 대시보드 조회 | 지정 기간의 지표를 읽고 요약 파일 작성                              | 원본 수치와 요약 값 대조           |
| 웹앱 검증          | 테스트 계정으로 로컬 웹앱의 로그인·검색 흐름 확인                   | 화면·URL·실패 지점 기록            |
| 반복 브리핑        | 지정 자료의 새 변경을 주기적으로 정리하는 routine 초안 작성         | 실행 일정·자료 범위·산출물 검토    |

이 저장소의 조사 업무에 적용한다면 원문 링크·확인일·버전·미확인을 포함한 결과를 요청할 수 있습니다. Git commit·push나 운영 변경은 조사 결과 작성과 별도의 수행 범위로 지정합니다.

관련 자료: [AI 개발 요청 템플릿](./ai_development_request_template.md), [AI 에이전트 샌드박스 개념](../../04_security/hardening/ai_agent_sandbox_concepts.md).

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- [Aside 공식 사이트](https://aside.com/).
- [시작 도움말](https://docs.aside.com/help/get-started).
- [모델 공급자 설정](https://docs.aside.com/help/ai).
- [요금 페이지](https://aside.com/pricing), [구독 도움말](https://docs.aside.com/help/subscription).
- [권한 설정](https://docs.aside.com/help/security), [개인정보 정책](https://aside.com/policy/privacy).
- [CLI·MCP·REPL](https://docs.aside.com/help/developers).
- [브라우저 변경 이력](https://docs.aside.com/changelog/native).
- [제작사 공개 벤치마크](https://github.com/at-inc/aside-benchmarks).
- [공식 참조 노트](../../_reference/aside_browser_official_notes.md).

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-10-13

**마지막 업데이트**: 2026-10-13

© 2026 siasia86. Licensed under CC BY 4.0.

# Codex 스킬 목록과 한 줄 설명

2026-10-04 문서 작성 세션에서 제공된 스킬 31개의 용도를 정리합니다. 개인 스킬 7개, 기본 스킬 4개, 플러그인 스킬 20개이며, 필요한 작업 절차를 고르는 참고 목록입니다.

작성·설치·비활성화 방법은 [Codex Skills 설정 가이드](codex_skills_setup_guide.md)에서 확인합니다.

## 목차

- [1. 목록의 확인 범위](#1-목록의-확인-범위)
- [2. 개인 스킬](#2-개인-스킬)
- [3. 기본 스킬](#3-기본-스킬)
- [4. 플러그인 스킬](#4-플러그인-스킬)
- [5. 업무별 선택 예시](#5-업무별-선택-예시)
- [6. 명시적 호출 방법](#6-명시적-호출-방법)
- [7. 목록 유지와 스킬 수정](#7-목록-유지와-스킬-수정)

---

## 1. 목록의 확인 범위

출처는 해당 세션에 제공된 스킬 이름·설명·분류 경로입니다. 모든 PC나 모든 Codex 세션에 같은 스킬이 설치되어 있다는 뜻은 아닙니다. 아래 이름은 제공된 식별자를 유지하며, 플러그인은 `플러그인:스킬` 형식으로 구분합니다.

목록에 표시되는 상태와 실제 도구 실행 가능 여부는 별개입니다. 예를 들어 PC 제어·Excel 연결·사이트 게시에는 해당 도구의 연결, 권한과 지원 환경 확인이 필요합니다. 이 문서 작성 과정에서는 목록 대조와 문서 검사를 수행하며 각 스킬의 실제 동작을 새로 시험하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 개인 스킬

| 스킬                     | 한 줄 설명                                                      |
|--------------------------|-----------------------------------------------------------------|
| `work-rules`             | 저장소 작업의 범위·검증·보고·게시 공통 규칙을 적용합니다.       |
| `planning-and-breakdown` | 큰 작업을 실행 순서와 완료 기준이 있는 단계로 나눕니다.         |
| `code-review`            | 코드·스크립트·IaC의 정확성·보안·오류 처리·성능을 검토합니다.    |
| `debugging-and-recovery` | 서비스·빌드·배포 장애의 원인을 분석하고 복구 절차를 정리합니다. |
| `git-commit-rule`        | 한글 commit 메시지 형식과 검증한 변경의 게시 절차를 적용합니다. |
| `markdown-review`        | Markdown의 구조·표현·표·예시·일관성을 읽기 전용으로 검토합니다. |
| `md-link-check`          | Markdown 파일 링크·앵커·헤딩·목차를 검사합니다.                 |

`markdown-review`의 외부 사실 검증과 `md-link-check`의 외부 URL 도달성 검사는 별도 범위입니다. 파일 존재, 같은 파일 앵커와 다른 파일 앵커도 검사 결과를 구분합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 기본 스킬

| 스킬              | 한 줄 설명                                                                |
|-------------------|---------------------------------------------------------------------------|
| `openai-docs`     | OpenAI·Codex 제품의 사용법·설정·모델·API를 공식 자료로 확인합니다.        |
| `skill-creator`   | 작업 범위에 맞는 Codex 스킬과 필요한 보조 자료를 만들거나 수정합니다.     |
| `skill-installer` | 카탈로그나 GitHub 저장소에서 요청한 Codex 스킬을 설치합니다.              |
| `imagegen`        | 사진·일러스트·텍스처·스프라이트 등 비트맵 이미지를 생성하거나 편집합니다. |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 플러그인 스킬

| 스킬 식별자                           | 한 줄 설명                                                      |
|---------------------------------------|-----------------------------------------------------------------|
| `computer-use:computer-use`           | 지원되는 도구 환경에서 Windows 앱을 읽고 조작합니다.            |
| `documents:documents`                 | Word 문서를 작성·편집하고 렌더링 결과로 배치를 확인합니다.      |
| `pdf:pdf`                             | PDF를 읽고 만들거나 수정하며 페이지의 시각적 배치를 확인합니다. |
| `presentations:Presentations`         | PowerPoint·Google Slides 발표 자료를 읽고 작성·편집합니다.      |
| `spreadsheets:Spreadsheets`           | 독립된 Excel·CSV·TSV 파일을 작성·편집·분석·검증합니다.          |
| `spreadsheets:excel-live-control`     | 연결된 Microsoft Excel 세션의 열린 통합 문서를 조작합니다.      |
| `template-creator:template-creator`   | 참고 결과물을 재사용 가능한 개인 산출물 템플릿 스킬로 만듭니다. |
| `visualize:visualize`                 | 대화 안에서 차트·비교·시뮬레이션·대화형 도구를 만듭니다.        |
| `plugin-management:plugin-management` | 플러그인을 탐색하고 연결·권한·의존성·제거를 관리합니다.         |
| `pages:maintain-space`                | 새 근거를 기존 ChatGPT Page·Space 내용에 반영합니다.            |
| `pages:manage-schedules`              | ChatGPT Space의 예약 작업을 검토하고 생성·수정·제거합니다.      |
| `pages:organize-space`                | 기존 ChatGPT Page·Space의 문서 구조와 배치를 정리합니다.        |
| `pages:write-page`                    | 요청한 ChatGPT Page·Space 내용을 작성하거나 수정합니다.         |
| `sites:sites-building`                | Sites로 웹사이트를 만들거나 기존 Sites 웹사이트를 수정합니다.   |
| `sites:sites-hosting`                 | Sites 웹사이트의 게시·호스팅을 처리합니다.                      |
| `sites:sites-mcp`                     | Sites에서 호스팅할 MCP 서버를 만들고 접근 방법을 연결합니다.    |
| `sites:sites-preview-troubleshooting` | 지원되는 Sites 미리보기 환경의 실행 실패를 진단하고 복구합니다. |
| `work-pets:create-pet`                | ChatGPT Work용 애니메이션 펫을 생성·검증·업로드·활성화합니다.   |
| `work-pets:pets`                      | ChatGPT Work 펫을 조회·선택·다운로드·삭제합니다.                |
| `work-pets:update-pet`                | 기존 ChatGPT Work 펫의 정보·이미지·애니메이션을 수정합니다.     |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 업무별 선택 예시

| 요청                                  | 우선 선택할 스킬         |
|---------------------------------------|--------------------------|
| 코드에 보완·개선할 부분이 있는지 검토 | `code-review`            |
| 문서 구조와 설명이 읽기 좋은지 검토   | `markdown-review`        |
| 문서 링크·목차·헤딩 누락 확인         | `md-link-check`          |
| 실행 오류의 원인 분석과 복구          | `debugging-and-recovery` |
| 여러 단계의 구현 순서와 작업 분해     | `planning-and-breakdown` |
| 반복해서 사용할 검토 절차 만들기      | `skill-creator`          |

`improvement-review`는 이 목록에 등록된 스킬이 아닙니다. 코드·문서·운영 검토를 묶는 별도 스킬이 필요하면 검토 대상, 판정 기준, 결과 형식, 수정 허용 범위를 먼저 정해 작성합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 6. 명시적 호출 방법

공식 문서는 Codex CLI·IDE의 명시적 호출에 `/skills` 또는 `$`를, ChatGPT의 명시적 호출에 `@`를 안내합니다. 실제 화면에서 제공되는 선택 목록과 스킬 이름을 확인해 사용합니다. [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills)

다음은 Codex에 보내는 요청 문장 예시이며 터미널 명령이 아닙니다.

```text
$code-review 서버 관리 UI의 변경 코드를 검토해줘. 수정은 하지 말아줘.
$markdown-review 대상.md의 구조와 표현에 보완할 부분을 알려줘.
$md-link-check 대상.md의 파일 링크와 앵커를 확인해줘.
$debugging-and-recovery 서버 실행 실패의 로그를 분석하고 복구 순서를 정리해줘.
```

검토만 필요한지, 검토 후 수정까지 원하는지 요청에 함께 적습니다. 자연어 요청에 맞는 스킬을 자동 선택하는 방식도 지원되지만, 특정 절차를 지정하려면 실제 제공되는 스킬을 명시합니다. [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills)

[⬆ 목차로 돌아가기](#목차)

---

## 7. 목록 유지와 스킬 수정

스킬을 추가·제거하거나 설명을 바꾸면 목록의 기준일, 이름·설명, 분류별 개수를 함께 갱신합니다. 이름이 같은 스킬은 실제 출처를 확인하며, 이 참고 문서의 내용을 설치된 `SKILL.md` 지시사항으로 간주하지 않습니다.

32번 저장소는 참고 자료를 보관합니다. 개인 스킬 구현·검증·설치 반영은 35번 관리 원본에서 진행하며, 설치본만 단독 수정하지 않는 실제 작업 지침을 따릅니다. 이 문서 추가는 스킬 설치·설정 변경을 포함하지 않습니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- OpenAI Build skills: [learn.chatgpt.com/docs/build-skills](https://learn.chatgpt.com/docs/build-skills) — ★★★☆☆
- OpenAI Skills and plugins: [learn.chatgpt.com/docs/skills-and-plugins](https://learn.chatgpt.com/docs/skills-and-plugins) — ★★★☆☆
- 작성·설치 상세: [Codex Skills 설정 가이드](codex_skills_setup_guide.md) — ★★★☆☆

공식 호출 방법 확인일은 2026-10-04입니다. 스킬 31개 목록은 세션에 제공된 메타데이터를 대조한 결과이며 각 플러그인의 설치·실행 검증 기록은 아닙니다.

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-10-04

**마지막 업데이트**: 2026-10-04

© 2026 siasia86. Licensed under CC BY 4.0.

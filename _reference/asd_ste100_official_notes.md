---
name: asd-ste100-official-notes
description: ASD-STE100 공식 설명과 Codex 소통 적용 후보의 직접 근거.
tags:
  - asd-ste100
  - codex
  - communication
last_checked: 2026-10-09
sources:
  - https://www.asd-ste100.org/about_STE.html
  - https://www.asd-ste100.org/STE_faq.html
  - https://learn.chatgpt.com/docs/build-skills
  - https://learn.chatgpt.com/docs/agent-configuration/agents-md
  - https://github.com/nuelcyoung/asd-ste100
  - https://github.com/avectats7/technical-writing-ste
  - https://github.com/mdlamar/ASD-STE100
  - https://github.com/blagoySimandov/asd-ste100-writer-skill
  - https://github.com/sysmatt/ste-rules
---

# ASD-STE100 공식 사실과 구현 참조 노트

## 1. 확인 범위

`STE-20261009-01`에서 2026-10-09 한국 시간에 조사했습니다. [사용 방안 문서](../06_career/ai_tools/asd_ste100_codex_communication.md)의 근거 노트입니다. 공식 표준과 커뮤니티 구현의 출처를 구분합니다. 원문 규칙·사전·skill 전체를 이 저장소에 복제하지 않았습니다.

ASD 공식 소개·FAQ는 PowerShell HTTP 조회에서 상태 200과 본문을 확인했습니다. 웹 도구의 동일 URL 조회는 접근 오류였고, 다운로드 안내는 HTTP 시간 초과였습니다. 검색 요약만으로 다운로드 페이지나 백서를 검증했다고 판단하지 않았습니다.

OpenAI 공식 URL은 현재 ChatGPT Learn 문서로 연결됐으며 실제 본문을 읽었습니다. GitHub는 API로 기준 커밋·파일 구성을 확인하고 원저자 README·SKILL·라이선스·관련 설치 코드를 읽었습니다. 설치·clone·코드 실행은 미실행입니다.

## 2. 공식 설명에서 확인한 사실

| 항목        | 확인 결과                                                          | 근거                                                                             |
|-------------|--------------------------------------------------------------------|----------------------------------------------------------------------------------|
| 정체        | 영어 기술 문서를 위한 통제된 자연어 표준                           | [ASD 소개](https://www.asd-ste100.org/about_STE.html)                            |
| 현행판      | Issue 9, 2025-01-15                                                | [ASD 소개](https://www.asd-ste100.org/about_STE.html)                            |
| 구성        | 작성 규칙 53개와 통제 사전, 분야별 기술 용어 허용                  | [ASD 소개](https://www.asd-ste100.org/about_STE.html)                            |
| 적용 범위   | 기술 절차·설명 문서가 목적. 일반 글에는 일부 원칙을 참고할 수 있음 | [ASD FAQ](https://www.asd-ste100.org/STE_faq.html)                               |
| 자료 제공   | 공식 표준은 무료 PDF로 요청할 수 있다고 안내                       | [ASD FAQ](https://www.asd-ste100.org/STE_faq.html)                               |
| Codex skill | SKILL.md의 이름·설명으로 선택하고 전체 지침을 읽는 재사용 절차     | [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills)               |
| 로컬 발견   | 사용자·저장소의 .agents/skills 등 공식 위치에서 발견               | [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills)               |
| 지속 지침   | 전역·프로젝트 AGENTS.md를 경로에 따라 결합                         | [OpenAI AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) |

한국어 응용의 표준 인증·Codex 기본 기능 내장·성능 개선 보장은 위 설명에서 확인하지 않았습니다. 커뮤니티 도구의 라이선스로 공식 사전 재배포를 허용한다고 해석하지 않습니다.

## 3. GitHub 후보별 근거

### nuelcyoung/asd-ste100

- 기준: `3fe2ccb51b1a98fb8d40aa88ec448575b8439ddb`, 최근 커밋 시각 `2026-08-22T19:05:41Z`.
- [README](https://github.com/nuelcyoung/asd-ste100/blob/3fe2ccb51b1a98fb8d40aa88ec448575b8439ddb/README.md), [MIT LICENSE](https://github.com/nuelcyoung/asd-ste100/blob/3fe2ccb51b1a98fb8d40aa88ec448575b8439ddb/LICENSE), [SKILL.md](https://github.com/nuelcyoung/asd-ste100/blob/3fe2ccb51b1a98fb8d40aa88ec448575b8439ddb/SKILL.md), [사전 접근 절차](https://github.com/nuelcyoung/asd-ste100/blob/3fe2ccb51b1a98fb8d40aa88ec448575b8439ddb/references/dictionary-access.md).
- Codex·Claude·opencode를 명시한 문서형 구현입니다. 비공식·미인증을 고지하며 의미와 불확실성 보존을 우선합니다. 사전·참고 자료 읽기 절차가 있어 한국어 일반 대화용으로 그대로 적용하는 것은 별도 판단이 필요합니다.

### avectats7/technical-writing-ste

- 기준: `3581b839334a7831ae02e302c4b7183fa510eff7`, 최근 커밋 날짜 `2026-08-04`.
- [README](https://github.com/avectats7/technical-writing-ste/blob/3581b839334a7831ae02e302c4b7183fa510eff7/README.md), [SKILL.md](https://github.com/avectats7/technical-writing-ste/blob/3581b839334a7831ae02e302c4b7183fa510eff7/SKILL.md), [NOTICE](https://github.com/avectats7/technical-writing-ste/blob/3581b839334a7831ae02e302c4b7183fa510eff7/NOTICE), [MIT LICENSE](https://github.com/avectats7/technical-writing-ste/blob/3581b839334a7831ae02e302c4b7183fa510eff7/LICENSE).
- Claude용 문서형 skill·참고·예시·평가 입력입니다. 공식 사전 전체를 포함하지 않는다고 고지합니다. 실행 코드 없이 문서 작성과 재작성을 구분하는 구조를 참고할 수 있습니다.

### mdlamar/ASD-STE100

- 기준: `b57d6b8ec8f984b3c54b57a9744c73eeb77b8355`, 최근 커밋 날짜 `2026-09-06`.
- [README](https://github.com/mdlamar/ASD-STE100/blob/b57d6b8ec8f984b3c54b57a9744c73eeb77b8355/README.md), [CC0-1.0 LICENSE](https://github.com/mdlamar/ASD-STE100/blob/b57d6b8ec8f984b3c54b57a9744c73eeb77b8355/LICENSE), [설치기](https://github.com/mdlamar/ASD-STE100/blob/b57d6b8ec8f984b3c54b57a9744c73eeb77b8355/install.sh), [검사기](https://github.com/mdlamar/ASD-STE100/blob/b57d6b8ec8f984b3c54b57a9744c73eeb77b8355/scripts/ste-lint.py).
- opencode용 구현입니다. 영어 정규식 검사와 필수 검사기 실행을 포함합니다. 전역 파일 교체 가능성을 코드에서 확인했으며, README의 개선율은 독립 시험하지 않았습니다.

### blagoySimandov/asd-ste100-writer-skill

- 기준: `858eab440e034b70cb038dbd3823cacd764052ab`, 최근 커밋 날짜 `2026-08-01`.
- [README](https://github.com/blagoySimandov/asd-ste100-writer-skill/blob/858eab440e034b70cb038dbd3823cacd764052ab/README.md), [SKILL.md](https://github.com/blagoySimandov/asd-ste100-writer-skill/blob/858eab440e034b70cb038dbd3823cacd764052ab/skills/ste100-writer/SKILL.md), [package.json](https://github.com/blagoySimandov/asd-ste100-writer-skill/blob/858eab440e034b70cb038dbd3823cacd764052ab/package.json), [Node 설치기](https://github.com/blagoySimandov/asd-ste100-writer-skill/blob/858eab440e034b70cb038dbd3823cacd764052ab/bin/skills-install.js).
- LICENSE 파일은 없고 package.json에 MIT 선언이 있습니다. 설치기의 `--force`는 대상 폴더를 삭제하고 복사합니다. 라이선스 완결성과 설치 동작은 실제 도입 전에 추가 확인할 항목입니다.

### sysmatt/ste-rules

- 기준: `c18369e275a6873e09a417ac93219499190a2059`, 최근 커밋 날짜 `2026-07-28`.
- [규칙 요약](https://github.com/sysmatt/ste-rules/blob/c18369e275a6873e09a417ac93219499190a2059/STE100-writing-rules.md).
- 기준 커밋에는 위 문서만 있으며 README·SKILL.md·LICENSE가 없습니다. 직접 설치 후보가 아닌 보조 자료로 분류했습니다.

## 4. 미확인과 재사용 범위

- 공식 표준 PDF 전체, 통제 사전의 항목별 검사, AI 백서의 본문은 미확인입니다.
- 각 구현의 Windows 설치·Codex 실제 발견·선택·행동, 한국어 응답 개선 효과는 미시험입니다.
- 자료 날짜는 모두 조사일 이전입니다. 저장소 최신 main은 변경될 수 있으므로 위 고정 SHA를 재사용합니다.
- 한국어 사용 방안은 이 조사에서 만든 제안이며 영어 표준의 인증된 번역 규칙이 아닙니다.
- 원본이나 판단 조건이 달라진 경우 해당 범위만 다시 확인합니다. 취소된 31 작업이나 전체 저장소 조사를 재개하는 근거로 쓰지 않습니다.

---

**작성일**: 2026-10-09

**마지막 업데이트**: 2026-10-09

© 2026 siasia86. Licensed under CC BY 4.0.

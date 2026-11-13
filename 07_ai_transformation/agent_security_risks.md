# 에이전트 보안 위협 점검

<!-- reference: _reference/gitleaks_official_notes.md, _reference/agent_skills_spec_official_notes.md -->

AX 환경에서 에이전트가 만드는 보안 위협을 점검하는 방법 문서입니다. 위협 분류는 OWASP Top 10 for Agentic Applications for 2026의 항목 이름을 따르고, 점검 방법은 이 문서가 AX 환경에 맞춰 정리했습니다.

## 목차

| 섹션                                                                                       |
|--------------------------------------------------------------------------------------------|
| [1. 출처와 인용 범위](#1-출처와-인용-범위) / [2. 위협 항목](#2-위협-항목)                  |
| [3. AX 환경 적용](#3-ax-환경-적용) / [4. 점검 순서](#4-점검-순서) / [5. 미확인](#5-미확인) |

## 1. 출처와 인용 범위

| 항목      | 내용                                                                                         |
|-----------|----------------------------------------------------------------------------------------------|
| 출처      | OWASP GenAI Security Project, Top 10 for Agentic Applications for 2026                       |
| 게시일    | 2025-12-09                                                                                   |
| 확인일    | 2026-11-13                                                                                   |
| 라이선스  | 사이트 기본 CC BY-SA 4.0                                                                     |
| 인용 범위 | 항목 번호·이름과 이 문서의 한 줄 설명만 둡니다. 원문의 완화책·표·그림·예시는 옮기지 않습니다 |

[⬆ 목차로 돌아가기](#목차)

## 2. 위협 항목

설명은 원문 번역이 아니라 이 문서가 쓴 한 줄입니다.

- ASI01 Agent Goal Hijack — 에이전트가 읽은 내용이 원래 목표를 바꿔 놓는 위협
- ASI02 Tool Misuse — 허용된 도구를 의도와 다르게 써서 피해를 내는 위협
- ASI03 Identity & Privilege Abuse — 에이전트의 자격 증명·권한이 맡은 범위를 넘어 쓰이는 위협
- ASI04 Agentic Supply Chain Vulnerabilities — 외부에서 가져온 도구·skill·연결 서버가 오염되는 위협
- ASI05 Unexpected Code Execution — 자연어 지시가 의도하지 않은 코드 실행으로 이어지는 위협
- ASI06 Memory & Context Poisoning — 메모리나 문맥에 들어간 잘못된 내용이 이후 행동을 계속 비트는 위협
- ASI07 Insecure Inter-Agent Communication — 에이전트 사이의 메시지가 위조되거나 가로채이는 위협
- ASI08 Cascading Failures — 한 단계의 잘못된 결과가 자동 흐름을 따라 퍼지는 위협
- ASI09 Human-Agent Trust Exploitation — 사람이 에이전트의 그럴듯한 설명을 확인 없이 믿게 되는 위협
- ASI10 Rogue Agents — 에이전트가 맡은 범위를 벗어나 스스로 움직이는 위협

[⬆ 목차로 돌아가기](#목차)

## 3. AX 환경 적용

각 위협이 AX 환경의 어디에서 생기는지와 확인할 장치입니다.

| 위협  | AX 환경에서 생기는 자리                       | 확인할 장치                                                            |
|-------|-----------------------------------------------|------------------------------------------------------------------------|
| ASI01 | 웹 문서, 내려받은 파일, 다른 세션의 메시지    | 외부 내용은 지시가 아닌 자료로 다룬다는 규칙, 지침 우선순위            |
| ASI02 | 셸 명령, Git push, 파일 삭제                  | 권한 모드, 허용·차단 목록, 도구 호출 전 hook                           |
| ASI03 | API 키, 토큰, SSH 키, 클라우드 자격 증명      | 자격 증명을 지침·기록에 넣지 않음, 비밀 정보 검사, 최소 권한 토큰      |
| ASI04 | 설치하는 skill·plugin·MCP 서버, 외부 스크립트 | 설치 전 동봉 파일 검토, 출처 확인, 버전 고정                           |
| ASI05 | 에이전트가 만든 스크립트, 붙여 넣은 명령      | 샌드박스, 실행 전 내용 읽기, 위험 명령 실행 전 확인                    |
| ASI06 | 메모리 파일, 인계 파일, 요약된 문맥           | 메모리에 둘 것의 규칙, 인계 파일 검토, 요약 뒤 원본 다시 읽기          |
| ASI07 | 세션 간 메시지, 하위 에이전트 결과            | 메시지는 사용자 승인이 아니라는 규칙, 결과의 사실·diff 직접 확인       |
| ASI08 | 작성 → 검사 → 게시 자동 흐름                  | 단계마다 검사 0건 확인 뒤 다음 단계, 검사와 게시를 한 명령에 묶지 않음 |
| ASI09 | 완료 보고, 검토 회신                          | 실행·검증·미실행을 나눈 보고, 사람이 확인할 항목 명시                  |
| ASI10 | 오래 도는 작업, 여러 세션 동시 작업           | 작업 ID·담당 파일 명시, 중단 지시 우선, 모든 변경을 기록에 남김        |

[⬆ 목차로 돌아가기](#목차)

## 4. 점검 순서

1. 에이전트가 쓸 수 있는 도구와 권한을 목록으로 적습니다(ASI02·ASI03).
2. 외부에서 들어오는 내용(웹, 파일, 메시지, skill)의 경로를 적고 각각 자료로만 다루는지 확인합니다(ASI01·ASI04·ASI07).
3. 되돌리기 어려운 행동(삭제, push, 배포)에 사람 확인이나 hook이 걸려 있는지 봅니다(ASI02·ASI05·ASI10).
4. 메모리·인계 파일에 무엇이 쌓이는지 주기적으로 검토합니다(ASI06).
5. 자동 흐름의 각 단계에 검사와 정지 조건이 있는지 봅니다(ASI08).
6. 보고 양식이 확인한 것과 확인하지 못한 것을 나누는지 봅니다(ASI09).

비밀 정보 검사 도구는 [Gitleaks 노트](../_reference/gitleaks_official_notes.md), skill 설치 전 검토 기준은 [Agent Skills 규격 노트](../_reference/agent_skills_spec_official_notes.md) 4절에서 확인합니다.

[⬆ 목차로 돌아가기](#목차)

## 5. 미확인

- 원문 PDF는 공식 다운로드 링크가 접근 제한 페이지를 돌려줘 열람하지 못했습니다(2026-11-13).
- 항목 이름은 OWASP 조직 저장소 두 곳에서 대조했습니다. `secure-agent-playbook`의 위험 평가 절차 문서(`plays/agentic-ai-risk-assess.md`)에서 열 개를 모두 확인했고, ASI04는 그 문서 제목의 표기를 따랐습니다. 같은 저장소의 skill 파일은 ASI04를 "Agentic Supply Chain"으로 줄여 적습니다.
- 최종 원문 표기를 확인하지 못한 항목은 두 개입니다. ASI02는 `AISVS`가 "Tool Misuse & Exploitation"으로 적어 표기가 다릅니다. ASI05는 공개 초안에서 "Unexpected Code Execution (RCE)"로 적었다는 보고가 있으나 직접 확인하지 못했습니다.
- 원문 자체의 라이선스 예외 여부는 확인하지 못했습니다.

[⬆ 목차로 돌아가기](#목차)

## 참고 자료

- OWASP: [Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) — ★★★☆☆ (확인일 2026-11-13)
- OWASP: [secure-agent-playbook](https://github.com/OWASP/secure-agent-playbook), [AISVS](https://github.com/OWASP/AISVS) — 항목 이름 대조용 — ★★☆☆☆
- [에이전트 설계 원칙](agent_design_principles.md)

[⬆ 07 README로 돌아가기](README.md)

---

**작성일**: 2026-11-13

**마지막 업데이트**: 2026-11-13

© 2026 siasia86. Licensed under CC BY 4.0.

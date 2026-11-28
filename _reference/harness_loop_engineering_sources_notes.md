---
name: harness-loop-engineering-sources-notes
description: Harness Engineering·Loop Engineering 1차 자료(Hashimoto, OpenAI, Böckeler, LangChain, Anthropic, Addy Osmani, Ralph)의 게시일·저자·정의·핵심 주장 대조 노트.
tags:
  - harness-engineering
  - loop-engineering
  - ai-agent
last_checked: 2026-11-28
sources:
  - https://mitchellh.com/writing/my-ai-adoption-journey
  - https://openai.com/index/harness-engineering/
  - https://martinfowler.com/articles/harness-engineering.html
  - https://www.langchain.com/blog/the-anatomy-of-an-agent-harness
  - https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
  - https://www.anthropic.com/engineering/harness-design-long-running-apps
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://www.anthropic.com/engineering/building-effective-agents
  - https://addyosmani.com/blog/loop-engineering/
  - https://addyosmani.com/blog/practical-loop-engineering/
  - https://www.oreilly.com/radar/practical-loop-engineering/
  - https://ghuntley.com/ralph
---

# Harness·Loop Engineering 1차 자료 참조 노트

| 항목               | 내용                                                                |
|--------------------|---------------------------------------------------------------------|
| 확인일             | 2026-11-28 (12개 페이지 모두 읽음)                                  |
| 버전               | 블로그·기사라 버전 표기 없음. 게시일과 개정일로 구분                |
| 라이선스·인용 범위 | 모두 저자·회사 저작물. 짧은 인용과 요약·링크만                      |
| 표준 여부          | 두 용어 모두 표준 정의 없음. 출처마다 범위가 다르므로 출처별로 적음 |

## 1. 게시일과 저자

| 자료                                            | 게시일     | 저자·주체                       | 비고                                |
|-------------------------------------------------|------------|---------------------------------|-------------------------------------|
| Ralph Wiggum as a "software engineer"           | 2025-07-14 | Geoffrey Huntley                | 반복 실행 기법, 용어 이전           |
| Effective harnesses for long-running agents     | 2025-11-26 | Anthropic(Justin Young)         |                                     |
| My AI Adoption Journey                          | 2026-02-05 | Mitchell Hashimoto              | "harness engineering" 이름 붙임     |
| Harness engineering(OpenAI)                     | 2026-02-11 | OpenAI(Ryan Lopopolo)           |                                     |
| The Anatomy of an Agent Harness                 | 2026-03-10 | LangChain(Vivek Trivedy)        |                                     |
| Harness design for long-running application dev | 2026-03-24 | Anthropic(Prithvi Rajasekaran)  |                                     |
| Harness engineering for coding agent users      | 2026-04-02 | Birgitta Böckeler(Thoughtworks) | 2026-02-17 메모를 대체한 전체 글    |
| Loop Engineering                                | 2026-06-07 | Addy Osmani                     |                                     |
| Practical Loop Engineering                      | 2026-08-14 | Addy Osmani                     | O'Reilly Radar 재게재 2026-11-02    |
| Effective context engineering for AI agents     | 2025-09-29 | Anthropic Applied AI 팀         | 관련 개념                           |
| Building effective agents                       | 2024-12-19 | Anthropic(Erik S., Barry Zhang) | 페이지에 "도구 환경이 바뀜" 안내 띠 |

마지막 두 행은 두 용어가 쓰이기 전의 관련 글이라 따로 두었습니다.

## 2. 하네스의 정의

- Hashimoto: "anytime you find an agent makes a mistake, you take the time to engineer a solution such that the agent never makes that mistake again." 방법은 두 가지로, AGENTS.md 같은 지침 파일 갱신과 실제로 만든 도구(화면 캡처, 일부 테스트만 돌리는 스크립트 등)입니다. 그의 6단계 중 5단계("Engineer the Harness")입니다. 업계 공통 용어인지는 모른다고 적었습니다.
- Böckeler: "everything in an AI agent except the model itself"를 출발점으로, 코딩 에이전트를 쓰는 사람이 만드는 바깥 하네스로 범위를 좁힙니다.
- LangChain: "Agent = Model + Harness", "If you're not the model, you're the harness." 구성 요소로 시스템 프롬프트, 도구·skill·MCP와 그 설명, 묶음 기반 시설(파일 시스템·sandbox·브라우저), 조율 논리(하위 에이전트·인계·모델 선택), 결정적 실행용 hook·middleware(요약·계속 실행·lint)를 듭니다.
- Google Cloud의 "What is an agent harness?" 페이지는 본문이 거의 비어 읽지 못했습니다(미확인).
- 평가용 하네스(evaluation harness, 모델 성능 측정용)와 이름이 겹칩니다. 이 노트의 하네스는 에이전트 실행 환경을 뜻합니다.

## 3. OpenAI 사례 수치

- 2025-08 말 빈 저장소에서 시작, 약 5개월. 처음 엔지니어 3명, 글 작성 시점 7명.
- 직접 쓴 코드 0줄, 약 100만 줄, PR 약 1,500개 병합, 엔지니어 1명당 하루 평균 PR 3.5개.
- Codex 1회 실행이 한 작업에 6시간 넘게 동작하는 일이 잦다고 적었습니다.
- AGENTS.md는 약 100줄로 "map" 역할을 합니다.
- 정리 작업: 처음에는 매주 금요일(한 주의 20%)을 "AI slop" 정리에 썼고, 이후 원칙을 코드로 정해 두고 배경 작업이 어긋난 곳을 찾아 품질 등급을 갱신하고 리팩터링 PR을 엽니다. 글은 이를 garbage collection에 비유합니다. 오래된 문서를 찾아 고치는 doc-gardening 에이전트도 둡니다.

## 4. Böckeler의 틀

| 개념                | 내용                                                                                       |
|---------------------|--------------------------------------------------------------------------------------------|
| Guides(feedforward) | 에이전트가 행동하기 전에 방향을 잡음(지침, 규칙, 예시)                                     |
| Sensors(feedback)   | 행동한 뒤 관찰해 스스로 고치게 함(테스트, lint, 리뷰)                                      |
| Computational       | 결정적이고 빠름(테스트, linter, type checker, 구조 분석)                                   |
| Inferential         | 의미 분석, AI 코드 리뷰, LLM as judge. 결정적이지 않음                                     |
| 조절 영역           | Maintainability harness, Architecture fitness harness(fitness function), Behaviour harness |
| 고리 그림           | 가운데 모델, 그 바깥 만드는 쪽(builder) 하네스, 가장 바깥 쓰는 쪽(user) 하네스             |
| 그 밖               | steering loop, keep quality left, harnessability, harness templates, Ashby's Law           |

- 컨텍스트 엔지니어링과의 관계: "Engineering a user harness for a coding agent is a specific form of context engineering." 컨텍스트 엔지니어링이 guide·sensor를 에이전트에 전달하는 수단이라고 봅니다.
- steering loop: "The human's job in this is to steer the agent by iterating on the harness." harnessability: "Not every codebase is equally amenable to harnessing."
- Behaviour harness(기능이 맞게 동작하는지)는 글에서 "the elephant in the room"이라고 부를 만큼 아직 어려운 영역입니다.

## 5. Anthropic의 장기 실행 하네스

- 2025-11 글: 첫 실행에서 환경을 준비하는 initializer 에이전트와, 매 세션 조금씩 진척시키는 coding 에이전트로 나눕니다. 둘은 첫 사용자 프롬프트만 다르고 시스템 프롬프트·도구는 같습니다. 기능 목록 JSON, `claude-progress.txt` 진행 기록, 개발 서버 실행용 `init.sh`, 설명이 있는 git commit으로 세션을 잇습니다.
- 관찰된 실패: 한 번에 다 만들려는 시도(one-shot), 진척이 보이면 일이 끝났다고 선언, 시험 없이 기능을 완료로 표시. 브라우저 자동화(Puppeteer MCP)로 끝에서 끝까지 확인하게 하자 나아졌고, 브라우저 기본 alert 창은 보지 못했다고 적었습니다.
- 2026-03 글: planner(1~4문장 요청을 제품 명세로), generator(sprint 단위 구현), evaluator(Playwright MCP로 실제 앱을 조작해 평가)로 나눕니다. 작업 전에 generator와 evaluator가 그 묶음의 "완료" 기준을 합의하는 sprint contract를 둡니다. evaluator는 점수 분해가 있는 few-shot 예시로 보정합니다.
- 문맥 처리: 일부 모델은 문맥 한도가 가까워지면 일을 서둘러 마무리하는 "context anxiety"를 보입니다. 문맥을 비우고 새 에이전트로 시작하는 reset과, 앞부분을 요약해 같은 에이전트가 이어가는 compaction을 구분하고, compaction은 깨끗한 출발이 아니라서 이 현상이 남을 수 있다고 합니다.
- 걷어내기: "every component in a harness encodes an assumption about what the model can't do on its own." 새 모델에서 reset과 sprint 구조를 뺐고, 새 모델이 나오면 더 이상 하중을 받지 않는 부분을 걷어내라고 합니다.

## 6. Loop Engineering

- Osmani 2026-06-07: "Loop engineering is replacing yourself as the person who prompts the agent." 형식 정의는 없습니다. Peter Steinberger("designing loops that prompt your agents")와 Boris Cherny("My job is to write loops")의 말을 출발점으로 씁니다.
- 구성: Automations, Worktrees, Skills, Plugins and connectors, Sub-agents 다섯 가지와 상태를 적을 한 곳(markdown 파일이나 Linear 보드).
- 루프가 대신하지 않는 것 세 가지: 검증, comprehension debt, cognitive surrender. "intent debt"와 "orchestration tax"는 이 글에서 다른 글로 가는 링크로만 나오며 위험 목록에 들지 않습니다.
- 실무편 2026-08-14(O'Reilly 2026-11-02 재게재, 본문은 거의 같음): 정지 조건과 제약을 분명히 하고, 통과한 테스트 수나 점수 기준 같은 결정적 기준이 효과적이라고 합니다. 예로 턴 상한(5회·10회), 두 턴 연속 개선이 없으면 중단, 같은 명령을 바뀐 것 없이 세 번째 내면 멈출 때라는 기준을 듭니다. 일을 한 에이전트가 그 일을 좋다고 판정하지 않게 하고, 초안과 검증을 다른 하위 에이전트로 나눕니다. `/goal` 뒤의 evaluator는 대화 기록으로 지정한 규칙만 확인하므로 그 검증자가 아니라고 적었습니다. 인증·보안·금융에 닿으면 가까이 지켜보고 문서·테스트 범위 점검은 더 맡깁니다. 반복 예약은 생성 7일 뒤 만료되고 세션 범위라고 적었습니다.

## 7. Ralph 루프

- Huntley 2025-07-14: "In its purest form, Ralph is a Bash loop." 예: `while :; do cat PROMPT.md | claude-code ; done`
- 한 번에 한 가지 일, 실패를 본 뒤 프롬프트에 표지를 더함, 구현이 없다고 가정하기 전에 코드 검색, 테스트·정적 검사로 되밀기(back-pressure), `fix_plan.md`로 남은 일 관리.
- 도구 호출·사용량에 상한이 없는 도구라면 어느 것으로도 할 수 있다고 적었습니다. Osmani 실무편과 LangChain 글이 이 기법을 언급합니다.

## 8. 미확인

- Google Cloud 정의 페이지 본문.
- arXiv·preprint의 형식 정의(검색 결과로만 봄, 동료 심사 여부 미확인).
- Huntley의 `ghuntley.com/loop` 페이지(읽지 않음).
- OpenAI 수치는 회사 자체 보고이며 외부 재현 없음.

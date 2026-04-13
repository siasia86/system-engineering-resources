# Kiro CLI Command Reference

## 목차

| 단계              | 섹션                                                                          |
|-------------------|-------------------------------------------------------------------------------|
| 기본              | [1.명령어 전체 목록](#1-명령어-전체-목록) / [2.컨텍스트·도구 상세](#2-컨텍스트--도구-상세) / [3.단축키](#3-단축키-및-특수-입력) |
| 핵심 개념         | [4.Context Window](#4-context-window-개념) / [5.@ 참조](#5--참조-기능) / [6.쉘 통합](#6-쉘-통합-shell-integration) |
| 일상 사용         | [7.도구 권한](#7-도구-권한-관리-tool-trust) / [8./plan](#8-plan--plan-에이전트-상세) / [9..kiro/](#9-kiro-디렉토리-활용) |
| 커스터마이징      | [10.토큰·성능](#10-토큰-절약--성능-최적화) / [11.Hooks](#11-hooks-사용자-정의-동작) / [12.Output Style](#12-output-style-출력-스타일-제어) / [13.실험적 기능](#13-experimental-features-실험적-기능) |
| 고급 활용         | [14.병렬 처리](#14-병렬-처리-parallel-execution) / [15.CI/CD](#15-cicd-비대화형-모드) / [16.MCP](#16-mcp-서버-연동) |
| 레퍼런스·부록     | [17.트러블슈팅](#17-트러블슈팅) / [18.설정 전체](#18-설정-옵션-전체-목록) / [19.모델](#19-model-모델-선택) / [20.대화 관리](#20-대화-관리-chat-saveload) |
| 부록              | [21.활용도 요약](#21-인프라-엔지니어-활용도-요약) / [22.참고 URL](#22-참고-url) |


## 1. 명령어 전체 목록

### 대화 관리

| 명령어       | 설명                                              |
|--------------|---------------------------------------------------|
| `/quit`      | 종료 (별칭: `/q`, `/exit`)                      |
| `/clear`     | 대화 이력 초기화                                  |
| `/compact`   | 대화 요약하여 컨텍스트 확보                       |
| `/chat`      | 저장된 대화 관리 (save/load)                      |
| `/model`     | 현재 세션의 모델 선택/변경                        |

### 입력 도구

| 명령어       | 설명                                              |
|--------------|---------------------------------------------------|
| `/editor`    | `$EDITOR` (기본 vi) 열어서 멀티라인 프롬프트 작성 |
| `/reply`     | 마지막 AI 응답을 인용한 상태로 에디터 열기        |
| `/paste`     | 클립보드 이미지 붙여넣기                          |

### 에이전트 / 플래닝

| 명령어       | 설명                                              |
|--------------|---------------------------------------------------|
| `/agent`     | 에이전트 관리 (목록, 전환, 생성)                  |
| `/plan`      | Plan 에이전트로 전환 (Shift+Tab 으로 복귀)        |
| `/help`      | Help 에이전트로 전환 (기능/명령어 질문)           |

### 컨텍스트 / 도구

| 명령어       | 설명                                              |
|--------------|---------------------------------------------------|
| `/context`   | 컨텍스트 파일 관리, 컨텍스트 윈도우 사용량 확인   |
| `/tools`     | 사용 가능한 도구 및 권한 확인                     |
| `/code`      | LSP 기반 코드 인텔리전스 (`/code init` 으로 초기화)|
| `/prompts`   | 프롬프트 템플릿 조회/관리                         |
| `/hooks`     | 컨텍스트 훅 조회                                  |
| `/knowledge` | 지식 베이스 관리 (add/search/remove)              |
| `/mcp`       | 로드된 MCP 서버 확인                              |

### 작업 관리

| 명령어       | 설명                                              |
|--------------|---------------------------------------------------|
| `/todos`     | TODO 리스트 조회/관리/재개                        |

### 기타

| 명령어       | 설명                                              |
|--------------|---------------------------------------------------|
| `/usage`     | 빌링/크레딧 정보 확인                             |
| `/experiment`| 실험적 기능 토글                                  |
| `/changelog` | Kiro CLI 변경 이력 확인                           |
| `/issue`     | GitHub 이슈/기능 요청 생성                        |
| `/logdump`   | 지원용 로그 zip 파일 생성                         |

### 단축키

| 키           | 설명                                              |
|--------------|---------------------------------------------------|
| `Shift+Tab`  | Plan 에이전트 ↔ 이전 에이전트 전환                |

[⬆ 목차로 돌아가기](#목차)

## 2. 컨텍스트 / 도구 상세

### `/context` — 컨텍스트 관리

컨텍스트(Context)란 AI가 답변을 생성할 때 참고하는 모든 정보입니다.
시스템 프롬프트, 이전 대화 내용, 등록된 파일, 도구 정의 등이 모두 컨텍스트에 포함됩니다.
`/context` 명령어로 이 컨텍스트에 파일을 추가하거나, 현재 사용량을 확인할 수 있습니다.

> 💡 Context Window 개념 상세는 [섹션 4. Context Window](#4-context-window-개념) 참고

#### 서브커맨드

| 명령어                          | 설명                                              |
|---------------------------------|---------------------------------------------------|
| `/context`                      | 컨텍스트 윈도우 토큰 사용량 상세 표시             |
| `/context show`                 | 컨텍스트 규칙 및 매칭된 파일 목록 표시            |
| `/context show --expand`        | 파일 내용 및 대화 요약까지 표시                   |
| `/context add <경로...>`        | 컨텍스트 파일 규칙 추가 (glob 패턴 가능)          |
| `/context add --force <경로...>`| 크기 제한 초과 파일도 강제 추가                   |
| `/context remove <경로...>`     | 컨텍스트 파일 규칙 제거 (별칭: `/context rm`)     |
| `/context clear`                | 모든 세션 컨텍스트 규칙 제거                      |

#### 사용량 확인 예시

```
> /context

Context Window Usage:
  Context files:    15,234 tokens (15.2%)
  Tool definitions:  2,456 tokens  (2.5%)
  Assistant:        45,678 tokens (45.7%)
  User prompts:     12,345 tokens (12.3%)
  Total:            75,713 tokens (75.7%)
```

#### 컨텍스트 파일 확인 예시

```
> /context show

Agent (rust-expert)
  - src/**/*.rs
      src/main.rs
      src/lib.rs
  - Cargo.toml  /Users/me/project/Cargo.toml
  - skill://.kiro/skills/**/SKILL.md
      database-helper

Session (temporary)
  <none>

3 matched files in use
  - src/main.rs          (2.3% of context window)
  - src/lib.rs           (1.8% of context window)
  - database-helper      (0.1% of context window)
Context files total: 4.2% of context window
```

#### 파일 추가/제거 예시

```bash
/context add README.md docs/**/*.md    # 파일 또는 glob 패턴 추가
/context remove README.md              # 제거
/context clear                         # 전체 초기화
```

#### Agent 컨텍스트 vs Session 컨텍스트

| 구분              | Agent (영구)                       | Session (임시)                     |
|-------------------|------------------------------------|------------------------------------|
| 설정 방법         | 에이전트 JSON의 `resources` 필드   | `/context add` 명령어              |
| 지속성            | 세션 종료 후에도 유지              | 세션 종료 시 삭제                  |
| 용도              | 항상 참고해야 하는 파일            | 현재 작업에만 필요한 파일          |

⚠️ `/context add/remove/clear` 는 세션 한정입니다. 영구 설정은 에이전트 JSON의 `resources` 필드를 수정하세요.

#### 크기 제한

- 컨텍스트 윈도우 비율 기준으로 제한 적용
- 초과 시 오래된 파일부터 자동 제거 (경고 표시)
- `--force` 옵션으로 제한 무시 가능

### `/code` — 코드 인텔리전스 (LSP)

코드 프로젝트에서 함수/클래스 정의 찾기, 심볼 검색 등 IDE 수준의 코드 분석 기능입니다.

```bash
/code init          # 현재 디렉토리에서 LSP 초기화 (언어 자동 감지)
/code status        # LSP 서버 상태 확인
/code overview      # 코드베이스 구조 요약
/code summary       # 코드베이스 문서 자동 생성
/code logs          # LSP 로그 확인
```

지원 언어: TypeScript, Rust, Python, Go, Java, Ruby, C/C++

### `/tools` — 사용 가능한 도구 확인

AI가 현재 사용할 수 있는 도구 목록과 권한을 보여줍니다.

```
/tools              ← 파일 읽기/쓰기, bash 실행, 검색 등 도구 목록
```

### `/prompts` — 프롬프트 템플릿

프롬프트 템플릿은 자주 반복하는 요청을 `.md` 파일로 저장해두고, `@이름` 또는 `/prompts get` 으로 재사용하는 기능입니다.
매번 같은 지시를 타이핑하지 않아도 되고, 인자(argument)를 넘겨서 동적으로 내용을 바꿀 수 있습니다.

#### 저장 위치 및 우선순위

| 범위              | 경로                          | 우선순위 |
|-------------------|-------------------------------|----------|
| 로컬 (워크스페이스)| `.kiro/prompts/`             | 1 (최고) |
| 글로벌 (사용자)   | `~/.kiro/prompts/`            | 2        |
| MCP 서버          | MCP 서버 제공                 | 3 (최저) |

같은 이름이면 로컬 > 글로벌 > MCP 순으로 적용됩니다.

#### 서브커맨드

| 명령어                                    | 설명                                  |
|-------------------------------------------|---------------------------------------|
| `/prompts list [검색어]`                  | 프롬프트 목록 (검색어로 필터 가능)    |
| `/prompts get <이름> [인자...]`           | 프롬프트 로드 후 메시지로 전송        |
| `/prompts create --name <이름> [--content <내용>] [--global]` | 새 프롬프트 생성 |
| `/prompts edit <이름> [--global]`         | 기존 프롬프트 편집 ($EDITOR)          |
| `/prompts remove <이름> [--global]`       | 프롬프트 삭제                         |
| `/prompts details <이름>`                 | 상세 정보 (설명, 인자, 출처)          |

#### `@` 빠른 호출

```
@<Tab>                    ← 전체 프롬프트 자동완성
@server-check             ← server-check 프롬프트 실행
@deploy-check prd nginx   ← 인자 전달
```

#### 프롬프트 파일 형식

`.kiro/prompts/` 에 `.md` 파일로 저장합니다. 인자는 플레이스홀더로 지정합니다.

| 플레이스홀더 | 동작                              |
|-------------|-----------------------------------|
| `${1}`~`${10}` | 위치 기반 인자                |
| `$ARGUMENTS`   | 모든 인자를 공백으로 연결     |
| `${@}`         | `$ARGUMENTS` 와 동일 (별칭)  |

#### 이름 규칙

- 영숫자, 하이픈(`-`), 언더스코어(`_`) 만 허용
- 최대 50자
- 패턴: `^[a-zA-Z0-9_-]+$`

#### 인프라 엔지니어 활용 예시

##### 예시 1: 서버 상태 점검

```markdown
<!-- ~/.kiro/prompts/server-check.md -->
${1} 서버의 다음 항목을 점검해줘:
- CPU, Memory, Disk 사용률
- 최근 에러 로그 (최근 1시간)
- 프로세스 상태 (${2} 서비스)
결과를 표로 정리해줘.
```

```
@server-check prd-web-01 nginx
```

##### 예시 2: 배포 전 체크리스트

```markdown
<!-- ~/.kiro/prompts/deploy-check.md -->
${1} 환경에 ${2} 배포 전 체크리스트:
1. 현재 서비스 상태 확인
2. 디스크 여유 공간 확인 (최소 5GB)
3. 최근 배포 이력 확인
4. 롤백 절차 확인
5. 모니터링 대시보드 URL 확인
```

```
@deploy-check prd game-server
```

##### 예시 3: 장애 분석

```markdown
<!-- ~/.kiro/prompts/incident-analysis.md -->
다음 장애를 분석해줘:
- 대상: ${1}
- 증상: ${2}

분석 항목:
1. 타임라인 정리
2. 근본 원인 추정
3. 영향 범위
4. 재발 방지 대책
```

```
@incident-analysis "prd-db-01" "커넥션 풀 고갈로 응답 지연"
```

##### 예시 4: Ansible Playbook 리뷰

```markdown
<!-- ~/.kiro/prompts/ansible-review.md -->
@${1} Ansible Playbook을 리뷰해줘:
- idempotent 여부
- 에러 핸들링 (failed_when, ignore_errors)
- 변수 하드코딩 여부
- 보안 (vault, 권한)
- 성능 (serial, forks, async)
```

```
@ansible-review ./playbooks/deploy.yml
```

#### 팁

- 공통 프롬프트는 `~/.kiro/prompts/` (글로벌), 프로젝트 전용은 `.kiro/prompts/` (로컬)에 배치
- 따옴표로 감싸면 공백 포함 인자를 하나로 전달: `@분석 "prd DB 서버"`
- MCP 프롬프트는 읽기 전용 (편집 불가)
- 프롬프트 내에서 `@파일경로` 로 파일 참조도 함께 사용 가능

### `/hooks` — 컨텍스트 훅

AI가 도구를 실행하기 전/후에 자동으로 실행되는 스크립트를 설정합니다.

```
/hooks              ← 설정된 훅 목록 확인
```

에이전트 설정 파일(`.kiro/agents/xxx.json`)에서 정의합니다.

> Hook 예제와 상세 설정은 [섹션 11. Hooks](#11-hooks-사용자-정의-동작) 참고

| 훅 타입          | 실행 시점                    | 활용 예시                      |
|------------------|------------------------------|--------------------------------|
| agentSpawn       | 에이전트 시작 시             | git status 자동 출력           |
| userPromptSubmit | 사용자 메시지 전송 시        | 타임스탬프 기록                |
| preToolUse       | 도구 실행 전                 | prd 파일 수정 차단             |
| postToolUse      | 도구 실행 후                 | 실행 로그 기록                 |
| stop             | AI 응답 완료 후              | 린트/포맷 자동 실행            |

### `/knowledge` — 지식 베이스

파일이나 디렉토리를 인덱싱해서 AI가 의미 기반 검색으로 참고할 수 있게 합니다.

```bash
/knowledge add --name docs --path ./docs/     # 문서 디렉토리 인덱싱
/knowledge show                                # 등록된 항목 확인
/knowledge remove <path>                       # 항목 삭제
/knowledge clear                               # 전체 초기화
```

`/context` 와의 차이:

| 항목          | `/context`                     | `/knowledge`                   |
|---------------|--------------------------------|--------------------------------|
| 방식          | 파일 전체를 컨텍스트에 로드    | 인덱싱 후 필요한 부분만 검색   |
| 적합 규모     | 소수 파일                      | 대량 문서                      |
| 검색 방식     | 없음 (전체 포함)               | 의미 기반 검색                 |

### `/mcp` — MCP 서버

외부 도구(Git, GitHub, DB 등)를 MCP 프로토콜로 연결해서 AI가 사용할 수 있게 합니다.

```bash
/mcp                # 연결된 MCP 서버 상태 확인
/mcp add            # MCP 서버 추가
/mcp remove         # MCP 서버 제거
```

에이전트 설정 파일에서 MCP 서버를 정의합니다:

> MCP 상세 설정, CLI 명령어, 트러블슈팅은 [섹션 16. MCP 서버 연동](#16-mcp-서버-연동) 참고

```json
{
  "mcpServers": {
    "git": {
      "command": "mcp-server-git",
      "args": ["--stdio"]
    }
  }
}
```
[⬆ 목차로 돌아가기](#목차)

## 3. 단축키 및 특수 입력

### 기본 단축키

| 단축키           | 기능                          | 비고                           |
|------------------|-------------------------------|--------------------------------|
| `Shift+Tab`      | Plan 에이전트 ↔ 이전 에이전트 | 토글 방식                      |
| `Ctrl+F`         | 퍼지 검색                     | 설정으로 키 변경 가능          |
| `Ctrl+T`         | Tangent 모드 토글             | 활성화 필요, 키 변경 가능      |
| `Ctrl+D`         | Delegate 모드                 | 활성화 필요, 키 변경 가능      |
| `Ctrl+C`         | 현재 응답 중단                | 일반 터미널 동작               |
| `Tab`            | 자동완성 힌트 수락            | 키 변경 가능                   |
| `@` + `Tab`      | 프롬프트 템플릿 자동완성      |                                |
| `↑` (위 화살표)  | 이전 입력 이력                |                                |
| `Ctrl+R`         | 입력 히스토리 검색 (대소문자 무시)    |

### 단축키 변경 설정

```bash
# 퍼지 검색 키 변경 (기본 f → Ctrl+F)
kiro-cli settings chat.skimCommandKey "f"

# Tangent 모드 키 변경 (기본 t → Ctrl+T)
kiro-cli settings chat.tangentModeKey "t"

# Delegate 모드 키 변경 (기본 d → Ctrl+D)
kiro-cli settings chat.delegateModeKey "d"

# 자동완성 수락 키 변경 (기본 Tab)
kiro-cli settings chat.autocompletionKey "Tab"
```


### 도구 승인 프롬프트 키

AI가 도구 실행 허가를 요청할 때 사용하는 키입니다.

| 키       | 기능                                              |
|----------|---------------------------------------------------|
| `y`      | 도구 실행 승인                                    |
| `n`      | 도구 실행 거부                                    |
| `t`      | 이 도구를 이후 자동 승인 (세션 내 trust)          |

### Subagent 실행 중 키

| 키         | 기능                                              |
|------------|---------------------------------------------------|
| `j` / `↓`  | 아래로 이동                                      |
| `k` / `↑`  | 위로 이동                                        |
| `y`        | 도구 실행 승인                                    |
| `n`        | 도구 실행 거부                                    |
| `Esc`      | 선택 해제                                         |
| `Ctrl+C`   | 전체 중단                                         |
### 에이전트별 커스텀 단축키

에이전트 설정 파일(`.kiro/agents/xxx.json`)에서 전용 단축키를 지정할 수 있습니다:

```json
{
  "name": "infra-agent",
  "keyboardShortcut": "ctrl+shift+a"
}
```

사용 가능한 조합:

| 수식키 (조합 가능)               | 키                             |
|----------------------------------|--------------------------------|
| `ctrl`, `shift`, `alt`          | `a-z`, `0-9`, `f1-f12`, `tab` |

⚠️ 같은 단축키를 여러 에이전트에 지정하면 충돌로 비활성화됩니다.

[⬆ 목차로 돌아가기](#목차)

## 4. Context Window 개념

### Context Window 란?

AI가 한 번에 읽을 수 있는 텍스트의 최대 크기입니다.
사람으로 치면 "책상 위에 펼쳐놓을 수 있는 종이의 양"과 같습니다.

```
+------------------------------------------------------------------+
|                     Context Window (책상)                         |
|                                                                  |
|  +--------------+  +----------------+  +----------------------+  |
|  | 시스템 프롬프트|  | 이전 대화 내용  |  | 참고 파일 (context)  |  |
|  | (AI 설정)    |  | (질문+답변)    |  | (코드, 문서 등)      |  |
|  +--------------+  +----------------+  +----------------------+  |
|                                                                  |
|  +--------------------+  +------------------------------------+  |
|  | 현재 질문           |  | AI 가 생성할 답변 공간             |  |
|  +--------------------+  +------------------------------------+  |
|                                                                  |
+------------------------------------------------------------------+
```

### 왜 중요한가?

Context Window 가 가득 차면:
- 이전 대화 내용을 잊어버림 (오래된 대화부터 잘림)
- 참고 파일을 더 이상 추가할 수 없음
- AI 답변 품질이 떨어짐

### 크기 비유

```
Context Window 크기 ≈ 약 200,000 토큰 (모델마다 다름)

1 토큰 ≈ 영어 4글자 / 한글 1~2글자

200,000 토큰 ≈ 일반 문서 약 300~500 페이지
```

### 사용량 확인

```
/context              ← 현재 Context Window 사용량 확인
```

출력 예시:
```
Context usage: 45% (90,000 / 200,000 tokens)
```

### Context Window 를 아끼는 방법

| 방법                 | 명령어       | 효과                                    |
|----------------------|--------------|-----------------------------------------|
| 대화 요약            | `/compact`   | 이전 대화를 요약하여 토큰 절약          |
| 대화 초기화          | `/clear`     | 전체 대화 삭제 (처음부터 시작)          |
| 파일 참고 최소화     | `/context`   | 필요한 파일만 등록                      |
| 지식 베이스 활용     | `/knowledge` | 대량 문서는 인덱싱으로 (전체 로드 방지) |

### 실제 흐름 예시

```
1회차: "서버 설정 방법 알려줘"
       Context: [시스템 프롬프트] + [질문] = 5%

2회차: "Ansible Playbook 만들어줘"
       Context: [시스템 프롬프트] + [1회차 대화] + [질문] = 15%

3회차: "이 파일 참고해서 수정해줘" + 파일 3개 첨부
       Context: [시스템 프롬프트] + [1~2회차 대화] + [파일 3개] + [질문] = 60%

  ... 대화가 계속되면 ...

N회차: Context 90% → /compact 실행 → 이전 대화 요약 → 40% 로 감소
```

⚠️ 긴 작업 시 `/compact` 를 중간중간 실행하면 Context Window 를 효율적으로 사용할 수 있습니다.

[⬆ 목차로 돌아가기](#목차)

## 5. `@` 참조 기능

프롬프트 입력 중 `@`를 사용하면 파일/디렉토리 내용을 메시지에 삽입하거나, 프롬프트 템플릿을 호출할 수 있습니다.

### 파일 참조

```
> @src/main.rs 이 파일 리뷰해줘
→ main.rs 내용이 메시지에 자동 삽입됨

> @config.toml 참고해서 @src/settings.rs 수정해줘
→ 두 파일 모두 삽입됨

> @src/ 디렉토리 구조 보여줘
→ 디렉토리 트리가 삽입됨
```

### 프롬프트 템플릿 호출

```
> @code-review src/main.rs rust
→ code-review 프롬프트 템플릿이 인자와 함께 실행됨
```

### Tab 자동완성

```
> @src/<Tab>          ← src/ 하위 파일 목록 표시
> @Cargo<Tab>         ← Cargo.toml 로 자동완성
> @code-<Tab>         ← 프롬프트 템플릿 자동완성
```

### 우선순위

같은 이름이 프롬프트와 파일 모두에 있을 경우:

| 우선순위 | 대상                           |
|----------|--------------------------------|
| 1 (최고) | 프롬프트 템플릿 (`/prompts`)   |
| 2        | 파일                           |
| 3 (최저) | 디렉토리                       |

파일을 강제로 참조하려면 `@./파일명` 으로 경로를 명시합니다.

### 제한 사항

| 항목              | 제한                                              |
|-------------------|---------------------------------------------------|
| 파일 크기         | 250KB 초과 시 잘림 (경고 표시)                    |
| 디렉토리 깊이     | 최대 3단계                                        |
| 디렉토리 항목     | 단계당 최대 10개 (초과 시 "... N more" 표시)      |
| 바이너리 파일     | ❌ 지원 안 됨 (이미지, 실행파일 등)               |
| glob 패턴         | ❌ `@*.rs` 불가                                   |
| 홈 디렉토리       | ❌ `@~` 불가                                      |
| 공백 포함 경로    | `@"path with spaces.txt"` 으로 따옴표 사용        |

[⬆ 목차로 돌아가기](#목차)

## 6. 쉘 통합 (Shell Integration)

### 설정

```bash
# ~/.bashrc 에 추가
eval "$(kiro-cli init bash pre)"
eval "$(kiro-cli init bash post)"
```

지원 쉘: `bash`, `zsh`, `fish`, `nu`

### pre / post 동작 원리

bash 의 `PROMPT_COMMAND` 메커니즘을 이용합니다.

```
명령어 실행 완료
       │
       ▼
  ┌─────────────┐
  │  post 훅    │  ← 이전 명령어 결과 수집 (exit code, 실행 시간 등)
  └─────────────┘
       │
       ▼
  ┌─────────────┐
  │  pre 훅     │  ← 다음 프롬프트 표시 직전 준비 (환경 설정, 자동완성 등)
  └─────────────┘
       │
       ▼
    $ _            ← 사용자 입력 대기
```

둘 다 설정해야 쉘 통합 기능이 정상 동작합니다.

### `kiro-cli translate` — 자연어 → 쉘 명령어 변환

```bash
$ kiro-cli translate "현재 디렉토리에서 10MB 이상 파일 찾기"
→ find . -size +10M -type f

$ kiro-cli translate "nginx 로그에서 500 에러만 추출"
→ grep " 500 " /var/log/nginx/access.log

$ kiro-cli translate "3일 이상 된 로그 파일 삭제"
→ find /var/log -name "*.log" -mtime +3 -delete
```

### `kiro-cli inline` — 쉘 인라인 자동완성

일반 쉘 프롬프트에서 타이핑하면 AI가 명령어를 자동완성 제안합니다.

```bash
# 활성화 / 비활성화 / 상태 확인
kiro-cli inline enable
kiro-cli inline disable
kiro-cli inline status
```

### CLI 서브커맨드 전체 목록

| 명령어                       | 설명                           |
|------------------------------|--------------------------------|
| `kiro-cli chat`              | AI 채팅 시작                   |
| `kiro-cli agent`             | 에이전트 관리                  |
| `kiro-cli settings`          | 설정 관리                      |
| `kiro-cli translate`         | 자연어 → 쉘 명령어 변환       |
| `kiro-cli inline`            | 쉘 인라인 자동완성             |
| `kiro-cli init <shell> pre`  | 쉘 통합 pre 훅 생성           |
| `kiro-cli init <shell> post` | 쉘 통합 post 훅 생성          |
| `kiro-cli mcp`               | MCP 서버 관리                  |
| `kiro-cli doctor`            | 설치 문제 진단                 |
| `kiro-cli update`            | Kiro CLI 업데이트              |
| `kiro-cli login`             | 로그인                         |
| `kiro-cli logout`            | 로그아웃                       |
| `kiro-cli whoami`            | 현재 사용자 정보               |
| `kiro-cli issue`             | GitHub 이슈 생성               |
| `kiro-cli diagnostic`        | 진단 테스트 실행               |
| `kiro-cli --version`         | 버전 확인                      |
| `kiro-cli --help-all`        | 전체 서브커맨드 도움말         |

[⬆ 목차로 돌아가기](#목차)

## 7. 도구 권한 관리 (Tool Trust)

### 세션 중 권한 변경

| 명령어                              | 설명                                    |
|-------------------------------------|-----------------------------------------|
| `/tools`                            | 도구 목록 및 현재 권한 확인             |
| `/tools trust-all`                  | 모든 도구 자동 승인 (확인 없이 실행)    |
| `/tools trust fs_write`             | 특정 도구만 자동 승인                   |
| `/tools trust fs_write execute_bash`| 여러 도구 동시 자동 승인                |
| `/tools untrust fs_write`           | 다시 확인 모드로 복원                   |
| `/tools reset`                      | 에이전트 기본 권한으로 초기화           |

⚠️ 세션 중 변경한 권한은 세션 종료 시 초기화됩니다.

### 시작 시 옵션으로 지정

```bash
# 전체 자동 승인
kiro-cli chat --trust-all-tools

# 특정 도구만 자동 승인
kiro-cli chat --trust-tools=fs_read,fs_write,execute_bash

# 모든 도구 확인 모드 (자동 승인 없음)
kiro-cli chat --trust-tools=
```

### `--trust-tools` 에 사용 가능한 도구 목록

#### 기본 내장 도구 (Native)

| 도구명          | 설명                           | 별칭 (alias)   |
|-----------------|--------------------------------|----------------|
| `fs_read`       | 파일/디렉토리 읽기             | `read`         |
| `fs_write`      | 파일 생성/수정                 | `write`        |
| `execute_bash`  | 쉘 명령어 실행                 | `shell`        |
| `grep`          | 텍스트 패턴 검색               |                |
| `glob`          | 파일 경로 패턴 검색            |                |
| `code`          | 코드 인텔리전스 (AST/LSP)     |                |
| `web_search`    | 웹 검색                        |                |
| `web_fetch`     | 웹 페이지 내용 가져오기        |                |
| `use_aws`       | AWS CLI 호출                   | `aws`          |
| `use_subagent`  | 서브에이전트 실행              | `subagent`     |
| `report_issue`  | GitHub 이슈 생성               | `report`       |
| `introspect`    | Kiro CLI 문서 검색             |                |

#### MCP 서버 도구

MCP 도구는 `@서버명/도구명` 형식으로 지정합니다:

```bash
kiro-cli chat --trust-tools=fs_read,@git/git_status,@git/git_log
```

### 에이전트 설정으로 영구 적용

> 에이전트 설정 파일 구조는 [섹션 9. .kiro/ 디렉토리 활용](#9-kiro-디렉토리-활용) 참고

`.kiro/agents/xxx.json` 에서 `allowedTools` 로 영구 자동 승인을 설정합니다:

```json
{
  "name": "infra-agent",
  "allowedTools": [
    "fs_read",
    "fs_write",
    "execute_bash",
    "grep",
    "glob",
    "@git/git_status"
  ]
}
```

### 권한 우선순위 (높은 순서)

| 우선순위 | 방법                              | 범위     |
|----------|-----------------------------------|----------|
| 1 (최고) | `/tools trust-all`                | 세션     |
| 2        | `/tools trust <도구>`             | 세션     |
| 3        | 에이전트 `allowedTools`           | 영구     |
| 4 (기본) | 확인 후 실행 (Ask)                | 기본값   |

[⬆ 목차로 돌아가기](#목차)

## 8. `/plan` — Plan 에이전트 상세

### 개요

복잡한 작업을 구조화된 구현 계획으로 분해하는 전용 에이전트입니다.
읽기 전용으로 동작하며, 파일 수정이나 명령 실행 없이 계획 수립에만 집중합니다.

### 사용법

```
/plan                       ← Plan 에이전트로 전환
Shift+Tab                   ← 이전 에이전트로 복귀
```

### 활용 시나리오

| 시나리오                          | 예시 입력                                          |
|-----------------------------------|----------------------------------------------------|
| 신규 서비스 구축 계획             | "게임 서버 모니터링 시스템 구축 계획 세워줘"       |
| 마이그레이션 계획                 | "CentOS 7 → Rocky 10 마이그레이션 단계 정리해줘"  |
| 자동화 설계                       | "Ansible 로 서버 100대 초기 세팅 자동화 설계해줘"  |
| 장애 대응 프로세스                | "DB 장애 시 복구 절차 플로우 만들어줘"             |

### 워크플로우

```
1. /plan 으로 전환
2. 구현하고 싶은 내용 설명
3. Plan 에이전트가 요구사항 정리 + 단계별 계획 출력
4. 계획 확인/수정
5. Shift+Tab 으로 기본 에이전트 복귀
6. 계획 기반으로 실제 작업 수행
```

### 특징

| 항목          | 내용                                              |
|---------------|---------------------------------------------------|
| 파일 수정     | ❌ 불가 (읽기 전용)                               |
| 명령 실행     | ❌ 불가                                           |
| 코드 분석     | ✅ 가능 (파일 읽기로 현재 구조 파악)              |
| 계획 출력     | ✅ 단계별 구조화된 계획                           |
| 전환 방법     | `/plan` 또는 `Shift+Tab`                          |

### 실전 사용 예시

#### 예시 1: CentOS → Rocky 마이그레이션 계획

```
> /plan
✔ Switched to agent: planner

[plan] > CentOS 7 서버 50대를 Rocky 10 으로 마이그레이션 계획 세워줘.
         현재 환경: 웹서버 20대, 게임서버 20대, DB 10대.
         다운타임 최소화 필요.

Plan 에이전트 출력 예시:

## 마이그레이션 계획

### Phase 1: 사전 준비 (1주)
- 현재 서버 인벤토리 작성 (OS 버전, 패키지 목록, 커널 파라미터)
- Rocky 10 테스트 서버 구축 및 호환성 검증
- 롤백 절차 수립

### Phase 2: dev/qa 환경 (1주)
- dev 서버 마이그레이션 → 기능 테스트
- qa 서버 마이그레이션 → QA 검증

### Phase 3: stg 환경 (1주)
- stg 서버 마이그레이션 → 부하 테스트
- 모니터링 지표 비교 (CPU, Memory, IO)

### Phase 4: prd 환경 (2주)
- 웹서버 → 게임서버 → DB 순서로 진행
- 서버당 1대씩 롤링 마이그레이션
- 각 서버 마이그레이션 후 24시간 모니터링

[plan] > Shift+Tab  ← 기본 에이전트로 복귀
> 위 계획대로 Phase 1 Ansible Playbook 만들어줘  ← 실제 작업 시작
```

#### 예시 2: 모니터링 시스템 구축 설계

```
[plan] > 게임 서버 100대 모니터링 시스템 구축 계획.
         요구사항: CPU/Memory/Disk/Network 실시간 모니터링,
         장애 알림 (Slack), 대시보드, 로그 수집.
```

#### 예시 3: Ansible 자동화 설계

```
[plan] > 신규 게임 서버 초기 세팅 자동화.
         OS 튜닝, 보안 설정, 모니터링 에이전트,
         게임 바이너리 배포까지 Ansible 로 자동화 설계해줘.
```

⚠️ Plan 에이전트는 계획만 세우고, 실제 파일 생성/명령 실행은 기본 에이전트로 복귀 후 수행합니다.

[⬆ 목차로 돌아가기](#목차)

## 9. `.kiro/` 디렉토리 활용

### 디렉토리 구조

```
~/.kiro/                           ← 글로벌 (모든 프로젝트 공통)
├── agents/                        ← 에이전트 설정
│   └── infra-agent.json
├── settings/                      ← CLI 설정
│   └── cli.json
└── skills/                        ← 스킬 (AI 행동 규칙)
    └── work-rules/
        └── SKILL.md

.kiro/                             ← 로컬 (프로젝트별, 글로벌보다 우선)
├── agents/
├── settings/
└── skills/
```

### agents/ — 에이전트 설정

용도별 AI 에이전트를 만들어서 도구 권한, 프롬프트, 참고 파일을 분리합니다.

#### `tools` vs `allowedTools` vs `prompt` vs `skill://`

| 필드             | 역할                                | 값 형태                          | 없으면?                    |
|------------------|-------------------------------------|----------------------------------|----------------------------|
| `tools`          | 사용 가능한 도구 카테고리 활성화    | 카테고리명 (`shell`, `read` 등)  | 해당 도구 자체를 못 씀     |
| `allowedTools`   | 사용자 확인 없이 자동 승인할 도구   | 실제 도구명 (`execute_bash` 등)  | 매번 `y/n` 확인 프롬프트   |
| `prompt`         | 에이전트 페르소나/정체성 정의       | 자유 텍스트                      | 기본 에이전트 동작         |
| `resources`      | 스킬(행동 규칙) 또는 파일 참조      | `skill://xxx`, `file://xxx`      | 추가 규칙 없음             |

`tools` 카테고리 → 실제 도구 매핑:

| `tools` 카테고리 | 포함되는 실제 도구 (`allowedTools`용)           |
|-------------------|-------------------------------------------------|
| `read`            | `fs_read`, `glob`, `grep`, `code`               |
| `write`           | `fs_write`                                      |
| `shell`           | `execute_bash`                                  |
| `aws`             | `use_aws`                                       |
| `delegate`        | `use_subagent`                                  |
| `thinking`        | 내부 추론 (별도 도구명 없음)                    |
| `knowledge`       | `web_search`, `web_fetch`                       |

실행 흐름:

```
1단계: tools → "이 카테고리 도구를 쓸 수 있나?"
   shell ✅ → execute_bash 사용 가능
   (tools에 없으면 아예 호출 불가)

2단계: allowedTools → "확인 없이 바로 실행할까?"
   execute_bash ✅ → 자동 실행
   (allowedTools에 없으면 매번 y/n 물어봄)
```

`prompt` vs `skill://` 설계 패턴:

```
prompt  = 직무기술서 (Job Description) — "너는 인프라 엔지니어다"
skill:// = 사내 업무 규정 (SOP)        — "위험 작업 전 확인받아라"

infra-engineer.json  ← prompt: 인프라 전문가 페르소나
  └── skill://work-rules   ← 공통 업무 규칙 (여러 에이전트 재사용)

dev-engineer.json    ← prompt: 개발자 페르소나
  └── skill://work-rules   ← 같은 규칙 재사용
  └── skill://code-review  ← 추가 스킬
```

#### 예시: 인프라 운영 에이전트

```json
// ~/.kiro/agents/infra.json
{
  "name": "infra",
  "description": "인프라 운영 전용 에이전트",
  "prompt": "시스템 엔지니어로서 답변해줘. 서버 운영, 모니터링, 자동화 중심으로.",
  "tools": [
    "fs_read", "fs_write", "execute_bash",
    "grep", "glob", "use_aws"
  ],
  "allowedTools": [
    "fs_read", "grep", "glob"
  ],
  "toolsSettings": {
    "execute_bash": {
      "autoAllowReadonly": true
    },
    "fs_write": {
      "allowedPaths": ["~/ansible/**", "~/terraform/**"]
    }
  },
  "resources": [
    "file://README.md"
  ],
  "hooks": {
    "agentSpawn": [
      {
        "command": "hostname && uptime",
        "description": "서버 상태 확인"
      }
    ]
  },
  "keyboardShortcut": "ctrl+shift+i",
  "welcomeMessage": "인프라 운영 에이전트입니다. 무엇을 도와드릴까요?"
}
```

```bash
# 사용법
kiro-cli chat --agent infra
# 또는 채팅 중
/agent swap infra
# 또는 단축키
Ctrl+Shift+I
```

#### 예시: 읽기 전용 에이전트 (안전 모드)

```json
// ~/.kiro/agents/readonly.json
{
  "name": "readonly",
  "description": "읽기 전용 - 파일 수정/명령 실행 불가",
  "tools": ["fs_read", "grep", "glob", "code"],
  "allowedTools": ["fs_read", "grep", "glob", "code"],
  "keyboardShortcut": "ctrl+shift+r"
}
```

### settings/ — CLI 설정

```json
// ~/.kiro/settings/cli.json
{
  "chat.enableCheckpoint": true,
  "chat.enableContextUsageIndicator": true,
  "chat.disableAutoCompaction": false,
  "chat.enableTodoList": true
}
```

```bash
# 터미널에서 설정 변경
kiro-cli settings chat.enableCheckpoint true

# 설정 확인
kiro-cli settings chat.enableCheckpoint
```

### skills/ — 스킬 (AI 행동 규칙)

스킬은 AI의 행동 규칙을 정의하는 markdown 파일입니다.
에이전트의 `resources` 에 등록하면 필요할 때 자동으로 로드됩니다.

#### 예시: 인프라 운영 규칙 스킬

```
# ~/.kiro/skills/infra-rules/SKILL.md
---
name: infra-operation-rules
description: Infrastructure operation rules for server tasks and deployments.
---
# Infra Operation Rules
# 1. Confirm before action
# 2. Environment: dev / qa / stg / prd
# 3. prd changes require confirmation
# 4. Delete: list targets → show impact → confirm
# 5. Docs: Korean, tables, vi-aligned
```

#### 에이전트에 스킬 연결

```json
{
  "name": "infra",
  "resources": [
    "skill://~/.kiro/skills/infra-rules/SKILL.md",
    "skill://~/.kiro/skills/work-rules/SKILL.md"
  ]
}
```

스킬은 `file://` 과 달리 항상 로드되지 않고, AI가 필요하다고 판단할 때만 로드됩니다 (Context Window 절약).

### 실전 구성 예시

```
~/.kiro/
├── agents/
│   ├── infra.json          ← 인프라 운영 (서버 관리, 모니터링)
│   ├── readonly.json       ← 읽기 전용 (안전 모드)
│   └── ansible.json        ← Ansible 전용 (playbook 작성)
├── settings/
│   └── cli.json            ← 전역 설정
└── skills/
    ├── work-rules/
    │   └── SKILL.md        ← 작업 확인 규칙 (복명복창)
    ├── infra-rules/
    │   └── SKILL.md        ← 인프라 운영 규칙
    └── naming-rules/
        └── SKILL.md        ← 네이밍 규칙
```

| 구분       | `file://` 리소스               | `skill://` 리소스              |
|------------|--------------------------------|--------------------------------|
| 로드 시점  | 에이전트 시작 시 항상 로드     | AI가 필요할 때만 로드          |
| 용도       | 항상 참고해야 하는 파일        | 상황에 따라 참고하는 규칙      |
| 토큰 사용  | 항상 소비                      | 필요할 때만 소비               |
| 예시       | README.md, 설정 파일           | 운영 규칙, 네이밍 규칙         |

[⬆ 목차로 돌아가기](#목차)

## 10. 토큰 절약 & 성능 최적화

### 스킬/프롬프트는 영어로 작성

한글은 토큰당 1\~2글자, 영어는 토큰당 3\~4글자입니다.
같은 의미를 영어로 작성하면 토큰을 약 30~50% 절약할 수 있습니다.

```
한글: "모든 작업 전에 수행할 내용을 명확히 출력합니다"  → ~25 토큰
영어: "Print task summary before execution"              → ~7 토큰
```

스킬 파일(SKILL.md)이나 에이전트 프롬프트는 영어로 작성하고,
출력 규칙에 `output language: Korean` 한 줄만 추가하면 됩니다.

### 적용 전후 비교

```markdown
<!-- 비효율: 한글 스킬 파일 (~600 토큰) -->
## 1. 복명복창 (작업 확인)
모든 작업 전에 요청 사항을 다시 확인하고 수행할 내용을 명확히 출력합니다.

<!-- 효율: 영어 스킬 파일 (~250 토큰) -->
## 1. Confirm before action
Print task summary before execution. format: "수행할 작업: - [item]"
```

### 토큰 절약 체크리스트

| 항목                          | 방법                                    | 절약 효과 |
|-------------------------------|-----------------------------------------|-----------|
| 스킬 파일 영어 작성           | SKILL.md 를 영어로, 출력만 한국어       | 30~50%    |
| 에이전트 프롬프트 영어 작성   | `"prompt"` 필드를 영어로                | 30~50%    |
| 불필요한 예시 제거            | AI는 패턴만 알면 됨                     | 20~30%    |
| `/compact` 주기적 실행        | 이전 대화 요약                          | 40~60%    |
| `/context` 최소화             | 필요한 파일만 등록                      | 가변      |
| `skill://` 사용               | `file://` 대신 필요 시에만 로드         | 가변      |

### 한글 높임말과 토큰

한글 높임말 어미(`~합니다`, `~하시겠습니까`)는 평서형보다 토큰을 더 소비합니다.

```
"추가 완료했습니다"   → ~10 토큰
"추가 완료"           → ~5 토큰

"진행하시겠습니까?"   → ~8 토큰
"진행할까요?"         → ~6 토큰
```

단, 이는 AI 응답(출력) 토큰이므로 스킬 파일(입력)과 성격이 다릅니다.

| 구분              | 토큰 절약 효과 | 권장                                    |
|-------------------|----------------|-----------------------------------------|
| 스킬/프롬프트     | ★★★★★         | 영어 작성 (매번 로드, 누적 효과 큼)     |
| AI 응답 높임말    | ★★☆☆☆         | 가독성 우선 (1회성 출력, 절약량 적음)   |
| 에이전트 prompt   | ★★★★☆         | 영어 작성 (에이전트 시작 시 로드)       |
| 사용자 질문       | ★☆☆☆☆         | 편한 대로 (입력량 자체가 적음)          |


### 모델별 비용/속도 선택

모델별 비용/속도 비교는 [섹션 19. Model](#19-model-모델-선택) 참고. `/model` 로 전환하면 비용과 속도를 최적화할 수 있습니다.

### Context Window 사용량 모니터링

```bash
# 프롬프트에 사용량 표시 활성화
kiro-cli settings chat.enableContextUsageIndicator true
```

표시 예시: `[45%] >` — 45% 사용 중

| 사용량     | 상태     | 조치                                    |
|------------|----------|-----------------------------------------|
| 0~50%      | 여유     | 정상 사용                               |
| 50~75%     | 주의     | 불필요한 `/context` 파일 제거 고려      |
| 75~90%     | 경고     | `/compact` 실행 권장                    |
| 90%~       | 위험     | `/compact` 필수, 또는 `/clear` 후 재시작|

### 자동 요약 (Compaction) 튜닝

> 전체 설정 옵션은 [섹션 18. 설정 옵션 전체 목록](#18-설정-옵션-전체-목록) 참고

```bash
# 자동 요약 비활성화 (수동 /compact 만 사용)
kiro-cli settings chat.disableAutoCompaction true

# 요약 시 최근 N쌍 메시지 보존
kiro-cli settings compaction.excludeMessages 5

# 요약 시 컨텍스트 윈도우 N% 보존
kiro-cli settings compaction.excludeContextWindowPercent 30
```

| 설정                                  | 효과                                  |
|---------------------------------------|---------------------------------------|
| `disableAutoCompaction: true`         | 자동 요약 끔 (수동 제어 선호 시)      |
| `excludeMessages: 5`                  | 최근 5쌍 대화는 요약에서 제외         |
| `excludeContextWindowPercent: 30`     | 컨텍스트 30%는 요약에서 보존          |

### MCP 도구 토큰 비용 확인

MCP 도구는 스키마만으로도 토큰을 소비합니다.

```
/tools
```

출력의 `~Tokens` 컬럼으로 도구별 토큰 비용을 확인할 수 있습니다:

```
Tool          ~Tokens  Permission
Native
- fs_read     1.2k     Trusted
- fs_write    892      Ask
@git
- git_status  423      Allowed
Total         2.5k
```

⚠️ 사용하지 않는 MCP 서버는 `"disabled": true` 로 비활성화하면 토큰을 절약할 수 있습니다.

### 대용량 파일 처리 전략

| 상황                          | 방법                                          |
|-------------------------------|-----------------------------------------------|
| 250KB 이상 파일               | `@` 참조 시 자동 잘림 → 필요한 부분만 지정   |
| 대량 문서 참조                | `/context` 대신 `/knowledge` 인덱싱 사용      |
| 로그 파일 분석                | `grep` 으로 필요한 부분만 추출 후 전달        |
| 디렉토리 전체 참조            | `@dir/` 대신 특정 파일만 `@dir/file.conf`    |

### 응답 속도 최적화

| 방법                          | 효과                                          |
|-------------------------------|-----------------------------------------------|
| 경량 모델 사용                | `claude-haiku-4.5` 또는 `qwen3-coder-next`   |
| Context Window 줄이기         | 불필요한 파일/대화 정리                       |
| MCP 서버 최소화               | 필요한 서버만 활성화                          |
| `autoAllowReadonly: true`     | 읽기 도구 승인 프롬프트 제거 → 흐름 끊김 방지|
| `/tools trust-all`            | 전체 승인 → 중단 없는 연속 작업              |


[⬆ 목차로 돌아가기](#목차)

## 11. Hooks (사용자 정의 동작)

Kiro CLI에는 사용자 정의 슬래시 명령어 기능은 없지만,
Hooks 시스템으로 특정 시점에 자동 실행되는 커스텀 동작을 만들 수 있습니다.

### Hook 트리거 종류

| 트리거             | 실행 시점                  | matcher | 용도                          |
|--------------------|----------------------------|---------|-------------------------------|
| `agentSpawn`       | 에이전트 시작 시           | ❌      | 환경 정보 수집                |
| `userPromptSubmit` | 사용자 입력 시마다         | ❌      | 타임스탬프, 컨텍스트 주입     |
| `preToolUse`       | 도구 실행 전               | ✅      | 보안 검증, 작업 차단          |
| `postToolUse`      | 도구 실행 후               | ✅      | 로깅, 감사 기록               |
| `stop`             | AI 응답 완료 후            | ❌      | 포맷팅, 테스트, 정리          |

### Exit Code 동작

| Exit Code | 의미                                              |
|-----------|---------------------------------------------------|
| 0         | 성공. STDOUT이 컨텍스트에 추가됨                  |
| 2         | (preToolUse만) 도구 실행 차단. STDERR이 AI에 전달 |
| 기타      | 실패. STDERR이 경고로 표시됨                      |

### Hook 입력 (STDIN)

Hook은 JSON 형식으로 이벤트 정보를 STDIN으로 받습니다.

```json
{
  "hook_event_name": "preToolUse",
  "cwd": "/home/sjyun/project",
  "tool_name": "fs_write",
  "tool_input": {
    "path": "/etc/nginx/nginx.conf",
    "command": "create"
  }
}
```

### Matcher 패턴

| 패턴               | 매칭 대상                              |
|--------------------|----------------------------------------|
| `fs_write`         | fs_write 정확히 일치                   |
| `write`            | fs_write (별칭)                        |
| `fs_*`             | fs_read, fs_write 등                   |
| `@git`             | git MCP 서버의 모든 도구              |
| `@git/status`      | git MCP 서버의 status 도구만          |
| `@builtin`         | 모든 내장 도구                         |
| `*`                | 모든 도구 (내장 + MCP)                |

### 예제 1: 에이전트 시작 시 서버 상태 수집

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

AI가 시작할 때 서버 정보를 자동으로 컨텍스트에 포함합니다.

### 예제 2: prd 경로 파일 쓰기 차단

```bash
#!/bin/bash
# ~/.kiro/hooks/block-prd-write.sh
EVENT=$(cat)
PATH_VALUE=$(echo "$EVENT" | jq -r '.tool_input.path // empty')

if echo "$PATH_VALUE" | grep -q '/prd/\|/prd-'; then
  echo "❌ prd 환경 파일 쓰기 차단: $PATH_VALUE" >&2
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

### 예제 3: 위험 명령어 차단

```bash
#!/bin/bash
# ~/.kiro/hooks/block-dangerous-cmd.sh
EVENT=$(cat)
CMD=$(echo "$EVENT" | jq -r '.tool_input.command // empty')

BLOCKED="rm -rf|mkfs|dd if=|shutdown|reboot|systemctl stop"
if echo "$CMD" | grep -qE "$BLOCKED"; then
  echo "❌ 위험 명령어 차단: $CMD" >&2
  echo "해당 명령어는 직접 터미널에서 실행하세요." >&2
  exit 2
fi
exit 0
```

```json
{
  "hooks": {
    "preToolUse": [
      {
        "matcher": "execute_bash",
        "command": "~/.kiro/hooks/block-dangerous-cmd.sh",
        "description": "위험 명령어 차단"
      }
    ]
  }
}
```

### 예제 4: 파일 변경 시 Git diff 자동 표시

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

### 예제 5: 매 입력마다 현재 시각 주입

```json
{
  "hooks": {
    "userPromptSubmit": [
      {
        "command": "echo \"Current time: $(date '+%Y-%m-%d %H:%M:%S %Z')\"",
        "description": "현재 시각 컨텍스트 주입"
      }
    ]
  }
}
```

### 예제 6: AI 응답 후 자동 lint 실행

```json
{
  "hooks": {

    "stop": [
      {
        "command": "cd /home/sjyun/project && make lint 2>&1 | tail -5",
        "description": "응답 완료 후 lint 실행"
      }
    ]
  }
}
```

### 예제 7: 도구 실행 감사 로그

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

### 인프라 에이전트 Hooks 조합 예시

```json
{
  "name": "infra",
  "hooks": {
    "agentSpawn": [
      {
        "command": "hostname && uptime",
        "description": "서버 상태"
      }
    ],
    "preToolUse": [
      {
        "matcher": "fs_write",
        "command": "~/.kiro/hooks/block-prd-write.sh",
        "description": "prd 쓰기 차단"
      },
      {
        "matcher": "execute_bash",
        "command": "~/.kiro/hooks/block-dangerous-cmd.sh",
        "description": "위험 명령어 차단"
      }
    ],
    "postToolUse": [
      {
        "matcher": "*",
        "command": "~/.kiro/hooks/audit-log.sh",
        "description": "감사 로그"
      }
    ]
  }
}
```

### Hook 확인 명령어

```bash
# 현재 설정된 hooks 확인
/hooks

# 감사 로그 확인
tail -f ~/.kiro/audit.log
```

[⬆ 목차로 돌아가기](#목차)

## 12. Output Style (출력 스타일 제어)

Claude의 `/output-format` 같은 내장 스타일 전환 명령어는 없습니다.
대신 에이전트 `prompt` 또는 스킬로 출력 스타일을 제어합니다.

### 공식 설정

| 설정                              | 효과                          |
|-----------------------------------|-------------------------------|
| `chat.disableMarkdownRendering`   | 마크다운 렌더링 on/off        |
| `chat.diffTool`                   | diff 출력 도구 변경           |

```bash
# 마크다운 렌더링 끄기 (plain text)
kiro-cli settings chat.disableMarkdownRendering true

# diff 도구 변경
kiro-cli settings chat.diffTool delta
```

### 에이전트 prompt로 스타일 전환

용도별 에이전트를 만들어서 `/agent swap`으로 전환합니다.

```json
// ~/.kiro/agents/concise.json
{
  "name": "concise",
  "prompt": "Be extremely concise. No explanations unless asked. Bullet points only. Max 5 lines.",
  "keyboardShortcut": "ctrl+shift+c",
  "welcomeMessage": "간결 모드입니다."
}
```

```json
// ~/.kiro/agents/verbose.json
{
  "name": "verbose",
  "prompt": "Provide detailed explanations with examples, code snippets, and step-by-step reasoning.",
  "keyboardShortcut": "ctrl+shift+v",
  "welcomeMessage": "상세 모드입니다."
}
```

```bash
# 전환
/agent swap concise       # 간결 모드
/agent swap verbose       # 상세 모드
Ctrl+Shift+C              # 단축키로 간결 모드
Ctrl+Shift+V              # 단축키로 상세 모드
```

### 스킬로 스타일 제어

SKILL.md에 응답 규칙을 정의하면 모든 에이전트에 공통 적용됩니다.

```markdown
## Response style
- Concise and direct answers
- Skip unnecessary praise/agreement
- Output language: Korean
- Use tables for comparisons
- Use code blocks for commands
```

### 스타일 제어 방법 비교

| 방법                    | 범위              | 전환 방식              | 용도                |
|-------------------------|-------------------|------------------------|---------------------|
| `disableMarkdownRendering` | 전체           | 설정 변경              | 렌더링 on/off       |
| 에이전트 `prompt`       | 에이전트별        | `/agent swap` 또는 단축키 | 간결/상세 전환   |
| 스킬 (SKILL.md)         | 전체 또는 에이전트별 | 자동 적용           | 공통 출력 규칙      |
| 대화 중 직접 요청       | 현재 대화만       | "간결하게 답해줘"      | 일시적 변경         |


[⬆ 목차로 돌아가기](#목차)

## 13. Experimental Features (실험적 기능)

`/experiment` 명령어로 토글하거나 설정으로 활성화하는 실험적 기능입니다.

### 기능 목록

| 기능                    | 설정 키                          | 명령어/도구      | 설명                              |
|-------------------------|----------------------------------|------------------|-----------------------------------|
| Thinking                | `chat.enableThinking`          | `thinking` 도구 | 복잡한 문제 단계별 추론           |
| Tangent Mode            | `chat.enableTangentMode`       | `Ctrl+T`       | 대화 체크포인트, 사이드 토픽 탐색 |
| Knowledge               | `chat.enableKnowledge`         | `/knowledge`   | 대량 문서 인덱싱/검색             |
| Todo Lists              | `chat.enableTodoList`          | `/todos`       | 멀티스텝 작업 추적                |
| Checkpoint              | `chat.enableCheckpoint`        | `/checkpoint`  | 워크스페이스 스냅샷/복원          |
| Delegate                | `chat.enableDelegate`          | `delegate` 도구| 비동기 백그라운드 에이전트        |
| Subagent                | `chat.enableSubagent`          | `subagent` 도구| 동기 병렬 에이전트 (최대 4개)     |
| Context Usage Indicator | `chat.enableContextUsageIndicator` | 프롬프트 표시| 컨텍스트 사용량 % 표시            |

### 활성화 방법

```bash
# 방법 1: 대화형 토글
/experiment

# 방법 2: 설정 명령어
kiro-cli settings chat.enableThinking true
```

### Thinking (확장 추론)

Claude의 Extended Thinking과 유사한 기능입니다.
활성화하면 AI가 복잡한 질문에서 자동으로 단계별 추론 과정을 거친 뒤 답변합니다.

```bash
kiro-cli settings chat.enableThinking true
```

#### 예시 1: 아키텍처 설계

```
> 게임 서버 100대의 로그 수집 아키텍처를 설계해줘.
>  실시간 검색, 7일 보존, 비용 최소화 조건.

[thinking]
  1. 요구사항 분석: 100대, 실시간, 7일, 비용 최소화
  2. 옵션 비교:
     - ELK Stack: 유연하지만 운영 비용 높음
     - Loki + Grafana: 경량, 라벨 기반, 비용 효율적
     - CloudWatch: 관리형이지만 대량 시 비용 증가
  3. 트레이드오프 분석:
     - Loki가 비용/성능 균형 최적
     - 단, 전문 검색은 ELK 대비 약함
  4. 결론: Loki + Grafana + Promtail 조합 추천
[/thinking]

추천 아키텍처: Loki + Grafana + Promtail
(상세 설계 이어서...)
```

#### 예시 2: 트러블슈팅 추론

```
> 서버 CPU 100%인데 프로세스별 사용량 합계는 30%밖에 안 돼.
>  원인이 뭘까?

[thinking]
  1. CPU 100% vs 프로세스 합계 30% 불일치
  2. 가능한 원인:
     - top/ps가 보여주는 것은 user+system 중 user만
     - iowait가 높을 수 있음 (디스크 병목)
     - kernel thread (kworker, ksoftirqd) 미표시
     - steal time (가상화 환경)
  3. 확인 순서: vmstat → iostat → mpstat
[/thinking]

가장 가능성 높은 원인은 iowait 또는 steal time입니다.
확인 명령어: ...
```

#### 예시 3: 마이그레이션 의사결정

```
> MySQL 8.0 → PostgreSQL 17 마이그레이션 해야 할까?
>  현재 게임 서버 DB로 사용 중.

[thinking]
  1. 현재 상태: MySQL 8.0, 게임 서버 DB
  2. 마이그레이션 비용:
     - 쿼리 호환성 (AUTO_INCREMENT → SERIAL 등)
     - ORM 변경, 드라이버 변경
     - 데이터 마이그레이션 + 검증
  3. PostgreSQL 장점: JSON, 확장성, 라이선스
  4. MySQL 유지 장점: 변경 비용 0, 게임 업계 레퍼런스 많음
  5. 결론: 명확한 기술적 이유 없으면 마이그레이션 비추천
[/thinking]

현재 상황에서는 MySQL 유지를 추천합니다.
마이그레이션이 필요한 경우는: ...
```

### Tangent Mode (사이드 토픽)

대화 중 사이드 질문을 탐색하고 원래 대화로 돌아오는 기능입니다.

```bash
kiro-cli settings chat.enableTangentMode true
```

```
> Ansible playbook 작성 중...

Ctrl+T  ← tangent 모드 진입
[tangent] > YAML 문법에서 | 와 > 차이가 뭐야?
[tangent] > (답변 받음)
Ctrl+T  ← 원래 대화로 복귀, playbook 작업 계속
```

### 인프라 엔지니어 추천 실험 기능

```bash
# 추천 활성화 세트
kiro-cli settings chat.enableThinking true
kiro-cli settings chat.enableTodoList true
kiro-cli settings chat.enableCheckpoint true
kiro-cli settings chat.enableContextUsageIndicator true
kiro-cli settings chat.enableSubagent true
```

| 기능              | 인프라 활용도 | 이유                                  |
|-------------------|---------------|---------------------------------------|
| Thinking          | ★★★★★        | 아키텍처 설계, 장애 분석에 필수       |
| Todo Lists        | ★★★★☆        | 마이그레이션 등 멀티스텝 작업 추적    |
| Checkpoint        | ★★★★☆        | 위험한 변경 전 스냅샷                 |
| Context Indicator | ★★★★☆        | 긴 작업 시 컨텍스트 관리              |
| Subagent          | ★★★☆☆        | 병렬 조회/비교 분석                   |
| Tangent Mode      | ★★★☆☆        | 작업 중 사이드 질문                   |
| Knowledge         | ★★☆☆☆        | 대량 문서 있을 때만                   |
| Delegate          | ★★☆☆☆        | 장시간 백그라운드 작업                |


> Subagent/Delegate 실전 활용은 [섹션 14. 병렬 처리](#14-병렬-처리-parallel-execution) 참고
⚠️ 실험적 기능은 향후 변경되거나 제거될 수 있습니다.

---


[⬆ 목차로 돌아가기](#목차)

## 14. 병렬 처리 (Parallel Execution)

### 채팅 모드에서 병렬 처리

#### Subagent (동기 병렬, 최대 4개)

활성화:
```bash
kiro-cli settings chat.enableSubagent true
```

자연어로 요청하면 AI가 자동으로 서브에이전트를 분배합니다.

```
# 예시 1: 모든 리전 EC2 조회
"모든 AWS 리전의 EC2 인스턴스 개수를 병렬로 조회해줘"

# 예시 2: 여러 서버 상태 동시 확인
"dev, stg, prd 서버의 디스크 사용량을 동시에 확인해줘"

# 예시 3: 기술 비교
"Rocky Linux 10, Ubuntu 24.04, AlmaLinux 10 을 병렬로 비교 분석해줘"
```

실행 시 화면:
```
Invoking 3 subagents in parallel
1. default: Check EC2 in us-east-1, us-east-2, us-west-1, us-west-2
2. default: Check EC2 in ap-northeast-1, ap-northeast-2, ap-northeast-3, ap-southeast-1
3. default: Check EC2 in eu-west-1, eu-central-1, eu-north-1, sa-east-1
```

조작키:
```
j/↓  — 아래로 이동
k/↑  — 위로 이동
y    — 도구 실행 승인
n    — 도구 실행 거부
Ctrl+C — 전체 중단
```

#### Delegate (비동기 백그라운드)

활성화:
```bash
kiro-cli settings chat.enableDelegate true
```

백그라운드에서 실행하고 메인 대화를 계속할 수 있습니다.

```
# 장시간 작업을 백그라운드로
"ansible playbook 문법 검사를 백그라운드로 실행해줘"

# 상태 확인
"백그라운드 작업 상태 확인해줘"
```

#### Subagent vs Delegate 비교

| 항목           | Subagent                  | Delegate                  |
|----------------|---------------------------|---------------------------|
| 실행 방식      | 동기 (결과 대기)          | 비동기 (백그라운드)       |
| 동시 실행      | 최대 4개                  | 에이전트당 1개            |
| 결과 확인      | 자동으로 합산             | 수동 상태 확인            |
| 용도           | 병렬 조회, 비교 분석      | 장시간 작업               |
| 상호 통신      | ❌ 서로 독립              | ❌ 서로 독립              |

#### 에이전트 설정으로 서브에이전트 제어

```json
{
  "name": "infra",
  "toolsSettings": {
    "subagent": {
      "availableAgents": ["aws-ops", "ansible-agent", "monitoring-agent"],
      "trustedAgents": ["aws-ops"]
    }
  }
}
```

| 필드              | 설명                                          |
|-------------------|-----------------------------------------------|
| `availableAgents` | 서브에이전트로 사용 가능한 에이전트 목록       |
| `trustedAgents`   | 승인 없이 자동 실행되는 에이전트              |

### CLI 환경에서 병렬 처리 (비대화형)

`kiro-cli chat`의 `--no-interactive` 모드와 쉘 병렬 실행을 조합합니다.

#### 방법 1: xargs 병렬

```bash
# 모든 리전의 EC2 개수를 병렬 조회
aws ec2 describe-regions --query 'Regions[].RegionName' --output text \
  | tr '\t' '\n' \
  | xargs -P 8 -I {} bash -c '
    COUNT=$(aws ec2 describe-instances --region {} \
      --query "length(Reservations[].Instances[])" --output text 2>/dev/null)
    echo "{}: ${COUNT:-0}"
  ' \
  | sort
```

#### 방법 2: GNU parallel

```bash
# 여러 서버에 동시 명령 실행
parallel -j 10 'ssh {} "uptime && df -h / | tail -1"' \
  ::: server1 server2 server3 server4 server5
```

#### 방법 3: Ansible (인프라 병렬 실행의 정석)

```bash
# 기본 fork 5개 (ansible.cfg 에서 변경 가능)
ansible all -m shell -a "df -h / | tail -1" -f 20

# playbook 에서 serial 제어
ansible-playbook deploy.yml --forks 20
```

```yaml
# playbook 내 serial 제어
- hosts: webservers
  serial: 5          # 5대씩 순차 배포
  tasks:
    - name: Deploy application
      ...
```

#### 방법 4: Kiro CLI 비대화형 + 쉘 병렬

```bash
# 리전별 EC2 조회를 Kiro CLI로 병렬 실행
REGIONS="us-east-1 ap-northeast-2 eu-west-1"
for REGION in $REGIONS; do
  echo "$REGION 리전의 EC2 인스턴스 목록을 조회해줘" \
    | kiro-cli chat --no-interactive --trust-tools 2>/dev/null \
    > "result-${REGION}.txt" &
done
wait
cat result-*.txt
```

### 용도별 추천

| 작업                          | 추천 방법                     | 이유                          |
|-------------------------------|-------------------------------|-------------------------------|
| AWS 리소스 병렬 조회          | xargs + AWS CLI               | 가장 빠르고 직접적            |
| 서버 상태 동시 확인           | Ansible ad-hoc                | 인프라 표준 도구              |
| 기술 비교/분석                | Subagent (채팅)               | AI가 분석 + 요약              |
| 장시간 코드 분석              | Delegate (채팅)               | 백그라운드 실행               |
| CI/CD 파이프라인              | Kiro CLI --no-interactive     | 자동화 통합                   |
| 대규모 서버 배포              | Ansible playbook + serial     | 롤링 배포 제어                |


[⬆ 목차로 돌아가기](#목차)

## 15. CI/CD 비대화형 모드

### 기본 사용법

```bash
# 비대화형 모드로 실행, 결과를 파일로 저장
kiro-cli chat --no-interactive --trust-all-tools \
  "$(git diff main..HEAD) 이 변경사항의 개선점을 검토해줘" \
  > review.log 2>&1
```

### 주요 옵션

| 옵션                    | 설명                                    |
|-------------------------|-----------------------------------------|
| `--no-interactive`      | 비대화형 모드 (사용자 입력 없이 실행)   |
| `--trust-all-tools`     | 모든 도구 자동 승인 (확인 프롬프트 없음)|
| `--trust-tools=fs_read` | 특정 도구만 자동 승인                   |
| `--agent <name>`        | 특정 에이전트 사용                      |
| `--model <model>`       | 특정 모델 지정                          |
| `--wrap <always|never>` | 줄 바꿈 제어 (기본: auto-detect)        |

### GitLab CI 예시

```yaml
code-review:
  stage: review
  script:
    - git diff $CI_MERGE_REQUEST_DIFF_BASE_SHA..HEAD > diff.patch
    - |
      kiro-cli chat --no-interactive --trust-all-tools \
        "아래 diff 를 리뷰해줘. 보안, 성능, 코드 품질 관점에서 개선점을 정리해줘.
        $(cat diff.patch)" > review.log 2>&1
    - cat review.log
  artifacts:
    paths:
      - review.log
  only:
    - merge_requests
```

### GitHub Actions 예시

```yaml
- name: AI Code Review
  run: |
    git diff ${{ github.event.pull_request.base.sha }}..HEAD > diff.patch
    kiro-cli chat --no-interactive --trust-all-tools \
      "아래 diff 를 리뷰해줘. 보안, 성능, 코드 품질 관점에서 개선점을 정리해줘.
      $(cat diff.patch)" > review.log 2>&1
    cat review.log

- name: Upload Review
  uses: actions/upload-artifact@v4
  with:
    name: ai-review
    path: review.log
```

### 주의사항

| 항목                 | 내용                                              |
|----------------------|---------------------------------------------------|
| 인증                 | CI 환경에서 `kiro-cli login` 사전 설정 필요       |
| 토큰 제한            | diff 가 크면 Context Window 초과 가능             |
| 비용                 | 실행마다 API 호출 발생                            |
| `--trust-all-tools`  | CI 에서는 필수 (확인 프롬프트 불가)               |

> 도구 권한 상세는 [섹션 7. 도구 권한 관리](#7-도구-권한-관리-tool-trust) 참고
| diff 크기            | 너무 크면 파일별로 나눠서 리뷰하는 방식 권장      |


[⬆ 목차로 돌아가기](#목차)

## 16. MCP 서버 연동

### MCP (Model Context Protocol) 란

외부 도구(Git, GitHub, DB, 웹 검색 등)를 AI에 연결하는 프로토콜입니다.
MCP 서버를 추가하면 AI가 해당 도구를 직접 호출할 수 있습니다.

### 설정 파일 위치

| 범위              | 경로                              |
|-------------------|-----------------------------------|
| 글로벌            | `~/.kiro/settings/mcp.json`     |
| 워크스페이스      | `.kiro/settings/mcp.json`       |
| 에이전트별        | 에이전트 JSON의 `mcpServers` 필드|

워크스페이스 > 글로벌 순으로 우선 적용됩니다.

### CLI 명령어

```bash
# 서버 추가
kiro-cli mcp add --name git --command mcp-server-git --args --stdio

# 서버 추가 (워크스페이스 범위)
kiro-cli mcp add --name git --command mcp-server-git --args --stdio --scope workspace

# 서버 목록
kiro-cli mcp list

# 서버 상태 확인
kiro-cli mcp status --name git

# 서버 제거
kiro-cli mcp remove --name git

# 설정 파일에서 가져오기
kiro-cli mcp import --file servers.json workspace
```

### 채팅 중 확인

```
/mcp                ← 연결된 MCP 서버 상태 확인
/tools              ← MCP 도구 포함 전체 도구 목록 + 토큰 비용
```

### 에이전트에 MCP 서버 설정

```json
// ~/.kiro/agents/infra.json
{
  "name": "infra",
  "mcpServers": {
    "git": {
      "command": "mcp-server-git",
      "args": ["--stdio"]
    },
    "github": {
      "command": "mcp-server-github",
      "args": ["--stdio"],
      "env": {
        "GITHUB_TOKEN": "$GITHUB_TOKEN"
      },
      "timeout": 120000
    }
  },
  "tools": ["@git", "@github/get_issues"],
  "allowedTools": ["@git/git_status", "@git/git_log"]
}
```

### mcpServers 필드 옵션

| 필드        | 타입   | 필수 | 설명                              |
|-------------|--------|------|-----------------------------------|
| `command`   | string | ✅   | 서버 실행 명령어                  |
| `args`      | array  | ❌   | 명령어 인자                       |
| `env`       | object | ❌   | 환경 변수                         |
| `timeout`   | number | ❌   | 요청 타임아웃 ms (기본 120000)    |
| `disabled`  | boolean| ❌   | true 시 로드 안 함                |

### MCP 도구 참조 형식

| 형식                    | 의미                              |
|-------------------------|-----------------------------------|
| `@git`                | git 서버의 모든 도구              |
| `@git/git_status`     | git 서버의 git_status 도구만      |
| `@git/git_*`          | git 서버의 git_ 로 시작하는 도구  |

### 도구 이름 충돌 해결 (toolAliases)

여러 MCP 서버가 같은 이름의 도구를 제공할 때:

```json
{
  "toolAliases": {
    "@github-mcp/get_issues": "github_issues",
    "@gitlab-mcp/get_issues": "gitlab_issues"
  }
}
```

### 레거시 설정 호환

기존 `~/.aws/amazonq/mcp.json` 또는 `.amazonq/mcp.json` 설정을 사용하려면:

```json
{
  "useLegacyMcpJson": true
}
```

### MCP 트러블슈팅

| 증상                              | 원인                          | 해결                                  |
|-----------------------------------|-------------------------------|---------------------------------------|
| 서버 연결 실패                    | 바이너리 미설치               | `which mcp-server-git` 으로 확인    |
| 도구 목록에 안 보임               | 서버 로드 실패                | `/mcp` 로 상태 확인                 |
| 도구 이름 검증 오류               | 이름 64자 초과 또는 특수문자  | 서버 관리자에게 수정 요청             |
| 도구 설명 너무 큼 경고            | 설명 10,000자 초과            | 동작은 하지만 성능 저하 가능          |
| 타임아웃                          | 서버 응답 느림                | `timeout` 값 증가 또는 `mcp.initTimeout` 설정 |
| CI/CD에서 MCP 실패 시 종료        | 서버 시작 실패                | `--require-mcp-startup` 옵션 사용   |

---


[⬆ 목차로 돌아가기](#목차)

## 17. 트러블슈팅

### 자주 발생하는 문제

| 증상                              | 원인                          | 해결                                              |
|-----------------------------------|-------------------------------|---------------------------------------------------|
| 토큰 초과 / 응답 중단             | Context Window 가득 참        | `/compact` 실행 또는 `/clear` 후 재시작           |
| 에이전트 로드 안 됨               | JSON 문법 오류                | `kiro-cli agent validate --path <파일>` 로 검증   |
| MCP 서버 연결 실패                | 바이너리 미설치               | [섹션 16. MCP 트러블슈팅](#16-mcp-서버-연동) 참고                       |
| 설정 변경 후 반영 안 됨           | 세션 재시작 필요              | 채팅 종료 후 `kiro-cli chat` 재실행               |
| `/code` 명령 동작 안 함           | LSP 미초기화                  | `/code init` 실행                                 |
| 도구 권한 거부                    | trust 미설정                  | `/tools trust-all` 또는 `--trust-tools` 옵션      |
| 스킬 파일 로드 안 됨              | YAML frontmatter 누락         | `---` 로 감싼 name/description 추가               |
| 글로벌 에이전트 대신 로컬 적용    | 같은 이름 로컬 우선           | 파일명 확인 (대소문자 구분)                       |

### 디버깅 명령어

```bash
# 에이전트 목록 확인
kiro-cli agent list

# 에이전트 설정 검증
kiro-cli agent validate --path ~/.kiro/agents/infra.json

# MCP 서버 상태 확인
kiro-cli mcp list
kiro-cli mcp status --name <서버명>

# 설정값 확인
kiro-cli settings list
kiro-cli settings chat.enableCheckpoint

# 로그 수집 (지원 요청 시)
/logdump
```

### Context Window 초과 시 대처

```
1. /compact 실행 → 이전 대화 요약
2. 그래도 부족하면 /context 에서 불필요한 파일 제거
3. 최후 수단: /clear 후 필요한 컨텍스트만 다시 로드
```
[⬆ 목차로 돌아가기](#목차)

## 18. 설정 옵션 전체 목록

### 설정 관리 명령어

```bash
# 설정 목록 조회
kiro-cli settings list

# 특정 설정 조회
kiro-cli settings <KEY>

# 글로벌 설정 변경 (기본)
kiro-cli settings <KEY> <VALUE>

# 워크스페이스 설정 변경 (프로젝트별)
kiro-cli settings --workspace <KEY> <VALUE>

# 설정 삭제
kiro-cli settings --delete <KEY>

# 설정 파일 열기
kiro-cli settings open
```

### 설정 우선순위

```
워크스페이스 (.kiro/settings/cli.json) > 글로벌 (~/.kiro/settings/cli.json)
```

### 주요 설정 옵션

#### 채팅 기능

| 설정 키                              | 타입    | 기본값 | 설명                              |
|--------------------------------------|---------|--------|-----------------------------------|
| `chat.enableCheckpoint`              | boolean | false  | 체크포인트 기능                   |
| `chat.enableTodoList`                | boolean | false  | TODO 리스트 기능                  |
| `chat.enableThinking`                | boolean | false  | 복잡한 추론용 thinking 도구       |
| `chat.enableKnowledge`               | boolean | false  | 지식 베이스 기능                  |
| `chat.enableCodeIntelligence`        | boolean | false  | LSP 코드 인텔리전스              |
| `chat.enableDelegate`                | boolean | false  | delegate (비동기 백그라운드 에이전트) |
| `chat.enableTangentMode`             | boolean | false  | tangent 모드                      |
| `chat.enableSubagent`                | boolean | false  | subagent 기능                     |

#### 모델 / 에이전트

| 설정 키                              | 타입    | 기본값 | 설명                              |
|--------------------------------------|---------|--------|-----------------------------------|
| `chat.defaultModel`                  | string  | none   | 기본 AI 모델                      |
| `chat.defaultAgent`                  | string  | none   | 기본 에이전트                     |

#### UI / 표시

| 설정 키                              | 타입    | 기본값 | 설명                              |
|--------------------------------------|---------|--------|-----------------------------------|
| `chat.enableContextUsageIndicator`   | boolean | false  | 프롬프트에 컨텍스트 사용량 표시   |
| `chat.disableMarkdownRendering`      | boolean | false  | 마크다운 렌더링 비활성화          |
| `chat.greeting.enabled`              | boolean | true   | 시작 인사 메시지                  |
| `chat.enableHistoryHints`            | boolean | -      | 대화 히스토리 힌트                |
| `chat.enablePromptHints`             | boolean | -      | 빈 입력 시 프롬프트 힌트          |
| `chat.enableNotifications`           | boolean | -      | 데스크톱 알림                     |

#### 자동 요약 (Compaction)

| 설정 키                                  | 타입    | 기본값 | 설명                              |
|------------------------------------------|---------|--------|-----------------------------------|
| `chat.disableAutoCompaction`             | boolean | false  | 자동 요약 비활성화                |
| `compaction.excludeContextWindowPercent` | number  | -      | 요약 제외 컨텍스트 비율 (0~100)   |
| `compaction.excludeMessages`             | number  | -      | 요약 제외 최소 메시지 쌍 수       |

#### 단축키

| 설정 키                              | 타입    | 기본값 | 설명                              |
|--------------------------------------|---------|--------|-----------------------------------|
| `chat.tangentModeKey`                | string  | t      | tangent 모드 토글 키              |
| `chat.autocompletionKey`             | string  | -      | 자동완성 힌트 수락 키             |
| `chat.skimCommandKey`               | string  | -      | 퍼지 검색 키                      |
| `chat.delegateModeKey`              | string  | -      | delegate 명령 키                  |

#### MCP / API

| 설정 키                              | 타입    | 기본값  | 설명                              |
|--------------------------------------|---------|---------|-----------------------------------|
| `mcp.initTimeout`                    | number  | -       | MCP 서버 초기화 타임아웃 (ms)     |
| `mcp.noInteractiveTimeout`           | number  | -       | 비대화형 MCP 타임아웃 (ms)        |
| `api.timeout`                        | number  | -       | API 요청 타임아웃 (초)            |

#### 기타

| 설정 키                              | 타입    | 기본값 | 설명                              |
|--------------------------------------|---------|--------|-----------------------------------|
| `telemetry.enabled`                  | boolean | -      | 텔레메트리 수집 (글로벌 전용)     |
| `cleanup.periodDays`                 | number  | -      | 오래된 대화 자동 삭제 주기 (일)   |
| `chat.disableGranularTrust`          | boolean | -      | 세분화된 도구 권한 비활성화       |
| `chat.diffTool`                      | string  | -      | 외부 diff 도구 명령               |

### 인프라 엔지니어 추천 설정

```json
// ~/.kiro/settings/cli.json
{
  "chat.enableCheckpoint": true,
  "chat.enableContextUsageIndicator": true,
  "chat.enableTodoList": true,
  "chat.enableDelegate": true,
  "chat.greeting.enabled": false,
  "chat.disableAutoCompaction": false
}
```

[⬆ 목차로 돌아가기](#목차)

## 19. Model (모델 선택)

### 사용 가능한 모델

| 모델                   | 크레딧 배율 | 설명                                          |
|------------------------|-------------|-----------------------------------------------|
| `auto` (기본)        | 1.00x       | 작업별 최적 모델 자동 선택                    |
| `claude-opus-4.6`    | 2.20x       | 최신 Opus, 1M 컨텍스트                        |
| `claude-sonnet-4.6`  | 1.30x       | 최신 Sonnet, 1M 컨텍스트                      |
| `claude-sonnet-4`    | 1.30x       | 일반 코딩/추론용                              |
| `claude-haiku-4.5`   | 0.40x       | 경량 모델, 빠른 응답                          |
| `deepseek-3.2`       | 0.25x       | 실험적 프리뷰                                 |
| `minimax-m2.5`       | 0.25x       | 실험적 프리뷰                                 |
| `qwen3-coder-next`   | 0.05x       | 실험적 프리뷰, 최저 비용                      |

⚠️ 모델 목록은 리전과 시점에 따라 달라질 수 있습니다.

### 모델 변경 방법

| 방법                              | 범위              | 명령어                                    |
|-----------------------------------|-------------------|-------------------------------------------|
| 채팅 중 대화형 선택               | 현재 세션         | `/model`                                |
| 채팅 중 직접 지정                 | 현재 세션         | `/model claude-sonnet-4`                |
| 현재 모델을 기본값으로 저장       | 영구              | `/model set-current-as-default`         |
| CLI 시작 시 지정                  | 현재 세션         | `kiro-cli chat --model claude-opus-4.6` |
| 설정으로 기본 모델 지정           | 영구              | `kiro-cli settings chat.defaultModel <model-id>` |
| 에이전트별 모델 지정              | 에이전트별        | agent JSON의 `"model"` 필드           |
| 사용 가능한 모델 목록 확인        | -                 | `kiro-cli chat --list-models`           |

### 모델 선택 우선순위

```
에이전트 model 필드 > --model 옵션 > chat.defaultModel 설정 > auto (시스템 기본)
```

### 용도별 추천

| 용도                          | 추천 모델              | 이유                          |
|-------------------------------|------------------------|-------------------------------|
| 일반 작업 (기본)              | `auto`               | 작업별 최적 모델 자동 선택    |
| 복잡한 아키텍처 설계          | `claude-opus-4.6`    | 최고 추론 능력                |
| 일상 코딩/문서 작업           | `claude-sonnet-4.6`  | 성능/비용 균형                |
| 간단한 질문/빠른 응답         | `claude-haiku-4.5`   | 빠르고 저렴                   |
| 비용 최소화                   | `qwen3-coder-next`   | 0.05x 최저 비용               |

### 크레딧 확인

```
/usage              ← 현재 크레딧 사용량 확인
```

---


[⬆ 목차로 돌아가기](#목차)

## 20. 대화 관리 (Chat Save/Load)

### 대화 저장/불러오기

```bash
/chat save                    # 현재 대화 저장
/chat save my-session         # 이름 지정 저장
/chat load                    # 저장된 대화 목록에서 선택
/chat load my-session         # 이름으로 불러오기
```

### CLI에서 대화 관리

```bash
kiro-cli chat --resume                # 마지막 대화 이어서
kiro-cli chat --resume-picker         # 대화 선택해서 이어서
kiro-cli chat --list-sessions         # 저장된 대화 목록
kiro-cli chat --delete-session <ID>   # 대화 삭제
```

### 대화 저장 특성

| 항목              | 내용                                          |
|-------------------|-----------------------------------------------|
| 저장 범위         | 현재 디렉토리 기준 (디렉토리별 분리)          |
| 저장 위치         | 내부 DB (직접 접근 불필요)                     |
| resume            | 현재 디렉토리의 대화만 표시                   |
| 자동 삭제         | `cleanup.periodDays` 설정으로 제어           |

[⬆ 목차로 돌아가기](#목차)

## 21. 인프라 엔지니어 활용도 요약

| 명령어       | 한 줄 요약                                    | 활용도   |
|--------------|-----------------------------------------------|----------|
| `/context`   | AI에게 참고 파일 제공                         | ★★★★★   |
| `/plan`      | 복잡한 작업 계획 수립                         | ★★★★★   |
| `/hooks`     | 도구 실행 전/후 자동 스크립트                 | ★★★★☆   |
| `/prompts`   | 반복 프롬프트 템플릿                          | ★★★★☆   |
| `/mcp`       | 외부 도구 연결 (Git, DB 등)                   | ★★★★☆   |
| `/compact`   | 긴 대화 요약하여 컨텍스트 확보                | ★★★★☆   |
| `/chat`      | 대화 저장/불러오기                            | ★★★☆☆   |
| `/knowledge` | 대량 문서 인덱싱/검색                         | ★★★☆☆   |
| `/tools`     | AI 도구 목록/권한 확인                        | ★★★☆☆   |
| `/code`      | IDE 수준 코드 분석                            | ★★☆☆☆   |

[⬆ 목차로 돌아가기](#목차)

## 22. 참고 URL

### 공식 문서 (kiro.dev)

| 분류                    | URL                                                              |
|-------------------------|------------------------------------------------------------------|
| CLI 시작 가이드         | https://kiro.dev/docs/cli/                                       |
| CLI 소개                | https://kiro.dev/cli/                                            |
| 슬래시 명령어 레퍼런스  | https://kiro.dev/docs/cli/reference/slash-commands/              |
| 내장 도구 레퍼런스      | https://kiro.dev/docs/cli/reference/built-in-tools/              |
| 에이전트 생성           | https://kiro.dev/docs/cli/custom-agents/creating/                |
| 에이전트 설정 레퍼런스  | https://kiro.dev/docs/cli/custom-agents/configuration-reference  |
| 에이전트 예시           | https://kiro.dev/docs/cli/custom-agents/examples                 |
| Hooks                   | https://kiro.dev/docs/cli/hooks/                                 |
| Agent Skills            | https://kiro.dev/docs/cli/skills/                                |
| Code Intelligence       | https://kiro.dev/docs/cli/code-intelligence/                     |
| Tangent Mode            | https://kiro.dev/docs/cli/experimental/tangent-mode/             |
| Help Agent              | https://kiro.dev/docs/cli/chat/help-agent/                       |
| CLI Changelog           | https://kiro.dev/changelog/cli/                                  |

### 커뮤니티 / 외부 자료

| 분류                    | URL                                                              |
|-------------------------|------------------------------------------------------------------|
| Book of Kiro (커뮤니티) | https://kiro-community.github.io/book-of-kiro/kiro-intro/best-practices/ |
| Kiro Skills 모음 (GitHub)| https://github.com/jasonkneen/kiro                              |
| ARM 설치 가이드         | https://learn.arm.com/install-guides/kiro-cli/                   |
| AWS Kiro Boilerplate    | https://repost.aws/articles/ARXfJeAJ14Sh65Odc0rw6wOg            |

### AI 에이전트 스킬 관련

| 분류                    | URL                                                              |
|-------------------------|------------------------------------------------------------------|
| Agent Skills 공식 사이트 | https://agentskills.io/                                         |
| Agent Skills 스펙       | https://agentskills.io/specification                             |
| Anthropic Skills 저장소 | https://github.com/anthropics/skills                             |
| MADR (ADR 템플릿)       | https://adr.github.io/madr/                                     |


[⬆ 목차로 돌아가기](#목차)


---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-11

© 2026 siasia86. Licensed under CC BY 4.0.

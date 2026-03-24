# Kiro CLI 슬래시 명령어 레퍼런스

## 1. 명령어 전체 목록

### 대화 관리

| 명령어       | 설명                                              |
|--------------|---------------------------------------------------|
| `/quit`      | 종료                                              |
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

---

## 2. 컨텍스트 / 도구 상세

### `/context` — 컨텍스트 관리

AI에게 대화 중 참고할 파일을 추가하거나, 현재 컨텍스트 윈도우 사용량을 확인합니다.

```
/context                    ← 현재 컨텍스트 상태 확인
```

파일을 컨텍스트에 등록하면 매번 내용을 붙여넣지 않아도 AI가 참고할 수 있습니다.

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

자주 쓰는 프롬프트를 `.kiro/prompts/` 에 저장해두고 재사용합니다.

```
/prompts            ← 등록된 프롬프트 목록 확인
```

반복 요청 (코드 리뷰, 배포 체크리스트 등) 을 템플릿으로 만들어두는 용도입니다.

### `/hooks` — 컨텍스트 훅

AI가 도구를 실행하기 전/후에 자동으로 실행되는 스크립트를 설정합니다.

```
/hooks              ← 설정된 훅 목록 확인
```

에이전트 설정 파일(`.kiro/agents/xxx.json`)에서 정의합니다.

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

---

## 3. `/plan` — Plan 에이전트 상세

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

---

## 4. 인프라 엔지니어 활용도 요약

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

---

## 5. 단축키 및 특수 입력

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

---

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

---

## 7. Context Window 개념

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

---

## 8. `@` 참조 기능

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

---

## 9. CI/CD 비대화형 모드

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
| diff 크기            | 너무 크면 파일별로 나눠서 리뷰하는 방식 권장      |

---

## 10. 도구 권한 관리 (Tool Trust)

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

---

## 11. `.kiro/` 디렉토리 활용

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

```markdown
<!-- ~/.kiro/skills/infra-rules/SKILL.md -->
---
name: infra-operation-rules
description: 인프라 운영 시 따라야 할 규칙. 서버 작업, 배포, 삭제 시 적용.
---

# 인프라 운영 규칙

## 1. 작업 전 확인 (복명복창)
모든 작업 전에 수행할 내용을 명확히 출력합니다.

## 2. 환경 구분
- dev (Development) / qa (Quality Assurance) / stg (Staging) / prd (Production)
- 네이밍: [env]-[category]-[service]-[detail]

## 3. prd 환경 작업 제한
- prd 환경 파일 수정 시 반드시 확인 요청
- terraform apply, 서비스 재시작 전 확인 필수

## 4. 삭제 작업
- 삭제 대상 목록 출력 → 영향 범위 설명 → 확인 후 진행

## 5. 문서 작성 규칙
- 한국어 작성
- 테이블과 코드 블록 활용
- vi 에서 세로줄이 맞도록 정렬
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

---

## 12. 토큰 절약 팁

### 스킬/프롬프트는 영어로 작성

한글은 토큰당 1~2글자, 영어는 토큰당 3~4글자입니다.
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

---

## 13. 트러블슈팅

### 자주 발생하는 문제

| 증상                              | 원인                          | 해결                                              |
|-----------------------------------|-------------------------------|---------------------------------------------------|
| 토큰 초과 / 응답 중단             | Context Window 가득 참        | `/compact` 실행 또는 `/clear` 후 재시작           |
| 에이전트 로드 안 됨               | JSON 문법 오류                | `kiro-cli agent validate --path <파일>` 로 검증   |
| MCP 서버 연결 실패                | 바이너리 미설치 또는 PATH 누락| 터미널에서 직접 실행 테스트                       |
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

---

## 14. 설정 옵션 전체 목록

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
| `chat.enableDelegate`                | boolean | false  | subagent 위임 기능                |
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

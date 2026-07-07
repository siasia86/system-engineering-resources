# .kiro — Agent System Configuration

## 디렉토리 구조

```
.kiro/
├── README.md              ← 이 파일 (시스템 진입점)
├── memory.md              ← 세션 간 영구 기억 (100줄 제한)
├── agents/                ← 에이전트 정의 (*.json)
├── skills/                ← 재사용 가능 규칙/가이드 (SKILL.md)
├── prompts/               ← 작업별 프롬프트 템플릿 (*.md)
├── markdown/              ← 마크다운 작성 규칙 (STYLE.md, INDEX.md)
├── hooks/                 ← pre/post 훅 스크립트
├── settings/              ← CLI 설정 (cli.json)
└── sessions/              ← 세션 로그 (자동 생성)
```

## 오케스트레이션 규칙

- **system-engineer**가 오케스트레이터입니다
- 페르소나는 다른 페르소나를 호출하지 않습니다
- system-engineer만 `delegate`로 전문가 페르소나를 호출합니다

## 에이전트 매트릭스

| 에이전트         | 역할           | 모델              | 호출 조건           |
|------------------|----------------|-------------------|---------------------|
| system-engineer  | 오케스트레이터 | claude-sonnet-4.6 | 기본 세션           |
| code-reviewer    | 코드 리뷰      | claude-haiku-4.6  | 리뷰 요청 시        |
| security-auditor | 보안 감사      | claude-haiku-4.6  | 보안 검토 요청 시   |
| git-manager      | Git 워크플로우 | claude-haiku-4.6  | 커밋/PR 작성 시     |
| doc-reviewer     | 문서 품질 검사 | claude-sonnet-4.6 | .md 파일 검증 시    |
| markdown-writer  | 문서 작성      | claude-sonnet-4.6 | 문서 생성/수정 시   |
| se-lite          | 경량 Q&A       | claude-sonnet-4.6 | 개념/명령어 질문 시 |

## 호출 패턴

```
system-engineer (orchestrator)
    ├── delegate → code-reviewer     (코드/스크립트 리뷰)
    ├── delegate → security-auditor  (IaC 보안 감사)
    ├── delegate → git-manager       (커밋 메시지, PR)
    ├── delegate → doc-reviewer      (문서 품질 검증)
    └── delegate → markdown-writer   (문서 작성)
```


## Agent Loop 현황

Observe → Plan → Act → Verify 사이클이 skill/tool/rule로 동작합니다.

| 단계     | 대응                                              | 상태 |
|----------|---------------------------------------------------|------|
| Observe  | memory.md, STYLE.md, _reference/INDEX.md          | ✅   |
| Plan     | planning-and-breakdown, spec-driven-infra, §13    | ✅   |
| Act      | allowedTools, incremental-change, script templates | ✅   |
| Verify   | md-style-check.py, §12, testing-guide, hooks      | ✅   |
| Feedback | debugging-and-recovery, §1-1 (2회 실패→전환)      | ✅   |

### 향후 개선 (미구현)

| 항목 | 내용 | 트리거 |
|------|------|--------|
| Observe 자동화 | 세션 종료 시 memory.md 자동 summary 업데이트 | 세션 관리 기능 확장 시 |
| Verify 자동화 | hook에서 md-style-check/terraform validate 자동 실행 | CI 파이프라인 구축 시 |
| Feedback 자동 트리거 | 검증 실패 시 자동으로 수정 루프 재진입 | 에이전트 자율 실행 지원 시 |
## 금지 패턴

- code-reviewer → security-auditor 호출 (중첩 금지)
- security-auditor → code-reviewer 호출 (중첩 금지)
- "라우터" 페르소나 생성 (오케스트레이션은 system-engineer의 역할)

## 병렬 실행

배포 전 리뷰 시 병렬 fan-out 가능:

```
system-engineer
    ├── delegate → code-reviewer     ─┐
    ├── delegate → security-auditor  ─┼── 병렬 실행
    └── merge results                ─┘
```

## Skill Resources (system-engineer)

| skill                    | 용도                      | 자동 트리거    |
|--------------------------|---------------------------|----------------|
| `work-rules`             | 전체 작업 규칙 (§1~25)    | 항상 로드      |
| `using-skills`           | 작업 → skill 매핑         | 세션 시작 시   |
| `readme-template`        | README 푸터/배지          | .md 작성 시    |
| `bash-script-template`   | Bash 표준 구조/로깅       | .sh 작성 시    |
| `python-script-template` | Python 표준 구조/argparse | .py 작성 시    |
| `security-tools`         | 보안 검토/마스킹          | 보안 작업 시   |
| `md-link-check`          | 마크다운 링크/목차 검증   | .md 검증 시    |
| `debugging-and-recovery` | 장애 복구 워크플로        | 오류 발생 시   |
| `incremental-change`     | IaC 점진적 변경           | 코드 수정 시   |
| `planning-and-breakdown` | 작업 분해                 | 복합 작업 시   |
| `spec-driven-infra`      | 스펙 기반 인프라          | 신규 구축 시   |
| `doubt-driven-infra`     | 비가역 변경 안전 장치     | 위험 작업 시   |
| `shipping-checklist`     | 배포 체크리스트           | 배포/런칭 시   |
| `testing-guide`          | 테스트 작성 가이드        | 테스트 작성 시 |
| `code-review`            | 코드 리뷰 규칙            | 리뷰 요청 시   |
| `git-commit-rule`        | 커밋/PR 규칙              | Git 작업 시    |

### Context 파일

| 파일                                                               | 용도                 |
|--------------------------------------------------------------------|----------------------|
| `file://~/.kiro/memory.md`                                         | 세션 간 영구 기억    |
| `file://~/.kiro/markdown/STYLE.md`                                 | Markdown 작성 규칙   |
| `file:///root/32_system-engineering-resources/_reference/INDEX.md` | 기술 레퍼런스 인덱스 |

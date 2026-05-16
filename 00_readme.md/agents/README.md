# Agents

## 오케스트레이션 규칙

- **system-engineer**가 오케스트레이터입니다
- 페르소나는 다른 페르소나를 호출하지 않습니다
- system-engineer만 `delegate`로 전문가 페르소나를 호출합니다

## 에이전트 매트릭스

| 에이전트         | 역할               | 모델              | 호출 조건                    |
|------------------|--------------------|--------------------|------------------------------|
| system-engineer  | 오케스트레이터     | claude-sonnet-4.6  | 기본 세션                    |
| code-reviewer    | 코드 리뷰         | claude-haiku-4.6   | 리뷰 요청 시                 |
| security-auditor | 보안 감사         | claude-haiku-4.6   | 보안 검토 요청 시            |
| git-manager      | Git 워크플로우    | claude-haiku-4.6   | 커밋/PR 작성 시              |
| doc-reviewer     | 문서 품질 검사    | claude-sonnet-4.6  | .md 파일 검증 시             |
| markdown-writer  | 문서 작성         | claude-sonnet-4.6  | 문서 생성/수정 시            |

## 호출 패턴

```
system-engineer (orchestrator)
    ├── delegate → code-reviewer     (코드/스크립트 리뷰)
    ├── delegate → security-auditor  (IaC 보안 감사)
    ├── delegate → git-manager       (커밋 메시지, PR)
    ├── delegate → doc-reviewer      (문서 품질 검증)
    └── delegate → markdown-writer   (문서 작성)
```

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

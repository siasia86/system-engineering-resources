# Skills Index

전체 skill 목록과 용도입니다.

## Skill 목록

| skill                    | 용도                      | 트리거          |
|--------------------------|---------------------------|-----------------|
| `work-rules`             | 전체 작업 규칙 (§ 1~22)   | 항상            |
| `kiro-lock`              | 파일 동시 수정 방지       | 파일 수정 시    |
| `using-skills`           | 작업 유형 → skill 매핑    | 세션 시작       |
| `readme-template`        | README 푸터/배지          | .md 작성        |
| `bash-script-template`   | Bash 표준 구조/로깅       | .sh 작성        |
| `python-script-template` | Python 표준 구조/argparse | .py 작성        |
| `security-tools`         | 보안 검토/IP·JSON 마스킹  | 보안 작업       |
| `md-link-check`          | 마크다운 링크/목차 검증   | .md 검증        |
| `debugging-and-recovery` | 장애 복구 워크플로        | 오류 발생       |
| `incremental-change`     | IaC 점진적 변경           | 코드 수정       |
| `planning-and-breakdown` | 복합 작업 분해            | 3단계 이상 작업 |
| `spec-driven-infra`      | 스펙 기반 인프라 구축     | 신규 구축       |
| `doubt-driven-infra`     | 비가역 변경 안전 장치     | 위험 작업       |
| `shipping-checklist`     | 배포 전 체크리스트        | 배포/런칭       |
| `testing-guide`          | 테스트 작성 가이드        | 테스트 작성     |
| `code-review`            | 코드 리뷰 규칙            | 리뷰 요청       |
| `git-commit-rule`        | 커밋/PR 규칙              | Git 작업        |

## Agent 매핑

| agent            | 등록된 skills                                                                                 |
|------------------|-----------------------------------------------------------------------------------------------|
| system-engineer  | skill 17개 + file 2개 = 총 18개 (kiro-lock 제외, disabled)                                    |
| code-reviewer    | work-rules, kiro-lock, code-review, security-tools, testing-guide, git-commit-rule            |
| security-auditor | work-rules, kiro-lock, security-tools, code-review                                            |
| doc-reviewer     | work-rules, kiro-lock, md-link-check, STYLE.md                                                |
| markdown-writer  | work-rules, kiro-lock, readme-template, git-commit-rule, md-link-check, code-review, STYLE.md |
| se-lite          | work-rules, STYLE.md                                                                          |

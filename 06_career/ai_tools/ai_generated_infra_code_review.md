# AI가 만든 인프라 코드 검토 방법

AI 코딩 도구가 작성한 셸 스크립트, Terraform, Ansible, Dockerfile, Kubernetes 매니페스트를 운영에 넣기 전에 사람이 검토하는 기준을 정리합니다. 도구 비교가 아니라 결과물을 어떻게 의심하고 확인할지에 초점을 둡니다. 에이전트가 스스로 검증하게 만드는 환경 설계는 [Harness Engineering](./harness_engineering.md)을 참고합니다.

## 목차

| 섹션                                                                                                            |
|-----------------------------------------------------------------------------------------------------------------|
| [1. 왜 따로 검토해야 하는가](#1-왜-따로-검토해야-하는가) / [2. 자주 나오는 오류 유형](#2-자주-나오는-오류-유형) |
| [3. 검토 순서](#3-검토-순서) / [4. 형식별 자동 검사](#4-형식별-자동-검사)                                       |
| [5. 사람이 봐야 하는 항목](#5-사람이-봐야-하는-항목) / [6. 검토 점검표](#6-검토-점검표)                         |
| [7. 팀 운영 규칙](#7-팀-운영-규칙)                                                                              |

---

## 1. 왜 따로 검토해야 하는가

AI가 만든 코드는 문법이 맞고 그럴듯해 보여서 검토가 느슨해지기 쉽습니다. 인프라 코드는 실행 결과가 곧 운영 환경 변경이므로, 작은 실수도 데이터 손실·권한 노출·비용 증가로 이어집니다.

OWASP는 LLM 애플리케이션의 주요 위험 10가지(Top 10 for LLM, 2025판)를 정리하며, 그중 다음 항목이 AI 코드 작성과 직접 관련됩니다.

| 항목                                | AI 코드 작성에서 나타나는 모습                           |
|-------------------------------------|----------------------------------------------------------|
| LLM09:2025 Misinformation           | 없는 옵션·없는 패키지·안전하지 않은 코드를 사실처럼 제시 |
| LLM05:2025 Improper Output Handling | 모델 출력을 검증 없이 셸·SQL·설정에 그대로 사용          |
| LLM06:2025 Excessive Agency         | 에이전트에 필요 이상 권한을 줘 의도하지 않은 변경 실행   |
| LLM03:2025 Supply Chain             | 출처가 불분명한 모듈·이미지·패키지 도입                  |

OWASP의 Misinformation 항목은 코딩 도우미가 존재하지 않는 패키지 이름을 제안하고, 공격자가 그 이름으로 악성 패키지를 등록하는 시나리오를 예로 듭니다. 이 문서의 검토 기준은 이런 위험을 사람이 걸러 내기 위한 것입니다.

[⬆ 목차로 돌아가기](#목차)

---

## 2. 자주 나오는 오류 유형

| 유형                | 예                                                                 | 확인 방법                                |
|---------------------|--------------------------------------------------------------------|------------------------------------------|
| 없는 옵션·인자      | 실제로는 없는 CLI 플래그, 판이 다른 Terraform 인자                 | 공식 문서·`--help`·provider 문서 대조    |
| 오래된 문법         | 폐기된 모듈 이름, 옛 API 판                                        | 사용하는 도구 판의 변경 기록 확인        |
| 없는 패키지·이미지  | 비슷한 이름의 존재하지 않는 패키지                                 | 공식 저장소에서 이름·배포자·이력 확인    |
| 과도한 권한         | `"Action": "*"`, `0.0.0.0/0` 허용, `chmod 777`, `privileged: true` | 정책 검사 도구, 사람 검토                |
| 오류 무시           | 실패해도 다음 단계 진행, 오류를 `true`로 덮음                      | `set -euo pipefail`, 종료 코드 처리 확인 |
| 멱등성 부족         | 두 번 실행하면 중복 생성·덮어쓰기                                  | 두 번 실행해 보는 시험                   |
| 하드코딩된 값       | 비밀번호, 계정 ID, 지역, 내부 주소가 코드에 들어감                 | 비밀 검사 도구, 변수화                   |
| 범위를 넘는 변경    | 요청하지 않은 파일·리소스까지 수정                                 | diff 전체 확인, plan 결과 확인           |
| 자신 있는 틀린 설명 | 코드와 다른 동작을 주석·설명에 적음                                | 설명이 아니라 코드와 실행 결과로 판단    |

멱등성(idempotency)은 같은 작업을 여러 번 실행해도 결과가 한 번 실행한 것과 같은 성질입니다. Ansible·Terraform 코드는 이 성질을 기대하고 운영됩니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. 검토 순서

```text
1. Scope check    : diff touches only requested files/resources?
2. Static checks  : formatter, linter, policy scanner
3. Dry run        : plan / --check / server-side dry run
4. Human review   : permissions, data loss, cost, rollback
5. Test env apply : apply in non-production, run twice
6. Record         : what was checked, by whom, what was not checked
```

각 단계의 판단 기준입니다.

1. **범위 확인**: `git diff --stat`으로 바뀐 파일 목록부터 봅니다. 요청과 관계없는 파일이 있으면 이유를 확인하거나 되돌립니다.
2. **정적 검사**: 자동 도구로 잡을 수 있는 문제를 먼저 없앱니다. 사람의 검토 시간은 자동 도구가 못 잡는 항목에 씁니다.
3. **모의 실행**: 실제로 무엇이 바뀌는지 도구가 계산한 결과를 봅니다. 특히 삭제(destroy)·교체(replace) 항목을 찾습니다.
4. **사람 검토**: 5절의 항목을 확인합니다.
5. **시험 환경 적용**: 운영과 분리된 환경에서 적용하고, 같은 코드를 한 번 더 적용해 변경이 없는지(멱등성) 봅니다.
6. **기록**: 실행한 검사, 실행하지 못한 검사, 남은 위험을 변경 기록에 남깁니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 형식별 자동 검사

아래 도구는 판 번호에 따라 옵션이 달라질 수 있으므로 설치한 판의 `--help`와 공식 문서로 확인한 뒤 사용합니다.

### 셸 스크립트

```bash
bash -n deploy.sh           # 문법만 검사, 실행하지 않음
shellcheck deploy.sh        # 따옴표 누락, 잘못된 비교, 위험한 패턴 경고
```

ShellCheck는 셸 스크립트의 흔한 실수(변수 따옴표 누락으로 인한 단어 분리, 잘못된 조건식 등)를 정적으로 찾는 도구입니다.

### Terraform

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
tflint --recursive
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary > tfplan.json
checkov -f tfplan.json
```

- `terraform validate`는 문법과 내부 일관성을 검사하지만 원격 상태나 실제 리소스는 확인하지 않습니다.
- TFLint는 provider별 규칙으로 잘못된 인스턴스 유형 같은 오류를 찾습니다.
- Checkov는 Terraform 코드나 plan JSON을 정책 규칙(공개 버킷, 암호화 누락 등)으로 검사합니다.

plan 결과에서 삭제·교체 항목만 골라 보는 예입니다(`jq` 필요).

```bash
jq -r '.resource_changes[]
  | select(.change.actions | index("delete"))
  | "\(.change.actions | join(",")) \(.address)"' tfplan.json
```

### Ansible

```bash
ansible-playbook site.yml --syntax-check
ansible-lint site.yml
ansible-playbook -i inventory/staging site.yml --check --diff
```

🟡 주의: `--check` 모드는 모든 모듈이 지원하지 않습니다. `command`·`shell` 모듈 작업은 check 모드에서 건너뛰거나 실제와 다르게 보일 수 있으므로, 이런 작업은 사람이 따로 읽습니다.

### Dockerfile과 Kubernetes

```bash
hadolint Dockerfile
kubectl apply --dry-run=server -f manifest.yaml
kubectl diff -f manifest.yaml
checkov -d k8s/ --framework kubernetes
```

`--dry-run=server`는 API 서버가 검증만 하고 저장하지 않는 모드입니다. 클러스터 접근 권한이 필요하므로 대상 컨텍스트를 먼저 확인합니다(`kubectl config current-context`).

### 비밀 정보

```bash
gitleaks dir -v .           # 작업 디렉터리 검사
gitleaks git -v .           # 저장소 이력 검사
```

Gitleaks 공식 저장소는 v8.19.0부터 `detect`·`protect` 하위 명령이 폐기 예정이 되었고 `git`·`dir`·`stdin`을 쓰라고 안내합니다(2026-11-16 확인).

[⬆ 목차로 돌아가기](#목차)

---

## 5. 사람이 봐야 하는 항목

자동 검사를 통과해도 다음은 사람이 판단해야 합니다.

### 권한

- IAM 정책·역할에 와일드카드(`*`)가 있다면 실제 필요한 동작으로 줄일 수 있는가
- 보안 그룹·방화벽 규칙이 필요한 출발지와 포트만 허용하는가
- 컨테이너가 root로 실행되거나 `privileged`·호스트 경로 마운트를 쓰는가
- 스크립트가 `sudo`를 필요 이상으로 쓰는가

### 데이터 손실

- 삭제·교체되는 리소스에 데이터가 있는가(DB, 볼륨, 버킷)
- `prevent_destroy`, 삭제 보호, 백업 설정이 유지되는가
- 셸에서 `rm -rf "$VAR/"`처럼 변수가 비면 위험한 경로가 되는 패턴이 있는가

```bash
# 위험: TARGET이 비어 있으면 "/"를 지우게 됨
rm -rf "$TARGET/"

# 안전한 형태: 변수가 비었거나 설정되지 않았으면 즉시 중단
rm -rf "${TARGET:?TARGET is empty}/"
```

### 비용과 규모

- 인스턴스 유형·노드 수·저장 용량이 요청한 규모와 맞는가
- 로그 보존 기간, 데이터 전송 경로(리전 간·인터넷)가 비용을 키우지 않는가

### 출처와 판

- 새로 추가된 모듈·패키지·이미지가 실제 공식 배포처에 있는가
- 판 번호를 고정했는가(`latest` 태그, 판 범위 미지정 피하기)
- 이미지 태그 대신 다이제스트 고정이 필요한 환경인가

### 되돌리기

- 실패하면 어떻게 원복하는가(이전 상태 파일, 이전 이미지, 설정 백업)
- 되돌리기 절차를 실제로 시험했는가

[⬆ 목차로 돌아가기](#목차)

---

## 6. 검토 점검표

변경 요청(PR·MR)마다 붙여 쓰는 점검표 예입니다.

```markdown
## AI 작성 코드 검토

- 작성 도구와 요청 요약:
- 사람 검토자:

### 범위
- [ ] 바뀐 파일이 요청 범위 안에 있다
- [ ] 요청하지 않은 리소스 변경이 없다

### 자동 검사
- [ ] 형식 검사 통과
- [ ] 린터 통과 (경고를 무시했다면 이유 기록)
- [ ] 정책 검사 통과
- [ ] 비밀 검사 통과
- [ ] 모의 실행 결과 첨부 (plan / --check / dry-run)

### 사람 검토
- [ ] 삭제·교체 항목을 하나씩 확인했다
- [ ] 권한이 최소 범위다
- [ ] 새 패키지·모듈·이미지의 출처를 공식 배포처에서 확인했다
- [ ] 판 번호가 고정되어 있다
- [ ] 오류 처리와 멱등성을 확인했다
- [ ] 되돌리기 방법이 있다

### 기록
- 실행한 검사:
- 실행하지 못한 검사와 이유:
- 남은 위험:
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 팀 운영 규칙

| 규칙                                 | 이유                                                           |
|--------------------------------------|----------------------------------------------------------------|
| 작성자와 다른 사람이 승인            | 요청한 사람은 결과를 기대대로 읽기 쉬움                        |
| AI 작성 여부를 변경 기록에 표시      | 사후 분석 때 원인 추적에 도움                                  |
| 자동 검사는 CI에서 강제              | 사람마다 검사 누락이 생기지 않게 함                            |
| 운영 자격증명을 에이전트에 주지 않음 | 모의 실행까지만 에이전트가 하고, 적용은 승인된 파이프라인이 함 |
| 적용 권한은 단계별로 분리            | 개발 → 시험 → 운영 순서로 승인                                 |
| 실패 사례를 공유                     | 같은 유형의 오류를 지침·린터 규칙으로 막음                     |

에이전트의 권한 범위와 위험은 [AI 에이전트 보안 위험](../../07_ai_transformation/agent_security_risks.md), 반복 실행 설계는 [Loop Engineering](./loop_engineering.md)을 함께 참고합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- OWASP GenAI Security Project: [LLM Top 10 for 2025](https://genai.owasp.org/llm-top-10/) — ★★★☆☆ (확인일 2026-11-16)
- OWASP: [LLM09:2025 Misinformation](https://genai.owasp.org/llmrisk/llm092025-misinformation/) — ★★★☆☆ (확인일 2026-11-16)
- [ShellCheck](https://www.shellcheck.net/) — ★★★☆☆ (확인일 2026-11-16)
- HashiCorp: [terraform validate](https://developer.hashicorp.com/terraform/cli/commands/validate), [terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan) — ★★★☆☆ (확인일 2026-11-16)
- GitHub: [terraform-linters/tflint](https://github.com/terraform-linters/tflint) — ★★★☆☆ (확인일 2026-11-16)
- Checkov: [Terraform Plan Scanning](https://www.checkov.io/7.Scan%20Examples/Terraform%20Plan%20Scanning.html) — ★★★☆☆ (확인일 2026-11-16)
- Ansible: [Ansible Lint Documentation](https://ansible.readthedocs.io/projects/lint/) — ★★★☆☆ (확인일 2026-11-16)
- GitHub: [hadolint/hadolint](https://github.com/hadolint/hadolint) — ★★★☆☆ (확인일 2026-11-16)
- GitHub: [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) — ★★★☆☆ (확인일 2026-11-16)
- 관련 문서: [Harness Engineering](./harness_engineering.md), [Loop Engineering](./loop_engineering.md), [AI 에이전트 보안 위험](../../07_ai_transformation/agent_security_risks.md)

---

**작성일**: 2026-11-16

**마지막 업데이트**: 2026-11-16

© 2026 siasia86. Licensed under CC BY 4.0.

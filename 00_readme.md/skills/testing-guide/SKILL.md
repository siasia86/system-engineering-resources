---
name: testing-guide
description: Guides test writing with AAA pattern, BVA, and equivalence partitioning. Use when writing unit tests, integration tests, or infrastructure validation tests.
---

# Testing Guide

Apply when: "테스트 작성", "테스트 추가", "test", "write test"

## Structure (AAA Pattern)

```python
def test_<target>_<condition>_<expected>():
    # Arrange
    ...
    # Act
    ...
    # Assert
    ...
```

## FIRST Principles
- Fast: no external I/O
- Isolated: no dependency between tests
- Repeatable: same result every run
- Self-validating: assert determines pass/fail
- Timely: written with production code

## Boundary Value Analysis (BVA)

For any range [min, max], always test:
- min-1, min, min+1, max-1, max, max+1

## Equivalence Partitioning (EP)

- Identify valid/invalid partitions
- Pick 1 representative from each partition
- Include: None, empty string, empty list

## Coverage Target
- Branch coverage priority (both if/else)
- Exception paths (try/except, raise conditions)
- Normal path + error path

## pytest Rules
- `@pytest.mark.parametrize` for multiple inputs
- `@pytest.fixture` for shared setup
- `pytest.raises()` for exception verification
- File: `test_<module>.py`
- Function: `test_<target>_<condition>_<expected>()`

## Mock Rules
- External API, DB, filesystem → Mock
- Pure logic functions → no Mock
- Use `unittest.mock.patch`

## Test Type Selection

| Request | Test Type |
|---------|-----------|
| Function/class | Unit test (BVA + EP) |
| Module integration | Integration test |
| Bug fix | Regression test (reproduce bug) |
| API endpoint | Integration + status code |

## Checklist (every test)
- [ ] Happy path
- [ ] Error case (invalid input, exception)
- [ ] Boundary values (min, max, min-1, max+1)
- [ ] Empty input (None, "", [])
- [ ] Idempotency (if applicable)

## Infrastructure Testing

| 대상 | 검증 명령어 |
|------|-------------|
| Terraform syntax | `terraform validate` |
| Terraform format | `terraform fmt -check` |
| Terraform plan | `terraform plan` (No unexpected changes) |
| Ansible syntax | `ansible-playbook --syntax-check` |
| Ansible dry-run | `ansible-playbook --check --diff` |
| Shell scripts | `shellcheck <script>.sh` |
| Shell syntax | `bash -n <script>.sh` |

### IaC Test Principles
- `terraform plan` before every apply
- `ansible --check` before every run
- Idempotency: re-run produces no changes
- Validate after apply: health check, resource state query
- Test failure → switch to `skill://debugging-and-recovery`

### Container / Docker Testing

| 대상 | 검증 명령어 |
|------|-------------|
| Dockerfile lint | `hadolint Dockerfile` |
| Image build | `docker build --no-cache -t test .` |
| Container health | `docker inspect --format='{{.State.Health.Status}}'` |
| Compose syntax | `docker compose config` |
| Port binding | `ss -tlnp \| grep <port>` |

### Post-Change Verification Pattern

변경 후 반드시 실행하는 검증 순서:

```bash
# 1. 문법/구문 검증
terraform validate && terraform fmt -check
ansible-playbook --syntax-check site.yml
bash -n script.sh && shellcheck script.sh

# 2. Dry-run
terraform plan
ansible-playbook --check --diff site.yml

# 3. 적용 후 상태 확인
terraform plan  # "No changes" 확인
curl -f http://endpoint/health
aws ec2 describe-instance-status --instance-ids <id>
```

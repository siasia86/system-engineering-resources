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

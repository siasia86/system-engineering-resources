# 배열 (Array)

## 개요

연속된 메모리 공간에 같은 타입의 데이터를 순서대로 저장하는 자료구조.

## 종류

| 종류                | 설명                                                            |
|---------------------|-----------------------------------------------------------------|
| 정적 배열 (Static)  | 크기 고정, 컴파일 타임에 결정                                   |
| 동적 배열 (Dynamic) | 크기 가변, 용량 초과 시 자동 확장 (Python list, Java ArrayList) |
| 다차원 배열         | 2D, 3D 등 행렬 표현에 사용                                      |

## 메모리 구조

```
┌─────┬─────┬─────┬─────┬─────┐
│ [0] │ [1] │ [2] │ [3] │ [4] │
│  10 │  20 │  30 │  40 │  50 │
└─────┴─────┴─────┴─────┴─────┘
  0x00  0x04  0x08  0x0C  0x10   (int 4byte 기준)
```

인덱스 접근 공식: `주소 = 시작주소 + (인덱스 × 요소크기)`

## 2차원 배열

```
행 우선 (Row-major, C/Python):     열 우선 (Column-major, Fortran):
┌───┬───┬───┐                      ┌───┬───┬───┐
│ 1 │ 2 │ 3 │  → 메모리: 1 2 3    | 1 │ 2 │ 3 │  → 메모리: 1 4 2 5 3 6
├───┼───┼───┤             4 5 6    ├───┼───┼───┐
│ 4 │ 5 │ 6 │                      │ 4 │ 5 │ 6 │
└───┴───┴───┘                      └───┴───┴───┘
```

2D 인덱스 접근 (행 우선): `주소 = 시작 + (행 × 열수 + 열) × 요소크기`

## 시간 복잡도

| 연산            | 시간 복잡도 | 비고                |
|-----------------|-------------|---------------------|
| 인덱스 접근     | O(1)        | 랜덤 액세스 가능    |
| 탐색 (선형)     | O(n)        | 정렬 안 된 경우     |
| 탐색 (이진)     | O(log n)    | 정렬된 경우         |
| 맨 뒤 삽입      | O(1)        | 동적 배열 amortized |
| 맨 뒤 삭제      | O(1)        |                     |
| 맨 앞 삽입/삭제 | O(n)        | 전체 요소 이동 필요 |
| 중간 삽입/삭제  | O(n)        | 요소 이동 필요      |

## 공간 복잡도

| 항목      | 복잡도 | 비고                                  |
|-----------|--------|---------------------------------------|
| 정적 배열 | O(n)   | 선언 크기만큼 고정 할당               |
| 동적 배열 | O(n)   | 실제 사용량 대비 최대 2배 메모리 사용 |

## 동적 배열 확장 원리

```
용량 4 → 가득 참 → 새 배열(용량 8) 할당 → 복사 → 기존 해제

┌───┬───┬───┬───┐
│ 1 │ 2 │ 3 │ 4 │  ← 가득 참
└───┴───┴───┴───┘

┌───┬───┬───┬───┬───┬───┬───┬───┐
│ 1 │ 2 │ 3 │ 4 │ 5 │   │   │   │  ← 2배 확장
└───┴───┴───┴───┴───┴───┴───┴───┘
```

- 확장 시 복사 비용: O(n)
- 하지만 n번 삽입 중 확장은 log n번 → amortized O(1)

## 구현 (Python)

```python
arr = []
arr.append(10)      # O(1) amortized
arr.insert(0, 5)    # O(n) - 맨 앞 삽입
arr.pop()           # O(1) - 맨 뒤 삭제
arr.pop(0)          # O(n) - 맨 앞 삭제

# 슬라이싱
arr = [1, 2, 3, 4, 5]
arr[1:3]            # [2, 3] - O(k), k=슬라이스 크기
arr[::-1]           # [5, 4, 3, 2, 1] - 역순, O(n)

# 리스트 컴프리헨션
squares = [x**2 for x in range(5)]  # [0, 1, 4, 9, 16]

# 2D 배열
matrix = [[0] * 3 for _ in range(3)]  # 3x3 영행렬
```

## 장단점

| 장점                      | 단점                        |
|---------------------------|-----------------------------|
| O(1) 랜덤 액세스          | 중간 삽입/삭제 O(n)         |
| 캐시 친화적 (연속 메모리) | 정적 배열은 크기 변경 불가  |
| 구현 단순                 | 동적 배열 확장 시 복사 비용 |

## 자주 나오는 문제 패턴

| 문제                 | 핵심 접근법                |
|----------------------|----------------------------|
| 두 수의 합 (Two Sum) | 해시맵으로 보수 탐색, O(n) |
| 중복 제거            | set 변환 또는 정렬 후 순회 |
| 배열 회전            | 역순 3회 (전체 → 앞 → 뒤)  |
| 최대 부분 배열 합    | Kadane's Algorithm, O(n)   |
| 병합 정렬된 배열     | 투 포인터                  |

### 배열 회전 예시

```python
def rotate(nums, k):
    k %= len(nums)
    nums.reverse()
    nums[:k] = reversed(nums[:k])
    nums[k:] = reversed(nums[k:])
```

## 활용

- 정렬 알고리즘의 기본 자료구조
- 행렬 연산
- 동적 프로그래밍 테이블
- 스택, 큐의 내부 구현
- 이미지 처리 (픽셀 배열)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-05

© 2026 siasia86. Licensed under CC BY 4.0.

# Python print() 함수 가이드

## 목차
- [기본 사용법](#기본-사용법)
- [주요 매개변수](#주요-매개변수)
- [실전 예제](#실전-예제)
- [print vs logging](#print-vs-logging)
- [언제 무엇을 사용할까?](#언제-무엇을-사용할까)

---

## 기본 사용법

```python
print("Hello, World!")
print("a", "b", "c")  # a b c
```

## 주요 매개변수

### 1. sep - 구분자 (기본값: 공백)

```python
print("a", "b", "c")           # a b c
print("a", "b", "c", sep=",")  # a,b,c
print("a", "b", "c", sep="")   # abc
print("a", "b", "c", sep=" | ")  # a | b | c
```

### 2. end - 끝 문자 (기본값: \n)

```python
print("a")              # a\n (줄바꿈)
print("a", end="")      # a (줄바꿈 없음)
print("a", end=" ")     # a (공백으로 끝)

# 진행바 예제
for i in range(5):
    print(i, end=" ")  # 0 1 2 3 4
```

### 3. file - 출력 대상 (기본값: sys.stdout)

```python
# 파일에 출력
with open("log.txt", "w") as f:
    print("로그 메시지", file=f)

# 에러 출력
import sys
print("에러 메시지", file=sys.stderr)
```

### 4. flush - 버퍼 비우기 (기본값: False)

```python
# 즉시 출력
print("진행 중...", flush=True)

# 실시간 진행률 표시
for i in range(100):
    print(f"\r진행: {i}%", end="", flush=True)
```

## 실전 예제

### CSV 형식 출력
```python
print("이름", "나이", "직업", sep=",")
print("홍길동", "30", "개발자", sep=",")
```

### 진행 상황 표시
```python
import time

for i in range(10):
    print(f"\r처리 중: {i+1}/10", end="", flush=True)
    time.sleep(0.5)
print("\n완료!")
```

### 로그 파일 작성
```python
with open("app.log", "a") as f:
    print("2026-03-03", "작업 시작", sep=" | ", file=f)
    print("2026-03-03", "작업 완료", sep=" | ", file=f)
```

## print vs logging

### print 사용 (간단한 경우)
```python
print("디버그 정보")
with open("log.txt", "a") as f:
    print("로그", file=f)
```

### logging 사용 (실무 권장)
```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("작업 시작")
logging.error("에러 발생")
```

## 언제 무엇을 사용할까?

- **print** - 간단한 스크립트, 디버깅, 테스트
- **logging** - 프로덕션 코드, 실무 프로젝트, 복잡한 로그 관리

# Python 예외 처리 (Exception Handling)

Python 예외 처리의 기초부터 고급 활용까지 다루는 완벽 가이드입니다.

## 목차
- [예외란?](#예외란)
- [try/except 기본](#tryexcept-기본)
- [여러 예외 처리](#여러-예외-처리)
- [else와 finally](#else와-finally)
- [예외 발생시키기 (raise)](#예외-발생시키기-raise)
- [사용자 정의 예외](#사용자-정의-예외)
- [예외 체이닝](#예외-체이닝)
- [컨텍스트 매니저](#컨텍스트-매니저)
- [실전 예제](#실전-예제)
- [실전 팁](#실전-팁)
- [자주하는 실수](#자주하는-실수)
- [요약](#요약)

---

## 예외란?

프로그램 실행 중 발생하는 오류를 처리하는 메커니즘입니다.

### 왜 사용하나?

- **안정성**: 프로그램 비정상 종료 방지
- **디버깅**: 오류 원인 파악 용이
- **사용자 경험**: 친절한 오류 메시지 제공
- **복구**: 오류 상황에서 대안 실행

### 주요 내장 예외

```python
# ZeroDivisionError: 0으로 나누기
10 / 0

# ValueError: 잘못된 값
int("abc")

# TypeError: 잘못된 타입
"2" + 2

# KeyError: 존재하지 않는 키
{"a": 1}["b"]

# IndexError: 범위 초과
[1, 2, 3][10]

# FileNotFoundError: 파일 없음
open("없는파일.txt")

# AttributeError: 속성 없음
"hello".non_existent_method()
```

---

## try/except 기본

### 기본 구조

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("0으로 나눌 수 없습니다")
# 0으로 나눌 수 없습니다
```

### 예외 객체 접근

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"오류 발생: {e}")
# 오류 발생: division by zero
```

### 모든 예외 처리

```python
try:
    result = int("abc")
except Exception as e:
    print(f"예외 발생: {type(e).__name__}: {e}")
# 예외 발생: ValueError: invalid literal for int() with base 10: 'abc'
```

---

## 여러 예외 처리

### 개별 처리

```python
try:
    value = int(input("숫자 입력: "))
    result = 10 / value
except ValueError:
    print("숫자를 입력하세요")
except ZeroDivisionError:
    print("0이 아닌 숫자를 입력하세요")
```

### 동일하게 처리

```python
try:
    # 작업 수행
    pass
except (ValueError, TypeError) as e:
    print(f"입력 오류: {e}")
```

### 계층적 처리

```python
try:
    # 작업 수행
    pass
except ValueError:
    print("값 오류")
except Exception:
    print("기타 오류")
```

---

## else와 finally

### else: 예외 없을 때 실행

```python
try:
    result = 10 / 2
except ZeroDivisionError:
    print("0으로 나눌 수 없습니다")
else:
    print(f"결과: {result}")
# 결과: 5.0
```

### finally: 항상 실행

```python
try:
    file = open("data.txt", "r")
    content = file.read()
except FileNotFoundError:
    print("파일을 찾을 수 없습니다")
finally:
    file.close()  # 항상 실행
```

### 전체 구조

```python
try:
    result = 10 / 2
except ZeroDivisionError:
    print("오류 발생")
else:
    print(f"성공: {result}")
finally:
    print("정리 작업")
# 성공: 5.0
# 정리 작업
```

---

## 예외 발생시키기 (raise)

### 기본 사용

```python
def divide(a, b):
    if b == 0:
        raise ValueError("b는 0이 될 수 없습니다")
    return a / b

try:
    divide(10, 0)
except ValueError as e:
    print(e)
# b는 0이 될 수 없습니다
```

### 예외 재발생

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("로그 기록")
    raise  # 예외 다시 발생
```

### 다른 예외로 변환

```python
try:
    value = int("abc")
except ValueError:
    raise TypeError("타입 변환 실패")
```

---

## 사용자 정의 예외

### 기본 정의

```python
class CustomError(Exception):
    pass

def check_positive(value):
    if value < 0:
        raise CustomError("양수만 허용됩니다")
    return value

try:
    check_positive(-5)
except CustomError as e:
    print(e)
# 양수만 허용됩니다
```

### 메시지와 코드 포함

```python
class ValidationError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code

def validate_age(age):
    if age < 0:
        raise ValidationError("나이는 음수일 수 없습니다", "NEGATIVE_AGE")
    if age > 150:
        raise ValidationError("나이가 너무 큽니다", "AGE_TOO_HIGH")

try:
    validate_age(-5)
except ValidationError as e:
    print(f"오류 [{e.code}]: {e}")
# 오류 [NEGATIVE_AGE]: 나이는 음수일 수 없습니다
```

### 예외 계층 구조

```python
class DatabaseError(Exception):
    """데이터베이스 관련 예외"""
    pass

class ConnectionError(DatabaseError):
    """연결 오류"""
    pass

class QueryError(DatabaseError):
    """쿼리 오류"""
    pass

try:
    raise QueryError("잘못된 SQL 쿼리")
except DatabaseError as e:
    print(f"DB 오류: {e}")
# DB 오류: 잘못된 SQL 쿼리
```

---

## 예외 체이닝

### from으로 원인 명시

```python
def process_data(data):
    try:
        return int(data)
    except ValueError as e:
        raise TypeError("데이터 처리 실패") from e

try:
    process_data("abc")
except TypeError as e:
    print(f"오류: {e}")
    print(f"원인: {e.__cause__}")
# 오류: 데이터 처리 실패
# 원인: invalid literal for int() with base 10: 'abc'
```

### 자동 체이닝

```python
try:
    try:
        result = 10 / 0
    except ZeroDivisionError:
        raise ValueError("계산 오류")
except ValueError as e:
    print(f"오류: {e}")
    print(f"컨텍스트: {e.__context__}")
```

---

## 컨텍스트 매니저

### with 문 사용

```python
# 자동으로 파일 닫기
with open("data.txt", "r") as file:
    content = file.read()
# 예외 발생해도 파일 자동 닫힘
```

### 사용자 정의 컨텍스트 매니저

```python
class DatabaseConnection:
    def __enter__(self):
        print("데이터베이스 연결")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("데이터베이스 연결 종료")
        if exc_type:
            print(f"예외 발생: {exc_val}")
        return False  # 예외 전파

with DatabaseConnection() as db:
    print("작업 수행")
# 데이터베이스 연결
# 작업 수행
# 데이터베이스 연결 종료
```

### contextlib 사용

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    print("리소스 획득")
    try:
        yield "리소스"
    finally:
        print("리소스 해제")

with managed_resource() as resource:
    print(f"사용: {resource}")
# 리소스 획득
# 사용: 리소스
# 리소스 해제
```

---

## 실전 예제

### 예제 1: 파일 읽기 안전하게

```python
def read_file_safe(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {filename}")
        return None
    except PermissionError:
        print(f"파일 접근 권한이 없습니다: {filename}")
        return None
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        return None

content = read_file_safe("data.txt")
if content:
    print(content)
```

### 예제 2: API 호출 재시도

```python
import time

def api_call_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            # API 호출 시뮬레이션
            response = fetch_data(url)
            return response
        except ConnectionError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"재시도 {attempt + 1}/{max_retries} ({wait_time}초 후)")
                time.sleep(wait_time)
            else:
                raise Exception(f"최대 재시도 횟수 초과: {e}")
```

### 예제 3: 입력 검증

```python
class InputValidator:
    @staticmethod
    def validate_email(email):
        if "@" not in email:
            raise ValueError("유효하지 않은 이메일 형식")
        return email
    
    @staticmethod
    def validate_age(age):
        try:
            age = int(age)
        except ValueError:
            raise ValueError("나이는 숫자여야 합니다")
        
        if age < 0 or age > 150:
            raise ValueError("나이는 0-150 사이여야 합니다")
        return age

try:
    email = InputValidator.validate_email("user@example.com")
    age = InputValidator.validate_age("25")
    print(f"검증 성공: {email}, {age}")
except ValueError as e:
    print(f"검증 실패: {e}")
```

### 예제 4: 트랜잭션 관리

```python
class Transaction:
    def __init__(self):
        self.operations = []
    
    def add_operation(self, operation):
        self.operations.append(operation)
    
    def execute(self):
        completed = []
        try:
            for op in self.operations:
                op.execute()
                completed.append(op)
        except Exception as e:
            print(f"트랜잭션 실패: {e}")
            # 롤백
            for op in reversed(completed):
                try:
                    op.rollback()
                except Exception as rollback_error:
                    print(f"롤백 실패: {rollback_error}")
            raise

class Operation:
    def __init__(self, name):
        self.name = name
    
    def execute(self):
        print(f"{self.name} 실행")
    
    def rollback(self):
        print(f"{self.name} 롤백")

# 사용
transaction = Transaction()
transaction.add_operation(Operation("작업1"))
transaction.add_operation(Operation("작업2"))
transaction.execute()
```

### 예제 5: 로깅과 예외 처리

```python
import logging

logging.basicConfig(level=logging.ERROR)

def safe_divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        logging.error(f"0으로 나누기 시도: {a} / {b}")
        return None
    except TypeError as e:
        logging.error(f"타입 오류: {e}")
        return None
    else:
        logging.info(f"계산 성공: {a} / {b} = {result}")
        return result
    finally:
        logging.debug("safe_divide 함수 종료")

result = safe_divide(10, 0)
```

---

## 실전 팁

### Tip 1: 구체적인 예외 먼저 처리

```python
# 좋은 예
try:
    value = int("abc")
except ValueError:
    print("값 오류")
except Exception:
    print("기타 오류")

# 나쁜 예
try:
    value = int("abc")
except Exception:  # 모든 예외 잡음
    print("오류")
except ValueError:  # 도달 불가
    print("값 오류")
```

### Tip 2: 빈 except 피하기

```python
# 나쁜 예
try:
    risky_operation()
except:  # 모든 예외 무시
    pass

# 좋은 예
try:
    risky_operation()
except SpecificError as e:
    logging.error(f"오류: {e}")
```

### Tip 3: 예외를 제어 흐름으로 사용하지 않기

```python
# 나쁜 예
try:
    return my_dict[key]
except KeyError:
    return default_value

# 좋은 예
return my_dict.get(key, default_value)
```

### Tip 4: 예외 메시지는 명확하게

```python
# 나쁜 예
raise ValueError("오류")

# 좋은 예
raise ValueError(f"나이는 0-150 사이여야 합니다. 입력값: {age}")
```

### Tip 5: assert는 디버깅용

```python
# 개발 중 검증
def calculate_discount(price, discount):
    assert 0 <= discount <= 1, "할인율은 0-1 사이여야 합니다"
    return price * (1 - discount)

# 프로덕션에서는 예외 사용
def calculate_discount(price, discount):
    if not 0 <= discount <= 1:
        raise ValueError("할인율은 0-1 사이여야 합니다")
    return price * (1 - discount)
```

### Tip 6: 예외 계층 활용

```python
class AppError(Exception):
    """애플리케이션 기본 예외"""
    pass

class ValidationError(AppError):
    """검증 오류"""
    pass

class DatabaseError(AppError):
    """데이터베이스 오류"""
    pass

# 모든 앱 예외 한 번에 처리
try:
    process_data()
except AppError as e:
    logging.error(f"앱 오류: {e}")
```

### Tip 7: 예외 무시할 때는 명시적으로

```python
from contextlib import suppress

# 명시적으로 무시
with suppress(FileNotFoundError):
    os.remove("temp.txt")

# 또는
try:
    os.remove("temp.txt")
except FileNotFoundError:
    pass  # 파일 없어도 괜찮음
```

### Tip 8: 예외 정보 보존

```python
import traceback

try:
    risky_operation()
except Exception as e:
    # 전체 스택 트레이스 로깅
    logging.error(f"오류 발생:\n{traceback.format_exc()}")
```

---

## 자주하는 실수

### 실수 1: 너무 광범위한 예외 처리

```python
# 나쁜 예
try:
    process_data()
except Exception:  # 모든 예외 잡음
    pass

# 좋은 예
try:
    process_data()
except (ValueError, TypeError) as e:
    logging.error(f"데이터 처리 오류: {e}")
```

### 실수 2: 예외 정보 손실

```python
# 나쁜 예
try:
    result = int("abc")
except ValueError:
    raise TypeError("변환 실패")  # 원인 손실

# 좋은 예
try:
    result = int("abc")
except ValueError as e:
    raise TypeError("변환 실패") from e
```

### 실수 3: finally에서 return

```python
# 나쁜 예
def bad_function():
    try:
        return "try"
    finally:
        return "finally"  # 항상 이 값 반환

print(bad_function())  # "finally"

# 좋은 예
def good_function():
    try:
        return "try"
    finally:
        cleanup()  # 정리 작업만
```

### 실수 4: 예외를 문자열로 발생

```python
# 나쁜 예
raise "오류 발생"  # TypeError!

# 좋은 예
raise ValueError("오류 발생")
```

### 실수 5: 리소스 누수

```python
# 나쁜 예
file = open("data.txt")
try:
    content = file.read()
except Exception:
    pass
# 예외 발생 시 파일 안 닫힘

# 좋은 예
with open("data.txt") as file:
    content = file.read()
# 자동으로 닫힘
```

### 실수 6: 예외 메시지에 민감 정보

```python
# 나쁜 예
raise ValueError(f"로그인 실패: 비밀번호 {password}")

# 좋은 예
raise ValueError("로그인 실패: 잘못된 인증 정보")
```

---

## 요약

| 개념        | 설명            | 예시                          |
|-------------|-----------------|-------------------------------|
| try/except  | 예외 처리       | `try: ... except ValueError:` |
| else        | 예외 없을 때    | `else: print("성공")`         |
| finally     | 항상 실행       | `finally: cleanup()`          |
| raise       | 예외 발생       | `raise ValueError("오류")`    |
| 사용자 정의 | 커스텀 예외     | `class MyError(Exception):`   |
| with        | 컨텍스트 매니저 | `with open(...) as f:`        |
| from        | 예외 체이닝     | `raise ... from e`            |

**핵심 포인트:**
- 구체적인 예외부터 처리
- 빈 except 사용 금지
- 예외를 제어 흐름으로 사용하지 않기
- 명확한 예외 메시지 작성
- 리소스는 with 문으로 관리
- 예외 정보 보존 (from 사용)

**관련 문서:**
- [함수 튜토리얼](./python_functions.md) - 함수에서 예외 처리
- [클래스 튜토리얼](./python_class.md) - 사용자 정의 예외 클래스
- [로깅 튜토리얼](./python_logging.md) - 예외 로깅

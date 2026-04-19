# Python 모듈 속성 (Module Attributes)

Python 모듈과 패키지에서 사용되는 특수 속성들에 대한 가이드입니다.

> **참고**: 클래스의 매직 메서드(`__init__`, `__str__` 등)는 [python_class_components.md](./python_class_components.md)를 참고하세요.

---

## 목차
- [Dunder란?](#dunder란)
- [모듈 관련 속성](#모듈-관련-속성)
- [패키지 관련 속성](#패키지-관련-속성)
- [클래스/인스턴스 속성](#클래스인스턴스-속성)
- [함수 관련 속성](#함수-관련-속성)
- [실용 예제](#실용-예제)
- [__pycache__ 디렉토리](#__pycache__-디렉토리)
- [요약](#요약)
- [관련 문서](#관련-문서)

---

## Dunder란?

`__name__`처럼 앞뒤로 더블 언더스코어(`__`)가 붙은 것들을 **dunder**(double underscore)라고 부릅니다.
- **매직(magic)** 또는 **특수(special)** 속성이라고도 함
- Python이 내부적으로 사용하는 특별한 이름

---

## 모듈 관련 속성

### `__name__`

모듈의 이름을 나타냅니다. 파일을 직접 실행하면 `"__main__"`이 됩니다.

```python
# my_module.py
print(f"모듈 이름: {__name__}")

if __name__ == "__main__":
    print("직접 실행됨")
else:
    print("import됨")
```

**직접 실행 시:**
```bash
$ python my_module.py
모듈 이름: __main__
직접 실행됨
```

**import 시:**
```python
import my_module
# 모듈 이름: my_module
# import됨
```

### `__file__`

현재 파일의 경로를 나타냅니다.

```python
# /home/user/project/app.py
print(__file__)  # /home/user/project/app.py

# 절대 경로 얻기
import os
print(os.path.abspath(__file__))

# 디렉토리 경로 얻기
print(os.path.dirname(__file__))  # /home/user/project
```

**실용 예제:**
```python
import os

# 현재 파일과 같은 디렉토리의 config.json 읽기
current_dir = os.path.dirname(__file__)
config_path = os.path.join(current_dir, "config.json")

with open(config_path) as f:
    config = f.read()
```

### `__doc__`

모듈, 함수, 클래스의 docstring을 나타냅니다.

```python
"""이것은 모듈의 docstring입니다."""

def greet(name):
    """인사말을 반환합니다.
    
    Args:
        name (str): 이름
    
    Returns:
        str: 인사말
    """
    return f"Hello, {name}!"

print(__doc__)        # 이것은 모듈의 docstring입니다.
print(greet.__doc__)  # 인사말을 반환합니다...
```

### `__package__`

모듈이 속한 패키지의 이름을 나타냅니다.

```python
# mypackage/subpackage/module.py
print(__package__)  # mypackage.subpackage

# 최상위 모듈
print(__package__)  # '' (빈 문자열)
```

### `__cached__`

컴파일된 `.pyc` 파일의 경로를 나타냅니다.

```python
print(__cached__)
# __pycache__/my_module.cpython-311.pyc
```

---

## 패키지 관련 속성

### `__path__`

패키지의 경로 리스트입니다. (패키지에만 존재)

```python
# mypackage/__init__.py
print(__path__)  # ['/home/user/project/mypackage']
```

### `__all__`

`from module import *` 시 import될 이름들을 정의합니다.

```python
# mymodule.py
__all__ = ['public_func', 'PublicClass']

def public_func():
    pass

def _private_func():
    pass

class PublicClass:
    pass
```

```python
from mymodule import *
# public_func와 PublicClass만 import됨
# _private_func는 import 안 됨
```

---

## 클래스/인스턴스 속성

### `__class__`

인스턴스가 속한 클래스를 나타냅니다.

```python
class Dog:
    pass

dog = Dog()
print(dog.__class__)        # <class '__main__.Dog'>
print(dog.__class__.__name__)  # Dog
```

### `__dict__`

객체의 속성을 딕셔너리로 나타냅니다.

```python
class Person:
    species = "Human"
    
    def __init__(self, name, age):
        self.name = name
        self.age = age

person = Person("홍길동", 30)

# 인스턴스 속성
print(person.__dict__)  # {'name': '홍길동', 'age': 30}

# 클래스 속성
print(Person.__dict__)  # {..., 'species': 'Human', ...}
```

### `__bases__`

클래스의 부모 클래스들을 튜플로 나타냅니다.

```python
class Animal:
    pass

class Flyable:
    pass

class Bird(Animal, Flyable):
    pass

print(Bird.__bases__)  # (<class 'Animal'>, <class 'Flyable'>)
```

### `__mro__`

메서드 해석 순서(Method Resolution Order)를 나타냅니다.

```python
class A:
    pass

class B(A):
    pass

class C(A):
    pass

class D(B, C):
    pass

print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
```

---

## 함수 관련 속성

### `__name__`

함수의 이름을 나타냅니다.

```python
def my_function():
    pass

print(my_function.__name__)  # my_function
```

### `__code__`

함수의 코드 객체를 나타냅니다.

```python
def add(a, b):
    return a + b

print(add.__code__.co_argcount)  # 2 (인자 개수)
print(add.__code__.co_varnames)  # ('a', 'b')
```

### `__defaults__`

함수의 기본 인자 값들을 튜플로 나타냅니다.

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet.__defaults__)  # ('Hello',)
```

---

## 실용 예제

### 예제 1: 스크립트 vs 모듈 구분

```python
# utils.py
def process_data(data):
    return data.upper()

# 테스트 코드 (직접 실행 시에만 동작)
if __name__ == "__main__":
    test_data = "hello"
    result = process_data(test_data)
    print(f"테스트 결과: {result}")
```

### 예제 2: 프로젝트 루트 경로 찾기

```python
# project/src/utils/helper.py
import os

# 현재 파일의 절대 경로
current_file = os.path.abspath(__file__)
# /home/user/project/src/utils/helper.py

# 프로젝트 루트 (3단계 위)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
# /home/user/project

print(f"프로젝트 루트: {project_root}")
```

### 예제 3: 동적 클래스 정보 확인

```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "멍멍"

dog = Dog()

# 클래스 이름
print(dog.__class__.__name__)  # Dog

# 부모 클래스 확인
print(isinstance(dog, Animal))  # True

# 속성 목록
print(dog.__dict__)  # {}

# 메서드 해석 순서
print(Dog.__mro__)
# (<class 'Dog'>, <class 'Animal'>, <class 'object'>)
```

### 예제 4: 패키지 공개 API 정의

```python
# mypackage/__init__.py
"""유틸리티 패키지"""

from .core import process
from .helpers import format_data

# 공개 API 정의
__all__ = ['process', 'format_data']

# 버전 정보
__version__ = '1.0.0'
```

```python
# 사용
import mypackage

print(mypackage.__version__)  # 1.0.0
print(mypackage.__doc__)      # 유틸리티 패키지

from mypackage import *
# process와 format_data만 import됨
```

---

## __pycache__ 디렉토리

Python이 모듈을 import할 때 자동 생성하는 바이트코드 캐시 디렉토리입니다.

### 생성 원리

```
mypackage/
    __init__.py
    module1.py
    __pycache__/              ← Python이 자동 생성
        __init__.cpython-311.pyc
        module1.cpython-311.pyc
```

```python
# module1.py를 import하면
import mypackage.module1

# Python이 자동으로 수행하는 과정:
# 1. module1.py 소스 코드 읽기
# 2. 바이트코드(.pyc)로 컴파일
# 3. __pycache__/module1.cpython-311.pyc 에 저장
# 4. 다음 import 시 .pyc 캐시 사용 (소스 변경 없으면)
```

### 파일명 규칙

```
<모듈명>.cpython-<버전>.pyc

module1.cpython-311.pyc    # Python 3.11
module1.cpython-312.pyc    # Python 3.12
```

여러 Python 버전이 공존할 수 있도록 버전 번호가 포함됩니다.

### 동작 방식

```python
# 첫 import: 소스 → 컴파일 → .pyc 생성 → 실행
import module1  # 느림 (컴파일 필요)

# 두 번째 import: .pyc 캐시 사용 → 실행
import module1  # 빠름 (캐시 사용)

# 소스 수정 후 import: 재컴파일 → .pyc 갱신 → 실행
import module1  # 자동 감지하여 재컴파일
```

### .gitignore 설정

```gitignore
# 반드시 추가 (버전 관리 불필요)
__pycache__/
*.pyc
```

### 삭제 방법

```bash
# 현재 디렉토리 하위 전체 삭제
find . -type d -name __pycache__ -exec rm -rf {} +

# 특정 디렉토리만
rm -rf mypackage/__pycache__

# Python 옵션으로 .pyc 생성 자체를 방지
python -B script.py
PYTHONDONTWRITEBYTECODE=1 python script.py
```

### 환경 변수

```bash
# .pyc 생성 방지
export PYTHONDONTWRITEBYTECODE=1

# .pyc 저장 경로 변경 (Python 3.8+)
export PYTHONPYCACHEPREFIX=/tmp/pycache
```

---

## 요약

### 모듈 속성

| 속성 | 설명 | 주요 용도 |
|------|------|----------|
| `__name__` | 모듈 이름 | 스크립트 vs 모듈 구분 |
| `__file__` | 파일 경로 | 상대 경로 계산 |
| `__doc__` | docstring | 문서화 |
| `__package__` | 패키지 이름 | 패키지 구조 파악 |
| `__all__` | 공개 API | import * 제어 |

### 클래스 속성

| 속성 | 설명 | 주요 용도 |
|------|------|----------|
| `__class__` | 클래스 참조 | 타입 확인 |
| `__dict__` | 속성 딕셔너리 | 동적 속성 접근 |
| `__bases__` | 부모 클래스 | 상속 구조 파악 |
| `__mro__` | 메서드 해석 순서 | 다중 상속 디버깅 |

---

## 관련 문서

- [클래스 구성 요소](./python_class_components.md) - 클래스 매직 메서드 상세 가이드
- [클래스 튜토리얼](./python_class.md) - 클래스 기초부터 실전까지

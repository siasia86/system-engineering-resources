# Python 타입 힌트 (Type Hints)
<!-- reference: https://docs.python.org/3/library/typing.html -->

Python 3.5+에서 도입된 타입 힌트(PEP 484)와 typing 모듈 사용법을 정리합니다.

## 목차

| 섹션                                                                                                                             |
|----------------------------------------------------------------------------------------------------------------------------------|
| [1. 기초 타입 힌트](#1-기초-타입-힌트) / [2. 컬렉션 타입](#2-컬렉션-타입) / [3. 특수 타입](#3-특수-타입)                         |
| [4. dataclass](#4-dataclass) / [5. TypedDict / NamedTuple](#5-typeddict--namedtuple) / [6. 제네릭 / TypeVar](#6-제네릭--typevar) |
| [7. Protocol](#7-protocol) / [8. 런타임 vs 정적 검사](#8-런타임-vs-정적-검사)                                                    |

---

## 1. 기초 타입 힌트

### 변수 / 함수 어노테이션

```python
# 변수 어노테이션
name: str = "홍길동"
age: int = 30
pi: float = 3.14
active: bool = True

# 함수 파라미터 + 반환 타입
def greet(name: str, age: int) -> str:
    return f"{name}은(는) {age}살입니다."

# 반환값 없음
def log(msg: str) -> None:
    print(msg)

# 반환값이 없을 수도 있음 (명시적 return 없는 분기 포함)
def find(items: list, target: int) -> int | None:  # Python 3.10+
    for i, item in enumerate(items):
        if item == target:
            return i
    return None
```

### Python 버전별 문법 변화

```python
# Python 3.9 이전 — typing 모듈 필요
from typing import List, Dict, Tuple, Optional, Union

def process(items: List[int]) -> Dict[str, int]:
    ...

def find(items: List[int], target: int) -> Optional[int]:  # Optional[X] = Union[X, None]
    ...

# Python 3.9+ — 내장 타입 직접 사용
def process(items: list[int]) -> dict[str, int]:
    ...

# Python 3.10+ — | 로 Union 표현
def find(items: list[int], target: int) -> int | None:
    ...
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 컬렉션 타입

```python
from typing import Sequence, Mapping, Iterable, Iterator, Callable

# 불변 시퀀스 (list, tuple 모두 허용)
def first(items: Sequence[int]) -> int:
    return items[0]

# 이터러블 (for 루프에 사용 가능한 모든 타입)
def total(nums: Iterable[float]) -> float:
    return sum(nums)

# 매핑 (dict, defaultdict 등)
def get_value(m: Mapping[str, int], key: str) -> int | None:
    return m.get(key)

# 콜러블: Callable[[파라미터], 반환]
def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

apply(lambda x, y: x + y, 3, 5)  # 8

# 튜플 — 고정 길이
def coords() -> tuple[float, float]:
    return 1.0, 2.0

# 가변 길이 튜플
def varargs() -> tuple[int, ...]:
    return (1, 2, 3)
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 특수 타입

### Optional / Union / Literal

```python
from typing import Optional, Union, Literal

# Optional[X] = X | None
def find_user(user_id: int) -> Optional[str]:
    ...

# Union — 여러 타입 허용
def process(value: Union[int, str]) -> str:
    return str(value)

# Python 3.10+
def process(value: int | str) -> str:
    return str(value)

# Literal — 특정 값만 허용
def set_direction(direction: Literal["left", "right", "up", "down"]) -> None:
    ...

set_direction("left")    # OK
# set_direction("back") # 타입 오류
```

### Any / Final / ClassVar

```python
from typing import Any, Final, ClassVar

# Any — 타입 검사 비활성화 (최후 수단)
def process(data: Any) -> Any:
    return data

# Final — 재할당 금지 상수
MAX_RETRIES: Final = 3
# MAX_RETRIES = 5  # 타입 체커가 오류 보고

# ClassVar — 클래스 변수임을 명시
class Config:
    DEBUG: ClassVar[bool] = False
    host: str  # 인스턴스 변수
```

### TYPE_CHECKING — 순환 import 방지

```python
from __future__ import annotations  # 지연 평가 (Python 3.10+에서 기본화 예정)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mymodule import MyClass  # 런타임에는 import 안 됨, 타입 검사 시에만

def process(obj: "MyClass") -> None:  # 문자열 어노테이션
    ...
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. dataclass

`dataclass`는 `__init__`, `__repr__`, `__eq__` 등을 자동 생성하는 클래스 데코레이터입니다.

```python
from dataclasses import dataclass, field

@dataclass
class Server:
    name: str
    ip: str
    port: int = 80               # 기본값
    tags: list[str] = field(default_factory=list)  # 가변 기본값은 field() 사용

s = Server(name="web-01", ip="192.0.2.1")
print(s)          # Server(name='web-01', ip='192.0.2.1', port=80, tags=[])
print(s.name)     # 'web-01'

s2 = Server(name="web-01", ip="192.0.2.1")
print(s == s2)    # True (__eq__ 자동 생성)
```

### frozen=True — 불변 dataclass

```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
# p.x = 3.0  # FrozenInstanceError

# frozen dataclass는 dict 키, set 원소로 사용 가능 (__hash__ 자동 생성)
points = {Point(0.0, 0.0), Point(1.0, 2.0)}
```

### order=True — 비교 연산자 자동 생성

```python
@dataclass(order=True)
class Version:
    major: int
    minor: int
    patch: int

v1 = Version(1, 2, 3)
v2 = Version(1, 3, 0)
print(v1 < v2)   # True
versions = [Version(2,0,0), Version(1,3,0)]
print(sorted(versions))  # [Version(major=1,...), Version(major=2,...)]
```

### field() 옵션

```python
from dataclasses import dataclass, field

@dataclass
class Task:
    name: str
    priority: int = field(default=1, compare=True)
    # repr=False — __repr__에서 제외
    _internal: str = field(default="", repr=False, compare=False)
    # init=False — 생성자 파라미터에서 제외
    created_at: str = field(default="", init=False)

    def __post_init__(self):
        # 생성자 후처리
        import datetime
        self.created_at = datetime.datetime.now().isoformat()
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. TypedDict / NamedTuple

### TypedDict — 딕셔너리 구조 타입 명세

```python
from typing import TypedDict

class UserInfo(TypedDict):
    name: str
    age: int
    email: str

# 일부 키를 선택적으로
class PartialUser(TypedDict, total=False):
    nickname: str
    bio: str

def create_user(info: UserInfo) -> None:
    print(f"{info['name']}, {info['age']}세")

user: UserInfo = {"name": "홍길동", "age": 30, "email": "user@example.com"}
create_user(user)
```

### NamedTuple — 타입이 있는 namedtuple

```python
from typing import NamedTuple

class Server(NamedTuple):
    name: str
    ip: str
    port: int = 80

s = Server("web-01", "192.0.2.1")
print(s.name)   # 'web-01'
print(s[1])     # '192.0.2.1' (인덱스 접근 가능)
print(s._asdict())

# dataclass vs NamedTuple 선택 기준
# - 불변 + 튜플 언패킹 필요 → NamedTuple
# - 변경 가능 + 추가 메서드 필요 → dataclass
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 제네릭 / TypeVar

### TypeVar — 타입 파라미터

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    return items[0]

first([1, 2, 3])        # 반환 타입: int
first(["a", "b", "c"])  # 반환 타입: str
```

### 제약 조건이 있는 TypeVar

```python
from typing import TypeVar

# 특정 타입만 허용
Numeric = TypeVar("Numeric", int, float)

def double(x: Numeric) -> Numeric:
    return x * 2

double(3)    # int → int
double(3.0)  # float → float
# double("3")  # 타입 오류

# bound — 상위 타입 제한
from typing import SupportsFloat

F = TypeVar("F", bound=SupportsFloat)

def to_float(x: F) -> float:
    return float(x)
```

### 제네릭 클래스 (Python 3.12+: type 파라미터 문법)

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def is_empty(self) -> bool:
        return not self._items

stack: Stack[int] = Stack()
stack.push(1)
stack.push(2)
print(stack.pop())  # 2
```

```python
# Python 3.12+ — type 파라미터 문법 (PEP 695)
class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. Protocol

`Protocol`은 구조적 서브타이핑(덕 타이핑)을 타입 시스템에서 표현합니다.
ABC처럼 상속 없이 인터페이스를 정의할 수 있습니다.

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...
    def resize(self, factor: float) -> None: ...

class Circle:
    def draw(self) -> None:
        print("원 그리기")

    def resize(self, factor: float) -> None:
        print(f"크기 조정: {factor}")

class Square:
    def draw(self) -> None:
        print("사각형 그리기")

    def resize(self, factor: float) -> None:
        print(f"크기 조정: {factor}")

# Circle, Square는 Drawable을 상속하지 않았지만 타입 체커는 허용
def render(shape: Drawable) -> None:
    shape.draw()

render(Circle())   # OK
render(Square())   # OK
```

### runtime_checkable Protocol

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Closable(Protocol):
    def close(self) -> None: ...

class FileHandle:
    def close(self) -> None:
        print("파일 닫기")

fh = FileHandle()
print(isinstance(fh, Closable))  # True (runtime_checkable 있어야 작동)
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 런타임 vs 정적 검사

### 타입 힌트는 런타임에 강제되지 않음

```python
def add(a: int, b: int) -> int:
    return a + b

# 런타임에 오류 없음 — Python은 타입 힌트를 무시
result = add("3", "5")   # "35" 반환, 예외 없음
```

### mypy / pyright — 정적 타입 체커

```bash
# mypy 설치 및 실행
pip install mypy
mypy script.py

# pyright (Microsoft, VS Code 기본 사용)
pip install pyright
pyright script.py
```

```ini
# mypy.ini 설정 예시
[mypy]
python_version = 3.12
strict = true          # 엄격 모드 (모든 타입 힌트 강제)
ignore_missing_imports = true
```

### get_type_hints — 런타임에 힌트 확인

```python
import typing

def greet(name: str) -> str:
    return f"안녕, {name}!"

hints = typing.get_type_hints(greet)
print(hints)  # {'name': <class 'str'>, 'return': <class 'str'>}
```

### dataclass + mypy 활용 예시

```python
from dataclasses import dataclass
from typing import ClassVar

@dataclass
class Config:
    host: str
    port: int
    _instances: ClassVar[int] = 0  # 클래스 변수

    def __post_init__(self) -> None:
        Config._instances += 1

    @classmethod
    def instance_count(cls) -> int:
        return cls._instances

c1 = Config("localhost", 8080)
c2 = Config("192.0.2.1", 443)
print(Config.instance_count())  # 2
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- Python typing docs: [docs.python.org/3/library/typing.html](https://docs.python.org/3/library/typing.html) — ★★★☆☆
- mypy docs: [mypy.readthedocs.io](https://mypy.readthedocs.io/) — ★★★☆☆
- PEP 484 Type Hints: [peps.python.org/pep-0484](https://peps.python.org/pep-0484/) — ★★★☆☆
- PEP 695 Type Parameter Syntax: [peps.python.org/pep-0695](https://peps.python.org/pep-0695/) — ★★☆☆☆

---

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)

---

**작성일**: 2026-08-09

**마지막 업데이트**: 2026-08-09

© 2026 siasia86. Licensed under CC BY 4.0.

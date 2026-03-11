# Python 매직 속성/메서드 (Dunder)

`__name__`처럼 앞뒤로 더블 언더스코어(`__`)가 붙은 것들.
- **dunder** = double underscore 줄임말
- **매직(magic)** 또는 **특수(special)** 속성/메서드라고 부름

---

## 모듈/파일 관련 속성

| 속성 | 설명 | 예시 |
|------|------|------|
| `__name__` | 모듈 이름 (직접 실행 시 `"__main__"`) | `if __name__ == "__main__":` |
| `__file__` | 현재 파일 경로 | `/home/user/app.py` |
| `__doc__` | 모듈/함수/클래스의 docstring | `print(함수.__doc__)` |
| `__package__` | 패키지 이름 | `mypackage.subpackage` |
| `__cached__` | 컴파일된 .pyc 파일 경로 | `__pycache__/app.cpython-311.pyc` |

```python
if __name__ == "__main__":
    print("직접 실행됨")
else:
    print("import됨")
```

---

## 클래스 기본 메서드

| 메서드 | 호출 시점 | 용도 |
|--------|----------|------|
| `__init__(self)` | 인스턴스 생성 시 | 초기화 |
| `__new__(cls)` | `__init__` 전에 호출 | 인스턴스 생성 제어 |
| `__del__(self)` | 객체 삭제 시 | 정리 작업 |
| `__repr__(self)` | `repr()` 호출 시 | 개발자용 문자열 |
| `__str__(self)` | `str()`, `print()` 시 | 사용자용 문자열 |

```python
class User:
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"User: {self.name}"
    
    def __repr__(self):
        return f"User('{self.name}')"

u = User("홍길동")
print(u)        # User: 홍길동
print(repr(u))  # User('홍길동')
```

---

## 비교 연산자

| 메서드 | 연산자 |
|--------|--------|
| `__eq__` | `==` |
| `__ne__` | `!=` |
| `__lt__` | `<` |
| `__le__` | `<=` |
| `__gt__` | `>` |
| `__ge__` | `>=` |

```python
class Score:
    def __init__(self, value):
        self.value = value
    
    def __lt__(self, other):
        return self.value < other.value

a, b = Score(80), Score(90)
print(a < b)   # True
```

---

## 산술 연산자

| 메서드 | 연산자 | 역연산 |
|--------|--------|--------|
| `__add__` | `+` | `__radd__` |
| `__sub__` | `-` | `__rsub__` |
| `__mul__` | `*` | `__rmul__` |
| `__truediv__` | `/` | `__rtruediv__` |
| `__floordiv__` | `//` | `__rfloordiv__` |
| `__mod__` | `%` | `__rmod__` |
| `__pow__` | `**` | `__rpow__` |

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

v1, v2 = Vector(1, 2), Vector(3, 4)
print(v1 + v2)  # Vector(4, 6)
```

---

## 컨테이너 관련

| 메서드 | 호출 | 용도 |
|--------|------|------|
| `__len__` | `len(obj)` | 길이 |
| `__getitem__` | `obj[key]` | 인덱싱 |
| `__setitem__` | `obj[key] = v` | 값 설정 |
| `__delitem__` | `del obj[key]` | 삭제 |
| `__contains__` | `x in obj` | 포함 여부 |
| `__iter__` | `for x in obj` | 반복자 |
| `__next__` | `next(obj)` | 다음 값 |

```python
class MyList:
    def __init__(self, data):
        self.data = data
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, i):
        return self.data[i]

lst = MyList([1, 2, 3])
print(len(lst))  # 3
print(lst[0])    # 1
```

---

## 속성 접근

| 메서드 | 호출 시점 |
|--------|----------|
| `__getattr__` | 없는 속성 접근 시 |
| `__setattr__` | 속성 설정 시 |
| `__delattr__` | 속성 삭제 시 |
| `__getattribute__` | 모든 속성 접근 시 |

```python
class Config:
    def __getattr__(self, name):
        return f"{name} 없음"

cfg = Config()
print(cfg.host)  # host 없음
```

---

## 컨텍스트 매니저 (with문)

| 메서드 | 호출 시점 |
|--------|----------|
| `__enter__` | `with` 블록 진입 시 |
| `__exit__` | `with` 블록 종료 시 |

```python
class Timer:
    def __enter__(self):
        import time
        self.start = time.time()
        return self
    
    def __exit__(self, *args):
        import time
        print(f"소요: {time.time() - self.start:.2f}초")

with Timer():
    sum(range(1000000))
# 소요: 0.03초
```

---

## 호출 가능 객체

```python
class Counter:
    def __init__(self):
        self.count = 0
    
    def __call__(self):
        self.count += 1
        return self.count

counter = Counter()
print(counter())  # 1
print(counter())  # 2
```

---

## 클래스 속성

| 속성 | 설명 |
|------|------|
| `__class__` | 인스턴스의 클래스 |
| `__dict__` | 속성 딕셔너리 |
| `__bases__` | 부모 클래스 튜플 |
| `__mro__` | 메서드 해석 순서 |
| `__slots__` | 허용할 속성 제한 (메모리 최적화) |

---

## 요약

| 카테고리 | 주요 메서드 |
|----------|------------|
| 생성/소멸 | `__init__`, `__new__`, `__del__` |
| 문자열 | `__str__`, `__repr__` |
| 비교 | `__eq__`, `__lt__`, `__gt__` |
| 산술 | `__add__`, `__sub__`, `__mul__` |
| 컨테이너 | `__len__`, `__getitem__`, `__iter__` |
| 속성 | `__getattr__`, `__setattr__` |
| 컨텍스트 | `__enter__`, `__exit__` |
| 호출 | `__call__` |

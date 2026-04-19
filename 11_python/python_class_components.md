# Python 클래스 구성 요소 레퍼런스

Python 클래스의 주요 구성 요소와 특수 메서드들에 대한 종합 레퍼런스입니다.

> **참고**: 클래스 기초 개념과 실전 예제는 [python_class.md](./python_class.md)를 참고하세요.

## 목차
- [생성자 (Constructor)](#생성자-constructor)
- [인스턴스 변수와 클래스 변수](#인스턴스-변수와-클래스-변수)
- [메서드 종류](#메서드-종류)
- [프로퍼티 (Property)](#프로퍼티-property)
- [매직 메서드 (Magic Methods)](#매직-메서드-magic-methods)
- [오버로딩 대안](#오버로딩-대안)
- [추가 팁과 베스트 프랙티스](#추가-팁과-베스트-프랙티스)
- [참고 자료](#참고-자료)

---

## 생성자 (Constructor)

객체가 생성될 때 자동으로 호출되는 특별한 메서드입니다.

### 기본 사용법

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

person = Person("김철수", 25)
```

### 주요 특징

- `self`는 첫 번째 매개변수로 필수 (생성되는 인스턴스 자신을 가리킴)
- 객체의 초기 상태를 설정하는 데 사용
- 반환값이 없음 (항상 None 반환)
- 클래스당 하나만 정의 가능 (오버로딩 불가)

### 기본 생성자

`__init__`을 정의하지 않으면 Python이 자동으로 빈 생성자를 제공합니다:

```python
class Empty:
    pass

obj = Empty()  # 기본 생성자 사용
```

### 선택적 매개변수

```python
class Product:
    def __init__(self, name, price=0, stock=0):
        self.name = name
        self.price = price
        self.stock = stock

p1 = Product("노트북", 1000000)
p2 = Product("펜")  # price와 stock은 0으로 설정됨
```

### 가변 키워드 인자 활용

```python
class Person:
    def __init__(self, name, **kwargs):
        self.name = name
        self.age = kwargs.get('age')
        self.email = kwargs.get('email')
        self.phone = kwargs.get('phone')

# 필요한 정보만 선택적으로 전달
p1 = Person("김철수", age=25, email="kim@example.com")
p2 = Person("이영희", phone="010-1234-5678")
```

---

## 인스턴스 변수와 클래스 변수

### 인스턴스 변수 (Instance Variables)

각 객체마다 고유한 값을 가지는 변수입니다:

```python
class Person:
    def __init__(self, name, age):
        self.name = name  # 인스턴스 변수
        self.age = age    # 인스턴스 변수

p1 = Person("김철수", 25)
p2 = Person("이영희", 30)
print(p1.name)  # 김철수
print(p2.name)  # 이영희
```

### 클래스 변수 (Class Variables)

모든 인스턴스가 공유하는 변수입니다:

```python
class Person:
    count = 0  # 클래스 변수
    species = "Homo sapiens"  # 클래스 변수
    
    def __init__(self, name):
        self.name = name
        Person.count += 1

p1 = Person("김철수")
p2 = Person("이영희")
print(Person.count)  # 2
print(p1.species)    # Homo sapiens
print(p2.species)    # Homo sapiens
```

### Tip: 클래스 변수 주의사항

```python
class MyClass:
    shared_list = []  # 위험! 모든 인스턴스가 공유
    
    def __init__(self, name):
        self.name = name
        self.shared_list.append(name)

a = MyClass("A")
b = MyClass("B")
print(a.shared_list)  # ['A', 'B'] - 의도하지 않은 공유!

# 올바른 방법
class MyClass:
    def __init__(self, name):
        self.name = name
        self.my_list = []  # 각 인스턴스마다 독립적
```

---

## 메서드 종류

### 1. 인스턴스 메서드 (Instance Method)

가장 일반적인 메서드로, `self`를 첫 매개변수로 받습니다:

```python
class Person:
    def __init__(self, name):
        self.name = name
    
    def greet(self):  # 인스턴스 메서드
        return f"안녕하세요, {self.name}입니다"
    
    def set_name(self, name):
        self.name = name

p = Person("김철수")
print(p.greet())  # 안녕하세요, 김철수입니다
```

### 2. 클래스 메서드 (Class Method)

클래스 자체를 다루는 메서드로, `@classmethod` 데코레이터를 사용합니다:

```python
class Person:
    count = 0
    
    def __init__(self, name):
        self.name = name
        Person.count += 1
    
    @classmethod
    def get_count(cls):  # cls는 클래스 자체
        return cls.count
    
    @classmethod
    def create_anonymous(cls):  # 팩토리 메서드로 활용
        return cls("익명")

p1 = Person("김철수")
p2 = Person("이영희")
print(Person.get_count())  # 2

p3 = Person.create_anonymous()
print(p3.name)  # 익명
```

### 3. 정적 메서드 (Static Method)

클래스나 인스턴스와 무관한 메서드로, `@staticmethod` 데코레이터를 사용합니다:

```python
class Math:
    @staticmethod
    def add(a, b):  # self나 cls 없음
        return a + b
    
    @staticmethod
    def is_even(n):
        return n % 2 == 0

# 인스턴스 생성 없이 호출 가능
print(Math.add(1, 2))      # 3
print(Math.is_even(4))     # True
```

### Tip: 메서드 선택 가이드

- **인스턴스 메서드**: 인스턴스의 데이터를 사용하거나 수정할 때
- **클래스 메서드**: 클래스 변수를 다루거나 대체 생성자(팩토리 메서드)가 필요할 때
- **정적 메서드**: 클래스와 논리적으로 관련있지만 클래스/인스턴스 데이터가 필요없을 때

---

## 프로퍼티 (Property)

메서드를 속성처럼 사용할 수 있게 해주는 기능입니다.

### 기본 사용법

```python
class Person:
    def __init__(self, name):
        self._name = name
    
    @property
    def name(self):
        """Getter 메서드"""
        return self._name
    
    @name.setter
    def name(self, value):
        """Setter 메서드"""
        if not value:
            raise ValueError("이름은 비어있을 수 없습니다")
        self._name = value
    
    @name.deleter
    def name(self):
        """Deleter 메서드"""
        print(f"{self._name} 삭제됨")
        del self._name

p = Person("김철수")
print(p.name)      # Getter 호출 (메서드지만 속성처럼 접근)
p.name = "이영희"  # Setter 호출
del p.name         # Deleter 호출
```

### 읽기 전용 프로퍼티

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        return self._radius
    
    @property
    def area(self):  # setter 없음 = 읽기 전용
        return 3.14159 * self._radius ** 2
    
    @property
    def diameter(self):
        return self._radius * 2

c = Circle(5)
print(c.area)      # 78.53975
print(c.diameter)  # 10
# c.area = 100     # AttributeError! (setter가 없음)
```

### Tip: 프로퍼티 활용 시나리오

```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius
    
    @property
    def celsius(self):
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("절대영도 이하는 불가능합니다")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5/9

temp = Temperature(25)
print(temp.celsius)     # 25
print(temp.fahrenheit)  # 77.0
temp.fahrenheit = 86
print(temp.celsius)     # 30.0
```

---

## 매직 메서드 (Magic Methods)

`__`로 시작하고 끝나는 특수 메서드들로, Python의 내장 동작을 커스터마이징할 수 있습니다.

### 문자열 표현

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __str__(self):
        """print() 또는 str() 호출 시 사용 (사용자용)"""
        return f"{self.name} ({self.age}세)"
    
    def __repr__(self):
        """repr() 호출 시 사용 (개발자용, 디버깅)"""
        return f"Person('{self.name}', {self.age})"

p = Person("김철수", 25)
print(p)        # 김철수 (25세) - __str__ 호출
print(repr(p))  # Person('김철수', 25) - __repr__ 호출
```

### 비교 연산자

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __eq__(self, other):  # ==
        return self.age == other.age
    
    def __lt__(self, other):  # <
        return self.age < other.age
    
    def __le__(self, other):  # <=
        return self.age <= other.age
    
    def __gt__(self, other):  # >
        return self.age > other.age
    
    def __ge__(self, other):  # >=
        return self.age >= other.age

p1 = Person("김철수", 25)
p2 = Person("이영희", 30)
print(p1 < p2)   # True
print(p1 == p2)  # False
```

### 산술 연산자

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):  # +
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):  # -
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):  # *
        return Vector(self.x * scalar, self.y * scalar)
    
    def __str__(self):
        return f"Vector({self.x}, {self.y})"

v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1 + v2)  # Vector(4, 6)
print(v1 * 3)   # Vector(3, 6)
```

### 컨테이너 관련

```python
class MyList:
    def __init__(self):
        self.items = []
    
    def __len__(self):  # len() 호출 시
        return len(self.items)
    
    def __getitem__(self, index):  # obj[index] 접근 시
        return self.items[index]
    
    def __setitem__(self, index, value):  # obj[index] = value 시
        self.items[index] = value
    
    def __contains__(self, item):  # in 연산자
        return item in self.items
    
    def add(self, item):
        self.items.append(item)

my_list = MyList()
my_list.add("apple")
my_list.add("banana")
print(len(my_list))      # 2
print(my_list[0])        # apple
print("apple" in my_list)  # True
```

### 컨텍스트 매니저

```python
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        """with 블록 진입 시"""
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """with 블록 종료 시"""
        if self.file:
            self.file.close()

# with 문과 함께 사용
with FileManager('test.txt', 'w') as f:
    f.write('Hello, World!')
# 자동으로 파일이 닫힘
```

### 호출 가능 객체

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor
    
    def __call__(self, x):
        """객체를 함수처럼 호출 가능하게 만듦"""
        return x * self.factor

double = Multiplier(2)
triple = Multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15
```

### Tip: 자주 사용되는 매직 메서드

| 메서드 | 용도 | 예시 |
|--------|------|------|
| `__init__` | 생성자 | `obj = MyClass()` |
| `__str__` | 문자열 표현 (사용자용) | `print(obj)` |
| `__repr__` | 문자열 표현 (개발자용) | `repr(obj)` |
| `__len__` | 길이 | `len(obj)` |
| `__getitem__` | 인덱싱 | `obj[key]` |
| `__setitem__` | 인덱스 할당 | `obj[key] = value` |
| `__eq__` | 동등 비교 | `obj1 == obj2` |
| `__lt__` | 작음 비교 | `obj1 < obj2` |
| `__add__` | 덧셈 | `obj1 + obj2` |
| `__call__` | 호출 가능 | `obj()` |
| `__enter__`, `__exit__` | 컨텍스트 매니저 | `with obj:` |

---

## 오버로딩 대안

Python은 전통적인 메서드 오버로딩을 지원하지 않지만, 여러 대안이 있습니다.

### 오버로딩이란?

같은 이름의 함수나 메서드를 매개변수의 개수나 타입을 다르게 해서 여러 개 정의하는 것입니다.

**다른 언어의 오버로딩 (Java 예시):**
```java
class Calculator {
    int add(int a, int b) { return a + b; }
    double add(double a, double b) { return a + b; }
    int add(int a, int b, int c) { return a + b + c; }
}
```

### Python에서 오버로딩이 안 되는 이유

```python
class Calculator:
    def add(self, a, b):
        return a + b
    
    def add(self, a, b, c):  # 이전 add를 덮어씀
        return a + b + c

calc = Calculator()
# calc.add(1, 2)  # TypeError! 3개의 인자가 필요함
```

### 대안 1: 기본 매개변수

```python
class Calculator:
    def add(self, a, b, c=0, d=0):
        return a + b + c + d

calc = Calculator()
print(calc.add(1, 2))        # 3
print(calc.add(1, 2, 3))     # 6
print(calc.add(1, 2, 3, 4))  # 10
```

### 대안 2: 가변 인자 (*args)

```python
class Calculator:
    def add(self, *args):
        return sum(args)

calc = Calculator()
print(calc.add(1, 2))           # 3
print(calc.add(1, 2, 3, 4, 5))  # 15
```

### 대안 3: 가변 키워드 인자 (**kwargs)

```python
class Person:
    def __init__(self, name, **kwargs):
        self.name = name
        self.age = kwargs.get('age')
        self.email = kwargs.get('email')
        self.phone = kwargs.get('phone')

p1 = Person("김철수", age=25, email="kim@example.com")
p2 = Person("이영희", phone="010-1234-5678")
```

### 대안 4: 타입 체크

```python
class Printer:
    def print_value(self, value):
        if isinstance(value, int):
            print(f"정수: {value}")
        elif isinstance(value, str):
            print(f"문자열: {value}")
        elif isinstance(value, list):
            print(f"리스트: {', '.join(map(str, value))}")
        else:
            print(f"기타: {value}")

p = Printer()
p.print_value(42)           # 정수: 42
p.print_value("Hello")      # 문자열: Hello
p.print_value([1, 2, 3])    # 리스트: 1, 2, 3
```

### 대안 5: functools.singledispatch (타입 기반 디스패치)

```python
from functools import singledispatch

@singledispatch
def process(value):
    print(f"기본: {value}")

@process.register(int)
def _(value):
    print(f"정수 처리: {value * 2}")

@process.register(str)
def _(value):
    print(f"문자열 처리: {value.upper()}")

@process.register(list)
def _(value):
    print(f"리스트 처리: {sum(value)}")

process(10)           # 정수 처리: 20
process("hello")      # 문자열 처리: HELLO
process([1, 2, 3])    # 리스트 처리: 6
```

### Tip: *args와 **kwargs 차이

```python
def print_info(*args, **kwargs):
    print("위치 인자 (args):", args)      # 튜플
    print("키워드 인자 (kwargs):", kwargs)  # 딕셔너리

print_info(1, 2, 3, name="김철수", age=25)
# 위치 인자 (args): (1, 2, 3)
# 키워드 인자 (kwargs): {'name': '김철수', 'age': 25}
```

- `*args`: 위치 인자들을 **튜플**로 받음
- `**kwargs`: 키워드 인자들을 **딕셔너리**로 받음

---

## 추가 팁과 베스트 프랙티스

### 1. Private 변수 관례

Python에는 진정한 private 변수가 없지만, 관례를 따릅니다:

```python
class BankAccount:
    def __init__(self, balance):
        self._balance = balance      # Protected (관례상 외부에서 접근 자제)
        self.__secret = "비밀"       # Name mangling (더 강한 보호)
    
    def get_balance(self):
        return self._balance

account = BankAccount(1000)
print(account._balance)    # 접근 가능하지만 권장하지 않음
# print(account.__secret)  # AttributeError
print(account._BankAccount__secret)  # Name mangling으로 접근 가능 (비권장)
```

### 2. 상속과 super()

```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return "소리를 냅니다"

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)  # 부모 클래스의 __init__ 호출
        self.breed = breed
    
    def speak(self):  # 메서드 오버라이딩
        return "멍멍!"

dog = Dog("바둑이", "진돗개")
print(dog.name)   # 바둑이
print(dog.speak())  # 멍멍!
```

### 3. 추상 클래스

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        """하위 클래스에서 반드시 구현해야 함"""
        pass
    
    @abstractmethod
    def perimeter(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

# shape = Shape()  # TypeError! 추상 클래스는 인스턴스화 불가
rect = Rectangle(5, 3)
print(rect.area())  # 15
```

### 4. 데이터 클래스 (Python 3.7+)

반복적인 코드를 줄여주는 편리한 기능:

```python
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
    email: str = ""  # 기본값
    
    # __init__, __repr__, __eq__ 등이 자동 생성됨

p1 = Person("김철수", 25, "kim@example.com")
p2 = Person("이영희", 30)
print(p1)  # Person(name='김철수', age=25, email='kim@example.com')
print(p1 == p2)  # False
```

### 5. 슬롯 (__slots__)

메모리 최적화를 위한 기능:

```python
class Point:
    __slots__ = ['x', 'y']  # 이 속성들만 허용
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
# p.z = 3  # AttributeError! z는 __slots__에 없음
```

### 6. 디스크립터 (고급)

프로퍼티보다 더 강력한 속성 제어:

```python
class PositiveNumber:
    def __init__(self, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name, 0)
    
    def __set__(self, obj, value):
        if value < 0:
            raise ValueError(f"{self.name}은 양수여야 합니다")
        obj.__dict__[self.name] = value

class Product:
    price = PositiveNumber('price')
    stock = PositiveNumber('stock')
    
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

p = Product("노트북", 1000000, 10)
# p.price = -100  # ValueError!
```

---

## 참고 자료

- [Python 공식 문서 - 클래스](https://docs.python.org/ko/3/tutorial/classes.html)
- [Python 공식 문서 - 데이터 모델 (매직 메서드)](https://docs.python.org/ko/3/reference/datamodel.html)
- [PEP 8 - Python 코딩 스타일 가이드](https://peps.python.org/pep-0008/)

# Python Class 튜토리얼

초보자를 위한 Python 클래스 완벽 가이드입니다.

> **참고**: 클래스 구성 요소(생성자, 메서드, 프로퍼티, 매직 메서드 등)의 상세한 레퍼런스는 [python_class_components.md](./python_class_components.md)를 참고하세요.

## 목차
1. [기초 개념](#기초-개념)
2. [클래스 정의와 인스턴스](#클래스-정의와-인스턴스)
3. [생성자와 기본 사용법](#생성자와-기본-사용법)
4. [상속](#상속)
5. [실전 예제](#실전-예제)
6. [고급 주제](#고급-주제)
7. [실전 팁 (Tips)](#실전-팁-tips)
8. [자주하는 실수](#자주하는-실수)
9. [베스트 프랙티스](#베스트-프랙티스)
10. [요약](#요약)

---

## 기초 개념

### 클래스란?
객체를 만들기 위한 설계도 (blueprint)

### 객체(인스턴스)란?
클래스로부터 만들어진 실체

```python
# 클래스 = 붕어빵 틀
# 객체 = 붕어빵
```

---

## 클래스 정의와 인스턴스

### 가장 간단한 클래스
```python
class Dog:
    pass

# 인스턴스 생성
my_dog = Dog()
```

### 기본 클래스
```python
class Dog:
    def bark(self):
        print("멍멍!")

# 사용
dog = Dog()
dog.bark()  # 멍멍!
```

### self란?
인스턴스 자기 자신을 가리키는 매개변수

```python
class Dog:
    def bark(self):
        print(f"{self}가 짖습니다")

dog1 = Dog()
dog2 = Dog()

dog1.bark()  # <__main__.Dog object at 0x...>가 짖습니다
dog2.bark()  # <__main__.Dog object at 0x...>가 짖습니다 (다른 주소)
```

---

## 생성자와 기본 사용법

### 생성자 (__init__)
인스턴스 생성 시 자동 호출

```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def bark(self):
        print(f"{self.name}가 멍멍!")

# 사용
dog = Dog("바둑이", 3)
print(dog.name)  # 바둑이
print(dog.age)   # 3
dog.bark()       # 바둑이가 멍멍!
```

### 기본값 설정
```python
class Dog:
    def __init__(self, name, age=1):
        self.name = name
        self.age = age

dog1 = Dog("바둑이", 3)
dog2 = Dog("멍멍이")  # age는 기본값 1
```

### 인스턴스 속성과 메서드
```python
class Dog:
    def __init__(self, name):
        self.name = name  # 인스턴스 속성
    
    def bark(self):  # 인스턴스 메서드
        return f"{self.name}가 멍멍!"
    
    def get_age_in_human_years(self, dog_age):
        return dog_age * 7

dog = Dog("바둑이")
print(dog.bark())  # 바둑이가 멍멍!
print(dog.get_age_in_human_years(3))  # 21
```

> **더 알아보기**: 생성자, 메서드 종류, 프로퍼티, 매직 메서드에 대한 자세한 내용은 [python_class_components.md](./python_class_components.md)를 참고하세요.

---

## 상속

### 기본 상속
```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        pass

class Dog(Animal):  # Animal 상속
    def speak(self):
        return f"{self.name}가 멍멍!"

class Cat(Animal):
    def speak(self):
        return f"{self.name}가 야옹!"

dog = Dog("바둑이")
cat = Cat("나비")

print(dog.speak())  # 바둑이가 멍멍!
print(cat.speak())  # 나비가 야옹!
```

### super() 사용
```python
class Animal:
    def __init__(self, name):
        self.name = name
        print(f"Animal 생성: {name}")

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)  # 부모 클래스 생성자 호출
        self.breed = breed
        print(f"Dog 생성: {breed}")

dog = Dog("바둑이", "진돗개")
# Animal 생성: 바둑이
# Dog 생성: 진돗개
```

### 다중 상속
```python
class Flyable:
    def fly(self):
        return "날 수 있어요"

class Swimmable:
    def swim(self):
        return "수영할 수 있어요"

class Duck(Flyable, Swimmable):
    def __init__(self, name):
        self.name = name

duck = Duck("도널드")
print(duck.fly())   # 날 수 있어요
print(duck.swim())  # 수영할 수 있어요
```

---

## 실전 예제

### 예제 1: 은행 계좌
```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance
    
    @property
    def balance(self):
        return self._balance
    
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("입금액은 0보다 커야 합니다")
        self._balance += amount
        return self._balance
    
    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("출금액은 0보다 커야 합니다")
        if amount > self._balance:
            raise ValueError("잔액이 부족합니다")
        self._balance -= amount
        return self._balance
    
    def __str__(self):
        return f"BankAccount(owner={self.owner}, balance={self._balance})"

# 사용
account = BankAccount("홍길동", 10000)
print(account)  # BankAccount(owner=홍길동, balance=10000)

account.deposit(5000)
print(account.balance)  # 15000

account.withdraw(3000)
print(account.balance)  # 12000
```

### 예제 2: 학생 관리
```python
class Student:
    def __init__(self, name, student_id):
        self.name = name
        self.student_id = student_id
        self.grades = []
    
    def add_grade(self, grade):
        if 0 <= grade <= 100:
            self.grades.append(grade)
        else:
            raise ValueError("성적은 0-100 사이여야 합니다")
    
    def get_average(self):
        if not self.grades:
            return 0
        return sum(self.grades) / len(self.grades)
    
    def __str__(self):
        return f"Student(name={self.name}, avg={self.get_average():.2f})"

# 사용
student = Student("김철수", "2024001")
student.add_grade(85)
student.add_grade(90)
student.add_grade(88)

print(student)  # Student(name=김철수, avg=87.67)
print(f"평균: {student.get_average():.2f}")  # 평균: 87.67
```

### 예제 3: 쇼핑 카트
```python
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price
    
    def __str__(self):
        return f"{self.name}: {self.price}원"

class ShoppingCart:
    def __init__(self):
        self.items = []
    
    def add_item(self, product, quantity=1):
        self.items.append({"product": product, "quantity": quantity})
    
    def remove_item(self, product_name):
        self.items = [item for item in self.items 
                      if item["product"].name != product_name]
    
    def get_total(self):
        return sum(item["product"].price * item["quantity"] 
                   for item in self.items)
    
    def __len__(self):
        return len(self.items)
    
    def __str__(self):
        lines = ["쇼핑 카트:"]
        for item in self.items:
            product = item["product"]
            quantity = item["quantity"]
            lines.append(f"  - {product.name} x {quantity}: {product.price * quantity}원")
        lines.append(f"총액: {self.get_total()}원")
        return "\n".join(lines)

# 사용
cart = ShoppingCart()
cart.add_item(Product("노트북", 1000000), 1)
cart.add_item(Product("마우스", 30000), 2)
cart.add_item(Product("키보드", 80000), 1)

print(cart)
# 쇼핑 카트:
#   - 노트북 x 1: 1000000원
#   - 마우스 x 2: 60000원
#   - 키보드 x 1: 80000원
# 총액: 1140000원

print(f"상품 개수: {len(cart)}")  # 상품 개수: 3
```

### 예제 4: 날짜 클래스
```python
class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day
    
    @classmethod
    def from_string(cls, date_string):
        """문자열에서 Date 객체 생성"""
        year, month, day = map(int, date_string.split('-'))
        return cls(year, month, day)
    
    @classmethod
    def today(cls):
        """오늘 날짜 반환 (예시)"""
        return cls(2026, 3, 11)
    
    def __str__(self):
        return f"{self.year}-{self.month:02d}-{self.day:02d}"
    
    def __eq__(self, other):
        return (self.year == other.year and 
                self.month == other.month and 
                self.day == other.day)

# 사용
date1 = Date(2026, 3, 11)
date2 = Date.from_string("2026-03-11")
date3 = Date.today()

print(date1)  # 2026-03-11
print(date2)  # 2026-03-11
print(date1 == date2)  # True
```

---

## 고급 주제

### 추상 클래스
```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "멍멍!"

class Cat(Animal):
    def speak(self):
        return "야옹!"

# animal = Animal()  # TypeError: 추상 클래스는 인스턴스화 불가
dog = Dog()
print(dog.speak())  # 멍멍!
```

### 데이터 클래스 (Python 3.7+)
```python
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
    email: str = ""
    
    def greet(self):
        return f"안녕하세요, {self.name}입니다"

# 자동으로 __init__, __repr__, __eq__ 생성
person = Person("홍길동", 30, "hong@example.com")
print(person)  # Person(name='홍길동', age=30, email='hong@example.com')
print(person.greet())  # 안녕하세요, 홍길동입니다
```

### 싱글톤 패턴
```python
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

s1 = Singleton()
s2 = Singleton()
print(s1 is s2)  # True (같은 인스턴스)
```

---

## 실전 팁 (Tips)

### Tip 1: 언더스코어 네이밍 규칙
```python
class MyClass:
    def __init__(self):
        self.public = 1        # public: 어디서나 접근 가능
        self._protected = 2    # protected: 내부 사용 권장 (강제 아님)
        self.__private = 3     # private: 이름 맹글링 (name mangling)

obj = MyClass()
print(obj.public)      # 1
print(obj._protected)  # 2 (접근 가능하지만 권장 안 함)
# print(obj.__private) # AttributeError
print(obj._MyClass__private)  # 3 (맹글링된 이름으로 접근 가능)
```

### Tip 2: isinstance()와 type() 차이
```python
class Animal:
    pass

class Dog(Animal):
    pass

dog = Dog()

# isinstance: 상속 관계 고려
print(isinstance(dog, Dog))     # True
print(isinstance(dog, Animal))  # True (상속)

# type: 정확한 타입만
print(type(dog) == Dog)     # True
print(type(dog) == Animal)  # False
```

### Tip 3: hasattr, getattr, setattr
```python
class Dog:
    def __init__(self, name):
        self.name = name

dog = Dog("바둑이")

# 속성 존재 확인
print(hasattr(dog, 'name'))  # True
print(hasattr(dog, 'age'))   # False

# 속성 가져오기 (기본값 설정 가능)
print(getattr(dog, 'name'))           # 바둑이
print(getattr(dog, 'age', 0))         # 0 (기본값)

# 속성 설정
setattr(dog, 'age', 3)
print(dog.age)  # 3
```

### Tip 4: 메서드 체이닝
```python
class Calculator:
    def __init__(self, value=0):
        self.value = value
    
    def add(self, n):
        self.value += n
        return self  # self 반환
    
    def multiply(self, n):
        self.value *= n
        return self
    
    def subtract(self, n):
        self.value -= n
        return self

# 체이닝 사용
result = Calculator(10).add(5).multiply(2).subtract(3)
print(result.value)  # 27
```

### Tip 5: 상속 순서 확인 (MRO)
```python
class A:
    pass

class B(A):
    pass

class C(A):
    pass

class D(B, C):
    pass

# Method Resolution Order
print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
```

### Tip 6: 복사 (얕은 복사 vs 깊은 복사)
```python
import copy

class Dog:
    def __init__(self, name, toys):
        self.name = name
        self.toys = toys

dog1 = Dog("바둑이", ["공", "인형"])

# 얕은 복사 (shallow copy)
dog2 = copy.copy(dog1)
dog2.name = "멍멍이"
dog2.toys.append("뼈다귀")

print(dog1.name)  # 바둑이 (독립적)
print(dog1.toys)  # ['공', '인형', '뼈다귀'] (공유됨!)

# 깊은 복사 (deep copy)
dog3 = copy.deepcopy(dog1)
dog3.toys.append("공2")

print(dog1.toys)  # ['공', '인형', '뼈다귀'] (독립적)
print(dog3.toys)  # ['공', '인형', '뼈다귀', '공2']
```

---

## 자주하는 실수

### 실수 1: 가변 기본 인자
```python
# 나쁜 예
class Dog:
    def __init__(self, name, tricks=[]):  # 위험!
        self.name = name
        self.tricks = tricks

# 좋은 예
class Dog:
    def __init__(self, name, tricks=None):
        self.name = name
        self.tricks = tricks if tricks is not None else []
```

### 실수 2: self 빠뜨리기
```python
# 나쁜 예
class Dog:
    def bark():  # self 없음!
        print("멍멍")

# 좋은 예
class Dog:
    def bark(self):
        print("멍멍")
```

### 실수 3: 클래스 변수와 인스턴스 변수 혼동
```python
# 나쁜 예
class Dog:
    name = "기본이름"  # 클래스 변수
    
    def __init__(self, name):
        name = name  # self 없음! 지역 변수

# 좋은 예
class Dog:
    def __init__(self, name):
        self.name = name  # 인스턴스 변수
```

### 실수 4: super() 잘못 사용
```python
# 나쁜 예
class Dog(Animal):
    def __init__(self, name):
        Animal.__init__(self, name)  # 다중 상속 시 문제

# 좋은 예
class Dog(Animal):
    def __init__(self, name):
        super().__init__(name)  # MRO 따름
```

---

## 베스트 프랙티스

### 1. 명명 규칙
```python
class MyClass:           # 클래스: PascalCase
    class_variable = 0   # 클래스 변수: snake_case
    
    def __init__(self):
        self.public_var = 1      # public: snake_case
        self._protected_var = 2  # protected: _로 시작
        self.__private_var = 3   # private: __로 시작
    
    def public_method(self):     # public 메서드
        pass
    
    def _protected_method(self): # protected 메서드
        pass
    
    def __private_method(self):  # private 메서드
        pass
```

### 2. 단일 책임 원칙
```python
# 나쁜 예
class User:
    def __init__(self, name):
        self.name = name
    
    def save_to_database(self):
        pass
    
    def send_email(self):
        pass

# 좋은 예
class User:
    def __init__(self, name):
        self.name = name

class UserRepository:
    def save(self, user):
        pass

class EmailService:
    def send(self, user):
        pass
```

### 3. 문서화
```python
class Dog:
    """강아지를 나타내는 클래스
    
    Attributes:
        name (str): 강아지 이름
        age (int): 강아지 나이
    """
    
    def __init__(self, name, age):
        """Dog 인스턴스 초기화
        
        Args:
            name (str): 강아지 이름
            age (int): 강아지 나이
        """
        self.name = name
        self.age = age
    
    def bark(self):
        """강아지가 짖는 소리를 반환
        
        Returns:
            str: 짖는 소리
        """
        return f"{self.name}가 멍멍!"
```

---

## 요약

| 개념 | 설명 | 예시 |
|------|------|------|
| 클래스 | 객체의 설계도 | `class Dog:` |
| 인스턴스 | 클래스로 만든 객체 | `dog = Dog()` |
| `__init__` | 생성자 | 인스턴스 초기화 |
| `self` | 인스턴스 자신 | 메서드 첫 매개변수 |
| 상속 | 부모 클래스 기능 물려받기 | `class Dog(Animal):` |
| `@property` | getter/setter | 속성처럼 사용 |
| `@staticmethod` | 정적 메서드 | 클래스/인스턴스 무관 |
| `@classmethod` | 클래스 메서드 | 클래스 자체 다룸 |

**핵심 포인트:**
- 클래스는 객체를 만드는 틀
- `self`는 인스턴스 자신을 가리킴
- 상속으로 코드 재사용
- 특수 메서드로 연산자 오버로딩
- 프로퍼티로 캡슐화

**더 알아보기:**
- [python_class_components.md](./python_class_components.md) - 클래스 구성 요소 상세 레퍼런스

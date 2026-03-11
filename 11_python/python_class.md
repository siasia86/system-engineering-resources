# Python Class 가이드

## 목차
1. [기초 개념](#기초-개념)
2. [클래스 정의와 인스턴스](#클래스-정의와-인스턴스)
3. [생성자와 소멸자](#생성자와-소멸자)
4. [속성과 메서드](#속성과-메서드)
5. [상속](#상속)
6. [특수 메서드](#특수-메서드)
7. [클래스 변수 vs 인스턴스 변수](#클래스-변수-vs-인스턴스-변수)
8. [정적 메서드와 클래스 메서드](#정적-메서드와-클래스-메서드)
9. [프로퍼티](#프로퍼티)
10. [실전 예제](#실전-예제)
11. [고급 주제](#고급-주제)
12. [실전 팁](#실전-팁-tips)
13. [자주하는 실수](#자주하는-실수)
14. [베스트 프랙티스](#베스트-프랙티스)

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

## 생성자와 소멸자

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

### 소멸자 (__del__)
인스턴스 삭제 시 자동 호출

```python
class Dog:
    def __init__(self, name):
        self.name = name
        print(f"{self.name} 생성됨")
    
    def __del__(self):
        print(f"{self.name} 삭제됨")

dog = Dog("바둑이")  # 바둑이 생성됨
del dog              # 바둑이 삭제됨
```

---

## 속성과 메서드

### 인스턴스 속성
```python
class Dog:
    def __init__(self, name, age):
        self.name = name  # 인스턴스 속성
        self.age = age

dog = Dog("바둑이", 3)
print(dog.name)  # 바둑이

# 속성 추가/수정 가능
dog.color = "갈색"
print(dog.color)  # 갈색
```

### 인스턴스 메서드
```python
class Dog:
    def __init__(self, name):
        self.name = name
    
    def bark(self):  # 인스턴스 메서드
        return f"{self.name}가 멍멍!"
    
    def get_age_in_human_years(self, dog_age):
        return dog_age * 7

dog = Dog("바둑이")
print(dog.bark())  # 바둑이가 멍멍!
print(dog.get_age_in_human_years(3))  # 21
```

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

**실행 결과:**
```
Animal 생성: 바둑이
Dog 생성: 진돗개
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

## 특수 메서드

### __str__ (문자열 표현)
```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __str__(self):
        return f"Dog(name={self.name}, age={self.age})"

dog = Dog("바둑이", 3)
print(dog)  # Dog(name=바둑이, age=3)
```

### __repr__ (개발자용 표현)
```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __repr__(self):
        return f"Dog('{self.name}', {self.age})"

dog = Dog("바둑이", 3)
print(repr(dog))  # Dog('바둑이', 3)
```

### __len__ (길이)
```python
class Team:
    def __init__(self, members):
        self.members = members
    
    def __len__(self):
        return len(self.members)

team = Team(["철수", "영희", "민수"])
print(len(team))  # 3
```

### __getitem__ (인덱싱)
```python
class Team:
    def __init__(self, members):
        self.members = members
    
    def __getitem__(self, index):
        return self.members[index]

team = Team(["철수", "영희", "민수"])
print(team[0])  # 철수
print(team[1])  # 영희
```

### __add__ (덧셈)
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    def __str__(self):
        return f"Point({self.x}, {self.y})"

p1 = Point(1, 2)
p2 = Point(3, 4)
p3 = p1 + p2
print(p3)  # Point(4, 6)
```

**실행 결과:**
```
Point(4, 6)
```

### __eq__ (비교)
```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __eq__(self, other):
        return self.name == other.name and self.age == other.age

dog1 = Dog("바둑이", 3)
dog2 = Dog("바둑이", 3)
dog3 = Dog("멍멍이", 3)

print(dog1 == dog2)  # True
print(dog1 == dog3)  # False
```

---

## 클래스 변수 vs 인스턴스 변수

### 인스턴스 변수
각 인스턴스마다 독립적

```python
class Dog:
    def __init__(self, name):
        self.name = name  # 인스턴스 변수

dog1 = Dog("바둑이")
dog2 = Dog("멍멍이")

print(dog1.name)  # 바둑이
print(dog2.name)  # 멍멍이
```

### 클래스 변수
모든 인스턴스가 공유

```python
class Dog:
    species = "Canis familiaris"  # 클래스 변수
    
    def __init__(self, name):
        self.name = name  # 인스턴스 변수

dog1 = Dog("바둑이")
dog2 = Dog("멍멍이")

print(dog1.species)  # Canis familiaris
print(dog2.species)  # Canis familiaris

# 클래스 변수 변경
Dog.species = "개"
print(dog1.species)  # 개
print(dog2.species)  # 개
```

### 인스턴스 카운팅
```python
class Dog:
    count = 0  # 클래스 변수
    
    def __init__(self, name):
        self.name = name
        Dog.count += 1  # 생성될 때마다 증가

dog1 = Dog("바둑이")
dog2 = Dog("멍멍이")
dog3 = Dog("뽀삐")

print(Dog.count)  # 3
```

---

## 정적 메서드와 클래스 메서드

### 정적 메서드 (@staticmethod)
클래스나 인스턴스와 무관한 독립적인 메서드

```python
class Math:
    @staticmethod
    def add(x, y):
        return x + y
    
    @staticmethod
    def multiply(x, y):
        return x * y

# 인스턴스 생성 없이 호출
print(Math.add(5, 3))       # 8
print(Math.multiply(5, 3))  # 15
```

### 클래스 메서드 (@classmethod)
클래스 자체를 다루는 메서드

```python
class Dog:
    count = 0
    
    def __init__(self, name):
        self.name = name
        Dog.count += 1
    
    @classmethod
    def get_count(cls):
        return cls.count
    
    @classmethod
    def create_puppy(cls, name):
        return cls(name)

dog1 = Dog("바둑이")
dog2 = Dog("멍멍이")

print(Dog.get_count())  # 2

# 팩토리 메서드로 활용
puppy = Dog.create_puppy("뽀삐")
print(Dog.get_count())  # 3
```

**실행 결과:**
```
2
3
```

### 비교

```python
class Example:
    class_var = "클래스 변수"
    
    def instance_method(self):
        # self: 인스턴스 접근
        return f"인스턴스 메서드: {self}"
    
    @classmethod
    def class_method(cls):
        # cls: 클래스 접근
        return f"클래스 메서드: {cls.class_var}"
    
    @staticmethod
    def static_method():
        # self, cls 없음
        return "정적 메서드"

obj = Example()
print(obj.instance_method())     # 인스턴스 메서드
print(Example.class_method())    # 클래스 메서드: 클래스 변수
print(Example.static_method())   # 정적 메서드
```

---

## 프로퍼티

### @property (getter)
```python
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        return self._radius
    
    @property
    def diameter(self):
        return self._radius * 2
    
    @property
    def area(self):
        return 3.14 * self._radius ** 2

circle = Circle(5)
print(circle.radius)    # 5
print(circle.diameter)  # 10
print(circle.area)      # 78.5
```

**실행 결과:**
```
5
10
78.5
```

### @property.setter
```python
class Person:
    def __init__(self, name, age):
        self._name = name
        self._age = age
    
    @property
    def age(self):
        return self._age
    
    @age.setter
    def age(self, value):
        if value < 0:
            raise ValueError("나이는 0 이상이어야 합니다")
        self._age = value

person = Person("홍길동", 30)
print(person.age)  # 30

person.age = 31    # setter 호출
print(person.age)  # 31

# person.age = -1  # ValueError
```

**실행 결과:**
```
30
31
```
`person.age = -1` 실행 시: `ValueError: 나이는 0 이상이어야 합니다`

### 읽기 전용 속성
```python
class Product:
    def __init__(self, name, price):
        self._name = name
        self._price = price
    
    @property
    def name(self):
        return self._name
    
    @property
    def price(self):
        return self._price
    
    # setter 없음 = 읽기 전용

product = Product("노트북", 1000000)
print(product.name)   # 노트북
print(product.price)  # 1000000

# product.price = 900000  # AttributeError
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
        return cls(2026, 3, 3)
    
    def __str__(self):
        return f"{self.year}-{self.month:02d}-{self.day:02d}"
    
    def __eq__(self, other):
        return (self.year == other.year and 
                self.month == other.month and 
                self.day == other.day)

# 사용
date1 = Date(2026, 3, 3)
date2 = Date.from_string("2026-03-03")
date3 = Date.today()

print(date1)  # 2026-03-03
print(date2)  # 2026-03-03
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

**실행 결과:**
```
1
2
3
```

### Tip 2: __slots__로 메모리 절약
```python
# 일반 클래스 (딕셔너리 사용)
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# __slots__ 사용 (메모리 절약)
class PointWithSlots:
    __slots__ = ['x', 'y']
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

# 장점: 메모리 사용량 감소 (수천~수만 개 인스턴스 생성 시 유용)
# 단점: 동적으로 속성 추가 불가

p = PointWithSlots(1, 2)
print(p.x, p.y)  # 1 2
# p.z = 3  # AttributeError: 'PointWithSlots' object has no attribute 'z'
```

**실행 결과:**
```
1 2
```
`p.z = 3` 실행 시: `AttributeError: 'PointWithSlots' object has no attribute 'z'`

###  Tip 3: isinstance()와 type() 차이
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

**실행 결과:**
```
True
True
True
False
```

###  Tip 4: hasattr, getattr, setattr
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

###  Tip 5: 클래스 변수 주의사항
```python
# 위험: 가변 객체를 클래스 변수로 사용
class Dog:
    tricks = []  # 클래스 변수 (모든 인스턴스 공유!)
    
    def __init__(self, name):
        self.name = name
    
    def add_trick(self, trick):
        self.tricks.append(trick)

dog1 = Dog("바둑이")
dog2 = Dog("멍멍이")

dog1.add_trick("앉아")
dog2.add_trick("손")

print(dog1.tricks)  # ['앉아', '손'] - 공유됨!
print(dog2.tricks)  # ['앉아', '손'] - 공유됨!

# 올바른 방법: 인스턴스 변수 사용
class Dog:
    def __init__(self, name):
        self.name = name
        self.tricks = []  # 인스턴스 변수
    
    def add_trick(self, trick):
        self.tricks.append(trick)
```

**실행 결과:**
```
['앉아', '손']
['앉아', '손']
```
⚠️ 두 개가 같은 리스트를 공유합니다!

###  Tip 6: 메서드 체이닝
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

**실행 결과:**
```
27
```
계산 과정: (10 + 5) × 2 - 3 = 15 × 2 - 3 = 30 - 3 = 27

###  Tip 7: __call__로 호출 가능한 객체
```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor
    
    def __call__(self, x):
        return x * self.factor

double = Multiplier(2)
triple = Multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15
```

**실행 결과:**
```
10
15
```

###  Tip 8: 컨텍스트 매니저 (__enter__, __exit__)
```python
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

# with 문 사용
with FileManager('test.txt', 'w') as f:
    f.write('Hello, World!')
# 자동으로 파일 닫힘
```

###  Tip 9: 클래스 데코레이터
```python
def singleton(cls):
    """싱글톤 데코레이터"""
    instances = {}
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class Database:
    def __init__(self):
        print("Database 연결")

db1 = Database()  # Database 연결
db2 = Database()  # 출력 없음 (같은 인스턴스)
print(db1 is db2)  # True
```

###  Tip 10: __dict__로 속성 확인
```python
class Dog:
    species = "Canis familiaris"
    
    def __init__(self, name, age):
        self.name = name
        self.age = age

dog = Dog("바둑이", 3)

# 인스턴스 속성
print(dog.__dict__)  # {'name': '바둑이', 'age': 3}

# 클래스 속성
print(Dog.__dict__)  # {..., 'species': 'Canis familiaris', ...}
```

**실행 결과:**
```
{'name': '바둑이', 'age': 3}
{'__module__': '__main__', 'species': 'Canis familiaris', '__init__': <function Dog.__init__ at ...>, '__dict__': <attribute '__dict__' of 'Dog' objects>, '__weakref__': <attribute '__weakref__' of 'Dog' objects>, '__doc__': None}
```

###  Tip 11: 상속 순서 확인 (MRO)
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

# 또는
print(D.mro())
```

**실행 결과:**
```
(<class '__main__.D'>, <class '__main__.B'>, <class '__main__.C'>, <class '__main__.A'>, <class 'object'>)
```
메서드 탐색 순서: D → B → C → A → object

###  Tip 12: 추상 속성
```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @property
    @abstractmethod
    def area(self):
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    @property
    def area(self):
        return 3.14 * self.radius ** 2

circle = Circle(5)
print(circle.area)  # 78.5
```

###  Tip 13: 클래스 비교 연산자 전체 구현
```python
from functools import total_ordering

@total_ordering
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __eq__(self, other):
        return self.age == other.age
    
    def __lt__(self, other):
        return self.age < other.age
    
    # @total_ordering이 나머지 연산자 자동 생성
    # __le__, __gt__, __ge__

p1 = Person("철수", 20)
p2 = Person("영희", 25)

print(p1 < p2)   # True
print(p1 <= p2)  # True
print(p1 > p2)   # False
print(p1 >= p2)  # False
```

**실행 결과:**
```
True
True
False
False
```

###  Tip 14: 복사 (얕은 복사 vs 깊은 복사)
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

**실행 결과:**
```
바둑이
['공', '인형', '뼈다귀']
['공', '인형', '뼈다귀']
['공', '인형', '뼈다귀', '공2']
```
얕은 복사: name은 독립적이지만 toys 리스트는 공유됨!

###  Tip 15: 디버깅용 __repr__
```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __repr__(self):
        # 재생성 가능한 형태로 표현
        return f"Dog('{self.name}', {self.age})"
    
    def __str__(self):
        # 사용자 친화적 표현
        return f"{self.name} ({self.age}살)"

dog = Dog("바둑이", 3)
print(str(dog))   # 바둑이 (3살)
print(repr(dog))  # Dog('바둑이', 3)
print(dog)        # 바둑이 (3살) (__str__ 우선)

# 리스트에서는 __repr__ 사용
dogs = [dog]
print(dogs)  # [Dog('바둑이', 3)]
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

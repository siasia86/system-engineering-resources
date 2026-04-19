# Python 상속 (Inheritance)

Python의 상속 개념과 활용 방법에 대한 종합 가이드입니다.

> **참고**: 클래스 기초는 [python_class.md](./python_class.md)를 참고하세요.

## 목차
- [상속이란?](#상속이란)
- [기본 상속](#기본-상속)
- [super() 함수](#super-함수)
- [다중 상속](#다중-상속)
- [메서드 오버라이딩](#메서드-오버라이딩)
- [추상 클래스](#추상-클래스)
- [실전 예제](#실전-예제)
- [상속 vs 컴포지션](#상속-vs-컴포지션)
- [실전 팁](#실전-팁)
- [베스트 프랙티스](#베스트-프랙티스)
- [자주하는 실수](#자주하는-실수)
- [요약](#요약)

---

## 상속이란?

기존 클래스의 속성과 메서드를 물려받아 새로운 클래스를 만드는 것입니다.

### 왜 사용하나?

- **코드 재사용**: 중복 코드 제거
- **계층 구조**: 논리적인 클래스 구조
- **확장성**: 기존 코드 수정 없이 기능 추가
- **다형성**: 같은 인터페이스로 다른 동작

### 용어

- **부모 클래스** (Parent Class): 상속을 해주는 클래스 (Base Class, Super Class)
- **자식 클래스** (Child Class): 상속을 받는 클래스 (Derived Class, Sub Class)

---

## 기본 상속

### 단순 상속

```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return "소리를 냅니다"
    
    def move(self):
        return f"{self.name}가 움직입니다"

class Dog(Animal):  # Animal을 상속
    def speak(self):  # 메서드 오버라이딩
        return "멍멍!"

class Cat(Animal):
    def speak(self):
        return "야옹!"

# 사용
dog = Dog("바둑이")
cat = Cat("나비")

print(dog.name)      # 바둑이 (부모로부터 상속)
print(dog.speak())   # 멍멍! (오버라이딩)
print(dog.move())    # 바둑이가 움직입니다 (부모 메서드)

print(cat.speak())   # 야옹!
```

### 상속 확인

```python
class Animal:
    pass

class Dog(Animal):
    pass

dog = Dog()

# isinstance: 인스턴스 확인
print(isinstance(dog, Dog))     # True
print(isinstance(dog, Animal))  # True (상속 관계)
print(isinstance(dog, object))  # True (모든 클래스는 object 상속)

# issubclass: 클래스 상속 확인
print(issubclass(Dog, Animal))  # True
print(issubclass(Animal, Dog))  # False
```

---

## super() 함수

부모 클래스의 메서드를 호출할 때 사용합니다.

### 기본 사용

```python
class Animal:
    def __init__(self, name):
        self.name = name
        print(f"Animal 생성: {name}")
    
    def speak(self):
        return "소리를 냅니다"

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)  # 부모 생성자 호출
        self.breed = breed
        print(f"Dog 생성: {breed}")
    
    def speak(self):
        parent_speak = super().speak()  # 부모 메서드 호출
        return f"{parent_speak} - 멍멍!"

dog = Dog("바둑이", "진돗개")
# Animal 생성: 바둑이
# Dog 생성: 진돗개

print(dog.speak())
# 소리를 냅니다 - 멍멍!
```

### super() vs 직접 호출

```python
class Animal:
    def __init__(self, name):
        self.name = name

# 나쁜 예: 직접 호출
class Dog(Animal):
    def __init__(self, name, breed):
        Animal.__init__(self, name)  # 다중 상속 시 문제
        self.breed = breed

# 좋은 예: super() 사용
class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)  # MRO를 따름
        self.breed = breed
```

---

## 다중 상속

여러 부모 클래스로부터 상속받는 것입니다.

### 기본 다중 상속

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
    
    def quack(self):
        return "꽥꽥!"

duck = Duck("도널드")
print(duck.fly())    # 날 수 있어요
print(duck.swim())   # 수영할 수 있어요
print(duck.quack())  # 꽥꽥!
```

### MRO (Method Resolution Order)

메서드 탐색 순서를 나타냅니다.

```python
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return "B"

class C(A):
    def method(self):
        return "C"

class D(B, C):
    pass

d = D()
print(d.method())  # B

# MRO 확인
print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)

# 또는
print(D.mro())
```

### 다이아몬드 문제

```python
class A:
    def __init__(self):
        print("A 초기화")

class B(A):
    def __init__(self):
        super().__init__()
        print("B 초기화")

class C(A):
    def __init__(self):
        super().__init__()
        print("C 초기화")

class D(B, C):
    def __init__(self):
        super().__init__()
        print("D 초기화")

d = D()
# A 초기화
# C 초기화
# B 초기화
# D 초기화

# super()가 MRO를 따라 A가 한 번만 호출됨
```

---

## 메서드 오버라이딩

부모 클래스의 메서드를 자식 클래스에서 재정의하는 것입니다.

### 완전 오버라이딩

```python
class Animal:
    def speak(self):
        return "소리를 냅니다"

class Dog(Animal):
    def speak(self):  # 완전히 새로 정의
        return "멍멍!"

dog = Dog()
print(dog.speak())  # 멍멍!
```

### 부분 오버라이딩 (확장)

```python
class Animal:
    def speak(self):
        return "소리를 냅니다"

class Dog(Animal):
    def speak(self):
        parent_result = super().speak()  # 부모 메서드 활용
        return f"{parent_result} - 멍멍!"

dog = Dog()
print(dog.speak())  # 소리를 냅니다 - 멍멍!
```

### 특수 메서드 오버라이딩

```python
class Person:
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"Person: {self.name}"

class Student(Person):
    def __init__(self, name, student_id):
        super().__init__(name)
        self.student_id = student_id
    
    def __str__(self):
        return f"Student: {self.name} (ID: {self.student_id})"

student = Student("김철수", "2024001")
print(student)  # Student: 김철수 (ID: 2024001)
```

---

## 추상 클래스

인스턴스를 만들 수 없고, 자식 클래스에서 반드시 구현해야 하는 메서드를 정의합니다.

### 기본 사용

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        """면적을 계산합니다"""
        pass
    
    @abstractmethod
    def perimeter(self):
        """둘레를 계산합니다"""
        pass

# shape = Shape()  # TypeError: 추상 클래스는 인스턴스화 불가

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14159 * self.radius ** 2
    
    def perimeter(self):
        return 2 * 3.14159 * self.radius

rect = Rectangle(5, 3)
print(rect.area())       # 15
print(rect.perimeter())  # 16

circle = Circle(5)
print(circle.area())     # 78.53975
```

### 추상 속성

```python
from abc import ABC, abstractmethod

class Vehicle(ABC):
    @property
    @abstractmethod
    def max_speed(self):
        pass

class Car(Vehicle):
    @property
    def max_speed(self):
        return 200

car = Car()
print(car.max_speed)  # 200
```

### 일부 구현된 추상 클래스

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    def __init__(self, name):
        self.name = name
    
    @abstractmethod
    def speak(self):
        pass
    
    def move(self):  # 구현된 메서드
        return f"{self.name}가 움직입니다"

class Dog(Animal):
    def speak(self):  # 추상 메서드 구현 필수
        return "멍멍!"

dog = Dog("바둑이")
print(dog.speak())  # 멍멍!
print(dog.move())   # 바둑이가 움직입니다
```

---

## 실전 예제

### 예제 1: 직원 관리 시스템

```python
class Employee:
    def __init__(self, name, employee_id):
        self.name = name
        self.employee_id = employee_id
    
    def get_info(self):
        return f"직원: {self.name} (ID: {self.employee_id})"
    
    def calculate_salary(self):
        raise NotImplementedError("하위 클래스에서 구현해야 합니다")

class FullTimeEmployee(Employee):
    def __init__(self, name, employee_id, monthly_salary):
        super().__init__(name, employee_id)
        self.monthly_salary = monthly_salary
    
    def calculate_salary(self):
        return self.monthly_salary
    
    def get_info(self):
        base_info = super().get_info()
        return f"{base_info} - 정규직 (월급: {self.monthly_salary}원)"

class PartTimeEmployee(Employee):
    def __init__(self, name, employee_id, hourly_rate, hours_worked):
        super().__init__(name, employee_id)
        self.hourly_rate = hourly_rate
        self.hours_worked = hours_worked
    
    def calculate_salary(self):
        return self.hourly_rate * self.hours_worked
    
    def get_info(self):
        base_info = super().get_info()
        return f"{base_info} - 시간제 (시급: {self.hourly_rate}원)"

# 사용
employees = [
    FullTimeEmployee("김철수", "E001", 3000000),
    PartTimeEmployee("이영희", "E002", 15000, 80),
    FullTimeEmployee("박민수", "E003", 3500000)
]

for emp in employees:
    print(emp.get_info())
    print(f"급여: {emp.calculate_salary()}원\n")
```

### 예제 2: 게임 캐릭터

```python
class Character:
    def __init__(self, name, hp, attack):
        self.name = name
        self.hp = hp
        self.attack = attack
    
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
    
    def is_alive(self):
        return self.hp > 0
    
    def basic_attack(self, target):
        print(f"{self.name}의 기본 공격!")
        target.take_damage(self.attack)

class Warrior(Character):
    def __init__(self, name, hp, attack, defense):
        super().__init__(name, hp, attack)
        self.defense = defense
    
    def take_damage(self, damage):
        actual_damage = max(0, damage - self.defense)
        super().take_damage(actual_damage)
        print(f"{self.name}이(가) {actual_damage} 데미지를 받았습니다 (방어력: {self.defense})")
    
    def shield_bash(self, target):
        print(f"{self.name}의 방패 강타!")
        target.take_damage(self.attack * 1.5)

class Mage(Character):
    def __init__(self, name, hp, attack, mana):
        super().__init__(name, hp, attack)
        self.mana = mana
    
    def fireball(self, target):
        if self.mana >= 30:
            print(f"{self.name}의 파이어볼!")
            target.take_damage(self.attack * 2)
            self.mana -= 30
        else:
            print(f"{self.name}의 마나가 부족합니다!")
            self.basic_attack(target)

# 사용
warrior = Warrior("전사", 150, 20, 10)
mage = Mage("마법사", 100, 15, 100)

mage.fireball(warrior)
# 마법사의 파이어볼!
# 전사이(가) 20 데미지를 받았습니다 (방어력: 10)

warrior.shield_bash(mage)
# 전사의 방패 강타!

print(f"전사 HP: {warrior.hp}")
print(f"마법사 HP: {mage.hp}")
```

### 예제 3: 결제 시스템

```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    def process_payment(self, amount):
        pass
    
    @abstractmethod
    def refund(self, amount):
        pass

class CreditCard(PaymentMethod):
    def __init__(self, card_number, cvv):
        self.card_number = card_number
        self.cvv = cvv
    
    def process_payment(self, amount):
        print(f"신용카드 결제: {amount}원")
        print(f"카드번호: {self.card_number[-4:]}")
        return True
    
    def refund(self, amount):
        print(f"신용카드 환불: {amount}원")
        return True

class BankTransfer(PaymentMethod):
    def __init__(self, account_number, bank_name):
        self.account_number = account_number
        self.bank_name = bank_name
    
    def process_payment(self, amount):
        print(f"계좌이체 결제: {amount}원")
        print(f"은행: {self.bank_name}")
        return True
    
    def refund(self, amount):
        print(f"계좌이체 환불: {amount}원")
        return True

class PaymentProcessor:
    def __init__(self, payment_method: PaymentMethod):
        self.payment_method = payment_method
    
    def execute_payment(self, amount):
        print(f"결제 처리 시작...")
        if self.payment_method.process_payment(amount):
            print("결제 완료!\n")
        else:
            print("결제 실패!\n")

# 사용
credit_card = CreditCard("1234-5678-9012-3456", "123")
bank_transfer = BankTransfer("110-123-456789", "국민은행")

processor1 = PaymentProcessor(credit_card)
processor1.execute_payment(50000)

processor2 = PaymentProcessor(bank_transfer)
processor2.execute_payment(100000)
```

---

## 상속 vs 컴포지션

### 상속 (Inheritance)

"is-a" 관계: 자식이 부모의 한 종류

```python
class Animal:
    def eat(self):
        return "먹습니다"

class Dog(Animal):  # Dog is an Animal
    def bark(self):
        return "멍멍"
```

**장점:**
- 코드 재사용
- 다형성 지원
- 계층 구조 명확

**단점:**
- 강한 결합
- 부모 변경 시 자식 영향
- 다중 상속 복잡

### 컴포지션 (Composition)

"has-a" 관계: 객체가 다른 객체를 포함

```python
class Engine:
    def start(self):
        return "엔진 시동"

class Car:  # Car has an Engine
    def __init__(self):
        self.engine = Engine()
    
    def start(self):
        return self.engine.start()
```

**장점:**
- 느슨한 결합
- 유연한 구조
- 런타임에 변경 가능

**단점:**
- 코드가 더 많을 수 있음
- 간접 호출 필요

### 선택 기준

```python
# 상속 사용: is-a 관계
class Vehicle:
    pass

class Car(Vehicle):  # Car is a Vehicle
    pass

# 컴포지션 사용: has-a 관계
class Engine:
    pass

class Car:  # Car has an Engine
    def __init__(self):
        self.engine = Engine()
```

**상속을 사용할 때:**
- 명확한 is-a 관계
- 부모의 모든 기능 필요
- 다형성 활용

**컴포지션을 사용할 때:**
- has-a 관계
- 일부 기능만 필요
- 런타임에 동작 변경

---

## 실전 팁

### Tip 1: 상속 깊이는 3단계 이내로

```python
# 나쁜 예: 너무 깊은 상속
class A:
    pass
class B(A):
    pass
class C(B):
    pass
class D(C):
    pass
class E(D):  # 5단계 - 너무 깊음!
    pass

# 좋은 예: 적절한 깊이
class Animal:
    pass
class Mammal(Animal):
    pass
class Dog(Mammal):  # 3단계 - 적절함
    pass
```

### Tip 2: 상속보다 컴포지션 우선 고려

```python
# 상속 (강한 결합)
class Logger:
    def log(self, msg):
        print(msg)

class Service(Logger):  # Service is a Logger? 어색함
    def process(self):
        self.log("처리 중")

# 컴포지션 (느슨한 결합) - 더 좋음
class Logger:
    def log(self, msg):
        print(msg)

class Service:
    def __init__(self):
        self.logger = Logger()  # Service has a Logger
    
    def process(self):
        self.logger.log("처리 중")
```

### Tip 3: 다중 상속은 신중하게

```python
# Mixin 패턴 사용 (다중 상속의 좋은 예)
class JSONMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__)

class LogMixin:
    def log(self, msg):
        print(f"[{self.__class__.__name__}] {msg}")

class User(JSONMixin, LogMixin):
    def __init__(self, name):
        self.name = name

user = User("홍길동")
print(user.to_json())  # {"name": "홍길동"}
user.log("생성됨")     # [User] 생성됨
```

### Tip 4: isinstance() 대신 덕 타이핑

```python
# 나쁜 예: 타입 체크
def process(obj):
    if isinstance(obj, Dog):
        obj.bark()
    elif isinstance(obj, Cat):
        obj.meow()

# 좋은 예: 덕 타이핑 (메서드 존재 여부만 확인)
def process(obj):
    if hasattr(obj, 'speak'):
        obj.speak()
```

### Tip 5: 부모 클래스 변경 시 영향 파악

```python
class Parent:
    def method(self):
        return "Parent"

class Child(Parent):
    def use_parent(self):
        return self.method()  # 부모 메서드 의존

# Parent.method 변경 시 Child에 영향!
# 상속은 강한 결합을 만듦
```

### Tip 6: __init__에서 항상 super() 호출

```python
class Parent:
    def __init__(self):
        self.parent_attr = "parent"

# 나쁜 예
class Child(Parent):
    def __init__(self):
        self.child_attr = "child"  # 부모 초기화 안 됨!

# 좋은 예
class Child(Parent):
    def __init__(self):
        super().__init__()  # 부모 초기화
        self.child_attr = "child"
```

### Tip 7: 추상 클래스로 계약 명시

```python
from abc import ABC, abstractmethod

# 인터페이스 역할
class Drawable(ABC):
    @abstractmethod
    def draw(self):
        """반드시 구현해야 함"""
        pass

class Circle(Drawable):
    def draw(self):  # 구현 강제
        print("원 그리기")

# class Square(Drawable):  # draw() 미구현 시 에러!
#     pass
```

### Tip 8: 메서드 해석 순서(MRO) 확인

```python
class A:
    def method(self):
        return "A"

class B(A):
    pass

class C(A):
    def method(self):
        return "C"

class D(B, C):
    pass

# MRO 확인
print(D.mro())
# [D, B, C, A, object]

d = D()
print(d.method())  # "C" (B에 없으면 C 확인)
```

### Tip 9: 상속 대신 프로토콜 사용 (Python 3.8+)

```python
from typing import Protocol

# 명시적 상속 없이 인터페이스 정의
class Drawable(Protocol):
    def draw(self) -> None:
        ...

class Circle:
    def draw(self):
        print("원")

class Square:
    def draw(self):
        print("사각형")

def render(obj: Drawable):  # Drawable 프로토콜 준수 확인
    obj.draw()

render(Circle())  # OK
render(Square())  # OK
```

### Tip 10: 상속 체인 디버깅

```python
class Animal:
    def __init__(self, name):
        print(f"Animal.__init__: {name}")
        self.name = name

class Mammal(Animal):
    def __init__(self, name, warm_blooded=True):
        print(f"Mammal.__init__: {name}")
        super().__init__(name)
        self.warm_blooded = warm_blooded

class Dog(Mammal):
    def __init__(self, name, breed):
        print(f"Dog.__init__: {name}")
        super().__init__(name)
        self.breed = breed

dog = Dog("바둑이", "진돗개")
# Dog.__init__: 바둑이
# Mammal.__init__: 바둑이
# Animal.__init__: 바둑이
```

---

## 베스트 프랙티스

### 1. 얕은 상속 계층

```python
# 나쁜 예: 너무 깊은 상속
class A:
    pass

class B(A):
    pass

class C(B):
    pass

class D(C):  # 너무 깊음
    pass

# 좋은 예: 2-3단계 이내
class Animal:
    pass

class Mammal(Animal):
    pass

class Dog(Mammal):  # 적절한 깊이
    pass
```

### 2. 리스코프 치환 원칙

자식 클래스는 부모 클래스를 완전히 대체할 수 있어야 합니다.

```python
# 나쁜 예
class Bird:
    def fly(self):
        return "날아갑니다"

class Penguin(Bird):
    def fly(self):
        raise Exception("펭귄은 날 수 없습니다")  # 위반!

# 좋은 예
class Bird:
    def move(self):
        return "이동합니다"

class FlyingBird(Bird):
    def fly(self):
        return "날아갑니다"

class Penguin(Bird):
    def swim(self):
        return "수영합니다"
```

### 3. super() 일관성 있게 사용

```python
class A:
    def __init__(self):
        print("A")

class B(A):
    def __init__(self):
        super().__init__()  # 항상 super() 사용
        print("B")

class C(A):
    def __init__(self):
        super().__init__()
        print("C")

class D(B, C):
    def __init__(self):
        super().__init__()
        print("D")
```

### 4. 추상 클래스로 인터페이스 정의

```python
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    @abstractmethod
    def load_data(self):
        pass
    
    @abstractmethod
    def process_data(self):
        pass
    
    @abstractmethod
    def save_data(self):
        pass

class CSVProcessor(DataProcessor):
    def load_data(self):
        print("CSV 로드")
    
    def process_data(self):
        print("CSV 처리")
    
    def save_data(self):
        print("CSV 저장")
```

### 5. 문서화

```python
class Animal:
    """동물 기본 클래스
    
    모든 동물 클래스의 부모 클래스입니다.
    """
    
    def __init__(self, name):
        """
        Args:
            name (str): 동물 이름
        """
        self.name = name
    
    def speak(self):
        """동물의 소리를 반환합니다
        
        Returns:
            str: 동물의 소리
        
        Note:
            하위 클래스에서 오버라이드해야 합니다.
        """
        raise NotImplementedError("하위 클래스에서 구현하세요")
```

---

## 자주하는 실수

### 실수 1: super() 호출 누락

```python
# 나쁜 예
class Parent:
    def __init__(self, name):
        self.name = name

class Child(Parent):
    def __init__(self, name, age):
        # super().__init__(name) 누락!
        self.age = age

child = Child("홍길동", 30)
# print(child.name)  # AttributeError!

# 좋은 예
class Child(Parent):
    def __init__(self, name, age):
        super().__init__(name)  # 부모 초기화
        self.age = age
```

### 실수 2: 다중 상속 순서 무시

```python
class A:
    def method(self):
        return "A"

class B:
    def method(self):
        return "B"

# 순서가 중요!
class C(A, B):  # A가 우선
    pass

class D(B, A):  # B가 우선
    pass

print(C().method())  # "A"
print(D().method())  # "B"
```

### 실수 3: 부모 메서드 직접 호출

```python
# 나쁜 예: 다중 상속 시 문제
class A:
    def __init__(self):
        print("A")

class B(A):
    def __init__(self):
        A.__init__(self)  # 직접 호출
        print("B")

class C(A):
    def __init__(self):
        A.__init__(self)
        print("C")

class D(B, C):
    def __init__(self):
        B.__init__(self)
        C.__init__(self)
        print("D")

D()
# A
# B
# A  <- A가 두 번 호출됨!
# C
# D

# 좋은 예: super() 사용
class B(A):
    def __init__(self):
        super().__init__()  # MRO를 따름
        print("B")
```

### 실수 4: 리스코프 치환 원칙 위반

```python
# 나쁜 예
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def set_width(self, width):
        self.width = width
    
    def set_height(self, height):
        self.height = height
    
    def area(self):
        return self.width * self.height

class Square(Rectangle):
    def set_width(self, width):
        self.width = width
        self.height = width  # 정사각형은 가로세로 같음
    
    def set_height(self, height):
        self.width = height
        self.height = height

# 문제 발생
def test(rect: Rectangle):
    rect.set_width(5)
    rect.set_height(4)
    assert rect.area() == 20  # Rectangle은 OK, Square는 실패!

# 좋은 예: 별도 클래스로 분리
class Shape:
    def area(self):
        raise NotImplementedError

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

class Square(Shape):
    def __init__(self, side):
        self.side = side
    
    def area(self):
        return self.side ** 2
```

### 실수 5: 순환 import

```python
# animal.py
from dog import Dog  # 순환 import!

class Animal:
    pass

# dog.py
from animal import Animal

class Dog(Animal):
    pass

# 해결: 타입 힌트만 필요하면 TYPE_CHECKING 사용
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dog import Dog

class Animal:
    pass
```

### 실수 6: 가변 기본 인자

```python
# 나쁜 예
class Parent:
    def __init__(self, items=[]):  # 위험!
        self.items = items

class Child(Parent):
    pass

c1 = Child()
c2 = Child()
c1.items.append(1)
print(c2.items)  # [1] - 공유됨!

# 좋은 예
class Parent:
    def __init__(self, items=None):
        self.items = items if items is not None else []
```

### 실수 7: 추상 메서드 미구현

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

# 나쁜 예
class Dog(Animal):
    pass  # speak() 미구현

# dog = Dog()  # TypeError!

# 좋은 예
class Dog(Animal):
    def speak(self):  # 반드시 구현
        return "멍멍"
```

### 실수 8: 부모 속성 덮어쓰기

```python
# 나쁜 예
class Parent:
    important_value = 100

class Child(Parent):
    important_value = 0  # 부모 속성 덮어씀

# 좋은 예: 다른 이름 사용
class Child(Parent):
    child_value = 0
```

---

## 요약

| 개념 | 설명 | 예시 |
|------|------|------|
| 상속 | 부모 클래스 기능 물려받기 | `class Dog(Animal):` |
| `super()` | 부모 클래스 메서드 호출 | `super().__init__()` |
| 오버라이딩 | 부모 메서드 재정의 | `def speak(self):` |
| 다중 상속 | 여러 부모로부터 상속 | `class Duck(Flyable, Swimmable):` |
| MRO | 메서드 탐색 순서 | `Class.__mro__` |
| 추상 클래스 | 인스턴스화 불가, 구현 강제 | `ABC`, `@abstractmethod` |

**핵심 포인트:**
- 상속은 is-a 관계일 때 사용
- `super()`로 부모 메서드 호출
- 다중 상속 시 MRO 이해 필요
- 추상 클래스로 인터페이스 정의
- 깊은 상속보다 컴포지션 고려

**관련 문서:**
- [클래스 튜토리얼](./python_class.md) - 클래스 기초
- [클래스 구성 요소](./python_class_components.md) - 메서드, 프로퍼티

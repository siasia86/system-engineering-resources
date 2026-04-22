# Python 패키지 (Packages)

Python에서 모듈을 구조화하고 재사용 가능한 패키지를 만드는 실용 가이드입니다.

## 목차
- [패키지란?](#패키지란)
- [패키지 구조](#패키지-구조)
- [__init__.py](#__init__py)
- [import 방법](#import-방법)
- [절대 import](#절대-import)
- [상대 import](#상대-import)
- [__all__ 변수](#__all__-변수)
- [실전 예제](#실전-예제)
- [실전 팁](#실전-팁)
- [자주하는 실수](#자주하는-실수)
- [요약](#요약)

---

## 패키지란?

모듈들을 디렉토리로 구조화한 것입니다.

### 왜 사용하나?

- **코드 구조화**: 관련 모듈을 그룹화
- **네임스페이스 관리**: 이름 충돌 방지
- **재사용성**: 다른 프로젝트에서 사용
- **유지보수**: 코드 관리 용이

### 모듈 vs 패키지

```python
# 모듈: 단일 .py 파일
math_utils.py

# 패키지: 디렉토리 + __init__.py
mypackage/
    __init__.py
    module1.py
    module2.py
```

---

## 패키지 구조

### 기본 구조

```
myproject/
    mypackage/
        __init__.py
        module1.py
        module2.py
    main.py
```

### 중첩 패키지

```
myproject/
    mypackage/
        __init__.py
        core/
            __init__.py
            engine.py
            utils.py
        api/
            __init__.py
            client.py
            server.py
    main.py
```

### 실제 프로젝트 구조

```
myproject/
    mypackage/
        __init__.py
        models/
            __init__.py
            user.py
            product.py
        services/
            __init__.py
            auth.py
            payment.py
        utils/
            __init__.py
            helpers.py
            validators.py
    tests/
        test_models.py
        test_services.py
    main.py
    setup.py
    README.md
```

---

## __init__.py

패키지를 정의하는 특수 파일입니다.

### 빈 __init__.py

```python
# mypackage/__init__.py
# 빈 파일도 가능 (Python 3.3+)
```

### 패키지 초기화

```python
# mypackage/__init__.py
print("mypackage 로드됨")

# 패키지 레벨 변수
VERSION = "1.0.0"
```

### 모듈 import

```python
# mypackage/__init__.py
from .module1 import func1
from .module2 import func2

# 이제 직접 접근 가능
# from mypackage import func1
```

### 서브패키지 import

```python
# mypackage/__init__.py
from .core import engine
from .api import client

# from mypackage import engine, client
```

### 편의 함수 제공

```python
# mypackage/__init__.py
from .models.user import User
from .models.product import Product
from .services.auth import login, logout

# 간단한 접근
# from mypackage import User, login
```

---

## import 방법

### 패키지 import

```python
# 패키지 전체
import mypackage

# 모듈 import
import mypackage.module1

# 특정 함수/클래스
from mypackage.module1 import func1
from mypackage.module2 import MyClass
```

### 중첩 패키지 import

```python
# 서브패키지
import mypackage.core.engine

# 서브패키지 모듈
from mypackage.core import engine
from mypackage.api.client import APIClient
```

### 별칭 사용

```python
import mypackage as mp
import mypackage.core.engine as engine
from mypackage.module1 import func1 as f1
```

### 여러 항목 import

```python
from mypackage import (
    func1,
    func2,
    MyClass
)
```

---

## 절대 import

프로젝트 루트부터 전체 경로를 명시합니다.

### 기본 사용

```python
# mypackage/core/engine.py
from mypackage.utils.helpers import format_data
from mypackage.models.user import User
```

### 장점

```python
# 명확한 경로
from mypackage.core.engine import Engine
from mypackage.api.client import APIClient

# 어디서든 동일하게 동작
# 리팩토링 시 안전
```

### 예제

```
myproject/
    mypackage/
        __init__.py
        models/
            __init__.py
            user.py
        services/
            __init__.py
            auth.py
```

```python
# mypackage/services/auth.py
from mypackage.models.user import User  # 절대 import

def authenticate(username, password):
    user = User.find(username)
    return user.check_password(password)
```

---

## 상대 import

현재 모듈 위치를 기준으로 import합니다.

### 기본 문법

```python
# . : 현재 디렉토리
# .. : 상위 디렉토리
# ... : 상위의 상위

from . import module1          # 같은 디렉토리
from .module1 import func1     # 같은 디렉토리
from .. import parent_module   # 상위 디렉토리
from ..sibling import func     # 형제 디렉토리
```

### 예제

```
mypackage/
    __init__.py
    models/
        __init__.py
        user.py
        product.py
    services/
        __init__.py
        auth.py
```

```python
# mypackage/models/product.py
from .user import User  # 같은 디렉토리

class Product:
    def __init__(self, owner_id):
        self.owner = User.find(owner_id)
```

```python
# mypackage/services/auth.py
from ..models.user import User  # 상위 디렉토리의 models

def login(username, password):
    user = User.find(username)
    return user
```

### 상대 import 제약

```python
# 스크립트로 직접 실행 불가
# python mypackage/services/auth.py  # 에러!

# 패키지로 실행해야 함
# python -m mypackage.services.auth
```

---

## __all__ 변수

`from package import *` 시 import할 항목을 지정합니다.

### 기본 사용

```python
# mypackage/__init__.py
__all__ = ['func1', 'func2', 'MyClass']

from .module1 import func1
from .module2 import func2, MyClass
```

```python
# 사용
from mypackage import *  # func1, func2, MyClass만 import
```

### 모듈에서 사용

```python
# mypackage/utils.py
__all__ = ['public_func', 'PublicClass']

def public_func():
    pass

def _private_func():  # import * 시 제외
    pass

class PublicClass:
    pass
```

### 권장 사항

```python
# 나쁜 예
from mypackage import *  # 무엇이 import되는지 불명확

# 좋은 예
from mypackage import func1, func2, MyClass  # 명시적
```

---

## 실전 예제

### 예제 1: 간단한 패키지

```
mathlib/
    __init__.py
    basic.py
    advanced.py
```

```python
# mathlib/basic.py
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
```

```python
# mathlib/advanced.py
def power(base, exp):
    return base ** exp

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

```python
# mathlib/__init__.py
from .basic import add, subtract
from .advanced import power, factorial

__all__ = ['add', 'subtract', 'power', 'factorial']
```

```python
# main.py
from mathlib import add, power

print(add(5, 3))      # 8
print(power(2, 10))   # 1024
```

### 예제 2: 웹 API 패키지

```
webapi/
    __init__.py
    client.py
    auth.py
    exceptions.py
```

```python
# webapi/exceptions.py
class APIError(Exception):
    pass

class AuthError(APIError):
    pass
```

```python
# webapi/auth.py
class Auth:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def get_headers(self):
        return {'Authorization': f'Bearer {self.api_key}'}
```

```python
# webapi/client.py
from .auth import Auth
from .exceptions import APIError

class APIClient:
    def __init__(self, api_key):
        self.auth = Auth(api_key)
    
    def get(self, endpoint):
        headers = self.auth.get_headers()
        # API 호출 로직
        return {'status': 'success'}
```

```python
# webapi/__init__.py
from .client import APIClient
from .exceptions import APIError, AuthError

__version__ = '1.0.0'
__all__ = ['APIClient', 'APIError', 'AuthError']
```

```python
# main.py
from webapi import APIClient

client = APIClient('my-api-key')
result = client.get('/users')
```

### 예제 3: 데이터베이스 패키지

```
database/
    __init__.py
    connection.py
    models/
        __init__.py
        user.py
        product.py
    queries/
        __init__.py
        user_queries.py
```

```python
# database/connection.py
class Database:
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    def connect(self):
        print(f"연결: {self.host}:{self.port}")
```

```python
# database/models/user.py
class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    @classmethod
    def find(cls, id):
        return cls(id, f"User{id}")
```

```python
# database/queries/user_queries.py
from ..models.user import User

def get_user(user_id):
    return User.find(user_id)

def get_all_users():
    return [User.find(i) for i in range(1, 4)]
```

```python
# database/__init__.py
from .connection import Database
from .models.user import User
from .queries.user_queries import get_user, get_all_users

__all__ = ['Database', 'User', 'get_user', 'get_all_users']
```

```python
# main.py
from database import Database, get_user

db = Database('localhost', 5432)
db.connect()

user = get_user(1)
print(user.name)
```

### 예제 4: 유틸리티 패키지

```
utils/
    __init__.py
    string_utils.py
    date_utils.py
    file_utils.py
```

```python
# utils/string_utils.py
def to_snake_case(text):
    return text.lower().replace(' ', '_')

def to_camel_case(text):
    words = text.split('_')
    return words[0] + ''.join(w.capitalize() for w in words[1:])
```

```python
# utils/date_utils.py
from datetime import datetime

def now_str():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')
```

```python
# utils/__init__.py
from .string_utils import to_snake_case, to_camel_case
from .date_utils import now_str, parse_date

__all__ = [
    'to_snake_case',
    'to_camel_case',
    'now_str',
    'parse_date'
]
```

```python
# main.py
from utils import to_snake_case, now_str

print(to_snake_case('Hello World'))  # hello_world
print(now_str())  # 2024-03-11 10:30:45
```

### 예제 5: 플러그인 시스템

```
plugins/
    __init__.py
    base.py
    email_plugin.py
    sms_plugin.py
```

```python
# plugins/base.py
class Plugin:
    def execute(self):
        raise NotImplementedError
```

```python
# plugins/email_plugin.py
from .base import Plugin

class EmailPlugin(Plugin):
    def execute(self):
        return "이메일 전송"
```

```python
# plugins/sms_plugin.py
from .base import Plugin

class SMSPlugin(Plugin):
    def execute(self):
        return "SMS 전송"
```

```python
# plugins/__init__.py
from .base import Plugin
from .email_plugin import EmailPlugin
from .sms_plugin import SMSPlugin

def get_plugin(name):
    plugins = {
        'email': EmailPlugin,
        'sms': SMSPlugin
    }
    return plugins.get(name)()

__all__ = ['Plugin', 'EmailPlugin', 'SMSPlugin', 'get_plugin']
```

```python
# main.py
from plugins import get_plugin

email = get_plugin('email')
print(email.execute())  # 이메일 전송

sms = get_plugin('sms')
print(sms.execute())  # SMS 전송
```

---

## 실전 팁

### Tip 1: 절대 import 우선

```python
# 나쁜 예: 상대 import 남용
from ..models.user import User
from ...utils.helpers import format_data

# 좋은 예: 절대 import
from mypackage.models.user import User
from mypackage.utils.helpers import format_data
```

### Tip 2: __init__.py 간결하게

```python
# 나쁜 예: 복잡한 로직
# mypackage/__init__.py
from .module1 import *
from .module2 import *
# 많은 초기화 코드...

# 좋은 예: 필요한 것만
# mypackage/__init__.py
from .module1 import func1
from .module2 import func2

__all__ = ['func1', 'func2']
```

### Tip 3: 순환 import 방지

```python
# 나쁜 예: 순환 참조
# models/user.py
from .product import Product

# models/product.py
from .user import User  # 순환!

# 좋은 예: 함수 내부에서 import
# models/user.py
class User:
    def get_products(self):
        from .product import Product  # 지연 import
        return Product.find_by_user(self.id)
```

### Tip 4: 명시적 import

```python
# 나쁜 예
from mypackage import *

# 좋은 예
from mypackage import func1, func2, MyClass
```

### Tip 5: 패키지 버전 관리

```python
# mypackage/__init__.py
__version__ = '1.0.0'
__author__ = 'Your Name'

from .core import main_func

__all__ = ['main_func']
```

```python
# 사용
import mypackage
print(mypackage.__version__)  # 1.0.0
```

### Tip 6: 네임스페이스 패키지

```python
# Python 3.3+: __init__.py 없이도 패키지
mypackage/
    module1.py
    module2.py

# import 가능
from mypackage import module1
```

### Tip 7: 패키지 실행

```python
# mypackage/__main__.py
from .core import main

if __name__ == '__main__':
    main()
```

```bash
# 패키지를 스크립트처럼 실행
python -m mypackage
```

### Tip 8: 리소스 파일 포함

```
mypackage/
    __init__.py
    data/
        config.json
        template.txt
```

```python
# mypackage/loader.py
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent / 'data' / 'config.json'
    return config_path.read_text()
```

---

## 자주하는 실수

### 실수 1: __init__.py 누락 (Python 3.2 이하)

```python
# 나쁜 예: Python 3.2 이하
mypackage/
    module1.py  # __init__.py 없음

# 좋은 예
mypackage/
    __init__.py
    module1.py
```

### 실수 2: 순환 import

```python
# 나쁜 예
# a.py
from b import func_b

# b.py
from a import func_a  # 순환!

# 좋은 예: 구조 재설계 또는 지연 import
# a.py
def func_a():
    from b import func_b  # 함수 내부에서
    return func_b()
```

### 실수 3: 상대 import 오용

```python
# 나쁜 예: 스크립트로 실행
# mypackage/module.py
from . import other  # 직접 실행 시 에러

# 좋은 예: 절대 import 또는 패키지로 실행
from mypackage import other
# 또는
python -m mypackage.module
```

### 실수 4: import * 남용

```python
# 나쁜 예
from mypackage import *  # 무엇이 import되는지 불명확

# 좋은 예
from mypackage import func1, func2, MyClass
```

### 실수 5: 패키지명과 모듈명 충돌

```python
# 나쁜 예
mypackage/
    mypackage.py  # 패키지명과 동일!

# 좋은 예
mypackage/
    core.py
    utils.py
```

### 실수 6: 깊은 중첩

```python
# 나쁜 예
from mypackage.sub1.sub2.sub3.sub4.module import func

# 좋은 예: __init__.py에서 단축
# mypackage/__init__.py
from .sub1.sub2.sub3.sub4.module import func

# 사용
from mypackage import func
```

### 실수 7: __all__ 불일치

```python
# 나쁜 예
# mypackage/__init__.py
__all__ = ['func1', 'func2']

from .module import func1
# func2는 import 안함!

# 좋은 예
__all__ = ['func1', 'func2']

from .module import func1, func2
```

---

## 요약

| 개념          | 설명            | 예제                                |
|---------------|-----------------|-------------------------------------|
| 패키지        | 모듈의 디렉토리 | `mypackage/`                        |
| `__init__.py` | 패키지 정의     | 초기화 코드                         |
| 절대 import   | 전체 경로       | `from mypackage.module import func` |
| 상대 import   | 상대 경로       | `from .module import func`          |
| `__all__`     | export 목록     | `__all__ = ['func1']`               |

**핵심 포인트:**
- 절대 import 우선 사용
- `__init__.py`로 패키지 정의
- 순환 import 방지
- 명시적 import 사용
- 패키지 구조 단순하게

**관련 문서:**
- [함수](./python_functions.md) - 모듈화의 기본
- [클래스](./python_class.md) - 패키지 내 클래스 구조
- [예외 처리](./python_exceptions.md) - import 에러 처리

# Python JSON/YAML 처리

설정 파일과 데이터 교환을 위한 JSON/YAML 처리 가이드입니다.

## 목차
- [JSON](#json)
- [YAML](#yaml)
- [실전 예제](#실전-예제)
- [요약](#요약)

---

## JSON

### 기본 사용법

```python
import json

# Python 객체 → JSON 문자열
data = {'name': '홍길동', 'age': 30, 'skills': ['Python', 'Linux']}
json_str = json.dumps(data, ensure_ascii=False, indent=2)
print(json_str)
# {
#   "name": "홍길동",
#   "age": 30,
#   "skills": ["Python", "Linux"]
# }

# JSON 문자열 → Python 객체
parsed = json.loads(json_str)
print(parsed['name'])  # '홍길동'
```

### 파일 읽기/쓰기

```python
# 쓰기
with open('config.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 읽기
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
```

### 주요 옵션

```python
json.dumps(data,
    ensure_ascii=False,   # 한글 그대로 출력
    indent=2,             # 들여쓰기
    sort_keys=True,       # 키 정렬
    default=str,          # 직렬화 불가 객체 처리 (datetime 등)
    separators=(',', ':') # 구분자 (압축 시)
)
```

### 타입 매핑

| Python | JSON |
|--------|------|
| dict | object |
| list, tuple | array |
| str | string |
| int, float | number |
| True/False | true/false |
| None | null |

---

## YAML

### 설치

```bash
pip install pyyaml
```

### 기본 사용법

```python
import yaml

# YAML 문자열 → Python 객체
yaml_str = """
server:
  host: 0.0.0.0
  port: 8080
  debug: false
database:
  host: localhost
  port: 5432
  name: mydb
"""

config = yaml.safe_load(yaml_str)
print(config['server']['port'])  # 8080

# Python 객체 → YAML 문자열
output = yaml.dump(config, default_flow_style=False, allow_unicode=True)
print(output)
```

### 파일 읽기/쓰기

```python
# 읽기
with open('config.yml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 쓰기
with open('config.yml', 'w', encoding='utf-8') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
```

### 여러 문서 처리

```python
# YAML 파일에 --- 구분자로 여러 문서가 있을 때
with open('multi.yml', 'r') as f:
    docs = list(yaml.safe_load_all(f))
    for doc in docs:
        print(doc)
```

### ⚠️ 보안 주의

```python
# yaml.load()는 임의 코드 실행 위험
# 반드시 yaml.safe_load() 사용
config = yaml.safe_load(yaml_str)    # ✅ 안전
# config = yaml.load(yaml_str)       # ❌ 위험
```

---

## 실전 예제

### 설정 파일 관리

```python
from pathlib import Path
import json

class Config:
    def __init__(self, path):
        self.path = Path(path)
        self.data = {}
        self.load()

    def load(self):
        if self.path.exists():
            with open(self.path, 'r', encoding='utf-8') as f:
                if self.path.suffix == '.json':
                    self.data = json.load(f)
                elif self.path.suffix in ('.yml', '.yaml'):
                    import yaml
                    self.data = yaml.safe_load(f) or {}

    def get(self, key, default=None):
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

# 사용
config = Config('config.yml')
db_host = config.get('database.host', 'localhost')
```

### JSON 로그 파싱

```python
def parse_json_logs(log_file):
    errors = []
    with open(log_file) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get('level') == 'ERROR':
                    errors.append(entry)
            except json.JSONDecodeError:
                continue
    return errors
```

### API 응답 처리

```python
import json
from urllib.request import urlopen

def fetch_api(url):
    with urlopen(url) as response:
        data = json.loads(response.read().decode('utf-8'))
    return data
```

### datetime 직렬화

```python
from datetime import datetime
import json

# datetime은 기본 직렬화 불가
data = {'timestamp': datetime.now(), 'value': 42}

# default 함수로 처리
def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"직렬화 불가: {type(obj)}")

result = json.dumps(data, default=json_serial, ensure_ascii=False)
print(result)  # {"timestamp": "2026-04-20T10:30:45.123456", "value": 42}
```

### 환경별 설정 오버라이드

```python
import yaml
from pathlib import Path

def load_config(env='dev'):
    base = yaml.safe_load(Path('config.yml').read_text())
    env_file = Path(f'config.{env}.yml')
    if env_file.exists():
        override = yaml.safe_load(env_file.read_text()) or {}
        base.update(override)
    return base

config = load_config('prd')
```

---

## 요약

| 항목 | JSON | YAML |
|------|------|------|
| 모듈 | `json` (내장) | `pyyaml` (설치 필요) |
| 읽기 | `json.load()` / `loads()` | `yaml.safe_load()` |
| 쓰기 | `json.dump()` / `dumps()` | `yaml.dump()` |
| 용도 | API, 데이터 교환 | 설정 파일 |
| 주석 | ❌ 불가 | ✅ 가능 (`#`) |
| 가독성 | 보통 | 좋음 |

**관련 문서:**
- [파일 입출력](./python_file_io.md) - 파일 처리
- [파일/디렉토리 조작](./python_os_pathlib.md) - 경로 처리
- [예외 처리](./python_exceptions.md) - 에러 핸들링

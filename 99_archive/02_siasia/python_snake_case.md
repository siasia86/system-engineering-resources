# Python Snake Case 명명 규칙

## 적용 범위
- 파일 타입: `*.py`
- 모든 Python 파일

## 규칙 내용

### 변수명과 함수명은 snake_case를 사용해야 합니다

**올바른 예시:**
```python
user_name = "홍길동"
file_path = "/home/user/data.txt"
max_retry_count = 3

def get_user_info():
    pass

def calculate_total_price():
    pass

def send_email_notification():
    pass
```

**잘못된 예시:**
```python
userName = "홍길동"          # camelCase 사용 금지
filePath = "/home/user/data.txt"  # camelCase 사용 금지
MaxRetryCount = 3            # PascalCase 사용 금지

def getUserInfo():           # camelCase 사용 금지
    pass

def CalculateTotalPrice():   # PascalCase 사용 금지
    pass
```

### 예외 사항
- 클래스명은 PascalCase 사용: `UserManager`, `DataProcessor`
- 상수는 UPPER_SNAKE_CASE 사용: `MAX_SIZE`, `DEFAULT_TIMEOUT`

### 이유
- Python PEP 8 표준 준수
- 코드 가독성 향상
- 팀 내 일관성 유지
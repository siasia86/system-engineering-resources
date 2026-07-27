# Bash Shell 명명 규칙

## 적용 범위
- 파일 타입: `*.sh`, `*.bash`
- 모든 Bash 스크립트 파일

## 규칙 내용

### 변수명 규칙

**지역변수는 lowercase 또는 snake_case 사용:**
```bash
# 올바른 예시
user_name="홍길동"
file_path="/home/user/data.txt"
temp_dir="/tmp"
count=0

# 함수 내 지역변수
function process_data() {
    local input_file="$1"
    local output_dir="/output"
}
```

**상수와 환경변수는 UPPER_CASE 사용:**
```bash
# 올바른 예시
readonly MAX_RETRY=3
readonly SCRIPT_DIR="/opt/scripts"
export PATH="/usr/local/bin:$PATH"
declare -r CONFIG_FILE="/etc/app.conf"
```

### 함수명 규칙

**함수명은 snake_case 사용:**
```bash
# 올바른 예시
get_user_info() {
    echo "Getting user info"
}

backup_database() {
    local db_name="$1"
    mysqldump "$db_name" > "/backup/${db_name}.sql"
}

calculate_total_size() {
    du -sh "$1" | cut -f1
}
```

### 잘못된 예시
```bash
# camelCase 사용 금지
userName="test"              # 변수명
getUserInfo() { }            # 함수명

# PascalCase 사용 금지  
UserName="test"              # 변수명
GetUserInfo() { }            # 함수명

# 혼합 사용 금지
User_Name="test"             # 일관성 없음
get_UserInfo() { }           # 일관성 없음
```

### 특별 규칙
- **스크립트 파일명**: `backup_db.sh`, `user_manager.sh`
- **임시 변수**: `tmp_file`, `temp_dir`
- **루프 변수**: `i`, `j`, `item` (짧은 이름 허용)

### 이유
- Google Shell Style Guide 준수
- 코드 가독성 향상
- POSIX 호환성 유지
- 팀 내 일관성 보장
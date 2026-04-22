# 프로그래밍 언어 비교

## 언어별 특징 요약

| 언어       | 타입           | 실행 방식               | 메모리 관리        | 주요 용도               |
|------------|----------------|-------------------------|--------------------|-------------------------|
| **C**      | 정적, 컴파일   | AOT → 네이티브          | 수동 (malloc/free) | OS, 임베디드, 시스템    |
| **C++**    | 정적, 컴파일   | AOT → 네이티브          | 수동 (RAII)        | 게임, 시스템, 고성능    |
| **C#**     | 정적, 컴파일   | JIT (CIL)               | GC                 | 엔터프라이즈, Unity, 웹 |
| **Go**     | 정적, 컴파일   | AOT → 네이티브          | GC                 | 백엔드, 클라우드, CLI   |
| **Python** | 동적, 스크립트 | 바이트코드 + 인터프리터 | GC                 | 데이터, ML, 자동화      |
| **Bash**   | 동적, 스크립트 | 인터프리터              | 자동               | 시스템 관리, 자동화     |

---

## 1. C

### 특징
- **최소주의**: 작고 단순한 언어 (키워드 32개)
- **하드웨어 직접 제어**: 포인터, 메모리 주소 직접 조작
- **이식성**: "Write once, compile anywhere"
- **시스템 프로그래밍의 표준**: 대부분의 OS가 C로 작성됨

### 실행 방식
```
C 소스 (.c) → 전처리기 → 컴파일러 (gcc, clang) → 어셈블리 → 링커 → 네이티브 바이너리
```

### 코드 예시
```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    int numbers[] = {1, 2, 3, 4, 5};
    int size = sizeof(numbers) / sizeof(numbers[0]);
    
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += numbers[i];
    }
    
    printf("Sum: %d\n", sum);
    return 0;
}
```

### 메모리 관리 예시
```c
#include <stdlib.h>
#include <string.h>

// 동적 메모리 할당
int* create_array(int size) {
    int* arr = (int*)malloc(size * sizeof(int));
    if (arr == NULL) {
        return NULL;  // 할당 실패
    }
    memset(arr, 0, size * sizeof(int));
    return arr;
}

int main() {
    int* data = create_array(100);
    
    // 사용
    data[0] = 42;
    
    // 반드시 해제
    free(data);
    
    return 0;
}
```

### 포인터 예시
```c
void swap(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int main() {
    int x = 10, y = 20;
    swap(&x, &y);  // x=20, y=10
    return 0;
}
```

### C의 독특한 특징

**1. 전처리기 (Preprocessor)**
```c
#define MAX_SIZE 100
#define MIN(a, b) ((a) < (b) ? (a) : (b))

#ifdef DEBUG
    printf("Debug mode\n");
#endif
```

**2. 구조체 (Struct)**
```c
typedef struct {
    char name[50];
    int age;
} Person;

Person p = {"Alice", 30};
```

**3. 함수 포인터**
```c
int add(int a, int b) { return a + b; }
int (*operation)(int, int) = add;
int result = operation(5, 3);  // 8
```

**4. 헤더 파일 시스템**
```c
// math.h
int add(int a, int b);

// math.c
int add(int a, int b) {
    return a + b;
}

// main.c
#include "math.h"
```

### 사용 사례
- 운영체제 (Linux, Windows 커널)
- 임베디드 시스템, 펌웨어
- 디바이스 드라이버
- 컴파일러, 인터프리터 (Python CPython, Ruby MRI)
- 데이터베이스 (PostgreSQL, SQLite)
- 네트워크 프로토콜 스택
- 고성능 라이브러리 (OpenSSL, zlib)

### 장단점
**장점:**
- 최고 성능과 최소 오버헤드
- 완전한 하드웨어 제어
- 작은 바이너리 크기
- 모든 플랫폼 지원
- 오래된 안정적인 생태계
- 다른 언어와 쉬운 연동 (FFI)
- 예측 가능한 동작

**단점:**
- 메모리 안전성 없음 (버퍼 오버플로우, 댕글링 포인터)
- 수동 메모리 관리 (메모리 누수 위험)
- 문자열 처리 불편
- 표준 라이브러리 빈약
- 긴 개발 시간
- 디버깅 어려움
- 현대적 기능 부족 (클래스, 예외 처리 등)

### C vs C++

| 특징          | C                | C++                        |
|---------------|------------------|----------------------------|
| 패러다임      | 절차적           | 절차적 + 객체지향 + 제네릭 |
| 복잡도        | 단순             | 복잡                       |
| 컴파일 속도   | 빠름             | 느림                       |
| 바이너리 크기 | 작음             | 큼                         |
| 사용처        | 시스템, 임베디드 | 게임, 애플리케이션         |

---

## 2. C++

## 2. C++

### 특징
- **최고 성능**: 네이티브 기계어, 제로 오버헤드
- **완전한 제어**: 메모리, CPU 직접 제어
- **멀티 패러다임**: 절차적, 객체지향, 제네릭, 함수형
- **복잡성**: 수동 메모리 관리, 긴 컴파일 시간

### 실행 방식
```
C++ 소스 (.cpp) → 컴파일러 (g++, clang++) → 네이티브 바이너리 → CPU 직접 실행
```

### 코드 예시
```cpp
#include <iostream>
#include <vector>

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    
    int sum = 0;
    for (int n : numbers) {
        sum += n;
    }
    
    std::cout << "Sum: " << sum << std::endl;
    return 0;
}
```

### 사용 사례
- 게임 엔진 (Unreal Engine)
- 운영체제, 디바이스 드라이버
- 임베디드 시스템
- 고빈도 거래 시스템
- 브라우저 엔진 (Chrome, Firefox)

### 장단점
**장점:**
- 최고 성능과 효율성
- 하드웨어 직접 제어
- 방대한 레거시 라이브러리

**단점:**
- 개발 속도 느림
- 메모리 안전성 문제 (segfault, 메모리 누수)
- 복잡한 문법과 빌드 시스템

---

## 2. C#

### 특징
- **생산성 + 성능**: 현대적 문법, JIT 최적화
- **안전성**: 메모리 안전, 타입 안전
- **생태계**: .NET 플랫폼, 풍부한 라이브러리

### 실행 방식
```
C# 소스 (.cs) → 컴파일러 (Roslyn) → CIL 바이트코드 (.dll) 
→ .NET Runtime → JIT 컴파일 → 네이티브 기계어 → 실행
```

### 코드 예시
```csharp
using System;
using System.Linq;

class Program 
{
    static void Main() 
    {
        var numbers = new[] { 1, 2, 3, 4, 5 };
        
        int sum = numbers.Sum();
        
        Console.WriteLine($"Sum: {sum}");
    }
}
```

### 사용 사례
- 엔터프라이즈 애플리케이션
- 웹 서비스 (ASP.NET Core)
- 게임 개발 (Unity)
- 데스크톱 앱 (WPF, WinForms, MAUI)
- 클라우드 서비스 (Azure)

### 장단점
**장점:**
- 빠른 개발 속도
- 우수한 성능 (C++의 80-95%)
- 강력한 IDE 지원 (Visual Studio)
- 크로스 플랫폼 (.NET Core/5+)

**단점:**
- 런타임 필요 (.NET)
- GC 일시 정지 (pause)
- C++보다는 느림
- 주로 Microsoft 생태계

---

## 3. Go

### 특징
- **단순함**: 최소한의 문법, 빠른 학습 (키워드 25개)
- **동시성**: 고루틴으로 쉬운 병렬 처리
- **빠른 컴파일**: 대규모 프로젝트도 초 단위 빌드
- **정적 링킹**: 단일 바이너리에 모든 의존성 포함

### 실행 방식
```
Go 소스 (.go) → 컴파일러 (go build) → 네이티브 바이너리 (단일 파일) → 실행
```

### 코드 예시
```go
package main

import "fmt"

func main() {
    numbers := []int{1, 2, 3, 4, 5}
    
    sum := 0
    for _, n := range numbers {
        sum += n
    }
    
    fmt.Printf("Sum: %d\n", sum)
}
```

### 고루틴 예시 (동시성)
```go
package main

import (
    "fmt"
    "time"
)

func worker(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        fmt.Printf("Worker %d processing job %d\n", id, j)
        time.Sleep(time.Second)
        results <- j * 2
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)
    
    // 3개의 워커 고루틴 시작
    for w := 1; w <= 3; w++ {
        go worker(w, jobs, results)
    }
    
    // 5개 작업 전송
    for j := 1; j <= 5; j++ {
        jobs <- j
    }
    close(jobs)
    
    // 결과 수집
    for a := 1; a <= 5; a++ {
        <-results
    }
}
```

### Go의 독특한 특징

**1. 고루틴 (Goroutine)**
- 경량 스레드 (2KB 스택으로 시작)
- 수천~수만 개 동시 실행 가능
- OS 스레드보다 훨씬 가벼움

**2. 채널 (Channel)**
- 고루틴 간 안전한 통신
- "메모리를 공유하지 말고, 통신으로 공유하라"

**3. 인터페이스**
- 암묵적 구현 (명시적 선언 불필요)
- 덕 타이핑과 유사하지만 컴파일 타임 체크

**4. defer 문**
```go
func readFile() {
    f, _ := os.Open("file.txt")
    defer f.Close()  // 함수 종료 시 자동 실행
    // 파일 작업
}
```

**5. 에러 처리**
```go
result, err := someFunction()
if err != nil {
    return err  // 명시적 에러 처리
}
```

**6. 크로스 컴파일**
```bash
# Linux에서 Windows용 빌드
GOOS=windows GOARCH=amd64 go build

# Mac에서 Linux용 빌드
GOOS=linux GOARCH=amd64 go build
```

### 사용 사례
- 백엔드 서비스, API 서버
- 클라우드 인프라 (Docker, Kubernetes, Terraform)
- CLI 도구 (kubectl, hugo, gh)
- 마이크로서비스
- 네트워크 프로그래밍
- 실시간 데이터 처리

### 장단점
**장점:**
- 매우 빠른 컴파일 (수백만 줄도 초 단위)
- 단순하고 읽기 쉬운 코드
- 우수한 동시성 지원 (고루틴)
- 단일 바이너리 배포 (의존성 없음)
- 강력한 표준 라이브러리
- 빠른 실행 속도 (C++에 근접)
- 내장 포맷터 (gofmt), 테스트 도구
- 뛰어난 크로스 컴파일

**단점:**
- 제네릭 지원 늦음 (Go 1.18+에서 추가)
- 에러 처리가 장황함 (`if err != nil` 반복)
- 객체지향 기능 제한적 (상속 없음)
- GC로 인한 지연 (C++보다 느림)
- 예외(exception) 없음
- 패키지 관리 초기에 혼란 (현재는 go modules로 해결)

---

## 4. Python

### 특징
- **생산성 최우선**: 간결한 문법, 빠른 프로토타이핑
- **방대한 생태계**: 라이브러리가 거의 모든 분야 커버
- **동적 타입**: 유연하지만 런타임 에러 가능

### 실행 방식
```
Python 소스 (.py) → CPython 인터프리터 → 바이트코드 (.pyc) 
→ Python VM이 바이트코드 해석 실행
```

### 코드 예시
```python
numbers = [1, 2, 3, 4, 5]

total = sum(numbers)

print(f"Sum: {total}")
```

### Python 컴파일 방법

**1. 기본 바이트코드 컴파일 (자동)**
```bash
# 실행 시 자동으로 .pyc 생성
python script.py

# __pycache__ 디렉토리에 바이트코드 저장됨
# script.cpython-311.pyc
```

**2. 수동 바이트코드 컴파일**
```bash
# 단일 파일
python -m py_compile script.py

# 디렉토리 전체
python -m compileall .
```

**3. 실행 파일로 패키징**

**PyInstaller** (가장 많이 사용)
```bash
pip install pyinstaller

# 단일 실행 파일 생성
pyinstaller --onefile script.py

# dist/script.exe (Windows) 또는 dist/script (Linux/Mac) 생성
```

**Nuitka** (진짜 컴파일 - C로 변환)
```bash
pip install nuitka

# C 코드로 변환 후 네이티브 바이너리 생성
nuitka --onefile script.py

# 성능 향상 (2-3배 빠름)
```

**cx_Freeze**
```bash
pip install cx_Freeze

# setup.py 작성 후
python setup.py build
```

**4. Cython (성능 최적화)**
```bash
pip install cython

# .py → .c → .so (공유 라이브러리)
cython script.py --embed
gcc -O3 script.c -o script $(python3-config --includes --ldflags)
```

**5. PyPy (JIT 컴파일러)**
```bash
# CPython 대신 PyPy 사용
pypy3 script.py

# 장시간 실행 프로그램은 5-10배 빠름
```

### 컴파일 방법 비교

| 방법            | 속도 향상 | 배포 편의성 | 용도               |
|-----------------|-----------|-------------|--------------------|
| **바이트코드**  | 없음      | 낮음        | 기본               |
| **PyInstaller** | 없음      | 높음        | 배포용 실행 파일   |
| **Nuitka**      | 2-3배     | 높음        | 성능 + 배포        |
| **Cython**      | 10-100배  | 중간        | 성능 critical 부분 |
| **PyPy**        | 5-10배    | 낮음        | 장시간 실행        |

### 실제 사용 예시

**PyInstaller로 배포**
```bash
# 개발
python app.py

# 배포용 빌드
pyinstaller --onefile --windowed app.py

# 생성된 실행 파일 배포
# Windows: dist/app.exe
# Linux: dist/app
```

**Cython으로 성능 최적화**
```python
# compute.pyx (Cython 파일)
def calculate(int n):
    cdef int i, sum = 0
    for i in range(n):
        sum += i
    return sum
```

```bash
# 컴파일
cython compute.pyx
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing \
    -I/usr/include/python3.11 -o compute.so compute.c
```

```python
# Python에서 사용
import compute
result = compute.calculate(1000000)  # C 속도로 실행
```

### 사용 사례
- 데이터 분석, 머신러닝 (NumPy, Pandas, TensorFlow)
- 웹 개발 (Django, Flask, FastAPI)
- 자동화 스크립트
- 과학 계산
- DevOps, 시스템 관리
- API 백엔드

### 장단점
**장점:**
- 가장 빠른 개발 속도
- 읽기 쉬운 코드
- 엄청난 라이브러리 생태계
- 초보자 친화적
- 다양한 분야 활용
- REPL로 즉시 테스트 가능

**단점:**
- 매우 느린 실행 속도 (C++의 10-100배 느림)
- GIL로 인한 멀티스레딩 제약
- 런타임 타입 에러
- 메모리 사용량 많음
- 배포 복잡 (의존성 관리)
- 모바일 앱 개발 어려움

---

## 6. Bash

### 특징
- **시스템 자동화**: 파일, 프로세스, 명령어 조합
- **즉시 실행**: 컴파일 없이 바로 실행
- **유닉스 철학**: 작은 도구들을 파이프로 연결
- **텍스트 처리**: sed, awk, grep 등과 강력한 조합

### 실행 방식
```
Bash 스크립트 (.sh) → Bash 인터프리터 → 명령어 실행
```

### 코드 예시
```bash
#!/bin/bash

numbers=(1 2 3 4 5)

sum=0
for n in "${numbers[@]}"; do
    sum=$((sum + n))
done

echo "Sum: $sum"
```

### 실용적인 Bash 팁

**1. 에러 처리**
```bash
#!/bin/bash
set -euo pipefail  # 에러 시 즉시 종료, 미정의 변수 에러, 파이프 에러 감지

# 에러 핸들러
trap 'echo "Error on line $LINENO"' ERR

# 함수에서 에러 체크
if ! command_that_might_fail; then
    echo "Command failed"
    exit 1
fi
```

**2. 함수 사용**
```bash
#!/bin/bash

# 함수 정의
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

check_file() {
    local file=$1
    if [[ -f "$file" ]]; then
        log "File exists: $file"
        return 0
    else
        log "File not found: $file"
        return 1
    fi
}

# 사용
log "Starting script"
check_file "/etc/hosts"
```

**3. 배열 활용**
```bash
#!/bin/bash

# 배열 선언
servers=("web1" "web2" "db1")

# 순회
for server in "${servers[@]}"; do
    echo "Connecting to $server"
    ssh "$server" "uptime"
done

# 배열 길이
echo "Total servers: ${#servers[@]}"

# 특정 인덱스
echo "First server: ${servers[0]}"
```

**4. 문자열 처리**
```bash
#!/bin/bash

filename="document.txt"

# 확장자 제거
echo "${filename%.txt}"        # document

# 경로에서 파일명 추출
path="/home/user/file.txt"
echo "${path##*/}"             # file.txt

# 문자열 치환
text="hello world"
echo "${text/world/bash}"      # hello bash

# 대소문자 변환
echo "${text^^}"               # HELLO WORLD
echo "${text,,}"               # hello world
```

**5. 조건문 팁**
```bash
#!/bin/bash

# 파일 체크
[[ -f file.txt ]] && echo "File exists"
[[ -d /tmp ]] && echo "Directory exists"
[[ -x script.sh ]] && echo "Executable"

# 문자열 체크
[[ -z "$var" ]] && echo "Empty"
[[ -n "$var" ]] && echo "Not empty"

# 숫자 비교
[[ $count -gt 10 ]] && echo "Greater than 10"

# 정규식 매칭
[[ "test123" =~ ^test[0-9]+$ ]] && echo "Matched"
```

**6. 파이프와 리다이렉션**
```bash
#!/bin/bash

# 표준 출력 리다이렉션
echo "log" > file.txt          # 덮어쓰기
echo "log" >> file.txt         # 추가

# 표준 에러 리다이렉션
command 2> error.log           # 에러만
command &> all.log             # 출력 + 에러

# 파이프 체인
cat file.txt | grep "error" | wc -l

# 프로세스 치환
diff <(ls dir1) <(ls dir2)
```

**7. 병렬 실행**
```bash
#!/bin/bash

# 백그라운드 실행
task1 &
task2 &
task3 &

# 모든 작업 완료 대기
wait

echo "All tasks completed"

# xargs로 병렬 실행
cat urls.txt | xargs -P 4 -I {} curl -O {}
```

**8. 명령어 치환과 산술 연산**
```bash
#!/bin/bash

# 명령어 치환
current_date=$(date +%Y-%m-%d)
file_count=$(ls | wc -l)

# 산술 연산
count=10
count=$((count + 1))
result=$((5 * 3 + 2))

# 부동소수점 (bc 사용)
result=$(echo "scale=2; 10 / 3" | bc)
```

**9. 디버깅**
```bash
#!/bin/bash

# 디버그 모드
set -x  # 실행되는 명령어 출력
set +x  # 디버그 모드 종료

# 조건부 디버깅
DEBUG=1
[[ $DEBUG -eq 1 ]] && set -x

# 함수 트레이싱
trap 'echo "Executing: $BASH_COMMAND"' DEBUG
```

**10. 실용 스크립트 템플릿**
```bash
#!/bin/bash
set -euo pipefail

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'  # No Color

# 로깅 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

# 사용법 출력
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    -h, --help      Show this help
    -v, --verbose   Verbose mode
    -f, --file      Input file
EOF
    exit 1
}

# 인자 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -f|--file)
            INPUT_FILE="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            ;;
    esac
done

# 메인 로직
main() {
    log_info "Starting script"
    
    # 작업 수행
    
    log_info "Script completed"
}

main "$@"
```

**11. 유용한 원라이너**
```bash
# 디렉토리 크기 정렬
du -sh */ | sort -h

# 가장 큰 파일 10개
find . -type f -exec du -h {} + | sort -rh | head -10

# 프로세스 모니터링
watch -n 1 'ps aux | grep python'

# 파일 백업
cp file.txt{,.bak}  # file.txt -> file.txt.bak

# 여러 파일 일괄 이름 변경
for f in *.txt; do mv "$f" "${f%.txt}.md"; done

# JSON 파싱 (jq 사용)
curl -s api.example.com | jq '.data[] | .name'

# 로그 실시간 모니터링
tail -f /var/log/app.log | grep --line-buffered ERROR
```

### 사용 사례
- 시스템 관리 스크립트
- CI/CD 파이프라인
- 배포 자동화
- 파일 처리, 백업
- 개발 환경 설정
- 로그 분석
- 크론 작업

### 장단점
**장점:**
- 시스템 명령어 직접 실행
- 파이프, 리다이렉션으로 강력한 조합
- 모든 유닉스 시스템에 기본 설치
- 빠른 프로토타이핑
- 텍스트 처리 강력
- 다른 언어 스크립트 실행 가능

**단점:**
- 복잡한 로직 작성 어려움
- 에러 처리 취약
- 이식성 문제 (bash vs sh vs zsh)
- 디버깅 어려움
- 대규모 프로젝트 부적합
- 성능 느림 (반복문)
- 타입 안전성 없음

---

## 성능 비교

### 벤치마크 (동일 작업 기준)

```
작업: 1억 번 루프 + 정수 연산

C:          0.08초  ███
C++:        0.10초  ████
Go:         0.30초  ████████████
C#:         0.50초  ████████████████████
Python:     5.00초  ████████████████████████████████████████████████████
Bash:      50.00초  (측정 불가)
```

### 메모리 사용량

```
Hello World 프로그램 메모리 사용

C:          0.5 MB
C++:        1.5 MB
Go:         2.0 MB
C#:        30.0 MB (.NET Runtime)
Python:    10.0 MB (인터프리터)
Bash:       5.0 MB
```

---

## 언어 선택 가이드

### 성능이 최우선
→ **C** (OS, 임베디드, 드라이버)  
→ **C++** (게임, HFT, 고성능 컴퓨팅)

### 성능 + 생산성 균형
→ **Go** (백엔드, 클라우드, 마이크로서비스)  
→ **C#** (엔터프라이즈, Unity, 데스크톱)

### 빠른 개발, 프로토타입
→ **Python** (데이터, ML, 스크립트)

### 시스템 자동화
→ **Bash** (DevOps, 배포, 시스템 관리)

### 프로젝트별 추천

| 프로젝트 유형 | 1순위     | 2순위      |
|---------------|-----------|------------|
| 운영체제      | C         | C++        |
| 게임 엔진     | C++       | C# (Unity) |
| 웹 API        | Go        | C#         |
| 데이터 분석   | Python    | -          |
| 모바일 앱     | C# (MAUI) | -          |
| CLI 도구      | Go        | Bash       |
| 머신러닝      | Python    | -          |
| 임베디드      | C         | C++        |
| 배포 스크립트 | Bash      | Python     |
| 컴파일러      | C         | C++        |

---

## 실행 방식 상세 비교

### AOT (Ahead-of-Time) Compilation
**언어:** C, C++, Go

```
장점:
- 최고 성능
- 예측 가능한 실행 시간
- 런타임 불필요

단점:
- 플랫폼별 빌드 필요
- 컴파일 시간 소요
```

### JIT (Just-in-Time) Compilation
**언어:** C#, Java

```
장점:
- 플랫폼 독립적
- 런타임 최적화 가능
- 동적 기능 지원

단점:
- 워밍업 시간
- 런타임 오버헤드
- 메모리 사용량 증가
```

### 인터프리터
**언어:** Python, Bash

```
장점:
- 즉시 실행
- 동적 타입
- 빠른 개발

단점:
- 느린 실행 속도
- 런타임 에러
- 배포 복잡
```

---

## 메모리 관리 비교

### 수동 관리 (C, C++)
```c
int* ptr = malloc(sizeof(int));  // C: malloc
*ptr = 42;
free(ptr);                       // 해제 (필수!)

// C++
int* ptr2 = new int(42);         // C++: new
delete ptr2;                     // 해제 (필수!)
```
- 완전한 제어, 최고 성능
- 실수하면 메모리 누수/크래시

### Garbage Collection (C#, Go, Python)
```csharp
var obj = new MyClass();  // 할당
// 사용
// GC가 자동으로 해제
```
- 편리하고 안전
- 예측 불가능한 일시 정지

### 자동 (Bash)
```bash
var="hello"  # 자동 할당
# 자동 해제
```
- 신경 쓸 필요 없음
- 제어 불가

---

## 동시성/병렬성

### C, C++
```cpp
#include <thread>

std::thread t1([]{ /* 작업 */ });
std::thread t2([]{ /* 작업 */ });
t1.join();
t2.join();
```
- 완전한 제어, 복잡함
- C는 pthread 라이브러리 사용

### C#
```csharp
await Task.WhenAll(
    Task.Run(() => { /* 작업 */ }),
    Task.Run(() => { /* 작업 */ })
);
```
- async/await로 편리함

### Go
```go
go func() { /* 작업 */ }()
go func() { /* 작업 */ }()
```
- 가장 간단하고 강력함

### Python
```python
import threading

t1 = threading.Thread(target=lambda: None)
t2 = threading.Thread(target=lambda: None)
t1.start(); t2.start()
t1.join(); t2.join()
```
- GIL로 인해 진정한 병렬 처리 불가

### Bash
```bash
command1 &
command2 &
wait
```
- 프로세스 레벨 병렬만 가능

---

## 타입 시스템

### 정적 타입 (C, C++, C#, Go)
```go
var count int = 42        // 컴파일 타임에 타입 확정
count = "hello"           // 컴파일 에러!
```
- 컴파일 시 에러 발견
- IDE 자동완성 우수
- 리팩토링 안전

### 동적 타입 (Python, Bash)
```python
count = 42                # 정수
count = "hello"           # 문자열로 변경 가능
count.upper()             # 런타임에 타입 체크
```
- 유연하고 빠른 개발
- 런타임 에러 위험
- IDE 지원 제한적

---

## 빌드 & 배포

### C, C++
```bash
gcc main.c -o app         # C 컴파일
g++ main.cpp -o app       # C++ 컴파일
./app                     # 실행
```
- 플랫폼별 빌드 필요
- 의존성 관리 복잡 (pkg-config, CMake 등)

### C#
```bash
dotnet build              # 빌드
dotnet run                # 실행
dotnet publish            # 배포 패키지
```
- .NET Runtime 필요
- NuGet으로 의존성 관리

### Go
```bash
go build                  # 빌드
./app                     # 실행
```
- 단일 바이너리
- 크로스 컴파일 쉬움

### Python
```bash
python script.py          # 바로 실행
```
- 인터프리터 + 라이브러리 필요
- pip로 의존성 관리

### Bash
```bash
bash script.sh            # 바로 실행
chmod +x script.sh
./script.sh
```
- 별도 설치 불필요

---

## 학습 난이도

```
쉬움 ←―――――――――――――――――――――――――――――――――→ 어려움

Bash ―― Python ―― Go ―― C# ―――――― C ―――――― C++
  ↓        ↓       ↓      ↓        ↓         ↓
 1주      1주    1개월  2개월    3개월     6개월+
```

---

## 결론

**만능 언어는 없습니다.** 상황에 맞는 도구를 선택하세요:

- **극한의 성능 + 하드웨어 제어**: C
- **극한의 성능 + 현대적 기능**: C++
- **균형잡힌 선택**: Go, C#
- **빠른 개발**: Python
- **자동화**: Bash

**실무에서는 여러 언어를 조합**합니다:
- Python으로 프로토타입 → Go로 재작성
- C로 핵심 라이브러리 → Python으로 래핑
- C++로 핵심 엔진 → C#으로 게임 로직 (Unity)
- Bash로 배포 자동화 → Go로 CLI 도구

**첫 언어 추천:**
- 프로그래밍 입문: **Python**
- 시스템 이해: **C**
- 백엔드 개발: **Go**
- 게임 개발: **C#** (Unity)
- 시스템 프로그래밍: **C** → **C++**


---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-11

© 2026 siasia86. Licensed under CC BY 4.0.

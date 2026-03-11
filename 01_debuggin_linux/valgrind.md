# valgrind - 메모리 디버깅 및 프로파일링 도구

## valgrind란?

**Memory Debugging and Profiling Tool** - 메모리 누수, 버퍼 오버플로우, 초기화되지 않은 메모리 사용 등을 감지하는 도구입니다.

## 주요 기능

- 메모리 누수 감지
- 잘못된 메모리 접근 감지
- 초기화되지 않은 메모리 사용 감지
- 캐시 프로파일링
- 힙 프로파일링
- 스레드 에러 감지

## 설치

```bash
# Ubuntu/Debian
sudo apt-get install valgrind

# CentOS/RHEL
sudo yum install valgrind

# 버전 확인
valgrind --version
```

## 주요 도구

### 1. Memcheck (메모리 검사)

**기본 사용:**
```bash
# 기본 검사
valgrind ./myapp

# 상세 정보
valgrind --leak-check=full ./myapp

# 누수 위치 표시
valgrind --leak-check=full --show-leak-kinds=all ./myapp

# 추적 정보 포함
valgrind --leak-check=full --track-origins=yes ./myapp
```

**출력 예시:**
```
==12345== HEAP SUMMARY:
==12345==     in use at exit: 1,024 bytes in 1 blocks
==12345==   total heap usage: 10 allocs, 9 frees, 2,048 bytes allocated
==12345==
==12345== 1,024 bytes in 1 blocks are definitely lost
==12345==    at 0x4C2FB0F: malloc (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
==12345==    by 0x108A: main (test.c:5)
```

### 2. Cachegrind (캐시 프로파일링)

```bash
# 캐시 프로파일링
valgrind --tool=cachegrind ./myapp

# 결과 분석
cg_annotate cachegrind.out.12345

# 특정 파일만
cg_annotate cachegrind.out.12345 myapp.c
```

**출력:**
```
I   refs:      1,234,567
I1  misses:       12,345
LLi misses:        1,234
D   refs:        987,654
D1  misses:       98,765
LLd misses:        9,876
```

### 3. Massif (힙 프로파일링)

```bash
# 힙 프로파일링
valgrind --tool=massif ./myapp

# 결과 분석
ms_print massif.out.12345

# 그래프 생성
massif-visualizer massif.out.12345
```

### 4. Helgrind (스레드 에러)

```bash
# 스레드 에러 검사
valgrind --tool=helgrind ./multithread_app

# 데이터 레이스 감지
valgrind --tool=helgrind --history-level=full ./myapp
```

### 5. Callgrind (콜 그래프)

```bash
# 콜 그래프 프로파일링
valgrind --tool=callgrind ./myapp

# 결과 분석
callgrind_annotate callgrind.out.12345

# GUI 분석
kcachegrind callgrind.out.12345
```

## 실전 예제

### 예제 1: 메모리 누수 감지

```c
// leak.c
#include <stdlib.h>

int main() {
    int *ptr = malloc(1024);
    // free(ptr); 누락!
    return 0;
}
```

**검사:**
```bash
gcc -g leak.c -o leak
valgrind --leak-check=full ./leak

# 출력:
# ==12345== 1,024 bytes in 1 blocks are definitely lost
# ==12345==    at 0x...: malloc
# ==12345==    by 0x...: main (leak.c:4)
```

### 예제 2: 초기화되지 않은 메모리

```c
// uninit.c
#include <stdio.h>

int main() {
    int x;
    printf("%d\n", x);  // 초기화 안 됨
    return 0;
}
```

**검사:**
```bash
gcc -g uninit.c -o uninit
valgrind --track-origins=yes ./uninit

# 출력:
# ==12345== Conditional jump or move depends on uninitialised value(s)
# ==12345==    at 0x...: printf
# ==12345==    by 0x...: main (uninit.c:5)
```

### 예제 3: 버퍼 오버플로우

```c
// overflow.c
#include <string.h>

int main() {
    char buf[10];
    strcpy(buf, "This is too long!");  // 오버플로우
    return 0;
}
```

**검사:**
```bash
gcc -g overflow.c -o overflow
valgrind ./overflow

# 출력:
# ==12345== Invalid write of size 1
# ==12345==    at 0x...: strcpy
# ==12345==    by 0x...: main (overflow.c:5)
```

### 예제 4: Use After Free

```c
// uaf.c
#include <stdlib.h>

int main() {
    int *ptr = malloc(sizeof(int));
    free(ptr);
    *ptr = 42;  // 해제된 메모리 사용
    return 0;
}
```

**검사:**
```bash
gcc -g uaf.c -o uaf
valgrind ./uaf

# 출력:
# ==12345== Invalid write of size 4
# ==12345==    at 0x...: main (uaf.c:6)
# ==12345==  Address 0x... is 0 bytes inside a block of size 4 free'd
```

### 예제 5: 더블 프리

```c
// double_free.c
#include <stdlib.h>

int main() {
    int *ptr = malloc(sizeof(int));
    free(ptr);
    free(ptr);  // 이중 해제
    return 0;
}
```

**검사:**
```bash
gcc -g double_free.c -o double_free
valgrind ./double_free

# 출력:
# ==12345== Invalid free() / delete / delete[] / realloc()
# ==12345==    at 0x...: free
# ==12345==    by 0x...: main (double_free.c:6)
```

## 유용한 옵션

### Memcheck 옵션

```bash
# 전체 누수 검사
valgrind --leak-check=full \
         --show-leak-kinds=all \
         --track-origins=yes \
         --verbose \
         --log-file=valgrind.log \
         ./myapp

# 억제 파일 사용
valgrind --suppressions=myapp.supp ./myapp

# 자식 프로세스 추적
valgrind --trace-children=yes ./myapp
```

### 성능 옵션

```bash
# 빠른 검사 (정확도 낮음)
valgrind --leak-check=summary ./myapp

# 상세 검사 (느림)
valgrind --leak-check=full --track-origins=yes ./myapp
```

## 메모리 누수 종류

### 1. Definitely Lost

```
확실히 누수됨 - 접근 불가능한 메모리
해결: free() 호출 추가
```

### 2. Indirectly Lost

```
간접적 누수 - 다른 누수로 인한 누수
해결: 부모 메모리 해제
```

### 3. Possibly Lost

```
가능성 있는 누수 - 포인터가 중간을 가리킴
확인 필요
```

### 4. Still Reachable

```
여전히 접근 가능 - 프로그램 종료 시 남은 메모리
일반적으로 문제 없음
```

## 억제 파일 (Suppression)

**생성:**
```bash
# 억제 파일 생성
valgrind --gen-suppressions=all ./myapp > myapp.supp

# 편집
vim myapp.supp
```

**사용:**
```bash
valgrind --suppressions=myapp.supp ./myapp
```

**예시:**
```
{
   <insert_a_suppression_name_here>
   Memcheck:Leak
   fun:malloc
   fun:some_library_function
}
```

## 성능 오버헤드

```bash
# 일반 실행
time ./myapp
# real    0m1.000s

# Memcheck
time valgrind ./myapp
# real    0m20.000s (20배 느림)

# Cachegrind
time valgrind --tool=cachegrind ./myapp
# real    0m50.000s (50배 느림)
```

**권장:**
- 개발/테스트 환경에서만 사용
- 프로덕션에서는 사용 금지

## 트러블슈팅

### 문제 1: "Cannot execute binary file"

```bash
# 원인: 32비트/64비트 불일치
# 해결: 올바른 아키텍처로 컴파일
gcc -m64 myapp.c -o myapp
```

### 문제 2: 너무 많은 에러

```bash
# 에러 개수 제한
valgrind --error-limit=no ./myapp

# 특정 에러만
valgrind --show-error-list=yes ./myapp
```

### 문제 3: 라이브러리 에러

```bash
# 라이브러리 에러 무시
valgrind --suppressions=/usr/share/valgrind/default.supp ./myapp
```

## 실무 팁

### 1. CI/CD 통합

```bash
#!/bin/bash
# valgrind_check.sh

valgrind --leak-check=full \
         --error-exitcode=1 \
         --log-file=valgrind.log \
         ./myapp

if [ $? -ne 0 ]; then
    echo "Memory errors detected!"
    cat valgrind.log
    exit 1
fi
```

### 2. 자동화 스크립트

```bash
# 모든 테스트 실행
for test in tests/*; do
    echo "Testing $test"
    valgrind --leak-check=full $test
done
```

### 3. 로그 분석

```bash
# 누수만 추출
grep "definitely lost" valgrind.log

# 에러 개수
grep "ERROR SUMMARY" valgrind.log
```

## 관련 도구

| 도구 | 용도 |
|------|------|
| **valgrind** | 메모리 디버깅 |
| **AddressSanitizer** | 빠른 메모리 검사 |
| **LeakSanitizer** | 누수 검사 |
| **MemorySanitizer** | 초기화 검사 |
| **gdb** | 소스 디버깅 |

## 요약

**valgrind의 강점:**
- 메모리 문제 정확한 감지
- 다양한 프로파일링 도구
- 소스 위치 정확히 표시

**주요 도구:**
- Memcheck - 메모리 검사
- Cachegrind - 캐시 프로파일링
- Massif - 힙 프로파일링
- Helgrind - 스레드 에러

**언제 사용?**
- 메모리 누수 찾기
- 버퍼 오버플로우 감지
- 초기화 에러 확인
- 성능 최적화

# Bash 수학 연산

참고: [phoenixNAP - Bash Math Operations](https://phoenixnap.com/kb/bash-math)

## 개요

Bash 스크립팅에서 산술 연산을 수행하는 다양한 방법을 정리한 문서이다.

## 주요 활용

- 기본 산술 연산 (덧셈, 뺄셈, 곱셈, 나눗셈)
- 증감 연산
- 단위 변환
- 소수점 연산
- 백분율 계산
- 진법 변환 (2진수, 8진수, 16진수)

## 연산 방법

### 1. 산술 확장 (권장)

```bash
$((expression))
```

```bash
echo $((2+3))  # 출력: 5
```

### 2. awk

```bash
awk 'BEGIN { x = 2; y = 3; print "x + y = "(x+y) }'
```

### 3. bc (기본 계산기)

임의 정밀도 산술 지원:

```bash
echo "2+3" | bc
```

### 4. dc (역폴란드 표기법)

```bash
echo "2 3 + p" | dc
```

### 5. declare

`-i` 옵션으로 정수 연산:

```bash
declare -i x=2 y=3 z=x+y
echo $x + $y = $z
```

### 6. expr (레거시)

```bash
expr 2 + 3
```

### 7. let

```bash
let x=2+3
echo $x
```

### 8. test

조건식 평가:

```bash
test 2 -gt 3; echo $?
# 또는
[ 2 -gt 3 ]; echo $?
```

## 산술 연산자

| 연산자               | 설명                     |                        |                   |
|----------------------|--------------------------|------------------------|-------------------|
| `++x`, `x++`         | 전위/후위 증가           |                        |                   |
| `--x`, `x--`         | 전위/후위 감소           |                        |                   |
| `+`, `-`, `*`, `/`   | 덧셈, 뺄셈, 곱셈, 나눗셈 |                        |                   |
| `%`                  | 나머지 (모듈로)          |                        |                   |
| `**`                 | 거듭제곱                 |                        |                   |
| `&&`, `\             | \                        | `, `!`                 | 논리 AND, OR, NOT |
| `&`, `\              | `, `^`, `~`              | 비트 AND, OR, XOR, NOT |                   |
| `<=`, `<`, `>`, `>=` | 비교 연산자              |                        |                   |
| `==`, `!=`           | 동등/부등 연산자         |                        |                   |
| `=`                  | 대입 연산자              |                        |                   |

> `^`는 Bash `$(())`에서 비트 XOR 연산자이다. 거듭제곱은 `**`만 해당.

## 실전 예제

### 정수 연산

```bash
echo $((x=2, y=3, x+y))  # 출력: 5

# 여러 계산 동시 수행
((x=2, y=3, a=x+y, b=x*y, c=x**y))
echo $a, $b, $c  # 출력: 5, 6, 8
```

### 증감 연산

전위 증가 (증가 후 사용):
```bash
number=1
echo $((++number))  # 출력: 2
```

후위 증가 (사용 후 증가):
```bash
number=1
echo $((number++))  # 출력: 1
echo $number        # 출력: 2
```

### 소수점 연산

Bash 산술 확장은 정수만 지원한다. 소수점은 아래 도구 사용:

awk:
```bash
awk 'BEGIN { x = 2.3; y = 3.2; print "x * y = "(x * y) }'
```

bc:
```bash
echo "2.3 * 3.2" | bc -l
```

Perl:
```bash
perl -e 'print 2.3*3.2'
```

### 백분율 계산

printf:
```bash
printf %.2f%% "$((10**4 * 40/71))e-4"%
```

awk:
```bash
awk 'BEGIN { printf "%.2f%%", (40/71*100) }'
```

### 팩토리얼 함수

```bash
factorial () { 
    if (($1 > 1))
    then
        echo $(( $( factorial $(($1 - 1)) ) * $1 ))
    else
        echo 1
        return
    fi
}

factorial 5  # 출력: 120
```

큰 수는 bc 사용:
```bash
echo 'define factorial(x) {if (x>1){return x*factorial(x-1)};return 1} factorial(50)' | bc
```

### 계산기 함수

bc 사용:
```bash
calculate() { printf "%s\n" "$@" | bc -l; }
calculate "2.5 * 3.7"
```

산술 확장 사용:
```bash
calculate() { echo $(("$@")); }
calculate "2 + 3"
```

### 진법 변환

2진수:
```bash
echo $((2#1010+2#1010))  # 출력: 20
```

8진수:
```bash
echo $((010+010))  # 출력: 16
```

16진수:
```bash
echo $((0xA+0xA))  # 출력: 20
```

## 자주 발생하는 오류

### "value too great for base"

진법 범위를 벗어난 숫자 사용 시 발생:
```bash
echo $((2#2+2#2))    # 오류: 2는 2진수에서 유효하지 않음
echo $((2#10+2#10))  # 정상: 2진수 10 = 10진수 2
```

### "syntax error: invalid arithmetic operator"

산술 확장은 정수만 지원:
```bash
echo $((2.1+2.1))      # 오류
echo "2.1+2.1" | bc -l  # 해결
```

### "integer expression expected"

test 명령은 정수만 허용:
```bash
[ 1 -gt 1.5 ]  # 오류
[ 1 -gt 1 ]    # 정상
```

## 권장 사항

- 정수 계산은 산술 확장 `$(())` 사용
- 소수점 연산은 `bc` 또는 `awk` 사용
- 출력 포맷팅은 `printf` 활용
- 자주 쓰는 계산은 `.bashrc`에 함수로 등록
- 정수 나눗셈의 소수점 버림에 주의

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**마지막 업데이트**: 2026-04-12

© 2026 siasia86. Licensed under CC BY 4.0.

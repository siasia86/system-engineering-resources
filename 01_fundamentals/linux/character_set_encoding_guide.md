# Character Set & Encoding 가이드

## 목차

| 섹션 |
|------|
| [1. 기초 개념](#1-기초-개념) |
| [2. 주요 Character Set](#2-주요-character-set) |
| [3. 주요 Encoding](#3-주요-encoding) |
| [4. BOM (Byte Order Mark)](#4-bom-byte-order-mark) |
| [5. 실무 예제](#5-실무-예제) |
| [6. 고급: 인코딩 문제 디버깅](#6-고급-인코딩-문제-디버깅) |
| [7. 정리](#7-정리) |

---


[⬆ 목차로 돌아가기](#목차)

---

## 1. 기초 개념

### Character Set (문자 집합)

문자와 숫자(코드 포인트)의 매핑 테이블입니다.

```
문자 → 코드 포인트
'A'  → 65
'B'  → 66
'가' → 44032
```

### Encoding (인코딩)

코드 포인트를 실제 바이트로 변환하는 규칙입니다.

```
코드 포인트 → 바이트
65 (A)     → 0x41              (UTF-8: 1바이트)
44032 (가) → 0xEA 0xB0 0x80    (UTF-8: 3바이트)
44032 (가) → 0xB0 0xA1         (EUC-KR: 2바이트)
```

### 관계

```
+----------------+     +------------+     +----------+
|  Character Set |     |  Encoding  |     |  Bytes   |
|  (문자 집합)   | --> |  (변환 규칙)| --> | (저장값) |
|  A = 65        |     |  UTF-8     |     | 0x41     |
|  가 = 44032    |     |  EUC-KR    |     | 0xB0A1   |
+----------------+     +------------+     +----------+
```

[⬆ 목차로 돌아가기](#목차)

---

## 2. 주요 Character Set

### ASCII (7bit, 128문자)

```
+-------+--------+----------+
| 범위  | 내용   | 예시     |
+-------+--------+----------+
| 0-31  | 제어   | \n \t \r |
| 32-47 | 특수   | ! " # $  |
| 48-57 | 숫자   | 0-9      |
| 65-90 | 대문자 | A-Z      |
| 97-122| 소문자 | a-z      |
| 127   | DEL    |          |
+-------+--------+----------+
```

```bash
# ASCII 코드 확인
python3 -c "print(ord('A'), ord('a'), ord('0'))"
# 65 97 48
```

### ISO-8859-1 (Latin-1, 8bit, 256문자)

ASCII 확장. 서유럽 문자 지원.

```
ASCII (0-127) + 서유럽 확장 (128-255)
'é' = 233, 'ñ' = 241, 'ü' = 252
```

### EUC-KR (한국어)

한글 완성형. 2바이트로 한글 표현. 2,350자만 지원.

```
'가' = 0xB0A1
'힣' = 0xC8FE
'똠' = 표현 불가 ← KS X 1001 기준 (Python euc-kr 코덱은 CP949 확장 포함)
```

### CP949 (MS949)

EUC-KR 확장. Windows 한국어 기본. 11,172자 지원.

```
'가' = 0xB0A1 (EUC-KR 호환)
'똠' = 0x8C63 (확장 영역)
```

### Unicode

전 세계 모든 문자를 하나의 체계로. 현재 149,000+ 문자.

```
'A'  = U+0041
'가' = U+AC00
'😀' = U+1F600
'漢' = U+6F22
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. 주요 Encoding

### UTF-8 (가변 길이: 1~4바이트)

현재 웹 표준. ASCII 호환.

```
+------------------+--------+---------------------------+
| 범위             | 바이트 | 예시                      |
+------------------+--------+---------------------------+
| U+0000-007F      | 1      | A → 0x41                  |
| U+0080-07FF      | 2      | é → 0xC3 0xA9             |
| U+0800-FFFF      | 3      | 가 → 0xEA 0xB0 0x80      |
| U+10000-10FFFF   | 4      | 😀 → 0xF0 0x9F 0x98 0x80 |
+------------------+--------+---------------------------+
```

```python
# UTF-8 인코딩 확인
text = '가'
encoded = text.encode('utf-8')
print(encoded)        # b'\xea\xb0\x80'
print(len(encoded))   # 3바이트
```

### UTF-16 (가변 길이: 2 또는 4바이트)

Windows 내부, Java 내부에서 사용.

```
'A'  → 0x00 0x41 (2바이트)
'가' → 0xAC 0x00 (2바이트)
'😀' → 0xD8 0x3D 0xDE 0x00 (4바이트, surrogate pair)
```

```python
text = '가'
print(text.encode('utf-16-be').hex())  # ac00
print(text.encode('utf-16-le').hex())  # 00ac
```

### UTF-32 (고정 길이: 4바이트)

```
'A'  → 0x00 0x00 0x00 0x41
'가' → 0x00 0x00 0xAC 0x00
```

메모리 낭비가 크지만 인덱싱이 빠름.

### 인코딩 비교

```
+----------+------+--------+--------+--------+
| 문자     | ASCII| UTF-8  | UTF-16 | EUC-KR |
+----------+------+--------+--------+--------+
| A        | 1B   | 1B     | 2B     | 1B     |
| é        | -    | 2B     | 2B     | -      |
| 가       | -    | 3B     | 2B     | 2B     |
| 😀       | -    | 4B     | 4B     | -      |
+----------+------+--------+--------+--------+
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. BOM (Byte Order Mark)

파일 시작 부분에 인코딩을 표시하는 마커.

```
+-------------+--------------------+
| 인코딩      | BOM (hex)          |
+-------------+--------------------+
| UTF-8       | EF BB BF           |
| UTF-16 BE   | FE FF              |
| UTF-16 LE   | FF FE              |
| UTF-32 BE   | 00 00 FE FF        |
| UTF-32 LE   | FF FE 00 00        |
+-------------+--------------------+
```

```bash
# BOM 확인 (Linux)
xxd file.txt | head -1
# 00000000: efbb bf48 656c 6c6f  ...Hello

# BOM 확인 (PowerShell)
Format-Hex file.txt | Select-Object -First 1
```

### BOM 유무에 따른 차이

```bash
# UTF-8 BOM 있음 (Windows 메모장 기본)
echo -ne '\xEF\xBB\xBF' > bom.txt
echo "Hello" >> bom.txt

# UTF-8 BOM 없음 (Linux 기본)
echo "Hello" > nobom.txt
```

🟡 BOM이 있으면 셸 스크립트, CSV 파싱 등에서 문제가 발생할 수 있음.

```bash
# BOM 제거
sed -i '1s/^\xEF\xBB\xBF//' file.txt
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 실무 예제

### 5-1. 파일 인코딩 확인

```bash
# Linux
file -i document.txt
# document.txt: text/plain; charset=utf-8

# 상세 확인
xxd document.txt | head -3

# Python
python3 -c "
import chardet
with open('document.txt', 'rb') as f:
    result = chardet.detect(f.read())
    print(result)
"
# {'encoding': 'utf-8', 'confidence': 0.99}
```

```powershell
# PowerShell
[System.IO.File]::ReadAllBytes("document.txt")[0..2]
```

### 5-2. 인코딩 변환

```bash
# Linux: EUC-KR → UTF-8
iconv -f euc-kr -t utf-8 input.txt > output.txt

# 확인
iconv -f euc-kr -t utf-8 input.txt | file -

# 디렉토리 내 전체 변환
for f in *.txt; do
  iconv -f euc-kr -t utf-8 "$f" > "${f%.txt}_utf8.txt"
done
```

```python
# Python: EUC-KR → UTF-8
with open('input.txt', 'r', encoding='euc-kr') as f:
    content = f.read()
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write(content)
```

```powershell
# PowerShell: 인코딩 지정하여 저장
Get-Content input.txt -Encoding Default | Set-Content output.txt -Encoding UTF8
```

### 5-3. 깨진 문자 복구

```python
# 잘못된 인코딩으로 읽은 경우
broken = '¾È³çÇÏ¼¼¿ä'  # UTF-8로 읽었지만 실제는 EUC-KR

# 복구: 잘못 디코딩된 것을 원래 바이트로 되돌린 후 올바른 인코딩으로 디코딩
fixed = broken.encode('latin-1').decode('euc-kr')
print(fixed)  # 안녕하세요
```

### 5-4. 데이터베이스 인코딩

```sql
-- MySQL: 테이블 인코딩 확인
SHOW CREATE TABLE my_table;

-- 데이터베이스 인코딩 확인
SHOW VARIABLES LIKE 'character_set%';

-- 결과 예시:
-- character_set_client     | utf8mb4
-- character_set_connection | utf8mb4
-- character_set_database   | utf8mb4
-- character_set_results    | utf8mb4
-- character_set_server     | utf8mb4
```

```
+----------+----------+----------------------------------+
| 설정     | utf8     | utf8mb4                          |
+----------+----------+----------------------------------+
| 바이트   | 최대 3B  | 최대 4B                          |
| 이모지   | ❌       | ✅                               |
| 권장     | ❌       | ✅ (MySQL 8.0 기본)              |
+----------+----------+----------------------------------+
```

🟡 MySQL의 `utf8`은 진짜 UTF-8이 아님. `utf8mb4`를 사용해야 함.

### 5-5. HTTP 인코딩

```
# HTTP 헤더
Content-Type: text/html; charset=utf-8

# HTML meta 태그
<meta charset="UTF-8">

# 우선순위: HTTP 헤더 > BOM > meta 태그
```

### 5-6. SSH/터미널 인코딩

```bash
# 현재 로케일 확인
locale
# LANG=en_US.UTF-8

# 로케일 변경
export LANG=ko_KR.UTF-8

# 사용 가능한 로케일 확인
locale -a | grep -i utf
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 고급: 인코딩 문제 디버깅

### 6-1. hex dump로 바이트 확인

```bash
# '가'의 각 인코딩별 바이트
echo -n '가' | xxd
# UTF-8:  ea b0 80

echo -n '가' | iconv -t euc-kr | xxd
# EUC-KR: b0 a1

echo -n '가' | iconv -t utf-16be | xxd
# UTF-16: ac 00
```

### 6-2. Python으로 바이트 레벨 분석

```python
text = '가나다ABC😀'

for char in text:
    cp = ord(char)
    utf8 = char.encode('utf-8')
    try:
        euckr = char.encode('euc-kr')
    except UnicodeEncodeError:
        euckr = b'N/A'
    print(f"'{char}' U+{cp:04X} UTF-8:{utf8.hex()} EUC-KR:{euckr.hex() if euckr != b'N/A' else 'N/A'}")

# 출력:
# '가' U+AC00 UTF-8:eab080 EUC-KR:b0a1
# '나' U+B098 UTF-8:eb8298 EUC-KR:b3aa
# '다' U+B2E4 UTF-8:eb8ba4 EUC-KR:b4d9
# 'A'  U+0041 UTF-8:41     EUC-KR:41
# 'B'  U+0042 UTF-8:42     EUC-KR:42
# 'C'  U+0043 UTF-8:43     EUC-KR:43
# '😀' U+1F600 UTF-8:f09f9880 EUC-KR:N/A
```

### 6-3. 흔한 깨짐 패턴

```
+----------------------------+------------------+---------------------------+
| 증상                       | 원인             | 해결                      |
+----------------------------+------------------+---------------------------+
| ¾È³çÇÏ¼¼¿ä              | EUC-KR을 Latin-1 | Latin-1 → bytes → EUC-KR  |
|                            | 로 읽음          |                           |
+----------------------------+------------------+---------------------------+
| 안녕하세요 → ????? | UTF-8을 ASCII로  | UTF-8로 다시 읽기         |
|                            | 읽음             |                           |
+----------------------------+------------------+---------------------------+
| 가 → ê°€                  | UTF-8을 Latin-1  | Latin-1 → bytes → UTF-8   |
|                            | 로 읽음          |                           |
+----------------------------+------------------+---------------------------+
| 가 → &#xAC00;             | HTML 엔티티 변환 | HTML 디코딩               |
+----------------------------+------------------+---------------------------+
```

### 6-4. 파일 인코딩 일괄 변환 스크립트

```bash
#!/bin/bash
# EUC-KR → UTF-8 일괄 변환
find . -name "*.txt" -type f | while read f; do
    encoding=$(file -bi "$f" | grep -oP 'charset=\K[^ ]+')
    if [ "$encoding" = "euc-kr" ] || [ "$encoding" = "iso-8859-1" ]; then
        iconv -f euc-kr -t utf-8 "$f" > "${f}.tmp" && mv "${f}.tmp" "$f"
        echo "converted: $f"
    fi
done
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 정리

### 인코딩 선택 가이드

```
+-------------------+---------------------------+
| 상황              | 권장 인코딩               |
+-------------------+---------------------------+
| 새 프로젝트       | UTF-8 (BOM 없음)          |
| 웹 개발           | UTF-8                     |
| Windows 앱        | UTF-8 또는 UTF-16         |
| 한국어 레거시     | EUC-KR → UTF-8 마이그레이션 |
| MySQL             | utf8mb4                   |
| API/JSON          | UTF-8                     |
| CSV (Excel 호환)  | UTF-8 BOM                 |
+-------------------+---------------------------+
```

### 핵심 원칙

1. 새 프로젝트는 무조건 UTF-8
2. 입력/저장/출력 모든 단계에서 인코딩을 명시적으로 지정
3. 인코딩 변환은 바이트 레벨에서 확인 후 진행
4. MySQL은 `utf8`이 아닌 `utf8mb4` 사용

---

## 참고 자료

- Unicode Standard: [unicode.org](https://www.unicode.org/standard/standard.html) — ★★☆☆☆
- MySQL Character Sets: [dev.mysql.com](https://dev.mysql.com/doc/refman/8.0/en/charset.html) — ★★★☆☆
- Python Documentation: [codecs](https://docs.python.org/3/library/codecs.html) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-04-03

**마지막 업데이트**: 2026-04-03

© 2026 siasia86. Licensed under CC BY 4.0.

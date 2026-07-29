---
name: charset-encoding-official-notes
description: Character Set / Encoding 문서 작성 시 참조할 공식 소스. Unicode, RFC, MySQL, Python 공식 문서 기반. 01_fundamentals/linux/ 인코딩 문서 생성/검토 시 참조.
tags:
  - encoding
  - unicode
  - utf-8
  - charset
last_checked: 2026-07-07
sources:
  - https://www.unicode.org/standard/standard.html
  - https://www.unicode.org/faq/utf_bom.html
  - https://datatracker.ietf.org/doc/html/rfc3629
  - https://dev.mysql.com/doc/refman/8.0/en/charset-unicode-utf8mb4.html
  - https://docs.python.org/3/library/codecs.html
  - https://en.wikipedia.org/wiki/KS_X_1001  # KS X 1001 공식 문서 비공개, Wikipedia로 수치 확인
---

# Character Set / Encoding 공식 참조 노트

## 1. Unicode 표준

- 현재 버전: Unicode 16.0 (2024-09)
- 총 문자 수: 154,998 characters (16.0 기준)
- 코드 포인트 범위: U+0000 ~ U+10FFFF (1,114,112 코드 포인트, 17 planes)
- 한글 Syllables Block: U+AC00 ~ U+D7A3 (11,172자)
- 출처: https://www.unicode.org/standard/standard.html

## 2. UTF-8 (RFC 3629)

바이트 범위 (RFC 3629 Table):

| 코드 포인트 범위   | UTF-8 바이트 수 | 선두 비트 패턴                      |
|--------------------|-----------------|-------------------------------------|
| U+0000 ~ U+007F    | 1               | 0xxxxxxx                            |
| U+0080 ~ U+07FF    | 2               | 110xxxxx 10xxxxxx                   |
| U+0800 ~ U+FFFF    | 3               | 1110xxxx 10xxxxxx 10xxxxxx          |
| U+10000 ~ U+10FFFF | 4               | 11110xxx 10xxxxxx 10xxxxxx 10xxxxxx |

- ASCII 하위 호환 (U+0000~U+007F는 1바이트, 값 동일)
- 자기 동기화(self-synchronizing): 어느 바이트에서든 문자 경계 식별 가능
- 출처: RFC 3629 (2003), https://datatracker.ietf.org/doc/html/rfc3629

## 3. BOM (Byte Order Mark)

Unicode FAQ 공식 값:

| 인코딩    | BOM (hex)   |
|-----------|-------------|
| UTF-8     | EF BB BF    |
| UTF-16 BE | FE FF       |
| UTF-16 LE | FF FE       |
| UTF-32 BE | 00 00 FE FF |
| UTF-32 LE | FF FE 00 00 |

- UTF-8 BOM은 선택사항 (Linux에서는 사용 안 함, Windows 메모장은 기본 추가)
- 출처: https://www.unicode.org/faq/utf_bom.html

## 4. 한국어 인코딩

### KS X 1001 (EUC-KR 원본)

- 완성형 한글: 2,350자
- 범위: Row 16~40 (한글 음절)
- 한계: 현대 한글 11,172자 중 일부만 표현 가능
- 출처: KS X 1001:2004, https://en.wikipedia.org/wiki/KS_X_1001

### CP949 (MS949, Unified Hangul Code)

- EUC-KR 확장: 11,172 한글 음절 전부 지원
- Windows 한국어 기본 코드 페이지
- EUC-KR 영역과 하위 호환
- 출처: https://en.wikipedia.org/wiki/Unified_Hangul_Code

### Python euc-kr 코덱 주의사항

- Python의 `euc-kr` 코덱은 CP949 확장을 포함 (순수 KS X 1001이 아님)
- `euc-kr`과 `cp949`는 동일하지 않지만, Python 구현상 euc-kr이 확장 문자도 처리
- 출처: https://docs.python.org/3/library/codecs.html#standard-encodings

## 5. MySQL Character Set

### utf8 vs utf8mb4

| 항목        | utf8 (utf8mb3)   | utf8mb4      |
|-------------|------------------|--------------|
| 최대 바이트 | 3                | 4            |
| BMP 외 문자 | ❌ (이모지 불가) | ✅           |
| MySQL 8.0   | deprecated alias | 기본 charset |

- MySQL 8.0 기본: `utf8mb4` + `utf8mb4_0900_ai_ci` collation
- `utf8`은 `utf8mb3`의 alias (향후 제거 예정)
- 출처: https://dev.mysql.com/doc/refman/8.0/en/charset-unicode-utf8mb4.html

### PostgreSQL

- 기본: UTF-8 (`ENCODING UTF8`)
- ICU collation 지원 (PG 10+)
- `C.UTF-8` locale 권장 (Ubuntu 24.04+)
- 출처: https://www.postgresql.org/docs/current/multibyte.html

## 6. HTTP/HTML 인코딩 선언

우선순위 (높은 순):
1. HTTP Content-Type 헤더: `Content-Type: text/html; charset=utf-8`
2. BOM (있는 경우)
3. HTML meta: `<meta charset="UTF-8">`

- 출처: WHATWG HTML Standard, https://html.spec.whatwg.org/multipage/parsing.html#determining-the-character-encoding

## 7. ASCII (RFC 20)

- 7-bit: 128 문자 (0~127)
- 제어 문자: 0~31, 127 (DEL)
- 출력 가능: 32~126 (95자)
- 출처: RFC 20 (1969), ANSI X3.4-1968

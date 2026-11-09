---
name: charset-encoding-official-notes
description: Character Set / Encoding 문서 작성 시 참조할 공식 소스. Unicode, RFC, MySQL, Python 공식 문서 기반. 01_fundamentals/linux/ 인코딩 문서 생성/검토 시 참조.
tags:
  - encoding
  - unicode
  - utf-8
  - charset
last_checked: 2026-11-09
sources:
  - https://www.unicode.org/standard/standard.html
  - https://www.unicode.org/faq/utf_bom.html
  - https://datatracker.ietf.org/doc/html/rfc3629
  - https://dev.mysql.com/doc/refman/8.4/en/charset-unicode-utf8mb4.html
  - https://docs.python.org/3/library/codecs.html
  - https://en.wikipedia.org/wiki/KS_X_1001  # KS X 1001 공식 문서 비공개, Wikipedia로 수치 확인
  - https://www.unicode.org/versions/latest/
  - https://html.spec.whatwg.org/multipage/parsing.html#determining-the-character-encoding
  - https://blogs.windows.com/windows-insider/2018/12/10/announcing-windows-10-insider-preview-build-18298/
---

# Character Set / Encoding 공식 참조 노트

## 1. Unicode 표준

- 현재 버전: Unicode 18.0 (2026-09-16 발표, 2026-11-09 확인)
- 총 문자 수: 172,808 characters (18.0 기준, 16.0은 154,998)
- 코드 포인트 범위: U+0000 ~ U+10FFFF (1,114,112 코드 포인트, 17 planes)
- 한글 Syllables Block: U+AC00 ~ U+D7A3 (11,172자)
- 출처: https://www.unicode.org/standard/standard.html, https://www.unicode.org/versions/latest/

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

- UTF-8 BOM은 선택사항 (Linux에서는 사용 안 함). Windows 10 1903(Insider Build 18298) 이후 메모장은 새 파일을 BOM 없는 UTF-8로 저장하며, 그 전에는 BOM을 붙였습니다
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

- Python의 `euc-kr` 코덱은 CP949(UHC) 확장 영역을 해석하지 않습니다. 예: `b'\x8c\x63'.decode('euc-kr')`는 `UnicodeDecodeError`, `cp949`로는 '똠'
- 2,350자 밖 음절은 KS X 1001의 자모 조합 8바이트 시퀀스로 인코딩합니다. 예: `'똠'.encode('euc-kr')` → `b'\xa4\xd4\xa4\xa8\xa4\xc7\xa4\xb1'` (2026-11-09 Python 3.14.6 재현)
- 출처: https://docs.python.org/3/library/codecs.html#standard-encodings

## 5. MySQL Character Set

### utf8 vs utf8mb4

| 항목        | utf8 (utf8mb3)   | utf8mb4      |
|-------------|------------------|--------------|
| 최대 바이트 | 3                | 4            |
| BMP 외 문자 | ❌ (이모지 불가) | ✅           |
| MySQL 8.0   | deprecated alias | 기본 charset |

- MySQL 8.0 기본: `utf8mb4` + `utf8mb4_0900_ai_ci` collation (8.4 LTS도 같음, 8.0은 2026-04 지원 종료)
- `utf8`은 `utf8mb3`의 alias (향후 제거 예정)
- 출처: https://dev.mysql.com/doc/refman/8.4/en/charset-unicode-utf8mb4.html, https://dev.mysql.com/doc/refman/8.4/en/charset-server.html

### PostgreSQL

- 기본: UTF-8 (`ENCODING UTF8`)
- ICU collation 지원 (PG 10+)
- `C.UTF-8` locale 권장 (Ubuntu 24.04+)
- 출처: https://www.postgresql.org/docs/current/multibyte.html

## 6. HTTP/HTML 인코딩 선언

우선순위 (높은 순):
1. BOM (있는 경우)
2. HTTP Content-Type 헤더: `Content-Type: text/html; charset=utf-8`
3. HTML meta: `<meta charset="UTF-8">`

- 인코딩 감지 알고리즘의 첫 단계가 BOM 감지이며, BOM이 있으면 HTTP 헤더보다 우선합니다(2026-11-09 확인)
- 출처: WHATWG HTML Standard, https://html.spec.whatwg.org/multipage/parsing.html#determining-the-character-encoding

## 7. ASCII (RFC 20)

- 7-bit: 128 문자 (0~127)
- 제어 문자: 0~31, 127 (DEL)
- 출력 가능: 32~126 (95자)
- 출처: RFC 20 (1969), ANSI X3.4-1968

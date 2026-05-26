# 에러 코드 레퍼런스

## 목차

| 섹션 |
|------|
| [1. HTTP 상태 코드](#1-http-상태-코드) / [2. SMTP 응답 코드](#2-smtp-응답-코드) / [3. FTP 응답 코드](#3-ftp-응답-코드) |
| [4. DNS RCODE](#4-dns-rcode) / [5. 비공식 확장 코드](#5-비공식-확장-코드) |

---

## 1. HTTP 상태 코드

출처: IANA HTTP Status Code Registry (https://www.iana.org/assignments/http-status-codes/)

### 1xx — Informational

| 코드 | 이름                | 설명                                    |
|------|---------------------|-----------------------------------------|
| 100  | Continue            | 요청 헤더 수신, 본문 계속 전송 가능     |
| 101  | Switching Protocols | 프로토콜 전환 (WebSocket 업그레이드 등) |
| 102  | Processing          | 요청 처리 중 (WebDAV)                   |
| 103  | Early Hints         | 응답 전 Link 헤더 미리 전송             |

### 2xx — Success

| 코드 | 이름                   | 설명                                  |
|------|------------------------|---------------------------------------|
| 200  | OK                     | 요청 성공                             |
| 201  | Created                | 리소스 생성 성공 (POST)               |
| 202  | Accepted               | 요청 수락, 처리는 비동기              |
| 203  | Non-Authoritative Info | 프록시가 수정한 응답                  |
| 204  | No Content             | 성공, 반환할 본문 없음                |
| 205  | Reset Content          | 클라이언트 폼 초기화 요청             |
| 206  | Partial Content        | 범위 요청 성공 (Range 헤더)           |
| 207  | Multi-Status           | 여러 리소스 상태 (WebDAV)             |
| 208  | Already Reported       | 이미 보고된 바인딩 (WebDAV)           |
| 226  | IM Used                | 인스턴스 조작 적용됨 (Delta encoding) |

### 3xx — Redirection

| 코드 | 이름               | 설명                                 |
|------|--------------------|--------------------------------------|
| 300  | Multiple Choices   | 여러 응답 중 선택 가능               |
| 301  | Moved Permanently  | 영구 이동 (메서드 GET으로 변경 가능) |
| 302  | Found              | 임시 이동 (메서드 GET으로 변경 가능) |
| 303  | See Other          | 다른 URL로 GET 요청                  |
| 304  | Not Modified       | 캐시 유효, 본문 없음                 |
| 307  | Temporary Redirect | 임시 이동 (메서드 유지)              |
| 308  | Permanent Redirect | 영구 이동 (메서드 유지)              |

### 4xx — Client Error

| 코드 | 이름                        | 설명                                  |
|------|-----------------------------|---------------------------------------|
| 400  | Bad Request                 | 잘못된 요청 문법                      |
| 401  | Unauthorized                | 인증 필요 (미인증)                    |
| 402  | Payment Required            | 결제 필요 (예약됨)                    |
| 403  | Forbidden                   | 권한 없음 (인증됐지만 접근 불가)      |
| 404  | Not Found                   | 리소스 없음                           |
| 405  | Method Not Allowed          | 허용되지 않는 HTTP 메서드             |
| 406  | Not Acceptable              | Accept 헤더 조건 불충족               |
| 407  | Proxy Auth Required         | 프록시 인증 필요                      |
| 408  | Request Timeout             | 요청 시간 초과                        |
| 409  | Conflict                    | 리소스 충돌 (중복 등)                 |
| 410  | Gone                        | 리소스 영구 삭제됨                    |
| 411  | Length Required             | Content-Length 헤더 필요              |
| 412  | Precondition Failed         | 조건부 요청 실패                      |
| 413  | Content Too Large           | 요청 본문이 너무 큼                   |
| 414  | URI Too Long                | URI가 너무 길음                       |
| 415  | Unsupported Media Type      | 지원하지 않는 Content-Type            |
| 416  | Range Not Satisfiable       | 요청 범위 처리 불가                   |
| 417  | Expectation Failed          | Expect 헤더 조건 불충족               |
| 421  | Misdirected Request         | 잘못된 서버로 요청                    |
| 422  | Unprocessable Content       | 문법은 맞지만 처리 불가 (유효성 오류) |
| 423  | Locked                      | 리소스 잠김 (WebDAV)                  |
| 424  | Failed Dependency           | 이전 요청 실패로 인한 실패 (WebDAV)   |
| 425  | Too Early                   | 재전송 공격 방지 (TLS Early Data)     |
| 426  | Upgrade Required            | 프로토콜 업그레이드 필요              |
| 428  | Precondition Required       | 조건부 요청 필수                      |
| 429  | Too Many Requests           | 요청 횟수 초과 (Rate Limit)           |
| 431  | Request Header Fields Large | 요청 헤더가 너무 큼                   |
| 451  | Unavailable For Legal       | 법적 사유로 접근 불가                 |

### 5xx — Server Error

| 코드 | 이름                       | 설명                                 |
|------|----------------------------|--------------------------------------|
| 500  | Internal Server Error      | 서버 내부 오류                       |
| 501  | Not Implemented            | 서버가 해당 기능 미구현              |
| 502  | Bad Gateway                | 게이트웨이/프록시가 잘못된 응답 수신 |
| 503  | Service Unavailable        | 서버 과부하 또는 점검 중             |
| 504  | Gateway Timeout            | 게이트웨이/프록시 응답 시간 초과     |
| 505  | HTTP Version Not Supported | HTTP 버전 미지원                     |
| 506  | Variant Also Negotiates    | 콘텐츠 협상 순환 참조                |
| 507  | Insufficient Storage       | 저장 공간 부족 (WebDAV)              |
| 508  | Loop Detected              | 무한 루프 감지 (WebDAV)              |
| 511  | Network Auth Required      | 네트워크 인증 필요 (캡티브 포털)     |

[⬆ 목차로 돌아가기](#목차)

---

## 2. SMTP 응답 코드

출처: RFC 5321 (https://datatracker.ietf.org/doc/html/rfc5321)

### 2xx — 성공

| 코드 | 설명                                        |
|------|---------------------------------------------|
| 211  | System status / help reply                  |
| 214  | Help message                                |
| 220  | Service ready                               |
| 221  | Service closing transmission channel        |
| 250  | Requested mail action okay, completed       |
| 251  | User not local; will forward                |
| 252  | Cannot VRFY user, but will attempt delivery |

### 3xx — 추가 정보 필요

| 코드 | 설명                                       |
|------|--------------------------------------------|
| 334  | Server challenge (AUTH)                    |
| 354  | Start mail input; end with `<CRLF>.<CRLF>` |

### 4xx — 일시적 오류 (재시도 가능)

| 코드 | 설명                                    |
|------|-----------------------------------------|
| 421  | Service not available, closing channel  |
| 450  | Mailbox unavailable (일시적)            |
| 451  | Requested action aborted: local error   |
| 452  | Insufficient system storage             |
| 455  | Server unable to accommodate parameters |

### 5xx — 영구 오류 (재시도 불가)

| 코드 | 설명                                        |
|------|---------------------------------------------|
| 500  | Syntax error, command unrecognized          |
| 501  | Syntax error in parameters or arguments     |
| 502  | Command not implemented                     |
| 503  | Bad sequence of commands                    |
| 504  | Command parameter not implemented           |
| 521  | Host does not accept mail                   |
| 530  | Not logged in / Authentication required     |
| 535  | Authentication credentials invalid          |
| 550  | Mailbox unavailable (영구적, 존재하지 않음) |
| 551  | User not local; please try forwarding       |
| 552  | Exceeded storage allocation                 |
| 553  | Mailbox name not allowed                    |
| 554  | Transaction failed / spam rejected          |
| 555  | MAIL FROM/RCPT TO parameters not recognized |

[⬆ 목차로 돌아가기](#목차)

---

## 3. FTP 응답 코드

출처: RFC 959 (https://datatracker.ietf.org/doc/html/rfc959)

### 1xx — 예비 응답

| 코드 | 설명                                            |
|------|-------------------------------------------------|
| 110  | Restart marker reply                            |
| 120  | Service ready in N minutes                      |
| 125  | Data connection already open; transfer starting |
| 150  | File status okay; about to open data connection |

### 2xx — 완료

| 코드 | 설명                                          |
|------|-----------------------------------------------|
| 200  | Command okay                                  |
| 202  | Command not implemented (superfluous)         |
| 211  | System status / help reply                    |
| 212  | Directory status                              |
| 213  | File status                                   |
| 214  | Help message                                  |
| 215  | NAME system type                              |
| 220  | Service ready for new user                    |
| 221  | Service closing control connection            |
| 225  | Data connection open; no transfer in progress |
| 226  | Closing data connection; transfer complete    |
| 227  | Entering Passive Mode                         |
| 228  | Entering Long Passive Mode                    |
| 229  | Entering Extended Passive Mode                |
| 230  | User logged in                                |
| 231  | User logged out; service terminated           |
| 232  | Logout command noted                          |
| 234  | AUTH command accepted                         |
| 250  | Requested file action okay, completed         |
| 257  | PATHNAME created                              |

### 3xx — 추가 정보 필요

| 코드 | 설명                                              |
|------|---------------------------------------------------|
| 331  | User name okay, need password                     |
| 332  | Need account for login                            |
| 350  | Requested file action pending further information |

### 4xx — 일시적 오류

| 코드 | 설명                                              |
|------|---------------------------------------------------|
| 421  | Service not available, closing control connection |
| 425  | Can't open data connection                        |
| 426  | Connection closed; transfer aborted               |
| 430  | Invalid username or password                      |
| 434  | Requested host unavailable                        |
| 450  | Requested file action not taken (file busy)       |
| 451  | Requested action aborted: local error             |
| 452  | Requested action not taken: insufficient storage  |

### 5xx — 영구 오류

| 코드 | 설명                                                       |
|------|------------------------------------------------------------|
| 500  | Syntax error, command unrecognized                         |
| 501  | Syntax error in parameters or arguments                    |
| 502  | Command not implemented                                    |
| 503  | Bad sequence of commands                                   |
| 504  | Command not implemented for that parameter                 |
| 530  | Not logged in                                              |
| 532  | Need account for storing files                             |
| 534  | Could not connect to server; issue with policy             |
| 550  | Requested action not taken: file unavailable               |
| 551  | Requested action aborted: page type unknown                |
| 552  | Requested file action aborted: exceeded storage allocation |
| 553  | Requested action not taken: file name not allowed          |

[⬆ 목차로 돌아가기](#목차)

---

## 4. DNS RCODE

출처: IANA DNS Parameters (https://www.iana.org/assignments/dns-parameters/)

| 코드 | 이름      | 설명                           |
|------|-----------|--------------------------------|
| 0    | NoError   | 오류 없음                      |
| 1    | FormErr   | 쿼리 형식 오류                 |
| 2    | ServFail  | 서버 처리 실패                 |
| 3    | NXDomain  | 존재하지 않는 도메인           |
| 4    | NotImp    | 미구현 쿼리 타입               |
| 5    | Refused   | 정책상 쿼리 거부               |
| 6    | YXDomain  | 존재하면 안 되는 이름이 존재   |
| 7    | YXRRSet   | 존재하면 안 되는 RR Set이 존재 |
| 8    | NXRRSet   | 존재해야 할 RR Set이 없음      |
| 9    | NotAuth   | 해당 존에 대한 권한 없음       |
| 10   | NotZone   | 이름이 존에 포함되지 않음      |
| 11   | DSOTYPENI | DSO-TYPE 미구현                |
| 16   | BADSIG    | TSIG 서명 실패                 |
| 17   | BADKEY    | 키 인식 불가                   |
| 18   | BADTIME   | 서명 시간 범위 초과            |
| 19   | BADMODE   | TKEY 모드 오류                 |
| 20   | BADNAME   | 중복 키 이름                   |
| 21   | BADALG    | 알고리즘 미지원                |
| 22   | BADTRUNC  | 잘못된 Truncation              |
| 23   | BADCOOKIE | 잘못된 서버 쿠키               |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 비공식 확장 코드

공식 IANA 등록 외 벤더/플랫폼에서 사용하는 코드입니다.

### HTTP 비공식 확장

| 코드 | 출처       | 설명                                                 |
|------|------------|------------------------------------------------------|
| 444  | Nginx      | 응답 없이 연결 종료 (악성 요청 차단)                 |
| 494  | Nginx      | Request Header Too Large                             |
| 495  | Nginx      | SSL Certificate Error                                |
| 496  | Nginx      | SSL Certificate Required                             |
| 497  | Nginx      | HTTP Request Sent to HTTPS Port                      |
| 499  | Nginx      | Client Closed Request (응답 전 클라이언트 연결 끊음) |
| 520  | Cloudflare | Unknown Error                                        |
| 521  | Cloudflare | Web Server Is Down                                   |
| 522  | Cloudflare | Connection Timed Out                                 |
| 523  | Cloudflare | Origin Is Unreachable                                |
| 524  | Cloudflare | A Timeout Occurred                                   |
| 525  | Cloudflare | SSL Handshake Failed                                 |
| 526  | Cloudflare | Invalid SSL Certificate                              |
| 530  | Cloudflare | Site Is Frozen / 1xxx error                          |

### curl 종료 코드 (Exit Code)

| 코드 | 설명                                     |
|------|------------------------------------------|
| 0    | 성공                                     |
| 1    | Unsupported protocol                     |
| 3    | URL malformed                            |
| 5    | Couldn't resolve proxy                   |
| 6    | Couldn't resolve host                    |
| 7    | Failed to connect to host                |
| 22   | HTTP page not retrieved (4xx/5xx)        |
| 23   | Write error                              |
| 26   | Read error                               |
| 28   | Operation timeout                        |
| 35   | SSL connect error                        |
| 47   | Too many redirects                       |
| 51   | SSL peer certificate verification failed |
| 52   | Server returned nothing                  |
| 56   | Failure in receiving network data        |
| 60   | SSL certificate problem                  |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- IANA HTTP Status Codes: [iana.org/assignments/http-status-codes](https://www.iana.org/assignments/http-status-codes/) — ★★★☆☆
- RFC 9110 HTTP Semantics: [datatracker.ietf.org/doc/html/rfc9110](https://datatracker.ietf.org/doc/html/rfc9110) — ★★★★☆
- RFC 5321 SMTP: [datatracker.ietf.org/doc/html/rfc5321](https://datatracker.ietf.org/doc/html/rfc5321) — ★★★★☆
- RFC 959 FTP: [datatracker.ietf.org/doc/html/rfc959](https://datatracker.ietf.org/doc/html/rfc959) — ★★★★☆
- IANA DNS Parameters: [iana.org/assignments/dns-parameters](https://www.iana.org/assignments/dns-parameters/) — ★★★☆☆
- curl Exit Codes: [curl.se/libcurl/c/libcurl-errors.html](https://curl.se/libcurl/c/libcurl-errors.html) — ★★★☆☆

---

**작성일**: 2026-05-26

**마지막 업데이트**: 2026-05-26

© 2026 siasia86. Licensed under CC BY 4.0.

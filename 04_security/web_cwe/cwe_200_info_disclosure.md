# CWE-200: Information Disclosure

서버 구성, 버전, 경로, 환경 변수 등 민감한 정보가 외부에 노출되어 공격자의 정보 수집(Reconnaissance)에 활용되는 취약점입니다.

## 목차

| 섹션                                                                                                 |
|------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 원리](#2-원리) / [3. PoC](#3-poc) / [4. 영향](#4-영향) / [5. 대응](#5-대응) |

---

## 1. 개요

| 항목      | 내용                                                       |
|-----------|------------------------------------------------------------|
| CWE ID    | CWE-200                                                    |
| 이름      | Exposure of Sensitive Information to an Unauthorized Actor |
| OWASP     | A01:2021 Broken Access Control                             |
| 영향      | 정보 수집 (후속 공격의 기초 데이터 제공)                   |
| 빈도      | 매우 높음 — phpinfo(), 에러 메시지, 디렉토리 리스팅        |
| 전제 조건 | 디버깅 설정 미제거, 기본 설정 그대로 운영                  |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 원리

### 정보 노출 유형

| 유형            | 예시                 | 노출 정보                                |
|-----------------|----------------------|------------------------------------------|
| phpinfo()       | info.php             | PHP 버전, 모듈, 경로, 환경 변수, OS 정보 |
| 에러 메시지     | PHP Fatal Error      | 파일 경로, 라인 번호, 함수명, DB 쿼리    |
| HTTP 헤더       | Server, X-Powered-By | 웹 서버 종류·버전, PHP 버전              |
| 디렉토리 리스팅 | Options +Indexes     | 파일 목록 전체 노출                      |
| 기본 페이지     | Apache "It works!"   | 서버 소프트웨어 식별                     |
| .git 노출       | /.git/HEAD           | 소스 코드 전체 복원 가능                 |

### 공격자 활용 흐름

```
1. phpinfo() 확인
   → PHP 8.2.x, Rocky Linux, httpd 2.4.x
   → disable_functions: (없음)
   → DocumentRoot: /var/www/html
   → DOCUMENT_ROOT, SERVER_ADDR, SERVER_SOFTWARE

2. 버전 정보로 알려진 취약점 검색
   → PHP 8.2.x CVE 확인
   → httpd 2.4.x 취약점 확인

3. 경로 정보로 정밀 공격
   → DocumentRoot 기반 파일 업로드 경로 추정
   → open_basedir 미설정 확인 → Path Traversal 시도
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. PoC

### 실습 URL

```
http://10.200.101.182/info.php
```

### phpinfo() 노출 정보 확인

| 섹션              | 수집 가능 정보      | 공격 활용                   |
|-------------------|---------------------|-----------------------------|
| PHP Version       | 8.2.x               | CVE 검색                    |
| System            | Linux rocky10 6.x.x | 커널 취약점 확인            |
| Server API        | Apache 2.0 Handler  | 웹 서버 종류                |
| DOCUMENT_ROOT     | /var/www/html       | 파일 경로 추정              |
| disable_functions | (없음)              | Command Injection 가능 확인 |
| open_basedir      | no value            | Path Traversal 가능 확인    |
| upload_tmp_dir    | /tmp                | 업로드 임시 경로            |
| REMOTE_ADDR       | 10.200.90.155       | 요청 IP                     |
| SERVER_ADDR       | 10.200.101.182      | 서버 IP                     |
| Environment       | PATH, HOME 등       | 시스템 환경                 |

### HTTP 헤더 확인

```bash
curl -I http://10.200.101.182/
# 예상:
# Server: Apache/2.4.x (Rocky Linux)
# X-Powered-By: PHP/8.2.x
```

### 에러 메시지 유도

```bash
# 존재하지 않는 파일 include 시도
curl "http://10.200.101.182/file_read.php?file=/nonexistent"
# 예상: Warning: file_get_contents(/nonexistent): Failed to open stream
#        in /var/www/html/file_read.php on line 12
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 영향

| 영향           | 설명                                                  |
|----------------|-------------------------------------------------------|
| 공격 벡터 식별 | 버전 정보 → 알려진 CVE 검색 → 정밀 공격               |
| 보안 설정 파악 | disable_functions, open_basedir → 공격 가능 범위 확정 |
| 내부 구조 노출 | 파일 경로, 네트워크 구성 → 침투 계획 수립             |
| 자격 증명 유출 | 환경 변수에 DB 비밀번호, API 키 포함 가능             |
| 소스 코드 노출 | .git 디렉토리 → 전체 소스 코드 복원                   |

🟡 Information Disclosure 자체는 직접적 피해를 주지 않지만, **다른 공격의 성공 확률을 높이는 정보**를 제공합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 5. 대응

### php.ini 설정

```ini
; PHP 버전 숨기기
expose_php = Off

; 에러 표시 끄기 (로그에만 기록)
display_errors = Off
log_errors = On
error_log = /var/log/php/error.log
```

### httpd.conf 설정

```apache
# 서버 버전 숨기기
ServerTokens Prod
ServerSignature Off

# 디렉토리 리스팅 금지
<Directory "/var/www/html">
    Options -Indexes
</Directory>

# X-Powered-By 헤더 제거 (mod_headers)
Header unset X-Powered-By
Header always unset X-Powered-By
```

### 운영 체크리스트

| 항목            | 조치                                           |
|-----------------|------------------------------------------------|
| phpinfo() 파일  | 삭제 또는 IP 제한                              |
| 에러 메시지     | display_errors = Off                           |
| 디렉토리 리스팅 | Options -Indexes                               |
| 서버 헤더       | ServerTokens Prod                              |
| .git 디렉토리   | DocumentRoot에 배포 금지 또는 접근 차단        |
| 기본 페이지     | 제거 또는 커스텀 페이지로 교체                 |
| 에러 페이지     | 커스텀 403/404/500 페이지 설정                 |
| 백업 파일       | .bak, .old, .swp 파일 DocumentRoot에 방치 금지 |

### .git 접근 차단

```apache
<DirectoryMatch "^/.*/\.git">
    Require all denied
</DirectoryMatch>
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- CWE-200: [cwe.mitre.org/data/definitions/200.html](https://cwe.mitre.org/data/definitions/200.html) — ★★★☆☆
- OWASP Information Disclosure: [owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering) — ★★★☆☆

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-07-02

**마지막 업데이트**: 2026-07-02

© 2026 siasia86. Licensed under CC BY 4.0.

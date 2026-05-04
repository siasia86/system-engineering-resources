# MySQL 설치 가이드

## 목차

| 섹션 |
|------|
| [1. 개요](#1-개요) / [2. Ubuntu 설치](#2-ubuntu-설치) / [3. RHEL 계열 설치](#3-rhel-계열-설치) |
| [4. 초기 보안 설정](#4-초기-보안-설정) / [5. 기본 설정 (my.cnf)](#5-기본-설정-mycnf) / [6. 복제 설정](#6-복제-설정) |
| [7. 방화벽 설정](#7-방화벽-설정) / [8. 설치 검증](#8-설치-검증) / [9. 트러블슈팅](#9-트러블슈팅) |
| [10. 기본 사용법](#10-기본-사용법) |

---

## 1. 개요

### 시스템 요구사항

| 항목     | 최소                  | 권장 (프로덕션)       |
|----------|-----------------------|-----------------------|
| CPU      | 1 core                | 4 core 이상           |
| RAM      | 1 GB                  | 8 GB 이상             |
| 디스크   | 5 GB                  | SSD 100 GB 이상       |
| OS       | Ubuntu 20.04+         | Ubuntu 22.04 / Rocky 9 / Alma 9 / RHEL 9 |
| 포트     | 3306/tcp              | 3306/tcp              |

### 버전 선택 기준

| 버전       | 상태          | 권장 여부                     |
|------------|---------------|-------------------------------|
| MySQL 8.0  | LTS (2026 EOL)| ⚠️ 신규 구축 비권장           |
| MySQL 8.4  | LTS (2032 EOL)| ✅ 신규 구축 권장             |
| MySQL 9.x  | Innovation    | 실험적 기능 평가용            |

[⬆ 목차로 돌아가기](#목차)

---

## 2. Ubuntu 설치

### Ubuntu 버전별 차이

| 항목                  | Ubuntu 22.04 (Jammy)          | Ubuntu 24.04 (Noble)              |
|-----------------------|-------------------------------|-----------------------------------|
| 기본 저장소 MySQL     | 8.0.x                         | 8.0.x                             |
| root 인증 방식        | `auth_socket`                 | `auth_socket`                     |
| my.cnf 경로           | `/etc/mysql/mysql.conf.d/mysqld.cnf` | `/etc/mysql/mysql.conf.d/mysqld.cnf` |
| Python 기본           | 3.10                          | 3.12                              |

### 2-1. 시스템 업데이트

```bash
sudo apt update && sudo apt upgrade -y
```

### 2-2. 설치 방법 A: APT (Ubuntu 기본 저장소)

Ubuntu 22.04 / 24.04 모두 동일하게 적용됩니다.

```bash
sudo apt install mysql-server -y
sudo systemctl enable --now mysql
```

⚠️ Ubuntu 기본 저장소의 MySQL 버전은 최신이 아닐 수 있습니다. 특정 버전이 필요하면 방법 B를 사용합니다.

### 2-3. 설치 방법 B: MySQL 공식 저장소

```bash
# MySQL APT 저장소 패키지 다운로드
wget https://dev.mysql.com/get/mysql-apt-config_0.8.33-1_all.deb
sudo dpkg -i mysql-apt-config_0.8.33-1_all.deb
# 대화형 메뉴에서 MySQL 8.4 선택 후 OK

sudo apt update
sudo apt install mysql-server -y
sudo systemctl enable --now mysql
```

### 2-4. Ubuntu 24.04 특이사항

Ubuntu 24.04는 `auth_socket` 플러그인이 기본값이므로 `sudo mysql -u root`로 접속합니다.
패스워드 인증이 필요하면 섹션 4-4 참고.

```bash
# Ubuntu 24.04: root 인증 방식 확인
sudo mysql -u root -e "SELECT user, host, plugin FROM mysql.user WHERE user='root';"
# plugin: auth_socket
```

### 2-5. 설치 확인

```bash
mysql --version
sudo systemctl status mysql
```

[⬆ 목차로 돌아가기](#목차)

---

## 3. RHEL 계열 설치

Rocky Linux, AlmaLinux, RHEL, CentOS Stream에서 동일하게 적용됩니다.

### 배포판별 EL 버전 대응

| 배포판              | EL 버전 | 저장소 RPM 경로 키워드 |
|---------------------|---------|------------------------|
| RHEL 8 / Rocky 8 / Alma 8 | el8 | `el8` |
| RHEL 9 / Rocky 9 / Alma 9 | el9 | `el9` |
| CentOS Stream 9     | el9     | `el9`                  |

### 3-1. 시스템 업데이트

```bash
sudo dnf update -y
```

### 3-2. 설치 방법 A: DNF (AppStream)

AppStream 저장소에 포함된 버전을 사용합니다. 최신 버전이 필요하면 방법 B를 사용합니다.

```bash
# 사용 가능한 MySQL 모듈 확인
sudo dnf module list mysql

# MySQL 8.0 설치
sudo dnf module enable mysql:8.0 -y
sudo dnf install mysql-server -y
sudo systemctl enable --now mysqld
```

### 3-3. 설치 방법 B: MySQL 공식 저장소

```bash
# EL9 (Rocky 9 / Alma 9 / RHEL 9 / CentOS Stream 9)
sudo dnf install -y https://dev.mysql.com/get/mysql84-community-release-el9-1.noarch.rpm

# EL8 (Rocky 8 / Alma 8 / RHEL 8)
sudo dnf install -y https://dev.mysql.com/get/mysql84-community-release-el8-1.noarch.rpm

sudo dnf install mysql-community-server -y
sudo systemctl enable --now mysqld
```

### 3-4. 임시 root 패스워드 확인

MySQL 최초 시작 시 임시 패스워드가 생성됩니다.

```bash
sudo grep 'temporary password' /var/log/mysqld.log
# [Note] A temporary password is generated for root@localhost: XXXXXXXX
```

### 3-5. SELinux 설정

RHEL 계열은 SELinux가 기본 활성화되어 있습니다. 비표준 포트 사용 시 설정이 필요합니다.

```bash
# SELinux 상태 확인
getenforce

# 기본 포트(3306) 사용 시 추가 설정 불필요
# 비표준 포트(예: 3307) 사용 시
sudo semanage port -a -t mysqld_port_t -p tcp 3307

# MySQL 데이터 디렉토리 변경 시 컨텍스트 설정
sudo semanage fcontext -a -t mysqld_db_t "/data/mysql(/.*)?"
sudo restorecon -Rv /data/mysql
```

### 3-6. 설치 확인

```bash
mysql --version
sudo systemctl status mysqld
```

[⬆ 목차로 돌아가기](#목차)

---

## 4. 초기 보안 설정

### 4-1. mysql_secure_installation

```bash
sudo mysql_secure_installation
```

```
Securing the MySQL server deployment.

Enter password for user root:          # 임시 패스워드 입력 (Rocky) 또는 엔터 (Ubuntu)

New password: SecurePassword123        # 새 root 패스워드 설정
Re-enter new password: SecurePassword123

Remove anonymous users? [Y/n] Y
Disallow root login remotely? [Y/n] Y
Remove test database and access to it? [Y/n] Y
Reload privilege tables now? [Y/n] Y
```

### 4-2. root 접속 확인

```bash
# Ubuntu: auth_socket 플러그인 사용 (sudo 필요)
sudo mysql -u root

# Rocky / 패스워드 인증
mysql -u root -p
```

### 4-3. 애플리케이션 전용 계정 생성

```sql
-- DB 생성
CREATE DATABASE mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 전용 계정 생성 (로컬 접속)
CREATE USER 'Secureuser123'@'localhost' IDENTIFIED BY 'SecurePassword123';
GRANT ALL PRIVILEGES ON mydb.* TO 'Secureuser123'@'localhost';

-- 원격 접속 허용 (특정 IP 대역)
CREATE USER 'Secureuser123'@'10.0.1.%' IDENTIFIED BY 'SecurePassword123';
GRANT SELECT, INSERT, UPDATE, DELETE ON mydb.* TO 'Secureuser123'@'10.0.1.%';

FLUSH PRIVILEGES;
```

### 4-4. Ubuntu auth_socket → 패스워드 인증 전환 (선택)

```sql
-- root 계정 인증 방식 변경
ALTER USER 'root'@'localhost'
    IDENTIFIED WITH caching_sha2_password BY 'SecurePassword123';
FLUSH PRIVILEGES;
```

[⬆ 목차로 돌아가기](#목차)

---

## 5. 기본 설정 (my.cnf)

```bash
# Ubuntu
sudo vi /etc/mysql/mysql.conf.d/mysqld.cnf

# Rocky Linux
sudo vi /etc/my.cnf
```

```ini
[mysqld]
# 기본
server_id        = 1
bind-address     = 0.0.0.0          # 원격 접속 허용 시 (기본: 127.0.0.1)
port             = 3306
datadir          = /var/lib/mysql
socket           = /var/run/mysqld/mysqld.sock

# 문자셋
character-set-server  = utf8mb4
collation-server      = utf8mb4_unicode_ci

# InnoDB
innodb_buffer_pool_size    = 1G     # RAM의 50~70% 권장
innodb_log_file_size       = 256M
innodb_flush_log_at_trx_commit = 1  # 1: 완전 내구성 (프로덕션 권장)
innodb_flush_method        = O_DIRECT

# 연결
max_connections            = 200
wait_timeout               = 600
interactive_timeout        = 600

# 슬로우 쿼리 로그
slow_query_log             = 1
slow_query_log_file        = /var/log/mysql/slow.log
long_query_time            = 1

# Binary Log (복제 사용 시)
log_bin                    = /var/log/mysql/mysql-bin.log
binlog_format              = ROW
binlog_expire_logs_seconds = 604800
```

```bash
sudo systemctl restart mysql   # Ubuntu
sudo systemctl restart mysqld  # Rocky
```

[⬆ 목차로 돌아가기](#목차)

---

## 6. 복제 설정

복제 상세 설정은 [rdbms_replication.md](../09_database/rdbms_replication.md) 참고.

### Primary 계정 생성

```sql
CREATE USER 'repl'@'10.0.1.%' IDENTIFIED BY 'SecurePassword123';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'10.0.1.%';
FLUSH PRIVILEGES;
```

### GTID 활성화 (my.cnf)

```ini
[mysqld]
gtid_mode                = ON
enforce_gtid_consistency = ON
log_replica_updates      = ON
```

[⬆ 목차로 돌아가기](#목차)

---

## 7. 방화벽 설정

### Ubuntu (ufw)

```bash
sudo ufw allow from 10.0.1.0/24 to any port 3306
sudo ufw reload
sudo ufw status
```

### Rocky Linux (firewalld)

```bash
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="10.0.1.0/24" port port="3306" protocol="tcp" accept'
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

[⬆ 목차로 돌아가기](#목차)

---

## 8. 설치 검증

```bash
# 서비스 상태
sudo systemctl status mysql      # Ubuntu
sudo systemctl status mysqld     # Rocky

# 포트 리스닝 확인
ss -tlnp | grep 3306

# 접속 테스트
mysql -u Secureuser123 -p mydb -e "SELECT VERSION(), NOW();"

# 슬로우 쿼리 로그 확인
sudo tail -f /var/log/mysql/slow.log
```

```sql
-- 주요 변수 확인
SHOW VARIABLES LIKE 'character_set_server';
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';
SHOW VARIABLES LIKE 'max_connections';
SHOW VARIABLES LIKE 'log_bin';
```

[⬆ 목차로 돌아가기](#목차)

---

## 9. 트러블슈팅

| 증상                                    | 원인                              | 해결 방법                                                    |
|-----------------------------------------|-----------------------------------|--------------------------------------------------------------|
| `Access denied for user 'root'`         | auth_socket 플러그인              | `sudo mysql -u root` 또는 인증 방식 변경 (섹션 4-4)         |
| `Can't connect to MySQL server`         | bind-address 제한 또는 방화벽     | `bind-address = 0.0.0.0` 설정 + 방화벽 허용                 |
| `ERROR 1045: Access denied`             | 계정/패스워드 불일치              | `SHOW GRANTS FOR 'user'@'host';` 확인                        |
| `Table 'mysql.user' doesn't exist`      | 초기화 미완료                     | `sudo mysqld --initialize` 재실행                            |
| `InnoDB: Cannot allocate memory`        | `innodb_buffer_pool_size` 과다    | RAM의 50~70% 이하로 조정                                     |
| `Too many connections`                  | `max_connections` 초과            | `SET GLOBAL max_connections = 300;`                          |
| Rocky: `mysqld.log` 에 임시 PW 없음     | 이미 초기화된 상태                | `sudo mysqld --initialize --user=mysql` 후 재시작            |

### 디버깅 명령

```bash
# 에러 로그 확인
sudo tail -100 /var/log/mysql/error.log    # Ubuntu
sudo tail -100 /var/log/mysqld.log         # Rocky

# 프로세스 목록
sudo mysqladmin -u root -p processlist

# 상태 확인
sudo mysqladmin -u root -p status
```

[⬆ 목차로 돌아가기](#목차)

---

## 10. 기본 사용법

### 접속

```bash
# root (Ubuntu: auth_socket)
sudo mysql -u root

# 패스워드 인증
mysql -u Secureuser123 -p mydb

# 원격 접속
mysql -h 10.0.1.10 -u Secureuser123 -p mydb
```

### DB / 테이블 기본 조작

```sql
-- DB 목록 / 선택
SHOW DATABASES;
USE mydb;

-- 테이블 생성
CREATE TABLE users (
    id         INT          NOT NULL AUTO_INCREMENT,
    username   VARCHAR(50)  NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- CRUD
INSERT INTO users (username, email) VALUES ('alice', 'alice@example.com');
SELECT * FROM users WHERE id = 1;
UPDATE users SET email = 'new@example.com' WHERE id = 1;
DELETE FROM users WHERE id = 1;

-- 테이블 목록 / 구조 확인
SHOW TABLES;
DESCRIBE users;
```

### 사용자 관리

```sql
-- 계정 목록
SELECT user, host FROM mysql.user;

-- 권한 확인
SHOW GRANTS FOR 'Secureuser123'@'localhost';

-- 패스워드 변경
ALTER USER 'Secureuser123'@'localhost' IDENTIFIED BY 'NewPassword123';

-- 계정 삭제
DROP USER 'Secureuser123'@'localhost';
```

### 백업 / 복원

```bash
# 백업 (Ubuntu: auth_socket 환경에서는 sudo 필요)
sudo mysqldump -u root mydb > mydb_$(date +%Y%m%d).sql

# 전체 백업
sudo mysqldump -u root --all-databases > all_$(date +%Y%m%d).sql

# 복원
sudo mysql -u root mydb < mydb_20260504.sql
```

### 서비스 관리

```bash
sudo systemctl start|stop|restart|status mysql
sudo mysqladmin -u root -p status        # 간단 상태
sudo mysqladmin -u root -p processlist   # 실행 중인 쿼리
```

[⬆ 목차로 돌아가기](#목차)

---

## 참고 자료

- MySQL Documentation: [Installing MySQL](https://dev.mysql.com/doc/refman/8.4/en/installing.html) — ★★★☆☆
- MySQL Documentation: [Postinstallation Setup](https://dev.mysql.com/doc/refman/8.4/en/postinstallation.html) — ★★★☆☆
- [rdbms_replication.md](../09_database/rdbms_replication.md)

---

## 통계

![GitHub stars](https://img.shields.io/github/stars/siasia86/system-engineering-resources?style=social)
![GitHub forks](https://img.shields.io/github/forks/siasia86/system-engineering-resources?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/siasia86/system-engineering-resources?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/siasia86/system-engineering-resources)
![License](https://img.shields.io/github/license/siasia86/system-engineering-resources)
![Actions](https://img.shields.io/github/actions/workflow/status/siasia86/system-engineering-resources/update-date.yml)

---

**작성일**: 2026-05-04

**마지막 업데이트**: 2026-05-04

© 2026 siasia86. Licensed under CC BY 4.0.
